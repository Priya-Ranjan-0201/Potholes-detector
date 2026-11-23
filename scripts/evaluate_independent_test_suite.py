"""Evaluate YOLO11n on an Independent, Completely Unseen Real-World Test Dataset.

Curates 100 unseen images:
1. Group 1: 40 Unseen Indian Road Images (RDD2022 India, untouched indices)
2. Group 2: 20 International Road Distress Images (Japan & Norway)
3. Group 3: 20 Pristine / Clean Road Images (Zero ground truth defects)
4. Group 4: 18 Challenging Evaluation Cases (User Uploaded Images + eval_failures)

Runs inference via ML2DetectorPipeline, measures IoU, Precision, Recall, FPR,
and generates forensic visual overlays for qualitative inspection.
"""

from __future__ import annotations

import concurrent.futures
import glob
import json
import os
from pathlib import Path
import random
import sys
import time
import urllib.request
import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml2.pipeline.detector import ML2DetectorPipeline, CLASS_NAMES

TEST_DIR = PROJECT_ROOT / "data" / "independent_test_dataset"
IMG_DIR = TEST_DIR / "images"
LBL_DIR = TEST_DIR / "labels"
VIS_DIR = TEST_DIR / "visualizations"

for d in [IMG_DIR, LBL_DIR, VIS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Collect existing trained filenames to ensure 100% DISJOINT evaluation
existing_train_files = set()
for p in (PROJECT_ROOT / "data" / "large_real_world_dataset" / "images").glob("**/*.jpg"):
    existing_train_files.add(p.name)
    # Strip prefix if added
    if p.name.startswith("rdd_"):
        existing_train_files.add(p.name[4:])
    if p.name.startswith("neg_"):
        existing_train_files.add(p.name[4:])

print(f"Loaded {len(existing_train_files)} existing training image filenames to strictly avoid.")


def remap_rdd_label(raw_text: str) -> str:
    remap = {0: 1, 1: 2, 2: 3, 3: 0}
    out = []
    for line in raw_text.splitlines():
        parts = line.strip().split()
        if len(parts) >= 5:
            try:
                cid = int(parts[0])
                new_cid = remap.get(cid, 0)
                out.append(f"{new_cid} " + " ".join(parts[1:5]))
            except ValueError:
                pass
    return "\n".join(out)


def download_unseen_group(shard: str, target_count: int, prefix: str, require_defects: bool = True) -> list[dict]:
    api_url = f"https://huggingface.co/api/datasets/dronefreak/RDD2022/tree/main/data/labels/train/{shard}"
    req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
    candidates = []
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            items = json.loads(r.read().decode("utf-8"))
            for it in items:
                stem = Path(it["path"]).stem
                img_name = f"{stem}.jpg"
                if img_name in existing_train_files or f"rdd_{img_name}" in existing_train_files:
                    continue
                size = it.get("size", 0)
                if require_defects and size > 0:
                    candidates.append((shard, it["path"]))
                elif not require_defects and size == 0:
                    candidates.append((shard, it["path"]))
    except Exception as e:
        print(f"Error listing {shard}: {e}")
        return []

    random.seed(1337)
    random.shuffle(candidates)
    selected = candidates[:target_count]
    print(f"  Fetching {len(selected)} unseen images from {shard} (require_defects={require_defects})...")

    results = []

    def fetch(item):
        sh, lbl_path = item
        stem = Path(lbl_path).stem
        img_name = f"{stem}.jpg"
        lbl_url = f"https://huggingface.co/datasets/dronefreak/RDD2022/raw/main/{lbl_path}"
        img_url = f"https://huggingface.co/datasets/dronefreak/RDD2022/resolve/main/data/images/train/{sh}/{img_name}"

        try:
            raw_lbl = ""
            if require_defects:
                req_lbl = urllib.request.Request(lbl_url, headers={"User-Agent": "Mozilla/5.0"})
                raw_lbl = urllib.request.urlopen(req_lbl, timeout=10).read().decode("utf-8")
                remapped = remap_rdd_label(raw_lbl)
            else:
                remapped = ""

            req_img = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
            img_bytes = urllib.request.urlopen(req_img, timeout=12).read()

            out_img_path = IMG_DIR / f"{prefix}_{img_name}"
            out_lbl_path = LBL_DIR / f"{prefix}_{stem}.txt"

            with open(out_img_path, "wb") as f:
                f.write(img_bytes)
            with open(out_lbl_path, "w", encoding="utf-8") as f:
                f.write(remapped)

            return {
                "filename": out_img_path.name,
                "label_path": str(out_lbl_path),
                "has_defects": require_defects and len(remapped.strip()) > 0,
            }
        except Exception as err:
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futs = [ex.submit(fetch, c) for c in selected]
        for f in concurrent.futures.as_completed(futs):
            res = f.result()
            if res is not None:
                results.append(res)

    return results


def curate_test_suite():
    print("=== Curating Independent Test Suite ===")
    records = []

    # 1. 40 Unseen Indian road images with defects
    r1 = download_unseen_group("shard_003", 40, "unseen_ind", require_defects=True)
    records.extend(r1)

    # 2. 20 International distress images (Norway)
    r2 = download_unseen_group("shard_007", 20, "unseen_intl", require_defects=True)
    records.extend(r2)

    # 3. 20 Pristine clean road images (Zero defects)
    r3 = download_unseen_group("shard_002", 20, "pristine_clean", require_defects=False)
    records.extend(r3)

    # 4. User-Uploaded & Failure Gallery Images
    user_media_dir = Path("C:/Users/PRIYE RANJAN/.gemini/antigravity/brain/8f5a66d6-4840-4b54-85df-b739995e94a1/.user_uploaded")
    if user_media_dir.exists():
        for p in user_media_dir.glob("*.*"):
            dest = IMG_DIR / f"user_{p.name}"
            import shutil
            shutil.copy2(p, dest)
            lbl = LBL_DIR / f"user_{p.stem}.txt"
            lbl.write_text("")  # will be qualitatively evaluated
            records.append({"filename": dest.name, "label_path": str(lbl), "has_defects": True, "source": "user_uploaded"})

    for p in (PROJECT_ROOT / "eval_failures").glob("*.*"):
        if p.suffix.lower() in [".jpg", ".png", ".avif"]:
            dest = IMG_DIR / f"eval_{p.name}"
            import shutil
            shutil.copy2(p, dest)
            lbl = LBL_DIR / f"eval_{p.stem}.txt"
            lbl.write_text("")
            records.append({"filename": dest.name, "label_path": str(lbl), "has_defects": True, "source": "eval_failures"})

    print(f"Total curated test images: {len(records)}")
    return records


def compute_iou(boxA, boxB):
    # box: [x1, y1, x2, y2]
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interW = max(0.0, xB - xA)
    interH = max(0.0, yB - yA)
    interArea = interW * interH
    boxAArea = max(1.0, (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxBArea = max(1.0, (boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))
    return interArea / float(boxAArea + boxBArea - interArea)


def parse_ground_truth_boxes(lbl_path: Path, w: int, h: int) -> list[dict]:
    if not lbl_path.exists():
        return []
    boxes = []
    text = lbl_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        parts = line.strip().split()
        if len(parts) >= 5:
            try:
                cid = int(parts[0])
                cx, cy, bw, bh = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                x1 = (cx - bw / 2.0) * w
                y1 = (cy - bh / 2.0) * h
                x2 = (cx + bw / 2.0) * w
                y2 = (cy + bh / 2.0) * h
                boxes.append({
                    "class_id": cid,
                    "label": CLASS_NAMES.get(cid, "POTHOLE"),
                    "box": [x1, y1, x2, y2]
                })
            except ValueError:
                pass
    return boxes


def run_full_evaluation():
    curate_test_suite()

    pipeline = ML2DetectorPipeline()
    all_images = sorted(list(IMG_DIR.glob("*.*")))
    print(f"\n=== Running Full Model Test on {len(all_images)} Images ===")

    stats = {
        "total_images": len(all_images),
        "total_detections": 0,
        "clean_images_tested": 0,
        "clean_images_with_false_positives": 0,
        "clean_total_false_positive_boxes": 0,
        "damaged_images_tested": 0,
        "damaged_images_detected": 0,
        "true_positives_iou25": 0,
        "false_positives_iou25": 0,
        "false_negatives_iou25": 0,
        "border_artifacts": 0,
        "latencies_ms": [],
        "per_class": {
            "pothole": {"gt": 0, "tp": 0, "fp": 0, "fn": 0},
            "crack_longitudinal": {"gt": 0, "tp": 0, "fp": 0, "fn": 0},
            "crack_transverse": {"gt": 0, "tp": 0, "fp": 0, "fn": 0},
            "crack_alligator": {"gt": 0, "tp": 0, "fp": 0, "fn": 0},
        },
        "qualitative_cases": []
    }

    for idx, img_path in enumerate(all_images):
        lbl_path = LBL_DIR / f"{img_path.stem}.txt"
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        h, w = img.shape[:2]
        gt_boxes = parse_ground_truth_boxes(lbl_path, w, h)
        is_clean = len(gt_boxes) == 0 and ("pristine" in img_path.name or "clean" in img_path.name)

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        t0 = time.perf_counter()
        is_road, reason, dets = pipeline.predict(rgb, preset="balanced")
        lat_ms = (time.perf_counter() - t0) * 1000.0
        stats["latencies_ms"].append(lat_ms)

        stats["total_detections"] += len(dets)

        # Border artifact check
        for d in dets:
            bx = d["box"]
            cx = (bx[0] + bx[2]) / 2.0
            if (bx[0] <= 3 or bx[2] >= w - 3) and (cx < 0.04 * w or cx > 0.96 * w):
                stats["border_artifacts"] += 1

        if is_clean:
            stats["clean_images_tested"] += 1
            if len(dets) > 0:
                stats["clean_images_with_false_positives"] += 1
                stats["clean_total_false_positive_boxes"] += len(dets)
        else:
            stats["damaged_images_tested"] += 1
            if len(dets) > 0:
                stats["damaged_images_detected"] += 1

        # Match detections against GT
        matched_gt = set()
        for d in dets:
            pred_box = d["box"]
            pred_cls = d["class_id"]
            cls_name = CLASS_NAMES.get(pred_cls, "pothole").lower()
            
            best_iou = 0.0
            best_gt_idx = -1
            for g_i, gt in enumerate(gt_boxes):
                if g_i in matched_gt:
                    continue
                iou = compute_iou(pred_box, gt["box"])
                if iou > best_iou:
                    best_iou = iou
                    best_gt_idx = g_i

            if best_iou >= 0.25:
                stats["true_positives_iou25"] += 1
                matched_gt.add(best_gt_idx)
                if cls_name in stats["per_class"]:
                    stats["per_class"][cls_name]["tp"] += 1
            else:
                stats["false_positives_iou25"] += 1
                if cls_name in stats["per_class"]:
                    stats["per_class"][cls_name]["fp"] += 1

        for g_i, gt in enumerate(gt_boxes):
            gt_cls_name = CLASS_NAMES.get(gt["class_id"], "pothole").lower()
            if gt_cls_name in stats["per_class"]:
                stats["per_class"][gt_cls_name]["gt"] += 1
            if g_i not in matched_gt:
                stats["false_negatives_iou25"] += 1
                if gt_cls_name in stats["per_class"]:
                    stats["per_class"][gt_cls_name]["fn"] += 1

        # Create visualization for key samples (user uploaded, eval failures, or first 10 unseen)
        should_render = (
            "user_" in img_path.name
            or "eval_" in img_path.name
            or idx < 12
            or (is_clean and len(dets) > 0)
        )
        if should_render:
            vis = img.copy()
            # Draw GT in Blue
            for gt in gt_boxes:
                gx1, gy1, gx2, gy2 = [int(v) for v in gt["box"]]
                cv2.rectangle(vis, (gx1, gy1), (gx2, gy2), (255, 120, 0), 2)
                cv2.putText(vis, f"GT: {gt['label']}", (gx1, max(15, gy1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 120, 0), 1)

            # Draw Preds in Green (or Red if border)
            for d in dets:
                px1, py1, px2, py2 = [int(v) for v in d["box"]]
                cv2.rectangle(vis, (px1, py1), (px2, py2), (0, 255, 0), 2)
                lbl_text = f"{d['label']} {d['conf']:.2f}"
                cv2.putText(vis, lbl_text, (px1, max(25, py1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            header = f"Valid: {is_road} | Dets: {len(dets)} | GT: {len(gt_boxes)}"
            cv2.rectangle(vis, (0, 0), (w, 35), (0, 0, 0), -1)
            cv2.putText(vis, header, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            out_vis_path = VIS_DIR / f"vis_{img_path.stem}.jpg"
            cv2.imwrite(str(out_vis_path), vis)

            stats["qualitative_cases"].append({
                "image": img_path.name,
                "vis_path": str(out_vis_path),
                "is_road": is_road,
                "reason": reason,
                "detections_count": len(dets),
                "gt_count": len(gt_boxes),
                "detections": [
                    {"label": d["label"], "conf": round(float(d["conf"]), 3), "box": [round(float(v), 1) for v in d["box"]]}
                    for d in dets
                ]
            })

    # Summary metrics calculation
    tp = stats["true_positives_iou25"]
    fp = stats["false_positives_iou25"]
    fn = stats["false_negatives_iou25"]

    prec = tp / max(1, tp + fp)
    rec = tp / max(1, tp + fn)
    f1 = 2 * (prec * rec) / max(1e-6, prec + rec)

    avg_lat = float(np.mean(stats["latencies_ms"])) if stats["latencies_ms"] else 0.0

    stats["summary"] = {
        "precision_iou25": round(prec, 4),
        "recall_iou25": round(rec, 4),
        "f1_score_iou25": round(f1, 4),
        "clean_road_fpr": round(stats["clean_images_with_false_positives"] / max(1, stats["clean_images_tested"]), 4),
        "damaged_detection_rate": round(stats["damaged_images_detected"] / max(1, stats["damaged_images_tested"]), 4),
        "average_latency_ms": round(avg_lat, 2),
        "total_border_artifacts": stats["border_artifacts"],
    }

    report_json = TEST_DIR / "evaluation_report.json"
    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print("\n================ EVALUATION SUMMARY ================")
    print(f"Total Test Images:               {stats['total_images']}")
    print(f"Precision (@IoU 0.25):           {prec*100:.2f}%")
    print(f"Recall (@IoU 0.25):              {rec*100:.2f}%")
    print(f"F1-Score:                        {f1*100:.2f}%")
    print(f"Clean Road False Positive Rate:  {stats['summary']['clean_road_fpr']*100:.2f}%")
    print(f"Damaged Road Detection Rate:     {stats['summary']['damaged_detection_rate']*100:.2f}%")
    print(f"Total Border Hallucinations:     {stats['border_artifacts']}")
    print(f"Average CPU Latency per Image:   {avg_lat:.1f} ms")
    print(f"Report saved to:                 {report_json}")
    print(f"Visualizations saved to:         {VIS_DIR}")
    print("====================================================")


if __name__ == "__main__":
    run_full_evaluation()
