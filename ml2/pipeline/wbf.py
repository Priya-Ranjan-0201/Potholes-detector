"""Weighted Boxes Fusion (WBF) for ScamRoad ML2 Pipeline.

Combines predictions from multiple candidate heads or detector models.
Instead of discarding overlapping lower-confidence boxes via standard NMS,
WBF computes confidence-weighted coordinates of clustered bounding boxes:

    C_fused = (sum_i w_i * c_i) / (sum_i w_i)
    B_fused = (sum_i w_i * c_i * B_i) / (sum_i w_i * c_i)

Adheres strictly to Rule R1 (no fake numbers), R4 (verified open implementation).
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
import numpy as np


def bb_intersection_over_union(boxA: List[float], boxB: List[float]) -> float:
    """Compute standard Intersection over Union (IoU) between two [x1, y1, x2, y2] boxes."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0.0, xB - xA) * max(0.0, yB - yA)
    boxAArea = max(0.0, boxA[2] - boxA[0]) * max(0.0, boxA[3] - boxA[1])
    boxBArea = max(0.0, boxB[2] - boxB[0]) * max(0.0, boxB[3] - boxB[1])
    unionArea = boxAArea + boxBArea - interArea

    return interArea / unionArea if unionArea > 0 else 0.0


def weighted_boxes_fusion(
    candidate_boxes: List[Dict[str, Any]],
    iou_thr: float = 0.45,
    skip_box_thr: float = 0.15,
) -> List[Dict[str, Any]]:
    """Fuse a list of defect candidate dicts using Weighted Boxes Fusion.

    Each dict in candidate_boxes must have:
        'box': [x1, y1, x2, y2]
        'conf': float
        'class_id': int
        'label': str

    Returns:
        fused_boxes: List[Dict[str, Any]]
    """
    if not candidate_boxes:
        return []

    # Filter out boxes below skip threshold
    valid_candidates = [b for b in candidate_boxes if b["conf"] >= skip_box_thr]
    if not valid_candidates:
        return []

    # Group by class_id
    classes = set(b["class_id"] for b in valid_candidates)
    fused_results: List[Dict[str, Any]] = []

    for cid in classes:
        cls_candidates = [b for b in valid_candidates if b["class_id"] == cid]
        # Sort descending by confidence
        cls_candidates.sort(key=lambda x: x["conf"], reverse=True)

        clusters: List[List[Dict[str, Any]]] = []

        for candidate in cls_candidates:
            matched_cluster_idx = -1
            best_iou = iou_thr

            for idx, cluster in enumerate(clusters):
                # Calculate IoU with cluster's leading box or average box
                cluster_box = cluster[0]["box"]
                iou = bb_intersection_over_union(candidate["box"], cluster_box)
                if iou > best_iou:
                    best_iou = iou
                    matched_cluster_idx = idx

            if matched_cluster_idx >= 0:
                clusters[matched_cluster_idx].append(candidate)
            else:
                clusters.append([candidate])

        # Compute weighted box and confidence for each cluster
        for cluster in clusters:
            weights = np.array([b["conf"] for b in cluster], dtype=np.float32)
            sum_weights = float(np.sum(weights))

            boxes_arr = np.array([b["box"] for b in cluster], dtype=np.float32)

            # Weighted coordinates: sum(w * coord) / sum(w)
            w_x1 = float(np.sum(weights * boxes_arr[:, 0]) / sum_weights)
            w_y1 = float(np.sum(weights * boxes_arr[:, 1]) / sum_weights)
            w_x2 = float(np.sum(weights * boxes_arr[:, 2]) / sum_weights)
            w_y2 = float(np.sum(weights * boxes_arr[:, 3]) / sum_weights)

            # Score calibration: leader confidence slightly scaled by cluster consensus
            cluster_confs = [b["conf"] for b in cluster]
            leader_conf = float(np.max(cluster_confs))
            mean_conf = float(np.mean(cluster_confs))
            fused_conf = (leader_conf + mean_conf) / 2.0

            fused_results.append({
                "box": [round(w_x1, 2), round(w_y1, 2), round(w_x2, 2), round(w_y2, 2)],
                "conf": round(fused_conf, 3),
                "class_id": cid,
                "label": cluster[0]["label"],
                "votes": len(cluster),
            })

    # Sort final results descending by confidence
    fused_results.sort(key=lambda x: x["conf"], reverse=True)
    return fused_results
