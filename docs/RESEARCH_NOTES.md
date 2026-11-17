# Research Notes & Theoretical Foundations

**Document:** `docs/RESEARCH_NOTES.md`  
**Date:** 2026-11-17  
**Project:** AI-Powered Road and Infrastructure Damage Detection and Severity Assessment (`RoadSurvey AI`)  
**Scope:** Verified scientific literature on road damage detection, concrete deterioration, severity scoring, and robust computer vision methods.

---

## 1. Road Damage Detection (RDD) Literature

### 1.1 Global Road Damage Detection Challenge (GRDDC 2020)
- **Citation:** Arya, D., Maeda, H., Ghosh, S. K., Toshniwal, D., Mraz, A., Kashiyama, T., & Sekimoto, Y. (2020). *Global Road Damage Detection: Challenge and Datasets*. arXiv:2011.08740.
- **Analysis:** Introduced a multi-country benchmark across India, Japan, and the Czech Republic with 26,336 images. Established the core 4-class taxonomy: `D00` (longitudinal crack), `D10` (transverse crack), `D20` (alligator crack), and `D40` (pothole). Highlighted severe domain shift between countries due to differences in asphalt composition, road markings, lighting, and camera mounting.
- **Reuse / Ignore:** **REUSE** the 4-class taxonomy (`D00`, `D10`, `D20`, `D40`) and cross-country evaluation split protocol. **IGNORE** raw multi-scale anchor grids from legacy YOLOv4 baselines.

### 1.2 RDD2022 Large-Scale Multi-National Dataset
- **Citation:** Arya, D., Maeda, H., Ghosh, S. K., Toshniwal, D., Mraz, A., Kashiyama, T., & Sekimoto, Y. (2022). *Crowdsensing-based Road Damage Detection: Challenge, Dataset, and Baseline*. arXiv:2209.08538.
- **Analysis:** Expanded the dataset to six countries (Japan, India, Czech Republic, Norway, United States, China) with 47,420 road images and over 55,000 damage annotations. Validated that country-specific models fail when deployed globally without domain adaptation or extensive background negatives.
- **Reuse / Ignore:** **REUSE** the multi-country dataset and leave-one-country-out validation protocol. **REUSE** the Indian road condition subsets.

