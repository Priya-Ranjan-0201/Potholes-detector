# ScamRoad — Phase 1 Forensic Audit Report

**Date:** 2026-11-16 06:27:58 UTC  
**Host Hardware:** AMD64 Family 25 Model 124 Stepping 0, AuthenticAMD (Windows AMD64)  
**Audit Mode:** Read-Only Forensic Analysis  

---

## 1. Executive Summary & Top Ranked Root Causes

Empirical investigation of the ScamRoad AI inference pipeline revealed why new photos and videos yield wrong or inaccurate results.
The errors are not minor parameter drift; they stem from structural pipeline flaws, uncalibrated multi-model fusion, hard-set ad-hoc heuristic filters, and fabricated evaluation data.

### Ranked Root Causes of Detection Failures:

1. **Hardcoded Evaluation Metrics (Zero Real Generalization Validation):**
   - `scripts/evaluate_model_pipeline.py` hardcodes the reported 85.75% mAP@50 and confusion matrix as Python dictionary and list literals.
   - The model was never genuinely verified on a large, multi-country held-out set.
2. **Overly Broad COCO Scene Blocker (`conf=0.12` and IoM > 0.20):**
   - The COCO obstacle filter triggers dozens of false detections in urban scenes (e.g. 27 detections on `bengaluru_potholes.jpg`), which then mask valid road surfaces and discard legitimate road defects.
3. **Zero Detection on Valid Road Scans (`pothole_nh44.jpg`):**
   - Edge YOLO11n produced 0 raw detections.
   - PyResearch model produced 0 raw detections.
   - D-FINE produced a detection with confidence 0.116, which was discarded because the single-model threshold required >= 0.42.
   - Crack engine detected alligator crack at 0.228, but line 790 enforced `crack_floor = max(0.32, conf_thresh)`, discarding it.
4. **Input Fragility & Image Decoding Pipeline:**
   - `cv2.imdecode` fails silently on AVIF/HEIC images (`case_06_mumbai_potholes.avif`).
   - EXIF orientation metadata is ignored: portrait smartphone photos are not rotated before inference.
   - Images are stretched directly to 640x640 with `cv2.resize` without letterboxing, distorting aspect ratios by over 40% on standard 16:9 dashcam frames.
5. **Uncalibrated 70/30 Ensemble & Arbitrary Scoring:**
   - D-FINE sigmoid logits and YOLO confidences operate on different scales.
   - A fixed linear combination (0.70/0.30) with arbitrary multipliers (1.15 for 3 votes, 1.10 for 2 votes, 0.85 penalty for solo D-FINE) distorts true probability calibration.
6. **Brittle Color & Geometry Filters:**
   - Saturation thresholds (> 115 for potholes, > 58 for cracks) discard real defects on weathered, dusty, or gravel roads.
   - Bottom-corner and bounding box size filters reject large craters and wheel-path distress.
7. **Lack of Video Tracking Implementation:**
   - Despite frontend marketing of video detection, no video pipeline endpoint exists in FastAPI backend.
8. **Synthetic Data and Seed Pollution:**
   - Synthetic shapes generated in `run_hard_negative_ablation.py`.
   - Fabricated corridors, wards, and contractors inserted into database via `ingest_real_rdd_data.py`.

---

## 2. Failure Case Reproduction & Classification

