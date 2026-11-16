"""Video defect tracking service for ScamRoad.

Extracts video frames respecting rotation metadata, runs deep learning defect detection,
tracks candidate defects across consecutive frames using spatial IoU association,
requires minimum track persistence to eliminate flickers, and consolidates tracks
into unique, non-duplicated temporal defect events.
"""

from __future__ import annotations

import base64
import os
import tempfile
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple

import cv2
import numpy as np


def compute_iou_xyxy(b1: List[float] | Tuple[float, ...], b2: List[float] | Tuple[float, ...]) -> float:
    """Compute Intersection-over-Union between two [x1, y1, x2, y2] bounding boxes."""
    x_a = max(b1[0], b2[0])
    y_a = max(b1[1], b2[1])
    x_b = min(b1[2], b2[2])
    y_b = min(b1[3], b2[3])
    inter = max(0.0, x_b - x_a) * max(0.0, y_b - y_a)
    area1 = max(0.0, b1[2] - b1[0]) * max(0.0, b1[3] - b1[1])
    area2 = max(0.0, b2[2] - b2[0]) * max(0.0, b2[3] - b2[1])
    union = area1 + area2 - inter
    return inter / union if union > 0 else 0.0


def compute_iom_xyxy(b1: List[float] | Tuple[float, ...], b2: List[float] | Tuple[float, ...]) -> float:
    """Compute Intersection-over-Minimum-Area between two [x1, y1, x2, y2] boxes."""
    x_a = max(b1[0], b2[0])
    y_a = max(b1[1], b2[1])
    x_b = min(b1[2], b2[2])
    y_b = min(b1[3], b2[3])
    inter = max(0.0, x_b - x_a) * max(0.0, y_b - y_a)
    area1 = max(0.0, b1[2] - b1[0]) * max(0.0, b1[3] - b1[1])
    area2 = max(0.0, b2[2] - b2[0]) * max(0.0, b2[3] - b2[1])
    min_area = min(area1, area2)
    return inter / min_area if min_area > 0 else 0.0


@dataclass
class VideoDefectEvent:
    """Consolidated defect event representing a physical road defect observed across time."""

    event_id: str
    label: str
    severity: str
    score: int
    peak_confidence: float
    mean_confidence: float
    start_frame: int
    end_frame: int
    start_time_s: float
    end_time_s: float
    duration_s: float
    total_detections: int
    best_bbox_pct: List[float]  # [x%, y%, w%, h%]
    best_bbox_px: List[float]   # [x1, y1, x2, y2]
    thumbnail_base64: Optional[str] = None
    action: str = ""


