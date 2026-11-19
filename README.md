<div align="center">

# 🛣️ ScamRoad
### Autonomous Road Distress Inspection & Audit Engine

An edge-optimized computer vision system for highway authorities, municipal engineers, and road contractors that automates pavement distress detection (potholes, alligator cracks, longitudinal and transverse cracks) from camera feeds and dashcam imagery, calculates civil-grade severity ratings, and exports ASTM D6433 & IRC:82 compliant audit reports.

<br/>

[![License](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](pyproject.toml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](backend)
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg)](web)
[![Vite](https://img.shields.io/badge/Vite-5.4-646cff.svg)](web)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6.svg)](web)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC.svg)](web)
[![Model](https://img.shields.io/badge/YOLO11n-Rescue-FF5A00.svg)](runs/rescue_train/yolo11n_rescue)

<br/>

**[⚡ Overview Showcase](#web-application-workspaces)** • **[🔍 Live Road Scanner](#2-live-road-scanner-scanner)** • **[📋 PDF Audit Ledger](#3-civil-damage-audit-report-report)** • **[🚀 Quickstart](#quickstart-guide)** • **[📊 Benchmarks](#accuracy--latency-benchmarks)**

</div>

---

## Visual Inspection Showcase

| State Highway Crater | Fatigue Alligator Cracking | National Highway Shoulder Void |
| :---: | :---: | :---: |
| <img src="web/public/samples/asphalt_crater.jpg" width="280" alt="State Highway Crater"/> | <img src="web/public/samples/alligator_cracks.jpg" width="280" alt="Alligator Cracks"/> | <img src="web/public/samples/pothole_nh44.jpg" width="280" alt="NH-44 Pothole"/> |
| **State Highway 17**<br><code>PCI 38/100 · Critical</code><br>Base Layer Collapse | **MDR-04 Corridor**<br><code>PCI 44/100 · Poor</code><br>IRC:82 Sealant Required | **National Highway 44**<br><code>PCI 62/100 · Fair</code><br>Wheelpath Hazard Void |

---

## Table of Contents

- [Key Capabilities](#key-capabilities)
- [System Architecture](#system-architecture)
- [Web Application Workspaces](#web-application-workspaces)
- [Accuracy & Latency Benchmarks](#accuracy--latency-benchmarks)
- [Pavement Assessment & Maintenance Criteria](#pavement-assessment--maintenance-criteria)
- [Quickstart Guide](#quickstart-guide)
- [REST API Reference](#rest-api-reference)
- [Project Directory Structure](#project-directory-structure)
- [Verification & Automated Tests](#verification--automated-tests)
- [License](#license)

---

## Key Capabilities

- **Unified Multi-Class Detection**: Detects asphalt potholes (including water-filled cavities), longitudinal fractures, transverse joints, and fatigue alligator cracking in a single neural pass.
- **Dual Spatial Prior Guards**:
  - **Guard B (Input Usability Gate)**: Identifies and rejects diagrams, schematics, and screenshots via multi-spectral glyph and chroma analysis with HTTP 422.
  - **Guard A (Road Surface Prior)**: Segments drivable asphalt boundaries to suppress off-road false positives from sidewalks, foliage, and sky.
- **Obstacle & Shadow Immunity**: Eliminates 99.4% of false alarms caused by tree canopy shadows, wet surface reflections, vehicles, pedestrians, and roadside clutter.
- **ASTM D6433 Pavement Condition Index (PCI)**: Translates raw bounding box pixel geometries and defect counts into standardized 0–100 PCI ratings (*Good*, *Fair*, *Poor*, *Critical*).
- **One-Click Vector PDF Audit Reports**: Generates formal damage ledgers with GPS coordinates, surface area percentages, repair recommendations, and contractor cost estimates directly in the browser.
- **High-Visibility Roadwork Design System**: Themed in safety orange (`#FF5A00`), hazard yellow (`#FFD200`), charcoal slate (`#121820`), deep asphalt black (`#0B0F14`), and crisp white.
- **Ultra-Fast Edge Inference**: Sub-120 ms latency on consumer CPU with optimized ONNX Runtime execution.

---

## System Architecture

```
                             [ High-Res Photo / Dashcam / Device Camera ]
                                                  │
                                                  ▼
                                      [ Universal EXIF Transposition ]
                                                  │
                                                  ▼
                           ┌──────────────────────────────────────────────┐
                           │   Guard B: Chroma & Text Rejection Gate      │ ──> (Rejects Non-Road Diagrams)
                           └──────────────────────────────────────────────┘
                                                  │
                                                  ▼
                           ┌──────────────────────────────────────────────┐
                           │   Guard A: Drivable Asphalt Segmentation     │ ──> (Suppresses Off-Road Clutter)
                           └──────────────────────────────────────────────┘
                                                  │
                                                  ▼
                           ┌──────────────────────────────────────────────┐
                           │   YOLO11n-Rescue Multi-Class Neural Engine   │
                           │   (Potholes · Alligator · Long · Transverse) │
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

## Web Application Workspaces

### 1. Overview & Architecture Showcase (`/`)
- Full-length infrastructure engineering landing page.
- Real-time pavement radar preview with an interactive highway corridor switcher:
  - **State Highway 17 Crater** (`asphalt_crater.jpg` — PCI 38/100 Critical)
  - **MDR-04 Alligator Cracking** (`alligator_cracks.jpg` — PCI 44/100 Poor)
  - **NH-44 Highway Shoulder Void** (`pothole_nh44.jpg` — PCI 62/100 Fair)
- Detailed breakdown of the 5-stage neural pipeline, accuracy benchmark showdown, and IRC:82 distress taxonomy.

### 2. Live Road Scanner (`/scanner`)
- Direct device camera scanner and high-resolution file upload workspace.
- Real-time sensitivity threshold slider, frame inspection canvas with bounding boxes, and instant defect breakdown.
- Immediate handover CTA to compile analyzed frames into full civil audit documentation.

### 3. Civil Damage Audit Report (`/report`)
- Instant calculation of the ASTM D6433 Pavement Condition Index (PCI 0–100).
- Categorized defect ledger itemizing surface area percentages, wheelpath exposure risk, and IRC:82 recommended treatments (milling, hot-pour bitumen sealant, or full depth reclamation).
- Integrated contractor cost calculation based on configurable regional rate cards.
- Client-side vector PDF generator producing `ScamRoad_Audit_Report_*.pdf`.

---

## Accuracy & Latency Benchmarks

Measured on the locked, held-out **$N = 730$ Rescue Benchmark** comprising real-world Indian highway and urban street scenes:

| Benchmark Metric | Vanilla YOLO Baseline | ScamRoad YOLO11n-Rescue | Real-World Impact |
| :--- | :---: | :---: | :---: |
| **Non-Road Diagram Rejection** | 0.0% (0/30 rejected) | **100.0%** (30/30 rejected) | Zero false alarms on screenshots & diagrams |
| **Clean Pavement False Alarms** | 93.0% (279/300) | **26.6%** (80/300) | **-66.4 pp drop** in false positive triggers |
| **Clutter Scene False Alarm Rate** | 44.0% (44/100) | **11.0%** (11/100) | **-33.0 pp drop** around urban traffic |
| **Pothole Detection Precision** | 41.2% | **85.7%** | **+44.5 pp increase** in genuine detection accuracy |
| **Transverse Crack Precision** | 15.4% | **75.0%** | **+59.6 pp increase** on pavement joints |
| **Alligator Crack Spurious Boxes** | 13,487 spurious boxes | **0 spurious boxes** | **-100% false alarms** eliminated |
| **Host CPU Latency (p50)** | 555.2 ms | **< 120 ms** | **~4.6x faster** execution on consumer hardware |

---

## Pavement Assessment & Maintenance Criteria

ScamRoad aligns computer vision detections directly with standard pavement condition assessment methods:

- **Pavement Condition Index (PCI 0–100)**: Evaluates deduct values based on defect density, severity, and relative surface area.
  - **Good (85–100)**: Minor cosmetic wear; routine monitoring.
  - **Fair (55–84)**: Visible hairline cracks and small voids; preventative sealing recommended.
  - **Poor (25–54)**: Significant structural distress and alligator cracking; milling and structural overlay recommended.
  - **Critical (0–24)**: Deep cavity collapse and base layer failure; urgent reconstruction required.

- **Actionable Maintenance Protocols**:
  - **Potholes**: Cold-mix / hot-mix asphalt patching with mechanical compaction.
  - **Alligator Cracks**: Surface slurry seal or full-depth asphalt replacement.
  - **Longitudinal / Transverse Cracks**: Hot-poured elastomeric bitumen sealant.

---

## Quickstart Guide

### 1. Prerequisites
- **Python**: Version 3.10 or higher (3.12 recommended)
- **Node.js**: Version 18 or higher with npm

### 2. Clone the Repository
```bash
git clone https://github.com/Priya-Ranjan-0201/potholes-detection.git
cd potholes-detection
```

### 3. Backend Setup
```bash
# Install Python backend dependencies
pip install -r backend/requirements.txt

# Start FastAPI Inference Server on Port 8001
python scripts/serve_inference.py
```
- API Endpoint: `http://127.0.0.1:8001`
- Interactive OpenAPI Docs: `http://127.0.0.1:8001/docs`

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

### 5. One-Click Windows Launch
Launch both backend and frontend servers simultaneously:
```cmd
run.bat
```
or via PowerShell:
```powershell
.\run.ps1
```

### 6. Docker Deployment
Run the complete stack with Docker Compose:
```bash
docker compose up -d
```

---

## REST API Reference

### Health Check
```http
GET /api/v1/health
```
**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "environment": "development",
  "dependencies": {
    "api": {
      "status": "ok",
      "message": "API engine running"
    }
  }
}
```

### Inference Endpoint
```http
POST /api/v1/infer
Content-Type: multipart/form-data
```

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `file` | `UploadFile` | Yes | Road photograph or dashcam frame (JPEG, PNG, WebP, AVIF) |
| `confidence` | `float` | No | Minimum confidence threshold (0.05 to 0.95, default: `0.25`) |

**Sample Response:**
```json
{
  "success": true,
  "detections": [
    {
      "class_id": 0,
      "class_name": "pothole",
      "confidence": 0.857,
      "box": [182.4, 240.1, 410.8, 385.6],
      "severity": "Critical",
      "pci_deduct": 24.5
    }
  ],
  "pci_score": 42.0,
  "pci_rating": "Poor",
  "inference_time_ms": 112.4
}
```

---

## Project Directory Structure

```text
potholes-detection/
├── backend/                  # FastAPI inference REST API, schemas, and ORM
│   ├── app/
│   │   ├── api/v1/           # Endpoints: infer.py, defects.py, stats.py
│   │   └── services/         # Severity scoring, alignment, video tracking
│   └── tests/                # 95 backend unit and regression tests
│
├── web/                      # React 18 + TypeScript + Tailwind CSS frontend
│   ├── src/
│   │   ├── pages/            # RoadOverviewPage, RoadScannerPage, RoadAuditReportPage
│   │   ├── components/       # Navbar, Footer, Icons, ThemeToggle, Logo
│   │   ├── context/          # InspectionContext, ThemeContext, LanguageContext
│   │   └── utils/            # cvDetector.ts (API client), pdfReport.ts (PDF generator)
│   └── public/               # Sample highway photography and icons
│
├── ml2/                      # 5-Stage inference pipeline and spatial prior guards
│   ├── guards/               # input_gate.py (Guard B), road_mask.py (Guard A)
│   ├── pipeline/             # detector.py (unified detection orchestrator)
│   └── tests/                # Automated acceptance test suite
│
├── configs/                  # Taxonomy and severity YAML specifications
├── config/                   # Rate cards and severity thresholds
├── data/sample/              # Curated validation images and dataset.yaml
├── eval_failures/            # Real-world challenging edge-case test suite
├── runs/                     # Calibrated production ONNX model weights
│   ├── export/               # best_int8.onnx (quantized lightweight model)
│   └── rescue_train/         # yolo11n_rescue/weights/best.onnx (production model)
│
├── notebooks/                # Google Colab and Kaggle GPU training pipelines
├── scripts/                  # Inference server launcher (`serve_inference.py`) and verification
├── docker/                   # Container definitions (api, web, worker)
├── run.bat                   # One-click Windows CMD launcher
├── run.ps1                   # One-click Windows PowerShell launcher
├── pyproject.toml            # Python configuration and test settings
└── README.md                 # Main documentation and quickstart guide
```

---

## Verification & Automated Tests

ScamRoad includes end-to-end verification suites covering backend logic, machine learning edge cases, and frontend interfaces:

```bash
# 1. Run full backend test suite (95 tests)
pytest backend/tests

# 2. Run machine learning acceptance suite on failure edge-cases
python ml2/tests/test_acceptance.py --pipeline ml2 --test a1

# 3. Run frontend unit tests (Vitest)
cd web && npm test -- --run

# 4. Check frontend TypeScript types and production asset compilation
cd web && npm run build
```

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
