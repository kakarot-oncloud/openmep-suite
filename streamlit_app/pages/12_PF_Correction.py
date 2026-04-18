"""Power Factor Correction — OpenMEP"""

import streamlit as st
import sys
import os
import math
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, page_header, result_card, compliance_badge, section_title, format_summary,
    api_post, region_selector,
    TEAL, TEAL_L
)

st.set_page_config(page_title="PF Correction — OpenMEP", page_icon="⚡", layout="wide")
apply_theme_css()

page_header("Power Factor Correction", "Capacitor bank sizing per IEC 60831 to achieve target power factor", "⚡")

with st.sidebar:
    st.markdown(f"<h3 style='color:{TEAL_L}; font-size:0.9rem; text-transform:uppercase; letter-spacing:2px;'>IEC 60831 / EN 60831</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{DARK_GREY}; padding:1rem; border-radius:6px; font-size:0.8rem; color:{WHITE}; line-height:1.8;">
    <b style='color:{TEAL_L}'>PF Targets (min):</b><br>
    DEWA: ≥ 0.90 lagging<br>
    SEC: ≥ 0.90 lagging<br>
    UK DNO: ≥ 0.95<br>
    India CEA: ≥ 0.90<br>
    Australia: ≥ 0.90<br><br>
    <b style='color:{TEAL_L}'>Benefits:</b><br>
    Reduced kVA demand charges<br>
    Lower cable losses<br>
    Better voltage regulation<br><br>
    <b style='color:{TEAL_L}'>Harmonic Note:</b><br>
    With VFDs/UPS present use<br>
    detuned capacitor banks<br>
    (5.67% or 7% reactor).
    </div>
    """, unsafe_allow_html=True)

with st.form("pf_form"):
    section_title("Regional Standards")
    region_code, sub_code = region_selector("pf")
    st.info("Minimum PF requirements and tariff penalties vary by authority. Select sub-authority above for specific targets.")

    section_title("Load Data")
    col1, col2, col3 = st.columns(3)
    with col1:
        active_power_kw = st.number_input("Active Power (kW)", min_value=1.0, max_value=50000.0, value=500.0, step=10.0)
    with col2:
        existing_pf = st.number_input("Existing Power Factor", min_value=0.3, max_value=1.0, value=0.72, step=0.01,
                                       help="Current uncorrected power factor (lagging)")
    with col3:
        target_pf = st.number_input("Target Power Factor", min_value=0.85, max_value=1.0, value=0.95, step=0.01)

    section_title("System Parameters")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        supply_voltage = st.number_input("Supply Voltage (V)", min_value=200, max_value=33000, value=415, step=5)
    with col2:
        phases = st.selectbox("Phases", [3, 1], index=0)
    with col3:
        apply_harmonic_derating = st.checkbox("Harmonics present (VFDs/UPS)?", value=False,
                                               help="Adds detuned reactor recommendation to prevent capacitor damage")
    with col4:
        transformer_kva = st.number_input("Transformer Rating (kVA)", min_value=100.0, max_value=20000.0, value=1000.0, step=100.0)

    submitted = st.form_submit_button("Calculate PF Correction", use_container_width=True)

if submitted:
    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "active_power_kw": active_power_kw,
        "existing_pf": existing_pf,
        "target_pf": target_pf,
        "supply_voltage_v": float(supply_voltage),
        "phases": phases,
        "apply_harmonic_derating": apply_harmonic_derating,
        "transformer_kva": transformer_kva,
    }
    with st.spinner("Calculating capacitor bank size..."):
        result = api_post("/api/electrical/pf-correction", payload)

    if result:
        section_title("PF Correction Results")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Required kVAr", f"{result.get('required_correction_kvar', 0):.1f}", "kVAr")
        with col2:
            result_card("Standard Bank", f"{result.get('standard_bank_kvar', 0):.0f}", "kVAr")
        with col3:
            result_card("Corrected PF", f"{result.get('corrected_pf', 0):.3f}", "lagging")
        with col4:
            corrected_kva = result.get("corrected_apparent_kva", 0)
            existing_kva = result.get("existing_apparent_kva", 0)
            result_card("kVA Reduction", f"{max(0, existing_kva - corrected_kva):.1f}", "kVA")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Before: kVA", f"{result.get('existing_apparent_kva', 0):.1f}", "kVA")
        with col2:
            result_card("After: kVA", f"{result.get('corrected_apparent_kva', 0):.1f}", "kVA")
        with col3:
            result_card("Before: kVAr", f"{result.get('existing_reactive_kvar', 0):.1f}", "kVAr")
        with col4:
            result_card("Current Reduction", f"{result.get('current_reduction_pct', 0):.1f}", "%")

        # Compliance badge
        compliant = result.get("compliant", False)
        compliance_badge(compliant, f"{result.get('standard', '')} | Min PF: {result.get('utility_min_pf', 0):.2f}")

        if result.get("tariff_note"):
            st.info(f"💡 {result['tariff_note']}")

        # Power triangle diagram
        section_title("Power Triangle Visualisation")
        kw = active_power_kw
        kvar_before = result.get("existing_reactive_kvar", kw * math.tan(math.acos(max(0.01, existing_pf))))
        kvar_after_corrected = kw * math.tan(math.acos(max(0.01, result.get("corrected_pf", target_pf))))
        kva_before = result.get("existing_apparent_kva", kw / max(0.01, existing_pf))
        kva_after = result.get("corrected_apparent_kva", kw / max(0.01, target_pf))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0, kw, kw, 0], y=[0, 0, kvar_before, 0],
            fill="toself", fillcolor=f"{TEAL}33", line=dict(color=TEAL, width=2),
            name=f"Before: PF={existing_pf:.2f}, {kva_before:.0f} kVA"))
        fig.add_trace(go.Scatter(x=[0, kw, kw, 0], y=[0, 0, kvar_after_corrected, 0],
            fill="toself", fillcolor="#00AA4433", line=dict(color="#00AA44", width=2),
            name=f"After: PF={result.get('corrected_pf', target_pf):.2f}, {kva_after:.0f} kVA"))
        fig.update_layout(
            paper_bgcolor=DARK_GREY, plot_bgcolor=BLACK,
            font=dict(color=WHITE), xaxis_title="Active Power (kW)",
            yaxis_title="Reactive Power (kVAr)", height=350,
            xaxis=dict(gridcolor="#333"), yaxis=dict(gridcolor="#333"),
            legend=dict(bgcolor=DARK_GREY, bordercolor="#444"),
        )
        st.plotly_chart(fig, use_container_width=True)

        if result.get("apfc_steps"):
            section_title("APFC Panel Suggestion")
            col1, col2, col3 = st.columns(3)
            with col1:
                result_card("APFC Steps", str(result.get("apfc_steps", 0)), "steps")
            with col2:
                result_card("Step Size", f"{result.get('apfc_step_kvar', 0):.0f}", "kVAr")
            with col3:
                result_card("Total APFC", f"{result.get('apfc_panel_kvar', 0):.0f}", "kVAr")

        if result.get("loss_reduction_kw"):
            section_title("Energy Savings")
            col1, col2 = st.columns(2)
            with col1:
                result_card("Loss Reduction", f"{result.get('loss_reduction_kw', 0):.1f}", "kW")
            with col2:
                result_card("Annual Saving", f"{result.get('annual_saving_kwh', 0):,.0f}", "kWh/yr")

        if apply_harmonic_derating:
            st.warning("⚠️ Harmonics detected: Use **detuned capacitor banks** with series reactor (typically 5.67% or 7% detuning) to prevent resonance and capacitor damage. IEC 60831 + EN 61921 apply.")

        if result.get("summary"):
            section_title("Calculation Summary")
            format_summary(result.get("summary", ""))

        # ── Export / Add-to-BOQ ───────────────────────────────────────────────
        section_title("Export")
        import io as _io
        import pandas as pd
        exp1, exp2, exp3 = st.columns(3)

        with exp1:
            try:
                from report_generator import generate_calculation_pdf
                report_meta = {
                    "project_name": st.session_state.get("project_name", "MEP Project"),
                    "region": region_code, "report_type": "pf_correction",
                    "discipline": "electrical", "revision": "P01",
                    "date": str(pd.Timestamp.today().date()),
                }
                pdf_bytes = generate_calculation_pdf(report_meta, result)
                if pdf_bytes:
                    st.download_button("⬇️ PDF Report", data=pdf_bytes,
                        file_name=f"PFCorrection_{pd.Timestamp.today().date()}.pdf",
                        mime="application/pdf", use_container_width=True)
            except Exception:
                st.info("PDF export available after report generator is configured.")

        with exp2:
            rows = [{
                "Parameter": k.replace("_", " ").title(), "Value": v
            } for k, v in result.items() if isinstance(v, (int, float, str)) and not k.startswith("_")]
            try:
                buf = _io.BytesIO()
                pd.DataFrame(rows).to_excel(buf, index=False, sheet_name="PF_Correction")
                buf.seek(0)
                st.download_button("⬇️ Excel Results", data=buf.getvalue(),
                    file_name=f"PFCorrection_{pd.Timestamp.today().date()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            except ImportError:
                st.info("Install openpyxl for Excel export.")

        with exp3:
            if st.button("📋 Add Cap. Bank to BOQ", use_container_width=True):
                boq_item = {
                    "description": f"Capacitor Bank — {result.get('standard_bank_kvar', 0):.0f} kVAr at {active_power_kw:.0f} kW",
                    "required_kvar": result.get("required_correction_kvar", 0),
                    "standard_kvar": result.get("standard_bank_kvar", 0),
                }
                if "boq_items" not in st.session_state:
                    st.session_state.boq_items = []
                st.session_state.boq_items.append(boq_item)
                st.success(f"Capacitor bank ({result.get('standard_bank_kvar',0):.0f} kVAr) added to BOQ session.")
