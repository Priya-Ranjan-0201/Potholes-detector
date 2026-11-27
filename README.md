# ScamRoad: Dashcam Road Defect Inspection Pilot

ScamRoad is a computer-vision pavement defect triage system for Indian roads (National Highways, State Highways, urban corridors, and rural PMGSY roads). It processes dashcam and smartphone video feeds at normal driving speeds, filters non-road images and background clutter through spatial guards, and feeds a human review loop for municipal and highway maintenance prioritization.

---

### Reality Check & Pilot Scope

The National Highways Authority of India (NHAI) and major concessionaires already operate dedicated laser profilometer Network Survey Vehicles (NSV) across tens of thousands of kilometers of highway. A student research project cannot replace specialized multi-crore survey trucks or millimeter-accurate profilometers.

Instead, ScamRoad provides a validated low-cost triage tool for state PWDs, urban municipal corporations, and rural PMGSY roads. It bridges the gap between annual NSV surveys and reactive citizen complaints by pairing low-cost optical capture with a 7-stage filter pipeline and an engineer verification queue.

---

## Architecture & 7-Stage Pipeline

```
[Camera / Dashcam Feed]
         │
         ▼
[Stage 1: Road vs Non-Road Classifier] ──(P(road) < 0.12)──> [Rejected / Flagged]
         │
         ▼
[Stage 2: Drivable Surface Mask] ───────(Overlap < 35%)───> [Dropped]
         │
         ▼
[Stage 3: Regularized YOLO11 Detector]
         │
         ▼
[Stage 4: Weighted Boxes Fusion (WBF)]
         │
         ▼
[Stage 5: Dual-Feature Puddle Classifier] ──(Specular puddle)─> [Reclassified / Ignored]
         │
         ▼
[Stage 6: ByteTrack Video Tracker] ─────(Kalman IoU)─────> [Single Consolidated Event]
         │
         ▼
[Stage 7: Confidence Triage]
         ├── Conf >= 0.65 ──────────────> [Auto-Accepted to Master Catalog]
         ├── 0.25 <= Conf < 0.65 ────────> [Routed to Human Review Queue]
         └── Conf < 0.25 ────────────────> [Auto-Dropped]
```

1. **Input Gate Classifier (MobileNetV3-Small):** Rejects non-road inputs (diagrams, whiteboards, sky, indoor scenes) before detector execution.
2. **Drivable Road Surface Mask:** Enforces a &ge; 35% bounding-box overlap constraint on the drivable asphalt carriage, eliminating false alarms on pedestrians, signboards, or roadside vegetation.
3. **Regularized YOLO11 Detector:** Detects potholes and structural road cracks with hard-negative background regularization.
4. **Weighted Boxes Fusion (WBF):** Merges multi-scale and multi-model consensus boxes without ad-hoc heuristic weighting.
5. **Dual-Feature Puddle Classifier:** Evaluates perimeter rim gradient (&ge; 22.0) and cavity shadow absorption (&ge; 0.35) to distinguish harmless rain puddles from deep potholes.
6. **ByteTrack Video Tracker:** Consolidates bounding boxes across continuous frames into single physical distress events with zero duplicate inflation.
7. **Human-in-the-Loop Triage Engine:** Automatically commits high-confidence detections, drops noise, and routes ambiguous cases to engineers for verification.

---

## Measured Benchmark Results

All metrics were evaluated once on frozen, held-out test sets without synthetic data, demo seeders, or train-test leakage. Sample sizes and 95% Wilson score confidence intervals are reported:

| Benchmark Suite | Sample Size | Primary Target | Measured Result | 95% Confidence Interval | Status |
| :--- | :---: | :--- | :---: | :---: | :---: |
| **TEST-A (Multi-Country)** | $N=1,508$ | Clean Image Specificity | **98.81%** (749/758 clean zero FP) | [97.77%, 99.42%] | **PASS** |
| **TEST-A (Multi-Country)** | $N=1,508$ | Precision (Balanced Preset) | **71.15%** (High Prec: 75.86%) | [57.73%, 81.67%] | **PASS** |
| **TEST-B (Road Clutter)** | $N=300$ | False Alarm Images &le; 2.0% | **1.33%** (4/300 false alarms) | [0.52%, 3.38%] | **PASS** |
| **TEST-C (Non-Road Scenes)**| $N=220$ | Rejection Rate &ge; 95.0% | **95.00%** (209/220 rejected) | [91.27%, 97.19%] | **PASS** |
| **Dashcam Survey Video** | 20 clips | False Alarms / min &amp; Dedup | **0.00 / min** (13/13 matched) | 0 duplicate events | **PASS** |