| File | Image Shape | COCO Obstacles | D-FINE Raw | PyRes Raw | Edge Raw | Crack Raw | Final Total | Classification vs Ground Truth |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `case_01_pothole_nh44.jpg` | 720x720 | 0 | 0 | 0 | 0 | 0 | 0 | **MISSED DEFECT** (True pothole gave 0 detections) |
| `case_02_civil_distress_diagram.jpg` | 399x501 | 1 | 3 | 1 | 1 | 5 | 4 | **FALSE POSITIVE** (Diagram detected as road defects) |
| `case_03_alligator_cracks.jpg` | 387x516 | 0 | 0 | 0 | 0 | 15 | 2 | **WRONG CLASS** (Alligator crack detected as Longitudinal) |
| `case_04_bengaluru_potholes.jpg` | 399x501 | 27 | 17 | 2 | 4 | 9 | 5 | **PARTIAL / OVER-DETECTION** (Redundant or noisy boxes) |
| `case_05_asphalt_crater.jpg` | 581x395 | 0 | 2 | 1 | 1 | 5 | 1 | **PARTIAL / OVER-DETECTION** (Redundant or noisy boxes) |
| `case_06_mumbai_potholes.avif` | 402x275 | 12 | 8 | 4 | 22 | 8 | 16 | **FORMAT FRAGILITY** (OpenCV decode failed, PIL required) |
| `case_07_user_tested_potholes.jpg` | 692x257 | 1 | 18 | 7 | 12 | 2 | 12 | **PARTIAL / OVER-DETECTION** (Redundant or noisy boxes) |
| `alligator_cracks.jpg` | 387x516 | 0 | 0 | 0 | 0 | 15 | 2 | **WRONG CLASS** (Alligator crack detected as Longitudinal) |
| `asphalt_crater.jpg` | 581x395 | 0 | 2 | 1 | 1 | 5 | 1 | **PARTIAL / OVER-DETECTION** (Redundant or noisy boxes) |
| `bengaluru_potholes.jpg` | 399x501 | 27 | 17 | 2 | 4 | 9 | 5 | **PARTIAL / OVER-DETECTION** (Redundant or noisy boxes) |
| `civil_distress_diagram.jpg` | 399x501 | 1 | 3 | 1 | 1 | 5 | 4 | **FALSE POSITIVE** (Diagram detected as road defects) |
| `mumbai_potholes.avif` | 402x275 | 12 | 8 | 4 | 22 | 8 | 16 | **FORMAT FRAGILITY** (OpenCV decode failed, PIL required) |
| `pothole_nh44.jpg` | 720x720 | 0 | 0 | 0 | 0 | 0 | 0 | **MISSED DEFECT** (True pothole gave 0 detections) |
| `user_tested_potholes.jpg` | 692x257 | 1 | 18 | 7 | 12 | 2 | 12 | **PARTIAL / OVER-DETECTION** (Redundant or noisy boxes) |

---

## 3. Pipeline Integrity Checks

### 3.1 EXIF Orientation
- `cv2.imdecode` does NOT respect EXIF orientation tags.
- Photos taken in portrait orientation on mobile phones have orientation tag 6 or 8. When decoded with `cv2.imdecode`, the image remains rotated horizontally, causing horizontal detection boxes across vertical roads.

### 3.2 Color Order & Normalization
- Inference endpoint uses BGR for OpenCV and RGB for D-FINE and PyResearch.
- D-FINE normalizes with ImageNet mean `[0.485, 0.456, 0.406]` and std `[0.229, 0.224, 0.225]`.
- YOLO models normalize to `[0, 1]` without standardization.
- Direct resize `cv2.resize(rgb, (640, 640))` squashes aspect ratios, distorting spatial proportions by over 40% on standard 16:9 dashcam frames.

### 3.3 Image Formats
- AVIF format fails with `cv2.imdecode` natively; requires PIL Image fallback.
- RGBA PNGs decode as 3-channel in IMREAD_COLOR, but 16-bit PNGs require explicit casting.

### 3.4 Hardware Execution Latency & Parity
- Measured FP32 ONNX Latency (p50): **44.76 ms** (~22.3 FPS)
- Measured INT8 ONNX Latency (p50): **92.26 ms** (~10.8 FPS)
- **Finding:** INT8 quantization on host x86_64 CPU is **0.49x slower** than FP32 due to quantization overhead without hardware VNNI acceleration.

---

## 4. Heuristics & Hand-Set Filters Audit

| Rule / Filter | Configured Value | Stated Purpose | Measured Harm on Unseen Data | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| Obstacle Blocker | `conf=0.12`, IoM > 0.20 | Mask traffic/pedestrians | Masks entire road segments in urban areas (27 false blocks in Bengaluru) | **REMOVE / REPLACE** |
| Pothole Saturation | `sat > 115` | Reject painted car surfaces | Discards sunlit dirt roads and reddish clay pavement | **REMOVE** |
| Crack Saturation | `sat > 58` | Reject road lines/clothing | Rejects real road cracks on dusty or weathered asphalt | **REMOVE** |
| Box Size Limit | `w > 0.58` or `h > 0.50` | Reject monster boxes | Drops large, critical craters and near-hood potholes | **REMOVE** |
| Corner Shoulder | Bottom 10%, side 8% | Reject curb artifacts | Drops potholes in driver wheel paths | **REMOVE** |
| Cavity Depression | `diff < -8.0` | Reject flat glare | Drops water-filled and low-contrast potholes | **REMOVE** |
| Consensus Multiplier | 1.15 (3 votes), 1.10 (2 votes) | Boost ensemble | Uncalibrated score inflation | **REMOVE** |
| Solo Model Penalty | `0.85 * conf`, min 0.42 | Suppress noise | Discards valid detections from D-FINE | **REMOVE** |

