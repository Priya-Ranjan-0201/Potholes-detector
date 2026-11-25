"""Generate ScamRoad 12-slide Class Presentation (.pptx).
Designed with simple, clear, punchy, human-crafted content:
- Clean, high-contrast light background (perfect for classroom projectors)
- Authoritative deep navy and warm civil-engineering amber accents
- Concise, easy-to-read bullet points without heavy jargon
- Direct project facts, authentic screenshots, and honest engineering findings
"""

from __future__ import annotations

import os
from pathlib import Path
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

PROJECT_ROOT = Path(__file__).resolve().parent

# --- Prepare Clean Cropped Preview Images ---
img_dir = PROJECT_ROOT / "docs" / "images"
p_scan = img_dir / "preview_scanner.png"
p_rep = img_dir / "preview_report.png"
clean_scan_path = img_dir / "preview_scanner_clean.png"
clean_rep_path = img_dir / "preview_report_clean.png"

if p_scan.exists():
    img_scan = Image.open(p_scan)
    clean_scan = img_scan.crop((168, 130, 1992, 1280))
    clean_scan.save(clean_scan_path)

if p_rep.exists():
    img_rep = Image.open(p_rep)
    clean_rep = img_rep.crop((168, 130, 1992, 1280))
    clean_rep.save(clean_rep_path)

# --- Professional Academic & Civil Engineering Palette ---
COLOR_BG = RGBColor(248, 250, 252)          # #F8FAFC Soft Pearl Canvas (Projector Legibility)
COLOR_CARD = RGBColor(255, 255, 255)        # #FFFFFF Pure Crisp White Surface
COLOR_CARD_MUTED = RGBColor(241, 245, 249)  # #F1F5F9 Soft Tint Slate Surface
COLOR_BORDER = RGBColor(226, 232, 240)      # #E2E8F0 Subtle Clean Border
COLOR_BORDER_STRONG = RGBColor(203, 213, 225) # #CBD5E1 Visible Card Border

COLOR_NAVY = RGBColor(15, 41, 66)           # #0F2942 Deep Navy Slate (Primary Heading)
COLOR_ROYAL = RGBColor(30, 64, 175)         # #1E40AF Classic Academic Blue
COLOR_AMBER = RGBColor(217, 119, 6)         # #D97706 Warm Road Safety Amber
COLOR_EMERALD = RGBColor(5, 150, 105)       # #059669 Forest Emerald Success
COLOR_CRIMSON = RGBColor(220, 38, 38)       # #DC2626 Hazard Crimson Red
COLOR_PURPLE = RGBColor(109, 40, 217)       # #6D28D9 Royal Purple Accent

COLOR_TEXT_MAIN = RGBColor(15, 23, 42)      # #0F172A Deep Charcoal (Ultra-readable)
COLOR_TEXT_BODY = RGBColor(51, 65, 85)      # #334155 Slate Grey Body
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)  # #64748B Supporting Metadata

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]


def set_slide_background(slide, color=COLOR_BG):
    """Fills slide background with crisp, projector-friendly light canvas."""
    bg_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5)
    )
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = color
    bg_shape.line.fill.background()
    return bg_shape


def add_header(slide, title_text, category_text, slide_num=None, total_slides=12):
    """Creates a clean, human-designed academic header bar."""
    top_bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.08)
    )
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = COLOR_ROYAL
    top_bar.line.fill.background()

    # Category label
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(8.5), Inches(0.32))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    tf_cat.margin_left = tf_cat.margin_right = tf_cat.margin_top = tf_cat.margin_bottom = 0
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.name = "Segoe UI"
    p_cat.font.size = Pt(10.5)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_AMBER

    # Slide Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(10.5), Inches(0.65))
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.name = "Segoe UI"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    # Slide Number
    if slide_num:
        num_box = slide.shapes.add_textbox(Inches(11.333), Inches(0.38), Inches(1.2), Inches(0.35))
        tf_num = num_box.text_frame
        tf_num.margin_left = tf_num.margin_right = tf_num.margin_top = tf_num.margin_bottom = 0
        p_num = tf_num.paragraphs[0]
        p_num.alignment = PP_ALIGN.RIGHT
        p_num.text = f"{slide_num:02d} / {total_slides:02d}"
        p_num.font.name = "Segoe UI"
        p_num.font.size = Pt(11)
        p_num.font.bold = True
        p_num.font.color.rgb = COLOR_TEXT_MUTED


