# ScamRoad — Field Pilot Validation Protocol (Gate F)

> **Rule R3 Notice:** Student research project. Not an official government system. Not safety-certified.  
> **Rule R1 Integrity Notice:** This document establishes the formal scientific protocol for field pilot trials. In adherence to Rule R1, pilot metrics are **never fabricated or simulated**. All data sheets represent template execution structures pending field drive acquisition.

---

## 1. Pilot Corridor Selection & Specifications

| Parameter | Specification |
| :--- | :--- |
| **Designated Highway Corridor** | **National Highway 44 (NH-44)** — Bengaluru Outer Ring Road to Devanahalli Corridor |
| **Chainage Range** | **km 10.000 to km 35.000 (Total Length: 25.0 km)** |
| **Jurisdiction / Road Class** | National Highway (NHAI Regional Office Bengaluru / PWD Karnataka) |
| **Pavement Structure** | Flexible bituminous pavement (Bituminous Concrete BC + Dense Bituminous Macadam DBM) |
| **Lanes & Direction** | 6-lane divided carriageway (3 lanes northbound, 3 lanes southbound) |
| **Target Survey Speed** | 45–65 km/h in dedicated survey vehicle or smartphone-equipped passenger vehicle |
| **Operating Weather Window** | Daylight clear pavement (10:00–16:00 IST), dry asphalt surface, wind < 25 km/h |

---

## 2. Ground Truth Acquisition Methodology

To validate ScamRoad AI against engineer-certified ground truth without circular bias, ground truth must be captured via one of two authorized physical methods:

### Method A: Engineer Manual Walking Survey (Primary Baseline)
- **Personnel:** Two certified Civil Diploma / Graduate Engineers accompanied by safety vehicle and highway patrol escort.
- **Instrumentation:**
  - Calibrated survey wheel / rolling distance meter (chainage resolution: 0.1 m).
  - High-precision RTK-GNSS receiver (sub-meter horizontal position accuracy: $\le 0.5\text{ m}$).
  - Depth gauge and graduated rule (depth resolution: 1.0 mm).
- **Recorded Attributes per Physical Defect:**
  1. Chainage ($km + m$, e.g. `km 14.320`)
  2. Carriageway & Lane Position (L1, L2, L3, Shoulder)
  3. Defect Classification (Pothole, Longitudinal Crack, Transverse Crack, Alligator Fatigue Crack, Ravelling)
  4. Dimensions: Length ($L$), Width ($W$), Maximum Depth ($D$) in cm
  5. Photographic reference with physical scale board

### Method B: Automated Network Survey Vehicle (NSV / ROMDAS)
- Where available through institutional partnership (e.g. NHAI / CRRI survey), calibrated NSV laser profilometer and automated crack survey logs serve as the secondary continuous benchmark.

---

## 3. Survey Synchronization & Matching Rules

### 3.1 Temporal Synchronization
- Vehicle survey runs must be executed within **$\le 24\text{ hours}$** of the ground truth engineer survey.
- Prevents defect morphing (pothole expansion from rainfall traffic) or unrecorded contractor cold-patching.

### 3.2 Spatial Matching Window
An AI-detected defect event ($D_{\text{pred}}$) is matched to a Ground Truth defect ($D_{\text{gt}}$) if and only if:
1. **Along-Track Distance Error:** $|\text{Chainage}_{\text{pred}} - \text{Chainage}_{\text{gt}}| \le 5.0\text{ meters}$.
2. **Cross-Track Distance Error:** $|\Delta \text{Lateral Position}| \le 1.8\text{ meters}$ (same or immediately adjacent lane).
3. **Class Compatibility:** Exact class match (`POTHOLE` $\leftrightarrow$ `POTHOLE`, `CRACK_*` $\leftrightarrow$ `CRACK_*`).
4. **One-to-One Bipartite Matching:** Solved via Hungarian Algorithm minimizing spatial distance. Unmatched predictions count as False Positives ($\text{FP}$); unmatched ground truth records count as False Negatives ($\text{FN}$).

---

## 4. Formal Pilot Validation Metrics

ScamRoad evaluates 5 distinct mathematical dimensions of field pilot reliability:

### 4.1 Defect Detection Accuracy
$$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}, \quad \text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}, \quad F_1 = \frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

### 4.2 Spatial Location Error
Evaluated across all true positive matched pairs:
$$\overline{\Delta x}_{\text{along-track}} = \frac{1}{\text{TP}} \sum_{i=1}^{\text{TP}} |\text{Chainage}_{\text{pred}, i} - \text{Chainage}_{\text{gt}, i}|$$
$$\text{Target:} \quad \overline{\Delta x} \le 3.5\text{ meters}$$

### 4.3 Repeat-Pass Consistency (Reliability across Passes)
Two independent survey drives (Pass A and Pass B) conducted on the same day over the identical 25.0 km corridor:
$$C_{\text{repeat}} = \frac{|\text{Events}_{\text{Pass A}} \cap \text{Events}_{\text{Pass B}}|}{|\text{Events}_{\text{Pass A}} \cup \text{Events}_{\text{Pass B}}|}$$
$$\text{Target:} \quad C_{\text{repeat}} \ge 85.0\%$$

### 4.4 Review Workload Ratio (Gate E Integration)
Measures the operational load placed on human reviewers:
$$W_{\text{review}} = \frac{N_{\text{triage queue}} (0.25 \le \text{conf} < 0.65)}{N_{\text{total detections}}}$$
$$\text{Target:} \quad W_{\text{review}} \le 25.0\% \text{ of detections requiring human inspection}$$

### 4.5 False Alarm Rate per Kilometer
$$\text{FAR}_{\text{km}} = \frac{\text{False Positive Defects}}{\text{Total Highway Length (km)}}$$
$$\text{Target:} \quad \text{FAR}_{\text{km}} \le 0.50 \text{ false alarms per kilometer}$$

---

## 5. Field Execution Checklist & Data Sheet Template

```
PILOT RUN ID:          PILOT-NH44-2026-____
DATE OF SURVEY:        YYYY-MM-DD
SURVEY VEHICLE:        ________________________________
MOUNT TYPE:            Windshield Suction Rig (Phone / Dashcam)
CAMERA MODEL:          ________________________________
CORRIDOR:              NH-44 (Hebbal km 10.000 to Devanahalli km 35.000)
WEATHER CONDITION:     Dry Daylight / Overcast / Glare

GROUND TRUTH LOG (Blank Template):
+-----+---------------+----------+-----------+------------+------------+---------------+
| No. | Chainage (km) | Lane     | Defect    | L x W (cm) | Depth (mm) | RTK GPS (Lat) |
+-----+---------------+----------+-----------+------------+------------+---------------+
| 01  | km 10.450     | Lane 2   | Pothole   | 45 x 30    | 42 mm      | 13.045123     |
| 02  | km 12.180     | Shoulder | Pothole   | 60 x 55    | 65 mm      | 13.061890     |
| 03  | km 14.820     | Lane 1   | Alligator | 180 x 90   | N/A        | 13.084210     |
+-----+---------------+----------+-----------+------------+------------+---------------+
```

*(Field work pending physical collection logged in docs/HUMAN_TODO.md).*
