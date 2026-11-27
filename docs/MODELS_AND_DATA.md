# Models & Datasets Provenance Register

In compliance with **Rule G4 (Provenance and Licenses)**, this register documents the source, version, license, cryptographic SHA-256 hash, and training lineage for every production model weight and evaluation dataset used in ScamRoad.

---

## 1. Production Model Weights

### 1.1 Primary General Defect Detector (YOLO11n)
- **Path:** `runs/export/best.onnx` / `ml/weights/yolo11n_pothole_best.onnx`
- **Architecture:** YOLO11 Nano (ONNX FP32, input: `1x3x640x640`)
- **File Size:** 10.17 MB (10,666,410 bytes)
- **SHA-256:** `a6b1255ed53f247800bc50b94517cb745449461488acd89a0d024ba51246727e`
- **Source / Lineage:** Fine-tuned from Ultralytics YOLO11n on unified road distress data (asphalt potholes and structural distress).
- **License:** AGPL-3.0
- **Operational Role:** Primary high-recall road cavity and pothole detector (confidence threshold: `>= 0.20`, NMS IoU: `0.35`).

### 1.2 Crack & Distress Classifier Specialist (YOLOv8n)
- **Path:** `ml/runs/pothole_yolov8n/weights/best.onnx`
- **Architecture:** YOLOv8 Nano (ONNX FP32, input: `1x3x640x640`)
- **File Size:** 12.18 MB (12,776,151 bytes)
- **SHA-256:** `f8d1d6b9446f6b4e58ac5c018ed9f2aca3a1e226e0f19298ff0378a16729d9ad`
- **Source / Lineage:** Fine-tuned on RDD2022 multi-class distress dataset.
- **License:** AGPL-3.0
- **Operational Role:** Surface crack specialist for longitudinal, transverse, and alligator cracks (confidence threshold: `>= 0.65`).

### 1.3 Quantized INT8 Edge Models
- **Path:** `ml/weights/best_int8.onnx` / `ml/weights/best_yolo11_int8.onnx`
- **Architecture:** YOLO11n INT8 static quantization via ONNX Runtime
- **File Size:** 2.89 MB (3,029,809 bytes)
- **SHA-256:** `371b1e5eed8da9a7d6d7757a18c544a4f3fb72530506df4854eff2529e9ee7bf`
- **Source / Lineage:** Quantized from `best.onnx` using MinMax calibration on representative asphalt road tiles.
- **License:** AGPL-3.0
- **Operational Role:** Ultra-low-latency deployment on resource-constrained embedded edge devices (45.5 ms p50 latency on host CPU).

### 1.4 Semantic Obstacle Gate (COCO)
- **Path:** `ml/weights/coco_scene_blocker.onnx`
- **Architecture:** YOLO11n trained on MS-COCO 80 classes
- **File Size:** 10.24 MB (10,741,396 bytes)
- **SHA-256:** `af569e7ed6e2524a0be900991b1a1024f9ead17b5da8958b6f10bb3dbcb10492`
- **Source / Lineage:** Ultralytics official COCO pretrained release.
- **License:** AGPL-3.0
- **Operational Role:** Suppresses road defect false alarms that overlap non-road scene obstacles (vehicles, buses, motorcycles, pedestrians, and traffic signs).

### 1.5 Polygonal Instance Segmentation Specialist
- **Path:** `ml/weights/yolov8n_seg_pothole.onnx`
- **Architecture:** YOLOv8n-Seg (ONNX FP32)
- **File Size:** 12.67 MB (13,288,120 bytes)
- **SHA-256:** `57a02ba92e788fa781bf2b35319bf8da70744723c612ffa8f1eb32c3e631e00b`
- **Source / Lineage:** Fine-tuned from keremberke/yolov8n-pothole-segmentation on road damage masks.
- **License:** AGPL-3.0
- **Operational Role:** Generates polygonal segmentation masks constrained inside confirmed bounding boxes.

### 1.6 Road Scene vs Non-Road Neural Classifier (Gate B)
- **Path:** `ml2/models/road_classifier.onnx`
- **Architecture:** MobileNetV3-Small (TorchVision fine-tuned, ONNX opset 14)
- **File Size:** 5.81 MB (6,089,255 bytes)
- **SHA-256:** `ec843f51da259068c07e0523d45ef450700d3d57d7eeff5be3c07248108a7395`
- **Source / Lineage:** Fine-tuned from PyTorch MobileNetV3-Small weights on 250 verified road scenes and 230 non-road scenes.
- **License:** BSD-3-Clause
- **Operational Role:** Gate B2 input gate rejection of non-road scenes (diagrams, UI screenshots, indoor, and landscapes).

---

## 2. Evaluation Datasets

### 2.1 Multi-Source Held-Out Test Set
- **Location:** `data/evaluation_set/`
- **Sample Size:** 1,728 images (984 defect images, 744 hard-negative clean road images)
- **Manifest:** `ml/data/test_manifest.json` (SHA-256: `20daf21bd17bdc8ce5b89fe10ce42c899d55327000519b30a064cca511da6628`)
- **Leakage Verification:** 0 SHA-256 hash collisions, 0 perceptual hash collisions (pHash distance <= 2) against training datasets.
- **Geographic Composition:** 6 countries (India, United States, Japan, Egypt, Norway, China).
- **Contributing Datasets:**
  1. **RDD2022 (Road Damage Dataset 2022):** Arya et al., IEEE BigData 2022. License: CC BY-SA 4.0.
  2. **Manot Road Distress:** Public research benchmark. License: CC BY 4.0.
  3. **Taroii Road Potholes & Clean Roads:** Kaggle open benchmark. License: Open Data.
  4. **Kauevestena Deep Pavements:** Diverse non-asphalt pavement patches (concrete, sett stone, cobblestone, gravel). License: CC0 / Public Domain.

### 2.2 Dashcam Video Test Suite
- **Location:** `data/test_videos/`
- **Clips Count:** 20 verified dashcam video clips (120 seconds total duration)
- **Ground Truth Manifest:** `data/test_videos/video_ground_truth.json` (SHA-256: `7847575a839d44cfcc66294b48e1f7a12cf0f4a2c0f2233a21b52fbb1a2c17f2`)
- **Environmental Conditions Covered:** Urban daylight, high-contrast glare, dusk/dawn, wet/rainy asphalt, and highway corridors.
- **Ground Truth Defect Events:** 13 verified physical defect encounters.

### 2.3 Gate B Benchmark TEST-B (Clean Clutter Road Scenes)
- **Location:** `data/benchmarks/test_b_clutter/`
- **Sample Size:** 300 authentic clean road images with zero defects across 3 geographical groups:
  - 100 China/Czech rural and urban highways
  - 100 Japan/Norway suburban corridors
  - 100 India urban, highway, and rural roads
- **Manifest:** `data/benchmarks/manifest_test_b.json` (SHA-256 locked)
- **License:** CC BY-SA 4.0 (RDD2022 benchmark)
- **Benchmark Target:** False-alarm images <= 2.0%.

### 2.4 Gate B Benchmark TEST-C (Non-Road Scenes)
- **Location:** `data/benchmarks/test_c_non_road/`
- **Sample Size:** 220 authentic non-road scenes (50 technical diagrams / UI screenshots / slide formats + 170 natural landscapes, indoor interiors, architectural structures, and portrait photos)
- **Manifest:** `data/benchmarks/manifest_test_c.json` (SHA-256 locked)
- **License:** CC0 / Public Domain / CC BY-SA 4.0
- **Benchmark Target:** Rejection rate >= 95.0%.
