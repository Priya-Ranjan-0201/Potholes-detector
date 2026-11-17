# Architecture Decision Records (ADR)

This document logs non-trivial technology and design decisions made during
the ScamRoad project. Each entry follows the ADR format: context, decision,
consequences.

---

## ADR-001: Use Python 3.12 Instead of 3.11

**Date:** 2026-10-30
**Status:** Accepted
**Phase:** 1

### Context
The original specification suggested Python 3.11 for its stability. However,
Python 3.11 is not installed on the development machine, while Python 3.12
is already present and configured. All key dependencies (FastAPI, Ultralytics,
SQLAlchemy 2, Celery, Pydantic v2) fully support Python 3.12.

### Decision
Use **Python 3.12** as the project runtime.

### Consequences
- **Positive:** Access to Python 3.12 performance improvements (continued
  specialised adaptive interpreter from 3.11, improved error messages,
  `type` statement for type aliases, `@override` decorator in `typing`).
- **Positive:** No need to install and manage a separate Python version.
- **Positive:** Better long-term support timeline (3.12 EOL is later than 3.11).
- **Negative:** Minor risk of encountering bugs in newer stdlib features, but
  this is mitigated by the maturity of 3.12 (released October 2023, now well
  past its stabilisation period).
- **Neutral:** Docker images will use `python:3.12-slim` base.

---

## ADR-002: Use GNU Make on Windows (with PowerShell Fallback)

**Date:** 2026-10-30
**Status:** Accepted
**Phase:** 1

### Context
The project uses a `Makefile` as its task runner (rule R15). The development
machine runs Windows, where GNU Make is not installed by default. Alternatives
considered:
1. Install GNU Make via `choco install make` or `winget`.
2. Use PowerShell scripts (`scripts/*.ps1`) as the primary runner.
3. Use `just` (a modern Make alternative) — requires separate installation.
4. Use `invoke` (Python-based) — adds a Python dependency for task running.

### Decision
Install **GNU Make** via `choco install make` (or `winget install GnuWin32.Make`).
Document a **PowerShell fallback** in `README.md` for each Make target, so the
project remains usable even if Make is not installed.

### Consequences
- **Positive:** `Makefile` is the standard approach, compatible with CI
  (GitHub Actions runners have Make pre-installed).
- **Positive:** Single `Makefile` works on Linux, macOS, and Windows (with Make).
- **Negative:** One-time setup step required on Windows dev machines.
- **Mitigation:** `README.md` includes equivalent PowerShell commands for every
  Make target, so Windows users without Make are not blocked.

---

## ADR-003: Start with RDD2022-India Subset (~2 GB)

**Date:** 2026-10-30
**Status:** Accepted
**Phase:** 1 (affects Phase 2)

### Context
The full RDD2022 dataset (all countries) is approximately 15–20 GB. The
development machine has only **26.6 GB free disk space**, which must also
accommodate Docker images (~3 GB), model checkpoints (~1–2 GB), and general
system overhead.

Available subsets:
- India: ~2 GB (most relevant for deployment context)
- Japan: ~5 GB
- Czech Republic, Norway, USA: varying sizes

### Decision
Download and train on the **RDD2022-India subset only** in Phase 2. Defer
other country subsets to later phases or cloud-based training.

### Consequences
- **Positive:** Fits within disk budget with comfortable headroom (~14 GB remaining
  after raw data, processed data, and model artefacts).
- **Positive:** India subset is the most relevant for the target deployment
  context (Indian roads, lighting conditions, damage patterns).
- **Negative:** Model may not generalise well to roads in other countries.
  This is acceptable for an MVP — cross-country generalisation is a Phase 5+
  concern.
- **Negative:** Smaller training set may limit model accuracy. Mitigated by
  data augmentation and the option to train on Kaggle with larger datasets.
- **Future:** When disk space allows or cloud training is available, add Japan
  and multi-country subsets for improved generalisation.

---

## ADR-004: Laptop as Primary Edge Target (Phone for Mobile Testing)

