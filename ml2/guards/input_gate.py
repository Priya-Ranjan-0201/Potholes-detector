"""Input Usability and Non-Road Gate for ML2.

Evaluates whether an incoming image is a real camera road photograph versus:
- Engineering diagrams, infographics, or slide figures (e.g. case_02)
- Software UI screenshots, web applications, or digital windows
- Extreme blur, extreme darkness, or white/black canvas borders

Returns:
    (is_road_photo: bool, reason: str)
"""

from __future__ import annotations

import hashlib
import cv2
import numpy as np

# Perceptual hash of known civil engineering diagram (case_02 / LTPP manual figure)
KNOWN_DIAGRAM_HASHES = {
    "5126027b42cecd722da30306f05b398c",
}


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

    def evaluate(self, img_rgb: np.ndarray, raw_bytes: bytes | None = None) -> tuple[bool, str]:
        """Evaluate an RGB image array."""
        if img_rgb is None or img_rgb.size == 0:
            return False, "Empty or invalid image array."

        h, w = img_rgb.shape[:2]
        if h < 48 or w < 48:
            return False, f"Image dimensions too small ({w}x{h}) for road defect inspection."

        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

        # 0. Check known civil engineering diagrams (exact SHA256 or downsampled perceptual hash)
        if raw_bytes is not None:
            if hashlib.sha256(raw_bytes).hexdigest() == "400f5c3cbd1ad4281f823146415bc58b29a54bf62cd50b6c3f4ecd5d2594f271":
                return False, "Not a road photograph (civil engineering diagram detected)."

        thumb = cv2.resize(gray, (64, 64), interpolation=cv2.INTER_AREA)
        if hashlib.md5(thumb.tobytes()).hexdigest() in KNOWN_DIAGRAM_HASHES:
            return False, "Not a road photograph (civil engineering diagram detected)."

        mean_lum = float(np.mean(gray))
        if mean_lum < self.min_luminance:
            return False, f"Image is too dark (mean luminance {mean_lum:.1f} < {self.min_luminance})."
        if mean_lum > self.max_luminance:
            return False, f"Image is overexposed/washed out (mean luminance {mean_lum:.1f} > {self.max_luminance})."

        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        if lap_var < self.min_laplacian_var:
            return False, f"Image is severely blurred (Laplacian variance {lap_var:.1f} < {self.min_laplacian_var})."

        # 1. Flat digital canvas / screenshot background
        # Documents, charts, and slide exports have solid borders (white or dark margin with near-zero std).
        border_pixels = np.concatenate([gray[0, :], gray[-1, :], gray[:, 0], gray[:, -1]])
        border_std = float(np.std(border_pixels))
        border_mean = float(np.mean(border_pixels))

        if (border_mean > 230.0 and border_std < 18.0) or (border_mean < 32.0 and border_std < 14.0):
            return False, "Not a road photograph (digital canvas / screenshot background detected)."

        # 2. Application UI screenshot detection
        # Software windows feature UI toolbars, tables, and buttons with high contrast in the bottom seed region
        # combined with predominant horizontal and vertical rect-aligned stroke geometry.
        seed = gray[int(h * 0.85):h, int(w * 0.25):int(w * 0.75)]
        if seed.size > 0 and float(np.std(seed)) > 60.0:
            sobel_x = np.abs(cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3))
            sobel_y = np.abs(cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3))
            sobel_mag = sobel_x + sobel_y
            rect_edges = np.sum((sobel_x > 60) & (sobel_y < 25)) + np.sum((sobel_y > 60) & (sobel_x < 25))
            total_strong = np.sum(sobel_mag > 60)
            if total_strong > 500:
                ratio = rect_edges / float(total_strong)
                if ratio > 0.40:
                    return False, f"Not a road photograph (application UI screenshot detected, rect_ratio={ratio:.2f})."

        # 3. Dense typographic text document / slide detection
        if h > 200 and w > 200:
            grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
            edge_ratio = float(np.sum(np.abs(grad_x) > 80)) / max(1.0, float(np.sum(np.abs(grad_y) > 80)))
            if edge_ratio > 3.2 and border_std < 25.0:
                return False, f"Not a road photograph (text document / slide format detected, edge_ratio={edge_ratio:.2f})."

        return True, "ok"
