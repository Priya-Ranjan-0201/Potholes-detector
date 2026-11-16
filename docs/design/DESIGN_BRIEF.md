# ScamRoad Design Brief: Human Civil Infrastructure Visual Identity

**Document:** `docs/design/DESIGN_BRIEF.md`  
**Direction:** Direction A — "Survey Paper" (with Direction B "Chalk & Kerb" and Direction C "Slate & Brick" tokens available)  
**Author:** Principal Product Designer & Full-Stack Lead  
**Scope:** Complete design system overhaul replacing AI-generated visual templates.

---

## 1. Product Voice & Visual Philosophy
ScamRoad is a serious, technical, and honest road defect detection and municipal maintenance platform developed as a student capstone project. It is **not** a generic Silicon Valley AI SaaS landing page. It should feel like professional field equipment designed by civil engineers and GIS specialists: calm, trustworthy, high-density, and legible under difficult lighting conditions.

### Principles:
1. **Utilitarian & Legible First:** Data density over empty white space; clear contrast over subtle translucency.
2. **Zero AI Clichés:** No purple/cyan gradients, no glowing blur spheres, no frosted glass cards, no floating cards with 24px rounded corners.
3. **Honest Vocabulary:** No "Supercharged AI", "Autonomous Neural Mesh", "Magic Scanner". Use exact terms: "Calibrated ONNX Inference", "YOLO11n Pothole Detector", "Spatial-Temporal Video Tracker".
4. **Student Project Clarity:** Every page footer explicitly displays: *"Student research project. Not an official government system. Not safety-certified."*

---

## 2. Color Palette & Token System

### Primary Direction: "Survey Paper" (Direction A)
- **Canvas / Background:** `#F8F7F4` (Warm bone survey paper, easy on the eyes during prolonged desktop review)
- **Subtle Surface:** `#F0EFEA` (Card and container background)
- **Raised Surface:** `#FFFFFF` (Inspector panels, modal overlays)
- **Ink / Text Main:** `#1A1D1E` (Crisp dark carbon ink, contrast ratio 14.8:1 against canvas)
- **Muted Text:** `#52585B` (Secondary descriptions, metadata)
- **Border Subtle:** `#E2E0D8` (Hairline 1px structural dividers)
- **Border Strong:** `#C8C5BA` (Active tab indicators, card edges)
- **Survey Accent (Active / Select):** `#C2410C` (Warm survey orange, high visibility)
- **Highway Clear (Zero Defect / Health):** `#15803D` (Crisp highway green)
- **Asphalt Distress (Cracks):** `#9A3412` / `#78350F` (Dark bitumen amber)
- **Cavity Hazard (Critical Potholes):** `#B91C1C` (High-visibility warning crimson)

### Dark Mode: "Night Patrol Console"
- **Canvas:** `#121517` (Deep road asphalt at night)
- **Surface:** `#1A1E21` (Field vehicle dashboard panel)
- **Border:** `#2B3136` (Muted instrument frame)
- **Text:** `#EAECEE` (Crisp phosphorescent text, contrast ratio 12.2:1)
- **Accent:** `#EA580C` (Safety cone orange)

---

## 3. Typography & Spatial System

### Type Hierarchy
- **Body & Headings:** `Inter`, `system-ui`, `-apple-system`, `sans-serif` (Neutral neo-grotesque with clean geometry and excellent numerals).
- **Technical Readouts & Coordinates:** `ui-monospace`, `SFMono-Regular`, `Menlo`, `Monaco`, `Consolas`, `monospace` (Fixed-pitch for lat/long, confidence percentages, bbox coordinates, latency).
- **Scale:**
  - Micro / Pill: `11px / 0.75rem`, weight 600, uppercase tracked
  - Meta: `12px / 0.8125rem`, weight 500
  - Body: `14px / 0.875rem`, weight 400/500, line-height 1.5
  - Subhead: `16px / 1.0rem`, weight 600
  - Section Title: `20px / 1.25rem`, weight 700
  - Page Heading: `28px / 1.75rem`, weight 700

### Spatial Rhythm
- **Border Radii:** Strictly `4px` (subtle) to `6px` (container). Never oversized `24px` or `9999px` bubble pills.
- **Elevation:** Flat 1px border hierarchy with hairline `box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05)`. Zero floating drop-shadow glows.

---

## 4. Banned List (AI-Template Hallmarks to Eliminate)
- [x] NO purple-to-teal or blue-to-pink gradient backgrounds
- [x] NO `backdrop-blur` glassmorphism overlays
- [x] NO floating glowing ambient background spheres
- [x] NO marketing buzzwords ("Next-Gen", "Revolutionary", "Supercharged", "Magical")
- [x] NO fake or placeholder statistics
