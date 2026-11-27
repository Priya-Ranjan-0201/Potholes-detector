# About the Build & AI Assistance Disclosure

This document provides full institutional transparency regarding the engineering methodologies, software frameworks, and AI tools utilized in building the ScamRoad National Pilot project.

---

## 1. Project Overview

- **Project Name:** ScamRoad (Autonomous Pavement Distress Detection & Review Engine)
- **Role:** Lead Student Researcher & Computer Vision Engineer
- **Academic Context:** Capstone Engineering Project & National Pilot Research Proposal
- **Repository:** `https://github.com/Priya-Ranjan-0201/potholes-detection`

---

## 2. AI Tools & Developer Frameworks Utilized

In accordance with academic disclosure standards, the following tools were employed during development:

| Tool / Model | Provider | Function & Contribution |
| :--- | :--- | :--- |
| **Antigravity AI Agent** | Google DeepMind (Gemini 2.5) | Architecture scaffolding, test suite creation, forensic diagnosis of golden failure cases, refactoring, and documentation drafting. |
| **Ultralytics YOLO11** | Ultralytics (AGPL-3.0) | Neural object detection backbone architecture fine-tuned on multi-country road damage data. |
| **MobileNetV3-Small** | PyTorch / TorchVision (BSD-3-Clause) | Lightweight neural image classifier fine-tuned as Stage 1 input gate. |
| **ONNX Runtime** | Microsoft (MIT) | Cross-platform accelerated inference engine for CPU host and edge execution. |
| **OpenCV & NumPy** | Open Source (Apache 2.0 / BSD) | Image preprocessing, letterbox resizing, Sobel edge gradient computation, and morphological operations. |
| **SciPy** | Open Source (BSD) | Hungarian bipartite matching algorithm for spatial ground-truth association. |
| **FastAPI & Uvicorn** | Open Source (MIT) | High-performance asynchronous Python REST API server. |
| **React 18 & Vite 5** | Meta / Evan You (MIT) | Modern frontend client SPA with typed component architecture. |
| **TailwindCSS 3** | Tailwind Labs (MIT) | Utility-first CSS framework implementing "Paper and Asphalt" design tokens. |

---

## 3. Human Engineering Principles & Empirical Verification

1. **Zero Hallucinated Numbers (Rule R1):** All metrics reported across `README.md`, `docs/`, and web benchmarks originate from physical executions on held-out disk datasets (`scripts/evaluate_gate_c.py`, `scripts/evaluate_model_pipeline.py`).
2. **Zero Test Leakage (Rule R2):** Sequence-aware grouping ensures training and evaluation sets have zero overlapping drives or cryptographic SHA-256 hash collisions.
3. **Root-Cause Fixes (Rule R5):** Every bug encountered across Gates A through G was addressed via underlying algorithmic and data curation changes rather than weakening test thresholds.
4. **Mandatory Disclaimers (Rule R3):** Every report, interface, and API payload enforces the exact disclaimer: *"Student research project. Not an official government system. Not safety-certified."*

---

*Student research project. Not an official government system. Not safety-certified.*
