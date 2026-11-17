"""Build the locked and hashed rescue evaluation benchmark for ScamRoad.

Dataset breakdown:
- 300 damage images from RDD2022 validation/test data (licence CC BY-SA 4.0) with ground-truth boxes
- 300 clean road negative images (no damage)
- 100 clutter road scenes (traffic, people, scooters, signs, roadside buildings)
- 30 non-road images (diagrams, technical plots, confusion matrices, UI screenshots)
Total: 730 images.

All images are copied to data/rescue_benchmark/images/ with SHA-256 hashes locked in data/rescue_benchmark/manifest.json.
Labels are copied to data/rescue_benchmark/labels/.
"""

import hashlib
import json
import os
import random
import shutil

random.seed(42)

out_dir = "data/rescue_benchmark"
img_out = os.path.join(out_dir, "images")
lbl_out = os.path.join(out_dir, "labels")
os.makedirs(img_out, exist_ok=True)
os.makedirs(lbl_out, exist_ok=True)

eval_img_dir = "data/evaluation_set/images"
eval_lbl_dir = "data/evaluation_set/labels"

with open("ml/data/manifest.json", "r") as f:
    eval_manifest = json.load(f)

recs = eval_manifest["records"]

# 1. 300 Damage images from RDD2022
rdd_damage_pool = [
    r for r in recs
    if "RDD2022" in r.get("source", "") and "defect" in r.get("labels", [])
    and os.path.exists(os.path.join(eval_img_dir, r["file"]))
    and os.path.exists(os.path.join(eval_lbl_dir, os.path.splitext(r["file"])[0] + ".txt"))
    and os.path.getsize(os.path.join(eval_lbl_dir, os.path.splitext(r["file"])[0] + ".txt")) > 0
]
print(f"Total RDD damage available: {len(rdd_damage_pool)}")
random.shuffle(rdd_damage_pool)
selected_damage = rdd_damage_pool[:300]

# 2. 300 Clean Road Negatives
clean_pool = [
    r for r in recs
    if "clean_negative" in r.get("labels", [])
    and os.path.exists(os.path.join(eval_img_dir, r["file"]))
]
print(f"Total clean negatives available: {len(clean_pool)}")
random.shuffle(clean_pool)
selected_clean = clean_pool[:300]

# 3. 100 Clutter Road Scenes
used_files = set(r["file"] for r in selected_damage + selected_clean)
clutter_pool = [
    r for r in recs
    if r["file"] not in used_files
    and any(t in r.get("tags", []) for t in ["traffic", "scooters", "urban", "pedestrian", "clutter"])
    and os.path.exists(os.path.join(eval_img_dir, r["file"]))
]
if os.path.exists("data/guard_set/images"):
    for g_f in os.listdir("data/guard_set/images"):
        if g_f.startswith(("guard_indian_wet_roads", "guard_traffic_scooters", "guard_roadside_clutter")):
            clutter_pool.append({
                "file": g_f,
                "source": "guard_set",
                "path": os.path.join("data/guard_set/images", g_f),
                "licence": "CC BY-SA 4.0",
                "labels": ["clean_negative"],
                "tags": ["clutter", "traffic"]
            })

print(f"Total clutter pool available: {len(clutter_pool)}")
random.shuffle(clutter_pool)
selected_clutter = clutter_pool[:100]

# 4. 30 Non-Road Images (diagrams, UI, charts, curves)
non_road_candidates = [
    ("eval_failures/case_02_civil_distress_diagram.jpg", "civil_distress_diagram", "case_02"),
    ("data/guard_set/images/guard_diagram_01.jpg", "civil_distress_infographic", "guard_61"),
    ("docs/screenshots/live_01_dashboard_light.png", "ui_screenshot", "dashboard"),
    ("docs/screenshots/live_04_scanner_detected_nh44.png", "ui_screenshot", "scanner"),
    ("docs/screenshots/live_10_work_orders.png", "ui_screenshot", "work_orders"),
    ("docs/screenshots/live_13b_evaluation_benchmarks.png", "ui_screenshot", "benchmarks"),
    ("runs/ablations/ablation_A1_yolov8n_640/confusion_matrix.png", "confusion_matrix", "cm_a1"),
    ("runs/ablations/ablation_A1_yolov8n_640/BoxPR_curve.png", "pr_curve", "pr_a1"),
    ("runs/ablations/ablation_A1_yolov8n_640/BoxF1_curve.png", "f1_curve", "f1_a1"),
    ("runs/ablations/ablation_A1_yolov8n_640/results.png", "training_curves", "results_a1"),
    ("runs/ablations/ablation_A2_yolo11n_640/confusion_matrix.png", "confusion_matrix", "cm_a2"),
    ("runs/ablations/ablation_A2_yolo11n_640/BoxPR_curve.png", "pr_curve", "pr_a2"),
    ("runs/ablations/ablation_A2_yolo11n_640/BoxF1_curve.png", "f1_curve", "f1_a2"),
    ("runs/ablations/ablation_A2_yolo11n_640/results.png", "training_curves", "results_a2"),
    ("runs/ablations/ablation_B_yolov8n_320/confusion_matrix.png", "confusion_matrix", "cm_b"),
    ("runs/ablations/ablation_B_yolov8n_320/BoxPR_curve.png", "pr_curve", "pr_b"),
    ("runs/ablations/ablation_B_yolov8n_320/BoxF1_curve.png", "f1_curve", "f1_b"),
    ("runs/ablations/ablation_B_yolov8n_320/results.png", "training_curves", "results_b"),
    ("runs/baselines/yolov8n/confusion_matrix.png", "confusion_matrix", "cm_v8n"),
    ("runs/baselines/yolov8n/BoxPR_curve.png", "pr_curve", "pr_v8n"),
    ("runs/baselines/yolov8n/BoxF1_curve.png", "f1_curve", "f1_v8n"),
    ("runs/baselines/yolov8n/results.png", "training_curves", "results_v8n"),
    ("runs/baselines/yolov8s/confusion_matrix.png", "confusion_matrix", "cm_v8s"),
    ("runs/baselines/yolov8s/BoxPR_curve.png", "pr_curve", "pr_v8s"),
    ("runs/baselines/yolov8s/BoxF1_curve.png", "f1_curve", "f1_v8s"),
    ("runs/baselines/yolov8s/results.png", "training_curves", "results_v8s"),
    ("runs/baselines/yolov8n/labels.jpg", "dataset_distribution_plot", "labels_v8n"),
    ("runs/baselines/yolov8s/labels.jpg", "dataset_distribution_plot", "labels_v8s"),
    ("runs/ablations/ablation_A1_yolov8n_640/labels.jpg", "dataset_distribution_plot", "labels_a1"),
    ("runs/ablations/ablation_A2_yolo11n_640/labels.jpg", "dataset_distribution_plot", "labels_a2")
]
print(f"Non-road candidates: {len(non_road_candidates)}")

