"""Ablation experiment measuring Guard A (Road Surface Prior) on the benchmark.

Measures:
1. False alarms off-road dropped (on clutter scenes with trees, signboards, sky, buildings)
2. True road damage kept (on damage benchmark images)
"""

import os
import sys
import json
import cv2
import numpy as np

sys.path.insert(0, os.path.abspath("."))
from edge.agent.infer import EdgeInferenceEngine
from ml.guard.road_guards import compute_road_surface_mask, filter_boxes_by_road_mask

def main():
    bench_dir = "data/rescue_benchmark"
    img_dir = os.path.join(bench_dir, "images")
    with open(os.path.join(bench_dir, "manifest.json"), "r") as f:
        manifest = json.load(f)
    records = manifest["records"]
    
    model_path = "runs/rescue_train/yolo11n_rescue/weights/best.onnx"
    eng = EdgeInferenceEngine(model_path, conf_threshold=0.20, iou_threshold=0.35)
    
    damage_recs = [r for r in records if r["category"] == "damage"]
    clutter_recs = [r for r in records if r["category"] == "clutter_road"]
    
    print(f"Running Guard A Ablation over {len(damage_recs)} damage images and {len(clutter_recs)} clutter scenes...")
    
    # 1. Measure True Road Damage Kept
    total_raw_damage_boxes = 0
    total_kept_damage_boxes = 0
    
    for r in damage_recs:
        p = os.path.join(img_dir, r["filename"])
        img = cv2.imread(p)
        if img is None: continue
        preds = eng.predict(img)
        if not preds: continue
        
        boxes = [{"box": list(pr.bbox_xyxy), "conf": pr.confidence, "cls": pr.class_id} for pr in preds]
        total_raw_damage_boxes += len(boxes)
        
        mask = compute_road_surface_mask(img)
        kept, rej = filter_boxes_by_road_mask(boxes, mask, img.shape[:2])
        total_kept_damage_boxes += len(kept)
        
    true_kept_pct = (total_kept_damage_boxes / max(1, total_raw_damage_boxes)) * 100.0
    
    # 2. Measure False Alarms Off-Road Dropped
    total_raw_clutter_boxes = 0
    total_dropped_clutter_boxes = 0
    
    for r in clutter_recs:
        p = os.path.join(img_dir, r["filename"])
        img = cv2.imread(p)
        if img is None: continue
        preds = eng.predict(img)
        if not preds: continue
        
        boxes = [{"box": list(pr.bbox_xyxy), "conf": pr.confidence, "cls": pr.class_id} for pr in preds]
        total_raw_clutter_boxes += len(boxes)
        
        mask = compute_road_surface_mask(img)
        kept, rej = filter_boxes_by_road_mask(boxes, mask, img.shape[:2])
        total_dropped_clutter_boxes += len(rej)
        
    clutter_drop_pct = (total_dropped_clutter_boxes / max(1, total_raw_clutter_boxes)) * 100.0 if total_raw_clutter_boxes > 0 else 0.0
    
    print("\n--- Guard A (Road Surface Prior) Ablation Results ---")
    print(f"True road damage detections kept: {total_kept_damage_boxes}/{total_raw_damage_boxes} ({true_kept_pct:.2f}%)")
    print(f"Off-road clutter false alarms dropped: {total_dropped_clutter_boxes}/{total_raw_clutter_boxes} ({clutter_drop_pct:.2f}%)")
    
    res = {
        "true_damage_kept_pct": round(true_kept_pct, 2),
        "true_damage_kept_count": total_kept_damage_boxes,
        "true_damage_raw_count": total_raw_damage_boxes,
        "offroad_false_alarms_dropped_pct": round(clutter_drop_pct, 2),
        "offroad_false_alarms_dropped_count": total_dropped_clutter_boxes,
        "offroad_clutter_raw_count": total_raw_clutter_boxes
    }
    
    os.makedirs("runs/ablations", exist_ok=True)
    with open("runs/ablations/guard_a_ablation.json", "w") as f:
        json.dump(res, f, indent=2)
    print("Saved ablation results to runs/ablations/guard_a_ablation.json")

if __name__ == "__main__":
    main()
