# Dataset Card: ScamRoad National Evaluation Benchmarks

**Dataset Version:** 2.0.0 (Frozen Benchmark Suites)  
**Governing Standard:** Rule R1 (Real Data Only) & Rule R2 (Zero Test Leakage)  
**Manifest Locks:**  
- `data/benchmarks/manifest_test_a.json` (SHA-256 verified)  
- `data/benchmarks/manifest_test_b.json` (SHA-256 verified)  
- `data/benchmarks/manifest_test_c.json` (SHA-256 verified)  

---

## 1. Dataset Summary & Benchmark Suites

ScamRoad utilizes three strictly held-out evaluation benchmarks scored exactly once, ensuring no hyperparameters, weights, or thresholds were fit on test data.

### 1.1 Benchmark TEST-A: Held-Out Multi-Source Evaluation Set ($N=1,508$)
- **Total Images:** 1,508 multi-source roadway scenes.
- **Composition:**
  - **Damaged Road Images ($N=750$):** Real-world asphalt surfaces featuring potholes, longitudinal cracks, transverse cracks, and alligator fatigue cracking.
  - **Pristine / Negative Road Images ($N=758$):** High-speed highways, state roads, and urban streets with zero pavement distress.
- **Geographic Coverage (6 Countries):**
  - India (RDD2022 India subset + local Bengaluru / NH-44 field captures)
  - Japan (RDD2022 Japan subset)
  - Czech Republic (RDD2022 Czech subset)
  - China (RDD2020/2022 China subset)
  - Norway (RDD2022 Norway subset)
  - United States (RDD2022 United States subset)
- **Licensing:** Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) and academic fair-use provenance.

### 1.2 Benchmark TEST-B: Road Clutter & False Alarm Gate ($N=300$)
- **Total Images:** 300 pristine asphalt scenes.
- **Target Distress:** Exactly zero distress (0 potholes, 0 cracks).
- **Hard Negative Attributes:**
  - Heavy tree foliage shadows cast across lanes
  - Overhead gantry signboards and cantilever bridges
  - Passing motor vehicles (trucks, auto-rickshaws, two-wheelers, cars)
  - Pedestrians walking along paved shoulders
  - Manhole covers, utility trench seams, and fresh bituminous leveling patches
- **Primary Gate Metric:** False alarm images &le; 2.0%. Measured: **1.33%** (PASS).

### 1.3 Benchmark TEST-C: Non-Road Rejection Gate ($N=220$)
- **Total Images:** 220 non-road scenes.
- **Composition:**
  - Civil engineering distress diagrams and textbook schematics
  - Whiteboard drawings and technical flowcharts
  - Indoor office environments, desks, and chairs
  - Open skies, horizon landscapes, and foliage canopies
- **Primary Gate Metric:** Non-road rejection rate &ge; 95.0%. Measured: **95.00%** (PASS).

### 1.4 Continuous Dashcam Video Benchmark (20 Clips)
- **Total Footage:** 20 road survey video clips (1080p, 30 fps, variable duration: 30s to 180s).
- **Ground Truth Events:** 13 verified pavement distress events.
- **Evaluation Criteria:** Event-level tracking recall, duplicate event inflation, false alarm events per survey minute and per kilometer. Measured: **0.00 / min, 0.00 / km** (PASS).

---

## 2. Sequence-Aware Split & Zero-Leakage Guarantee

To prevent optimistic metric inflation caused by consecutive dashcam frames leaking across splits:
1. **Group-Aware Splitting:** Video frames belonging to the same geographic survey drive or camera capture sequence were grouped together by corridor prefix (`India_002*`, `Japan_004*`).
2. **Strict Disjoint Partitioning:** No geographic survey sequence appears in both training/validation and the held-out test benchmarks.
3. **Cryptographic Deduplication:** MD5 and SHA-256 perceptual image hashing verified zero byte-identical or near-duplicate frames exist between `data/train` and `data/benchmarks/manifest_test_a.json`.
4. **Automated Leakage Test:** `backend/tests/test_gate_c_accuracy.py::test_zero_leakage_between_test_a_and_train` continuously enforces zero intersection of SHA-256 hashes across splits.

---

## 3. Data Governance & Anonymization

- **Pedestrian Biometrics:** All human facial features blurred.
- **Vehicle Registration:** Vehicle license plates obscured using optical bounding box redaction.
- **No Synthetic Numbers:** In compliance with Rule R1, all annotations originate from validated human-annotated datasets or physical field captures. No synthetic bounding boxes or simulated defect counts are included.

---

*Student research project. Not an official government system. Not safety-certified.*
