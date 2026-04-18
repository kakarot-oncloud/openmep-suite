import streamlit as st
import sys
import os
import plotly.graph_objects as go
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, MID_GREY, LIGHT_GREY,
    page_header, section_title, format_summary,
    api_post, region_selector,
    TEAL, TEAL_L
)

st.set_page_config(page_title="Duct Sizing — OpenMEP", page_icon="🌬️", layout="wide")
apply_theme_css()

page_header("Duct Sizing", "Equal friction method per ASHRAE / CIBSE — rectangular and circular ductwork", "🌬️")

region_code, sub_code = region_selector("ds")

if "duct_sections" not in st.session_state:
    st.session_state.duct_sections = [
        {"name": "Main Duct (AHU to DB1)", "flow_lps": 2000.0, "length_m": 15.0, "duct_type": "rectangular"},
        {"name": "Branch 1 (DB1 to Zone A)", "flow_lps": 800.0, "length_m": 20.0, "duct_type": "rectangular"},
        {"name": "Branch 2 (DB1 to Zone B)", "flow_lps": 600.0, "length_m": 25.0, "duct_type": "rectangular"},
        {"name": "Circular Return Duct", "flow_lps": 1800.0, "length_m": 18.0, "duct_type": "circular"},
    ]

section_title("Design Criteria")
col1, col2 = st.columns(2)
with col1:
    friction_rate = st.number_input("Friction Rate (Pa/m)", min_value=0.3, max_value=2.0, value=0.8, step=0.1,
                                     help="Target pressure drop per metre. ASHRAE: 0.6-1.0 Pa/m")
with col2:
    max_velocity = st.number_input("Max Velocity (m/s)", min_value=2.0, max_value=15.0, value=8.0, step=0.5,
                                    help="Supply: 5-8 m/s, Return: 4-6 m/s")

section_title("Duct Network Sections")
col1, col2, col3, col4, col5 = st.columns([3, 1.5, 1.5, 1.5, 1])
with col1: st.markdown(f"<span style='color:{LIGHT_GREY}; font-size:0.85rem;'>Section Description</span>", unsafe_allow_html=True)
with col2: st.markdown(f"<span style='color:{LIGHT_GREY}; font-size:0.85rem;'>Airflow (L/s)</span>", unsafe_allow_html=True)
with col3: st.markdown(f"<span style='color:{LIGHT_GREY}; font-size:0.85rem;'>Length (m)</span>", unsafe_allow_html=True)
with col4: st.markdown(f"<span style='color:{LIGHT_GREY}; font-size:0.85rem;'>Shape</span>", unsafe_allow_html=True)
with col5: st.markdown(f"<span style='color:{LIGHT_GREY}; font-size:0.85rem;'>Del</span>", unsafe_allow_html=True)

to_remove = []
for i, sec in enumerate(st.session_state.duct_sections):
    col1, col2, col3, col4, col5 = st.columns([3, 1.5, 1.5, 1.5, 1])
    with col1:
        sec["name"] = st.text_input(f"ds_name_{i}", value=sec["name"], label_visibility="collapsed", key=f"ds_name_{i}")
    with col2:
        sec["flow_lps"] = st.number_input(f"ds_flow_{i}", min_value=10.0, max_value=100000.0, value=sec["flow_lps"], step=50.0, label_visibility="collapsed", key=f"ds_flow_{i}")
    with col3:
        sec["length_m"] = st.number_input(f"ds_len_{i}", min_value=1.0, max_value=500.0, value=sec["length_m"], step=1.0, label_visibility="collapsed", key=f"ds_len_{i}")
    with col4:
        sec["duct_type"] = st.selectbox(f"ds_type_{i}", ["rectangular", "circular"], index=0 if sec["duct_type"] == "rectangular" else 1, label_visibility="collapsed", key=f"ds_type_{i}")
    with col5:
        if st.button("🗑", key=f"ds_del_{i}"):
            to_remove.append(i)

for i in reversed(to_remove):
    st.session_state.duct_sections.pop(i)

if st.button("+ Add Section"):
    st.session_state.duct_sections.append({"name": "New Section", "flow_lps": 500.0, "length_m": 10.0, "duct_type": "rectangular"})
    st.rerun()

