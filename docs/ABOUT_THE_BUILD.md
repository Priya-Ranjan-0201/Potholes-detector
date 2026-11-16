# Academic Disclosure: About the Build & AI Assistance

This document fulfills institutional academic transparency requirements regarding the use of AI tools in the development of the ScamRoad B.Tech capstone project.

---

## 1. Project Background

- **Project Title:** ScamRoad — Road Defect Detection and Municipal Maintenance Platform
- **Degree Program:** Bachelor of Technology (B.Tech) in Computer Science & Engineering
- **Project Role:** Lead Student Researcher & Software Engineer

---

## 2. AI Assistance Disclosure

In compliance with academic integrity guidelines, the following AI tools and environments were utilized during project engineering:

| AI System / Environment | Provider / Model | Scope of Assistance |
| :--- | :--- | :--- |
| **Antigravity Agent Manager** | Google DeepMind / Gemini | Code refactoring, test script authoring, forensic error classification, and documentation scaffolding. |
| **Ultralytics YOLO** | Ultralytics / AGPL-3.0 | Pretrained computer vision neural network backbones (YOLO11n and YOLOv8n) fine-tuned on road damage datasets. |

---

## 3. Human Oversight & Empirical Verification

To ensure research validity and ethical standards:
1. **Zero Hallucinated Metrics:** Every numerical metric reported in `README.md`, `docs/AI_EVALUATION.md`, and the web user interface was generated through physical execution on disk (`python scripts/evaluate_model_pipeline.py`) across 1,728 held-out images and 20 dashcam videos.
2. **Empirical Forensic Diagnosis:** All 12 evaluation failure cases were reproduced and traced through the production ONNX pipeline to diagnose orientation, format, and threshold root causes.
3. **No Synthetic or Seeded Records:** All demonstration mock data, hardcoded presets, and synthetic database seeders were purged from the production codebase.
4. **Independent Execution:** The entire system builds from scratch (`pip install -r requirements.txt`, `npm run build`, `pytest`), runs unit tests, and serves predictions on standard consumer CPU hardware.
