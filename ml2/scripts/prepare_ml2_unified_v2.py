"""Prepare ML2 Unified Balanced Dataset v2.

Creates an evenly balanced training and validation dataset for road damage detection:
- Classes: 0: POTHOLE, 1: CRACK_LONGITUDINAL, 2: CRACK_TRANSVERSE, 3: CRACK_ALLIGATOR
- Negative regularization: ~30% negative background scenes (clean pavement, wet asphalt, rain, scooters, roadside clutter)
- Hard negative guards: 33 guard negatives from data/guard_set (+ hflips)
- Zero Leakage: Strict SHA-256 verification guaranteeing NO image in data/rescue_benchmark/manifest.json
  or eval_failures/ is included.
"""

from __future__ import annotations

import hashlib
import json
import random
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def augment_sample(
    img: np.ndarray, boxes: List[Tuple[int, float, float, float, float]], aug_type: str
) -> Tuple[np.ndarray, List[Tuple[int, float, float, float, float]]]:
    aug_boxes = []

    if aug_type == "orig":
        return img.copy(), [b for b in boxes]
    elif aug_type == "hflip":
        aug_img = cv2.flip(img, 1)
        for cls_id, cx, cy, bw, bh in boxes:
            aug_boxes.append((cls_id, 1.0 - cx, cy, bw, bh))
        return aug_img, aug_boxes
    elif aug_type == "bright_up":
        aug_img = cv2.convertScaleAbs(img, alpha=1.15, beta=15)
        return aug_img, [b for b in boxes]
    elif aug_type == "bright_down":
        aug_img = cv2.convertScaleAbs(img, alpha=0.85, beta=-15)
        return aug_img, [b for b in boxes]
    elif aug_type == "contrast_up":
        aug_img = cv2.convertScaleAbs(img, alpha=1.25, beta=0)
        return aug_img, [b for b in boxes]
    elif aug_type == "contrast_down":
        aug_img = cv2.convertScaleAbs(img, alpha=0.80, beta=0)
        return aug_img, [b for b in boxes]
    elif aug_type == "hflip_bright_up":
        aug_img = cv2.flip(cv2.convertScaleAbs(img, alpha=1.15, beta=15), 1)
        for cls_id, cx, cy, bw, bh in boxes:
            aug_boxes.append((cls_id, 1.0 - cx, cy, bw, bh))
        return aug_img, aug_boxes
    elif aug_type == "hflip_contrast":
        aug_img = cv2.flip(cv2.convertScaleAbs(img, alpha=1.20, beta=5), 1)
        for cls_id, cx, cy, bw, bh in boxes:
            aug_boxes.append((cls_id, 1.0 - cx, cy, bw, bh))
        return aug_img, aug_boxes
    elif aug_type == "blur":
        aug_img = cv2.GaussianBlur(img, (3, 3), 0)
        return aug_img, [b for b in boxes]
    else:
        return img.copy(), [b for b in boxes]


def parse_labels(lbl_p: Path) -> List[Tuple[int, float, float, float, float]]:
    if not lbl_p.exists():
        return []
    boxes = []
    for line in lbl_p.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) >= 5:
            boxes.append((int(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])))
    return boxes


def write_yolo_sample(img: np.ndarray, boxes: List[Tuple[int, float, float, float, float]], out_img_p: Path, out_lbl_p: Path):
    cv2.imwrite(str(out_img_p), img)
    lines = [f"{b[0]} {b[1]:.6f} {b[2]:.6f} {b[3]:.6f} {b[4]:.6f}" for b in boxes]
    out_lbl_p.write_text("\n".join(lines), encoding="utf-8")


