import streamlit as st
import sys
import os
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, MID_GREY, page_header, result_card, section_title, format_summary,
    api_post, region_selector,
    TEAL, TEAL_L
)

st.set_page_config(page_title="Sprinkler Design — OpenMEP", page_icon="🔥", layout="wide")
apply_theme_css()

page_header("Sprinkler System Design", "BS EN 12845 / NFPA 13 — hydraulic calculation, pump sizing, tank capacity", "🔥")

with st.sidebar:
    st.markdown(f"<h3 style='color:{TEAL_L}; font-size:0.9rem; text-transform:uppercase; letter-spacing:2px;'>Hazard Classification</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{DARK_GREY}; padding:1rem; border-radius:6px; font-size:0.8rem; color:{WHITE}; line-height:2.0;">
    <b style='color:{TEAL_L}'>LH</b> — Light Hazard<br>
    Residential, offices<br><br>
    <b style='color:{TEAL_L}'>OH1</b> — Ordinary Hazard 1<br>
    Hotels, schools<br><br>
    <b style='color:{TEAL_L}'>OH2</b> — Ordinary Hazard 2<br>
    Retail, warehouses<br><br>
    <b style='color:{TEAL_L}'>EH1/EH2</b> — Extra High<br>
    Industrial, chemical
    </div>
    """, unsafe_allow_html=True)

HAZARD_CLASSES = {
    "LH — Light Hazard (Office/Residential)": "LH",
    "OH1 — Ordinary Hazard 1 (Hotels/Schools)": "OH1",
    "OH2 — Ordinary Hazard 2 (Retail/Warehouse)": "OH2",
    "EH1 — Extra High Hazard 1": "EH1",
    "EH2 — Extra High Hazard 2": "EH2",
}

with st.form("sprinkler_form"):
    section_title("Regional Standards")
    region_code, sub_code = region_selector("sp")
    hazard_label = st.selectbox("Hazard Classification", list(HAZARD_CLASSES.keys()))
    hazard_class = HAZARD_CLASSES[hazard_label]

    section_title("Protected Area")
    col1, col2, col3 = st.columns(3)
    with col1:
        area_protected = st.number_input("Total Protected Area (m²)", min_value=50.0, max_value=50000.0, value=5000.0, step=100.0)
    with col2:
        ceiling_height = st.number_input("Ceiling Height (m)", min_value=2.0, max_value=30.0, value=4.0, step=0.5)
    with col3:
        sprinkler_coverage = st.number_input("Max Coverage per Sprinkler (m²)", min_value=4.0, max_value=25.0, value=9.0, step=0.5)

    section_title("Sprinkler Data")
    col1, col2, col3 = st.columns(3)
    with col1:
        k_factor = st.number_input("K-Factor (L/min/bar^0.5)", min_value=40.0, max_value=200.0, value=80.0, step=5.0,
                                    help="K80 = Standard response. K115/K161 = ESFR.")
    with col2:
        hose_allowance = st.number_input("Hose Allowance (L/min)", min_value=0.0, max_value=2000.0, value=500.0, step=100.0,
                                          help="Standpipe hose stream allowance per BS EN 12845")
    with col3:
        pass

    submitted = st.form_submit_button("Design Sprinkler System", use_container_width=True)

if submitted:
    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "occupancy_hazard": hazard_class,
        "area_protected_m2": area_protected,
        "ceiling_height_m": ceiling_height,
        "sprinkler_coverage_m2": sprinkler_coverage,
        "sprinkler_k_factor": k_factor,
        "hose_allowance_l_min": hose_allowance,
    }
    with st.spinner("Designing sprinkler system..."):
        result = api_post("/api/fire/sprinkler", payload)

    if result and result.get("status") == "success":
        section_title("Sprinkler Design Results")

        st.markdown(f"""
            <div style="background:{DARK_GREY}; border: 1px solid {TEAL}; border-radius:8px; padding:1rem; margin-bottom:1rem;">
                <span style='color:{TEAL_L}; font-weight:700;'>Standard: </span>
                <span style='color:{WHITE};'>{result.get('design_standard', '')}</span>
            </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Hazard Class", result.get("hazard_class", ""), "")
        with col2:
            result_card("Design Area Sprinklers", f"{result.get('num_sprinklers_design_area', 0)}", "simultaneously active")
        with col3:
            result_card("Design Flow Rate", f"{result.get('design_flow_l_min', 0):.0f}", "L/min")
        with col4:
            result_card("Total System Flow", f"{result.get('total_system_flow_l_min', 0):.0f}", "L/min (inc. hose)")

        section_title("Pump & Tank Requirements")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Pump Flow", f"{result.get('pump_flow_l_min', 0):.0f}", "L/min")
        with col2:
            result_card("Pump Head", f"{result.get('pump_head_m', 0):.1f}", "m")
        with col3:
            result_card("Fire Duration", f"{result.get('supply_duration_min', 60)}", "minutes")
        with col4:
            result_card("Tank Capacity", f"{result.get('tank_capacity_m3', 0):.1f}", "m³")

        section_title("Flow & Pressure Summary")
        labels = ["Design Flow\n(L/min)", "Hose\nAllowance", "Total System\nFlow", "Pump Flow"]
        values = [
            result.get("design_flow_l_min", 0),
            result.get("hose_allowance_l_min", 0),
            result.get("total_system_flow_l_min", 0),
            result.get("pump_flow_l_min", 0),
        ]
        fig = go.Figure(go.Bar(
            x=labels, y=values,
            marker_color=[TEAL, TEAL_L, "#00729E", "#005F85"],
            text=[f"{v:.0f}" for v in values],
            textposition="outside",
            textfont=dict(color=WHITE),
        ))
        fig.update_layout(
            plot_bgcolor=BLACK, paper_bgcolor=DARK_GREY,
            font=dict(color=WHITE), height=280,
            yaxis=dict(title="Flow (L/min)", color=WHITE, gridcolor=MID_GREY),
            xaxis=dict(color=WHITE),
            margin=dict(l=40, r=20, t=20, b=60),
            showlegend=False,
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
                      'region': result.get('region', 'gcc'), 'report_type': 'sprinkler',
                      'discipline': 'fire', 'revision': 'P01',
                      'date': str(_pd.Timestamp.today().date())}
                _pdf = _gp(_m, result)
                if _pdf:
                    st.download_button('⬇️ PDF Report', data=_pdf,
                        file_name=f'OpenMEP_sprinkler_{_pd.Timestamp.today().date()}.pdf',
                        mime='application/pdf', use_container_width=True)
            except Exception:
                st.info('PDF: install reportlab.')
        with c2:
            try:
                _buf = _io.BytesIO()
                _rows = [{k: v for k, v in result.items() if isinstance(v, (int, float, str))}]
                _pd.DataFrame(_rows).to_excel(_buf, index=False, sheet_name='sprinkler')
                _buf.seek(0)
                st.download_button('⬇️ Excel Results', data=_buf.getvalue(),
                    file_name=f'OpenMEP_sprinkler_{_pd.Timestamp.today().date()}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True)
            except ImportError:
                st.info('Install openpyxl for Excel export.')
        with c3:
            if st.button('📋 Add Sprinkler to BOQ', use_container_width=True):
                if 'boq_items' not in st.session_state:
                    st.session_state.boq_items = []
                st.session_state.boq_items.append({
                    'type': 'sprinkler',
                    'description': 'Sprinkler Design: ' + str(result.get('sprinklers_required', '—')),
                    'value': result.get('sprinklers_required'),
                })
                st.success(f'Sprinkler Design added to BOQ session ({len(st.session_state.boq_items)} items).')
