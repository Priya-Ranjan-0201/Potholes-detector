"""Automated Acceptance Test Suite for Road Damage Detector.

Executes:
- A1: Eval Failures Test Suite (eval_failures/expected.json)
- A2: Locked Benchmark Evaluation (N=730, SHA-256 hashed in data/rescue_benchmark/manifest.json)
  - Damage Yes/No Accuracy (target >= 90%)
  - Clutter False Alarm Rate (target <= 2%)
  - Non-Road Rejection Rate (target >= 95%)
  - Object-Level F1 @ IoU 0.5 (with 95% bootstrap CI)

Usage:
    python ml2/tests/test_acceptance.py --pipeline old
    python ml2/tests/test_acceptance.py --pipeline ml2
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np
from PIL import Image, ImageOps

# Ensure scam_road root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def load_image_rgb(path: Path | str) -> np.ndarray:
    """Load image universally with EXIF orientation correction, returning RGB array."""
    pil_img = Image.open(str(path))
    pil_img = ImageOps.exif_transpose(pil_img)
    return np.array(pil_img.convert("RGB"))


def compute_iou(boxA: List[float], boxB: List[float]) -> float:
    """Compute IoU between two [x1, y1, x2, y2] bounding boxes."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    inter = max(0.0, xB - xA) * max(0.0, yB - yA)
    areaA = max(0.0, boxA[2] - boxA[0]) * max(0.0, boxA[3] - boxA[1])
    areaB = max(0.0, boxB[2] - boxB[0]) * max(0.0, boxB[3] - boxB[1])
    union = areaA + areaB - inter
    return inter / union if union > 0 else 0.0


def bootstrap_ci(metric_samples: List[float], n_resamples: int = 1000, alpha: float = 0.05) -> Tuple[float, float]:
    """Compute 95% bootstrap confidence interval."""
    if not metric_samples:
        return 0.0, 0.0
    rng = np.random.default_rng(42)
    arr = np.array(metric_samples)
    n = len(arr)
    boot_means = [float(np.mean(rng.choice(arr, size=n, replace=True))) for _ in range(n_resamples)]
    low = float(np.percentile(boot_means, (alpha / 2.0) * 100))
    high = float(np.percentile(boot_means, (1.0 - alpha / 2.0) * 100))
    return round(low, 4), round(high, 4)


class OldPipelineAdapter:
    """Adapter wrapping the legacy / current baseline pipeline."""

    def __init__(self):
        from backend.app.api.v1.infer import check_image_usability, run_pipeline_on_image
        self.check_usability = check_image_usability
        self.run_pipeline = run_pipeline_on_image

    def predict(self, img_rgb: np.ndarray, preset: str = "balanced") -> Tuple[bool, str, List[Dict[str, Any]]]:
        """Returns (is_road, rejection_reason, list_of_detections)."""
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        usable, reason = self.check_usability(img_bgr)
        if not usable:
            return False, reason, []

        h, w = img_rgb.shape[:2]
        dets = self.run_pipeline(img_bgr, conf_thresh=0.25, iou_thresh=0.35, preset=preset)
        boxes = []
        for d in dets:
            bx = d.box  # [x_pct, y_pct, w_pct, h_pct]
            x1 = (bx[0] / 100.0) * w
            y1 = (bx[1] / 100.0) * h
            x2 = x1 + (bx[2] / 100.0) * w
            y2 = y1 + (bx[3] / 100.0) * h
            boxes.append({
                "box": [float(x1), float(y1), float(x2), float(y2)],
                "conf": float(d.confidence),
                "label": str(d.label).upper(),
            })
        return True, "ok", boxes


def get_pipeline(name: str):
    if name == "old":
        return OldPipelineAdapter()
    elif name == "ml2":
        from ml2.pipeline.detector import ML2DetectorPipeline
        return ML2DetectorPipeline()
    else:
        raise ValueError(f"Unknown pipeline: {name}")


