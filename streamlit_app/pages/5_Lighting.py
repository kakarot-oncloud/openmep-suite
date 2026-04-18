import streamlit as st
import sys
import os
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, MID_GREY, page_header, result_card, compliance_badge, section_title, format_summary,
    api_post, region_selector,
    TEAL, TEAL_L
)

st.set_page_config(page_title="Lighting Design — OpenMEP", page_icon="💡", layout="wide")
apply_theme_css()

page_header("Lighting Design", "Lumen method — maintained illuminance, LPD, uniformity ratio per EN 12464/IS 3646/AS 1680", "💡")

SPACE_TYPES = {
    "office": 500, "meeting_room": 300, "corridor": 100,
    "lobby": 200, "retail": 500, "warehouse": 200,
    "car_park": 75, "stairwell": 150, "plant_room": 200,
    "data_centre": 500, "classroom": 500, "hospital_ward": 300,
    "laboratory": 750, "kitchen": 500,
}

SPACE_TYPE_LABELS = {
    "Office — Open Plan": "office",
    "Meeting Room": "meeting_room",
    "Corridor / Circulation": "corridor",
    "Lobby / Reception": "lobby",
    "Retail / Shop": "retail",
    "Warehouse": "warehouse",
    "Car Park (Indoor)": "car_park",
    "Stairwell": "stairwell",
    "Plant Room": "plant_room",
    "Data Centre": "data_centre",
    "Classroom": "classroom",
    "Hospital Ward": "hospital_ward",
    "Laboratory": "laboratory",
    "Kitchen": "kitchen",
}

with st.form("lighting_form"):
    section_title("Regional Standards")
    region_code, sub_code = region_selector("lt")

    section_title("Space Parameters")
    col1, col2 = st.columns(2)
    with col1:
        space_type_label = st.selectbox("Space Type", list(SPACE_TYPE_LABELS.keys()))
        space_type = SPACE_TYPE_LABELS[space_type_label]
        default_lux = SPACE_TYPES.get(space_type, 300)
    with col2:
        room_name = st.text_input("Room / Space Name", value="Office Level 4")

    col1, col2, col3 = st.columns(3)
    with col1:
        room_length = st.number_input("Length (m)", min_value=1.0, max_value=500.0, value=20.0, step=0.5, key="lt_len")
    with col2:
        room_width = st.number_input("Width (m)", min_value=1.0, max_value=500.0, value=15.0, step=0.5, key="lt_wid")
    with col3:
        room_height = st.number_input("Room Height (m)", min_value=2.0, max_value=20.0, value=3.0, step=0.1, key="lt_hgt")

    col1, col2 = st.columns(2)
    with col1:
        work_plane_height = st.number_input("Work Plane Height (m)", min_value=0.0, max_value=2.0, value=0.8, step=0.1)
    with col2:
        target_lux = st.number_input("Required Maintained Illuminance (lux)", min_value=50, max_value=5000, value=default_lux, step=50)

    section_title("Luminaire Data")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        luminaire_lumens = st.number_input("Lumens per Luminaire", min_value=100, max_value=100000, value=4000, step=100)
    with col2:
        luminaire_watts = st.number_input("Watts per Luminaire (W)", min_value=1.0, max_value=1000.0, value=40.0, step=1.0)
    with col3:
        llf = st.number_input("Light Loss Factor (LLF)", min_value=0.5, max_value=1.0, value=0.80, step=0.01,
                               help="Maintenance Factor = LLMF × LSF × LMF × RSMF")
    with col4:
        luminaire_efficiency = st.number_input("Luminaire Efficiency", min_value=0.5, max_value=1.0, value=1.0, step=0.01,
                                                help="Light Output Ratio (LOR)")

    col1, col2, col3 = st.columns(3)
    with col1:
        ceiling_reflectance = st.number_input("Ceiling Reflectance (ρc)", min_value=0.1, max_value=0.9, value=0.7, step=0.05)
    with col2:
        wall_reflectance = st.number_input("Wall Reflectance (ρw)", min_value=0.1, max_value=0.9, value=0.5, step=0.05)
    with col3:
        floor_reflectance = st.number_input("Floor Reflectance (ρf)", min_value=0.05, max_value=0.5, value=0.2, step=0.05)

    submitted = st.form_submit_button("Calculate Lighting Design", use_container_width=True)

