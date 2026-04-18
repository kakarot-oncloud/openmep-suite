"""PDF Report Generator — OpenMEP"""

import streamlit as st
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, page_header, result_card, section_title, compliance_badge, format_summary,
    api_post, region_selector,
    TEAL, TEAL_L
)

st.set_page_config(page_title="PDF Reports — OpenMEP", page_icon="📄", layout="wide")
apply_theme_css()

page_header("PDF Report Generator", "Generate professional engineering calculation reports with regional letterhead and compliance summary", "📄")

with st.sidebar:
    st.markdown(f"<h3 style='color:{TEAL_L}; font-size:0.9rem; text-transform:uppercase; letter-spacing:2px;'>Report Templates</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{DARK_GREY}; padding:1rem; border-radius:6px; font-size:0.8rem; color:{WHITE}; line-height:1.8;">
    All reports include:<br>
    • Letterhead (region-specific)<br>
    • Project / client info<br>
    • Design basis &amp; standards<br>
    • Input parameters table<br>
    • Calculation methodology<br>
    • Results with compliance<br>
    • Engineer's sign-off block<br>
    • Revision history table
    </div>
    """, unsafe_allow_html=True)

# Report-type → API endpoint + default payload mapping
REPORT_CONFIGS = {
    "cable_sizing": {
        "label": "Cable Sizing (Electrical)",
        "endpoint": "/api/electrical/cable-sizing",
        "discipline": "electrical",
        "inputs": ["load_kw", "cable_length", "voltage_v", "pf"],
    },
    "voltage_drop": {
        "label": "Voltage Drop (Electrical)",
        "endpoint": "/api/electrical/voltage-drop",
        "discipline": "electrical",
        "inputs": ["load_kw", "cable_length", "voltage_v", "pf"],
    },
    "maximum_demand": {
        "label": "Maximum Demand (Electrical)",
        "endpoint": "/api/electrical/maximum-demand",
        "discipline": "electrical",
        "inputs": ["load_kw", "voltage_v", "pf"],
    },
    "cooling_load": {
        "label": "Cooling Load (HVAC)",
        "endpoint": "/api/mechanical/cooling-load",
        "discipline": "hvac",
        "inputs": ["floor_area_m2", "glass_area_m2"],
    },
    "heating_load": {
        "label": "Heating Load (HVAC)",
        "endpoint": "/api/mechanical/heating-load",
        "discipline": "hvac",
        "inputs": ["floor_area_m2"],
    },
    "ventilation": {
        "label": "Ventilation (HVAC)",
        "endpoint": "/api/mechanical/ventilation",
        "discipline": "hvac",
        "inputs": ["floor_area_m2"],
    },
    "pipe_sizing": {
        "label": "Pipe Sizing (Plumbing)",
        "endpoint": "/api/plumbing/pipe-sizing",
        "discipline": "plumbing",
        "inputs": ["load_kw"],
    },
    "hot_water": {
        "label": "Hot Water System (Plumbing)",
        "endpoint": "/api/plumbing/hot-water-system",
        "discipline": "plumbing",
        "inputs": ["load_kw"],
    },
    "sprinkler": {
        "label": "Sprinkler Design (Fire)",
        "endpoint": "/api/fire/sprinkler-design",
        "discipline": "fire",
        "inputs": ["floor_area_m2"],
    },
    "fire_pump": {
        "label": "Fire Pump Sizing (Fire)",
        "endpoint": "/api/fire/fire-pump",
        "discipline": "fire",
        "inputs": ["load_kw"],
    },
}

section_title("Report Configuration")
region_code, sub_code = region_selector("rpt")

col2, col3 = st.columns(2)
with col2:
    report_type = st.selectbox("Report Type", list(REPORT_CONFIGS.keys()),
                                format_func=lambda x: REPORT_CONFIGS[x]["label"])
with col3:
    report_format = st.selectbox("Output Format", ["pdf", "html"])

config = REPORT_CONFIGS[report_type]
discipline = config["discipline"]

section_title("Project Information")
col1, col2, col3 = st.columns(3)
with col1:
    project_name = st.text_input("Project Name", value=st.session_state.get("project_name", "MEP Project"))
    client_name = st.text_input("Client Name", value=st.session_state.get("client_name", ""))
with col2:
    engineer_name = st.text_input("Prepared By", value=st.session_state.get("engineer_name", ""))
    checked_by = st.text_input("Checked By", value="")
with col3:
    project_number = st.text_input("Project Number", value=st.session_state.get("project_number", ""))
    revision = st.text_input("Revision", value="P01")

section_title(f"Calculation Inputs — {config['label']}")

# Show relevant inputs based on selected report type
col1, col2, col3, col4 = st.columns(4)
with col1:
    load_kw = st.number_input("Load (kW)", value=45.0, step=0.5)
    floor_area_m2 = st.number_input("Floor Area (m²)", value=500.0, step=10.0)
with col2:
    cable_length = st.number_input("Cable / Pipe Length (m)", value=80.0, step=5.0)
    glass_area_m2 = st.number_input("Glass / Glazing Area (m²)", value=100.0, step=5.0)
with col3:
    voltage_v = st.number_input("Voltage (V)", value=415.0, step=5.0)
    num_occupants = st.number_input("Occupants / Persons", value=100, step=10)
with col4:
    pf = st.number_input("Power Factor", value=0.85, step=0.01)
    ambient_temp = st.number_input("Ambient / Outdoor Temp (°C)", value=40.0 if region_code in ("gcc", "india") else 30.0, step=1.0)

if st.button("Generate & Download PDF Report", use_container_width=True):
    # Build calculation payload specific to the selected report type
    if report_type == "cable_sizing":
        calc_payload = {
            "region": region_code, "sub_region": sub_code,
            "load_kw": load_kw, "power_factor": pf,
            "phases": "3", "voltage_v": voltage_v,
            "cable_type": "XLPE_CU", "installation_method": "C",
            "cable_length_m": cable_length, "circuit_type": "power",
            "ambient_temp_c": ambient_temp,
        }
    elif report_type == "voltage_drop":
        calc_payload = {
            "region": region_code, "sub_region": sub_code,
            "load_kw": load_kw, "power_factor": pf,
            "voltage_v": voltage_v, "cable_length_m": cable_length,
            "cable_size_mm2": 35.0, "cable_type": "XLPE_CU",
            "phases": "3", "circuit_type": "power",
        }
    elif report_type == "maximum_demand":
        calc_payload = {
            "region": region_code, "sub_region": sub_code,
            "loads": [
                {"load_name": "HVAC", "kva": load_kw / pf, "power_factor": pf, "demand_factor": 0.8, "quantity": 1},
                {"load_name": "Lighting", "kva": load_kw * 0.2 / pf, "power_factor": 0.95, "demand_factor": 0.9, "quantity": 1},
            ],
            "voltage_v": voltage_v, "phases": "3",
        }
    elif report_type == "cooling_load":
        calc_payload = {
            "region": region_code, "sub_region": sub_code,
            "zone_name": "Typical Zone", "zone_type": "office",
            "floor_area_m2": floor_area_m2, "height_m": 3.0,
            "glass_area_m2": glass_area_m2, "glass_u_value": 2.0, "glass_shgc": 0.4,
            "glass_orientation": "south", "wall_area_m2": floor_area_m2 * 0.3,
            "wall_u_value": 0.5, "occupancy": num_occupants,
            "lighting_w_m2": 12.0, "equipment_w_m2": 20.0,
            "fresh_air_l_s_person": 10.0, "cop": 3.5, "safety_factor": 1.1,
        }
    elif report_type == "heating_load":
        calc_payload = {
            "region": region_code,
            "zone_name": "Typical Zone", "zone_type": "office",
            "floor_area_m2": floor_area_m2, "height_m": 3.0,
            "wall_area_m2": floor_area_m2 * 0.4, "wall_u_value": 0.30,
            "roof_area_m2": floor_area_m2, "roof_u_value": 0.20,
            "window_area_m2": glass_area_m2, "window_u_value": 1.4,
            "floor_area_m2_uninsulated": 0.0, "floor_u_value": 0.25,
            "infiltration_ach": 0.5,
            "outdoor_design_temp_c": -5.0,
            "indoor_design_temp_c": 21.0,
            "safety_factor": 1.15,
        }
    elif report_type == "ventilation":
        calc_payload = {
            "region": region_code, "sub_region": sub_code,
            "zone_name": "Typical Zone", "zone_type": "office",
            "floor_area_m2": floor_area_m2, "height_m": 3.0,
            "occupancy": num_occupants, "fresh_air_l_s_person": 10.0,
            "min_ach": 6.0, "supply_temp_offset_k": 8.0,
        }
    elif report_type == "pipe_sizing":
        calc_payload = {
            "region": region_code, "sub_region": sub_code,
            "system": "cold_water", "flow_units": 20.0,
            "pipe_material": "copper", "max_velocity_m_s": 2.0,
        }
    elif report_type == "hot_water":
        calc_payload = {
            "region": region_code, "sub_region": sub_code,
            "system_type": "central_storage", "num_occupants": num_occupants,
            "hot_water_l_person_day": 50.0, "storage_temp_c": 60.0,
            "delivery_temp_c": 55.0, "inlet_water_temp_c": 15.0,
            "recovery_time_hr": 2.0, "standby_loss_pct": 10.0,
            "legionella_pasteurisation": True,
        }
    elif report_type == "sprinkler":
        calc_payload = {
            "region": region_code, "sub_region": sub_code,
            "hazard_class": "ordinary_group_1", "coverage_area_m2": floor_area_m2,
            "k_factor": 80.0, "design_density_mm_min": 5.0,
            "design_area_m2": 72.0, "safety_factor": 1.05,
        }
    elif report_type == "fire_pump":
        calc_payload = {
            "region": region_code,
            "system_type": "wet_riser",
            "sprinkler_demand_l_min": 2000.0,
            "hose_reel_demand_l_min": 600.0,
            "hydrant_demand_l_min": 0.0,
            "static_pressure_required_bar": 6.5,
            "friction_loss_bar": 1.5,
            "elevation_loss_bar": 2.0,
            "pump_efficiency": 0.72,
            "motor_efficiency": 0.90,
            "duty_standby_jockey": True,
        }
    else:
        calc_payload = {
            "region": region_code, "sub_region": sub_code,
            "load_kw": load_kw, "power_factor": pf,
            "phases": "3", "voltage_v": voltage_v,
            "cable_type": "XLPE_CU", "installation_method": "C",
            "cable_length_m": cable_length, "circuit_type": "power",
            "ambient_temp_c": ambient_temp,
        }

    with st.spinner(f"Running {config['label']} calculation..."):
        calc_result = api_post(config["endpoint"], calc_payload)

    if calc_result:
        section_title("Calculation Preview")
        # Display key results in a region-appropriate way
        display_items = {k: v for k, v in calc_result.items()
                         if k not in ("status", "summary", "notes", "checks", "standard")
                         and not isinstance(v, (dict, list))}
        metric_pairs = list(display_items.items())[:8]
        if metric_pairs:
            cols = st.columns(min(4, len(metric_pairs)))
            for col, (k, v) in zip(cols, metric_pairs[:4]):
                with col:
                    result_card(k.replace("_", " ").title(), str(v))
            if len(metric_pairs) > 4:
                cols2 = st.columns(min(4, len(metric_pairs) - 4))
                for col, (k, v) in zip(cols2, metric_pairs[4:8]):
                    with col:
                        result_card(k.replace("_", " ").title(), str(v))

        compliant = calc_result.get("overall_compliant", calc_result.get("compliant", True))
        standard = calc_result.get("standard", "")
        compliance_badge(bool(compliant), standard)

        if calc_result.get("summary"):
            format_summary(calc_result["summary"])

        # Build API report payload
        report_payload = {
            "metadata": {
                "project_name": project_name,
                "project_number": project_number,
                "client": client_name,
                "location": "",
                "prepared_by": engineer_name,
                "checked_by": checked_by,
                "approved_by": "",
                "revision": revision,
                "date": str(date.today()),
                "region": region_code,
                "sub_region": sub_code,
                "discipline": discipline,
                "report_type": report_type,
            },
            "calculations": [
                {
                    "section": config["label"],
                    "reference": f"{discipline[:2].upper()}-{project_number or 'P001'}-01",
                    "description": f"{config['label']} — {region_code.upper()} / {sub_code.upper()}",
                    "result_summary": {str(k): str(v) for k, v in display_items.items()},
                    "standard": standard,
                    "compliant": bool(compliant),
                    "notes": calc_result.get("notes", ""),
                }
            ],
            "include_appendix": True,
        }

        with st.spinner("Generating PDF..."):
            try:
                from report_generator import generate_calculation_pdf
                pdf_context = {
                    "project_name": project_name, "client_name": client_name,
                    "engineer_name": engineer_name, "checked_by": checked_by,
                    "project_number": project_number, "revision": revision,
                    "date": str(date.today()), "region": region_code,
                    "sub_region": sub_code, "discipline": discipline,
                    "report_type": report_type,
                }
                pdf_bytes = generate_calculation_pdf(pdf_context, calc_result)
                if pdf_bytes:
                    st.download_button(
                        "⬇️ Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"OpenMEP_{report_type}_{region_code.upper()}_{project_number or 'P001'}_{revision}_{date.today()}.pdf",
                        mime="application/pdf",
                    )
                    st.success(f"PDF report generated: {config['label']} | Region: {region_code.upper()} | {standard}")
            except Exception as ex:
                st.warning(f"PDF generation via report_generator: {ex}")

        with st.spinner("Registering calculation report with API..."):
            api_report = api_post("/api/reports/calculation-report", report_payload)

        if api_report:
            section_title("Report Index")
            st.markdown(f"""
            <div style="background:{DARK_GREY}; padding:1rem; border-radius:6px; color:{WHITE}; font-size:0.9rem;">
                <b>Report Reference:</b> {api_report.get('report_reference', '—')}<br>
                <b>Report Type:</b> {report_type}<br>
                <b>Calculations:</b> {api_report.get('total_calculations', 0)} total | {api_report.get('calculations_passed', 0)} passed<br>
                <b>Primary Standard:</b> {api_report.get('primary_standard', '—')}<br>
                <b>Prepared By:</b> {api_report.get('metadata', {}).get('prepared_by', '—')}<br>
                <b>Date:</b> {api_report.get('metadata', {}).get('date', '—')}
            </div>
            """, unsafe_allow_html=True)
