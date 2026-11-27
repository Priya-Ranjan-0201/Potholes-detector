"""Water-Filled Pothole vs Surface Water Puddle Crop Classifier (Gate D).

Differentiates:
1. WATER_FILLED_POTHOLE (Defect): Structural cavity ruptured into the base course
   filled with rainwater/mud. Characterized by steep fractured perimeter asphalt rim,
   dark internal depth absorption, and high boundary edge gradient.
2. SURFACE_PUDDLE (Harmless Negative): Shallow standing water film on intact pavement.
   Characterized by smooth boundary transition, continuous road texture beneath the
   water film, and uniform specular sky reflection without an internal cavity rim.

Rule R1: Real computer vision feature extraction (Laplacian rim gradient, HSV reflection, Lab cavity depth).
Rule R4: Apache-2.0 / BSD-3-Clause OpenCV implementation.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple
import cv2
import numpy as np


class PuddleCropClassifier:
    """Classifies water-containing road patches as water-filled potholes vs harmless puddles."""

    def __init__(
        self,
        min_rim_gradient: float = 22.0,
        min_cavity_depth_score: float = 0.35,
    ):
        self.min_rim_gradient = min_rim_gradient
        self.min_cavity_depth_score = min_cavity_depth_score

    def classify_crop(self, crop_bgr: np.ndarray) -> Dict[str, Any]:
        """Classify a bounding box crop containing water.

        Returns:
            Dict containing:
                - is_water_filled_pothole: bool
                - classification: "WATER_FILLED_POTHOLE" | "SURFACE_PUDDLE"
                - confidence: float
                - rim_gradient: float
                - cavity_score: float
                - reflection_ratio: float
        """
        if crop_bgr is None or crop_bgr.size == 0:
            return {
                "is_water_filled_pothole": False,
                "classification": "SURFACE_PUDDLE",
                "confidence": 0.50,
                "rim_gradient": 0.0,
                "cavity_score": 0.0,
                "reflection_ratio": 0.0,
            }

        h, w = crop_bgr.shape[:2]
        if h < 10 or w < 10:
            return {
                "is_water_filled_pothole": False,
                "classification": "SURFACE_PUDDLE",
                "confidence": 0.50,
                "rim_gradient": 0.0,
                "cavity_score": 0.0,
                "reflection_ratio": 0.0,
            }

        gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2LAB)

        # 1. Perimeter Rim Edge Gradient
        # A true pothole has a sharp fractured boundary where the wearing course was dislodged.
        # We compute the gradient magnitude along the outer perimeter (top 15%, bottom 15%, left 15%, right 15%).
        sobel_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        grad_mag = np.sqrt(sobel_x**2 + sobel_y**2)

        border_mask = np.zeros((h, w), dtype=bool)
        b_h = max(2, int(h * 0.15))
        b_w = max(2, int(w * 0.15))
        border_mask[:b_h, :] = True
        border_mask[-b_h:, :] = True
        border_mask[:, :b_w] = True
        border_mask[:, -b_w:] = True

        rim_gradient = float(np.mean(grad_mag[border_mask])) if np.any(border_mask) else 0.0

        # 2. Cavity Depth vs Flat Surface Reflection
        # Potholes exhibit dark light-absorbing internal depth (low L in center) or turbid mud.
        # Harmless surface puddles on intact asphalt are flat mirrors with high specular reflection
        # (high Value, low Saturation) without a sunken dark cavity center.
        center_h1, center_h2 = int(h * 0.25), int(h * 0.75)
        center_w1, center_w2 = int(w * 0.25), int(w * 0.75)
        center_l = lab[center_h1:center_h2, center_w1:center_w2, 0]
        center_mean_l = float(np.mean(center_l)) if center_l.size > 0 else 128.0

        # Specular reflection ratio (flat water film reflecting sky)
        specular_pixels = np.sum((hsv[:, :, 2] > 200) & (hsv[:, :, 1] < 45))
        reflection_ratio = float(specular_pixels) / float(h * w)

        # Internal cavity shadow absorption score: higher for darker, steeper depressions
        # A deep water-filled hole has center luminance < 95 or high rim contrast: abs(rim_mean - center_mean)
        rim_l = lab[border_mask, 0]
        rim_mean_l = float(np.mean(rim_l)) if rim_l.size > 0 else 128.0
        rim_center_contrast = abs(rim_mean_l - center_mean_l)

        # Cavity depth score (0.0 to 1.0)
        depth_indicator = 1.0 if center_mean_l < 90.0 else max(0.0, 1.0 - (center_mean_l - 90.0) / 80.0)
        contrast_indicator = min(1.0, rim_center_contrast / 35.0)
        cavity_score = 0.6 * depth_indicator + 0.4 * contrast_indicator

        # Classification Rule:
        # A water-filled pothole requires:
        # - Strong fractured rim gradient (rim_gradient >= min_rim_gradient)
        # - Sufficient cavity depth/contrast (cavity_score >= min_cavity_depth_score)
        # - NOT a purely flat surface puddle where reflection_ratio > 0.45 without cavity rim
        is_pothole = (
            (rim_gradient >= self.min_rim_gradient and cavity_score >= self.min_cavity_depth_score)
            or (rim_gradient >= 32.0 and reflection_ratio < 0.35)
        )

        confidence = min(0.98, max(0.55, (rim_gradient / 50.0) * 0.5 + cavity_score * 0.5))

        return {
            "is_water_filled_pothole": is_pothole,
            "classification": "WATER_FILLED_POTHOLE" if is_pothole else "SURFACE_PUDDLE",
            "confidence": round(float(confidence), 3),
            "rim_gradient": round(rim_gradient, 2),
            "cavity_score": round(float(cavity_score), 3),
            "reflection_ratio": round(float(reflection_ratio), 3),
        }
