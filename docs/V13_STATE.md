# ScamRoad V13 Execution State

- **Current Phase:** Phase 1 — Forensic Audit
- **Status:** COMPLETED (Gate Passed)
- **Branch:** `v13/global-fix`
- **Baseline Git Tag:** `before-v13`
- **Completed Tag:** `v13-phase-1-done`
- **Evidence Paths:**
  - `docs/FORENSICS.md`
  - `docs/forensics/`
  - `eval_failures/`
- **Phase 1 Deliverables:**
  - Complete failure case reproductions with intermediate tensors, obstacle masks, model outputs, and visual overlays.
  - Ranked root-cause analysis with concrete code evidence.
  - Pipeline integrity audit (EXIF orientation bug, aspect ratio squashing bug, AVIF decode failure, CPU INT8 vs FP32 latency paradox).
  - Heuristics audit of 8 brittle hand-crafted rules.
  - Audit of hardcoded evaluation metrics and synthetic data generators.
- **Next Action:** Proceed to Phase 2 — Build a Trustworthy Evaluation Set (images and video).