**Date:** 2026-10-30
**Status:** Accepted
**Phase:** 1 (affects Phases 5, 8)

### Context
The specification envisions edge deployment on various devices (Raspberry Pi,
Jetson Nano, Android phone). The available hardware is:
- **Primary:** Laptop with NVIDIA RTX 3050 (6 GB VRAM), running Windows.
- **Secondary:** OPPO K13 Android phone (available for mobile app testing).
- **Not available:** Raspberry Pi, Jetson Nano, or other dedicated edge devices.

### Decision
Use the **laptop** as the primary edge device for development and testing of the
edge agent. Use the **OPPO K13** for testing the React Native mobile app. Do not
target Raspberry Pi or Jetson Nano in the initial phases.

### Consequences
- **Positive:** Laptop has a capable GPU for both training and inference, enabling
  fast iteration without needing separate edge hardware.
- **Positive:** OPPO K13 provides a real Android device for mobile app testing
  (camera, GPS, push notifications).
- **Negative:** No ARM-based edge device testing. ONNX model compatibility on
  ARM/Jetson is not validated until such hardware is available.
- **Negative:** Laptop is not a realistic "field deployment" device — it requires
  power and is not weather-resistant. This is acceptable for an academic/portfolio
  project.
- **Mitigation:** The edge agent architecture is device-agnostic (Python + ONNX
  Runtime), so porting to Pi/Jetson later requires only environment setup, not
  code changes.
- **Future:** If Jetson Nano or Raspberry Pi becomes available, add it as a
  deployment target and run inference benchmarks.


---

## ADR-005: Licensing Compliance (AGPL-3.0 & CC BY-SA 4.0) and Student Project Scope

**Date:** 2026-11-07  
**Status:** Accepted  
**Phase:** 2 (Rule R7, R8, R9, R11)

### Context
1. Ultralytics YOLO11 is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. Anyone modifying or distributing applications incorporating Ultralytics models over a network must provide source code under AGPL-3.0 unless an enterprise commercial license is obtained.
2. The Road Damage Dataset 2022 (RDD2022) is licensed under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**, mandating that derivatives share adaptations under the same license terms with explicit attribution.
3. Earlier project artifacts contained unverified institutional affiliation claims and compliance badges, which violate ethical research guidelines.

### Decision
1. **License Harmonization (Rule R11):** Explicitly declare that all components utilizing Ultralytics YOLO code and weights inherit AGPL-3.0 compliance terms. The standalone client web UI and schemas remain permissively available, while backend and ML pipelines follow AGPL-3.0 and CC BY-SA 4.0 share-alike provisions.
2. **Student Project Identity (Rule R7):** State explicitly in all user interfaces, headers, footers, and documentation that ScamRoad is a **Student Research Project** and is **NOT** an official government portal, nor is it endorsed or operated by MoRTH, NHAI, or PWD.
3. **Standards Honesty (Rule R8):** Remove all compliance claims. Reference Indian Road Congress specifications strictly as: "Severity rubric inspired by IRC:82-2023 Clause 4.2 and IRC:SP:84-2019".
4. **Configurable Illustrative Rate Card (Rule R9):** Move repair costs from hardcoded static formulas to a structured JSON rate card (`config/rate_card.json`), accompanied by a clear disclosure: "Illustrative estimate, not an official Schedule of Rates".
5. **Hardware Benchmark Honesty (Rule R10):** Disclose that physical on-device benchmarks are currently verified on AMD64 development hardware (`generic_best_bench.json`), while mobile (OPPO K13 Snapdragon NPU) and SBC targets (Raspberry Pi 5, Jetson Orin Nano) are categorized as `UNTESTED (Hardware Benchmark Pending)` until physical runs are executed.

---

## ADR-006: PWA Drive-Mode Capture App Chosen Over Standalone Expo Mobile App

**Date:** 2026-11-07  
**Status:** Accepted  
**Phase:** 5 (Semester Scope & Architecture Consolidation)

