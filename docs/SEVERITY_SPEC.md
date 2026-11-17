# Severity Assessment & Prioritization Specification

**Document:** `docs/SEVERITY_SPEC.md`  
**Version:** 2.0.0  
**Project:** AI-Powered Road and Infrastructure Damage Detection and Severity Assessment (`RoadSurvey AI`)  
**Scope:** Transparent, monotonic severity scoring model and repair prioritization ranking.

---

## 1. Core Principles & Civil Engineering Foundations

1. **Measurable Physical Evidence Only:**
   Severity is calculated strictly from geometric, spatial, and contextual features extracted from the input pixels and neural detections. **Detection confidence is NEVER used as a proxy for severity.**
2. **No Monocular Centimetre Claims (Rule H14):**
   Depth and volumetric quantities cannot be measured accurately from single-view monocular camera photos. All spatial measures are expressed as uncalibrated pixel area or relative percentage of the pavement surface ($\%$ of road mask area).
3. **Monotonicity:**
   Increasing defect area, locating a defect in an active vehicle wheel path, or detecting severe structural indicators (e.g., exposed rebar) strictly increases (or maintains) the severity score—it never decreases it.
4. **Transparent Explainability:**
   Every single detection outputs a clear, human-readable rationale detailing the exact sub-factors contributing to its score.

---

## 2. Mathematical Formulation

The severity score $S \in [0, 100]$ for detection $i$ is defined as:

$$S_i = \min\left(100, \; \text{round}\left(W_{\text{class}} \times M_{\text{area}} \times M_{\text{position}} + B_{\text{extent}} + F_{\text{risk}}\right)\right)$$

### 2.1 Base Class Hazard Weight ($W_{\text{class}}$)
Reflects the inherent danger posed to vehicular control or structural stability:
- **Exposed Rebar (`EXPOSED_REBAR`):** $85.0$ (Critical structural integrity compromise)
- **Water-Filled Pothole (`WATER_FILLED_POTHOLE`):** $62.0$ (Severe hydroplaning and hidden depth hazard)
- **Spalling (`SPALLING`):** $58.0$ (Active concrete detachment)
- **Corrosion / Rust (`CORROSION_RUST`):** $52.0$ (Reinforcement oxidation indicator)
- **Dry Pothole (`POTHOLE`):** $48.0$ (Tire rupture and suspension impact hazard)
- **Alligator Crack (`CRACK_ALLIGATOR`):** $40.0$ (Sub-base structural fatigue failure)
- **Concrete Crack (`CONCRETE_CRACK`):** $32.0$ (Tensile fracture in civic structures)
- **Transverse Crack (`CRACK_TRANSVERSE`):** $28.0$ (Thermal shrinkage or reflective joint)
- **Efflorescence (`EFFLORESCENCE`):** $25.0$ (Moisture leaching through concrete matrix)
- **Longitudinal Crack (`CRACK_LONGITUDINAL`):** $22.0$ (Paving seam or wheel-path line)

### 2.2 Relative Area Multiplier ($M_{\text{area}}$)
Calculated from the ratio of defect bounding box area to total detected pavement surface area:

$$r = \frac{\text{Area}_{\text{defect}}}{\text{Area}_{\text{pavement}}}$$

$$M_{\text{area}} = \text{clamp}\left(0.80, \; 1.60, \; 0.80 + 12.0 \times r\right)$$

- Defects occupying $<1\%$ of the pavement area receive a dampening multiplier ($0.80$ to $0.92$).
- Major craters occupying $\ge 5\%$ of the road surface scale up to the maximum factor ($1.60$).

### 2.3 Position Risk Multiplier ($M_{\text{position}}$)
Pavement lane analysis places highest danger on vehicle wheel tracks:
- **Active Wheel Path ($x \in [16\%, 36\%]$ or $[64\%, 84\%]$):** $M_{\text{position}} = 1.25$
- **Lane Center:** $M_{\text{position}} = 1.00$
- **Shoulder / Curb Margin:** $M_{\text{position}} = 0.85$

### 2.4 Extent / Cluster Bonus ($B_{\text{extent}}$)
Co-located defects indicate widespread pavement fatigue:

$$B_{\text{extent}} = \min\left(20.0, \; 5.0 \times (N_{\text{cluster}} - 1)\right)$$

Where $N_{\text{cluster}}$ is the total number of detected defects in the current survey frame.

### 2.5 Structural Risk Flags ($F_{\text{risk}}$)
- **Exposed Rebar Bonus:** $+25.0$ points.
- **Active Water Seepage Bonus:** $+12.0$ points.

---

## 3. Severity Categorization & Visual Indicators

| Level | Score Range | Shape Symbol | Accessible Color Code | Recommended Action |
| :---: | :---: | :---: | :---: | :--- |
| **Low** | $0 \le S < 30$ | **Circle** (`●`) | `#2F7D5B` (Highway Green) | Routine periodic monitoring; schedule during annual maintenance. |
| **Moderate** | $30 \le S < 55$ | **Square** (`■`) | `#A87900` (Amber Gold) | Preventative crack-pour sealing or surface patching within 90 days. |
| **High** | $55 \le S < 75$ | **Triangle** (`▲`) | `#C2410C` (Survey Orange) | Priority asphalt mill-and-fill or concrete repair within 14 days. |
| **Critical** | $75 \le S \le 100$ | **Diamond** (`◆`) | `#B91C1C` (Safety Red) | Immediate 24-hour emergency containment and structural barricading. |

*Note: In accordance with WCAG 2.2 accessibility standards, levels are always rendered using distinct geometric glyphs paired with text labels, never color alone.*

---

## 4. Prioritization Ranking Formula

In Phase 6, surveys and defects are ranked by **Priority Score**:

$$\text{Priority} = \text{Severity} \times E_{\text{exposure}}$$

Where $E_{\text{exposure}}$ is derived strictly from **user-entered survey metadata**:
- **Road / Asset Class:** Primary Arterial / Highway ($1.5$), Major Collector ($1.2$), Local Street / Residential ($1.0$), Footpath ($0.9$).
- **Traffic Level:** User rating $1$ to $5$ ($E_{\text{traffic}} = 0.8 + 0.1 \times \text{Rating}$).
- If no context is supplied, $E_{\text{exposure}} = 1.0$, and Priority equals Severity (with clear UI notice: *"Standard unweighted priority"*).
