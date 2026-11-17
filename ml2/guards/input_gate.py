"""Input Usability and Non-Road Gate for ML2.

Evaluates whether an incoming image is a real camera road photograph versus:
- Engineering diagrams, infographics, or slide figures (e.g. case_02)
- Software UI screenshots, web applications, or digital windows
- Extreme blur, extreme darkness, or white/black canvas borders

Returns:
    (is_road_photo: bool, reason: str)
"""

from __future__ import annotations

import cv2
import numpy as np


class InputGate:
    """Non-road infographic, diagram, and digital screenshot gate."""

    def __init__(
        self,
        min_luminance: float = 15.0,
        max_luminance: float = 245.0,
        min_laplacian_var: float = 15.0,
        glyph_threshold: int = 35,
    ):
        self.min_luminance = min_luminance
        self.max_luminance = max_luminance
        self.min_laplacian_var = min_laplacian_var
        self.glyph_threshold = glyph_threshold

    def evaluate(self, img_rgb: np.ndarray) -> tuple[bool, str]:
        """Evaluate an RGB image array."""
        if img_rgb is None or img_rgb.size == 0:
            return False, "Empty or invalid image array."

        h, w = img_rgb.shape[:2]
        if h < 48 or w < 48:
            return False, f"Image dimensions too small ({w}x{h}) for road defect inspection."

        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        mean_lum = float(np.mean(gray))

        if mean_lum < self.min_luminance:
            return False, f"Image is too dark (mean luminance {mean_lum:.1f} < {self.min_luminance})."
        if mean_lum > self.max_luminance:
            return False, f"Image is overexposed/washed out (mean luminance {mean_lum:.1f} > {self.max_luminance})."

        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        if lap_var < self.min_laplacian_var:
            return False, f"Image is severely blurred (Laplacian variance {lap_var:.1f} < {self.min_laplacian_var})."

        # 1. Flat digital canvas / screenshot background
        # Real camera road photos have natural vignetting, perspective lighting, and organic edges.
        # Documents and slides have solid borders (white or dark margin with near-zero std).
        border_pixels = np.concatenate([gray[0, :], gray[-1, :], gray[:, 0], gray[:, -1]])
        border_std = float(np.std(border_pixels))
        border_mean = float(np.mean(border_pixels))

        if (border_mean > 230.0 and border_std < 15.0) or (border_mean < 25.0 and border_std < 10.0):
            return False, "Not a road photograph (digital canvas / screenshot background detected)."

        # 2. Civil distress diagram / Infographic detection
        # Multi-panel figures contain:
        # (a) Header title banner in upper 12% of frame
        # (b) High density of typographic text glyphs / labels across the image
        top_band = gray[: max(10, int(h * 0.12)), :]
        if top_band.size > 0 and h > 150:
            top_std = float(np.std(top_band))
            top_mean = float(np.mean(top_band))

            # Color saturation across image
            r, g, b = img_rgb[:, :, 0], img_rgb[:, :, 1], img_rgb[:, :, 2]
            chroma = float(np.mean(np.abs(r.astype(float) - g.astype(float)) + np.abs(g.astype(float) - b.astype(float))))

            # If top band is a graphic title bar with contrast
            if (top_mean < 125.0 and top_std > 45.0) and chroma < 22.0:
                # Count isolated text glyph components
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                nl, _, stats, _ = cv2.connectedComponentsWithStats(thresh)
                glyphs = sum(
                    1
                    for i in range(1, nl)
                    if 6 <= stats[i, cv2.CC_STAT_HEIGHT] <= 42
                    and 3 <= stats[i, cv2.CC_STAT_WIDTH] <= 42
                    and 12 <= stats[i, cv2.CC_STAT_AREA] <= 500
                )
                if glyphs >= self.glyph_threshold:
                    return False, f"Not a road photograph (civil engineering diagram detected, glyphs={glyphs})."

        # 3. Dense typographic text document / slide detection
        # Check global text glyph count across the entire image
        if h > 200 and w > 200:
            # High frequency horizontal gradient transitions typical of font lines
            grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
            edge_ratio = float(np.sum(np.abs(grad_x) > 80)) / max(1.0, float(np.sum(np.abs(grad_y) > 80)))
            
            # Text lines have strong vertical strokes yielding edge_ratio > 2.2 on clean documents
            if edge_ratio > 2.8 and border_std < 30.0:
                return False, f"Not a road photograph (text document / slide format detected, edge_ratio={edge_ratio:.2f})."

        return True, "ok"
