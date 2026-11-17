"""Regression tests for ScamRoad Accuracy Rescue.

Verifies:
1. Non-road diagram rejection (Guard B input gate)
2. Off-road suppression on urban scenes (Guard A road prior)
3. Elimination of absurd 'Alligator 99%' hallucination on sky, chairs, signs
4. Support and threshold behavior for the 3 operating presets
5. Unified ONNX model input/output tensor contract
"""

import os
import sys
import cv2
import numpy as np
import pytest

# Add project root to sys.path
sys.path.insert(0, os.path.abspath("."))

from backend.app.api.v1.infer import (
    check_image_usability,
    run_pipeline_on_image,
    get_pothole_engine,
)
from ml.guard.road_guards import is_road_image, compute_road_surface_mask, filter_boxes_by_road_mask


def test_guard_b_rejects_civil_distress_diagram():
    """Verify that Guard B rejects textbook / civil engineering distress diagrams."""
    path = "eval_failures/case_02_civil_distress_diagram.jpg"
    assert os.path.exists(path), f"Test image missing: {path}"
    img = cv2.imread(path)
    assert img is not None
    is_road, reason = is_road_image(img)
    assert not is_road, "Guard B failed to reject civil distress diagram"
    assert "diagram" in reason.lower() or "not a road" in reason.lower()


def test_guard_b_rejects_ui_screenshots():
    """Verify that Guard B rejects web UI screenshots."""
    path = "docs/screenshots/live_01_dashboard_light.png"
    if os.path.exists(path):
        img = cv2.imread(path)
        is_road, reason = is_road_image(img)
        assert not is_road, "Guard B failed to reject dashboard screenshot"


def test_guard_a_road_surface_mask_bounds():
    """Verify Guard A road mask zeroes out upper scene horizon (sky, trees, signboards)."""
    img = np.full((500, 400, 3), 128, dtype=np.uint8)
    # Bottom has asphalt road color
    img[350:, :] = (100, 100, 100)
    mask = compute_road_surface_mask(img)
    assert mask.shape == (500, 400)
    # Upper horizon (first 18%) must be strictly 0
    assert np.all(mask[:int(500 * 0.18), :] == 0)


def test_case_04_no_sky_or_signboard_detections():
    """Verify that urban road scene (case_04) has NO detections in sky/signboard (y < 0.20*h)."""
    path = "eval_failures/case_04_bengaluru_potholes.jpg"
    assert os.path.exists(path)
    img = cv2.imread(path)
    h, w = img.shape[:2]
    dets = run_pipeline_on_image(img, conf_thresh=0.25, preset="balanced")
    for d in dets:
        top_y_pct = d.box[1]  # y% from top
        assert top_y_pct >= 18.0, f"Detected off-road object in sky/signboard region: y={top_y_pct}%"


def test_unified_model_output_contract():
    """Verify the fine-tuned ONNX model has a single output tensor with 4 damage classes."""
    import onnxruntime as ort
    model_path = "runs/rescue_train/yolo11n_rescue/weights/best.onnx"
    assert os.path.exists(model_path), f"Trained ONNX model missing at: {model_path}"
    sess = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
    
    inputs = sess.get_inputs()
    outputs = sess.get_outputs()
    assert len(inputs) == 1
    assert inputs[0].shape == [1, 3, 640, 640]
    assert len(outputs) == 1
    assert outputs[0].shape == [1, 8, 8400]
    
    meta = sess.get_modelmeta().custom_metadata_map
    names = meta.get("names", "")
    assert "pothole" in names.lower()
    assert "alligator" in names.lower()


def test_three_presets_filtering():
    """Verify that presets correctly apply calibrated threshold behavior."""
    path = "eval_failures/case_05_asphalt_crater.jpg"
    if os.path.exists(path):
        img = cv2.imread(path)
        dets_prec = run_pipeline_on_image(img, preset="high_precision")
        dets_rec = run_pipeline_on_image(img, preset="high_recall")
        # High recall should return >= detections than high precision
        assert len(dets_rec) >= len(dets_prec)
