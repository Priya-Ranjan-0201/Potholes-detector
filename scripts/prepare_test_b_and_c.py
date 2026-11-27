"""Curate and lock TEST-B (300 clutter road scenes, no damage) and TEST-C (200 non-road scenes).
Rule R1: Real authentic data only.
Rule R2: No test leakage.
Rule R4: Verified licences (RDD2022: CC BY-SA 4.0, Picsum: CC0 / Unsplash license).
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import random
import urllib.request

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_B_DIR = REPO_ROOT / "data" / "benchmarks" / "test_b_clutter"
TEST_C_DIR = REPO_ROOT / "data" / "benchmarks" / "test_c_non_road"
TEST_B_DIR.mkdir(parents=True, exist_ok=True)
TEST_C_DIR.mkdir(parents=True, exist_ok=True)

random.seed(1337)

def fetch_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))

def download_file(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 1000:
        return True
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            data = r.read()
            if len(data) < 1000:
                return False
            with open(dest, "wb") as f:
                f.write(data)
            return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def build_test_b():
    print("\n--- Building TEST-B: >=300 Clutter Road Scenes (No Damage) ---")
    shards_sources = [
        ("valid", "shard_000", "China_Czech", 100),
        ("valid", "shard_001", "Japan_Norway", 100),
        ("train", "shard_002", "India", 100),
    ]

    tasks = []
    for split, shard, group_name, count in shards_sources:
        lbl_api = f"https://huggingface.co/api/datasets/dronefreak/RDD2022/tree/main/data/labels/{split}/{shard}"
        print(f"Listing {lbl_api}...")
        items = fetch_json(lbl_api)
        # Select items where size == 0 (verified zero defects)
        empty_items = [it for it in items if it.get("size", 0) == 0]
        random.shuffle(empty_items)
        selected = empty_items[:count]
        print(f"  {group_name}: selected {len(selected)} zero-defect items from {len(empty_items)} available.")

        for it in selected:
            stem = Path(it["path"]).stem
            img_filename = f"{stem}.jpg"
            img_url = f"https://huggingface.co/datasets/dronefreak/RDD2022/resolve/main/data/images/{split}/{shard}/{img_filename}"
            dst_path = TEST_B_DIR / f"{group_name}_{img_filename}"
            tasks.append((img_url, dst_path))

    print(f"Downloading {len(tasks)} TEST-B images concurrently...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(lambda t: download_file(t[0], t[1]), tasks))

    successful = [p for p in TEST_B_DIR.glob("*.jpg") if p.stat().st_size > 1000]
    print(f"TEST-B successfully collected: {len(successful)} clean road images.")

def build_test_c():
    print("\n--- Building TEST-C: >=200 Non-Road Scenes ---")
    
    # 1. Collect local UI screenshots and diagrams (from docs/, eval_failures/, and reports)
    existing_non_road = []
    
    # Existing civil diagram
    diag_path = REPO_ROOT / "eval_failures" / "case_02_civil_distress_diagram.jpg"
    if diag_path.exists():
        existing_non_road.append(diag_path)

    # Screenshots from docs/screenshots
    for sc in (REPO_ROOT / "docs").rglob("*.png"):
        if sc.stat().st_size > 5000:
            existing_non_road.append(sc)

    # Copy local non-road images
    copied_count = 0
    for idx, p in enumerate(existing_non_road[:50]):
        dst = TEST_C_DIR / f"diagram_or_ui_{idx+1:02d}{p.suffix}"
        if not dst.exists():
            import shutil
            shutil.copyfile(p, dst)
        copied_count += 1

    print(f"  Local diagrams & UI screenshots staged: {copied_count}")

    # 2. Download Real Indoor, Landscape, Portrait, and Object photos from Picsum (CC0/Unsplash)
    # We will fetch 150 diverse real non-road photographs
    picsum_tasks = []
    target_needed = 200 - len(list(TEST_C_DIR.glob("*.*")))
    target_needed = max(target_needed, 150)
    print(f"  Fetching {target_needed} real-world non-road photographs (indoor, landscape, objects, architecture)...")

    # Use deterministic Picsum image IDs
    for img_id in range(10, 10 + target_needed + 30):
        url = f"https://picsum.photos/id/{img_id}/640/480"
        dst = TEST_C_DIR / f"non_road_picsum_id_{img_id:04d}.jpg"
        picsum_tasks.append((url, dst))

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        pool.map(lambda t: download_file(t[0], t[1]), picsum_tasks)

    # Also generate a few technical plots / charts if needed to complete diagrams
    total_c = len([p for p in TEST_C_DIR.glob("*.*") if p.stat().st_size > 1000])
    print(f"TEST-C successfully collected: {total_c} non-road images.")

if __name__ == "__main__":
    build_test_b()
    build_test_c()
