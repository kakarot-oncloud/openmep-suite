import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    TEAL_L,
    api_post,
    api_post_bytes,
    apply_theme_css,
    page_header,
    region_selector,
    section_title,
)

st.set_page_config(page_title="Cable Schedule (Batch) — OpenMEP", page_icon="📋", layout="wide")
apply_theme_css()

page_header("Cable Schedule — Batch Sizing",
            "Size every circuit at once against a shared project design basis, then export to Excel/CSV", "📋")

# ── Design basis (shared assumptions inherited by every circuit) ───────────────
section_title("Design Basis")
region, sub_region = region_selector("batch")

c1, c2, c3, c4 = st.columns(4)
with c1:
    ambient = st.number_input("Ambient °C (blank = region default)", value=45.0, step=1.0)
with c2:
    pf = st.number_input("Power factor", min_value=0.10, max_value=1.0, value=0.85, step=0.01)
with c3:
    cable_type = st.selectbox("Default cable type", ["XLPE_CU", "PVC_CU", "XLPE_AL"], index=0)
with c4:
    method = st.selectbox("Default install method", ["C", "E", "B", "D", "F", "A1", "A2"], index=0)

design_basis = {
    "region": region,
    "sub_region": sub_region,
    "ambient_temp_c": ambient,
    "power_factor": pf,
    "default_cable_type": cable_type,
    "default_installation_method": method,
}

# ── Circuit schedule ──────────────────────────────────────────────────────────
section_title("Circuits")
st.caption("Add one row per circuit. Blank cable type / method / PF inherit the design basis above.")

default_rows = pd.DataFrame([
    {"circuit_ref": "C1", "description": "AHU-1", "load_kw": 45.0, "phases": 3,
     "cable_length_m": 80.0, "circuit_type": "power"},
    {"circuit_ref": "C2", "description": "Lighting DB", "load_kw": 6.0, "phases": 1,
     "cable_length_m": 40.0, "circuit_type": "lighting"},
])

edited = st.data_editor(
    default_rows,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "load_kw": st.column_config.NumberColumn("Load (kW)", min_value=0.0, step=1.0),
        "phases": st.column_config.SelectboxColumn("Phases", options=[1, 3]),
        "cable_length_m": st.column_config.NumberColumn("Length (m)", min_value=1.0, step=5.0),
        "circuit_type": st.column_config.SelectboxColumn("Type", options=["power", "lighting"]),
    },
    key="batch_editor",
)

if st.button("⚡ Size all circuits", type="primary", use_container_width=True):
    circuits = []
    for _, row in edited.iterrows():
        try:
            load = float(row.get("load_kw") or 0)
            length = float(row.get("cable_length_m") or 0)
        except (TypeError, ValueError):
            continue
        if load <= 0 or length <= 0:
            continue
        circuits.append({
            "circuit_ref": str(row.get("circuit_ref") or ""),
            "description": str(row.get("description") or ""),
            "load_kw": load,
            "phases": int(row.get("phases") or 3),
            "cable_length_m": length,
            "circuit_type": str(row.get("circuit_type") or "power"),
        })

    if not circuits:
        st.warning("Add at least one circuit with a positive load and length.")
    else:
        result = api_post("/api/electrical/cable-schedule",
                          {"design_basis": design_basis, "circuits": circuits})
        if result:
            st.session_state["batch_result"] = result

# ── Results ───────────────────────────────────────────────────────────────────
result = st.session_state.get("batch_result")
if result:
    section_title("Sized Schedule")
    m1, m2, m3 = st.columns(3)
    m1.metric("Circuits", result["circuit_count"])
    m2.metric("Non-compliant", result["non_compliant_count"])
    m3.metric("Overall", "✅ Compliant" if result["all_compliant"] else "❌ Review")

    table = result["table"]
    df = pd.DataFrame(table["rows"], columns=table["columns"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    export_payload = {"title": "Cable_Schedule", "columns": table["columns"], "rows": table["rows"]}
    d1, d2 = st.columns(2)
    with d1:
        xlsx = api_post_bytes("/api/exports/table.xlsx", export_payload)
        if xlsx:
            st.download_button("⬇️ Download Excel (.xlsx)", xlsx, file_name="cable_schedule.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True)
    with d2:
        csv = api_post_bytes("/api/exports/table.csv", export_payload)
        if csv:
            st.download_button("⬇️ Download CSV", csv, file_name="cable_schedule.csv",
                               mime="text/csv", use_container_width=True)

    st.markdown(f"<p style='color:{TEAL_L};font-size:0.8rem;'>Standard: {result['circuits'][0]['standard']}</p>",
                unsafe_allow_html=True)