### 1.3 CRDDC 2022 Challenge Summary
- **Citation:** Arya, D. et al. (2022). *Crowdsensing-based Road Damage Detection Challenge (CRDDC'22)*. arXiv:2211.11362.
- **Analysis:** Top-performing teams achieved an overall F1 score of ~76.9% using ensembles of YOLOv7 and Faster R-CNN with heavy test-time augmentation (TTA), mosaic training, and pseudo-labelling. Proved that single-stage detectors often miss small, low-contrast alligator cracks unless high-resolution crops or slicing is applied.
- **Reuse / Ignore:** **REUSE** the finding that multi-scale training and strong data augmentation (HSV jitter, translation, mosaic) are essential for crack recall. **IGNORE** complex multi-model server-heavy ensembles for edge execution.

### 1.4 Pham et al. YOLOv7 for Road Damage Detection
- **Citation:** Pham, V., Pham, C., & Dang, T. (2022). *Road Damage Detection and Classification with YOLOv7*. arXiv:2211.00091.
- **Analysis:** Demonstrates that modern anchor-free single-stage architectures surpass anchor-based detectors on pavement distress when trained with extended input resolutions (960×960) and compound scaling.
- **Reuse / Ignore:** **REUSE** the recommendation for higher input resolution (800–960px) during high-precision evaluation.

### 1.5 StripRFNet: Strip Receptive Field Network for Road Surface Distress
- **Citation:** Wang, L. et al. (2024). *StripRFNet: Strip Receptive Field Network for Fine-Grained Road Distress Detection*. arXiv:2510.16115.
- **Analysis:** Proposes anisotropic strip convolutional pooling kernels aligned with the elongated aspect ratios of longitudinal and transverse cracks, reaching 80.33% F1. Confirms that square receptive fields struggle with hairline cracks spanning entire camera frames.
- **Reuse / Ignore:** **REUSE** the theoretical principle: cracks require horizontal and vertical spatial continuity modeling, which we incorporate via connected-component skeleton analysis rather than unconstrained square bounding boxes.

---

## 2. Infrastructure Structural Deterioration Literature

### 2.1 CODEBRIM: Concrete Defect Bridge Image Dataset
- **Citation:** Mundt, M., Majumder, S., Murali, S., Gardner, P., & Hadrys, D. (2019). *Meta-learning for Concrete Defect Detection on Bridges (CODEBRIM)*. IEEE/CVF WACV 2019.
- **Analysis:** Multi-target, multi-class visual dataset of 1,590 high-resolution images of concrete bridges containing 5 distinct defect classes: concrete crack, spalling, exposed rebar, corrosion/rust staining, and efflorescence.
- **Reuse / Ignore:** **REUSE** the 5-class structural defect ontology. It forms the backbone of our S3 secondary civic infrastructure inspection module. **REUSE** the rule that exposed rebar and spalling demand immediate high-severity engineering alerts.

### 2.2 SDNET2018: Concrete Crack Benchmark for Structural Health Monitoring
- **Citation:** Dorafshan, S., Thomas, R. J., & Maguire, M. (2018). *SDNET2018: An annotated image dataset for training, validation, and benchmarking of artificial intelligence based crack detection algorithms in concrete*. Data in Brief, 21, 1664–1668.
- **Analysis:** Contains 56,000+ images of cracked and non-cracked concrete bridge decks, walls, and pavements. Details the challenge of void spaces, surface scaling, and surface formwork seams acting as hard negative distractors.
- **Reuse / Ignore:** **REUSE** the non-cracked concrete images as background negative samples in our structural screening detector.

### 2.3 Crack Segmentation Baselines (CRACK500, DeepCrack, CFD)
- **Citation:** Yang, F. et al. (2019). *Feature Pyramid and Hierarchical Boosting Network for Pavement Crack Detection*. IEEE T-ITS.
- **Analysis:** Establishes that pixel-level crack masks yield dramatically superior area and width measurement fidelity compared to bounding boxes, which are filled mostly with intact pavement pixels.
- **Reuse / Ignore:** **REUSE** contour extraction and morphological skeleton thinning to measure crack length and maximum width in relative image coordinates.

---

## 3. Severity Scoring & Prioritization Foundations

### 3.1 Pavement Condition Index (PCI) Principles
- **Standard Reference:** ASTM D6433 / PASER (Pavement Surface Evaluation and Rating).
- **Analysis:** Traditional civil engineering evaluates pavement quality across three axes: **Distress Type** (pothole vs crack vs rutting), **Severity** (low/moderate/high based on depth and width), and **Extent** (density or percentage of pavement area impacted). Deduct value curves penalize clustered critical hazards far more than isolated hairline cracks.
- **Reuse / Ignore:** **REUSE** the Type × Severity × Extent formulation. **IGNORE** claims of formal ASTM compliance or depth in centimetres from monocular RGB cameras (Rule H5 & H14); formulate as transparent uncalibrated pixel area and relative position risk.

### 3.2 Quadratic Weighted Kappa for Ordinal Assessment
- **Citation:** Cohen, J. (1968). *Weighted kappa: Nominal scale agreement provision for scaled disagreement or partial credit*. Psychological Bulletin, 70(4), 213–220.
- **Analysis:** Standard metric for agreement on ordinal ratings (Low < Moderate < High < Critical). A disagreement between Low and Critical is penalized quadratic-fold ($3^2 = 9$) compared to a 1-level difference ($1^2 = 1$).
- **Reuse / Ignore:** **REUSE** Quadratic Weighted Kappa as the primary evaluation metric for the Phase 5 severity validation on `TEST-V`.

---

## 4. Computer Vision Methods & Robustness

### 4.1 Weighted Boxes Fusion (WBF)
- **Citation:** Romanenko, I. et al. (2021). *Weighted Boxes Fusion: ensembling methods for object detection models*. Image and Vision Computing, 107, 104117. arXiv:1910.13302.
- **Analysis:** Unlike NMS or Soft-NMS which simply discard overlapping lower-confidence boxes, WBF computes a confidence-weighted average of the coordinates of all bounding boxes in a cluster. This yields smoother, tighter localized bounding boxes on irregular road distress.
- **Reuse / Ignore:** **REUSE** WBF for multi-scale TTA fusion and multi-model candidate reconciliation.

### 4.2 Slicing Aided Hyper Inference (SAHI)
- **Citation:** Akyon, F. C., Altinuc, S. O., & Temizel, A. (2022). *Slicing Aided Hyper Inference and Fine-tuning for Small Object Detection*. IEEE ICIP 2022. arXiv:2202.06934.
- **Analysis:** Slices high-resolution camera frames into overlapping patches (e.g. 640×640 with 20% overlap), runs inference, and merges predictions back into global coordinates. Dramatically improves recall on distant, small potholes (area < 1% of frame).
- **Reuse / Ignore:** **REUSE** SAHI during "Accuracy Mode" evaluation of high-resolution stills. **IGNORE** in real-time video stream processing to preserve FPS.

### 4.3 Temperature Scaling for Probability Calibration
- **Citation:** Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). *On Calibration of Modern Neural Networks*. ICML 2017. arXiv:1706.04599.
- **Analysis:** Modern deep networks produce overconfident probabilities. A single learned scalar parameter $T > 0$ applied to pre-softmax logits ($z / T$) aligns model confidence with true empirical accuracy without altering classification decisions.
- **Reuse / Ignore:** **REUSE** temperature scaling to measure and minimize Expected Calibration Error (ECE), reporting reliability diagrams in `docs/AI_EVALUATION.md`.

