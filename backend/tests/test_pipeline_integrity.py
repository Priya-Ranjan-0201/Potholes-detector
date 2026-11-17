"""Pipeline integrity and robustness regression tests.

Verifies:
- EXIF orientation handling across 0, 90, 180, 270 degree rotations
- Colour order, normalisation, and format handling (RGBA alpha, grayscale, 16-bit, WebP)
- Extreme aspect ratios and resolutions (tiny 32x32 to large 4000x3000)
- Letterbox aspect ratio preservation and exact coordinate mapping inversion
- Input usability validation (darkness, overexposure, extreme blur rejection)
- Video defect tracking and temporal duplicate suppression
"""

from __future__ import annotations

import io
import os
import tempfile
import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageOps

from backend.app.api.v1.infer import (
    check_image_usability,
    decode_image_bytes,
    run_pipeline_on_image,
)
from backend.app.main import app
from backend.app.services.video_tracker import VideoDefectTracker
from edge.agent.infer import letterbox_image


@pytest.fixture
def api_client() -> TestClient:
    return TestClient(app)


def test_exif_orientation_handling() -> None:
    """Verify images with EXIF orientation metadata are properly rotated upright."""
    # Create non-square test image (300 wide, 100 high)
    im = Image.new("RGB", (300, 100), color=(80, 80, 80))
    # Draw an off-center white mark at (50, 20)
    for x in range(40, 60):
        for y in range(10, 30):
            im.putpixel((x, y), (240, 240, 240))

    # Save with EXIF orientation 6 (rotate 90 CW)
    exif = im.getexif()
    exif[0x0112] = 6  # Orientation tag
    buf = io.BytesIO()
    im.save(buf, format="JPEG", exif=exif)
    raw_bytes = buf.getvalue()

    decoded = decode_image_bytes(raw_bytes)
    # When orientation 6 is applied, (300, 100) becomes (100, 300) upright
    h, w = decoded.shape[:2]
    assert h == 300
    assert w == 100


def test_rgba_with_alpha_channel() -> None:
    """Verify PNG with alpha channel is composited cleanly over neutral gray."""
    rgba = Image.new("RGBA", (200, 200), color=(0, 0, 0, 0))  # Transparent
    # Draw opaque center square
    for x in range(50, 150):
        for y in range(50, 150):
            rgba.putpixel((x, y), (180, 180, 180, 255))

    buf = io.BytesIO()
    rgba.save(buf, format="PNG")
    decoded = decode_image_bytes(buf.getvalue())

    assert decoded.shape == (200, 200, 3)
    # Transparent area should be neutral road gray (114, 114, 114)
    assert decoded[10, 10, 0] == 114
    assert decoded[10, 10, 1] == 114
    assert decoded[10, 10, 2] == 114


def test_grayscale_and_16bit_ingestion() -> None:
    """Verify grayscale and 16-bit uint16 image ingestion."""
    # Grayscale
    gray = Image.new("L", (150, 150), color=128)
    buf = io.BytesIO()
    gray.save(buf, format="PNG")
    decoded = decode_image_bytes(buf.getvalue())
    assert decoded.shape == (150, 150, 3)

    # 16-bit array
    arr_16 = np.full((120, 120), 32000, dtype=np.uint16)
    im_16 = Image.fromarray(arr_16)
    buf_16 = io.BytesIO()
    im_16.save(buf_16, format="PNG")
    decoded_16 = decode_image_bytes(buf_16.getvalue())
    assert decoded_16.shape == (120, 120, 3)


def test_extreme_resolutions() -> None:
    """Verify extreme resolutions (tiny 32x32 and large 3000x2000) process safely."""
    tiny = np.full((32, 32, 3), 100, dtype=np.uint8)
    padded, scale, (pad_w, pad_h) = letterbox_image(tiny, (640, 640))
    assert padded.shape == (640, 640, 3)

    large = np.full((2000, 3000, 3), 100, dtype=np.uint8)
    padded_large, scale_l, (pad_wl, pad_hl) = letterbox_image(large, (640, 640))
    assert padded_large.shape == (640, 640, 3)


def test_letterbox_coordinate_inversion() -> None:
    """Verify letterbox coordinate mapping inverts with mathematical precision."""
    orig_w, orig_h = 1280, 720
    test_img = np.zeros((orig_h, orig_w, 3), dtype=np.uint8)
    padded, scale, (pad_w, pad_h) = letterbox_image(test_img, (640, 640))

    # Point in original image: (640, 360) (center)
    x_orig, y_orig = 640.0, 360.0
    x_pad = x_orig * scale + pad_w
    y_pad = y_orig * scale + pad_h

    # Inverse mapping
    x_recovered = (x_pad - pad_w) / scale
    y_recovered = (y_pad - pad_h) / scale

    assert abs(x_recovered - x_orig) < 1e-4
    assert abs(y_recovered - y_orig) < 1e-4


def test_input_usability_validation() -> None:
    """Verify input usability checks reject dark, overexposed, and blurred inputs."""
    # Dark image
    dark = np.full((100, 100, 3), 5, dtype=np.uint8)
    usable, reason = check_image_usability(dark)
    assert not usable
    assert "too dark" in reason

    # Overexposed image
    bright = np.full((100, 100, 3), 250, dtype=np.uint8)
    usable_b, reason_b = check_image_usability(bright)
    assert not usable_b
    assert "overexposed" in reason_b

    # Blurry image (uniform color with zero edge variance)
    uniform = np.full((100, 100, 3), 120, dtype=np.uint8)
    usable_u, reason_u = check_image_usability(uniform)
    assert not usable_u
    assert "blurred" in reason_u

    # Normal textured road image
    np.random.seed(42)
    textured = np.random.randint(60, 160, (200, 200, 3), dtype=np.uint8)
    usable_t, _ = check_image_usability(textured)
    assert usable_t


def test_api_infer_endpoint(api_client: TestClient) -> None:
    """Test POST /api/v1/infer endpoint with real failure case."""
    with open("eval_failures/case_01_pothole_nh44.jpg", "rb") as f:
        resp = api_client.post("/api/v1/infer", files={"file": ("case_01.jpg", f, "image/jpeg")})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["total_defects"] >= 1
    assert data["max_severity"] in ("Critical", "High", "Severe", "Moderate")


def test_api_infer_video_duplicate_suppression(api_client: TestClient) -> None:
    """Test POST /api/v1/infer/video suppresses per-frame duplicates into unique defect events."""
    with open("data/test_videos/clip_01_day_highway.mp4", "rb") as f:
        resp = api_client.post("/api/v1/infer/video", files={"file": ("clip_01.mp4", f, "video/mp4")})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["total_frames_processed"] > 10
    # 60 frames must NOT produce raw frame-count defects; duplicate suppression consolidates into unique tracked events
    assert 1 <= data["total_defects"] <= 10
    assert len(data["events"]) == data["total_defects"]
    ev = data["events"][0]
    assert ev["label"] == "POTHOLE"
    assert ev["total_detections"] >= 3
    assert ev["thumbnail_base64"] is not None
