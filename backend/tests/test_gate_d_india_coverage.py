"""Gate D India Coverage & Annotation Quality Regression Suite for ScamRoad.

Verifies Gate D requirements:
- Coverage matrix by zone/state, road type (NH, SH, urban, rural/PMGSY),
  condition (day, night, monsoon wet, glare, dust), camera (phone, dashcam).
- CVAT guide + two-annotator quality check protocol.
- Water-filled pothole vs harmless surface puddle policy in LABELING_GUIDE.md.
- PuddleCropClassifier differentiates water-filled potholes from surface puddles.
- Cells > 10 points under overall have documented engineering root causes & remediation.
"""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from ml2.guards.puddle_classifier import PuddleCropClassifier

REPO_ROOT = Path(__file__).resolve().parents[2]
LABELING_GUIDE = REPO_ROOT / "docs" / "LABELING_GUIDE.md"
COVERAGE_MD = REPO_ROOT / "docs" / "INDIA_COVERAGE_MATRIX.md"
COVERAGE_JSON = REPO_ROOT / "data" / "benchmarks" / "india_coverage_matrix.json"


def test_labeling_guide_contains_cvat_and_two_annotator_protocol():
    """Verify LABELING_GUIDE.md contains CVAT guidelines and two-annotator agreement protocol."""
    assert LABELING_GUIDE.exists(), f"Missing {LABELING_GUIDE}"
    content = LABELING_GUIDE.read_text(encoding="utf-8")

    assert "CVAT" in content, "Missing CVAT protocol in LABELING_GUIDE.md"
    assert "Two-Annotator" in content or "two-annotator" in content.lower(), "Missing two-annotator protocol"
    assert "Cohen's Kappa" in content or "Kappa" in content, "Missing Cohen's Kappa agreement metric"
    assert "Water-Filled Pothole vs. Surface Water Puddle" in content, "Missing puddle vs water-filled pothole policy"


def test_puddle_crop_classifier_water_filled_pothole():
    """Verify PuddleCropClassifier recognizes deep water-filled potholes with broken asphalt rims."""
    classifier = PuddleCropClassifier(min_rim_gradient=22.0, min_cavity_depth_score=0.35)

    # Synthetic water-filled pothole: dark cavity center (L=40), jagged asphalt perimeter with high gradient
    crop = np.zeros((100, 100, 3), dtype=np.uint8)
    crop[:, :] = [50, 50, 50]  # dark mud/water center
    # Add high-contrast jagged rim
    crop[:15, :] = [180, 180, 180]
    crop[-15:, :] = [180, 180, 180]
    crop[:, :15] = [180, 180, 180]
    crop[:, -15:] = [180, 180, 180]

    result = classifier.classify_crop(crop)
    assert result["is_water_filled_pothole"] is True
    assert result["classification"] == "WATER_FILLED_POTHOLE"
    assert result["rim_gradient"] >= 22.0


def test_puddle_crop_classifier_surface_puddle():
    """Verify PuddleCropClassifier rejects flat surface puddles on intact asphalt."""
    classifier = PuddleCropClassifier(min_rim_gradient=22.0, min_cavity_depth_score=0.35)

    # Synthetic harmless surface puddle: flat reflection, smooth low-gradient boundary
    crop = np.full((100, 100, 3), 160, dtype=np.uint8)
    # Add smooth subtle gradient (smooth water transition, no broken edge)
    for r in range(100):
        crop[r, :] = int(150 + 10 * np.sin(r / 15.0))

    result = classifier.classify_crop(crop)
    assert result["is_water_filled_pothole"] is False
    assert result["classification"] == "SURFACE_PUDDLE"
    assert result["rim_gradient"] < 22.0


def test_india_coverage_matrix_dimensions_and_flagged_cells():
    """Verify coverage matrix covers required dimensions and documents flagged cells (>10pt below)."""
    assert COVERAGE_MD.exists(), f"Missing {COVERAGE_MD}"
    assert COVERAGE_JSON.exists(), f"Missing {COVERAGE_JSON}"

    with open(COVERAGE_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    cells = data["cells"]
    dimensions = set(c["dimension"] for c in cells)

    # Must cover 4 required dimensions
    assert "Zone / State" in dimensions
    assert "Road Type" in dimensions
    assert "Environmental Condition" in dimensions
    assert "Camera Hardware" in dimensions

    # Verify road types: NH, SH, Urban, Rural/PMGSY
    road_types = [c["category"] for c in cells if c["dimension"] == "Road Type"]
    assert any("National Highway" in r for r in road_types)
    assert any("State Highway" in r for r in road_types)
    assert any("Urban" in r for r in road_types)
    assert any("Rural" in r or "PMGSY" in r for r in road_types)

    # Verify environmental conditions: Day, Night, Monsoon, Glare, Dust
    conditions = [c["category"] for c in cells if c["dimension"] == "Environmental Condition"]
    assert any("Daylight" in cond for cond in conditions)
    assert any("Night" in cond for cond in conditions)
    assert any("Monsoon" in cond for cond in conditions)
    assert any("Glare" in cond for cond in conditions)
    assert any("Dust" in cond for cond in conditions)

    # Verify flagged cells (> 10 points below overall) have documented explanations
    for c in cells:
        if c["below_overall_10pts"]:
            assert "FLAGGED" in c["notes"], f"Cell {c['category']} missing root-cause explanation!"
            assert "Remediation" in c["notes"] or "remediation" in c["notes"].lower()
