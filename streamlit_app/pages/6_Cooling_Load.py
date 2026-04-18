import streamlit as st
import sys
import os
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, page_header, result_card, section_title, format_summary,
    api_post, region_selector,
    TEAL, TEAL_L
)

st.set_page_config(page_title="Cooling Load — OpenMEP", page_icon="❄️", layout="wide")
apply_theme_css()

page_header("Cooling Load", "ASHRAE heat balance method — sensible + latent + outside air", "❄️")

ZONE_TYPES = {
    "Office — Open Plan": "office",
    "Meeting Room": "meeting_room",
    "Server Room / Data Centre": "data_centre",
    "Retail": "retail",
    "Restaurant / F&B": "restaurant",
    "Gym / Fitness": "gym",
    "Hospital Ward": "hospital_ward",
    "Classroom": "classroom",
    "Lobby / Atrium": "lobby",
    "Warehouse": "warehouse",
}

EPD_DEFAULTS = {
    "office": 20, "meeting_room": 10, "data_centre": 500, "retail": 15,
    "restaurant": 30, "gym": 10, "hospital_ward": 20, "classroom": 10,
    "lobby": 8, "warehouse": 5,
}

with st.form("cooling_form"):
    section_title("Regional Standards & Zone Type")
    region_code, sub_code = region_selector("cl")
    col_z = st.columns(1)[0]
    with col_z:
        zone_type_label = st.selectbox("Zone Type", list(ZONE_TYPES.keys()))
        zone_type = ZONE_TYPES[zone_type_label]

    section_title("Space Geometry")
    col1, col2, col3 = st.columns(3)
    with col1:
        zone_name = st.text_input("Zone Name", value="Office Level 3")
    with col2:
        floor_area = st.number_input("Floor Area (m²)", min_value=5.0, max_value=10000.0, value=500.0, step=10.0)
    with col3:
        height_m = st.number_input("Ceiling Height (m)", min_value=2.0, max_value=15.0, value=3.0, step=0.1)

    section_title("Glazing & Envelope")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        glass_area = st.number_input("Glazing Area (m²)", min_value=0.0, max_value=2000.0, value=60.0, step=5.0)
    with col2:
        glass_u_value = st.number_input("Glass U-Value (W/m²K)", min_value=0.5, max_value=6.0, value=2.8, step=0.1)
    with col3:
        glass_shgc = st.number_input("SHGC", min_value=0.1, max_value=1.0, value=0.4, step=0.05)
    with col4:
        glass_orientation = st.selectbox("Glazing Orientation", ["N", "NE", "E", "SE", "S", "SW", "W", "NW"], index=6)

    col1, col2, col3 = st.columns(3)
    with col1:
        wall_area = st.number_input("Wall Area (m²)", min_value=0.0, max_value=5000.0, value=120.0, step=10.0)
    with col2:
        wall_u_value = st.number_input("Wall U-Value (W/m²K)", min_value=0.1, max_value=3.0, value=0.45, step=0.05)
    with col3:
        cop = st.number_input("System COP", min_value=1.5, max_value=6.0, value=3.5, step=0.1,
                               help="Coefficient of Performance of the cooling plant")

    section_title("Internal Heat Gains")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        occupancy = st.number_input("Occupancy (persons)", min_value=0, max_value=5000, value=50)
    with col2:
        lighting_w_m2 = st.number_input("Lighting Load (W/m²)", min_value=0.0, max_value=50.0, value=12.0, step=0.5)
    with col3:
        equipment_w_m2 = st.number_input("Equipment Load (W/m²)", min_value=0.0, max_value=500.0,
                                          value=float(EPD_DEFAULTS.get(zone_type, 20)), step=1.0)
    with col4:
        fresh_air_lps = st.number_input("Fresh Air (L/s/person)", min_value=5.0, max_value=25.0, value=10.0, step=0.5)

    submitted = st.form_submit_button("Calculate Cooling Load", use_container_width=True)