class VideoDefectTracker:
    """Spatial-temporal IoU tracker for consolidating video defect observations."""

    def __init__(
        self,
        iou_threshold: float = 0.20,
        iom_threshold: float = 0.40,
        min_hits: int = 3,
        max_lost: int = 6,
    ) -> None:
        self.iou_threshold = iou_threshold
        self.iom_threshold = iom_threshold
        self.min_hits = min_hits
        self.max_lost = max_lost
        self._next_id = 1
        self._active_tracks: List[dict] = []
        self._confirmed_events: List[dict] = []

    def update(
        self,
        frame_idx: int,
        timestamp_s: float,
        detections: List[dict],
        frame_bgr: np.ndarray,
    ) -> None:
        """Process detections from a single video frame."""
        h, w = frame_bgr.shape[:2]
        matched_track_ids = set()

        for det in detections:
            bbox = det["box"]  # [x1, y1, x2, y2] in pixels
            label = det["label"]
            conf = float(det["conf"])

            # Find best matching active track
            best_track = None
            best_score = 0.0

            for track in self._active_tracks:
                if track["label"] != label:
                    continue
                iou = compute_iou_xyxy(bbox, track["last_bbox"])
                iom = compute_iom_xyxy(bbox, track["last_bbox"])
                match_score = max(iou, iom * 0.7)
                if match_score > max(self.iou_threshold, self.iom_threshold * 0.7) and match_score > best_score:
                    best_score = match_score
                    best_track = track

            if best_track is not None:
                best_track["end_frame"] = frame_idx
                best_track["end_time_s"] = timestamp_s
                best_track["hits"] += 1
                best_track["lost"] = 0
                best_track["last_bbox"] = bbox
                best_track["confs"].append(conf)

                if conf > best_track["peak_conf"]:
                    best_track["peak_conf"] = conf
                    best_track["best_bbox"] = bbox
                    best_track["best_frame"] = frame_bgr.copy()

                matched_track_ids.add(best_track["id"])
            else:
                # Create candidate track
                track_id = f"evt-{self._next_id}"
                self._next_id += 1
                self._active_tracks.append({
                    "id": track_id,
                    "label": label,
                    "start_frame": frame_idx,
                    "end_frame": frame_idx,
                    "start_time_s": timestamp_s,
                    "end_time_s": timestamp_s,
                    "hits": 1,
                    "lost": 0,
                    "last_bbox": bbox,
                    "best_bbox": bbox,
                    "best_frame": frame_bgr.copy(),
                    "peak_conf": conf,
                    "confs": [conf],
                })

        # Age active tracks and finalize lost ones
        surviving_tracks = []
        for track in self._active_tracks:
            if track["id"] not in matched_track_ids:
                track["lost"] += 1

            if track["lost"] >= self.max_lost:
                if track["hits"] >= self.min_hits:
                    self._confirmed_events.append(track)
            else:
                surviving_tracks.append(track)

        self._active_tracks = surviving_tracks

    def finalize(self, frame_w: int, frame_h: int) -> List[VideoDefectEvent]:
        """Flush remaining active tracks and generate consolidated defect events."""
        for track in self._active_tracks:
            if track["hits"] >= self.min_hits:
                self._confirmed_events.append(track)
        self._active_tracks.clear()

        # Deduplicate overlapping events with spatial overlap (regardless of frame gap)
        deduped: List[dict] = []
        for ev in sorted(self._confirmed_events, key=lambda x: (x["hits"], x["peak_conf"]), reverse=True):
            merged_into = None
            for prev in deduped:
                if ev["label"] == prev["label"]:
                    space_iou = compute_iou_xyxy(ev["best_bbox"], prev["best_bbox"])
                    space_iom = compute_iom_xyxy(ev["best_bbox"], prev["best_bbox"])
                    if space_iou > 0.18 or space_iom > 0.35:
                        merged_into = prev
                        break
            if merged_into is not None:
                # Merge track bounds and stats
                merged_into["start_frame"] = min(merged_into["start_frame"], ev["start_frame"])
                merged_into["end_frame"] = max(merged_into["end_frame"], ev["end_frame"])
                merged_into["start_time_s"] = min(merged_into["start_time_s"], ev["start_time_s"])
                merged_into["end_time_s"] = max(merged_into["end_time_s"], ev["end_time_s"])
                merged_into["hits"] += ev["hits"]
                merged_into["confs"].extend(ev["confs"])
                if ev["peak_conf"] > merged_into["peak_conf"]:
                    merged_into["peak_conf"] = ev["peak_conf"]
                    merged_into["best_bbox"] = ev["best_bbox"]
                    if ev.get("best_frame") is not None:
                        merged_into["best_frame"] = ev["best_frame"]
            else:
                deduped.append(ev)

        events: List[VideoDefectEvent] = []
        for ev in deduped:
            bx = ev["best_bbox"]
            bw = max(1.0, bx[2] - bx[0])
            bh = max(1.0, bx[3] - bx[1])
            area_px = int(bw * bh)
            area_ratio = area_px / max(1, frame_w * frame_h)

            is_pothole = "POTHOLE" in ev["label"].upper()
            score = min(
                100,
                max(
                    15,
                    (45 if is_pothole else 35) + min(40, int(area_ratio * 400)),
                ),
            )
            severity = "Critical" if score >= 70 else ("Severe" if score >= 50 else "Moderate")
            action = (
                "Immediate 24-hour asphalt compaction and sealing"
                if is_pothole
                else "Hot-pour rubberized bitumen crack sealing"
            )

            # Generate thumbnail JPEG
            thumbnail_b64 = None
            if ev.get("best_frame") is not None:
                bf = ev["best_frame"]
                x1 = int(max(0, bx[0] - bw * 0.15))
                y1 = int(max(0, bx[1] - bh * 0.15))
                x2 = int(min(frame_w, bx[2] + bw * 0.15))
                y2 = int(min(frame_h, bx[3] + bh * 0.15))
                crop = bf[y1:y2, x1:x2]
                if crop.size > 0:
                    thumb = cv2.resize(crop, (160, 120))
                    _, buf = cv2.imencode(".jpg", thumb, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    thumbnail_b64 = f"data:image/jpeg;base64,{base64.b64encode(buf).decode('ascii')}"

            dur = round(max(0.0, ev["end_time_s"] - ev["start_time_s"]), 2)
            events.append(
                VideoDefectEvent(
                    event_id=ev["id"],
                    label=ev["label"],
                    severity=severity,
                    score=score,
                    peak_confidence=round(float(ev["peak_conf"]), 3),
                    mean_confidence=round(float(np.mean(ev["confs"])), 3),
                    start_frame=ev["start_frame"],
                    end_frame=ev["end_frame"],
                    start_time_s=round(ev["start_time_s"], 2),
                    end_time_s=round(ev["end_time_s"], 2),
                    duration_s=dur,
                    total_detections=ev["hits"],
                    best_bbox_pct=[
                        round((bx[0] / frame_w) * 100, 1),
                        round((bx[1] / frame_h) * 100, 1),
                        round((bw / frame_w) * 100, 1),
                        round((bh / frame_h) * 100, 1),
                    ],
                    best_bbox_px=[round(v, 1) for v in bx],
                    thumbnail_base64=thumbnail_b64,
                    action=action,
                )
            )

        events.sort(key=lambda e: e.start_time_s)
        return events
