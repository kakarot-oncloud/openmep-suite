"""HVAC Heating Load — OpenMEP"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, page_header, result_card, section_title, format_summary,
    api_post, region_selector,
    TEAL, TEAL_L
)

st.set_page_config(page_title="Heating Load — OpenMEP", page_icon="🔥", layout="wide")
apply_theme_css()

page_header("HVAC Heating Load", "Space heating design per EN 12831:2017 / CIBSE Guide A / ASHRAE / NBC", "🔥")

with st.sidebar:
    st.markdown(f"<h3 style='color:{TEAL_L}; font-size:0.9rem; text-transform:uppercase; letter-spacing:2px;'>EN 12831 / CIBSE</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{DARK_GREY}; padding:1rem; border-radius:6px; font-size:0.8rem; color:{WHITE}; line-height:1.8;">
    Standards:<br>
    • GCC: ASHRAE 90.1 / ADM<br>
    • Europe: EN 12831:2017 / CIBSE A<br>
    • India: NBC 2016 Part 8 / IS SP7<br>
    • Australia: NCC 2022 Section J<br><br>
    Fabric losses (U-values × ΔT)<br>
    + Infiltration losses<br>
    × Safety factor
    </div>
    """, unsafe_allow_html=True)

section_title("Region & Project")
region_code, sub_code = region_selector("hl")

col1, col2 = st.columns(2)
with col1:
    zone_name = st.text_input("Zone Name", value="Zone 1")
    zone_type = st.selectbox("Zone Type", ["office", "retail", "residential", "hotel", "industrial", "warehouse", "corridor"])
with col2:
    floor_area_m2 = st.number_input("Floor Area (m²)", value=200.0, step=10.0)
    height_m = st.number_input("Zone Height (m)", value=3.0, step=0.1)

section_title("Design Temperatures")
col1, col2 = st.columns(2)
with col1:
    outdoor_temp = st.number_input("Outdoor Design Temp (°C)", value=-5.0, step=1.0,
        help="GCC: 5°C min | UK: -5°C | India: 5°C | Australia: 0°C")
with col2:
    indoor_temp = st.number_input("Indoor Design Temp (°C)", value=21.0, step=0.5)

section_title("Building Envelope")
col1, col2, col3 = st.columns(3)
with col1:
    wall_area = st.number_input("External Wall Area (m²)", value=120.0, step=5.0)
    wall_u = st.number_input("Wall U-value (W/m²K)", value=0.30, step=0.01, format="%.2f")
with col2:
    window_area = st.number_input("Window/Glazing Area (m²)", value=30.0, step=2.0)
    window_u = st.number_input("Window U-value (W/m²K)", value=1.4, step=0.1, format="%.1f")
with col3:
    roof_area = st.number_input("Roof Area (m²)", value=floor_area_m2, step=10.0)
    roof_u = st.number_input("Roof U-value (W/m²K)", value=0.20, step=0.01, format="%.2f")

col1, col2 = st.columns(2)
with col1:
    floor_uninsulated = st.number_input("Uninsulated Floor Area (m²)", value=0.0, step=5.0)
    floor_u = st.number_input("Floor U-value (W/m²K)", value=0.25, step=0.01, format="%.2f")
with col2:
    infiltration_ach = st.number_input("Infiltration Rate (ACH)", value=0.5, step=0.1, format="%.1f")
    safety_factor = st.number_input("Safety Factor", value=1.15, step=0.05, format="%.2f")

if st.button("Calculate Heating Load", use_container_width=True):
    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "zone_name": zone_name,
        "zone_type": zone_type,
        "floor_area_m2": floor_area_m2,
        "height_m": height_m,
        "wall_area_m2": wall_area,
        "wall_u_value": wall_u,
        "roof_area_m2": roof_area,
        "roof_u_value": roof_u,
        "window_area_m2": window_area,
        "window_u_value": window_u,
        "floor_area_m2_uninsulated": floor_uninsulated,
        "floor_u_value": floor_u,
        "infiltration_ach": infiltration_ach,
        "outdoor_design_temp_c": outdoor_temp,
        "indoor_design_temp_c": indoor_temp,
        "safety_factor": safety_factor,
    }
    with st.spinner("Calculating heating load..."):
        result = api_post("/api/mechanical/heating-load", payload)

    if result:
        section_title("Heating Load Results")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Total Heating Load", f"{result.get('total_heat_loss_kw', 0):.2f}", "kW")
        with col2:
            result_card("W per m²", f"{result.get('heat_load_w_per_m2', 0):.0f}", "W/m²")
        with col3:
            result_card("Fabric Loss", f"{result.get('fabric_heat_loss_w', 0)/1000:.2f}", "kW")
        with col4:
            result_card("Infiltration Loss", f"{result.get('infiltration_heat_loss_w', 0)/1000:.2f}", "kW")

        col1, col2, col3 = st.columns(3)
        with col1:
            result_card("Delta T", f"{result.get('delta_t_k', 0):.1f}", "K")
        with col2:
            result_card("Outdoor Design", f"{outdoor_temp:.1f}", "°C")
        with col3:
            result_card("Safety Factor", f"{result.get('safety_factor', 1.0):.2f}", "×")

        section_title(f"Standard: {result.get('standard', '')}")
        format_summary(result.get("summary", ""))

        section_title("Export")
        exp1, exp2, exp3 = st.columns(3)
        with exp1:
            try:
                from report_generator import generate_calculation_pdf as _gp
                import pandas as _pd
                _m = {"project_name": st.session_state.get("project_name", "MEP Project"),
                      "region": region_code, "report_type": "heating_load",
                      "discipline": "hvac", "revision": "P01",
                      "date": str(_pd.Timestamp.today().date())}
                _pdf = _gp(_m, result)
                if _pdf:
                    st.download_button("⬇️ PDF Report", data=_pdf,
                        file_name=f"HeatingLoad_{zone_name.replace(' ','_')}_{_pd.Timestamp.today().date()}.pdf",
                        mime="application/pdf", use_container_width=True)
            except Exception:
                st.info("PDF export: install reportlab.")
        with exp2:
            try:
                import io as _io
                import pandas as _pd
                _rows = [{k: v for k, v in result.items() if isinstance(v, (int, float, str))}]
                _buf = _io.BytesIO()
                _pd.DataFrame(_rows).to_excel(_buf, index=False, sheet_name="Heating_Load")
                _buf.seek(0)
                st.download_button("⬇️ Excel Results", data=_buf.getvalue(),
                    file_name=f"HeatingLoad_{_pd.Timestamp.today().date()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            except ImportError:
                st.info("Install openpyxl.")
        with exp3:
            if st.button("📋 Add Heating to BOQ", use_container_width=True):
                if "boq_items" not in st.session_state:
                    st.session_state.boq_items = []
                st.session_state.boq_items.append({
                    "type": "heating_load",
                    "description": f"Heating Load — {zone_name}: {result.get('total_heat_loss_kw', 0):.1f} kW",
                    "value": result.get("total_heat_loss_kw"),
                })
                st.success(f"Heating load added to BOQ ({len(st.session_state.boq_items)} items).")