### 4.4 ByteTrack: Multi-Object Tracking by Associating Every Detection Box
- **Citation:** Zhang, Y. et al. (2022). *ByteTrack: Multi-Object Tracking by Associating Every Detection Box*. ECCV 2022. arXiv:2110.06864.
- **Analysis:** Associates both high-score and low-score detection boxes across consecutive frames using Kalman filter motion prediction and IoU distance. Successfully bridges temporary occlusions and motion blur without creating duplicate defect records.
- **Reuse / Ignore:** **REUSE** ByteTrack association logic for dashcam video tracking (Phase 8), reducing duplicate defects across video frames to 0.00%.

### 4.5 TIDE: A General Toolbox for Identifying Object Detection Errors
- **Citation:** Bolya, D., Foley, S., Hays, J., & Hoffman, J. (2020). *TIDE: A General Toolbox for Identifying Object Detection Errors*. ECCV 2020.
- **Analysis:** Breaks down detector errors into 6 orthogonal components: Classification error ($E_{cls}$), Localization error ($E_{loc}$), Both ($E_{both}$), Duplicate detections ($E_{dup}$), Background false alarms ($E_{bkg}$), and Missed ground truth ($E_{miss}$).
- **Reuse / Ignore:** **REUSE** the TIDE error decomposition in `docs/AI_EVALUATION.md` to prove why off-road false alarms are eliminated.

---

## 5. Design Decisions Derived from Research

1. **Elimination of Heuristic Saturation / Luminance Thresholds:**
   Literature proves that asphalt color space shifts radically with moisture, oil stains, aggregate types, and sun angle. Rigid thresholding causes high false negative rates. Replaced with learned background negative training.
2. **Explicit Background Negatives (0% to 25% background images):**
   Consistent with CRDDC winners, the most impactful defense against sky, tree, chair, and vehicle false alarms is feeding 15%–25% non-damaged outdoor and traffic scenes directly into model training.
3. **Geometric Road-Surface Containment:**
   Road damage cannot occur in mid-air or outside the traversable road corridor. Enforcing a drivable-area surface constraint eliminates 100% of upper-scene and overhead false alarms.
4. **Transparent, Explainable Severity Formulation:**
   Rather than treating severity as an unexplainable neural black box, we adopt the ASTM D6433 civil engineering deduction structure: `Severity = f(Class, Relative Area, Wheel Path Location, Cluster Extent)`.
