"""Prepare Balanced ML2 Training Dataset with Negative Background Regularization.

Zero-Leakage Guarantee:
- Every image in data/rescue_benchmark/manifest.json is excluded by SHA-256 hash.
- Stratifies and balances all 4 road damage classes:
  0: POTHOLE
  1: CRACK_LONGITUDINAL
  2: CRACK_TRANSVERSE
  3: CRACK_ALLIGATOR
- Integrates 20-25% hard negative background images (clean asphalt, traffic, pedestrians, clutter, diagrams).
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import shutil
from pathlib import Path
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
random.seed(42)
np.random.seed(42)


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def augment_sample(
    img: np.ndarray, boxes: List[Tuple[int, float, float, float, float]], aug_type: str
) -> Tuple[np.ndarray, List[Tuple[int, float, float, float, float]]]:
    """Applies label-preserving geometric or photometric augmentations."""
    h, w = img.shape[:2]
    aug_img = img.copy()
    aug_boxes = []

    if aug_type == "orig":
        aug_boxes = [b for b in boxes]
    elif aug_type == "hflip":
        aug_img = cv2.flip(img, 1)
        for cls_id, cx, cy, bw, bh in boxes:
            aug_boxes.append((cls_id, 1.0 - cx, cy, bw, bh))
    elif aug_type == "bright_up":
        aug_img = cv2.convertScaleAbs(img, alpha=1.15, beta=15)
        aug_boxes = [b for b in boxes]
    elif aug_type == "bright_down":
        aug_img = cv2.convertScaleAbs(img, alpha=0.85, beta=-15)
        aug_boxes = [b for b in boxes]
    elif aug_type == "contrast_up":
        aug_img = cv2.convertScaleAbs(img, alpha=1.25, beta=0)
        aug_boxes = [b for b in boxes]
    elif aug_type == "contrast_down":
        aug_img = cv2.convertScaleAbs(img, alpha=0.80, beta=0)
        aug_boxes = [b for b in boxes]
    elif aug_type == "hflip_bright_up":
        aug_img = cv2.flip(cv2.convertScaleAbs(img, alpha=1.15, beta=15), 1)
        for cls_id, cx, cy, bw, bh in boxes:
            aug_boxes.append((cls_id, 1.0 - cx, cy, bw, bh))
    elif aug_type == "hflip_bright_down":
        aug_img = cv2.flip(cv2.convertScaleAbs(img, alpha=0.85, beta=-15), 1)
        for cls_id, cx, cy, bw, bh in boxes:
            aug_boxes.append((cls_id, 1.0 - cx, cy, bw, bh))
    elif aug_type == "blur":
        aug_img = cv2.GaussianBlur(img, (3, 3), 0)
        aug_boxes = [b for b in boxes]
    elif aug_type == "hflip_contrast":
        aug_img = cv2.flip(cv2.convertScaleAbs(img, alpha=1.20, beta=5), 1)
        for cls_id, cx, cy, bw, bh in boxes:
            aug_boxes.append((cls_id, 1.0 - cx, cy, bw, bh))
    else:
        aug_boxes = [b for b in boxes]

    return aug_img, aug_boxes


def main():
    print("=================================================================")
    print(" PREPARING BALANCED ML2 TRAINING DATASET (ZERO LEAKAGE)")
    print("=================================================================")

    bench_manifest = PROJECT_ROOT / "data" / "rescue_benchmark" / "manifest.json"
    if not bench_manifest.exists():
        raise FileNotFoundError(f"Missing benchmark manifest at {bench_manifest}")

    with open(bench_manifest, "r", encoding="utf-8") as f:
        bench_data = json.load(f)

    bench_shas = set(r["sha256"] for r in bench_data["records"])
    print(f"[1/5] Loaded {len(bench_shas)} locked benchmark hashes to exclude.")

    eval_img_dir = PROJECT_ROOT / "data" / "evaluation_set" / "images"
    eval_lbl_dir = PROJECT_ROOT / "data" / "evaluation_set" / "labels"

    # Destination directories
    out_dir = PROJECT_ROOT / "data" / "datasets" / "ml2_training"
    for split in ["train", "val"]:
        (out_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (out_dir / "labels" / split).mkdir(parents=True, exist_ok=True)

    # 1. Harvest candidates outside the benchmark
    print("[2/5] Scanning available images outside benchmark...")
    crack3_samples = []  # Alligator
    crack2_samples = []  # Transverse
    crack1_samples = []  # Longitudinal
    pothole_samples = [] # Pothole
    clean_samples = []   # Clean road

    all_eval_imgs = list(eval_img_dir.glob("*.jpg"))
    for img_p in all_eval_imgs:
        sha = compute_sha256(img_p)
        if sha in bench_shas:
            continue

        lbl_p = eval_lbl_dir / f"{img_p.stem}.txt"
        if not lbl_p.exists() or lbl_p.stat().st_size == 0:
            clean_samples.append(img_p)
            continue

        # Parse boxes
        boxes = []
        for line in lbl_p.read_text().splitlines():
            parts = line.strip().split()
            if len(parts) >= 5:
                cid = int(parts[0])
                cx, cy, bw, bh = map(float, parts[1:5])
                boxes.append((cid, cx, cy, bw, bh))

        if not boxes:
            clean_samples.append(img_p)
            continue

        classes = set(b[0] for b in boxes)
        if 3 in classes:
            crack3_samples.append((img_p, boxes))
        elif 2 in classes:
            crack2_samples.append((img_p, boxes))
        elif 1 in classes:
            crack1_samples.append((img_p, boxes))
        elif 0 in classes:
            pothole_samples.append((img_p, boxes))

    print(f"  Found outside benchmark:")
    print(f"    Class 3 (Alligator): {len(crack3_samples)} source images")
    print(f"    Class 2 (Transverse): {len(crack2_samples)} source images")
    print(f"    Class 1 (Longitudinal): {len(crack1_samples)} source images")
    print(f"    Class 0 (Pothole): {len(pothole_samples)} source images")
    print(f"    Clean Negatives: {len(clean_samples)} source images")

    # 2. Stratified Balancing with Photometric Variations
    print("[3/5] Stratifying and balancing classes...")
    final_dataset: List[Tuple[np.ndarray, List[Tuple[int, float, float, float, float]], str]] = []

    aug_types_c3 = [
        "orig", "hflip", "bright_up", "bright_down", "contrast_up",
        "contrast_down", "hflip_bright_up", "hflip_bright_down",
        "hflip_contrast", "blur"
    ]
    # Replicate class 3 (alligator) with 10 variations each -> ~220 samples
    for img_p, boxes in crack3_samples:
        img = cv2.imread(str(img_p))
        if img is None:
            continue
        for aug in aug_types_c3:
            aug_img, aug_bx = augment_sample(img, boxes, aug)
            final_dataset.append((aug_img, aug_bx, f"c3_{img_p.stem}_{aug}"))

    # Replicate class 2 (transverse) with 6 variations each -> ~246 samples
    aug_types_c2 = ["orig", "hflip", "bright_up", "bright_down", "contrast_up", "hflip_contrast"]
    for img_p, boxes in crack2_samples:
        img = cv2.imread(str(img_p))
        if img is None:
            continue
        for aug in aug_types_c2:
            aug_img, aug_bx = augment_sample(img, boxes, aug)
            final_dataset.append((aug_img, aug_bx, f"c2_{img_p.stem}_{aug}"))

    # Replicate class 1 (longitudinal) with 2 variations each -> ~190 samples
    aug_types_c1 = ["orig", "hflip"]
    for img_p, boxes in crack1_samples:
        img = cv2.imread(str(img_p))
        if img is None:
            continue
        for aug in aug_types_c1:
            aug_img, aug_bx = augment_sample(img, boxes, aug)
            final_dataset.append((aug_img, aug_bx, f"c1_{img_p.stem}_{aug}"))

    # Select ~150 pothole images from evaluation set (1x, unaugmented)
    random.shuffle(pothole_samples)
    for img_p, boxes in pothole_samples[:150]:
        img = cv2.imread(str(img_p))
        if img is None:
            continue
        final_dataset.append((img, boxes, f"c0_eval_{img_p.stem}"))

    # Include positive pothole images from pothole_unified (outside benchmark)
    unified_potholes = []
    for img_p in (PROJECT_ROOT / "data" / "datasets" / "pothole_unified" / "images").glob("**/*.jpg"):
        sha = compute_sha256(img_p)
        if sha in bench_shas:
            continue
        lbl_p = PROJECT_ROOT / "data" / "datasets" / "pothole_unified" / "labels" / img_p.parent.name / f"{img_p.stem}.txt"
        if lbl_p.exists() and lbl_p.stat().st_size > 0:
            boxes = []
            for line in lbl_p.read_text().splitlines():
                parts = line.strip().split()
                if len(parts) >= 5:
                    boxes.append((int(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])))
            if boxes:
                unified_potholes.append((img_p, boxes))

    random.shuffle(unified_potholes)
    # Give priority to Indian road pothole images (ind_*.jpg)
    ind_potholes = [p for p in unified_potholes if "ind_" in p[0].name]
    other_potholes = [p for p in unified_potholes if "ind_" not in p[0].name]
    selected_unified = ind_potholes + other_potholes[:(200 - len(ind_potholes))]
    for img_p, boxes in selected_unified:
        img = cv2.imread(str(img_p))
        if img is None:
            continue
        final_dataset.append((img, boxes, f"c0_uni_{img_p.stem}"))

    print(f"  Added {len(pothole_samples[:150])} eval potholes + {len(selected_unified)} unified positive potholes")

    # 3. Negative Background Regularization (~20-25% negatives)
    # Use ONLY verified clean roads and guard sets (NEVER unannotated road files)
    print("[4/5] Adding verified negative background images (clean road, clutter, diagrams)...")
    for img_p in clean_samples:
        img = cv2.imread(str(img_p))
        if img is None:
            continue
        final_dataset.append((img, [], f"neg_clean_{img_p.stem}"))
        # Add a flipped version for lighting/geometric variety
        final_dataset.append((cv2.flip(img, 1), [], f"neg_clean_flip_{img_p.stem}"))

    # Guard set negatives outside benchmark
    guard_manifest = PROJECT_ROOT / "data" / "guard_set" / "manifest.json"
    if guard_manifest.exists():
        with open(guard_manifest, "r", encoding="utf-8") as f:
            gm = json.load(f)
        for g_item in gm.get("images", []):
            if not g_item.get("has_defect_gt", False):
                g_p = PROJECT_ROOT / "data" / "guard_set" / "images" / g_item["filename"]
                if g_p.exists():
                    sha = compute_sha256(g_p)
                    if sha not in bench_shas:
                        img = cv2.imread(str(g_p))
                        if img is not None:
                            final_dataset.append((img, [], f"neg_guard_{g_p.stem}"))
                        if img is not None:
                            final_dataset.append((img, [], f"neg_guard_{g_p.stem}"))

    # 4. Shuffle and Write Train/Val Splits (85/15)
    print(f"[5/5] Writing {len(final_dataset)} total images to disk...")
    random.shuffle(final_dataset)
    val_cutoff = int(len(final_dataset) * 0.15)
    val_set = final_dataset[:val_cutoff]
    train_set = final_dataset[val_cutoff:]

    def write_split(samples, split_name):
        cls_counter = {0: 0, 1: 0, 2: 0, 3: 0}
        neg_count = 0
        for img, boxes, name in samples:
            img_out = out_dir / "images" / split_name / f"{name}.jpg"
            lbl_out = out_dir / "labels" / split_name / f"{name}.txt"
            cv2.imwrite(str(img_out), img)

            lines = []
            if boxes:
                for cid, cx, cy, bw, bh in boxes:
                    cls_counter[cid] = cls_counter.get(cid, 0) + 1
                    lines.append(f"{cid} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")
            else:
                neg_count += 1

            lbl_out.write_text("\n".join(lines), encoding="utf-8")

        print(f"  {split_name.upper()} split: {len(samples)} images (Negatives: {neg_count})")
        print(f"    Boxes: {cls_counter}")

    write_split(train_set, "train")
    write_split(val_set, "val")

    # Write dataset.yaml
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
    print("ML2 dataset preparation completed successfully!")


if __name__ == "__main__":
    main()
