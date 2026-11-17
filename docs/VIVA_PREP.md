# Viva Preparation Guide & 10-Minute Demonstration Script

**Document:** `docs/VIVA_PREP.md`  
**Project:** AI-Powered Road and Infrastructure Damage Detection and Severity Assessment  
**Nickname:** RoadSurvey AI  
**Author:** Priye Ranjan (Lead Student Researcher)  
**Degree:** B.Tech in Computer Science & Engineering  

---

## Part 1: 40 Examiner Questions & Defensible Answers

### Category A: Problem Scope, Motivation & Domain Understanding
1. **Q: What is the exact problem this project solves?**  
   *A:* It provides an automated computer-vision system for surveying road and civic infrastructure that detects damage (potholes, cracks, concrete structural deterioration) from photos or video, and computes a transparent severity score to prioritise maintenance repairs.
2. **Q: Why not rely on municipal citizen complaints instead of automated vision?**  
   *A:* Citizen complaints are reactive, biased toward affluent neighborhoods, lack standardized defect classification, and provide no consistent measurement of geometric severity or cluster progression.
3. **Q: Is this system certified for government compliance or autonomous driving?**  
   *A:* No. This is an academic research project and screening tool. It is not an official government system and is not safety-certified for life-critical or autonomous vehicle control.
4. **Q: Why include civic infrastructure (bridges, retaining walls) alongside roads?**  
   *A:* Bridge decks, culverts, and retaining walls share the same transportation corridor. Concrete deterioration like exposed rebar and spalling poses catastrophic structural risks that must be flagged alongside pavement cavities.
5. **Q: How does this differ from commercial solutions like RoadBotics or Pavemetrics?**  
   *A:* Pavemetrics uses specialized high-cost 3D LiDAR laser profilers ($100k+). Our system uses commodity monocular smartphone/dashcam video with open neural architectures and transparent civil-engineering-aligned scoring.

### Category B: Data, Provenance, & Test Leakage
6. **Q: What datasets did you use, and under what licences?**  
   *A:* RDD2022 (CC BY-SA 4.0, six countries), Deep Pavements (open research), CODEBRIM (academic), and Manot/Taroii benchmark sets. All licences and SHA-256 hashes are logged in `docs/MODELS_AND_DATA.md`.
7. **Q: How did you ensure zero test leakage?**  
   *A:* Splitting was performed strictly by recording sequence and geographic source—never random frame shuffling. We verified zero SHA-256 and perceptual hash (pHash) collisions between train and test sets using `scripts/verify_leakage.py`.
8. **Q: What is the size of your final held-out test set?**  
   *A:* N = 1,728 diverse held-out images, comprising 978 real damage annotations, 743 hard background negatives, and user field cases across 5 geographic regions.
9. **Q: What is the GUARD-SET and why did you build it?**  
   *A:* A locked set of 60 held-out images matching our golden failure cases (wet monsoon roads, Indian clutter, scooters, diagrams). It was hashed before tuning to ensure we never overfitted post-processing filters to our debug cases.
10. **Q: Did you use synthetic data?**  
    *A:* Only for training augmentation (copy-paste pothole crops on asphalt negatives tagged `synthetic=true`). Synthetic data is strictly forbidden in our evaluation test sets.

### Category C: Detection Architectures & Computer Vision Methods
11. **Q: Why use YOLO11n as the primary pothole detector?**  
    *A:* YOLO11n provides an optimal Pareto trade-off between latency (44 ms on CPU) and recall (97.5%), allowing lightweight deployment on edge laptops without requiring discrete server GPUs.
12. **Q: What is Intersection over Union (IoU)?**  
    *A:* IoU is the ratio between the overlapping area of the predicted and ground truth bounding boxes and their total combined area: $\text{IoU} = \frac{\text{Area of Overlap}}{\text{Area of Union}}$.
13. **Q: What is the difference between mAP@50 and mAP@50-95?**  
    *A:* mAP@50 measures mean average precision at an IoU threshold of 0.50. mAP@50-95 calculates the average across 10 IoU thresholds from 0.50 to 0.95 in 0.05 steps, strictly penalizing loose or inaccurate bounding box localization.
14. **Q: Why were there false 'Alligator 99%' detections on signboards and chairs in previous models?**  
    *A:* The secondary crack model was trained exclusively on tight pavement crops with near-zero negative background samples. When exposed to outdoor scenes, high-frequency textures in sky, tree leaves, and commercial chairs triggered high confidence scores.
