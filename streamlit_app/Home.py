import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (
    RED, BLACK, WHITE, DARK_GREY, MID_GREY, LIGHT_GREY,
    api_get
)

st.set_page_config(
    page_title="OpenMEP — MEP Engineering Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(f"""
<style>
    .stApp {{ background-color: {BLACK}; }}
    .stSidebar {{ background-color: {DARK_GREY} !important; }}
    section[data-testid="stSidebar"] {{ background-color: {DARK_GREY} !important; }}
    div[data-testid="stSidebarContent"] {{ background-color: {DARK_GREY} !important; }}
    .css-1d391kg {{ background-color: {DARK_GREY} !important; }}
    .stMetric {{ background-color: {DARK_GREY}; border-radius: 8px; padding: 1rem; }}
    div.stButton > button {{
        background-color: {RED};
        color: {WHITE};
        border: none;
        border-radius: 6px;
        font-weight: 600;
        padding: 0.5rem 2rem;
        transition: opacity 0.2s;
    }}
    div.stButton > button:hover {{ opacity: 0.85; }}
    .stSelectbox > div {{ background-color: {DARK_GREY}; }}
    h1, h2, h3 {{ color: {WHITE} !important; }}
    label {{ color: {WHITE} !important; }}
    .stAlert {{ border-radius: 8px; }}
    .block-container {{ padding-top: 1rem; }}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="background: linear-gradient(135deg, {BLACK} 0%, #1a0000 50%, {DARK_GREY} 100%);
            padding: 3rem 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            border: 1px solid {RED}33;">
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
        <div style="width: 6px; height: 60px; background: {RED}; border-radius: 3px;"></div>
        <div>
            <h1 style="color: {WHITE}; margin: 0; font-size: 2.5rem; font-weight: 800; letter-spacing: -1px;">
                OpenMEP
            </h1>
            <p style="color: {RED}; margin: 0; font-size: 0.85rem; font-weight: 600; letter-spacing: 3px; text-transform: uppercase;">
                Open-Source MEP Engineering Suite
            </p>
        </div>
    </div>
    <p style="color: #BBBBBB; font-size: 1.05rem; max-width: 700px; margin-bottom: 1.5rem;">
        Professional-grade calculations for Mechanical, Electrical, and Plumbing engineering.
        Compliant with BS 7671, IS 3961, AS/NZS 3008, IEC 60364, and regional authority standards.
    </p>
    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
        <span style="background: {RED}22; border: 1px solid {RED}; color: {RED}; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
            🌍 4 Regions
        </span>
        <span style="background: {RED}22; border: 1px solid {RED}; color: {RED}; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
            ⚡ 9 Engines
        </span>
        <span style="background: {RED}22; border: 1px solid {RED}; color: {RED}; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
            📐 12 API Endpoints
        </span>
        <span style="background: {RED}22; border: 1px solid {RED}; color: {RED}; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
            ✓ Open Source
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

status_data = api_get("/")
if status_data:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div style="background: {DARK_GREY}; border: 1px solid {'#00AA44'}; border-radius: 8px; padding: 1.2rem; text-align: center;">
                <div style="color: {'#00AA44'}; font-size: 1.5rem;">●</div>
                <div style="color: {WHITE}; font-weight: 700;">Engine Online</div>
                <div style="color: {LIGHT_GREY}; font-size: 0.8rem;">FastAPI v{status_data.get('version', '0.1.0')}</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        regions = ", ".join([r.upper() for r in status_data.get("regions", [])])
        st.markdown(f"""
            <div style="background: {DARK_GREY}; border: 1px solid {RED}; border-radius: 8px; padding: 1.2rem; text-align: center;">
                <div style="color: {RED}; font-size: 1.5rem;">🌍</div>
                <div style="color: {WHITE}; font-weight: 700;">Regions Active</div>
                <div style="color: {LIGHT_GREY}; font-size: 0.8rem;">{regions}</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        disciplines = ", ".join([d.capitalize() for d in status_data.get("disciplines", [])])
        st.markdown(f"""
            <div style="background: {DARK_GREY}; border: 1px solid {RED}; border-radius: 8px; padding: 1.2rem; text-align: center;">
                <div style="color: {RED}; font-size: 1.5rem;">📐</div>
                <div style="color: {WHITE}; font-weight: 700;">Disciplines</div>
                <div style="color: {LIGHT_GREY}; font-size: 0.8rem;">{disciplines}</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div style="background: {DARK_GREY}; border: 1px solid {RED}; border-radius: 8px; padding: 1.2rem; text-align: center;">
                <div style="color: {RED}; font-size: 1.5rem;">📋</div>
                <div style="color: {WHITE}; font-weight: 700;">Standards</div>
                <div style="color: {LIGHT_GREY}; font-size: 0.8rem;">BS 7671 · IS 732 · AS 3008</div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.warning("Calculation engine is offline. Start the FastAPI server: `python3 -m uvicorn backend.main:app --reload --port 8000`")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(f"<h2 style='color:{WHITE}; font-size:1.3rem;'>Calculation Modules</h2>", unsafe_allow_html=True)

modules = [
    {
        "discipline": "Electrical",
        "color": RED,
        "icon": "⚡",
        "calcs": [
            ("Cable Sizing", "IEC/BS 7671 — derating factors, VD compliance, earth sizing"),
            ("Voltage Drop", "Dedicated VD analysis with upsize recommendation"),
            ("Maximum Demand", "Diversity-based MD + transformer sizing"),
            ("Short Circuit", "IEC 60909 impedance method — 3ph & 1ph fault levels"),
            ("Lighting Design", "Lumen method — maintained illuminance, LPD, uniformity"),
        ]
    },
    {
        "discipline": "Mechanical",
        "color": "#0066CC",
        "icon": "❄️",
        "calcs": [
            ("Cooling Load", "ASHRAE heat balance method — sensible + latent + OA"),
            ("Duct Sizing", "Equal friction method — rectangular/circular ducts"),
        ]
    },
    {
        "discipline": "Plumbing",
        "color": "#008855",
        "icon": "🔧",
        "calcs": [
            ("Pipe Sizing", "Hunter loading unit method — BS EN 806 / IS 1172 / AS 3500"),
        ]
    },
    {
        "discipline": "Fire",
        "color": "#FF6600",
        "icon": "🔥",
        "calcs": [
            ("Sprinkler Design", "BS EN 12845 / NFPA 13 — pump & tank sizing"),
        ]
    },
]

for module in modules:
    with st.expander(f"{module['icon']} {module['discipline']} Engineering", expanded=(module['discipline'] == 'Electrical')):
        for calc_name, calc_desc in module["calcs"]:
            st.markdown(f"""
                <div style="background: {BLACK};
                            border-left: 3px solid {module['color']};
                            padding: 0.6rem 1rem;
                            margin: 0.3rem 0;
                            border-radius: 0 4px 4px 0;">
                    <span style="color: {WHITE}; font-weight: 600;">{calc_name}</span>
                    <span style="color: {LIGHT_GREY}; font-size: 0.85rem; margin-left: 0.5rem;">— {calc_desc}</span>
                </div>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"<h2 style='color:{WHITE}; font-size:1.3rem;'>Supported Regions & Standards</h2>", unsafe_allow_html=True)

regions_data = [
    {
        "region": "GCC (Gulf Cooperation Council)",
        "flag": "🇦🇪",
        "countries": "UAE · Saudi Arabia · Qatar · Kuwait",
        "standard": "BS 7671:2018+A2:2022 / IEC 60364",
        "ambient": "50°C air / 35°C ground",
        "authority": "DEWA · ADDC · KAHRAMAA · SEC · MEW",
        "vd": "3%/4% (DEWA)",
    },
    {
        "region": "Europe / United Kingdom",
        "flag": "🇬🇧",
        "countries": "UK · EU Member States",
        "standard": "BS 7671:2018+A2:2022 (18th Edition)",
        "ambient": "30°C air / 20°C ground",
        "authority": "UKPN · Western Power · SP Manweb",
        "vd": "3%/5%",
    },
    {
        "region": "India",
        "flag": "🇮🇳",
        "countries": "Republic of India",
        "standard": "IS 732 / IS 3961 / IS 7098 / NBC 2016",
        "ambient": "45°C air / 30°C ground",
        "authority": "CEA · MSEDCL · BESCOM · State DISCOMs",
        "vd": "2.5%/5%",
    },
    {
        "region": "Australia",
        "flag": "🇦🇺",
        "countries": "Australia · New Zealand",
        "standard": "AS/NZS 3008.1.1:2017 / AS/NZS 3000:2018",
        "ambient": "40°C air / 25°C ground",
        "authority": "Ausgrid · Energex · Western Power",
        "vd": "5% total",
    },
]

cols = st.columns(2)
for i, rd in enumerate(regions_data):
    with cols[i % 2]:
        st.markdown(f"""
            <div style="background: {DARK_GREY};
                        border: 1px solid {MID_GREY};
                        border-top: 3px solid {RED};
                        border-radius: 8px;
                        padding: 1rem;
                        margin-bottom: 1rem;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{rd['flag']}</div>
                <div style="color: {WHITE}; font-weight: 700; font-size: 1rem;">{rd['region']}</div>
                <div style="color: {LIGHT_GREY}; font-size: 0.8rem;">{rd['countries']}</div>
                <hr style="border-color: {MID_GREY}; margin: 0.6rem 0;">
                <div style="color: {LIGHT_GREY}; font-size: 0.8rem;"><b style='color:{WHITE}'>Standard:</b> {rd['standard']}</div>
                <div style="color: {LIGHT_GREY}; font-size: 0.8rem;"><b style='color:{WHITE}'>Ambient:</b> {rd['ambient']}</div>
                <div style="color: {LIGHT_GREY}; font-size: 0.8rem;"><b style='color:{WHITE}'>Authority:</b> {rd['authority']}</div>
                <div style="color: {LIGHT_GREY}; font-size: 0.8rem;"><b style='color:{WHITE}'>VD Limits:</b> {rd['vd']}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<hr style='border-color: #333; margin: 2rem 0;'>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align: center; color: {LIGHT_GREY}; font-size: 0.8rem;">
    <b style="color: {RED}">OpenMEP</b> — Open-Source MEP Engineering Suite v0.1.0 &nbsp;|&nbsp;
    Apache 2.0 License &nbsp;|&nbsp;
    <a href="http://localhost:8000/docs" style="color: {RED}; text-decoration: none;">API Docs</a>
</div>
""", unsafe_allow_html=True)
