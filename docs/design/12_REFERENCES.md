# Human Design Precedent Study: 12 Real-World Infrastructure & Survey References

**Document:** `docs/design/12_REFERENCES.md`  
**Purpose:** Provide empirical, human-crafted design foundations for ScamRoad's frontend rebuild, moving away from AI-generated template cliches (purple gradients, glowing backdrop-blurs, floating glass cards) toward durable, utilitarian infrastructure software.

---

### 1. Ordnance Survey (UK National Mapping Agency — OS MasterMap)
- **Visual Aesthetic:** Warm off-white bone paper background (`#f8f7f4`), crisp 1px hair-line survey borders, high-contrast black ink typography.
- **Key Takeaway for ScamRoad:** Roadway polygons and bounding boxes must look like surveyor survey markings on high-grade cartographic paper, not glowing neon boxes on a dark void.

### 2. USGS National Map & Geological Survey Data Portal
- **Visual Aesthetic:** Utilitarian government research layout, dense technical tabular metadata, muted stone-grey framing, zero decorative animations.
- **Key Takeaway for ScamRoad:** The inspection metrics and defect coordinate tables should prioritize data density and reading clarity over oversized marketing cards.

### 3. Trimble Geospatial / InSphere Field Suite
- **Visual Aesthetic:** Ruggedized handheld survey screen design: charcoal asphalt background, safety survey amber/orange (`#d97706` / `#c2410c`) for active markers, monospaced GPS coordinates.
- **Key Takeaway for ScamRoad:** Use survey amber as the primary operational accent for active selections and alert tags, conveying genuine field survey tools.

### 4. Leica Geosystems Infinity Inspection Suite
- **Visual Aesthetic:** Industrial measurement UI with chamfered, sharp-cornered data pill tags, deep slate-grey headers, precise mm/px unit annotations.
- **Key Takeaway for ScamRoad:** All measurements must show explicit units (`px_relative_pct` or calibrated area) with clear measurement method badges.

### 5. Topcon MAGNET Field Pavement Profiler
- **Visual Aesthetic:** High-contrast kerb-paint yellow (`#eab308`) and stark white markings against dark asphalt textures, high readability under direct outdoor sunlight.
- **Key Takeaway for ScamRoad:** Defect bounding boxes must remain legible over both glaring wet concrete and pitch-dark shadow asphalt without relying on translucent overlays.

### 6. OpenStreetMap iD Editor
- **Visual Aesthetic:** Functional web-based vector inspection interface: clean grey toolbar, sharp vector nodes, high-contrast sidebar property editor.
- **Key Takeaway for ScamRoad:** The defect inspector sidebar should behave as an authoritative property inspector with editable fields for human engineer review.

### 7. NOAA Nautical Bathymetry & Hazard Chart Viewer
- **Visual Aesthetic:** Monochromatic nautical depth charts with stepped elevation tinting, crisp contour lines, and clear hazard warning diamonds.
- **Key Takeaway for ScamRoad:** Pothole cavity depth estimation ("Shallow", "Medium", "Deep") should use stepped tonal contrast badges rather than rainbow gradients.

### 8. Transport for London (TfL) Street Asset Management Register
- **Visual Aesthetic:** Clean British municipal civic design: Johnston/Helvetica typography, restrained palette, stark white data tables with slate divider rules.
- **Key Takeaway for ScamRoad:** The municipal maintenance work order system should read like an authentic city council asset dispatch console.

### 9. Strava Route Builder (Engineering & Surface View)
- **Visual Aesthetic:** Clean vector line segments showing pavement surface transitions (paved, unpaved, gravel) with crisp monochrome elevation profiles.
- **Key Takeaway for ScamRoad:** Road health maps should display continuous street segments with clear surface distress condition coding.

### 10. Linear.app (Desktop Project System)
- **Visual Aesthetic:** The benchmark for non-decorative, human-crafted modern software: 1px border hierarchy, subtle 4px corner radii, precise keyboard shortcuts, no AI marketing fluff.
- **Key Takeaway for ScamRoad:** Eliminate all floating shadows, neon glowing text, and machine-generated buzzwords; use tight 8px baseline grids.

### 11. GOV.UK Design System
- **Visual Aesthetic:** The global standard for accessible, honest digital public services: absolute minimum contrast ratio 7:1, clear plain-language labels, bold informative banners.
- **Key Takeaway for ScamRoad:** Clear status callouts, honest disclaimers ("Student research project"), and clean error envelopes with plain English explanations.

### 12. Pavemetrics Laser Crack Measurement System (LCMS)
- **Visual Aesthetic:** Industrial road inspection workstation software: monochrome greyscale road profile scans with sharp safety-orange crack skeleton overlays.
- **Key Takeaway for ScamRoad:** Road distress crack contours should be rendered as distinct geometric hulls in deep amber-brown, clearly separated from pothole crater fills.
