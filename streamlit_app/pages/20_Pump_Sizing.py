"""Pump Sizing — OpenMEP"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, page_header, result_card, section_title, format_summary,
    api_post, region_selector,
    TEAL, TEAL_L
)

st.set_page_config(page_title="Pump Sizing — OpenMEP", page_icon="⚙️", layout="wide")
apply_theme_css()

page_header("Centrifugal Pump Sizing", "TDH, shaft power, motor selection per CIBSE C / ASHRAE / IS 1011 / AS 2941", "⚙️")

with st.sidebar:
    st.markdown(f"<h3 style='color:{TEAL_L}; font-size:0.9rem; text-transform:uppercase; letter-spacing:2px;'>CIBSE Guide C</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{DARK_GREY}; padding:1rem; border-radius:6px; font-size:0.8rem; color:{WHITE}; line-height:1.8;">
    TDH = Static + Friction + Velocity<br><br>
    Hydraulic power:<br>
    P = ρ × g × Q × TDH / η<br><br>
    Duty + Standby:<br>
    • Always provide standby<br>
    • Sized identically to duty<br>
    • Common discharge manifold<br><br>
    Standard motor sizes:<br>
    0.37 / 0.75 / 1.5 / 2.2 / 3 / 4 /<br>
    5.5 / 7.5 / 11 / 15 / 22 / 30 kW…
    </div>
    """, unsafe_allow_html=True)

section_title("Region & System")
region_code, sub_code = region_selector("pump")

col1, col2 = st.columns(2)
with col1:
    system_type = st.selectbox("System Type", ["cold_water", "hot_water", "chilled_water", "condenser_water", "sewage", "irrigation"],
        format_func=lambda x: x.replace("_", " ").title())
with col2:
    duty_standby = st.checkbox("Duty + Standby Configuration", value=True)

section_title("Flow & Head")
col1, col2, col3 = st.columns(3)
with col1:
    flow_l_s = st.number_input("Design Flow Rate (L/s)", value=5.0, step=0.5)
    pump_eff = st.number_input("Pump Efficiency", value=0.75, step=0.01, format="%.2f")
with col2:
    static_head = st.number_input("Static Head (m)", value=20.0, step=1.0,
        help="Vertical height difference between pump and highest outlet")
    motor_eff = st.number_input("Motor Efficiency", value=0.92, step=0.01, format="%.2f")
with col3:
    friction_loss = st.number_input("Pipe Friction Loss (m)", value=10.0, step=1.0,
        help="Total pressure drop in pipework at design flow")
    safety_factor = st.number_input("Safety Factor", value=1.15, step=0.05, format="%.2f")

velocity_head = st.number_input("Velocity Head (m)", value=0.5, step=0.1, format="%.1f")

if st.button("Size Pump", use_container_width=True):
    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "system_type": system_type,
        "flow_rate_l_s": flow_l_s,
        "static_head_m": static_head,
        "pipe_friction_loss_m": friction_loss,
        "velocity_head_m": velocity_head,
        "pump_efficiency": pump_eff,
        "motor_efficiency": motor_eff,
        "safety_factor": safety_factor,
        "duty_standby": duty_standby,
    }
    with st.spinner("Sizing pump..."):
        result = api_post("/api/plumbing/pump-sizing", payload)

    if result:
        section_title("Pump Sizing Results")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Total Dynamic Head", f"{result.get('total_dynamic_head_m', 0):.1f}", "m")
        with col2:
            result_card("Flow Rate", f"{result.get('flow_rate_m3_h', 0):.1f}", "m³/h")
        with col3:
            result_card("Motor Selected", f"{result.get('selected_motor_kw', 0)}", "kW")
        with col4:
            result_card("No. Pumps", str(result.get("num_pumps", 1)), "pumps")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Hydraulic Power", f"{result.get('hydraulic_power_kw', 0):.2f}", "kW")
        with col2:
            result_card("Shaft Power", f"{result.get('shaft_power_kw', 0):.2f}", "kW")
        with col3:
            result_card("Motor Power", f"{result.get('motor_power_kw', 0):.2f}", "kW")
        with col4:
            result_card("Pump Efficiency", f"{result.get('pump_efficiency', 0)*100:.0f}", "%")

        section_title(f"Standard: {result.get('standard', '')}")
        st.info(f"Configuration: {result.get('pump_set_description', '')}")
        format_summary(result.get("summary", ""))

        section_title("Export")
        exp1, exp2, exp3 = st.columns(3)
        with exp1:
            try:
                from report_generator import generate_calculation_pdf as _gp
                import pandas as _pd
                _m = {"project_name": st.session_state.get("project_name", ""), "region": region_code,
                      "report_type": "pump_sizing", "discipline": "plumbing", "revision": "P01",
                      "date": str(_pd.Timestamp.today().date())}
                _pdf = _gp(_m, result)
                if _pdf:
                    st.download_button("⬇️ PDF Report", data=_pdf,
                        file_name=f"PumpSizing_{system_type}_{_pd.Timestamp.today().date()}.pdf",
                        mime="application/pdf", use_container_width=True)
            except Exception:
                st.info("PDF export: install reportlab.")
        with exp2:
            try:
                import io as _io
                import pandas as _pd
                _buf = _io.BytesIO()
                _pd.DataFrame([{k: v for k, v in result.items() if isinstance(v, (int, float, str))}]).to_excel(
                    _buf, index=False, sheet_name="Pump_Sizing")
                _buf.seek(0)
                st.download_button("⬇️ Excel Results", data=_buf.getvalue(),
                    file_name=f"PumpSizing_{_pd.Timestamp.today().date()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            except ImportError:
                st.info("Install openpyxl.")
        with exp3:
            if st.button("📋 Add Pump to BOQ", use_container_width=True):
                if "boq_items" not in st.session_state:
                    st.session_state.boq_items = []
                st.session_state.boq_items.append({
                    "type": "pump_sizing",
                    "description": f"Pump — {system_type.replace('_',' ').title()} {result.get('selected_motor_kw', 0)} kW, {result.get('flow_rate_m3_h', 0):.1f} m³/h",
                    "value": result.get("selected_motor_kw"),
                })
                st.success(f"Pump added to BOQ ({len(st.session_state.boq_items)} items).")
