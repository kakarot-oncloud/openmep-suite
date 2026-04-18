import streamlit as st
import sys
import os
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, MID_GREY, page_header, result_card, compliance_badge, section_title, format_summary,
    api_post, region_selector, CIRCUIT_TYPES,
    TEAL, TEAL_L
)

st.set_page_config(page_title="Voltage Drop — OpenMEP", page_icon="⚡", layout="wide")
apply_theme_css()

page_header("Voltage Drop Analysis", "mV/A/m method per BS 7671 / IS 732 / AS 3000 with upsize recommendation", "⚡")

CABLE_SIZES = [1.5, 2.5, 4.0, 6.0, 10.0, 16.0, 25.0, 35.0, 50.0, 70.0, 95.0, 120.0, 150.0, 185.0, 240.0, 300.0]

with st.form("voltage_drop_form"):
    section_title("Regional Standards")
    region_code, sub_code = region_selector("vd")

    section_title("Circuit Parameters")
    col1, col2, col3 = st.columns(3)
    with col1:
        design_current_a = st.number_input("Design Current Ib (A)", min_value=0.1, max_value=5000.0, value=76.0, step=0.5)
    with col2:
        cable_size = st.selectbox("Cable Size (mm²)", CABLE_SIZES, index=8)
    with col3:
        cable_length_m = st.number_input("Cable Length (m)", min_value=1.0, max_value=5000.0, value=120.0, step=5.0)

    col1, col2, col3 = st.columns(3)
    with col1:
        phases = st.selectbox("Phases", [3, 1], index=0)
    with col2:
        circuit_type_label = st.selectbox("Circuit Type", list(CIRCUIT_TYPES.keys()))
        circuit_type = CIRCUIT_TYPES[circuit_type_label]
    with col3:
        existing_vd_pct = st.number_input("Upstream VD Already Used (%)", min_value=0.0, max_value=10.0, value=0.5, step=0.1,
                                           help="Voltage drop already consumed by upstream cables (leave 0 if this is the only cable)")

    submitted = st.form_submit_button("Analyse Voltage Drop", use_container_width=True)

if submitted:
    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "design_current_a": design_current_a,
        "conductor_size_mm2": float(cable_size),
        "cable_length_m": cable_length_m,
        "phases": phases,
        "circuit_type": circuit_type,
    }
    with st.spinner("Analysing voltage drop..."):
        result = api_post("/api/electrical/voltage-drop", payload)

    if result and result.get("status") == "success":
        section_title("Voltage Drop Results")

        compliance_badge(result.get("compliant", False), f"{region_code.upper()} | {result.get('standard', '')}")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Voltage Drop", f"{result.get('vd_percent', 0):.2f}", "%")
        with col2:
            status = "pass" if result.get("compliant") else "fail"
            result_card("VD Limit", f"{result.get('vd_limit_percent', 5):.1f}", "%", status=status)
        with col3:
            result_card("Absolute VD", f"{result.get('vd_total_v', 0):.1f}", "V")
        with col4:
            result_card("mV/A/m Factor", f"{result.get('vd_mv_am', 0):.2f}", "mV/A/m")

        section_title("Voltage Profile")
        vd_v = result.get("vd_total_v", 0)
        supply_v = result.get("supply_voltage_v", 400)
        end_v = result.get("receiving_end_voltage_v", supply_v - vd_v)
        limit_pct = result.get("vd_limit_percent", 5)
        limit_v = supply_v * (1 - limit_pct / 100)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=["Source", "Cable End"],
            y=[supply_v, end_v],
            mode="lines+markers",
            line=dict(color=TEAL, width=3),
            marker=dict(size=10, color=TEAL),
            name="Voltage Profile",
        ))
        fig.add_hline(y=limit_v, line_dash="dash", line_color="#FF8800", annotation_text=f"VD Limit ({limit_pct}%)")
        fig.update_layout(
            plot_bgcolor=BLACK, paper_bgcolor=DARK_GREY,
            font=dict(color=WHITE), height=300,
            yaxis=dict(title="Voltage (V)", color=WHITE, gridcolor=MID_GREY),
            xaxis=dict(color=WHITE, gridcolor=MID_GREY),
            margin=dict(l=40, r=20, t=20, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

        if not result.get("compliant") and result.get("recommended_size_mm2"):
            st.warning(f"VD exceeds limit. Recommended cable size: **{result['recommended_size_mm2']} mm²**")

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
                      'region': result.get('region', 'gcc'), 'report_type': 'voltage_drop',
                      'discipline': 'electrical', 'revision': 'P01',
                      'date': str(_pd.Timestamp.today().date())}
                _pdf = _gp(_m, result)
                if _pdf:
                    st.download_button('⬇️ PDF Report', data=_pdf,
                        file_name=f'OpenMEP_voltage_drop_{_pd.Timestamp.today().date()}.pdf',
                        mime='application/pdf', use_container_width=True)
            except Exception:
                st.info('PDF: install reportlab.')
        with c2:
            try:
                _buf = _io.BytesIO()
                _rows = [{k: v for k, v in result.items() if isinstance(v, (int, float, str))}]
                _pd.DataFrame(_rows).to_excel(_buf, index=False, sheet_name='voltage_drop')
                _buf.seek(0)
                st.download_button('⬇️ Excel Results', data=_buf.getvalue(),
                    file_name=f'OpenMEP_voltage_drop_{_pd.Timestamp.today().date()}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True)
            except ImportError:
                st.info('Install openpyxl for Excel export.')
        with c3:
            if st.button('📋 Add VD Check to BOQ', use_container_width=True):
                if 'boq_items' not in st.session_state:
                    st.session_state.boq_items = []
                st.session_state.boq_items.append({
                    'type': 'voltage_drop',
                    'description': 'Voltage Drop: ' + str(result.get('voltage_drop_pct', '—')),
                    'value': result.get('voltage_drop_pct'),
                })
                st.success(f'Voltage Drop added to BOQ session ({len(st.session_state.boq_items)} items).')
