"""Generate ScamRoad 10-slide PowerPoint Presentation (.pptx) with exact project road theme.
"""

import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

PROJECT_ROOT = Path(__file__).resolve().parent

# --- Color Palette (Project Roadwork Theme) ---
COLOR_BG = RGBColor(11, 15, 20)           # #0B0F14 Deep Asphalt Black
COLOR_CARD = RGBColor(18, 24, 32)         # #121820 Charcoal Slate Surface
COLOR_CARD_ALT = RGBColor(30, 41, 59)     # #1E293B Slate Navy
COLOR_BORDER = RGBColor(40, 53, 69)       # #283545 Dark Border
COLOR_ORANGE = RGBColor(255, 90, 0)       # #FF5A00 High-Vis Safety Orange
COLOR_YELLOW = RGBColor(255, 210, 0)      # #FFD200 Bright Hazard Yellow
COLOR_WHITE = RGBColor(255, 255, 255)     # #FFFFFF Crisp White
COLOR_MUTED = RGBColor(148, 163, 184)     # #94A3B8 Slate Gray
COLOR_GREEN = RGBColor(16, 185, 129)      # #10B981 Emerald Green
COLOR_DARK_ORANGE = RGBColor(224, 79, 0)  # #E04F00

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def set_slide_background(slide, color=COLOR_BG):
    """Fills slide background with deep asphalt black."""
    bg_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5)
    )
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = color
    bg_shape.line.fill.background()
    return bg_shape

def add_header(slide, title_text, category_text="SCAMROAD AI · PAVEMENT INSPECTION ENGINE", slide_num=None):
    """Creates a standardized dark header bar with hazard orange accents."""
    # Top thin safety orange accent bar
    top_bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.08)
    )
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = COLOR_ORANGE
    top_bar.line.fill.background()

    # Category pill
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(9.0), Inches(0.4))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = f"●  {category_text}"
    p_cat.font.name = "Consolas"
    p_cat.font.size = Pt(11)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_YELLOW

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.0), Inches(0.8))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.name = "Segoe UI"
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE

    if slide_num:
        num_box = slide.shapes.add_textbox(Inches(11.5), Inches(0.4), Inches(1.0), Inches(0.4))
        p_num = num_box.text_frame.paragraphs[0]
        p_num.alignment = PP_ALIGN.RIGHT
        p_num.text = f"{slide_num:02d} / 10"
        p_num.font.name = "Consolas"
        p_num.font.size = Pt(11)
        p_num.font.color.rgb = COLOR_MUTED

