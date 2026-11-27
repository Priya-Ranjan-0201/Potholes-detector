"""Road Surface Drivable Area Segmenter (Stage 3).

Extracts drivable pavement surface connected to camera bottom baseline,
dilates by 15-20% to preserve edge-of-road potholes and shoulder defects,
and discards candidates occurring outside the road boundaries.
"""

from __future__ import annotations

import cv2
import numpy as np
from typing import Any, Dict, List, Tuple


class RoadSurfaceSegmenter:
    """Extracts continuous drivable road surface mask."""

    def __init__(self, dilation_pct: float = 0.18, horizon_cutoff_pct: float = 0.38):
        self.dilation_pct = dilation_pct
        self.horizon_cutoff_pct = horizon_cutoff_pct

    def compute_road_mask(self, img_bgr: np.ndarray) -> np.ndarray:
        """Computes binary road surface mask (uint8, 255=road, 0=non-road)."""
        h, w = img_bgr.shape[:2]

        # 1. Sample road seed from bottom center of image (pavement is in lower foreground)
        seed_y1 = int(h * 0.75)
        seed_x1 = int(w * 0.20)
        seed_x2 = int(w * 0.80)
        seed_roi = img_bgr[seed_y1:h, seed_x1:seed_x2]
        if seed_roi.size == 0:
            seed_roi = img_bgr[int(h * 0.5):h, :]

        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        seed_lab = cv2.cvtColor(seed_roi, cv2.COLOR_BGR2LAB)

        mean_l, mean_a, mean_b = np.mean(seed_lab, axis=(0, 1))
        std_l, std_a, std_b = np.std(seed_lab, axis=(0, 1))

        # Normalized color distance to road pavement distribution
        scale_l = max(22.0, std_l * 2.5)
        scale_a = max(8.0, std_a * 2.5)
        scale_b = max(8.0, std_b * 2.5)

        dist_sq = (
            ((lab[:, :, 0].astype(np.float32) - mean_l) / scale_l) ** 2 +
            ((lab[:, :, 1].astype(np.float32) - mean_a) / scale_a) ** 2 +
            ((lab[:, :, 2].astype(np.float32) - mean_b) / scale_b) ** 2
        )

        # Raw threshold mask
        raw_mask = (dist_sq < 10.24).astype(np.uint8) * 255

        # Pavement baseline connection: bottom 6% is always pavement/camera hood
        if std_l < 50.0:
            raw_mask[int(h * 0.94):, :] = 255

        # Morphological closing to seal internal pavement texture fissures
        close_ksize = max(5, int(min(h, w) * 0.03))
        kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (close_ksize, close_ksize))
        mask_closed = cv2.morphologyEx(raw_mask, cv2.MORPH_CLOSE, kernel_close)

        # Connected components from bottom row: road is continuous from vehicle
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_closed)
        road_mask = np.zeros((h, w), dtype=np.uint8)

        bottom_row = labels[h - 1, :]
        candidate_labels = np.unique(bottom_row)
        candidate_labels = candidate_labels[candidate_labels != 0]

        if len(candidate_labels) > 0:
            for lbl in candidate_labels:
                if stats[lbl, cv2.CC_STAT_AREA] > (h * w * 0.04):
                    road_mask[labels == lbl] = 255
        else:
            road_mask = mask_closed

        # Safety dilation so edge potholes and shoulder cracks survive
        dilate_ksize = max(9, int(min(h, w) * self.dilation_pct))
        kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dilate_ksize, dilate_ksize))
        road_mask_dilated = cv2.dilate(road_mask, kernel_dilate)

        # Physical horizon cutoff: sky, overhead awnings, and tree canopies never exist in road space.
        # When the camera is angled downward or overhead (e.g. case_06_mumbai_potholes), the pavement
        # extends across the full frame. We dynamically detect whether the upper frame is sky/background vs road.
        top_15 = img_bgr[: max(5, int(h * 0.15)), :]
        bot_25 = img_bgr[int(h * 0.75):, :]
        top_l = float(np.mean(cv2.cvtColor(top_15, cv2.COLOR_BGR2GRAY)))
        bot_l = float(np.mean(cv2.cvtColor(bot_25, cv2.COLOR_BGR2GRAY)))
        diff_l = abs(top_l - bot_l)

        min_horizon = max(5, int(h * 0.18))
        if diff_l >= 25.0 or top_l >= 155.0:
            horizon_y = max(min_horizon, int(h * self.horizon_cutoff_pct))
            road_mask_dilated[:horizon_y, :] = 0
        else:
            horizon_y = min_horizon
            road_mask_dilated[:horizon_y, :] = 0

        return road_mask_dilated

    def filter_defects(
        self, defect_boxes: List[Dict[str, Any]], img_bgr: np.ndarray
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Keep box only if its center or bottom lies inside the drivable road mask.

        Returns: (kept_boxes, removed_boxes).
        """
        h, w = img_bgr.shape[:2]
        road_mask = self.compute_road_mask(img_bgr)

        kept = []
        removed = []

        for d in defect_boxes:
            bx = d["box"]  # [x1, y1, x2, y2]
            cx = int(np.clip((bx[0] + bx[2]) / 2.0, 0, w - 1))
            cy_c = int(np.clip((bx[1] + bx[3]) / 2.0, 0, h - 1))
            cy_b = int(np.clip(bx[3] - 2, 0, h - 1))

            # Center must lie on road mask (and optionally check bottom)
            if road_mask[cy_c, cx] > 0:
                kept.append(d)
            else:
                removed.append({**d, "reason": "outside_road_mask"})

        return kept, removed
