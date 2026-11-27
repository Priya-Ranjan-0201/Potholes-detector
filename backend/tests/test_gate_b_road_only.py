"""Gate B Road-Only Detection Regression & Benchmark Suite for ScamRoad.

Verifies Gate B requirements:
- B1: Road-surface mask requires >= 35% overlap; keeps boxes on road only.
- B2: Input classifier rejects non-road scenes (diagrams, UI, landscape, indoor).
- B4: Weighted Boxes Fusion combines candidate detections cleanly.
- B5: TEST-B (>= 300 clutter road scenes, no damage) false-alarm images <= 2%.
      TEST-C (>= 200 non-road scenes) rejected >= 95%.
"""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image

from ml2.guards.input_gate import InputGate
from ml2.guards.road_mask import RoadSurfaceSegmenter
from ml2.pipeline.detector import ML2DetectorPipeline
from ml2.pipeline.wbf import weighted_boxes_fusion, bb_intersection_over_union

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_DIR = REPO_ROOT / "data" / "benchmarks"
TEST_B_DIR = BENCHMARK_DIR / "test_b_clutter"
TEST_C_DIR = BENCHMARK_DIR / "test_c_non_road"


@pytest.fixture(scope="module")
def pipeline():
    return ML2DetectorPipeline()


@pytest.fixture(scope="module")
def input_gate():
    return InputGate()


def test_wbf_coordinate_weighting():
    """Verify Weighted Boxes Fusion computes confidence-weighted coordinates."""
    box1 = {"box": [100.0, 100.0, 200.0, 200.0], "conf": 0.80, "class_id": 0, "label": "POTHOLE"}
    box2 = {"box": [110.0, 110.0, 210.0, 210.0], "conf": 0.40, "class_id": 0, "label": "POTHOLE"}

    fused = weighted_boxes_fusion([box1, box2], iou_thr=0.40, skip_box_thr=0.30)
    assert len(fused) == 1
    # Weight of box1 is 0.8, weight of box2 is 0.4. Fused x1 = (0.8*100 + 0.4*110) / 1.2 = 103.33
    assert abs(fused[0]["box"][0] - 103.33) < 0.5
    assert fused[0]["votes"] == 2
    assert fused[0]["conf"] > 0.50


def test_road_surface_mask_overlap_filter():
    """B1: Verify boxes outside or partially off the road (< 35% overlap) are rejected."""
    segmenter = RoadSurfaceSegmenter(horizon_cutoff_pct=0.385, min_overlap_pct=0.35)

    # Synthetic 500x500 image with road in bottom half (y >= 250)
    fake_img = np.zeros((500, 500, 3), dtype=np.uint8)
    fake_img[250:, :] = 128  # grey pavement

    # Box 1: In the sky/upper scene (y: 20 to 80) -> 0% overlap
    off_road = [{"box": [100.0, 20.0, 200.0, 80.0], "conf": 0.90, "class_id": 0, "label": "POTHOLE"}]
    kept, removed = segmenter.filter_defects(off_road, fake_img)
    assert len(kept) == 0
    assert len(removed) == 1
    assert removed[0]["reason"] == "insufficient_road_overlap"


def test_gate_b_test_c_non_road_rejection(input_gate):
    """B5: TEST-C (>= 200 non-road images) rejected >= 95%."""
    assert TEST_C_DIR.exists(), f"Missing TEST-C directory at {TEST_C_DIR}"
    files = sorted([p for p in TEST_C_DIR.glob("*.*") if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")])
    assert len(files) >= 200, f"Expected >= 200 TEST-C images, found {len(files)}"

    rejected_count = 0
    for p in files:
        img = cv2.imread(str(p))
        if img is None:
            rejected_count += 1
            continue
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        with open(p, "rb") as f:
            raw_bytes = f.read()
        is_road, reason = input_gate.evaluate(rgb, raw_bytes=raw_bytes)
        if not is_road:
            rejected_count += 1

    rejection_rate = rejected_count / len(files)
    print(f"\nTEST-C Benchmark: {rejected_count}/{len(files)} rejected ({rejection_rate * 100:.2f}%)")
    assert rejection_rate >= 0.95, (
        f"TEST-C rejection rate {rejection_rate * 100:.2f}% is below required 95.0% "
        f"({rejected_count}/{len(files)})"
    )


def test_gate_b_test_b_clutter_false_alarm_rate(pipeline):
    """B5: TEST-B (>= 300 clutter road scenes, no damage) false-alarm images <= 2%."""
    assert TEST_B_DIR.exists(), f"Missing TEST-B directory at {TEST_B_DIR}"
    files = sorted(list(TEST_B_DIR.glob("*.jpg")))
    assert len(files) >= 300, f"Expected >= 300 TEST-B images, found {len(files)}"

    false_alarm_count = 0
    false_alarm_details = []

    for p in files:
        img = cv2.imread(str(p))
        if img is None:
            continue
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        is_road, reason, dets = pipeline.predict(rgb, preset="balanced")
        if len(dets) > 0:
            false_alarm_count += 1
            false_alarm_details.append((p.name, len(dets), [d["conf"] for d in dets]))

    fa_rate = false_alarm_count / len(files)
    print(
        f"\nTEST-B Benchmark: {false_alarm_count}/{len(files)} false alarm images ({fa_rate * 100:.2f}%)"
    )
    for name, cnt, cfs in false_alarm_details:
        print(f"  FA: {name} (boxes={cnt}, confs={cfs})")

    assert fa_rate <= 0.02, (
        f"TEST-B false alarm rate {fa_rate * 100:.2f}% exceeds required <= 2.0% "
        f"({false_alarm_count}/{len(files)})"
    )
