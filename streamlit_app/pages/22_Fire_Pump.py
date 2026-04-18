"""Fire Pump Sizing — OpenMEP"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, page_header, result_card, section_title, format_summary,
    api_post, region_selector,
    TEAL, TEAL_L
)

st.set_page_config(page_title="Fire Pump — OpenMEP", page_icon="🚒", layout="wide")
apply_theme_css()

page_header("Fire Pump Sizing", "Fire pump set design per BS EN 12845 / NFPA 20 / NBC Part 4 / AS 2941", "🚒")

with st.sidebar:
    st.markdown(f"<h3 style='color:{TEAL_L}; font-size:0.9rem; text-transform:uppercase; letter-spacing:2px;'>BS EN 12845 / NFPA 20</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{DARK_GREY}; padding:1rem; border-radius:6px; font-size:0.8rem; color:{WHITE}; line-height:1.8;">
    Pump set minimum:<br>
    • 1 Duty + 1 Standby (equal)<br>
    • 1 Jockey pump (leak detection)<br>
    • Diesel backup if >45 kW<br><br>
    GCC / Civil Defence (UAE):<br>
    • Diesel duty + Electric standby<br>
    • Jockey at 110% rated pressure<br>
    • Monthly test runs required<br><br>
    Rated point: 100% flow & head<br>
    Churn: 140% rated head at 0 flow
    </div>
    """, unsafe_allow_html=True)

section_title("Region & System")
region_code, sub_code = region_selector("fp")

col1, col2 = st.columns(2)
with col1:
    system_type = st.selectbox("System Type", ["wet_riser", "combined", "deluge", "foam"],
        format_func=lambda x: x.replace("_", " ").title())
with col2:
    duty_standby = st.checkbox("Duty + Standby + Jockey Configuration", value=True)

section_title("System Flow Demands")
col1, col2, col3 = st.columns(3)
with col1:
    sprinkler_flow = st.number_input("Sprinkler Demand (L/min)", value=2000.0, step=100.0)
with col2:
    hose_reel_flow = st.number_input("Hose Reel Demand (L/min)", value=600.0, step=50.0)
with col3:
    hydrant_flow = st.number_input("Hydrant Allowance (L/min)", value=0.0, step=100.0)

section_title("System Pressure")
col1, col2, col3 = st.columns(3)
with col1:
    static_pres = st.number_input("Pressure Required at Outlet (bar)", value=6.5, step=0.5,
        help="GCC: typically 6.5 bar | UK: 5.0 bar | Sprinkler head: 1.0-2.5 bar")
with col2:
    friction_pres = st.number_input("Friction Loss (bar)", value=1.5, step=0.25)
with col3:
    elevation_pres = st.number_input("Elevation Loss (bar)", value=2.0, step=0.5,
        help="0.1 bar per metre rise (0.981 bar/10m)")

section_title("Pump Efficiencies")
col1, col2 = st.columns(2)
with col1:
    pump_eff = st.number_input("Pump Efficiency", value=0.72, step=0.01, format="%.2f")
with col2:
    motor_eff = st.number_input("Motor Efficiency", value=0.90, step=0.01, format="%.2f")

if st.button("Size Fire Pump Set", use_container_width=True):
    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "system_type": system_type,
        "sprinkler_demand_l_min": sprinkler_flow,
        "hose_reel_demand_l_min": hose_reel_flow,
        "hydrant_demand_l_min": hydrant_flow,
        "static_pressure_required_bar": static_pres,
        "friction_loss_bar": friction_pres,
        "elevation_loss_bar": elevation_pres,
        "pump_efficiency": pump_eff,
        "motor_efficiency": motor_eff,
        "duty_standby_jockey": duty_standby,
    }
    with st.spinner("Sizing fire pump set..."):
        result = api_post("/api/fire/fire-pump", payload)

    if result:
        section_title("Fire Pump Sizing Results")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Total Flow", f"{result.get('total_flow_l_min', 0):.0f}", "L/min")
        with col2:
            result_card("Total Flow", f"{result.get('total_flow_m3_h', 0):.1f}", "m³/h")
        with col3:
            result_card("TDH", f"{result.get('total_dynamic_head_m', 0):.1f}", "m")
        with col4:
            result_card("System Pressure", f"{result.get('total_dynamic_head_bar', 0):.2f}", "bar")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Hydraulic Power", f"{result.get('hydraulic_power_kw', 0):.1f}", "kW")
        with col2:
            result_card("Duty Motor", f"{result.get('selected_motor_kw', 0)}", "kW")
        with col3:
            result_card("Jockey Flow", f"{result.get('jockey_pump_flow_l_min', 0):.0f}", "L/min")
        with col4:
            result_card("Jockey Motor", f"{result.get('jockey_motor_kw', 0)}", "kW")

        section_title("Pump Set Configuration")
        st.info(f"**{result.get('pump_set_description', '')}**")
        section_title(f"Standard: {result.get('standard', '')}")
        format_summary(result.get("summary", ""))

        section_title("Export")
        exp1, exp2, exp3 = st.columns(3)
        with exp1:
            try:
                from report_generator import generate_calculation_pdf as _gp
                import pandas as _pd
                _m = {"project_name": st.session_state.get("project_name", ""), "region": region_code,
                      "report_type": "fire_pump", "discipline": "fire", "revision": "P01",
                      "date": str(_pd.Timestamp.today().date())}
                _pdf = _gp(_m, result)
                if _pdf:
                    st.download_button("⬇️ PDF Report", data=_pdf,
                        file_name=f"FirePump_{_pd.Timestamp.today().date()}.pdf",
                        mime="application/pdf", use_container_width=True)
            except Exception:
                st.info("PDF export: install reportlab.")
        with exp2:
            try:
                import io as _io
                import pandas as _pd
                _buf = _io.BytesIO()
                _pd.DataFrame([{k: v for k, v in result.items() if isinstance(v, (int, float, str))}]).to_excel(
                    _buf, index=False, sheet_name="Fire_Pump")
                _buf.seek(0)
                st.download_button("⬇️ Excel Results", data=_buf.getvalue(),
                    file_name=f"FirePump_{_pd.Timestamp.today().date()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            except ImportError:
                st.info("Install openpyxl.")
        with exp3:
            if st.button("📋 Add Pump to BOQ", use_container_width=True):
                if "boq_items" not in st.session_state:
                    st.session_state.boq_items = []
                st.session_state.boq_items.append({
                    "type": "fire_pump",
                    "description": f"Fire Pump Set — {result.get('selected_motor_kw', 0)} kW duty, {result.get('total_flow_l_min', 0):.0f} L/min",
                    "value": result.get("selected_motor_kw"),
                })
                st.success(f"Fire pump added to BOQ ({len(st.session_state.boq_items)} items).")
