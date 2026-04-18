"""
OpenMEP Project Report Generator
Generates a professional PDF project report using ReportLab.
Theme: Red #CC0000 / Black #0A0A0A / White #FFFFFF
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen.canvas import Canvas

# ── Colour palette ────────────────────────────────────────────────────────────
RED    = HexColor("#CC0000")
DARK   = HexColor("#0A0A0A")
MID    = HexColor("#1A1A1A")
GREY   = HexColor("#555555")
LGREY  = HexColor("#AAAAAA")
XLGREY = HexColor("#E8E8E8")
WHITE  = HexColor("#FFFFFF")
ACCENT = HexColor("#990000")

PAGE_W, PAGE_H = A4
MARGIN = 2.0 * cm

# ── Page template with header/footer ─────────────────────────────────────────
def make_doc(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=2.5*cm, bottomMargin=2.5*cm,
        title="OpenMEP Project Report",
        author="Luquman A",
        subject="MEP Engineering Calculation Suite — Technical Documentation",
    )
    return doc

def draw_header_footer(canvas: Canvas, doc):
    canvas.saveState()
    # Header bar
    canvas.setFillColor(DARK)
    canvas.rect(0, PAGE_H - 1.5*cm, PAGE_W, 1.5*cm, fill=1, stroke=0)
    canvas.setFillColor(RED)
    canvas.rect(0, PAGE_H - 1.65*cm, PAGE_W, 0.15*cm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(MARGIN, PAGE_H - 1.1*cm, "OpenMEP — Open-Source MEP Engineering Calculation Suite")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 1.1*cm, "Version 0.1.0 | March 2024")

    # Footer bar
    canvas.setFillColor(DARK)
    canvas.rect(0, 0, PAGE_W, 1.2*cm, fill=1, stroke=0)
    canvas.setFillColor(RED)
    canvas.rect(0, 1.2*cm, PAGE_W, 0.12*cm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(MARGIN, 0.45*cm, "© 2025 Luquman A | MIT License | github.com/kakarot-oncloud/openmep-suite")
    canvas.drawRightString(PAGE_W - MARGIN, 0.45*cm, f"Page {doc.page}")
    canvas.restoreState()

def draw_cover(canvas: Canvas, doc):
    """Special cover page — no header/footer lines."""
    canvas.saveState()
    # Full dark background
    canvas.setFillColor(DARK)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # Red accent stripe
    canvas.setFillColor(RED)
    canvas.rect(0, PAGE_H * 0.38, PAGE_W, PAGE_H * 0.005, fill=1, stroke=0)
    canvas.rect(0, PAGE_H * 0.62, PAGE_W, PAGE_H * 0.005, fill=1, stroke=0)
    # Footer bar on cover
    canvas.setFillColor(HexColor("#111111"))
    canvas.rect(0, 0, PAGE_W, 2.0*cm, fill=1, stroke=0)
    canvas.setFillColor(LGREY)
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(PAGE_W / 2, 0.7*cm, "© 2025 Luquman A | MIT License | Open-Source MEP Engineering")
    canvas.restoreState()

# ── Style sheet ───────────────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()
    styles = {}

    styles["cover_title"] = ParagraphStyle(
        "cover_title", fontSize=44, fontName="Helvetica-Bold",
        textColor=WHITE, alignment=TA_CENTER, spaceAfter=6,
        leading=52,
    )
    styles["cover_sub"] = ParagraphStyle(
        "cover_sub", fontSize=16, fontName="Helvetica",
        textColor=XLGREY, alignment=TA_CENTER, spaceAfter=4, leading=22,
    )
    styles["cover_tagline"] = ParagraphStyle(
        "cover_tagline", fontSize=13, fontName="Helvetica-Oblique",
        textColor=RED, alignment=TA_CENTER, spaceAfter=0, leading=18,
    )
    styles["cover_meta"] = ParagraphStyle(
        "cover_meta", fontSize=10, fontName="Helvetica",
        textColor=LGREY, alignment=TA_CENTER, spaceAfter=2, leading=16,
    )
    styles["h1"] = ParagraphStyle(
        "h1", fontSize=22, fontName="Helvetica-Bold",
        textColor=DARK, spaceBefore=18, spaceAfter=8,
        borderPad=4, leading=28,
    )
    styles["h2"] = ParagraphStyle(
        "h2", fontSize=15, fontName="Helvetica-Bold",
        textColor=RED, spaceBefore=12, spaceAfter=5, leading=20,
    )
    styles["h3"] = ParagraphStyle(
        "h3", fontSize=12, fontName="Helvetica-Bold",
        textColor=DARK, spaceBefore=8, spaceAfter=3, leading=16,
    )
    styles["body"] = ParagraphStyle(
        "body", fontSize=10, fontName="Helvetica",
        textColor=MID, spaceBefore=3, spaceAfter=3, leading=15,
        alignment=TA_JUSTIFY,
    )
    styles["body_left"] = ParagraphStyle(
        "body_left", fontSize=10, fontName="Helvetica",
        textColor=MID, spaceBefore=2, spaceAfter=2, leading=15,
        alignment=TA_LEFT,
    )
    styles["bullet"] = ParagraphStyle(
        "bullet", fontSize=10, fontName="Helvetica",
        textColor=MID, spaceBefore=2, spaceAfter=2, leading=14,
        leftIndent=16, bulletIndent=4,
        alignment=TA_LEFT,
    )
    styles["caption"] = ParagraphStyle(
        "caption", fontSize=8, fontName="Helvetica-Oblique",
        textColor=GREY, spaceBefore=2, spaceAfter=6, leading=11, alignment=TA_CENTER,
    )
    styles["toc_h1"] = ParagraphStyle(
        "toc_h1", fontSize=11, fontName="Helvetica-Bold",
        textColor=DARK, spaceBefore=6, spaceAfter=2, leading=15,
    )
    styles["toc_h2"] = ParagraphStyle(
        "toc_h2", fontSize=10, fontName="Helvetica",
        textColor=MID, spaceBefore=2, spaceAfter=1, leading=13, leftIndent=16,
    )
    styles["code"] = ParagraphStyle(
        "code", fontSize=8.5, fontName="Courier",
        textColor=DARK, backColor=XLGREY,
        spaceBefore=4, spaceAfter=4, leading=12,
        leftIndent=10, rightIndent=10, borderPad=5,
    )
    styles["table_header"] = ParagraphStyle(
        "table_header", fontSize=9, fontName="Helvetica-Bold",
        textColor=WHITE, alignment=TA_CENTER, leading=12,
    )
    styles["table_cell"] = ParagraphStyle(
        "table_cell", fontSize=9, fontName="Helvetica",
        textColor=DARK, alignment=TA_LEFT, leading=12,
    )
    styles["table_cell_c"] = ParagraphStyle(
        "table_cell_c", fontSize=9, fontName="Helvetica",
        textColor=DARK, alignment=TA_CENTER, leading=12,
    )
    return styles

# ── Helper flowables ──────────────────────────────────────────────────────────

def section_rule(styles):
    return HRFlowable(width="100%", thickness=2, color=RED, spaceAfter=4)

def subsection_rule(styles):
    return HRFlowable(width="40%", thickness=1, color=XLGREY, spaceAfter=3, hAlign="LEFT")

def red_box_heading(text, styles):
    """A red background box used for section headings."""
    data = [[Paragraph(text, styles["table_header"])]]
    t = Table(data, colWidths=[PAGE_W - 2*MARGIN])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), RED),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    return t

def dark_box_heading(text, styles):
    data = [[Paragraph(text, styles["table_header"])]]
    t = Table(data, colWidths=[PAGE_W - 2*MARGIN])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    return t

def make_table(headers, rows, styles, col_widths=None):
    """Build a styled ReportLab table."""
    header_row = [Paragraph(h, styles["table_header"]) for h in headers]
    data = [header_row]
    for row in rows:
        data.append([Paragraph(str(c), styles["table_cell"]) for c in row])

    if col_widths is None:
        n = len(headers)
        col_widths = [(PAGE_W - 2*MARGIN) / n] * n

    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK),
        ("TEXTCOLOR", (0,0), (-1,0), WHITE),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, XLGREY]),
        ("GRID", (0,0), (-1,-1), 0.5, LGREY),
        ("LINEBELOW", (0,0), (-1,0), 1.5, RED),
    ]))
    return t

def bullet_list(items, styles, symbol="•"):
    result = []
    for item in items:
        result.append(Paragraph(f"<b>{symbol}</b>  {item}", styles["bullet"]))
    return result

# ─────────────────────────────────────────────────────────────────────────────
# BUILD THE REPORT
# ─────────────────────────────────────────────────────────────────────────────

def build_report(output_path: str):
    doc = make_doc(output_path)
    styles = make_styles()
    story = []

    # ══════════════════════════════════════════════════════════════════════════
    # COVER PAGE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 5*cm))
    story.append(Paragraph("OpenMEP", styles["cover_title"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Open-Source MEP Engineering Calculation Suite", styles["cover_sub"]))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Engineering calculations should be open.", styles["cover_tagline"]))
    story.append(Spacer(1, 3.0*cm))
    story.append(Paragraph("PROJECT REPORT", styles["cover_sub"]))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Version 0.1.0 | Initial Release | March 2024", styles["cover_meta"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("4 Regions  ·  26 Calculation Modules  ·  35+ API Endpoints", styles["cover_meta"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("GCC / Europe / India / Australia", styles["cover_meta"]))
    story.append(Spacer(1, 3.0*cm))
    story.append(Paragraph("FastAPI  ·  Streamlit  ·  Python 3.11  ·  ReportLab  ·  Docker", styles["cover_meta"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Table of Contents", styles["h1"]))
    story.append(section_rule(styles))
    story.append(Spacer(1, 0.3*cm))

    toc_items = [
        ("1.", "Executive Summary", None),
        ("2.", "Project Overview", None),
        ("3.", "Region Support", [
            ("3.1", "GCC / UAE / Saudi Arabia / Qatar / Kuwait"),
            ("3.2", "Europe / United Kingdom"),
            ("3.3", "India"),
            ("3.4", "Australia / New Zealand"),
        ]),
        ("4.", "Calculation Modules", [
            ("4.1", "Electrical Engineering (8 modules)"),
            ("4.2", "HVAC / Mechanical Engineering (4 modules)"),
            ("4.3", "Plumbing & Drainage (6 modules)"),
            ("4.4", "Fire Protection (4 modules)"),
            ("4.5", "Project Tools (4 modules)"),
        ]),
        ("5.", "Technical Architecture", None),
        ("6.", "Standards & Compliance Framework", None),
        ("7.", "API Reference Overview", None),
        ("8.", "Bill of Quantities Engine", None),
        ("9.", "PDF Report Generation", None),
        ("10.", "Deployment Options", None),
        ("11.", "Market Value & Use Cases", None),
        ("12.", "Technology Stack", None),
        ("13.", "Roadmap", None),
        ("14.", "How to Contribute", None),
        ("15.", "License & Acknowledgements", None),
    ]

    for num, title, sub in toc_items:
        story.append(Paragraph(f"<b>{num}</b>  {title}", styles["toc_h1"]))
        if sub:
            for snum, stitle in sub:
                story.append(Paragraph(f"{snum}  {stitle}", styles["toc_h2"]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 1. EXECUTIVE SUMMARY
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("1. Executive Summary", styles))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "OpenMEP is a comprehensive, open-source MEP (Mechanical, Electrical & Plumbing) engineering calculation suite "
        "built for practising engineers in four global regions: the GCC states (UAE, Saudi Arabia, Qatar, Kuwait), "
        "Europe and the United Kingdom, India, and Australia/New Zealand. The system provides 26 calculation modules, "
        "a 35-endpoint REST API, and a production-ready Streamlit multi-page application — all under the MIT licence.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "Commercial MEP software typically costs $2,000–$10,000 per seat per year and produces proprietary, "
        "non-auditable outputs. OpenMEP addresses this by making every calculation formula, every correction factor, "
        "and every standard reference openly readable in Python source code. Engineers can verify, modify, and extend "
        "every calculation — something no commercial tool allows.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.2*cm))

    summary_data = [
        ["Metric", "Value"],
        ["Calculation Modules", "26 (Electrical 8, HVAC 4, Plumbing 6, Fire 4, Tools 4)"],
        ["REST API Endpoints", "35+"],
        ["Regions Supported", "4 (GCC, Europe/UK, India, Australia)"],
        ["Standards Implemented", "40+ international and regional standards"],
        ["Programming Language", "Python 3.11+"],
        ["Backend Framework", "FastAPI 0.109"],
        ["Frontend Framework", "Streamlit 1.30"],
        ["Licence", "MIT (open source)"],
        ["Deployment Options", "Local, Docker, Streamlit Cloud, VPS, Google Colab"],
    ]
    t = make_table(summary_data[0], summary_data[1:], styles, [6*cm, 11*cm])
    story.append(t)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 2. PROJECT OVERVIEW
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("2. Project Overview", styles))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "MEP engineering encompasses the mechanical (HVAC, plumbing, drainage), electrical (power, lighting, "
        "protection), and fire protection systems that make buildings habitable and safe. Every building — "
        "from a small office to a hospital or data centre — requires MEP design calculations before construction.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("<b>Why Open Source?</b>", styles["h3"]))
    for item in [
        "Calculation transparency — every formula and every correction factor is auditable in source code",
        "Zero licensing cost — free for individuals, SMEs, and government agencies",
        "Extensibility — add a new calculation engine in < 50 lines of Python",
        "Community-driven standards updates — when a standard is revised, any contributor can update the engine",
        "Academic use — universities and research institutions can use and cite the code",
    ]:
        story.append(Paragraph(f"•  {item}", styles["bullet"]))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("<b>Project Goals</b>", styles["h3"]))
    story.append(Paragraph(
        "The v0.1.0 release targets MEP engineers in the four regions that represent the majority of the world's "
        "high-growth construction markets: the GCC states (where billions in MEP contracts are awarded annually), "
        "the UK and Europe (mature markets with rigorous standards), India (the world's fastest-growing construction "
        "market), and Australia/New Zealand.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("<b>Problem Statement</b>", styles["h3"]))
    story.append(Paragraph(
        "Existing MEP calculation tools fall into two categories: (1) expensive commercial software with black-box "
        "calculations and no source access, or (2) Excel spreadsheets that are not version-controlled, not "
        "standardised across firms, and not auditable. OpenMEP fills the gap — a free, open, standardised, and "
        "deployable alternative that produces professional output (Excel BOQs, PDF reports, API responses) "
        "compatible with existing workflows.",
        styles["body"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 3. REGION SUPPORT
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("3. Region Support", styles))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "OpenMEP implements a 3-level region selector: Region → Country/State → Utility/Authority. "
        "Selecting a utility switches the applicable standard, ambient temperature defaults, "
        "correction factor tables, and currency automatically.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.3*cm))

    region_table = [
        ["Region", "Countries / States", "Utilities / AHJ", "Currency", "Primary Electrical Standard"],
        ["GCC", "UAE, KSA, Qatar, Kuwait, Bahrain, Oman",
         "DEWA, ADDC, SEWA, SEC, KAHRAMAA, MEW", "AED / SAR / QAR", "BS 7671:2018 AMD2"],
        ["Europe / UK", "UK, Ireland, Germany, France, Netherlands, Nordics",
         "UK DNOs, VDE, EDF/Enedis, NEN", "GBP / EUR", "BS 7671 / IEC 60364"],
        ["India", "All 28 states + 8 UTs",
         "MSEDCL, BESCOM, TANGEDCO, BSES, TSSPDCL, WBSEDCL, others", "INR", "IS 3961"],
        ["Australia / NZ", "All 6 states + ACT/NT + NZ",
         "Ausgrid, Powercor, Energex, SA Power, Western Power, others", "AUD / NZD", "AS/NZS 3008.1.1:2017"],
    ]
    t = make_table(region_table[0], region_table[1:], styles, [2.5*cm, 4.5*cm, 4.5*cm, 2*cm, 3.5*cm])
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    # GCC detail
    story.append(Paragraph("3.1  GCC Region", styles["h2"]))
    story.append(Paragraph(
        "The Gulf Cooperation Council region is one of the world's most active MEP markets. Projects typically "
        "follow BS 7671 for electrical, NFPA 13/20 for fire protection, and BS EN 806 for plumbing — but with "
        "significant overlays from each country's Civil Defence authority and utility. "
        "OpenMEP implements DEWA (Dubai), ADDC (Abu Dhabi), SEWA (Sharjah), SEC (Saudi Arabia), KAHRAMAA (Qatar), "
        "and MEW (Kuwait) as distinct authorities with their own technical requirements applied on top of the base standards.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Key GCC defaults:", styles["h3"]))
    gcc_defaults = [
        ["Parameter", "Value", "Standard/Basis"],
        ["Ambient temperature", "40°C (outdoor) / 25°C (conditioned)", "BS 7671 Table 4B1"],
        ["Cable type preference", "XLPE/Cu", "DEWA Technical Requirements 2023"],
        ["Voltage drop limit", "4% power, 3% lighting", "BS 7671 Section 525"],
        ["Earthing system", "TN-S", "DEWA / SEC requirements"],
        ["Supply voltage", "415/240 V, 50 Hz", "GCC utility standard"],
        ["Fire standard", "NFPA 13/20 + Civil Defence code", "UAE/Qatar Civil Defence"],
    ]
    t = make_table(gcc_defaults[0], gcc_defaults[1:], styles, [4*cm, 5.5*cm, 7.5*cm])
    story.append(t)
    story.append(Spacer(1, 0.4*cm))

    # Europe
    story.append(Paragraph("3.2  Europe / United Kingdom", styles["h2"]))
    story.append(Paragraph(
        "The UK applies BS 7671:2018 AMD2 (18th Edition) as the primary wiring regulation, with CIBSE Guides "
        "governing HVAC design and BS EN 12845 for sprinkler systems. Continental European countries use IEC 60364 "
        "as the base, with national deviations (DIN VDE 0100 in Germany, NFC 15-100 in France, NEN 1010 in Netherlands). "
        "OpenMEP uses BS 7671 / IEC 60364 as the common base for all European sub-regions in v0.1.0.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.4*cm))

    # India
    story.append(Paragraph("3.3  India", styles["h2"]))
    story.append(Paragraph(
        "India follows the Bureau of Indian Standards (BIS) suite of standards, with the National Building Code "
        "(NBC 2016) as the overarching compliance framework. The CPWD Schedule of Rates (DSR) governs BOQ "
        "pricing for government and public sector projects. OpenMEP implements 9 major state Distribution Companies "
        "and applies IS 3961 (cable sizing at 35°C ambient basis), IS 5329 (drainage), IS 1172 (plumbing), "
        "and NBC 2016 Part 4 (fire) as the primary standards.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.4*cm))

    # Australia
    story.append(Paragraph("3.4  Australia / New Zealand", styles["h2"]))
    story.append(Paragraph(
        "Australia uses AS/NZS 3008.1.1:2017 for LV cable sizing with the unique column-reference system "
        "for installation methods. OpenMEP maps the universal installation method codes (A1, B1, C, D1, E, F) "
        "to the correct AS/NZS 3008 Table column numbers automatically. The National Construction Code (NCC 2022) "
        "and AS 2118.1:2017 govern fire protection. AS 3500 series covers plumbing and drainage.",
        styles["body"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 4. CALCULATION MODULES
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("4. Calculation Modules", styles))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "OpenMEP v0.1.0 provides 26 calculation modules across five disciplines. "
        "Each module is implemented as a pure Python calculation engine in "
        "<font name='Courier'>backend/engines/</font>, paired with a FastAPI route and a Streamlit page.",
        styles["body"]
    ))

    # 4.1 Electrical
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("4.1  Electrical Engineering (8 Modules)", styles["h2"]))
    elec_modules = [
        ["Module", "Standard (GCC/Europe)", "Standard (India)", "Standard (Australia)", "Key Output"],
        ["Cable Sizing", "BS 7671:2018 AMD2, Table 4D2A", "IS 3961 Part 1/2", "AS/NZS 3008.1.1:2017", "Min. cable size (mm²)"],
        ["Voltage Drop", "BS 7671 Section 525 (4%/3%)", "IS 732 (5%)", "AS/NZS 3000 (5%)", "VD in V and %"],
        ["Maximum Demand", "DEWA TR / SEC / IEE method", "IS method / CEA Reg.", "NCC method", "Demand kW/kVA, incomer A"],
        ["Short Circuit", "IEC 60909:2016", "IEC 60909:2016", "IEC 60909:2016", "Isc peak and symm (kA)"],
        ["Lighting Design", "CIBSE LG7:2005", "IS 3646:1992", "AS/NZS 1680:2006", "No. of luminaires, lux"],
        ["Panel Schedule", "BS 7671 / NEMA", "IS 3043 / BIS", "AS/NZS 3000", "Phase loads, incomer A"],
        ["Generator Sizing", "BS EN ISO 8528", "BS EN ISO 8528", "BS EN ISO 8528", "Generator kVA, fuel L/hr"],
        ["PF Correction", "IEC 60831-1", "IEC 60831-1", "IEC 60831-1", "Capacitor bank kVAr"],
    ]
    t = make_table(elec_modules[0], elec_modules[1:], styles, [3*cm, 3.5*cm, 3*cm, 3*cm, 4*cm])
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    # Cable sizing formula box
    story.append(Paragraph("Key Formula: Cable Sizing (BS 7671 Method)", styles["h3"]))
    story.append(Paragraph(
        "<font name='Courier'>I_b ≤ I_n ≤ I_z</font><br/><br/>"
        "Where:<br/>"
        "<font name='Courier'>I_b</font> = design current (A) = P / (√3 × V × cos φ)  for 3-phase<br/>"
        "<font name='Courier'>I_n</font> = nominal current of protective device (A)<br/>"
        "<font name='Courier'>I_z</font> = current-carrying capacity of cable (A) = I_t × Ca × Cg × Cs<br/><br/>"
        "<font name='Courier'>Ca</font> = ambient temperature correction factor (BS 7671 Table 4B1)<br/>"
        "<font name='Courier'>Cg</font> = grouping derating factor (BS 7671 Table 4C1)<br/>"
        "<font name='Courier'>Cs</font> = soil/thermal resistance factor (buried cables)",
        styles["code"]
    ))
    story.append(Spacer(1, 0.3*cm))

    # 4.2 HVAC
    story.append(Paragraph("4.2  HVAC / Mechanical Engineering (4 Modules)", styles["h2"]))
    hvac_modules = [
        ["Module", "Primary Standard", "Method", "Key Output"],
        ["Cooling Load", "ASHRAE 90.1 / CIBSE Guide A", "CLTD/CLF (ASHRAE)", "Sensible + latent kW, tons"],
        ["Duct Sizing", "SMACNA HVAC Duct Std 2nd Ed", "Equal-friction method", "Duct dimensions mm×mm, vel m/s"],
        ["Heating Load", "EN 12831 / CIBSE Guide A", "Transmission + ventilation loss", "Total heat load W and kW"],
        ["Ventilation", "ASHRAE 62.1 / AS 1668.2", "Occupancy + area method", "OA l/s, ACH, heat recovery kW"],
    ]
    t = make_table(hvac_modules[0], hvac_modules[1:], styles, [3*cm, 4.5*cm, 4.5*cm, 5*cm])
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Key Formula: Cooling Load (ASHRAE CLTD Method)", styles["h3"]))
    story.append(Paragraph(
        "<font name='Courier'>Q_transmission = U × A × CLTD_corr</font><br/><br/>"
        "<font name='Courier'>CLTD_corr = CLTD + (25.5 - T_room) + (T_outdoor_mean - 29.4)</font><br/><br/>"
        "<font name='Courier'>Q_people = N × (sensible_gain + latent_gain_per_person)</font><br/>"
        "<font name='Courier'>Q_lighting = W/m² × Area × CLF_lighting</font><br/>"
        "<font name='Courier'>Q_total = Q_transmission + Q_solar + Q_people + Q_lighting + Q_equipment + Q_ventilation</font>",
        styles["code"]
    ))
    story.append(Spacer(1, 0.3*cm))

    # 4.3 Plumbing
    story.append(Paragraph("4.3  Plumbing & Drainage (6 Modules)", styles["h2"]))
    plumb_modules = [
        ["Module", "Standard", "Method", "Key Output"],
        ["Pipe Sizing", "BS EN 806-3 / IS 1172 / AS 3500.1", "Loading unit method", "Pipe dia. mm, velocity m/s"],
        ["Drainage Sizing", "BS EN 12056 / IS 5329 / AS 3500.2", "Discharge unit (DU) method", "Stack dia. mm, branch dia. mm"],
        ["Pump Sizing", "Darcy-Weisbach / BS EN 806", "Friction head calculation", "Duty point: flow l/s × head m"],
        ["Hot Water System", "BS EN 806-3 / BS 8558", "Simultaneous demand", "Storage vol. l, heat-up kW"],
        ["Rainwater Harvesting", "BS 8515 / AS 3500.1 App. D", "Yield-demand algorithm", "Tank vol. m³, mains offset %"],
        ["Tank Sizing", "BS EN 806 / IS 1172", "Daily demand method", "Tank vol. m³, inlet/outlet pipe mm"],
    ]
    t = make_table(plumb_modules[0], plumb_modules[1:], styles, [3.5*cm, 4.5*cm, 3.5*cm, 5*cm])
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    # 4.4 Fire
    story.append(Paragraph("4.4  Fire Protection (4 Modules)", styles["h2"]))
    fire_modules = [
        ["Module", "Standard (GCC/India)", "Standard (UK)", "Standard (Australia)", "Key Output"],
        ["Sprinkler Design", "NFPA 13:2022", "BS EN 12845:2015+A1", "AS 2118.1:2017", "Flow l/min, pressure bar"],
        ["Fire Pump", "NFPA 20:2022", "BS EN 12845:2015", "AS 2941:2013", "Duty flow/pressure, motor kW"],
        ["Fire Tank", "NFPA 22 / NBC 2016", "BS 9251:2021", "AS 2941:2013", "Tank vol. m³, inlet pipe mm"],
        ["Standpipe", "NFPA 14:2019", "BS 9990:2015", "AS 2419.1:2021", "Riser mm, pump bar, PRV floors"],
    ]
    t = make_table(fire_modules[0], fire_modules[1:], styles, [3*cm, 3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Key Formula: Sprinkler Hydraulic Calculation", styles["h3"]))
    story.append(Paragraph(
        "<font name='Courier'>Q = K × √P</font><br/><br/>"
        "Where:<br/>"
        "<font name='Courier'>Q</font> = flow from head (l/min)<br/>"
        "<font name='Courier'>K</font> = K-factor of sprinkler head (l/min / bar^0.5)<br/>"
        "<font name='Courier'>P</font> = pressure at the head (bar)<br/><br/>"
        "System demand = Σ(Q_i) for all heads in remote area + hose allowance<br/>"
        "Design density = Q_total / Remote Area (mm/min checked ≥ table minimum)",
        styles["code"]
    ))
    story.append(Spacer(1, 0.3*cm))

    # 4.5 Project Tools
    story.append(Paragraph("4.5  Project Tools (4 Modules)", styles["h2"]))
    tools_modules = [
        ["Tool", "Schema / Format", "Export", "Purpose"],
        ["BOQ Generator", "FIDIC / NRM2 / CPWD DSR / AIQS", "Excel (.xlsx) — multi-sheet", "Regional Bill of Quantities with FX"],
        ["Compliance Checker", "BS 7671 / NFPA / IS / AS checks", "PDF summary report", "Pass/fail compliance matrix"],
        ["PDF Reports", "A4 letterhead — all 26 modules", "PDF (ReportLab)", "Professional calculation report"],
        ["Submittal Tracker", "Custom — submittals, RFIs, equipment", "Excel (.xlsx)", "Project document status tracking"],
    ]
    t = make_table(tools_modules[0], tools_modules[1:], styles, [3.5*cm, 4.5*cm, 3.5*cm, 5.5*cm])
    story.append(t)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 5. TECHNICAL ARCHITECTURE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("5. Technical Architecture", styles))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "OpenMEP follows a clean three-layer architecture: calculation engines, REST API, and user interface. "
        "Each layer is independently deployable and independently testable.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Architecture Diagram (Text Representation)", styles["h3"]))
    story.append(Paragraph(
        "┌─────────────────────────────────────────────────────────────────────┐<br/>"
        "│                        USER INTERFACE LAYER                         │<br/>"
        "│  Streamlit Multi-Page App (26 pages)  │  (future) React/TypeScript  │<br/>"
        "│           localhost:8501              │       (future) mobile app    │<br/>"
        "└──────────────────────────┬──────────────────────────────────────────┘<br/>"
        "                           │  HTTP/JSON REST calls<br/>"
        "┌──────────────────────────▼──────────────────────────────────────────┐<br/>"
        "│                         API LAYER                                   │<br/>"
        "│         FastAPI 0.109 — localhost:8000/api/...                      │<br/>"
        "│  /electrical/  /mechanical/  /plumbing/  /fire/  /boq/  /reports/  │<br/>"
        "│      Pydantic v2 request validation + OpenAPI auto-documentation     │<br/>"
        "└──────────────────────────┬──────────────────────────────────────────┘<br/>"
        "                           │  Python function calls<br/>"
        "┌──────────────────────────▼──────────────────────────────────────────┐<br/>"
        "│                    CALCULATION ENGINE LAYER                         │<br/>"
        "│  backend/engines/electrical/   backend/engines/mechanical/          │<br/>"
        "│  backend/engines/plumbing/     backend/engines/fire/                │<br/>"
        "│  Pure Python — no I/O, no HTTP, fully unit-testable                 │<br/>"
        "└─────────────────────────────────────────────────────────────────────┘",
        styles["code"]
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Key Design Decisions", styles["h3"]))
    arch_items = [
        "<b>Stateless API</b> — every request carries all required inputs; no server-side session state",
        "<b>Pydantic v2 validation</b> — all inputs are validated before reaching the engine; invalid inputs return HTTP 422 with descriptive errors",
        "<b>Pure engine functions</b> — calculation engines have no side effects; they can be imported directly in any Python script without FastAPI",
        "<b>Region-parametric design</b> — a single engine function handles all regions via dict lookups; no region-specific engine files",
        "<b>Streaming PDF</b> — reports are generated in-memory by ReportLab and streamed to the client; no file storage required",
    ]
    for item in arch_items:
        story.append(Paragraph(f"•  {item}", styles["bullet"]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 6. STANDARDS & COMPLIANCE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("6. Standards & Compliance Framework", styles))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "OpenMEP implements over 40 published engineering standards. The following table lists the primary "
        "electrical and fire standards by region. The complete standards reference is in docs/STANDARDS_REFERENCE.md.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.3*cm))

    std_table = [
        ["Discipline", "Standard", "Edition", "Regions"],
        ["Electrical", "BS 7671 (IET Wiring Regs)", "18th Ed, AMD2 2022", "GCC, Europe"],
        ["Electrical", "IEC 60364-5-52", "2009", "GCC, Europe"],
        ["Electrical", "IS 3961", "2011", "India"],
        ["Electrical", "AS/NZS 3008.1.1", "2017", "Australia"],
        ["Electrical", "IEC 60909-0", "2016", "All regions"],
        ["HVAC", "ASHRAE 90.1", "2022", "GCC, Australia"],
        ["HVAC", "CIBSE Guide A", "2015", "Europe/UK, GCC"],
        ["HVAC", "EN 12831", "2017", "Europe"],
        ["HVAC", "SMACNA Duct Std", "2nd Ed", "All regions"],
        ["HVAC", "ASHRAE 62.1", "2022", "All regions"],
        ["Plumbing", "BS EN 806 / 806-3", "2006/2012", "GCC, Europe"],
        ["Plumbing", "BS EN 12056", "2000", "GCC, Europe"],
        ["Plumbing", "IS 1172", "1983 (R2019)", "India"],
        ["Plumbing", "AS 3500.1/2", "2021", "Australia"],
        ["Fire", "NFPA 13", "2022", "GCC, Australia"],
        ["Fire", "BS EN 12845", "2015+A1", "GCC, Europe"],
        ["Fire", "NFPA 20", "2022", "GCC, Australia"],
        ["Fire", "AS 2118.1", "2017", "Australia"],
        ["Fire", "NBC 2016 Part 4", "2016", "India"],
    ]
    t = make_table(std_table[0], std_table[1:], styles, [3*cm, 5*cm, 3.5*cm, 5.5*cm])
    story.append(t)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 7. API REFERENCE OVERVIEW
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("7. API Reference Overview", styles))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "All endpoints accept JSON via POST and return JSON. Interactive Swagger UI is at "
        "<font name='Courier'>http://localhost:8000/docs</font>. "
        "Full reference with request/response schemas is in docs/API_DOCS.md.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.3*cm))

    api_table = [
        ["Endpoint", "Method", "Description"],
        ["/api/electrical/cable-sizing", "POST", "Cable size for a given load (BS 7671 / IS 3961 / AS 3008)"],
        ["/api/electrical/voltage-drop", "POST", "Voltage drop check (% and absolute)"],
        ["/api/electrical/maximum-demand", "POST", "Maximum demand with utility diversity factors"],
        ["/api/electrical/short-circuit", "POST", "Short-circuit fault current (IEC 60909)"],
        ["/api/electrical/lighting", "POST", "Luminaire count for a target illuminance"],
        ["/api/electrical/panel-schedule", "POST", "Panel schedule with load balancing check"],
        ["/api/electrical/generator-sizing", "POST", "Generator kVA with starting kVA step analysis"],
        ["/api/electrical/pf-correction", "POST", "Capacitor bank kVAr for PF correction"],
        ["/api/mechanical/cooling-load", "POST", "ASHRAE CLTD cooling load (kW and tons)"],
        ["/api/mechanical/duct-sizing", "POST", "Duct size (equal-friction method, SMACNA)"],
        ["/api/mechanical/heating-load", "POST", "Heating load (EN 12831 / CIBSE Guide A)"],
        ["/api/mechanical/ventilation", "POST", "Outdoor air requirement (ASHRAE 62.1 / AS 1668.2)"],
        ["/api/plumbing/pipe-sizing", "POST", "Pipe diameter (loading unit method)"],
        ["/api/plumbing/drainage-sizing", "POST", "Drain/stack diameter (discharge unit method)"],
        ["/api/plumbing/pump-sizing", "POST", "Pump duty point (Darcy-Weisbach)"],
        ["/api/plumbing/hot-water", "POST", "Hot water storage volume and heat-up kW"],
        ["/api/plumbing/rainwater-harvesting", "POST", "Rainwater tank size (BS 8515 / AS 3500)"],
        ["/api/plumbing/tank-sizing", "POST", "Cold water tank with fire reserve"],
        ["/api/fire/sprinkler-design", "POST", "Sprinkler hydraulics (NFPA 13 / BS EN 12845)"],
        ["/api/fire/fire-pump", "POST", "Fire pump duty point (NFPA 20 / BS EN 12845)"],
        ["/api/fire/fire-tank", "POST", "Fire water storage volume"],
        ["/api/fire/standpipe", "POST", "Wet riser / standpipe (NFPA 14 / BS 9990)"],
        ["/api/boq/generate", "POST", "Generate Bill of Quantities (FIDIC/NRM2/CPWD/AIQS)"],
        ["/api/compliance/check", "POST", "Multi-standard compliance pass/fail matrix"],
        ["/api/reports/generate", "POST", "Generate A4 PDF calculation report (stream)"],
    ]
    t = make_table(api_table[0], api_table[1:], styles, [7.5*cm, 1.5*cm, 8*cm])
    story.append(t)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 8. BILL OF QUANTITIES ENGINE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("8. Bill of Quantities Engine", styles))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "The BOQ Generator produces a multi-sheet Excel workbook with discipline subtotals and a grand total "
        "in local currency and USD. FX rates are provided by the API in real time. "
        "The schema (FIDIC/NRM2/CPWD/AIQS) and column headers are automatically selected by region.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.2*cm))

    boq_table = [
        ["Region", "BOQ Schema", "Column Headers", "Currency"],
        ["GCC", "FIDIC Red/Yellow Book", "Item Ref | Description | Unit | Qty | Rate (AED) | Amount (AED) | Amount (USD) | Remarks", "AED"],
        ["Europe/UK", "RICS NRM2", "NRM2 Ref | Description | Unit | Quantity | Rate (£) | Amount (£) | Amount (USD) | Notes", "GBP"],
        ["India", "CPWD DSR", "DSR Ref | Description | Unit | Qty | Rate (INR) | Amount (INR) | Amount (USD) | Spec Ref", "INR"],
        ["Australia", "AIQS Cost Mgmt Manual", "AIQS Ref | Description | Unit | Quantity | Rate (AUD) | Amount (AUD) | Amount (USD) | Trade Code", "AUD"],
    ]
    t = make_table(boq_table[0], boq_table[1:], styles, [2.5*cm, 3*cm, 7.5*cm, 2*cm])
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("FX Conversion Logic", styles["h3"]))
    story.append(Paragraph(
        "<font name='Courier'>amount_local = amount_usd × usd_fx_rate</font><br/><br/>"
        "Where <font name='Courier'>usd_fx_rate</font> is returned by the API for the selected region "
        "(e.g., 3.67 for AED, 0.79 for GBP, 83.5 for INR, 1.53 for AUD). "
        "Grand totals use the <font name='Courier'>grand_total_{currency}</font> field from the BOQ API response.",
        styles["code"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 9. PDF REPORT GENERATION
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("9. PDF Report Generation", styles))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "OpenMEP generates professional A4 PDF calculation reports using ReportLab 4.4.10. "
        "Reports are generated in memory (no disk write required) and streamed to the client via FastAPI's "
        "StreamingResponse. The red/black/white theme is consistent with the Streamlit UI.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Report Format:", styles["h3"]))
    pdf_items = [
        "Cover: project name, engineer, checked by, date, revision, applicable standard",
        "Title block: client, project, location, drawing/report reference",
        "Calculation methodology section: formulas used, standard references, assumptions",
        "Input parameters table: all inputs with units",
        "Results table: all outputs with pass/fail status",
        "Sign-off block: space for engineer stamp and signature",
        "Footer: page number, version, standard reference",
    ]
    for item in pdf_items:
        story.append(Paragraph(f"•  {item}", styles["bullet"]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 10. DEPLOYMENT OPTIONS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("10. Deployment Options", styles))
    story.append(Spacer(1, 0.3*cm))

    deploy_table = [
        ["Method", "Command / Platform", "Best For", "Notes"],
        ["Local", "uvicorn + streamlit run", "Developers, single user", "2 terminals, Python 3.11+ required"],
        ["Docker Compose", "docker-compose up -d", "Teams, self-hosted server", "Single command, all-in-one"],
        ["VPS systemd", "systemctl start openmep-*", "Production VPS (Ubuntu/Debian)", "Persistent, auto-restart on boot"],
        ["Streamlit Cloud", "GitHub connect + deploy", "Quick public demo", "API must be hosted separately"],
        ["Google Colab", "Colab notebook (1-click)", "One-off calculations, training", "Sessions disconnect after 12 hr"],
    ]
    t = make_table(deploy_table[0], deploy_table[1:], styles, [3*cm, 4*cm, 3.5*cm, 6.5*cm])
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Environment Variables", styles["h3"]))
    story.append(Paragraph(
        "<font name='Courier'>API_BASE</font> — FastAPI server URL (default: http://localhost:8000)<br/>"
        "<font name='Courier'>PORT</font> — FastAPI listen port (default: 8000)<br/>"
        "<font name='Courier'>POSTGRES_PASSWORD</font> — optional PostgreSQL password<br/>"
        "<font name='Courier'>SECRET_KEY</font> — reserved for v0.2.0 authentication",
        styles["code"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 11. MARKET VALUE & USE CASES
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("11. Market Value & Use Cases", styles))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "The global MEP engineering software market is valued at over $4 billion (2023) and growing at 8% CAGR. "
        "OpenMEP targets segments that are currently underserved by commercial tools:",
        styles["body"]
    ))
    story.append(Spacer(1, 0.2*cm))

    use_cases = [
        ["Use Case", "Target User", "Value Delivered"],
        ["Small MEP consultancy (< 10 engineers)", "Engineers, partners", "Zero licensing cost vs. $2–10k/seat/yr commercial tools"],
        ["Freelance MEP engineer", "Individual engineer", "Professional PDF reports with zero software cost"],
        ["Government / public sector project", "MEP engineers in PWD, CPWD, municipalities", "Open, auditable calculations for public accountability"],
        ["University / academic research", "Professors, PhD researchers", "Citable open-source implementation of IEC/BS/IS standards"],
        ["MEP software training", "Training institutes, BIM academies", "Free teaching tool with full source code access"],
        ["Pre-bid estimation", "MEP estimators", "Quick BOQ generation in FIDIC/NRM2/CPWD format with FX"],
        ["AI/ML training data", "AI researchers in AEC", "Structured MEP calculation data from open API"],
    ]
    t = make_table(use_cases[0], use_cases[1:], styles, [4*cm, 4*cm, 9*cm])
    story.append(t)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 12. TECHNOLOGY STACK
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("12. Technology Stack", styles))
    story.append(Spacer(1, 0.3*cm))

    stack_table = [
        ["Component", "Technology", "Version", "Purpose"],
        ["Backend API", "FastAPI", "0.109+", "REST API with OpenAPI auto-documentation"],
        ["API Server", "Uvicorn", "0.27+", "ASGI server for FastAPI"],
        ["Data Validation", "Pydantic v2", "2.5+", "Request/response model validation"],
        ["UI Framework", "Streamlit", "1.30+", "26-page multi-page calculation app"],
        ["Charting", "Plotly", "5.20+", "Interactive charts in Streamlit pages"],
        ["Data Tables", "Pandas", "2.0+", "Tabular data manipulation"],
        ["Numerical", "NumPy", "1.26+", "Vector operations in engine calculations"],
        ["PDF Generation", "ReportLab", "4.4.10", "A4 PDF calculation reports"],
        ["Excel Export", "openpyxl", "3.1+", "BOQ and submittal tracker Excel export"],
        ["HTTP Client", "httpx / requests", "0.26+ / 2.31+", "API calls from Streamlit pages"],
        ["Testing", "pytest + pytest-asyncio", "7.4+ / 0.23+", "Unit and integration testing"],
        ["Containerisation", "Docker + Docker Compose", "Latest", "Production deployment"],
        ["Language", "Python", "3.11+", "All backend and frontend code"],
    ]
    t = make_table(stack_table[0], stack_table[1:], styles, [3.5*cm, 3*cm, 2.5*cm, 8*cm])
    story.append(t)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 13. ROADMAP
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("13. Roadmap", styles))
    story.append(Spacer(1, 0.3*cm))

    roadmap_table = [
        ["Version", "Target", "Key Features"],
        ["v0.1.0", "March 2024 (Current)", "26 modules, 4 regions, 35+ API endpoints, BOQ, PDF reports, Streamlit UI"],
        ["v0.2.0", "Q3 2024", "North America region (NEC/NFPA 70), API key auth, PostgreSQL results history"],
        ["v0.3.0", "Q1 2025", "React + TypeScript frontend (replaces Streamlit for production deployments)"],
        ["v0.4.0", "Q2 2025", "Expo React Native mobile app (iOS + Android)"],
        ["v0.5.0", "Q3 2025", "Singapore (SS standards) + South Africa (SANS 10142) regions"],
        ["v1.0.0", "2026", "BIM/IFC export, AI design recommendations, team workspaces, billing"],
    ]
    t = make_table(roadmap_table[0], roadmap_table[1:], styles, [2.5*cm, 3*cm, 11.5*cm])
    story.append(t)
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Planned Calculation Modules (v0.2.0 – v0.3.0)", styles["h3"]))
    planned = [
        "Arc Flash Analysis (IEEE 1584:2018)",
        "Lightning Protection (IEC 62305)",
        "UPS Sizing (IEC 62040-3) — engine implemented, page pending",
        "NFPA 72 Fire Alarm System Design",
        "Solar PV System Sizing (IEC 61730 / AS/NZS 4777.2)",
        "Electric Vehicle Charging Infrastructure (IEC 61851)",
        "Building Automation System (BAS) Point Schedule",
    ]
    for item in planned:
        story.append(Paragraph(f"•  {item}", styles["bullet"]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # APPENDIX A: SAMPLE CALCULATION WALKTHROUGH — CABLE SIZING
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("Appendix A: Sample Calculation — Cable Sizing (GCC/DEWA)", styles))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("<b>Project:</b> Office Tower, Dubai, UAE<br/><b>Standard:</b> BS 7671:2018 AMD2, Table 4D2A", styles["body_left"]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Step 1: Design Current", styles["h3"]))
    story.append(Paragraph(
        "<font name='Courier'>I_b = P / (√3 × V × cos φ)</font><br/>"
        "<font name='Courier'>I_b = 45,000 / (1.732 × 415 × 0.85)</font><br/>"
        "<font name='Courier'>I_b = 45,000 / 611.3 = 73.6 A</font>",
        styles["code"]
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Step 2: Ambient Temperature Correction (Table 4B1, 40°C)", styles["h3"]))
    story.append(Paragraph(
        "<font name='Courier'>Ca (for XLPE, 40°C) = 0.87  (BS 7671 Table 4B1, XLPE row)</font>",
        styles["code"]
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Step 3: Grouping Factor (single circuit)", styles["h3"]))
    story.append(Paragraph(
        "<font name='Courier'>Cg = 1.00  (no grouping)</font>",
        styles["code"]
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Step 4: Required Tabulated Current", styles["h3"]))
    story.append(Paragraph(
        "<font name='Courier'>I_t = I_b / (Ca × Cg) = 73.6 / (0.87 × 1.00) = 84.6 A</font>",
        styles["code"]
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Step 5: Cable Selection (Table 4D2A, Method C, XLPE/Cu)", styles["h3"]))
    cable_sel = [
        ["Size (mm²)", "It Method C (A)", "Selected?"],
        ["16", "74", "No — 74 < 84.6"],
        ["25", "99", "No — marginal, check VD"],
        ["35", "121", "Yes — 121 ≥ 84.6 ✓"],
    ]
    t = make_table(cable_sel[0], cable_sel[1:], styles, [4*cm, 5*cm, 8*cm])
    story.append(t)
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Step 6: Voltage Drop Verification", styles["h3"]))
    story.append(Paragraph(
        "<font name='Courier'>VD = (I_b × L × (r cos φ + x sin φ)) / 1000</font><br/>"
        "<font name='Courier'>r = 0.524 mΩ/m (35 mm² Cu, Table 4D2B)</font><br/>"
        "<font name='Courier'>x = 0.0966 mΩ/m (Table 4D2B)</font><br/>"
        "<font name='Courier'>VD = 73.6 × 80 × (0.524×0.85 + 0.0966×0.527) / 1000 = 2.73 V</font><br/>"
        "<font name='Courier'>VD% = (2.73 / 415) × 100 = 0.66% &lt; 4.0% PASS ✓</font>",
        styles["code"]
    ))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("<b>Result:</b> 35 mm² XLPE/Cu 3-core cable, Method C, 80 m run. Design current 73.6 A. "
        "Installed capacity 121 A (derated 0.87 → 105 A). Voltage drop 0.66%. COMPLIANT.",
        styles["body"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # APPENDIX B: SAMPLE CALCULATION — COOLING LOAD
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("Appendix B: Sample Calculation — Cooling Load (GCC/Dubai)", styles))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("<b>Project:</b> Open-plan office, 20 m × 15 m × 3.5 m, South-facing, Dubai<br/><b>Standard:</b> ASHRAE 90.1-2022, CLTD/CLF method", styles["body_left"]))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Design Conditions (Dubai, ASHRAE)", styles["h3"]))
    dc_table = [
        ["Parameter", "Value", "Source"],
        ["Outdoor dry-bulb (summer)", "45°C", "ASHRAE 2021 Fundamentals, Dubai"],
        ["Outdoor wet-bulb (summer)", "30°C", "ASHRAE 2021 Fundamentals, Dubai"],
        ["Indoor design", "24°C / 50% RH", "ASHRAE 55:2020"],
        ["Occupancy", "40 persons", "Assumed"],
        ["Lighting power density", "12 W/m²", "ASHRAE 90.1-2022"],
        ["Equipment load", "8 kW total", "Assumed"],
    ]
    t = make_table(dc_table[0], dc_table[1:], styles, [5*cm, 4*cm, 8*cm])
    story.append(t)
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Load Components", styles["h3"]))
    load_table = [
        ["Load Component", "Formula / Method", "Value (kW)"],
        ["Wall transmission (South)", "U × A × CLTD_corr = 0.4 × (3.5×20) × 12.5", "3.5 kW"],
        ["Roof transmission", "U × A × CLTD_roof = 0.25 × 300 × 34", "2.55 kW"],
        ["Solar gain (South glazing)", "A × SC × CLF_glass = 60 × 0.6 × 180 W/m²", "6.48 kW"],
        ["People (sensible)", "40 × 73 W/person", "2.92 kW"],
        ["People (latent)", "40 × 59 W/person", "2.36 kW"],
        ["Lighting", "12 W/m² × 300 m² × 0.95 CLF", "3.42 kW"],
        ["Equipment", "8 kW × 1.0 CLF", "8.0 kW"],
        ["Ventilation (10 l/s/person × 40)", "ASHRAE 62.1", "6.8 kW"],
        ["Total sensible", "Sum of sensible", "33.7 kW"],
        ["Total latent", "People + ventilation", "6.2 kW"],
        ["<b>Total cooling load</b>", "Sensible + latent", "<b>39.9 kW (11.4 tons)</b>"],
        ["Design load (10% margin)", "× 1.10", "<b>43.9 kW (12.5 tons)</b>"],
    ]
    t = make_table(load_table[0], load_table[1:], styles, [5*cm, 6.5*cm, 5.5*cm])
    story.append(t)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # APPENDIX C: SAMPLE CALCULATION — SPRINKLER SYSTEM
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("Appendix C: Sample Calculation — Sprinkler System (GCC/NFPA 13)", styles))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "<b>Project:</b> Office floor, Ordinary Hazard Group 2, 12 heads in remote area<br/>"
        "<b>Standard:</b> NFPA 13:2022 + UAE Civil Defence Code 2011",
        styles["body_left"]
    ))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Design Parameters (NFPA 13:2022, Table 11.2.3.1.1)", styles["h3"]))
    sp_table = [
        ["Parameter", "Value", "Source"],
        ["Hazard class", "Ordinary Hazard Group 2 (OH2)", "NFPA 13:2022 Table 5.1"],
        ["Density/area curve", "0.15 gpm/ft² over 1500 ft² (6.1 mm/min over 139 m²)", "NFPA 13:2022 Fig 11.2.3.1.1"],
        ["K-factor", "80 (K80 standard response)", "NFPA 13:2022 Table 6.2.3.1"],
        ["Min. head pressure", "0.5 bar (7.25 psi)", "K=80 for 56.6 l/min minimum"],
        ["Remote area heads", "12 heads × 12 m² coverage", "NFPA 13:2022 Table 8.6.2.2.1(a)"],
        ["Hose allowance", "500 gpm (1,893 l/min) — Class III standpipe", "NFPA 13:2022 Cl 11.2.3.1.3"],
    ]
    t = make_table(sp_table[0], sp_table[1:], styles, [4*cm, 5.5*cm, 7.5*cm])
    story.append(t)
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Hydraulic Calculation (Most Unfavourable Head)", styles["h3"]))
    story.append(Paragraph(
        "<font name='Courier'>Q_head = K × √P = 80 × √0.5 = 56.6 l/min (min. head)</font><br/><br/>"
        "<font name='Courier'>Remote area flow = 12 heads × average Q</font><br/>"
        "<font name='Courier'>Density check: 679 l/min ÷ 139 m² = 4.9 l/min/m² ≥ 6.1 l/min/m² FAIL → increase pressure</font><br/><br/>"
        "<font name='Courier'>Recalculate at P = 0.7 bar:</font><br/>"
        "<font name='Courier'>Q_head = 80 × √0.7 = 66.9 l/min</font><br/>"
        "<font name='Courier'>Remote area flow = 12 × 72 (avg) = 864 l/min</font><br/>"
        "<font name='Courier'>Density = 864 / 139 = 6.2 l/min/m² ≥ 6.1 PASS ✓</font><br/><br/>"
        "<font name='Courier'>Total system demand = 864 + 1893 (hose) = 2757 l/min</font><br/>"
        "<font name='Courier'>Pump duty = 2757 l/min @ 8.5 bar (including friction + elevation)</font>",
        styles["code"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # APPENDIX D: DESIGN DATA TABLES
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("Appendix D: Regional Design Data Tables", styles))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("D.1  Ambient Temperature Correction Factors for Cable Sizing", styles["h2"]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Table D.1-1: BS 7671 Table 4B1 — Ambient Temperature Correction Factors (Ca) for XLPE cables", styles["caption"]))
    ca_xlpe = [
        ["Ambient Temp (°C)", "Ca — Thermoplastic (PVC)", "Ca — Thermosetting (XLPE)", "Applies To"],
        ["25", "1.06", "1.04", "UK indoor conditioned"],
        ["30", "1.00", "1.00", "UK/Europe outdoor, reference"],
        ["35", "0.94", "0.96", "India standard ambient"],
        ["40", "0.87", "0.91", "GCC, India hot zone"],
        ["45", "0.79", "0.87", "GCC outdoor / hot climate"],
        ["50", "0.71", "0.82", "GCC extreme / rooftop"],
        ["55", "0.61", "0.76", "Equipment room worst case"],
    ]
    t = make_table(ca_xlpe[0], ca_xlpe[1:], styles, [3.5*cm, 4.5*cm, 4.5*cm, 5*cm])
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("D.2  GCC Outdoor Design Conditions (ASHRAE)", styles["h2"]))
    story.append(Spacer(1, 0.2*cm))
    gcc_climate = [
        ["City", "Summer DB (°C)", "Summer WB (°C)", "Coincident RH (%)", "Winter DB (°C)", "Reference"],
        ["Dubai (DEWA)", "45", "30", "45", "12", "ASHRAE 2021 HOF"],
        ["Abu Dhabi (ADDC)", "46", "30", "43", "11", "ASHRAE 2021 HOF"],
        ["Riyadh (SEC)", "46", "18", "7", "5", "ASHRAE 2021 HOF"],
        ["Jeddah (SEC)", "41", "28", "52", "17", "ASHRAE 2021 HOF"],
        ["Doha (KAHRAMAA)", "45", "29", "46", "12", "ASHRAE 2021 HOF"],
        ["Kuwait City (MEW)", "47", "25", "22", "8", "ASHRAE 2021 HOF"],
        ["Muscat", "43", "29", "54", "18", "ASHRAE 2021 HOF"],
        ["Manama", "43", "29", "53", "14", "ASHRAE 2021 HOF"],
    ]
    t = make_table(gcc_climate[0], gcc_climate[1:], styles, [3*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 4*cm])
    story.append(t)
    story.append(PageBreak())

    story.append(Paragraph("D.3  Per Capita Water Demand by Region and Building Type", styles["h2"]))
    story.append(Spacer(1, 0.2*cm))
    water_demand = [
        ["Building Type", "GCC l/p/day", "UK l/p/day", "India l/p/day", "Australia l/p/day", "Standard"],
        ["Residential", "250", "150", "135 (municipal)", "155", "Various"],
        ["Residential (premium)", "350", "220", "200", "220", "Various"],
        ["Office", "45", "40", "45", "50", "Various"],
        ["Hotel (per bed)", "400", "220", "180", "220", "Various"],
        ["Hospital (per bed)", "500", "350", "340", "400", "Various"],
        ["School (per pupil)", "50", "30", "45", "30", "Various"],
        ["Restaurant (per cover)", "70", "60", "50", "60", "Various"],
        ["Industrial (per worker)", "50", "40", "30–45", "45", "Various"],
    ]
    t = make_table(water_demand[0], water_demand[1:], styles, [3.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 4*cm])
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("D.4  Sprinkler Hazard Classification Comparison", styles["h2"]))
    story.append(Spacer(1, 0.2*cm))
    hazard_comp = [
        ["Occupancy", "NFPA 13:2022 Class", "BS EN 12845 Class", "AS 2118.1 Class"],
        ["Offices, hotels, hospitals", "Light Hazard", "Light Hazard (LH)", "Light Hazard"],
        ["Libraries, showrooms", "Ordinary Hazard Gp 1", "Ordinary Hazard 1 (OH1)", "Ordinary Hazard 1"],
        ["Cold stores, laundries", "Ordinary Hazard Gp 1", "Ordinary Hazard 1 (OH1)", "Ordinary Hazard 1"],
        ["Car parks, light manufacturing", "Ordinary Hazard Gp 2", "Ordinary Hazard 2 (OH2)", "Ordinary Hazard 1"],
        ["Retail, warehouses (low)", "Ordinary Hazard Gp 2", "Ordinary Hazard 2 (OH2)", "Ordinary Hazard 2"],
        ["Timber processing, paint spray", "Extra Hazard Gp 1", "Extra High Hazard (EH1)", "Extra High Hazard"],
        ["High-piled storage, flammables", "Extra Hazard Gp 2", "Extra High Hazard (EH2)", "Extra High Hazard"],
    ]
    t = make_table(hazard_comp[0], hazard_comp[1:], styles, [4.5*cm, 4*cm, 4*cm, 4.5*cm])
    story.append(t)
    story.append(PageBreak())

    story.append(Paragraph("D.5  SMACNA Duct Velocity Limits by Application", styles["h2"]))
    story.append(Spacer(1, 0.2*cm))
    duct_vel = [
        ["Application", "Max Velocity (m/s)", "Recommended (m/s)", "Note"],
        ["Main supply duct (low velocity)", "8.0", "5.0–6.0", "Commercial HVAC"],
        ["Main supply duct (high velocity)", "15.0", "10.0–12.0", "Industrial / VAV"],
        ["Branch supply duct", "6.0", "3.5–4.5", "Commercial"],
        ["Final diffuser connection", "3.5", "2.0–3.0", "Noise control"],
        ["Return air duct", "6.0", "4.0–5.0", "Commercial"],
        ["Kitchen exhaust", "10.0", "8.0–10.0", "Grease removal"],
        ["Toilet exhaust", "5.0", "3.5–4.0", "Odour control"],
        ["Car park exhaust", "6.0", "4.0–5.0", "CO purge"],
    ]
    t = make_table(duct_vel[0], duct_vel[1:], styles, [5*cm, 3.5*cm, 3.5*cm, 5*cm])
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("D.6  Standard Protective Device Ratings", styles["h2"]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("IEC standard MCB/MCCB current ratings (A):", styles["body_left"]))
    story.append(Paragraph(
        "<font name='Courier'>MCB:  1, 2, 4, 6, 10, 13, 16, 20, 25, 32, 40, 50, 63 A</font><br/>"
        "<font name='Courier'>MCCB: 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600 A</font><br/>"
        "<font name='Courier'>ACB:  630, 800, 1000, 1250, 1600, 2000, 2500, 3200, 4000 A</font>",
        styles["code"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # APPENDIX E: PROJECT FILE STRUCTURE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("Appendix E: Project File Structure", styles))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "The complete OpenMEP repository file structure as of v0.1.0:",
        styles["body"]
    ))
    story.append(Paragraph(
        "<font name='Courier'>openmep/</font><br/>"
        "<font name='Courier'>├── README.md                        # Project overview and quick start</font><br/>"
        "<font name='Courier'>├── CONTRIBUTING.md                  # Contributor guide</font><br/>"
        "<font name='Courier'>├── CODE_OF_CONDUCT.md               # Community standards</font><br/>"
        "<font name='Courier'>├── SECURITY.md                      # Responsible disclosure policy</font><br/>"
        "<font name='Courier'>├── CHANGELOG.md                     # Version history</font><br/>"
        "<font name='Courier'>├── requirements.txt                 # Python dependencies</font><br/>"
        "<font name='Courier'>├── pyproject.toml                   # Project metadata</font><br/>"
        "<font name='Courier'>├── Dockerfile                       # Container build file</font><br/>"
        "<font name='Courier'>├── docker-compose.yml               # Multi-service orchestration</font><br/>"
        "<font name='Courier'>├── .env.example                     # Environment variable template</font><br/>"
        "<font name='Courier'>├── colab_launcher.ipynb             # Google Colab notebook</font><br/>"
        "<font name='Courier'>│</font><br/>"
        "<font name='Courier'>├── backend/</font><br/>"
        "<font name='Courier'>│   ├── main.py                      # FastAPI app + router registration</font><br/>"
        "<font name='Courier'>│   ├── engines/</font><br/>"
        "<font name='Courier'>│   │   ├── electrical/              # 8 electrical calculation modules</font><br/>"
        "<font name='Courier'>│   │   │   ├── cable_sizing.py</font><br/>"
        "<font name='Courier'>│   │   │   ├── voltage_drop.py</font><br/>"
        "<font name='Courier'>│   │   │   ├── demand_load.py</font><br/>"
        "<font name='Courier'>│   │   │   ├── short_circuit.py</font><br/>"
        "<font name='Courier'>│   │   │   ├── lighting.py</font><br/>"
        "<font name='Courier'>│   │   │   ├── panel_schedule.py</font><br/>"
        "<font name='Courier'>│   │   │   ├── generator_sizing.py</font><br/>"
        "<font name='Courier'>│   │   │   └── pf_correction.py</font><br/>"
        "<font name='Courier'>│   │   ├── mechanical/              # 4 HVAC calculation modules</font><br/>"
        "<font name='Courier'>│   │   ├── plumbing/                # 6 plumbing calculation modules</font><br/>"
        "<font name='Courier'>│   │   └── fire/                    # 4 fire protection modules</font><br/>"
        "<font name='Courier'>│   ├── api/routes/                  # FastAPI route handlers</font><br/>"
        "<font name='Courier'>│   │   ├── electrical.py            # 10+ electrical endpoints</font><br/>"
        "<font name='Courier'>│   │   ├── mechanical.py            # 4 HVAC endpoints</font><br/>"
        "<font name='Courier'>│   │   ├── plumbing.py              # 6 plumbing endpoints</font><br/>"
        "<font name='Courier'>│   │   ├── fire.py                  # 4 fire endpoints</font><br/>"
        "<font name='Courier'>│   │   ├── boq.py                   # BOQ generator endpoint</font><br/>"
        "<font name='Courier'>│   │   ├── compliance.py            # Compliance checker endpoint</font><br/>"
        "<font name='Courier'>│   │   └── reports.py               # PDF report generator endpoint</font><br/>"
        "<font name='Courier'>│   └── models/                      # Pydantic v2 model definitions</font><br/>"
        "<font name='Courier'>│</font><br/>"
        "<font name='Courier'>├── streamlit_app/</font><br/>"
        "<font name='Courier'>│   ├── app.py                       # Landing page + sidebar navigation</font><br/>"
        "<font name='Courier'>│   ├── utils.py                     # Region selector, API client, helpers</font><br/>"
        "<font name='Courier'>│   └── pages/                       # 26 Streamlit pages (numbered 1-26)</font><br/>"
        "<font name='Courier'>│       ├── 1_Cable_Sizing.py</font><br/>"
        "<font name='Courier'>│       ├── 2_Voltage_Drop.py</font><br/>"
        "<font name='Courier'>│       ├── ...  (pages 3 through 26)</font><br/>"
        "<font name='Courier'>│       └── 26_Plumbing_Tank_Sizing.py</font><br/>"
        "<font name='Courier'>│</font><br/>"
        "<font name='Courier'>├── docs/                            # All documentation</font><br/>"
        "<font name='Courier'>│   ├── USER_GUIDE.md</font><br/>"
        "<font name='Courier'>│   ├── API_DOCS.md</font><br/>"
        "<font name='Courier'>│   ├── STANDARDS_REFERENCE.md</font><br/>"
        "<font name='Courier'>│   ├── DEPLOYMENT.md</font><br/>"
        "<font name='Courier'>│   ├── regions/</font><br/>"
        "<font name='Courier'>│   │   ├── GCC_GUIDE.md</font><br/>"
        "<font name='Courier'>│   │   ├── EUROPE_GUIDE.md</font><br/>"
        "<font name='Courier'>│   │   ├── INDIA_GUIDE.md</font><br/>"
        "<font name='Courier'>│   │   └── AUSTRALIA_GUIDE.md</font><br/>"
        "<font name='Courier'>│   ├── contributing/</font><br/>"
        "<font name='Courier'>│   │   ├── ADDING_NEW_REGION.md</font><br/>"
        "<font name='Courier'>│   │   └── ADDING_NEW_CALCULATOR.md</font><br/>"
        "<font name='Courier'>│   └── OpenMEP_Project_Report.pdf   # This document</font><br/>"
        "<font name='Courier'>│</font><br/>"
        "<font name='Courier'>├── tests/                           # Pytest test suite</font><br/>"
        "<font name='Courier'>├── scripts/                         # Utility scripts</font><br/>"
        "<font name='Courier'>└── .github/ISSUE_TEMPLATE/          # GitHub issue templates</font>",
        styles["code"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # APPENDIX F: GLOSSARY OF TERMS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("Appendix F: Glossary of Terms", styles))
    story.append(Spacer(1, 0.3*cm))

    glossary = [
        ["Term", "Definition"],
        ["ACH", "Air Changes per Hour — ventilation measure (air volume / room volume per hour)"],
        ["AHJ", "Authority Having Jurisdiction — regulatory body that enforces standards (e.g., DEWA, Civil Defence)"],
        ["AIQS", "Australian Institute of Quantity Surveyors"],
        ["API", "Application Programming Interface — the REST endpoint layer of OpenMEP"],
        ["ASHRAE", "American Society of Heating, Refrigerating and Air-Conditioning Engineers"],
        ["BOQ / BQ", "Bill of Quantities — priced document listing work items for tendering"],
        ["Ca", "Correction factor for ambient temperature (cable sizing)"],
        ["Cg", "Correction factor for cable grouping (BS 7671)"],
        ["CIBSE", "Chartered Institution of Building Services Engineers (UK)"],
        ["CLTD", "Cooling Load Temperature Difference — ASHRAE thermal calculation method"],
        ["CPWD", "Central Public Works Department (India) — publishes DSR"],
        ["DU", "Discharge Unit — flow unit for drainage design (BS EN 12056)"],
        ["DEWA", "Dubai Electricity and Water Authority"],
        ["DNO", "Distribution Network Operator (UK electricity distribution companies)"],
        ["DSR", "Departmental Schedule of Rates (India, CPWD)"],
        ["DISCOM", "Distribution Company (India) — e.g., MSEDCL, BESCOM"],
        ["FX", "Foreign Exchange rate (e.g., USD to AED)"],
        ["FIDIC", "Fédération Internationale des Ingénieurs-Conseils — standard form of construction contract"],
        ["I_b", "Design current (A) — actual operating current of a circuit"],
        ["I_t", "Tabulated current (A) — current capacity from standard tables before derating"],
        ["I_z", "Installed current capacity (A) — tabulated capacity after all derating factors"],
        ["IEC", "International Electrotechnical Commission"],
        ["IET", "Institution of Engineering and Technology (UK) — publishes BS 7671"],
        ["KAHRAMAA", "Qatar General Electricity and Water Corporation"],
        ["LH / OH / EH", "Light Hazard / Ordinary Hazard / Extra High Hazard (sprinkler classification)"],
        ["LU", "Loading Unit — flow unit for water supply pipe sizing (BS EN 806)"],
        ["MEP", "Mechanical, Electrical & Plumbing engineering"],
        ["MEN", "Multiple Earthed Neutral — Australia/NZ earthing system"],
        ["NBC", "National Building Code of India 2016"],
        ["NCC", "National Construction Code (Australia, replaces BCA)"],
        ["NFPA", "National Fire Protection Association (USA) — publishes NFPA 13, 14, 20, 70"],
        ["NRM2", "New Rules of Measurement 2 (RICS) — UK BOQ measurement method"],
        ["NPV", "Net Present Value — used in PF correction payback calculation"],
        ["NPSH", "Net Positive Suction Head — pump cavitation check"],
        ["PF", "Power Factor — ratio of real power to apparent power"],
        ["PRV", "Pressure Reducing Valve — used in high-rise fire risers to limit pressure"],
        ["RICS", "Royal Institution of Chartered Surveyors (UK)"],
        ["SEC", "Saudi Electricity Company"],
        ["SBC", "Saudi Building Code"],
        ["SMACNA", "Sheet Metal and Air Conditioning Contractors' National Association"],
        ["TN-S", "Earthing system: separate Neutral and Protective Earth conductors throughout"],
        ["TN-C-S", "Earthing system: combined N+PE to distribution board, then split (PME in UK)"],
        ["VD", "Voltage Drop — loss of voltage along a cable run"],
        ["VFD", "Variable Frequency Drive — motor starting method"],
    ]
    t = make_table(glossary[0], glossary[1:], styles, [3*cm, 14*cm])
    story.append(t)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 14. HOW TO CONTRIBUTE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("14. How to Contribute", styles))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "OpenMEP is built by engineers for engineers. Contributions from practising MEP engineers, "
        "software developers, and standards experts are all welcome.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.2*cm))

    contrib_table = [
        ["Contribution Type", "Skills Needed", "Time Estimate", "Guide"],
        ["Bug report", "Engineering knowledge", "15 minutes", ".github/ISSUE_TEMPLATE/bug_report.md"],
        ["New calculation engine", "Python + standard knowledge", "4–8 hours", "docs/contributing/ADDING_NEW_CALCULATOR.md"],
        ["New region", "Regional standards expertise + Python", "1–3 days", "docs/contributing/ADDING_NEW_REGION.md"],
        ["Standards update", "Python + updated standard", "2–4 hours", "CONTRIBUTING.md"],
        ["Documentation", "Technical writing", "1–4 hours", "CONTRIBUTING.md"],
        ["UI improvement", "Streamlit / Python", "2–8 hours", "CONTRIBUTING.md"],
    ]
    t = make_table(contrib_table[0], contrib_table[1:], styles, [4*cm, 3.5*cm, 2.5*cm, 7*cm])
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Contribution Workflow", styles["h3"]))
    story.append(Paragraph(
        "<font name='Courier'>git clone → git checkout -b feature/my-feature</font><br/>"
        "<font name='Courier'>→ make changes → pytest tests/ → git push → open Pull Request</font>",
        styles["code"]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 15. LICENSE & ACKNOWLEDGEMENTS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(red_box_heading("15. License & Acknowledgements", styles))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("<b>License: MIT</b>", styles["h3"]))
    story.append(Paragraph(
        "OpenMEP is released under the MIT Licence. This means you are free to use, copy, modify, merge, "
        "publish, distribute, sublicense, and/or sell copies of the software. "
        "The only requirement is that the original copyright notice and licence text are preserved.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Copyright © 2025 Luquman A", styles["body_left"]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("<b>Acknowledgements</b>", styles["h3"]))
    story.append(Paragraph(
        "OpenMEP stands on the work of the standards committees, researchers, and practitioners who wrote "
        "and maintain the engineering standards referenced throughout this software. We acknowledge the "
        "following organisations whose published standards form the technical basis of OpenMEP:",
        styles["body"]
    ))
    ack_list = [
        "The Institution of Engineering and Technology (IET) — BS 7671 IET Wiring Regulations",
        "CIBSE — Chartered Institution of Building Services Engineers — CIBSE Guides A, B, LG7",
        "IEC — International Electrotechnical Commission — IEC 60364, IEC 60909, IEC 62040",
        "ASHRAE — American Society of Heating, Refrigerating and Air-Conditioning Engineers",
        "NFPA — National Fire Protection Association — NFPA 13, 14, 20, 22, 70",
        "Bureau of Indian Standards (BIS) — IS 3961, IS 1172, IS 5329, NBC 2016",
        "Standards Australia — AS/NZS 3008, AS/NZS 3000, AS 3500, AS 2118.1",
        "SMACNA — Sheet Metal and Air Conditioning Contractors' National Association",
        "RICS — Royal Institution of Chartered Surveyors — NRM2",
        "FIDIC — Fédération Internationale des Ingénieurs-Conseils",
        "CPWD — Central Public Works Department, India — Schedule of Rates (DSR)",
    ]
    for ack in ack_list:
        story.append(Paragraph(f"•  {ack}", styles["bullet"]))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Document Information", styles["h3"]))
    doc_info = [
        ["Document title", "OpenMEP Project Report"],
        ["Version", "0.1.0"],
        ["Date", "March 2024"],
        ["Status", "Released"],
        ["Repository", "github.com/openmep/openmep"],
        ["Licence", "MIT"],
    ]
    t = make_table(["Field", "Value"], doc_info, styles, [5*cm, 12*cm])
    story.append(t)

    # ══════════════════════════════════════════════════════════════════════════
    # BUILD
    # ══════════════════════════════════════════════════════════════════════════
    doc.build(
        story,
        onFirstPage=draw_cover,
        onLaterPages=draw_header_footer,
    )
    print(f"PDF generated: {output_path}")
    page_count = sum(1 for el in story if isinstance(el, PageBreak)) + 1
    print(f"Estimated sections: {page_count} (actual page count varies with content reflow)")


if __name__ == "__main__":
    os.makedirs("docs", exist_ok=True)
    build_report("docs/OpenMEP_Project_Report.pdf")