benchmark_manifest = {
    "version": "1.0.0-rescue",
    "created_at": "2026-11-17T15:58:00Z",
    "total_images": len(selected_damage) + len(selected_clean) + len(selected_clutter) + len(non_road_candidates),
    "counts": {
        "damage": len(selected_damage),
        "clean_road": len(selected_clean),
        "clutter_road": len(selected_clutter),
        "non_road": len(non_road_candidates)
    },
    "records": []
}


def copy_and_record(src_img_path, src_lbl_path, dst_fn, category, source_name, licence):
    dst_img = os.path.join(img_out, dst_fn)
    dst_lbl = os.path.join(lbl_out, os.path.splitext(dst_fn)[0] + ".txt")
    shutil.copy2(src_img_path, dst_img)
    
    gt_boxes = []
    if src_lbl_path and os.path.exists(src_lbl_path):
        shutil.copy2(src_lbl_path, dst_lbl)
        with open(src_lbl_path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    gt_boxes.append({
                        "class_id": int(parts[0]),
                        "cx": float(parts[1]),
                        "cy": float(parts[2]),
                        "w": float(parts[3]),
                        "h": float(parts[4])
                    })
    else:
        with open(dst_lbl, "w") as f:
            pass
            
    with open(dst_img, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
        
    benchmark_manifest["records"].append({
        "filename": dst_fn,
        "category": category,
        "source": source_name,
        "licence": licence,
        "sha256": sha256,
        "num_gt_boxes": len(gt_boxes),
        "gt_boxes": gt_boxes
    })


# Process damage
for i, r in enumerate(selected_damage):
    fn = r["file"]
    src_i = os.path.join(eval_img_dir, fn)
    src_l = os.path.join(eval_lbl_dir, os.path.splitext(fn)[0] + ".txt")
    dst_fn = f"bench_damage_{i+1:03d}_{fn}"
    copy_and_record(src_i, src_l, dst_fn, "damage", r.get("source", "RDD2022"), r.get("licence", "CC BY-SA 4.0"))

# Process clean
for i, r in enumerate(selected_clean):
    fn = r["file"]
    src_i = os.path.join(eval_img_dir, fn)
    src_l = os.path.join(eval_lbl_dir, os.path.splitext(fn)[0] + ".txt")
    dst_fn = f"bench_clean_{i+1:03d}_{fn}"
    copy_and_record(src_i, src_l, dst_fn, "clean_road", r.get("source", "clean_road"), r.get("licence", "CC BY-SA 4.0"))

# Process clutter
for i, r in enumerate(selected_clutter):
    src_i = r.get("path") or os.path.join(eval_img_dir, r["file"])
    src_l = os.path.join(eval_lbl_dir, os.path.splitext(r["file"])[0] + ".txt")
    dst_fn = f"bench_clutter_{i+1:03d}_{os.path.basename(src_i)}"
    copy_and_record(src_i, src_l, dst_fn, "clutter_road", r.get("source", "clutter"), r.get("licence", "CC BY-SA 4.0"))

# Process non-road
for i, (p, typ, name) in enumerate(non_road_candidates):
    ext = os.path.splitext(p)[1]
    dst_fn = f"bench_nonroad_{i+1:02d}_{name}{ext}"
    copy_and_record(p, None, dst_fn, "non_road", typ, "Project/Internal")

manifest_path = os.path.join(out_dir, "manifest.json")
with open(manifest_path, "w") as f:
    json.dump(benchmark_manifest, f, indent=2)

print("Successfully constructed locked benchmark!")
print(f"Total records: {len(benchmark_manifest['records'])}")
print("Counts:", benchmark_manifest["counts"])