def main():
    print("=================================================================")
    print(" PREPARING ML2 UNIFIED BALANCED DATASET v2")
    print("=================================================================")

    # 1. Build forbidden SHAs
    bench_manifest = PROJECT_ROOT / "data" / "rescue_benchmark" / "manifest.json"
    with open(bench_manifest, "r", encoding="utf-8") as f:
        bench_data = json.load(f)
    bench_shas = set(r["sha256"] for r in bench_data["records"])

    eval_fail_shas = set()
    for p in (PROJECT_ROOT / "eval_failures").glob("*.*"):
        if p.suffix.lower() in (".jpg", ".png", ".avif", ".jpeg"):
            eval_fail_shas.add(compute_sha256(p))

    forbidden_shas = bench_shas | eval_fail_shas
    print(f"Locked benchmark SHAs: {len(bench_shas)}")
    print(f"Eval failures SHAs:    {len(eval_fail_shas)}")
    print(f"Total forbidden SHAs:  {len(forbidden_shas)}")

    # Target directory
    out_dir = PROJECT_ROOT / "data" / "datasets" / "ml2_unified_v2"
    if out_dir.exists():
        shutil.rmtree(out_dir)

    for s in ["train", "val"]:
        (out_dir / "images" / s).mkdir(parents=True, exist_ok=True)
        (out_dir / "labels" / s).mkdir(parents=True, exist_ok=True)

    random.seed(42)

    # 2. Gather candidates from evaluation_set outside forbidden
    eval_img_dir = PROJECT_ROOT / "data" / "evaluation_set" / "images"
    eval_lbl_dir = PROJECT_ROOT / "data" / "evaluation_set" / "labels"

    c3_samples = []
    c2_samples = []
    c1_samples = []
    c0_samples = []
    clean_samples = []

    for img_p in sorted(eval_img_dir.glob("*.*")):
        if img_p.suffix.lower() not in (".jpg", ".png", ".jpeg"):
            continue
        sha = compute_sha256(img_p)
        if sha in forbidden_shas:
            continue

        lbl_p = eval_lbl_dir / f"{img_p.stem}.txt"
        boxes = parse_labels(lbl_p)

        if not boxes:
            clean_samples.append(img_p)
        else:
            classes = set(b[0] for b in boxes)
            if 3 in classes:
                c3_samples.append((img_p, boxes))
            elif 2 in classes:
                c2_samples.append((img_p, boxes))
            elif 1 in classes:
                c1_samples.append((img_p, boxes))
            elif 0 in classes:
                c0_samples.append((img_p, boxes))

    print(f"\nUnfiltered candidates outside benchmark:")
    print(f"  Class 3 (alligator):   {len(c3_samples)} images")
    print(f"  Class 2 (transverse):  {len(c2_samples)} images")
    print(f"  Class 1 (longitudinal):{len(c1_samples)} images")
    print(f"  Class 0 (pothole):     {len(c0_samples)} images")
    print(f"  Clean negatives:       {len(clean_samples)} images")

    # 3. Validation Split Selection (independent, zero overlap with train)
    random.shuffle(c3_samples)
    random.shuffle(c2_samples)
    random.shuffle(c1_samples)
    random.shuffle(c0_samples)
    random.shuffle(clean_samples)

    val_c3 = c3_samples[:3]
    train_c3 = c3_samples[3:]

    val_c2 = c2_samples[:5]
    train_c2 = c2_samples[5:]

    val_c1 = c1_samples[:10]
    train_c1 = c1_samples[10:]

    val_c0 = c0_samples[:30]
    train_c0 = c0_samples[30:280]  # Take 250 pothole images for train

    val_clean = clean_samples[:20]
    train_clean = clean_samples[20:290]  # Take 270 clean images for train (ensuring 25-35% negative regularization)

    print(f"\nValidation set allocation: {len(val_c3)+len(val_c2)+len(val_c1)+len(val_c0)+len(val_clean)} images")
    for img_p, boxes in val_c3 + val_c2 + val_c1 + val_c0:
        img = cv2.imread(str(img_p))
        if img is not None:
            write_yolo_sample(img, boxes, out_dir / "images" / "val" / img_p.name, out_dir / "labels" / "val" / f"{img_p.stem}.txt")

    for img_p in val_clean:
        img = cv2.imread(str(img_p))
        if img is not None:
            write_yolo_sample(img, [], out_dir / "images" / "val" / img_p.name, out_dir / "labels" / "val" / f"{img_p.stem}.txt")

    # 4. Train Split: Process cracks with augmentation to balance classes
    print("\nPopulating train split with augmented cracks and balanced potholes...")
    aug_c3 = ["orig", "hflip", "bright_up", "bright_down", "contrast_up", "contrast_down", "hflip_bright_up", "hflip_contrast", "blur"]
    aug_c2 = ["orig", "hflip", "bright_up", "bright_down", "contrast_up", "hflip_bright_up"]
    aug_c1 = ["orig", "hflip", "bright_up", "contrast_up"]

    for img_p, boxes in train_c3:
        img = cv2.imread(str(img_p))
        if img is None:
            continue
        for aug in aug_c3:
            a_img, a_bx = augment_sample(img, boxes, aug)
            out_fn = f"c3_{img_p.stem}_{aug}.jpg"
            write_yolo_sample(a_img, a_bx, out_dir / "images" / "train" / out_fn, out_dir / "labels" / "train" / f"{Path(out_fn).stem}.txt")

    for img_p, boxes in train_c2:
        img = cv2.imread(str(img_p))
        if img is None:
            continue
        for aug in aug_c2:
            a_img, a_bx = augment_sample(img, boxes, aug)
            out_fn = f"c2_{img_p.stem}_{aug}.jpg"
            write_yolo_sample(a_img, a_bx, out_dir / "images" / "train" / out_fn, out_dir / "labels" / "train" / f"{Path(out_fn).stem}.txt")

    for img_p, boxes in train_c1:
        img = cv2.imread(str(img_p))
        if img is None:
            continue
        for aug in aug_c1:
            a_img, a_bx = augment_sample(img, boxes, aug)
            out_fn = f"c1_{img_p.stem}_{aug}.jpg"
            write_yolo_sample(a_img, a_bx, out_dir / "images" / "train" / out_fn, out_dir / "labels" / "train" / f"{Path(out_fn).stem}.txt")

    # Potholes (train_c0): take original + hflip for half
    for idx, (img_p, boxes) in enumerate(train_c0):
        img = cv2.imread(str(img_p))
        if img is None:
            continue
        out_fn = f"c0_{img_p.stem}_orig.jpg"
        write_yolo_sample(img, boxes, out_dir / "images" / "train" / out_fn, out_dir / "labels" / "train" / f"{Path(out_fn).stem}.txt")
        if idx % 2 == 0:
            a_img, a_bx = augment_sample(img, boxes, "hflip")
            out_fn_flip = f"c0_{img_p.stem}_hflip.jpg"
            write_yolo_sample(a_img, a_bx, out_dir / "images" / "train" / out_fn_flip, out_dir / "labels" / "train" / f"{Path(out_fn_flip).stem}.txt")

    # Clean pavement negatives (train_clean)
    for img_p in train_clean:
        img = cv2.imread(str(img_p))
        if img is None:
            continue
        out_fn = f"clean_{img_p.stem}.jpg"
        write_yolo_sample(img, [], out_dir / "images" / "train" / out_fn, out_dir / "labels" / "train" / f"{Path(out_fn).stem}.txt")

    # Hard negative guards from data/guard_set
    guard_dir = PROJECT_ROOT / "data" / "guard_set" / "images"
    guard_count = 0
    for img_p in guard_dir.glob("*.*"):
        if img_p.suffix.lower() not in (".jpg", ".png", ".jpeg"):
            continue
        sha = compute_sha256(img_p)
        if sha in forbidden_shas:
            continue
        img = cv2.imread(str(img_p))
        if img is None:
            continue
        # Add original and hflip
        out_fn1 = f"guard_{img_p.stem}_orig.jpg"
        out_fn2 = f"guard_{img_p.stem}_hflip.jpg"
        write_yolo_sample(img, [], out_dir / "images" / "train" / out_fn1, out_dir / "labels" / "train" / f"{Path(out_fn1).stem}.txt")
        flip_img = cv2.flip(img, 1)
        write_yolo_sample(flip_img, [], out_dir / "images" / "train" / out_fn2, out_dir / "labels" / "train" / f"{Path(out_fn2).stem}.txt")
        guard_count += 2

    print(f"Added {guard_count} hard guard negative samples (wet asphalt, rain, scooters, roadside clutter).")

    # 5. Write dataset.yaml
    yaml_content = f"""path: {out_dir.as_posix()}
train: images/train
val: images/val
names:
  0: POTHOLE
  1: CRACK_LONGITUDINAL
  2: CRACK_TRANSVERSE
  3: CRACK_ALLIGATOR
"""
    yaml_path = out_dir / "dataset.yaml"
    yaml_path.write_text(yaml_content, encoding="utf-8")
    print(f"Dataset YAML written to {yaml_path}")

    # 6. Final Verification and Distribution Statistics
    print("\n--- FINAL DATASET STATISTICS & VERIFICATION ---")
    for s in ["train", "val"]:
        img_files = list((out_dir / "images" / s).glob("*.jpg"))
        cls_box_counts = {0: 0, 1: 0, 2: 0, 3: 0}
        empty_count = 0

        # Check leakage
        leaks = 0
        for ip in img_files:
            h = compute_sha256(ip)
            if h in forbidden_shas:
                leaks += 1
            lp = out_dir / "labels" / s / f"{ip.stem}.txt"
            bx = parse_labels(lp)
            if not bx:
                empty_count += 1
            for b in bx:
                cls_box_counts[b[0]] = cls_box_counts.get(b[0], 0) + 1

        pct_empty = (empty_count / len(img_files) * 100.0) if img_files else 0.0
        print(f"Split [{s.upper()}]:")
        print(f"  Total Images: {len(img_files)} | Empty Negatives: {empty_count} ({pct_empty:.1f}%)")
        print(f"  Box Counts:   {cls_box_counts}")
        print(f"  Zero Leakage Check: {'PASSED (0 leaks)' if leaks == 0 else f'FAILED ({leaks} leaks)'}")
        assert leaks == 0, f"Critical: {leaks} images leaked into {s} split!"


if __name__ == "__main__":
    main()
