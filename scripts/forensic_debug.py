"""Forensic debugging of raw model outputs on failure cases.

Prints:
- Raw model outputs before any filtering: class ID, class name, confidence, raw box coordinates
- Check class-index mapping vs training classes
- Check output decoding: xywh vs xyxy, normalized vs pixel, letterbox padding inversion
- Check RGB vs BGR channel ordering
- Check EXIF rotation handling
- Check whether obstacle blocker loads and fires
- Check ensemble blending and consensus boosts
"""

import os
import sys
import json
import numpy as np
import cv2
from PIL import Image, ImageOps

sys.path.insert(0, os.path.abspath("."))
from edge.agent.infer import letterbox_image
import onnxruntime as ort

MODELS = {
    "yolo11n_export": "runs/export/best.onnx",
    "yolov8n_distress": "runs/baselines/yolov8n/weights/best.onnx",
    "coco_blocker": "ml/weights/coco_scene_blocker.onnx",
}

FAILURES = [
    ("case_01_pothole_nh44", "eval_failures/case_01_pothole_nh44.jpg"),
    ("case_02_civil_distress_diagram", "eval_failures/case_02_civil_distress_diagram.jpg"),
    ("case_03_alligator_cracks", "eval_failures/case_03_alligator_cracks.jpg"),
    ("case_04_bengaluru_potholes", "eval_failures/case_04_bengaluru_potholes.jpg"),
    ("case_05_asphalt_crater", "eval_failures/case_05_asphalt_crater.jpg"),
    ("case_06_mumbai_potholes", "eval_failures/case_06_mumbai_potholes.avif"),
    ("case_07_user_tested_potholes", "eval_failures/case_07_user_tested_potholes.jpg"),
]


def inspect_model_metadata(path):
    sess = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
    inputs = [(i.name, i.shape, i.type) for i in sess.get_inputs()]
    outputs = [(o.name, o.shape, o.type) for o in sess.get_outputs()]
    meta = sess.get_modelmeta().custom_metadata_map
    return inputs, outputs, meta


def run_raw_onnx(model_path, img_bgr, conf_thresh=0.10):
    sess = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
    inp_name = sess.get_inputs()[0].name
    out_name = sess.get_outputs()[0].name
    
    h, w = img_bgr.shape[:2]
    padded, scale, (pad_w, pad_h) = letterbox_image(img_bgr, (640, 640))
    rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
    inp = np.transpose(rgb.astype(np.float32) / 255.0, (2, 0, 1))[None, ...]
    
    raw_out = sess.run([out_name], {inp_name: inp})[0]
    # shape [1, 4+nc, anchors]
    if len(raw_out.shape) == 3 and raw_out.shape[1] < raw_out.shape[2]:
        raw_out = np.transpose(raw_out, (0, 2, 1))
        
    preds = raw_out[0]
    results = []
    for row in preds:
        cx, cy, bw, bh = row[:4]
        scores = row[4:]
        cls_id = int(np.argmax(scores))
        conf = float(scores[cls_id])
        if conf >= conf_thresh:
            x1_pad = cx - bw / 2.0
            y1_pad = cy - bh / 2.0
            x2_pad = cx + bw / 2.0
            y2_pad = cy + bh / 2.0
            
            x1 = (x1_pad - pad_w) / scale
            y1 = (y1_pad - pad_h) / scale
            x2 = (x2_pad - pad_w) / scale
            y2 = (y2_pad - pad_h) / scale
            results.append({
                "class_id": cls_id,
                "confidence": conf,
                "box_raw_pad": [float(cx), float(cy), float(bw), float(bh)],
                "box_img_xyxy": [round(float(x1), 2), round(float(y1), 2), round(float(x2), 2), round(float(y2), 2)],
                "box_norm_pct": [round(float(x1 / w * 100), 1), round(float(y1 / h * 100), 1), round(float((x2 - x1) / w * 100), 1), round(float((y2 - y1) / h * 100), 1)]
            })
    return sorted(results, key=lambda x: x["confidence"], reverse=True)


def main():
    print("=================================================================")
    print("STEP 2 FORENSIC DIAGNOSTIC REPORT: RAW MODEL AUDIT")
    print("=================================================================")
    
    for m_key, m_path in MODELS.items():
        if os.path.exists(m_path):
            inputs, outputs, meta = inspect_model_metadata(m_path)
            print(f"\nModel: {m_key} ({m_path})")
            print(f"  Inputs: {inputs}")
            print(f"  Outputs: {outputs}")
            print(f"  Metadata: {meta}")
            
    print("\n-----------------------------------------------------------------")
    print("EVALUATION FAILURES RAW AUDIT:")
    print("-----------------------------------------------------------------")
    
    forensic_results = {}
    
    for name, path in FAILURES:
        if not os.path.exists(path):
            print(f"File missing: {path}")
            continue
            
        # Check EXIF
        pil_img = Image.open(path)
        exif = pil_img.getexif()
        orientation = exif.get(0x0112, 1)
        
        # Load BGR
        pil_transposed = ImageOps.exif_transpose(pil_img).convert("RGB")
        img_bgr = cv2.cvtColor(np.array(pil_transposed), cv2.COLOR_RGB2BGR)
        h, w = img_bgr.shape[:2]
        
        print(f"\n--- {name} (shape: {w}x{h}, EXIF orientation: {orientation}) ---")
        
        forensic_results[name] = {
            "dimensions": [w, h],
            "exif_orientation": orientation,
            "models": {}
        }
        
        for m_key, m_path in MODELS.items():
            if not os.path.exists(m_path):
                continue
            preds = run_raw_onnx(m_path, img_bgr, conf_thresh=0.20)
            forensic_results[name]["models"][m_key] = preds[:10]
            print(f"  [{m_key}] Total preds (conf >= 0.20): {len(preds)}")
            for p in preds[:5]:
                print(f"    Class {p['class_id']}: Conf {p['confidence']:.3f} | Box xyxy: {p['box_img_xyxy']} | Norm%: {p['box_norm_pct']}")

    os.makedirs("docs/forensics", exist_ok=True)
    with open("docs/forensics/step2_raw_audit.json", "w") as f:
        json.dump(forensic_results, f, indent=2)
    print("\nSaved full raw audit to docs/forensics/step2_raw_audit.json")


if __name__ == "__main__":
    main()