def run_test_a1(pipeline, verbose: bool = True) -> Tuple[bool, Dict[str, Any]]:
    """A1: Test on eval_failures/ cases."""
    expected_path = PROJECT_ROOT / "eval_failures" / "expected.json"
    if not expected_path.exists():
        print(f"[FAIL] Missing {expected_path}")
        return False, {}

    with open(expected_path, "r", encoding="utf-8") as f:
        expected = json.load(f)

    print("\n" + "=" * 70)
    print(" ACCEPTANCE TEST A1: eval_failures/ TEST CASES")
    print("=" * 70)

    all_pass = True
    results = {}

    # Define known off-road / obstacle regions for eval cases
    # case_04: signboard/trees/chairs/sky are upper 40% and right edge
    # case_02: diagram must be rejected
    for filename, spec in expected.items():
        img_path = PROJECT_ROOT / "eval_failures" / filename
        if not img_path.exists():
            print(f"[FAIL] {filename:<35} | Missing image file")
            all_pass = False
            continue

        img_rgb = load_image_rgb(img_path)
        h, w = img_rgb.shape[:2]

        is_road, reason, detections = pipeline.predict(img_rgb, preset="balanced")

        case_passed = True
        failure_reasons = []

        # Check road photo rejection
        if not spec.get("road_photo", True):
            if is_road and len(detections) > 0:
                case_passed = False
                failure_reasons.append(f"Expected diagram rejection but got {len(detections)} boxes")
            elif not is_road:
                # Correctly rejected
                pass
        else:
            if not is_road:
                case_passed = False
                failure_reasons.append(f"Real road falsely rejected: {reason}")

            # Check min potholes / cracks
            min_potholes = spec.get("min_potholes", 0)
            pothole_count = sum(1 for d in detections if "POTHOLE" in d["label"])
            if pothole_count < min_potholes:
                case_passed = False
                failure_reasons.append(f"Expected >= {min_potholes} potholes, got {pothole_count}")

            min_cracks = spec.get("min_cracks", 0)
            crack_count = sum(1 for d in detections if "CRACK" in d["label"])
            if crack_count < min_cracks:
                case_passed = False
                failure_reasons.append(f"Expected >= {min_cracks} cracks, got {crack_count}")

            # Check forbidden boxes (off-road, sky, signboards)
            # In case_04, upper 33% is sky/storefronts
            if filename == "case_04_bengaluru_potholes.jpg":
                offroad_boxes = [d for d in detections if (d["box"][1] + d["box"][3]) / 2.0 < 0.35 * h]
                if offroad_boxes:
                    case_passed = False
                    failure_reasons.append(f"{len(offroad_boxes)} boxes in upper sky/signboard zone")

            if spec.get("max_detections") is not None and len(detections) > spec["max_detections"]:
                case_passed = False
                failure_reasons.append(f"Expected <= {spec['max_detections']} detections, got {len(detections)}")

        status_str = "[PASS]" if case_passed else "[FAIL]"
        if not case_passed:
            all_pass = False

        msg = f"{status_str} {filename:<35} | Detections: {len(detections):<2}"
        if failure_reasons:
            msg += f" | Reason: {'; '.join(failure_reasons)}"
        print(msg)

        results[filename] = {
            "passed": case_passed,
            "detections": detections,
            "failure_reasons": failure_reasons,
        }

    return all_pass, results


