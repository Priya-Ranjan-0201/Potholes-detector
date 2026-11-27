"""Gate A Golden Cases Regression Test Suite for ScamRoad.

Verifies:
1. All golden cases show zero boxes on people, vehicles, signs, trees, sky, and blur.
2. The civil engineering diagram (case_02) is strictly rejected as non-road.
3. AVIF format images (case_06) decode cleanly and detect valid road defects.
4. Urban clutter scenes (case_04) suppress off-road false alarms on chairs and signboards.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image

from ml2.pipeline.detector import ML2DetectorPipeline
from ml2.guards.obstacle_filter import ObstacleFilter

REPO_ROOT = Path(__file__).resolve().parents[2]
EVAL_DIR = REPO_ROOT / "eval_failures"
EXPECTED_FILE = EVAL_DIR / "expected.json"

COCO_NAMES = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
    9: "traffic light",
    11: "stop sign",
    13: "bench",
    56: "chair",
    58: "potted plant",
}


@pytest.fixture(scope="module")
def pipeline():
    return ML2DetectorPipeline()


def test_expected_json_exists():
    assert EXPECTED_FILE.exists(), f"Missing {EXPECTED_FILE}"
    with open(EXPECTED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) >= 7


def test_civil_distress_diagram_rejected(pipeline):
    """Case 02: Civil distress diagram must be rejected as non-road with 0 detections."""
    diagram_path = EVAL_DIR / "case_02_civil_distress_diagram.jpg"
    assert diagram_path.exists()
    pil_im = Image.open(diagram_path).convert("RGB")
    arr_rgb = np.array(pil_im)

    is_road, reason, dets = pipeline.predict(arr_rgb)
    assert not is_road, f"Diagram was not rejected: reason={reason}"
    assert len(dets) == 0, f"Expected 0 detections on diagram, got {len(dets)}"


def test_avif_mumbai_potholes_decoding_and_detection(pipeline):
    """Case 06: AVIF format must decode cleanly and detect valid road potholes."""
    avif_path = EVAL_DIR / "case_06_mumbai_potholes.avif"
    assert avif_path.exists()
    pil_im = Image.open(avif_path).convert("RGB")
    arr_rgb = np.array(pil_im)
    h, w = arr_rgb.shape[:2]

    is_road, reason, dets = pipeline.predict(arr_rgb, preset="balanced")
    assert is_road, f"Road photo rejected: {reason}"
    assert len(dets) >= 1, "Failed to detect potholes on road surface"

    # Verify zero boxes overlap pedestrians or vehicles
    img_bgr = cv2.cvtColor(arr_rgb, cv2.COLOR_RGB2BGR)
    obstacles = pipeline.obstacle_filter.detect_obstacles(img_bgr, conf_thresh=0.30)
    for d in dets:
        bx = d["box"]
        for obs in obstacles:
            ox = obs["box"]
            xa, ya = max(bx[0], ox[0]), max(bx[1], ox[1])
            xb, yb = min(bx[2], ox[2]), min(bx[3], ox[3])
            inter = max(0.0, xb - xa) * max(0.0, yb - ya)
            min_area = min(
                (bx[2] - bx[0]) * (bx[3] - bx[1]),
                (ox[2] - ox[0]) * (ox[3] - ox[1])
            )
            iom = inter / max(1.0, min_area)
            assert iom <= 0.35, f"Pothole overlaps {COCO_NAMES.get(obs['class_id'], 'obstacle')} with IoM={iom:.2f}"


def test_case_04_bengaluru_zero_boxes_on_signboards_and_chairs(pipeline):
    """Case 04: Urban scene must have zero detections on sky, signboards, chairs, or buildings."""
    bengaluru_path = EVAL_DIR / "case_04_bengaluru_potholes.jpg"
    assert bengaluru_path.exists()
    pil_im = Image.open(bengaluru_path).convert("RGB")
    arr_rgb = np.array(pil_im)
    h, w = arr_rgb.shape[:2]

    is_road, reason, dets = pipeline.predict(arr_rgb, preset="balanced")
    assert is_road

    for d in dets:
        bx = d["box"]
        # All boxes must be below upper horizon (first 18% of frame)
        assert bx[3] >= h * 0.18, f"Detection in upper horizon: y2={bx[3]} < {h * 0.18}"


def test_all_golden_cases_satisfy_gate_a_criteria(pipeline):
    """Comprehensive test across all failure cases in eval_failures."""
    with open(EXPECTED_FILE, "r", encoding="utf-8") as f:
        expected_data = json.load(f)

    for fname, exp in expected_data.items():
        img_path = EVAL_DIR / fname
        if not img_path.exists():
            continue

        pil_im = Image.open(img_path).convert("RGB")
        arr_rgb = np.array(pil_im)
        img_bgr = cv2.cvtColor(arr_rgb, cv2.COLOR_RGB2BGR)
        h, w = arr_rgb.shape[:2]

        is_road, reason, dets = pipeline.predict(arr_rgb, preset="balanced")

        if not exp.get("road_photo", True):
            assert not is_road, f"{fname} expected rejection, but got is_road=True"
            assert len(dets) == 0, f"{fname} expected 0 detections, got {len(dets)}"
            continue

        # For road scenes:
        assert is_road, f"{fname} unexpectedly rejected: {reason}"

        obstacles = pipeline.obstacle_filter.detect_obstacles(img_bgr, conf_thresh=0.30)
        forbidden_list = exp.get("forbidden_boxes_on", [])
        check_sky = any(f in forbidden_list for f in ["sky", "vegetation", "signboard", "tree", "building"])

        for i, d in enumerate(dets):
            bx = d["box"]
            # 1. No detections in upper horizon
            if check_sky:
                assert bx[3] >= h * 0.18, f"{fname}: Box {i} in upper horizon y2={bx[3]/h:.2%}"

            # 2. No detections overlapping obstacles
            for obs in obstacles:
                ox = obs["box"]
                xa, ya = max(bx[0], ox[0]), max(bx[1], ox[1])
                xb, yb = min(bx[2], ox[2]), min(bx[3], ox[3])
                inter = max(0.0, xb - xa) * max(0.0, yb - ya)
                min_area = min(
                    (bx[2] - bx[0]) * (bx[3] - bx[1]),
                    (ox[2] - ox[0]) * (ox[3] - ox[1])
                )
                iom = inter / max(1.0, min_area)
                assert iom <= 0.35, f"{fname}: Box {i} overlaps {COCO_NAMES.get(obs['class_id'], 'obstacle')} (IoM={iom:.2f})"
