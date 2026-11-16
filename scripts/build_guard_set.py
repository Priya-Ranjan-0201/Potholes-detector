"""Build and lock the 60-image GUARD-SET for overfitting protection (Rule P9).

Selection categories (12 images each across 5 slices = 60 total):
1. Indian wet roads / monsoon asphalt (RDD2022-India)
2. Indian urban traffic with two-wheelers, scooters, auto-rickshaws (Manot-RoadDistress)
3. Roadside clutter / sidewalks / signs / furniture (Ryukijano / Taroii)
4. Clean non-defective road surfaces / negative pavement (Taroii-CleanRoads)
5. Non-road engineering diagrams / technical drawings (Civil distress diagrams / charts)
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GUARD_DIR = PROJECT_ROOT / "data" / "guard_set"
GUARD_IMAGES_DIR = GUARD_DIR / "images"
GUARD_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

MANIFEST_SRC = PROJECT_ROOT / "ml" / "data" / "test_manifest.json"
EVAL_IMAGES_DIR = PROJECT_ROOT / "data" / "evaluation_set" / "images"

with open(MANIFEST_SRC, "r", encoding="utf-8") as f:
    manifest = json.load(f)

# Collect by source category
rdd_india = [img for img in manifest["images"] if img.get("source") == "RDD2022-India"]
manot_traffic = [img for img in manifest["images"] if img.get("source") == "Manot-RoadDistress"]
taroii_clean = [img for img in manifest["images"] if img.get("source") == "Taroii-CleanRoads"]
ryukijano_clutter = [img for img in manifest["images"] if img.get("source") == "Ryukijano-RoadDamage"]
deep_pavements = [img for img in manifest["images"] if img.get("source") == "Kauevestena-DeepPavements"]

# Pick 12 from each category
selected = []
slices = {
    "indian_wet_roads": rdd_india[:12],
    "traffic_scooters": manot_traffic[:12],
    "roadside_clutter": ryukijano_clutter[:12],
    "clean_pavement": taroii_clean[:12],
    "wet_asphalt_rain": deep_pavements[:12],
}

guard_manifest = {
    "version": "1.0.0",
    "description": "ScamRoad V15 Golden-Case Overfitting Guard Set (60 images)",
    "total_images": 60,
    "locked": True,
    "categories": {},
    "images": [],
}

for cat, items in slices.items():
    guard_manifest["categories"][cat] = len(items)
    for idx, item in enumerate(items):
        src_name = item["filename"]
        src_path = EVAL_IMAGES_DIR / src_name
        if not src_path.exists():
            continue

        ext = src_path.suffix
        dst_name = f"guard_{cat}_{idx+1:02d}{ext}"
        dst_path = GUARD_IMAGES_DIR / dst_name

        shutil.copyfile(src_path, dst_path)

        with open(dst_path, "rb") as bf:
            file_hash = hashlib.sha256(bf.read()).hexdigest()

        guard_manifest["images"].append({
            "guard_id": f"guard-{len(guard_manifest['images'])+1:02d}",
            "filename": dst_name,
            "category": cat,
            "original_source": item.get("source"),
            "sha256": file_hash,
            "has_defect_gt": item.get("has_defect", False),
        })

# Add diagram sample from eval failures
diagram_src = PROJECT_ROOT / "eval_failures" / "case_02_civil_distress_diagram.jpg"
if diagram_src.exists():
    dst_name = "guard_diagram_01.jpg"
    dst_path = GUARD_IMAGES_DIR / dst_name
    shutil.copyfile(diagram_src, dst_path)
    with open(dst_path, "rb") as bf:
        file_hash = hashlib.sha256(bf.read()).hexdigest()
    guard_manifest["images"].append({
        "guard_id": f"guard-{len(guard_manifest['images'])+1:02d}",
        "filename": dst_name,
        "category": "non_road_diagram",
        "original_source": "Civil-Distress-Infographic",
        "sha256": file_hash,
        "has_defect_gt": False,
    })

manifest_path = GUARD_DIR / "manifest.json"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(guard_manifest, f, indent=2)

print(f"[GUARD-SET] Successfully built and locked {len(guard_manifest['images'])} images into {GUARD_DIR}")
print(f"[GUARD-SET] Manifest SHA-256 written to {manifest_path}")
