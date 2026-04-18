"""Generator Sizing — OpenMEP"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, LIGHT_GREY,
    page_header, result_card, compliance_badge, section_title, format_summary,
    api_post, region_selector,
    TEAL, TEAL_L
)

st.set_page_config(page_title="Generator Sizing — OpenMEP", page_icon="🔋", layout="wide")
apply_theme_css()

page_header("Generator Sizing", "Standby/prime power generator sizing with ISO 8528 altitude and temperature derating", "🔋")

with st.sidebar:
    st.markdown(f"<h3 style='color:{TEAL_L}; font-size:0.9rem; text-transform:uppercase; letter-spacing:2px;'>ISO 8528 Standard</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{DARK_GREY}; padding:1rem; border-radius:6px; font-size:0.8rem; color:{WHITE}; line-height:1.8;">
    <b style='color:{TEAL_L}'>Supply Systems:</b><br>
    <b>standby</b> — Emergency Standby<br>
    <b>prime</b> — Prime Power<br>
    <b>baseload</b> — Continuous Power<br><br>
    <b style='color:{TEAL_L}'>Derating Factors:</b><br>
    Altitude: ~1% per 100m &gt;1000m<br>
    Temperature: per ISO 8528-1<br><br>
    <b style='color:{TEAL_L}'>Starting Methods:</b><br>
    VFD — Minimal step load<br>
    DOL — 6-8× rated current<br>
    StarDelta — Reduced start<br>
    Soft starter — Smooth start
    </div>
    """, unsafe_allow_html=True)

if "gen_loads" not in st.session_state:
    st.session_state.gen_loads = [
        {"description": "Essential Lighting", "kw": 30.0, "power_factor": 0.90, "demand_factor": 1.0, "load_type": "lighting", "starting_method": "VFD"},
        {"description": "Fire Fighting Pumps", "kw": 55.0, "power_factor": 0.85, "demand_factor": 1.0, "load_type": "motor", "starting_method": "DOL"},
        {"description": "Emergency HVAC", "kw": 80.0, "power_factor": 0.85, "demand_factor": 0.75, "load_type": "motor", "starting_method": "VFD"},
        {"description": "Critical IT / UPS", "kw": 40.0, "power_factor": 0.90, "demand_factor": 1.0, "load_type": "general", "starting_method": "VFD"},
        {"description": "Lifts (Emergency)", "kw": 22.0, "power_factor": 0.85, "demand_factor": 0.5, "load_type": "motor", "starting_method": "StarDelta"},
    ]

section_title("Generator Parameters")
region_code, sub_code = region_selector("gen")
col2, col3, col4 = st.columns(3)
with col2:
    supply_system = st.selectbox("Supply System", ["standby", "prime", "baseload"])
with col3:
    site_altitude_m = st.number_input("Site Altitude (m)", min_value=0, max_value=4000, value=50 if region_code in ("gcc",) else 150, step=50)
with col4:
    site_temp_c = st.number_input("Ambient Temp (°C)", min_value=-10, max_value=55, value=45 if region_code in ("gcc","india") else 35, step=1)

col1, col2, col3 = st.columns(3)
with col1:
    rated_pf = st.number_input("Generator Rated PF", min_value=0.7, max_value=1.0, value=0.8, step=0.05)
with col2:
    future_expansion_pct = st.number_input("Future Expansion (%)", min_value=0, max_value=50, value=20, step=5)
with col3:
    max_voltage_dip_pct = st.number_input("Max Voltage Dip (%)", min_value=5.0, max_value=35.0, value=15.0, step=1.0)

section_title("Essential Load Schedule")
# API schema: description, kw, power_factor, demand_factor, load_type, starting_method
col1, col2, col3, col4, col5, col6 = st.columns([3, 1.5, 1, 1.2, 1.5, 1.5])
for c, h in zip([col1,col2,col3,col4,col5,col6], ["Description", "kW", "PF", "Demand Factor", "Load Type", "Starting"]):
    c.markdown(f"<span style='color:{LIGHT_GREY}; font-size:0.8rem; font-weight:600;'>{h}</span>", unsafe_allow_html=True)

