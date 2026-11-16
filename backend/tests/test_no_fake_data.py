"""Tests verifying complete removal of fake, seeded, and mock data (Phase 4).

Verifies:
- (a) A fresh database installation shows clean empty states everywhere
- (b) After real defect creation, dashboard counts match database counts exactly
- (c) Scans production code ensuring no demo badges, is_demo flags, or synthetic mock generators exist
"""

from __future__ import annotations

import os
import re
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.app.db.session import sync_engine
from backend.app.main import app
from backend.app.models.defect import Defect, SeverityAssessment


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_fresh_install_empty_states(client: TestClient) -> None:
    """Verify that a fresh database produces 0 defects, 0 complaints, 0 work orders, and empty lists."""
    # Ensure database is clean
    try:
        with sync_engine.begin() as conn:
            conn.execute(
                text(
                    "TRUNCATE defects, defect_observations, severity_assessments, "
                    "complaints, work_orders, wards, roads, contractors CASCADE;"
                )
            )
    except Exception:
        pass

    # 1. Overview stats must be 0
    resp = client.get("/api/v1/stats/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_defects"] == 0
    assert data["open_defects"] == 0
    assert data["repaired_defects"] == 0
    assert data["critical_defects"] == 0
    assert data["total_complaints"] == 0
    assert data["total_work_orders"] == 0
    assert data["total_roads_monitored"] == 0
    assert data["average_road_health_index"] is None

    # 2. Wards endpoint must be empty list
    ward_resp = client.get("/api/v1/stats/wards")
    assert ward_resp.status_code == 200
    assert ward_resp.json() == []

    # 3. Contractors endpoint must be empty list
    contr_resp = client.get("/api/v1/stats/contractors")
    assert contr_resp.status_code == 200
    assert contr_resp.json() == []

    # 4. Trends must have 0 observations
    trend_resp = client.get("/api/v1/stats/trends?days=7")
    assert trend_resp.status_code == 200
    t_data = trend_resp.json()
    assert t_data["days"] == 7
    for item in t_data["trends"]:
        assert item["observations_count"] == 0
        assert item["complaints_count"] == 0
        assert item["repairs_count"] == 0


def test_real_action_count_equality(client: TestClient) -> None:
    """Verify that dashboard counts match database records exactly after a real ingestion."""
    from sqlalchemy.orm import Session

    with Session(sync_engine) as session:
        defect = Defect(
            class_code="POTHOLE",
            location="SRID=4326;POINT(0.0 0.0)",
            status="ACTIVE",
            first_seen=datetime.now(UTC),
            last_seen=datetime.now(UTC),
            times_seen=1,
        )
        session.add(defect)
        session.flush()

        assessment = SeverityAssessment(
            defect_id=defect.id,
            raw_score=0.75,
            normalized_score=75,
            level="Critical",
            needs_human_review=False,
            source="test",
            factor_breakdown={},
            missing_factors=[],
        )
        session.add(assessment)
        session.commit()

    # Check overview
    resp = client.get("/api/v1/stats/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_defects"] == 1
    assert data["open_defects"] == 1
    assert data["critical_defects"] == 1


def test_no_mock_data_in_production_code() -> None:
    """Static AST/string scan verifying zero mock/demo plumbing in production source trees."""
    project_root = Path(__file__).resolve().parent.parent.parent

    # Check backend/app
    backend_app = project_root / "backend" / "app"
    forbidden_terms = ["is_demo", "seed_demo_data", "switchDemoRole", "DemoBadge"]

    violations = []

    for root, _, files in os.walk(backend_app):
        for f in files:
            if f.endswith(".py"):
                fpath = os.path.join(root, f)
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                    for line_no, line in enumerate(fp, 1):
                        for term in forbidden_terms:
                            if term in line and not line.strip().startswith("#"):
                                violations.append(f"{fpath}:{line_no}: contains {term}")

    # Check web/src
    web_src = project_root / "web" / "src"
    if web_src.exists():
        for root, _, files in os.walk(web_src):
            for f in files:
                if f.endswith((".ts", ".tsx")):
                    fpath = os.path.join(root, f)
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                        for line_no, line in enumerate(fp, 1):
                            for term in forbidden_terms:
                                if term in line and not line.strip().startswith("//"):
                                    violations.append(f"{fpath}:{line_no}: contains {term}")

    assert not violations, f"Forbidden fake/demo plumbing found in production code:\n" + "\n".join(violations)
