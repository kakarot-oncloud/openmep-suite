"""Plumbing Tank Sizing — OpenMEP"""

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

st.set_page_config(page_title="Plumbing Tank Sizing — OpenMEP", page_icon="🏊", layout="wide")
apply_theme_css()

page_header("Plumbing Tank Sizing", "Cold water, fire reserve, and combined storage tank calculation", "🏊")

region_code, sub_code = region_selector("pts")

STANDARDS = {
    "gcc": "BS EN 806-2 / Dubai Municipality / NFPA 22 / CIBSE Guide G",
    "europe": "BS EN 806-2:2005 / BS 6700 / WRAS / BS EN 12845",
    "india": "IS 1172:1993 / NBC 2016 Part 9 / IS 9668 / CPWD Plumbing Manual",
    "australia": "AS/NZS 3500.1:2018 / NCC Volume One / AS 2118.1",
}
PER_CAPITA_L = {"gcc": 250, "europe": 150, "india": 135, "australia": 180}
STORAGE_HOURS_MIN = {"gcc": 24, "europe": 12, "india": 24, "australia": 12}

std = STANDARDS.get(region_code, STANDARDS["gcc"])
pc_default = PER_CAPITA_L.get(region_code, 200)
storage_hrs_min = STORAGE_HOURS_MIN.get(region_code, 24)

st.markdown(f"<div class='metric-card'><b style='color:{TEAL_L}'>Standard:</b> <span style='color:{WHITE}'>{std}</span></div>", unsafe_allow_html=True)

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    section_title("Tank Type & Occupancy")
    tank_type = st.selectbox("Tank Type", ["cold_water", "fire_reserve", "combined"],
                              format_func=lambda x: {"cold_water": "Cold Water Storage Tank",
                                                      "fire_reserve": "Fire Reserve Tank",
                                                      "combined": "Combined CW + Fire Reserve"}[x])
    tank_material = st.selectbox("Tank Material", ["GRP", "Stainless Steel", "MDPE", "Concrete"],
                                  help="GRP: Glass Reinforced Plastic (most common). WRAS-approved required in UK.")
    num_occ = st.number_input("Number of Occupants / Persons", min_value=0, max_value=100000, value=500, step=10)
    dwelling_units = st.number_input("Dwelling Units (residential, if applicable)", min_value=0, max_value=5000, value=0, step=5,
                                      help="BS EN 806 allocates ~450 L/dwelling/day for residential buildings")
with col2:
    section_title("Demand & Storage Parameters")
    daily_demand_l = st.number_input(
        "Daily Demand per Person (L/person/day)",
        min_value=50.0, max_value=600.0, value=float(pc_default), step=10.0,
        help=f"Recommended: GCC {PER_CAPITA_L['gcc']} L | Europe {PER_CAPITA_L['europe']} L | India {PER_CAPITA_L['india']} L | AUS {PER_CAPITA_L['australia']} L"
    )
    storage_hours = st.number_input(
        "Storage Duration (hours)",
        min_value=4.0, max_value=48.0, value=float(storage_hrs_min), step=1.0,
        help=f"Minimum recommended: {storage_hrs_min} h for {region_code.upper()}"
    )
    fire_reserve_l = 0.0
    if tank_type in ("fire_reserve", "combined"):
        fire_reserve_l = st.number_input("Fire Reserve Volume (L)", min_value=0.0, max_value=500000.0,
                                          value=50000.0, step=1000.0,
                                          help="From fire pump/sprinkler calculation. NFPA 22 / BS EN 12845 / AS 2118")
    operating_pressure = st.number_input("Operating Pressure (bar)", min_value=0.5, max_value=10.0, value=3.0, step=0.5)

if st.button("Calculate Plumbing Tank Size", use_container_width=True):
    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "tank_type": tank_type,
        "num_occupants": num_occ,
        "dwelling_units": dwelling_units,
        "daily_demand_l_person": daily_demand_l,
        "storage_hours": storage_hours,
        "fire_reserve_l": fire_reserve_l,
        "tank_material": tank_material,
        "operating_pressure_bar": operating_pressure,
    }
    with st.spinner("Sizing plumbing storage tank…"):
        res = api_post("/api/plumbing/plumbing-tank-sizing", payload)

    if res and res.get("status") == "success":
        st.success("Plumbing Tank Sizing Complete")
        st.markdown(f"**Standard applied:** {res['standard']}")

        cols = st.columns(4)
        metrics = [
            ("Daily Demand", f"{res['total_daily_demand_l']:,.0f} L"),
            ("Cold Storage", f"{res['cold_storage_l']:,.0f} L"),
            ("Fire Reserve", f"{res['fire_reserve_l']:,.0f} L"),
            ("Total Required", f"{res['total_volume_required_l']:,.0f} L"),
        ]
        for col, (label, val) in zip(cols, metrics):
            with col:
                st.markdown(metric_card_html(label, val), unsafe_allow_html=True)

        st.markdown("---")
        cols2 = st.columns(4)
        metrics2 = [
            ("Selected Tank", f"{res['selected_tank_m3']:.1f} m³ ({res['selected_tank_l']:,} L)"),
            ("Peak Flow", f"{res['peak_flow_l_min']:.1f} L/min"),
            ("Inlet Flow", f"{res['inlet_flow_l_s']:.3f} L/s"),
            ("Overflow Pipe", f"DN{res['overflow_pipe_dn_mm']}"),
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
            "Tank Type": res["tank_type"], "Tank Material": res["tank_material"],
            "Occupants": res["num_occupants"],
            "Total Daily Demand (L)": res["total_daily_demand_l"],
            "Cold Storage Required (L)": res["cold_storage_l"],
            "Fire Reserve (L)": res["fire_reserve_l"],
            "Total Volume Required (L)": res["total_volume_required_l"],
            "Gross Tank Volume (L)": res["gross_tank_volume_l"],
            "Selected Tank (L)": res["selected_tank_l"],
            "Selected Tank (m³)": res["selected_tank_m3"],
            "Peak Flow (L/min)": res["peak_flow_l_min"],
            "Inlet Flow (L/s)": res["inlet_flow_l_s"],
            "Overflow Pipe (DN mm)": res["overflow_pipe_dn_mm"],
        }
        buf = io.BytesIO()
        pd.DataFrame([export_data]).T.reset_index().rename(columns={"index": "Parameter", 0: "Value"}).to_excel(
            buf, index=False, sheet_name="Tank Sizing")
        buf.seek(0)
        st.download_button("⬇️ Export Results to Excel", data=buf.getvalue(),
                           file_name=f"Plumbing_Tank_Sizing_{region_code}_{date.today()}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
