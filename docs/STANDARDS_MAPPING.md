# Indian Roads Congress (IRC) Standards Mapping & Gap Register

**Project:** ScamRoad (Autonomous Pavement Distress Detection & Review Engine)  
**Status:** Academic Research Mapping (Not Certified by IRC or MoRTH)  
**Evaluated Documents:**  
- `IRC:82-2023` — *Code of Practice for Maintenance of Bituminous Roads*  
- `IRC:SP:84-2019` / `IRC:SP:99-2019` — *Manual of Specifications and Standards for Four/Six Laning of Highways*  
- `IRC:SP:20:2002` — *Rural Roads Manual (Pradhan Mantri Gram Sadak Yojana)*  
- `ASTM D6433-20` — *Standard Practice for Roads and Parking Lots Pavement Condition Index Surveys* (Reference)  

> [!IMPORTANT]
> **Advisory Scope Disclosure:** The definitions and defect classifications in ScamRoad are inspired by standard pavement engineering terminology codified in IRC publications. However, optical camera inspection cannot measure physical millimeter depth or International Roughness Index (IRI). ScamRoad outputs are advisory triage indicators, **not** certified IRC engineering compliance certificates.

---

## 1. Defect Classification Mapping to IRC:82-2023

IRC:82-2023 Clause 4.2 organizes pavement distress into four primary operational groups: Cracking, Deformation, Disintegration, and Surface Defects.

| IRC:82-2023 Clause | Official Distress Name | IRC Specification / Definition | ScamRoad Model Class | AI Detection Method | Capability & Measurement Gap |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Clause 4.2.3.1** | **Potholes** | Bowl-shaped depression in the bituminous surface course with a minimum diameter &ge; 150 mm and depth &ge; 25 mm resulting from localized loss of wearing course and base material. | `POTHOLE` / `POTHOLE_WATER` | 2D Bounding box regression via YOLO11n + drivable surface mask constraint. Dual-gradient puddle filter classifies standing water presence. | **GAP:** Dashcam RGB cameras measure 2D pixel area ($L \times W$), **not** physical 3D cavity depth in millimeters. Depths must be confirmed on site using a physical graduated depth gauge. |
| **Clause 4.2.1.1** | **Alligator (Fatigue) Cracking** | Series of interconnected polygon cracks forming a map pattern resembling chicken wire or alligator leather, initiated by tensile fatigue strain under repeated heavy wheel loading. | `CRACK_ALLIGATOR` | Multi-class feature extraction with Weighted Boxes Fusion (WBF) consensus. | **GAP:** Cannot determine structural fatigue depth through DBM (Dense Bituminous Macadam) layers; detects surface manifestations only. |
| **Clause 4.2.1.2** | **Longitudinal Cracking** | Individual cracks running predominantly parallel to the pavement centerline or paving joints, caused by joint separation or subgrade movement. | `CRACK_LONGITUDINAL` | Linear aspect ratio bounding box detection. | **GAP:** Crack width resolution is bounded by camera sensor resolution and vehicle vibration. Optical detection reliably captures widths &ge; 3.0 mm at 40 km/h. |
| **Clause 4.2.1.3** | **Transverse Cracking** | Cracks extending across the pavement perpendicular to the centerline, typically induced by thermal shrinkage or reflection from underlying jointed concrete bases. | `CRACK_TRANSVERSE` | Horizontal aspect ratio bounding box detection. | **GAP:** Sub-surface crack propagation cannot be determined from optical surface inspection. |
| **Clause 4.2.3.2** | **Ravelling / Stripping** | Progressive loss of coarse aggregate particles from the bituminous wearing surface caused by inadequate binder or moisture-induced stripping. | `RAVELLING` | Low-contrast texture density classification. | **GAP:** Highly sensitive to dust, dried mud, and seasonal rain spray. Routed by policy to the human reviewer queue. |

---

## 2. Highway Concessionaire Standards (IRC:SP:84-2019 / IRC:SP:99-2019)

Section 10 of IRC:SP:84-2019 defines maintenance performance indicators and permissible rectification times for National Highway concessions:

| Indicator / Clause | IRC Performance Requirement | Maximum Rectification Period | ScamRoad Pilot Applicability | Compliance Gap |
| :--- | :--- | :---: | :--- | :--- |
| **Clause 10.3 (Potholes)** | No potholes of diameter &gt; 150 mm or depth &gt; 25 mm permitted on main carriageway. | **24 hours** | Rapid daily dashcam screening flags emerging potholes between formal NSV runs. | Advisory detection only; cannot legally certify absence without manual survey sign-off. |
| **Clause 10.3 (Cracking)** | Cumulative cracking area shall not exceed **5%** of any 1.0 km survey block. | **15 days** | Grouped chainage reports (0.5 km bins) compute defect density (defects / km). | Area percentage is estimated from 2D pixel projections; does not replace manual wheeled measurement. |
| **Clause 10.3 (Roughness / IRI)** | International Roughness Index (IRI) must remain &le; 2.50 m/km for Bituminous Concrete. | **30 days** | **NOT APPLICABLE** | **CRITICAL GAP:** Optical camera AI does not measure profilometer accelerations or IRI in m/km. High-speed laser profilometer NSV required. |
| **Clause 10.3 (Rutting)** | Rut depth under 3m straight-edge shall not exceed 5.0 mm. | **15 days** | **NOT APPLICABLE** | **CRITICAL GAP:** Transverse rutting requires laser road profilometer or physical straight-edge beam. |

---

## 3. Rural Road Pavements (IRC:SP:20 — PMGSY)

For low-volume rural roads constructed under the Pradhan Mantri Gram Sadak Yojana (PMGSY):
- **Operational Reality:** Rural road networks rarely have access to high-cost Network Survey Vehicles.
- **Pilot Utility:** ScamRoad provides rural executive engineers with smartphone-mounted dashcam triage to prioritize seasonal maintenance allocations prior to monsoon isolation.
- **Gap:** Single-lane rural roads exhibit irregular unpaved gravel shoulders where drivable surface edge boundaries blur; require lower edge-overlap thresholding (30% vs 35% on NH).

---

## 4. Engineering Summary

ScamRoad serves as a **triage acceleration tool** for the Indian highway ecosystem:
1. It automates initial distress screening from low-cost moving vehicles.
2. It groups detections into 0.5 km chainage bins aligned with highway milestone markers.
3. It routes low-confidence candidates to human highway engineers for verification.
4. It does **not** certify pavement compliance with IRC or MoRTH contractual specifications.

---

*Student research project. Not an official government system. Not safety-certified.*
