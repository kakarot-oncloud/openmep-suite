"""
OpenMEP PDF Report Generator
Generates professional engineering calculation reports using ReportLab.
Regional letterhead and formatting per project plan Section 4.
"""

import io
from datetime import date
from typing import Optional, Dict, Any

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor
    from reportlab.lib.units import mm
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable,
    )
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False

# ── Theme colours ──────────────────────────────────────────────────────────────
RED = HexColor("#CC0000") if REPORTLAB_OK else None
BLACK_C = HexColor("#0A0A0A") if REPORTLAB_OK else None
DARK_GREY_C = HexColor("#1A1A1A") if REPORTLAB_OK else None
MID_GREY_C = HexColor("#444444") if REPORTLAB_OK else None
LIGHT_GREY_C = HexColor("#888888") if REPORTLAB_OK else None
WHITE_C = HexColor("#FFFFFF") if REPORTLAB_OK else None

# ── Regional header metadata ────────────────────────────────────────────────────
REGION_META = {
    "gcc": {
        "title": "GCC ENGINEERING CALCULATION",
        "subtitle": "Gulf Cooperation Council Region",
        "standards": "BS 7671:2018+A2:2022 / IEC 60364 / ASHRAE / BS EN 806",
        "authorities": "DEWA · ADDC · SEWA · KAHRAMAA · SEC · MEW",
        "disclaimer": "This calculation has been prepared in accordance with BS 7671:2018+A2:2022 (IEE Wiring Regulations 18th Edition) and relevant IEC standards as adopted by the respective GCC utility authority.",
        "footer_tag": "OpenMEP | GCC Edition | BS 7671 / IEC 60364",
    },
    "europe": {
        "title": "ENGINEERING CALCULATION",
        "subtitle": "United Kingdom & Europe",
        "standards": "BS 7671:2018+A2:2022 / CIBSE Guide / BS EN 806 / BS EN 12845",
        "authorities": "DNO / Distribution Network Operators",
        "disclaimer": "This calculation has been prepared in accordance with BS 7671:2018+A2:2022 (IET Wiring Regulations 18th Edition) and relevant CIBSE / BSRIA guidance.",
        "footer_tag": "OpenMEP | UK/EU Edition | BS 7671:2018+A2:2022",
    },
    "india": {
        "title": "ENGINEERING CALCULATION",
        "subtitle": "India — Bureau of Indian Standards",
        "standards": "IS 732:2019 / IS 3961:2011 / IS 7098 (FRLS) / IS 1172 / NBC 2016",
        "authorities": "CEA · MSEDCL · BESCOM · TANGEDCO · WBSEDCL · APDCL",
        "disclaimer": "This calculation has been prepared in accordance with IS 732:2019, IS 3961:2011, and NBC 2016 (National Building Code of India). FRLS cables mandatory per NBC Part 4.",
        "footer_tag": "OpenMEP | India Edition | IS 732 / IS 3961 / NBC 2016",
    },
    "australia": {
        "title": "ENGINEERING CALCULATION",
        "subtitle": "Australia / New Zealand",
        "standards": "AS/NZS 3000:2018 / AS/NZS 3008.1.1:2017 / AS 3500 / AS 2118",
        "authorities": "Ausgrid · Energex · CitiPower · Western Power · Orion NZ",
        "disclaimer": "This calculation has been prepared in accordance with AS/NZS 3000:2018 (Wiring Rules), AS/NZS 3008.1.1:2017, and relevant Australian Standards.",
        "footer_tag": "OpenMEP | AU/NZ Edition | AS/NZS 3000:2018",
    },
}


