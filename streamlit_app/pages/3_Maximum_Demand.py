import streamlit as st
import sys
import os
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, LIGHT_GREY,
    page_header, result_card, section_title, format_summary,
    api_post, region_selector,
    TEAL, TEAL_L
)

st.set_page_config(page_title="Maximum Demand — OpenMEP", page_icon="📊", layout="wide")
apply_theme_css()

page_header("Maximum Demand", "Diversity-based MD calculation with transformer sizing per BS 7671 / NBC / AS 3000", "📊")

if "loads" not in st.session_state:
    st.session_state.loads = [
        {"name": "General Lighting", "kw": 15.0, "demand_factor": 0.85, "pf": 1.0, "load_type": "lighting", "phases": 3},
        {"name": "Power Outlets", "kw": 30.0, "demand_factor": 0.60, "pf": 0.90, "load_type": "power", "phases": 3},
        {"name": "HVAC", "kw": 80.0, "demand_factor": 0.75, "pf": 0.85, "load_type": "hvac", "phases": 3},
        {"name": "Lifts/Escalators", "kw": 22.0, "demand_factor": 0.60, "pf": 0.80, "load_type": "power", "phases": 3},
        {"name": "Emergency / UPS", "kw": 10.0, "demand_factor": 1.00, "pf": 0.90, "load_type": "power", "phases": 3},
    ]

section_title("Regional Standards")
region_code, sub_code = region_selector("md")

section_title("Load Schedule")
col1, col2, col3, col4, col5, col6, col7 = st.columns([3, 1.5, 1.5, 1.5, 1.5, 1.5, 1])
headers = ["Load Description", "kW", "Demand Factor", "Power Factor", "Type", "Phases", "Del"]
for col, header in zip([col1, col2, col3, col4, col5, col6, col7], headers):
    with col:
        st.markdown(f"<span style='color:{LIGHT_GREY}; font-size:0.85rem;'>{header}</span>", unsafe_allow_html=True)

loads_to_remove = []
LOAD_TYPES = ["lighting", "power", "hvac", "motor", "emergency"]
for i, load in enumerate(st.session_state.loads):
    col1, col2, col3, col4, col5, col6, col7 = st.columns([3, 1.5, 1.5, 1.5, 1.5, 1.5, 1])
    with col1:
        load["name"] = st.text_input(f"name_{i}", value=load["name"], label_visibility="collapsed", key=f"name_{i}")
    with col2:
        load["kw"] = st.number_input(f"kw_{i}", min_value=0.0, max_value=5000.0, value=load["kw"], step=0.5, label_visibility="collapsed", key=f"kw_{i}")
    with col3:
        load["demand_factor"] = st.number_input(f"df_{i}", min_value=0.1, max_value=1.0, value=load["demand_factor"], step=0.01, label_visibility="collapsed", key=f"df_{i}")
    with col4:
        load["pf"] = st.number_input(f"pf_{i}", min_value=0.5, max_value=1.0, value=load["pf"], step=0.01, label_visibility="collapsed", key=f"pf_{i}")
    with col5:
        load["load_type"] = st.selectbox(f"lt_{i}", LOAD_TYPES, index=LOAD_TYPES.index(load.get("load_type", "power")), label_visibility="collapsed", key=f"lt_{i}")
    with col6:
        load["phases"] = st.selectbox(f"ph_{i}", [3, 1], index=0 if load.get("phases", 3) == 3 else 1, label_visibility="collapsed", key=f"ph_{i}")
    with col7:
        if st.button("🗑", key=f"del_{i}"):
            loads_to_remove.append(i)

for i in reversed(loads_to_remove):
    st.session_state.loads.pop(i)

if st.button("+ Add Load"):
    st.session_state.loads.append({"name": "New Load", "kw": 10.0, "demand_factor": 0.80, "pf": 0.85, "load_type": "power", "phases": 3})
    st.rerun()

section_title("System Parameters")
col1, col2, col3 = st.columns(3)
with col1:
    supply_voltage_lv = st.number_input("Supply Voltage (V)", min_value=200, max_value=40000, value=400, step=5)
with col2:
    diversity_factor = st.number_input("Overall Diversity Factor", min_value=0.1, max_value=1.0, value=0.85, step=0.01)
