"""ML2 Harmonized Road Damage Detector Pipeline.

Fresh, modular road damage detection pipeline implementing:
- Stage 5: Input Gate (rejects diagrams, screenshots, infographics)
- Stage 1: Balanced YOLO11 Detector (trained with 26.8% negative background regularization)
- Stage 2: Specialized Expert Heads (Crack specialist + Local road depression specialist)
- Stage 4: Person / Vehicle / Obstacle Subtraction (COCO detector with startup self-test)
- Stage 3: Drivable Road Surface Mask Prior (0.38h physical horizon cutoff, road continuity)
- Stage 7: Calibrated Operating Presets (High Precision, Balanced, High Recall)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np
import onnxruntime as ort

from ml2.guards.input_gate import InputGate
from ml2.guards.obstacle_filter import ObstacleFilter
from ml2.guards.road_mask import RoadSurfaceSegmenter
from ml2.pipeline.wbf import weighted_boxes_fusion

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CLASS_NAMES = {
    0: "POTHOLE",
    1: "CRACK_LONGITUDINAL",
    2: "CRACK_TRANSVERSE",
    3: "CRACK_ALLIGATOR",
}


class ML2DetectorPipeline:
    """Fresh ML2 Road Damage Detection Pipeline."""

    def __init__(self, model_path: Path | str | None = None):
        # 1. Initialize Guards
        self.input_gate = InputGate()
        self.obstacle_filter = ObstacleFilter()
        self.road_segmenter = RoadSurfaceSegmenter(horizon_cutoff_pct=0.385, min_overlap_pct=0.35)

        # 2. Locate trained detector models
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 2
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        bal_path = PROJECT_ROOT / "ml2" / "models" / "yolo11_road_damage.onnx"
        crk_path = PROJECT_ROOT / "ml2" / "models" / "yolo11_road_damage_prev.onnx"
        dep_path = PROJECT_ROOT / "runs" / "rescue_train" / "yolo11n_rescue" / "weights" / "best.onnx"
        pot_path = PROJECT_ROOT / "ml" / "weights" / "yolo11n_pothole_best.onnx"

        if model_path is not None:
            bal_path = Path(model_path)
        elif not bal_path.exists() and dep_path.exists():
            bal_path = dep_path

        self.sess_balanced = None
        self.sess_crack = None
        self.sess_deep = None
        self.sess_pothole = None

        if bal_path.exists():
            self.sess_balanced = ort.InferenceSession(str(bal_path), opts, providers=["CPUExecutionProvider"])
        else:
            raise FileNotFoundError(f"Primary ML2 detector model not found at {bal_path}")

        if crk_path.exists():
            self.sess_crack = ort.InferenceSession(str(crk_path), opts, providers=["CPUExecutionProvider"])

        if dep_path.exists():
            self.sess_deep = ort.InferenceSession(str(dep_path), opts, providers=["CPUExecutionProvider"])

        if pot_path.exists():
            self.sess_pothole = ort.InferenceSession(str(pot_path), opts, providers=["CPUExecutionProvider"])

        self.model_path = str(bal_path)

    def predict(
        self, img_rgb: np.ndarray, preset: str = "balanced"
    ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """Runs the complete ML2 pipeline on an RGB image array.

        Returns:
            (is_road_photo: bool, rejection_reason: str, detections: List[Dict])
        """
        # --- Stage 5: Input Gate ---
        is_road, reason = self.input_gate.evaluate(img_rgb)
        if not is_road:
            return False, reason, []

        h, w = img_rgb.shape[:2]
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        # Specular reflection ratio & texture sharpness
        specular_ratio = np.sum((hsv[:, :, 2] > 220) & (hsv[:, :, 1] < 40)) / (h * w)
        lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Calibrated Preset Thresholds
        if preset == "high_precision":
            conf_thresh = 0.45
            crack_thresh = 0.45
            dep_thresh = 0.45
        elif preset == "high_recall":
            conf_thresh = 0.20
            crack_thresh = 0.25
            dep_thresh = 0.25
        else:  # balanced
            conf_thresh = 0.35
            crack_thresh = 0.35
            dep_thresh = 0.35

        # Letterbox 640x640
        scale = min(640.0 / h, 640.0 / w)
        nw, nh = int(round(w * scale)), int(round(h * scale))
        dx, dy = (640 - nw) // 2, (640 - nh) // 2

        resized = cv2.resize(img_bgr, (nw, nh), interpolation=cv2.INTER_LINEAR)
        canvas = np.full((640, 640, 3), 114, dtype=np.uint8)
        canvas[dy : dy + nh, dx : dx + nw] = resized

        inp = canvas[:, :, ::-1].transpose(2, 0, 1).astype(np.float32) / 255.0
        inp = inp[None, ...]

        candidates = []
        boxes_nms = []
        confs_nms = []

        # --- Stage 1: Primary Balanced Detector ---
        out_name = self.sess_balanced.get_outputs()[0].name
        in_name = self.sess_balanced.get_inputs()[0].name
        p_bal = self.sess_balanced.run([out_name], {in_name: inp})[0][0]

        scores_bal = p_bal[4:, :]
        confs_bal = np.max(scores_bal, axis=0)
        cids_bal = np.argmax(scores_bal, axis=0)
        mask_bal = ((cids_bal == 0) & (confs_bal >= conf_thresh)) | (
            (cids_bal != 0) & (confs_bal >= max(conf_thresh, 0.22))
        )

        for cx, cy, bw, bh, cid, c in zip(
            p_bal[0, mask_bal],
            p_bal[1, mask_bal],
            p_bal[2, mask_bal],
            p_bal[3, mask_bal],
            cids_bal[mask_bal],
            confs_bal[mask_bal],
        ):
            x1 = max(0.0, min(float(w), ((cx - bw / 2.0) - dx) / scale))
            y1 = max(0.0, min(float(h), ((cy - bh / 2.0) - dy) / scale))
            x2 = max(0.0, min(float(w), ((cx + bw / 2.0) - dx) / scale))
            y2 = max(0.0, min(float(h), ((cy + bh / 2.0) - dy) / scale))
            bw_px, bh_px = x2 - x1, y2 - y1
            area_ratio = (bw_px * bh_px) / (w * h)
            cx_box = (x1 + x2) / 2.0
            # Border artifact rejection: ignore spurious slice artifacts hugging image perimeter
            if ((x1 <= 3 or x2 >= w - 3) and c < 0.45) or cx_box < 0.03 * w or cx_box > 0.97 * w:
                continue
            # Horizon noise rejection: upper 12% should not have weak detections
            if y2 < h * 0.12 and c < 0.55:
                continue
            if c < 0.30 and (bh_px > h * 0.45 or area_ratio > 0.18):
                continue
            if bw_px >= 12 and bh_px >= 12:
                boxes_nms.append([int(x1), int(y1), int(bw_px), int(bh_px)])
                confs_nms.append(float(c))
                candidates.append({
                    "box": [x1, y1, x2, y2],
                    "conf": float(c),
                    "class_id": int(cid),
                    "label": CLASS_NAMES.get(int(cid), "POTHOLE"),
                })

        # --- Stage 2A: Crack Specialist Head (Dry road surface only) ---
        if self.sess_crack is not None and specular_ratio < 0.10 and lap_var > 600:
            out_c = self.sess_crack.get_outputs()[0].name
            in_c = self.sess_crack.get_inputs()[0].name
            p_crk = self.sess_crack.run([out_c], {in_c: inp})[0][0]

            scores_crk = p_crk[4:, :]
            confs_crk = np.max(scores_crk, axis=0)
            cids_crk = np.argmax(scores_crk, axis=0)
            mask_crk = (confs_crk >= crack_thresh) & (cids_crk == 3)

            for cx, cy, bw, bh, cid, c in zip(
                p_crk[0, mask_crk],
                p_crk[1, mask_crk],
                p_crk[2, mask_crk],
                p_crk[3, mask_crk],
                cids_crk[mask_crk],
                confs_crk[mask_crk],
            ):
                x1 = max(0.0, min(float(w), ((cx - bw / 2.0) - dx) / scale))
                y1 = max(0.0, min(float(h), ((cy - bh / 2.0) - dy) / scale))
                x2 = max(0.0, min(float(w), ((cx + bw / 2.0) - dx) / scale))
                y2 = max(0.0, min(float(h), ((cy + bh / 2.0) - dy) / scale))
                bw_px, bh_px = x2 - x1, y2 - y1
                area_ratio = (bw_px * bh_px) / (w * h)
                if c < 0.30 and (bh_px > h * 0.45 or area_ratio > 0.18):
                    continue
                if bw_px >= 4 and bh_px >= 4:
                    boxes_nms.append([int(x1), int(y1), int(bw_px), int(bh_px)])
                    confs_nms.append(float(c))
                    candidates.append({
                        "box": [x1, y1, x2, y2],
                        "conf": float(c),
                        "class_id": 3,
                        "label": "CRACK_ALLIGATOR",
                    })

        # --- Stage 2B: Rescue Pothole and Distress Specialist ---
        if self.sess_deep is not None:
            out_d = self.sess_deep.get_outputs()[0].name
            in_d = self.sess_deep.get_inputs()[0].name
            p_dep = self.sess_deep.run([out_d], {in_d: inp})[0][0]

            scores_dep = p_dep[4:, :]
            confs_dep = np.max(scores_dep, axis=0)
            cids_dep = np.argmax(scores_dep, axis=0)
            mask_dep = (confs_dep >= dep_thresh) & ((cids_dep == 0) | (cids_dep == 3))

            for cx, cy, bw, bh, cid, c in zip(
                p_dep[0, mask_dep],
                p_dep[1, mask_dep],
                p_dep[2, mask_dep],
                p_dep[3, mask_dep],
                cids_dep[mask_dep],
                confs_dep[mask_dep],
            ):
                x1 = max(0.0, min(float(w), ((cx - bw / 2.0) - dx) / scale))
                y1 = max(0.0, min(float(h), ((cy - bh / 2.0) - dy) / scale))
                x2 = max(0.0, min(float(w), ((cx + bw / 2.0) - dx) / scale))
                y2 = max(0.0, min(float(h), ((cy + bh / 2.0) - dy) / scale))
                bw_px, bh_px = x2 - x1, y2 - y1
                area_ratio = (bw_px * bh_px) / (w * h)
                cx_box = (x1 + x2) / 2.0
                if ((x1 <= 3 or x2 >= w - 3) and c < 0.45) or cx_box < 0.03 * w or cx_box > 0.97 * w:
                    continue
                if y2 < h * 0.12 and c < 0.55:
                    continue
                if c < 0.30 and (bh_px > h * 0.45 or area_ratio > 0.18):
                    continue
                if bw_px >= 12 and bh_px >= 12:
                    boxes_nms.append([int(x1), int(y1), int(bw_px), int(bh_px)])
                    confs_nms.append(float(c))
                    candidates.append({
                        "box": [x1, y1, x2, y2],
                        "conf": float(c),
                        "class_id": int(cid),
                        "label": CLASS_NAMES.get(int(cid), "POTHOLE"),
                    })

        # --- Stage 2C: Dedicated Pothole & Puddle Specialist ---
        if self.sess_pothole is not None:
            out_p = self.sess_pothole.get_outputs()[0].name
            in_p = self.sess_pothole.get_inputs()[0].name
            p_pot = self.sess_pothole.run([out_p], {in_p: inp})[0][0]

            scores_pot = p_pot[4:, :]
            confs_pot = np.max(scores_pot, axis=0)
            cids_pot = np.argmax(scores_pot, axis=0)
            mask_pot = (confs_pot >= conf_thresh) & (cids_pot == 0)

            for cx, cy, bw, bh, cid, c in zip(
                p_pot[0, mask_pot],
                p_pot[1, mask_pot],
                p_pot[2, mask_pot],
                p_pot[3, mask_pot],
                cids_pot[mask_pot],
                confs_pot[mask_pot],
            ):
                x1 = max(0.0, min(float(w), ((cx - bw / 2.0) - dx) / scale))
                y1 = max(0.0, min(float(h), ((cy - bh / 2.0) - dy) / scale))
                x2 = max(0.0, min(float(w), ((cx + bw / 2.0) - dx) / scale))
                y2 = max(0.0, min(float(h), ((cy + bh / 2.0) - dy) / scale))
                bw_px, bh_px = x2 - x1, y2 - y1
                area_ratio = (bw_px * bh_px) / (w * h)
                if c < 0.30 and (bh_px > h * 0.45 or area_ratio > 0.18):
                    continue
                if bw_px >= 4 and bh_px >= 4:
                    boxes_nms.append([int(x1), int(y1), int(bw_px), int(bh_px)])
                    confs_nms.append(float(c))
                    candidates.append({
                        "box": [x1, y1, x2, y2],
                        "conf": float(c),
                        "class_id": 0,
                        "label": "POTHOLE",
                    })

        if not candidates:
            return True, "ok", []

        # --- Stage 6: Weighted Boxes Fusion (WBF) ---
        fused_candidates = weighted_boxes_fusion(
            candidates, iou_thr=0.40, skip_box_thr=conf_thresh
        )
        if not fused_candidates:
            return True, "ok", []

        # --- Stage 4: Person / Vehicle / Obstacle Subtraction ---
        after_obstacles, _ = self.obstacle_filter.filter_defects(
            fused_candidates, img_bgr, iom_thresh=0.40
        )

        # --- Stage 3: Road Surface Mask Prior Filtering ---
        final_boxes, _ = self.road_segmenter.filter_defects(after_obstacles, img_bgr)

        return True, "ok", final_boxes
