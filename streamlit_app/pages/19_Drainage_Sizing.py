"""Drainage Sizing — OpenMEP"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, page_header, result_card, compliance_badge, section_title, format_summary,
    api_post, region_selector,
    TEAL, TEAL_L
)

st.set_page_config(page_title="Drainage Sizing — OpenMEP", page_icon="🚿", layout="wide")
apply_theme_css()

page_header("Drainage Pipe Sizing", "Sanitary & rainwater drainage per BS EN 12056 / IS 1742 / AS/NZS 3500.2", "🚿")

with st.sidebar:
    st.markdown(f"<h3 style='color:{TEAL_L}; font-size:0.9rem; text-transform:uppercase; letter-spacing:2px;'>BS EN 12056 / AS 3500</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{DARK_GREY}; padding:1rem; border-radius:6px; font-size:0.8rem; color:{WHITE}; line-height:1.8;">
    Fixture discharge units (DU):<br>
    • WC: 2 DU | Basin: 0.5 DU<br>
    • Shower: 0.6 DU | Bath: 0.8 DU<br>
    • Kitchen sink: 0.8 DU<br>
    • Urinal: 0.5 DU<br>
    • Floor drain: 1.0 DU<br><br>
    Self-cleaning velocity: ≥ 0.75 m/s
    </div>
    """, unsafe_allow_html=True)

section_title("Region & System")
region_code, sub_code = region_selector("drain")

col1, col2, col3 = st.columns(3)
with col1:
    system_type = st.selectbox("System Type", ["sanitary", "rainwater", "combined"],
        format_func=lambda x: {"sanitary": "Sanitary (Foul Water)", "rainwater": "Rainwater", "combined": "Combined"}[x])
with col2:
    pipe_material = st.selectbox("Pipe Material", ["uPVC", "cast_iron", "HDPE", "GRP", "copper"])
with col3:
    gradient = st.number_input("Pipe Gradient (%)", value=1.0, min_value=0.5, max_value=5.0, step=0.25)

section_title("Flow Estimation")
col1, col2 = st.columns(2)
with col1:
    if system_type in ("sanitary", "combined"):
        discharge_units = st.number_input("Total Discharge Units (DU)", value=50.0, step=5.0,
            help="Sum of all fixture DU values connected to this pipe section")
        simultaneous = st.number_input("Simultaneous Use Factor", value=0.7, step=0.05, format="%.2f")
    else:
        discharge_units = 0.0
        simultaneous = 1.0

with col2:
    if system_type in ("rainwater", "combined"):
        roof_area = st.number_input("Roof/Catchment Area (m²)", value=500.0, step=50.0)
        rainfall = st.number_input("Rainfall Intensity (mm/hr)", value=100.0, step=10.0,
            help="GCC: 80-120 mm/hr | UK: 75 mm/hr | India: 100-200 mm/hr | AU: 75-200 mm/hr")
    else:
        roof_area = 0.0
        rainfall = 0.0

if st.button("Size Drainage Pipe", use_container_width=True):
    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "system_type": system_type,
        "discharge_units": discharge_units,
        "roof_area_m2": roof_area,
        "rainfall_intensity_mm_hr": rainfall,
        "gradient_percent": gradient,
        "pipe_material": pipe_material,
        "simultaneous_use_factor": simultaneous,
    }
    with st.spinner("Sizing drainage pipe..."):
        result = api_post("/api/plumbing/drainage-sizing", payload)

    if result:
        section_title("Drainage Results")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Selected DN", f"DN{result.get('selected_dn', 0)}", pipe_material)
        with col2:
            result_card("Design Flow", f"{result.get('design_flow_l_s', 0):.2f}", "L/s")
        with col3:
            result_card("Pipe Capacity", f"{result.get('pipe_capacity_l_s', 0):.2f}", "L/s")
        with col4:
            result_card("Velocity", f"{result.get('pipe_velocity_m_s', 0):.2f}", "m/s")

        compliant = result.get("compliant", False)
        cleaning = result.get("self_cleaning_velocity", False)
        compliance_badge(compliant, f"Self-cleaning: {'✓ Yes' if cleaning else '✗ Increase gradient'}")

        section_title(f"Standard: {result.get('standard', '')}")
        format_summary(result.get("summary", ""))

        section_title("Export")
        exp1, exp2, exp3 = st.columns(3)
        with exp1:
            try:
                from report_generator import generate_calculation_pdf as _gp
                import pandas as _pd
                _m = {"project_name": st.session_state.get("project_name", ""), "region": region_code,
                      "report_type": "drainage_sizing", "discipline": "plumbing", "revision": "P01",
                      "date": str(_pd.Timestamp.today().date())}
                _pdf = _gp(_m, result)
                if _pdf:
                    st.download_button("⬇️ PDF Report", data=_pdf,
                        file_name=f"DrainageSizing_{_pd.Timestamp.today().date()}.pdf",
                        mime="application/pdf", use_container_width=True)
            except Exception:
                st.info("PDF export: install reportlab.")
        with exp2:
            try:
                import io as _io
                import pandas as _pd
                _buf = _io.BytesIO()
                _pd.DataFrame([{k: v for k, v in result.items() if isinstance(v, (int, float, str))}]).to_excel(
                    _buf, index=False, sheet_name="Drainage")
                _buf.seek(0)
                st.download_button("⬇️ Excel Results", data=_buf.getvalue(),
                    file_name=f"DrainageSizing_{_pd.Timestamp.today().date()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            except ImportError:
                st.info("Install openpyxl.")
        with exp3:
            if st.button("📋 Add Drainage to BOQ", use_container_width=True):
                if "boq_items" not in st.session_state:
                    st.session_state.boq_items = []
                st.session_state.boq_items.append({
                    "type": "drainage_sizing",
                    "description": f"Drainage — DN{result.get('selected_dn', 0)} {pipe_material} at {gradient}% gradient",
                    "value": result.get("selected_dn"),
                })
                st.success(f"Drainage added to BOQ ({len(st.session_state.boq_items)} items).")
