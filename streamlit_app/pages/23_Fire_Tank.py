"""Fire Water Tank Sizing — OpenMEP"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, page_header, result_card, section_title, format_summary,
    api_post, region_selector,
    TEAL, TEAL_L
)

st.set_page_config(page_title="Fire Tank — OpenMEP", page_icon="🛢️", layout="wide")
apply_theme_css()

page_header("Fire Water Storage Tank", "Tank capacity sizing per BS EN 12845 / NFPA 22 / NBC Part 4 / AS 2118", "🛢️")

with st.sidebar:
    st.markdown(f"<h3 style='color:{TEAL_L}; font-size:0.9rem; text-transform:uppercase; letter-spacing:2px;'>BS EN 12845 / NFPA 22</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{DARK_GREY}; padding:1rem; border-radius:6px; font-size:0.8rem; color:{WHITE}; line-height:1.8;">
    Duration requirements:<br>
    • Sprinkler LH: 30 min<br>
    • Sprinkler OH1/OH2: 60 min<br>
    • Sprinkler OH3/OH4: 90 min<br>
    • High Hazard: 120 min<br>
    • Wet riser + hose: 45-60 min<br><br>
    Compartmentation:<br>
    • Minimum 2 compartments<br>
    • Each holds 50% of total<br>
    • Cross-connection with valve
    </div>
    """, unsafe_allow_html=True)

section_title("Region & System")
region_code, sub_code = region_selector("ft")

col1, col2 = st.columns(2)
with col1:
    system_type = st.selectbox("System Type", ["sprinkler", "wet_riser", "combined", "foam"],
        format_func=lambda x: x.replace("_", " ").title())
with col2:
    num_compartments = st.number_input("Number of Tank Compartments", value=2, min_value=1, max_value=4, step=1)

section_title("Flow & Duration")
col1, col2, col3 = st.columns(3)
with col1:
    total_flow = st.number_input("Total System Flow (L/min)", value=2000.0, step=100.0)
with col2:
    duration = st.number_input("Fire Duration (minutes)", value=60.0, step=15.0,
        help="See sidebar for duration requirements per hazard class")
with col3:
    hose_allowance = st.number_input("Hose Allowance (L)", value=3000.0, step=500.0,
        help="GCC/BS EN: 3000 L | NFPA: typically 5000 L")

col1, col2 = st.columns(2)
with col1:
    additional_pct = st.number_input("Additional Allowance (%)", value=10.0, step=5.0,
        help="Typically 10% added to calculated volume for contingency")
with col2:
    refill_hr = st.number_input("Tank Refill Time (hours)", value=4.0, step=0.5,
        help="BS EN 12845: tank to refill within 4 hours of end of supply")

if st.button("Size Fire Tank", use_container_width=True):
    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "system_type": system_type,
        "total_flow_l_min": total_flow,
        "supply_duration_min": duration,
        "hose_allowance_l": hose_allowance,
        "additional_allowance_pct": additional_pct,
        "number_of_compartments": num_compartments,
        "refill_time_hr": refill_hr,
    }
    with st.spinner("Sizing fire water tank..."):
        result = api_post("/api/fire/fire-tank", payload)

    if result:
        section_title("Fire Tank Sizing Results")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Total Required", f"{result.get('total_volume_required_m3', 0):.1f}", "m³")
        with col2:
            result_card("Per Compartment", f"{result.get('selected_tank_per_compartment_m3', 0)}", "m³")
        with col3:
            result_card("No. Compartments", str(result.get("number_of_compartments", 0)), "tanks")
        with col4:
            result_card("Total Capacity", f"{result.get('total_tank_capacity_m3', 0)}", "m³")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Base Volume", f"{result.get('base_volume_l', 0)/1000:.1f}", "m³")
        with col2:
            result_card("Hose Allowance", f"{result.get('hose_allowance_l', 0)/1000:.1f}", "m³")
        with col3:
            result_card("Refill Time", f"{result.get('refill_time_hr', 0):.1f}", "hr")
        with col4:
            result_card("Inlet Flow", f"{result.get('inlet_flow_l_min', 0):.0f}", "L/min")

        section_title(f"Standard: {result.get('standard', '')}")
        format_summary(result.get("summary", ""))

        section_title("Export")
        exp1, exp2, exp3 = st.columns(3)
        with exp1:
            try:
                from report_generator import generate_calculation_pdf as _gp
                import pandas as _pd
                _m = {"project_name": st.session_state.get("project_name", ""), "region": region_code,
                      "report_type": "fire_tank", "discipline": "fire", "revision": "P01",
                      "date": str(_pd.Timestamp.today().date())}
                _pdf = _gp(_m, result)
                if _pdf:
                    st.download_button("⬇️ PDF Report", data=_pdf,
                        file_name=f"FireTank_{_pd.Timestamp.today().date()}.pdf",
                        mime="application/pdf", use_container_width=True)
            except Exception:
                st.info("PDF export: install reportlab.")
        with exp2:
            try:
                import io as _io
                import pandas as _pd
                _buf = _io.BytesIO()
                _pd.DataFrame([{k: v for k, v in result.items() if isinstance(v, (int, float, str))}]).to_excel(
                    _buf, index=False, sheet_name="Fire_Tank")
                _buf.seek(0)
                st.download_button("⬇️ Excel Results", data=_buf.getvalue(),
                    file_name=f"FireTank_{_pd.Timestamp.today().date()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            except ImportError:
                st.info("Install openpyxl.")
        with exp3:
            if st.button("📋 Add Tank to BOQ", use_container_width=True):
                if "boq_items" not in st.session_state:
                    st.session_state.boq_items = []
                st.session_state.boq_items.append({
                    "type": "fire_tank",
                    "description": f"Fire Tank — {num_compartments} × {result.get('selected_tank_per_compartment_m3', 0)} m³ = {result.get('total_tank_capacity_m3', 0)} m³ total",
                    "value": result.get("total_tank_capacity_m3"),
                })
                st.success(f"Fire tank added to BOQ ({len(st.session_state.boq_items)} items).")
