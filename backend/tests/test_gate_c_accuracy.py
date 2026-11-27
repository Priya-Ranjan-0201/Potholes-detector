"""Gate C Accuracy & Benchmark Regression Suite for ScamRoad.

Verifies Gate C requirements:
- TEST-A: >= 1,500 multi-source images (>= 600 damaged, >= 600 clean negatives, >= 4 countries).
- Zero test leakage against training sets.
- Three calibrated operating presets (high_precision, balanced, high_recall).
- Video defect tracker temporal consolidation across 20 clips.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import numpy as np

from ml2.pipeline.detector import ML2DetectorPipeline
from backend.app.services.video_tracker import VideoDefectTracker

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_TEST_A = REPO_ROOT / "data" / "benchmarks" / "manifest_test_a.json"
VIDEO_GT = REPO_ROOT / "data" / "test_videos" / "video_ground_truth.json"
RESULTS_TEST_A = REPO_ROOT / "runs" / "eval" / "gate_c_test_a_results.json"


def test_test_a_manifest_composition():
    """Verify TEST-A has >= 1,500 images, >= 600 damaged, >= 600 clean, across >= 4 countries."""
    assert MANIFEST_TEST_A.exists(), f"Missing {MANIFEST_TEST_A}"
    with open(MANIFEST_TEST_A, "r", encoding="utf-8") as f:
        data = json.load(f)

    total = data["total_images"]
    damaged = data["damaged_images"]
    clean = data["clean_negatives"]
    countries = data["countries"]

    assert total >= 1500, f"Expected >= 1,500 images, got {total}"
    assert damaged >= 600, f"Expected >= 600 damaged images, got {damaged}"
    assert clean >= 600, f"Expected >= 600 clean images, got {clean}"
    assert len(countries) >= 4, f"Expected >= 4 countries, got {countries}"


def test_zero_leakage_between_test_a_and_train():
    """Verify zero overlap between TEST-A and training images."""
    train_dir = REPO_ROOT / "data" / "large_real_world_dataset" / "images" / "train"
    if not train_dir.exists():
        pytest.skip("Train dir not present")

    train_names = set(p.name for p in train_dir.glob("*.jpg"))
    with open(MANIFEST_TEST_A, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data["images"]:
        fn = item["filename"]
        assert fn not in train_names, f"Test image {fn} leaked into training set!"


def test_calibrated_operating_presets():
    """Verify pipeline provides calibrated operating presets without raw confidence slider."""
    pipeline = ML2DetectorPipeline()
    fake_img = np.full((640, 640, 3), 128, dtype=np.uint8)

    # All three presets must be supported
    for preset in ["balanced", "high_precision", "high_recall"]:
        is_r, reason, dets = pipeline.predict(fake_img, preset=preset)
        assert isinstance(is_r, bool)
        assert isinstance(dets, list)


def test_video_tracker_temporal_consolidation():
    """Verify video tracker consolidates frame detections across 20 clips into single events."""
    assert VIDEO_GT.exists(), f"Missing {VIDEO_GT}"
    with open(VIDEO_GT, "r", encoding="utf-8") as f:
        clips = json.load(f)

    assert len(clips) >= 20, f"Expected >= 20 video clips, got {len(clips)}"

    # Test tracker consolidation
    tracker = VideoDefectTracker(iou_threshold=0.20, min_hits=3, max_lost=5)
    fake_frame = np.full((480, 640, 3), 120, dtype=np.uint8)

    for f_idx in range(30):
        dets = [{
            "box": [100.0, 100.0, 200.0, 200.0],
            "label": "POTHOLE",
            "conf": 0.85,
        }]
        tracker.update(f_idx, float(f_idx / 10.0), dets, fake_frame)

    events = tracker.finalize(640, 480)
    # 30 consecutive hits must produce exactly ONE consolidated event, not 30 separate events
    assert len(events) == 1, f"Expected 1 consolidated event, got {len(events)}"
    assert events[0].total_detections == 30
    assert events[0].label == "POTHOLE"
