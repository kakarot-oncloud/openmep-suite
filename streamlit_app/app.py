"""
OpenMEP — Open-Source MEP Engineering Calculation Suite
Entry point: streamlit run streamlit_app/app.py
"""

import streamlit as st
import sys
import os
import requests
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (
    NAVY, TEAL, TEAL_L, INK, WHITE, SILVER,
    RED, BLACK, DARK_GREY, LIGHT_GREY,
    API_BASE, apply_theme_css
)

st.set_page_config(
    page_title="OpenMEP — MEP Engineering Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme_css()

# ── Hero banner ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background: linear-gradient(135deg, {NAVY} 0%, {INK} 50%, #0a1e3d 100%);
            padding: 3rem 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            border: 1px solid {TEAL}33;">
  <div style="display:flex; align-items:center; gap:1.5rem; margin-bottom:1rem;">
    <div style="background:{TEAL}; color:{WHITE}; font-size:2.5rem; width:70px; height:70px;
                border-radius:12px; display:flex; align-items:center; justify-content:center;
                font-weight:900; box-shadow:0 4px 20px {TEAL}55;">M</div>
    <div>
      <h1 style="color:{WHITE}; margin:0; font-size:2.2rem; font-weight:800; letter-spacing:-1px;">
        OpenMEP
      </h1>
      <p style="color:{SILVER}; margin:0; font-size:1rem;">
        Open-Source MEP Engineering Calculation Suite — v0.2.0
      </p>
    </div>
  </div>
  <p style="color:{WHITE}88; font-size:0.95rem; margin:0; max-width:700px; line-height:1.7;">
    Professional mechanical, electrical, plumbing and fire protection calculations
    with full multi-regional compliance checking. Supports GCC (BS 7671 / IEC 60364),
    Europe/UK (BS 7671:2018+A2), India (IS 732 / IS 3961), and Australia (AS/NZS 3008).
  </p>
</div>
""", unsafe_allow_html=True)

# ── API health check ──────────────────────────────────────────────────────────
try:
    health = requests.get(f"{API_BASE}/health", timeout=3)
    api_ok = health.status_code == 200
except Exception:
    api_ok = False

status_color = "#00AA44" if api_ok else "#CC3300"
status_text = "Online" if api_ok else "Offline"
st.markdown(f"""
<div style="background:{INK}; border:1px solid {'#00AA44' if api_ok else '#CC3300'}44;
            border-radius:8px; padding:0.75rem 1.25rem; margin-bottom:1.5rem;
            display:flex; align-items:center; gap:0.75rem;">
  <div style="width:10px; height:10px; border-radius:50%; background:{status_color};
              box-shadow:0 0 8px {status_color};"></div>
  <span style="color:{WHITE}; font-size:0.9rem;">
    Calculation Engine: <b style="color:{status_color};">{status_text}</b>
    {'&nbsp;&nbsp;·&nbsp;&nbsp;<span style="color:' + SILVER + '">All 22 endpoints operational</span>' if api_ok else '&nbsp;&nbsp;·&nbsp;&nbsp;<span style="color:#CC3300">Start the FastAPI server on port 8000</span>'}
  </span>
</div>
""", unsafe_allow_html=True)

# ── Module cards ──────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
modules = [
    (col1, "⚡", "Electrical", TEAL,
     ["Cable Sizing", "Voltage Drop", "Maximum Demand", "Short Circuit",
      "Lighting Design", "Generator Sizing", "PF Correction", "Panel Schedule"],
     "BS 7671 / IS 3961 / AS 3008"),
    (col2, "❄️", "Mechanical/HVAC", "#0066CC",
     ["Cooling Load", "Heating Load", "Duct Sizing", "Ventilation"],
     "ASHRAE / CIBSE / ECBC / NCC"),
    (col3, "💧", "Plumbing", "#006644",
     ["Pipe Sizing", "Drainage Design", "Pump Head", "Hot Water", "Tank Sizing"],
     "BS EN 806 / IS 1172 / AS 3500"),
    (col4, "🔥", "Fire Protection", "#FF6600",
     ["Sprinkler Design", "Fire Pump", "Fire Tank", "Standpipe"],
     "NFPA 13 / BS EN 12845 / IS / AS"),
]
for col, icon, title, color, items, std in modules:
    with col:
        items_html = "".join([
            f"<div style='color:{WHITE}99; font-size:0.8rem; padding:0.2rem 0;'>• {it}</div>"
            for it in items
        ])
        st.markdown(f"""
        <div style="background:{INK}; border:1px solid {color}44; border-top:3px solid {color};
                    border-radius:8px; padding:1.25rem; height:280px;">
          <div style="font-size:1.8rem; margin-bottom:0.5rem;">{icon}</div>
          <div style="color:{WHITE}; font-weight:700; font-size:1rem; margin-bottom:0.75rem;">{title}</div>
          {items_html}
          <div style="margin-top:0.75rem; color:{color}; font-size:0.75rem; font-weight:600;">{std}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Regional Standards matrix ─────────────────────────────────────────────────
st.markdown(f"""
<div style="border-bottom:1px solid {TEAL}; margin:2rem 0 1rem 0; padding-bottom:0.5rem;">
  <span style="color:{TEAL_L}; font-weight:700; font-size:0.85rem; text-transform:uppercase; letter-spacing:2px;">
    Regional Standards Support
  </span>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
regions = [
    (col1, "GCC", "UAE / Saudi / Qatar / Kuwait",
     [("Electrical", "BS 7671 / IEC 60364"), ("HVAC", "ASHRAE 90.1 / DEWA MEW"),
      ("Plumbing", "BS EN 806 / DEWA regs"), ("Fire", "NFPA 13 / Civil Defence")],
     "DEWA · ADDC · KAHRAMAA · SEC · MEW"),
    (col2, "Europe/UK", "United Kingdom & Europe",
     [("Electrical", "BS 7671:2018+A2:2022"), ("HVAC", "CIBSE Guide A/B"),
      ("Plumbing", "BS EN 806:2012"), ("Fire", "BS EN 12845:2015")],
     "DNO · G99 · IEC 60364"),
    (col3, "India", "All States — DISCOMs",
     [("Electrical", "IS 732 / IS 3961 / IS 7098"), ("HVAC", "ECBC 2017 / NBC"),
      ("Plumbing", "IS 1172 / NBC Part 9"), ("Fire", "TAC / IS 15105")],
     "MSEDCL · BESCOM · TANGEDCO · WBSEDCL"),
    (col4, "Australia", "AU & New Zealand",
     [("Electrical", "AS/NZS 3000 / AS/NZS 3008"), ("HVAC", "NCC Section J"),
      ("Plumbing", "AS 3500 / AS 1345"), ("Fire", "AS 2118 / AS 2941")],
     "Ausgrid · Energex · CitiPower · Western Power"),
]
for col, region, subtitle, standards, authorities in regions:
    with col:
        stds_html = "".join([
            f"<div style='display:flex; justify-content:space-between; padding:0.25rem 0; border-bottom:1px solid #1C3A6A;'>"
            f"<span style='color:{LIGHT_GREY}; font-size:0.78rem;'>{disc}</span>"
            f"<span style='color:{WHITE}; font-size:0.78rem; text-align:right; max-width:60%;'>{std}</span></div>"
            for disc, std in standards
        ])
        st.markdown(f"""
        <div style="background:{INK}; border:1px solid #1e3050; border-radius:8px; padding:1rem;">
          <div style="color:{TEAL_L}; font-weight:700; font-size:1rem;">{region}</div>
          <div style="color:{SILVER}; font-size:0.78rem; margin-bottom:0.75rem;">{subtitle}</div>
          {stds_html}
          <div style="margin-top:0.75rem; color:{SILVER}; font-size:0.72rem;">{authorities}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Quick navigation ──────────────────────────────────────────────────────────
st.markdown(f"""
<div style="border-bottom:1px solid {TEAL}; margin:2rem 0 1rem 0; padding-bottom:0.5rem;">
  <span style="color:{TEAL_L}; font-weight:700; font-size:0.85rem; text-transform:uppercase; letter-spacing:2px;">
    Quick Start — Use the sidebar to navigate to any calculation
  </span>
</div>
<div style="background:{INK}; border:1px solid #1e3050; border-radius:8px; padding:1.25rem; margin-bottom:1rem;">
  <p style="color:{WHITE}88; font-size:0.9rem; margin:0; line-height:1.8;">
    <b style="color:{TEAL_L};">Electrical Pages:</b>
    Cable Sizing · Voltage Drop · Maximum Demand · Short Circuit · Lighting · Generator · PF Correction · Panel Schedule<br>
    <b style="color:#0066CC;">HVAC Pages:</b>
    Cooling Load · Duct Sizing<br>
    <b style="color:#006644;">Plumbing:</b>
    Pipe Sizing<br>
    <b style="color:#FF6600;">Fire Protection:</b>
    Sprinkler Design<br>
    <b style="color:{WHITE};">Utilities:</b>
    BOQ Generator · Compliance Checker · PDF Reports · Submittal Tracker
  </p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar: project info + grouped navigation ─────────────────────────────────
with st.sidebar:
    st.markdown(f"<h3 style='color:{TEAL_L}; font-size:0.85rem; text-transform:uppercase; letter-spacing:2px; margin-bottom:0.5rem;'>Project Information</h3>", unsafe_allow_html=True)
    for key in ("project_name", "client_name", "engineer_name", "project_number"):
        st.session_state.setdefault(key, "")

    st.session_state.project_name = st.text_input("Project Name", value=st.session_state.project_name, key="sidebar_project")
    st.session_state.client_name = st.text_input("Client", value=st.session_state.client_name, key="sidebar_client")
    st.session_state.engineer_name = st.text_input("Engineer", value=st.session_state.engineer_name, key="sidebar_engineer")
    st.session_state.project_number = st.text_input("Project No.", value=st.session_state.project_number, key="sidebar_proj_no")
    st.markdown(f"<div style='color:{LIGHT_GREY}; font-size:0.75rem; margin-top:0.5rem;'>Date: {date.today().strftime('%d %B %Y')}</div>", unsafe_allow_html=True)

    st.markdown("---")

    NAV_GROUPS = [
        ("⚡ Electrical", [
            ("Cable Sizing", "1_Cable_Sizing"),
            ("Voltage Drop", "2_Voltage_Drop"),
            ("Maximum Demand", "3_Maximum_Demand"),
            ("Short Circuit", "4_Short_Circuit"),
            ("Lighting Design", "5_Lighting"),
            ("Panel Schedule", "10_Panel_Schedule"),
            ("Generator Sizing", "11_Generator_Sizing"),
            ("PF Correction", "12_PF_Correction"),
        ]),
        ("❄️ HVAC", [
            ("Cooling Load", "6_Cooling_Load"),
            ("Duct Sizing", "7_Duct_Sizing"),
            ("Heating Load", "17_Heating_Load"),
            ("Ventilation", "18_Ventilation"),
        ]),
        ("💧 Plumbing", [
            ("Pipe Sizing", "8_Pipe_Sizing"),
            ("Drainage Sizing", "19_Drainage_Sizing"),
            ("Pump Sizing", "20_Pump_Sizing"),
            ("Hot Water System", "21_Hot_Water_System"),
            ("Rainwater Harvesting", "25_Rainwater_Harvesting"),
            ("Plumbing Tank Sizing", "26_Plumbing_Tank_Sizing"),
        ]),
        ("🔥 Fire Protection", [
            ("Sprinkler Design", "9_Sprinkler_Design"),
            ("Fire Pump", "22_Fire_Pump"),
            ("Fire Tank", "23_Fire_Tank"),
            ("Standpipe", "24_Standpipe"),
        ]),
        ("📁 Project Tools", [
            ("BOQ Generator", "13_BOQ_Generator"),
            ("Compliance Checker", "14_Compliance_Checker"),
            ("PDF Reports", "15_PDF_Reports"),
            ("Submittal Tracker", "16_Submittal_Tracker"),
        ]),
    ]

    for group_title, pages in NAV_GROUPS:
        st.markdown(f"<div style='color:{TEAL}; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin:0.8rem 0 0.2rem 0;'>{group_title}</div>", unsafe_allow_html=True)
        for page_label, page_file in pages:
            page_path = os.path.join(os.path.dirname(__file__), "pages", f"{page_file}.py")
            if os.path.exists(page_path):
                st.page_link(page_path, label=page_label)

    st.markdown("---")
    st.markdown(f"<div style='color:{SILVER}; font-size:0.75rem; text-align:center; line-height:1.8;'>OpenMEP v0.2.0<br>MIT License<br><a href='https://github.com/kakarot-oncloud/openmep' style='color:{TEAL};'>GitHub</a></div>", unsafe_allow_html=True)
