"""Confidence Triage and Human Review Queue Service (Gate E).

Implements Gate E requirements:
- Auto-accept detections above T_high (>= 0.65).
- Route detections between T_low (>= 0.25) and T_high (< 0.65) to reviewer queue.
- Discard candidate detections below T_low (< 0.25).
- Reviewer actions: confirm, reject, edit_bbox, change_class.
- Persist all reviewer decisions with audit trail.

Rule R1: Real authentic decision persistence.
Rule R3: Not an official government system. Not safety-certified.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

REPO_ROOT = Path(__file__).resolve().parents[3]
REVIEW_STORE_DIR = REPO_ROOT / "data" / "review_store"
DECISIONS_FILE = REVIEW_STORE_DIR / "review_decisions.json"
REVIEW_STORE_DIR.mkdir(parents=True, exist_ok=True)


class ConfidenceTriageService:
    """Confidence triage and human review lifecycle manager."""

    def __init__(self, t_high: float = 0.65, t_low: float = 0.25):
        self.t_high = t_high
        self.t_low = t_low
        self._init_store()

    def _init_store(self):
        if not DECISIONS_FILE.exists():
            DECISIONS_FILE.write_text(json.dumps([], indent=2), encoding="utf-8")

    def triage_detection(self, detection: Dict[str, Any]) -> Dict[str, Any]:
        """Triage an incoming detection based on confidence score."""
        conf = float(detection.get("conf", detection.get("confidence", 0.0)))
        defect_id = str(detection.get("defect_id", uuid.uuid4()))

        if conf >= self.t_high:
            action = "AUTO_ACCEPTED"
            status = "CONFIRMED"
        elif conf >= self.t_low:
            action = "REVIEW_QUEUE"
            status = "PENDING_REVIEW"
        else:
            action = "AUTO_DROPPED"
            status = "DROPPED"

        return {
            "defect_id": defect_id,
            "label": detection.get("label", "POTHOLE"),
            "box": detection.get("box", [0, 0, 0, 0]),
            "confidence": conf,
            "triage_action": action,
            "status": status,
            "t_high": self.t_high,
            "t_low": self.t_low,
            "triaged_at": datetime.now(UTC).isoformat(),
        }

    def record_decision(
        self,
        defect_id: str,
        reviewer_id: str,
        decision: str,  # "confirm", "reject", "edit"
        notes: str = "",
        edited_box: Optional[List[float]] = None,
        corrected_label: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record human reviewer decision and update audit log."""
        if decision not in ("confirm", "reject", "edit"):
            raise ValueError(f"Invalid review decision: {decision}")

        record = {
            "decision_id": str(uuid.uuid4()),
            "defect_id": defect_id,
            "reviewer_id": reviewer_id,
            "decision": decision,
            "notes": notes,
            "edited_box": edited_box,
            "corrected_label": corrected_label,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Append to persistent store
        try:
            with open(DECISIONS_FILE, "r", encoding="utf-8") as f:
                decisions = json.load(f)
        except Exception:
            decisions = []

        decisions.append(record)
        with open(DECISIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(decisions, f, indent=2)

        return record

    def list_decisions(self) -> List[Dict[str, Any]]:
        """List all recorded human review decisions."""
        try:
            with open(DECISIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []


triage_service = ConfidenceTriageService()