### Context
Maintaining two separate frontend codebases (React 18 + TypeScript web app and React Native / Expo mobile app) doubled the maintenance burden, broke CI synchronization across multiple dependency managers, and created feature parity drift. The primary requirement for field demonstrations is an installable, mobile-responsive patrol mode accessible directly on any smartphone with rear camera streaming, offline queueing, and audio alerts.

### Decision
PWA chosen over Expo to halve maintenance burden and guarantee 100% feature parity on a student budget.
1. Implement a dedicated mobile-first Drive Mode at `/capture` inside the React 18 single-page application.
2. Configure standard Progressive Web App capabilities via `web/public/manifest.json` and a lightweight service worker `web/public/sw.js` for offline shell caching.
3. Access camera hardware directly through standard W3C `navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: "environment" } } })`.
4. Provide high-visibility glanceable HUD (speedometer, NavIC/GPS accuracy, distress counter, audio chirp, and IndexedDB outbox queue).
5. Retain `mobile/` as an archived reference prototype.

### Consequences
- **Positive:** Zero dependency fragmentation between Expo and Vite/React.
- **Positive:** Works instantly on Android Chrome and iOS Safari via "Add to Home Screen" without App Store or APK sideloading.
- **Positive:** 100% code sharing for taxonomy, localization, styles, and API clients.
- **Neutral:** Background processing while phone screen is locked requires PWA to remain foregrounded during vehicle patrol.


---

## ADR-007: Global Pipeline Robustness & Real-Data Architecture (v13)

**Date:** 2026-11-16  
**Status:** Accepted  
**Scope:** Production Pipeline, Evaluation, and User Interface

### Context
Previous iterations exhibited performance instability on unseen field media. A forensic audit revealed multiple root causes:
1. EXIF phone rotation metadata was ignored, feeding rotated images into neural networks and misaligning bounding boxes.
2. Hand-crafted heuristics (luminance depression, edge shoulder crops, saturation filters) overfitted to small sample sets and clipped genuine defects on varying road surfaces.
3. Uncalibrated external models (D-FINE Large DETR) were producing skewed probability outputs.
4. Legacy demonstration code relied on `is_demo` database flags and mock seeders.

### Decision
1. **Robust Ingestion Pipeline:** Implemented universal EXIF transpose (`ImageOps.exif_transpose`), RGBA alpha blending over neutral road gray, 16-bit uint16 scaling, and exact letterbox inverse coordinate mapping.
2. **Calibrated Multi-Model Neural Architecture:** Paired high-recall YOLO11n (`runs/export/best.onnx`, conf $\ge 0.20$) with YOLOv8n crack specialist (`ml/runs/pothole_yolov8n/weights/best.onnx`, conf $\ge 0.65$) and a COCO obstacle gate to suppress false alarms on vehicles and pedestrians. Deleted brittle heuristics.
3. **Spatial-Temporal Video Tracking:** Integrated associative IoU tracking across consecutive dashcam frames (`min_hits >= 3`) to suppress duplicate defect entries (0.00% duplicate rate).
4. **Zero Fake Data Architecture:** Dropped `is_demo` columns from all physical database tables, deleted all mock seed scripts, and ensured empty database states return exact zero counts.
5. **Highway Green Redesign:** Redesigned frontend with WCAG AA compliant Highway Green tokens, dynamic benchmark visualizations pulling live from `metrics.json`, and an interactive before/after repair comparison slider.

### Consequences
- **Positive:** Defect recall reached **97.46%** across 1,728 diverse held-out images.
- **Positive:** Video duplicate rate reduced to **0.00%** across 20 dashcam video clips.
- **Positive:** Asphalt pavement F1 reached **96.2% – 99.7%**.
- **Negative:** Non-asphalt surfaces (cobblestone / sett stone mortar joints) remain challenging (0% F1 on Kauevestena patches), transparently documented in evaluation reports.

---

---

## ADR-009: Repository Refocus to AI-Powered Road and Infrastructure Damage Detection and Severity Assessment

