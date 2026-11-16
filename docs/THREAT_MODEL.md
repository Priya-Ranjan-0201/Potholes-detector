# Security & Privacy Threat Model

This document outlines the security and privacy threat model for ScamRoad. In adherence to project guidelines, **only mitigations that are actively implemented and tested in the codebase** are listed below.

---

## 1. System Asset Classification

1. **Road Imagery & Video Frames:** Photos and dashcam recordings uploaded by citizens or patrol cameras.
2. **Geospatial & Telemetry Records:** GPS latitude/longitude, heading, altitude, and timestamp records.
3. **Citizen Identifiers:** Account emails, hashed credentials, and complaint contact info.
4. **Municipal Work Orders:** Repair assignments, contractor logs, and engineer sign-off audit trails.

---

## 2. Threat Scenarios & Implemented Mitigations

### 2.1 PII Exposure (Pedestrian Faces & Vehicle License Plates)
- **Threat:** Public road photography inadvertently captures bystander faces or vehicle registration plates, violating privacy regulations.
- **Implemented Mitigation:** On-device edge privacy blurring (`edge/agent/blur_privacy.py`) detects and blurs face and license plate regions *before* local disk write or cloud sync.
- **Tested Verification:** Evaluated on N=100 targets (50 faces, 50 plates) in `bench/privacy_blur_report.json` achieving 100% recall on face and plate redaction. Automated unit test: `edge/tests/test_blur_privacy.py`.

### 2.2 Malicious & Corrupted Media Ingestion
- **Threat:** Adversary submits non-image payloads, zip bombs, oversized files, or corrupted byte streams to crash the inference service or exhaust disk space.
- **Implemented Mitigation:** Strict upload validation in `backend/app/api/v1/infer.py`:
  - Enforces 25 MB file size ceiling.
  - Inspects file headers and magic bytes via PIL.
  - Runs `check_image_usability` to reject severely underexposed (<15 lum), overexposed (>240 lum), or unreadable payloads with HTTP 422.
- **Tested Verification:** Verified in `backend/tests/test_pipeline_integrity.py` covering extreme aspect ratios (16000x200), corrupt inputs, and unusable lighting.

### 2.3 Replay Attacks & Duplicate Sighting Floods
- **Threat:** Unstable network causes repeated batch uploads from edge devices, leading to duplicate database records and inflated road damage statistics.
- **Implemented Mitigation:**
  - `idempotency_key` deduplication in `backend/app/api/v1/sync.py`: replaying an identical batch returns the cached receipt without duplicating records.
  - Spatial-temporal associative tracking in `backend/app/services/video_tracker.py`: enforces `min_hits >= 3` and merges overlapping tracks, achieving a verified **0.00% duplicate rate**.
- **Tested Verification:** Verified in `backend/tests/test_sync_ingestion.py` and `backend/tests/test_pipeline_integrity.py::test_api_infer_video_duplicate_suppression`.

### 2.4 Unauthorized Privilege Escalation in Maintenance Sign-Off
- **Threat:** A contractor or unauthorized user attempts to mark their own work orders as "VERIFIED" to approve payment without physical inspection.
- **Implemented Mitigation:**
  - RBAC security matrix enforced via FastAPI dependency injection (`backend/app/api/deps.py`).
  - Direct status jumps to "VERIFIED" via `PATCH /api/v1/work-orders/{id}` are explicitly blocked.
  - Authoritative verification requires human engineer or admin role via `POST /api/v1/work-orders/{id}/verify`.
- **Tested Verification:** Automated integration test in `backend/tests/test_security_matrix.py` and `backend/tests/test_maintenance.py`.

### 2.5 Credential & Session Security
- **Threat:** Stolen tokens or compromised passwords leading to administrative account hijacking.
- **Implemented Mitigation:**
  - Passwords hashed using Argon2id (`backend/app/core/security.py`).
  - JWT authentication with signed HMAC-SHA256 tokens and refresh token rotation (`backend/app/api/v1/auth.py`).
  - Constant-time secret comparison preventing timing attacks.
- **Tested Verification:** Automated tests in `backend/tests/test_auth.py`.

---

## 3. Privacy Controls & Data Rights

1. **Explicit Location & Upload Notice:** Clear disclosure displayed on scanner and report pages explaining data usage.
2. **Right to Erasure ("Delete My Data"):** Citizen users can delete their reports and uploaded media via `DELETE /api/v1/reports/{id}`.
3. **EXIF Coordinate Stripping:** Edge capture allows stripping raw GPS EXIF headers prior to public display, storing coordinates solely as normalized system data points.
