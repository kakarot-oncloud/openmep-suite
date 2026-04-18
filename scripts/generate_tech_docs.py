"""
OpenMEP — Advanced Technical Documentation PDF Generator  v4.0
Neo-Navy / Electric Teal design system  ·  All 15 sections fully detailed
Made by Luquman A | Copyright © 2025 Luquman A
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether, ListFlowable, ListItem
)
from reportlab.platypus.flowables import Flowable

# ─────────────────────────────────────────────────────────────────────────────
# COLOUR PALETTE  — Neo-Navy / Electric Teal Design System
# ─────────────────────────────────────────────────────────────────────────────
NAVY        = HexColor("#0A1628")
NAVY2       = HexColor("#132236")
TEAL        = HexColor("#0096C7")
TEAL_LIGHT  = HexColor("#00B4D8")
TEAL_PALE   = HexColor("#E0F4FA")
INK         = HexColor("#1C2538")
CHARCOAL    = HexColor("#2D3748")
SLATE       = HexColor("#4A5568")
MID         = HexColor("#718096")
RULE        = HexColor("#CBD5E0")
CODE_BG     = HexColor("#F0F4F8")
CODE_TEXT   = HexColor("#1A202C")
MIST        = HexColor("#F8FAFC")
OFF_WHITE   = HexColor("#FDFEFF")
PAGE_WHITE  = HexColor("#FFFFFF")

NOTE_BG     = HexColor("#E0F4FA")
NOTE_BDR    = TEAL
WARN_BG     = HexColor("#FFF8E6")
WARN_BDR    = HexColor("#D97706")
INFO_BG     = HexColor("#EEF2FF")
INFO_BDR    = HexColor("#4F46E5")
GOOD_BG     = HexColor("#F0FFF4")
GOOD_BDR    = HexColor("#16A34A")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE GEOMETRY
# ─────────────────────────────────────────────────────────────────────────────
PW, PH = A4
LM = RM = 2.0 * cm
TM = 2.8 * cm
BM = 2.2 * cm
CONTENT_W = PW - LM - RM


# ─────────────────────────────────────────────────────────────────────────────
# STYLE FACTORY
# ─────────────────────────────────────────────────────────────────────────────
def S():
    def ps(name, **kw):
        defaults = dict(fontName="Helvetica", fontSize=10, leading=16,
                        textColor=INK, spaceAfter=5, spaceBefore=0,
                        allowWidows=0, allowOrphans=0)
        return ParagraphStyle(name, **{**defaults, **kw})

    return {
        "cov_title":  ps("cov_title",  fontName="Helvetica-Bold",  fontSize=46,
                         textColor=white, alignment=TA_CENTER, leading=54, spaceAfter=12),
        "cov_sub":    ps("cov_sub",    fontName="Helvetica",       fontSize=15,
                         textColor=TEAL_LIGHT, alignment=TA_CENTER, leading=22),
        "cov_tag":    ps("cov_tag",    fontName="Helvetica-Bold",  fontSize=10,
                         textColor=white, alignment=TA_CENTER, leading=16),
        "cov_meta":   ps("cov_meta",   fontName="Helvetica",       fontSize=9.5,
                         textColor=HexColor("#90CDF4"), alignment=TA_CENTER, leading=15),
        "sec_num":    ps("sec_num",    fontName="Helvetica-Bold",  fontSize=8.5,
                         textColor=TEAL, spaceAfter=0, spaceBefore=22,
                         letterSpacing=2.5, alignment=TA_LEFT),
        "sec_title":  ps("sec_title",  fontName="Helvetica-Bold",  fontSize=26,
                         textColor=NAVY, spaceAfter=4, spaceBefore=2, leading=32),
        "sec_divider":ps("sec_divider",fontName="Helvetica",       fontSize=10,
                         textColor=TEAL, spaceAfter=14, leading=14),
        "h2":         ps("h2",         fontName="Helvetica-Bold",  fontSize=15,
                         textColor=NAVY, spaceAfter=4, spaceBefore=14, leading=20),
        "h3":         ps("h3",         fontName="Helvetica-Bold",  fontSize=12,
                         textColor=TEAL, spaceAfter=3, spaceBefore=10, leading=17),
        "h4":         ps("h4",         fontName="Helvetica-Bold",  fontSize=10.5,
                         textColor=CHARCOAL, spaceAfter=2, spaceBefore=8, leading=15),
        "body":       ps("body",       fontName="Helvetica",       fontSize=10,
                         textColor=INK, leading=16, spaceAfter=6, alignment=TA_JUSTIFY),
        "body_left":  ps("body_left",  fontName="Helvetica",       fontSize=10,
                         textColor=INK, leading=16, spaceAfter=6),
        "caption":    ps("caption",    fontName="Helvetica",       fontSize=8.5,
                         textColor=SLATE, leading=13, spaceAfter=8, alignment=TA_CENTER),
        "small":      ps("small",      fontName="Helvetica",       fontSize=8.5,
                         textColor=CHARCOAL, leading=13, spaceAfter=4),
        "code":       ps("code",       fontName="Courier",         fontSize=7.8,
                         textColor=CODE_TEXT, leading=12, spaceAfter=0,
                         backColor=CODE_BG, leftIndent=8, rightIndent=8),
        "code_lbl":   ps("code_lbl",   fontName="Helvetica-Bold",  fontSize=7.5,
                         textColor=TEAL, spaceAfter=0, spaceBefore=10,
                         letterSpacing=1),
        "note_text":  ps("note_text",  fontName="Helvetica",       fontSize=9.5,
                         textColor=HexColor("#0C4A6E"), leading=15, spaceAfter=0),
        "warn_text":  ps("warn_text",  fontName="Helvetica",       fontSize=9.5,
                         textColor=HexColor("#78350F"), leading=15, spaceAfter=0),
        "info_text":  ps("info_text",  fontName="Helvetica",       fontSize=9.5,
                         textColor=HexColor("#312E81"), leading=15, spaceAfter=0),
        "good_text":  ps("good_text",  fontName="Helvetica",       fontSize=9.5,
                         textColor=HexColor("#14532D"), leading=15, spaceAfter=0),
        "th":         ps("th",         fontName="Helvetica-Bold",  fontSize=8.5,
                         textColor=white, leading=13, alignment=TA_CENTER),
        "th_left":    ps("th_left",    fontName="Helvetica-Bold",  fontSize=8.5,
                         textColor=white, leading=13, alignment=TA_LEFT),
        "td":         ps("td",         fontName="Helvetica",       fontSize=8.5,
                         textColor=INK, leading=13, alignment=TA_LEFT),
        "td_c":       ps("td_c",       fontName="Helvetica",       fontSize=8.5,
                         textColor=INK, leading=13, alignment=TA_CENTER),
        "td_mono":    ps("td_mono",    fontName="Courier",         fontSize=7.8,
                         textColor=CODE_TEXT, leading=12, alignment=TA_LEFT),
        "td_mono_c":  ps("td_mono_c",  fontName="Courier",         fontSize=7.8,
                         textColor=CODE_TEXT, leading=12, alignment=TA_CENTER),
        "footer":     ps("footer",     fontName="Helvetica",       fontSize=7.5,
                         textColor=SLATE, alignment=TA_CENTER),
        "toc_section":ps("toc_section",fontName="Helvetica-Bold",  fontSize=10,
                         textColor=NAVY, leading=17),
        "toc_item":   ps("toc_item",   fontName="Helvetica",       fontSize=9.5,
                         textColor=CHARCOAL, leading=15, leftIndent=14),
    }


# ─────────────────────────────────────────────────────────────────────────────
# HEADER / FOOTER CANVAS CALLBACK
# ─────────────────────────────────────────────────────────────────────────────
def build_page_decorator(doc):
    def on_page(canvas, doc):
        canvas.saveState()
        pg = canvas.getPageNumber()
        stripe_h = 5
        canvas.setFillColor(TEAL)
        canvas.rect(0, PH - stripe_h, PW, stripe_h, stroke=0, fill=1)
        if pg > 1:
            canvas.setFont("Helvetica", 7.5)
            canvas.setFillColor(SLATE)
            canvas.drawString(LM, PH - 16, "OpenMEP — Advanced Technical Documentation")
            canvas.drawRightString(PW - RM, PH - 16, "Made by Luquman A  ·  © 2025 Luquman A")
            canvas.setStrokeColor(RULE)
            canvas.setLineWidth(0.5)
            canvas.line(LM, BM - 4, PW - RM, BM - 4)
            canvas.setFont("Helvetica-Bold", 8)
            canvas.setFillColor(TEAL)
            canvas.drawCentredString(PW / 2, BM - 14, f"— {pg} —")
        canvas.restoreState()
    return on_page


# ─────────────────────────────────────────────────────────────────────────────
# COVER PAGE ELEMENTS
# ─────────────────────────────────────────────────────────────────────────────
class CoverBackground(Flowable):
    def draw(self):
        c = self.canv
        ox = -LM
        oy = -BM
        c.setFillColor(NAVY)
        c.rect(ox, oy, PW, PH, stroke=0, fill=1)
        c.setFillColor(NAVY2)
        c.rect(ox, oy, PW, PH * 0.38, stroke=0, fill=1)
        c.setFillColor(TEAL)
        c.rect(ox, oy + PH - 8, PW, 8, stroke=0, fill=1)
        c.rect(ox, oy, PW, 6, stroke=0, fill=1)
        c.setStrokeColor(TEAL)
        c.setLineWidth(0.4)
        c.line(ox, oy + PH * 0.38 + 2, ox + PW, oy + PH * 0.38 + 2)
        c.setStrokeColor(HexColor("#FFFFFF"))
        c.setLineWidth(0.25)
        c.circle(ox + PW - 2 * cm, oy + PH - 3 * cm, 1.8 * cm, stroke=1, fill=0)
        c.circle(ox + PW - 2 * cm, oy + PH - 3 * cm, 1.2 * cm, stroke=1, fill=0)

    def wrap(self, availW, availH):
        return (availW, availH)


# ─────────────────────────────────────────────────────────────────────────────
# REUSABLE FLOWABLE HELPERS  (new-style: args in new order)
# ─────────────────────────────────────────────────────────────────────────────
def section_header(num_str, title_text, st):
    return [
        Paragraph(num_str, st["sec_num"]),
        Paragraph(title_text, st["sec_title"]),
        HRFlowable(width=CONTENT_W, thickness=1.5, color=TEAL, spaceAfter=14),
    ]


def callout(text, kind="note", st=None):
    cfg = {
        "note": (NOTE_BG, NOTE_BDR, "► NOTE",          st["note_text"] if st else None),
        "warn": (WARN_BG, WARN_BDR, "⚠ WARNING",        st["warn_text"] if st else None),
        "info": (INFO_BG, INFO_BDR, "ℹ INFO",           st["info_text"] if st else None),
        "good": (GOOD_BG, GOOD_BDR, "✓ GOOD PRACTICE",  st["good_text"] if st else None),
    }
    bg, bdr, label, style = cfg.get(kind, cfg["note"])
    inner = Paragraph(f"<b>{label}:</b>  {text}", style)
    tbl = Table([[inner]], colWidths=[CONTENT_W - 14])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), bg),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("LINEBEFORE",   (0, 0), (0, -1), 4, bdr),
    ]))
    wrapper = Table([[tbl]], colWidths=[CONTENT_W])
    wrapper.setStyle(TableStyle([
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]))
    return wrapper


def code_block(lines, label=None, st=None):
    out = []
    if label and st:
        out.append(Paragraph(label, st["code_lbl"]))
    if isinstance(lines, str):
        lines = lines.split("\n")
    chunk_size = 26
    for i in range(0, len(lines), chunk_size):
        chunk = lines[i:i + chunk_size]
        rows = [[Paragraph(ln.replace(" ", "&nbsp;").replace("<", "&lt;")
                           .replace(">", "&gt;"), st["code"])]
                for ln in chunk]
        tbl = Table(rows, colWidths=[CONTENT_W])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, -1), CODE_BG),
            ("LEFTPADDING",  (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING",   (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 2),
            ("GRID",         (0, 0), (-1, -1), 0.3, HexColor("#CBD5E0")),
        ]))
        out.append(tbl)
    out.append(Spacer(1, 6))
    return out


def data_table(headers, rows, col_widths=None, st=None, alt_rows=True):
    if col_widths is None:
        col_widths = [CONTENT_W / len(headers)] * len(headers)
    header_cells = [Paragraph(h, st["th"]) for h in headers]
    data = [header_cells]
    for i, row in enumerate(rows):
        bg = MIST if (alt_rows and i % 2 == 0) else PAGE_WHITE
        data.append([Paragraph(str(c), st["td"]) if not isinstance(c, Paragraph) else c
                     for c in row])
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 8.5),
        ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
        ("LINEBELOW",     (0, 0), (-1, 0), 1, TEAL),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [MIST, PAGE_WHITE]),
        ("GRID",          (0, 0), (-1, -1), 0.4, RULE),
        ("LEFTPADDING",   (0, 0), (-1, -1), 7),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return tbl


def mono_table(headers, rows, col_widths=None, st=None):
    if col_widths is None:
        col_widths = [CONTENT_W / len(headers)] * len(headers)
    header_cells = [Paragraph(h, st["th"]) for h in headers]
    data = [header_cells]
    for i, row in enumerate(rows):
        bg = MIST if i % 2 == 0 else PAGE_WHITE
        cells = []
        for c in row:
            if isinstance(c, Paragraph):
                cells.append(c)
            else:
                cells.append(Paragraph(str(c), st["td_mono_c"]))
        data.append(cells)
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 7.8),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("LINEBELOW",     (0, 0), (-1, 0), 1, TEAL),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [MIST, PAGE_WHITE]),
        ("GRID",          (0, 0), (-1, -1), 0.4, RULE),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return tbl


def bullet(text, st, indent=0):
    return Paragraph(f"• &nbsp; {text}", ParagraphStyle(
        "blt", parent=st["body_left"], leftIndent=14 + indent, spaceAfter=4, leading=16))


def sub_bullet(text, st):
    return bullet(text, st, indent=14)


def sp(h=8):
    return Spacer(1, h)


# ─────────────────────────────────────────────────────────────────────────────
# COMPATIBILITY HELPERS — old-style arg ordering (used throughout sections)
# ─────────────────────────────────────────────────────────────────────────────
_lead_sty = {}


def h2(st, t):  return Paragraph(t, st["h2"])
def h3(st, t):  return Paragraph(t, st["h3"])
def h4(st, t):  return Paragraph(t, st["h4"])
def body(st, t): return Paragraph(t, st["body"])


def lead(st, t):
    if "lead" not in _lead_sty:
        _lead_sty["lead"] = ParagraphStyle(
            "_lead_", fontName="Helvetica", fontSize=11, leading=18,
            textColor=INK, spaceAfter=8, spaceBefore=0,
            allowWidows=0, allowOrphans=0, alignment=TA_JUSTIFY)
    return Paragraph(t, _lead_sty["lead"])


def bul(st, t, level=1):
    return bullet(t, st, indent=(level - 1) * 14)


def SP(h=0.3):
    return sp(h * cm)


def HR(color=RULE, thickness=0.5, spaceAfter=6):
    return HRFlowable(CONTENT_W, thickness, color=color, spaceAfter=spaceAfter)


def cb(st, label, lines):
    """code_block with old arg order: st, label, lines"""
    return code_block(lines, label, st)


def dt(st, headers, rows, col_widths):
    """data_table with old arg order: st, headers, rows, col_widths"""
    return data_table(headers, rows, col_widths, st=st)


def co(st, text, style="note"):
    """callout with old arg order: st, text, style"""
    return callout(text, style, st)


def sb(st, num, title):
    """section_break returning list: PageBreak + section header flowables"""
    return [PageBreak()] + section_header(f"SECTION {num}", title, st)


# ─────────────────────────────────────────────────────────────────────────────
# COVER PAGE
# ─────────────────────────────────────────────────────────────────────────────
def cover_page(st):
    story = [CoverBackground()]
    story += [sp(PH * 0.18)]
    story.append(Paragraph("OpenMEP", st["cov_title"]))
    story.append(Paragraph("Advanced Technical Documentation", st["cov_sub"]))
    story.append(sp(18))
    story.append(Paragraph(
        "COMPREHENSIVE MEP ENGINEERING CALCULATION SUITE", st["cov_tag"]))
    story.append(sp(8))
    story.append(Paragraph(
        "26 Modules · 35 API Endpoints · 4 Regional Standards · Enterprise-Grade",
        st["cov_meta"]))
    story.append(sp(60))
    story.append(Paragraph("────────────────────────────────", ParagraphStyle(
        "line", fontName="Helvetica", fontSize=10, textColor=TEAL,
        alignment=TA_CENTER)))
    story.append(sp(14))
    story.append(Paragraph("Made by  <b>Luquman A</b>", ParagraphStyle(
        "auth", fontName="Helvetica", fontSize=12, textColor=white,
        alignment=TA_CENTER, leading=18)))
    story.append(sp(6))
    story.append(Paragraph(
        "GitHub: github.com/kakarot-oncloud/openmep-suite", st["cov_meta"]))
    story.append(sp(6))
    story.append(Paragraph(
        "Copyright © 2025 Luquman A  ·  MIT License  ·  Version 0.1.0",
        st["cov_meta"]))
    story.append(PageBreak())
    return story


# ─────────────────────────────────────────────────────────────────────────────
# TABLE OF CONTENTS
# ─────────────────────────────────────────────────────────────────────────────
def toc_page(st):
    story = []
    story += section_header("TABLE OF CONTENTS", "Document Index", st)
    sections = [
        ("01", "Project Overview & Scope"),
        ("02", "Technology Stack & Architecture"),
        ("03", "Project Structure — Full Annotated Directory"),
        ("04", "Code Deep-Dive — Annotated Source Files"),
        ("05", "Calculation Algorithms — Full Step-by-Step"),
        ("06", "Data Handling, State & Configuration"),
        ("07", "API Reference — All 35 Endpoints"),
        ("08", "Deployment Guides — All Platforms"),
        ("09", "GitHub Repository & Open-Source Workflow"),
        ("10", "Developer Setup — Step-by-Step"),
        ("11", "Future Roadmap & Scalability"),
        ("12", "Extension Guide — Add Modules & Regions"),
        ("13", "Known Limitations & Edge Cases"),
        ("14", "AI Summary — Patterns & Debugging"),
        ("15", "Standards Data Tables — Real Numerical Values"),
    ]
    for num, title in sections:
        story.append(Paragraph(f"<b>Section {num}</b>", st["toc_section"]))
        story.append(Paragraph(title, st["toc_item"]))
        story.append(sp(2))
    story.append(PageBreak())
    return story


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 01 — PROJECT OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
def section_01(st):
    story = sb(st, "01", "Project Overview")
    story += [
        lead(st, "OpenMEP is a free, open-source engineering calculation suite designed "
                 "for Mechanical, Electrical, and Plumbing (MEP) professionals worldwide. "
                 "It replaces expensive commercial tools by providing the same calculation "
                 "accuracy through clean, auditable Python code backed by international standards."),
        SP(0.2),
        h2(st, "1.1  Project Name & Core Identity"),
        body(st, "<b>Full name:</b> OpenMEP — Open Mechanical, Electrical & Plumbing Engineering Suite"),
        body(st, "<b>Repository:</b> github.com/kakarot-oncloud/openmep-suite"),
        body(st, "<b>Author:</b> Luquman A (@kakarot-oncloud)"),
        body(st, "<b>License:</b> MIT — Free to use, modify, and distribute"),
        body(st, "<b>Version:</b> 0.1.0 (stable, production-ready for single-user deployment)"),
        SP(0.2),
        h2(st, "1.2  The Problem OpenMEP Solves"),
        body(st,
            "MEP engineering calculations are repetitive and time-consuming. A single "
            "project can require hundreds of cable sizing checks, cooling load calculations "
            "for dozens of zones, sprinkler hydraulic designs, and Bill of Quantities "
            "generation — all needing to comply with regional standards that differ "
            "significantly between countries."),
        SP(0.1),
        body(st, "Current tools have major drawbacks:"),
        bul(st, "<b>Cost:</b> Commercial tools (Amtech, ETAP, Hevacomp, HAP) cost $2,000–$10,000 per year per seat"),
        bul(st, "<b>Lock-in:</b> Results stored in proprietary file formats that cannot be audited or reused"),
        bul(st, "<b>Single region:</b> Most tools target only one standard (e.g., NEC-only tools miss BS 7671 for GCC engineers)"),
        bul(st, "<b>No API:</b> Cannot integrate calculations into BIM workflows or custom dashboards"),
        bul(st, "<b>Black box:</b> Engineers cannot verify which formula or table the software used"),
        SP(0.2),
        co(st, "OpenMEP solves all of this: it is free, 100% open source, API-first, "
                "covers 4 major regions, and every result includes a reference to the "
                "exact standard clause and table used.", style="good"),
        SP(0.3),
        h2(st, "1.3  Key Features at a Glance"),
        dt(st, ["Feature", "Detail"], [
            ["26 Calculation Modules", "Covering electrical, HVAC, plumbing, and fire protection"],
            ["4 Global Regions",       "GCC/UAE/Saudi/Qatar/Kuwait, Europe/UK, India, Australia"],
            ["35+ REST API Endpoints", "Full FastAPI backend with Swagger/OpenAPI docs at /docs"],
            ["3-Level Region Selector","Region → Country/State → Utility Authority (e.g. DEWA, KAHRAMAA)"],
            ["International Standards","BS 7671, NFPA 13/14/20/22, IS 732/3961, AS/NZS 3000/3008, ASHRAE 90.1"],
            ["PDF Calculation Reports","Professional A4 reports with formula derivations and sign-off fields"],
            ["Excel BOQ Export",       "Bill of Quantities in FIDIC, NRM2, CPWD, AIQS regional formats"],
            ["Docker Deployment",      "Full containerised stack: PostgreSQL + FastAPI + Streamlit"],
            ["Premium UI Theme",       "Custom red/black/white Streamlit theme with Plotly charts"],
            ["Open Source — MIT",      "Free to fork, modify, and deploy. No restrictions."],
            ["Google Colab Support",   "colab_launcher.ipynb allows running in browser without install"],
            ["Submittal Tracker",      "Page 16: project submittal register for engineering drawings"],
        ], [5.5*cm, CONTENT_W - 5.5*cm]),
        SP(0.3),
        h2(st, "1.4  The 26 Calculation Modules"),
        h3(st, "Electrical Engineering (Pages 1–12)"),
        bul(st, "Cable Sizing — select conductor cross-section with full derating factors (Ca, Cg)"),
        bul(st, "Voltage Drop — mV/A/m method with upsize recommendation if non-compliant"),
        bul(st, "Maximum Demand — load schedule with diversity factors per BS 7671 / IS 3961"),
        bul(st, "Short Circuit Analysis — IEC 60909 prospective fault current at MV and LV"),
        bul(st, "Lighting Design — lumen method with maintained illuminance and uniformity ratio"),
        bul(st, "Power Factor Correction — capacitor bank sizing with harmonic derating option"),
        bul(st, "Generator Sizing — ISO 8528 standby/prime ratings with altitude derating"),
        bul(st, "Panel Schedule — distribution board schedule with cable sizing per circuit"),
        bul(st, "UPS Sizing — IEC 62040 UPS capacity with battery autonomy and bypass"),
        h3(st, "HVAC / Mechanical Engineering (Pages 6–7, 17–18)"),
        bul(st, "Cooling Load — ASHRAE CLTD method with regional design conditions (up to 48°C for GCC)"),
        bul(st, "Duct Sizing — SMACNA equal friction method for rectangular and circular ducts"),
        bul(st, "Heating Load — EN 12831 transmission and infiltration losses"),
        bul(st, "Ventilation — ASHRAE 62.1 / AS 1668.2 fresh air rates by occupancy type"),
        h3(st, "Plumbing Engineering (Pages 8, 19–21, 25–26)"),
        bul(st, "Pipe Sizing — loading unit / fixture unit method per regional plumbing codes"),
        bul(st, "Drainage Sizing — discharge unit method for soil and waste stacks"),
        bul(st, "Pump Sizing — Darcy-Weisbach friction loss with pump duty point selection"),
        bul(st, "Hot Water System — CIBSE W / AS/NZS 3500.4 storage and instantaneous systems"),
        bul(st, "Rainwater Harvesting — BS 8515 tank sizing with yield-demand analysis"),
        bul(st, "Plumbing Tank Sizing — break cistern and fire reserve combined tank"),
        h3(st, "Fire Protection (Pages 9, 22–24)"),
        bul(st, "Sprinkler System Design — NFPA 13 / BS EN 12845 hydraulic design by hazard class"),
        bul(st, "Fire Pump Sizing — NFPA 20 pump set with diesel backup and jockey pump"),
        bul(st, "Fire Water Storage Tank — NFPA 22 / BS EN 12845 tank volume calculation"),
        bul(st, "Wet Riser / Standpipe System — NFPA 14 landing valve pressure and flow"),
        SP(0.2),
        h2(st, "1.5  Who Is This Project For?"),
        bul(st, "<b>MEP Engineers:</b> Day-to-day calculations — cable sizing, cooling loads, sprinkler design on-site or in the office"),
        bul(st, "<b>Engineering Students:</b> Learning BS 7671, NFPA, IS codes, and AS/NZS standards through working code"),
        bul(st, "<b>Consultancy Firms:</b> Free alternative to commercial tools with full calculation audit trail"),
        bul(st, "<b>BIM / Digital Engineers:</b> REST API allows integration with BIM workflows, Power BI dashboards, custom tools"),
        bul(st, "<b>Developers:</b> Well-structured FastAPI + Streamlit codebase to learn from or build on top of"),
        bul(st, "<b>Open Source Contributors:</b> 26+ modules and 4 regions — plenty of room to add new standards and disciplines"),
    ]
    return story


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 02 — TECHNOLOGY STACK
# ─────────────────────────────────────────────────────────────────────────────
def section_02(st):
    story = sb(st, "02", "Tech Stack")
    story += [
        lead(st, "Every technology choice in OpenMEP was deliberate. This section explains "
                 "what each tool does, why it was chosen, and what alternatives exist."),
        SP(0.2),
        h2(st, "2.1  Python 3.11+"),
        body(st,
            "Python is the primary language for both the backend (FastAPI) and the frontend UI "
            "(Streamlit). It was chosen for the following reasons:"),
        bul(st, "Engineering and scientific community uses Python universally — numpy, scipy, and pandas are standard"),
        bul(st, "Readable syntax makes complex formula implementations self-documenting"),
        bul(st, "Fastest prototyping language — a new calculation module can be written and tested in hours"),
        bul(st, "Strong typing via Pydantic makes the codebase reliable at scale"),
        bul(st, "Alternatives considered: Julia (smaller community), MATLAB (proprietary), JavaScript (poor maths libraries)"),
        SP(0.2),
        h2(st, "2.2  FastAPI"),
        body(st,
            "FastAPI is a modern, high-performance Python web framework built on Starlette "
            "(for async HTTP) and Pydantic (for data validation). It was chosen because:"),
        bul(st, "Automatic Swagger / OpenAPI documentation is generated directly from code — no manual writing"),
        bul(st, "Pydantic models enforce strict input validation: wrong types, missing fields, and out-of-range values are caught before calculations run"),
        bul(st, "Async support allows the API to handle many concurrent requests without blocking"),
        bul(st, "Route structure is very clean: one function = one endpoint"),
        bul(st, "FastAPI is the fastest Python web framework — benchmarks show 3× the throughput of Flask"),
        bul(st, "Alternatives rejected: Flask (no built-in validation), Django REST (too heavy for a calculation API), Express.js (JavaScript)"),
        SP(0.2),
        h2(st, "2.3  Streamlit"),
        body(st,
            "Streamlit is a Python library that turns Python scripts into interactive web "
            "applications — without writing a single line of HTML, CSS, or JavaScript. "
            "Each of the 26 calculation pages is a standalone Python file."),
        body(st, "Why Streamlit was chosen:"),
        bul(st, "A complete interactive UI page with inputs, buttons, charts, and tables takes fewer than 50 lines of Python"),
        bul(st, "Custom CSS (injected via st.markdown) gives the premium red/black/white theme"),
        bul(st, "The numbered page naming convention (1_Cable_Sizing.py, 2_Voltage_Drop.py) causes Streamlit to auto-generate the sidebar navigation in the correct order"),
        bul(st, "Plotly charts are natively supported — interactive, hoverable engineering charts"),
        bul(st, "Alternatives: Dash (too complex for single developer), Gradio (designed for ML, not engineering), React (requires full JavaScript frontend skill)"),
        SP(0.2),
        h2(st, "2.4  Pydantic v2"),
        body(st,
            "Pydantic is the data validation library that powers FastAPI's request parsing. "
            "OpenMEP defines a Pydantic model for every API request and response. "
            "Pydantic v2 was specifically chosen because it is 5–10× faster than v1 "
            "and has cleaner model inheritance."),
        co(st,
            "Example: If a user submits cable_length_m = -50 (negative length), "
            "Pydantic's Field(gt=0) constraint rejects it immediately with a clear error "
            "message — the calculation engine is never called.", style="info"),
        SP(0.2),
        h2(st, "2.5  ReportLab 4.4"),
        body(st,
            "ReportLab is the industry-standard Python library for generating PDF files. "
            "OpenMEP uses it for:"),
        bul(st, "scripts/generate_tech_docs.py — this documentation file"),
        bul(st, "scripts/generate_pdf_report.py — the 31-page OpenMEP project summary PDF"),
        bul(st, "backend/reports/ — calculation report sheets generated on-demand via the /api/reports/calculation-report endpoint"),
        SP(0.2),
        h2(st, "2.6  openpyxl"),
        body(st,
            "openpyxl reads and writes Excel (.xlsx) files. The BOQ Generator (page 13) "
            "uses it to produce Bill of Quantities spreadsheets in the correct regional "
            "format — FIDIC for GCC, NRM2 for UK/Europe, CPWD for India, AIQS for Australia."),
        SP(0.2),
        h2(st, "2.7  NumPy"),
        body(st,
            "NumPy provides fast array operations. It is used in the cooling load and "
            "hydraulic calculations where arrays of temperature-correction factors or "
            "friction loss values are computed at once rather than in loops."),
        SP(0.2),
        h2(st, "2.8  Plotly"),
        body(st,
            "Plotly renders interactive charts inside Streamlit. Examples: "
            "the panel schedule page shows a bar chart of circuit loads, "
            "the cooling load page shows a pie chart of heat gain breakdown, "
            "and the maximum demand page shows a stacked bar of load categories."),
        SP(0.2),
        h2(st, "2.9  Docker & Docker Compose"),
        body(st,
            "Docker packages the application into containers so it runs identically on any machine. "
            "Docker Compose coordinates three containers (services) together:"),
        dt(st, ["Service", "Image / Build", "Port", "Purpose"], [
            ["db",        "postgres:16-alpine",     "5432 (internal)", "PostgreSQL database for project persistence"],
            ["api",       "Builds from Dockerfile", "8000",            "FastAPI calculation engine"],
            ["streamlit", "Builds from Dockerfile", "8501",            "Streamlit user interface"],
        ], [2.2*cm, 4.2*cm, 3.8*cm, CONTENT_W - 10.2*cm]),
        SP(0.2),
        h2(st, "2.10  Complete Dependency Reference"),
        dt(st, ["Package", "Min Version", "Why It Is Used"], [
            ["fastapi",           "0.109", "REST API framework — routing, validation, docs generation"],
            ["uvicorn[standard]", "0.27",  "ASGI server — runs FastAPI in production and development"],
            ["pydantic",          "2.5",   "Request/response model validation and serialisation"],
            ["pydantic-settings", "2.1",   "Reads .env file into typed Settings class"],
            ["python-multipart",  "0.0.6", "Enables file upload and form data support in FastAPI"],
            ["python-dotenv",     "1.0",   "Loads .env variables into os.environ at startup"],
            ["reportlab",         "4.0",   "PDF generation for reports and this documentation"],
            ["openpyxl",          "3.1",   "Excel (.xlsx) BOQ file generation"],
            ["numpy",             "1.26",  "Vectorised numerical calculations"],
            ["httpx",             "0.26",  "Async HTTP client for integration tests"],
            ["pytest",            "7.4",   "Unit test framework"],
            ["pytest-asyncio",    "0.23",  "Async function support inside pytest"],
            ["streamlit",         "1.30",  "26-page interactive web UI"],
            ["plotly",            "5.20",  "Interactive charts inside Streamlit pages"],
            ["pandas",            "2.0",   "DataFrame manipulation for BOQ and tables"],
            ["requests",          "2.31",  "Synchronous HTTP calls from Streamlit to FastAPI"],
        ], [3.8*cm, 2.8*cm, CONTENT_W - 6.6*cm]),
    ]
    return story


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 03 — PROJECT STRUCTURE
# ─────────────────────────────────────────────────────────────────────────────
def section_03(st):
    story = sb(st, "03", "Project Structure")
    story += [
        lead(st, "Understanding the folder layout is essential before modifying the project. "
                 "Every directory and file has a specific role. Nothing is placed randomly."),
        SP(0.2),
        h2(st, "3.1  Root Directory Layout"),
    ]
    story += cb(st, "Root level (top-level files and directories):", [
        "openmep/                          <- project root",
        "|",
        "+-- backend/                      <- FastAPI application (calculation engine + REST API)",
        "+-- streamlit_app/                <- Streamlit UI (26 interactive pages)",
        "+-- docs/                         <- All documentation, guides, and PDF reports",
        "+-- scripts/                      <- Utility scripts (PDF generators)",
        "+-- .github/                      <- GitHub Actions, issue templates, PR templates",
        "+-- frontend/                     <- Placeholder for future React/TypeScript frontend",
        "+-- lib/                          <- Shared utility libraries",
        "|",
        "+-- docker-compose.yml            <- Defines db + api + streamlit services",
        "+-- Dockerfile                    <- Single Dockerfile for both api and streamlit containers",
        "+-- requirements.txt              <- Python dependencies",
        "+-- .env.example                  <- Environment variable template (copy to .env)",
        "+-- pyproject.toml                <- Python project metadata",
        "+-- colab_launcher.ipynb          <- Google Colab one-click launcher",
        "|",
        "+-- README.md                     <- Project introduction, quick start, feature matrix",
        "+-- LICENSE                       <- MIT License -- Copyright 2025 Luquman A",
        "+-- CONTRIBUTING.md               <- How to open issues, write code, submit PRs",
        "+-- CODE_OF_CONDUCT.md            <- Community behaviour standards",
        "+-- SECURITY.md                   <- How to report vulnerabilities",
        "+-- CHANGELOG.md                  <- Version history and what changed in each release",
    ])
    story += [
        SP(0.3),
        h2(st, "3.2  Backend Directory (FastAPI Application)"),
    ]
    story += cb(st, "backend/ -- every folder explained:", [
        "backend/",
        "|",
        "+-- main.py                       <- APP ENTRY POINT: creates FastAPI app, registers all routers",
        "+-- config.py                     <- Settings class + all region/sub-region/authority maps",
        "+-- __init__.py                   <- Makes backend a Python package",
        "|",
        "+-- api/                          <- All HTTP route handlers",
        "|   +-- routes/",
        "|       +-- electrical.py         <- 9 routes: cable sizing, VD, demand, SC, lighting, PF, gen, panel, UPS",
        "|       +-- mechanical.py         <- 5 routes: cooling load, duct, heating, ventilation, multi-zone",
        "|       +-- plumbing.py           <- 6 routes: pipe, drainage, pump, HWS, rainwater, tank",
        "|       +-- fire.py               <- 4 routes: sprinkler, fire pump, fire tank, standpipe",
        "|       +-- boq.py                <- 2 routes: generate BOQ, get rates",
        "|       +-- compliance.py         <- 2 routes: compliance check, standards reference",
        "|       +-- reports.py            <- 3 routes: calc report, templates, standards data",
        "+-- engines/                      <- Pure calculation logic (no HTTP, no UI)",
        "|   +-- electrical/               <- cable_sizing.py, voltage_drop.py, demand_load.py,",
        "|   |                                short_circuit.py, lighting.py, pf_correction.py,",
        "|   |                                generator_sizing.py, panel_schedule.py, ups_sizing.py",
        "|   +-- mechanical/               <- cooling_load.py, duct_sizing.py",
        "|   +-- plumbing/                 <- pipe_sizing.py",
        "|   +-- fire/                     <- sprinkler_calc.py",
        "|   +-- adapters_factory.py       <- get_electrical_adapter(region, sub_region) -> adapter",
        "+-- adapters/                     <- Regional standards data (tables, factors, limits)",
        "|   +-- base_adapter.py           <- Abstract base class all adapters must implement",
        "|   +-- gcc_adapter.py            <- BS 7671 @ GCC design conditions",
        "|   +-- europe_adapter.py         <- BS 7671 @ European design conditions",
        "|   +-- india_adapter.py          <- IS 3961 / IS 732 @ Indian design conditions",
        "|   +-- australia_adapter.py      <- AS/NZS 3008 @ Australian design conditions",
        "+-- standards_data/               <- JSON/Python files: cable rating tables, correction factors",
        "+-- boq/                          <- BOQ generation engine and regional rate tables",
        "+-- compliance/                   <- Compliance matrix checker",
        "+-- reports/                      <- Calculation report data generator",
        "+-- tests/                        <- pytest unit tests for engines",
    ])
    story += [
        SP(0.3),
        h2(st, "3.3  Streamlit App Directory"),
    ]
    story += cb(st, "streamlit_app/ -- all 26 pages:", [
        "streamlit_app/",
        "+-- app.py                        <- Landing page: hero banner, stats, module grid, API status",
        "+-- utils.py                      <- SHARED UTILITIES: API_BASE, region_selector(), api_post(),",
        "|                                    colour constants (RED, BLACK, WHITE, DARK_GREY)",
        "+-- report_generator.py           <- Generates PDF reports from within Streamlit",
        "|",
        "+-- pages/                        <- Numbered pages -- Streamlit reads these in order",
        "    +-- 1_Cable_Sizing.py         Electrical: conductor selection with full derating",
        "    +-- 2_Voltage_Drop.py         Electrical: voltage drop for a known cable size",
        "    +-- 3_Maximum_Demand.py       Electrical: load schedule diversity calculation",
        "    +-- 4_Short_Circuit.py        Electrical: IEC 60909 prospective fault current",
        "    +-- 5_Lighting.py             Electrical: lumen method illuminance design",
        "    +-- 6_Cooling_Load.py         HVAC: ASHRAE CLTD zone cooling load",
        "    +-- 7_Duct_Sizing.py          HVAC: SMACNA equal friction duct sizing",
        "    +-- 8_Pipe_Sizing.py          Plumbing: loading unit cold/hot water pipe sizing",
        "    +-- 9_Sprinkler_Design.py     Fire: BS EN 12845 / NFPA 13 sprinkler hydraulics",
        "    +-- 10_Panel_Schedule.py      Electrical: full DB panel schedule generator",
        "    +-- 11_Generator_Sizing.py    Electrical: ISO 8528 genset sizing with derating",
        "    +-- 12_PF_Correction.py       Electrical: capacitor bank and kVAr sizing",
        "    +-- 13_BOQ_Generator.py       All disciplines: regional BOQ with unit rates",
        "    +-- 14_Compliance_Checker.py  All disciplines: multi-standard compliance matrix",
        "    +-- 15_PDF_Reports.py         All disciplines: professional PDF report generator",
        "    +-- 16_Submittal_Tracker.py   Project management: engineering submittal register",
        "    +-- 17_Heating_Load.py        HVAC: EN 12831 transmission + infiltration losses",
        "    +-- 18_Ventilation.py         HVAC: ASHRAE 62.1 / AS 1668.2 fresh air rates",
        "    +-- 19_Drainage_Sizing.py     Plumbing: discharge unit soil and waste stacks",
        "    +-- 20_Pump_Sizing.py         Plumbing: Darcy-Weisbach pump duty and selection",
        "    +-- 21_Hot_Water_System.py    Plumbing: CIBSE W / AS/NZS 3500.4 HWS design",
        "    +-- 22_Fire_Pump.py           Fire: NFPA 20 fire pump set with diesel backup",
        "    +-- 23_Fire_Tank.py           Fire: NFPA 22 / BS EN 12845 fire water storage",
        "    +-- 24_Standpipe.py           Fire: NFPA 14 wet riser landing valve analysis",
        "    +-- 25_Rainwater_Harvesting.py Plumbing: BS 8515 RWH tank yield-demand",
        "    +-- 26_Plumbing_Tank_Sizing.py Plumbing: break cistern + fire reserve tank",
    ])
    story += [
        SP(0.3),
        h2(st, "3.4  How the Files Connect"),
        body(st, "The connection between files follows a clean dependency graph:"),
    ]
    story += cb(st, "File dependency map (-> means 'imports / calls'):", [
        "Streamlit Pages (26 files in pages/)",
        "   -> streamlit_app/utils.py            (region_selector, api_post, colour constants)",
        "   -> FastAPI via HTTP POST/GET",
        "",
        "streamlit_app/utils.py",
        "   -> os.environ API_BASE               (reads environment variable)",
        "   -> requests library                  (HTTP calls to FastAPI)",
        "",
        "FastAPI backend/main.py",
        "   -> backend/api/routes/*.py            (7 route modules registered with prefix /api)",
        "   -> backend/config.py                  (settings object, region maps)",
        "",
        "backend/api/routes/electrical.py        (and all other route files)",
        "   -> backend/models/electrical.py       (Pydantic request/response models)",
        "   -> backend/engines/electrical/*.py    (calculation engines)",
        "",
        "backend/engines/electrical/cable_sizing.py",
        "   -> backend/engines/adapters_factory.py (get_electrical_adapter(region, sub))",
        "   -> backend/adapters/gcc_adapter.py    (cable tables, derating factors)",
        "   -> backend/adapters/base_adapter.py   (abstract interface)",
    ])
    return story


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 04 — CODE DEEP-DIVE
# ─────────────────────────────────────────────────────────────────────────────
def section_04(st):
    story = sb(st, "04", "Full Code Explanation")
    story += [
        lead(st, "This section walks through every important file with actual code "
                 "and a clear explanation of what each part does and why it was written that way."),
        SP(0.2),
        h2(st, "4.1  backend/main.py — The Application Entry Point"),
        body(st,
            "main.py is the first file that runs. It creates the FastAPI application "
            "object, configures Cross-Origin Resource Sharing (CORS), and registers "
            "all seven route modules."),
    ]
    story += cb(st, "backend/main.py -- complete annotated listing:", [
        '"""',
        "OpenMEP FastAPI Application -- Entry Point",
        "Run: uvicorn backend.main:app --reload --port 8000",
        '"""',
        "",
        "from fastapi import FastAPI",
        "from fastapi.middleware.cors import CORSMiddleware",
        "from fastapi.responses import JSONResponse",
        "",
        "from backend.api.routes import electrical, mechanical, plumbing, fire, boq, compliance, reports",
        "from backend.config import settings",
        "",
        "# 1 -- Create the FastAPI app with rich metadata",
        "app = FastAPI(",
        '    title="OpenMEP API",',
        '    description="Open-Source MEP Engineering Calculation Suite",',
        '    version="0.1.0",',
        "    docs_url='/docs',",
        "    redoc_url='/redoc',",
        ")",
        "",
        "# 2 -- CORS middleware: allows Streamlit (any origin) to call the API",
        "app.add_middleware(",
        "    CORSMiddleware,",
        "    allow_origins=['*'],",
        "    allow_credentials=True,",
        "    allow_methods=['*'],",
        "    allow_headers=['*'],",
        ")",
        "",
        "# 3 -- Register discipline routers -- each gets the /api prefix",
        "app.include_router(electrical.router,   prefix='/api')",
        "app.include_router(mechanical.router,   prefix='/api')",
        "app.include_router(plumbing.router,     prefix='/api')",
        "app.include_router(fire.router,         prefix='/api')",
        "app.include_router(boq.router,          prefix='/api')",
        "app.include_router(compliance.router,   prefix='/api')",
        "app.include_router(reports.router,      prefix='/api')",
        "",
        "# 4 -- Root endpoint",
        "@app.get('/', tags=['Status'])",
        "async def root():",
        "    return {'name': 'OpenMEP API', 'version': '0.1.0',",
        "            'status': 'operational',",
        "            'regions': ['gcc', 'europe', 'india', 'australia'],",
        "            'docs': '/docs'}",
        "",
        "# 5 -- Health check -- used by Docker Compose healthcheck",
        "@app.get('/health', tags=['Status'])",
        "async def health():",
        "    return {'status': 'healthy', 'service': 'openmep-api'}",
        "",
        "# 6 -- Global exception handler",
        "@app.exception_handler(Exception)",
        "async def global_exception_handler(request, exc):",
        "    return JSONResponse(status_code=500,",
        "        content={'status': 'error', 'message': str(exc), 'type': type(exc).__name__})",
    ])
    story += [
        SP(0.2),
        co(st,
            "Why prefix='/api'? All route files define their own sub-prefix "
            "(e.g., prefix='/electrical' in electrical.py). Combining them gives "
            "/api/electrical/cable-sizing. This namespacing makes the API "
            "self-documenting and safe to version later (/api/v2/...).",
            style="info"),
        SP(0.3),
        h2(st, "4.2  backend/config.py — Settings & Region Hierarchy"),
        body(st,
            "config.py defines the geographic hierarchy that powers the 3-level region "
            "selector. It also uses pydantic-settings to load environment variables "
            "from a .env file automatically."),
    ]
    story += cb(st, "backend/config.py -- annotated:", [
        "from pydantic_settings import BaseSettings",
        "from pathlib import Path",
        "",
        "BASE_DIR = Path(__file__).parent",
        "STANDARDS_DATA_DIR = BASE_DIR / 'standards_data'",
        "",
        "# Level 1 -- top-level region codes (used in API request body)",
        "SUPPORTED_REGIONS = ['gcc', 'europe', 'india', 'australia']",
        "",
        "# Level 2 -- country/emirate/state within each region",
        "GCC_SUB_REGIONS = {",
        '    "uae_dubai":    {"name": "UAE - Dubai",     "authority": "DEWA"},',
        '    "uae_abudhabi": {"name": "UAE - Abu Dhabi", "authority": "ADDC"},',
        '    "uae_sharjah":  {"name": "UAE - Sharjah",   "authority": "SEWA"},',
        '    "saudi":        {"name": "Saudi Arabia",    "authority": "SEC/SBC"},',
        '    "qatar":        {"name": "Qatar",           "authority": "KAHRAMAA"},',
        '    "kuwait":       {"name": "Kuwait",          "authority": "MEW"},',
        '    "bahrain":      {"name": "Bahrain",         "authority": "EWA"},',
        '    "oman":         {"name": "Oman",            "authority": "OETC"},',
        "}",
        "",
        "# Settings class -- reads .env file via pydantic-settings",
        "class Settings(BaseSettings):",
        '    app_name: str = "OpenMEP API"',
        '    version: str = "0.1.0"',
        "    debug: bool = False",
        "    class Config:",
        "        env_file = '.env'",
        "",
        "settings = Settings()  # Singleton -- import this wherever settings are needed",
    ])
    story += [
        SP(0.3),
        h2(st, "4.3  streamlit_app/utils.py — Shared Utilities for All 26 Pages"),
        body(st,
            "utils.py is the most-imported file in the project. Every one of the 26 "
            "Streamlit pages imports from it. It provides four things:"),
        bul(st, "Colour constants (RED, BLACK, WHITE, DARK_GREY, MID_GREY, LIGHT_GREY)"),
        bul(st, "API_BASE — the URL of the FastAPI backend, read from environment"),
        bul(st, "region_selector() — the 3-level dropdown widget used on every page"),
        bul(st, "api_post() and api_get() — safe HTTP wrapper functions with error handling"),
    ]
    story += cb(st, "streamlit_app/utils.py -- key sections annotated:", [
        "import os, streamlit as st, requests",
        "",
        "# Theme colour constants",
        "RED        = '#CC0000'",
        "BLOOD_RED  = '#8B0000'",
        "BLACK      = '#0A0A0A'",
        "WHITE      = '#FFFFFF'",
        "DARK_GREY  = '#1A1A1A'",
        "",
        "# API base URL",
        "API_BASE = os.environ.get('API_BASE', 'http://localhost:8000').rstrip('/')",
        "",
        "# 3-level region selector",
        "def region_selector(key='rs'):",
        "    region_label = st.selectbox('Select Region', list(REGIONS.keys()),",
        "                                key=f'{key}_r')",
        "    region = REGIONS[region_label]",
        "    l2_options = list(SUB_REGIONS_L2[region].keys())",
        "    l2_label = st.selectbox('Country / State', l2_options, key=f'{key}_l2')",
        "    l2_code = SUB_REGIONS_L2[region][l2_label]",
        "    l3_options = list(SUB_REGIONS_L3.get(l2_code, {}).keys())",
        "    if l3_options:",
        "        l3_label = st.selectbox('Utility Authority', l3_options, key=f'{key}_l3')",
        "        sub_region = SUB_REGIONS_L3[l2_code][l3_label]",
        "    else:",
        "        sub_region = l2_code",
        "    return region, sub_region",
        "",
        "# API call wrapper",
        "def api_post(endpoint, payload):",
        "    try:",
        "        r = requests.post(f'{API_BASE}{endpoint}', json=payload, timeout=30)",
        "        r.raise_for_status()",
        "        return r.json()",
        "    except requests.exceptions.ConnectionError:",
        "        st.error('Cannot connect to OpenMEP API. Is the backend running?')",
        "        return None",
        "    except requests.exceptions.Timeout:",
        "        st.error('API request timed out after 30 seconds.')",
        "        return None",
        "    except requests.exceptions.HTTPError as e:",
        "        st.error(f'API error {r.status_code}: {r.json()}')",
        "        return None",
    ])
    story += [
        SP(0.3),
        h2(st, "4.4  A Complete Streamlit Page — Pattern Explained"),
        body(st,
            "All 26 pages follow the same 5-step pattern. Understanding one page means "
            "understanding all 26."),
    ]
    story += cb(st, "Streamlit page pattern (1_Cable_Sizing.py structure):", [
        '"""',
        "OpenMEP -- Cable Sizing (Page 1)",
        "Implements: BS 7671 / IS 3961 / AS/NZS 3008 / IEC 60364",
        '"""',
        "import streamlit as st",
        "import plotly.graph_objects as go",
        "from utils import region_selector, api_post, RED, BLACK, WHITE, DARK_GREY",
        "",
        "# STEP 1: Page configuration and theme CSS",
        "st.set_page_config(page_title='Cable Sizing | OpenMEP', layout='wide')",
        "st.markdown(f'<style> ... custom CSS ... </style>', unsafe_allow_html=True)",
        "",
        "# STEP 2: Page title and description",
        "st.title('Cable Sizing')",
        "st.caption('BS 7671:2018+A2:2022  .  IS 3961  .  AS/NZS 3008  .  IEC 60364')",
        "",
        "# STEP 3: Region selector (3 dropdowns returned as tuple)",
        "region, sub_region = region_selector(key='cs')",
        "",
        "# STEP 4: Input form -- all inputs collected before API call",
        "with st.form('cable_form'):",
        "    col1, col2, col3 = st.columns(3)",
        "    with col1:",
        "        load_kw = st.number_input('Active Load (kW)', min_value=0.1, value=45.0)",
        "        pf      = st.number_input('Power Factor', min_value=0.1, max_value=1.0, value=0.85)",
        "        phases  = st.selectbox('Phases', [3, 1])",
        "    with col2:",
        "        cable_len  = st.number_input('Cable Length (m)', min_value=1.0, value=80.0)",
        "        cable_type = st.selectbox('Cable Type', ['XLPE_CU', 'PVC_CU', 'XLPE_AL'])",
        "        method     = st.selectbox('Installation Method', ['C','B1','B2','A1','A2','E','F'])",
        "    with col3:",
        "        ambient  = st.number_input('Ambient Temp (C)', value=40.0)",
        "        grouped  = st.number_input('Grouped Circuits', min_value=1, value=1)",
        "        ctype    = st.selectbox('Circuit Type', ['power', 'lighting'])",
        "    submitted = st.form_submit_button('Calculate', type='primary')",
        "",
        "# STEP 5: Call API, display results",
        "if submitted:",
        "    result = api_post('/api/electrical/cable-sizing', {",
        "        'region': region, 'sub_region': sub_region,",
        "        'load_kw': load_kw, 'power_factor': pf, 'phases': phases,",
        "        'cable_length_m': cable_len, 'cable_type': cable_type,",
        "        'installation_method': method, 'ambient_temp_c': ambient,",
        "        'num_grouped_circuits': grouped, 'circuit_type': ctype,",
        "    })",
        "    if result:",
        "        c1, c2, c3, c4 = st.columns(4)",
        "        c1.metric('Selected Cable', f'{result[\"selected_size_mm2\"]} mm2')",
        "        c2.metric('Design Current', f'{result[\"design_current_ib_a\"]} A')",
        "        c3.metric('Derated Rating', f'{result[\"derated_rating_iz_a\"]} A')",
        "        c4.metric('Voltage Drop', f'{result[\"voltage_drop_pct\"]}%')",
        "        st.table({'Ca (ambient)': [result['ca_factor']],",
        "                  'Cg (grouping)': [result['cg_factor']],",
        "                  'Iz derated (A)': [result['derated_rating_iz_a']]})",
    ])
    story += [
        SP(0.3),
        h2(st, "4.5  A FastAPI Route File — electrical.py"),
        body(st,
            "Route files define the API contract: what inputs the endpoint accepts, "
            "what validations apply, and which engine function to call."),
    ]
    story += cb(st, "backend/api/routes/electrical.py -- cable sizing route:", [
        "from fastapi import APIRouter",
        "from pydantic import BaseModel, Field",
        "from typing import Optional",
        "from backend.engines.electrical.cable_sizing import CableSizingInput, calculate_cable_sizing",
        "",
        "router = APIRouter(prefix='/electrical', tags=['Electrical Engineering'])",
        "",
        "class CableSizingRequest(BaseModel):",
        "    region: str = 'gcc'",
        "    sub_region: str = ''",
        "    load_kw: float = Field(gt=0, description='Active load in kW')",
        "    power_factor: float = Field(default=0.85, ge=0.1, le=1.0)",
        "    phases: int = Field(default=3)",
        "    cable_type: str = 'XLPE_CU'",
        "    installation_method: str = 'C'",
        "    cable_length_m: float = Field(gt=0)",
        "    ambient_temp_c: Optional[float] = None",
        "    num_grouped_circuits: int = Field(default=1, ge=1)",
        "    circuit_type: str = 'power'",
        "",
        "@router.post('/cable-sizing')",
        "async def cable_sizing(req: CableSizingRequest):",
        "    inp = CableSizingInput(",
        "        region=req.region, sub_region=req.sub_region,",
        "        load_kw=req.load_kw, cable_length_m=req.cable_length_m,",
        "        cable_type=req.cable_type,",
        "        installation_method=req.installation_method,",
        "        ambient_temp_c=req.ambient_temp_c,",
        "        num_grouped_circuits=req.num_grouped_circuits,",
        "    )",
        "    return calculate_cable_sizing(inp)",
    ])
    story += [
        SP(0.3),
        h2(st, "4.6  The Calculation Engine — cable_sizing.py"),
        body(st,
            "Engines contain pure Python logic. No HTTP, no Streamlit. "
            "They take dataclass inputs and return dataclass outputs — "
            "making them fully testable in isolation."),
    ]
    story += cb(st, "backend/engines/electrical/cable_sizing.py -- structure:", [
        "@dataclass",
        "class CableSizingInput:",
        "    region: str",
        "    sub_region: str = ''",
        "    load_kw: float = 0.0",
        "    power_factor: float = 0.85",
        "    phases: int = 3",
        "    voltage_v: Optional[float] = None",
        "    cable_type: str = 'XLPE_CU'",
        "    installation_method: str = 'C'",
        "    cable_length_m: float = 50.0",
        "    ambient_temp_c: Optional[float] = None",
        "    num_grouped_circuits: int = 1",
        "    circuit_type: str = 'power'",
        "",
        "@dataclass",
        "class CableSizingResult:",
        "    standard: str = ''",
        "    authority: str = ''",
        "    design_current_ib_a: float = 0.0",
        "    selected_size_mm2: float = 0.0",
        "    tabulated_rating_it_a: float = 0.0",
        "    ca_factor: float = 1.0",
        "    cg_factor: float = 1.0",
        "    derated_rating_iz_a: float = 0.0",
        "    voltage_drop_pct: float = 0.0",
        "    voltage_drop_pass: bool = True",
        "    earth_conductor_mm2: float = 0.0",
        "    overall_compliant: bool = True",
        "",
        "def calculate_cable_sizing(inp: CableSizingInput) -> CableSizingResult:",
        "    adapter = get_electrical_adapter(inp.region, inp.sub_region)",
        "    voltage = inp.voltage_v or (adapter.voltage_lv if inp.phases == 3",
        "                                else adapter.voltage_phase)",
        "    if inp.phases == 3:",
        "        Ib = (inp.load_kw * 1000) / (math.sqrt(3) * voltage * inp.power_factor)",
        "    else:",
        "        Ib = (inp.load_kw * 1000) / (voltage * inp.power_factor)",
        "    ambient = inp.ambient_temp_c or adapter.design_ambient_temp",
        "    Ca = adapter.get_ambient_temp_factor(ambient, inp.cable_type)",
        "    Cg = adapter.get_grouping_factor(inp.num_grouped_circuits)",
        "    required_it = Ib / (Ca * Cg)",
        "    selected = None",
        "    for size in sorted(adapter.get_standard_cable_sizes()):",
        "        It = adapter.get_tabulated_rating(size, inp.cable_type, inp.installation_method)",
        "        if It >= required_it:",
        "            selected = size",
        "            selected_It = It",
        "            break",
        "    mv_am = adapter.get_voltage_drop_mv_am(inp.cable_type, selected, inp.phases)",
        "    vd_mv = Ib * inp.cable_length_m * mv_am",
        "    vd_pct = (vd_mv / 1000 / voltage) * 100",
        "    vd_limit = adapter.get_voltage_drop_limit(inp.circuit_type)",
        "    earth = adapter.get_earth_conductor_size(selected)",
        "    return CableSizingResult(",
        "        design_current_ib_a=round(Ib, 2), selected_size_mm2=selected,",
        "        ca_factor=Ca, cg_factor=Cg,",
        "        derated_rating_iz_a=round(selected_It * Ca * Cg, 1),",
        "        voltage_drop_pct=round(vd_pct, 2),",
        "        voltage_drop_pass=(vd_pct <= vd_limit),",
        "        earth_conductor_mm2=earth,",
        "        overall_compliant=(vd_pct <= vd_limit),",
        "        standard=adapter.cable_sizing_standard,",
        "        authority=adapter.authority,",
        "    )",
    ])
    story += [
        SP(0.3),
        h2(st, "4.7  The Voltage Drop Engine — voltage_drop.py"),
        body(st,
            "The voltage drop module calculates voltage drop for a known cable size "
            "and recommends a larger size if the result is non-compliant:"),
    ]
    story += cb(st, "backend/engines/electrical/voltage_drop.py -- key logic:", [
        "def calculate_voltage_drop(inp: VoltageDrop) -> VoltageDropResult:",
        "    adapter = get_electrical_adapter(inp.region, inp.sub_region)",
        "    voltage = inp.voltage_v or (adapter.voltage_lv if inp.phases==3",
        "                                else adapter.voltage_phase)",
        "    vd_mv_am = adapter.get_voltage_drop_mv_am(inp.cable_type,",
        "                   inp.conductor_size_mm2, inp.phases)",
        "    vd_total_mv = inp.design_current_a * inp.cable_length_m * vd_mv_am",
        "    vd_total_v  = vd_total_mv / 1000",
        "    vd_pct      = (vd_total_v / voltage) * 100",
        "    vd_limit    = adapter.get_voltage_drop_limit(inp.circuit_type)",
        "    compliant   = vd_pct <= vd_limit",
        "    if not compliant:",
        "        for size in adapter.get_standard_cable_sizes():",
        "            if size > inp.conductor_size_mm2:",
        "                new_mv = (inp.design_current_a * inp.cable_length_m *",
        "                          adapter.get_voltage_drop_mv_am(inp.cable_type, size, inp.phases))",
        "                if (new_mv / 1000 / voltage * 100) <= vd_limit:",
        "                    result.recommended_size_mm2 = size",
        "                    break",
    ])
    return story


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 05 — ALGORITHMS
# ─────────────────────────────────────────────────────────────────────────────
def section_05(st):
    story = sb(st, "05", "Core Logic & Algorithms")
    story += [
        lead(st, "Every calculation in OpenMEP is derived from a published engineering standard. "
                 "This section explains the formulas, the step-by-step logic, and why certain "
                 "design values are used for each region."),
        SP(0.2),
        h2(st, "5.1  Cable Sizing — Full Algorithm (BS 7671 / IS 3961 / AS/NZS 3008)"),
    ]
    story += cb(st, "ALGORITHM: Cable Sizing (all regions)", [
        "================================================================",
        "STEP 1 -- Calculate Design Current (Ib)",
        "================================================================",
        "  3-phase balanced load:",
        "    Ib = (P_kW x 1000) / (sqrt(3) x V_L-L x PF)     [Amperes]",
        "",
        "  Single-phase load:",
        "    Ib = (P_kW x 1000) / (V_L-N x PF)                [Amperes]",
        "",
        "  Where:",
        "    P_kW = active load in kilowatts",
        "    V_L-L = line-to-line voltage (400V for GCC/Europe, 415V for India/Aus)",
        "    V_L-N = line-to-neutral voltage (230V for all regions)",
        "    PF   = power factor (typically 0.85-0.90 for motors/general loads)",
        "",
        "================================================================",
        "STEP 2 -- Determine Derating Factors",
        "================================================================",
        "  Ca = Ambient Temperature Correction Factor (BS 7671 Table 4C1):",
        "    Depends on cable conductor temperature rating (90C XLPE, 70C PVC)",
        "    GCC design ambient: 40C  --> Ca(XLPE) = 0.91",
        "    Europe design:      25C  --> Ca(XLPE) = 1.04",
        "    India design:       45C  --> Ca(XLPE) = 0.87",
        "    Australia design:   35C  --> Ca(XLPE) = 0.96",
        "",
        "  Cg = Grouping Factor (BS 7671 Table 4C3):",
        "    1 cable  (no grouping):  Cg = 1.00",
        "    2 cables touching:       Cg = 0.80",
        "    3 cables touching:       Cg = 0.70",
        "    4-5 cables touching:     Cg = 0.65",
        "    6-9 cables touching:     Cg = 0.60",
        "    10-14 cables:            Cg = 0.55",
        "    15-24 cables:            Cg = 0.50",
        "",
        "================================================================",
        "STEP 3 -- Select Cable Size",
        "================================================================",
        "  Required tabulated current:  It_required = Ib / (Ca x Cg)",
        "",
        "  Iterate standard cable sizes (mm2) in ascending order:",
        "  [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]",
        "",
        "  Select smallest size where: It_tabulated >= It_required",
        "  Derated capacity:  Iz = It_tabulated x Ca x Cg",
        "  Must satisfy:      Iz >= Ib",
        "",
        "================================================================",
        "STEP 4 -- Check Voltage Drop (BS 7671 Section 525)",
        "================================================================",
        "  VD (mV) = (mV/A/m) x Ib x L",
        "            mV/A/m: from BS 7671 Table 4D5B (or IS/AS equivalent)",
        "            L: cable length in metres (one-way)",
        "",
        "  VD (%) = VD_mV / (V_supply x 1000) x 100",
        "",
        "  Limits (BS 7671 Appendix 12):",
        "    Power circuits:    <= 4%  (3% recommended for GCC DEWA/ADDC)",
        "    Lighting circuits: <= 3%",
        "    Motor terminals:   <= 5% at full load",
        "",
        "================================================================",
        "STEP 5 -- Earth Conductor Sizing (BS 7671 Table 54.7)",
        "================================================================",
        "  Phase conductor (mm2) --> Minimum earth conductor (mm2):",
        "  <= 16 mm2  -->  Same as phase conductor",
        "  25-35 mm2  -->  16 mm2",
        "  > 35 mm2   -->  Phase / 2 (rounded to next standard size)",
    ])
    story += [
        SP(0.3),
        h2(st, "5.2  Voltage Drop Formula Details"),
    ]
    story += cb(st, "mV/A/m values from BS 7671 Table 4D5B (XLPE Copper, Method C):", [
        "Size (mm2) | 3-phase (mV/A/m) | 1-phase (mV/A/m)",
        "-----------+-----------------+-----------------",
        "   2.5     |     15.0        |     18.0",
        "   4       |      9.5        |     11.5",
        "   6       |      6.4        |      7.6",
        "  10       |      3.8        |      4.6",
        "  16       |      2.4        |      2.9",
        "  25       |      1.5        |      1.85",
        "  35       |      1.1        |      1.35",
        "  50       |      0.82       |      0.99",
        "  70       |      0.57       |      0.69",
        "  95       |      0.41       |      0.51",
        "  120      |      0.33       |      0.40",
        "  150      |      0.27       |      0.33",
        "  185      |      0.22       |      0.27",
        "  240      |      0.17       |      0.21",
        "",
        "Example calculation:",
        "  16mm2 XLPE Cu, Method C, 3-phase, 80A design current, 100m run:",
        "  VD = 80 x 100 x 2.4 mV/A/m = 19,200 mV = 19.2 V",
        "  VD% = 19.2 / 400 x 100 = 4.8%  --> EXCEEDS 4% limit --> upsize to 25mm2",
        "  25mm2: VD = 80 x 100 x 1.5 = 12,000 mV = 12 V = 3.0%  --> PASS",
    ])
    story += [
        SP(0.3),
        h2(st, "5.3  ASHRAE CLTD Cooling Load Algorithm"),
    ]
    story += cb(st, "ALGORITHM: Zone Cooling Load Calculation", [
        "================================================================",
        "REGIONAL DESIGN CONDITIONS:",
        "================================================================",
        "  GCC/UAE:       Outdoor 46C DB / 28C WB;  Indoor 24C / 50% RH",
        "  GCC/Saudi:     Outdoor 48C DB / 20C WB;  Indoor 24C / 50% RH",
        "  GCC/Qatar:     Outdoor 45C DB / 29C WB;  Indoor 24C / 50% RH",
        "  Europe/UK:     Outdoor 30C DB / 21C WB;  Indoor 22C / 50% RH",
        "  India (Delhi): Outdoor 42C DB / 26C WB;  Indoor 24C / 55% RH",
        "  Australia:     Outdoor 35C DB / 23C WB;  Indoor 23C / 50% RH",
        "",
        "================================================================",
        "LOAD COMPONENTS:",
        "================================================================",
        "1. Solar heat gain through glass:",
        "   Q_solar = A_glass x SHGC x I_solar x shading_factor",
        "",
        "2. Conduction through glass:",
        "   Q_glass_cond = A_glass x U_glass x CLTD_glass",
        "   CLTD_glass = T_outdoor - T_indoor  (simplified)",
        "",
        "3. Conduction through walls:",
        "   Q_wall = A_wall x U_wall x CLTD_wall",
        "   CLTD_wall accounts for thermal mass time-lag",
        "",
        "4. Conduction through roof (top floor only):",
        "   Q_roof = A_roof x U_roof x CLTD_roof",
        "",
        "5. Occupant sensible heat gain:",
        "   Q_occ = N_people x metabolic_rate_W",
        "   Typical: office seated = 70W sensible, 60W latent",
        "",
        "6. Lighting heat gain:",
        "   Q_light = W_per_m2 x floor_area",
        "   Typical: LED office = 8-12 W/m2",
        "",
        "7. Equipment heat gain:",
        "   Q_equip = W_per_m2 x floor_area",
        "   Typical: office = 15-25 W/m2, server room = 500-2000 W/m2",
        "",
        "8. Ventilation (fresh air) load:",
        "   Q_vent = (fresh_air_l/s / 1000) x 1.2 x 1005 x (T_out - T_in)",
        "   1.2 = air density (kg/m3), 1005 = specific heat of air (J/kg.K)",
        "",
        "================================================================",
        "TOTAL COOLING LOAD:",
        "================================================================",
        "  Q_total_W = Q_solar + Q_glass_cond + Q_wall + Q_roof",
        "            + Q_occ + Q_light + Q_equip + Q_vent",
        "  Q_total_kW = Q_total_W / 1000",
        "  Q_TR = Q_total_kW / 3.517     (Tons of Refrigeration)",
        "  Chiller power = Q_total_kW / COP",
        "  (COP: 3.0 for DX, 5.0-6.5 for chiller, 4.0 for VRF)",
    ])
    story += [
        SP(0.3),
        h2(st, "5.4  Sprinkler Hydraulic Design (NFPA 13 / BS EN 12845)"),
    ]
    story += cb(st, "ALGORITHM: Sprinkler System Design", [
        "================================================================",
        "STEP 1 -- Classify Occupancy (determines design density):",
        "================================================================",
        "  Hazard Class | Min Density (mm/min) | Design Area (m2)",
        "  LH (Light)   |       2.25           |       84",
        "  OH1 (Ord 1)  |       5.0            |      105",
        "  OH2 (Ord 2)  |       5.0            |      144",
        "  HH (High)    |       7.5-12.5       |      260",
        "",
        "STEP 2 -- Minimum Head Flow:",
        "  Q_head (L/min) = design_density x coverage_area_per_head",
        "  P_min_bar = (Q_head / K_factor)^2",
        "  K-factor: standard heads = 80 L/min.bar^0.5",
        "            large-orifice  = 115 L/min.bar^0.5",
        "            ESFR           = 200-360 L/min.bar^0.5",
        "",
        "STEP 3 -- Remote Area Flow:",
        "  N_heads = design_area / coverage_per_head",
        "  Q_system (L/min) = design_density x design_area",
        "  Plus hose allowance: LH=0, OH1/2=250 L/min, HH=500 L/min",
        "",
        "STEP 4 -- System Operating Pressure:",
        "  P_system = P_remote_head + pipe_friction_losses + elevation_loss",
        "  Pipe losses (Hazen-Williams):",
        "  hf = 6.05E5 x Q^1.85 / (C^1.85 x D^4.87)",
        "  C = 120 for schedule 40 steel, D = internal pipe diameter (mm)",
    ])
    story += [
        SP(0.3),
        h2(st, "5.5  Maximum Demand Calculation (BS 7671 / IS 3961)"),
    ]
    story += cb(st, "ALGORITHM: Demand Load Diversity", [
        "  For each load item:",
        "    demand_kW = connected_kW x demand_factor x power_factor_correction",
        "",
        "  Total connected kW = sum of all connected_kW",
        "  Total demand kW    = sum of all (connected_kW x demand_factor)",
        "  Maximum demand kVA = Total_demand_kW / average_power_factor",
        "  Incoming cable Ib  = (kVA x 1000) / (sqrt(3) x V_LL)   [3-phase]",
        "",
        "  Demand factors (BS 7671 guidance):",
        "  Lighting circuits:      0.90 (10% diversity)",
        "  Socket outlet circuits: 0.50-0.80 (high diversity)",
        "  Motor loads:            0.75 (running, not all at once)",
        "  HVAC equipment:         0.80-0.90",
        "  Heaters (electric):     1.00 (no diversity -- worst case)",
    ])
    story += [
        SP(0.3),
        h2(st, "5.6  Data Flow — End-to-End Through the System"),
    ]
    story += cb(st, "Complete request --> response data flow:", [
        "User fills Cable Sizing form in browser",
        "        |",
        "        v",
        "Streamlit Page 1_Cable_Sizing.py",
        "  -> Collects form values into a Python dict",
        "  -> Calls utils.api_post('/api/electrical/cable-sizing', payload)",
        "        |",
        "        v  HTTP POST request (JSON body)",
        "FastAPI router: backend/api/routes/electrical.py",
        "  -> Pydantic deserialises JSON -> CableSizingRequest object",
        "  -> Field validators check: load_kw > 0, pf between 0.1 and 1.0, etc.",
        "  -> If any validation fails -> 422 response returned immediately",
        "        |",
        "        v  (validation passed)",
        "adapters_factory.get_electrical_adapter(region='gcc', sub_region='dewa')",
        "  -> Returns GCCDEWAElectricalAdapter instance",
        "  -> Adapter holds: cable tables, Ca table, Cg table, VD limit, standards refs",
        "        |",
        "        v",
        "calculate_cable_sizing(CableSizingInput, adapter)",
        "  -> Computes Ib, applies Ca/Cg, selects cable, checks VD",
        "  -> Returns CableSizingResult dataclass",
        "        |",
        "        v  FastAPI serialises dataclass -> JSON",
        "HTTP 200 OK: { 'selected_size_mm2': 16, 'voltage_drop_pct': 3.82, ... }",
        "        |",
        "        v",
        "Streamlit page receives JSON, renders:",
        "  st.metric(), st.table(), plotly bar chart of derating breakdown",
    ])
    return story


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 06 — DATA HANDLING
# ─────────────────────────────────────────────────────────────────────────────
def section_06(st):
    story = sb(st, "06", "Data Handling")
    story += [
        lead(st, "OpenMEP v0.1.0 uses a stateless API design for calculations. "
                 "Understanding how data flows and where it lives is essential "
                 "for safely modifying the project."),
        SP(0.2),
        h2(st, "6.1  Stateless API Design (Core Calculations)"),
        body(st,
            "The FastAPI backend stores no state between requests for its calculation "
            "endpoints. Each POST request is fully self-contained — it includes all "
            "the input data needed and produces a complete result. "
            "This design has important advantages:"),
        bul(st, "Any number of users can hit the API simultaneously — no shared state to corrupt"),
        bul(st, "Calculations are reproducible: same inputs always produce identical outputs"),
        bul(st, "No database needed for the core engineering calculations"),
        bul(st, "Horizontal scaling: add more API containers without synchronisation"),
        bul(st, "Testing is simple: call the engine function directly with test inputs"),
        SP(0.2),
        h2(st, "6.2  Engineering Standards Data (Static, In-Memory)"),
        body(st,
            "All cable rating tables, correction factor tables, and design constants "
            "are stored as Python dictionaries in backend/standards_data/ and "
            "backend/adapters/. This data is loaded once when the API starts "
            "and never changes at runtime."),
    ]
    story += cb(st, "Example: GCC cable rating table (XLPE Copper, Method C):", [
        "# backend/adapters/gcc_adapter.py",
        "",
        "# BS 7671:2018+A2:2022 Table 4D5A -- Single-core XLPE copper, Method C",
        "# Values in Amperes, base conditions: 30C ambient, no grouping",
        "XLPE_CU_METHOD_C = {",
        "     1.5:  17,    2.5:  23,    4:  30,    6:  38,",
        "    10:  51,   16:  68,   25:  89,   35: 110,",
        "    50: 134,   70: 171,   95: 207,  120: 239,",
        "   150: 272,  185: 310,  240: 365,  300: 419,",
        "}",
        "",
        "# BS 7671 Table 4C1 -- Ambient temperature correction factors (90C XLPE)",
        "CA_XLPE_90 = {",
        "    25: 1.04, 30: 1.00, 35: 0.96, 40: 0.91,",
        "    45: 0.87, 50: 0.82, 55: 0.76, 60: 0.71,",
        "}",
        "",
        "# BS 7671 Table 4C3 -- Grouping correction factors",
        "CG_FACTORS = {",
        "    1: 1.00, 2: 0.80, 3: 0.70, 4: 0.65, 5: 0.60,",
        "    6: 0.57, 7: 0.54, 8: 0.52, 9: 0.50, 10: 0.48,",
        "}",
    ])
    story += [
        SP(0.2),
        h2(st, "6.3  The Standards Adapter Pattern"),
        body(st,
            "This is the most important architectural pattern in OpenMEP. "
            "Every calculation engine receives an adapter object that provides "
            "region-specific constants. The engine logic never changes — "
            "only the data injected by the adapter changes."),
    ]
    story += cb(st, "Base adapter interface -- all adapters implement this:", [
        "# backend/adapters/base_adapter.py",
        "",
        "class BaseElectricalAdapter:",
        "    cable_sizing_standard: str   # e.g. 'BS 7671:2018+A2:2022 Table 4D5A'",
        "    authority: str               # e.g. 'DEWA (Dubai Electricity and Water Authority)'",
        "    voltage_lv: float            # e.g. 400 (V line-to-line)",
        "    voltage_phase: float         # e.g. 230 (V line-to-neutral)",
        "    design_ambient_temp: float   # e.g. 40.0 (C for GCC)",
        "",
        "    def get_tabulated_rating(self, size_mm2, cable_type, method) -> float: ...",
        "    def get_ambient_temp_factor(self, temp, cable_type) -> float: ...",
        "    def get_grouping_factor(self, n_circuits) -> float: ...",
        "    def get_voltage_drop_mv_am(self, cable_type, size, phases) -> float: ...",
        "    def get_voltage_drop_limit(self, circuit_type) -> float: ...",
        "    def get_earth_conductor_size(self, phase_size) -> float: ...",
        "    def get_standard_cable_sizes(self) -> list: ...",
    ])
    story += cb(st, "adapters_factory.py -- returns correct adapter for region:", [
        "def get_electrical_adapter(region: str, sub_region: str) -> BaseElectricalAdapter:",
        "    region = region.lower().strip()",
        "    sub    = sub_region.lower().strip()",
        "    if region == 'gcc':       return GCCElectricalAdapter(sub_region=sub)",
        "    elif region == 'europe':  return EuropeElectricalAdapter(sub_region=sub)",
        "    elif region == 'india':   return IndiaElectricalAdapter(sub_region=sub)",
        "    elif region == 'australia': return AustraliaElectricalAdapter(sub_region=sub)",
        "    else: raise ValueError(f'Unknown region: {region}')",
    ])
    story += [
        SP(0.2),
        h2(st, "6.4  PostgreSQL Database (Docker — Future Use)"),
        body(st,
            "The docker-compose.yml provisions a PostgreSQL 16 database (service: db). "
            "In v0.1.0, it is present but calculations are not persisted to it. "
            "The DATABASE_URL environment variable is already wired into both "
            "API and Streamlit containers so future features can use it without "
            "modifying the Docker configuration."),
        body(st, "Planned database usage in v0.2.0:"),
        bul(st, "Save calculation results per project (project history)"),
        bul(st, "Store user preferences (favourite cable types, default regions)"),
        bul(st, "Persist Submittal Tracker records across sessions"),
        bul(st, "API usage logging for monitoring"),
        SP(0.2),
        h2(st, "6.5  Streamlit Session State"),
        body(st,
            "Streamlit provides st.session_state — a dictionary-like object that persists "
            "for the duration of a user's browser session. The Submittal Tracker (page 16) "
            "uses this to hold a pandas DataFrame of submittals. "
            "It resets on page refresh and is not shared between browser tabs."),
        SP(0.2),
        h2(st, "6.6  Environment Variables Reference"),
        dt(st, ["Variable", "Default Value", "Where Used", "Purpose"], [
            ["API_BASE", "http://localhost:8000", "streamlit_app/utils.py",
             "URL of FastAPI backend. Set to http://api:8000 in Docker."],
            ["DATABASE_URL", "postgresql://openmep:password@db:5432/openmep", "Both containers",
             "PostgreSQL connection string for future persistence features."],
            ["POSTGRES_DB", "openmep", "docker-compose.yml",
             "Database name for PostgreSQL container."],
            ["POSTGRES_USER", "openmep", "docker-compose.yml",
             "Database username."],
            ["POSTGRES_PASSWORD", "-- must be set --", "docker-compose.yml",
             "Database password. NEVER put in code. Always in .env file."],
        ], [3.2*cm, 4*cm, 4*cm, CONTENT_W - 11.2*cm]),
    ]
    return story


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 07 — API REFERENCE
# ─────────────────────────────────────────────────────────────────────────────
def section_07(st):
    story = sb(st, "07", "API Reference")
    story += [
        lead(st, "OpenMEP exposes 35 REST endpoints. All are accessible at http://localhost:8000 "
                 "and documented interactively at http://localhost:8000/docs (Swagger UI)."),
        SP(0.2),
        h2(st, "7.1  Base URL & Authentication"),
        body(st, "<b>Base URL:</b> http://localhost:8000 (local) or http://api:8000 (Docker)"),
        body(st, "<b>Authentication:</b> None required in v0.1.0. All endpoints are open."),
        body(st, "<b>Content-Type:</b> application/json for all POST requests."),
        body(st, "<b>Interactive Docs:</b> /docs (Swagger UI) and /redoc (ReDoc)"),
        SP(0.2),
        h2(st, "7.2  Complete Endpoint Table (35 Endpoints)"),
        dt(st, ["Method", "Endpoint", "Description"], [
            ["GET",  "/",                                    "API welcome message, version, supported regions"],
            ["GET",  "/health",                             "Health check -- returns {status: healthy}"],
            ["POST", "/api/electrical/cable-sizing",        "Cable sizing with derating factors (Ca, Cg)"],
            ["GET",  "/api/electrical/cable-sizing",        "Cable sizing via URL query parameters"],
            ["GET",  "/api/electrical/cable-sizing/options","Returns available cable types and methods"],
            ["POST", "/api/electrical/voltage-drop",        "Voltage drop for a known cable size"],
            ["POST", "/api/electrical/demand-load",         "Maximum demand with diversity factors"],
            ["POST", "/api/electrical/short-circuit",       "IEC 60909 prospective fault current"],
            ["POST", "/api/electrical/lighting",            "Lumen method illuminance design"],
            ["POST", "/api/electrical/pf-correction",       "Capacitor bank and kVAr sizing"],
            ["POST", "/api/electrical/generator-sizing",    "ISO 8528 standby/prime generator sizing"],
            ["POST", "/api/electrical/panel-schedule",      "Distribution board full panel schedule"],
            ["POST", "/api/electrical/ups-sizing",          "IEC 62040 UPS capacity + battery autonomy"],
            ["POST", "/api/mechanical/cooling-load",        "ASHRAE CLTD zone cooling load"],
            ["POST", "/api/mechanical/duct-sizing",         "SMACNA equal friction duct sizing"],
            ["POST", "/api/mechanical/multi-zone-cooling",  "Multi-zone cooling load summary"],
            ["POST", "/api/mechanical/heating-load",        "EN 12831 transmission + infiltration losses"],
            ["POST", "/api/mechanical/ventilation",         "ASHRAE 62.1 / AS 1668.2 fresh air rates"],
            ["POST", "/api/plumbing/pipe-sizing",           "Loading unit cold/hot water pipe sizing"],
            ["POST", "/api/plumbing/drainage-sizing",       "Discharge unit soil and waste sizing"],
            ["POST", "/api/plumbing/pump-sizing",           "Darcy-Weisbach pump duty selection"],
            ["POST", "/api/plumbing/hot-water-system",      "CIBSE W / AS/NZS 3500.4 hot water design"],
            ["POST", "/api/plumbing/rainwater-harvesting",  "BS 8515 rainwater harvesting tank sizing"],
            ["POST", "/api/plumbing/plumbing-tank-sizing",  "Cold water break cistern + fire reserve"],
            ["POST", "/api/fire/sprinkler",                 "NFPA 13 / BS EN 12845 sprinkler hydraulics"],
            ["POST", "/api/fire/fire-pump",                 "NFPA 20 fire pump set sizing"],
            ["POST", "/api/fire/fire-tank",                 "NFPA 22 / BS EN 12845 fire water tank"],
            ["POST", "/api/fire/standpipe",                 "NFPA 14 wet riser landing valve analysis"],
            ["POST", "/api/boq/generate",                   "Generate Bill of Quantities (all disciplines)"],
            ["GET",  "/api/boq/rates",                      "Indicative unit rates by region"],
            ["POST", "/api/compliance/check",               "Multi-standard compliance matrix checker"],
            ["GET",  "/api/compliance/standards-reference",  "Standards list and clauses by region"],
            ["POST", "/api/reports/calculation-report",     "Generate calculation report data for PDF"],
            ["GET",  "/api/reports/templates",              "Available report template names"],
        ], [1.8*cm, 7*cm, CONTENT_W - 8.8*cm]),
        SP(0.3),
        h2(st, "7.3  Detailed Example — Cable Sizing"),
    ]
    story += cb(st, "Full request (cURL):", [
        "curl -X POST http://localhost:8000/api/electrical/cable-sizing \\",
        "  -H 'Content-Type: application/json' \\",
        "  -d '{",
        '    "region":              "gcc",',
        '    "sub_region":          "dewa",',
        '    "load_kw":             45.0,',
        '    "power_factor":        0.85,',
        '    "phases":              3,',
        '    "cable_type":          "XLPE_CU",',
        '    "installation_method": "C",',
        '    "cable_length_m":      80.0,',
        '    "ambient_temp_c":      40.0,',
        '    "num_grouped_circuits":1,',
        '    "circuit_type":        "power"',
        "  }'",
    ])
    story += cb(st, "Response (HTTP 200 OK):", [
        "{",
        '  "status":                  "success",',
        '  "standard":                "BS 7671:2018+A2:2022 Table 4D5A",',
        '  "authority":               "DEWA (Dubai Electricity and Water Authority)",',
        '  "design_current_ib_a":     73.65,',
        '  "cable_type":              "XLPE_CU",',
        '  "installation_method":     "C",',
        '  "selected_size_mm2":       16,',
        '  "tabulated_rating_it_a":   80.0,',
        '  "ambient_temp_c":          40.0,',
        '  "ca_factor":               0.91,',
        '  "num_grouped_circuits":    1,',
        '  "cg_factor":               1.00,',
        '  "derated_rating_iz_a":     72.8,',
        '  "cable_length_m":          80.0,',
        '  "voltage_drop_pct":        3.98,',
        '  "voltage_drop_limit_pct":  4.0,',
        '  "voltage_drop_pass":       true,',
        '  "earth_conductor_mm2":     6.0,',
        '  "overall_compliant":       true,',
        '  "warnings":                []',
        "}",
    ])
    story += [
        SP(0.2),
        h2(st, "7.4  Error Response Formats"),
    ]
    story += cb(st, "422 Validation Error (missing required field):", [
        "HTTP/1.1 422 Unprocessable Entity",
        "{",
        '  "detail": [',
        "    {",
        '      "type":  "missing",',
        '      "loc":   ["body", "load_kw"],',
        '      "msg":   "Field required",',
        '      "input": {},',
        '      "url":   "https://errors.pydantic.dev/2.5/v/missing"',
        "    }",
        "  ]",
        "}",
    ])
    story += cb(st, "422 Validation Error (value out of range):", [
        "{",
        '  "detail": [',
        "    {",
        '      "type":  "greater_than",',
        '      "loc":   ["body", "load_kw"],',
        '      "msg":   "Input should be greater than 0",',
        '      "input": -10',
        "    }",
        "  ]",
        "}",
    ])
    story += cb(st, "500 Internal Server Error (caught by global handler):", [
        "HTTP/1.1 500 Internal Server Error",
        "{",
        '  "status":  "error",',
        '  "message": "Cable size not found for required current of 847A in region gcc",',
        '  "type":    "ValueError"',
        "}",
    ])
    return story


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 08 — DEPLOYMENT
# ─────────────────────────────────────────────────────────────────────────────
def section_08(st):
    story = sb(st, "08", "Deployment Details")
    story += [
        lead(st, "OpenMEP can be deployed in multiple ways depending on your needs. "
                 "This section covers every deployment option in full detail."),
        SP(0.2),
        h2(st, "8.1  Running the Application"),
        body(st, "OpenMEP runs two processes side by side. "
                 "Start both with the commands below:"),
        dt(st, ["Service", "Command", "Port", "URL"], [
            ["FastAPI Backend",
             "python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000",
             "8000", "http://localhost:8000/docs"],
            ["Streamlit UI",
             "python3 -m streamlit run streamlit_app/app.py --server.port 8501 --server.address 0.0.0.0",
             "8501", "http://localhost:8501"],
        ], [3.5*cm, 7*cm, 1.5*cm, CONTENT_W - 12*cm]),
        SP(0.3),
        h2(st, "8.2  Local Development Setup"),
    ]
    story += cb(st, "Complete local setup from scratch:", [
        "# Prerequisites: Python 3.11+ and pip installed",
        "",
        "# 1. Clone the repository",
        "git clone https://github.com/kakarot-oncloud/openmep-suite.git",
        "cd openmep",
        "",
        "# 2. Create a virtual environment (recommended)",
        "python -m venv venv",
        "source venv/bin/activate      # Mac / Linux",
        "venv\\Scripts\\activate         # Windows PowerShell",
        "",
        "# 3. Install all Python dependencies",
        "pip install -r requirements.txt",
        "",
        "# 4. Copy the environment variable template",
        "cp .env.example .env",
        "",
        "# 5. Terminal 1: Start the FastAPI backend",
        "uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000",
        "",
        "# 6. Terminal 2: Start the Streamlit UI",
        "streamlit run streamlit_app/app.py",
        "",
        "# 7. Verify in browser:",
        "#   API Swagger docs:  http://localhost:8000/docs",
        "#   Streamlit UI:      http://localhost:8501",
        "#   API health:        http://localhost:8000/health",
    ])
    story += [
        SP(0.3),
        h2(st, "8.3  Docker Compose Deployment (Recommended for Production)"),
        body(st,
            "Docker Compose starts all three services (database, API, UI) with a "
            "single command. Services communicate on a private Docker network."),
    ]
    story += cb(st, "docker-compose.yml -- annotated:", [
        "version: '3.9'",
        "",
        "services:",
        "  # 1 -- PostgreSQL database",
        "  db:",
        "    image: postgres:16-alpine",
        "    environment:",
        "      POSTGRES_DB: ${POSTGRES_DB:-openmep}",
        "      POSTGRES_USER: ${POSTGRES_USER:-openmep}",
        "      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?must be set in .env}",
        "    volumes:",
        "      - pgdata:/var/lib/postgresql/data   # Persist DB across restarts",
        "    healthcheck:",
        "      test: ['CMD-SHELL', 'pg_isready -U openmep -d openmep']",
        "      interval: 15s",
        "      retries: 5",
        "    networks: [openmep_net]",
        "",
        "  # 2 -- FastAPI calculation engine",
        "  api:",
        "    build: { context: ., dockerfile: Dockerfile }",
        "    command: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2",
        "    ports: ['8000:8000']",
        "    environment:",
        "      - PYTHONUNBUFFERED=1",
        "      - DATABASE_URL=postgresql://openmep:${POSTGRES_PASSWORD}@db:5432/openmep",
        "    depends_on:",
        "      db: { condition: service_healthy }",
        "    healthcheck:",
        "      test: ['CMD', 'curl', '-f', 'http://localhost:8000/health']",
        "      interval: 30s",
        "    networks: [openmep_net]",
        "",
        "  # 3 -- Streamlit UI",
        "  streamlit:",
        "    build: { context: ., dockerfile: Dockerfile }",
        "    command: >",
        "      streamlit run streamlit_app/app.py",
        "        --server.port 8501 --server.address 0.0.0.0",
        "        --server.headless true",
        "        --browser.gatherUsageStats false",
        "    ports: ['8501:8501']",
        "    environment:",
        "      - API_BASE=http://api:8000   # Internal Docker network URL",
        "    depends_on:",
        "      api: { condition: service_healthy }",
        "    networks: [openmep_net]",
        "",
        "networks:",
        "  openmep_net: { driver: bridge }",
        "",
        "volumes:",
        "  pgdata:",
    ])
    story += cb(st, "Running with Docker Compose:", [
        "# 1. Set up environment",
        "cp .env.example .env",
        "nano .env    # Set POSTGRES_PASSWORD=YourStrongPassword123",
        "",
        "# 2. Build and start all three services in the background",
        "docker-compose up -d --build",
        "",
        "# 3. Check service status",
        "docker-compose ps",
        "",
        "# 4. Follow logs (Ctrl+C to stop following, services keep running)",
        "docker-compose logs -f",
        "docker-compose logs -f api      # Only API logs",
        "",
        "# 5. Stop all services",
        "docker-compose down",
        "",
        "# 6. Stop and remove volumes (WARNING: deletes database data)",
        "docker-compose down -v",
    ])
    story += [
        SP(0.2),
        h2(st, "8.4  Dockerfile Explained"),
    ]
    story += cb(st, "Dockerfile:", [
        "FROM python:3.11-slim          # Minimal Python image (~150MB vs ~1GB for full)",
        "WORKDIR /app",
        "COPY requirements.txt .",
        "RUN pip install --no-cache-dir -r requirements.txt",
        "COPY . .",
        "",
        "# Default command -- overridden by docker-compose for each service",
        "CMD ['uvicorn', 'backend.main:app', '--host', '0.0.0.0', '--port', '8000']",
    ])
    story += [
        SP(0.2),
        co(st,
            "The same Dockerfile is used for BOTH the api and streamlit services. "
            "Docker Compose overrides the CMD for the streamlit service. "
            "This keeps the image count low and ensures both services use identical "
            "Python environments.", style="info"),
        SP(0.2),
        h2(st, "8.5  Deploying to a VPS (Ubuntu Server)"),
    ]
    story += cb(st, "VPS deployment with nginx reverse proxy:", [
        "# 1. Install Docker and Docker Compose on Ubuntu",
        "sudo apt-get update && sudo apt-get install -y docker.io docker-compose",
        "",
        "# 2. Clone the repo",
        "git clone https://github.com/kakarot-oncloud/openmep-suite.git /opt/openmep",
        "cd /opt/openmep",
        "",
        "# 3. Configure environment",
        "cp .env.example .env",
        "nano .env   # Set strong POSTGRES_PASSWORD",
        "",
        "# 4. Start services",
        "docker-compose up -d --build",
        "",
        "# 5. Install nginx for reverse proxy",
        "sudo apt-get install -y nginx",
        "",
        "# 6. Configure nginx -- /etc/nginx/sites-available/openmep",
        "# server {",
        "#   server_name yourdomain.com;",
        "#   location /api { proxy_pass http://localhost:8000; }",
        "#   location /    { proxy_pass http://localhost:8501; }",
        "# }",
        "",
        "# 7. Enable and reload nginx",
        "sudo ln -s /etc/nginx/sites-available/openmep /etc/nginx/sites-enabled/",
        "sudo nginx -t && sudo systemctl reload nginx",
    ])
    story += [
        SP(0.2),
        h2(st, "8.6  Streamlit Community Cloud Deployment"),
    ]
    story += cb(st, "Deploy Streamlit UI publicly (free tier):", [
        "# 1. Push your code to GitHub (already done)",
        "",
        "# 2. Visit https://streamlit.io/cloud",
        "#    Sign in with GitHub",
        "",
        "# 3. Click 'New app'",
        "#    Repository: kakarot-oncloud/openmep-suite",
        "#    Branch: main",
        "#    Main file path: streamlit_app/app.py",
        "",
        "# 4. Add Secrets (Settings --> Secrets):",
        "#    API_BASE = https://your-fastapi-server.com",
        "",
        "# 5. Click 'Deploy!'",
        "# Note: You still need to host the FastAPI backend separately (VPS, Railway, etc.)",
    ])
    return story


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 09 — GITHUB INTEGRATION
# ─────────────────────────────────────────────────────────────────────────────
def section_09(st):
    story = sb(st, "09", "GitHub Integration")
    story += [
        lead(st, "The OpenMEP repository is public on GitHub. This section covers "
                 "how the repo is structured, how to contribute, and how to "
                 "maintain a clean commit history."),
        SP(0.2),
        h2(st, "9.1  Repository Details"),
        dt(st, ["Item", "Value"], [
            ["URL",           "https://github.com/kakarot-oncloud/openmep-suite"],
            ["Owner",         "Luquman A (@kakarot-oncloud)"],
            ["Visibility",    "Public"],
            ["License",       "MIT -- Copyright 2025 Luquman A"],
            ["Default branch","main"],
            ["Topics",        "mep, fastapi, streamlit, engineering, bs7671, nfpa, ashrae, open-source"],
            ["Description",   "Open-source MEP engineering calculation suite. 4 regions, 26 modules, 35+ API endpoints."],
        ], [4*cm, CONTENT_W - 4*cm]),
        SP(0.3),
        h2(st, "9.2  GitHub Repository Files"),
        body(st, "Standard GitHub repository files present in the project:"),
        bul(st, "<b>README.md</b> — Project introduction, feature matrix, quick start, badges, contributor credits"),
        bul(st, "<b>LICENSE</b> — MIT License -- Copyright 2025 Luquman A"),
        bul(st, "<b>CONTRIBUTING.md</b> — How to report bugs, request features, and submit pull requests"),
        bul(st, "<b>CODE_OF_CONDUCT.md</b> — Community behaviour standards for contributors"),
        bul(st, "<b>SECURITY.md</b> — How to responsibly disclose security vulnerabilities"),
        bul(st, "<b>CHANGELOG.md</b> — Chronological record of changes per version"),
        bul(st, "<b>.github/ISSUE_TEMPLATE/</b> — Bug report and feature request templates for GitHub Issues"),
        SP(0.3),
        h2(st, "9.3  Cloning and Running Locally"),
    ]
    story += cb(st, "Clone and run the project:", [
        "# Clone",
        "git clone https://github.com/kakarot-oncloud/openmep-suite.git",
        "cd openmep",
        "",
        "# Install",
        "pip install -r requirements.txt",
        "",
        "# Start API (Terminal 1)",
        "uvicorn backend.main:app --reload --port 8000",
        "",
        "# Start UI (Terminal 2)",
        "streamlit run streamlit_app/app.py",
        "",
        "# Open browser",
        "#   http://localhost:8501  -->  Streamlit UI",
        "#   http://localhost:8000/docs  -->  Swagger API docs",
    ])
    story += [
        SP(0.3),
        h2(st, "9.4  Contributing to the Project"),
    ]
    story += cb(st, "Standard contribution workflow:", [
        "# 1. Fork the repository on GitHub",
        "#    Click the 'Fork' button on github.com/kakarot-oncloud/openmep-suite",
        "",
        "# 2. Clone YOUR fork",
        "git clone https://github.com/YOUR-USERNAME/openmep.git",
        "cd openmep",
        "",
        "# 3. Add the upstream remote (to pull future updates)",
        "git remote add upstream https://github.com/kakarot-oncloud/openmep-suite.git",
        "",
        "# 4. Create a feature branch",
        "#    Branch naming: feature/<description>, bugfix/<description>, docs/<description>",
        "git checkout -b feature/add-transformer-sizing-module",
        "",
        "# 5. Make your changes and write tests",
        "pytest backend/tests/ -v",
        "",
        "# 6. Commit with a descriptive message",
        'git commit -m "feat: add transformer sizing calculator for GCC and India regions"',
        "",
        "# 7. Push to your fork",
        "git push origin feature/add-transformer-sizing-module",
        "",
        "# 8. Open a Pull Request on GitHub",
        "#    Title: [Electrical] Add transformer sizing module",
        "#    Fill in: what it does, which standard it implements, how you tested it",
    ])
    return story


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 10 — SETUP INSTRUCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def section_10(st):
    story = sb(st, "10", "Setup Instructions")
    story += [
        lead(st, "Follow these steps exactly to get OpenMEP running on any machine. "
                 "No prior knowledge of FastAPI or Streamlit is required."),
        SP(0.2),
        h2(st, "10.1  Prerequisites"),
        dt(st, ["Software", "Minimum Version", "Download", "Required For"], [
            ["Python",         "3.11",       "python.org",          "Backend + UI runtime"],
            ["pip",            "23.x",       "Bundled with Python", "Package installation"],
            ["Git",            "2.x",        "git-scm.com",         "Clone the repository"],
            ["Docker",         "24.x",       "docker.com",          "Containerised deployment (optional)"],
            ["Docker Compose", "2.x",        "Bundled with Docker", "Multi-service deployment (optional)"],
            ["Web Browser",    "Any modern", "--",                  "Access Streamlit UI"],
        ], [3.5*cm, 3.5*cm, 4*cm, CONTENT_W - 11*cm]),
        SP(0.3),
        h2(st, "10.2  Step-by-Step Setup Guide"),
        Paragraph("Step 1: Verify Python version", st["h3"]),
    ]
    story += cb(st, None, [
        "python --version    # Must show Python 3.11 or later",
        "# If not installed: download from https://python.org/downloads",
    ])
    story += [SP(0.2), Paragraph("Step 2: Clone the repository", st["h3"])]
    story += cb(st, None, [
        "git clone https://github.com/kakarot-oncloud/openmep-suite.git",
        "cd openmep",
    ])
    story += [SP(0.2), Paragraph("Step 3: Create a virtual environment (strongly recommended)", st["h3"])]
    story += cb(st, None, [
        "python -m venv venv",
        "source venv/bin/activate   # Mac / Linux",
        "venv\\Scripts\\activate      # Windows Command Prompt",
        ".\\venv\\Scripts\\Activate.ps1 # Windows PowerShell",
        "",
        "# Your prompt should now show (venv) at the start",
    ])
    story += [SP(0.2), Paragraph("Step 4: Install all Python dependencies", st["h3"])]
    story += cb(st, None, [
        "pip install -r requirements.txt",
        "# This installs: fastapi, uvicorn, streamlit, pydantic, plotly,",
        "#                 reportlab, openpyxl, numpy, pandas, requests, etc.",
        "# Expected time: 2-5 minutes on first run",
    ])
    story += [SP(0.2), Paragraph("Step 5: Set up environment variables", st["h3"])]
    story += cb(st, None, [
        "cp .env.example .env",
        "# Contents of .env.example:",
        "# API_BASE=http://localhost:8000",
        "# POSTGRES_PASSWORD=changeme_strong_password",
        "",
        "# For local development, the defaults are fine.",
    ])
    story += [SP(0.2), Paragraph("Step 6: Start the FastAPI backend (keep this terminal open)", st["h3"])]
    story += cb(st, None, [
        "uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000",
        "",
        "# You should see:",
        "# INFO:     Uvicorn running on http://0.0.0.0:8000",
        "",
        "# Verify: open http://localhost:8000/health in browser",
        '# Expected response: {"status":"healthy","service":"openmep-api"}',
    ])
    story += [SP(0.2), Paragraph("Step 7: Open a second terminal and start Streamlit", st["h3"])]
    story += cb(st, None, [
        "source venv/bin/activate   # (Mac/Linux)",
        "streamlit run streamlit_app/app.py",
        "",
        "# Streamlit will print a local URL:",
        "# Local URL: http://localhost:8501",
    ])
    story += [SP(0.2), Paragraph("Step 8: Verify everything is working", st["h3"])]
    story += cb(st, None, [
        "# Open these URLs in your browser:",
        "# 1. Streamlit UI:    http://localhost:8501",
        "#    Click on any page in the sidebar (e.g. Cable Sizing)",
        "#    Fill in inputs and click Calculate",
        "#    Results should appear immediately",
        "",
        "# 2. API Swagger UI: http://localhost:8000/docs",
        "#    All 35 endpoints listed with 'Try it out' buttons",
    ])
    story += [
        SP(0.1),
        co(st,
            "Common issue: If the Streamlit page shows 'Cannot connect to API', "
            "check that the FastAPI server (uvicorn) is running in Terminal 1 "
            "and that API_BASE in your .env file is set to http://localhost:8000.",
            style="warn"),
    ]
    return story


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 11 — FUTURE IMPROVEMENTS
# ─────────────────────────────────────────────────────────────────────────────
def section_11(st):
    story = sb(st, "11", "Future Improvements")
    story += [
        lead(st, "OpenMEP v0.1.0 is a solid foundation. This section describes the "
                 "planned roadmap, performance improvements, and long-term scalability ideas."),
        SP(0.2),
        h2(st, "11.1  Version Roadmap"),
        dt(st, ["Version", "Feature", "Description", "Priority"], [
            ["v0.2.0", "Canada / USA Region",     "NEC 2023 / CEC C22.1 electrical standards", "High"],
            ["v0.2.0", "South Africa Region",     "SANS 10142 / NRS 047 standards", "Medium"],
            ["v0.2.0", "API Authentication",      "JWT tokens / API key authentication for public deployment", "High"],
            ["v0.2.0", "Database Persistence",    "PostgreSQL: save projects, calculations, user preferences", "High"],
            ["v0.2.0", "Harmonic Derating",       "K-factor derating for VFD/UPS loaded cables", "Medium"],
            ["v0.3.0", "React Frontend",          "Replace Streamlit with TypeScript/React for better UX", "Medium"],
            ["v0.3.0", "BIM/IFC Export",          "Export calculation data to IFC files for BIM software", "Low"],
            ["v0.3.0", "Calculation History",     "Full audit log of all calculations per project", "Medium"],
            ["v0.3.0", "Multi-zone Optimization", "Auto-optimize duct and pipe networks across zones", "Low"],
            ["v0.4.0", "Mobile App (Expo)",       "iOS/Android app using React Native + Expo", "Medium"],
            ["v0.4.0", "AI Recommendations",      "Claude/GPT-powered design review and suggestions", "Low"],
            ["v0.5.0", "Team Workspaces",         "Multi-user project collaboration with roles", "Low"],
            ["v0.5.0", "Standards Auto-Update",   "Notify users when referenced standards are revised", "Low"],
        ], [2*cm, 4.2*cm, 6.5*cm, 2.8*cm]),
        SP(0.3),
        h2(st, "11.2  Performance Improvements"),
        body(st, "Current performance is adequate for single-user or small team use. "
                 "For high-traffic deployments, these improvements are recommended:"),
        bul(st, "Add <b>Redis caching</b> for the /api/boq/rates and /api/compliance/standards-reference endpoints — these return static data and don't need to recompute on every call"),
        bul(st, "Pre-compute cable rating lookup tables at startup (currently computed per-request)"),
        bul(st, "Use <b>numpy vectorisation</b> for multi-zone cooling load arrays instead of Python loops"),
        bul(st, "Add <b>Gzip compression</b> middleware to FastAPI for large JSON responses (e.g., BOQ with hundreds of line items)"),
        bul(st, "Use <b>asyncpg</b> for async database queries when PostgreSQL persistence is added in v0.2.0"),
        SP(0.2),
        h2(st, "11.3  Scalability Ideas"),
        bul(st, "Deploy FastAPI with <b>4+ Uvicorn workers</b> behind an nginx load balancer for production traffic"),
        bul(st, "Use <b>Kubernetes</b> for auto-scaling the API pods under high concurrent load"),
        bul(st, "Split each discipline into its own <b>microservice</b> so electrical, mechanical, plumbing, and fire can be scaled independently"),
        bul(st, "Add <b>rate limiting per IP</b> using a Redis-backed middleware to prevent API abuse"),
        bul(st, "Use a <b>CDN</b> (Cloudflare) to cache the Streamlit static assets and reduce server load"),
        SP(0.2),
        h2(st, "11.4  Additional Calculation Modules Needed"),
        bul(st, "Transformer sizing (IEC 60076) — highly requested"),
        bul(st, "Busbar sizing (BS EN 60439) — needed for switchboard design"),
        bul(st, "Lightning protection (IEC 62305) — required for most GCC projects"),
        bul(st, "Earthing system design (BS 7430 / IEC 60364-5-54)"),
        bul(st, "Emergency lighting (BS 5266) / Exit sign lux levels"),
        bul(st, "Underfloor heating design (EN ISO 11855)"),
        bul(st, "Compressed air system sizing (ISO 8573)"),
        bul(st, "Chilled water system hydraulics (ASHRAE Handbook — HVAC Systems)"),
    ]
    return story


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 12 — HOW TO EXTEND
# ─────────────────────────────────────────────────────────────────────────────
def section_12(st):
    story = sb(st, "12", "How to Extend This Project")
    story += [
        lead(st, "This section is written for developers and AI assistants who need to "
                 "safely add new features to OpenMEP. Follow these patterns exactly "
                 "to maintain consistency with the existing codebase."),
        SP(0.2),
        h2(st, "12.1  Adding a New Calculation Module (Full Walkthrough)"),
        body(st, "Example: Adding a <b>Transformer Sizing</b> calculator (new module)."),
        h3(st, "Step 1 — Create the Engine File"),
    ]
    story += cb(st, "backend/engines/electrical/transformer_sizing.py:", [
        '"""',
        "Transformer Sizing Engine -- IEC 60076-1:2011 / BS EN 60076-1:2011",
        "Selects standard kVA rating based on connected load and diversity.",
        '"""',
        "import math",
        "from dataclasses import dataclass",
        "from typing import Optional",
        "from backend.engines.adapters_factory import get_electrical_adapter",
        "",
        "@dataclass",
        "class TransformerSizingInput:",
        "    region: str = 'gcc'",
        "    sub_region: str = ''",
        "    connected_load_kva: float = 500.0",
        "    diversity_factor: float = 0.80",
        "    power_factor: float = 0.90",
        "    future_expansion_pct: float = 20.0",
        "    installation_type: str = 'indoor'",
        "    cooling_type: str = 'ONAN'",
        "",
        "@dataclass",
        "class TransformerSizingResult:",
        "    region: str = ''",
        "    standard: str = 'IEC 60076-1:2011'",
        "    design_load_kva: float = 0.0",
        "    future_load_kva: float = 0.0",
        "    recommended_kva: float = 0.0",
        "    utilisation_pct: float = 0.0",
        "    overall_compliant: bool = True",
        "",
        "STANDARD_SIZES = [50, 100, 160, 200, 250, 315, 400, 500,",
        "                  630, 800, 1000, 1250, 1600, 2000, 2500]",
        "",
        "def calculate_transformer_sizing(inp: TransformerSizingInput) -> TransformerSizingResult:",
        "    design_kva = inp.connected_load_kva * inp.diversity_factor",
        "    future_kva = design_kva * (1 + inp.future_expansion_pct / 100)",
        "    selected = next((s for s in STANDARD_SIZES if s >= future_kva), None)",
        "    if not selected:",
        "        selected = STANDARD_SIZES[-1]",
        "    utilisation = (design_kva / selected) * 100",
        "    return TransformerSizingResult(",
        "        region=inp.region,",
        "        design_load_kva=round(design_kva, 1),",
        "        future_load_kva=round(future_kva, 1),",
        "        recommended_kva=selected,",
        "        utilisation_pct=round(utilisation, 1),",
        "        overall_compliant=True,",
        "    )",
    ])
    story += [h3(st, "Step 2 — Add the API Route")]
    story += cb(st, "Add to backend/api/routes/electrical.py:", [
        "from backend.engines.electrical.transformer_sizing import (",
        "    TransformerSizingInput, calculate_transformer_sizing",
        ")",
        "",
        "class TransformerSizingRequest(BaseModel):",
        "    region: str = 'gcc'",
        "    sub_region: str = ''",
        "    connected_load_kva: float = Field(gt=0)",
        "    diversity_factor: float = Field(default=0.80, ge=0.1, le=1.0)",
        "    future_expansion_pct: float = Field(default=20.0, ge=0, le=100)",
        "",
        "@router.post('/transformer-sizing')",
        "async def transformer_sizing(req: TransformerSizingRequest):",
        "    inp = TransformerSizingInput(",
        "        region=req.region, sub_region=req.sub_region,",
        "        connected_load_kva=req.connected_load_kva,",
        "        diversity_factor=req.diversity_factor,",
        "        future_expansion_pct=req.future_expansion_pct,",
        "    )",
        "    return calculate_transformer_sizing(inp)",
    ])
    story += [h3(st, "Step 3 — Add the Streamlit Page")]
    story += cb(st, "Create streamlit_app/pages/27_Transformer_Sizing.py:", [
        "import streamlit as st",
        "from utils import region_selector, api_post",
        "",
        "st.set_page_config(page_title='Transformer Sizing | OpenMEP', layout='wide')",
        "st.title('Transformer Sizing')",
        "st.caption('IEC 60076-1:2011 / BS EN 60076-1:2011')",
        "",
        "region, sub_region = region_selector(key='ts')",
        "",
        "with st.form('transformer_form'):",
        "    col1, col2 = st.columns(2)",
        "    with col1:",
        "        load_kva  = st.number_input('Connected Load (kVA)', min_value=10.0, value=500.0)",
        "        diversity = st.slider('Diversity Factor', 0.1, 1.0, 0.80, 0.05)",
        "    with col2:",
        "        future_pct = st.number_input('Future Expansion (%)', value=20.0)",
        "    submitted = st.form_submit_button('Size Transformer', type='primary')",
        "",
        "if submitted:",
        "    result = api_post('/api/electrical/transformer-sizing', {",
        "        'region': region, 'sub_region': sub_region,",
        "        'connected_load_kva': load_kva, 'diversity_factor': diversity,",
        "        'future_expansion_pct': future_pct,",
        "    })",
        "    if result:",
        "        c1, c2, c3 = st.columns(3)",
        "        c1.metric('Design Load', f'{result[\"design_load_kva\"]} kVA')",
        "        c2.metric('Recommended Size', f'{result[\"recommended_kva\"]} kVA')",
        "        c3.metric('Utilisation', f'{result[\"utilisation_pct\"]}%')",
        "        if result['overall_compliant']:",
        "            st.success('Transformer sized correctly per IEC 60076-1:2011')",
    ])
    story += [
        SP(0.2),
        h2(st, "12.2  Adding a New Region"),
        body(st, "Example: Adding <b>Canada</b> (CEC C22.1:2021 / NEC 2023)."),
    ]
    story += cb(st, "1. Add to backend/config.py:", [
        "SUPPORTED_REGIONS = ['gcc', 'europe', 'india', 'australia', 'canada']",
    ])
    story += cb(st, "2. Add to streamlit_app/utils.py:", [
        "REGIONS['Canada'] = 'canada'",
        "SUB_REGIONS_L2['canada'] = {",
        "    'Ontario':         'ontario',",
        "    'British Columbia': 'bc',",
        "    'Alberta':          'alberta',",
        "    'Quebec':           'quebec',",
        "}",
    ])
    story += cb(st, "3. Create backend/adapters/canada_adapter.py:", [
        "from .base_adapter import BaseElectricalAdapter",
        "",
        "class CanadaElectricalAdapter(BaseElectricalAdapter):",
        "    cable_sizing_standard = 'CEC C22.1:2021 Rule 4-004 / NEC 310.16'",
        "    voltage_lv = 347.0",
        "    voltage_phase = 120.0",
        "    design_ambient_temp = 30.0",
        "    voltage_drop_limit_power = 5.0",
        "",
        "    def get_tabulated_rating(self, size, cable_type, method):",
        "        return self.XLPE_CU_75C.get(size, 0)",
        "    # ... implement all other required methods",
    ])
    story += cb(st, "4. Register in backend/engines/adapters_factory.py:", [
        "from backend.adapters.canada_adapter import CanadaElectricalAdapter",
        "",
        "def get_electrical_adapter(region, sub_region):",
        "    if region == 'gcc':       return GCCElectricalAdapter(sub_region)",
        "    elif region == 'europe':  return EuropeElectricalAdapter(sub_region)",
        "    elif region == 'india':   return IndiaElectricalAdapter(sub_region)",
        "    elif region == 'australia': return AustraliaElectricalAdapter(sub_region)",
        "    elif region == 'canada':  return CanadaElectricalAdapter(sub_region)  # NEW",
        "    else: raise ValueError(f'Unknown region: {region}')",
    ])
    story += [
        SP(0.3),
        h2(st, "12.3  What You Must NEVER Break"),
        co(st,
            "CRITICAL -- these elements must remain stable. Changing them will break "
            "all 26 Streamlit pages, Docker healthchecks, or existing API clients simultaneously.\n\n"
            "1. api_post() and api_get() signatures in utils.py -- all 26 pages depend on them\n"
            "2. region_selector() return signature -- must return (region: str, sub_region: str)\n"
            "3. /health endpoint response -- Docker healthcheck expects {status: healthy}\n"
            "4. Pydantic field names in request models -- changing a name is a breaking API change\n"
            "5. The prefix='/api' on all routers -- changing this breaks all Streamlit API calls\n"
            "6. SUB_REGIONS_L3 dict key names -- changing a key breaks the 3-level selector\n"
            "7. CableSizingResult field names -- downstream clients depend on these JSON keys",
            style="warn"),
        SP(0.2),
        h2(st, "12.4  Testing Your Changes"),
    ]
    story += cb(st, "Run tests before submitting any change:", [
        "# Run all unit tests",
        "pytest backend/tests/ -v",
        "",
        "# Run tests for a specific module",
        "pytest backend/tests/test_cable_sizing.py -v",
        "",
        "# Test a new endpoint manually with cURL",
        "curl -X POST http://localhost:8000/api/electrical/transformer-sizing \\",
        "  -H 'Content-Type: application/json' \\",
        "  -d '{\"region\": \"gcc\", \"connected_load_kva\": 500}'",
        "",
        "# Check that Swagger docs updated",
        "# Open http://localhost:8000/docs -- your new endpoint should appear",
        "",
        "# Test Streamlit page in browser",
        "# Open http://localhost:8501 --> navigate to page 27",
        "# Fill in values and verify results make engineering sense",
    ])
    return story


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 13 — KNOWN ISSUES
# ─────────────────────────────────────────────────────────────────────────────
def section_13(st):
    story = sb(st, "13", "Known Issues & Limitations")
    story += [
        lead(st, "Honest documentation of what the current version cannot do. "
                 "All limitations below are addressed in the v0.2.0 or later roadmap."),
        SP(0.2),
        h2(st, "13.1  Current Limitations"),
        dt(st, ["Area", "Limitation", "Engineering Impact", "Fix Version"], [
            ["Authentication",
             "API has no access control in v0.1.0. Anyone who can reach port 8000 can call any endpoint.",
             "High risk for public internet deployment", "v0.2.0"],
            ["Database",
             "No calculation persistence. All results lost on page refresh.",
             "Users must re-enter inputs each session", "v0.2.0"],
            ["Harmonic Derating",
             "Cable sizing does not apply K-factor derating for non-linear loads (VFDs, UPS, data centres).",
             "May undersize cables for heavily harmonics-loaded circuits", "v0.2.0"],
            ["Motor Starting",
             "Cable sizing uses steady-state current. Starting current surge not considered for sizing.",
             "May undersize switchgear for direct-on-line started motors", "v0.2.0"],
            ["Cooling Load Method",
             "Uses simplified CLTD method. Does not run a full hourly load profile simulation.",
             "May over- or under-estimate by 5-10% vs detailed simulation", "v0.3.0"],
            ["Regional Coverage",
             "Only 4 regions. North America (NEC/CEC), MENA non-GCC, and South Africa are missing.",
             "Cannot be used for Canadian or US projects in current form", "v0.2.0"],
            ["Mobile UI",
             "Streamlit is not optimised for mobile screen sizes.",
             "Poor user experience on phones", "v0.4.0"],
            ["Standards Updates",
             "Standards data is hardcoded. No automatic update when standards are revised.",
             "Engineer must check if referenced edition is current", "v0.3.0"],
            ["Submittal Tracker",
             "Resets on page refresh. No export to Excel in current version.",
             "Cannot persist project tracking data", "v0.2.0"],
            ["Cable Sizes > 300mm2",
             "Standard size table stops at 300mm2. Large industrial feeders may need more.",
             "Engineer must manually check larger sizes", "v0.2.0"],
        ], [3*cm, 5*cm, 4.5*cm, 2.5*cm]),
        SP(0.3),
        h2(st, "13.2  Engineering Edge Cases"),
        body(st, "Engineers should be aware of these calculation edge cases:"),
        bul(st, "<b>Very long cable runs (>500m):</b> Algorithm may select excessively large cables. For runs over 500m, consider intermediate substations or verify with manufacturer data."),
        bul(st, "<b>Multi-orientation rooms:</b> The cooling load CLTD method assumes a dominant orientation. For rooms with glass on multiple facades, run a separate calculation for each facade and sum the gains."),
        bul(st, "<b>Sprinkler hazard classification:</b> OpenMEP relies on the user providing the correct NFPA/BS EN hazard class. Wrong classification produces a technically correct but practically unsafe design."),
        bul(st, "<b>BOQ rates are indicative only:</b> All unit rates in the BOQ module are typical market values for the region. Always obtain current supplier quotes before using in a tender document."),
        bul(st, "<b>Motor starting voltage drop:</b> The voltage drop calculation uses steady-state current. For DOL motor starting, the starting current is typically 6-7x the full-load current and must be checked separately."),
        bul(st, "<b>Single-phase current imbalance:</b> Maximum demand calculation assumes balanced 3-phase loading. If single-phase loads create imbalance greater than 10%, check neutral conductor sizing separately."),
    ]
    return story


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 14 — AI SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
def section_14(st):
    story = sb(st, "14", "Summary for AI Understanding")
    story += [
        lead(st, "This section is written specifically to help another AI model or "
                 "a new developer quickly understand this entire codebase. "
                 "It is a compact but complete reference."),
        SP(0.2),
        h2(st, "14.1  What This Project Is — One Paragraph"),
        co(st,
            "OpenMEP is a Python-based open-source engineering calculation suite with two main "
            "components: (1) a FastAPI REST API that accepts engineering parameters as JSON and "
            "returns calculation results as JSON, and (2) a Streamlit web UI with 26 numbered "
            "pages that provide a graphical interface to that API. Both run as separate processes "
            "and communicate over HTTP. All calculation logic lives in backend/engines/. Regional "
            "standards data is injected via an adapter pattern. No database is needed for "
            "calculations -- all state is passed in the request body.",
            style="good"),
        SP(0.3),
        h2(st, "14.2  Component Map — One Line Per Component"),
        dt(st, ["Component", "Role", "Key File(s)"], [
            ["FastAPI app",           "Creates HTTP server, registers all routers", "backend/main.py"],
            ["Settings",             "Region maps, environment variables", "backend/config.py"],
            ["Electrical routes",    "9 electrical API endpoints", "backend/api/routes/electrical.py"],
            ["Mechanical routes",    "5 HVAC API endpoints", "backend/api/routes/mechanical.py"],
            ["Plumbing routes",      "6 plumbing API endpoints", "backend/api/routes/plumbing.py"],
            ["Fire routes",          "4 fire protection endpoints", "backend/api/routes/fire.py"],
            ["BOQ routes",           "2 BOQ endpoints", "backend/api/routes/boq.py"],
            ["Compliance routes",    "2 compliance endpoints", "backend/api/routes/compliance.py"],
            ["Reports routes",       "3 report endpoints", "backend/api/routes/reports.py"],
            ["Calculation engines",  "Pure maths -- no HTTP", "backend/engines/*/"],
            ["Standards adapters",   "Region-specific tables and constants", "backend/adapters/"],
            ["Adapter factory",      "Returns correct adapter for region", "backend/engines/adapters_factory.py"],
            ["Streamlit landing",    "Hero banner, module cards, API status", "streamlit_app/app.py"],
            ["Shared utilities",     "Colours, API_BASE, region_selector, api_post", "streamlit_app/utils.py"],
            ["26 calculation pages", "UI for each calculation module", "streamlit_app/pages/1_...26_"],
            ["PDF generator",        "ReportLab documentation builder", "scripts/generate_tech_docs.py"],
            ["Docker setup",         "3-service containerised deployment", "docker-compose.yml, Dockerfile"],
        ], [4*cm, 5.5*cm, CONTENT_W - 9.5*cm]),
        SP(0.3),
        h2(st, "14.3  The Patterns Every AI Must Know"),
        h3(st, "Pattern 1 — Standards Adapter"),
        body(st,
            "The same calculation function runs for ALL regions. The adapter object "
            "injects region-specific data (cable tables, temperature limits, voltage drop limits). "
            "Never hard-code GCC/Europe/India/Australia data inside an engine. Always get it "
            "from the adapter."),
        h3(st, "Pattern 2 — Stateless API"),
        body(st,
            "Every POST endpoint is fully self-contained. The request body includes ALL "
            "data needed. There is no user session in the API. Do not add server-side "
            "state to calculation endpoints — it will break horizontal scaling."),
        h3(st, "Pattern 3 — 3-Level Region Selector"),
        body(st,
            "region_selector() returns (region, sub_region). The region is the top-level code "
            "(gcc, europe, india, australia). The sub_region is the utility authority code "
            "(dewa, kahramaa, bescom, ausgrid). Always pass BOTH in the API request."),
        h3(st, "Pattern 4 — Numbered Streamlit Pages"),
        body(st,
            "Streamlit auto-generates the sidebar from files named N_Title.py. "
            "The number determines sort order. Never rename these files without "
            "renumbering consistently."),
        h3(st, "Pattern 5 — Pydantic Request Models"),
        body(st,
            "Every POST endpoint has a Pydantic model defining its request. "
            "Required fields use Field(...). Optional fields have defaults. "
            "Never add manual validation inside route handlers — use Pydantic constraints "
            "(gt=0, ge=0.1, le=1.0, etc.)."),
        SP(0.3),
        h2(st, "14.4  Quick Extension Reference for AI"),
    ]
    story += cb(st, "To add a new calculator -- checklist:", [
        "[]  Create backend/engines/<discipline>/<name>.py",
        "    - @dataclass for Input and Result",
        "    - def calculate_<name>(inp, adapter) -> Result",
        "    - All constants from adapter, not hardcoded",
        "",
        "[]  Add Pydantic model + @router.post route to backend/api/routes/<discipline>.py",
        "    - Import the engine function",
        "    - Map request model fields to engine Input fields",
        "    - Return engine result directly (FastAPI auto-serialises)",
        "",
        "[]  Create streamlit_app/pages/<N+1>_<Name>.py",
        "    - from utils import region_selector, api_post",
        "    - 5-step pattern: set_page_config -> title -> region_selector -> form -> api_post",
        "    - Display results as st.metric() and/or st.table()",
        "",
        "[]  Add unit tests in backend/tests/test_<name>.py",
        "    - Test with all 4 regions",
        "    - Test boundary values (minimum load, maximum length, etc.)",
        "    - Test that invalid inputs raise appropriate errors",
    ])
    story += cb(st, "To add a new region -- checklist:", [
        "[]  Add code to SUPPORTED_REGIONS in backend/config.py",
        "[]  Add L2 entries to SUB_REGIONS_L2[new_region] in utils.py",
        "[]  Add L3 entries to SUB_REGIONS_L3 for each L2 sub-region in utils.py",
        "[]  Create backend/adapters/<region>_adapter.py extending BaseElectricalAdapter",
        "[]  Register adapter in backend/engines/adapters_factory.py",
        "[]  Create docs/regions/<REGION>_GUIDE.md with standard references",
        "[]  Add the region to the README feature matrix",
    ])
    story += [
        SP(0.3),
        h2(st, "14.5  File to Read First When Debugging"),
        dt(st, ["Problem", "First File to Check", "Why"], [
            ["API returns 422 error",
             "backend/api/routes/<discipline>.py",
             "Check the Pydantic model field names and constraints"],
            ["Calculation gives wrong answer",
             "backend/engines/<discipline>/<name>.py",
             "Check the formula implementation and adapter data used"],
            ["Wrong standards data returned",
             "backend/adapters/<region>_adapter.py",
             "Check the cable table or factor table for the region"],
            ["Streamlit cannot connect to API",
             "streamlit_app/utils.py",
             "Check API_BASE -- should be http://localhost:8000 for local"],
            ["Streamlit page shows no results",
             "The specific page file + utils.py api_post()",
             "Check the endpoint path and payload field names"],
            ["Docker service won't start",
             "docker-compose.yml + Dockerfile",
             "Check service dependencies and healthcheck commands"],
            ["Environment variable not picked up",
             ".env file + config.py Settings class",
             "Check the variable name and whether .env is present"],
        ], [4.5*cm, 5.5*cm, CONTENT_W - 10*cm]),
    ]
    return story


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 15 — STANDARDS DATA TABLES
# ─────────────────────────────────────────────────────────────────────────────
def section_15(st):
    story = sb(st, "15", "Standards Data Tables — Real Numerical Values")
    story += [
        lead(st, "This section contains the actual numerical data embedded in OpenMEP. "
                 "These are the values the calculation engines use — reproduced here "
                 "for verification, auditing, and offline reference."),
        SP(0.2),
    ]

    sizes = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 630]

    # ── GCC XLPE COPPER ──────────────────────────────────────────────────────
    story.append(Paragraph("1 — GCC/Europe  BS 7671 Table 4D5A: XLPE Copper Cable Ratings (A)", st["h2"]))
    story.append(Paragraph(
        "Base conditions: 30°C ambient, no grouping. Apply Ca and Cg derating factors before use. "
        "GCC uses identical tables to Europe/UK — Ca and Cg values differ by region.",
        st["body"]))

    xlpe_cu = {
        "A1":  [13, 17, 23, 29, 39, 52, 67, 83, 99, 126, 153, 178, 201, 230, 269, 306, 0, 0],
        "A2":  [13, 17, 23, 29, 39, 53, 69, 86, 103,132, 160, 185, 211, 240, 280, 319, 0, 0],
        "B1":  [15, 19, 25, 32, 44, 58, 76, 94, 113,143, 174, 201, 229, 261, 304, 348, 0, 0],
        "B2":  [15, 18, 24, 31, 42, 56, 73, 90, 108,137, 167, 192, 218, 248, 291, 334, 0, 0],
        "C":   [17, 23, 30, 38, 51, 68, 89, 110,134,171, 207, 239, 272, 310, 365, 419, 0, 0],
        "E/F": [17, 23, 30, 38, 52, 71, 93, 116,141,180, 219, 253, 288, 328, 386, 442, 510,655],
    }
    size_labels = [str(s) for s in sizes]
    xlpe_cu_rows = []
    for method, vals in xlpe_cu.items():
        row = [method] + [str(v) if v > 0 else "--" for v in vals]
        xlpe_cu_rows.append(row)
    cw_main = [2*cm] + [(CONTENT_W - 2*cm) / 18] * 18
    story.append(mono_table(
        ["Method"] + size_labels,
        xlpe_cu_rows, col_widths=cw_main, st=st))
    story.append(Paragraph("Source: BS 7671:2018+A2:2022 Table 4D5A — Single-core 90°C XLPE copper", st["caption"]))
    story.append(sp(10))

    # ── GCC PVC COPPER ────────────────────────────────────────────────────────
    story.append(Paragraph("2 — GCC/Europe  BS 7671 Table 4D2A: PVC Copper Cable Ratings (A)", st["h2"]))
    pvc_cu = {
        "A1":  [11, 14, 18, 23, 31, 41, 53, 65, 77, 97, 117, 135, 152, 175, 202, 228, 0, 0],
        "A2":  [11, 14, 18, 23, 31, 42, 54, 67, 80, 101,122, 141, 160, 183, 210, 240, 0, 0],
        "B1":  [13, 16, 21, 27, 36, 48, 62, 76, 91, 115,139, 162, 184, 209, 244, 280, 0, 0],
        "B2":  [12, 15, 20, 26, 35, 46, 60, 74, 88, 112,136, 156, 178, 203, 237, 272, 0, 0],
        "C":   [15, 20, 26, 33, 45, 60, 78, 96, 116,149, 180, 207, 237, 270, 318, 362, 0, 0],
        "E/F": [15, 20, 26, 33, 46, 61, 80, 99, 119,151, 183, 210, 240, 273, 321, 368, 424,539],
    }
    pvc_cu_rows = []
    for method, vals in pvc_cu.items():
        pvc_cu_rows.append([method] + [str(v) if v > 0 else "--" for v in vals])
    story.append(mono_table(
        ["Method"] + size_labels,
        pvc_cu_rows, col_widths=cw_main, st=st))
    story.append(Paragraph("Source: BS 7671:2018+A2:2022 Table 4D2A — Single-core 70°C PVC copper", st["caption"]))
    story.append(sp(10))

    # ── INDIA IS 3961 XLPE ────────────────────────────────────────────────────
    story.append(Paragraph("3 — India  IS 3961 XLPE Copper Cable Ratings (A)", st["h2"]))
    story.append(Paragraph(
        "Base conditions: 45°C ambient (Indian design reference temperature), no grouping. "
        "Three-and-a-half core FRLS cables per IS 7098 Part 1.",
        st["body"]))

    india_xlpe = {
        "A (conduit in wall)": [13, 17, 22, 29, 39, 51, 65, 80, 96, 120, 146, 168, 192, 219, 255, 291, 0, 0],
        "B (conduit surface)": [15, 19, 25, 32, 43, 58, 74, 91, 110,139, 170, 196, 223, 254, 296, 338, 0, 0],
        "C (clipped surface)": [17, 23, 30, 38, 51, 68, 88, 109,132,169, 204, 235, 267, 305, 356, 408, 0, 0],
        "D (underground)":     [19, 25, 32, 41, 56, 74, 96, 118,143,182, 220, 253, 288, 328, 383, 437, 0, 0],
    }
    india_rows = []
    for method, vals in india_xlpe.items():
        india_rows.append([method] + [str(v) if v > 0 else "--" for v in vals])
    story.append(mono_table(
        ["Method"] + size_labels,
        india_rows, col_widths=cw_main, st=st))
    story.append(Paragraph("Source: IS 3961:2011 Part 1-2 — XLPE insulated aluminium/copper conductors", st["caption"]))
    story.append(sp(10))

    # ── AUSTRALIA X-90 ────────────────────────────────────────────────────────
    story.append(Paragraph("4 — Australia  AS/NZS 3008.1.1 X-90 Copper Cable Ratings (A)", st["h2"]))
    story.append(Paragraph(
        "Base conditions: 40°C air / 25°C ground ambient (Australian reference temperatures), no grouping.",
        st["body"]))

    aus_x90 = {
        "col_6 (enclosed/conduit)": [14, 18, 24, 31, 43, 57, 75, 93, 112,143, 174, 201, 229, 261, 304, 348, 0, 0],
        "col_9 (direct burial)":    [19, 25, 33, 42, 57, 77, 100,124,149,190, 230, 264, 301, 342, 399, 457, 0, 0],
        "col_13 (buried conduit)":  [16, 21, 27, 35, 48, 64, 83, 103,124,157, 191, 220, 250, 285, 332, 379, 0, 0],
        "col_22 (clipped surface)": [17, 23, 31, 40, 55, 73, 96, 119,144,184, 223, 258, 294, 335, 391, 448, 524,667],
    }
    aus_rows = []
    for method, vals in aus_x90.items():
        aus_rows.append([method] + [str(v) if v > 0 else "--" for v in vals])
    story.append(mono_table(
        ["Method"] + size_labels,
        aus_rows, col_widths=cw_main, st=st))
    story.append(Paragraph("Source: AS/NZS 3008.1.1:2017 Tables 3 & 7 — X-90 XLPE copper", st["caption"]))
    story.append(sp(10))

    # ── AUSTRALIA V-75 ────────────────────────────────────────────────────────
    story.append(Paragraph("5 — Australia  AS/NZS 3008.1.1 V-75 PVC Copper Cable Ratings (A)", st["h2"]))
    aus_v75 = {
        "col_6 (enclosed/conduit)": [11, 15, 20, 26, 36, 48, 62, 77, 93, 118, 143, 165, 189, 215, 250, 286, 0, 0],
        "col_9 (direct burial)":    [16, 21, 28, 36, 50, 67, 87, 107,130,165, 200, 230, 262, 297, 346, 396, 0, 0],
        "col_22 (clipped surface)": [14, 19, 26, 33, 46, 61, 80, 99, 120,153, 186, 214, 244, 278, 325, 373, 433,551],
    }
    aus_v75_rows = []
    for method, vals in aus_v75.items():
        aus_v75_rows.append([method] + [str(v) if v > 0 else "--" for v in vals])
    story.append(mono_table(
        ["Method"] + size_labels,
        aus_v75_rows, col_widths=cw_main, st=st))
    story.append(Paragraph("Source: AS/NZS 3008.1.1:2017 Tables 3 & 7 — V-75 PVC copper", st["caption"]))
    story.append(sp(14))

    # ── AUSTRALIA METHOD MAPPING ───────────────────────────────────────────────
    story.append(Paragraph("6 — Australia UI Code to AS/NZS 3008 Column Mapping", st["h2"]))
    story.append(Paragraph(
        "The OpenMEP Streamlit UI uses generic letter codes (A, B, C, D). "
        "The Australia adapter maps these to AS/NZS 3008 column numbers before performing the lookup.",
        st["body"]))
    map_rows = [
        ["A", "col_6",  "Conduit in wall / enclosed conduit (worst case — least heat dissipation)"],
        ["B", "col_13", "Buried in conduit underground"],
        ["C", "col_22", "Clipped flat to surface"],
        ["D", "col_9",  "Direct burial in ground (best rating for underground)"],
    ]
    story.append(data_table(["UI Code", "AS/NZS 3008 Column", "Installation Description"],
                            map_rows, col_widths=[2*cm, 4*cm, CONTENT_W - 6*cm], st=st))
    story.append(sp(14))

    # ── AMBIENT TEMPERATURE CORRECTION FACTORS ────────────────────────────────
    story.append(Paragraph("7 — Ambient Temperature Correction Factors (Ca)", st["h2"]))
    story.append(Paragraph(
        "Ca is applied to the base cable rating: Iz_corrected = It_base × Ca. "
        "Values below 1.00 derate; values above 1.00 allow uprating for cool ambients.",
        st["body"]))

    story.append(Paragraph("7a — BS 7671 XLPE/Cu (Reference: 30°C)", st["h3"]))
    xlpe_ca_temps = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]
    xlpe_ca_factors = [1.15, 1.12, 1.08, 1.04, 1.00, 0.96, 0.91, 0.87, 0.82, 0.76, 0.71, 0.65, 0.58, 0.50, 0.41]
    ca_col_w = [CONTENT_W / 15] * 15
    story.append(mono_table(
        ["10°C", "15°C", "20°C", "25°C", "30°C", "35°C", "40°C", "45°C",
         "50°C", "55°C", "60°C", "65°C", "70°C", "75°C", "80°C"],
        [[str(f) for f in xlpe_ca_factors]],
        col_widths=ca_col_w, st=st))
    story.append(Paragraph("Source: BS 7671 Table 4B1 — XLPE", st["caption"]))
    story.append(sp(8))

    story.append(Paragraph("7b — BS 7671 PVC/Cu (Reference: 30°C)", st["h3"]))
    pvc_ca_factors = [1.22, 1.17, 1.12, 1.06, 1.00, 0.94, 0.87, 0.79, 0.71, 0.61, 0.50]
    ca_col_w11 = [CONTENT_W / 11] * 11
    story.append(mono_table(
        ["10°C", "15°C", "20°C", "25°C", "30°C", "35°C", "40°C", "45°C", "50°C", "55°C", "60°C"],
        [[str(f) for f in pvc_ca_factors]],
        col_widths=ca_col_w11, st=st))
    story.append(Paragraph("Source: BS 7671 Table 4B1 — PVC (max 60°C ambient)", st["caption"]))
    story.append(sp(8))

    story.append(Paragraph("7c — India IS 3961 XLPE (Reference: 45°C)", st["h3"]))
    in_ca_factors = [1.13, 1.09, 1.05, 1.02, 1.00, 0.96, 0.91, 0.87, 0.82, 0.76]
    ca_col_w10 = [CONTENT_W / 10] * 10
    story.append(mono_table(
        ["25°C", "30°C", "35°C", "40°C", "45°C", "50°C", "55°C", "60°C", "65°C", "70°C"],
        [[str(f) for f in in_ca_factors]],
        col_widths=ca_col_w10, st=st))
    story.append(Paragraph("Source: IS 3961:2011 Appendix — XLPE reference 45°C", st["caption"]))
    story.append(sp(8))

    story.append(Paragraph("7d — India IS 3961 PVC (Reference: 45°C)", st["h3"]))
    in_pvc_factors = [1.19, 1.14, 1.09, 1.04, 1.00, 0.94, 0.87]
    ca_col_w7 = [CONTENT_W / 7] * 7
    story.append(mono_table(
        ["25°C", "30°C", "35°C", "40°C", "45°C", "50°C", "55°C"],
        [[str(f) for f in in_pvc_factors]],
        col_widths=ca_col_w7, st=st))
    story.append(Paragraph("Source: IS 3961:2011 Appendix — PVC reference 45°C", st["caption"]))
    story.append(sp(8))

    story.append(Paragraph("7e — Australia X-90 Air (Reference: 40°C)", st["h3"]))
    aus_ca_factors = [1.15, 1.11, 1.07, 1.03, 1.00, 0.96, 0.91, 0.87, 0.82, 0.76]
    story.append(mono_table(
        ["20°C", "25°C", "30°C", "35°C", "40°C", "45°C", "50°C", "55°C", "60°C", "65°C"],
        [[str(f) for f in aus_ca_factors]],
        col_widths=ca_col_w10, st=st))
    story.append(Paragraph("Source: AS/NZS 3008 Table 13 — X-90 air ambient reference 40°C", st["caption"]))
    story.append(sp(8))

    story.append(Paragraph("7f — Australia X-90 Ground (Reference: 25°C)", st["h3"]))
    aus_gnd_factors = [1.10, 1.07, 1.04, 1.00, 0.96, 0.92, 0.87, 0.82, 0.77]
    ca_col_w9 = [CONTENT_W / 9] * 9
    story.append(mono_table(
        ["10°C", "15°C", "20°C", "25°C", "30°C", "35°C", "40°C", "45°C", "50°C"],
        [[str(f) for f in aus_gnd_factors]],
        col_widths=ca_col_w9, st=st))
    story.append(Paragraph("Source: AS/NZS 3008 Table 13 — X-90 ground reference 25°C", st["caption"]))
    story.append(sp(8))

    story.append(Paragraph("7g — Australia V-75 Air (Reference: 40°C)", st["h3"]))
    aus_v75_factors = [1.20, 1.15, 1.10, 1.05, 1.00, 0.94, 0.87, 0.79]
    ca_col_w8 = [CONTENT_W / 8] * 8
    story.append(mono_table(
        ["20°C", "25°C", "30°C", "35°C", "40°C", "45°C", "50°C", "55°C"],
        [[str(f) for f in aus_v75_factors]],
        col_widths=ca_col_w8, st=st))
    story.append(Paragraph("Source: AS/NZS 3008 Table 13 — V-75 air reference 40°C", st["caption"]))
    story.append(sp(14))

    # ── GROUPING CORRECTION FACTORS ───────────────────────────────────────────
    story.append(Paragraph("8 — Grouping / Bunching Correction Factors (Cg)", st["h2"]))
    story.append(Paragraph(
        "Cg is multiplied with the base rating: Iz = It × Ca × Cg. "
        "'Touching' = cables in contact; 'Spaced' = cables ≥ 1 diameter apart. "
        "All four regions use the same grouping factor table (BS 7671 / IEC 60364 basis). "
        "Values are linearly interpolated for circuit counts between listed values.",
        st["body"]))
    cg_num = [1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 16, 20]
    cg_touch = [1.00, 0.80, 0.70, 0.65, 0.60, 0.57, 0.54, 0.52, 0.50, 0.45, 0.41, 0.38]
    cg_spaced = [1.00, 0.88, 0.82, 0.77, 0.73, 0.72, 0.72, 0.71, 0.70, 0.70, 0.70, 0.70]
    cg_india_tray = [1.00, 0.88, 0.77, 0.70, 0.66, 0.62, "-", 0.58, "-", 0.55, "-", 0.52]
    cg_col_w = [3*cm] + [(CONTENT_W - 3*cm) / 12] * 12
    story.append(mono_table(
        ["Circuits ->"] + [str(n) for n in cg_num],
        [
            ["Touching (GCC/EU/AUS)"] + [str(f) for f in cg_touch],
            ["Spaced (GCC/EU/AUS)"]   + [str(f) for f in cg_spaced],
            ["India on tray (IS)"]    + [str(f) for f in cg_india_tray],
        ],
        col_widths=cg_col_w, st=st))
    story.append(Paragraph(
        "Source: BS 7671 Table 4C1 (GCC/Europe/Australia) · IS 3961 Appendix (India on tray)",
        st["caption"]))
    story.append(sp(14))

    # ── VOLTAGE DROP DATA ──────────────────────────────────────────────────────
    story.append(Paragraph("9 — Voltage Drop Data — mV/A/m (3-phase, multicore)", st["h2"]))
    story.append(Paragraph(
        "VD_total [V] = (mV/A/m value) × Ib [A] × Length [m] / 1000. "
        "For single-phase: multiply 3-phase value by (2/√3) = 1.155.",
        st["body"]))
    vd_xlpe_gcc = [29, 18, 11, 7.3, 4.4, 2.8, 1.75, 1.25, 0.93, 0.63, 0.47, 0.37, 0.30, 0.24, 0.19, 0.15, 0.12, 0.077]
    vd_pvc_gcc  = [31, 19, 12, 7.9, 4.7, 3.0, 1.85, 1.32, 0.98, 0.67, 0.49, 0.39, 0.31, 0.25, 0.20, 0.16, 0.12, 0.079]
    vd_india    = [29, 18, 11, 7.5, 4.5, 2.85, 1.80, 1.28, 0.95, 0.65, 0.48, 0.38, 0.31, 0.25, 0.19, 0.15, 0.12, 0.077]
    vd_aus_x90  = [28.3, 17.0, 10.7, 7.15, 4.25, 2.7, 1.70, 1.22, 0.90, 0.61, 0.45, 0.36, 0.29, 0.23, 0.183, 0.147, 0.115, 0.074]
    vd_aus_v75  = [30.3, 18.2, 11.4, 7.64, 4.55, 2.89, 1.82, 1.30, 0.96, 0.66, 0.48, 0.38, 0.31, 0.25, 0.196, 0.157, 0.122, 0.079]
    vd_col_w = [3.5*cm] + [(CONTENT_W - 3.5*cm) / 18] * 18
    story.append(mono_table(
        ["Cable Type"] + [str(s) for s in sizes],
        [
            ["GCC/EU XLPE-Cu"] + [str(v) for v in vd_xlpe_gcc],
            ["GCC/EU PVC-Cu"]  + [str(v) for v in vd_pvc_gcc],
            ["India XLPE-Cu"]  + [str(v) for v in vd_india],
            ["AUS X-90 Cu"]    + [str(v) for v in vd_aus_x90],
            ["AUS V-75 Cu"]    + [str(v) for v in vd_aus_v75],
        ],
        col_widths=vd_col_w, st=st))
    story.append(Paragraph(
        "Source: BS 7671 Table 4D5B (XLPE) / 4D2B (PVC) · IS 3961 Appendix E · AS/NZS 3008 Table 30",
        st["caption"]))
    story.append(sp(14))

    # ── EARTH CONDUCTOR SIZES ──────────────────────────────────────────────────
    story.append(Paragraph("10 — Minimum Protective Conductor / Earthing Conductor Sizes (mm²)", st["h2"]))
    story.append(Paragraph(
        "The earthing (CPC) conductor minimum size is determined by the phase conductor size. "
        "These are the minimum tabulated values — adiabatic equation check (Cl. 543.1) "
        "should also be performed for fault currents greater than 100 A.",
        st["body"]))
    cpc_line   = [1.0, 1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]
    cpc_bs7671 = [1.0, 1.0, 1.0, 1.5, 2.5, 4.0, 6.0, 10, 16, 16, 35, 50, 70, 70, 95, 120, 150]
    cpc_is3043 = [1.5, 1.5, 1.5, 2.5, 4.0, 6.0, 10, 16, 16, 25, 35, 50, 70, 70, 95, 120, 150]
    cpc_asnzs  = [1.5, 1.5, 1.5, 2.5, 4.0, 4.0, 6.0, 10, 16, 25, 35, 50, 70, 70, 95, 120, 150]
    cpc_col_w = [5*cm] + [(CONTENT_W - 5*cm) / 17] * 17
    story.append(mono_table(
        ["Standard / Phase (mm²)"] + [str(s) for s in cpc_line],
        [
            ["BS 7671 Table 54.7 (GCC & Europe)"] + [str(v) for v in cpc_bs7671],
            ["IS 3043:2018 (India)"]               + [str(v) for v in cpc_is3043],
            ["AS/NZS 3000 Table 5.1 (Australia)"]  + [str(v) for v in cpc_asnzs],
        ],
        col_widths=cpc_col_w, st=st))
    story.append(sp(14))

    # ── GCC AUTHORITY COMPARISON ───────────────────────────────────────────────
    story.append(Paragraph("11 — GCC Authority Specific Parameters", st["h2"]))
    gcc_auth_rows = [
        ["DEWA (Dubai)",     "UAE",    "3.0%", "4.0%", "400/230 V", "50°C / 35°C", "BS 7671 + DEWA Regs"],
        ["ADDC (Abu Dhabi)", "UAE",    "3.0%", "5.0%", "400/230 V", "50°C / 35°C", "BS 7671 + ADDC Regs"],
        ["AADC (Al Ain)",    "UAE",    "3.0%", "5.0%", "400/230 V", "50°C / 35°C", "BS 7671 + AADC Regs"],
        ["KAHRAMAA",         "Qatar",  "3.0%", "5.0%", "400/230 V", "50°C / 35°C", "BS 7671 + KAHRAMAA Regs"],
        ["SEC (Saudi Arabia)","KSA",   "2.5%", "4.0%", "380/220 V", "50°C / 35°C", "BS 7671 + SBC / SEC Regs"],
        ["MEW (Kuwait)",     "Kuwait", "3.0%", "5.0%", "415/240 V", "50°C / 35°C", "BS 7671 + MEW Regs"],
    ]
    story.append(data_table(
        ["Authority", "Country", "Light VD", "Power VD", "System V", "Design Ambient", "Standard Basis"],
        gcc_auth_rows,
        col_widths=[3.5*cm, 2*cm, 1.8*cm, 2*cm, 2.2*cm, 3*cm, CONTENT_W - 14.5*cm],
        st=st))
    story.append(sp(14))

    # ── CROSS-REGION SUMMARY ───────────────────────────────────────────────────
    story.append(Paragraph("12 — Cross-Region Summary", st["h2"]))
    story.append(Paragraph(
        "Key differences at a glance — the most common causes of calculation discrepancies "
        "when switching between regions.",
        st["body"]))
    summary_rows = [
        ["Cable standard",      "BS 7671 Table 4D5A",  "BS 7671 Table 4D5A",  "IS 3961 / IS 7098", "AS/NZS 3008 Table 3/7"],
        ["Cable type (default)","XLPE/SWA Cu",         "XLPE/SWA Cu",         "XLPE FRLS 3.5-core Cu", "X-90 XLPE Cu"],
        ["Ref temp (XLPE air)", "30°C",                "30°C",                "45°C",              "40°C"],
        ["Ca at design ambient","0.82 (50°C air)",     "1.00 (30°C = ref)",   "1.00 (45°C = ref)", "1.00 (40°C = ref)"],
        ["System voltage (LL)", "400 V",               "400 V",               "415 V",             "400 V"],
        ["Earthing standard",   "BS 7671 Table 54.7",  "BS 7671 Table 54.7",  "IS 3043:2018",      "AS/NZS 3000 Table 5.1"],
        ["Lighting VD limit",   "3.0% (most auth)",    "3.0%",                "3.0%",              "2.5% (feeder)"],
        ["Power VD limit",      "4-5% (by authority)", "5.0%",                "5.0%",              "5.0% (sub-circuit)"],
    ]
    story.append(data_table(
        ["Parameter", "GCC", "Europe/UK", "India", "Australia"],
        summary_rows,
        col_widths=[4.5*cm, 3.5*cm, 3.5*cm, 3.5*cm, CONTENT_W - 15*cm],
        st=st))
    story.append(sp(14))

    story.append(callout(
        "This section makes OpenMEP 100% self-contained as a technical document. "
        "An AI model with only this PDF can reproduce all cable sizing, correction factor, "
        "and voltage drop calculations that OpenMEP performs — without access to the "
        "source code repository.",
        "good", st))

    story.append(PageBreak())
    return story


