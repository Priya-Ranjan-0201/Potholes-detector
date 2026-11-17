# Scope Audit: Refocusing on Road & Infrastructure Damage Detection and Severity Assessment

**Document:** `docs/SCOPE_AUDIT.md`  
**Date:** 2026-11-17  
**Mission:** Refocus repository strictly on **"AI-Powered Road and Infrastructure Damage Detection and Severity Assessment"** (Scope S1–S10).  
**Protocol:** Every artifact is classified as **IN**, **OUT**, or **UNSURE** with technical justification.

---

## 1. Scope Boundary Definition (S1–S10 vs Out-of-Scope)

### In-Scope (Retained & Hardened):
- **S1:** Upload/capture images and video (live camera in browser).
- **S2:** Road damage detection: potholes (including water-filled when broken edges present), longitudinal cracks, transverse cracks, alligator cracks.
- **S3:** Civic infrastructure structural deterioration (bridges, retaining walls, culverts, footpaths, concrete): concrete cracks, spalling, exposed rebar, corrosion/rust, efflorescence. (Secondary module with separate metrics).
- **S4:** Per-detection Severity Score (0–100) with level (Low / Moderate / High / Critical) and transparent feature explanation.
- **S5:** Survey summary and Repair Priority ranking.
- **S6:** Survey records (asset type, date, inspector, coordinates, review status, before/after re-inspection photo comparison, CSV/GeoJSON/PDF export).
- **S7:** Benchmarks and Method pages generated directly from verifiable metric files.
- **S8:** Basic authentication (inspector, viewer).
- **S9:** Privacy protections (EXIF stripping, face/license plate redaction).
- **S10:** Localisation: English and Hindi.

### Out-of-Scope (Staged for Removal per Section 14):
- Citizen complaint/reporting portal.
- Work-order lifecycle with SLAs, contractor rate cards, wards, and cost estimations.
- Gamification, leaderboards, marketplaces, chat bots, and unrelated notification banners.
- "Command center" style municipal dashboards.
- Any Map UI, heat-map, or GIS tile viewer (Rule H10: location is plain-text coordinates only).
- Non-road AI features, demo tours, and seed scripts.

---

## 2. API Routes Audit (`backend/app/api/v1/`)

| Route File | Prefix / Endpoints | Classification | Justification |
| :--- | :--- | :---: | :--- |
| `infer.py` | `POST /infer`, `POST /infer/image`, `POST /infer/video` | **IN** | Primary defect detection & severity engine (S1, S2, S3, S4). |
| `benchmarks.py` | `GET /benchmarks`, `GET /benchmarks/metrics` | **IN** | Real benchmark file ingestion (S7). |
| `auth.py` | `POST /auth/login`, `POST /auth/register`, `GET /auth/me` | **IN** | Basic role-based access for inspector & viewer (S8). |
| `media.py` | `POST /media/upload`, `GET /media/{id}` | **IN** | Secure image/video storage & face/plate redaction (S1, S9). |
| `defects.py` | `GET /defects`, `PATCH /defects/{id}` | **IN** | Defect inspection and lightweight repair status review (S4, S5). |
| `verification.py`| `POST /verification/compare` | **IN** | Before/after re-inspection comparison (S6). |
| `drift.py` | `GET /drift/metrics` | **IN** | Continuous model drift & confidence monitoring (Phase 10). |
| `surveys.py` | `GET /surveys`, `POST /surveys`, `GET /surveys/{id}/export` | **IN (NEW)** | Replaces municipal dashboard with structured survey records (S6). |
| `priority.py` | `GET /priority/list` | **IN (NEW)** | Repair priority ranking: severity × exposure (S5). |
| `complaints.py` | `/complaints/*` | **OUT** | Citizen complaint portal explicitly removed. |
| `maintenance.py` | `/maintenance/*` | **OUT** | Work-order SLAs, contractor rate cards removed. Replaced by defect repair status. |
| `map.py` | `/map/*` | **OUT** | Map UI banned by Rule H10; location is plain text only. |
| `forecasts.py` | `/forecasts/*` | **OUT** | Weather and multi-year municipal degradation simulation out of scope. |
| `notifications.py`| `/notifications/*` | **OUT** | Municipal blast notifications out of scope. |
| `reports.py` | `/reports/*` | **OUT** | Legacy citizen report state machine removed. |
| `stats.py` | `/stats/*` | **OUT** | Ward and corridor statistics removed. |
| `sync.py` | `/sync/*` | **UNSURE** | Offline sync queue for field inspections; staged until S1 review. |

---

## 3. Database Models Audit (`backend/app/models/`)