with col3:
    future_expansion_pct = st.number_input("Future Expansion (%)", min_value=0.0, max_value=50.0, value=20.0, step=1.0)

if st.button("Calculate Maximum Demand", use_container_width=True):
    loads_payload = [
        {
            "description": l["name"],
            "quantity": 1,
            "unit_kw": l["kw"],
            "power_factor": l["pf"],
            "demand_factor": l["demand_factor"],
            "load_type": l["load_type"],
            "phases": l["phases"],
        }
        for l in st.session_state.loads if l["kw"] > 0
    ]
    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "supply_voltage_lv": supply_voltage_lv,
        "diversity_factor": diversity_factor,
        "future_expansion_pct": future_expansion_pct,
        "loads": loads_payload,
    }
    with st.spinner("Calculating maximum demand..."):
        result = api_post("/api/electrical/maximum-demand", payload)

    if result and result.get("status") == "success":
        section_title("Maximum Demand Results")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Total Connected", f"{result['total_connected_kw']:.1f}", "kW")
        with col2:
            result_card("Maximum Demand", f"{result['total_demand_kw']:.1f}", "kW")
        with col3:
            result_card("MD (kVA)", f"{result['total_demand_kva']:.1f}", "kVA")
        with col4:
            result_card("Overall PF", f"{result['overall_power_factor']:.3f}", "")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Design Current", f"{result['total_demand_current_a']:.1f}", "A")
        with col2:
            result_card("Main Protection", f"{result['main_protection_a']:.0f}", "A")
        with col3:
            result_card("Min TX Rating", f"{result['transformer_kva_min']:.0f}", "kVA")
        with col4:
            result_card("Recommended TX", f"{result['transformer_kva_recommended']:.0f}", "kVA")

        section_title("Load Breakdown by Type")
        breakdown = result.get("breakdown_by_type", {})
        if breakdown:
            labels = list(breakdown.keys())
            values = list(breakdown.values())
            colors = [TEAL, TEAL_L, "#00729E", "#005F85", "#00B4D8", "#48CAE4", "#90E0EF"]
            fig = go.Figure(go.Pie(
                labels=[l.capitalize() for l in labels],
                values=values,
                marker_colors=colors[:len(labels)],
                textfont_color=WHITE,
                hole=0.4,
            ))
            fig.update_layout(
                plot_bgcolor=BLACK, paper_bgcolor=DARK_GREY,
                font=dict(color=WHITE), height=350,
                legend=dict(font=dict(color=WHITE)),
                margin=dict(l=0, r=0, t=20, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)

        section_title("Engineering Summary")
        format_summary(result.get("calculation_summary", ""))


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
                      'region': result.get('region', 'gcc'), 'report_type': 'maximum_demand',
                      'discipline': 'electrical', 'revision': 'P01',
                      'date': str(_pd.Timestamp.today().date())}
                _pdf = _gp(_m, result)
                if _pdf:
                    st.download_button('⬇️ PDF Report', data=_pdf,
                        file_name=f'OpenMEP_maximum_demand_{_pd.Timestamp.today().date()}.pdf',
                        mime='application/pdf', use_container_width=True)
            except Exception:
                st.info('PDF: install reportlab.')
        with c2:
            try:
                _buf = _io.BytesIO()
                _rows = [{k: v for k, v in result.items() if isinstance(v, (int, float, str))}]
                _pd.DataFrame(_rows).to_excel(_buf, index=False, sheet_name='maximum_demand')
                _buf.seek(0)
                st.download_button('⬇️ Excel Results', data=_buf.getvalue(),
                    file_name=f'OpenMEP_maximum_demand_{_pd.Timestamp.today().date()}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True)
            except ImportError:
                st.info('Install openpyxl for Excel export.')
        with c3:
            if st.button('📋 Add MD to BOQ', use_container_width=True):
                if 'boq_items' not in st.session_state:
                    st.session_state.boq_items = []
                st.session_state.boq_items.append({
                    'type': 'maximum_demand',
                    'description': 'Maximum Demand: ' + str(result.get('maximum_demand_kva', '—')),
                    'value': result.get('maximum_demand_kva'),
                })
                st.success(f'Maximum Demand added to BOQ session ({len(st.session_state.boq_items)} items).')
