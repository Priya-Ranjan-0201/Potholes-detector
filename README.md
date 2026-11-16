# ScamRoad

An open-source road defect detection and maintenance tracking platform, built as an undergraduate B.Tech capstone research project.

> **Project Notice:**
> ScamRoad is a student engineering project. It is not an official government system, not affiliated with any highway authority or public works department, and not safety-certified for autonomous driving or critical operations.

---

## What It Is

ScamRoad explores how lightweight computer vision models running on standard hardware can help local communities and maintenance teams detect, track, and coordinate repairs for road damage (potholes and surface cracks) from ordinary photos and dashcam video.

Instead of relying on expensive survey vehicles equipped with specialized LiDAR, ScamRoad runs on standard monocular cameras and consumer CPUs.

---

## What It Does

- **Defect Detection:** Identifies asphalt potholes and distress cracks (alligator, longitudinal, and transverse) using an ONNX-based neural network pipeline.
- **Video Defect Tracking:** Uses spatial-temporal IoU tracking across consecutive dashcam frames to consolidate sightings of the same physical defect into a single record, eliminating duplicate entries (0.00% duplicate rate).
- **Format & Preprocessing Robustness:** Handles real-world input issues including EXIF phone orientation tags, alpha transparency PNGs, 16-bit uint16 images, grayscale, WebP, and AVIF.
- **Input Usability Check:** Validates incoming images before inference and flags unusable frames (under-exposed, over-exposed, or severely motion-blurred).
- **Maintenance Workflow:** Tracks defect lifecycle states (reported &rarr; assigned &rarr; in-progress &rarr; repaired &rarr; verified) with before-and-after image comparison for human engineer review.
- **Privacy Redaction:** Redacts faces and vehicle license plates on edge-captured frames before synchronization.

---

## What It Does Not Do

- **No Depth or Volumetric Calibration:** Monocular imagery measures relative pixel area only. Without calibrated stereo cameras or ground-truth scale markers, the system cannot measure absolute pothole depth in centimeters or asphalt volume in cubic meters.
- **Non-Asphalt Pavement Limitations:** The model was primarily trained on asphalt surfaces. On sett stone, cobblestone, or brick pavements, mortar joints and tile grooves can trigger false alarms.
- **No Autonomous Closing of Repairs:** AI assessment is advisory. A qualified human inspector or engineer must inspect the work and close work orders.
- **No Official Cost Certification:** Budget calculations use an illustrative rate card, not a government Schedule of Rates.

---

## Verified Evaluation Metrics

All metrics below were measured on an untouched held-out evaluation set consisting of **1,728 images** (984 defect images, 744 hard-negative clean road images) across 6 countries and 11 distinct datasets, plus **20 real dashcam video clips**, verified with 0 test leakage against training data.

| Metric | Measured Value | Sample Size / Basis | 95% Confidence Interval |
| :--- | :---: | :---: | :---: |
| **Defect Recall (Sensitivity)** | **97.46%** | 959 / 984 defect images | [96.3%, 98.4%] |
| **Image-Level F1 Score** | **78.83%** | N = 1,728 images | [77.10%, 80.65%] |
| **Image-Level Accuracy** | **70.20%** | N = 1,728 images | [68.06%, 72.46%] |
| **Asphalt Pavement Slices F1** | **96.2% – 99.7%** | USA, Egypt, Japan, Manot, Taroii | — |
| **Non-Asphalt Slices F1** | **0.0% – 42.9%** | Kauevestena sett stone / cobblestone | — |
| **Video Duplicate Rate** | **0.00%** | 20 dashcam video clips | [0.0%, 0.0%] |
| **Host CPU Latency (p50)** | **45.46 ms** | AMD Ryzen 7 7445HS (FP32 ONNX) | — |
| **Throughput** | **21.0 FPS** | AMD Ryzen 7 7445HS (single stream) | — |

Detailed breakdown by country, pavement slice, and failure gallery is documented in [`docs/AI_EVALUATION.md`](docs/AI_EVALUATION.md).

---

## Quick Start (3 Steps)

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Node.js 18+ and npm
- (Optional) PostgreSQL with PostGIS, or SQLite for local evaluation

### 1. Set Up Python Environment
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Start the Backend API
```bash
uvicorn backend.app.main:app --port 8000 --reload
```
The API documentation is available at `http://localhost:8000/docs`.

### 3. Start the Web Frontend
```bash
cd web
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## Repository Structure

```
scam_road/
├── backend/          # FastAPI backend, PostgreSQL/SQLite database models, API v1 routes, tests
├── web/              # React 18, Vite, TypeScript, Tailwind CSS frontend ("Highway Green" palette)
├── edge/             # Edge patrol agent (video frame capture, privacy blur, sync)
├── ml/               # Pipeline evaluation, calibration, and production weights in ml/weights/
├── data/
│   ├── evaluation_set/ # Untouched multi-source test set (1,728 images)
│   └── test_videos/    # 20 dashcam evaluation video clips
├── docker/           # Dockerfiles and Docker Compose manifests
├── docs/             # Engineering reports, audit logs, and provenance documentation
├── scripts/          # Evaluation and utility scripts
└── README.md
```

---

## Documentation Index

- [`docs/FORENSICS.md`](docs/FORENSICS.md) — Root-cause diagnosis of failure cases on new photos and videos.
- [`docs/AI_EVALUATION.md`](docs/AI_EVALUATION.md) — Complete held-out benchmark report across classes and slices.
- [`docs/CLEANUP_LOG.md`](docs/CLEANUP_LOG.md) — Record of purged legacy files and reclaimed storage.
- [`docs/MODELS_AND_DATA.md`](docs/MODELS_AND_DATA.md) — Provenance, licenses, and SHA-256 hashes for models and datasets.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Technical architecture and data flow diagrams.
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — Engineering decision records.
- [`docs/HUMAN_TODO.md`](docs/HUMAN_TODO.md) — Operational tasks requiring human action.

---

## License & Attribution

- **Code:** Licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](LICENSE).
- **Datasets:** Road Damage Dataset 2022 (RDD2022) is used under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (Arya et al., IEEE BigData 2022).
- **Model Checkpoints:** Derived from Ultralytics YOLO models (AGPL-3.0).