def run_test_a2(pipeline, verbose: bool = True) -> Tuple[bool, Dict[str, Any]]:
    """A2: Test on locked N=730 benchmark."""
    manifest_path = PROJECT_ROOT / "data" / "rescue_benchmark" / "manifest.json"
    if not manifest_path.exists():
        print(f"[FAIL] Missing {manifest_path}")
        return False, {}

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    records = manifest["records"]
    img_dir = PROJECT_ROOT / "data" / "rescue_benchmark" / "images"

    print("\n" + "=" * 70)
    print(f" ACCEPTANCE TEST A2: LOCKED BENCHMARK (N = {len(records)})")
    print("=" * 70)

    # Metrics accumulators
    img_lvl_tp = 0
    img_lvl_tn = 0
    img_lvl_fp = 0
    img_lvl_fn = 0
    img_lvl_correct = []

    clutter_total = 0
    clutter_with_offroad_box = 0

    nonroad_total = 0
    nonroad_rejected = 0

    obj_tp = 0
    obj_fp = 0
    obj_fn = 0

    t0 = time.perf_counter()

    for idx, rec in enumerate(records):
        fn = rec["filename"]
        cat = rec["category"]
        img_path = img_dir / fn
        if not img_path.exists():
            continue

        img_rgb = load_image_rgb(img_path)
        h, w = img_rgb.shape[:2]

        # Extract GT boxes
        gt_boxes = []
        for g in rec.get("gt_boxes", []):
            cx, cy, bw, bh = g["cx"] * w, g["cy"] * h, g["w"] * w, g["h"] * h
            x1 = max(0.0, cx - bw / 2.0)
            y1 = max(0.0, cy - bh / 2.0)
            x2 = min(float(w), cx + bw / 2.0)
            y2 = min(float(h), cy + bh / 2.0)
            gt_boxes.append({
                "box": [x1, y1, x2, y2],
                "matched": False
            })

        is_road, reason, dets = pipeline.predict(img_rgb, preset="balanced")

        is_gt_positive = (len(gt_boxes) > 0)
        is_pred_positive = (is_road and len(dets) > 0)

        # Image-level evaluation
        if is_gt_positive and is_pred_positive:
            img_lvl_tp += 1
            img_lvl_correct.append(1)
        elif not is_gt_positive and not is_pred_positive:
            img_lvl_tn += 1
            img_lvl_correct.append(1)
        elif not is_gt_positive and is_pred_positive:
            img_lvl_fp += 1
            img_lvl_correct.append(0)
        elif is_gt_positive and not is_pred_positive:
            img_lvl_fn += 1
            img_lvl_correct.append(0)

        # Non-road evaluation
        if cat == "non_road":
            nonroad_total += 1
            if not is_road or len(dets) == 0:
                nonroad_rejected += 1

        # Clutter evaluation (box on person/vehicle/sign/sky/off-road)
        if cat == "clutter_road":
            clutter_total += 1
            # In clutter images without ground truth damage, any detected box is an off-road / clutter false alarm
            if len(gt_boxes) == 0 and len(dets) > 0:
                clutter_with_offroad_box += 1

        # Object-level matching @ IoU 0.50
        sorted_dets = sorted(dets, key=lambda x: x["conf"], reverse=True)
        for p in sorted_dets:
            p_box = p["box"]
            best_iou = 0.0
            best_idx = -1
            for g_idx, g in enumerate(gt_boxes):
                if g["matched"]:
                    continue
                iou = compute_iou(p_box, g["box"])
                if iou > best_iou:
                    best_iou = iou
                    best_idx = g_idx
            if best_iou >= 0.5 and best_idx >= 0:
                gt_boxes[best_idx]["matched"] = True
                obj_tp += 1
            else:
                obj_fp += 1

        for g in gt_boxes:
            if not g["matched"]:
                obj_fn += 1

        if (idx + 1) % 150 == 0 or idx == len(records) - 1:
            print(f"  Processed {idx + 1}/{len(records)} benchmark images...")

    elapsed = time.perf_counter() - t0

    # Metrics computation
    total_imgs = img_lvl_tp + img_lvl_tn + img_lvl_fp + img_lvl_fn
    damage_acc = (img_lvl_tp + img_lvl_tn) / total_imgs if total_imgs > 0 else 0.0
    acc_ci = bootstrap_ci(img_lvl_correct)

    clutter_fa_rate = (clutter_with_offroad_box / max(1, clutter_total)) * 100.0
    nonroad_rejection_rate = (nonroad_rejected / max(1, nonroad_total)) * 100.0

    obj_prec = obj_tp / (obj_tp + obj_fp) if (obj_tp + obj_fp) > 0 else 0.0
    obj_rec = obj_tp / (obj_tp + obj_fn) if (obj_tp + obj_fn) > 0 else 0.0
    obj_f1 = (2 * obj_prec * obj_rec) / (obj_prec + obj_rec) if (obj_prec + obj_rec) > 0 else 0.0

    print("\n--- BENCHMARK A2 METRICS REPORT ---")
    p1 = damage_acc >= 0.90
    print(f"[{'PASS' if p1 else 'FAIL'}] A2.1 Damage Yes/No Accuracy: {damage_acc * 100:.2f}% (95% CI: [{acc_ci[0] * 100:.1f}%, {acc_ci[1] * 100:.1f}%]) | Target: >= 90.0%")

    p2 = clutter_fa_rate <= 2.0
    print(f"[{'PASS' if p2 else 'FAIL'}] A2.2 Clutter Off-Road False Alarm Rate: {clutter_fa_rate:.2f}% ({clutter_with_offroad_box}/{clutter_total}) | Target: <= 2.0%")

    p3 = nonroad_rejection_rate >= 95.0
    print(f"[{'PASS' if p3 else 'FAIL'}] A2.3 Non-Road Rejection Rate: {nonroad_rejection_rate:.2f}% ({nonroad_rejected}/{nonroad_total}) | Target: >= 95.0%")

    p4 = obj_f1 >= 0.80
    print(f"[{'PASS' if p4 else 'FAIL'}] A2.4 Object-Level F1 @ IoU 0.5: {obj_f1:.4f} (Prec: {obj_prec:.4f}, Rec: {obj_rec:.4f}) | Target: >= 0.8000")

    print(f"  Benchmark Evaluation Runtime: {elapsed:.1f}s ({elapsed / len(records) * 1000.0:.1f} ms/img)")

    all_pass = p1 and p2 and p3 and p4
    return all_pass, {
        "damage_accuracy": damage_acc,
        "damage_accuracy_ci": acc_ci,
        "clutter_false_alarm_rate": clutter_fa_rate,
        "nonroad_rejection_rate": nonroad_rejection_rate,
        "object_precision": obj_prec,
        "object_recall": obj_rec,
        "object_f1": obj_f1,
    }


def main():
    parser = argparse.ArgumentParser(description="Automated Acceptance Test Suite")
    parser.add_argument("--pipeline", choices=["old", "ml2"], default="old", help="Pipeline under test")
    parser.add_argument("--test", choices=["all", "a1", "a2"], default="all", help="Which acceptance test to run")
    args = parser.parse_args()

    print(f"\n[ACCEPTANCE SUITE] Loading pipeline: {args.pipeline}")
    pipeline = get_pipeline(args.pipeline)

    a1_ok = True
    a2_ok = True

    if args.test in ("all", "a1"):
        a1_ok, _ = run_test_a1(pipeline)

    if args.test in ("all", "a2"):
        a2_ok, _ = run_test_a2(pipeline)

    overall_ok = a1_ok and a2_ok
    print("\n" + "=" * 70)
    print(f" ACCEPTANCE SUITE FINAL RESULT: {'PASS' if overall_ok else 'FAIL'}")
    print("=" * 70)

    sys.exit(0 if overall_ok else 1)


if __name__ == "__main__":
    main()
