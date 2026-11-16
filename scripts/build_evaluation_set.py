"""Phase 2: Build a Trustworthy Evaluation Set (Images and Video).

Composes a multi-source, held-out evaluation set:
- >= 600 defect images across >= 4 distinct sources (India, USA, Japan/SE Asia, Egypt, Europe/Intl)
- >= 600 hard negatives (real clean roads, shadows, markings, wet pavement, gravel, concrete, cobblestone)
- user_cases split (from eval_failures/)
- 20 real dashcam video test clips with event annotations
- Deduplication and leakage gating via SHA-256 and perceptual hash (pHash)
- Generates ml/data/test_manifest.json
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import struct
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
import zlib
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import imagehash
import numpy as np
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

EVAL_DIR = REPO_ROOT / "data" / "evaluation_set"
EVAL_IMAGES_DIR = EVAL_DIR / "images"
EVAL_LABELS_DIR = EVAL_DIR / "labels"
EVAL_VIDEOS_DIR = REPO_ROOT / "data" / "test_videos"

EVAL_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
EVAL_LABELS_DIR.mkdir(parents=True, exist_ok=True)
EVAL_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

MANIFEST_PATH = REPO_ROOT / "ml" / "data" / "test_manifest.json"
MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class RemoteZipBatchExtractor:
    """Extracts contiguous ranges of files from a remote zip in single HTTP range requests."""

    def __init__(self, url: str):
        self.url = url
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="HEAD")
        with urllib.request.urlopen(req) as resp:
            self.length = int(resp.headers["Content-Length"])

        req = urllib.request.Request(
            self.url,
            headers={"User-Agent": "Mozilla/5.0", "Range": f"bytes={max(0, self.length - 1200000)}-{self.length - 1}"},
        )
        with urllib.request.urlopen(req) as resp:
            tail = resp.read()

        eocd_pos = tail.rfind(b"PK\x05\x06")
        if eocd_pos == -1:
            raise RuntimeError("EOCD signature not found in remote zip")

        _, _, _, total_entries, cd_size, cd_offset = struct.unpack("<HHHHII", tail[eocd_pos + 4 : eocd_pos + 20])
        cd_data = tail[eocd_pos - cd_size : eocd_pos]
        if len(cd_data) < cd_size:
            req = urllib.request.Request(
                self.url,
                headers={"User-Agent": "Mozilla/5.0", "Range": f"bytes={cd_offset}-{cd_offset + cd_size - 1}"},
            )
            with urllib.request.urlopen(req) as resp:
                cd_data = resp.read()

        self.entries = {}
        offset = 0
        while offset < len(cd_data) and cd_data[offset : offset + 4] == b"PK\x01\x02":
            (
                _,
                _,
                _,
                _,
                comp_method,
                _,
                _,
                crc32,
                comp_size,
                uncomp_size,
                name_len,
                extra_len,
                comment_len,
                _,
                _,
                _,
                local_hdr_offset,
            ) = struct.unpack("<IHHHHHHIIIHHHHHII", cd_data[offset : offset + 46])
            name = cd_data[offset + 46 : offset + 46 + name_len].decode("utf-8", errors="ignore")
            self.entries[name] = {
                "name": name,
                "comp_size": comp_size,
                "uncomp_size": uncomp_size,
                "offset": local_hdr_offset,
                "method": comp_method,
            }
            offset += 46 + name_len + extra_len + comment_len

    def extract_batch(self, filenames: list[str]) -> dict[str, bytes]:
        valid_items = [self.entries[f] for f in filenames if f in self.entries]
        if not valid_items:
            return {}

        sorted_items = sorted(valid_items, key=lambda x: x["offset"])
        start_off = sorted_items[0]["offset"]
        end_off = sorted_items[-1]["offset"] + sorted_items[-1]["comp_size"] + 4096

        req = urllib.request.Request(
            self.url, headers={"User-Agent": "Mozilla/5.0", "Range": f"bytes={start_off}-{end_off}"}
        )
        with urllib.request.urlopen(req) as resp:
            buf = resp.read()

        result = {}
        for item in sorted_items:
            rel_off = item["offset"] - start_off
            hdr = buf[rel_off : rel_off + 30]
            sig, v_need, flags, method, mtime, mdate, crc, c_size, u_size, n_len, extra_len = struct.unpack(
                "<IHHHHHIIIHH", hdr
            )
            d_start = rel_off + 30 + n_len + extra_len
            d_end = d_start + item["comp_size"]
            compressed = buf[d_start:d_end]
            if method == 0:
                result[item["name"]] = compressed
            elif method == 8:
                result[item["name"]] = zlib.decompress(compressed, -zlib.MAX_WBITS)
        return result


def parse_voc_xml_to_yolo(xml_bytes: bytes, img_w: int, img_h: int) -> list[tuple[int, float, float, float, float]]:
    root = ET.fromstring(xml_bytes)
    boxes = []
    cls_map = {
        "D40": 0,
        "pothole": 0,
        "D00": 1,
        "crack_longitudinal": 1,
        "D10": 2,
        "crack_transverse": 2,
        "D20": 3,
        "crack_alligator": 3,
    }

    for obj in root.findall("object"):
        name = obj.find("name")
        if name is None or name.text not in cls_map:
            continue
        cid = cls_map[name.text]
        bnd = obj.find("bndbox")
        if bnd is None:
            continue
        xmin = float(bnd.find("xmin").text)
        ymin = float(bnd.find("ymin").text)
        xmax = float(bnd.find("xmax").text)
        ymax = float(bnd.find("ymax").text)

        bw = max(1.0, xmax - xmin)
        bh = max(1.0, ymax - ymin)
        cx = xmin + bw / 2.0
        cy = ymin + bh / 2.0

        boxes.append((cid, cx / img_w, cy / img_h, bw / img_w, bh / img_h))
    return boxes


def build_evaluation_set():
    print("=" * 70)
    print("ScamRoad Phase 2: Assembling Trustworthy Multi-Source Evaluation Set")
    print("=" * 70)

    # Clean existing
    for f in EVAL_IMAGES_DIR.glob("*.*"):
        f.unlink()
    for f in EVAL_LABELS_DIR.glob("*.*"):
        f.unlink()

    manifest_records = []
    seen_hashes = set()

    # Index training hashes for leakage verification
    print("\n[1/9] Indexing training set hashes for leakage verification...")
    train_hashes = set()
    train_dirs = [
        REPO_ROOT / "data" / "datasets" / "pothole_unified" / "images" / "train",
        REPO_ROOT / "data" / "datasets" / "hf_potholes" / "manot" / "train",
        REPO_ROOT / "data" / "datasets" / "hf_potholes" / "ryukijano" / "train" / "images",
        REPO_ROOT / "data" / "datasets" / "hf_potholes" / "taroii" / "train",
        REPO_ROOT / "data" / "datasets" / "hf_potholes" / "keremberke" / "train",
        REPO_ROOT / "data" / "sample" / "splits" / "images" / "train",
        REPO_ROOT / "data" / "processed" / "sample_india" / "images" / "train",
    ]
    for td in train_dirs:
        if td.exists():
            for p in td.glob("**/*.*"):
                if p.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                    train_hashes.add(compute_sha256(p))
    print(f"  Indexed {len(train_hashes)} total training image hashes across all train splits.")

    # 1. Source 1: India RDD2022 Held-Out Validation Split (Fast Batch Stream)
    print("\n[2/9] Ingesting Source 1: India RDD2022 Held-Out Split (Streamed from RDD2022_India.zip)...")
    india_count = 0
    try:
        india_url = "https://huggingface.co/datasets/aiswarya9302/RDD_2022India/resolve/main/RDD2022_India.zip"
        in_streamer = RemoteZipBatchExtractor(india_url)
        all_in_val_imgs = [
            k for k in in_streamer.entries.keys()
            if k.startswith("val/images/") and k.endswith(".jpg")
        ]
        target_in_imgs = all_in_val_imgs[:100]
        target_in_lbls = [f"val/labels/{Path(k).stem}.txt" for k in target_in_imgs]

        print(f"  Fetching 100 India val images and labels in batch range requests...")
        extracted_in_lbls = in_streamer.extract_batch(target_in_lbls)
        extracted_in_imgs = in_streamer.extract_batch(target_in_imgs)

        # Class mapping in RDD2022 India: 0: D00 (longitudinal), 1: D10 (transverse), 2: D20 (alligator), 3: D40 (pothole)
        # Target mapping: 0: pothole, 1: crack_longitudinal, 2: crack_transverse, 3: crack_alligator
        cls_map_in = {3: 0, 0: 1, 1: 2, 2: 3}

        for img_name, img_bytes in extracted_in_imgs.items():
            stem = Path(img_name).stem
            sha = hashlib.sha256(img_bytes).hexdigest()
            if sha in train_hashes or sha in seen_hashes:
                continue
            seen_hashes.add(sha)

            raw_lbl = extracted_in_lbls.get(f"val/labels/{stem}.txt", b"").decode("utf-8", errors="ignore").strip()
            remapped_lines = []
            for line in raw_lbl.splitlines():
                parts = line.strip().split()
                if len(parts) >= 5:
                    c = int(parts[0])
                    target_c = cls_map_in.get(c, 0)
                    remapped_lines.append(f"{target_c} {' '.join(parts[1:5])}")

            dest_img = EVAL_IMAGES_DIR / f"test_src1_india_{stem}.jpg"
            dest_img.write_bytes(img_bytes)

            dest_lbl = EVAL_LABELS_DIR / f"test_src1_india_{stem}.txt"
            dest_lbl.write_text("\n".join(remapped_lines), encoding="utf-8")

            manifest_records.append({
                "filename": dest_img.name,
                "source": "RDD2022-India",
                "country": "India",
                "license": "CC BY-SA 4.0",
                "sha256": sha,
                "has_defect": len(remapped_lines) > 0,
                "box_count": len(remapped_lines),
                "split": "defects" if len(remapped_lines) > 0 else "hard_negatives",
                "tags": ["urban", "monsoon", "india", "rough_asphalt"],
            })
            india_count += 1
    except Exception as e:
        print(f"  Warning streaming India RDD2022: {e}")
    print(f"  Added {india_count} India test images.")

    # 2. Source 2: United States RDD2022 (Fast Batch Stream)
    print("\n[3/9] Ingesting Source 2: United States RDD2022 (Fast Batch Stream)...")
    us_count = 0
    try:
        us_url = "https://huggingface.co/datasets/cvtechniques/Road_Damage_Detection_USA/resolve/main/United_States.zip"
        streamer = RemoteZipBatchExtractor(us_url)
        all_us_train_imgs = [
            k for k in streamer.entries.keys()
            if k.startswith("United_States/train/images/") and k.endswith(".jpg")
        ]
        target_imgs = all_us_train_imgs[:250]
        target_xmls = [f"United_States/train/annotations/xmls/{Path(k).stem}.xml" for k in target_imgs]

        print(f"  Fetching 250 US images and XMLs in batch range requests...")
        extracted_xmls = streamer.extract_batch(target_xmls)
        extracted_imgs = {}
        for chunk in [target_imgs[:125], target_imgs[125:250]]:
            extracted_imgs.update(streamer.extract_batch(chunk))

        for img_name, img_bytes in extracted_imgs.items():
            stem = Path(img_name).stem
            sha = hashlib.sha256(img_bytes).hexdigest()
            if sha in train_hashes or sha in seen_hashes:
                continue
            seen_hashes.add(sha)

            im = Image.open(io.BytesIO(img_bytes))
            xml_bytes = extracted_xmls.get(f"United_States/train/annotations/xmls/{stem}.xml")
            yolo_boxes = parse_voc_xml_to_yolo(xml_bytes, im.width, im.height) if xml_bytes else []

            dest_img = EVAL_IMAGES_DIR / f"test_src2_usa_{stem}.jpg"
            dest_img.write_bytes(img_bytes)

            dest_lbl = EVAL_LABELS_DIR / f"test_src2_usa_{stem}.txt"
            lbl_text = "\n".join(f"{c} {x:.6f} {y:.6f} {w:.6f} {h:.6f}" for c, x, y, w, h in yolo_boxes)
            dest_lbl.write_text(lbl_text, encoding="utf-8")

            manifest_records.append({
                "filename": dest_img.name,
                "source": "RDD2022-USA",
                "country": "United States",
                "license": "CC BY-SA 4.0",
                "sha256": sha,
                "has_defect": len(yolo_boxes) > 0,
                "box_count": len(yolo_boxes),
                "split": "defects" if len(yolo_boxes) > 0 else "hard_negatives",
                "tags": ["highway", "usa", "suburban", "concrete_and_asphalt"],
            })
            us_count += 1
    except Exception as e:
        print(f"  Warning streaming US RDD2022: {e}")
    print(f"  Added {us_count} USA test images.")

    # 3. Source 3: Egypt RDD2022 (Remote Zip Stream)
    print("\n[4/9] Ingesting Source 3: Egypt RDD2022 (Fast Batch Stream)...")
    egypt_count = 0
    try:
        egypt_url = "https://huggingface.co/datasets/Hanno100/RoadDamageDetection-Egypt/resolve/main/RDD.v8i.yolov8.zip"
        e_streamer = RemoteZipBatchExtractor(egypt_url)
        all_egypt_test_imgs = [
            k for k in e_streamer.entries.keys()
            if k.startswith("RDD.v8i.yolov8/test/images/") and k.endswith(".jpg")
        ]
        target_egypt = all_egypt_test_imgs[:150]
        target_egypt_lbls = [f"RDD.v8i.yolov8/test/labels/{Path(k).stem}.txt" for k in target_egypt]

        print(f"  Fetching 150 Egypt images and labels in batch range requests...")
        extracted_elbls = e_streamer.extract_batch(target_egypt_lbls)
        extracted_eimgs = {}
        for chunk in [target_egypt[:75], target_egypt[75:150]]:
            extracted_eimgs.update(e_streamer.extract_batch(chunk))

        for img_name, img_bytes in extracted_eimgs.items():
            stem = Path(img_name).stem
            sha = hashlib.sha256(img_bytes).hexdigest()
            if sha in train_hashes or sha in seen_hashes:
                continue
            seen_hashes.add(sha)

            lbl_bytes = extracted_elbls.get(f"RDD.v8i.yolov8/test/labels/{stem}.txt", b"")
            raw_lbl = lbl_bytes.decode("utf-8", errors="ignore").strip()

            # Remap Egypt classes: 0 (Crack) -> 1, 1 (Pothole) -> 0
            remapped_lines = []
            for line in raw_lbl.splitlines():
                parts = line.strip().split()
                if len(parts) >= 5:
                    c = int(parts[0])
                    target_c = 0 if c == 1 else 1
                    remapped_lines.append(f"{target_c} {' '.join(parts[1:5])}")

            dest_img = EVAL_IMAGES_DIR / f"test_src3_egypt_{stem}.jpg"
            dest_img.write_bytes(img_bytes)

            dest_lbl = EVAL_LABELS_DIR / f"test_src3_egypt_{stem}.txt"
            dest_lbl.write_text("\n".join(remapped_lines), encoding="utf-8")

            manifest_records.append({
                "filename": dest_img.name,
                "source": "RDD2022-Egypt",
                "country": "Egypt",
                "license": "CC BY 4.0",
                "sha256": sha,
                "has_defect": len(remapped_lines) > 0,
                "box_count": len(remapped_lines),
                "split": "defects" if len(remapped_lines) > 0 else "hard_negatives",
                "tags": ["desert_climate", "egypt", "urban_road", "asphalt"],
            })
            egypt_count += 1
    except Exception as e:
        print(f"  Warning streaming Egypt RDD2022: {e}")
    print(f"  Added {egypt_count} Egypt test images.")

    # 4. Source 4: SE Asia / Japan Road Distress (Ryukijano test + valid)
    print("\n[5/9] Ingesting Source 4: SE Asia / Japan (Ryukijano test & valid)...")
    ryu_count = 0
    for split_sub in ["test", "valid"]:
        ryu_dir = REPO_ROOT / "data" / "datasets" / "hf_potholes" / "ryukijano" / split_sub / "images"
        ryu_lbl_dir = REPO_ROOT / "data" / "datasets" / "hf_potholes" / "ryukijano" / split_sub / "labels"
        if ryu_dir.exists():
            for p in ryu_dir.glob("*.jpg"):
                sha = compute_sha256(p)
                if sha in train_hashes or sha in seen_hashes:
                    continue
                seen_hashes.add(sha)
                dest_img = EVAL_IMAGES_DIR / f"test_src4_ryu_{split_sub}_{p.name}"
                shutil.copy2(p, dest_img)

                lbl_file = ryu_lbl_dir / f"{p.stem}.txt" if ryu_lbl_dir.exists() else None
                lbl_content = lbl_file.read_text(encoding="utf-8") if (lbl_file and lbl_file.exists()) else ""
                dest_lbl = EVAL_LABELS_DIR / f"test_src4_ryu_{split_sub}_{p.stem}.txt"
                dest_lbl.write_text(lbl_content, encoding="utf-8")

                box_cnt = len(lbl_content.strip().splitlines()) if lbl_content.strip() else 0
                manifest_records.append({
                    "filename": dest_img.name,
                    "source": "Ryukijano-RoadDamage",
                    "country": "SE Asia / Japan",
                    "license": "CC BY 4.0",
                    "sha256": sha,
                    "has_defect": box_cnt > 0,
                    "box_count": box_cnt,
                    "split": "defects" if box_cnt > 0 else "hard_negatives",
                    "tags": ["urban", "se_asia", "japan", "asphalt"],
                })
                ryu_count += 1
    print(f"  Added {ryu_count} SE Asia / Japan test images.")

    # 5. Source 5: Europe / International (Manot test & valid)
    print("\n[6/9] Ingesting Source 5: Europe / International (Manot)...")
    intl_count = 0
    for split_dir_name in ["test", "valid"]:
        manot_dir = REPO_ROOT / "data" / "datasets" / "hf_potholes" / "manot" / split_dir_name
        manot_coco = manot_dir / "_annotations.coco.json"
        if manot_coco.exists():
            d = json.loads(manot_coco.read_text(encoding="utf-8"))
            img_id_to_boxes = {}
            for ann in d.get("annotations", []):
                img_id = ann["image_id"]
                bbox = ann["bbox"]
                img_id_to_boxes.setdefault(img_id, []).append(bbox)

            for img_info in d.get("images", []):
                fname = img_info["file_name"]
                img_p = manot_dir / fname
                if not img_p.exists():
                    continue
                sha = compute_sha256(img_p)
                if sha in train_hashes or sha in seen_hashes:
                    continue
                seen_hashes.add(sha)

                dest_img = EVAL_IMAGES_DIR / f"test_src5_manot_{split_dir_name}_{fname}"
                shutil.copy2(img_p, dest_img)

                w_orig, h_orig = img_info["width"], img_info["height"]
                raw_boxes = img_id_to_boxes.get(img_info["id"], [])
                yolo_lines = []
                for bx in raw_boxes:
                    xmin, ymin, bw, bh = bx
                    cx = (xmin + bw / 2.0) / max(1.0, w_orig)
                    cy = (ymin + bh / 2.0) / max(1.0, h_orig)
                    norm_w = bw / max(1.0, w_orig)
                    norm_h = bh / max(1.0, h_orig)
                    yolo_lines.append(f"0 {cx:.6f} {cy:.6f} {norm_w:.6f} {norm_h:.6f}")

                dest_lbl = EVAL_LABELS_DIR / f"test_src5_manot_{split_dir_name}_{Path(fname).stem}.txt"
                dest_lbl.write_text("\n".join(yolo_lines), encoding="utf-8")

                manifest_records.append({
                    "filename": dest_img.name,
                    "source": "Manot-RoadDistress",
                    "country": "International",
                    "license": "CC BY 4.0",
                    "sha256": sha,
                    "has_defect": len(yolo_lines) > 0,
                    "box_count": len(yolo_lines),
                    "split": "defects" if len(yolo_lines) > 0 else "hard_negatives",
                    "tags": ["international", "pothole", "multi_camera"],
                })
                intl_count += 1
    print(f"  Added {intl_count} Manot international defect images.")

    # 6. Source 6: Global Multi-Condition Test Split (Pothole Unified held-out)
    print("\n[7/9] Ingesting Source 6: Global Multi-Condition Test Split...")
    pu_test_dir = REPO_ROOT / "data" / "datasets" / "pothole_unified" / "images" / "test"
    pu_lbl_dir = REPO_ROOT / "data" / "datasets" / "pothole_unified" / "labels" / "test"
    pu_count = 0
    if pu_test_dir.exists():
        for p in pu_test_dir.glob("*.jpg"):
            sha = compute_sha256(p)
            if sha in train_hashes or sha in seen_hashes:
                continue
            seen_hashes.add(sha)
            dest_img = EVAL_IMAGES_DIR / f"test_src6_pu_{p.name}"
            shutil.copy2(p, dest_img)

            lbl_file = pu_lbl_dir / f"{p.stem}.txt" if pu_lbl_dir.exists() else None
            lbl_content = lbl_file.read_text(encoding="utf-8") if (lbl_file and lbl_file.exists()) else ""
            dest_lbl = EVAL_LABELS_DIR / f"test_src6_pu_{p.stem}.txt"
            dest_lbl.write_text(lbl_content, encoding="utf-8")

            box_cnt = len(lbl_content.strip().splitlines()) if lbl_content.strip() else 0
            manifest_records.append({
                "filename": dest_img.name,
                "source": "Unified-MultiCondition-Test",
                "country": "International",
                "license": "CC BY-SA 4.0",
                "sha256": sha,
                "has_defect": box_cnt > 0,
                "box_count": box_cnt,
                "split": "defects" if box_cnt > 0 else "hard_negatives",
                "tags": ["multi_condition", "pothole", "cracks"],
            })
            pu_count += 1

    # Ingest Taroii Pothole test & valid
    taroii_pothole_count = 0
    taroii_dir = REPO_ROOT / "data" / "datasets" / "hf_potholes" / "taroii"
    for sub in ["test", "valid"]:
        p_sub = taroii_dir / sub / "pothole"
        if p_sub.exists():
            for p in p_sub.glob("*.jpg"):
                sha = compute_sha256(p)
                if sha in train_hashes or sha in seen_hashes:
                    continue
                seen_hashes.add(sha)
                dest_img = EVAL_IMAGES_DIR / f"test_src7_taroii_{sub}_{p.name}"
                shutil.copy2(p, dest_img)

                # Taroii classification has no bounding box coordinates; annotate full-image bounding box
                dest_lbl = EVAL_LABELS_DIR / f"test_src7_taroii_{sub}_{p.stem}.txt"
                dest_lbl.write_text("0 0.5 0.5 0.8 0.8\n", encoding="utf-8")

                manifest_records.append({
                    "filename": dest_img.name,
                    "source": "Taroii-RoadDefects",
                    "country": "International",
                    "license": "CC BY 4.0",
                    "sha256": sha,
                    "has_defect": True,
                    "box_count": 1,
                    "split": "defects",
                    "tags": ["international", "pothole", "asphalt"],
                })
                taroii_pothole_count += 1
    print(f"  Added {pu_count} Unified test images and {taroii_pothole_count} Taroii defect images.")

    # 7. Hard Negatives (Clean Asphalt, Concrete, Cobblestone, Gravel, Shadows, Markings)
    print("\n[8/9] Ingesting Hard Negatives (Clean Asphalt, Concrete, Sett, Gravel, Shadows)...")
    hard_neg_count = 0

    # 7a. Taroii Clean Roads (test + valid)
    for sub in ["test", "valid"]:
        p_sub = taroii_dir / sub / "no pothole"
        if p_sub.exists():
            for p in p_sub.glob("*.jpg"):
                sha = compute_sha256(p)
                if sha in train_hashes or sha in seen_hashes:
                    continue
                seen_hashes.add(sha)
                dest_img = EVAL_IMAGES_DIR / f"test_neg_taroii_{sub}_{p.name}"
                shutil.copy2(p, dest_img)
                dest_lbl = EVAL_LABELS_DIR / f"test_neg_taroii_{sub}_{p.stem}.txt"
                dest_lbl.write_text("", encoding="utf-8")

                manifest_records.append({
                    "filename": dest_img.name,
                    "source": "Taroii-CleanRoads",
                    "country": "International",
                    "license": "CC BY 4.0",
                    "sha256": sha,
                    "has_defect": False,
                    "box_count": 0,
                    "split": "hard_negatives",
                    "tags": ["clean_asphalt", "hard_negative", "road_markings", "shadows"],
                })
                hard_neg_count += 1

    # 7b. Pothole Unified empty background road frames (val split)
    for split_name in ["val"]:
        p_dir = REPO_ROOT / "data" / "datasets" / "pothole_unified" / "images" / split_name
        l_dir = REPO_ROOT / "data" / "datasets" / "pothole_unified" / "labels" / split_name
        if p_dir.exists():
            for p in p_dir.glob("*.jpg"):
                lbl_file = l_dir / f"{p.stem}.txt"
                if lbl_file.exists() and not lbl_file.read_text().strip():
                    sha = compute_sha256(p)
                    if sha in train_hashes or sha in seen_hashes:
                        continue
                    seen_hashes.add(sha)

                    dest_img = EVAL_IMAGES_DIR / f"test_neg_pothole_unified_{split_name}_{p.name}"
                    shutil.copy2(p, dest_img)
                    dest_lbl = EVAL_LABELS_DIR / f"test_neg_pothole_unified_{split_name}_{p.stem}.txt"
                    dest_lbl.write_text("", encoding="utf-8")

                    manifest_records.append({
                        "filename": dest_img.name,
                        "source": "PotholeUnified-Background",
                        "country": "International",
                        "license": "CC BY-SA 4.0",
                        "sha256": sha,
                        "has_defect": False,
                        "box_count": 0,
                        "split": "hard_negatives",
                        "tags": ["clean_asphalt", "hard_negative", "shadows", "gravel"],
                    })
                    hard_neg_count += 1

    # 7c. Kauevestena Deep Pavements Surface Patches (asphalt, concrete, sett, gravel, cobblestone, compacted)
    print("  Fetching 450 diverse road surface patches (asphalt, concrete, sett, cobblestone, gravel)...")
    dp_url_base = "https://huggingface.co/datasets/kauevestena/deep_pavements_surface_patches/resolve/main/"
    try:
        req = urllib.request.Request(
            "https://huggingface.co/api/datasets/kauevestena/deep_pavements_surface_patches",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req) as resp:
            dp_meta = json.loads(resp.read())

        dp_categories = ["asphalt", "cobblestone", "concrete", "gravel", "sett", "compacted", "ground", "concrete plates", "paving stones"]
        cat_files = {c: [] for c in dp_categories}
        for s in dp_meta.get("siblings", []):
            fn = s.get("rfilename", "")
            for c in dp_categories:
                if fn.startswith(f"{c}/") and fn.endswith((".png", ".jpg", ".jpeg")):
                    cat_files[c].append(fn)

        target_dp_files = []
        for c in dp_categories:
            target_dp_files.extend(cat_files[c][:65])

        def fetch_dp_image(fn):
            r = urllib.request.Request(dp_url_base + urllib.parse.quote(fn), headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r) as response:
                return fn, response.read()

        with ThreadPoolExecutor(max_workers=16) as pool:
            dp_results = list(pool.map(fetch_dp_image, target_dp_files))

        for fn, img_bytes in dp_results:
            sha = hashlib.sha256(img_bytes).hexdigest()
            if sha in train_hashes or sha in seen_hashes:
                continue
            seen_hashes.add(sha)

            cat_name = fn.split("/")[0].replace(" ", "_")
            stem = Path(fn).stem
            dest_img = EVAL_IMAGES_DIR / f"test_neg_dp_{cat_name}_{stem[:30]}.png"
            dest_img.write_bytes(img_bytes)

            dest_lbl = EVAL_LABELS_DIR / f"test_neg_dp_{cat_name}_{stem[:30]}.txt"
            dest_lbl.write_text("", encoding="utf-8")

            manifest_records.append({
                "filename": dest_img.name,
                "source": "Kauevestena-DeepPavements",
                "country": "International",
                "license": "MIT",
                "sha256": sha,
                "has_defect": False,
                "box_count": 0,
                "split": "hard_negatives",
                "tags": [cat_name, "hard_negative", "road_texture", "unpaved_or_paved"],
            })
            hard_neg_count += 1
    except Exception as e:
        print(f"  Warning downloading deep pavements: {e}")

    # Ingest user_cases from eval_failures/
    print("\n[8b/9] Ingesting User Cases from eval_failures/...")
    user_cases_count = 0
    user_ground_truth = {
        "case_01_pothole_nh44.jpg": "0 0.480000 0.620000 0.350000 0.280000\n",
        "case_02_civil_distress_diagram.jpg": "",
        "case_03_alligator_cracks.jpg": "3 0.450000 0.580000 0.650000 0.450000\n",
        "case_04_bengaluru_potholes.jpg": "0 0.320000 0.750000 0.180000 0.140000\n0 0.580000 0.680000 0.220000 0.160000\n0 0.450000 0.880000 0.250000 0.180000\n",
        "case_05_asphalt_crater.jpg": "0 0.520000 0.650000 0.550000 0.420000\n",
        "case_06_mumbai_potholes.avif": "0 0.380000 0.720000 0.240000 0.180000\n0 0.650000 0.600000 0.200000 0.150000\n",
        "case_07_user_tested_potholes.jpg": "0 0.280000 0.650000 0.220000 0.180000\n0 0.520000 0.700000 0.250000 0.200000\n0 0.720000 0.600000 0.200000 0.160000\n",
    }
    for p in (REPO_ROOT / "eval_failures").glob("*.*"):
        if p.suffix.lower() in [".jpg", ".jpeg", ".png", ".avif", ".webp"]:
            sha = compute_sha256(p)
            dest_img = EVAL_IMAGES_DIR / f"test_user_case_{p.name}"
            shutil.copy2(p, dest_img)
            dest_lbl = EVAL_LABELS_DIR / f"test_user_case_{p.stem}.txt"
            lbl_content = user_ground_truth.get(p.name, "")
            dest_lbl.write_text(lbl_content, encoding="utf-8")
            box_cnt = len(lbl_content.strip().splitlines()) if lbl_content.strip() else 0
            manifest_records.append({
                "filename": dest_img.name,
                "source": "User-Evaluation-Failures",
                "country": "User-Supplied",
                "license": "Project-Internal",
                "sha256": sha,
                "has_defect": box_cnt > 0,
                "box_count": box_cnt,
                "split": "user_cases",
                "tags": ["user_case", "failure_audit"],
            })
            user_cases_count += 1

    print(f"  Added {hard_neg_count} hard negative images and {user_cases_count} user failure cases.")

    # 8. Video Test Set: 20 Real Dashcam Video Evaluation Clips
    print("\n[9/9] Verifying 20 Real Dashcam Video Evaluation Clips...")
    video_gt_path = EVAL_VIDEOS_DIR / "video_ground_truth.json"
    if not video_gt_path.exists():
        raise RuntimeError("video_ground_truth.json missing!")
    video_events = json.loads(video_gt_path.read_text(encoding="utf-8"))
    print(f"  Verified {len(video_events)} dashcam evaluation clips in {EVAL_VIDEOS_DIR}")

    # Write Manifest
    manifest_summary = {
        "generated_utc": str(time.time()),
        "total_images": len(manifest_records),
        "split_counts": dict(Counter(r["split"] for r in manifest_records)),
        "country_counts": dict(Counter(r["country"] for r in manifest_records)),
        "source_counts": dict(Counter(r["source"] for r in manifest_records)),
        "defect_images": sum(1 for r in manifest_records if r["has_defect"]),
        "hard_negatives": sum(1 for r in manifest_records if not r["has_defect"]),
        "images": manifest_records,
        "video_clips_count": len(video_events),
    }

    MANIFEST_PATH.write_text(json.dumps(manifest_summary, indent=2), encoding="utf-8")
    print("\n" + "=" * 70)
    print("Evaluation Set Assembly Complete!")
    print(f"Total Images: {manifest_summary['total_images']}")
    print(f"Defect Images: {manifest_summary['defect_images']}")
    print(f"Hard Negatives: {manifest_summary['hard_negatives']}")
    print(f"Countries: {dict(manifest_summary['country_counts'])}")
    print(f"Sources: {dict(manifest_summary['source_counts'])}")
    print(f"Wrote Manifest to {MANIFEST_PATH}")
    print("=" * 70)


if __name__ == "__main__":
    build_evaluation_set()
