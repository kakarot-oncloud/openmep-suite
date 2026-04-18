"""Compliance Checker — OpenMEP"""

import streamlit as st
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, LIGHT_GREY,
    page_header, result_card, compliance_badge, section_title, api_post, region_selector,
    TEAL, TEAL_L
)

st.set_page_config(page_title="Compliance Checker — OpenMEP", page_icon="✅", layout="wide")
apply_theme_css()

page_header("Compliance Checker", "Verify MEP design parameters against regional electrical, lighting and mechanical standards", "✅")

with st.sidebar:
    st.markdown(f"<h3 style='color:{TEAL_L}; font-size:0.9rem; text-transform:uppercase; letter-spacing:2px;'>Standards Checked</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{DARK_GREY}; padding:1rem; border-radius:6px; font-size:0.8rem; color:{WHITE}; line-height:1.9;">
    <b style='color:{TEAL_L}'>GCC Electrical:</b><br>
    BS 7671 / IEC 60364<br>
    DEWA Schedule of Reqs<br><br>
    <b style='color:{TEAL_L}'>Europe / UK:</b><br>
    BS 7671:2018+A2:2022<br><br>
    <b style='color:{TEAL_L}'>India:</b><br>
    IS 732 / NBC Part 2<br><br>
    <b style='color:{TEAL_L}'>Australia:</b><br>
    AS/NZS 3000:2018<br><br>
    <b style='color:{TEAL_L}'>Lighting (all):</b><br>
    EN 12464-1 / NBC SP72<br><br>
    <b style='color:{TEAL_L}'>Mechanical (all):</b><br>
    ASHRAE 62.1 / ECBC
    </div>
    """, unsafe_allow_html=True)

section_title("Regional Settings")
region_code, sub_code = region_selector("cc")
discipline = st.selectbox("Discipline to Check", ["electrical", "mechanical", "plumbing", "fire", "all"])

tabs = st.tabs(["⚡ Cable Compliance", "💡 Lighting Compliance", "❄️ Mechanical Compliance", "🔧 Plumbing Compliance", "🚒 Fire Compliance"])

# ── Cable checks ───────────────────────────────────────────────────────────────
with tabs[0]:
    section_title("Add Cable Circuit Checks")
    if "cc_cables" not in st.session_state:
        st.session_state.cc_cables = [
            {"circuit_reference": "C1", "region": "gcc", "sub_region": "", "design_current_a": 30.0, "derated_rating_iz_a": 45.0, "voltage_drop_pct": 2.8, "vd_limit_pct": 5.0, "cable_size_mm2": 10.0, "earth_size_mm2": 6.0},
            {"circuit_reference": "C4-AHU", "region": "gcc", "sub_region": "", "design_current_a": 87.0, "derated_rating_iz_a": 82.0, "voltage_drop_pct": 4.1, "vd_limit_pct": 5.0, "cable_size_mm2": 25.0, "earth_size_mm2": 16.0},
        ]

    col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1.5, 1.5, 1.5, 1.5, 1.2, 1.2])
    for c, h in zip([col1,col2,col3,col4,col5,col6,col7], ["Circuit Ref", "Ib (A)", "Iz (A)", "VD %", "VD Limit %", "Size mm²", "Earth mm²"]):
        c.markdown(f"<span style='color:{LIGHT_GREY}; font-size:0.8rem; font-weight:600;'>{h}</span>", unsafe_allow_html=True)

    for i, check in enumerate(st.session_state.cc_cables):
        check["region"] = region_code
        c1,c2,c3,c4,c5,c6,c7 = st.columns([2, 1.5, 1.5, 1.5, 1.5, 1.2, 1.2])
        with c1: check["circuit_reference"] = st.text_input(f"ccref_{i}", value=check["circuit_reference"], label_visibility="collapsed", key=f"ccref_{i}")
        with c2: check["design_current_a"] = st.number_input(f"ccib_{i}", value=float(check["design_current_a"]), min_value=0.0, step=0.5, label_visibility="collapsed", key=f"ccib_{i}")
        with c3: check["derated_rating_iz_a"] = st.number_input(f"cciz_{i}", value=float(check["derated_rating_iz_a"]), min_value=0.0, step=0.5, label_visibility="collapsed", key=f"cciz_{i}")
        with c4: check["voltage_drop_pct"] = st.number_input(f"ccvd_{i}", value=float(check["voltage_drop_pct"]), min_value=0.0, max_value=20.0, step=0.1, label_visibility="collapsed", key=f"ccvd_{i}")
        with c5: check["vd_limit_pct"] = st.number_input(f"ccvdl_{i}", value=float(check["vd_limit_pct"]), min_value=0.5, max_value=20.0, step=0.5, label_visibility="collapsed", key=f"ccvdl_{i}")
        with c6: check["cable_size_mm2"] = st.number_input(f"ccmm_{i}", value=float(check["cable_size_mm2"]), min_value=1.5, max_value=630.0, step=0.5, label_visibility="collapsed", key=f"ccmm_{i}")
        with c7: check["earth_size_mm2"] = st.number_input(f"ccearth_{i}", value=float(check["earth_size_mm2"]), min_value=1.0, max_value=300.0, step=0.5, label_visibility="collapsed", key=f"ccearth_{i}")

    if st.button("+ Add Cable Check", key="add_cable_chk"):
        st.session_state.cc_cables.append({"circuit_reference": f"C{len(st.session_state.cc_cables)+1}", "region": region_code, "sub_region": "", "design_current_a": 0.0, "derated_rating_iz_a": 0.0, "voltage_drop_pct": 0.0, "vd_limit_pct": 5.0, "cable_size_mm2": 2.5, "earth_size_mm2": 1.5})
        st.rerun()

# ── Lighting checks ─────────────────────────────────────────────────────────────
with tabs[1]:
    section_title("Lighting Compliance Checks")
    if "cc_lighting" not in st.session_state:
        st.session_state.cc_lighting = [
            {"region": "gcc", "room_type": "office", "achieved_lux": 520.0, "target_lux": 500.0, "lpd_w_per_m2": 9.5, "lpd_limit_w_per_m2": 12.0, "uniformity_ratio": 0.65},
            {"region": "gcc", "room_type": "corridor", "achieved_lux": 80.0, "target_lux": 100.0, "lpd_w_per_m2": 4.0, "lpd_limit_w_per_m2": 5.0, "uniformity_ratio": 0.35},
        ]
    ROOM_TYPES = ["office", "meeting_room", "corridor", "lobby", "warehouse", "retail", "car_park", "general"]

    col1, col2, col3, col4, col5, col6 = st.columns([1.5, 1.5, 1.5, 1.5, 1.5, 1.5])
    for c, h in zip([col1,col2,col3,col4,col5,col6], ["Room Type", "Achieved lux", "Target lux", "LPD W/m²", "LPD Limit", "Uniformity"]):
        c.markdown(f"<span style='color:{LIGHT_GREY}; font-size:0.8rem; font-weight:600;'>{h}</span>", unsafe_allow_html=True)

    for i, lchk in enumerate(st.session_state.cc_lighting):
        lchk["region"] = region_code
        c1,c2,c3,c4,c5,c6 = st.columns([1.5, 1.5, 1.5, 1.5, 1.5, 1.5])
        with c1:
            rt_idx = ROOM_TYPES.index(lchk["room_type"]) if lchk["room_type"] in ROOM_TYPES else 0
            lchk["room_type"] = st.selectbox(f"lrt_{i}", ROOM_TYPES, index=rt_idx, label_visibility="collapsed", key=f"lrt_{i}")
        with c2: lchk["achieved_lux"] = st.number_input(f"llux_{i}", value=float(lchk["achieved_lux"]), min_value=0.0, step=10.0, label_visibility="collapsed", key=f"llux_{i}")
        with c3: lchk["target_lux"] = st.number_input(f"ltlux_{i}", value=float(lchk["target_lux"]), min_value=0.0, step=10.0, label_visibility="collapsed", key=f"ltlux_{i}")
        with c4: lchk["lpd_w_per_m2"] = st.number_input(f"llpd_{i}", value=float(lchk["lpd_w_per_m2"]), min_value=0.0, step=0.5, label_visibility="collapsed", key=f"llpd_{i}")
        with c5: lchk["lpd_limit_w_per_m2"] = st.number_input(f"llpdl_{i}", value=float(lchk["lpd_limit_w_per_m2"]), min_value=0.0, step=0.5, label_visibility="collapsed", key=f"llpdl_{i}")
        with c6: lchk["uniformity_ratio"] = st.number_input(f"lunif_{i}", value=float(lchk["uniformity_ratio"]), min_value=0.0, max_value=1.0, step=0.05, label_visibility="collapsed", key=f"lunif_{i}")

    if st.button("+ Add Lighting Check", key="add_light_chk"):
        st.session_state.cc_lighting.append({"region": region_code, "room_type": "office", "achieved_lux": 0.0, "target_lux": 500.0, "lpd_w_per_m2": 0.0, "lpd_limit_w_per_m2": 12.0, "uniformity_ratio": 0.0})
        st.rerun()

# ── Mechanical checks ───────────────────────────────────────────────────────────
with tabs[2]:
    section_title("Mechanical / HVAC Compliance Checks")
    if "cc_mechanical" not in st.session_state:
        st.session_state.cc_mechanical = [
            {"region": "gcc", "zone_type": "office", "fresh_air_l_s_person": 10.0, "supply_air_ach": 6.0, "cooling_w_per_m2": 75.0},
        ]
    ZONE_TYPES = ["office", "meeting_room", "corridor", "retail", "warehouse", "kitchen", "general"]

    col1, col2, col3, col4 = st.columns(4)
    for c, h in zip([col1,col2,col3,col4], ["Zone Type", "Fresh Air (L/s/person)", "Supply ACH", "Cooling W/m²"]):
        c.markdown(f"<span style='color:{LIGHT_GREY}; font-size:0.8rem; font-weight:600;'>{h}</span>", unsafe_allow_html=True)

    for i, mchk in enumerate(st.session_state.cc_mechanical):
        mchk["region"] = region_code
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            zt_idx = ZONE_TYPES.index(mchk["zone_type"]) if mchk["zone_type"] in ZONE_TYPES else 0
            mchk["zone_type"] = st.selectbox(f"mzt_{i}", ZONE_TYPES, index=zt_idx, label_visibility="collapsed", key=f"mzt_{i}")
        with c2: mchk["fresh_air_l_s_person"] = st.number_input(f"mfa_{i}", value=float(mchk["fresh_air_l_s_person"]), min_value=0.0, step=0.5, label_visibility="collapsed", key=f"mfa_{i}")
        with c3: mchk["supply_air_ach"] = st.number_input(f"mach_{i}", value=float(mchk["supply_air_ach"]), min_value=0.0, step=0.5, label_visibility="collapsed", key=f"mach_{i}")
        with c4: mchk["cooling_w_per_m2"] = st.number_input(f"mw2_{i}", value=float(mchk["cooling_w_per_m2"]), min_value=0.0, step=5.0, label_visibility="collapsed", key=f"mw2_{i}")

    if st.button("+ Add Mechanical Check", key="add_mech_chk"):
        st.session_state.cc_mechanical.append({"region": region_code, "zone_type": "office", "fresh_air_l_s_person": 10.0, "supply_air_ach": 6.0, "cooling_w_per_m2": 75.0})
        st.rerun()

# ── Plumbing checks ──────────────────────────────────────────────────────────────
with tabs[3]:
    section_title("Plumbing System Compliance Checks")
    if "cc_plumbing" not in st.session_state:
        st.session_state.cc_plumbing = [
            {"system_type": "cold_water", "pipe_velocity_m_s": 1.5, "design_pressure_bar": 4.0, "min_pressure_bar": 0.5, "max_pressure_bar": 10.0, "storage_temp_c": 0.0, "distribution_temp_c": 0.0, "has_backflow_preventer": True, "has_tmax_valve": False},
            {"system_type": "hot_water", "pipe_velocity_m_s": 1.2, "design_pressure_bar": 3.5, "min_pressure_bar": 0.5, "max_pressure_bar": 8.0, "storage_temp_c": 62.0, "distribution_temp_c": 55.0, "has_backflow_preventer": True, "has_tmax_valve": True},
        ]
    SYSTEM_TYPES_P = ["cold_water", "hot_water", "drainage"]

    col1, col2, col3, col4, col5 = st.columns(5)
    for c, h in zip([col1,col2,col3,col4,col5], ["System Type", "Velocity (m/s)", "Pressure (bar)", "Storage T (°C)", "Distribution T (°C)"]):
        c.markdown(f"<span style='color:{LIGHT_GREY}; font-size:0.8rem; font-weight:600;'>{h}</span>", unsafe_allow_html=True)

    for i, pchk in enumerate(st.session_state.cc_plumbing):
        pchk["region"] = region_code
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st_idx = SYSTEM_TYPES_P.index(pchk["system_type"]) if pchk["system_type"] in SYSTEM_TYPES_P else 0
            pchk["system_type"] = st.selectbox(f"pstype_{i}", SYSTEM_TYPES_P, index=st_idx, label_visibility="collapsed", key=f"pstype_{i}")
        with c2: pchk["pipe_velocity_m_s"] = st.number_input(f"pvel_{i}", value=float(pchk["pipe_velocity_m_s"]), min_value=0.0, step=0.1, label_visibility="collapsed", key=f"pvel_{i}")
        with c3: pchk["design_pressure_bar"] = st.number_input(f"ppress_{i}", value=float(pchk["design_pressure_bar"]), min_value=0.0, step=0.5, label_visibility="collapsed", key=f"ppress_{i}")
        with c4: pchk["storage_temp_c"] = st.number_input(f"pstmp_{i}", value=float(pchk["storage_temp_c"]), min_value=0.0, max_value=100.0, step=1.0, label_visibility="collapsed", key=f"pstmp_{i}")
        with c5: pchk["distribution_temp_c"] = st.number_input(f"pdtmp_{i}", value=float(pchk["distribution_temp_c"]), min_value=0.0, max_value=100.0, step=1.0, label_visibility="collapsed", key=f"pdtmp_{i}")
        c6, c7 = st.columns(2)
        with c6: pchk["has_backflow_preventer"] = st.checkbox("Backflow preventer fitted", value=pchk.get("has_backflow_preventer", False), key=f"pbfp_{i}")
        with c7: pchk["has_tmax_valve"] = st.checkbox("TMV / Tmax valve fitted", value=pchk.get("has_tmax_valve", False), key=f"ptmv_{i}")

    if st.button("+ Add Plumbing Check", key="add_plumb_chk"):
        st.session_state.cc_plumbing.append({"system_type": "cold_water", "pipe_velocity_m_s": 1.5, "design_pressure_bar": 4.0, "min_pressure_bar": 0.5, "max_pressure_bar": 10.0, "storage_temp_c": 0.0, "distribution_temp_c": 0.0, "has_backflow_preventer": False, "has_tmax_valve": False})
        st.rerun()

# ── Fire checks ──────────────────────────────────────────────────────────────────
with tabs[4]:
    section_title("Fire Protection Compliance Checks")
    if "cc_fire" not in st.session_state:
        st.session_state.cc_fire = [
            {"system_type": "sprinkler", "hazard_class": "OH1", "design_density_mm_min": 5.5, "min_density_mm_min": 5.0, "design_pressure_bar": 0.8, "min_pressure_bar": 0.35, "pump_rated_flow_l_min": 2000.0, "required_flow_l_min": 1500.0, "tank_volume_m3": 150.0, "required_volume_m3": 120.0, "has_duty_standby": True, "has_jockey_pump": True},
        ]
    SYSTEM_TYPES_F = ["sprinkler", "wet_riser", "fire_pump", "fire_tank"]
    HAZARD_CLASSES_F = ["LH", "OH1", "OH2", "EH1", "EH2"]

    col1, col2, col3, col4, col5 = st.columns(5)
    for c, h in zip([col1,col2,col3,col4,col5], ["System Type", "Hazard Class", "Density (mm/min)", "Pressure (bar)", "Flow (L/min)"]):
        c.markdown(f"<span style='color:{LIGHT_GREY}; font-size:0.8rem; font-weight:600;'>{h}</span>", unsafe_allow_html=True)

    for i, fchk in enumerate(st.session_state.cc_fire):
        fchk["region"] = region_code
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            fst_idx = SYSTEM_TYPES_F.index(fchk["system_type"]) if fchk["system_type"] in SYSTEM_TYPES_F else 0
            fchk["system_type"] = st.selectbox(f"fstype_{i}", SYSTEM_TYPES_F, index=fst_idx, label_visibility="collapsed", key=f"fstype_{i}")
        with c2:
            fhz_idx = HAZARD_CLASSES_F.index(fchk["hazard_class"]) if fchk["hazard_class"] in HAZARD_CLASSES_F else 1
            fchk["hazard_class"] = st.selectbox(f"fhaz_{i}", HAZARD_CLASSES_F, index=fhz_idx, label_visibility="collapsed", key=f"fhaz_{i}")
        with c3: fchk["design_density_mm_min"] = st.number_input(f"fdense_{i}", value=float(fchk["design_density_mm_min"]), min_value=0.0, step=0.25, label_visibility="collapsed", key=f"fdense_{i}")
        with c4: fchk["design_pressure_bar"] = st.number_input(f"fpress_{i}", value=float(fchk["design_pressure_bar"]), min_value=0.0, step=0.1, label_visibility="collapsed", key=f"fpress_{i}")
        with c5: fchk["pump_rated_flow_l_min"] = st.number_input(f"fpflow_{i}", value=float(fchk["pump_rated_flow_l_min"]), min_value=0.0, step=50.0, label_visibility="collapsed", key=f"fpflow_{i}")
        c6, c7, c8 = st.columns(3)
        with c6: fchk["required_flow_l_min"] = st.number_input(f"freqflow_{i}", label="Required Flow (L/min)", value=float(fchk["required_flow_l_min"]), min_value=0.0, step=50.0, key=f"freqflow_{i}")
        with c7: fchk["tank_volume_m3"] = st.number_input(f"ftankvol_{i}", label="Tank Vol (m³)", value=float(fchk["tank_volume_m3"]), min_value=0.0, step=5.0, key=f"ftankvol_{i}")
        with c8: fchk["required_volume_m3"] = st.number_input(f"freqvol_{i}", label="Required Vol (m³)", value=float(fchk["required_volume_m3"]), min_value=0.0, step=5.0, key=f"freqvol_{i}")
        c9, c10 = st.columns(2)
        with c9: fchk["has_duty_standby"] = st.checkbox("Duty + Standby pump", value=fchk.get("has_duty_standby", False), key=f"fds_{i}")
        with c10: fchk["has_jockey_pump"] = st.checkbox("Jockey pump fitted", value=fchk.get("has_jockey_pump", False), key=f"fjockey_{i}")

    if st.button("+ Add Fire Check", key="add_fire_chk"):
        st.session_state.cc_fire.append({"system_type": "sprinkler", "hazard_class": "OH1", "design_density_mm_min": 5.0, "min_density_mm_min": 5.0, "design_pressure_bar": 0.5, "min_pressure_bar": 0.35, "pump_rated_flow_l_min": 0.0, "required_flow_l_min": 0.0, "tank_volume_m3": 0.0, "required_volume_m3": 0.0, "has_duty_standby": False, "has_jockey_pump": False})
        st.rerun()

# ── Run compliance check ────────────────────────────────────────────────────────
if st.button("Run Compliance Check", use_container_width=True):
    # API ComplianceReportRequest: project_name, region, discipline, cable_checks, lighting_checks, mechanical_checks
    cable_checks = [
        {
            "circuit_reference": c["circuit_reference"],
            "region": region_code,
            "sub_region": "",
            "design_current_a": c["design_current_a"],
            "derated_rating_iz_a": c["derated_rating_iz_a"],
            "voltage_drop_pct": c["voltage_drop_pct"],
            "vd_limit_pct": c["vd_limit_pct"],
            "cable_size_mm2": c["cable_size_mm2"],
            "earth_size_mm2": c["earth_size_mm2"],
        }
        for c in st.session_state.cc_cables
    ] if discipline in ("electrical", "all") else []

    lighting_checks = [
        {
            "region": region_code,
            "room_type": l["room_type"],
            "achieved_lux": l["achieved_lux"],
            "target_lux": l["target_lux"],
            "lpd_w_per_m2": l["lpd_w_per_m2"],
            "lpd_limit_w_per_m2": l["lpd_limit_w_per_m2"],
            "uniformity_ratio": l["uniformity_ratio"],
        }
        for l in st.session_state.cc_lighting
    ] if discipline in ("electrical", "all") else []

    mechanical_checks = [
        {
            "region": region_code,
            "zone_type": m["zone_type"],
            "fresh_air_l_s_person": m["fresh_air_l_s_person"],
            "supply_air_ach": m["supply_air_ach"],
            "cooling_w_per_m2": m["cooling_w_per_m2"],
        }
        for m in st.session_state.cc_mechanical
    ] if discipline in ("mechanical", "all") else []

    plumbing_checks = [
        {
            "region": region_code,
            "system_type": p["system_type"],
            "pipe_velocity_m_s": p["pipe_velocity_m_s"],
            "design_pressure_bar": p["design_pressure_bar"],
            "min_pressure_bar": p.get("min_pressure_bar", 0.5),
            "max_pressure_bar": p.get("max_pressure_bar", 10.0),
            "storage_temp_c": p.get("storage_temp_c", 0.0),
            "distribution_temp_c": p.get("distribution_temp_c", 0.0),
            "has_backflow_preventer": p.get("has_backflow_preventer", False),
            "has_tmax_valve": p.get("has_tmax_valve", False),
        }
        for p in st.session_state.get("cc_plumbing", [])
    ] if discipline in ("plumbing", "all") else []

    fire_checks = [
        {
            "region": region_code,
            "system_type": f["system_type"],
            "hazard_class": f["hazard_class"],
            "design_density_mm_min": f.get("design_density_mm_min", 0.0),
            "min_density_mm_min": f.get("min_density_mm_min", 0.0),
            "design_pressure_bar": f.get("design_pressure_bar", 0.0),
            "min_pressure_bar": f.get("min_pressure_bar", 0.0),
            "pump_rated_flow_l_min": f.get("pump_rated_flow_l_min", 0.0),
            "required_flow_l_min": f.get("required_flow_l_min", 0.0),
            "tank_volume_m3": f.get("tank_volume_m3", 0.0),
            "required_volume_m3": f.get("required_volume_m3", 0.0),
            "has_duty_standby": f.get("has_duty_standby", False),
            "has_jockey_pump": f.get("has_jockey_pump", False),
        }
        for f in st.session_state.get("cc_fire", [])
    ] if discipline in ("fire", "all") else []

    payload = {
        "project_name": st.session_state.get("project_name", ""),
        "project_reference": st.session_state.get("project_number", ""),
        "region": region_code,
        "sub_region": sub_code,
        "discipline": discipline,
        "cable_checks": cable_checks,
        "lighting_checks": lighting_checks,
        "mechanical_checks": mechanical_checks,
        "plumbing_checks": plumbing_checks,
        "fire_checks": fire_checks,
    }
    with st.spinner("Checking compliance..."):
        result = api_post("/api/compliance/check", payload)

    if result:
        section_title("Compliance Summary")
        total_checks = result.get("total_checks", 0)
        checks_passed = result.get("checks_passed", 0)
        checks_failed = result.get("checks_failed", 0)

        col1, col2, col3 = st.columns(3)
        with col1:
            result_card("Total Checks", str(total_checks), "checks")
        with col2:
            result_card("✅ Passed", str(checks_passed), "checks", status="pass")
        with col3:
            result_card("❌ Failed", str(checks_failed), "checks", status="fail" if checks_failed > 0 else "pass")

        overall = result.get("overall_compliant", False)
        compliance_badge(overall, f"Region: {region_code.upper()} | Discipline: {discipline}")

        # Cable results — API structure: electrical.cable_circuits[].checks[]
        electrical = result.get("electrical", {})
        cable_circuits = electrical.get("cable_circuits", [])
        if cable_circuits:
            section_title("Cable Compliance Results")
            rows = []
            for circ in cable_circuits:
                circ_ref = circ.get("circuit_reference", "")
                overall_pass = circ.get("overall_passed", False)
                for chk in circ.get("checks", []):
                    rows.append({
                        "Circuit": circ_ref,
                        "Check": chk.get("check", ""),
                        "Clause": chk.get("clause", ""),
                        "Actual": chk.get("actual", ""),
                        "Limit": chk.get("limit", ""),
                        "Status": "✅ PASS" if chk.get("passed") else "❌ FAIL",
                        "Note": chk.get("note", ""),
                    })
                rows.append({
                    "Circuit": circ_ref, "Check": "─── OVERALL ───",
                    "Clause": "", "Actual": "", "Limit": "",
                    "Status": "✅ PASS" if overall_pass else "❌ FAIL", "Note": "",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # Lighting results — API: lighting.rooms[].checks[]
        lighting = result.get("lighting", {})
        lighting_rooms = lighting.get("rooms", [])
        if lighting_rooms:
            section_title("Lighting Compliance Results")
            rows = []
            for room in lighting_rooms:
                for chk in room.get("checks", []):
                    rows.append({
                        "Zone": room.get("room_type", ""),
                        "Check": chk.get("check", ""),
                        "Actual": chk.get("actual", ""),
                        "Required": chk.get("limit", ""),
                        "Status": "✅ PASS" if chk.get("passed") else "❌ FAIL",
                        "Standard": chk.get("standard", ""),
                    })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # Mechanical results — API: mechanical.zones[].checks[]
        mechanical = result.get("mechanical", {})
        mech_zones = mechanical.get("zones", [])
        if mech_zones:
            section_title("Mechanical Compliance Results")
            rows = []
            for zone in mech_zones:
                for chk in zone.get("checks", []):
                    rows.append({
                        "Zone": zone.get("zone_type", ""),
                        "Check": chk.get("check", ""),
                        "Actual": chk.get("actual", ""),
                        "Required": chk.get("limit", ""),
                        "Status": "✅ PASS" if chk.get("passed") else "❌ FAIL",
                    })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # Plumbing results — API: plumbing.systems[].checks[]
        plumbing_r = result.get("plumbing", {})
        plumbing_systems = plumbing_r.get("systems", [])
        if plumbing_systems:
            section_title("Plumbing Compliance Results")
            rows = []
            for sys in plumbing_systems:
                for chk in sys.get("checks", []):
                    rows.append({
                        "System": sys.get("system_type", ""),
                        "Check": chk.get("check", ""),
                        "Clause": chk.get("clause", ""),
                        "Actual": chk.get("actual", ""),
                        "Required": chk.get("limit", ""),
                        "Status": "✅ PASS" if chk.get("passed") else "❌ FAIL",
                        "Note": chk.get("note", ""),
                    })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # Fire results — API: fire.systems[].checks[]
        fire_r = result.get("fire", {})
        fire_systems = fire_r.get("systems", [])
        if fire_systems:
            section_title("Fire Protection Compliance Results")
            rows = []
            for sys in fire_systems:
                for chk in sys.get("checks", []):
                    rows.append({
                        "System": sys.get("system_type", ""),
                        "Hazard": sys.get("hazard_class", ""),
                        "Check": chk.get("check", ""),
                        "Clause": chk.get("clause", ""),
                        "Actual": chk.get("actual", ""),
                        "Required": chk.get("limit", ""),
                        "Status": "✅ PASS" if chk.get("passed") else "❌ FAIL",
                        "Note": chk.get("note", ""),
                    })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        if result.get("recommendations"):
            section_title("Recommendations")
            for rec in result.get("recommendations", []):
                st.markdown(f"""
                <div style="background:{DARK_GREY}; border-left:3px solid {TEAL}; padding:0.75rem 1rem; margin:0.5rem 0; border-radius:0 6px 6px 0;">
                    <span style="color:{WHITE}; font-size:0.9rem;">{rec}</span>
                </div>
                """, unsafe_allow_html=True)

        # ── Export ────────────────────────────────────────────────────────────
        section_title("Export")
        exp1, exp2 = st.columns(2)
        with exp1:
            try:
                from report_generator import generate_calculation_pdf as _gp
                _m = {"project_name": st.session_state.get("project_name", "MEP Project"),
                      "region": region_code, "report_type": "compliance",
                      "discipline": discipline, "revision": "P01",
                      "date": str(pd.Timestamp.today().date())}
                _pdf = _gp(_m, result)
                if _pdf:
                    st.download_button("⬇️ PDF Compliance Report", data=_pdf,
                        file_name=f"ComplianceReport_{region_code}_{pd.Timestamp.today().date()}.pdf",
                        mime="application/pdf", use_container_width=True)
            except Exception:
                st.info("PDF export: install reportlab.")
        with exp2:
            try:
                import io as _io
                _rows = []
                for circ in result.get("electrical", {}).get("cable_circuits", []):
                    for chk in circ.get("checks", []):
                        _rows.append({"Circuit": circ.get("circuit_reference",""),
                                      "Check": chk.get("check",""), "Actual": chk.get("actual",""),
                                      "Limit": chk.get("limit",""),
                                      "Status": "PASS" if chk.get("passed") else "FAIL"})
                if _rows:
                    _buf = _io.BytesIO()
                    pd.DataFrame(_rows).to_excel(_buf, index=False, sheet_name="Compliance")
                    _buf.seek(0)
                    st.download_button("⬇️ Excel Report", data=_buf.getvalue(),
                        file_name=f"ComplianceReport_{region_code}_{pd.Timestamp.today().date()}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True)
            except ImportError:
                st.info("Install openpyxl for Excel export.")