| Model File | Tables Defined | Classification | Action |
| :--- | :--- | :---: | :--- |
| `defect.py` | `Defect`, `Observation` | **IN** | Retain; add `severity_score`, `severity_breakdown`, `repair_status`. |
| `auth.py` | `User`, `ApiKey` | **IN** | Retain for inspector/viewer authentication. |
| `base.py` | `Base`, `TimestampMixin` | **IN** | Retain shared schema foundations. |
| `ml.py` | `ModelRegistry`, `InferenceLog` | **IN** | Retain for model versioning and audit telemetry. |
| `survey.py` | `Survey`, `SurveyMedia` | **IN (NEW)** | Create for S6 survey grouping (asset type, inspector, coordinates). |
| `complaint.py` | `CitizenComplaint` | **OUT** | Move to `_staging_trash/`; drop table. |
| `maintenance.py`| `WorkOrder`, `Contractor`, `RateCard` | **OUT** | Move to `_staging_trash/`; drop table. |
| `geo.py` | `Ward`, `Corridor` | **OUT** | Move to `_staging_trash/`; drop table. |
| `analytics.py` | `MunicipalTrend`, `SlaMetric` | **OUT** | Move to `_staging_trash/`; drop table. |
| `device.py` | `EdgeDevice` | **UNSURE** | Kept only if used for on-device browser/edge token registration. |

---

## 4. Frontend Pages & Components (`web/src/pages/`)

| Page File | Route | Classification | Action |
| :--- | :--- | :---: | :--- |
| `LandingPage.tsx` | `/` | **IN** | Redesign as editorial "survey drawing" Home with before/after divider. |
| `ScannerPage.tsx` | `/analyse` (`/scanner`) | **IN** | Primary inspection UI with Road vs Structure tabs, presets, and Okabe-Ito overlays. |
| `SurveysPage.tsx` | `/surveys` | **IN (NEW)** | Ruled table of road & bridge surveys with review actions and PDF/CSV export. |
| `PriorityListPage.tsx` | `/priority-list` | **IN (NEW)** | Repair priority ranking table (severity × exposure) with plain-text location. |
| `ModelBenchmarksPage.tsx`| `/benchmarks` | **IN** | Research-grade benchmark publication pulling from verified `metrics.json`. |
| `AboutPage.tsx` | `/method` (`/about`) | **IN** | Methodology, architecture diagram, verified citations, and disclaimers. |
| `LoginPage.tsx` | `/login` | **IN** | Simplified inspector sign-in. |
| `NotFoundPage.tsx` | `*` | **IN** | Clean plain 404 page. |
| `DashboardPage.tsx` | `/dashboard` | **OUT** | Replaced by `SurveysPage.tsx` and `PriorityListPage.tsx`. |
| `MaintenancePage.tsx` | `/maintenance` | **OUT** | Kanban work-order board removed. |

---

## 5. Scripts & Tooling Audit (`scripts/`)

| Script | Purpose | Classification | Action |
| :--- | :--- | :---: | :--- |
| `serve_inference.py` | Production FastAPI server | **IN** | Retain as primary backend launcher. |
| `evaluate_model_pipeline.py`| Real-data evaluation runner | **IN** | Retain; outputs verified `metrics.json`. |
| `build_guard_set.py` | Builds locked 60+ image GUARD-SET | **IN** | Retain for overfitting validation (Rule H2). |
| `verify_leakage.py` | SHA-256 and pHash test leakage check | **IN** | Retain in CI test suite. |
| `check_claims.py` | Audits documentation claims against metrics | **IN** | Retain in CI test suite. |
| `check_ui_copy.py` | Enforces ban on hype words and internal jargon | **IN** | Retain in CI test suite. |
| `check_i18n_keys.py` | Verifies parity between English and Hindi keys | **IN** | Retain for S10 compliance. |
| `run_onnx_parity.py` | Measures PyTorch vs ONNX vs INT8 parity | **IN** | Retain for inference engineering verification. |
| `rater_study_kit.py` | Tool for rating severity and computing kappa | **IN** | Retain for Phase 5 severity validation. |
| `test_live_api.py` | Live API integration smoke test | **IN** | Retain for CI regression testing. |
| `ingest_real_rdd_data.py` | Legacy seeder with wards/corridors | **OUT** | Remove fake seeder logic; retain raw dataset unpacker. |
| `run_hard_negative_ablation.py`| Hard negative ablation | **UNSURE** | Clean up any synthetic polygon shapes before reuse. |

---

## 6. Execution Plan for Scope Refactor
1. Create new survey and repair-priority endpoints and database schemas.
2. Stage out-of-scope files (`complaints`, `maintenance`, `map`, `geo`, `analytics`) into `_staging_trash/`.
3. Verify test suite passes without staged files.
4. Update frontend routing and navigation to match the 6 core pages:
   `Home` | `Analyse` | `Surveys` | `Priority list` | `Benchmarks` | `Method`
