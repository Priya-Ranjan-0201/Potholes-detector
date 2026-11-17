"""Comprehensive baseline evaluation of ScamRoad on the locked rescue benchmark (N=730).

Evaluates:
1. YOLO11n alone (runs/export/best.onnx)
2. YOLOv8n crack specialist alone (runs/baselines/yolov8n/weights/best.onnx)
3. Current full pipeline (backend/app/api/v1/infer.py: check_image_usability + run_pipeline_on_image)

Computes:
- Precision, Recall, F1 @ IoU 0.5 overall and per class with 95% bootstrap confidence intervals
- Clutter false alarm rate (% of clutter images with at least one false alarm)
- Clean road false alarm rate (% of clean images with false alarms)
- Non-road rejection and error rate (% of non-road images generating false defect detections)
- Top 20 worst failures with bounding box overlays saved in docs/forensics/rescue_baseline/
"""

import os
import sys
import json
import time
import numpy as np
import cv2

# Add project root to sys.path
sys.path.insert(0, os.path.abspath("."))

from edge.agent.infer import EdgeInferenceEngine
from backend.app.api.v1.infer import check_image_usability, run_pipeline_on_image

CLASS_NAMES = {
    0: "pothole",
    1: "crack_longitudinal",
    2: "crack_transverse",
    3: "crack_alligator",
}

LABEL_MAP = {
    "POTHOLE": 0,
    "CRACK_LONG": 1,
    "CRACK_LONGITUDINAL": 1,
    "LONGITUDINAL": 1,
    "CRACK_TRANS": 2,
    "CRACK_TRANSVERSE": 2,
    "TRANSVERSE": 2,
    "CRACK_ALLIGATOR": 3,
    "ALLIGATOR": 3,
}


def compute_iou(boxA, boxB):
    # box: [x1, y1, x2, y2]
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    inter = max(0.0, xB - xA) * max(0.0, yB - yA)
    areaA = max(0.0, boxA[2] - boxA[0]) * max(0.0, boxA[3] - boxA[1])
    areaB = max(0.0, boxB[2] - boxB[0]) * max(0.0, boxB[3] - boxB[1])
    union = areaA + areaB - inter
    return inter / union if union > 0 else 0.0


def bootstrap_ci(metric_samples, n_resamples=1000, alpha=0.05):
    if len(metric_samples) == 0:
        return 0.0, 0.0
    boot_means = []
    rng = np.random.default_rng(42)
    n = len(metric_samples)
    for _ in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        boot_means.append(np.mean(metric_samples[idx]))
    low = np.percentile(boot_means, (alpha / 2.0) * 100)
    high = np.percentile(boot_means, (1.0 - alpha / 2.0) * 100)
    return round(float(low), 4), round(float(high), 4)


