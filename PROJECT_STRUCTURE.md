# ScamRoad — Project Structure Guide

Directory layout and component responsibilities across the ScamRoad workspace.

---

## Directory Tree

```text
scam_road/
├── backend/                  # FastAPI backend and SQLAlchemy ORM (port 8001)
│   ├── app/
│   │   ├── api/v1/           # REST endpoints (infer.py, defects.py, maintenance.py, etc.)
│   │   ├── core/             # Config settings, password hashing, JWT helpers
│   │   ├── db/               # SQLAlchemy engine and session management
│   │   ├── models/           # SQLAlchemy ORM database models
│   │   ├── schemas/          # Pydantic request and response schemas
│   │   └── services/         # Severity scoring, alignment, drift, PDF export
│   ├── alembic/              # Database migration scripts
│   └── tests/                # 95 backend unit and integration tests
│
├── web/                      # React 18 + TypeScript + Tailwind frontend (port 3000)
│   ├── src/
│   │   ├── pages/            # RoadOverviewPage (/), RoadScannerPage (/scanner), RoadAuditReportPage (/report)
│   │   ├── motion/           # BoxOverlay, ScanLine
│   │   ├── components/       # Navbar, Footer, ThemeToggle, Icons, Logo
│   │   ├── ui/               # SeverityBadge, design system tokens
│   │   ├── context/          # InspectionContext, LanguageContext, ThemeContext, ToastContext
│   │   └── utils/            # cvDetector.ts (/api/v1/infer client), pdfReport.ts (Vector PDF generator)
│   ├── public/               # Static assets, icons, manifest, and /samples/ test images
│   └── dist/                 # Production build output (`npm run build`)
│
├── ml2/                      # Modern 5-stage inference architecture and guards
│   ├── guards/               # input_gate.py (Guard B), road_mask.py (Guard A), obstacle_filter.py
│   ├── pipeline/             # detector.py (unified detection engine)
│   └── tests/                # Automated acceptance tests (test_acceptance.py)
│
├── ml/                       # Legacy dataset manifests, evaluation scripts, and run metrics
│   ├── guard/                # Road surface prior filters
│   └── runs/                 # Final metric checkpoints and ONNX parity logs
│
├── runs/                     # Calibrated ONNX model weights and evaluation records
│   ├── export/               # best_int8.onnx (quantized lightweight model)
│   └── rescue_train/         # yolo11n_rescue/weights/best.onnx (production ONNX detector)
│
├── configs/                  # YAML path & taxonomy configuration
├── config/                   # Rate card (`rate_card.json`), severity thresholds, and severity.yaml
├── data/sample/              # Curated validation split images and dataset.yaml
├── eval_failures/            # Real-world challenging edge-case test suite
├── notebooks/                # Google Colab and Kaggle GPU training pipelines
├── scripts/                  # Inference server launcher (`serve_inference.py`), evaluation and verification
├── docker/                   # Production Dockerfiles (api, web, worker)
├── run.bat                   # Windows CMD one-click launcher
├── run.ps1                   # Windows PowerShell one-click launcher
├── pyproject.toml            # Python project, pytest, ruff, and tool configuration
└── README.md                 # Main repository showcase and quickstart guide
```

---

## 5-Stage Neural Inspection Pipeline

1. **Ingestion & Orientation**: Decodes image data with automatic EXIF orientation transposition.
2. **Guard B (Input Usability Gate)**: Multi-spectral digital canvas and glyph analyzer that immediately rejects non-road diagrams, schematics, and screenshots with HTTP 422.
3. **Guard A (Road Surface Prior)**: Drivable asphalt segmentation isolating pavement from sky, grass, and roadside structures.
4. **YOLO11n-Rescue Neural Inference**: Single-pass multi-class inference detecting potholes, alligator cracks, longitudinal cracks, and transverse cracks with 0 false alarms on car shadows.
5. **Civil Distress Scoring**: Evaluates distress area, wheel-track placement, and severity according to ASTM D6433 and IRC:82 standards, yielding a calibrated 0–100 Pavement Condition Index (PCI).

---

## Common Commands

| Action | Command | Description |
| :--- | :--- | :--- |
| **Start Full App** | `.\run.bat` or `.\run.ps1` | Launches FastAPI (`:8001`) and Vite frontend (`:3000`) and opens browser |
| **Start Backend Only** | `python scripts/serve_inference.py` | Launches FastAPI backend on port 8001 |
| **Start Frontend Only** | `cd web && npm run dev` | Launches Vite dev server on port 3000 |
| **Run Backend Tests** | `pytest backend/tests` | Runs all 95 backend unit and regression tests |
| **Run Frontend Tests** | `cd web && npm test -- --run` | Runs 10 Vitest specs |
| **Run Acceptance Suite** | `python ml2/tests/test_acceptance.py --pipeline ml2 --test a1` | Evaluates detection accuracy on edge-case benchmarks |
| **Build Frontend** | `cd web && npm run build` | Type-checks with `tsc` and builds Vite production bundle |
