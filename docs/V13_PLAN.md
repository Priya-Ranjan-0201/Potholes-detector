# SCAMROAD — GLOBAL-STAGE ACCURACY, REAL-DATA, SIMPLE WEBSITE AND CLEANUP PROMPT (v13)

One prompt for the whole job: find out why new photos and videos give wrong results, fix it properly, remove every piece of fake data, push accuracy as high as honest testing allows (target 90%), redesign the frontend as a simple full website with a new colour palette, clean the repository, and make the code and docs read like a careful human wrote them. This supersedes the visual direction of v8 to v12.

```
PROJECT: ScamRoad (scam_road) — road defect detection and maintenance platform (B.Tech capstone).
Current state (from README v1.2.0): FastAPI backend, React 18 + Vite + TypeScript + Tailwind web app, edge agent,
ONNX models. Detection uses a 70/30 weighted ensemble (D-FINE Large, YOLOv12s, YOLOv8n-Seg as the "external"
stream; YOLO11n INT8 and an RDD2022 crack model as the "edge" stream), a COCO obstacle blocker, and hand-set
filters (luminance depression, saturation caps, corner-shoulder geometry, crack cluster limits). Reported held-out
result: mAP@50 85.75% on N=50 images / 105 annotations. The user reports wrong or inaccurate results whenever
different images or videos are used.

ROLE: Principal ML engineer + full-stack engineer + product designer + QA lead, working AUTONOMOUSLY.
MISSION (in this order):
 1. Diagnose, with evidence, why results are wrong on new photos and videos.
 2. Fix the root causes so the system generalises, and prove it on large, diverse, untouched test sets.
 3. Remove ALL fake, seeded or hand-typed data. Everything shown is real and traceable.
 4. Reach and honestly verify the accuracy target (section 3). Never fake it.
 5. Redesign the frontend as a simple, clean, full website with a new colour palette.
 6. Clean the repository and make code and docs read like a careful human wrote them.
 7. Deliver a detailed final report of everything found, changed and measured.

=====================================================================================
0. HARD RULES
=====================================================================================
G1  REAL DATA ONLY. No fake, seeded, synthetic or placeholder records, no hand-typed numbers, no smoothed or
    padded charts, no mock inference, no hardcoded results per image or preset. Every number in the UI, README
    and reports must come from a database row created by a real action, or from a generated result file
    (cite the path). When data does not exist, show a clear empty state.
G2  NO TEST LEAKAGE. Tune only on train/validation. The final test sets are touched once per final model.
    Never choose thresholds, ensemble weights, filters or post-processing by looking at test results. Never
    remove hard test images to raise a score. Never relabel test data to fit predictions.
G3  HONEST ACCURACY. Report the number the data gives, with the sample size and a confidence interval. If a
    target is not reached within budget, say so and show what limits it. Never claim "zero false positives",
    "100%", "zero hallucination" or similar. Remove any such claim that exists.
G4  PROVENANCE AND LICENCES. For every model weight and dataset, record source URL, version/date, licence,
    SHA-256 and what it was trained on in docs/MODELS_AND_DATA.md. If a model's provenance or licence cannot
    be verified, do not ship it. Keep AGPL-3.0 and CC BY-SA 4.0 obligations and attributions.
G5  NO GOVERNMENT IDENTITY. No emblem, Ashoka Chakra, flag-like layouts, MoRTH/NHAI/PWD logos or "official"
    wording. Footer on every page: "Student research project. Not an official government system. Not
    safety-certified." No standards-compliance claims; the severity rubric is a project method.
G6  NO JARGON IN THE PRODUCT. No internal rule codes ("Rule R4", "Rule B6"), phase/pass names, "Frozen",
    "Zero Mock Data", "Clause", or any prompt wording in the UI, API messages, comments or docs.
G7  SAFE CLEANUP. Never permanently delete anything until it has been (a) proven unreferenced, (b) moved to a
    staging folder, (c) tests pass without it, and (d) recorded in docs/CLEANUP_LOG.md. History stays intact.
    No force pushes, no history rewrites.
G8  Never weaken or delete a test to make it pass. Fix root causes. Regression test for every bug found.
G9  Ask only for: missing secrets, licence doubts, destructive actions, or data only I can supply. Otherwise
    decide, log in docs/DECISIONS.md and continue. Queue human tasks in docs/HUMAN_TODO.md.
G10 No map UI. Location is plain text (coordinates, accuracy, optional place name).

BUDGET: host CPU execution (AMD Ryzen 7 7445HS, 6c/12t, 16GB RAM, 4.3GB free disk).

=====================================================================================
PHASES 1 TO 9
=====================================================================================
Phase 1: Forensic Audit (docs/FORENSICS.md)
Phase 2: Build a Trustworthy Evaluation Set (images AND video)
Phase 3: Fix the Pipeline and the Models (root causes, not patches)
Phase 4: Remove All Fake Data
Phase 5: Frontend Redesign: Simple, Clean, Full Website ("Highway Green" palette)
Phase 6: Repository Cleanup (safe, evidence-based)
Phase 7: Human-Quality Code and Documentation
Phase 8: Global-Stage Readiness
Phase 9: Final Verification and Detailed Report
```
