# Repository Cleanup Log (Phase 6)

This document records the safe cleanup of legacy, unreferenced, and duplicate artifacts in ScamRoad, in compliance with **Rule G7 (Safe Cleanup Protocol)**.

---

## 1. Safe Cleanup Protocol Verification

Per Rule G7:
1. **Identification & Documentation:** Candidate files were audited to ensure zero active production code or test references.
2. **Staging:** Candidates were moved to `_staging_trash/` without immediate permanent deletion.
3. **Verification Suite Execution:**
   - **Backend Automated Tests:** `backend/tests/test_no_fake_data.py` and `backend/tests/test_pipeline_integrity.py` executed. All 11 tests PASSED in 18.74s.
   - **Frontend Production Build:** `web/` built with `tsc && vite build`. Completed in 6.42s with 0 errors (gzip bundle: 263.45 kB).
   - **Production Inference Verification:** 50 real held-out images processed through `/api/v1/infer` via `scripts/run_evaluation_samples.py`. All 50 processed successfully.
4. **Purge:** Upon passing all verification gates, `_staging_trash/` was safely removed.

---

## 2. Removed Artifacts Inventory

| File / Directory Path | Type | Size | SHA-256 Hash | Reason for Removal |
| :--- | :---: | :---: | :---: | :--- |
| `yolo11n.pt` | File | 5.61 MB | `0ebbc80d4a7680d1...` | Duplicate root PyTorch weights; superseded by production `runs/export/best.onnx` and `ml/weights/best.onnx`. |
| `cloud_orchestrator.py` | File | 16.21 KB | `2be5d8433fbdad0b...` | Legacy cloud training orchestrator script; superseded by standard Docker Compose. |
| `checkpoint_manager.py` | File | 9.68 KB | `f8abc8f657cbb043...` | Legacy cloud checkpoint synchronization script; unreferenced in production. |
| `experiment_manager.py` | File | 8.14 KB | `3e7e99cb0680dd03...` | Legacy experiment manager; unreferenced in production. |
| `environment_manager.py` | File | 4.11 KB | `d224485b5379d42c...` | Legacy cloud environment setup script; unreferenced. |
| `cloud_config.yaml` | File | 2.18 KB | `01400171f9cc6f00...` | Duplicate cloud config in repository root; canonical copy retained in `configs/`. |
| `ml/weights/pavimentos_dfine_l.onnx` | File | 125.31 MB | `b6b76e8a8e59bdd6...` | Uncalibrated D-FINE Large DETR model weight; diagnosed in Phase 1 as inaccurate and replaced by calibrated YOLO11n + crack specialist. |
| `ml/weights/pyresearch_pothole_best.onnx` | File | 36.97 MB | `54f09e7213bee6a9...` | Uncalibrated secondary YOLOv12 model weight; unreferenced in production. |
| `ml/weights/pyresearch_pothole_best.pt` | File | 18.63 MB | `4a4aa7e6a3f2f9d5...` | PyTorch checkpoint for secondary YOLOv12; unreferenced in production. |
| `scripts/build_notebooks.py` | File | 23.69 KB | `cfae44ae490e3f3d...` | Legacy Jupyter notebook builder script; unreferenced in production. |
| `scripts/build_recovery_notebooks.py` | File | 18.05 KB | `c4baa538ab15dc41...` | Legacy recovery notebook generator; unreferenced. |
| `scripts/publish_to_kaggle.py` | File | 4.55 KB | `5d554c31f3efd797...` | One-off Kaggle dataset uploader script; unreferenced. |
| `scripts/test_live_poly.py` | File | 1.68 KB | `a8fc3a38ac98f8df...` | Ad-hoc polygon test script; covered by automated pytest `test_pipeline_integrity.py`. |
| `scripts/serve_inference.py` | File | 818 B | `623feeeb49bd6fab...` | Redundant standalone server; superseded by FastAPI `backend/app/main.py`. |
| `scripts/make.ps1` | File | 6.14 KB | `a089660b090f9ab3...` | Redundant PowerShell make script; superseded by `run.ps1` and `Makefile`. |
| `runs/detect/ml` | Directory | 112.44 MB | N/A | Intermediate training checkpoints from unified YOLO11n run; exported to production ONNX. |
| `runs/detect/val*` | Directory | 6.31 MB | N/A | Validation output directories from intermediate training runs. |

**Total Reclaimed Disk Space:** ~308.7 MB.

---

## 3. Retained Core Assets & Provenance

The following production model weights and test suites are strictly preserved:

1. **Production General Defect Detector:**
   - Path: `runs/export/best.onnx` and `ml/weights/yolo11n_pothole_best.onnx`
   - Architecture: YOLO11n (ONNX FP32)
   - Size: 10.66 MB
   - Role: Fast pothole and general distress detection (conf >= 0.20).
2. **Production Crack Specialist:**
   - Path: `ml/runs/pothole_yolov8n/weights/best.onnx`
   - Architecture: YOLOv8n (ONNX FP32)
   - Size: 12.78 MB
   - Role: Pothole & crack distress classifier (conf >= 0.65).
3. **COCO Obstacle Gate:**
   - Path: `ml/weights/coco_scene_blocker.onnx`
   - Architecture: YOLO11n COCO (ONNX FP32)
   - Size: 10.74 MB
   - Role: Suppresses road detections over vehicles, pedestrians, and traffic signs.
4. **Instance Segmentation Specialist:**
   - Path: `ml/weights/yolov8n_seg_pothole.onnx`
   - Architecture: YOLOv8n-Seg (ONNX FP32)
   - Size: 13.29 MB
   - Role: Optional polygon mask extraction.
5. **Multi-Source Evaluation Dataset:**
   - Path: `data/evaluation_set/` (1,728 images: 984 defects, 744 hard negatives across 6 countries & 11 datasets).
6. **Dashcam Video Suite:**
   - Path: `data/test_videos/` (20 real dashcam video test clips with ground truth).

---

## 4. Final Clean Repository Structure

```
scam_road/
├── backend/               # FastAPI application, database models, API v1 routes, tests
├── web/                   # React 18 + Vite + TypeScript frontend ("Highway Green" palette)
├── edge/                  # Edge patrol capture, privacy blur, and offline sync agent
├── ml/                    # Pipeline evaluation, calibration, and production weights in ml/weights/
├── data/
│   ├── evaluation_set/    # Untouched multi-source held-out test set (1,728 images)
│   └── test_videos/       # 20 dashcam evaluation video clips
├── docs/                  # Engineering reports, audit logs, and provenance documentation
├── docker/                # Production Dockerfiles and Docker Compose manifests
├── scripts/               # Developer utilities (run_evaluation, verify_leakage)
└── README.md              # Project documentation
```
