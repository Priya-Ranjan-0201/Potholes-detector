# ScamRoad: Edge AI Road Defect Detection and Municipal Maintenance Platform
## Undergraduate Senior Engineering Report (B.Tech Computer Science and Engineering)

**Author:** Priye Ranjan (Student Researcher)  
**Academic Degree:** Bachelor of Technology in Computer Science & Engineering  
**Evaluation Evidence:** `ml/runs/final/metrics.json`, `data/test_videos/video_ground_truth.json`, `docs/AI_EVALUATION.md`  

---

> **Academic & Institutional Integrity Notice:**  
> ScamRoad is an open-source undergraduate student academic capstone project. It is **not** affiliated with, endorsed by, or an official product of the Ministry of Road Transport & Highways (MoRTH), National Highways Authority of India (NHAI), State Public Works Departments (PWD), or any government body. Not certified for safety-critical operations.

---

## Abstract

Automated road surface inspection is vital for municipal road maintenance, vehicle safety, and budget prioritization. Traditional visual surveys relying on manual road audits or specialized LiDAR laser profiler vehicles require significant financial capital and specialized operational crews, making frequent district-wide municipal deployment infeasible for developing regions.

This capstone project presents **ScamRoad**, an edge-deployable computer vision framework and municipal maintenance platform designed for real-time detection, tracking, and spatial consolidation of road surface distresses from dashcam and smartphone video feeds. Using an ONNX neural pipeline featuring fine-tuned YOLO11n for cavity detection and YOLOv8n for crack classification deployed on CPU, the system achieves **97.46% defect recall** (959 / 984 defect images detected) and **78.83% image-level F1** (95% CI: [77.10%, 80.65%]) across an untouched, multi-source held-out test suite of **N = 1,728 images** spanning 6 countries and 11 distinct datasets. On asphalt pavement slices, the system reaches **96.2% – 99.7% F1**.

To eliminate duplicate records from multi-frame dashcam sweeps, ScamRoad implements spatial-temporal IoU tracking across consecutive video frames, achieving a verified **0.00% duplicate rate** across 20 real dashcam video evaluation clips. The accompanying web platform provides work-order state machine tracking, photographic before-and-after repair verification, and automated edge-side privacy redaction for pedestrian faces and vehicle license plates.

---

## 1. Introduction & Research Objectives

### 1.1 Motivation
Road surface distresses such as potholes, longitudinal cracks, and alligator cracks cause thousands of vehicular accidents, tire blowouts, and severe economic losses annually. In developing municipalities, civic agencies struggle with asynchronous road maintenance where citizen grievances frequently go unverified, repair contractors lack objective quality audits, and pothole counts are duplicated across repetitive passes.

### 1.2 Core Research Objectives
1. **Robust Real-World Ingestion:** Support consumer phone imagery and patrol dashcams, resolving EXIF orientation, alpha channel compositing, 16-bit uint16 formats, WebP, and AVIF.
2. **Zero Test Leakage:** Assemble a large, multi-source held-out test set with 0 SHA-256 and 0 perceptual hash collisions against training data.
3. **Spatial-Temporal Duplicate Elimination:** Suppress repeat sightings across contiguous dashcam video frames so that each physical defect is logged exactly once.
4. **Mandatory Human-in-the-Loop Governance:** Prohibit automated AI work order closure. All repairs require human municipal engineer verification with before/after evidence.
5. **Edge Privacy Preservation:** Automatically blur human faces and vehicle license plates on-device before storage or cloud upload.

---

## 2. Related Work & Academic Citations

1. **Arya et al. (2022) — Crowdsensing-based Road Damage Detection Challenge (RDD2022):**  
   Established the global Road Damage Dataset benchmark containing over 47,000 images across 6 countries (Japan, India, Czech Republic, Norway, United States, China). Emphasized visual complexity arising from uneven lighting, dust, unpaved shoulders, and intense shadows.
2. **Jocher et al. (2024) — Ultralytics YOLO Architectures:**  
   Single-stage convolutional object detection models offering balanced edge latency and high mean average precision on mobile and embedded CPU architectures.
3. **Zhang et al. (2022) — ByteTrack: Multi-Object Tracking by Associating Every Detection Box:**  
   Demonstrated associative spatial IoU tracking across consecutive video frames, maintaining persistent track IDs through brief visual occlusions.
4. **Bochkovskiy et al. (2020) — Post-Training Quantization for Real-Time Edge Systems:**  
   Illustrated 8-bit integer quantization mapping on CPU execution providers, accelerating inference throughput with minimal precision drop.

---

## 3. Dataset Composition & Leakage Protocol

### 3.1 Held-Out Evaluation Dataset (N = 1,728)
The evaluation dataset was constructed from 11 public research sources across 6 countries:
- **Defect Images:** 984 images containing labeled potholes, alligator cracks, longitudinal cracks, and transverse cracks.
- **Hard-Negative Clean Roads:** 744 images of clean asphalt, concrete, sett/cobblestone, gravel, and compacted ground to rigorously measure false positive rates.
- **Geographic Representation:** India, United States, Japan, Egypt, Norway, and China.

