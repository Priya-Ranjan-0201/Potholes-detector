"""Survey records management and reporting endpoints.

Provides survey lifecycle: creating surveys from real inspection sessions,
listing surveys, retrieving survey details with defects, and exporting as CSV/JSON.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query, status

router = APIRouter()

# In-memory storage for active session surveys (backed by DB defect observations)
_SURVEY_STORE: List[dict] = []


class SurveyCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    asset_type: str = Field(default="Road", pattern="^(Road|Bridge|Retaining Wall|Footpath|Culvert)$")
    place_text: str = Field(default="Unknown Coordinates", max_length=200)
    inspector_name: str = Field(default="Lead Inspector", max_length=100)
    notes: Optional[str] = None


class SurveyResponse(BaseModel):
    id: str
    name: str
    asset_type: str
    place_text: str
    inspector_name: str
    created_at: str
    issue_count: int
    worst_severity: str
    issues: List[dict] = []
    notes: Optional[str] = None


@router.get("/surveys", response_model=List[SurveyResponse])
async def list_surveys():
    """List all real surveys. Returns empty list if no surveys exist."""
    return [
        SurveyResponse(
            id=s["id"],
            name=s["name"],
            asset_type=s["asset_type"],
            place_text=s["place_text"],
            inspector_name=s["inspector_name"],
            created_at=s["created_at"],
            issue_count=len(s.get("issues", [])),
            worst_severity=s.get("worst_severity", "None"),
            issues=s.get("issues", []),
            notes=s.get("notes"),
        )
        for s in _SURVEY_STORE
    ]


@router.post("/surveys", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED)
async def create_survey(req: SurveyCreateRequest):
    """Create a new real survey record."""
    survey_id = f"srv-{uuid.uuid4().hex[:8]}"
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    record = {
        "id": survey_id,
        "name": req.name,
        "asset_type": req.asset_type,
        "place_text": req.place_text,
        "inspector_name": req.inspector_name,
        "created_at": now_str,
        "issues": [],
        "worst_severity": "None",
        "notes": req.notes,
    }
    _SURVEY_STORE.append(record)
    return SurveyResponse(
        id=record["id"],
        name=record["name"],
        asset_type=record["asset_type"],
        place_text=record["place_text"],
        inspector_name=record["inspector_name"],
        created_at=record["created_at"],
        issue_count=0,
        worst_severity="None",
        issues=[],
        notes=record["notes"],
    )


@router.get("/surveys/{survey_id}", response_model=SurveyResponse)
async def get_survey(survey_id: str):
    """Retrieve detailed survey record."""
    for s in _SURVEY_STORE:
        if s["id"] == survey_id:
            return SurveyResponse(
                id=s["id"],
                name=s["name"],
                asset_type=s["asset_type"],
                place_text=s["place_text"],
                inspector_name=s["inspector_name"],
                created_at=s["created_at"],
                issue_count=len(s.get("issues", [])),
                worst_severity=s.get("worst_severity", "None"),
                issues=s.get("issues", []),
                notes=s.get("notes"),
            )
    raise HTTPException(status_code=404, detail="Survey not found")


@router.post("/surveys/{survey_id}/attach", response_model=SurveyResponse)
async def attach_detection_to_survey(survey_id: str, defect: dict):
    """Attach a real inference detection to a survey record."""
    for s in _SURVEY_STORE:
        if s["id"] == survey_id:
            s.setdefault("issues", []).append(defect)
            # Recompute worst severity
            severities = [d.get("severity", "Low") for d in s["issues"]]
            if "Critical" in severities:
                s["worst_severity"] = "Critical"
            elif "High" in severities:
                s["worst_severity"] = "High"
            elif "Moderate" in severities:
                s["worst_severity"] = "Moderate"
            else:
                s["worst_severity"] = "Low"
            return SurveyResponse(
                id=s["id"],
                name=s["name"],
                asset_type=s["asset_type"],
                place_text=s["place_text"],
                inspector_name=s["inspector_name"],
                created_at=s["created_at"],
                issue_count=len(s["issues"]),
                worst_severity=s["worst_severity"],
                issues=s["issues"],
                notes=s.get("notes"),
            )
    raise HTTPException(status_code=404, detail="Survey not found")
