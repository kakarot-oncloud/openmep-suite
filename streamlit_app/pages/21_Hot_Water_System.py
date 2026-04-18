"""Hot Water System Design — OpenMEP"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, page_header, result_card, compliance_badge, section_title, format_summary,
    api_post, region_selector,
    TEAL, TEAL_L
)

st.set_page_config(page_title="Hot Water System — OpenMEP", page_icon="🌡️", layout="wide")
apply_theme_css()

page_header("Hot Water System Design", "Storage heater & tank sizing per CIBSE W / BS EN 806 / AS/NZS 3500.4 / IS 2065", "🌡️")

with st.sidebar:
    st.markdown(f"<h3 style='color:{TEAL_L}; font-size:0.9rem; text-transform:uppercase; letter-spacing:2px;'>CIBSE Guide W</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{DARK_GREY}; padding:1rem; border-radius:6px; font-size:0.8rem; color:{WHITE}; line-height:1.8;">
    Legionella Control (L8):<br>
    • Store at ≥ 60°C<br>
    • Deliver at ≥ 55°C<br>
    • Pasteurise at 70°C (1 min)<br>
    • Cold: store at ≤ 20°C<br><br>
    Typical allowances:<br>
    • Hotel: 90-150 L/person/day<br>
    • Office: 15-25 L/person/day<br>
    • Hospital: 180-250 L/bed/day<br>
    • Residential: 50-80 L/person/day
    </div>
    """, unsafe_allow_html=True)

section_title("Region & System")
region_code, sub_code = region_selector("hw")

col1, col2 = st.columns(2)
with col1:
    system_type = st.selectbox("System Type", ["domestic", "solar_assisted", "heat_pump", "centralized"],
        format_func=lambda x: {"domestic": "Electric/Gas Storage", "solar_assisted": "Solar Assisted DHW",
                               "heat_pump": "Heat Pump DHW", "centralized": "Central Plant DHW"}[x])
with col2:
    legionella = st.checkbox("Legionella Pasteurisation Control (L8/L8HS)", value=True)

section_title("Demand Estimation")
col1, col2, col3 = st.columns(3)
with col1:
    occupants = st.number_input("Number of Occupants / Beds / Covers", value=50, step=5)
with col2:
    daily_allowance = st.number_input("Hot Water Allowance (L/person/day)", value=60.0, step=5.0,
        help="Hotel: 100-150 | Residential: 50-80 | Office: 20-30 | Hospital: 200-250")
with col3:
    recovery_hr = st.number_input("Recovery Time (hours)", value=4.0, step=0.5)

section_title("Temperature Settings")
col1, col2, col3 = st.columns(3)
with col1:
    inlet_temp = st.number_input("Cold Water Inlet Temp (°C)", value=15.0, step=1.0,
        help="GCC: 25-35°C | UK: 10-15°C | India: 18-25°C | AU: 15-20°C")
with col2:
    storage_temp = st.number_input("Storage Temperature (°C)", value=60.0, step=1.0,
        help="Minimum 60°C for Legionella control (WHO / L8)")
with col3:
    standby_loss = st.number_input("Standby Loss (%/day)", value=5.0, step=0.5)

if st.button("Design Hot Water System", use_container_width=True):
    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "system_type": system_type,
        "num_occupants": occupants,
        "hot_water_l_person_day": daily_allowance,
        "inlet_water_temp_c": inlet_temp,
        "storage_temp_c": storage_temp,
        "delivery_temp_c": min(storage_temp - 5, 55),
        "legionella_pasteurisation": legionella,
        "recovery_time_hr": recovery_hr,
        "standby_loss_pct": standby_loss,
    }
    with st.spinner("Designing hot water system..."):
        result = api_post("/api/plumbing/hot-water-system", payload)

    if result:
        section_title("Hot Water System Results")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Daily Demand", f"{result.get('daily_demand_l', 0):.0f}", "L/day")
        with col2:
            result_card("Storage Volume", f"{result.get('selected_tank_l', 0):.0f}", "L tank")
        with col3:
            result_card("Heater Output", f"{result.get('heater_output_kw', 0):.1f}", "kW")
        with col4:
            result_card("Energy", f"{result.get('energy_required_kwh_day', 0):.1f}", "kWh/day")

        col1, col2, col3 = st.columns(3)
        with col1:
            result_card("Peak Hourly", f"{result.get('peak_hourly_demand_l', 0):.0f}", "L/hr")
        with col2:
            result_card("ΔT", f"{result.get('delta_t_k', 0):.1f}", "K")
        with col3:
            risk = result.get("legionella_risk", "HIGH")
            result_card("Legionella Risk", risk, "L8 Assessment", status="pass" if risk == "LOW" else "fail")

        legionella_ok = result.get("legionella_risk", "HIGH") == "LOW"
        compliance_badge(legionella_ok, f"Storage: {storage_temp}°C | L8/WHO Legionella Risk: {result.get('legionella_risk', '?')}")

        section_title(f"Standard: {result.get('standard', '')}")
        format_summary(result.get("summary", ""))

        section_title("Export")
        exp1, exp2, exp3 = st.columns(3)
        with exp1:
            try:
                from report_generator import generate_calculation_pdf as _gp
                import pandas as _pd
                _m = {"project_name": st.session_state.get("project_name", ""), "region": region_code,
                      "report_type": "hot_water_system", "discipline": "plumbing", "revision": "P01",
                      "date": str(_pd.Timestamp.today().date())}
                _pdf = _gp(_m, result)
                if _pdf:
                    st.download_button("⬇️ PDF Report", data=_pdf,
                        file_name=f"HotWater_{_pd.Timestamp.today().date()}.pdf",
                        mime="application/pdf", use_container_width=True)
            except Exception:
                st.info("PDF export: install reportlab.")
        with exp2:
            try:
                import io as _io
                import pandas as _pd
                _buf = _io.BytesIO()
                _pd.DataFrame([{k: v for k, v in result.items() if isinstance(v, (int, float, str))}]).to_excel(
                    _buf, index=False, sheet_name="Hot_Water")
                _buf.seek(0)
                st.download_button("⬇️ Excel Results", data=_buf.getvalue(),
                    file_name=f"HotWaterSystem_{_pd.Timestamp.today().date()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            except ImportError:
                st.info("Install openpyxl.")
        with exp3:
            if st.button("📋 Add to BOQ", use_container_width=True):
                if "boq_items" not in st.session_state:
                    st.session_state.boq_items = []
                st.session_state.boq_items.append({
                    "type": "hot_water_system",
                    "description": f"DHW System — {result.get('selected_tank_l', 0):.0f} L tank, {result.get('heater_output_kw', 0):.1f} kW heater",
                    "value": result.get("selected_tank_l"),
                })
                st.success(f"Hot water system added to BOQ ({len(st.session_state.boq_items)} items).")
