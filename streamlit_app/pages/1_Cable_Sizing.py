import streamlit as st
import sys
import os
import plotly.graph_objects as go
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    NAVY, TEAL, TEAL_L, INK, WHITE, SILVER,
    RED, BLACK, DARK_GREY, MID_GREY,
    apply_theme_css, page_header, result_card, compliance_badge, section_title, format_summary,
    api_post, region_selector,
    INSTALLATION_METHODS, CABLE_TYPES, CIRCUIT_TYPES
)

st.set_page_config(page_title="Cable Sizing — OpenMEP", page_icon="🔌", layout="wide")

apply_theme_css()

page_header(
    "Cable Sizing",
    "Full cable selection with derating factors, voltage drop compliance, and earth conductor sizing",
    "🔌"
)

with st.sidebar:
    st.markdown(f"<h3 style='color:{TEAL_L}; font-size:0.9rem; text-transform:uppercase; letter-spacing:2px;'>Standards Reference</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{INK}; padding:1rem; border-radius:6px; font-size:0.8rem; color:{WHITE}; line-height:1.8;">
    <b style='color:{TEAL_L}'>GCC</b><br>
    BS 7671 Table 4D5A (XLPE)<br>
    BS 7671 Table 4D2A (PVC)<br>
    Ca: Table 4B1<br>
    Cg: Table 4C1<br><br>
    <b style='color:{TEAL_L}'>India</b><br>
    IS 3961 / IS 7098<br>
    3.5-core FRLS cables<br>
    NBC 2016 Part 4<br><br>
    <b style='color:{TEAL_L}'>Australia</b><br>
    AS/NZS 3008.1.1:2017<br>
    X-90 XLPE / V-75 PVC<br>
    AS/NZS 3000:2018<br><br>
    <b style='color:{TEAL_L}'>Europe</b><br>
    BS 7671:2018+A2:2022<br>
    IEC 60364-5-52
    </div>
    """, unsafe_allow_html=True)

with st.form("cable_sizing_form"):
    section_title("Project Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        project_name = st.text_input("Project Name", value="My Project")
    with col2:
        circuit_from = st.text_input("Circuit From", value="MDB")
    with col3:
        circuit_to = st.text_input("Circuit To", value="SMDB-L01")

    section_title("Regional Standards")
    region_code, sub_code = region_selector("cs")

    section_title("Load Parameters")
    col1, col2, col3 = st.columns(3)
    with col1:
        load_kw = st.number_input("Load (kW)", min_value=0.1, max_value=5000.0, value=45.0, step=0.5)
    with col2:
        power_factor = st.number_input("Power Factor", min_value=0.5, max_value=1.0, value=0.85, step=0.01)
    with col3:
        phases = st.selectbox("Phases", [3, 1], index=0)

    section_title("Cable Parameters")
    col1, col2, col3 = st.columns(3)
    with col1:
        cable_type_label = st.selectbox("Cable Type", list(CABLE_TYPES.keys()))
        cable_type = CABLE_TYPES[cable_type_label]
    with col2:
        inst_method_label = st.selectbox("Installation Method", list(INSTALLATION_METHODS.keys()), index=4)
        installation_method = INSTALLATION_METHODS[inst_method_label]
    with col3:
        circuit_type_label = st.selectbox("Circuit Type", list(CIRCUIT_TYPES.keys()))
        circuit_type = CIRCUIT_TYPES[circuit_type_label]

    col1, col2, col3 = st.columns(3)
    with col1:
        cable_length_m = st.number_input("Cable Length (m)", min_value=1.0, max_value=2000.0, value=120.0, step=5.0)
    with col2:
        ambient_temp_c = st.number_input("Ambient Temp (°C)", min_value=10, max_value=80, value=50)
    with col3:
        num_grouped = st.number_input("Grouped Circuits", min_value=1, max_value=20, value=3, step=1)

    submitted = st.form_submit_button("Calculate Cable Size", use_container_width=True)

if submitted:
    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "load_kw": load_kw,
        "power_factor": power_factor,
        "phases": phases,
        "cable_type": cable_type,
        "installation_method": installation_method,
        "cable_length_m": cable_length_m,
        "ambient_temp_c": ambient_temp_c,
        "num_grouped_circuits": int(num_grouped),
        "circuit_type": circuit_type,
        "project_name": project_name,
        "circuit_from": circuit_from,
        "circuit_to": circuit_to,
    }
    with st.spinner("Calculating cable size..."):
        result = api_post("/api/electrical/cable-sizing", payload)

    if result and result.get("status") == "success":
        section_title("Calculation Results")

        compliance_badge(
            result.get("overall_compliant", False),
            f"Region: {result.get('region', '').upper()} | Authority: {result.get('authority', '')}"
        )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Design Current (Ib)", f"{result['design_current_ib_a']:.1f}", "A")
        with col2:
            result_card("Selected Cable", f"{result['selected_size_mm2']}", "mm²")
        with col3:
            result_card("Derated Rating (Iz)", f"{result['derated_rating_iz_a']:.1f}", "A")
        with col4:
            result_card("Protection Device", f"{result['protection_device_a']:.0f}", "A")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            status = "pass" if result.get("voltage_drop_pass") else "fail"
            result_card("Voltage Drop", f"{result['voltage_drop_pct']:.2f}", f"% (limit: {result['voltage_drop_limit_pct']}%)", status=status)
        with col2:
            result_card("Ca Factor (Temp)", f"{result['ca_factor']:.3f}", f"at {ambient_temp_c}°C")
        with col3:
            result_card("Cg Factor (Group)", f"{result['cg_factor']:.3f}", f"{int(num_grouped)} circuits")
        with col4:
            result_card("Earth Conductor", f"{result['earth_conductor_mm2']:.0f}", "mm²")

        section_title("Conductor Utilisation")
        ib = result['design_current_ib_a']
        iz = result['derated_rating_iz_a']
        util_pct = (ib / iz * 100) if iz > 0 else 0

        fig = go.Figure(go.Bar(
            x=[util_pct, 100 - util_pct],
            y=[""],
            orientation='h',
            marker_color=[TEAL, MID_GREY],
            hovertemplate=None,
        ))
        fig.add_vline(x=100, line_color=TEAL_L, line_dash="dash", line_width=2)
        fig.update_layout(
            showlegend=False,
            height=80,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor=NAVY,
            paper_bgcolor=INK,
            xaxis=dict(range=[0, 120], showticklabels=True, color=WHITE, gridcolor=MID_GREY),
            yaxis=dict(showticklabels=False),
            barmode='stack',
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Conductor utilisation: **{util_pct:.1f}%** (Ib={ib:.1f}A / Iz={iz:.1f}A)")

        section_title("Engineering Summary")
        format_summary(result.get("summary", ""))

        section_title("Schedule of Quantities")
        df = pd.DataFrame([{
            "Project": project_name,
            "From": circuit_from,
            "To": circuit_to,
            "Region": region_code.upper(),
            "Authority": result.get("authority", ""),
            "Load (kW)": load_kw,
            "PF": power_factor,
            "Phases": phases,
            "Ib (A)": round(result['design_current_ib_a'], 1),
            "Cable": f"{result['selected_size_mm2']}mm² {cable_type}",
            "Method": installation_method,
            "Length (m)": cable_length_m,
            "VD (%)": round(result['voltage_drop_pct'], 2),
            "VD Limit (%)": result['voltage_drop_limit_pct'],
            "Earth (mm²)": result['earth_conductor_mm2'],
            "MCB/MCCB (A)": result['protection_device_a'],
            "Compliant": "YES" if result.get("overall_compliant") else "NO",
        }])
        st.dataframe(df, use_container_width=True)


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
                      'region': result.get('region', 'gcc'), 'report_type': 'cable_sizing',
                      'discipline': 'electrical', 'revision': 'P01',
                      'date': str(_pd.Timestamp.today().date())}
                _pdf = _gp(_m, result)
                if _pdf:
                    st.download_button('⬇️ PDF Report', data=_pdf,
                        file_name=f'OpenMEP_cable_sizing_{_pd.Timestamp.today().date()}.pdf',
                        mime='application/pdf', use_container_width=True)
            except Exception:
                st.info('PDF: install reportlab.')
        with c2:
            try:
                _buf = _io.BytesIO()
                _rows = [{k: v for k, v in result.items() if isinstance(v, (int, float, str))}]
                _pd.DataFrame(_rows).to_excel(_buf, index=False, sheet_name='cable_sizing')
                _buf.seek(0)
                st.download_button('⬇️ Excel Results', data=_buf.getvalue(),
                    file_name=f'OpenMEP_cable_sizing_{_pd.Timestamp.today().date()}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True)
            except ImportError:
                st.info('Install openpyxl for Excel export.')
        with c3:
            if st.button('📋 Add Cable to BOQ', use_container_width=True):
                if 'boq_items' not in st.session_state:
                    st.session_state.boq_items = []
                st.session_state.boq_items.append({
                    'type': 'cable_sizing',
                    'description': 'Cable Sizing: ' + str(result.get('selected_size_mm2', '—')),
                    'value': result.get('selected_size_mm2'),
                })
                st.success(f'Cable Sizing added to BOQ session ({len(st.session_state.boq_items)} items).')
