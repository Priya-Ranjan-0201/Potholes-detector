# AI-Powered Road and Infrastructure Damage Detection and Severity Assessment

A computer-vision system for surveying road and civic infrastructure that detects damage such as potholes, cracks, and structural deterioration from images or video, and assigns a severity score to each detected issue to help prioritise repair and maintenance work.

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](web/src)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL_3.0-blue.svg)](LICENSE)
[![Python: 3.12](https://img.shields.io/badge/python-3.12-blue)](pyproject.toml)

> **Notice:** Student research project. Not an official government system. Not safety-certified.

---

## Overview

RoadSurvey AI explores how lightweight computer vision models running on standard hardware can help local communities and highway authorities detect, track, and score the severity of road and civic infrastructure damage from ordinary photos and dashcam video.

Instead of relying on expensive survey vehicles equipped with specialized 3D LiDAR laser profilers ($100,000+), the platform runs on commodity monocular cameras and consumer CPUs, outputting transparent, civil-engineering-aligned severity scores and prioritised repair queues.

---

## What It Does

- **Road Damage Detection:** Identifies asphalt potholes (including water-filled cavities), longitudinal cracks, transverse cracks, and alligator fatigue cracking.
- **Civic Infrastructure Deterioration:** Secondary screening module detects concrete cracks, spalling, exposed rebar, corrosion/rust staining, and efflorescence on bridges, culverts, and retaining walls.
- **Transparent Severity Scoring:** Calculates a continuous 0–100 severity score with four levels (Low, Moderate, High, Critical) derived from physical evidence: defect type, relative surface area, wheel-path risk, and cluster density.
- **Repair Prioritisation:** Ranks survey issues by Priority Score (Severity × Exposure) based on user-entered road class and traffic ratings.
- **Spatial-Temporal Video Tracking:** Employs ByteTrack associative tracking across consecutive dashcam frames to eliminate duplicate defect reports (0.00% duplicate rate).
- **Survey Records & Export:** Archives inspection runs with plain-text location coordinates, before/after re-inspection photo comparisons, and export to CSV, GeoJSON, and printable reports.
- **Privacy Preservation:** Strips EXIF metadata by default and applies automated Gaussian blurring over human faces and vehicular license plates on stored media.

---

## How It Works in 10 Steps

1. Ingestion decodes JPEG, PNG, WebP, and AVIF, applying universal EXIF transposition to correct phone orientation.
2. Stage A Input Gate evaluates image chroma, top title banners, and text glyph density, rejecting diagrams with HTTP 422.
3. Stage B Road-Region Prior checks drivable surface boundaries ($y \ge 0.33$) to eliminate sky, canopy, and signboard false alarms.
4. Stage C Neural Inference runs fine-tuned YOLO11n for cavity detection and YOLOv8n for pavement distress.
5. An expanded 11-class COCO obstacle blocker suppresses candidates occluded by vehicles, pedestrians, or roadside furniture.
6. Predictions are reconciled via confidence-weighted fusion and coordinate inversion.
7. Stage D Severity Engine evaluates class base hazard, relative pixel area, wheel-track placement, and cluster extents.
8. Every issue receives a human-readable assessment rationale explaining its assigned level.
9. In video streams, associative IoU tracking tracks defects across frames (`min_hits >= 3`), logging each physical hazard once.
10. Verified survey records and maintenance priority rankings are exported to standard CSV and GeoJSON formats.

---

## Verified Evaluation Results

All numbers below were measured once on an untouched, held-out evaluation suite of **1,728 images** across 6 countries and 11 distinct datasets, plus **20 real dashcam video clips**, verified with 0 test leakage (zero SHA-256 or perceptual hash collisions).

| Metric | Measured Value | 95% Bootstrap CI | Sample Size | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Image-Level Defect Recall** | **97.46%** | [96.3%, 98.4%] | 959 / 984 defect images | **Met** (Target ≥ 90%) |
| **Image-Level F1 Score** | **78.83%** | [77.10%, 80.65%] | N = 1,728 images | **Partially Met** |
| **Asphalt Pavement Slices F1** | **96.2% – 99.7%** | — | USA, Egypt, Japan, Manot, Taroii | **Met** |
| **Off-Road False Alarms (Clutter)** | **0.0%** | [0.0%, 0.4%] | N = 60 (GUARD-SET) | **Met** (Target ≤ 2%) |
| **Diagram / Graphic Rejection** | **100.0%** | [95.0%, 100.0%] | HTTP 422 Gate | **Met** (Target ≥ 95%) |
| **Video Duplicate Event Rate** | **0.00%** | [0.00%, 0.05%] | 20 Dashcam Clips | **Met** (Target < 1%) |
| **Host CPU Latency (p50)** | **45.46 ms** | — | AMD Ryzen 7 7445HS | **21.0 FPS** |

*Full evaluation reports, confusion matrices, and per-slice tables are documented in [`docs/AI_EVALUATION.md`](docs/AI_EVALUATION.md) and [`ml/runs/final/metrics.json`](ml/runs/final/metrics.json).*

---

## Known Limitations

- **Monocular Depth:** Relative pixel area only. True volumetric measurements or centimeter depth require physical calibration targets or stereoscopic cameras.
- **Non-Asphalt Pavements:** Stone sett paving and cobblestones exhibit natural mortar joints that resemble alligator fractures (0% F1 on Kauevestena sett stone patches).
- **Structural Screening Scope:** Automated detection of bridge cracks, spalling, and rebar serves as a preliminary screening aid and does not substitute for a certified structural engineer inspection.

---

## Quick Start

### 1. Installation
```bash
git clone https://github.com/your-username/scam_road.git
cd scam_road
pip install -r backend/requirements.txt
cd web && npm install && cd ..
```

### 2. Start AI Backend Server
```bash
python scripts/serve_inference.py
# Backend live on http://localhost:8000
# OpenAPI Docs: http://localhost:8000/docs
```

### 3. Start Frontend Client
```bash
cd web
npm run dev
# Frontend live on http://localhost:3000
```

---

## Automated Verification Tests

```bash
# Run full backend test suite (89 tests)
pytest backend/tests

# Run frontend production build (type checking & asset compilation)
cd web && npm run build
```

---

## Repository Structure

```
scam_road/
├── backend/            # FastAPI REST API, schemas, and database models
├── web/                # React 18, Vite, TypeScript, tokens.css, and pages
├── ml/                 # Data manifests, evaluation scripts, and run metrics
├── config/             # Severity scoring weights (severity.yaml)
├── data/               # Guard set images and local sample test sets
├── docs/               # Technical documentation, viva prep, and forensic reports
└── scripts/            # Standalone evaluation and server launcher utilities
```

---

## Datasets & Provenance

- **RDD2022 (Road Damage Dataset):** Global multi-national benchmark covering India, USA, Japan, and Egypt. Licenced under CC BY-SA 4.0.
- **Deep Pavements Dataset:** Real pavement surface patches across diverse paving materials. Open research license.
- **CODEBRIM:** Concrete defect bridge image dataset for spalling, crack, and rebar detection. Academic use.
- **Taroii & Manot Benchmarks:** Road distress validation sets. Licenced under MIT / CC BY 4.0.

Full dataset URLs, SHA-256 hashes, and license texts are detailed in [`docs/MODELS_AND_DATA.md`](docs/MODELS_AND_DATA.md).

---

## Acknowledgements

Developed as an undergraduate Senior Capstone Project in Computer Science & Engineering. Code is released under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.
