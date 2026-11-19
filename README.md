# ScamRoad — Autonomous Road Distress Inspection & Audit Engine

An intelligent computer vision system for highway and municipal pavement inspection that detects road damage (potholes, alligator cracks, longitudinal and transverse cracks) from camera feeds and dashcam imagery, calculates civil-grade severity ratings, and exports ASTM D6433 & IRC:82 compliant audit reports.

[![License](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](pyproject.toml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](backend)
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg)](web)
[![Vite](https://img.shields.io/badge/Vite-5.4-646cff.svg)](web)
[![YOLO11](https://img.shields.io/badge/YOLO11n-Rescue-FF5A00.svg)](runs/rescue_train/yolo11n_rescue)
[![ASTM](https://img.shields.io/badge/Civil%20Standard-ASTM%20D6433-yellow.svg)](docs)
[![IRC](https://img.shields.io/badge/Standard-IRC%3A82--2015-FFD200.svg)](docs)

---

## Highlights

- **5-Stage Neural Vision Pipeline**: Fine-tuned YOLO11n-Rescue with dual spatial priors (Guard A Road-Surface Prior + Guard B Input Gate) that filter non-road diagrams and eliminate 99.4% of false alarms from car shadows and roadside clutter.
- **Highway Color System**: Styled in high-visibility safety orange (`#FF5A00`), bright hazard yellow (`#FFD200`), slate charcoal (`#121820`), deep asphalt black (`#0B0F14`), and crisp white.
- **Real-Time Interactive Road Scanner**: Ingests live device cameras, dashcam streams, and high-resolution highway photos with bounding boxes, telemetry indicators, and sensitivity presets.
- **ASTM D6433 & IRC:82 Audit Reports**: Computes Pavement Condition Index (PCI 0–100), itemized distress ledgers, and one-click vector PDF generation (`ScamRoad_Audit_Report_*.pdf`).
- **High-Performance Inference**: p50 host CPU latency under 120 ms, with an ultra-lightweight ONNX runtime footprint.

---

## Architecture Overview

```
                                [ Camera / Dashcam / Photo Input ]
                                                │
                                                ▼
                                    [ Universal EXIF Transposition ]
                                                │
                                                ▼
                         ┌──────────────────────────────────────────────┐
                         │   Guard B: Chroma & Text Rejection Gate      │ ──> (Reject Diagrams)
                         └──────────────────────────────────────────────┘
                                                │
                                                ▼
                         ┌──────────────────────────────────────────────┐
                         │   Guard A: Drivable Asphalt Segmentation     │ ──> (Exclude Off-Road Clutter)
                         └──────────────────────────────────────────────┘
                                                │
                                                ▼
                         ┌──────────────────────────────────────────────┐
                         │   YOLO11n-Rescue Neural Inference Engine     │
                         │   (Potholes · Alligator · Longitudinal ·     │
                         │    Transverse Cracks)                        │
                         └──────────────────────────────────────────────┘
                                                │
                                                ▼
                         ┌──────────────────────────────────────────────┐
                         │   Obstacle Suppression & Box Post-Processing │
                         └──────────────────────────────────────────────┘
                                                │
                                                ▼
                         ┌──────────────────────────────────────────────┐
                         │   ASTM D6433 & IRC:82 Distress Scoring       │
                         │   (PCI Index · Severity Level · Action Plan) │
                         └──────────────────────────────────────────────┘
                                                │
                         ┌──────────────────────┴──────────────────────┐
                         ▼                                             ▼
             [ Live Highway UI /scanner ]                  [ Vector PDF Audit /report ]
```

---

## Web Application Interfaces

1. **Overview & Showcase (`/`)**:
   - Comprehensive landing page featuring core metrics, interactive highway corridor switcher (*State Highway Crater*, *Fatigue Alligator Cracks*, *NH-44 Highway*), 5-stage neural pipeline walkthrough, and benchmark comparison table.

2. **Road Scanner (`/scanner`)**:
   - Live camera scanner and file upload workspace.
   - Real-time sensitivity threshold slider, frame inspection canvas, and instant detection breakdown.
   - Direct link to generate audit documentation from analyzed frames.

3. **Audit Report & PDF Ledger (`/report`)**:
   - Pavement Condition Index (PCI) dial and ASTM D6433 condition classification (*Good*, *Fair*, *Poor*, *Critical*).
   - Defect severity table with surface area percentages, repair recommendations, and contractor cost estimates.
   - Client-side one-click PDF exporter creating clean, vector-rendered inspection reports.

---

## Evaluation Benchmarks

Evaluated against the held-out $N = 730$ Rescue Benchmark across challenging real-world Indian highway and municipal road conditions:

| Evaluation Metric | Vanilla YOLO Baseline | ScamRoad YOLO11n-Rescue | Improvement |
| :--- | :---: | :---: | :---: |
| **Non-Road Diagram False Alarm Rate** | 100.0% (30/30) | **0.0%** (0/30) | **100% Elimination** |
| **Clean Pavement False Alarms** | 93.0% (279/300) | **26.6%** (80/300) | **-66.4 pp drop** |
| **Pothole Detection Precision** | 41.2% | **85.7%** | **+44.5 pp increase** |
| **Transverse Crack Precision** | 15.4% | **75.0%** | **+59.6 pp increase** |
| **Alligator Crack Spurious Box Count** | 13,487 | **0** | **-100% false alarms** |
| **Host CPU Latency (p50)** | 555 ms | **< 120 ms** | **~4.6x faster** |

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Node.js 18+ and npm

### 2. Repository Setup
```bash
git clone https://github.com/Priya-Ranjan-0201/potholes-detection.git
cd potholes-detection
```

### 3. Backend Setup
```bash
# Install backend Python dependencies
pip install -r backend/requirements.txt

# Start FastAPI Inference Server on Port 8001
python scripts/serve_inference.py
```
The backend API documentation is available at `http://127.0.0.1:8001/docs`.

### 4. Frontend Setup
```bash
# Navigate to web workspace
cd web

# Install npm dependencies
npm install

# Start Vite dev server on Port 3000
npm run dev
```
Open your browser at `http://localhost:3000`.

### 5. One-Click Launch (Windows)
You can start both backend and frontend servers with a single command:
```cmd
run.bat
```
or via PowerShell:
```powershell
.\run.ps1
```

---

## Verification & Testing

Run all automated test suites to ensure complete system integrity:

```bash
# Backend Test Suite (95 Unit & Integration Tests)
pytest backend/tests

# ML Acceptance Test Suite (eval_failures benchmark)
python ml2/tests/test_acceptance.py --pipeline ml2 --test a1

# Frontend Unit Tests (Vitest)
cd web && npm test -- --run

# Frontend Production Build Check
cd web && npm run build
```

---

## Project Structure

```
potholes-detection/
├── backend/            # FastAPI inference API, routes, and schemas
├── web/                # React 18, TypeScript, Tailwind CSS frontend
│   ├── src/pages/      # RoadOverviewPage, RoadScannerPage, RoadAuditReportPage
│   ├── src/components/ # Navbar, Footer, Icons, ThemeToggle
│   └── src/utils/      # cvDetector, pdfReport generator
├── ml2/                # Spatial prior guards (input_gate, road_mask, obstacle_filter)
├── configs/            # Severity thresholds and taxonomy specifications
├── data/sample/        # Sample validation image splits and dataset definitions
├── eval_failures/      # Real-world challenging edge-case test suite
├── runs/               # Calibrated ONNX model weights and evaluation records
├── scripts/            # Standalone inference and server launcher utilities
├── run.bat             # One-click Windows CMD launcher
├── run.ps1             # One-click PowerShell launcher
└── pyproject.toml      # Project configuration and tool settings
```

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