15. **Q: How did you fix those false detections?**  
    *A:* We introduced a Road-Region Geometric Guard ($y \ge 0.33$) to eliminate upper-scene noise, expanded the COCO obstacle blocker to 11 classes (including chairs and signs), and enforced learned background negative training.
16. **Q: Why did your input gate reject the textbook distress diagram (G5)?**  
    *A:* An infographic structural check detects top title banners ($\bar{Y} < 115, \sigma > 60$), low chroma ($< 16.0$), and dense text glyph contours, cleanly returning HTTP 422 instead of hallucinating damage.
17. **Q: Why not use zero-shot CLIP for diagram rejection?**  
    *A:* In our empirical experiments, CLIP classified road textbook diagrams as real roads (95.7% probability) because the diagrams contained embedded photos of potholes, while falsely rejecting real highway photos as slides.
18. **Q: Why are bounding boxes suboptimal for cracks?**  
    *A:* Cracks are thin, winding fissures. A rectangular bounding box contains >80% intact asphalt pixels. Skeletons and contours measure true length and maximum width with far higher precision.
19. **Q: What is Weighted Boxes Fusion (WBF) and why use it over NMS?**  
    *A:* Non-Maximum Suppression (NMS) discards overlapping lower-confidence boxes. WBF averages the coordinates of all bounding boxes in a cluster weighted by confidence, producing smoother, tighter boundaries on irregular asphalt fissures.
20. **Q: Did you evaluate Test-Time Augmentation (TTA)?**  
    *A:* Yes. Multi-scale horizontal flip TTA improved recall by 1.2% in "Accuracy Mode" but tripled CPU latency, so it is toggled off in real-time video mode.

### Category D: Severity Scoring & Prioritization
21. **Q: How is the Severity Score computed?**  
    *A:* Using physical evidence: $\text{Severity} = \min(100, W_{\text{class}} \times M_{\text{area}} \times M_{\text{position}} + B_{\text{extent}} + F_{\text{risk}})$.
22. **Q: Does detection confidence affect the severity score?**  
    *A:* No. Detection confidence indicates the neural network's certainty that a defect exists, not how deep or dangerous the hazard is.
23. **Q: Can you measure pothole depth or centimetres from a single image?**  
    *A:* No. Monocular RGB cameras cannot determine absolute depth or metric dimensions without physical scale markers or stereoscopic parallax. We report uncalibrated pixel area and relative pavement percentage only.
24. **Q: What are the four severity levels and their thresholds?**  
    *A:* Low ($<30$, Circle `●`), Moderate ($30-54$, Square `■`), High ($55-74$, Triangle `▲`), and Critical ($\ge 75$, Diamond `◆`).
25. **Q: Why are water-filled potholes assigned higher base severity than dry potholes?**  
    *A:* Turbid water conceals crater depth and edge sharpness from drivers, creates severe hydroplaning hazards, and accelerates sub-base stripping under wheel impact.
26. **Q: What is Quadratic Weighted Kappa?**  
    *A:* An agreement statistic for ordinal ratings that penalizes severe disagreements (e.g., Low vs Critical) quadratically ($3^2 = 9$) compared to adjacent disagreements ($1^2 = 1$).
27. **Q: How is repair priority ranked?**  
    *A:* Priority = Severity × Exposure, where exposure is derived strictly from user-entered asset class and traffic rating. If the user provides no context, priority equals severity.
28. **Q: What happens when the same defect appears across multiple dashcam frames?**  
    *A:* Spatial IoU tracking (ByteTrack) tracks the defect across consecutive frames (`min_hits >= 3`), merging repeat detections into a single unique record with 0.00% duplicate inflation.
29. **Q: How does re-inspection verification work?**  
    *A:* When a surveyor uploads a follow-up image of a previously inspected corridor, the system matches defects by position and surface texture, labeling each as "new", "unchanged", "worse", or "repaired".
30. **Q: What if the road is made of cobblestones or gravel?**  
    *A:* Non-asphalt surfaces are a documented operational limitation. Cobblestone mortar joints trigger false crack alarms, and our system transparently displays an operational warning.

### Category E: Software Engineering, Security & Viva Defense
31. **Q: What is the backend and frontend stack?**  
    *A:* FastAPI (Python 3.12) backend with ONNX Runtime inference, React 18 with Vite, TypeScript, and Tailwind CSS.
32. **Q: How do you handle EXIF rotation on smartphones?**  
    *A:* Universal `ImageOps.exif_transpose` is applied during ingestion before neural processing, preventing horizontal box stretching on vertical phone captures.
