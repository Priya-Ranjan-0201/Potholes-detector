# Repository Cleanup & Gate H National Readiness Log

This document records the cleanup of legacy, unreferenced, demo, and duplicate artifacts in ScamRoad, in compliance with **Rule R1 (Real Data Only)** and **Gate H (National-Readiness Docs and Cleanup)**.

---

## 1. Safe Cleanup Protocol Verification

1. **Identification & Documentation:** Candidate files were audited to ensure zero active production code or test references.
2. **Demo & Synthetic Seeders Purged:**
   - Removed legacy `"seed:demo"` command from `web/package.json`.
   - Removed `.PHONY: demo` target and synthetic seeder execution from `Makefile`.
   - Verified zero seeded PRNG or mock generator files exist in active runtime directories.
3. **Verification Suite Execution:**
   - **Frontend Production Build:** Built with `tsc && vite build`. Completed in 4.77s with 0 errors.
   - **Web Automated Tests:** `npm test` across all 5 test suites (14/14 tests passed).
   - **Pytest Automated Tests:** 29/29 tests passed across Gates A through G.
   - **Golden Cases Verification:** All 9 failure cases in `eval_failures/` verified against `expected.json`.

---

## 2. Cleaned Artifacts & Streamlined Components

| File / Component | Type | Action Taken | Reason |
| :--- | :---: | :---: | :--- |
| `web/package.json` (`seed:demo`) | Config Line | Purged | Rule R1: No fake, seeded or hand-typed numbers permitted in repository. |
| `Makefile` (`demo` target) | Build Target | Purged | Legacy target referenced non-existent demo seeder; replaced with strict `make reproduce`. |
| `README.md` (Legacy 403 lines) | Documentation | Rewritten to 161 lines | Converted to plain-voice, measured metrics with 95% CIs, and enforced Rule R3 disclaimers. |
| `web/src/__tests__/gate_g_frontend.test.tsx` | Test | Streamlined | Removed node `fs`/`path` runtime dependencies in favor of Vite client asset typing. |
| `Makefile` (`reproduce` target) | Build Target | Upgraded | Configured to run `scripts/gate_a_verify_golden.py` and all 29 automated gate regression tests. |

---

## 3. Retained Core Assets & Provenance

The following production model weights and test suites are strictly preserved:

1. **Production Road Scene Classifier (Gate B):**
   - Path: `ml2/models/road_classifier.onnx`
   - Architecture: MobileNetV3-Small (TorchVision fine-tuned, ONNX opset 14)
   - Size: 5.81 MB
   - Role: Stage 1 non-road scene rejector (threshold: 0.12).
2. **Production General Defect Detector (Gate B/C):**
   - Path: `ml2/models/yolo11_road_damage.onnx` / `runs/export/best.onnx`
   - Architecture: YOLO11n (ONNX FP32)
   - Size: 10.17 MB
   - Role: Stage 3 general road damage detection.
3. **Puddle Crop Classifier (Gate D):**
   - Path: `ml2/guards/puddle_classifier.py`
   - Role: Stage 5 rim gradient and cavity shadow classifier.
4. **ByteTrack Video Tracker (Gate C):**
   - Path: `ml2/tracker/tracker.py`
   - Role: Stage 6 single-event temporal consolidation.

---

*Student research project. Not an official government system. Not safety-certified.*
