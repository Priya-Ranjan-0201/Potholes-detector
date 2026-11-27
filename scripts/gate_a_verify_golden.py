"""Gate A Forensic Verification and Trace Generator.
Reproduces all failure cases, audits model outputs across pipeline stages,
and verifies zero detections on people/vehicles/signs/trees/sky/blur and diagram rejection.
"""

from __future__ import annotations

import io
import json
import os
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

COCO_NAMES = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
    9: "traffic light",
    11: "stop sign",
    13: "bench",
    56: "chair",
    58: "potted plant",
}
import sys
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ml2.pipeline.detector import ML2DetectorPipeline
from ml2.guards.obstacle_filter import ObstacleFilter
EVAL_DIR = REPO_ROOT / "eval_failures"
FORENSICS_DIR = REPO_ROOT / "docs" / "forensics"
FORENSICS_DIR.mkdir(parents=True, exist_ok=True)

def run_gate_a_audit():
    pipe = ML2DetectorPipeline()
    obs_filter = pipe.obstacle_filter

    expected_file = EVAL_DIR / "expected.json"
    with open(expected_file, "r", encoding="utf-8") as f:
        expected_data = json.load(f)

    audit_results = {}
    total_violations = 0

    cases = sorted([f for f in os.listdir(EVAL_DIR) if f.endswith((".jpg", ".avif", ".png"))])

    for fname in cases:
        img_path = EVAL_DIR / fname
        case_name = Path(fname).stem
        case_forensics_dir = FORENSICS_DIR / case_name
        case_forensics_dir.mkdir(parents=True, exist_ok=True)

        pil_im = Image.open(img_path).convert("RGB")
        arr_rgb = np.array(pil_im)
        img_bgr = cv2.cvtColor(arr_rgb, cv2.COLOR_RGB2BGR)
        h, w = arr_rgb.shape[:2]

        # Stage 0: Input Gate
        is_road, reason = pipe.input_gate.evaluate(arr_rgb)

        # Stage 1: Obstacles (COCO detector)
        obstacles = obs_filter.detect_obstacles(img_bgr, conf_thresh=0.30)

        # Stage 2: Road Surface Mask
        road_mask = pipe.road_segmenter.compute_road_mask(img_bgr)

        # Stage 3: End-to-end ML2 prediction
        is_road_pred, pred_reason, final_dets = pipe.predict(arr_rgb, preset="balanced")

        # Save Visualizations
        overlay = img_bgr.copy()

        # Draw road mask outline (cyan)
        contours, _ = cv2.findContours(road_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(overlay, contours, -1, (255, 255, 0), 1)

        # Draw obstacles (blue)
        for obs in obstacles:
            ox = [int(v) for v in obs["box"]]
            obs_label = COCO_NAMES.get(obs["class_id"], "obstacle")
            cv2.rectangle(overlay, (ox[0], ox[1]), (ox[2], ox[3]), (255, 100, 0), 2)
            cv2.putText(
                overlay,
                f"{obs_label} {obs['conf']:.2f}",
                (ox[0], max(12, ox[1] - 4)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 100, 0),
                1,
            )

        # Check for forbidden box violations per expected.json
        expected_case = expected_data.get(fname, {})
        forbidden_list = expected_case.get("forbidden_boxes_on", [])
        forbidden_hits = []

        check_sky = any(f in forbidden_list for f in ["sky", "vegetation", "signboard", "tree", "building"])

        for i, d in enumerate(final_dets):
            bx = d["box"]
            x1, y1, x2, y2 = [int(v) for v in bx]

            # 1. Sky/horizon check (only for scenes containing sky/horizon)
            if check_sky and (y2 / h) < 0.18:
                forbidden_hits.append(f"Box {i} ({d['label']}) in upper horizon/sky zone y2={y2/h:.2%}")

            # 2. Obstacle overlap check (people, vehicles, scooters, chairs, etc.)
            for obs in obstacles:
                ox = obs["box"]
                obs_label = COCO_NAMES.get(obs["class_id"], "obstacle")
                xa = max(bx[0], ox[0])
                ya = max(bx[1], ox[1])
                xb = min(bx[2], ox[2])
                yb = min(bx[3], ox[3])
                inter = max(0.0, xb - xa) * max(0.0, yb - ya)
                area_d = max(1.0, (bx[2] - bx[0]) * (bx[3] - bx[1]))
                area_o = max(1.0, (ox[2] - ox[0]) * (ox[3] - ox[1]))
                iom = inter / min(area_d, area_o)
                if iom > 0.35:
                    forbidden_hits.append(f"Box {i} overlaps obstacle {obs_label} (IoM={iom:.2f})")

            # Draw final detection (green for pothole, orange for crack)
            color = (0, 255, 0) if "POTHOLE" in d["label"] else (0, 165, 255)
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                overlay,
                f"{d['label']} {d['conf']:.2f}",
                (x1, max(12, y1 - 4)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                color,
                1,
            )

        # Check diagram rejection expectation
        diagram_pass = True
        if fname == "case_02_civil_distress_diagram.jpg":
            diagram_pass = (not is_road_pred) and (len(final_dets) == 0)

        case_passed = (len(forbidden_hits) == 0) and diagram_pass

        trace = {
            "file": fname,
            "dimensions": [w, h],
            "input_gate": {
                "is_road": is_road,
                "reason": reason,
            },
            "obstacles_detected": len(obstacles),
            "obstacles": [
                {
                    "label": COCO_NAMES.get(o["class_id"], "obstacle"),
                    "conf": round(float(o["conf"]), 3),
                    "box": [round(float(v), 1) for v in o["box"]],
                }
                for o in obstacles
            ],
            "final_detections_count": len(final_dets),
            "final_detections": [
                {
                    "label": d["label"],
                    "conf": round(float(d["conf"]), 3),
                    "box": [round(float(v), 1) for v in d["box"]],
                }
                for d in final_dets
            ],
            "forbidden_box_violations": forbidden_hits,
            "passed_gate_a": case_passed,
        }

        # Save forensics files
        cv2.imwrite(str(case_forensics_dir / "input.jpg"), img_bgr)
        cv2.imwrite(str(case_forensics_dir / "overlay.jpg"), overlay)
        with open(case_forensics_dir / "trace.json", "w", encoding="utf-8") as f:
            json.dump(trace, f, indent=2)

        audit_results[fname] = trace
        if not case_passed:
            total_violations += 1

    summary_file = FORENSICS_DIR / "gate_a_forensics_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)

    print("\n" + "=" * 60)
    print("GATE A AUDIT SUMMARY")
    print("=" * 60)
    for fname, r in audit_results.items():
        status = "PASS" if r["passed_gate_a"] else "FAIL"
        print(f"[{status}] {fname}: {r['final_detections_count']} dets, {r['obstacles_detected']} obstacles, violations={len(r['forbidden_box_violations'])}")
        if r["forbidden_box_violations"]:
            for v in r["forbidden_box_violations"]:
                print(f"       -> {v}")
    print("=" * 60)
    print(f"Total Cases: {len(audit_results)}, Total Failing Cases: {total_violations}")
    print("=" * 60)
    return total_violations == 0

if __name__ == "__main__":
    success = run_gate_a_audit()
    exit(0 if success else 1)
