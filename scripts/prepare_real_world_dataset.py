"""Download and curate authentic real-world road defect dataset from public internet sources.

Combines:
1. Real-world Road Damage Dataset (RDD2022 - India & Global subsets from Hugging Face: dronefreak/RDD2022)
   - Longitudinal Cracks (D00 -> crack_longitudinal)
   - Transverse Cracks (D10 -> crack_transverse)
   - Alligator Cracks (D20 -> crack_alligator)
   - Potholes (D40 -> pothole)
2. Real-world Pothole Detection Dataset (michelpf/dataset-pothole from GitHub)
   - Potholes (pothole -> pothole)
3. Hard Negative Road Surfaces (clean asphalt, traffic shadows, clean pavement)

Canonical 4-Class Taxonomy:
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
from PIL import Image

random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "data" / "real_world_dataset"
TEMP_ZIP = PROJECT_ROOT / "temp_dataset_pothole.zip"

TRAIN_IMG = DATASET_DIR / "images" / "train"
VAL_IMG = DATASET_DIR / "images" / "val"
TRAIN_LBL = DATASET_DIR / "labels" / "train"
VAL_LBL = DATASET_DIR / "labels" / "val"

for p in [TRAIN_IMG, VAL_IMG, TRAIN_LBL, VAL_LBL]:
    p.mkdir(parents=True, exist_ok=True)


def download_url(url: str, dest: Path) -> bool:
    """Download single file with retry."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                content = resp.read()
                dest.write_bytes(content)
                return True
        except Exception:
            pass
    return False


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


def process_github_potholes(target_count: int = 250) -> list[dict]:
    """Extract real-world pothole images from GitHub archive."""
    print(f"\n[1/3] Extracting {target_count} real-world pothole images from GitHub dataset...")
    if not TEMP_ZIP.exists():
        print(f"Downloading {TEMP_ZIP.name} from GitHub...")
        urllib.request.urlretrieve(
            "https://github.com/michelpf/dataset-pothole/archive/refs/heads/main.zip",
            str(TEMP_ZIP),
        )

    records = []
    with zipfile.ZipFile(TEMP_ZIP, "r") as z:
        all_files = z.namelist()
        jpg_files = [f for f in all_files if f.endswith(".jpg") and "dataset/train/" in f]
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

            # In this dataset, class 0 is already 'pothole'
            records.append({
                "source": "github_michelpf_pothole",
                "filename": f"pothole_{base_stem}.jpg",
                "img_bytes": img_bytes,
                "label_text": txt_str.strip(),
                "classes": [0] if txt_str.strip() else [],
            })

    print(f"  Extracted {len(records)} pothole samples.")
    return records


def process_rdd2022_cracks(target_count: int = 150) -> list[dict]:
    """Fetch real-world crack and multi-damage images from Hugging Face RDD2022."""
    print(f"\n[2/3] Fetching {target_count} crack & damage images from RDD2022 (India & Global)...")
    records = []

    # Query shard_002 (India) and shard_000 (Global) label metadata
    candidates = []
    for shard in ["shard_002", "shard_000"]:
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
    print(f"  Downloading {len(selected)} image-label pairs via worker threads...")

    def fetch_item(item_info):
        shard, lbl_path = item_info
        filename = Path(lbl_path).name
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
                    classes.append(int(line.split()[0]))

            return {
                "source": f"rdd2022_{shard}",
                "filename": f"rdd_{img_name}",
                "img_bytes": img_bytes,
                "label_text": remapped_lbl,
                "classes": classes,
            }
        except Exception:
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(fetch_item, selected))

    valid_records = [r for r in results if r is not None]
    print(f"  Successfully retrieved {len(valid_records)} RDD2022 multi-class records.")
    return valid_records


def process_clean_negatives(target_count: int = 50) -> list[dict]:
    """Fetch clean background negative images (empty labels) for false positive suppression."""
    print(f"\n[3/3] Fetching {target_count} clean negative road images from RDD2022...")
    api_url = "https://huggingface.co/api/datasets/dronefreak/RDD2022/tree/main/data/labels/train/shard_002"
    empty_candidates = []
    try:
        req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            items = json.loads(r.read().decode("utf-8"))
            for it in items:
                if it.get("size", 0) == 0:
                    empty_candidates.append(it["path"])
    except Exception as e:
        print(f"  Warning fetching empty labels: {e}")

    random.shuffle(empty_candidates)
    selected = empty_candidates[:target_count]

    def fetch_negative(lbl_path):
        stem = Path(lbl_path).stem
        img_name = f"{stem}.jpg"
        img_url = f"https://huggingface.co/datasets/dronefreak/RDD2022/resolve/main/data/images/train/shard_002/{img_name}"
        try:
            req_img = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
            img_bytes = urllib.request.urlopen(req_img, timeout=12).read()
            return {
                "source": "rdd2022_clean_negative",
                "filename": f"neg_{img_name}",
                "img_bytes": img_bytes,
                "label_text": "",
                "classes": [],
            }
        except Exception:
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(fetch_negative, selected))

    valid_negatives = [r for r in results if r is not None]
    print(f"  Successfully retrieved {len(valid_negatives)} clean negative records.")
    return valid_negatives


def main() -> None:
    print("=" * 60)
    print("  Curating Real-World Internet Road Defect Dataset for ScamRoad")
    print("=" * 60)

    pothole_recs = process_github_potholes(target_count=220)
    crack_recs = process_rdd2022_cracks(target_count=130)
    neg_recs = process_clean_negatives(target_count=50)

    all_records = pothole_recs + crack_recs + neg_recs
    random.shuffle(all_records)
    print(f"\nTotal curated pool: {len(all_records)} real-world images.")

    # 80/20 train/val split
    split_idx = int(len(all_records) * 0.8)
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
    dataset_yaml_content = f"""# ScamRoad Real-World Internet Road Defect Dataset
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
        "dataset_name": "ScamRoad Real-World Internet Road Defect Dataset",
        "description": "Multi-source real-world road defect training set (RDD2022 + GitHub Pothole Dataset + Background Negatives)",
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
    print("=" * 60)


if __name__ == "__main__":
    main()
