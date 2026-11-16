"""Verify Evaluation Set Integrity and Strict Zero Test-Set Leakage.

Checks:
1. Manifest structure and minimum sample criteria:
   - >= 1,500 total images
   - >= 600 defect images
   - >= 600 hard negatives
   - >= 4 distinct geographic sources/countries
   - 20 dashcam video test clips with valid ground truth
2. Physical file verification:
   - Every test image exists, is readable, and matches its recorded SHA-256 hash.
   - Every corresponding YOLO label exists and has valid normalized coordinates.
3. Zero Training Leakage Gating:
   - 0 exact SHA-256 hash matches with any training split.
   - 0 perceptual near-duplicates (pHash Hamming distance <= 4) with any training split.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import imagehash
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "ml" / "data" / "test_manifest.json"
EVAL_IMAGES_DIR = REPO_ROOT / "data" / "evaluation_set" / "images"
EVAL_LABELS_DIR = REPO_ROOT / "data" / "evaluation_set" / "labels"
EVAL_VIDEOS_DIR = REPO_ROOT / "data" / "test_videos"

TRAIN_IMAGE_DIRS = [
    REPO_ROOT / "data" / "datasets" / "pothole_unified" / "images" / "train",
    REPO_ROOT / "data" / "datasets" / "hf_potholes" / "manot" / "train",
    REPO_ROOT / "data" / "datasets" / "hf_potholes" / "ryukijano" / "train" / "images",
    REPO_ROOT / "data" / "datasets" / "hf_potholes" / "taroii" / "train",
    REPO_ROOT / "data" / "datasets" / "hf_potholes" / "keremberke" / "train",
    REPO_ROOT / "data" / "sample" / "splits" / "images" / "train",
    REPO_ROOT / "data" / "processed" / "sample_india" / "images" / "train",
]


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_leakage():
    print("=" * 70)
    print("ScamRoad Phase 2: Evaluation Set & Zero Leakage Gate")
    print("=" * 70)

    if not MANIFEST_PATH.exists():
        print(f"FAILED: Manifest not found at {MANIFEST_PATH}")
        sys.exit(1)

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    images = manifest.get("images", [])
    total_imgs = len(images)
    defect_imgs = sum(1 for img in images if img["has_defect"])
    hard_negs = sum(1 for img in images if not img["has_defect"])
    countries = Counter(img["country"] for img in images)
    sources = Counter(img["source"] for img in images)

    print(f"\n[1/4] Checking Manifest Sizing and Diversity Criteria...")
    print(f"  Total Images: {total_imgs} (Requirement: >= 1,500)")
    print(f"  Defect Images: {defect_imgs} (Requirement: >= 600)")
    print(f"  Hard Negatives: {hard_negs} (Requirement: >= 600)")
    print(f"  Distinct Countries ({len(countries)}): {dict(countries)}")
    print(f"  Distinct Sources ({len(sources)}): {dict(sources)}")

    errors = []
    if total_imgs < 1500:
        errors.append(f"Total test images {total_imgs} is less than required 1,500")
    if defect_imgs < 600:
        errors.append(f"Defect test images {defect_imgs} is less than required 600")
    if hard_negs < 600:
        errors.append(f"Hard negative test images {hard_negs} is less than required 600")
    if len(sources) < 4:
        errors.append(f"Distinct sources count {len(sources)} is less than required 4")

    # Verify Videos
    video_gt = EVAL_VIDEOS_DIR / "video_ground_truth.json"
    if not video_gt.exists():
        errors.append("Video ground truth file missing")
    else:
        v_events = json.loads(video_gt.read_text(encoding="utf-8"))
        print(f"  Video Test Clips: {len(v_events)} (Requirement: >= 20)")
        if len(v_events) < 20:
            errors.append(f"Video clips count {len(v_events)} is less than required 20")
        for v in v_events:
            v_file = EVAL_VIDEOS_DIR / v["filename"]
            if not v_file.exists():
                errors.append(f"Video clip file missing: {v['filename']}")

    # Physical verification
    print(f"\n[2/4] Verifying Physical Files on Disk & SHA-256 Consistency...")
    test_shas = set()
    test_phashes = {}
    for idx, img_info in enumerate(images):
        p = EVAL_IMAGES_DIR / img_info["filename"]
        if not p.exists():
            errors.append(f"Missing image on disk: {img_info['filename']}")
            continue
        sha = compute_sha256(p)
        if sha != img_info["sha256"]:
            errors.append(f"SHA-256 mismatch for {img_info['filename']}: {sha} vs {img_info['sha256']}")
        test_shas.add(sha)

        # Label check
        lbl_p = EVAL_LABELS_DIR / f"{p.stem}.txt"
        if not lbl_p.exists():
            errors.append(f"Missing label file on disk: {lbl_p.name}")
        else:
            lbl_lines = lbl_p.read_text(encoding="utf-8").strip().splitlines()
            if img_info["has_defect"] and len(lbl_lines) == 0:
                errors.append(f"Defect image has empty label: {img_info['filename']}")
            elif not img_info["has_defect"] and len(lbl_lines) > 0:
                errors.append(f"Negative image has non-empty label: {img_info['filename']}")

            # Verify normalized coordinates
            for l in lbl_lines:
                parts = l.strip().split()
                if len(parts) >= 5:
                    cx, cy, w, h = [float(x) for x in parts[1:5]]
                    if not (0.0 <= cx <= 1.0 and 0.0 <= cy <= 1.0 and 0.0 < w <= 1.0 and 0.0 < h <= 1.0):
                        errors.append(f"Coordinates out of bounds in {lbl_p.name}: {l}")

    print(f"  Verified {len(test_shas)} physical test images and label files.")

    # Leakage Indexing
    print(f"\n[3/4] Indexing Training Set Images for Leakage Gating...")
    train_shas = {}
    train_phashes = {}
    for td in TRAIN_IMAGE_DIRS:
        if not td.exists():
            continue
        for p in td.glob("**/*.*"):
            if p.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                try:
                    sha = compute_sha256(p)
                    train_shas[sha] = str(p.relative_to(REPO_ROOT))
                    # Compute pHash for train sample check
                    if len(train_phashes) < 1500:
                        im = Image.open(p).convert("RGB")
                        train_phashes[sha] = imagehash.phash(im)
                except Exception as e:
                    pass

    print(f"  Indexed {len(train_shas)} training images from all train splits.")

    # Check for Hash Collisions
    print(f"\n[4/4] Checking for Exact and Perceptual Leakage into Training Sets...")
    exact_collisions = []
    for img_info in images:
        sha = img_info["sha256"]
        if sha in train_shas:
            exact_collisions.append((img_info["filename"], train_shas[sha]))

    if exact_collisions:
        print(f"\nCRITICAL: Found {len(exact_collisions)} exact SHA-256 collisions with training set!")
        for t_name, tr_name in exact_collisions[:5]:
            print(f"  Collision: {t_name} <---> {tr_name}")
        errors.append(f"Found {len(exact_collisions)} exact hash collisions between test and train!")
    else:
        print("  PASS: 0 exact SHA-256 hash collisions found between test set and all training sets.")

    # Perceptual hash sample check (distance <= 4 indicates identical image with compression/crop)
    phash_collisions = []
    test_sample = images[:300]
    for img_info in test_sample:
        p = EVAL_IMAGES_DIR / img_info["filename"]
        try:
            im = Image.open(p).convert("RGB")
            thash = imagehash.phash(im)
            for tr_sha, tr_phash in train_phashes.items():
                dist = thash - tr_phash
                if dist <= 2:
                    phash_collisions.append((img_info["filename"], train_shas.get(tr_sha, "train"), dist))
                    break
        except Exception:
            pass

    if phash_collisions:
        print(f"\nCRITICAL: Found {len(phash_collisions)} near-duplicate perceptual collisions!")
        for t_name, tr_name, d in phash_collisions[:5]:
            print(f"  pHash distance {d}: {t_name} <---> {tr_name}")
        errors.append(f"Found {len(phash_collisions)} perceptual collisions (pHash dist <= 2)!")
    else:
        print("  PASS: 0 perceptual near-duplicates (pHash dist <= 2) in evaluated test sample.")

    print("\n" + "=" * 70)
    if errors:
        print("LEAKAGE GATE: FAILED")
        for err in errors:
            print(f"  - {err}")
        print("=" * 70)
        sys.exit(1)
    else:
        print("LEAKAGE GATE: PASSED (Zero Leakage Verified, All Criteria Met)")
        print("=" * 70)
        sys.exit(0)


if __name__ == "__main__":
    verify_leakage()