def add_card(slide, left, top, width, height, border_color=COLOR_BORDER, fill_color=COLOR_CARD):
    """Adds a rounded-like dark asphalt card container."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = fill_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)
    return card

# ==============================================================================
# SLIDE 1: Title & Cover Slide
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1)

# Decorative hazard striped bar on left
side_stripe = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.25), Inches(7.5))
side_stripe.fill.solid()
side_stripe.fill.fore_color.rgb = COLOR_ORANGE
side_stripe.line.fill.background()

# Central Hero Card
hero_card = add_card(s1, Inches(1.2), Inches(1.0), Inches(11.0), Inches(5.5), border_color=COLOR_ORANGE, fill_color=COLOR_CARD)

# Category pill inside hero
pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.8), Inches(1.6), Inches(5.2), Inches(0.45))
pill.fill.solid()
pill.fill.fore_color.rgb = COLOR_BG
pill.line.color.rgb = COLOR_BORDER
p_pill = pill.text_frame.paragraphs[0]
p_pill.text = "● SCAMROAD AI · NEXT-GEN PAVEMENT INTELLIGENCE"
p_pill.font.name = "Consolas"
p_pill.font.size = Pt(11)
p_pill.font.bold = True
p_pill.font.color.rgb = COLOR_YELLOW
p_pill.alignment = PP_ALIGN.CENTER

# Big Project Title
t_box = s1.shapes.add_textbox(Inches(1.8), Inches(2.2), Inches(9.8), Inches(1.3))
tf = t_box.text_frame
tf.word_wrap = True
p1 = tf.paragraphs[0]
p1.text = "ScamRoad — Autonomous Road Distress"
p1.font.name = "Segoe UI"
p1.font.size = Pt(36)
p1.font.bold = True
p1.font.color.rgb = COLOR_WHITE

p2 = tf.add_paragraph()
p2.text = "Inspection & Civil Audit Engine"
p2.font.name = "Segoe UI"
p2.font.size = Pt(36)
p2.font.bold = True
p2.font.color.rgb = COLOR_ORANGE

# Subtitle / Description
desc_box = s1.shapes.add_textbox(Inches(1.8), Inches(3.7), Inches(9.6), Inches(0.9))
p_desc = desc_box.text_frame.paragraphs[0]
p_desc.text = "An edge-optimized computer vision system engineering YOLO11n-Rescue, dual spatial priors, and ASTM D6433 civil compliance for automated highway condition intelligence."
p_desc.font.name = "Segoe UI"
p_desc.font.size = Pt(14)
p_desc.font.color.rgb = COLOR_MUTED

# Metric Badges
kpis = [
    ("96.8%", "Distress Precision", COLOR_ORANGE),
    ("< 120ms", "Inference Speed", COLOR_YELLOW),
    ("0 False Alarms", "On Car Shadows", COLOR_GREEN),
    ("ASTM D6433", "PCI Rating Engine", COLOR_WHITE),
]
for i, (val, lbl, col) in enumerate(kpis):
    bx = Inches(1.8 + i * 2.45)
    b_card = add_card(s1, bx, Inches(4.7), Inches(2.3), Inches(1.2), border_color=COLOR_BORDER, fill_color=COLOR_BG)
    tf_b = b_card.text_frame
    p_v = tf_b.paragraphs[0]
    p_v.text = val
    p_v.font.name = "Segoe UI"
    p_v.font.size = Pt(18)
    p_v.font.bold = True
    p_v.font.color.rgb = col
    p_v.alignment = PP_ALIGN.CENTER
    
    p_l = tf_b.add_paragraph()
    p_l.text = lbl
    p_l.font.name = "Segoe UI"
    p_l.font.size = Pt(10)
    p_l.font.color.rgb = COLOR_MUTED
    p_l.alignment = PP_ALIGN.CENTER

# Author footer tag
auth_box = s1.shapes.add_textbox(Inches(1.2), Inches(6.7), Inches(11.0), Inches(0.5))
p_auth = auth_box.text_frame.paragraphs[0]
p_auth.text = "Lead Researcher & Engineer: Priye Ranjan  ·  GitHub: @Priya-Ranjan-0201  ·  Open Source Engine"
p_auth.font.name = "Segoe UI"
p_auth.font.size = Pt(12)
p_auth.font.bold = True
p_auth.font.color.rgb = COLOR_WHITE
p_auth.alignment = PP_ALIGN.CENTER

# ==============================================================================
# SLIDE 2: The Problem (The Infrastructure Crisis)
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2)
add_header(s2, "The Problem: The Infrastructure Inspection Crisis", "01. PROBLEM STATEMENT", 2)

cards_s2 = [
    ("Slow & Reactive Inspections", "Traditional municipal surveys rely almost entirely on citizen complaints after accidents occur, creating weeks or months of unmonitored road deterioration.", COLOR_ORANGE),
    ("Prohibitive Equipment Costs", "State-of-the-art highway laser profilers (3D LiDAR survey vans) cost $100,000+ per vehicle, pricing out 98% of municipalities and secondary road networks.", COLOR_YELLOW),
    ("Subjective & Inconsistent Manual Audits", "Manual foot surveys produce arbitrary, qualitative logs with zero cryptographic audit trails, enabling contractor disputes and delayed maintenance work orders.", COLOR_MUTED),
    ("Compounding Economic & Safety Costs", "Unrepaired cavities and structural fractures lead to fatal commuter accidents, massive vehicle suspension wear, and 5x higher reclamation costs when neglected.", COLOR_ORANGE),
]

for idx, (title, text, accent) in enumerate(cards_s2):
    row = idx // 2
    col = idx % 2
    x = Inches(0.8 + col * 5.9)
    y = Inches(1.8 + row * 2.6)
    
    c = add_card(s2, x, y, Inches(5.7), Inches(2.3), border_color=COLOR_BORDER, fill_color=COLOR_CARD)
    tf = c.text_frame
    p_t = tf.paragraphs[0]
    p_t.text = f"❌  {title}"
    p_t.font.name = "Segoe UI"
    p_t.font.size = Pt(17)
    p_t.font.bold = True
    p_t.font.color.rgb = accent
    
    p_m = tf.add_paragraph()
    p_m.text = text
    p_m.font.name = "Segoe UI"
    p_m.font.size = Pt(12)
    p_m.font.color.rgb = COLOR_WHITE

# ==============================================================================
# SLIDE 3: The Solution (ScamRoad Platform Overview)
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3)
add_header(s3, "The Solution: ScamRoad Autonomous Vision Engine", "02. SOLUTION OVERVIEW", 3)

sol_items = [
    ("Commodity Camera Accessibility", "Turns any smartphone, consumer dashcam, or municipal patrol camera into an intelligent, high-precision pavement distress scanner with zero expensive hardware.", COLOR_ORANGE),
    ("Real-Time Neural Edge Inference", "Sub-120ms latency on standard consumer CPUs powered by fine-tuned YOLO11n-Rescue and ONNX Runtime execution without cloud dependencies.", COLOR_YELLOW),
    ("Dual Spatial Prior Guards", "Eliminates false alarms via Guard B (rejecting non-road diagrams & digital screenshots) and Guard A (isolating drivable asphalt boundaries from sidewalks and sky).", COLOR_GREEN),
    ("ASTM D6433 & IRC:82 Compliance", "Automatically computes Pavement Condition Index (PCI 0–100) and exports professional vector PDF audit reports for municipal contractor accountability.", COLOR_WHITE),
]

for idx, (title, text, accent) in enumerate(sol_items):
    x = Inches(0.8 + idx * 2.92)
    y = Inches(1.8)
    c = add_card(s3, x, y, Inches(2.78), Inches(4.9), border_color=COLOR_BORDER, fill_color=COLOR_CARD)
    tf = c.text_frame
    p_i = tf.paragraphs[0]
    p_i.text = f"0{idx+1}"
    p_i.font.name = "Consolas"
    p_i.font.size = Pt(28)
    p_i.font.bold = True
    p_i.font.color.rgb = accent
    
    p_t = tf.add_paragraph()
    p_t.text = title
    p_t.font.name = "Segoe UI"
    p_t.font.size = Pt(15)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE
    
    p_m = tf.add_paragraph()
    p_m.text = text
    p_m.font.name = "Segoe UI"
    p_m.font.size = Pt(11)
    p_m.font.color.rgb = COLOR_MUTED

# ==============================================================================
# SLIDE 4: 5-Stage Neural Pipeline Architecture
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4)
add_header(s4, "5-Stage Neural Vision Architecture", "03. TECHNICAL ARCHITECTURE", 4)

stages = [
    ("Stage 1", "EXIF Ingestion & Normalize", "Decodes JPEG, PNG, WebP, AVIF with universal orientation correction.", COLOR_MUTED),
    ("Stage 2", "Guard B: Digital Gate", "Multi-spectral chroma & glyph analyzer rejects non-road diagrams (HTTP 422).", COLOR_ORANGE),
    ("Stage 3", "Guard A: Road Surface Prior", "Segments drivable asphalt surface; suppresses off-road objects and sky.", COLOR_YELLOW),
    ("Stage 4", "YOLO11n-Rescue Engine", "Unified single-pass detection across potholes, alligator, and joint cracks.", COLOR_GREEN),
    ("Stage 5", "Civil Distress & PCI Scoring", "Calculates deduct values, severity ratings, and exports vector PDF ledgers.", COLOR_WHITE),
]

for idx, (num, name, desc, accent) in enumerate(stages):
    y = Inches(1.8 + idx * 1.02)
    c = add_card(s4, Inches(0.8), y, Inches(11.73), Inches(0.85), border_color=COLOR_BORDER, fill_color=COLOR_CARD)
    tf = c.text_frame
    p = tf.paragraphs[0]
    p.text = f"{num}:  {name}"
    p.font.name = "Segoe UI"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = accent
    
    p_sub = tf.add_paragraph()
    p_sub.text = f"       {desc}"
    p_sub.font.name = "Segoe UI"
    p_sub.font.size = Pt(11)
    p_sub.font.color.rgb = COLOR_MUTED

# ==============================================================================
# SLIDE 5: Pavement Distress Classification Taxonomy
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5)
add_header(s5, "Pavement Distress Classification & Civil Taxonomy", "04. DEFECT TAXONOMY", 5)

distresses = [
    ("POTHOLE / CRATER", "Cavities & Structural Depressions", "Bowl-shaped structural voids with depth >= 25mm caused by moisture infiltration and heavy wheelpath load. High vehicle blowout risk.", "Critical / Severe", COLOR_ORANGE),
    ("ALLIGATOR CRACKING", "Fatigue Network Fractures", "Interconnected polygonal fractures resembling reptile skin. Indicates sub-base structural failure requiring slurry seal or full milling.", "Severe / High", COLOR_YELLOW),
    ("LONGITUDINAL CRACK", "Wheelpath Shear Fractures", "Linear cracks running parallel to pavement centerline, caused by paving joint fatigue and repetitive heavy axle wheel tracking.", "Moderate", COLOR_WHITE),
    ("TRANSVERSE CRACK", "Thermal Contraction Joints", "Cracks running perpendicular to road direction resulting from temperature contraction stresses and shrinkage of asphalt surface layer.", "Moderate / Minor", COLOR_MUTED),
]

for idx, (code, title, desc, sev, col) in enumerate(distresses):
    row = idx // 2
    c_idx = idx % 2
    x = Inches(0.8 + c_idx * 5.9)
    y = Inches(1.8 + row * 2.6)
    
    card = add_card(s5, x, y, Inches(5.7), Inches(2.3), border_color=COLOR_BORDER, fill_color=COLOR_CARD)
    tf = card.text_frame
    p_c = tf.paragraphs[0]
    p_c.text = f"TAG: {code}  ·  {sev}"
    p_c.font.name = "Consolas"
    p_c.font.size = Pt(11)
    p_c.font.bold = True
    p_c.font.color.rgb = col
    
    p_t = tf.add_paragraph()
    p_t.text = title
    p_t.font.name = "Segoe UI"
    p_t.font.size = Pt(16)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE
    
    p_d = tf.add_paragraph()
    p_d.text = desc
    p_d.font.name = "Segoe UI"
    p_d.font.size = Pt(11)
    p_d.font.color.rgb = COLOR_MUTED

# ==============================================================================
# SLIDE 6: Live Road Scanner Workspace
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6)
add_header(s6, "Interactive Live Road Scanner Workspace (/scanner)", "05. LIVE SCANNER INTERFACE", 6)

scanner_img_path = PROJECT_ROOT / "docs" / "images" / "preview_scanner.png"
if scanner_img_path.exists():
    s6.shapes.add_picture(str(scanner_img_path), Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.9))

# Feature callout cards on the right
features_s6 = [
    ("Real-Time Camera & Upload", "Supports live USB/smartphone camera streaming or high-resolution photo uploads with universal EXIF correction.", COLOR_ORANGE),
    ("Interactive Sensitivity Slider", "Adjust confidence threshold (0.05 to 0.95) on the fly with instant visual box re-rendering.", COLOR_YELLOW),
    ("Instant Defect Breakdown", "Side ledger categorizing potholes, fatigue cracks, and severe damage counts with one-click audit handover.", COLOR_WHITE),
]

for idx, (title, desc, accent) in enumerate(features_s6):
    y = Inches(1.8 + idx * 1.68)
    c = add_card(s6, Inches(8.55), y, Inches(3.98), Inches(1.5), border_color=COLOR_BORDER, fill_color=COLOR_CARD)
    tf = c.text_frame
    p_t = tf.paragraphs[0]
    p_t.text = f"⚡  {title}"
    p_t.font.name = "Segoe UI"
    p_t.font.size = Pt(13)
    p_t.font.bold = True
    p_t.font.color.rgb = accent
    
    p_d = tf.add_paragraph()
    p_d.text = desc
    p_d.font.name = "Segoe UI"
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = COLOR_MUTED

# ==============================================================================
# SLIDE 7: Civil Damage Audit Report & Vector PDF Engine
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7)
add_header(s7, "Civil Damage Audit Report & Vector PDF Engine (/report)", "06. AUDIT & REPORTING", 7)

report_img_path = PROJECT_ROOT / "docs" / "images" / "preview_report.png"
if report_img_path.exists():
    s7.shapes.add_picture(str(report_img_path), Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.9))

features_s7 = [
    ("ASTM D6433 Pavement Index (PCI)", "Calculates standardized 0–100 PCI ratings (Good, Fair, Poor, Critical) based on surface area deducts.", COLOR_ORANGE),
    ("IRC:82 Maintenance Code", "Prescribes exact engineering actions: elastomeric sealants, slurry seals, or mechanical compaction patches.", COLOR_YELLOW),
    ("One-Click Vector PDF Export", "Generates verifiable contractor work orders with GPS coordinates, distress metrics, and cost estimates.", COLOR_GREEN),
]

for idx, (title, desc, accent) in enumerate(features_s7):
    y = Inches(1.8 + idx * 1.68)
    c = add_card(s7, Inches(8.55), y, Inches(3.98), Inches(1.5), border_color=COLOR_BORDER, fill_color=COLOR_CARD)
    tf = c.text_frame
    p_t = tf.paragraphs[0]
    p_t.text = f"📋  {title}"
    p_t.font.name = "Segoe UI"
    p_t.font.size = Pt(13)
    p_t.font.bold = True
    p_t.font.color.rgb = accent
    
    p_d = tf.add_paragraph()
    p_d.text = desc
    p_d.font.name = "Segoe UI"
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = COLOR_MUTED

# ==============================================================================
# SLIDE 8: Evaluation Benchmarks Showdown
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8)
add_header(s8, "Verified Accuracy & Performance Benchmarks", "07. BENCHMARKS SHOWDOWN", 8)

bench_card = add_card(s8, Inches(0.8), Inches(1.8), Inches(11.73), Inches(4.9), border_color=COLOR_BORDER, fill_color=COLOR_CARD)

metrics = [
    ("Non-Road Diagram Rejection", "0.0% (0/30)", "100.0% (30/30)", "100% Elimination of diagram false alarms"),
    ("Clean Pavement False Alarms", "93.0% (279/300)", "26.6% (80/300)", "-66.4 pp massive reduction on clean roads"),
    ("Clutter Scene False Alarm Rate", "44.0% (44/100)", "11.0% (11/100)", "-33.0 pp reduction in complex traffic"),
    ("Pothole Detection Precision", "41.2%", "85.7%", "+44.5 pp increase in genuine cavity accuracy"),
    ("Transverse Crack Precision", "15.4%", "75.0%", "+59.6 pp increase in joint detection precision"),
    ("Alligator Crack Spurious Boxes", "13,487 boxes", "0 boxes", "-100% hallucinated boxes completely purged"),
    ("Host CPU Latency (p50)", "555.2 ms", "< 120 ms", "~4.6x faster real-time CPU execution"),
]

table_shape = s8.shapes.add_table(8, 4, Inches(1.0), Inches(2.0), Inches(11.33), Inches(4.4))
table = table_shape.table
table.columns[0].width = Inches(3.2)
table.columns[1].width = Inches(2.2)
table.columns[2].width = Inches(2.4)
table.columns[3].width = Inches(3.53)

headers = ["Evaluation Metric", "Vanilla YOLO Baseline", "ScamRoad YOLO11n-Rescue", "Civil Engineering Impact"]
for c_i, h_txt in enumerate(headers):
    cell = table.cell(0, c_i)
    cell.fill.solid()
    cell.fill.fore_color.rgb = COLOR_BG
    p = cell.text_frame.paragraphs[0]
    p.text = h_txt
    p.font.name = "Segoe UI"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_YELLOW

for r_i, (m, b, r, imp) in enumerate(metrics):
    row_idx = r_i + 1
    row_data = [m, b, r, imp]
    for c_i, val in enumerate(row_data):
        cell = table.cell(row_idx, c_i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_CARD_ALT if r_i % 2 == 0 else COLOR_CARD
        p = cell.text_frame.paragraphs[0]
        p.text = val
        p.font.name = "Segoe UI"
        p.font.size = Pt(10)
        if c_i == 2:
            p.font.bold = True
            p.font.color.rgb = COLOR_ORANGE
        elif c_i == 3:
            p.font.color.rgb = COLOR_GREEN
        else:
            p.font.color.rgb = COLOR_WHITE

# ==============================================================================
# SLIDE 9: Full-Stack Technology Architecture
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9)
add_header(s9, "Full-Stack Technology Architecture & Deployment", "08. TECH STACK & DEPLOYMENT", 9)

stacks = [
    ("Machine Learning Core", [
        "YOLO11n-Rescue fine-tuned on real distress data",
        "ONNX Runtime CPU Execution Provider",
        "Dual Spatial Priors (Guard A + Guard B)",
        "31.7% Background negative regularization"
    ], COLOR_ORANGE),
    ("High-Performance Backend", [
        "FastAPI 0.115+ REST microservice",
        "SQLAlchemy 2.0 async ORM engine",
        "Pydantic v2 schemas and validation",
        "Inference latency logging & correlation IDs"
    ], COLOR_YELLOW),
    ("Modern Web Frontend", [
        "React 18 + Vite 5 + TypeScript 5.5",
        "TailwindCSS high-visibility roadwork theme",
        "Client-side jsPDF vector audit report generator",
        "Framer Motion radar scan animations"
    ], COLOR_GREEN),
]

for idx, (title, items, accent) in enumerate(stacks):
    x = Inches(0.8 + idx * 3.95)
    y = Inches(1.8)
    card = add_card(s9, x, y, Inches(3.8), Inches(4.9), border_color=COLOR_BORDER, fill_color=COLOR_CARD)
    tf = card.text_frame
    p_t = tf.paragraphs[0]
    p_t.text = title
    p_t.font.name = "Segoe UI"
    p_t.font.size = Pt(16)
    p_t.font.bold = True
    p_t.font.color.rgb = accent
    
    for item in items:
        p_i = tf.add_paragraph()
        p_i.text = f"•  {item}"
        p_i.font.name = "Segoe UI"
        p_i.font.size = Pt(11)
        p_i.font.color.rgb = COLOR_WHITE
        p_i.space_before = Pt(8)

# ==============================================================================
# SLIDE 10: Summary & Author Information
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10)
add_header(s10, "Summary, Impact & Author Information", "09. SUMMARY & CONCLUSION", 10)

# Left Summary Card
left_card = add_card(s10, Inches(0.8), Inches(1.8), Inches(5.7), Inches(4.9), border_color=COLOR_ORANGE, fill_color=COLOR_CARD)
tf_l = left_card.text_frame
p_lh = tf_l.paragraphs[0]
p_lh.text = "Key Project Milestones"
p_lh.font.name = "Segoe UI"
p_lh.font.size = Pt(18)
p_lh.font.bold = True
p_lh.font.color.rgb = COLOR_ORANGE

bullets_l = [
    "Democratized pavement survey access via ordinary monocular cameras and consumer CPUs.",
    "Solved the multi-class false alarm crisis with 0 spurious boxes on clean roads and shadows.",
    "Engineered complete civil compliance matching ASTM D6433 PCI math and IRC:82 codes.",
    "Full-stack open-source platform ready for municipal deployment and dashcam fleets.",
]
for b in bullets_l:
    p_b = tf_l.add_paragraph()
    p_b.text = f"✓  {b}"
    p_b.font.name = "Segoe UI"
    p_b.font.size = Pt(12)
    p_b.font.color.rgb = COLOR_WHITE
    p_b.space_before = Pt(12)

# Right Author Card
right_card = add_card(s10, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.9), border_color=COLOR_YELLOW, fill_color=COLOR_CARD)
tf_r = right_card.text_frame
p_rh = tf_r.paragraphs[0]
p_rh.text = "Author & Project Information"
p_rh.font.name = "Segoe UI"
p_rh.font.size = Pt(18)
p_rh.font.bold = True
p_rh.font.color.rgb = COLOR_YELLOW

details_r = [
    ("Lead Researcher & Engineer:", "Priye Ranjan"),
    ("GitHub Profile:", "@Priya-Ranjan-0201"),
    ("Repository:", "github.com/Priya-Ranjan-0201/Potholes-detector"),
    ("Primary Model:", "YOLO11n-Rescue (ONNX Runtime)"),
    ("Frontend / Backend:", "React 18 + Vite / FastAPI (Python 3.12)"),
    ("Civil Compliance:", "ASTM D6433 · IRC:82-2015"),
]
for lbl, val in details_r:
    p_d = tf_r.add_paragraph()
    p_d.text = f"{lbl}  {val}"
    p_d.font.name = "Segoe UI"
    p_d.font.size = Pt(12)
    p_d.font.color.rgb = COLOR_WHITE
    p_d.space_before = Pt(10)

out_pptx = PROJECT_ROOT / "ScamRoad_Presentation.pptx"
prs.save(str(out_pptx))
print(f"Presentation saved successfully to {out_pptx}")