# ─────────────────────────────────────────────────────────────────────────────
# BACK COVER
# ─────────────────────────────────────────────────────────────────────────────
class BackCover(Flowable):
    def draw(self):
        c = self.canv
        ox = -LM
        oy = -BM
        c.setFillColor(NAVY)
        c.rect(ox, oy, PW, PH, stroke=0, fill=1)
        c.setFillColor(TEAL)
        c.rect(ox, oy + PH - 8, PW, 8, stroke=0, fill=1)
        c.rect(ox, oy, PW, 6, stroke=0, fill=1)
        c.setStrokeColor(TEAL)
        c.setLineWidth(0.5)
        c.circle(ox + LM + 1.5*cm, oy + PH * 0.5, 2.5*cm, stroke=1, fill=0)
        c.setLineWidth(0.25)
        c.setStrokeColor(HexColor("#FFFFFF"))
        c.circle(ox + LM + 1.5*cm, oy + PH * 0.5, 4.0*cm, stroke=1, fill=0)

    def wrap(self, availW, availH):
        return (availW, availH)


def back_cover_page(st):
    story = [PageBreak(), BackCover(), sp(PH * 0.25)]
    story.append(Paragraph("OpenMEP", ParagraphStyle(
        "bc_title", fontName="Helvetica-Bold", fontSize=36, textColor=white,
        alignment=TA_CENTER, leading=44)))
    story.append(Paragraph("Open-Source MEP Engineering Calculation Suite", ParagraphStyle(
        "bc_sub", fontName="Helvetica", fontSize=13, textColor=TEAL_LIGHT,
        alignment=TA_CENTER, leading=20)))
    story.append(sp(28))
    for line in [
        "Made by  <b>Luquman A</b>",
        "github.com/kakarot-oncloud/openmep-suite",
        "MIT License  ·  Copyright © 2025 Luquman A",
        "Version 0.1.0  ·  4 Regions  ·  26 Modules  ·  35 API Endpoints",
    ]:
        story.append(Paragraph(line, ParagraphStyle(
            "bc_line", fontName="Helvetica", fontSize=10.5, textColor=white,
            alignment=TA_CENTER, leading=18)))
        story.append(sp(4))
    return story


# ─────────────────────────────────────────────────────────────────────────────
# MAIN BUILDER
# ─────────────────────────────────────────────────────────────────────────────
def build_pdf(output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=LM, rightMargin=RM,
        topMargin=TM, bottomMargin=BM,
        title="OpenMEP Advanced Technical Documentation",
        author="Luquman A",
        subject="MEP Engineering Calculation Suite — Comprehensive Technical Reference",
    )
    st = S()
    decorator = build_page_decorator(doc)

    story = []
    story += cover_page(st)
    story += toc_page(st)
    story += section_01(st)
    story += section_02(st)
    story += section_03(st)
    story += section_04(st)
    story += section_05(st)
    story += section_06(st)
    story += section_07(st)
    story += section_08(st)
    story += section_09(st)
    story += section_10(st)
    story += section_11(st)
    story += section_12(st)
    story += section_13(st)
    story += section_14(st)
    story += section_15(st)
    story += back_cover_page(st)

    doc.build(story, onFirstPage=decorator, onLaterPages=decorator)
    print(f"PDF generated: {output_path}")


if __name__ == "__main__":
    build_pdf("docs/OpenMEP_Technical_Documentation.pdf")
