"""Standpipe / Wet Riser System — OpenMEP"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, LIGHT_GREY,
    page_header, result_card, section_title, format_summary,
    api_post, region_selector,
    TEAL, TEAL_L
)

st.set_page_config(page_title="Standpipe / Wet Riser — OpenMEP", page_icon="🔴", layout="wide")
apply_theme_css()

page_header("Standpipe / Wet Riser Design", "Multi-storey wet riser per NFPA 14 / BS 5306 / NBC Part 4 / AS 2118.1", "🔴")

with st.sidebar:
    st.markdown(f"<h3 style='color:{TEAL_L}; font-size:0.9rem; text-transform:uppercase; letter-spacing:2px;'>NFPA 14 / BS 5306</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{DARK_GREY}; padding:1rem; border-radius:6px; font-size:0.8rem; color:{WHITE}; line-height:1.8;">
    System Classes (NFPA 14):<br>
    • Class I: 2½" hose valves<br>
    • Class II: 1½" hose cabinets<br>
    • Class III: Both Class I + II<br><br>
    GCC / Civil Defence:<br>
    • Wet riser in all buildings >10m<br>
    • Landing valve: 65mm, 6.5 bar<br>
    • Each landing / every 30m<br>
    • 2-storey travel limit<br><br>
    DN range: DN65 – DN200<br>
    Typical: DN100 (2-pipe) / DN150
    </div>
    """, unsafe_allow_html=True)

section_title("Region & Building")
region_code, sub_code = region_selector("sp")

col1, col2, col3 = st.columns(3)
with col1:
    system_class = st.selectbox("System Class", ["III", "I", "II"],
        format_func=lambda x: {"I": "Class I (Firefighter Use)", "II": "Class II (Occupant Use)", "III": "Class III (Combined)"}[x])
with col2:
    building_height = st.number_input("Building Height (m)", value=50.0, step=5.0)
with col3:
    num_floors = st.number_input("Number of Floors", value=15, step=1)

col1, col2 = st.columns(2)
with col1:
    floor_height = st.number_input("Floor-to-Floor Height (m)", value=3.5, step=0.1)
    hose_spacing = st.number_input("Hose Station Spacing (m)", value=30.0, step=5.0,
        help="GCC: 30m | BS 5306: 30m | NFPA 14: maximum 60m")
with col2:
    pipe_material = st.selectbox("Riser Pipe Material",
        ["steel_galvanised", "steel_black", "stainless_316", "ductile_iron"])
    num_operating = st.number_input("Operating Standpipes Simultaneously", value=2, min_value=1, max_value=4, step=1)

section_title("Pressure & Flow")
col1, col2, col3 = st.columns(3)
with col1:
    outlet_pressure = st.number_input("Pressure at Outlet (bar)", value=6.5, step=0.5,
        help="UAE Civil Defence: 6.5 bar minimum | NFPA 14: 6.9 bar (100 psi) | BS 5306: 4.5 bar")
with col2:
    flow_per_standpipe = st.number_input("Flow per Standpipe (L/min)", value=950.0, step=50.0,
        help="NFPA 14 Class III: 950 L/min per standpipe | BS 5306: 750-1500 L/min")
with col3:
    st.markdown(f"<div style='color:{LIGHT_GREY}; font-size:0.8rem; margin-top:2rem;'>Total flow: {flow_per_standpipe * num_operating:.0f} L/min</div>", unsafe_allow_html=True)

if st.button("Design Standpipe System", use_container_width=True):
    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "system_class": system_class,
        "building_height_m": building_height,
        "num_floors": num_floors,
        "floor_height_m": floor_height,
        "hose_connection_spacing_m": hose_spacing,
        "pressure_at_outlet_bar": outlet_pressure,
        "flow_per_standpipe_l_min": flow_per_standpipe,
        "num_operating_standpipes": num_operating,
        "pipe_material": pipe_material,
    }
    with st.spinner("Designing standpipe system..."):
        result = api_post("/api/fire/standpipe", payload)

    if result:
        section_title("Standpipe System Results")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Riser DN", f"DN{result.get('selected_dn', 0)}", pipe_material.replace("_", " ").title())
        with col2:
            result_card("Total Flow", f"{result.get('total_flow_l_min', 0):.0f}", "L/min")
        with col3:
            result_card("System Pressure", f"{result.get('total_pressure_required_bar', 0):.1f}", "bar")
        with col4:
            result_card("Hose Stations", str(result.get("num_hose_stations", 0)), "stations")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Elevation Loss", f"{result.get('elevation_head_bar', 0):.2f}", "bar")
        with col2:
            result_card("Friction Loss", f"{result.get('friction_loss_bar', 0):.2f}", "bar")
        with col3:
            result_card("Total Flow m³/h", f"{result.get('total_flow_m3_h', 0):.1f}", "m³/h")
        with col4:
            result_card("Riser Diameter", f"{result.get('riser_main_diameter_mm', 0):.0f}", "mm calc.")

        section_title(f"Standard: {result.get('standard', '')}")
        format_summary(result.get("summary", ""))

        section_title("Export")
        exp1, exp2, exp3 = st.columns(3)
        with exp1:
            try:
                from report_generator import generate_calculation_pdf as _gp
                import pandas as _pd
                _m = {"project_name": st.session_state.get("project_name", ""), "region": region_code,
                      "report_type": "standpipe", "discipline": "fire", "revision": "P01",
                      "date": str(_pd.Timestamp.today().date())}
                _pdf = _gp(_m, result)
                if _pdf:
                    st.download_button("⬇️ PDF Report", data=_pdf,
                        file_name=f"Standpipe_Riser_{_pd.Timestamp.today().date()}.pdf",
                        mime="application/pdf", use_container_width=True)
            except Exception:
                st.info("PDF export: install reportlab.")
        with exp2:
            try:
                import io as _io
                import pandas as _pd
                _buf = _io.BytesIO()
                _pd.DataFrame([{k: v for k, v in result.items() if isinstance(v, (int, float, str))}]).to_excel(
                    _buf, index=False, sheet_name="Standpipe")
                _buf.seek(0)
                st.download_button("⬇️ Excel Results", data=_buf.getvalue(),
                    file_name=f"Standpipe_{_pd.Timestamp.today().date()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            except ImportError:
                st.info("Install openpyxl.")
        with exp3:
            if st.button("📋 Add to BOQ", use_container_width=True):
                if "boq_items" not in st.session_state:
                    st.session_state.boq_items = []
                st.session_state.boq_items.append({
                    "type": "standpipe",
                    "description": f"Wet Riser — DN{result.get('selected_dn', 0)} Class {system_class}, {result.get('total_flow_l_min', 0):.0f} L/min",
                    "value": result.get("selected_dn"),
                })
                st.success(f"Standpipe riser added to BOQ ({len(st.session_state.boq_items)} items).")