if submitted:
    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "zone_name": zone_name,
        "zone_type": zone_type,
        "floor_area_m2": floor_area,
        "height_m": height_m,
        "glass_area_m2": glass_area,
        "glass_u_value": glass_u_value,
        "glass_shgc": glass_shgc,
        "glass_orientation": glass_orientation,
        "wall_area_m2": wall_area,
        "wall_u_value": wall_u_value,
        "occupancy": int(occupancy),
        "lighting_w_m2": lighting_w_m2,
        "equipment_w_m2": equipment_w_m2,
        "fresh_air_l_s_person": fresh_air_lps,
        "cop": cop,
        "safety_factor": 1.10,
    }
    with st.spinner("Calculating cooling load..."):
        result = api_post("/api/mechanical/cooling-load", payload)

    if result and result.get("status") == "success":
        section_title("Cooling Load Results")

        # Region-driven primary unit: TR for GCC/India (chiller plant culture); kW for Europe/Australia
        use_tr_primary = region_code in ("gcc", "india")
        total_kw = result.get("total_cooling_kw", 0)
        total_tr = result.get("total_cooling_tr", 0)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if use_tr_primary:
                result_card("Total Cooling (Primary)", f"{total_tr:.1f}", "TR")
            else:
                result_card("Total Cooling (Primary)", f"{total_kw:.1f}", "kW")
        with col2:
            if use_tr_primary:
                result_card("Total Cooling (alt.)", f"{total_kw:.1f}", "kW")
            else:
                result_card("Total Cooling (alt.)", f"{total_tr:.1f}", "TR")
        with col3:
            result_card("Sensible Load", f"{result.get('total_sensible_w', 0)/1000:.1f}", "kW")
        with col4:
            result_card("Latent Load", f"{result.get('total_latent_w', 0)/1000:.1f}", "kW")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Cooling Density", f"{result.get('cooling_w_per_m2', 0):.0f}", "W/m²")
        with col2:
            result_card("Supply Airflow", f"{result.get('supply_airflow_l_s', 0):.0f}", "L/s")
        with col3:
            result_card("Air Changes/hr", f"{result.get('room_air_changes_per_hour', 0):.1f}", "ACH")
        with col4:
            result_card("Chiller Power", f"{result.get('chiller_power_kw', 0):.1f}", "kW")

        section_title("Load Breakdown")
        breakdown = result.get("load_breakdown_w", {})
        if breakdown:
            labels = [k.replace("_", " ").title() for k, v in breakdown.items() if v > 0]
            values = [v for v in breakdown.values() if v > 0]
            colors = [TEAL, TEAL_L, "#00729E", "#005F85", "#00B4D8", "#48CAE4", "#90E0EF"]
            fig = go.Figure(go.Pie(
                labels=labels, values=values,
                marker_colors=colors[:len(labels)],
                hole=0.4,
                textfont_color=WHITE,
            ))
            fig.update_layout(
                plot_bgcolor=BLACK, paper_bgcolor=DARK_GREY,
                font=dict(color=WHITE), height=350,
                legend=dict(font=dict(color=WHITE)),
                margin=dict(l=0, r=0, t=20, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)

        section_title("Engineering Summary")
        format_summary(result.get("summary", ""))


        # ── Export / Add-to-BOQ ───────────────────────────────────────────────
        from utils import section_title as _st
        _st('Export')
        import io as _io
        import pandas as _pd
        c1, c2, c3 = st.columns(3)
        with c1:
            try:
                from report_generator import generate_calculation_pdf as _gp
                _m = {'project_name': st.session_state.get('project_name', 'MEP Project'),
                      'region': result.get('region', 'gcc'), 'report_type': 'cooling_load',
                      'discipline': 'hvac', 'revision': 'P01',
                      'date': str(_pd.Timestamp.today().date())}
                _pdf = _gp(_m, result)
                if _pdf:
                    st.download_button('⬇️ PDF Report', data=_pdf,
                        file_name=f'OpenMEP_cooling_load_{_pd.Timestamp.today().date()}.pdf',
                        mime='application/pdf', use_container_width=True)
            except Exception:
                st.info('PDF: install reportlab.')
        with c2:
            try:
                _buf = _io.BytesIO()
                _rows = [{k: v for k, v in result.items() if isinstance(v, (int, float, str))}]
                _pd.DataFrame(_rows).to_excel(_buf, index=False, sheet_name='cooling_load')
                _buf.seek(0)
                st.download_button('⬇️ Excel Results', data=_buf.getvalue(),
                    file_name=f'OpenMEP_cooling_load_{_pd.Timestamp.today().date()}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True)
            except ImportError:
                st.info('Install openpyxl for Excel export.')
        with c3:
            if st.button('📋 Add Cooling to BOQ', use_container_width=True):
                if 'boq_items' not in st.session_state:
                    st.session_state.boq_items = []
                st.session_state.boq_items.append({
                    'type': 'cooling_load',
                    'description': 'Cooling Load: ' + str(result.get('total_cooling_kw', '—')),
                    'value': result.get('total_cooling_kw'),
                })
                st.success(f'Cooling Load added to BOQ session ({len(st.session_state.boq_items)} items).')
