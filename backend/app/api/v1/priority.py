"""Repair prioritization ranking API.

Computes priority score = severity x exposure (using user-entered context).
Provides ranked defect lists with tie-breaking, filters, and CSV export.
"""

from __future__ import annotations

import csv
import io
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Query, Response
from backend.app.api.v1.surveys import _SURVEY_STORE

router = APIRouter()


class PriorityItem(BaseModel):
    id: str
    survey_id: str
    survey_name: str
    asset_type: str
    place_text: str
    label: str
    severity_level: str
    severity_score: int
    exposure_factor: float
    priority_score: int
    reason: str
    repair_status: str
    created_at: str


@router.get("/priority", response_model=List[PriorityItem])
async def get_priority_list(
    asset_type: Optional[str] = Query(None),
    min_severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    """Retrieve ranked defects for maintenance prioritization."""
    items: List[PriorityItem] = []

    # Iterate through real survey store defects
    for survey in _SURVEY_STORE:
        for idx, issue in enumerate(survey.get("issues", [])):
            s_level = issue.get("severity", "Low")
            s_score = int(issue.get("score", 20))
            
            # Exposure factor from asset type (or default 1.0)
            a_type = survey.get("asset_type", "Road")
            exp_factor = 1.5 if a_type == "Bridge" else (1.2 if a_type == "Road" else 1.0)
            p_score = int(round(s_score * exp_factor))
            
            r_status = issue.get("repair_status", "Open")
            
            # Filters
            if asset_type and a_type.lower() != asset_type.lower():
                continue
            if min_severity and s_level.lower() != min_severity.lower():
                continue
            if status and r_status.lower() != status.lower():
                continue

            items.append(
                PriorityItem(
                    id=issue.get("id", f"{survey['id']}-d{idx+1}"),
                    survey_id=survey["id"],
                    survey_name=survey["name"],
                    asset_type=a_type,
                    place_text=survey["place_text"],
                    label=issue.get("label", "Distress"),
                    severity_level=s_level,
                    severity_score=s_score,
                    exposure_factor=exp_factor,
                    priority_score=p_score,
                    reason=issue.get("severity_breakdown") or f"{s_level} severity {a_type.lower()} distress",
                    repair_status=r_status,
                    created_at=survey["created_at"],
                )
            )

    # Sort descending by priority score, breaking ties by severity score
    items.sort(key=lambda x: (x.priority_score, x.severity_score), reverse=True)
    return items


@router.get("/priority/export/csv")
async def export_priority_csv():
    """Export the ranked priority list as a standard CSV file."""
    items = await get_priority_list()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Priority Rank", "Defect ID", "Survey Name", "Asset Type", "Location",
        "Defect Class", "Severity Level", "Severity Score (0-100)",
        "Exposure Factor", "Priority Score", "Repair Status", "Reason"
    ])
    for rank, it in enumerate(items, start=1):
        writer.writerow([
            rank, it.id, it.survey_name, it.asset_type, it.place_text,
            it.label, it.severity_level, it.severity_score,
            it.exposure_factor, it.priority_score, it.repair_status, it.reason
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=priority_maintenance_list.csv"}
    )
