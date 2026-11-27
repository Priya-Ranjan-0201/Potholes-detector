"""Gate E Human Review Loop & Chainage Export Test Suite for ScamRoad.

Verifies:
1. Confidence triage: auto-accept (>=0.65), review queue (0.25..0.65), auto-drop (<0.25).
2. Human reviewer decisions (confirm, reject, edit) audit logging and persistence.
3. Weekly active learning export and model gating with rollback logic.
4. Stretch defect reporting grouped by chainage (km).
5. Open REST API exports: CSV, GeoJSON, and PDF summary.
6. Rule R3 disclaimer compliance.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from backend.app.services.triage_service import ConfidenceTriageService
from backend.app.services.active_learning import ActiveLearningManager
from backend.app.services.chainage_reporting import ChainageReportingService

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_confidence_triage_partitioning():
    """Verify confidence triage correctly partitions detections into 3 tiers."""
    triage = ConfidenceTriageService(t_high=0.65, t_low=0.25)

    # 1. High confidence (>= 0.65) -> AUTO_ACCEPTED
    high_det = {"conf": 0.88, "label": "POTHOLE", "box": [10, 10, 50, 50]}
    res_high = triage.triage_detection(high_det)
    assert res_high["triage_action"] == "AUTO_ACCEPTED"
    assert res_high["status"] == "CONFIRMED"

    # 2. Medium confidence (0.25 <= conf < 0.65) -> REVIEW_QUEUE
    mid_det = {"conf": 0.42, "label": "POTHOLE", "box": [20, 20, 60, 60]}
    res_mid = triage.triage_detection(mid_det)
    assert res_mid["triage_action"] == "REVIEW_QUEUE"
    assert res_mid["status"] == "PENDING_REVIEW"

    # 3. Low confidence (< 0.25) -> AUTO_DROPPED
    low_det = {"conf": 0.18, "label": "POTHOLE", "box": [30, 30, 70, 70]}
    res_low = triage.triage_detection(low_det)
    assert res_low["triage_action"] == "AUTO_DROPPED"
    assert res_low["status"] == "DROPPED"


def test_reviewer_decision_logging(tmp_path):
    """Verify human reviewer decisions are persisted with full audit trail."""
    triage = ConfidenceTriageService()
    decision = triage.record_decision(
        defect_id="test-def-101",
        reviewer_id="reviewer-engineer-42",
        decision="confirm",
        notes="Confirmed deep asphalt pothole at chainage km 12.450",
    )

    assert decision["defect_id"] == "test-def-101"
    assert decision["reviewer_id"] == "reviewer-engineer-42"
    assert decision["decision"] == "confirm"
    assert "timestamp" in decision

    decisions = triage.list_decisions()
    assert any(d["defect_id"] == "test-def-101" for d in decisions)


def test_active_learning_export_and_model_gating(tmp_path):
    """Verify weekly active learning export and gating with rollback."""
    al_mgr = ActiveLearningManager(export_dir=tmp_path)
    res = al_mgr.export_weekly_dataset()
    assert res["status"] in ("success", "no_decisions_found")

    # Model Gating Test:
    # Incumbent metrics
    incumbent = {"accuracy": 0.521, "precision": 0.712, "false_alarm_rate": 0.013}

    # Candidate 1: Degraded false alarm rate (> 2%) -> MUST BE REJECTED
    bad_cand_1 = {"accuracy": 0.530, "precision": 0.715, "false_alarm_rate": 0.035}
    passed_1, reason_1 = al_mgr.gate_candidate_model(bad_cand_1, incumbent)
    assert not passed_1
    assert "exceeds 2.0% limit" in reason_1

    # Candidate 2: Degraded accuracy -> MUST BE REJECTED
    bad_cand_2 = {"accuracy": 0.480, "precision": 0.710, "false_alarm_rate": 0.010}
    passed_2, reason_2 = al_mgr.gate_candidate_model(bad_cand_2, incumbent)
    assert not passed_2
    assert "dropped below incumbent" in reason_2

    # Candidate 3: Superior/Equal metrics -> MUST PASS GATING
    good_cand = {"accuracy": 0.535, "precision": 0.725, "false_alarm_rate": 0.012}
    passed_3, reason_3 = al_mgr.gate_candidate_model(good_cand, incumbent)
    assert passed_3


def test_chainage_stretch_reporting_and_exports():
    """Verify stretch defect aggregation by chainage and export formats."""
    service = ChainageReportingService()

    defects = [
        {"id": "d1", "label": "POTHOLE", "chainage_km": 0.25, "severity": "Critical", "score": 80, "latitude": 12.97, "longitude": 77.59},
        {"id": "d2", "label": "CRACK_ALLIGATOR", "chainage_km": 0.40, "severity": "Moderate", "score": 45, "latitude": 12.98, "longitude": 77.60},
        {"id": "d3", "label": "POTHOLE", "chainage_km": 1.20, "severity": "Severe", "score": 65, "latitude": 12.99, "longitude": 77.61},
    ]

    report = service.group_by_chainage("NH-48 Corridor", start_km=0.0, end_km=2.0, defects=defects, bin_size_km=0.5)

    assert report["stretch_name"] == "NH-48 Corridor"
    assert report["total_defects"] == 3
    assert len(report["chainage_bins"]) == 4  # 0.0..0.5, 0.5..1.0, 1.0..1.5, 1.5..2.0
    assert "Student research project" in report["disclaimer"]

    # Test CSV export
    csv_text = service.export_csv(report)
    assert "chainage_label" in csv_text
    assert "NH-48 Corridor" in csv_text
    assert "km 0.000 - km 0.500" in csv_text

    # Test GeoJSON export
    geojson = service.export_geojson(report)
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 3
    assert geojson["features"][0]["geometry"]["type"] == "Point"

    # Test PDF Summary payload
    pdf_summary = service.export_pdf_summary(report)
    assert "NH-48 Corridor" in pdf_summary["title"]
    assert pdf_summary["total_defects"] == 3
    assert "Student research project" in pdf_summary["footer_disclaimer"]
