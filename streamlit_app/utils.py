import os
import streamlit as st
import requests
from typing import Any, Dict, Optional

# Environment-driven API base — works for localhost, Docker (api:8000), and VPS
API_BASE = os.environ.get("API_BASE", "http://localhost:8000").rstrip("/")

REGIONS = {
    "GCC (UAE/Saudi/Qatar/Kuwait)": "gcc",
    "Europe / United Kingdom": "europe",
    "India": "india",
    "Australia": "australia",
}

# 3-level hierarchical map: Region → Country/Emirate/State → Utility/Authority
# Level 1: REGIONS (region_code)
# Level 2: SUB_REGIONS_L2 — country/emirate/state within each region
# Level 3: SUB_REGIONS_L3 — utility authority within each country/emirate/state
SUB_REGIONS_L2 = {
    "gcc": {
        "UAE — United Arab Emirates": "uae",
        "Saudi Arabia — KSA": "ksa",
        "Qatar": "qatar",
        "Kuwait": "kuwait",
        "Bahrain": "bahrain",
        "Oman": "oman",
    },
    "europe": {
        "United Kingdom": "uk",
        "Ireland": "ireland",
        "Germany": "germany",
        "France": "france",
        "Netherlands": "netherlands",
        "Nordic Countries": "nordic",
        "EU Generic": "europe_generic",
    },
    "india": {
        "Delhi NCR": "delhi_ncr",
        "Mumbai / Maharashtra": "maharashtra",
        "Karnataka": "karnataka",
        "Tamil Nadu": "tamilnadu",
        "Telangana / Andhra Pradesh": "telangana",
        "Gujarat": "gujarat",
        "Rajasthan": "rajasthan",
        "West Bengal": "westbengal",
        "All India Generic": "india_generic",
    },
    "australia": {
        "New South Wales": "nsw",
        "Victoria": "vic",
        "Queensland": "qld",
        "South Australia": "sa",
        "Western Australia": "wa",
        "Tasmania": "tas",
        "Northern Territory": "nt",
        "ACT / Canberra": "act",
        "New Zealand": "nz",
    },
}

SUB_REGIONS_L3 = {
    "uae": {"DEWA — Dubai Electricity & Water Authority": "dewa", "ADDC — Abu Dhabi Distribution Co.": "addc", "AADC — Al Ain Distribution Co.": "aadc", "SEWA — Sharjah Electricity & Water": "sewa"},
    "ksa": {"SEC — Saudi Electricity Company (National)": "sec", "SEC-Central Region": "sec_central", "SEC-Western Region": "sec_western"},
    "qatar": {"KAHRAMAA — Qatar General Electricity & Water": "kahramaa"},
    "kuwait": {"MEW — Kuwait Ministry of Electricity & Water": "mew"},
    "bahrain": {"EWA — Electricity & Water Authority Bahrain": "ewa"},
    "oman": {"PAEW — Public Authority for Electricity & Water": "paew"},
    "uk": {"UK Generic — BS 7671:2018+A2:2022 / DNO": "uk"},
    "ireland": {"ESB Networks — ETCI / BS 7671": "ireland"},
    "germany": {"Generic — DIN VDE 0100": "germany"},
    "france": {"Generic — NF C 15-100": "france"},
    "netherlands": {"Generic — NEN 1010": "netherlands"},
    "nordic": {"Generic — SEK / CENELEC HD 60364": "nordic"},
    "europe_generic": {"EU Generic — IEC 60364": "europe_generic"},
    "delhi_ncr": {"BSES Rajdhani / BSES Yamuna": "bses", "Tata Power Delhi": "tpddl"},
    "maharashtra": {"MSEDCL (Rest of Maharashtra)": "msedcl", "BEST (Mumbai City)": "best", "Adani Electricity Mumbai": "adani"},
    "karnataka": {"BESCOM (Bengaluru & surrounding)": "bescom", "HESCOM / GESCOM / MESCOM": "hescom"},
    "tamilnadu": {"TANGEDCO (Tamil Nadu Genco)": "tangedco"},
    "telangana": {"TSSPDCL / TSNPDCL (Telangana)": "tsspdcl", "APEPDCL / APSPDCL (Andhra Pradesh)": "apepdcl"},
    "gujarat": {"DGVCL / MGVCL / PGVCL / UGVCL": "gujarat"},
    "rajasthan": {"JVVNL / JDVVNL / AVVNL": "rajasthan"},
    "westbengal": {"WBSEDCL / CESC (Kolkata)": "westbengal"},
    "india_generic": {"All India — IS 732:2019 / IS 3961 Generic": "india"},
    "nsw": {"Ausgrid (Sydney metro)": "ausgrid", "Endeavour Energy": "endeavour", "Essential Energy": "essential"},
    "vic": {"AusNet Services": "ausnet", "CitiPower / Powercor": "citipowercor", "Jemena / United Energy": "jemena"},
    "qld": {"Energex (SEQ)": "energex", "Ergon Energy (Regional QLD)": "ergon"},
    "sa": {"SA Power Networks": "sapn"},
    "wa": {"Western Power (Metro)": "westernpower", "Horizon Power (Regional WA)": "horizon"},
    "tas": {"TasNetworks": "tasnetworks"},
    "nt": {"Power and Water Corporation": "pawc"},
    "act": {"ActewAGL / Evoenergy": "evoenergy"},
    "nz": {"Transpower / Lines Companies — NZ Electricity Act": "nz"},
}