if st.button("Size All Duct Sections", use_container_width=True):
    all_results = []
    for i, sec in enumerate(st.session_state.duct_sections):
        payload = {
            "region": region_code,
            "sub_region": sub_code,
            "segment_id": f"S{i+1}",
            "airflow_l_s": sec["flow_lps"],
            "duct_type": sec["duct_type"],
            "max_velocity_m_s": max_velocity,
            "friction_rate_pa_m": friction_rate,
        }
        result = api_post("/api/mechanical/duct-sizing", payload)
        if result and result.get("status") == "success":
            result["section_name"] = sec["name"]
            result["length_m"] = sec["length_m"]
            result["total_dp"] = result.get("pressure_drop_pa_m", 0) * sec["length_m"]
            all_results.append(result)

    if all_results:
        section_title("Duct Sizing Results")

        rows = []
        for r in all_results:
            duct_dim = f"{r.get('diameter_mm', 0):.0f}mm ⌀" if r.get("duct_type") == "circular" else f"{r.get('width_mm', 0):.0f}×{r.get('height_mm', 0):.0f}mm"
            rows.append({
                "Section": r["section_name"],
                "Airflow (L/s)": r.get("airflow_l_s", 0),
                "Dimensions": duct_dim,
                "Dh (mm)": round(r.get("hydraulic_diameter_mm", 0), 0),
                "Velocity (m/s)": round(r.get("velocity_m_s", 0), 1),
                "Friction (Pa/m)": round(r.get("pressure_drop_pa_m", 0), 2),
                "Length (m)": r.get("length_m", 0),
                "ΔP Total (Pa)": round(r.get("total_dp", 0), 1),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

        section_title("Pressure Drop by Section")
        fig = go.Figure(go.Bar(
            x=[r["section_name"] for r in all_results],
            y=[r.get("total_dp", 0) for r in all_results],
            marker_color=TEAL,
            text=[f"{r.get('total_dp', 0):.0f} Pa" for r in all_results],
            textposition="outside",
            textfont=dict(color=WHITE),
        ))
        fig.update_layout(
            plot_bgcolor=BLACK, paper_bgcolor=DARK_GREY,
            font=dict(color=WHITE), height=300,
            yaxis=dict(title="Total Pressure Drop (Pa)", color=WHITE, gridcolor=MID_GREY),
            xaxis=dict(color=WHITE),
            margin=dict(l=40, r=20, t=20, b=80),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

        section_title("Engineering Summary (Last Section)")
        format_summary(all_results[-1].get("summary", ""))


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
                      'region': result.get('region', 'gcc'), 'report_type': 'duct_sizing',
                      'discipline': 'hvac', 'revision': 'P01',
                      'date': str(_pd.Timestamp.today().date())}
                _pdf = _gp(_m, result)
                if _pdf:
                    st.download_button('⬇️ PDF Report', data=_pdf,
                        file_name=f'OpenMEP_duct_sizing_{_pd.Timestamp.today().date()}.pdf',
                        mime='application/pdf', use_container_width=True)
            except Exception:
                st.info('PDF: install reportlab.')
        with c2:
            try:
                _buf = _io.BytesIO()
                _rows = [{k: v for k, v in result.items() if isinstance(v, (int, float, str))}]
                _pd.DataFrame(_rows).to_excel(_buf, index=False, sheet_name='duct_sizing')
                _buf.seek(0)
                st.download_button('⬇️ Excel Results', data=_buf.getvalue(),
                    file_name=f'OpenMEP_duct_sizing_{_pd.Timestamp.today().date()}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True)
            except ImportError:
                st.info('Install openpyxl for Excel export.')
        with c3:
            if st.button('📋 Add Duct to BOQ', use_container_width=True):
                if 'boq_items' not in st.session_state:
                    st.session_state.boq_items = []
                _duct_desc = (
                    f"{result.get('width_mm', '')}×{result.get('height_mm', '')} mm rect."
                    if result.get('duct_type') == 'rectangular'
                    else f"Ø{result.get('diameter_mm', result.get('hydraulic_diameter_mm', '—'))} mm"
                )
                st.session_state.boq_items.append({
                    'type': 'duct_sizing',
                    'description': f"Duct Sizing: {_duct_desc}, v={result.get('velocity_m_s', 0):.1f} m/s",
                    'value': result.get('hydraulic_diameter_mm', result.get('diameter_mm')),
                })
                st.success(f'Duct Sizing added to BOQ session ({len(st.session_state.boq_items)} items).')
