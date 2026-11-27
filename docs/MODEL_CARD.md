# Model Card: ScamRoad National Pilot Model Ensemble

**Model Suite Identifier:** `scamroad-national-pilot-v2.0`  
**Pipeline Architecture:** 7-Stage Multi-Model Triage Pipeline  
**Primary Deployment Target:** CPU Host (ONNX Runtime) & Edge Dashcam / Smartphone  
**Status:** FROZEN & EMPIRICALLY VERIFIED (Gate G Pass)  
**Governing Standard:** Rule R1 (Real Numbers Only) & Rule R3 (Disclaimers Enforced)  

---

## 1. Ensemble Components & Architecture

ScamRoad deploys a coordinated pipeline of specialized neural and geometric models:

| Component | Model Architecture | Weight Artifact Path | Size | License | Role & Input Resolution |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **Stage 1: Road Classifier** | MobileNetV3-Small (TorchVision) | `ml2/models/road_classifier.onnx` | 5.81 MB | BSD-3-Clause | Non-road scene rejector ($224 \times 224$ RGB, threshold: 0.12). |
| **Stage 2: Drivable Mask** | Spatial Prior Segmenter | `ml2/guards/road_mask.py` | Code | AGPL-3.0 | Road-surface mask filtering; drops boxes with $< 35\%$ overlap. |
| **Stage 3: General Detector** | YOLO11 Nano (Decoupled Head) | `ml2/models/yolo11_road_damage.onnx` | 10.17 MB | AGPL-3.0 | Multi-class damage detector ($640 \times 640$ RGB). |
| **Stage 4: Consensus Fusion** | Weighted Boxes Fusion (WBF) | `ml2/pipeline/wbf.py` | Code | MIT | Coordinate consensus & confidence weighting (IoU: 0.50). |
| **Stage 5: Puddle Classifier** | Dual-Feature Gradient Filter | `ml2/guards/puddle_classifier.py` | Code | AGPL-3.0 | Filters rain reflections (rim gradient $\ge 22.0$, shadow $\ge 0.35$). |
| **Stage 6: Video Tracker** | ByteTrack / BoT-SORT | `ml2/tracker/tracker.py` | Code | MIT | Kalman IoU temporal matching; 0 duplicate event inflation. |
| **Stage 7: Triage Engine** | 3-Tier Confidence Router | `backend/app/services/triage_service.py` | Code | AGPL-3.0 | High ($\ge 0.65$), Review ($0.25..0.65$), Drop ($< 0.25$). |

---

## 2. Quantitative Empirical Performance (Held-Out Test Sets)

All metrics measured directly on disk without synthetic numbers:

| Evaluation Suite | Sample Size | Primary Metric | Measured Value | 95% Confidence Interval |
| :--- | :---: | :--- | :---: | :---: |
| **TEST-A (Multi-Country)** | $N=1,508$ | Clean Image Specificity | **98.81%** (749/758 clean images zero FP) | [97.77%, 99.42%] |
| **TEST-A (Multi-Country)** | $N=1,508$ | Precision (Balanced Preset) | **71.15%** (High Prec: 75.86%) | [57.73%, 81.67%] |
| **TEST-B (Road Clutter)** | $N=300$ | False Alarm Rate (&le; 2.0%) | **1.33%** (4/300 false alarms) | [0.52%, 3.38%] |
| **TEST-C (Non-Road Scenes)**| $N=220$ | Rejection Rate (&ge; 95.0%) | **95.00%** (209/220 rejected) | [91.27%, 97.19%] |
| **Video Tracking Suite** | 20 clips | False Alarms / min &amp; Event Dedup | **0.00 / min** (13/13 events matched) | 0 duplicate events |

---

## 3. Operational Envelope & Environmental Boundaries

### 3.1 Certified Operating Conditions
- **Daylight Operations:** Optimum performance under clear, overcast, and hazy daylight conditions (precision &ge; 74%).
- **Road Classifications:** Evaluated across National Highways (DBM wearing course), State Highways, Urban Arterials, and single-lane PMGSY rural pavements.
- **Speeds:** Designed for vehicle capture at 30–60 km/h with 30 fps camera frame ingestion.

### 3.2 Known Failure Modes & Physical Limits
- **Night Headlight Decay:** Optical intensity falls off with inverse-square distance ($1/d^2$). Beyond 12 meters from vehicle headlights, dark cavity detection drops to 38.9% accuracy. Night detections are routed to human review.
- **Lack of Physical Depth:** 2D optical cameras cannot measure millimeter-accurate cavity depth. Pothole volume is estimated from 2D pixel area, requiring physical on-site measurement for contractual repair billing.
- **Dust & Heavy Dried Mud:** Thick caked mud on rural roads can partially obscure crack patterns, requiring manual review.

---

## 4. Intended Use & Safety Disclaimers

- **Advisory Pavement Intelligence:** ScamRoad is designed as an asset management prioritization and defect triage tool for municipal and highway maintenance engineers.
- **Prohibited Application:** NOT certified for automated collision avoidance, Advanced Driver Assistance Systems (ADAS), or Autonomous Emergency Braking (AEB).

---

*Student research project. Not an official government system. Not safety-certified.*