# Backward-compat flat map — all Level-3 authority options keyed by region
def _flatten_l3(*keys):
    result = {}
    for key in keys:
        result.update(SUB_REGIONS_L3.get(key, {}))
    return result

SUB_REGIONS = {
    "gcc": _flatten_l3("uae", "ksa", "qatar", "kuwait", "bahrain", "oman"),
    "europe": _flatten_l3("uk", "ireland", "germany", "france", "netherlands", "nordic", "europe_generic"),
    "india": _flatten_l3("delhi_ncr", "maharashtra", "karnataka", "tamilnadu", "telangana", "gujarat", "rajasthan", "westbengal", "india_generic"),
    "australia": _flatten_l3("nsw", "vic", "qld", "sa", "wa", "tas", "nt", "act", "nz"),
}

INSTALLATION_METHODS = {
    "A1 — Insulated, enclosed in conduit in thermally insulating wall": "A1",
    "A2 — Multicore, enclosed in conduit in thermally insulating wall": "A2",
    "B1 — Insulated, enclosed in conduit on wall or in trunking": "B1",
    "B2 — Multicore, enclosed in conduit on wall or in trunking": "B2",
    "C — Clipped direct to a non-metallic surface": "C",
    "D1 — In underground conduit": "D1",
    "D2 — Direct buried in ground": "D2",
    "E — Free air (spaced from surface)": "E",
    "F — Flat touching (free air)": "F",
}

CABLE_TYPES = {
    "XLPE Copper (XLPE_CU)": "XLPE_CU",
    "PVC Copper (PVC_CU)": "PVC_CU",
    "XLPE Aluminium (XLPE_AL)": "XLPE_AL",
    "PVC Aluminium (PVC_AL)": "PVC_AL",
}

CIRCUIT_TYPES = {
    "Power / Motor": "power",
    "Lighting": "lighting",
    "Combined": "combined",
}

NAVY = "#0A1628"
TEAL = "#0096C7"
TEAL_L = "#00B4D8"
INK = "#0D1F3C"
WHITE = "#FFFFFF"
SILVER = "#A8B8CC"

RED = "#CC0000"
BLACK = NAVY
DARK_GREY = INK
MID_GREY = "#162035"
LIGHT_GREY = SILVER


