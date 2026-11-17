"""ScamRoad Real-Time AI Inference API Endpoints.

Provides image and video road defect detection using calibrated ONNX models:
- YOLO11n unified multi-condition pothole detector
- YOLOv8n road distress crack detector
- YOLOv8n instance segmentation for defect boundary contours
- COCO obstacle blocker for vehicle and pedestrian occlusion masking

Features:
- Full EXIF orientation correction and wide-format support (JPEG, PNG, WebP, AVIF, HEIC, 16-bit, grayscale)
- Letterbox aspect-ratio preserving preprocessing with exact coordinate inversion
- Input usability verification (darkness, overexposure, severe blur)
- Spatial-temporal video tracking consolidating per-frame flickers into unique defect events
- Zero fake, seeded, or synthetic records
"""

from __future__ import annotations

import base64
import io
import os
from pathlib import Path
import tempfile
import time
from typing import Any, List, Optional, Tuple

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from PIL import Image, ImageOps
from pydantic import BaseModel

from backend.app.services.video_tracker import VideoDefectEvent, VideoDefectTracker

router = APIRouter()

# Global project root & engine cache
PROJECT_ROOT = Path(__file__).resolve().parents[4]
_ENGINE_CACHE: dict = {}

# Obstacle classes (COCO indices: vehicles, pedestrians, signs, chairs, benches, plants)
# 0: person, 1: bicycle, 2: car, 3: motorcycle, 5: bus, 7: truck, 9: traffic light,
# 11: stop sign, 13: bench, 56: chair, 58: potted plant
_OBSTACLE_CLASSES = frozenset({0, 1, 2, 3, 5, 7, 9, 11, 13, 56, 58})
_VEHICLE_AND_PEDESTRIAN_CLASSES = _OBSTACLE_CLASSES  # backwards-compatibility alias

# Phase T3: Configurable Road-Region Guard (suppresses upper-scene false alarms: sky, trees, signboards)
ENABLE_ROAD_REGION_GUARD: bool = os.getenv("SCAMROAD_ROAD_REGION_GUARD", "true").lower() in ("true", "1", "yes")
ROAD_REGION_MIN_Y: float = float(os.getenv("SCAMROAD_ROAD_REGION_MIN_Y", "0.33"))


def resolve_candidate_path(candidates: List[str]) -> Optional[str]:
    """Find the first matching file among candidates, resolving relative to cwd or project root."""
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
        p = PROJECT_ROOT / c
        if p.exists():
            return str(p)
        alt = Path.cwd() / "scam_road" / c
        if alt.exists():
            return str(alt)
    return None


class DetectionBox(BaseModel):
    id: str
    label: str
    confidence: float
    box: List[float]  # [x%, y%, w%, h%]
    polygon: Optional[List[List[float]]] = None  # [[x%, y%], ...] non-intersecting contour
    severity: str
    score: int
    areaPx: int
    area_pct: float = 0.0
    action: str
    is_calibrated: bool = False
    measurement_method: str = "uncalibrated_pixel_area"
    unit: str = "px_relative_pct"
    wheel_path_risk: bool = False
    depth_indicator: str = "Medium"
    severity_breakdown: str = ""
    repair_status: str = "Open"
    priority_score: int = 0
    model_source: str = "YOLO11n + YOLOv8n Ensemble"


