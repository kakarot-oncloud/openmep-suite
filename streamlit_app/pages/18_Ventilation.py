"""Ventilation Design — OpenMEP"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, page_header, result_card, section_title, format_summary,
    api_post, region_selector,
    TEAL, TEAL_L
)

st.set_page_config(page_title="Ventilation — OpenMEP", page_icon="💨", layout="wide")
apply_theme_css()

page_header("Ventilation Design", "Fresh air & supply air per ASHRAE 62.1 / CIBSE B2 / BS EN 15251 / AS 1668.2", "💨")

with st.sidebar:
    st.markdown(f"<h3 style='color:{TEAL_L}; font-size:0.9rem; text-transform:uppercase; letter-spacing:2px;'>Standards</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{DARK_GREY}; padding:1rem; border-radius:6px; font-size:0.8rem; color:{WHITE}; line-height:1.8;">
    • GCC: ASHRAE 62.1 / DEWA<br>
    • UK/EU: CIBSE Guide B2 / EN 16798<br>
    • India: NBC 2016 / IS 3103<br>
    • AU: AS 1668.2 / NCC 2022<br><br>
    Fresh air by:<br>
    • Occupancy (L/s·person)<br>
    • ACH (air changes/hr)<br>
    • Area (L/s·m²)
    </div>
    """, unsafe_allow_html=True)

section_title("Region & Zone")
region_code, sub_code = region_selector("vent")

col1, col2 = st.columns(2)
with col1:
    zone_name = st.text_input("Zone Name", value="Open Plan Office")
    zone_type = st.selectbox("Zone Type", ["office", "meeting_room", "retail", "restaurant", "gym", "lobby", "toilet", "car_park", "server_room"])
with col2:
    floor_area = st.number_input("Floor Area (m²)", value=250.0, step=10.0)
    height_m = st.number_input("Floor-to-Ceiling Height (m)", value=3.0, step=0.1)

section_title("Fresh Air Method")
col1, col2 = st.columns(2)
with col1:
    method = st.selectbox("Fresh Air Sizing Method", ["occupancy", "ach", "area"],
        format_func=lambda x: {"occupancy": "Occupancy-based (L/s·person)", "ach": "ACH Method (air changes/hr)", "area": "Area-based (L/s·m²)"}[x])
with col2:
    occupancy = st.number_input("Number of Occupants", value=25, step=1)

col1, col2, col3 = st.columns(3)
with col1:
    fa_person = st.number_input("Fresh Air (L/s·person)", value=10.0, step=0.5,
        help="ASHRAE 62.1: 10 L/s·person office | BS EN 16798: 10 L/s·person Cat II")
with col2:
    fa_ach = st.number_input("Fresh Air ACH", value=6.0, step=0.5,
        help="Office: 6 ACH | Toilet: 10 ACH | Car Park: 6 ACH | Server Room: 20+ ACH")
with col3:
    fa_m2 = st.number_input("Fresh Air (L/s·m²)", value=1.5, step=0.1,
        help="NCC 2022: 1.5 L/s·m² | CIBSE: 1.3-2.5 L/s·m² typical")

section_title("Supply Air Temperature")
col1, col2, col3 = st.columns(3)
with col1:
    supply_temp = st.number_input("Supply Air Temp (°C)", value=18.0, step=0.5)
with col2:
    room_temp = st.number_input("Room Design Temp (°C)", value=22.0, step=0.5)
with col3:
    cooling_kw = st.number_input("Cooling Load (kW)", value=15.0, step=1.0)

if st.button("Calculate Ventilation", use_container_width=True):
    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "zone_name": zone_name,
        "zone_type": zone_type,
        "floor_area_m2": floor_area,
        "height_m": height_m,
        "occupancy": occupancy,
        "fresh_air_method": method,
        "fresh_air_l_s_person": fa_person,
        "fresh_air_ach": fa_ach,
        "fresh_air_l_s_m2": fa_m2,
        "supply_air_temp_c": supply_temp,
        "room_temp_c": room_temp,
        "cooling_load_kw": cooling_kw,
    }
    with st.spinner("Calculating ventilation..."):
        result = api_post("/api/mechanical/ventilation", payload)

    if result:
        section_title("Ventilation Results")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Fresh Air", f"{result.get('fresh_air_m3_h', 0):.0f}", "m³/h")
        with col2:
            result_card("Fresh Air L/s", f"{result.get('fresh_air_l_s', 0):.0f}", "L/s")
        with col3:
            result_card("ACH Achieved", f"{result.get('ach_achieved', 0):.1f}", "ACH")
        with col4:
            result_card("Total Supply Air", f"{result.get('total_supply_air_m3_h', 0):.0f}", "m³/h")

        col1, col2, col3 = st.columns(3)
        with col1:
            result_card("L/s per Person", f"{result.get('fresh_air_l_s_person', 0):.1f}", "L/s·person")
        with col2:
            result_card("L/s per m²", f"{result.get('fresh_air_l_s_m2', 0):.2f}", "L/s·m²")
        with col3:
            result_card("Supply ΔT", f"{result.get('supply_air_delta_t_k', 0):.1f}", "K")

        section_title(f"Standard: {result.get('standard', '')}")
        st.info(f"Method: {result.get('method_description', '')}")
        format_summary(result.get("summary", ""))

        section_title("Export")
        exp1, exp2, exp3 = st.columns(3)
        with exp1:
            try:
                from report_generator import generate_calculation_pdf as _gp
                import pandas as _pd
                _m = {"project_name": st.session_state.get("project_name", ""), "region": region_code,
                      "report_type": "ventilation", "discipline": "hvac", "revision": "P01",
                      "date": str(_pd.Timestamp.today().date())}
                _pdf = _gp(_m, result)
                if _pdf:
                    st.download_button("⬇️ PDF Report", data=_pdf,
                        file_name=f"Ventilation_{zone_name.replace(' ','_')}_{_pd.Timestamp.today().date()}.pdf",
                        mime="application/pdf", use_container_width=True)
            except Exception:
                st.info("PDF export: install reportlab.")
        with exp2:
            try:
                import io as _io
                import pandas as _pd
                _buf = _io.BytesIO()
                _pd.DataFrame([{k: v for k, v in result.items() if isinstance(v, (int, float, str))}]).to_excel(
                    _buf, index=False, sheet_name="Ventilation")
                _buf.seek(0)
                st.download_button("⬇️ Excel Results", data=_buf.getvalue(),
                    file_name=f"Ventilation_{_pd.Timestamp.today().date()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            except ImportError:
                st.info("Install openpyxl.")
        with exp3:
            if st.button("📋 Add to BOQ", use_container_width=True):
                if "boq_items" not in st.session_state:
                    st.session_state.boq_items = []
                st.session_state.boq_items.append({
                    "type": "ventilation",
                    "description": f"Ventilation — {zone_name}: {result.get('total_supply_air_m3_h', 0):.0f} m³/h",
                    "value": result.get("total_supply_air_m3_h"),
                })
                st.success(f"Ventilation added to BOQ ({len(st.session_state.boq_items)} items).")