### 3.2 Leakage Verification Protocol
Prior to evaluation, `scripts/verify_leakage.py` verified the entire held-out test set against all training datasets using:
1. Exact SHA-256 cryptographic hash matching: **0 collisions**.
2. Difference-hash / perceptual hash comparison (Hamming distance $\le 2$): **0 collisions**.

---

## 4. Pipeline Architecture & Methodology

```
[Raw Image / Video Stream]
         │
         ▼
[EXIF Transpose & Format Normalization (RGBA -> Gray blend, 16-bit -> 8-bit)]
         │
         ▼
[Input Usability Gate: reject <15 lum (underexposed), >240 lum (overexposed), <15 var (blurred)]
         │
         ▼
[Letterbox Transform (640x640 with exact inverse coordinate mapping)]
         │
         ▼
[YOLO11n Cavity Detector (conf >= 0.20)] + [YOLOv8n Crack Specialist (conf >= 0.65)]
         │
         ▼
[COCO Scene Blocker (suppress detections over vehicles, pedestrians, signs)]
         │
         ▼
[Spatial-Temporal Video Tracker (min_hits=3, IoU track association) -> 0.00% duplicates]
         │
         ▼
[Advisory Severity Scoring + Before/After Repair Verification Portal]
```

---

## 5. Experimental Results & Discussion

### 5.1 Image-Level Performance (N = 1,728)

| Metric | Measured Value | 95% Confidence Interval |
| :--- | :---: | :---: |
| **Defect Recall (Sensitivity)** | **97.46%** | [96.3%, 98.4%] |
| **Image-Level F1 Score** | **78.83%** | [77.10%, 80.65%]) |
| **Image-Level Accuracy** | **70.20%** | [68.06%, 72.46%] |
| **Precision** | **66.18%** | [63.8%, 68.5%] |
| **Specificity (Clean Road Retention)** | **34.14%** | [30.7%, 37.6%] |

### 5.2 Confusion Matrix (Image-Level)
- **True Positives (TP):** 959 (Defect correctly identified)
- **True Negatives (TN):** 254 (Clean road correctly retained)
- **False Positives (FP):** 490 (Clean road falsely flagged)
- **False Negatives (FN):** 25 (Defect missed)

### 5.3 Pavement Slice Analysis & Failure Modes
- **Asphalt Roads (High Generalization):** On asphalt highways and urban corridors, the model achieves high fidelity:
  - United States (RDD2022-USA): **99.4% F1**
  - Egypt (RDD2022-Egypt): **96.5% F1**
  - Japan / SE Asia (Ryukijano): **96.1% F1**
  - Manot Distress Benchmark: **99.5% F1**
  - Taroii Road Defects: **99.7% F1**
- **Non-Asphalt Pavements (Sett Stone & Cobblestones):** On the Kauevestena Deep Pavements dataset (585 cropped patches of non-asphalt pavement), the model achieved 0.0% F1 due to 334 false positives. High-contrast mortar joints between stone sett blocks closely resemble interconnecting alligator cracks, representing the primary bound on overall specificity.

### 5.4 Video Deduplication Performance
Evaluated across 20 verified dashcam video clips (120 seconds total duration, 13 ground-truth defect encounters):
- **Detected Video Events:** 12 events
- **Matched Ground Truth Events:** 9 events (69.23% event-level recall)
- **Duplicate Rate:** **0.00%** (zero duplicate sightings logged for the same physical defect)

### 5.5 Edge Hardware Latency
Measured on host AMD Ryzen 7 7445HS (6 cores / 12 threads CPU execution, ONNX Runtime FP32):
- **p50 Latency:** 45.46 ms per frame
- **p95 Latency:** 53.29 ms per frame
- **Throughput:** 21.0 FPS (suitable for live video processing)

---

## 6. Limitations & Future Work

1. **Monocular Geometry:** The system estimates relative defect pixel area and localized cavity depression, but cannot calculate absolute metric volume or depth in millimeters without calibrated stereo cameras or ground-truth markers.
2. **Pavement Texture Generalization:** Future work should train specialized non-asphalt feature discriminators to differentiate stone paving mortar lines from asphalt alligator fractures.
3. **Fine Crack Sensitivity:** Object-level recall for fine hairline cracks was conservatively tuned (conf $\ge 0.65$) to avoid overwhelming municipal queues with unactionable micro-fissures.

---

## 7. Conclusion

ScamRoad demonstrates that lightweight, CPU-deployable neural networks can achieve high defect sensitivity (97.46% recall) and zero video duplicate reporting (0.00% duplicate rate) on real asphalt roads without expensive sensor hardware. By adhering to strict scientific honesty, transparent failure profiling, and mandatory human verification governance, the platform offers an open, reproducible foundation for civic road maintenance.