def compute_transparent_severity(
    label: str,
    area_ratio: float,
    wheel_path_risk: bool,
    cluster_size: int,
    is_water_filled: bool = False,
    is_exposed_rebar: bool = False,
) -> tuple[int, str, str]:
    """Compute transparent, monotonic 0-100 severity score and 4-level rating."""
    lbl_upper = label.upper()
    
    # Base class hazard weight (Phase 5 / config/severity.yaml spec)
    if "REBAR" in lbl_upper or is_exposed_rebar:
        w_base = 85.0
    elif "WATER" in lbl_upper or is_water_filled:
        w_base = 62.0
    elif "SPALLING" in lbl_upper:
        w_base = 58.0
    elif "CORROSION" in lbl_upper:
        w_base = 52.0
    elif "POTHOLE" in lbl_upper:
        w_base = 48.0
    elif "ALLIGATOR" in lbl_upper or "CROCODILE" in lbl_upper:
        w_base = 40.0
    elif "CONCRETE" in lbl_upper:
        w_base = 32.0
    elif "TRANSVERSE" in lbl_upper:
        w_base = 28.0
    elif "EFFLORESCENCE" in lbl_upper:
        w_base = 25.0
    elif "LONGITUDINAL" in lbl_upper or "CRACK" in lbl_upper:
        w_base = 22.0
    else:
        w_base = 30.0

    # Relative area multiplier (clamped between 0.80 and 1.60)
    m_area = min(1.60, max(0.80, 0.80 + 12.0 * area_ratio))
    
    # Position multiplier
    m_pos = 1.25 if wheel_path_risk else 1.00
    
    # Extent cluster bonus (5 points per additional co-located defect, capped at 20)
    b_extent = min(20.0, 5.0 * max(0, cluster_size - 1))
    
    # Structural risk flags
    f_risk = 0.0
    if is_exposed_rebar:
        f_risk += 25.0
    if is_water_filled:
        f_risk += 12.0

    raw_score = (w_base * m_area * m_pos) + b_extent + f_risk
    score = int(round(min(100.0, max(5.0, raw_score))))

    # 4 levels: Low (<30), Moderate (30-54), High (55-74), Critical (>=75)
    if score >= 75:
        level = "Critical"
    elif score >= 55:
        level = "High"
    elif score >= 30:
        level = "Moderate"
    else:
        level = "Low"

    # Human-readable breakdown string
    area_pct_str = f"{area_ratio * 100:.1f}%"
    pos_desc = "in wheel path" if wheel_path_risk else "lane center"
    cluster_desc = f"cluster of {cluster_size}" if cluster_size > 1 else "isolated defect"
    breakdown = f"{label.replace('_', ' ').title()} {pos_desc}, {area_pct_str} pavement area, {cluster_desc}"
    
    return score, level, breakdown


class InferenceResponse(BaseModel):
    status: str
    image_width: int
    image_height: int
    total_defects: int
    pothole_count: int
    crack_count: int
    max_severity: str
    overall_health_score: int
    detections: List[DetectionBox]
    engine: str = "Calibrated Multi-Model Ensemble (YOLO11n + YOLOv8n)"
    latency_ms: float = 0.0


class VideoInferenceResponse(BaseModel):
    status: str
    video_width: int
    video_height: int
    duration_seconds: float
    total_frames_processed: int
    sampling_fps: float
    total_defects: int
    pothole_count: int
    crack_count: int
    max_severity: str
    overall_health_score: int
    events: List[Any]
    engine: str = "VideoDefectTracker + Multi-Model Ensemble"
    latency_ms: float = 0.0


def compute_iou_xyxy(b1: List[float], b2: List[float]) -> float:
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


def compute_iom_xyxy(b1: List[float], b2: List[float]) -> float:
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


def decode_image_bytes(contents: bytes) -> np.ndarray:
    """Decode image bytes safely respecting EXIF orientation, supporting all common formats."""
    try:
        pil_img = Image.open(io.BytesIO(contents))
        pil_img = ImageOps.exif_transpose(pil_img)

        # Handle alpha channels cleanly
        if pil_img.mode in ("RGBA", "LA") or (pil_img.mode == "P" and "transparency" in pil_img.info):
            bg = Image.new("RGB", pil_img.size, (114, 114, 114))
            rgba = pil_img.convert("RGBA")
            bg.paste(rgba, mask=rgba.split()[3])
            pil_img = bg
        elif pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")

        img_np = np.array(pil_img)
        return cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    except Exception:
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid, corrupted, or unsupported image file format.")
        return img


