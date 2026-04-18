"""Rainwater Harvesting System Sizing — OpenMEP"""

import streamlit as st
import sys
import os
import io
import pandas as pd
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, LIGHT_GREY,
    page_header, section_title, region_selector, api_post,
    metric_card_html,
    TEAL, TEAL_L
)

st.set_page_config(page_title="Rainwater Harvesting — OpenMEP", page_icon="🌧️", layout="wide")
apply_theme_css()

page_header("Rainwater Harvesting", "Roof collection, first-flush, storage sizing and demand offset", "🌧️")

region_code, sub_code = region_selector("rh")

RAINFALL_DEFAULTS = {
    "gcc": {"rainfall_mm": 120, "runoff": 0.85, "filter_eff": 90, "storage_days": 5, "non_potable_lpd": 30},
    "europe": {"rainfall_mm": 700, "runoff": 0.90, "filter_eff": 90, "storage_days": 21, "non_potable_lpd": 50},
    "india": {"rainfall_mm": 800, "runoff": 0.80, "filter_eff": 85, "storage_days": 14, "non_potable_lpd": 40},
    "australia": {"rainfall_mm": 550, "runoff": 0.85, "filter_eff": 90, "storage_days": 30, "non_potable_lpd": 45},
}
STANDARDS = {
    "gcc": "BS 8515:2009+A1 / Dubai Green Building Regs / Estidama Pearl",
    "europe": "BS EN 16941-1:2018 / BS 8515 / CIRIA C626",
    "india": "NBC 2016 Part 9 / IS 15797 / CGWB Harvesting Manual",
    "australia": "AS/NZS 3500.1 / NCC Volume One / BASIX / AS 4020",
}
defaults = RAINFALL_DEFAULTS.get(region_code, RAINFALL_DEFAULTS["gcc"])

st.markdown(f"<div class='metric-card'><b style='color:{TEAL_L}'>Standard:</b> <span style='color:{WHITE}'>{STANDARDS.get(region_code, '')}</span></div>", unsafe_allow_html=True)

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    section_title("Site & Catchment")
    roof_area = st.number_input("Roof Catchment Area (m²)", min_value=50.0, max_value=50000.0, value=1000.0, step=50.0)
    annual_rainfall = st.number_input("Annual Rainfall (mm)", min_value=10.0, max_value=3000.0, value=float(defaults["rainfall_mm"]), step=10.0)
    runoff_coeff = st.slider("Runoff Coefficient", 0.50, 1.00, float(defaults["runoff"]), 0.01,
                             help="0.85–0.95 for metal/tile roof; 0.70–0.80 for green/gravel roof")
    filter_eff = st.slider("Filter Efficiency (%)", 70.0, 99.0, float(defaults["filter_eff"]), 1.0,
                           help="Cartridge/membrane filter: 90–95%; basic: 70–80%")

with col2:
    section_title("Demand Inputs")
    num_occ = st.number_input("Number of Occupants", min_value=1, max_value=50000, value=200, step=10)
    non_potable_lpd = st.number_input("Non-Potable Use per Person (L/person/day)", min_value=5.0, max_value=200.0,
                                       value=float(defaults["non_potable_lpd"]), step=5.0,
                                       help="Toilet flushing ~20 L, irrigation, cooling tower make-up")
    storage_days = st.number_input("Storage Period (days)", min_value=1, max_value=90, value=int(defaults["storage_days"]), step=1,
                                    help="Days of non-potable demand to store. GCC: 5d, Europe: 21d, Australia: 30d")

if st.button("Calculate Rainwater Harvesting System", use_container_width=True):
    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "roof_area_m2": roof_area,
        "annual_rainfall_mm": annual_rainfall,
        "runoff_coefficient": runoff_coeff,
        "filter_efficiency_pct": filter_eff,
        "num_occupants": num_occ,
        "non_potable_l_person_day": non_potable_lpd,
        "storage_days": storage_days,
    }
    with st.spinner("Sizing rainwater harvesting system…"):
        res = api_post("/api/plumbing/rainwater-harvesting", payload)

    if res and res.get("status") == "success":
        st.success("Rainwater Harvesting Sizing Complete")
        st.markdown(f"**Standard applied:** {res['standard']}")

        cols = st.columns(4)
        metrics = [
            ("Annual Harvest", f"{res['annual_harvestable_m3']:.1f} m³"),
            ("Monthly Harvest", f"{res['monthly_harvestable_m3']:.1f} m³"),
            ("Annual Demand", f"{res['annual_non_potable_demand_m3']:.1f} m³"),
            ("Demand Offset", f"{res['demand_offset_pct']:.0f}%"),
        ]
        for col, (label, val) in zip(cols, metrics):
            with col:
                st.markdown(metric_card_html(label, val), unsafe_allow_html=True)

        st.markdown("---")
        cols2 = st.columns(4)
        metrics2 = [
            ("Storage Required", f"{res['storage_volume_required_m3']:.1f} m³"),
            ("Selected Tank", f"{res['selected_tank_m3']} m³"),
            ("First-Flush Vol", f"{res['first_flush_volume_l']:.0f} L"),
            ("Peak Flow", f"{res['peak_flow_l_s']:.3f} L/s"),
        ]
        for col, (label, val) in zip(cols2, metrics2):
            with col:
                st.markdown(metric_card_html(label, val), unsafe_allow_html=True)

        section_title("Compliance Checks")
        df_chk = pd.DataFrame(res.get("compliance_checks", []))
        if not df_chk.empty:
            st.dataframe(df_chk, use_container_width=True, hide_index=True)

        section_title("Summary")
        st.markdown(f"<div class='metric-card'><span style='color:{LIGHT_GREY}'>{res['summary']}</span></div>", unsafe_allow_html=True)

        # Export
        export_data = {
            "Region": res["region"], "Sub Region": res["sub_region"], "Standard": res["standard"],
            "Roof Area (m²)": res["roof_area_m2"], "Annual Rainfall (mm)": res["annual_rainfall_mm"],
            "Runoff Coefficient": res["runoff_coefficient"], "Filter Efficiency (%)": res["filter_efficiency_pct"],
            "Annual Harvest (m³)": res["annual_harvestable_m3"],
            "Annual Demand (m³)": res["annual_non_potable_demand_m3"],
            "Demand Offset (%)": res["demand_offset_pct"],
            "Storage Required (m³)": res["storage_volume_required_m3"],
            "Selected Tank (m³)": res["selected_tank_m3"],
            "First-Flush Volume (L)": res["first_flush_volume_l"],
            "Peak Flow (L/s)": res["peak_flow_l_s"],
        }
        buf = io.BytesIO()
        pd.DataFrame([export_data]).T.reset_index().rename(columns={"index": "Parameter", 0: "Value"}).to_excel(
            buf, index=False, sheet_name="Rainwater Harvesting")
        buf.seek(0)
        st.download_button("⬇️ Export Results to Excel", data=buf.getvalue(),
                           file_name=f"Rainwater_Harvesting_{region_code}_{date.today()}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