def _styles():
    """Build custom paragraph styles."""
    getSampleStyleSheet()
    custom = {
        "title": ParagraphStyle("CTitle", fontName="Helvetica-Bold", fontSize=14,
                                 textColor=WHITE_C, leading=18, spaceAfter=4, alignment=TA_LEFT),
        "subtitle": ParagraphStyle("CSubtitle", fontName="Helvetica", fontSize=9,
                                    textColor=LIGHT_GREY_C, leading=12, alignment=TA_LEFT),
        "section": ParagraphStyle("CSection", fontName="Helvetica-Bold", fontSize=9,
                                   textColor=RED, leading=14, spaceBefore=8, spaceAfter=4,
                                   borderPadding=(0, 0, 2, 0)),
        "body": ParagraphStyle("CBody", fontName="Helvetica", fontSize=9,
                                textColor=BLACK_C, leading=13, alignment=TA_JUSTIFY),
        "small": ParagraphStyle("CSmall", fontName="Helvetica", fontSize=7.5,
                                 textColor=LIGHT_GREY_C, leading=10),
        "mono": ParagraphStyle("CMono", fontName="Courier", fontSize=8,
                                textColor=BLACK_C, leading=12),
        "table_hdr": ParagraphStyle("CTblHdr", fontName="Helvetica-Bold", fontSize=8,
                                     textColor=WHITE_C, leading=10, alignment=TA_CENTER),
        "table_cell": ParagraphStyle("CTblCell", fontName="Helvetica", fontSize=8,
                                      textColor=BLACK_C, leading=10),
        "result": ParagraphStyle("CResult", fontName="Helvetica-Bold", fontSize=10,
                                  textColor=BLACK_C, leading=14),
        "compliance_pass": ParagraphStyle("CPass", fontName="Helvetica-Bold", fontSize=9,
                                           textColor=HexColor("#006622"), leading=12),
        "compliance_fail": ParagraphStyle("CFail", fontName="Helvetica-Bold", fontSize=9,
                                           textColor=HexColor("#CC0000"), leading=12),
    }
    return custom


def _header_table(meta: dict, project_info: dict, report_type: str, revision: str) -> Table:
    """Build the letterhead header table."""
    logo_cell = Paragraph("""<font color="#CC0000" size="24"><b>M</b></font>
        <br/><font color="#FFFFFF" size="6">OpenMEP v0.1.0</font>""",
        ParagraphStyle("Logo", fontName="Helvetica-Bold", fontSize=24,
                       textColor=WHITE_C, alignment=TA_CENTER))

    title_cell = [
        Paragraph(meta["title"], _styles()["title"]),
        Paragraph(meta["subtitle"], _styles()["subtitle"]),
        Spacer(1, 4),
        Paragraph(f"<b>Standard:</b> {meta['standards']}", _styles()["subtitle"]),
        Paragraph(f"<b>Authority:</b> {meta['authorities']}", _styles()["subtitle"]),
    ]

    project_cell = [
        Paragraph(f"<b>Project:</b> {project_info.get('project_name', '')}", _styles()["subtitle"]),
        Paragraph(f"<b>Client:</b> {project_info.get('client_name', '')}", _styles()["subtitle"]),
        Paragraph(f"<b>Engineer:</b> {project_info.get('engineer_name', '')}", _styles()["subtitle"]),
        Paragraph(f"<b>Checked:</b> {project_info.get('checked_by', '')}", _styles()["subtitle"]),
        Paragraph(f"<b>Doc No.:</b> {project_info.get('project_number', '')}-{report_type.upper()}-{revision}", _styles()["subtitle"]),
        Paragraph(f"<b>Date:</b> {project_info.get('date', str(date.today()))}", _styles()["subtitle"]),
        Paragraph(f"<b>Rev:</b> {revision}", _styles()["subtitle"]),
    ]

    data = [[logo_cell, title_cell, project_cell]]
    t = Table(data, colWidths=[30*mm, 95*mm, 60*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), BLACK_C),
        ("BACKGROUND", (1, 0), (1, 0), DARK_GREY_C),
        ("BACKGROUND", (2, 0), (2, 0), MID_GREY_C),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("LINEAFTER", (0, 0), (0, 0), 2, RED),
        ("LINEAFTER", (1, 0), (1, 0), 0.5, LIGHT_GREY_C),
        ("BOX", (0, 0), (-1, -1), 0.5, LIGHT_GREY_C),
    ]))
    return t