if submitted:
    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "room_name": room_name,
        "room_type": space_type,
        "length_m": room_length,
        "width_m": room_width,
        "height_m": room_height,
        "work_plane_height_m": work_plane_height,
        "target_lux": float(target_lux),
        "luminaire_lumens": float(luminaire_lumens),
        "luminaire_watts": luminaire_watts,
        "luminaire_efficiency": luminaire_efficiency,
        "llf": llf,
        "ceiling_reflectance": ceiling_reflectance,
        "wall_reflectance": wall_reflectance,
        "floor_reflectance": floor_reflectance,
    }
    with st.spinner("Calculating lighting design..."):
        result = api_post("/api/electrical/lighting", payload)

    if result and result.get("status") == "success":
        section_title("Lighting Results")

        compliance_badge(result.get("lpd_compliant", False), f"LPD Compliance | {result.get('standard_reference', '')}")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Room Index (K)", f"{result.get('room_index_k', 0):.2f}", "")
        with col2:
            result_card("Utilisation Factor", f"{result.get('uf_coefficient', 0):.3f}", "")
        with col3:
            result_card("No. of Luminaires", f"{result.get('num_luminaires', 0)}", "luminaires")
        with col4:
            result_card("Achieved Illuminance", f"{result.get('achieved_lux', 0):.0f}", "lux")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Floor Area", f"{result.get('room_area_m2', 0):.1f}", "m²")
        with col2:
            result_card("Total Installed Load", f"{result.get('total_watts', 0)/1000:.2f}", "kW")
        with col3:
            lpd_status = "pass" if result.get("lpd_compliant") else "fail"
            result_card("LPD Achieved", f"{result.get('lpd_w_per_m2', 0):.1f}", f"W/m² (limit: {result.get('lpd_limit_w_per_m2', 0):.0f})", status=lpd_status)
        with col4:
            result_card("Uniformity Ratio", f"{result.get('uniformity_achieved', 0):.2f}", "(target ≥0.6)")

        section_title("Illuminance Comparison")
        achieved = result.get("achieved_lux", 0)
        required = target_lux
        fig = go.Figure(go.Bar(
            x=["Required (Em)", "Achieved", "Min Target (0.6×Em)"],
            y=[required, achieved, required * 0.6],
            marker_color=[MID_GREY, TEAL, "#883300"],
            text=[f"{v:.0f} lx" for v in [required, achieved, required * 0.6]],
            textposition="outside",
            textfont=dict(color=WHITE),
        ))
        fig.update_layout(
            plot_bgcolor=BLACK, paper_bgcolor=DARK_GREY,
            font=dict(color=WHITE), height=300,
            yaxis=dict(title="Illuminance (lux)", color=WHITE, gridcolor=MID_GREY),
            xaxis=dict(color=WHITE),
            margin=dict(l=40, r=20, t=20, b=40),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

        if result.get("recommendations"):
            st.info("Recommendations: " + " | ".join(result.get("recommendations", [])))

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
                      'region': result.get('region', 'gcc'), 'report_type': 'lighting',
                      'discipline': 'electrical', 'revision': 'P01',
                      'date': str(_pd.Timestamp.today().date())}
                _pdf = _gp(_m, result)
                if _pdf:
                    st.download_button('⬇️ PDF Report', data=_pdf,
                        file_name=f'OpenMEP_lighting_{_pd.Timestamp.today().date()}.pdf',
                        mime='application/pdf', use_container_width=True)
            except Exception:
                st.info('PDF: install reportlab.')
        with c2:
            try:
                _buf = _io.BytesIO()
                _rows = [{k: v for k, v in result.items() if isinstance(v, (int, float, str))}]
                _pd.DataFrame(_rows).to_excel(_buf, index=False, sheet_name='lighting')
                _buf.seek(0)
                st.download_button('⬇️ Excel Results', data=_buf.getvalue(),
                    file_name=f'OpenMEP_lighting_{_pd.Timestamp.today().date()}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True)
            except ImportError:
                st.info('Install openpyxl for Excel export.')
        with c3:
            if st.button('📋 Add Lighting to BOQ', use_container_width=True):
                if 'boq_items' not in st.session_state:
                    st.session_state.boq_items = []
                st.session_state.boq_items.append({
                    'type': 'lighting',
                    'description': 'Lighting: ' + str(result.get('luminaires_required', '—')),
                    'value': result.get('luminaires_required'),
                })
                st.success(f'Lighting added to BOQ session ({len(st.session_state.boq_items)} items).')