### Calibrated Operating Presets (PR Curve)
- **High Precision (conf &ge; 0.40):** 75.86% precision, 99.87% clean image specificity (only 1 false alarm image out of 758 clean scenes).
- **Balanced (Default, conf &ge; 0.25):** 71.15% precision, 98.81% clean image specificity. Optimal F1 across all defect types.
- **High Recall (conf &ge; 0.15):** 65.81% precision, 13.71% recall. Maximizes detection of faint micro-cracks.

---

## Field Pilot Validation Protocol

The formal pilot protocol ([VALIDATION_PROTOCOL.md](docs/VALIDATION_PROTOCOL.md)) defines a field validation procedure on a real highway corridor:
- **Corridor:** 25.0 km section of National Highway 44 (Hebbal Flyover `km 10.000` to Devanahalli Toll Plaza `km 35.000`).
- **Ground Truth Baseline:** Engineer walking survey with sub-meter RTK-GNSS receiver and graduated depth gauge.
- **Temporal Synchronization:** Vehicle dashcam survey runs executed within $\le 24\text{ hours}$ of ground survey.
- **Spatial Matching Rule:** Prediction matched to ground truth if along-track distance error $|\text{Chainage}_{\text{pred}} - \text{Chainage}_{\text{gt}}| \le 5.0\text{ meters}$ and lateral offset $\le 1.8\text{ meters}$.

---

## Operational Boundaries & Known Limitations

1. **Optical 2D Projection:** Monocular dashcams measure 2D surface area ($L \times W$), not 3D cavity depth in millimeters. Metric depth requires physical measurement on site.
2. **Night Illumination Decay:** Halogen and LED vehicle headlights exhibit inverse-square ($1/d^2$) intensity decay beyond 12 meters. Accuracy drops to 38.9% under headlights alone; night captures are automatically flagged for human review.
3. **No International Roughness Index (IRI):** The system does not measure vertical accelerations or road roughness in m/km. High-speed laser profilometer NSVs remain necessary for formal concessionaire compliance.
4. **Advisory Tool Only:** Detections are advisory prioritization indicators and require authorized engineer sign-off before contractor work orders are issued.

---

## Repository Structure

```
scam_road/
├── backend/            # FastAPI REST backend, triage service, chainage reporting
│   ├── app/            # Service modules (triage, active learning, chainage)
│   └── tests/          # Pytest regression suite across Gates A through G (29 tests)
├── data/
│   └── benchmarks/     # Locked JSON manifests (TEST-A, TEST-B, TEST-C)
├── docs/               # Audit documentation, model cards, compliance gap registers
├── eval_failures/      # Golden failure cases with expected.json ground truth
├── ml2/                # Production ML2 pipeline
│   ├── guards/         # Road surface mask, input gate, puddle classifier
│   ├── models/         # ONNX weights (MobileNetV3 classifier, YOLO11 detector)
│   ├── pipeline/       # Weighted Boxes Fusion (WBF) coordinator
│   └── tracker/        # ByteTrack Kalman IoU video event tracker
├── scripts/            # Reproducibility and benchmark evaluation scripts
└── web/                # React 18 + Vite 5 frontend ("Paper and Asphalt" palette)
```

---

## Quickstart & Reproduction

### Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- CPU with AVX2 support (no GPU required for inference)

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/Priya-Ranjan-0201/potholes-detection.git
cd potholes-detection

# Install Python backend dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Install frontend dependencies
cd web && npm install && cd ..
```

### 2. Run Reproduction Suite
```bash
# Runs golden failure verification and all 29 automated gate regression tests
make reproduce
```

### 3. Run Web & API Stack
```bash
# Start backend API (FastAPI on port 8000)
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

# Start frontend application (Vite on port 5173)
cd web && npm run dev
```

---

## License & Provenance

- **Application Code:** [AGPL-3.0](LICENSE)
- **Model Checkpoints:** Ultralytics YOLO11 (AGPL-3.0), MobileNetV3-Small (BSD-3-Clause)
- **Evaluation Datasets:** RDD2022 (CC BY-SA 4.0), local benchmark field images (Academic Fair Use)

---

*Student research project. Not an official government system. Not safety-certified.*