def _result_table(data_rows: list) -> Table:
    """Build a styled results table."""
    headers = [
        Paragraph("Parameter", _styles()["table_hdr"]),
        Paragraph("Value", _styles()["table_hdr"]),
        Paragraph("Unit", _styles()["table_hdr"]),
        Paragraph("Compliance", _styles()["table_hdr"]),
    ]
    rows = [headers]
    for i, row in enumerate(data_rows):
        HexColor("#F5F5F5") if i % 2 == 0 else WHITE_C
        compliance_style = _styles()["compliance_pass"] if row[3] in ("✅", "PASS", "") else _styles()["compliance_fail"]
        rows.append([
            Paragraph(str(row[0]), _styles()["table_cell"]),
            Paragraph(f"<b>{str(row[1])}</b>", _styles()["result"]),
            Paragraph(str(row[2]), _styles()["small"]),
            Paragraph(str(row[3]), compliance_style),
        ])
    t = Table(rows, colWidths=[75*mm, 45*mm, 25*mm, 40*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLACK_C),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#F5F5F5"), WHITE_C]),
        ("GRID", (0, 0), (-1, -1), 0.3, LIGHT_GREY_C),
        ("LINEABOVE", (0, 0), (-1, 0), 2, RED),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, LIGHT_GREY_C),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def _page_footer(canvas, doc):
    """Draw footer on every page."""
    canvas.saveState()
    region = getattr(doc, "_region", "gcc")
    meta = REGION_META.get(region, REGION_META["gcc"])
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(LIGHT_GREY_C)
    footer_text = meta.get("footer_tag", "OpenMEP Engineering Suite")
    canvas.drawString(20*mm, 12*mm, footer_text)
    canvas.drawRightString(190*mm, 12*mm, f"Page {doc.page}")
    canvas.setLineWidth(0.5)
    canvas.setStrokeColor(HexColor("#333333"))
    canvas.line(20*mm, 16*mm, 190*mm, 16*mm)
    canvas.restoreState()