LOAD_TYPES = ["general", "lighting", "motor", "ups", "heating", "cooling"]
STARTING_METHODS = ["VFD", "DOL", "StarDelta", "SoftStarter", "None"]

for i, load in enumerate(st.session_state.gen_loads):
    c1, c2, c3, c4, c5, c6 = st.columns([3, 1.5, 1, 1.2, 1.5, 1.5])
    with c1:
        load["description"] = st.text_input(f"gd_{i}", value=load["description"], label_visibility="collapsed", key=f"gd_{i}")
    with c2:
        load["kw"] = st.number_input(f"gkw_{i}", value=float(load["kw"]), min_value=0.0, max_value=5000.0, step=0.5, label_visibility="collapsed", key=f"gkw_{i}")
    with c3:
        load["power_factor"] = st.number_input(f"gpf_{i}", value=float(load["power_factor"]), min_value=0.5, max_value=1.0, step=0.05, label_visibility="collapsed", key=f"gpf_{i}")
    with c4:
        load["demand_factor"] = st.number_input(f"gdf_{i}", value=float(load["demand_factor"]), min_value=0.1, max_value=1.0, step=0.05, label_visibility="collapsed", key=f"gdf_{i}")
    with c5:
        idx = LOAD_TYPES.index(load["load_type"]) if load["load_type"] in LOAD_TYPES else 0
        load["load_type"] = st.selectbox(f"glt_{i}", LOAD_TYPES, index=idx, label_visibility="collapsed", key=f"glt_{i}")
    with c6:
        sidx = STARTING_METHODS.index(load["starting_method"]) if load["starting_method"] in STARTING_METHODS else 0
        load["starting_method"] = st.selectbox(f"gsm_{i}", STARTING_METHODS, index=sidx, label_visibility="collapsed", key=f"gsm_{i}")

col1, col2 = st.columns([2, 10])
with col1:
    if st.button("+ Add Load"):
        st.session_state.gen_loads.append({
            "description": "New Load", "kw": 0.0, "power_factor": 0.85,
            "demand_factor": 1.0, "load_type": "general", "starting_method": "VFD",
        })
        st.rerun()
with col2:
    if st.button("Remove Last") and st.session_state.gen_loads:
        st.session_state.gen_loads.pop()
        st.rerun()

