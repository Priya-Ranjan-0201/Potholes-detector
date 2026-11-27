# ScamRoad — Road Distress Annotation & Labeling Guide

**Standard:** YOLO Object Detection Format (`<class_id> <x_center> <y_center> <width> <height>`)  
**Single Source of Truth:** `shared/taxonomy.yaml`  
**Target Domain:** Indian Highway, Municipal, and Campus Pavements  

---

## 1. Class Taxonomy & Identification Criteria

| Class ID | Class Code | Taxonomy Name | Description & Key Visual Identifiers |
| :---: | :---: | :--- | :--- |
| **0** | **`D40`** | **Pothole** | Bowl-shaped cavity in asphalt surface where wearing course has ruptured and dislodged. Characterized by steep internal shadows, exposed aggregate sub-base, and sharp perimeter lips. |
| **1** | **`D00`** | **Longitudinal Crack** | Single structural crack line propagating parallel ($\pm 30^\circ$) to the direction of vehicular travel, commonly along paving seams, wheel tracks, or lane markings. |
| **2** | **`D10`** | **Transverse Crack** | Single crack line oriented predominantly perpendicular ($60^\circ\text{--}120^\circ$) across lane width, caused by thermal shrinkage cycles or reflective sub-grade shifting. |
| **3** | **`D20`** | **Alligator Crack** | Interconnected pattern of structural fatigue fissures forming a multi-sided polygonal mosaic (similar to reptilian skin). Indicates base course failure under heavy axle loads. |
| **4** | **`D41`** | **Water-Filled Pothole** | Depressed cavity filled with turbid water or mud where fractured perimeter asphalt edges are clearly visible. Treated with high severity due to hydroplaning risk. |
| **5** | **`S01`** | **Concrete Crack** | Structural fracture in concrete civil assets (bridges, retaining walls, culverts, abutments). |
| **6** | **`S02`** | **Spalling** | Flaking, chipping, or detachment of concrete surface exposing the sub-surface matrix. |
| **7** | **`S03`** | **Exposed Rebar** | Structural reinforcing steel bars visibly protruding or uncovered due to extensive concrete loss. Critical safety hazard. |
| **8** | **`S04`** | **Corrosion / Rust** | Oxidation staining and iron hydroxide runoff bleeding across concrete faces. |
| **9** | **`S05`** | **Efflorescence** | Crystalline salt deposits leached by moisture seepage through concrete joints and retaining structures. |

---

## 2. Pavement & Surface Distinctions

### Edge Case A: Water-Filled Pothole vs. Surface Water Puddle (Gate D Policy)
- **Water-Filled Pothole (Defect — `D41` / `POTHOLE`):**
  - **Definition:** Structural cavity in asphalt wearing and binder courses filled with rainwater, silt, or muddy runoff.
  - **Visual Criteria:**
    1. **Fractured Asphalt Rim:** Visible broken, jagged, or sharp asphalt lip perimeter indicating ruptured wearing course.
    2. **Internal Depth / Shadow:** Dark absorption cavity inside the water boundary; turbid bottom sediment distinct from surrounding road texture.
    3. **Structural Depression:** Visible height drop from surrounding road plane into the cavity.
  - **Classification:** **DEFECT (High Severity)** due to dynamic wheel impact damage and high hydroplaning hazard.

- **Surface Water Puddle (Negative / Non-Defect):**
  - **Definition:** Shallow, harmless standing water film on top of intact, undamaged asphalt or concrete pavement.
  - **Visual Criteria:**
    1. **Smooth Perimeter Transition:** Water edge thins continuously to zero depth with no broken asphalt edges or height drop.
    2. **Texture Continuation:** Underlying aggregate texture, painted lane lines, or road crown continue unbroken beneath the water film.
    3. **Specular Sky Reflection:** Flat mirror reflection of overcast sky or direct sunlight without internal cavity perimeter.
  - **Classification:** **NON-DEFECT (0 Annotations)**. Puddles on intact asphalt must NEVER be boxed as potholes.

---

