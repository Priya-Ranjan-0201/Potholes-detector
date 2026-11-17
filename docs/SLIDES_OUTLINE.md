# Capstone Defense Presentation Outline (14 Slides)

**Project:** AI-Powered Road and Infrastructure Damage Detection and Severity Assessment  
**Nickname:** RoadSurvey AI  
**Presenter:** Priye Ranjan (Lead Student Researcher)  
**Degree:** B.Tech in Computer Science & Engineering  

---

### Slide 1: Title & Overview
- **Title:** AI-Powered Road and Infrastructure Damage Detection and Severity Assessment
- **Subtitle:** An Edge-Deployable Vision System for Pavement Distress Scoring and Repair Prioritization
- **Presenter:** Priye Ranjan · Department of Computer Science & Engineering
- **Notice:** Student research project. Not an official government system. Not safety-certified.

### Slide 2: Problem Statement & Motivation
- **The Challenge:** Road degradation causes severe economic losses, vehicle wear, and fatal accidents.
- **Current Limitations:** Manual road surveys are sporadic and hazardous; high-end laser sensor vans ($100k+) cannot cover municipal networks continuously.
- **The Opportunity:** Commodity dashcam and smartphone vision paired with edge neural inference.

### Slide 3: Scope Boundaries (What Stays & What Goes)
- **In Scope (S1–S10):** Real-time defect detection, concrete structural deterioration, transparent 0–100 severity scoring, repair priority ranking, survey records, verified benchmarks, privacy redaction.
- **Eliminated Municipal Jargon:** Citizen complaints, work-order SLAs, contractor rate cards, wards, gamification, and map UIs removed to focus entirely on robust computer vision.

### Slide 4: Forensic Audit of Failure Modes
- **Root Cause 1:** Absurd 99% false alarms on sky, trees, signboards, and chairs (crack model lacked background negatives).
- **Root Cause 2:** Unhandled smartphone EXIF rotation feeding sideways pixels into networks.
- **Root Cause 3:** The "Clean Road" Fallacy: blunt confidence floor (0.65) suppressed 100% of real alligator cracks.
- **Figure:** Before/After failure overlays from `docs/TRIAGE_REPORT.md`.

### Slide 5: System Pipeline Architecture
- **Stage A:** Infographic & Non-Road Input Gate (rejects diagrams with HTTP 422).
- **Stage B:** Drivable Area Road-Region Geometric Prior ($y \ge 0.33$).
- **Stage C:** Calibrated Multi-Model Neural Detector (YOLO11n + YOLOv8n + COCO Obstacle Gate).
- **Stage D:** Transparent Severity Scoring Engine.
- **Stage E:** Repair Prioritization Queue.
- **Figure:** Vector architecture diagram from `docs/PROJECT_REPORT.md`.

### Slide 6: Dataset Provenance & Leakage Protection
- **Held-Out Test Set:** N = 1,728 images across 6 countries (India, USA, Japan, Egypt, etc.).
- **Zero Test Leakage:** Sequence-based splitting; 0 SHA-256 and 0 perceptual hash collisions between train and test.
- **Overfitting Guard (GUARD-SET):** 60 diverse held-out images locked before tuning.
- **Real Negatives:** 743 clean asphalt and traffic clutter images (Rule H1).

### Slide 7: Pavement Distress Detection Results
- **Image-Level Recall:** 97.5% [96.5%, 98.4%] on asphalt pavement.
- **Image-Level F1:** 78.8% [76.8%, 80.9%] across multi-country set.
- **Off-Road False Alarms:** 0.0% on GUARD-SET clutter scenes (Target ≤ 2% MET).
- **Infographic Rejection:** 100.0% on non-road diagrams (Target ≥ 95% MET).
- **Figure:** Precision-Recall curve from `ml/runs/final/metrics.json`.

### Slide 8: Secondary Civic Infrastructure Module
- **Domain:** Bridge decks, retaining walls, culverts, and abutments.
- **Taxonomy:** Concrete cracks, spalling, exposed rebar, corrosion/rust staining, efflorescence.
- **Safety Screening:** High-severity flagging for critical structural hazards (e.g. exposed rebar adds +25 severity points).
- **Caveat:** Screening aid only; does not replace hands-on certified civil engineer inspection.

### Slide 9: Severity Assessment Model
- **Guiding Principle:** Detection confidence is never used as severity; computed strictly from physical evidence.
- **Monotonic Formula:** $\text{Severity} = \min(100, W_{\text{class}} \times M_{\text{area}} \times M_{\text{position}} + B_{\text{extent}} + F_{\text{risk}})$.
- **4 Standard Levels:** Low (`●`), Moderate (`■`), High (`▲`), Critical (`◆`).
- **Explainability:** Human-readable breakdown generated for every detected issue.

### Slide 10: Repair Prioritization & Duplicate Elimination
- **Priority Formulation:** Priority Score = Severity × Exposure (user-entered road class and traffic rating).
- **Temporal Video Tracking:** ByteTrack associative tracking eliminates duplicate defect counts across dashcam video frames (0.00% duplicate rate across 20 test clips).
- **Survey Records:** Ruled surveys with review actions and CSV/GeoJSON exports.

### Slide 11: Human-Centered Design System
- **Philosophy:** "Survey Drawing" aesthetic inspired by cartographic and civic publications.
- **Color Palettes:** "Gauge and green" (#F4F6F3 / #1F6F54) and "Concrete and signal blue".
- **Accessible Overlays:** Okabe-Ito color-blind safe bounding boxes with 3px halo and non-overlapping badges.
- **Zero AI Clichés:** No purple/teal gradients, floating glassmorphism, or marketing hype words.

### Slide 12: Software Engineering & Performance
- **Backend:** FastAPI with typed Pydantic schemas and multi-threaded CPU ONNX Runtime.
- **Frontend:** React 18, Vite, TypeScript, initial JS bundle = 148 kB gzip (budget < 200 kB).
- **Automated Tests:** 89 / 89 backend tests passing (100%), 0 TypeScript compilation errors.
- **Security & Privacy:** Automatic face and license plate Gaussian blurring, EXIF coordinate stripping.

### Slide 13: Honest Limitations & Operating Boundaries
- **Monocular Depth:** Relative area only; true volumetric measurements require stereoscopic cameras.
- **Non-Asphalt Surfaces:** Kauevestena sett stone and cobblestones exhibit mortar joint noise (0% F1 on uncalibrated sett paving).
- **Weather Extremes:** Torrential monsoon rain obscuring road pavement limits optical detection.

### Slide 14: Conclusion & Future Directions
- **Accomplishments:** Delivered a complete, verified, and defensible road and infrastructure damage assessment platform.
- **Key Takeaway:** Model generalisation requires diverse background negatives and geometric priors, not ad-hoc heuristic thresholds.
- **Future Work:** Multi-scale Sliced Aided Hyper Inference (SAHI) and mobile WebGPU on-device browser inference.
