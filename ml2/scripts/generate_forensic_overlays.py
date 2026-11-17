"""Generate Before vs After Forensic Overlays for eval_failures/ Test Cases."""

from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2
import numpy as np
from PIL import Image, ImageOps

from ml2.pipeline.detector import ML2DetectorPipeline


def generate_forensics():
    pipe = ML2DetectorPipeline()
    cases = [
        "case_01_pothole_nh44",
        "case_02_civil_distress_diagram",
        "case_03_alligator_cracks",
        "case_04_bengaluru_potholes",
        "case_05_asphalt_crater",
        "case_06_mumbai_potholes",
        "case_07_user_tested_potholes",
    ]

    for case in cases:
        folder = PROJECT_ROOT / "docs" / "forensics" / case
        folder.mkdir(parents=True, exist_ok=True)
        img_files = list((PROJECT_ROOT / "eval_failures").glob(f"{case}*"))
        if not img_files:
            continue
        img_path = img_files[0]

        pil_img = ImageOps.exif_transpose(Image.open(img_path))
        rgb = np.array(pil_img.convert("RGB"))
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

        is_road, reason, dets = pipe.predict(rgb, preset="balanced")

        overlay = bgr.copy()
        if not is_road:
            cv2.putText(
                overlay,
                f"REJECTED: {reason}",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 255),
                2,
            )
        else:
            for d in dets:
                bx = [int(v) for v in d["box"]]
                cv2.rectangle(overlay, (bx[0], bx[1]), (bx[2], bx[3]), (0, 255, 0), 2)
                lbl = f"{d['label']} {d['conf']:.2f}"
                cv2.putText(
                    overlay,
                    lbl,
                    (bx[0], max(20, bx[1] - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )
            cv2.putText(
                overlay,
                f"ML2 RESCUED: {len(dets)} detections (0 off-road)",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

        out_overlay_path = folder / "overlay_ml2_after.jpg"
        cv2.imwrite(str(out_overlay_path), overlay)

        trace_data = {
            "case": case,
            "pipeline": "ML2 Harmonized Detector Pipeline",
            "is_road": is_road,
            "rejection_reason": reason,
            "detections_count": len(dets),
            "detections": [
                {
                    "box": [float(v) for v in d["box"]],
                    "conf": float(d["conf"]),
                    "label": d["label"],
                }
                for d in dets
            ],
        }
        with open(folder / "trace_ml2_after.json", "w", encoding="utf-8") as f:
            json.dump(trace_data, f, indent=2)

        print(f"[FORENSICS] {case:<30} -> {len(dets)} dets, is_road={is_road}")


if __name__ == "__main__":
    generate_forensics()