## 3. CVAT Annotation Protocol & Two-Annotator Quality Control

In compliance with **Gate D (India Coverage & Annotation Reliability)**, all ground truth datasets must adhere to the two-annotator quality gate:

### 3.1 CVAT Setup & Tooling
- Tool: Computer Vision Annotation Tool (CVAT) / Label Studio.
- Labeling Format: Rectangle bounding box with class attributes (`severity`, `wet_status`, `camera_mount`).
- Zoom & Precision: Annotators must zoom to $\ge 150\%$ resolution when boxing small distant defects ($< 32\times 32$ pixels).

### 3.2 Two-Annotator Agreement Verification Protocol
1. **Independent Dual Annotation:**
   - Every candidate image is labeled independently by **Annotator 1** and **Annotator 2** without cross-communication.
2. **Intersection-over-Union (IoU) Matching:**
   - Two boxes are considered matched if $\text{IoU} \ge 0.70$ and $\text{Class ID}$ matches exactly.
3. **Inter-Annotator Agreement Metric:**
   - Inter-annotator agreement is scored via Cohen's Kappa:
     $$\kappa = \frac{p_o - p_e}{1 - p_e}$$
   - **Quality Gate:** $\kappa \ge 0.75$ across the dataset batch.
4. **Adjudication Phase:**
   - All disagreements (boundary $\text{IoU} < 0.70$, class mismatch, or one-sided detections) are routed to the **Principal Civil Engineer Reviewer Queue**.
   - The adjudicator verifies ground truth against high-resolution zoom and local road condition logs before finalizing the master annotation.

### Edge Case B: Bitumen Patch vs. Pothole
- **Bitumen Patch (Negative / Non-Defect):** Fresh or weathered asphalt applied during municipal repairs. Surface is raised or coplanar with the road, exhibiting flat granular texture without an internal depression shadow.
- **Rule:** **DO NOT label bitumen patches as potholes.**

### Edge Case C: Non-Road Backgrounds & Off-Road Objects
- **Rule:** **NEVER label people, vehicles, signs, vegetation, or sky.** Defects exist strictly on road pavement or civil infrastructure surfaces. If an object is not road pavement or concrete structure, it must have 0 annotations.

### Edge Case B: Cast-Iron Manhole Cover vs. Pothole
- **Manhole Cover (Negative / Non-Defect):** Circular or rectangular metallic utility access cover. Displays concentric iron ridges, metallic luster, and level road grade.
- **Rule:** **DO NOT label manhole covers as potholes.** Save in hard-negative training set with a $0$-byte label file.

### Edge Case C: Bridge Expansion Joint vs. Transverse Crack
- **Expansion Joint (Negative / Non-Defect):** Uniform, straight linear seam running completely across the road deck, often reinforced with metal teeth or rubber elastomeric sealants.
- **Rule:** **DO NOT label expansion joints as transverse cracks.**

### Edge Case D: Tree / Building Shadow vs. Longitudinal Crack
- **Shadow Edge (Negative / Non-Defect):** Linear illumination drop caused by sunlight occlusions. Has a soft penumbra gradient and continuous road texture beneath the shadow.
- **Rule:** **DO NOT label shadow edges as cracks.**

---

## 4. File Format & Directory Structure

Each image file `sample_name.jpg` has an associated `sample_name.txt` label file in the adjacent `labels/` directory:

```
data/local_sample/
├── images/
│   ├── campus_01.jpg
│   └── campus_02.jpg
└── labels/
    ├── campus_01.txt
    └── campus_02.txt
```

Each line in `sample_name.txt` contains 5 space-delimited floats normalized to $[0.0, 1.0]$:
```
<class_id> <x_center> <y_center> <width> <height>
```
*Example:*
```
0 0.452100 0.683400 0.124500 0.089200
1 0.781200 0.542000 0.045000 0.285000
```

> **Background Images (Negative Samples):** If an image contains zero defects (e.g. clean surface, shadow, or manhole), the corresponding `.txt` file must be created with **0 bytes (empty)**.