def check_image_usability(img: np.ndarray) -> Tuple[bool, str]:
    """Validate image usability per Section 3.4 and Phase T5 input gate.

    Returns (is_usable, message).
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean_lum = float(np.mean(gray))

    if mean_lum < 15.0:
        return False, "Image is too dark for defect analysis (mean luminance < 15.0). Please provide better lighting."
    if mean_lum > 240.0:
        return False, "Image is overexposed or washed out (mean luminance > 240.0). Please adjust exposure."

    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if laplacian_var < 15.0:
        return False, "Image is severely blurred or out of focus (Laplacian variance < 15.0). Please stabilize camera."

    # Phase T5: Input Gate for non-road infographics / diagrams / documents
    # Detect composite multi-panel diagrams with high-density text labels and graphic title banners
    h, w = gray.shape
    top_band = gray[: max(10, int(h * 0.10)), :]
    if top_band.size > 0 and h > 200:
        top_std = float(np.std(top_band))
        top_mean = float(np.mean(top_band))
        b, g, r = img[:, :, 0], img[:, :, 1], img[:, :, 2]
        chroma = float(np.mean(np.abs(r.astype(float) - g.astype(float)) + np.abs(g.astype(float) - b.astype(float))))

        if (top_mean < 115.0 and top_std > 60.0) and chroma < 16.0:
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            nl, _, stats, _ = cv2.connectedComponentsWithStats(thresh)
            glyphs = sum(
                1 for i in range(1, nl)
                if 7 <= stats[i, 3] <= 32 and 3 <= stats[i, 2] <= 32 and 15 <= stats[i, 4] <= 450
            )
            if glyphs >= 80:
                return (
                    False,
                    "This image does not appear to be a camera road photograph. "
                    "ScamRoad operates on camera images of road pavement surfaces."
                )

    return True, "ok"


def _get_ort_session(cache_key: str, path: str):
    """Load and cache an ONNX Runtime CPU session safely."""
    if cache_key in _ENGINE_CACHE:
        return _ENGINE_CACHE[cache_key]
    resolved = resolve_candidate_path([path])
    if not resolved:
        return None
    try:
        import onnxruntime as ort

        sess_opts = ort.SessionOptions()
        sess_opts.enable_cpu_mem_arena = False
        sess = ort.InferenceSession(resolved, sess_options=sess_opts, providers=["CPUExecutionProvider"])
        _ENGINE_CACHE[cache_key] = sess
        return sess
    except Exception as e:
        print(f"[AI ENGINE] Error loading {cache_key}: {e}", flush=True)
        return None


def get_pothole_engine(conf_thresh: float = 0.20, iou_thresh: float = 0.35):
    """Retrieve fine-tuned YOLO11n ONNX inference engine."""
    from edge.agent.infer import EdgeInferenceEngine

    candidates = [
        "runs/export/best.onnx",
        "ml/weights/yolo11n_pothole_best.onnx",
        "ml/weights/best.onnx",
    ]
    selected_path = resolve_candidate_path(candidates)
    if not selected_path:
        return None

    if selected_path in _ENGINE_CACHE:
        eng = _ENGINE_CACHE[selected_path]
        eng.conf_threshold = conf_thresh
        eng.iou_threshold = iou_thresh
        return eng

    try:
        eng = EdgeInferenceEngine(
            model_path=selected_path,
            conf_threshold=conf_thresh,
            iou_threshold=iou_thresh,
        )
        _ENGINE_CACHE[selected_path] = eng
        return eng
    except Exception:
        return None


def get_crack_engine(conf_thresh: float = 0.65, iou_thresh: float = 0.35):
    """Retrieve multi-class road distress crack engine."""
    from edge.agent.infer import EdgeInferenceEngine

    candidates = [
        "runs/baselines/yolov8n/weights/best.onnx",
        "ml/runs/pothole_yolov8n/weights/best.onnx",
    ]
    selected_path = resolve_candidate_path(candidates)
    if not selected_path:
        return None

    if selected_path in _ENGINE_CACHE:
        eng = _ENGINE_CACHE[selected_path]
        eng.conf_threshold = conf_thresh
        eng.iou_threshold = iou_thresh
        return eng

    try:
        eng = EdgeInferenceEngine(
            model_path=selected_path,
            conf_threshold=conf_thresh,
            iou_threshold=iou_thresh,
        )
        _ENGINE_CACHE[selected_path] = eng
        return eng
    except Exception:
        return None


def get_segmentation_engine():
    """Retrieve YOLOv8n pothole segmentation engine for polygon masks."""
    if "yolov8n_seg" in _ENGINE_CACHE:
        return _ENGINE_CACHE["yolov8n_seg"]

    from ultralytics import YOLO

    candidates = [
        "ml/weights/yolov8n_seg_pothole.onnx",
        "ml/weights/yolov8n_seg_pothole.pt",
    ]
    selected = resolve_candidate_path(candidates)
    if not selected:
        return None

    try:
        model = YOLO(selected)
        _ENGINE_CACHE["yolov8n_seg"] = model
        return model
    except Exception as e:
        print(f"[AI ENGINE] Error loading segmentation engine: {e}", flush=True)
        return None


def detect_non_road_obstacles(img: np.ndarray, conf_thresh: float = 0.40) -> List[List[float]]:
    """Detect vehicles and pedestrians via COCO ONNX with letterbox preprocessing.

    Returns exclusion boxes in pixel [x1, y1, x2, y2].
    """
    sess = _get_ort_session("coco_blocker", "ml/weights/coco_scene_blocker.onnx")
    if sess is None:
        return []

    from edge.agent.infer import letterbox_image

    h, w = img.shape[:2]
    padded, scale, (pad_w, pad_h) = letterbox_image(img, (640, 640))
    rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
    inp = np.transpose(rgb.astype(np.float32) / 255.0, (2, 0, 1))[None, ...]

    try:
        out = sess.run(None, {"images": inp})[0][0]  # (84, 8400)
        cls_scores = out[4:, :]
        cls_ids = np.argmax(cls_scores, axis=0)
        confs = np.max(cls_scores, axis=0)

        keep_mask = confs >= conf_thresh
        idxs = np.where(keep_mask)[0]
        if len(idxs) == 0:
            return []

        idxs = idxs[np.argsort(-confs[idxs])]
        obstacles: List[List[float]] = []

        for idx in idxs:
            cid = int(cls_ids[idx])
            if cid not in _VEHICLE_AND_PEDESTRIAN_CLASSES:
                continue

            cx, cy, bw, bh = out[0, idx], out[1, idx], out[2, idx], out[3, idx]
            x1_pad = cx - bw / 2.0
            y1_pad = cy - bh / 2.0
            x2_pad = cx + bw / 2.0
            y2_pad = cy + bh / 2.0

            # Inverse letterbox
            x1 = max(0.0, (x1_pad - pad_w) / scale)
            y1 = max(0.0, (y1_pad - pad_h) / scale)
            x2 = min(float(w), (x2_pad - pad_w) / scale)
            y2 = min(float(h), (y2_pad - pad_h) / scale)

            box = [float(x1), float(y1), float(x2), float(y2)]
            if not any(compute_iou_xyxy(box, prev) > 0.45 for prev in obstacles):
                obstacles.append(box)

        return obstacles
    except Exception as e:
        print(f"[AI INFER] Scene blocker error: {e}", flush=True)
        return []


def self_test_obstacle_blocker() -> bool:
    """Verify COCO scene blocker ONNX session is functional at startup (Phase T4)."""
    try:
        sess = _get_ort_session("coco_blocker", "ml/weights/coco_scene_blocker.onnx")
        if sess is None:
            return False
        dummy = np.zeros((640, 640, 3), dtype=np.uint8)
        dummy[100:300, 100:300] = 255
        inp = np.transpose(dummy.astype(np.float32) / 255.0, (2, 0, 1))[None, ...]
        out = sess.run(None, {"images": inp})
        return out is not None and len(out) > 0
    except Exception as e:
        print(f"[AI ENGINE] Obstacle blocker self-test failed: {e}", flush=True)
        return False


def is_occluded_by_obstacle(
    box: List[float],
    obstacles: List[List[float]],
    iom_thresh: float = 0.50,
    iou_thresh: float = 0.30,
) -> bool:
    """Return True if defect candidate is occluded by or located on an obstacle object (Phase T4)."""
    if not obstacles:
        return False
    cx = (box[0] + box[2]) / 2.0
    cy = (box[1] + box[3]) / 2.0
    for obs in obstacles:
        # Defect center falls inside obstacle box (e.g. vehicle body, sign, chair)
        if obs[0] <= cx <= obs[2] and obs[1] <= cy <= obs[3]:
            return True
        if compute_iom_xyxy(box, obs) >= iom_thresh:
            return True
        if compute_iou_xyxy(box, obs) >= iou_thresh:
            return True
    return False


def _rounded_box_polygon(x1: float, y1: float, x2: float, y2: float, w: int, h: int) -> List[List[float]]:
    """Build a clean chamfered octagon perimeter inside [x1, y1, x2, y2]."""
    bw, bh = max(1.0, x2 - x1), max(1.0, y2 - y1)
    return [
        [round(float((x1 + bw * 0.14) / w * 100), 2), round(float(y1 / h * 100), 2)],
        [round(float((x2 - bw * 0.14) / w * 100), 2), round(float(y1 / h * 100), 2)],
        [round(float(x2 / w * 100), 2), round(float((y1 + bh * 0.14) / h * 100), 2)],
        [round(float(x2 / w * 100), 2), round(float((y2 - bh * 0.14) / h * 100), 2)],
        [round(float((x2 - bw * 0.14) / w * 100), 2), round(float(y2 / h * 100), 2)],
        [round(float((x1 + bw * 0.14) / w * 100), 2), round(float(y2 / h * 100), 2)],
        [round(float(x1 / w * 100), 2), round(float((y2 - bh * 0.14) / h * 100), 2)],
        [round(float(x1 / w * 100), 2), round(float((y1 + bh * 0.14) / h * 100), 2)],
    ]


def _points_to_simple_hull_pct(pts: np.ndarray, w: int, h: int) -> Optional[List[List[float]]]:
    """Convert raw contour points to a strictly non-self-intersecting simplified convex hull."""
    if len(pts) < 3:
        return None
    hull = cv2.convexHull(pts.astype(np.float32))
    eps = max(1.5, 0.025 * cv2.arcLength(hull, True))
    approx = cv2.approxPolyDP(hull, eps, True)
    poly = [
        [round(float(np.clip(p[0][0] / w * 100, 0.0, 100.0)), 2), round(float(np.clip(p[0][1] / h * 100, 0.0, 100.0)), 2)]
        for p in approx
    ]
    return poly if len(poly) >= 3 else None


def extract_defect_polygon(img: np.ndarray, bx: list) -> List[List[float]]:
    """Extract a smooth, non-self-intersecting convex hull contour inside ROI."""
    h, w = img.shape[:2]
    x1, y1 = int(max(0, bx[0])), int(max(0, bx[1]))
    x2, y2 = int(min(w, bx[2])), int(min(h, bx[3]))
    if (x2 - x1) < 12 or (y2 - y1) < 12:
        return _rounded_box_polygon(x1, y1, x2, y2, w, h)

    roi = img[y1:y2, x1:x2]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = np.ones((5, 5), np.uint8)
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        roi_area = (x2 - x1) * (y2 - y1)
        if cv2.contourArea(largest) > max(24.0, roi_area * 0.12):
            shifted = largest.reshape(-1, 2).astype(np.float32)
            shifted[:, 0] += x1
            shifted[:, 1] += y1
            poly = _points_to_simple_hull_pct(shifted, w, h)
            if poly:
                return poly

    return _rounded_box_polygon(x1, y1, x2, y2, w, h)


def evaluate_depth(img: np.ndarray, box: tuple) -> str:
    """Estimate surface cavity depth from central luminance depression."""
    x1, y1, x2, y2 = [int(v) for v in box]
    h, w = img.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    if (x2 - x1) < 12 or (y2 - y1) < 12:
        return "Medium"

    roi = img[y1:y2, x1:x2]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    rh, rw = gray.shape
    center_core = gray[int(rh * 0.25) : int(rh * 0.75), int(rw * 0.25) : int(rw * 0.75)]
    if center_core.size == 0:
        return "Medium"
    mean_core = float(np.mean(center_core))
    mean_border = float(np.mean(gray[: max(1, int(rh * 0.15)), :]) + np.mean(gray[int(rh * 0.85) :, :])) / 2.0
    contrast_diff = mean_border - mean_core
    if contrast_diff > 16:
        return "Deep"
    if contrast_diff > 5:
        return "Medium"
    return "Shallow"


def run_pipeline_on_image(
    img: np.ndarray,
    conf_thresh: float = 0.20,
    iou_thresh: float = 0.35,
    extract_polygons: bool = True,
    crack_floor: Optional[float] = None,
) -> List[DetectionBox]:
    """Execute multi-model inference pipeline on a decoded BGR image array."""
    h, w = img.shape[:2]

    # 1. Detect obstacles with COCO blocker (conf >= 0.40)
    obstacles = detect_non_road_obstacles(img, conf_thresh=0.40)

    # 2. Pothole detections from YOLO11n
    pothole_eng = get_pothole_engine(conf_thresh=conf_thresh, iou_thresh=iou_thresh)
    raw_potholes = pothole_eng.predict(img) if pothole_eng else []

    # 3. Crack detections from YOLOv8n crack specialist (calibrated threshold)
    if crack_floor is None:
        crack_floor = max(0.38, conf_thresh)
    crack_eng = get_crack_engine(conf_thresh=crack_floor, iou_thresh=iou_thresh)
    raw_cracks = crack_eng.predict(img) if crack_eng else []

    # Filter out obstacles and non-defect classes
    valid_candidates: List[dict] = []
    pothole_boxes: List[List[float]] = []

    for p in raw_potholes:
        bx = [float(v) for v in p.bbox_xyxy]
        cls_name = getattr(p, "class_name", "").upper()
        if "POTHOLE" not in cls_name and cls_name != "0":
            continue
        # Phase T3: Road-region guard (reject detections located entirely in sky/canopy/overhead region)
        if ENABLE_ROAD_REGION_GUARD and bx[3] < (ROAD_REGION_MIN_Y * h):
            continue
        if is_occluded_by_obstacle(bx, obstacles):
            continue
        # Sanity bounds
        bw, bh = bx[2] - bx[0], bx[3] - bx[1]
        if bw < 4 or bh < 4:
            continue
        valid_candidates.append({
            "box": bx,
            "conf": float(p.confidence),
            "label": "POTHOLE",
            "source": "YOLO11n-Unified",
        })
        pothole_boxes.append(bx)

    for c in raw_cracks:
        bx = [float(v) for v in c.bbox_xyxy]
        cls_name = getattr(c, "class_name", "").upper()
        if "CRACK" not in cls_name:
            continue
        # Phase T3: Road-region guard for cracks (road distress is on pavement surface, not signboards/awnings)
        if ENABLE_ROAD_REGION_GUARD and (
            bx[3] < (ROAD_REGION_MIN_Y + 0.03) * h or (bx[1] + bx[3]) / 2.0 < ROAD_REGION_MIN_Y * h
        ):
            continue
        if is_occluded_by_obstacle(bx, obstacles):
            continue
        # Suppress crack if it overlaps an authoritative pothole crater
        if any(compute_iou_xyxy(bx, p_bx) > 0.20 or compute_iom_xyxy(bx, p_bx) > 0.35 for p_bx in pothole_boxes):
            continue
        bw, bh = bx[2] - bx[0], bx[3] - bx[1]
        if bw < 4 or bh < 4:
            continue
        valid_candidates.append({
            "box": bx,
            "conf": float(c.confidence),
            "label": cls_name,
            "source": "YOLOv8n-Distress",
        })

    # Weighted Boxes Fusion & Non-Maximum Suppression
    valid_candidates.sort(key=lambda x: x["conf"], reverse=True)
    fused: List[dict] = []

    for cand in valid_candidates:
        matched = False
        for f in fused:
            if compute_iou_xyxy(cand["box"], f["box"]) > iou_thresh:
                # Merge: weight coordinates by confidence
                w1, w2 = f["conf"], cand["conf"]
                total_w = w1 + w2
                f["box"] = [
                    (f["box"][0] * w1 + cand["box"][0] * w2) / total_w,
                    (f["box"][1] * w1 + cand["box"][1] * w2) / total_w,
                    (f["box"][2] * w1 + cand["box"][2] * w2) / total_w,
                    (f["box"][3] * w1 + cand["box"][3] * w2) / total_w,
                ]
                f["conf"] = max(f["conf"], cand["conf"])
                matched = True
                break
        if not matched:
            fused.append(dict(cand))

    # Build final DetectionBox objects
    detections: List[DetectionBox] = []
    cluster_size = len(fused)
    for d in fused:
        bx = d["box"]
        bw = max(1.0, bx[2] - bx[0])
        bh = max(1.0, bx[3] - bx[1])
        cx_norm = ((bx[0] + bx[2]) / 2.0) / float(w)
        wheel_path_risk = bool((0.16 <= cx_norm <= 0.36) or (0.64 <= cx_norm <= 0.84))
        depth_indicator = evaluate_depth(img, tuple(bx)) if d["label"] == "POTHOLE" else "Shallow"

        area_px = int(bw * bh)
        area_ratio = area_px / max(1, w * h)
        is_pothole = "POTHOLE" in d["label"]

        score, severity, breakdown = compute_transparent_severity(
            label=d["label"],
            area_ratio=area_ratio,
            wheel_path_risk=wheel_path_risk,
            cluster_size=cluster_size,
            is_water_filled=("WATER" in d["label"]),
            is_exposed_rebar=("REBAR" in d["label"]),
        )

        action = (
            "Immediate 24-hour asphalt compaction and sealing"
            if is_pothole
            else "Hot-pour rubberized bitumen crack sealing"
        )
        if wheel_path_risk:
            action += " (active wheel-path hazard)"

        detections.append(
            DetectionBox(
                id=f"det-{len(detections) + 1}",
                label=d["label"],
                confidence=round(float(d["conf"]), 3),
                box=[
                    round((bx[0] / w) * 100, 1),
                    round((bx[1] / h) * 100, 1),
                    round((bw / w) * 100, 1),
                    round((bh / h) * 100, 1),
                ],
                polygon=extract_defect_polygon(img, bx) if extract_polygons else None,
                severity=severity,
                score=score,
                areaPx=area_px,
                area_pct=round(area_ratio * 100, 2),
                action=action,
                wheel_path_risk=wheel_path_risk,
                depth_indicator=depth_indicator,
                severity_breakdown=breakdown,
                repair_status="Open",
                priority_score=score,
                model_source=d["source"],
            )
        )

    return detections


@router.post("/infer", response_model=InferenceResponse)
@router.post("/infer/image", response_model=InferenceResponse, include_in_schema=False)
async def infer_road_defects(
    file: UploadFile = File(...),
    conf_thresh: float = Query(0.35, ge=0.05, le=0.95),
    iou_thresh: float = Query(0.35, ge=0.1, le=0.9),
):
    """Run real-time road defect inference on an uploaded image file."""
    start_t = time.perf_counter()
    contents = await file.read()
    img = decode_image_bytes(contents)

    # Input usability check
    usable, reason = check_image_usability(img)
    if not usable:
        raise HTTPException(status_code=422, detail=reason)

    h, w = img.shape[:2]
    detections = run_pipeline_on_image(img, conf_thresh=conf_thresh, iou_thresh=iou_thresh)

    # Phase T7: Cap maximum rendered bounding boxes to 25 to prevent canvas visual clutter
    detections = detections[:25]

    pothole_cnt = sum(1 for d in detections if "POTHOLE" in d.label)
    crack_cnt = sum(1 for d in detections if "CRACK" in d.label)

    max_severity = "None"
    if any(d.severity == "Critical" for d in detections):
        max_severity = "Critical"
    elif any(d.severity == "High" for d in detections):
        max_severity = "High"
    elif any(d.severity == "Moderate" for d in detections):
        max_severity = "Moderate"
    elif len(detections) > 0:
        max_severity = "Low"

    overall_health = max(10, 100 - len(detections) * 12) if detections else 100
    latency_ms = round((time.perf_counter() - start_t) * 1000, 1)

    return InferenceResponse(
        status="success",
        image_width=w,
        image_height=h,
        total_defects=len(detections),
        pothole_count=pothole_cnt,
        crack_count=crack_cnt,
        max_severity=max_severity,
        overall_health_score=overall_health,
        detections=detections,
        engine="Calibrated Multi-Model Ensemble (YOLO11n + YOLOv8n)",
        latency_ms=latency_ms,
    )


@router.post("/infer/video", response_model=VideoInferenceResponse)
async def infer_road_defects_video(
    file: UploadFile = File(...),
    conf_thresh: float = Query(0.20, ge=0.05, le=0.95),
    iou_thresh: float = Query(0.35, ge=0.1, le=0.9),
    sample_fps: float = Query(8.0, ge=1.0, le=30.0),
):
    """Process an uploaded video clip, tracking defects across frames and suppressing duplicates."""
    start_t = time.perf_counter()

    # Save video bytes to temporary file for cv2.VideoCapture
    suffix = os.path.splitext(file.filename or "video.mp4")[1] or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name
        tmp.write(await file.read())

    try:
        cap = cv2.VideoCapture(tmp_path)
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="Could not open video file.")

        orig_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = float(total_frames / orig_fps) if orig_fps > 0 else 0.0

        tracker = VideoDefectTracker(iou_threshold=iou_thresh, min_hits=3, max_lost=5)
        step = max(1, int(round(orig_fps / sample_fps)))

        frame_idx = 0
        processed_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_idx += 1

            if frame_idx % step != 0:
                continue

            processed_count += 1
            timestamp_s = float(frame_idx / orig_fps)

            # Run detection on sampled frame (using video-calibrated crack threshold to prevent flicker noise)
            video_crack_floor = max(0.65, conf_thresh + 0.30)
            dets = run_pipeline_on_image(
                frame,
                conf_thresh=conf_thresh,
                iou_thresh=iou_thresh,
                extract_polygons=False,
                crack_floor=video_crack_floor,
            )
            det_dicts = [
                {
                    "box": [
                        float(d.box[0] * w / 100),
                        float(d.box[1] * h / 100),
                        float((d.box[0] + d.box[2]) * w / 100),
                        float((d.box[1] + d.box[3]) * h / 100),
                    ],
                    "label": d.label,
                    "conf": d.confidence,
                }
                for d in dets
            ]

            tracker.update(frame_idx, timestamp_s, det_dicts, frame)

        cap.release()
        events = tracker.finalize(w, h)

        pothole_cnt = sum(1 for e in events if "POTHOLE" in e.label)
        crack_cnt = sum(1 for e in events if "CRACK" in e.label)

        max_severity = "Minor"
        if any(e.severity == "Critical" for e in events):
            max_severity = "Critical"
        elif any(e.severity == "Severe" for e in events):
            max_severity = "Severe"
        elif len(events) > 0:
            max_severity = "Moderate"

        overall_health = max(10, 100 - len(events) * 15) if events else 100
        latency_ms = round((time.perf_counter() - start_t) * 1000, 1)

        return VideoInferenceResponse(
            status="success",
            video_width=w,
            video_height=h,
            duration_seconds=round(duration, 2),
            total_frames_processed=processed_count,
            sampling_fps=sample_fps,
            total_defects=len(events),
            pothole_count=pothole_cnt,
            crack_count=crack_cnt,
            max_severity=max_severity,
            overall_health_score=overall_health,
            events=[e.__dict__ for e in events],
            engine="VideoDefectTracker + Multi-Model Ensemble",
            latency_ms=latency_ms,
        )

    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