def evaluate_system(name, predict_fn, benchmark_records, img_dir):
    print(f"\n--- Evaluating System: {name} ---")
    start_time = time.time()
    
    # Store per-image details
    all_tp = 0
    all_fp = 0
    all_fn = 0
    
    per_class_tp = {c: 0 for c in range(4)}
    per_class_fp = {c: 0 for c in range(4)}
    per_class_fn = {c: 0 for c in range(4)}
    
    clutter_total = 0
    clutter_fa_images = 0
    
    clean_total = 0
    clean_fa_images = 0
    
    nonroad_total = 0
    nonroad_rejected = 0
    nonroad_with_boxes = 0
    
    failures = []
    image_f1_samples = []

    for idx, rec in enumerate(benchmark_records):
        fn = rec["filename"]
        cat = rec["category"]
        img_path = os.path.join(img_dir, fn)
        img = cv2.imread(img_path)
        if img is None:
            continue
        h, w = img.shape[:2]
        
        # Ground truth boxes in pixels: [x1, y1, x2, y2, class_id]
        gt_boxes = []
        for g in rec.get("gt_boxes", []):
            cx, cy, bw, bh = g["cx"] * w, g["cy"] * h, g["w"] * w, g["h"] * h
            x1 = max(0.0, cx - bw / 2.0)
            y1 = max(0.0, cy - bh / 2.0)
            x2 = min(float(w), cx + bw / 2.0)
            y2 = min(float(h), cy + bh / 2.0)
            gt_boxes.append({
                "box": [x1, y1, x2, y2],
                "class_id": int(g["class_id"]),
                "matched": False
            })
            
        # Run prediction
        preds, is_rejected, rejection_reason = predict_fn(img)
        
        # Non-road evaluation
        if cat == "non_road":
            nonroad_total += 1
            if is_rejected:
                nonroad_rejected += 1
            elif len(preds) > 0:
                nonroad_with_boxes += 1
                # Severe failure: non-road got defect boxes
                failures.append({
                    "filename": fn,
                    "category": cat,
                    "type": "non_road_false_alarm",
                    "severity_score": 100.0,
                    "reason": f"Non-road image produced {len(preds)} detections (max conf: {max(p['conf'] for p in preds):.3f})",
                    "preds": preds,
                    "gt": gt_boxes,
                    "img_path": img_path
                })
            continue

        # Clutter evaluation
        if cat == "clutter_road":
            clutter_total += 1
            if len(preds) > 0:
                # If image had no GT defects, any pred is a false alarm
                if len(gt_boxes) == 0:
                    clutter_fa_images += 1
                    failures.append({
                        "filename": fn,
                        "category": cat,
                        "type": "clutter_false_alarm",
                        "severity_score": float(np.mean([p["conf"] for p in preds])) * 100.0,
                        "reason": f"Clutter scene produced {len(preds)} off-road/spurious boxes",
                        "preds": preds,
                        "gt": gt_boxes,
                        "img_path": img_path
                    })
                
        # Clean road evaluation
        if cat == "clean_road":
            clean_total += 1
            if len(preds) > 0:
                clean_fa_images += 1
                failures.append({
                    "filename": fn,
                    "category": cat,
                    "type": "clean_road_false_alarm",
                    "severity_score": float(np.mean([p["conf"] for p in preds])) * 100.0,
                    "reason": f"Clean pavement produced {len(preds)} phantom detections",
                    "preds": preds,
                    "gt": gt_boxes,
                    "img_path": img_path
                })

        # Match predictions to GT @ IoU 0.5
        # Sort predictions descending by confidence
        sorted_preds = sorted(preds, key=lambda x: x["conf"], reverse=True)
        img_tp = 0
        img_fp = 0
        
        for p in sorted_preds:
            p_box = p["box"]
            p_cls = p["class_id"]
            best_iou = 0.0
            best_gt_idx = -1
            
            for g_idx, g in enumerate(gt_boxes):
                if g["matched"]:
                    continue
                if g["class_id"] == p_cls:
                    iou = compute_iou(p_box, g["box"])
                    if iou > best_iou:
                        best_iou = iou
                        best_gt_idx = g_idx
                        
            if best_iou >= 0.5 and best_gt_idx >= 0:
                gt_boxes[best_gt_idx]["matched"] = True
                all_tp += 1
                img_tp += 1
                per_class_tp[p_cls] += 1
            else:
                all_fp += 1
                img_fp += 1
                per_class_fp[p_cls] += 1
                
        # Unmatched GT are FN
        img_fn = 0
        for g in gt_boxes:
            if not g["matched"]:
                all_fn += 1
                img_fn += 1
                per_class_fn[g["class_id"]] += 1
                
        # Per-image F1 sample for bootstrap
        denom = (2 * img_tp + img_fp + img_fn)
        img_f1 = (2.0 * img_tp / denom) if denom > 0 else (1.0 if (len(gt_boxes) == 0 and len(preds) == 0) else 0.0)
        image_f1_samples.append(img_f1)
        
        # If massive false negatives on damage image
        if cat == "damage" and img_fn > 0 and img_tp == 0:
            failures.append({
                "filename": fn,
                "category": cat,
                "type": "missed_damage",
                "severity_score": 80.0 + img_fn * 5.0,
                "reason": f"Missed all {img_fn} true defects on road damage image",
                "preds": preds,
                "gt": gt_boxes,
                "img_path": img_path
            })

    total_time = time.time() - start_time
    precision = (all_tp / (all_tp + all_fp)) if (all_tp + all_fp) > 0 else 0.0
    recall = (all_tp / (all_tp + all_fn)) if (all_tp + all_fn) > 0 else 0.0
    f1 = (2.0 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    
    f1_ci_low, f1_ci_high = bootstrap_ci(np.array(image_f1_samples))
    
    class_results = {}
    for c in range(4):
        c_name = CLASS_NAMES[c]
        c_tp = per_class_tp[c]
        c_fp = per_class_fp[c]
        c_fn = per_class_fn[c]
        c_prec = (c_tp / (c_tp + c_fp)) if (c_tp + c_fp) > 0 else 0.0
        c_rec = (c_tp / (c_tp + c_fn)) if (c_tp + c_fn) > 0 else 0.0
        c_f1 = (2.0 * c_prec * c_rec / (c_prec + c_rec)) if (c_prec + c_rec) > 0 else 0.0
        class_results[c_name] = {
            "precision": round(c_prec, 4),
            "recall": round(c_rec, 4),
            "f1": round(c_f1, 4),
            "tp": c_tp,
            "fp": c_fp,
            "fn": c_fn
        }

    clutter_fa_rate = (clutter_fa_images / max(1, clutter_total)) * 100.0
    clean_fa_rate = (clean_fa_images / max(1, clean_total)) * 100.0
    nonroad_rejection_rate = (nonroad_rejected / max(1, nonroad_total)) * 100.0
    nonroad_error_rate = (nonroad_with_boxes / max(1, nonroad_total)) * 100.0

    print(f"Results for {name}:")
    print(f"  Overall Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f} (95% CI: [{f1_ci_low:.4f}, {f1_ci_high:.4f}])")
    print(f"  Clutter False Alarm Rate: {clutter_fa_rate:.1f}% ({clutter_fa_images}/{clutter_total})")
    print(f"  Clean Road False Alarm Rate: {clean_fa_rate:.1f}% ({clean_fa_images}/{clean_total})")
    print(f"  Non-Road Rejection Rate: {nonroad_rejection_rate:.1f}% ({nonroad_rejected}/{nonroad_total})")
    print(f"  Non-Road Error Rate: {nonroad_error_rate:.1f}% ({nonroad_with_boxes}/{nonroad_total})")
    print(f"  Total inference time: {total_time:.2f}s ({total_time / len(benchmark_records) * 1000:.1f} ms/img)")

    return {
        "system": name,
        "overall": {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "f1_ci_95": [f1_ci_low, f1_ci_high],
            "total_tp": all_tp,
            "total_fp": all_fp,
            "total_fn": all_fn
        },
        "per_class": class_results,
        "clutter_false_alarm_rate_pct": round(clutter_fa_rate, 2),
        "clean_road_false_alarm_rate_pct": round(clean_fa_rate, 2),
        "non_road_rejection_rate_pct": round(nonroad_rejection_rate, 2),
        "non_road_error_rate_pct": round(nonroad_error_rate, 2),
        "timing": {
            "total_seconds": round(total_time, 2),
            "mean_ms_per_image": round(total_time / len(benchmark_records) * 1000, 2)
        },
        "failures": failures
    }


def main():
    bench_dir = "data/rescue_benchmark"
    img_dir = os.path.join(bench_dir, "images")
    manifest_p = os.path.join(bench_dir, "manifest.json")
    with open(manifest_p, "r") as f:
        manifest = json.load(f)
    records = manifest["records"]
    print(f"Loaded {len(records)} benchmark records.")

    # 1. YOLO11n Alone
    yolo11_eng = EdgeInferenceEngine("runs/export/best.onnx", conf_threshold=0.20, iou_threshold=0.35)
    def predict_yolo11n(img):
        raw = yolo11_eng.predict(img)
        preds = []
        for r in raw:
            preds.append({
                "box": list(r.bbox_xyxy),
                "conf": float(r.confidence),
                "class_id": int(r.class_id),
                "label": r.class_name
            })
        return preds, False, ""

    res_yolo11n = evaluate_system("YOLO11n-Alone (runs/export/best.onnx)", predict_yolo11n, records, img_dir)

    # 2. YOLOv8n Crack Specialist Alone
    yolov8_eng = EdgeInferenceEngine("runs/baselines/yolov8n/weights/best.onnx", conf_threshold=0.20, iou_threshold=0.35)
    def predict_yolov8n(img):
        raw = yolov8_eng.predict(img)
        preds = []
        for r in raw:
            preds.append({
                "box": list(r.bbox_xyxy),
                "conf": float(r.confidence),
                "class_id": int(r.class_id),
                "label": r.class_name
            })
        return preds, False, ""

    res_yolov8n = evaluate_system("YOLOv8n-Crack-Specialist (runs/baselines/yolov8n/weights/best.onnx)", predict_yolov8n, records, img_dir)

    # 3. Current Pipeline (check_image_usability + run_pipeline_on_image)
    def predict_pipeline(img):
        usable, reason = check_image_usability(img)
        if not usable:
            return [], True, reason
        dets = run_pipeline_on_image(img, conf_thresh=0.20, iou_thresh=0.35, extract_polygons=False)
        h, w = img.shape[:2]
        preds = []
        for d in dets:
            bx = d.box # [x_pct, y_pct, w_pct, h_pct]
            x1 = (bx[0] / 100.0) * w
            y1 = (bx[1] / 100.0) * h
            x2 = x1 + (bx[2] / 100.0) * w
            y2 = y1 + (bx[3] / 100.0) * h
            lbl = d.label.upper()
            cid = LABEL_MAP.get(lbl, 0)
            preds.append({
                "box": [float(x1), float(y1), float(x2), float(y2)],
                "conf": float(d.confidence),
                "class_id": cid,
                "label": d.label
            })
        return preds, False, ""

    res_pipeline = evaluate_system("Current-Full-Pipeline (FastAPI infer.py)", predict_pipeline, records, img_dir)

    # Save comprehensive evaluation results
    os.makedirs("runs/eval", exist_ok=True)
    out_eval_path = "runs/eval/rescue_baseline_results.json"
    with open(out_eval_path, "w") as f:
        json.dump({
            "timestamp": "2026-11-17T16:00:00Z",
            "benchmark_counts": manifest["counts"],
            "systems": [res_yolo11n, res_yolov8n, res_pipeline]
        }, f, indent=2)
    print(f"\nSaved evaluation metrics to: {out_eval_path}")

    # Generate Top 20 Worst Failures Visual Overlays
    # Pull from pipeline failures sorted by severity_score
    pipe_failures = sorted(res_pipeline["failures"], key=lambda x: x["severity_score"], reverse=True)
    forensics_dir = "docs/forensics/rescue_baseline"
    os.makedirs(forensics_dir, exist_ok=True)

    print(f"\nGenerating visual failure overlays in {forensics_dir}...")
    saved_count = 0
    failure_manifest = []

    for idx, f_item in enumerate(pipe_failures[:20]):
        img = cv2.imread(f_item["img_path"])
        if img is None:
            continue
        vis = img.copy()
        h, w = vis.shape[:2]

        # Draw GT boxes in green
        for g in f_item["gt"]:
            gx1, gy1, gx2, gy2 = [int(v) for v in g["box"]]
            c_name = CLASS_NAMES.get(g["class_id"], str(g["class_id"]))
            cv2.rectangle(vis, (gx1, gy1), (gx2, gy2), (0, 255, 0), 2)
            cv2.putText(vis, f"GT:{c_name}", (gx1, max(15, gy1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

        # Draw False Predictions in bright red
        for p in f_item["preds"]:
            px1, py1, px2, py2 = [int(v) for v in p["box"]]
            conf_str = f"{p['conf']:.2f}"
            lbl = p.get("label", str(p["class_id"]))
            cv2.rectangle(vis, (px1, py1), (px2, py2), (0, 0, 255), 2)
            cv2.putText(vis, f"FP:{lbl} {conf_str}", (px1, min(h - 5, py2 + 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1)

        # Add header banner with failure description
        banner = np.zeros((40, w, 3), dtype=np.uint8)
        text = f"FAIL #{idx+1}: {f_item['type']} - {f_item['reason']}"
        cv2.putText(banner, text[:75], (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 255), 1)
        composite = np.vstack([banner, vis])

        out_img_name = f"failure_{idx+1:02d}_{f_item['type']}_{os.path.basename(f_item['filename'])}"
        out_img_path = os.path.join(forensics_dir, out_img_name)
        cv2.imwrite(out_img_path, composite)
        saved_count += 1

        failure_manifest.append({
            "rank": idx + 1,
            "filename": f_item["filename"],
            "type": f_item["type"],
            "reason": f_item["reason"],
            "overlay_path": out_img_path
        })

    with open(os.path.join(forensics_dir, "failures_manifest.json"), "w") as f:
        json.dump(failure_manifest, f, indent=2)

    print(f"Saved {saved_count} failure overlay images to {forensics_dir}.")


if __name__ == "__main__":
    main()