**Date:** 2026-11-17  
**Status:** Accepted  
**Scope:** Architecture, Product Scope, Model Pipeline, and Visual Identity

### Context
The user issued the comprehensive refocus directive:
- **Title:** "AI-Powered Road and Infrastructure Damage Detection and Severity Assessment"
- **Nickname:** `RoadSurvey AI` (short: `RoadSurvey`)
- **Definition:** A computer-vision system for surveying road and civic infrastructure that detects damage such as potholes, cracks, and structural deterioration from images or video, and assigns a severity score to each detected issue to help prioritise repair and maintenance work.

Prior code retained legacy municipal features (citizen complaints, work-order SLAs, cost estimations, ward assignments, gamification) that dilute the technical focus of the computer vision capstone.

### Decision
1. **Scope Boundary (S1–S10):** Restrict system solely to:
   - S1: Image, video, and live camera input
   - S2: Road damage detection (potholes, water-filled potholes, longitudinal, transverse, alligator cracks)
   - S3: Civic infrastructure structural deterioration (concrete cracks, spalling, exposed rebar, corrosion, efflorescence)
   - S4: 0–100 Severity Score with 4 levels (Low, Moderate, High, Critical) and transparent feature breakdown
   - S5: Survey summary and Repair Priority ranking
   - S6: Survey records with review, before/after re-inspection, and CSV/GeoJSON/PDF exports
   - S7: Benchmarks & Method documentation from verified metric files
   - S8: Lightweight auth (inspector / viewer)
   - S9: Privacy preservation (EXIF stripping, face/plate redaction)
   - S10: English and Hindi localisation
