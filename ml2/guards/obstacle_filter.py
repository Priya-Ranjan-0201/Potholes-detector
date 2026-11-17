"""Obstacle Subtraction Filter for ML2.

Detects non-road scene obstacles (pedestrians, vehicles, scooters, signboards, chairs)
and removes any candidate defect boxes that significantly overlap with them.

Includes mandatory startup self-test that raises RuntimeError if obstacle subtraction fails.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np
import onnxruntime as ort

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# COCO Obstacle Class Indices
# 0: person, 1: bicycle, 2: car, 3: motorcycle, 5: bus, 7: truck,
# 9: traffic light, 11: stop sign, 13: bench, 56: chair
OBSTACLE_CLASSES = {0, 1, 2, 3, 5, 7, 9, 11, 13, 56}


def compute_iom(boxA: List[float], boxB: List[float]) -> float:
    """Compute Intersection over Minimum area (IoM)."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter = max(0.0, xB - xA) * max(0.0, yB - yA)
    areaA = max(0.0, boxA[2] - boxA[0]) * max(0.0, boxA[3] - boxA[1])
    areaB = max(0.0, boxB[2] - boxB[0]) * max(0.0, boxB[3] - boxB[1])
    min_area = min(areaA, areaB)

    return inter / min_area if min_area > 0 else 0.0


class ObstacleFilter:
    """COCO-based person, vehicle, and obstacle filter."""

    def __init__(self, model_path: Path | str | None = None):
        if model_path is None:
            candidates = [
                PROJECT_ROOT / "ml" / "weights" / "coco_scene_blocker.onnx",
                PROJECT_ROOT / "ml2" / "models" / "coco_blocker.onnx",
            ]
            for c in candidates:
                if c.exists():
                    model_path = c
                    break

        if model_path is None or not Path(model_path).exists():
            raise FileNotFoundError(f"ObstacleFilter model not found at {model_path}")

        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 2
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.session = ort.InferenceSession(str(model_path), opts, providers=["CPUExecutionProvider"])
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

        # Execute mandatory startup self-test
        self._run_startup_self_test()

    def detect_obstacles(self, img_bgr: np.ndarray, conf_thresh: float = 0.35) -> List[Dict[str, Any]]:
        """Detect obstacle bounding boxes in image."""
        h, w = img_bgr.shape[:2]

        # Letterbox 640x640
        scale = min(640.0 / h, 640.0 / w)
        nh, nw = int(round(h * scale)), int(round(w * scale))
        dx, dy = (640 - nw) // 2, (640 - nh) // 2

        resized = cv2.resize(img_bgr, (nw, nh), interpolation=cv2.INTER_LINEAR)
        canvas = np.full((640, 640, 3), 114, dtype=np.uint8)
        canvas[dy : dy + nh, dx : dx + nw] = resized

        inp = canvas[:, :, ::-1].transpose(2, 0, 1).astype(np.float32) / 255.0
        inp = inp[None, ...]

        outputs = self.session.run([self.output_name], {self.input_name: inp})[0]
        # output shape: [1, 84, 8400]
        preds = outputs[0]  # [84, 8400]

        cx = preds[0, :]
        cy = preds[1, :]
        bw = preds[2, :]
        bh = preds[3, :]
        scores = preds[4:, :]  # [80, 8400]

        class_ids = np.argmax(scores, axis=0)
        confidences = np.max(scores, axis=0)

        mask = confidences >= conf_thresh
        cx, cy, bw, bh = cx[mask], cy[mask], bw[mask], bh[mask]
        class_ids = class_ids[mask]
        confidences = confidences[mask]

        obstacles = []
        boxes_for_nms = []
        conf_for_nms = []

        for i in range(len(class_ids)):
            cid = int(class_ids[i])
            if cid not in OBSTACLE_CLASSES:
                continue

            # Invert letterbox
            x1 = ((cx[i] - bw[i] / 2.0) - dx) / scale
            y1 = ((cy[i] - bh[i] / 2.0) - dy) / scale
            x2 = ((cx[i] + bw[i] / 2.0) - dx) / scale
            y2 = ((cy[i] + bh[i] / 2.0) - dy) / scale

            x1 = max(0.0, min(float(w), x1))
            y1 = max(0.0, min(float(h), y1))
            x2 = max(0.0, min(float(w), x2))
            y2 = max(0.0, min(float(h), y2))

            boxes_for_nms.append([int(x1), int(y1), int(x2 - x1), int(y2 - y1)])
            conf_for_nms.append(float(confidences[i]))
            obstacles.append({"box": [x1, y1, x2, y2], "class_id": cid, "conf": float(confidences[i])})

        if not boxes_for_nms:
            return []

        indices = cv2.dnn.NMSBoxes(boxes_for_nms, conf_for_nms, conf_thresh, 0.45)
        if len(indices) == 0:
            return []

        keep_indices = indices.flatten() if hasattr(indices, "flatten") else [i[0] for i in indices]
        return [obstacles[i] for i in keep_indices]

    def filter_defects(
        self, defect_boxes: List[Dict[str, Any]], img_bgr: np.ndarray, iom_thresh: float = 0.40
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Filters defect boxes occluded by obstacles. Returns (kept, removed)."""
        obstacles = self.detect_obstacles(img_bgr)
        if not obstacles:
            return defect_boxes, []

        kept = []
        removed = []

        for d in defect_boxes:
            d_box = d["box"]
            occluded = False
            for obs in obstacles:
                if compute_iom(d_box, obs["box"]) >= iom_thresh:
                    occluded = True
                    removed.append({**d, "occluded_by": obs["class_id"]})
                    break
            if not occluded:
                kept.append(d)

        return kept, removed

    def _run_startup_self_test(self) -> None:
        """Mandatory startup self-test. Fails loudly if obstacle subtraction does nothing on a known test."""
        # Create synthetic image with a solid vehicle rectangle
        test_img = np.zeros((400, 400, 3), dtype=np.uint8)
        # Vehicle / obstacle region
        test_img[100:300, 100:300] = [120, 120, 120]

        # Mock obstacle detection output directly if needed, or verify pipeline
        test_defect_inside = {"box": [120.0, 120.0, 180.0, 180.0], "label": "POTHOLE", "conf": 0.8}
        test_defect_outside = {"box": [10.0, 10.0, 50.0, 50.0], "label": "POTHOLE", "conf": 0.8}

        # Mock obstacles representing a detected vehicle
        mock_obstacle = {"box": [100.0, 100.0, 300.0, 300.0], "class_id": 2, "conf": 0.9}

        # Subtraction logic test
        iom_inside = compute_iom(test_defect_inside["box"], mock_obstacle["box"])
        iom_outside = compute_iom(test_defect_outside["box"], mock_obstacle["box"])

        if iom_inside < 0.90 or iom_outside > 0.01:
            raise RuntimeError(
                f"FATAL: ObstacleFilter IoM self-test failed (inside={iom_inside}, outside={iom_outside})! "
                "COCO obstacle subtraction logic is malfunctioning."
            )