def apply_theme_css() -> None:
    """Inject the shared Neo-Navy theme CSS into the current Streamlit page.
    Call once at the top of every page after st.set_page_config().
    """
    st.markdown(f"""
<style>
    .stApp {{ background-color: {NAVY}; }}
    .stSidebar {{ background-color: {INK} !important; }}
    section[data-testid="stSidebar"] {{ background-color: {INK} !important; }}
    div[data-testid="stSidebarContent"] {{ background-color: {INK} !important; }}
    .stMetric {{ background-color: {INK}; border-radius: 8px; padding: 1rem; }}
    div.stButton > button {{
        background-color: {TEAL};
        color: {WHITE};
        border: none;
        border-radius: 6px;
        font-weight: 600;
        padding: 0.5rem 2rem;
        transition: opacity 0.2s;
    }}
    div.stButton > button:hover {{ opacity: 0.85; }}
    h1, h2, h3 {{ color: {WHITE} !important; }}
    label {{ color: {WHITE} !important; }}
    .stAlert {{ border-radius: 8px; }}
    .block-container {{ padding-top: 1rem; }}
    .stTextInput > div > div > input {{ background-color: {INK}; color: {WHITE}; border-color: #1e3050; }}
    .stSelectbox > div > div {{ background-color: {INK}; color: {WHITE}; }}
    .stNumberInput > div > div > input {{ background-color: {INK}; color: {WHITE}; }}
    p, span, div {{ color: {WHITE}; }}
</style>
""", unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = "") -> None:
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, {NAVY} 0%, {INK} 100%);
                    border-left: 4px solid {TEAL};
                    padding: 1.5rem 2rem;
                    border-radius: 0 8px 8px 0;
                    margin-bottom: 1.5rem;">
            <h1 style="color: {WHITE}; margin: 0; font-size: 1.8rem; font-weight: 700;">
                {icon} {title}
            </h1>
            {"<p style='color: " + SILVER + "; margin: 0.5rem 0 0 0; font-size: 0.95rem;'>" + subtitle + "</p>" if subtitle else ""}
        </div>
    """, unsafe_allow_html=True)


def result_card(label: str, value: str, unit: str = "", status: Optional[str] = None) -> None:
    border_color = TEAL
    if status == "pass":
        border_color = "#00AA44"
    elif status == "fail":
        border_color = "#CC3300"
    elif status == "warning":
        border_color = "#FF8800"
    st.markdown(f"""
        <div style="background: {INK};
                    border: 1px solid {border_color};
                    border-radius: 8px;
                    padding: 1rem;
                    margin: 0.25rem 0;
                    text-align: center;">
            <div style="color: {SILVER}; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">{label}</div>
            <div style="color: {WHITE}; font-size: 1.6rem; font-weight: 700; margin: 0.3rem 0;">{value}</div>
            {"<div style='color: " + SILVER + "; font-size: 0.85rem;'>" + unit + "</div>" if unit else ""}
        </div>
    """, unsafe_allow_html=True)


def compliance_badge(compliant: bool, label: str = "") -> None:
    if compliant:
        color, icon, text = "#00AA44", "✓", "COMPLIANT"
    else:
        color, icon, text = "#CC3300", "✗", "NON-COMPLIANT"
    st.markdown(f"""
        <div style="background: {color}22;
                    border: 2px solid {color};
                    border-radius: 8px;
                    padding: 1rem 1.5rem;
                    text-align: center;
                    margin: 1rem 0;">
            <span style="color: {color}; font-size: 2rem;">{icon}</span>
            <div style="color: {color}; font-weight: 700; font-size: 1.2rem;">{text}</div>
            {"<div style='color: " + SILVER + "; font-size: 0.85rem; margin-top: 0.3rem;'>" + label + "</div>" if label else ""}
        </div>
    """, unsafe_allow_html=True)


def metric_card_html(label: str, value: str) -> str:
    """Return an HTML metric card string for use with st.markdown(..., unsafe_allow_html=True)."""
    return (
        f"<div style='background:{INK}; border-left:4px solid {TEAL}; "
        f"padding:0.8rem 1rem; border-radius:6px; margin:0.3rem 0;'>"
        f"<div style='color:{SILVER}; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px;'>{label}</div>"
        f"<div style='color:{WHITE}; font-size:1.4rem; font-weight:700;'>{value}</div>"
        f"</div>"
    )


def render_metric_row(metrics: list) -> None:
    """Render a list of (label, value) tuples as metric cards in equal columns."""
    cols = st.columns(len(metrics))
    for col, (label, val) in zip(cols, metrics):
        with col:
            st.markdown(metric_card_html(label, val), unsafe_allow_html=True)


def section_title(text: str) -> None:
    st.markdown(f"""
        <div style="border-bottom: 1px solid {TEAL};
                    margin: 1.5rem 0 1rem 0;
                    padding-bottom: 0.5rem;">
            <span style="color: {TEAL_L}; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 2px;">
                {text}
            </span>
        </div>
    """, unsafe_allow_html=True)


def api_post(endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        resp = requests.post(f"{API_BASE}{endpoint}", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the calculation engine. Ensure the FastAPI server is running on port 8000.")
        return None
    except requests.exceptions.HTTPError as e:
        try:
            detail = resp.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        st.error(f"Calculation error: {detail}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def api_get(endpoint: str) -> Optional[Dict[str, Any]]:
    try:
        resp = requests.get(f"{API_BASE}{endpoint}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def region_selector(key_prefix: str = ""):
    """True 3-level hierarchical region selector.
    Level 1: Region (GCC / Europe / India / Australia)
    Level 2: Country / Emirate / State within region
    Level 3: Utility / Authority / DISCOM within country
    Returns (region_code, sub_code) — sub_code is the Level-3 authority code.
    Selections persist in st.session_state across pages.
    """
    col1, col2, col3 = st.columns(3)
    with col1:
        default_region = st.session_state.get("sel_region", list(REGIONS.keys())[0])
        try:
            default_idx = list(REGIONS.keys()).index(default_region)
        except ValueError:
            default_idx = 0
        region_label = st.selectbox(
            "Region",
            list(REGIONS.keys()),
            index=default_idx,
            key=f"{key_prefix}_region",
        )
        region_code = REGIONS[region_label]
        st.session_state["sel_region"] = region_label

    with col2:
        l2_opts = SUB_REGIONS_L2.get(region_code, {})
        default_l2 = st.session_state.get(f"sel_l2_{region_code}", list(l2_opts.keys())[0] if l2_opts else "")
        try:
            default_l2_idx = list(l2_opts.keys()).index(default_l2)
        except ValueError:
            default_l2_idx = 0
        l2_label = st.selectbox(
            "Country / State / Emirate",
            list(l2_opts.keys()),
            index=default_l2_idx,
            key=f"{key_prefix}_l2",
        )
        l2_code = l2_opts.get(l2_label, region_code)
        st.session_state[f"sel_l2_{region_code}"] = l2_label

    with col3:
        l3_opts = SUB_REGIONS_L3.get(l2_code, {})
        if l3_opts:
            default_l3 = st.session_state.get(f"sel_l3_{l2_code}", list(l3_opts.keys())[0])
            try:
                default_l3_idx = list(l3_opts.keys()).index(default_l3)
            except ValueError:
                default_l3_idx = 0
            l3_label = st.selectbox(
                "Utility / Authority",
                list(l3_opts.keys()),
                index=default_l3_idx,
                key=f"{key_prefix}_l3",
                help="Select the local utility/authority whose standards apply to this project.",
            )
            sub_code = l3_opts[l3_label]
            st.session_state[f"sel_l3_{l2_code}"] = l3_label
        else:
            sub_code = l2_code
            st.markdown(f"<span style='color:{LIGHT_GREY}; font-size:0.8rem;'>National standard applies</span>", unsafe_allow_html=True)

    return region_code, sub_code


def format_summary(summary: str) -> None:
    if summary:
        st.markdown(f"""
            <div style="background: {BLACK};
                        border: 1px solid {MID_GREY};
                        border-radius: 6px;
                        padding: 1rem;
                        font-family: monospace;
                        font-size: 0.8rem;
                        color: {WHITE};
                        white-space: pre-wrap;
                        overflow-x: auto;">
{summary}
            </div>
        """, unsafe_allow_html=True)
