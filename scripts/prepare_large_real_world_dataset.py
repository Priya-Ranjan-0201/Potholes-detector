"""Prepare Large-Scale Real-World Road Defect Dataset (~1,000+ authentic images).

Multi-source curation:
1. GitHub Pothole Dataset (michelpf/dataset-pothole) - 600 authentic pothole images
2. RDD2022 Multi-Country Dataset (India, US, Japan) from Hugging Face - 350 multi-class crack & pothole images
3. Hard Negative Road Pavement Samples - 150 clean pavement, lane line, and shadow images

Canonical 4-Class Mapping:
0: pothole
1: crack_longitudinal
2: crack_transverse
3: crack_alligator
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import random
import shutil
import urllib.request
import zipfile
from pathlib import Path

random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "data" / "large_real_world_dataset"
TEMP_ZIP = PROJECT_ROOT / "temp_pothole_archive.zip"

TRAIN_IMG = DATASET_DIR / "images" / "train"
VAL_IMG = DATASET_DIR / "images" / "val"
TRAIN_LBL = DATASET_DIR / "labels" / "train"
VAL_LBL = DATASET_DIR / "labels" / "val"

for p in [TRAIN_IMG, VAL_IMG, TRAIN_LBL, VAL_LBL]:
    p.mkdir(parents=True, exist_ok=True)


def remap_rdd_label(raw_text: str) -> str:
    """Remap RDD2022 classes:
    0 (longitudinal) -> 1 (crack_longitudinal)
    1 (transverse)   -> 2 (crack_transverse)
    2 (alligator)    -> 3 (crack_alligator)
    3 (pothole)      -> 0 (pothole)
    """
    remap = {0: 1, 1: 2, 2: 3, 3: 0}
    out_lines = []
    for line in raw_text.splitlines():
        parts = line.strip().split()
        if len(parts) >= 5:
            try:
                cls_id = int(parts[0])
                new_cls = remap.get(cls_id, 0)
                out_lines.append(f"{new_cls} " + " ".join(parts[1:5]))
            except ValueError:
                continue
    return "\n".join(out_lines)


def get_pothole_records(target_count: int = 600) -> list[dict]:
    """Extract authentic pothole images from GitHub dataset."""
    print(f"\n[1/3] Curating {target_count} real-world pothole images...")
    if not TEMP_ZIP.exists():
        print(f"Downloading pothole dataset archive...")
        urllib.request.urlretrieve(
            "https://github.com/michelpf/dataset-pothole/archive/refs/heads/main.zip",
            str(TEMP_ZIP),
        )

    records = []
    with zipfile.ZipFile(TEMP_ZIP, "r") as z:
        all_files = z.namelist()
        jpg_files = [
            f for f in all_files if f.endswith(".jpg") and ("dataset/train/" in f or "dataset/test/" in f)
        ]
        random.shuffle(jpg_files)
        selected_jpgs = jpg_files[:target_count]

        for jpg_name in selected_jpgs:
            txt_name = jpg_name.rsplit(".", 1)[0] + ".txt"
            base_stem = Path(jpg_name).stem

            try:
                img_bytes = z.read(jpg_name)
                txt_str = z.read(txt_name).decode("utf-8") if txt_name in all_files else ""
            except KeyError:
                continue

            classes = []
            for line in txt_str.splitlines():
                if line.strip():
                    try:
                        classes.append(int(line.split()[0]))
                    except ValueError:
                        pass

            records.append({
                "source": "github_potholes",
                "filename": f"pothole_{base_stem}.jpg",
                "img_bytes": img_bytes,
                "label_text": txt_str.strip(),
                "classes": classes,
            })

    print(f"  Extracted {len(records)} authentic pothole records.")
    return records


def get_rdd2022_damage_records(target_count: int = 350) -> list[dict]:
    """Fetch crack & distress records from RDD2022 India, US, and Global shards."""
    print(f"\n[2/3] Fetching {target_count} multi-class damage records from RDD2022...")
    shards = ["shard_002", "shard_003", "shard_008", "shard_000"]
    candidates = []

    for shard in shards:
        api_url = f"https://huggingface.co/api/datasets/dronefreak/RDD2022/tree/main/data/labels/train/{shard}"
        try:
            req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                items = json.loads(r.read().decode("utf-8"))
                for it in items:
                    if it.get("size", 0) > 0:
                        candidates.append((shard, it["path"]))
        except Exception as e:
            print(f"  Warning fetching {shard} metadata: {e}")

    random.shuffle(candidates)
    selected = candidates[:target_count]
    print(f"  Downloading {len(selected)} RDD images & labels across 16 parallel threads...")

    def fetch_item(item_info):
        shard, lbl_path = item_info
        stem = Path(lbl_path).stem
        img_name = f"{stem}.jpg"

        lbl_url = f"https://huggingface.co/datasets/dronefreak/RDD2022/raw/main/{lbl_path}"
        img_url = f"https://huggingface.co/datasets/dronefreak/RDD2022/resolve/main/data/images/train/{shard}/{img_name}"

        try:
            req_lbl = urllib.request.Request(lbl_url, headers={"User-Agent": "Mozilla/5.0"})
            raw_lbl = urllib.request.urlopen(req_lbl, timeout=10).read().decode("utf-8")
            remapped_lbl = remap_rdd_label(raw_lbl)

            req_img = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
            img_bytes = urllib.request.urlopen(req_img, timeout=12).read()

            classes = []
            for line in remapped_lbl.splitlines():
                if line.strip():
                    try:
                        classes.append(int(line.split()[0]))
                    except ValueError:
                        pass

            return {
                "source": f"rdd2022_{shard}",
                "filename": f"rdd_{stem}.jpg",
                "img_bytes": img_bytes,
                "label_text": remapped_lbl,
                "classes": classes,
            }
        except Exception:
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        results = list(executor.map(fetch_item, selected))

    valid = [r for r in results if r is not None]
    print(f"  Successfully retrieved {len(valid)} RDD2022 records.")
    return valid


def get_hard_negative_records(target_count: int = 150) -> list[dict]:
    """Fetch clean background road images (no defects) across diverse conditions."""
    print(f"\n[3/3] Fetching {target_count} clean negative road images...")
    shards = ["shard_002", "shard_003"]
    empty_candidates = []

    for shard in shards:
        api_url = f"https://huggingface.co/api/datasets/dronefreak/RDD2022/tree/main/data/labels/train/{shard}"
        try:
            req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                items = json.loads(r.read().decode("utf-8"))
                for it in items:
                    if it.get("size", 0) == 0:
                        empty_candidates.append((shard, it["path"]))
        except Exception as e:
            print(f"  Warning fetching empty labels: {e}")

    random.shuffle(empty_candidates)
    selected = empty_candidates[:target_count]

    def fetch_negative(item_info):
        shard, lbl_path = item_info
        stem = Path(lbl_path).stem
        img_name = f"{stem}.jpg"
        img_url = f"https://huggingface.co/datasets/dronefreak/RDD2022/resolve/main/data/images/train/{shard}/{img_name}"

        try:
            req_img = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
            img_bytes = urllib.request.urlopen(req_img, timeout=12).read()
            return {
                "source": "rdd2022_clean_pavement",
                "filename": f"neg_{stem}.jpg",
                "img_bytes": img_bytes,
                "label_text": "",
                "classes": [],
            }
        except Exception:
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        results = list(executor.map(fetch_negative, selected))

    valid = [r for r in results if r is not None]
    print(f"  Successfully retrieved {len(valid)} clean negative pavement records.")
    return valid


def main() -> None:
    print("=" * 65)
    print("  Curating 1,000+ Real-World Road Damage Dataset for ScamRoad")
    print("=" * 65)

    potholes = get_pothole_records(target_count=600)
    damages = get_rdd2022_damage_records(target_count=350)
    negatives = get_hard_negative_records(target_count=150)

    all_records = potholes + damages + negatives
    random.shuffle(all_records)
    print(f"\nTotal Curated Real-World Pool: {len(all_records)} images.")

    # 85/15 train/val split
    split_idx = int(len(all_records) * 0.85)
    train_pool = all_records[:split_idx]
    val_pool = all_records[split_idx:]

    print(f"Partitioned: {len(train_pool)} train images, {len(val_pool)} val images.")

    class_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    manifest_records = []

    def write_subset(subset, img_dir, lbl_dir, split_name):
        for rec in subset:
            fname = rec["filename"]
            stem = Path(fname).stem
            img_dest = img_dir / fname
            lbl_dest = lbl_dir / f"{stem}.txt"

            img_dest.write_bytes(rec["img_bytes"])
            lbl_dest.write_text(rec["label_text"], encoding="utf-8")

            for c in rec["classes"]:
                class_counts[c] = class_counts.get(c, 0) + 1

            sha256 = hashlib.sha256(rec["img_bytes"]).hexdigest()
            manifest_records.append({
                "filename": fname,
                "split": split_name,
                "source": rec["source"],
                "sha256": sha256,
                "classes": rec["classes"],
                "is_defect": len(rec["classes"]) > 0,
            })

    write_subset(train_pool, TRAIN_IMG, TRAIN_LBL, "train")
    write_subset(val_pool, VAL_IMG, VAL_LBL, "val")

    # Generate dataset.yaml
    dataset_yaml_path = DATASET_DIR / "dataset.yaml"
    dataset_yaml_content = f"""# ScamRoad Large-Scale Real-World Road Defect Dataset
path: {DATASET_DIR.resolve().as_posix()}
train: images/train
val: images/val
nc: 4
names:
  0: pothole
  1: crack_longitudinal
  2: crack_transverse
  3: crack_alligator
"""
    dataset_yaml_path.write_text(dataset_yaml_content, encoding="utf-8")

    # Save manifest
    manifest_path = DATASET_DIR / "manifest.json"
    manifest_data = {
        "dataset_name": "ScamRoad Large-Scale Real-World Road Defect Dataset",
        "description": "Comprehensive multi-source real-world road defect training set (RDD2022 + GitHub Potholes + Negative Pavement)",
        "total_images": len(all_records),
        "train_images": len(train_pool),
        "val_images": len(val_pool),
        "class_counts": class_counts,
        "classes": {
            0: "pothole",
            1: "crack_longitudinal",
            2: "crack_transverse",
            3: "crack_alligator",
        },
        "records": manifest_records,
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

    print("\nDataset preparation successfully completed!")
    print(f"  Dataset YAML:  {dataset_yaml_path}")
    print(f"  Class counts:  {class_counts}")
    print(f"  Manifest:      {manifest_path}")
    print("=" * 65)


if __name__ == "__main__":
    main()
