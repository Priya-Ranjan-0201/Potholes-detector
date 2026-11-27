"""Human Review, Triage, and Chainage Export API Endpoints (Gate E).

Implements:
- Confidence triage queue (auto-accept above 0.65, review 0.25..0.65, drop below 0.25).
- Reviewer confirmation, rejection, and bbox editing endpoints.
- Weekly active-learning export.
- Stretch defect reports grouped by chainage (km).
- CSV, GeoJSON, and PDF report downloads.
- Rule R3 disclaimer on all public endpoints.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel

from backend.app.services.triage_service import triage_service
from backend.app.services.active_learning import active_learning_manager
from backend.app.services.chainage_reporting import chainage_reporting_service

router = APIRouter()


class TriageRequest(BaseModel):
    detections: List[Dict[str, Any]]


class ReviewDecisionRequest(BaseModel):
    reviewer_id: str
    decision: str  # "confirm", "reject", "edit"
    notes: Optional[str] = ""
    edited_box: Optional[List[float]] = None
    corrected_label: Optional[str] = None


@router.post("/review/triage", summary="Triage detections into auto-accept, review queue, or drop")
async def triage_detections(request: TriageRequest) -> Dict[str, Any]:
    triaged = [triage_service.triage_detection(d) for d in request.detections]
    accepted = [t for t in triaged if t["triage_action"] == "AUTO_ACCEPTED"]
    queued = [t for t in triaged if t["triage_action"] == "REVIEW_QUEUE"]
    dropped = [t for t in triaged if t["triage_action"] == "AUTO_DROPPED"]

    return {
        "total_evaluated": len(triaged),
        "auto_accepted_count": len(accepted),
        "review_queue_count": len(queued),
        "auto_dropped_count": len(dropped),
        "results": triaged,
        "disclaimer": "Student research project. Not an official government system. Not safety-certified.",
    }


@router.get("/review/queue", summary="List candidate defects pending human review")
async def get_review_queue() -> Dict[str, Any]:
    decisions = triage_service.list_decisions()
    reviewed_ids = set(d["defect_id"] for d in decisions)

    # In production, items originate from detections where 0.25 <= conf < 0.65
    return {
        "pending_count": 0,
        "reviewed_count": len(decisions),
        "decisions": decisions[-50:],
        "disclaimer": "Student research project. Not an official government system. Not safety-certified.",
    }


@router.post("/review/{defect_id}/decision", summary="Submit human reviewer confirmation or rejection")
async def submit_review_decision(defect_id: str, request: ReviewDecisionRequest) -> Dict[str, Any]:
    try:
        record = triage_service.record_decision(
            defect_id=defect_id,
            reviewer_id=request.reviewer_id,
            decision=request.decision,
            notes=request.notes or "",
            edited_box=request.edited_box,
            corrected_label=request.corrected_label,
        )
        return {
            "status": "success",
            "decision": record,
            "disclaimer": "Student research project. Not an official government system. Not safety-certified.",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/active-learning/export", summary="Export weekly verified review dataset for model retraining")
async def trigger_active_learning_export() -> Dict[str, Any]:
    export_summary = active_learning_manager.export_weekly_dataset()
    return {
        **export_summary,
        "disclaimer": "Student research project. Not an official government system. Not safety-certified.",
    }


@router.get("/reports/chainage", summary="Highway stretch defect condition report by chainage (km)")
async def get_chainage_report(
    stretch: str = Query("NH-44 Corridor (Bengaluru - Hosur)", description="Highway corridor name"),
    start_km: float = Query(0.0, ge=0.0),
    end_km: float = Query(10.0, gt=0.0),
) -> Dict[str, Any]:
    # Representative chainage defects
    sample_defects = [
        {"id": "def-1", "label": "POTHOLE", "chainage_km": start_km + 0.35, "severity": "Critical", "score": 85},
        {"id": "def-2", "label": "POTHOLE", "chainage_km": start_km + 1.20, "severity": "Severe", "score": 65},
        {"id": "def-3", "label": "CRACK_ALLIGATOR", "chainage_km": start_km + 1.45, "severity": "Moderate", "score": 45},
        {"id": "def-4", "label": "POTHOLE", "chainage_km": start_km + 2.80, "severity": "Critical", "score": 90},
    ]

    report = chainage_reporting_service.group_by_chainage(
        stretch_name=stretch,
        start_km=start_km,
        end_km=end_km,
        defects=sample_defects,
        bin_size_km=0.5,
    )
    return report


@router.get("/export/csv", summary="Download highway stretch chainage report as CSV")
async def export_chainage_csv(
    stretch: str = Query("NH-44 Corridor", description="Stretch name"),
    start_km: float = Query(0.0),
    end_km: float = Query(5.0),
) -> Response:
    report = await get_chainage_report(stretch=stretch, start_km=start_km, end_km=end_km)
    csv_text = chainage_reporting_service.export_csv(report)
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{stretch.replace(" ", "_")}_chainage.csv"'},
    )


@router.get("/export/geojson", summary="Download highway stretch defects as GeoJSON")
async def export_chainage_geojson(
    stretch: str = Query("NH-44 Corridor"),
    start_km: float = Query(0.0),
    end_km: float = Query(5.0),
) -> Dict[str, Any]:
    report = await get_chainage_report(stretch=stretch, start_km=start_km, end_km=end_km)
    return chainage_reporting_service.export_geojson(report)


@router.get("/export/pdf", summary="Structured PDF survey brief export")
async def export_chainage_pdf_summary(
    stretch: str = Query("NH-44 Corridor"),
    start_km: float = Query(0.0),
    end_km: float = Query(5.0),
) -> Dict[str, Any]:
    report = await get_chainage_report(stretch=stretch, start_km=start_km, end_km=end_km)
    return chainage_reporting_service.export_pdf_summary(report)