---

## 5. Model Provenance & Checkpoint Audit

| Model Filename | Architecture | Size | Checkpoint SHA-256 | Training Provenance | Issues Found |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `coco_scene_blocker.onnx` | ONNX | 10.24 MB | `af569e7ed6e2524a...` | External / Audited | See provenance records |
| `pavimentos_dfine_l.onnx` | ONNX | 119.5 MB | `b6b76e8a8e59bdd6...` | External / Audited | See provenance records |
| `pyresearch_pothole_best.onnx` | ONNX | 35.26 MB | `54f09e7213bee6a9...` | External / Audited | See provenance records |
| `pyresearch_pothole_best.pt` | ONNX | 17.77 MB | `4a4aa7e6a3f2f9d5...` | External / Audited | See provenance records |
| `yolov8n_seg_pothole.onnx` | ONNX | 12.67 MB | `57a02ba92e788fa7...` | External / Audited | See provenance records |
| `yolov8n_seg_pothole.pt` | ONNX | 6.44 MB | `375c8a7c2603a3ff...` | External / Audited | See provenance records |

---

## 6. Audit of Claims vs Measured Reality

| Claim in README / UI | Claimed Value | Audit Finding | Evidence |
| :--- | :--- | :--- | :--- |
| 85.75% mAP@50 on RDD2022-India | Stated in docs | **UNVERIFIABLE / HARDCODED** | scripts/evaluate_model_pipeline.py hardcodes test_instances and per_class_metrics dictionary literals without running evaluation over images. |
| Zero False Positives / Zero Hallucination Display | Stated in docs | **FALSE** | civil_distress_diagram.jpg produced 4 false detections; non-road objects trigger false alarms. |
| 100% Recall retention on hard negatives | Stated in docs | **SYNTHETIC / FALSE** | scripts/run_hard_negative_ablation.py generates synthetic circle and rectangle drawings with OpenCV and writes hardcoded delta dictionary. |
| Real-time edge INT8 speedup | Stated in docs | **FALSE ON HOST CPU** | ml/runs/onnx_parity.json measures FP32 latency at 44.76 ms (22.3 FPS) vs INT8 latency at 92.26 ms (10.8 FPS). INT8 is 0.49x speedup (2x slower) on host CPU. |
| Real Municipal Corridors (NH-44 Grand Trunk Corridor, ORR-01) | Stated in docs | **SYNTHETIC / INVENTED** | scripts/ingest_real_rdd_data.py hardcodes CORRIDORS list with fabricated LINESTRING coordinates and Central Municipal District. |
| Real-time video inference and tracking | Stated in docs | **UNIMPLEMENTED IN BACKEND** | No video upload or video tracking endpoint exists under backend/app/api/v1/. |

---

## 7. Action Plan for Phase 2 & Phase 3

1. **Build a Trustworthy Multi-Source Evaluation Set (Phase 2):**
   - Assemble held-out test splits from RDD2022 and real road datasets with hard negatives (clean roads, shadows, manholes).
   - Never tune on this set; touch once for final reporting.
2. **Fix Pipeline Integrity (Phase 3):**
   - Add automatic EXIF transpose.
   - Standardize on aspect-ratio-preserving letterboxing across all models.
   - Implement multi-format image decoding with PIL fallback.
3. **Eliminate Brittle Heuristics (Phase 3):**
   - Strip away hand-crafted saturation, luminance, and corner-box filters.
   - Implement proper validation-tuned Weighted Boxes Fusion (WBF) or single high-accuracy unified detector.
4. **Deploy Trained Unified Model on Edge & Backend:**
   - Train/fine-tune on unified dataset with real hard negatives.
   - Evaluate FP32 vs INT8 latency honestly on host CPU.
5. **Implement True Video Event Pipeline:**
   - Build frame extraction, tracking (IoU/ByteTrack), and defect event consolidation.