def generate_calculation_pdf(project_info: Dict[str, Any], calc_data: Dict[str, Any]) -> Optional[bytes]:
    """
    Generate a professional PDF calculation report.
    Returns PDF bytes or None on failure.
    """
    if not REPORTLAB_OK:
        return None

    buf = io.BytesIO()
    region = project_info.get("region", "gcc")
    report_type = project_info.get("report_type", "cable_sizing")
    revision = project_info.get("revision", "P01")
    meta = REGION_META.get(region, REGION_META["gcc"])

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=15*mm, bottomMargin=25*mm,
        title=f"OpenMEP — {report_type.replace('_', ' ').title()}",
        author=project_info.get("engineer_name", "OpenMEP"),
        subject=f"{meta['title']} — {project_info.get('project_name', '')}",
    )
    doc._region = region
    st_styles = _styles()
    story = []

    # ── Header ─────────────────────────────────────────────────────────────────
    story.append(_header_table(meta, project_info, report_type, revision))
    story.append(Spacer(1, 6*mm))

    # ── Title bar ──────────────────────────────────────────────────────────────
    calc_title = report_type.replace("_", " ").upper()
    title_data = [[Paragraph(f"CALCULATION SHEET: {calc_title}", _styles()["title"])]]
    title_tbl = Table(title_data, colWidths=[185*mm])
    title_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_GREY_C),
        ("LINEABOVE", (0, 0), (-1, 0), 3, RED),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(title_tbl)
    story.append(Spacer(1, 4*mm))

    # ── Design Basis ───────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#CC0000"), spaceAfter=4))
    story.append(Paragraph("1.0  DESIGN BASIS", st_styles["section"]))
    story.append(HRFlowable(width="100%", thickness=0.2, color=LIGHT_GREY_C, spaceBefore=2, spaceAfter=4))
    standard = calc_data.get("standard", meta["standards"])
    authority = calc_data.get("authority", meta["authorities"])
    story.append(Paragraph(
        f"This calculation has been prepared in accordance with <b>{standard}</b>. "
        f"The applicable authority is <b>{authority}</b>. {meta['disclaimer']}",
        st_styles["body"]
    ))
    story.append(Spacer(1, 4*mm))

    # ── Input Parameters ────────────────────────────────────────────────────────
    story.append(Paragraph("2.0  INPUT PARAMETERS", st_styles["section"]))
    story.append(HRFlowable(width="100%", thickness=0.2, color=LIGHT_GREY_C, spaceBefore=2, spaceAfter=4))

    input_rows = []
    if calc_data.get("load_kw"):
        input_rows.append(["Connected Load", f"{calc_data['load_kw']:.2f}", "kW", ""])
    if calc_data.get("power_factor"):
        input_rows.append(["Power Factor", f"{calc_data['power_factor']:.3f}", "—", ""])
    if calc_data.get("phases"):
        input_rows.append(["Supply Phases", str(calc_data["phases"]), "phase", ""])
    if calc_data.get("supply_voltage_v"):
        input_rows.append(["Supply Voltage", f"{calc_data['supply_voltage_v']:.0f}", "V", ""])
    if calc_data.get("cable_type"):
        input_rows.append(["Cable Type", calc_data["cable_type"], "—", ""])
    if calc_data.get("installation_method"):
        input_rows.append(["Installation Method", calc_data.get("installation_method_description", calc_data["installation_method"]), "—", ""])
    if calc_data.get("cable_length_m"):
        input_rows.append(["Cable Length", f"{calc_data['cable_length_m']:.1f}", "m", ""])
    if calc_data.get("ambient_temp_c"):
        input_rows.append(["Ambient Temperature", f"{calc_data['ambient_temp_c']:.1f}", "°C", ""])
    if calc_data.get("num_grouped"):
        input_rows.append(["Grouped Circuits", f"{calc_data['num_grouped']}", "circuits", ""])

    if input_rows:
        story.append(_result_table(input_rows))
    story.append(Spacer(1, 4*mm))

    # ── Calculation Procedure ───────────────────────────────────────────────────
    story.append(Paragraph("3.0  CALCULATION METHODOLOGY", st_styles["section"]))
    story.append(HRFlowable(width="100%", thickness=0.2, color=LIGHT_GREY_C, spaceBefore=2, spaceAfter=4))

    if report_type == "cable_sizing":
        methodology = [
            "<b>Step 1 — Design Current (Ib):</b> Ib = kW × 1000 / (√3 × V × PF) for 3-phase",
            "<b>Step 2 — Tabulated Rating (It):</b> Select from BS 7671 Table 4D5A (XLPE) or 4D2A (PVC)",
            "<b>Step 3 — Ambient Temp Correction (Ca):</b> From BS 7671 Table 4B1 (XLPE: 90°C conductor)",
            "<b>Step 4 — Grouping Correction (Cg):</b> From BS 7671 Table 4C1",
            "<b>Step 5 — Derated Rating (Iz):</b> Iz = It × Ca × Cg — must satisfy Iz ≥ Ib",
            "<b>Step 6 — Voltage Drop:</b> VD = (mV/A/m × Ib × L) / 1000 — compare to % limit",
            "<b>Step 7 — Earth Conductor:</b> Per BS 7671 Table 54.7 / adiabatic equation",
        ]
    elif report_type == "voltage_drop":
        methodology = [
            "<b>Step 1:</b> Design current Ib calculated from load parameters",
            "<b>Step 2:</b> mV/A/m factor from BS 7671 Appendix 4 for selected cable size",
            "<b>Step 3:</b> VD (mV) = mV/A/m × Ib × cable length (m)",
            "<b>Step 4:</b> VD% = VD (V) / supply voltage × 100",
            "<b>Step 5:</b> Compare to limit (3% lighting / 5% power per BS 7671 Appendix 12)",
        ]
    else:
        methodology = [
            "<b>Calculation performed per applicable regional standards.</b>",
            f"Standard: {meta['standards']}",
        ]

    for step in methodology:
        story.append(Paragraph(f"  {step}", st_styles["body"]))
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 4*mm))

    # ── Results ─────────────────────────────────────────────────────────────────
    story.append(Paragraph("4.0  CALCULATION RESULTS", st_styles["section"]))
    story.append(HRFlowable(width="100%", thickness=0.2, color=LIGHT_GREY_C, spaceBefore=2, spaceAfter=4))

    result_rows = []
    if calc_data.get("design_current_ib_a"):
        result_rows.append(["Design Current (Ib)", f"{calc_data['design_current_ib_a']:.2f}", "A", "✅"])
    if calc_data.get("selected_size_mm2"):
        result_rows.append(["Selected Cable Size", f"{calc_data['selected_size_mm2']}", "mm²", "✅"])
    if calc_data.get("tabulated_rating_it_a"):
        result_rows.append(["Tabulated Rating (It)", f"{calc_data['tabulated_rating_it_a']:.1f}", "A", "✅"])
    if calc_data.get("ca_factor"):
        result_rows.append(["Ambient Temp Factor (Ca)", f"{calc_data['ca_factor']:.3f}", "—", "✅"])
    if calc_data.get("cg_factor"):
        result_rows.append(["Grouping Factor (Cg)", f"{calc_data['cg_factor']:.3f}", "—", "✅"])
    if calc_data.get("derated_rating_iz_a"):
        iz = calc_data["derated_rating_iz_a"]
        ib = calc_data.get("design_current_ib_a", 0)
        status = "✅ PASS" if iz >= ib else "❌ FAIL"
        result_rows.append(["Derated Rating (Iz)", f"{iz:.1f}", "A", status])
    if calc_data.get("voltage_drop_pct") is not None:
        vd = calc_data["voltage_drop_pct"]
        vd_limit = calc_data.get("voltage_drop_limit_pct", 5.0)
        vd_status = "✅ PASS" if vd <= vd_limit else "❌ FAIL"
        result_rows.append(["Voltage Drop", f"{vd:.2f}", "%", vd_status])
    if calc_data.get("voltage_drop_limit_pct"):
        result_rows.append(["VD Limit", f"{calc_data['voltage_drop_limit_pct']:.1f}", "%", ""])
    if calc_data.get("protection_device_a"):
        result_rows.append(["Protection Device", f"{calc_data['protection_device_a']:.0f}", "A MCB/MCCB", "✅"])
    if calc_data.get("earth_conductor_mm2"):
        result_rows.append(["CPC Earth Conductor", f"{calc_data['earth_conductor_mm2']}", "mm²", "✅"])

    if result_rows:
        story.append(_result_table(result_rows))
    story.append(Spacer(1, 4*mm))

    # ── Compliance Summary ─────────────────────────────────────────────────────
    story.append(Paragraph("5.0  COMPLIANCE SUMMARY", st_styles["section"]))
    story.append(HRFlowable(width="100%", thickness=0.2, color=LIGHT_GREY_C, spaceBefore=2, spaceAfter=4))

    overall = calc_data.get("overall_compliant", True)
    status_text = "COMPLIANT ✓" if overall else "NON-COMPLIANT ✗"
    status_color = HexColor("#006622") if overall else HexColor("#CC0000")
    status_bg = HexColor("#E8F5E9") if overall else HexColor("#FFEBEE")

    status_data = [[Paragraph(f"Overall Status: {status_text}", ParagraphStyle(
        "OS", fontName="Helvetica-Bold", fontSize=12,
        textColor=status_color, alignment=TA_CENTER))]]
    status_tbl = Table(status_data, colWidths=[185*mm])
    status_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), status_bg),
        ("LINEABOVE", (0, 0), (-1, 0), 2, status_color),
        ("LINEBELOW", (0, 0), (-1, 0), 2, status_color),
        ("PADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(status_tbl)
    story.append(Spacer(1, 3*mm))

    if calc_data.get("compliance_statements"):
        for stmt in calc_data["compliance_statements"]:
            clean_stmt = stmt.replace("✅", "[PASS]").replace("❌", "[FAIL]").replace("⚠️", "[WARN]")
            style = st_styles["compliance_pass"] if "[PASS]" in clean_stmt else st_styles["compliance_fail"]
            story.append(Paragraph(clean_stmt, style))
            story.append(Spacer(1, 2))

    if calc_data.get("warnings"):
        story.append(Spacer(1, 3*mm))
        story.append(Paragraph("Warnings / Recommendations:", st_styles["section"]))
        for w in calc_data["warnings"]:
            clean = w.replace("⚠️", "").strip()
            story.append(Paragraph(f"  • {clean}", st_styles["body"]))

    story.append(Spacer(1, 4*mm))

    # ── Sign-off block ─────────────────────────────────────────────────────────
    story.append(Paragraph("6.0  ENGINEER'S CERTIFICATION", st_styles["section"]))
    story.append(HRFlowable(width="100%", thickness=0.2, color=LIGHT_GREY_C, spaceBefore=2, spaceAfter=4))
    signoff_data = [
        ["Prepared by", "Checked by", "Approved by"],
        [project_info.get("engineer_name", "__________________"),
         project_info.get("checked_by", "__________________"),
         "__________________"],
        ["Signature: ________________", "Signature: ________________", "Signature: ________________"],
        [f"Date: {project_info.get('date', str(date.today()))}", "Date: ________________", "Date: ________________"],
    ]
    signoff_tbl = Table(signoff_data, colWidths=[60*mm, 60*mm, 65*mm])
    signoff_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK_GREY_C),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE_C),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.3, LIGHT_GREY_C),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
    ]))
    story.append(signoff_tbl)
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        f"<i>This document has been prepared using OpenMEP v0.1.0 (open-source MEP engineering suite). "
        f"All calculations must be independently reviewed by a qualified engineer before use in construction. "
        f"© OpenMEP | MIT License | {meta['footer_tag']}</i>",
        st_styles["small"]
    ))

    # ── Build ──────────────────────────────────────────────────────────────────
    doc.build(story, onFirstPage=_page_footer, onLaterPages=_page_footer)
    buf.seek(0)
    return buf.getvalue()
