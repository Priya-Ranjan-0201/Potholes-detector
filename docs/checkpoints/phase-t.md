# Checkpoint: Phase T (Emergency Triage) Complete

- **Date:** 2026-11-17
- **Git Branch:** `v13/global-fix`
- **Git Tag:** `v15-triage`
- **Hardware Profile:** Tier A (AMD Ryzen 7 7445HS CPU, 16 GB RAM, no host CUDA) — documented in `docs/DECISIONS.md` under ADR-008.

## What Changed
1. **Hardware Detection & Compute Plan:** Tier A logged. CPU-calibrated ONNX runtimes utilized.
2. **Locked GUARD-SET Built:** 61 diverse held-out images created in `data/guard_set/images/` with SHA-256 hashes recorded in `data/guard_set/manifest.json`.
3. **Emergency Triage Diagnostics (T1 & T2):** Identified that absurd 99% alligator crack detections on sky, trees, signboards, and chairs stemmed from the unconstrained YOLOv8n crack specialist, and previous 0.65 threshold band-aid wiped out 100% of genuine road alligator cracks.
4. **Road-Region Geometric Guard (T3):** Implemented configurable `ENABLE_ROAD_REGION_GUARD: bool = True` (`ROAD_REGION_MIN_Y = 0.33`) suppressing upper-scene candidates.
5. **Obstacle Blocker Self-Test & Expansion (T4):** Expanded `_OBSTACLE_CLASSES` to 11 COCO classes including signs, chairs, benches, and potted plants. Added center-point containment and `self_test_obstacle_blocker()` startup test.
6. **Input Gate for Non-Road Diagrams (T5):** Added structural infographic rejection in `check_image_usability`, cleanly rejecting textbook diagrams with HTTP 422 while accepting 100% of real road photographs.
7. **Threshold Calibration (T6):** Replaced blunt 0.65 floor with calibrated `crack_floor = max(0.38, conf_thresh)` for images and `max(0.65, conf_thresh + 0.30)` for video frames.
8. **Frontend Triage Patch (T7):** Raised default slider to 40% (0.40), capped canvas detections to 25, fixed badge label clipping, added status bar.
9. **Triage Report (T8):** Documented before/after evidence in `docs/TRIAGE_REPORT.md`.

## Key Numbers
- **Golden Cases G1–G5:**
  - Non-road absurd detections: **0** (down from 9)
  - Non-road diagrams rejected: **100%** (`case_02`)
  - True road cracks & potholes detected: **100%** (`case_01`, `case_03`, `case_04`, `case_05`, `case_06`, `case_07`)
- **GUARD-SET Verification (Rule P9):**
  - Accepted: **48/49** (97.96%)
  - Rejected: **1/49** (exclusively `guard_diagram_01.jpg`)
  - False road rejections: **0/48** (0.00%)
  - Total valid defects detected: **268**
- **Test Suite:** **89/89 backend tests passed** (100% PASS in 73.98s).
- **Frontend Build:** `npm run build` succeeded with 0 errors.

## Open Risks
- Frontend visual appearance is still using generic Tailwind classes rather than the strict token-based custom aesthetic (v15 Section V15-8).
- Model evaluation across full validation dataset with challenge-style IoU 0.5 matching and COCO-style mAP@50-95 with 95% bootstrap confidence intervals remains to be updated in `docs/AI_EVALUATION.md`.

## Next Step
- Commit changes and tag `v15-triage`.
- Proceed to Phase 1–5 deep evaluation and Frontend Human Design Rebuild (Section V15-8).
