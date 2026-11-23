"""Train and fine-tune ScamRoad YOLO11n on real-world road damage dataset.

Uses authentic data from:
- RDD2022 (India & Global)
- GitHub Pothole Dataset
- Road surface background negative regularizers

Exports clean, verified ONNX model for edge and backend inference.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path

import onnxruntime as ort
import torch
from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_YAML = PROJECT_ROOT / "data" / "real_world_dataset" / "dataset.yaml"
BASE_MODEL = PROJECT_ROOT / "yolo11n.pt"
RUNS_DIR = PROJECT_ROOT / "runs" / "real_world_train"


def main() -> None:
    print("=" * 65)
    print("  ScamRoad Real-World Neural Detector Training (YOLO11n)")
    print("=" * 65)

    if not DATASET_YAML.exists():
        raise FileNotFoundError(f"Dataset YAML not found at {DATASET_YAML}")

    if not BASE_MODEL.exists():
        print("Base model yolo11n.pt not found, downloading...")
        YOLO("yolo11n.pt")

    RUNS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nConfiguration:")
    print(f"  Dataset:     {DATASET_YAML}")
    print(f"  Base Model:  {BASE_MODEL}")
    print(f"  Runs Dir:    {RUNS_DIR}")
    print(f"  Device:      CPU ({os.cpu_count()} cores available)")

    # 1. Initialize YOLO11 model
    model = YOLO(str(BASE_MODEL))

    # 2. Train on real-world dataset
    print("\nStarting transfer learning and fine-tuning...")
    t0 = time.time()
    results = model.train(
        data=str(DATASET_YAML),
        epochs=5,
        imgsz=640,
        batch=16,
        freeze=10,
        lr0=0.002,
        lrf=0.01,
        weight_decay=0.0005,
        momentum=0.937,
        optimizer="AdamW",
        workers=min(4, os.cpu_count() or 2),
        device="cpu",
        project=str(RUNS_DIR),
        name="yolo11n_real_world",
        exist_ok=True,
        save=True,
        plots=True,
        verbose=True,
        seed=42,
    )
    t_train = time.time() - t0
    print(f"\nTraining completed in {t_train:.1f}s ({t_train/60:.2f} minutes).")

    # 3. Locate best.pt
    exp_dir = RUNS_DIR / "yolo11n_real_world"
    best_pt = exp_dir / "weights" / "best.pt"
    if not best_pt.exists():
        best_pt = exp_dir / "weights" / "last.pt"
    print(f"Best PyTorch weights: {best_pt}")

    # 4. Run formal evaluation on validation split
    print("\nRunning validation evaluation...")
    trained_model = YOLO(str(best_pt))
    val_res = trained_model.val(data=str(DATASET_YAML), imgsz=640, device="cpu")

    metrics_summary = {
        "mAP50": round(float(val_res.box.map50), 4),
        "mAP50_95": round(float(val_res.box.map), 4),
        "precision": round(float(val_res.box.mp), 4),
        "recall": round(float(val_res.box.mr), 4),
        "fitness": round(float(val_res.fitness), 4),
        "classes": {
            0: "pothole",
            1: "crack_longitudinal",
            2: "crack_transverse",
            3: "crack_alligator",
        },
        "per_class_mAP50": {
            name: round(float(map50), 4)
            for name, map50 in zip(["pothole", "crack_longitudinal", "crack_transverse", "crack_alligator"], val_res.box.maps[:4])
        } if hasattr(val_res.box, "maps") and len(val_res.box.maps) >= 4 else {},
        "training_time_seconds": round(t_train, 1),
    }
    print(f"\nValidation Metrics:")
    print(f"  mAP@0.50:      {metrics_summary['mAP50']}")
    print(f"  mAP@0.50:0.95: {metrics_summary['mAP50_95']}")
    print(f"  Precision:     {metrics_summary['precision']}")
    print(f"  Recall:        {metrics_summary['recall']}")
    print(f"  Per-class mAP50: {metrics_summary.get('per_class_mAP50')}")

    # Save metrics JSON
    metrics_path = exp_dir / "evaluation_metrics.json"
    metrics_path.write_text(json.dumps(metrics_summary, indent=2), encoding="utf-8")

    # 5. Export clean ONNX model
    print("\nExporting model to clean ONNX format (opset 17, fixed 640x640, batch 1)...")
    onnx_exported = trained_model.export(
        format="onnx",
        imgsz=640,
        dynamic=False,
        simplify=True,
        opset=17,
    )
    onnx_path = Path(onnx_exported)
    print(f"ONNX exported to: {onnx_path} ({onnx_path.stat().st_size / (1024**2):.2f} MB)")

    # 6. Verify ONNX tensor contract
    sess = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    inp = sess.get_inputs()[0]
    out = sess.get_outputs()[0]
    meta = sess.get_modelmeta().custom_metadata_map

    print("\nONNX Model Verification:")
    print(f"  Input:  {inp.name}, shape={inp.shape}, type={inp.type}")
    print(f"  Output: {out.name}, shape={out.shape}, type={out.type}")
    print(f"  Names:  {meta.get('names')}")

    # Assert contract
    assert inp.shape == [1, 3, 640, 640], f"Unexpected input shape: {inp.shape}"
    assert out.shape == [1, 8, 8400], f"Unexpected output shape: {out.shape}"

    # 7. Deploy to production weight locations
    target_deployments = [
        PROJECT_ROOT / "runs" / "rescue_train" / "yolo11n_rescue" / "weights" / "best.onnx",
        PROJECT_ROOT / "runs" / "export" / "best.onnx",
        PROJECT_ROOT / "ml" / "weights" / "yolo11n_pothole_best.onnx",
    ]
    for deploy_path in target_deployments:
        deploy_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(onnx_path), str(deploy_path))
        print(f"  Updated production model: {deploy_path.relative_to(PROJECT_ROOT)}")

    # Also update best.pt
    best_pt_deploy = PROJECT_ROOT / "runs" / "rescue_train" / "yolo11n_rescue" / "weights" / "best.pt"
    shutil.copy2(str(best_pt), str(best_pt_deploy))
    print(f"  Updated production PyTorch model: {best_pt_deploy.relative_to(PROJECT_ROOT)}")

    print("\n" + "=" * 65)
    print("  Real-World Model Training, Evaluation, and Deployment Succeeded!")
    print("=" * 65)


if __name__ == "__main__":
    main()
