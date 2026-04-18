"""Panel Schedule Builder — OpenMEP"""

import streamlit as st
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, LIGHT_GREY,
    page_header, result_card, compliance_badge, section_title, format_summary,
    api_post, region_selector,
    TEAL, TEAL_L
)

st.set_page_config(page_title="Panel Schedule — OpenMEP", page_icon="🗂", layout="wide")
apply_theme_css()

page_header("Panel Schedule Builder", "Distribution board load schedule with cable sizing and phase balancing", "🗂")

with st.sidebar:
    st.markdown(f"<h3 style='color:{TEAL_L}; font-size:0.9rem; text-transform:uppercase; letter-spacing:2px;'>Panel Schedule</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{DARK_GREY}; padding:1rem; border-radius:6px; font-size:0.8rem; color:{WHITE}; line-height:1.8;">
    <b style='color:{TEAL_L}'>IEC 60439</b><br>
    Distribution boards<br>
    Phase balancing &lt; 10%<br><br>
    <b style='color:{TEAL_L}'>BS 7671 Reg 433</b><br>
    Overload protection<br>
    Busbar rating compliance<br><br>
    <b style='color:{TEAL_L}'>DEWA reqs:</b><br>
    100% rated busbars<br>
    20% spare ways
    </div>
    """, unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "panel_circuits" not in st.session_state:
    st.session_state.panel_circuits = [
        {"circuit_no": "C1", "description": "Office Lighting L3-E", "load_kw": 2.5, "power_factor": 0.90, "demand_factor": 1.0, "phases": 1, "circuit_type": "lighting", "cable_type": "XLPE_CU", "installation_method": "C", "cable_length_m": 40.0, "space_reserved": False},
        {"circuit_no": "C2", "description": "Office Lighting L3-W", "load_kw": 2.5, "power_factor": 0.90, "demand_factor": 1.0, "phases": 1, "circuit_type": "lighting", "cable_type": "XLPE_CU", "installation_method": "C", "cable_length_m": 45.0, "space_reserved": False},
        {"circuit_no": "C3", "description": "Office Power Sockets", "load_kw": 6.0, "power_factor": 0.85, "demand_factor": 0.7, "phases": 1, "circuit_type": "power", "cable_type": "XLPE_CU", "installation_method": "C", "cable_length_m": 30.0, "space_reserved": False},
        {"circuit_no": "C4", "description": "AHU-L3-01", "load_kw": 15.0, "power_factor": 0.85, "demand_factor": 1.0, "phases": 3, "circuit_type": "power", "cable_type": "XLPE_CU", "installation_method": "C", "cable_length_m": 25.0, "space_reserved": False},
        {"circuit_no": "C5", "description": "Spare Way", "load_kw": 0.0, "power_factor": 0.85, "demand_factor": 1.0, "phases": 1, "circuit_type": "power", "cable_type": "XLPE_CU", "installation_method": "C", "cable_length_m": 20.0, "space_reserved": True},
    ]

section_title("Panel Information")
col1, col2, col3, col4 = st.columns(4)
with col1:
    panel_name = st.text_input("Panel Name", value="SMDB-L03-A")
with col2:
    panel_ref = st.text_input("Panel Reference", value="P-L3A")
with col3:
    location = st.text_input("Location", value="Level 3 Electrical Room")
with col4:
    fed_from = st.text_input("Fed From", value="MLVDB")

section_title("Regional Standards")
region_code, sub_code = region_selector("panel")
col2, col3 = st.columns(2)
with col2:
    supply_voltage_lv = st.number_input("Supply Voltage (V)", value=400.0, step=5.0)
with col3:
    incoming_cable_size_mm2 = st.number_input("Incomer Cable (mm²)", value=150.0, step=25.0)

section_title("Circuit Schedule")
CABLE_TYPES_LIST = ["XLPE_CU", "PVC_CU", "XLPE_AL"]
METHODS_LIST = ["A1", "A2", "B1", "B2", "C", "D1", "D2", "E", "F"]
CIRCUIT_TYPES_LIST = ["power", "lighting"]

col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([1.5, 3, 1.2, 1, 1, 1, 1.5, 1.5, 1.5])
for c, h in zip([col1,col2,col3,col4,col5,col6,col7,col8,col9], ["No.", "Description", "Load (kW)", "PF", "DF", "Ph", "Cable", "Method", "Len (m)"]):
    c.markdown(f"<span style='color:{LIGHT_GREY}; font-size:0.8rem; font-weight:600;'>{h}</span>", unsafe_allow_html=True)

for i, circ in enumerate(st.session_state.panel_circuits):
    c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([1.5, 3, 1.2, 1, 1, 1, 1.5, 1.5, 1.5])
    with c1:
        circ["circuit_no"] = st.text_input(f"cn_{i}", value=circ["circuit_no"], label_visibility="collapsed", key=f"cn_{i}")
    with c2:
        circ["description"] = st.text_input(f"cd_{i}", value=circ["description"], label_visibility="collapsed", key=f"cd_{i}")
    with c3:
        circ["load_kw"] = st.number_input(f"ckw_{i}", value=float(circ["load_kw"]), min_value=0.0, max_value=2000.0, step=0.5, label_visibility="collapsed", key=f"ckw_{i}")
    with c4:
        circ["power_factor"] = st.number_input(f"cpf_{i}", value=float(circ["power_factor"]), min_value=0.5, max_value=1.0, step=0.05, label_visibility="collapsed", key=f"cpf_{i}")
    with c5:
        circ["demand_factor"] = st.number_input(f"cdf_{i}", value=float(circ["demand_factor"]), min_value=0.1, max_value=1.0, step=0.05, label_visibility="collapsed", key=f"cdf_{i}")
    with c6:
        circ["phases"] = st.selectbox(f"cph_{i}", [1, 3], index=0 if circ["phases"] == 1 else 1, label_visibility="collapsed", key=f"cph_{i}")
    with c7:
        ct_idx = CABLE_TYPES_LIST.index(circ["cable_type"]) if circ["cable_type"] in CABLE_TYPES_LIST else 0
        circ["cable_type"] = st.selectbox(f"cct_{i}", CABLE_TYPES_LIST, index=ct_idx, label_visibility="collapsed", key=f"cct_{i}")
    with c8:
        m_idx = METHODS_LIST.index(circ["installation_method"]) if circ["installation_method"] in METHODS_LIST else 4
        circ["installation_method"] = st.selectbox(f"ccm_{i}", METHODS_LIST, index=m_idx, label_visibility="collapsed", key=f"ccm_{i}")
    with c9:
        circ["cable_length_m"] = st.number_input(f"clen_{i}", value=float(circ["cable_length_m"]), min_value=1.0, max_value=1000.0, step=5.0, label_visibility="collapsed", key=f"clen_{i}")

col1, col2 = st.columns([2, 10])
with col1:
    if st.button("+ Add Circuit"):
        n = len(st.session_state.panel_circuits) + 1
        st.session_state.panel_circuits.append({
            "circuit_no": f"C{n}", "description": "New Circuit",
            "load_kw": 0.0, "power_factor": 0.85, "demand_factor": 1.0, "phases": 1,
            "circuit_type": "power", "cable_type": "XLPE_CU",
            "installation_method": "C", "cable_length_m": 20.0, "space_reserved": False,
        })
        st.rerun()
with col2:
    if st.button("Remove Last") and st.session_state.panel_circuits:
        st.session_state.panel_circuits.pop()
        st.rerun()

if st.button("Generate Panel Schedule", use_container_width=True):
    # API PanelCircuitItem fields: circuit_no, description, load_kw, power_factor,
    # demand_factor, phases, circuit_type, cable_type, installation_method, cable_length_m, space_reserved
    circuits_payload = [
        {
            "circuit_no": c["circuit_no"],
            "description": c["description"],
            "load_kw": c["load_kw"],
            "power_factor": c["power_factor"],
            "demand_factor": c["demand_factor"],
            "phases": c["phases"],
            "circuit_type": c["circuit_type"],
            "cable_type": c["cable_type"],
            "installation_method": c["installation_method"],
            "cable_length_m": c["cable_length_m"],
            "space_reserved": c["space_reserved"],
        }
        for c in st.session_state.panel_circuits
    ]
    # API PanelScheduleRequest fields: region, panel_name, panel_reference, location,
    # fed_from, supply_voltage_lv, incoming_cable_size_mm2, circuits, future_spare_pct
    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "panel_name": panel_name,
        "panel_reference": panel_ref,
        "location": location,
        "fed_from": fed_from,
        "supply_voltage_lv": supply_voltage_lv,
        "incoming_cable_size_mm2": incoming_cable_size_mm2,
        "circuits": circuits_payload,
        "future_spare_pct": 20.0,
    }
    with st.spinner("Generating panel schedule..."):
        result = api_post("/api/electrical/panel-schedule", payload)

    if result:
        section_title("Distribution Board Schedule")
        # API response fields: total_connected_kw, total_demand_kw, incomer_protection_a,
        # incomer_current_a, phase_imbalance_pct, phase_balanced
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Total Connected", f"{result.get('total_connected_kw', 0):.1f}", "kW")
        with col2:
            result_card("Maximum Demand", f"{result.get('total_demand_kw', 0):.1f}", "kW")
        with col3:
            result_card("Incomer Protection", f"{result.get('incomer_protection_a', 0):.0f}", "A")
        with col4:
            result_card("Phase Imbalance", f"{result.get('phase_imbalance_pct', 0):.1f}", "%")

        col1, col2, col3 = st.columns(3)
        with col1:
            result_card("Incomer Current", f"{result.get('incomer_current_a', 0):.1f}", "A")
        with col2:
            result_card("Overall PF", f"{result.get('overall_pf', 0):.3f}", "")
        with col3:
            result_card("Spare Capacity", f"{result.get('spare_pct', 0):.1f}", "%")

        # Phase balancing
        section_title("Phase Loading")
        col1, col2, col3 = st.columns(3)
        with col1:
            result_card("Phase A (R)", f"{result.get('phase_a_kw', 0):.1f}", "kW")
        with col2:
            result_card("Phase B (Y)", f"{result.get('phase_b_kw', 0):.1f}", "kW")
        with col3:
            result_card("Phase C (B)", f"{result.get('phase_c_kw', 0):.1f}", "kW")

        phase_balanced = result.get("phase_balanced", False)
        compliance_badge(phase_balanced, f"Phase imbalance: {result.get('phase_imbalance_pct', 0):.1f}% (limit 10%)")

        # Circuit details table
        if result.get("circuits"):
            section_title("Circuit Details")
            df_data = []
            for c in result["circuits"]:
                df_data.append({
                    "Circuit": c.get("circuit_no", ""),
                    "Description": c.get("description", ""),
                    "Load kW": f"{c.get('load_kw', 0):.1f}",
                    "Demand kW": f"{c.get('demand_kw', 0):.1f}",
                    "Current (A)": f"{c.get('current_a', 0):.1f}",
                    "Cable mm²": str(c.get("cable_size_mm2", "")),
                    "MCB/MCCB (A)": f"{c.get('protection_a', 0):.0f}",
                    "VD %": f"{c.get('vd_percent', 0):.2f}",
                    "Status": "✅" if c.get("compliant", False) else "❌",
                    "Notes": c.get("notes", ""),
                })
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

        overall_compliant = result.get("compliant", False)
        section_title("Overall Compliance")
        compliance_badge(overall_compliant, result.get("standard", ""))

        if result.get("summary"):
            section_title("Calculation Summary")
            format_summary(result.get("summary", ""))

        # ── Export / Add-to-BOQ ───────────────────────────────────────────────
        section_title("Export")
        exp1, exp2, exp3 = st.columns(3)

        with exp1:
            try:
                from report_generator import generate_calculation_pdf
                report_meta = {
                    "project_name": st.session_state.get("project_name", "MEP Project"),
                    "region": region_code, "report_type": "panel_schedule",
                    "discipline": "electrical", "revision": "P01",
                    "date": str(pd.Timestamp.today().date()),
                }
                pdf_bytes = generate_calculation_pdf(report_meta, result)
                if pdf_bytes:
                    st.download_button("⬇️ PDF Report", data=pdf_bytes,
                        file_name=f"PanelSchedule_{panel_ref}_{pd.Timestamp.today().date()}.pdf",
                        mime="application/pdf", use_container_width=True)
            except Exception:
                st.info("PDF export available after report generator is configured.")

        with exp2:
            try:
                import io as _io
                buf = _io.BytesIO()
                export_rows = []
                for c in result.get("circuits", []):
                    export_rows.append({
                        "Circuit": c.get("circuit_no", ""), "Description": c.get("description", ""),
                        "Load kW": c.get("load_kw", 0), "Demand kW": c.get("demand_kw", 0),
                        "Current A": c.get("current_a", 0), "Cable mm²": c.get("cable_size_mm2", ""),
                        "Protection A": c.get("protection_a", 0), "VD %": c.get("vd_percent", 0),
                        "Compliant": c.get("compliant", False),
                    })
                pd.DataFrame(export_rows).to_excel(buf, index=False, sheet_name="Panel_Schedule")
                buf.seek(0)
                st.download_button("⬇️ Excel Schedule", data=buf.getvalue(),
                    file_name=f"PanelSchedule_{panel_ref}_{pd.Timestamp.today().date()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            except ImportError:
                st.info("Install openpyxl for Excel export.")

        with exp3:
            if st.button("📋 Add Panel to BOQ", use_container_width=True):
                boq_item = {
                    "description": f"Distribution Board — {panel_name} ({panel_ref})",
                    "total_demand_kw": result.get("total_demand_kw", 0),
                    "incomer_a": result.get("incomer_protection_a", 0),
                }
                if "boq_items" not in st.session_state:
                    st.session_state.boq_items = []
                st.session_state.boq_items.append(boq_item)
                st.success(f"Panel {panel_ref} added to BOQ session ({len(st.session_state.boq_items)} items total).")
