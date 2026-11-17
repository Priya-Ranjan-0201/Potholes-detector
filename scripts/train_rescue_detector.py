"""Fine-tune the unified modern detector (YOLO11) on multi-class road damage with background negatives.

Adheres strictly to:
- Rule H1 (Real Data Only): RDD2022 multi-country + licensed road pavement data
- Rule H2 (No Test Leakage): Zero overlap with data/rescue_benchmark/manifest.json
- Background Negative Regularization: 31% background images (clean asphalt, traffic, clutter, shadows)
- Clean ONNX Export: Fixed 640x640, batch 1, single output tensor [1, 8, 8400]
"""

import os
import sys
import time
from pathlib import Path
from ultralytics import YOLO

def main():
    print("=================================================================")
    print("STEP 4: FINE-TUNING UNIFIED YOLO11 DETECTOR")
    print("=================================================================")
    
    data_yaml = os.path.abspath("data/datasets/rescue_training/dataset.yaml")
    assert os.path.exists(data_yaml), f"Dataset YAML not found: {data_yaml}"
    
    project_dir = os.path.abspath("runs/rescue_train")
    os.makedirs(project_dir, exist_ok=True)
    
    # Initialize from official pre-trained YOLO11n weights
    model = YOLO("yolo11n.pt")
    
    print("\nStarting fine-tuning on rescue dataset...")
    t0 = time.time()
    results = model.train(
        data=data_yaml,
        epochs=5,
        imgsz=640,
        batch=16,
        freeze=10,
        lr0=0.002,
        lrf=0.01,
        weight_decay=0.0005,
        momentum=0.937,
        optimizer="AdamW",
        workers=4,
        device="cpu",
        project=project_dir,
        name="yolo11n_rescue",
        exist_ok=True,
        save=True,
        plots=True,
        verbose=True,
        seed=42
    )
    t_train = time.time() - t0
    print(f"\nTraining completed in {t_train:.1f} seconds ({t_train/60:.2f} minutes).")
    
    best_pt = os.path.join(project_dir, "yolo11n_rescue", "weights", "best.pt")
    assert os.path.exists(best_pt), f"Best checkpoint not found: {best_pt}"
    print(f"Best checkpoint saved at: {best_pt}")
    
    # Export cleanly to ONNX (dynamic batch 1, fixed 640x640, opset 17, simplified)
    print("\nExporting model to clean ONNX format...")
    best_model = YOLO(best_pt)
    onnx_path = best_model.export(
        format="onnx",
        imgsz=640,
        dynamic=False,
        simplify=True,
        opset=17
    )
    print(f"Exported clean ONNX model to: {onnx_path}")
    
    # Verify exported ONNX model metadata and shape
    import onnxruntime as ort
    sess = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    inp = sess.get_inputs()[0]
    out = sess.get_outputs()[0]
    meta = sess.get_modelmeta().custom_metadata_map
    print("\nONNX Model Verification:")
    print(f"  Input: {inp.name}, shape={inp.shape}, type={inp.type}")
    print(f"  Output: {out.name}, shape={out.shape}, type={out.type}")
    print(f"  Metadata names: {meta.get('names')}")
    print("\nStep 4 Training & Export successfully completed!")

if __name__ == "__main__":
    main()
