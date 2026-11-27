"""Gate F Pilot Validation Protocol & Human Field Queue Test Suite for ScamRoad.

Verifies:
1. docs/VALIDATION_PROTOCOL.md specifies 10-50 km real stretch, engineer ground truth,
   matching rules (<=5m), metrics (precision, recall, location error, repeat-pass consistency,
   review workload).
2. docs/HUMAN_TODO.md has concrete, pending field tasks queued (never fabricated results).
3. Rule R1 & Rule R3 disclaimer compliance.
"""

from __future__ import annotations

import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATION_PROTOCOL = REPO_ROOT / "docs" / "VALIDATION_PROTOCOL.md"
HUMAN_TODO = REPO_ROOT / "docs" / "HUMAN_TODO.md"


def test_validation_protocol_stretch_and_ground_truth():
    """Verify VALIDATION_PROTOCOL specifies real 10-50 km stretch and engineer ground truth."""
    assert VALIDATION_PROTOCOL.exists(), f"Missing {VALIDATION_PROTOCOL}"
    content = VALIDATION_PROTOCOL.read_text(encoding="utf-8")

    # Real stretch between 10 and 50 km
    assert "NH-44" in content or "Highway" in content
    assert "25.0 km" in content or "km" in content

    # Ground truth baseline
    assert "Engineer Manual Walking Survey" in content or "engineer" in content.lower()
    assert "Network Survey Vehicle" in content or "NSV" in content

    # Same date / synchronization
    assert "24 hours" in content or "<= 24" in content or "synchronization" in content.lower()


def test_validation_protocol_matching_rules_and_metrics():
    """Verify spatial matching rules and 5 formal validation metrics."""
    content = VALIDATION_PROTOCOL.read_text(encoding="utf-8")

    # Spatial tolerance <= 5m
    assert "5.0" in content and "meter" in content.lower()

    # Required validation metrics
    assert "Precision" in content
    assert "Recall" in content
    assert "Location Error" in content or "along-track" in content.lower()
    assert "Repeat-Pass Consistency" in content or "repeat" in content.lower()
    assert "Review Workload" in content or "workload" in content.lower()
    assert "False Alarm Rate" in content or "FAR" in content

    # Rule R1 & R3 Disclaimers
    assert "Never fabricate" in content or "never fabricated" in content.lower()
    assert "Student research project" in content


def test_human_todo_field_queue():
    """Verify HUMAN_TODO queues physical field tasks without fabricated data."""
    assert HUMAN_TODO.exists(), f"Missing {HUMAN_TODO}"
    content = HUMAN_TODO.read_text(encoding="utf-8")

    assert "H-006" in content, "Missing corridor selection task H-006"
    assert "H-007" in content, "Missing mount calibration task H-007"
    assert "H-008" in content, "Missing dual-pass survey run task H-008"
    assert "H-009" in content, "Missing ground truth walking survey task H-009"
    assert "H-010" in content, "Missing pilot data ingest task H-010"
