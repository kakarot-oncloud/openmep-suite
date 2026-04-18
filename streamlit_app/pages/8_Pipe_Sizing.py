import streamlit as st
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, LIGHT_GREY,
    page_header, result_card, section_title, format_summary,
    api_post, region_selector,
    TEAL, TEAL_L
)

st.set_page_config(page_title="Pipe Sizing — OpenMEP", page_icon="🔧", layout="wide")
apply_theme_css()

page_header("Pipe Sizing", "Loading unit (discharge unit) method per BS EN 806 / IS 1172 / AS 3500", "🔧")

with st.sidebar:
    st.markdown(f"<h3 style='color:{TEAL_L}; font-size:0.9rem; text-transform:uppercase; letter-spacing:2px;'>Discharge Unit Method</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{DARK_GREY}; padding:1rem; border-radius:6px; font-size:0.8rem; color:{WHITE}; line-height:1.8;">
    Discharge Units (DU) per BS EN 806:<br>
    • WC cistern: 2 DU<br>
    • WC flush valve: 6 DU<br>
    • Washbasin tap: 0.5 DU<br>
    • Shower: 2 DU<br>
    • Bath: 3 DU<br>
    • Urinal: 0.5–4 DU<br>
    • Kitchen sink: 1 DU<br>
    • Dishwasher: 1 DU<br><br>
    Total DU → Design Flow Rate<br>
    via probability conversion
    </div>
    """, unsafe_allow_html=True)

FIXTURE_TABLE = {
    "WC (Cistern flush)": 2.0,
    "WC (Flush valve)": 6.0,
    "Washbasin (tap)": 0.5,
    "Washbasin (mixer)": 1.0,
    "Shower": 2.0,
    "Bath (tub)": 3.0,
    "Kitchen Sink": 1.0,
    "Dishwasher": 1.0,
    "Urinal (cistern)": 0.5,
    "Urinal (flush valve)": 4.0,
    "Utility Sink": 3.0,
    "Washing Machine": 3.0,
}

if "fixtures" not in st.session_state:
    st.session_state.fixtures = [
        {"name": "WC (Cistern flush)", "count": 20, "du": 2.0},
        {"name": "Washbasin (tap)", "count": 30, "du": 0.5},
        {"name": "Shower", "count": 15, "du": 2.0},
        {"name": "Bath (tub)", "count": 10, "du": 3.0},
        {"name": "Kitchen Sink", "count": 10, "du": 1.0},
    ]

section_title("Regional Standards")
region_code, sub_code = region_selector("ps")
pipe_material = st.selectbox("Pipe Material", ["copper", "pvc", "ppr", "gi", "hdpe"])

section_title("Fixture Schedule")
col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])
with col1: st.markdown(f"<span style='color:{LIGHT_GREY}; font-size:0.85rem;'>Fixture Type</span>", unsafe_allow_html=True)
with col2: st.markdown(f"<span style='color:{LIGHT_GREY}; font-size:0.85rem;'>Count</span>", unsafe_allow_html=True)
with col3: st.markdown(f"<span style='color:{LIGHT_GREY}; font-size:0.85rem;'>DU Each</span>", unsafe_allow_html=True)
with col4: st.markdown(f"<span style='color:{LIGHT_GREY}; font-size:0.85rem;'>Del</span>", unsafe_allow_html=True)

to_remove = []
for i, fix in enumerate(st.session_state.fixtures):
    col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])
    with col1:
        fix["name"] = st.text_input(f"fn_{i}", value=fix["name"], label_visibility="collapsed", key=f"fn_{i}")
    with col2:
        fix["count"] = st.number_input(f"fc_{i}", min_value=0, max_value=1000, value=fix["count"], label_visibility="collapsed", key=f"fc_{i}")
    with col3:
        fix["du"] = st.number_input(f"fdu_{i}", min_value=0.1, max_value=20.0, value=fix["du"], step=0.5, label_visibility="collapsed", key=f"fdu_{i}")
    with col4:
        if st.button("🗑", key=f"fdel_{i}"):
            to_remove.append(i)

for i in reversed(to_remove):
    st.session_state.fixtures.pop(i)

col1, col2 = st.columns(2)
with col1:
    if st.button("+ Add Fixture"):
        st.session_state.fixtures.append({"name": "WC (Cistern flush)", "count": 5, "du": 2.0})
        st.rerun()

section_title("System Settings")
col1, col2, col3 = st.columns(3)
with col1:
    system_type = st.selectbox("System Type", ["CWDS", "DHWS", "drainage"])
with col2:
    max_velocity = st.number_input("Max Velocity (m/s)", min_value=0.5, max_value=5.0, value=2.0, step=0.1)
with col3:
    pass

if st.button("Calculate Pipe Size", use_container_width=True):
    total_du = sum(f["count"] * f["du"] for f in st.session_state.fixtures if f["count"] > 0)

    payload = {
        "region": region_code,
        "sub_region": sub_code,
        "system": system_type,
        "flow_units": total_du,
        "pipe_material": pipe_material,
        "max_velocity_m_s": max_velocity,
    }
    with st.spinner("Calculating pipe size..."):
        result = api_post("/api/plumbing/pipe-sizing", payload)

    if result and result.get("status") == "success":
        section_title("Pipe Sizing Results")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            result_card("Total Discharge Units", f"{total_du:.0f}", "DU")
        with col2:
            result_card("Design Flow Rate", f"{result.get('flow_rate_l_s', 0):.2f}", "L/s")
        with col3:
            result_card("Nominal Pipe Size", f"DN{result.get('pipe_nominal_dn', 0)}", "")
        with col4:
            result_card("Internal Diameter", f"{result.get('pipe_diameter_mm', 0)}", "mm")

        col1, col2, col3 = st.columns(3)
        with col1:
            result_card("Flow Velocity", f"{result.get('velocity_m_s', 0):.2f}", "m/s")
        with col2:
            result_card("Friction Loss", f"{result.get('pressure_drop_kpa_m', 0):.3f}", "kPa/m")
        with col3:
            result_card("Pipe Material", result.get("pipe_material", "").upper(), "")

        section_title("Fixture Summary")
        if st.session_state.fixtures:
            rows = []
            for f in st.session_state.fixtures:
                if f["count"] > 0:
                    rows.append({
                        "Fixture": f["name"],
                        "Count": f["count"],
                        "DU Each": f["du"],
                        "Total DU": f["count"] * f["du"],
                    })
            if rows:
                df = pd.DataFrame(rows)
                total_row = pd.DataFrame([{"Fixture": "TOTAL", "Count": sum(r["Count"] for r in rows),
                                           "DU Each": "", "Total DU": sum(r["Total DU"] for r in rows)}])
                df = pd.concat([df, total_row], ignore_index=True)
                st.dataframe(df, use_container_width=True)

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
                      'region': result.get('region', 'gcc'), 'report_type': 'pipe_sizing',
                      'discipline': 'hvac', 'revision': 'P01',
                      'date': str(_pd.Timestamp.today().date())}
                _pdf = _gp(_m, result)
                if _pdf:
                    st.download_button('⬇️ PDF Report', data=_pdf,
                        file_name=f'OpenMEP_pipe_sizing_{_pd.Timestamp.today().date()}.pdf',
                        mime='application/pdf', use_container_width=True)
            except Exception:
                st.info('PDF: install reportlab.')
        with c2:
            try:
                _buf = _io.BytesIO()
                _rows = [{k: v for k, v in result.items() if isinstance(v, (int, float, str))}]
                _pd.DataFrame(_rows).to_excel(_buf, index=False, sheet_name='pipe_sizing')
                _buf.seek(0)
                st.download_button('⬇️ Excel Results', data=_buf.getvalue(),
                    file_name=f'OpenMEP_pipe_sizing_{_pd.Timestamp.today().date()}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True)
            except ImportError:
                st.info('Install openpyxl for Excel export.')
        with c3:
            if st.button('📋 Add Pipe to BOQ', use_container_width=True):
                if 'boq_items' not in st.session_state:
                    st.session_state.boq_items = []
                st.session_state.boq_items.append({
                    'type': 'pipe_sizing',
                    'description': (
                        f"Pipe Sizing: DN{result.get('pipe_nominal_dn', result.get('selected_dn', '—'))} "
                        f"{result.get('pipe_material', '')} | "
                        f"v={result.get('velocity_m_s', 0):.2f} m/s | "
                        f"ΔP={result.get('pressure_drop_kpa_m', 0):.3f} kPa/m"
                    ),
                    'value': result.get('pipe_nominal_dn', result.get('selected_dn')),
                })
                st.success(f'Pipe Sizing added to BOQ session ({len(st.session_state.boq_items)} items).')