2. **Purge Out-of-Scope Modules:** Deprecate and stage for cleanup: citizen complaints, work orders, SLAs, contractor rate cards, wards, gamification, and map UI.
3. **Design Identity:** Implement the "Gauge and green" palette (#F4F6F3 light / #1F6F54 green / #0D1210 dark) and alternate "Concrete and signal blue", paired with Source Serif 4 + IBM Plex typography.
4. **Severity Formulation:** Use monotonic formula: `Severity = min(100, BaseWeight × AreaFactor × PositionFactor × ExtentFactor + StructuralRiskFlags)`.

### Consequences
- **Positive:** Laser-focused, highly defensible engineering capstone for academic defense and real-world civic inspection.
- **Positive:** Zero distraction from unverified municipal management simulations.
- **Negative:** Requires thorough removal and migration of legacy database tables and routes.

---

## ADR-010: Accuracy Rescue — Single Unified Detector and Guarded Road Prior Architecture

**Date:** 2026-11-17  
**Status:** Accepted  
**Scope:** Machine Learning, Computer Vision Pipeline, Forensics, and Guard Evaluation

### Context
On diverse user images and dashcam footage, ~80% of detections were spurious (severe false alarms such as "Alligator 97–99%" on sky, storefront signboards, chairs, people, and educational diagrams). Forensic inspection revealed:
1. `runs/baselines/yolov8n` (used as the secondary crack model) was trained on tight crops with zero background negative images, causing the BCE sigmoid head to output 0.95–1.000 confidence on any high-frequency outdoor texture (13,487 false alarms on clean benchmark roads).
2. The primary YOLO11n (`runs/export/best.onnx`) was trained on `pothole_unified`, which had 0 alligator cracks and 0 transverse cracks, forcing previous developers into an unstable two-model blend.
3. Earlier heuristic suppression filters wiped out 100% of real alligator cracks, causing the pipeline to falsely report "clean road" on actual damaged pavement.

### Decision
1. **Eliminate Multi-Model Ensemble:** Completely remove the secondary YOLOv8n crack model, consensus multipliers, and 70/30 blending.
2. **Train Unified Modern Detector:** Fine-tuned a single YOLO11n detector (`runs/rescue_train/yolo11n_rescue/weights/best.onnx`) with 31.7% background negative images (clean pavement, asphalt shadows, clutter, traffic) strictly outside the locked benchmark to ensure zero test leakage.
3. **Guard A (Road Surface Prior):** Implemented drivable road surface segmentation (`compute_road_surface_mask`) with 15% dilation. Any defect candidate whose center is not within the road pavement plane is discarded, eliminating sky and signboard false alarms while preserving 92.4% of real road damage.
4. **Guard B (Input Gate):** Implemented `is_road_image` to reject digital diagrams, textbooks, charts, and application UI screenshots before inference, achieving 100% non-road rejection (30/30).
5. **Operating Presets:** Calibrated 3 distinct operational modes:
   - High Precision (`conf >= 0.40`, P50 200ms, 11% clutter false alarm rate) for automated maintenance dispatch.
   - Balanced (`conf >= 0.25`, P50 202ms) for general condition surveys.
   - High Recall (`conf >= 0.15`, P50 203ms) for safety audits.

### Consequences
- **Positive:** Zero non-road errors (0.0% on diagrams and screenshots).
- **Positive:** Clean road false alarm rate dropped by over 66 percentage points (from 93.0% down to 26.6%).
- **Positive:** Latency decreased from 555ms down to 200ms P50 (2.7x faster) with a clean single ONNX tensor.
- **Positive:** Complete elimination of the "Alligator 99% on sky and signboards" bug backed by verified regression tests.

---

## ADR-011: ML2 Harmonized Multi-Expert Road Damage Architecture and App Integration

**Date:** 2026-11-17  
**Status:** Accepted  
**Scope:** Machine Learning Architecture, Backend API Integration, and Acceptance Verification

### Context
While ADR-010 established the training protocol with background negative images and baseline guards, empirical evaluation of diverse real-world test cases identified two distinct edge-case failure modes:
1. Low-contrast alligator cracks on weathered dry pavement require high sensitivity to avoid false negatives.
2. Wet pavement with specular reflections (e.g. monsoon dashcam footage) can trigger false positives if high-sensitivity crack models are unconstrained.
3. The application backend API (`backend/app/api/v1/infer.py`) previously retained legacy 70/30 blending logic and arbitrary heuristic thresholds (`crack_floor = max(0.65, conf_thresh + 0.30)`).

### Decision
1. **Harmonized ML2 Pipeline (`ml2/pipeline/detector.py`):**
   - Stage 1: Primary balanced detector (`ml2/models/yolo11_road_damage.onnx`) trained with 26.8% background negative regularization.
   - Stage 2: Specular-gated physical conditioning (`specular_ratio < 0.10` and `laplacian_var > 600`) enabling high-sensitivity crack and depression heads exclusively on dry pavement while preventing rain-glare false positives.
   - Stage 3: Drivable road surface mask prior with 0.385h horizon cutoff to eliminate sky and upper-scene hallucinations.
   - Stage 4: COCO obstacle filter with automated startup self-test.
   - Stage 5: Input gate rejecting non-road civil diagrams, textbooks, and UI screenshots.
2. **Full Application Wiring:**
   - Rewired `backend/app/api/v1/infer.py` to use `ML2DetectorPipeline` for single images, batch processing, and multi-frame video tracking with duplicate suppression.
   - Replaced legacy heuristic floors with transparent 0–100 severity scoring (Low, Moderate, High, Critical) per `SEVERITY_SPEC.md`.

### Consequences & Verified Metrics
- **A1 User Eval Failures Test:** 7/7 PASSED (100%).
- **A2 Locked Benchmark ($N=730$):**
  - Clutter Off-Road False Alarm Rate: **1.00% (1/100)** — PASSED (Target $\le 2.0\%$).
  - Non-Road Rejection Rate: **100.00% (30/30)** — PASSED (Target $\ge 95.0\%$).
  - Image-Level Damage Yes/No Accuracy: **61.23%** (95% CI: [57.4%, 64.5%]).
  - Object-Level $F_1$ @ IoU 0.5: **0.0693** (Honest reporting under 5-epoch CPU training vs multi-GPU benchmarks).
- **Backend Test Suite:** 14/14 automated regression and pipeline integrity tests PASSED.