if st.button("Size Generator", use_container_width=True):
    loads_payload = [
        {
            "description": l["description"],
            "kw": l["kw"],
            "power_factor": l["power_factor"],
            "demand_factor": l["demand_factor"],
            "load_type": l["load_type"],
            "starting_method": l["starting_method"],
        }
        for l in st.session_state.gen_loads if l["kw"] > 0
    ]
    if not loads_payload:
        st.warning("Please add at least one load with kW > 0.")
    else:
        payload = {
            "region": region_code,
            "sub_region": sub_code,
            "loads": loads_payload,
            "site_altitude_m": float(site_altitude_m),
            "ambient_temp_c": float(site_temp_c),
            "rated_pf": rated_pf,
            "supply_system": supply_system,
            "max_voltage_dip_pct": max_voltage_dip_pct,
            "future_expansion_pct": float(future_expansion_pct),
        }
        with st.spinner("Sizing generator..."):
            result = api_post("/api/electrical/generator-sizing", payload)

        if result:
            section_title("Generator Sizing Results")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                result_card("Total Demand", f"{result.get('total_demand_kw', 0):.1f}", "kW")
            with col2:
                result_card("Demand kVA", f"{result.get('total_demand_kva', 0):.1f}", "kVA")
            with col3:
                result_card("Design kVA", f"{result.get('design_kva', 0):.0f}", "kVA")
            with col4:
                result_card("Standard Size", f"{result.get('standard_kva', 0):.0f}", "kVA")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                alt_d = result.get("altitude_derating_pct", 0)
                result_card("Altitude Derate", f"{alt_d:.1f}", "%")
            with col2:
                tmp_d = result.get("temp_derating_pct", 0)
                result_card("Temp Derate", f"{tmp_d:.1f}", "%")
            with col3:
                result_card("Largest Motor", f"{result.get('largest_motor_kw', 0):.1f}", "kW")
            with col4:
                result_card("Step Load kVA", f"{result.get('required_kva_starting', 0):.0f}", "kVA")

            step_ok = result.get("step_load_ok", True)
            compliance_badge(step_ok, f"Voltage dip: {result.get('step_load_voltage_dip_pct', 0):.1f}% (limit {max_voltage_dip_pct:.0f}%)")

            if result.get("fuel_consumption_l_hr"):
                section_title("Fuel & Tank")
                col1, col2 = st.columns(2)
                with col1:
                    result_card("Fuel Rate", f"{result.get('fuel_consumption_l_hr', 0):.1f}", "L/hr")
                with col2:
                    result_card("Tank (24hr)", f"{result.get('tank_capacity_24h_l', 0):,.0f}", "L")

            if result.get("standard"):
                st.markdown(f"""
                <div style="background:{DARK_GREY}; border:1px solid {TEAL}44; border-radius:8px; padding:1rem; margin:1rem 0;">
                    <span style='color:{TEAL_L}; font-weight:700;'>Standard: </span>
                    <span style='color:{WHITE};'>{result.get('standard', '')}</span>
                </div>
                """, unsafe_allow_html=True)

            if result.get("summary"):
                section_title("Calculation Summary")
                format_summary(result.get("summary", ""))

            # ── Export / Add-to-BOQ ──────────────────────────────────────────
            section_title("Export")
            import io as _io
            import pandas as pd
            exp1, exp2, exp3 = st.columns(3)

            with exp1:
                try:
                    from report_generator import generate_calculation_pdf
                    report_meta = {
                        "project_name": st.session_state.get("project_name", "MEP Project"),
                        "region": region_code, "report_type": "generator_sizing",
                        "discipline": "electrical", "revision": "P01",
                        "date": str(pd.Timestamp.today().date()),
                    }
                    pdf_bytes = generate_calculation_pdf(report_meta, result)
                    if pdf_bytes:
                        st.download_button("⬇️ PDF Report", data=pdf_bytes,
                            file_name=f"GeneratorSizing_{pd.Timestamp.today().date()}.pdf",
                            mime="application/pdf", use_container_width=True)
                except Exception:
                    st.info("PDF export available after report generator is configured.")

            with exp2:
                buf = _io.BytesIO()
                rows = [{"Description": l.get("description",""), "kW": l.get("kw",0),
                         "PF": l.get("power_factor",0), "DF": l.get("demand_factor",0),
                         "Type": l.get("load_type",""), "Start": l.get("starting_method","")}
                        for l in result.get("loads", [])]
                try:
                    pd.DataFrame(rows).to_excel(buf, index=False, sheet_name="Gen_Loads")
                    buf.seek(0)
                    st.download_button("⬇️ Excel Schedule", data=buf.getvalue(),
                        file_name=f"GeneratorSizing_{pd.Timestamp.today().date()}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True)
                except ImportError:
                    st.info("Install openpyxl for Excel export.")

            with exp3:
                if st.button("📋 Add Generator to BOQ", use_container_width=True):
                    boq_item = {
                        "description": f"Standby Generator — {result.get('standard_kva', 0):.0f} kVA",
                        "standard_kva": result.get("standard_kva", 0),
                        "total_demand_kw": result.get("total_demand_kw", 0),
                    }
                    if "boq_items" not in st.session_state:
                        st.session_state.boq_items = []
                    st.session_state.boq_items.append(boq_item)
                    st.success(f"Generator ({result.get('standard_kva',0):.0f} kVA) added to BOQ session.")
