# Research Pilot Proposal: Dashcam Pavement Defect Triage

**Submitted To:** State Public Works Department (PWD) / NHAI Project Implementation Unit (PIU)  
**Submitted By:** Academic Research Institution (Lead Student Researcher & Faculty Advisor)  
**Project:** ScamRoad — Autonomous Pavement Distress Inspection Pilot  
**Corridor Proposed:** National Highway 44 (Hebbal Flyover `km 10.000` to Devanahalli Toll Plaza `km 35.000`) — 25.0 km  
**Status:** Academic Research Pilot Proposal (Not an Official Government System)  

---

## 1. Executive Summary & Problem Statement

Road distresses, particularly monsoon potholes and structural fatigue cracking, compromise motorist safety and accelerate vehicular maintenance costs across Indian highways. While the National Highways Authority of India (NHAI) mandates semi-annual surveys using high-speed laser profilometer Network Survey Vehicles (NSV), these systems cost over &#8377;1.5 Crore per unit and cannot be deployed continuously or across secondary urban and rural PMGSY roads.

Between scheduled NSV cycles, local road authorities rely on manual visual complaints. This proposal outlines a **validated, low-cost optical triage pilot**: using windshield-mounted consumer dashcams (1080p, 30 fps) operating at normal traffic speeds (40–60 km/h), paired with an open-source 7-stage computer vision pipeline and a structured human engineering review loop.

---

## 2. Technical Methodology

The pilot deploys a 7-stage sequential triage engine:
1. **Input Gate Classifier (MobileNetV3-Small):** Rejects non-road inputs (diagrams, sky, dashboard interiors) with 95.00% specificity.
2. **Drivable Pavement Surface Mask:** Enforces &ge; 35% bounding box overlap on the drivable asphalt carriage, eliminating false alarms on pedestrians, signboards, or roadside vegetation.
3. **Regularized YOLO11 Neural Detector:** Detects potholes and structural road cracking with hard-negative background regularization.
4. **Weighted Boxes Fusion (WBF):** Merges multi-scale and multi-model detections with coordinate consensus.
5. **Dual-Feature Puddle Classifier:** Evaluates perimeter rim gradient and cavity shadow absorption to distinguish standing rain puddles from dangerous deep potholes.
6. **ByteTrack Video Tracker:** Consolidates bounding boxes across continuous video frames into single physical distress events with zero duplicate inflation.
7. **Human-in-the-Loop Triage Engine:** Automatically commits high-confidence detections (&ge; 0.65), drops noise (< 0.25), and routes ambiguous cases (0.25–0.65) to state PWD highway engineers for verification.

---

## 3. Measured Empirical Performance (Held-Out Benchmarks)

All metrics were evaluated once on held-out test sets without synthetic data or train-test leakage:

| Benchmark Dataset | Sample Size | Primary Target | Measured Empirical Result | 95% Confidence Interval |
| :--- | :---: | :--- | :---: | :---: |
| **TEST-A (Multi-Country)** | $N=1,508$ | Clean Image Specificity | **98.81%** (749/758 clean images zero FP) | [97.77%, 99.42%] |
| **TEST-A (Multi-Country)** | $N=1,508$ | Detection Precision | **71.15%** (Balanced preset) | [57.73%, 81.67%] |
| **TEST-B (Road Clutter)** | $N=300$ | False Alarm Images &le; 2.0% | **1.33%** (4/300 false alarms) | [0.52%, 3.38%] |
| **TEST-C (Non-Road Scenes)**| $N=220$ | Rejection Rate &ge; 95.0% | **95.00%** (209/220 rejected) | [91.27%, 97.19%] |
| **Dashcam Survey Video** | 20 clips | False Alarms / min &amp; Event Dedup | **0.00 / min** (13/13 events matched) | 0 duplicate events |

---

## 4. Known Technical Limitations & Boundary Conditions

1. **Optical 2D Projection Only:** Dashcams measure surface width and length, **not** 3D cavity depth in millimeters.
2. **Night Headlight Attenuation:** In darkness, headlight inverse-square ($1/d^2$) decay drops accuracy to 38.9%. Night runs are restricted or automatically flagged for review.
3. **International Roughness Index (IRI):** The system does not measure vertical vehicular accelerations or IRI; it does not replace profilometer NSVs.

---

## 5. Field Pilot Plan (25.0 km NH-44 Corridor)

### 5.1 Study Stretch & Synchronization
- **Location:** NH-44 North Corridor (Bengaluru–Hyderabad), from Hebbal Flyover (`km 10.000`) to Devanahalli Toll Plaza (`km 35.000`).
- **Baseline Ground Truth:** Dedicated walking engineer survey using sub-meter RTK-GNSS receiver and graduated depth gauge.
- **Synchronization Window:** Vehicle camera survey executed within $\le 24\text{ hours}$ of ground survey.

### 5.2 Pilot Spatial Matching Rule
An AI detection is matched to a ground truth record if and only if along-track distance $|\text{Chainage}_{\text{pred}} - \text{Chainage}_{\text{gt}}| \le 5.0\text{ meters}$ and lateral offset $|\Delta \text{Lane}| \le 1.8\text{ meters}$.

---

## 6. Safety, Privacy & Risk Mitigation

- **Traffic Safety:** Survey vehicles operate at nominal highway speeds with traffic flow; no traffic stoppages or lane closures required.
- **DPDP Act 2023 Compliance:** Automatic edge blurring of all pedestrian faces and vehicle registration number plates. All survey data processed within Indian borders.
- **Zero Hallucination Guarantee:** No synthetic mock data or hardcoded numbers permitted in production reports.

---

## 7. Institutional Support Needed from PWD / NHAI

1. **Permission & Security Clearance:** Formal approval for academic survey runs along the specified 25 km pilot stretch.
2. **Ground Truth Validation Access:** Cooperation with local junior engineers to review the walking survey logbook for spatial cross-validation.
3. **Reviewer Interface Trial:** Access for two PWD maintenance engineers to trial the `/review` triage queue interface over a 14-day evaluation period.

---

*Student research project. Not an official government system. Not safety-certified.*
