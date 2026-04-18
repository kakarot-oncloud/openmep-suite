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

st.set_page_config(page_title="Short Circuit — OpenMEP", page_icon="⚠️", layout="wide")
apply_theme_css()

page_header(
    "Short Circuit Analysis",
    "IEC 60909 impedance method — prospective 3-phase and 1-phase fault levels, CPC thermal check",
    "⚠️"
)

region_code, sub_code = region_selector("sc")

with st.sidebar:
    st.markdown(f"<h3 style='color:{TEAL_L}; font-size:0.9rem; text-transform:uppercase; letter-spacing:2px;'>IEC 60909 Method</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{DARK_GREY}; padding:1rem; border-radius:6px; font-size:0.8rem; color:{WHITE}; line-height:1.8;">
    <b style='color:{TEAL_L}'>3-Phase Fault</b><br>
    Isc = U/(√3 × Z_total)<br><br>
    <b style='color:{TEAL_L}'>1-Phase Fault</b><br>
    Isc_1ph ≈ Isc_3ph × 0.87<br><br>
    <b style='color:{TEAL_L}'>CPC Thermal Check</b><br>
    k²S² ≥ I²t<br>
    k = 115 (Cu/PVC)<br>
    k = 143 (Cu/XLPE)<br><br>
    <b style='color:{TEAL_L}'>Adiabatic Equation</b><br>
    S = I√t / k (mm²)
    </div>
    """, unsafe_allow_html=True)

with st.form("short_circuit_form"):
    section_title("Transformer Data")
    col1, col2, col3 = st.columns(3)
    with col1:
        tx_kva = st.number_input("Transformer Rating (kVA)", min_value=50, max_value=10000, value=1000, step=50)
    with col2:
        tx_impedance_pct = st.number_input("Transformer Impedance Zt (%)", min_value=1.0, max_value=10.0, value=5.5, step=0.1)
    with col3:
        lv_voltage = st.selectbox("LV Voltage (V)", [400, 415, 380, 230], index=0)

    section_title("Outgoing Cable Data")
    col1, col2, col3 = st.columns(3)
    with col1:
        cable_size = st.selectbox("Cable Size (mm²)", [16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 500, 630], index=7)
    with col2:
        cable_length = st.number_input("Cable Length (m)", min_value=1, max_value=1000, value=50, step=5)
    with col3:
        cable_material = st.selectbox("Conductor Material", ["Copper", "Aluminium"])

    section_title("Protection Data")
    col1, col2 = st.columns(2)
    with col1:
        cpc_size = st.number_input("CPC Size (mm²)", min_value=1.5, max_value=300.0, value=95.0, step=0.5)
    with col2:
        fault_duration_s = st.number_input("Fault Clearing Time (s)", min_value=0.01, max_value=5.0, value=0.4, step=0.01)

    submitted = st.form_submit_button("Calculate Fault Levels", use_container_width=True)

if submitted:
    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "transformer_kva": tx_kva,
        "transformer_impedance_pct": tx_impedance_pct,
        "lv_voltage": lv_voltage,
        "cable_size_mm2": float(cable_size),
        "cable_length_m": float(cable_length),
    }
    with st.spinner("Calculating fault levels..."):
        result = api_post("/api/electrical/short-circuit", payload)

    if result:
        section_title("Fault Level Results")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("3-Phase Isc (Terminals)", f"{result['isc_tx_3ph_ka']:.2f}", "kA")
        with col2:
            result_card("1-Phase Isc (Terminals)", f"{result['isc_tx_1ph_ka']:.2f}", "kA")
        with col3:
            result_card("3-Phase Isc (End)", f"{result['isc_end_3ph_ka']:.2f}", "kA")
        with col4:
            result_card("Min Earth Fault (End)", f"{result['ief_min_ka']:.3f}", "kA")

        col1, col2, col3 = st.columns(3)
        with col1:
            result_card("Max Fault Duration", f"{result['max_fault_duration_s']:.3f}", "s")
        with col2:
            result_card("Min CPC (Adiabatic)", f"{result['min_cpc_adiabatic_mm2']:.1f}", "mm²")
        with col3:
            cpc_ok = cpc_size >= result['min_cpc_adiabatic_mm2']
            status = "pass" if cpc_ok else "fail"
            result_card("CPC Check", "PASS ✓" if cpc_ok else "FAIL ✗", f"Provided: {cpc_size}mm²", status=status)

        section_title("Fault Level Profile Along Cable")
        points = [0, cable_length / 4, cable_length / 2, cable_length * 3 / 4, cable_length]
        drop_per_m = (result['isc_tx_3ph_ka'] - result['isc_end_3ph_ka']) / max(cable_length, 1)
        isc_values = [result['isc_tx_3ph_ka'] - drop_per_m * p for p in points]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=points, y=isc_values,
            mode="lines+markers",
            line=dict(color=TEAL, width=3),
            marker=dict(size=8, color=TEAL),
            name="3-phase Isc",
        ))
        fig.update_layout(
            plot_bgcolor=BLACK, paper_bgcolor=DARK_GREY,
            font=dict(color=WHITE), height=280,
            xaxis=dict(title="Distance from LV board (m)", color=WHITE, gridcolor=MID_GREY),
            yaxis=dict(title="Isc (kA)", color=WHITE, gridcolor=MID_GREY),
            margin=dict(l=40, r=20, t=20, b=40),
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
                      'region': result.get('region', 'gcc'), 'report_type': 'short_circuit',
                      'discipline': 'electrical', 'revision': 'P01',
                      'date': str(_pd.Timestamp.today().date())}
                _pdf = _gp(_m, result)
                if _pdf:
                    st.download_button('⬇️ PDF Report', data=_pdf,
                        file_name=f'OpenMEP_short_circuit_{_pd.Timestamp.today().date()}.pdf',
                        mime='application/pdf', use_container_width=True)
            except Exception:
                st.info('PDF: install reportlab.')
        with c2:
            try:
                _buf = _io.BytesIO()
                _rows = [{k: v for k, v in result.items() if isinstance(v, (int, float, str))}]
                _pd.DataFrame(_rows).to_excel(_buf, index=False, sheet_name='short_circuit')
                _buf.seek(0)
                st.download_button('⬇️ Excel Results', data=_buf.getvalue(),
                    file_name=f'OpenMEP_short_circuit_{_pd.Timestamp.today().date()}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True)
            except ImportError:
                st.info('Install openpyxl for Excel export.')
        with c3:
            if st.button('📋 Add SC Check to BOQ', use_container_width=True):
                if 'boq_items' not in st.session_state:
                    st.session_state.boq_items = []
                st.session_state.boq_items.append({
                    'type': 'short_circuit',
                    'description': 'Short Circuit: ' + str(result.get('fault_current_ka', '—')),
                    'value': result.get('fault_current_ka'),
                })
                st.success(f'Short Circuit added to BOQ session ({len(st.session_state.boq_items)} items).')
