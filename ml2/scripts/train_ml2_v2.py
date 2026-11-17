"""Train ML2 Unified Balanced Road Damage Detector v2.

Fine-tunes YOLO11n on the balanced multi-class dataset with 26.8% negative background regularization.
Exports canonical ONNX model to ml2/models/yolo11_road_damage.onnx.
"""

from __future__ import annotations

import os
import shutil
import sys
import time
from pathlib import Path
from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main():
    print("=================================================================")
    print(" TRAINING ML2 UNIFIED BALANCED ROAD DAMAGE DETECTOR v2")
    print("=================================================================")

    data_yaml = PROJECT_ROOT / "data" / "datasets" / "ml2_unified_v2" / "dataset.yaml"
    if not data_yaml.exists():
        raise FileNotFoundError(f"Dataset YAML not found at {data_yaml}")

    runs_dir = PROJECT_ROOT / "ml2" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    weights_path = PROJECT_ROOT / "yolo11n.pt"
    if not weights_path.exists():
        weights_path = "yolo11n.pt"

    print(f"[1/4] Initializing YOLO11n from {weights_path}...")
    model = YOLO(str(weights_path))

    print("[2/4] Starting training on balanced ML2 dataset (1255 images, 26.8% negatives)...")
    t0 = time.time()
    results = model.train(
        data=str(data_yaml),
        epochs=6,
        imgsz=640,
        batch=16,
        freeze=6,
        lr0=0.003,
        lrf=0.01,
        weight_decay=0.0005,
        momentum=0.937,
        optimizer="AdamW",
        workers=0,
        device="cpu",
        project=str(runs_dir),
        name="yolo11_road_damage_v2",
        exist_ok=True,
        save=True,
        plots=True,
        verbose=True,
        seed=42,
    )
    t_train = time.time() - t0
    print(f"\nTraining completed in {t_train:.1f}s ({t_train / 60:.2f} mins).")

    # Locate best.pt
    best_pt = runs_dir / "yolo11_road_damage_v2" / "weights" / "best.pt"
    if not best_pt.exists():
        raise FileNotFoundError(f"Checkpoint not found at {best_pt}")
    print(f"[3/4] Best checkpoint saved at {best_pt}")

    # Export to ONNX
    print("[4/4] Exporting clean ONNX model (opset 17, fixed 640x640)...")
    best_model = YOLO(str(best_pt))
    exported_path = best_model.export(
        format="onnx",
        imgsz=640,
        dynamic=False,
        simplify=True,
        opset=17,
    )
    print(f"Exported to {exported_path}")

    # Back up previous onnx and copy new to canonical location
    models_dir = PROJECT_ROOT / "ml2" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    canonical_onnx = models_dir / "yolo11_road_damage.onnx"
    if canonical_onnx.exists():
        shutil.copyfile(canonical_onnx, models_dir / "yolo11_road_damage_prev.onnx")

    shutil.copyfile(exported_path, canonical_onnx)
    print(f"Canonical ONNX installed at {canonical_onnx}")

    # Verify ONNX model loading
    import onnxruntime as ort
    sess = ort.InferenceSession(str(canonical_onnx), providers=["CPUExecutionProvider"])
    inp = sess.get_inputs()[0]
    out = sess.get_outputs()[0]
    meta = sess.get_modelmeta().custom_metadata_map
    print("\nONNX Model Verification:")
    print(f"  Input: {inp.name}, shape={inp.shape}, type={inp.type}")
    print(f"  Output: {out.name}, shape={out.shape}, type={out.type}")
    print(f"  Metadata names: {meta.get('names')}")
    print("\nTraining and export pipeline finished successfully!")


if __name__ == "__main__":
    main()
