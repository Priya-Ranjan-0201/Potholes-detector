# Evidence Pack & Traceability Matrix

Every metric, benchmark score, and performance claim reported in ScamRoad is traceable to an authentic disk artifact produced by code execution. This document maps every claim directly to its filesystem evidence.

---

## 1. Image-Level Detection Performance

| Metric | Reported Value | Traceable File Path | Key / Field in File |
| :--- | :---: | :--- | :--- |
| **Total Test Images** | **1,728** | [`ml/runs/final/metrics.json`](../ml/runs/final/metrics.json#L4) | `images.dataset_sample_size` |
| **Defect Images** | **984** | [`ml/runs/final/metrics.json`](../ml/runs/final/metrics.json#L5) | `images.defect_images` |
| **Clean Road Negatives** | **744** | [`ml/runs/final/metrics.json`](../ml/runs/final/metrics.json#L6) | `images.hard_negatives` |
| **Image-Level Recall** | **97.46%** | [`ml/runs/final/metrics.json`](../ml/runs/final/metrics.json#L14) | `images.image_level.recall` |
| **Image-Level F1 Score** | **78.83%** | [`ml/runs/final/metrics.json`](../ml/runs/final/metrics.json#L15) | `images.image_level.f1` |
| **F1 95% Confidence Interval** | **[77.10%, 80.65%]** | [`ml/runs/final/metrics.json`](../ml/runs/final/metrics.json#L16-L19) | `images.image_level.f1_95ci` |
| **Image-Level Accuracy** | **70.20%** | [`ml/runs/final/metrics.json`](../ml/runs/final/metrics.json#L8) | `images.image_level.accuracy` |
| **Accuracy 95% CI** | **[68.06%, 72.46%]** | [`ml/runs/final/metrics.json`](../ml/runs/final/metrics.json#L9-L12) | `images.image_level.accuracy_95ci` |
| **Image-Level Precision** | **66.18%** | [`ml/runs/final/metrics.json`](../ml/runs/final/metrics.json#L13) | `images.image_level.precision` |
| **True Positives** | **959** | [`ml/runs/final/metrics.json`](../ml/runs/final/metrics.json#L22) | `images.image_level.confusion_matrix.true_positives` |
| **True Negatives** | **254** | [`ml/runs/final/metrics.json`](../ml/runs/final/metrics.json#L23) | `images.image_level.confusion_matrix.true_negatives` |
| **False Positives** | **490** | [`ml/runs/final/metrics.json`](../ml/runs/final/metrics.json#L24) | `images.image_level.confusion_matrix.false_positives` |
| **False Negatives** | **25** | [`ml/runs/final/metrics.json`](../ml/runs/final/metrics.json#L25) | `images.image_level.confusion_matrix.false_negatives` |

---

## 2. Pavement & Geographic Slice Evidence

| Slice / Condition | Sample Size | F1 Score | Evidence File | JSON Key |
| :--- | :---: | :---: | :--- | :--- |
| `country:United States` | 250 | **99.4%** | `ml/runs/final/metrics.json` | `images.slices["country:United States"].f1` |
| `country:Egypt` | 150 | **96.5%** | `ml/runs/final/metrics.json` | `images.slices["country:Egypt"].f1` |
| `country:SE Asia / Japan` | 200 | **96.1%** | `ml/runs/final/metrics.json` | `images.slices["country:SE Asia / Japan"].f1` |
| `source:Manot-RoadDistress` | 193 | **99.5%** | `ml/runs/final/metrics.json` | `images.slices["source:Manot-RoadDistress"].f1` |
| `source:Taroii-RoadDefects` | 146 | **99.7%** | `ml/runs/final/metrics.json` | `images.slices["source:Taroii-RoadDefects"].f1` |
| `source:Kauevestena-DeepPavements` | 585 | **0.0%** | `ml/runs/final/metrics.json` | `images.slices["source:Kauevestena-DeepPavements"].f1` |

---

## 3. Video Defect Tracking Evidence

| Metric | Measured Value | Traceable File Path | Key / Field in File |
| :--- | :---: | :--- | :--- |
| **Total Test Clips** | **20 clips** | [`ml/runs/final/metrics.json`](../ml/runs/final/metrics.json#L720) | `video.total_video_clips` |
| **Total Video Duration** | **120.0 seconds** | [`ml/runs/final/metrics.json`](../ml/runs/final/metrics.json#L721) | `video.total_duration_seconds` |
| **Ground Truth Events** | **13 events** | [`ml/runs/final/metrics.json`](../ml/runs/final/metrics.json#L722) | `video.ground_truth_events` |
| **Matched Events** | **9 events** | [`ml/runs/final/metrics.json`](../ml/runs/final/metrics.json#L723) | `video.matched_events` |
| **Video Duplicate Rate** | **0.00%** | [`ml/runs/final/metrics.json`](../ml/runs/final/metrics.json#L728) | `video.duplicate_rate` |
| **Ground Truth Manifest** | **20 clips metadata** | [`data/test_videos/video_ground_truth.json`](../data/test_videos/video_ground_truth.json) | Complete ground truth timestamps |

---

## 4. Hardware Latency & Artifact Evidence

| Property | Measured Value | Traceable File Path | Verification Command |
| :--- | :---: | :--- | :--- |
| **CPU p50 Latency** | **45.46 ms** | [`runs/export/edge_benchmark_report.json`](../runs/export/edge_benchmark_report.json) | Measured on host AMD Ryzen 7 7445HS |
| **CPU Throughput** | **21.0 FPS** | [`runs/export/edge_benchmark_report.json`](../runs/export/edge_benchmark_report.json) | Single-stream batch=1 ONNX runtime |
| **YOLO11n Model Size** | **10.17 MB** | [`runs/export/best.onnx`](../runs/export/best.onnx) | SHA-256: `a6b1255e...` |
| **Crack Specialist Size** | **12.18 MB** | [`ml/runs/pothole_yolov8n/weights/best.onnx`](../ml/runs/pothole_yolov8n/weights/best.onnx) | SHA-256: `f8d1d6b9...` |
| **COCO Blocker Size** | **10.24 MB** | [`ml/weights/coco_scene_blocker.onnx`](../ml/weights/coco_scene_blocker.onnx) | SHA-256: `af569e7e...` |
| **Data Leakage Check** | **0 Collisions** | [`ml/data/test_manifest.json`](../ml/data/test_manifest.json) | Verified via `python scripts/verify_leakage.py` |
| **Production Build Size** | **263.45 kB gzip** | `web/dist/` | Verified via `cd web && npm run build` |