def add_card(
    slide,
    left,
    top,
    width,
    height,
    border_color=COLOR_BORDER,
    fill_color=COLOR_CARD,
    border_width=1.0,
):
    """Adds a clean white rounded card with soft borders for clear readability."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = fill_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(border_width)
    else:
        card.line.fill.background()

    tf = card.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_top = Inches(0.22)
    tf.margin_bottom = Inches(0.22)
    tf.margin_left = Inches(0.25)
    tf.margin_right = Inches(0.25)
    return card


def add_para(tf, text, font_size=11, bold=False, color=COLOR_TEXT_BODY, space_before=0, align=PP_ALIGN.LEFT):
    """Helper to add cleanly aligned paragraph to a text frame."""
    if len(tf.paragraphs) == 1 and tf.paragraphs[0].text == "":
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    p.text = text
    p.font.name = "Segoe UI"
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.space_before = Pt(space_before)
    p.alignment = align
    return p


# ==============================================================================
# SLIDE 1: Title & Overview (Clean Academic Cover)
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1)

top_bar_1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
top_bar_1.fill.solid()
top_bar_1.fill.fore_color.rgb = COLOR_ROYAL
top_bar_1.line.fill.background()

# Left Column: Project Identity & Title
title_card = add_card(s1, Inches(0.8), Inches(1.1), Inches(7.4), Inches(4.3), border_color=COLOR_BORDER_STRONG, fill_color=COLOR_CARD)
tf1 = title_card.text_frame

add_para(tf1, "COMPUTER VISION & CIVIL INFRASTRUCTURE PROJECT", 11, bold=True, color=COLOR_AMBER)
add_para(tf1, "ScamRoad", 46, bold=True, color=COLOR_NAVY, space_before=4)
add_para(tf1, "AI-Powered Road Defect Detection & Civil Audit System", 17, bold=True, color=COLOR_ROYAL, space_before=2)
add_para(tf1, "A real-time computer vision system that detects road hazards (potholes and cracks) from everyday smartphone cameras and automatically generates standardized civil engineering audit reports.", 11.5, color=COLOR_TEXT_BODY, space_before=12)

# Right Column: Highlights Card
hl_card = add_card(s1, Inches(8.45), Inches(1.1), Inches(4.08), Inches(4.3), border_color=COLOR_ROYAL, fill_color=COLOR_CARD_MUTED, border_width=1.5)
htf = hl_card.text_frame
add_para(htf, "KEY PROJECT HIGHLIGHTS", 12, bold=True, color=COLOR_NAVY)

highlights = [
    ("⚡ Real-Time CPU Processing", "Runs under 65ms per frame on standard laptops (no GPU needed).", COLOR_ROYAL),
    ("🎯 Accurate Pothole Detection", "92.3% validation precision on authentic Indian road conditions.", COLOR_EMERALD),
    ("🛡️ Zero Clean Road False Alarms", "Eliminated border ghost boxes; 0% false positives on clean asphalt.", COLOR_AMBER),
    ("📋 Automated Civil Audit", "Generates ASTM D6433 road health scores and downloadable PDF reports.", COLOR_NAVY),
]
for h_title, h_desc, h_col in highlights:
    add_para(htf, h_title, 11.5, bold=True, color=h_col, space_before=8)
    add_para(htf, h_desc, 9.5, color=COLOR_TEXT_BODY)

# Bottom Author & Metadata Banner
auth_card = add_card(s1, Inches(0.8), Inches(5.65), Inches(11.73), Inches(1.3), border_color=COLOR_BORDER, fill_color=COLOR_CARD)
tf_a = auth_card.text_frame
add_para(tf_a, "Presented by: Priye Ranjan  (@Priya-Ranjan-0201)", 14, bold=True, color=COLOR_NAVY)
add_para(tf_a, "Topic: Computer Vision, Real-Time Edge AI & Smart Public Infrastructure", 10.5, color=COLOR_TEXT_BODY, space_before=3)
add_para(tf_a, "Open-Source Project: github.com/Priya-Ranjan-0201/Potholes-detector  ·  FastAPI + React + YOLO11 (ONNX)", 9.5, color=COLOR_TEXT_MUTED, space_before=2)


# ==============================================================================
# SLIDE 2: Problem Statement
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2)
add_header(s2, "Problem Statement: Why Road Distress is a Major Crisis", "01. Problem Statement", 2, 12)

# Left Card: The Human & Economic Impact
left_s2 = add_card(s2, Inches(0.8), Inches(1.6), Inches(5.7), Inches(4.35), border_color=COLOR_CRIMSON, fill_color=COLOR_CARD, border_width=1.5)
tf_ls2 = left_s2.text_frame
add_para(tf_ls2, "THE REAL-WORLD PROBLEM", 11, bold=True, color=COLOR_CRIMSON)
add_para(tf_ls2, "Public Safety & Financial Drain", 16, bold=True, color=COLOR_NAVY, space_before=3)

impact_items = [
    ("Over 3,500+ Deaths Annually", "Sudden potholes and depressions cause fatal road accidents and two-wheeler crashes every year."),
    ("Heavy Public Fund Wastage (₹15,000+ Cr)", "Billions are spent on substandard bitumen repairs that wash away during the very first monsoon."),
    ("Severe Vehicle Wear & Traffic Jams", "Rough roads cause tire blowouts, broken suspensions, and severe commercial transit delays."),
]
for title, desc in impact_items:
    add_para(tf_ls2, f"• {title}:", 11, bold=True, color=COLOR_CRIMSON, space_before=8)
    add_para(tf_ls2, f"   {desc}", 10, color=COLOR_TEXT_BODY)

# Right Card: Why Manual Audits Fail
right_s2 = add_card(s2, Inches(6.83), Inches(1.6), Inches(5.7), Inches(4.35), border_color=COLOR_AMBER, fill_color=COLOR_CARD, border_width=1.5)
tf_rs2 = right_s2.text_frame
add_para(tf_rs2, "LIMITATIONS OF CURRENT METHODS", 11, bold=True, color=COLOR_AMBER)
add_para(tf_rs2, "Why Traditional Inspections Fail", 16, bold=True, color=COLOR_NAVY, space_before=3)

limit_items = [
    ("Slow Manual Surveys", "Paper clipboard inspections take weeks or months; minor cracks turn into deep craters before repairs start."),
    ("Expensive Equipment (₹80+ Lakhs)", "Laser survey vans and LiDAR trucks are too expensive for 98% of municipal and rural budgets."),
    ("Subjective & Unverified", "Manual grading relies on individual human opinion, leading to disputed repairs and unchecked 'ghost repairs'."),
]
for title, desc in limit_items:
    add_para(tf_rs2, f"• {title}:", 11, bold=True, color=COLOR_AMBER, space_before=8)
    add_para(tf_rs2, f"   {desc}", 10, color=COLOR_TEXT_BODY)

# Bottom Summary Banner
b_s2 = add_card(s2, Inches(0.8), Inches(6.15), Inches(11.73), Inches(0.85), border_color=COLOR_BORDER, fill_color=COLOR_CARD_MUTED)
stf2 = b_s2.text_frame
add_para(stf2, "💡 The Project Mission: Use computer vision and ordinary cameras (smartphones, dashcams) to make road inspection fast, automated, affordable, and tamper-proof.", 11.5, bold=True, color=COLOR_NAVY)


# ==============================================================================
# SLIDE 3: System Overview (The 3 Core Pillars)
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3)
add_header(s3, "System Overview: How ScamRoad Works End-to-End", "02. System Architecture", 3, 12)

pillars = [
    ("1. CAMERA DATA INGESTION", "Everyday Mobile Input", [
        ("Smartphone & Dashcam Video", "Upload road photos or recorded video directly from consumer devices."),
        ("Automatic GPS Extraction", "Extracts latitude and longitude coordinates from image metadata (EXIF)."),
        ("Citizen Privacy Protection", "Automatically blurs vehicle number plates and human faces."),
        ("Universal File Support", "Seamlessly decodes JPEG, PNG, WebP, and AVIF formats.")
    ], "Zero expensive hardware needed; accessible to all citizens.", COLOR_ROYAL),
    ("2. COMPUTER VISION CORE", "5-Stage Edge AI Pipeline", [
        ("Input Validation Gate", "Instantly rejects screenshots, indoor photos, and textbook diagrams."),
        ("Road Horizon Masking", "Focuses on the pavement and ignores sky, trees, and buildings."),
        ("YOLO11 Feature Extraction", "Processes images in <65ms on standard laptops without a GPU."),
        ("Perimeter Filter", "Suppresses false-positive margin boxes hugging image borders.")
    ], "High accuracy with zero false alarms on clean asphalt.", COLOR_AMBER),
    ("3. CIVIL AUDIT & GOVERNANCE", "Actionable Municipal Reports", [
        ("Automated Work Orders", "Maps detected road damage to official IRC:82 maintenance codes."),
        ("ASTM D6433 Road Rating", "Calculates standard Pavement Condition Index (PCI: 0 to 100)."),
        ("Vector PDF Report Export", "Generates formal multi-page engineering reports with damage photos."),
        ("Before-and-After Verification", "Compares contractor photos against original damage to confirm repairs.")
    ], "Transparent municipal accountability and verified repairs.", COLOR_EMERALD),
]

p_x = Inches(0.8)
for p_tag, p_head, p_items, p_foot, p_col in pillars:
    pc = add_card(s3, p_x, Inches(1.6), Inches(3.75), Inches(4.35), border_color=p_col, fill_color=COLOR_CARD, border_width=1.5)
    ptf = pc.text_frame

    add_para(ptf, p_tag, 11, bold=True, color=p_col)
    add_para(ptf, p_head, 15, bold=True, color=COLOR_NAVY, space_before=3)

    for item_title, item_desc in p_items:
        add_para(ptf, f"• {item_title}:", 10, bold=True, color=COLOR_NAVY, space_before=5)
        add_para(ptf, f"   {item_desc}", 9, color=COLOR_TEXT_BODY)

    add_para(ptf, f"✓ {p_foot}", 9.5, bold=True, color=p_col, space_before=10)
    p_x += Inches(3.99)

b_strip3 = add_card(s3, Inches(0.8), Inches(6.15), Inches(11.73), Inches(0.85), border_color=COLOR_BORDER, fill_color=COLOR_CARD_MUTED)
st3 = b_strip3.text_frame
add_para(st3, "💡 Complete Closed Loop: A single road photo automatically triggers AI defect detection, civil severity scoring, and a verifiable contractor work order.", 11.5, bold=True, color=COLOR_NAVY)


# ==============================================================================
# SLIDE 4: Computer Vision Pipeline (5 Steps)
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4)
add_header(s4, "Under the Hood: 5 Steps of the Detection Pipeline", "03. Computer Vision Pipeline", 4, 12)

stages = [
    ("Step 1", "Input Validation Gate", "Checks if the input is a real road photo. Instantly blocks screenshots, diagrams, and indoor images.", "100% SPECIFICITY", COLOR_ROYAL),
    ("Step 2", "Road Surface Segmentation", "Isolates the bitumen road surface and masks out irrelevant background (sky, trees, oncoming cars).", "HORIZON MASK", COLOR_ROYAL),
    ("Step 3", "YOLO11 Feature Extraction", "Scans the road at 640×640 resolution to detect defect bounding boxes in under 65ms on simple CPU.", "FAST CPU INFERENCE", COLOR_AMBER),
    ("Step 4", "Perimeter Edge Filtering", "Removes false-positive boxes that hug the image borders, eliminating phantom edge glitches.", "ELIMINATES GHOST BOXES", COLOR_AMBER),
    ("Step 5", "Confidence Calibration & NMS", "Merges overlapping boxes and applies sensitivity modes: Balanced (0.30), High Precision, and High Recall.", "CALIBRATED OUTPUT", COLOR_EMERALD),
]

stg_y = Inches(1.55)
for s_num, s_title, s_desc, s_badge, s_color in stages:
    row_card = add_card(s4, Inches(0.8), stg_y, Inches(11.73), Inches(0.98), border_color=s_color, fill_color=COLOR_CARD)
    rtf = row_card.text_frame

    add_para(rtf, f"{s_num}: {s_title}    [{s_badge}]", 12.5, bold=True, color=s_color)
    add_para(rtf, s_desc, 10.5, color=COLOR_TEXT_BODY, space_before=3)

    stg_y += Inches(1.08)


# ==============================================================================
# SLIDE 5: Road Distress Types & Severity Standards
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5)
add_header(s5, "Road Distress Types & Severity Standards (ASTM D6433)", "04. Defect Taxonomy", 5, 12)

classes_data = [
    ("POTHOLE", "Cavity Hazard", [
        ("Description", "Bowl-shaped cavity with steep vertical edges."),
        ("Root Cause", "Water seepage and repeated heavy traffic impacts."),
        ("Safety Risk", "High hazard for two-wheelers and tire punctures."),
        ("Standard Repair", "Rapid compaction bitumen mastic."),
        ("Severity Code", "ASTM D6433-P / IRC:82")
    ], COLOR_AMBER),
    ("LONGITUDINAL CRACK", "Fatigue Seam", [
        ("Description", "Crack running parallel to the road centerline."),
        ("Root Cause", "Paving joint failure or heavy traffic wheel paths."),
        ("Safety Risk", "Allows rain water into lower road base."),
        ("Standard Repair", "Hot-pour rubberized bitumen sealant."),
        ("Severity Code", "ASTM D6433-LC / IRC:82")
    ], COLOR_ROYAL),
    ("TRANSVERSE CRACK", "Thermal Fracture", [
        ("Description", "Crack running across the road width."),
        ("Root Cause", "Temperature shrinkage cycles and ground shifts."),
        ("Safety Risk", "Creates noticeable bumps and weakens pavement."),
        ("Standard Repair", "Joint routing and elastomeric crack sealing."),
        ("Severity Code", "ASTM D6433-TC / IRC:82")
    ], COLOR_PURPLE),
    ("ALLIGATOR CRACK", "Structural Failure", [
        ("Description", "Interconnected web cracking resembling reptile skin."),
        ("Root Cause", "Complete failure of the underlying road foundation."),
        ("Safety Risk", "Rapidly collapses into widespread potholes under rain."),
        ("Standard Repair", "Full-depth asphalt milling and repaving."),
        ("Severity Code", "ASTM D6433-AC / IRC:82")
    ], COLOR_CRIMSON),
]

cls_x = Inches(0.8)
for c_name, c_sub, c_details, c_col in classes_data:
    cc = add_card(s5, cls_x, Inches(1.6), Inches(2.78), Inches(4.35), border_color=c_col, fill_color=COLOR_CARD, border_width=1.5)
    ctf = cc.text_frame

    add_para(ctf, c_name, 12.5, bold=True, color=c_col)
    add_para(ctf, c_sub, 10, bold=True, color=COLOR_NAVY, space_before=2)

    for d_lbl, d_val in c_details:
        add_para(ctf, f"• {d_lbl}:", 9.5, bold=True, color=COLOR_NAVY, space_before=4)
        add_para(ctf, f"   {d_val}", 9, color=COLOR_TEXT_BODY)

    cls_x += Inches(2.99)

# Severity Formula Banner
sev_banner = add_card(s5, Inches(0.8), Inches(6.15), Inches(11.73), Inches(0.85), border_color=COLOR_BORDER, fill_color=COLOR_CARD_MUTED)
stf5 = sev_banner.text_frame
add_para(stf5, "📐 Standard Civil Metric: Pavement Condition Index (PCI = 100 - ∑ Deduct Values) graded from 100 (Good) to 0 (Failed) based on defect size, depth, and wheel-path position.", 10.5, bold=True, color=COLOR_NAVY)


# ==============================================================================
# SLIDE 6: Live Road Scanner Interface
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6)
add_header(s6, "Real-Time Road Scanner Interface (/scanner)", "05. Live Scanner Interface", 6, 12)

# Left: Cropped Live Scanner Interface
if clean_scan_path.exists():
    s6.shapes.add_picture(str(clean_scan_path), Inches(0.8), Inches(1.6), width=Inches(6.8), height=Inches(5.2))
else:
    dummy_sc = add_card(s6, Inches(0.8), Inches(1.6), Inches(6.8), Inches(5.2), border_color=COLOR_BORDER, fill_color=COLOR_CARD)

# Right: Feature Highlights
feat_card = add_card(s6, Inches(7.8), Inches(1.6), Inches(4.73), Inches(5.2), border_color=COLOR_BORDER_STRONG, fill_color=COLOR_CARD)
ftf = feat_card.text_frame

add_para(ftf, "REAL-TIME SCANNER FEATURES", 11, bold=True, color=COLOR_AMBER)
add_para(ftf, "Computer Vision in Action", 16, bold=True, color=COLOR_NAVY, space_before=3)

feats = [
    ("Visual Bounding Boxes", "Overlays colored boxes with confidence percentage and severity tags."),
    ("Accurate Polygon Contours", "Draws precise outlines around defects to measure exact surface area."),
    ("Adjustable Presets", "Instant toggle between Balanced (0.30), High Precision, and High Recall."),
    ("Wheel-Path Warning", "Flags defects located directly in vehicle tire tracks where impact is highest."),
    ("Fast CPU Performance", "Runs at 15+ frames per second on standard laptops with no GPU required.")
]
for f_title, f_sub in feats:
    add_para(ftf, f"• {f_title}:", 10.5, bold=True, color=COLOR_NAVY, space_before=7)
    add_para(ftf, f"   {f_sub}", 9.5, color=COLOR_TEXT_BODY)


# ==============================================================================
# SLIDE 7: Civil Damage Audit Report & Vector PDF Engine
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7)
add_header(s7, "Automated Civil Damage Audit Reports (/report)", "06. Audit & Reporting", 7, 12)

# Left: Cropped Report Screenshot
if clean_rep_path.exists():
    s7.shapes.add_picture(str(clean_rep_path), Inches(0.8), Inches(1.6), width=Inches(6.8), height=Inches(5.2))
else:
    dummy_rep = add_card(s7, Inches(0.8), Inches(1.6), Inches(6.8), Inches(5.2), border_color=COLOR_BORDER, fill_color=COLOR_CARD)

# Right: Report Capabilities
rep_card = add_card(s7, Inches(7.8), Inches(1.6), Inches(4.73), Inches(5.2), border_color=COLOR_BORDER_STRONG, fill_color=COLOR_CARD)
rtf7 = rep_card.text_frame

add_para(rtf7, "MUNICIPAL REPORTING FEATURES", 11, bold=True, color=COLOR_EMERALD)
add_para(rtf7, "Standardized Civil Reports", 16, bold=True, color=COLOR_NAVY, space_before=3)

r_feats = [
    ("One-Click Vector PDF Export", "Generates professional engineering audit reports with embedded high-resolution defect photos."),
    ("Cryptographic Hashes", "Every uploaded inspection photo is sealed with a SHA-256 hash to prevent tampering."),
    ("Work Order Tracking", "Follows repair lifecycle from Reported → Assigned → In-Repair → Verified."),
    ("Photometric Verification", "Compares before-and-after photos to confirm completed contractor repairs and stop ghost billing."),
    ("ASTM D6433 Road Health Index", "Quantifies pavement condition index (PCI 0-100) per road corridor for municipal budgeting.")
]
for rf_title, rf_sub in r_feats:
    add_para(rtf7, f"• {rf_title}:", 10.5, bold=True, color=COLOR_NAVY, space_before=7)
    add_para(rtf7, f"   {rf_sub}", 9.5, color=COLOR_TEXT_BODY)


# ==============================================================================
# SLIDE 8: The Engineering Journey: Eliminating False Positives
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8)
add_header(s8, "Model Training & Engineering Fix: Eliminating Glitches", "07. Model Training & Rescue", 8, 12)

# Left Split: The Challenge
left_s8 = add_card(s8, Inches(0.8), Inches(1.6), Inches(5.7), Inches(4.35), border_color=COLOR_CRIMSON, fill_color=COLOR_CARD, border_width=1.5)
tf_ls8 = left_s8.text_frame
add_para(tf_ls8, "THE INITIAL CHALLENGE", 11, bold=True, color=COLOR_CRIMSON)
add_para(tf_ls8, "Border Boxes & False Alarms", 16, bold=True, color=COLOR_NAVY, space_before=3)

b_l8 = [
    ("Border Phantom Boxes", "Corrupt edge weights generated phantom boxes on left and right margins of every image."),
    ("Texture Clutter Glitches", "Faint asphalt gravel variations and shadow borders triggered false positive detections."),
    ("Non-Road Misclassifications", "Sky, trees, and signboards were falsely flagged as alligator cracking."),
    ("Overly Sensitive Thresholds", "Default 0.20 threshold allowed weak neural noise to register as critical road hazards.")
]
for g_title, g_desc in b_l8:
    add_para(tf_ls8, f"• {g_title}:", 11, bold=True, color=COLOR_CRIMSON, space_before=6)
    add_para(tf_ls8, f"   {g_desc}", 9.5, color=COLOR_TEXT_BODY)

# Right Split: The Solution
right_s8 = add_card(s8, Inches(6.83), Inches(1.6), Inches(5.7), Inches(4.35), border_color=COLOR_EMERALD, fill_color=COLOR_CARD, border_width=1.5)
tf_rs8 = right_s8.text_frame
add_para(tf_rs8, "THE ENGINEERING FIX", 11, bold=True, color=COLOR_EMERALD)
add_para(tf_rs8, "Real-World Data & Defensive Code", 16, bold=True, color=COLOR_NAVY, space_before=3)

b_r8 = [
    ("Curated 1,100 Real-World Images", "Assembled 1,100 authentic road images (935 train + 165 val) from RDD2022 India and real road photos."),
    ("150 Clean Road Negative Samples", "Trained the model on clean, undamaged asphalt to teach it zero activations on normal roads."),
    ("Perimeter Edge Exclusion Filter", "Programmatically rejected false boxes that hug image boundaries (x < 3% or x > 97%)."),
    ("Calibrated Presets", "Raised balanced threshold to 0.30 for potholes and 0.32 for cracks to suppress false alarms.")
]
for c_title, c_desc in b_r8:
    add_para(tf_rs8, f"✓ {c_title}:", 11, bold=True, color=COLOR_EMERALD, space_before=6)
    add_para(tf_rs8, f"   {c_desc}", 9.5, color=COLOR_TEXT_BODY)

# Bottom Result Banner
b_s8 = add_card(s8, Inches(0.8), Inches(6.15), Inches(11.73), Inches(0.85), border_color=COLOR_BORDER, fill_color=COLOR_CARD_MUTED)
st8 = b_s8.text_frame
add_para(st8, "✅ Verified Outcome: 0 border phantom boxes across all test images · 0.0% false alarms on clean roads · 92.28% validation precision.", 11.5, bold=True, color=COLOR_NAVY)


# ==============================================================================
# SLIDE 9: Independent Blind Test & Honest Evaluation
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9)
add_header(s9, "Independent Testing Results on 99 Unseen Road Images", "08. Model Evaluation & Insights", 9, 12)

# Left Column: The Benchmark Table
tbl_card = add_card(s9, Inches(0.8), Inches(1.6), Inches(5.7), Inches(4.35), border_color=COLOR_BORDER_STRONG, fill_color=COLOR_CARD)
ttf9 = tbl_card.text_frame

add_para(ttf9, "BLIND TEST ON 99 UNSEEN IMAGES", 11, bold=True, color=COLOR_ROYAL)
add_para(ttf9, "Real-World Benchmark Results", 16, bold=True, color=COLOR_NAVY, space_before=3)

table_rows = [
    ("Clean Highway False Alarm Rate", "0.00% (0 / 20)", "PERFECT", COLOR_EMERALD),
    ("Border Phantom Box Glitches", "0 Occurrences", "ELIMINATED", COLOR_EMERALD),
    ("Real Pothole Confidence", "65% - 87%", "HIGH PRECISION", COLOR_EMERALD),
    ("Non-Road Image Rejection", "100% Rejection", "SAFE", COLOR_EMERALD),
    ("Hairline Crack Recall", "Low at 640x640", "EXPLAINED BELOW", COLOR_CRIMSON),
]
for metric, val, status, col in table_rows:
    add_para(ttf9, f"• {metric}:  {val}  [{status}]", 10.5, color=col, space_before=7)

# Right Column: The Scientific Insight
ins_card = add_card(s9, Inches(6.83), Inches(1.6), Inches(5.7), Inches(4.35), border_color=COLOR_BORDER_STRONG, fill_color=COLOR_CARD)
itf9 = ins_card.text_frame

add_para(itf9, "HONEST SCIENTIFIC EXPLANATION", 11, bold=True, color=COLOR_AMBER)
add_para(itf9, "Why Potholes Work & Cracks are Harder", 16, bold=True, color=COLOR_NAVY, space_before=3)

insights = [
    ("Depth vs. Surface Lines", "Potholes have distinct depth, shadows, and bowl-shaped cavities that neural networks easily identify from any angle."),
    ("Image Downsampling Effect", "Resizing a 1080p photo down to 640×640 compresses a 1-pixel hairline crack below single-pixel size, causing it to blend into asphalt texture."),
    ("The Solution (SAHI Tiling)", "Processing road images in full-resolution 640×640 sliding-window patches preserves thin hairline cracks without downsampling blur.")
]
for i_title, i_body in insights:
    add_para(itf9, f"• {i_title}:", 10.5, bold=True, color=COLOR_NAVY, space_before=7)
    add_para(itf9, f"   {i_body}", 9.5, color=COLOR_TEXT_BODY)

# Bottom Takeaway Banner
b_s9 = add_card(s9, Inches(0.8), Inches(6.15), Inches(11.73), Inches(0.85), border_color=COLOR_BORDER, fill_color=COLOR_CARD_MUTED)
st9 = b_s9.text_frame
add_para(st9, "💡 Key Conclusion: The model is a highly reliable POTHOLE detector; hairline cracks will be resolved using SAHI high-resolution tiling.", 11.5, bold=True, color=COLOR_NAVY)


# ==============================================================================
# SLIDE 10: Technology Stack & Implementation
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10)
add_header(s10, "Technology Stack: Modular Full-Stack Architecture", "09. Implementation Stack", 10, 12)

tech_layers = [
    ("FRONTEND LAYER", "React 19 & TypeScript", [
        ("HTML5 Canvas Rendering", "Real-time bounding box and polygon rendering over video frames."),
        ("Tailwind CSS Dashboard", "Clean, responsive user interface with live control toggles."),
        ("Zustand State Store", "Low-latency state management for streaming feeds and presets."),
        ("Leaflet.js GIS Mapping", "Interactive map showing defect clusters and municipal ward boundaries.")
    ], "Modern responsive web dashboard running in any browser.", COLOR_ROYAL),
    ("BACKEND ENGINE", "FastAPI (Python 3.12)", [
        ("Asynchronous REST API", "High-throughput request handling with background processing queues."),
        ("OpenCV & Pillow Pipeline", "Color conversion, Otsu contour extraction, and EXIF orientation."),
        ("ReportLab PDF Engine", "Automated vector PDF report generation with embedded damage crops."),
        ("SQLite & PostGIS Storage", "Spatial database storing defect coordinates, timestamps, and hashes.")
    ], "Scalable asynchronous REST backend for real-time processing.", COLOR_AMBER),
    ("AI & EDGE INFERENCE", "ONNX Runtime CPU Engine", [
        ("Lightweight Model Graph", "Fine-tuned YOLO11n ONNX graph (10.2 MB) optimized with opset 17."),
        ("Sub-65ms Inference Latency", "Runs at 15+ FPS on standard laptop CPUs without needing GPUs."),
        ("Edge Deployable", "Deployable on low-power edge micro-PCs, drones, and mobile devices."),
        ("Standard Tensor Contract", "Clean [1, 3, 640, 640] input to [1, 8, 8400] output mapping.")
    ], "Runs smoothly on ordinary consumer hardware without GPUs.", COLOR_EMERALD),
]

t_x = Inches(0.8)
for t_layer, t_title, t_items, t_foot, t_col in tech_layers:
    tc = add_card(s10, t_x, Inches(1.6), Inches(3.75), Inches(4.35), border_color=t_col, fill_color=COLOR_CARD, border_width=1.5)
    ttf10 = tc.text_frame

    add_para(ttf10, t_layer, 11, bold=True, color=t_col)
    add_para(ttf10, t_title, 14, bold=True, color=COLOR_NAVY, space_before=3)

    for item_lbl, item_desc in t_items:
        add_para(ttf10, f"• {item_lbl}:", 10, bold=True, color=COLOR_NAVY, space_before=5)
        add_para(ttf10, f"   {item_desc}", 9, color=COLOR_TEXT_BODY)

    add_para(ttf10, f"✓ Role: {t_foot}", 9.5, bold=True, color=t_col, space_before=10)
    t_x += Inches(3.99)

# Bottom Deployment Banner
dep_banner = add_card(s10, Inches(0.8), Inches(6.15), Inches(11.73), Inches(0.85), border_color=COLOR_BORDER, fill_color=COLOR_CARD_MUTED)
dtf = dep_banner.text_frame
add_para(dtf, "🚀 Fully Deployable: Dockerized container architecture, automated healthchecks, and single-click 'run.bat' for local classroom demonstration.", 11.5, bold=True, color=COLOR_NAVY)


# ==============================================================================
# SLIDE 11: Future Scope & Roadmap
# ==============================================================================
s11 = prs.slides.add_slide(blank_layout)
set_slide_background(s11)
add_header(s11, "Future Scope: Advancements & Municipal Scaling", "10. Future Roadmap", 11, 12)

innovations = [
    ("Phase 1: High-Res Slicing", "Detecting Hairline Cracks", [
        ("SAHI Tiling Implementation", "Implement Slicing Aided Hyper Inference across the road surface."),
        ("Zero Downsampling Blur", "Splits 1080p frames into overlapping 640×640 patches."),
        ("Micro-Crack Preservation", "Captures 1-pixel micro-fractures without downscaling loss."),
        ("Target Performance", "Expected to boost crack detection recall from <2% to over 75%.")
    ], "Overcomes 640x640 resolution limits for fine cracks.", COLOR_ROYAL),
    ("Phase 2: Fleet Dashcam Units", "Continuous Road Surveys", [
        ("Edge Optimization", "Export INT8 quantized weights for Android and edge micro-PCs."),
        ("Municipal Fleet Mounting", "Mount units on municipal buses and waste collection trucks."),
        ("Automated Daily Audits", "Provides daily road scanning across the city with zero added drivers."),
        ("Edge Deduplication", "In-memory spatial deduplication prevents redundant defect alerts.")
    ], "Turns municipal service vehicles into automated scanners.", COLOR_AMBER),
    ("Phase 3: Multi-Sensor Fusion", "Camera + Accelerometer", [
        ("Vibration & Visual Fusion", "Fuse camera detections with smartphone accelerometer vibrations."),
        ("Physical Depth Validation", "Dual verification of cavity depth through vehicular impact telemetry."),
        ("Subgrade Moisture Detection", "Thermal infrared sensing to detect water accumulation under pavement."),
        ("Predictive Road Maintenance", "Forecast road failure weeks before potholes collapse completely.")
    ], "Proactive lifecycle management instead of emergency fixes.", COLOR_EMERALD),
]

in_x = Inches(0.8)
for in_tag, in_title, in_items, in_foot, in_col in innovations:
    inc = add_card(s11, in_x, Inches(1.6), Inches(3.75), Inches(4.35), border_color=in_col, fill_color=COLOR_CARD, border_width=1.5)
    itf11 = inc.text_frame

    add_para(itf11, in_tag, 11, bold=True, color=in_col)
    add_para(itf11, in_title, 14, bold=True, color=COLOR_NAVY, space_before=3)

    for item_lbl, item_desc in in_items:
        add_para(itf11, f"• {item_lbl}:", 10, bold=True, color=COLOR_NAVY, space_before=5)
        add_para(itf11, f"   {item_desc}", 9, color=COLOR_TEXT_BODY)

    add_para(itf11, f"✓ Goal: {in_foot}", 9.5, bold=True, color=in_col, space_before=10)
    in_x += Inches(3.99)

# Bottom Roadmap Banner
rm_banner = add_card(s11, Inches(0.8), Inches(6.15), Inches(11.73), Inches(0.85), border_color=COLOR_BORDER, fill_color=COLOR_CARD_MUTED)
rtf11 = rm_banner.text_frame
add_para(rtf11, "💡 Long-Term Vision: Transform road maintenance from reactive pothole patching into a proactive, data-driven pavement management lifecycle.", 11.5, bold=True, color=COLOR_NAVY)


# ==============================================================================
# SLIDE 12: Summary & Q&A
# ==============================================================================
s12 = prs.slides.add_slide(blank_layout)
set_slide_background(s12)
add_header(s12, "Summary, Conclusion & Open Discussion", "11. Conclusion & Q&A", 12, 12)

# Left Summary Card
left_card12 = add_card(s12, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.2), border_color=COLOR_BORDER_STRONG, fill_color=COLOR_CARD)
tf_l12 = left_card12.text_frame

add_para(tf_l12, "KEY TAKEAWAYS", 11, bold=True, color=COLOR_ROYAL)
add_para(tf_l12, "Project Summary", 16, bold=True, color=COLOR_NAVY, space_before=3)

bullets_l = [
    ("Accessible & Affordable", "Converts consumer cameras and CPUs into automated road inspectors without expensive LiDAR vehicles."),
    ("Zero Clean-Road False Alarms", "Eliminated border phantom boxes; achieves 0% false positives on clean highway pavement."),
    ("High Pothole Precision", "Demonstrates 92.3% validation precision with high confidence on real road cavities."),
    ("Standardized Civil Compliance", "Automates calculation of ASTM D6433 Pavement Condition Index (PCI) and vector PDF reports."),
    ("Honest Scientific Understanding", "Identified downsampling resolution loss as the key challenge for fine crack detection, paving the way for SAHI tiling.")
]
for b_head, b_body in bullets_l:
    add_para(tf_l12, f"✓ {b_head}:", 10.5, bold=True, color=COLOR_NAVY, space_before=7)
    add_para(tf_l12, f"   {b_body}", 9.5, color=COLOR_TEXT_BODY)

add_para(tf_l12, "✨ Thank you! Questions & discussion welcomed.", 12, bold=True, color=COLOR_EMERALD, space_before=14)

# Right Author & Project Card
right_card12 = add_card(s12, Inches(6.83), Inches(1.6), Inches(5.7), Inches(5.2), border_color=COLOR_BORDER_STRONG, fill_color=COLOR_CARD)
tf_r12 = right_card12.text_frame

add_para(tf_r12, "PROJECT CREDITS", 11, bold=True, color=COLOR_AMBER)
add_para(tf_r12, "Priye Ranjan", 17, bold=True, color=COLOR_NAVY, space_before=3)

details_r = [
    ("GitHub", "@Priya-Ranjan-0201"),
    ("Repository", "github.com/Priya-Ranjan-0201/Potholes-detector"),
    ("Domain", "Computer Vision & Smart Transportation"),
    ("Model", "YOLO11n-Rescued (ONNX Runtime CPU Engine)"),
    ("Stack", "FastAPI (Python 3.12) + React 19 + TypeScript + Vite"),
    ("Standards", "ASTM D6433 PCI Engine · IRC:82-2015 Repair Codes"),
    ("License", "Open-Source MIT License")
]
for lbl, val in details_r:
    add_para(tf_r12, f"•  {lbl}:  {val}", 10.5, color=COLOR_TEXT_BODY, space_before=6)

add_para(tf_r12, "⭐ Complete codebase & documentation available on GitHub", 11, bold=True, color=COLOR_ROYAL, space_before=14)

out_pptx = PROJECT_ROOT / "ScamRoad_Presentation.pptx"
prs.save(str(out_pptx))
print(f"Presentation saved successfully to {out_pptx}")