33. **Q: How is citizen privacy preserved?**  
    *A:* EXIF metadata is stripped by default, and automated Gaussian redaction is executed over civilian faces and vehicle license plates on stored media.
34. **Q: What design tokens did you implement?**  
    *A:* The "Gauge and green" palette (`#F4F6F3` light / `#1F6F54` deep green / `#0D1210` dark) and alternate "Concrete and signal blue", paired with Source Serif 4 and IBM Plex typography, completely avoiding AI template clichés.
35. **Q: Why use Okabe-Ito colors for bounding boxes?**  
    *A:* Okabe-Ito is universally distinguishable by individuals with deuteranopia, protanopia, and tritanopia. Every box also has a 3px halo so it reads clearly over any road pavement texture.
36. **Q: How do you prevent SQL injection and file upload vulnerabilities?**  
    *A:* SQLAlchemy parameterized ORM queries, file magic-byte validation (verifying true image headers, not just extensions), and size limits (max 20 MB).
37. **Q: What was the result of your clean clone build?**  
    *A:* Fresh clone passes all 89 backend tests (100%) and compiles frontend in 6.68s with 0 TypeScript errors and an initial JS bundle of 148 kB gzip.
38. **Q: What are the top 3 limitations of your project?**  
    *A:* 1) Monocular single-camera depth is uncalibrated; 2) Non-asphalt (cobblestone) surfaces produce joint noise; 3) Structural concrete defect detection is a screening aid, not a certified bridge safety certification.
39. **Q: What would you do with a $1,000 GPU budget?**  
    *A:* Train a multi-scale Sliced Aided Hyper Inference (SAHI) ensemble combining D-FINE Large with fine-tuned SegFormer crack segmentation masks across all 6 RDD2022 countries.
40. **Q: What is the single biggest lesson you learned from this capstone?**  
    *A:* Real-world computer vision generalisation is constrained by data diversity and background negatives, not by inventing complex ad-hoc heuristic thresholds.

---

## Part 2: 10-Minute Live Viva Demonstration Script

- **Minute 0:00–1:30 (Title & Problem Statement):**  
  Open `http://localhost:3000`. Introduce title: *"AI-Powered Road and Infrastructure Damage Detection and Severity Assessment"*. Highlight the student research disclaimer and explain why municipal maintenance needs automated severity scoring rather than unweighted detection.
- **Minute 1:30–3:30 (Image Inspection & False Alarm Elimination):**  
  Navigate to **Analyse** (`/scanner`).  
  1. Upload `case_04_bengaluru_potholes.jpg`. Show that potholes on pavement are cleanly boxed and scored, while signboards, trees, and plastic chairs have **zero** false detections.  
  2. Upload `case_02_civil_distress_diagram.jpg`. Demonstrate the structural gate returning HTTP 422: *"This image does not appear to be a camera road photograph"*.  
  3. Upload `case_03_alligator_cracks.jpg`. Show genuine alligator cracking detected with the calibrated 40% slider.
- **Minute 3:30–5:30 (Severity Scoring & Feature Breakdown):**  
  Click on a detected pothole in the list. Point out the transparent breakdown: *"Pothole in wheel path (1.25x), 2.4% pavement area, cluster of 3"*. Explain the 0–100 monotonic formula and the 4 standard severity levels.
- **Minute 5:30–7:00 (Surveys & Repair Prioritization):**  
  Navigate to **Surveys** (`/surveys`). Show the clean empty state when no surveys exist. Click "+ New Survey", create "NH-44 Corridor Survey", and show the ruled survey record.  
  Navigate to **Priority list** (`/priority-list`). Explain the priority formula: $\text{Priority} = \text{Severity} \times \text{Exposure}$. Demonstrate filtering by asset type and exporting the verified maintenance queue to CSV.
- **Minute 7:00–8:30 (Verified Benchmarks & Academic Honesty):**  
  Navigate to **Benchmarks** (`/benchmarks`). Show that all tables and charts render live from `metrics.json`. Highlight the sample size ($N = 1,728$), 95% bootstrap confidence intervals, and the honest disclosure of the non-asphalt cobblestone limitation.
- **Minute 8:30–10:00 (Viva Examiner Q&A & Code Quality):**  
  Switch color palette from "Gauge & Green" to "Concrete & Blue" using the navbar toggle. Show the terminal running 89 passed automated tests and 0 TypeScript build errors. Conclude the demonstration.
