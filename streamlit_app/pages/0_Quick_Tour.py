"""Quick Tour — OpenMEP Visual Walkthrough"""

import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, page_header,
    NAVY, TEAL, TEAL_L, WHITE, SILVER, RED, MID_GREY,
)

st.set_page_config(page_title="Quick Tour — OpenMEP", page_icon="🗺", layout="wide")
apply_theme_css()

page_header("Quick Tour", "A 5-screen visual walkthrough — see OpenMEP before running a single calculation", "🗺")

SCREENSHOTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "docs", "screenshots"
)

def tour_card(step: int, title: str, tag: str, description: str, insight: str, img_filename: str):
    st.markdown(f"""
    <div style="
        background: {MID_GREY};
        border: 1px solid {TEAL}22;
        border-radius: 12px;
        padding: 1.5rem 2rem 1rem 2rem;
        margin-bottom: 0.5rem;
    ">
        <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:0.5rem;">
            <span style="
                background: {TEAL};
                color: {NAVY};
                font-weight: 800;
                font-size: 0.78rem;
                padding: 0.2rem 0.65rem;
                border-radius: 999px;
                letter-spacing: 0.04em;
            ">STEP {step}</span>
            <span style="
                background: {TEAL}18;
                color: {TEAL_L};
                font-size: 0.73rem;
                padding: 0.15rem 0.6rem;
                border-radius: 999px;
                border: 1px solid {TEAL}33;
            ">{tag}</span>
        </div>
        <h3 style="color:{WHITE}; margin: 0.25rem 0 0.6rem 0; font-size:1.25rem;">{title}</h3>
        <p style="color:{SILVER}; font-size:0.92rem; line-height:1.65; margin:0;">{description}</p>
    </div>
    """, unsafe_allow_html=True)

    img_path = os.path.join(SCREENSHOTS_DIR, img_filename)
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        st.warning(f"Screenshot not found: {img_filename}")

    st.markdown(f"""
    <div style="
        background: {TEAL}12;
        border-left: 3px solid {TEAL};
        border-radius: 0 8px 8px 0;
        padding: 0.65rem 1rem;
        margin: 0.5rem 0 2rem 0;
        color: {SILVER};
        font-size: 0.85rem;
        line-height: 1.6;
    ">💡 {insight}</div>
    """, unsafe_allow_html=True)


tour_card(
    step=1,
    title="Dashboard — All 26 Modules at a Glance",
    tag="Landing Page",
    description=(
        "The home screen groups every calculator into five disciplines — "
        "Electrical (9), Mechanical/HVAC (4), Plumbing (6), Fire Protection (4), "
        "and Reports & Compliance (3). Each card shows the applicable standard so you "
        "know immediately whether the tool covers your project region."
    ),
    insight=(
        "Pick a module from the sidebar or click any discipline card to jump straight "
        "to that calculator. The live API status indicator at the top right confirms the "
        "backend is connected."
    ),
    img_filename="dashboard_module_grid.png",
)

tour_card(
    step=2,
    title="HVAC — Cooling Load Calculator (GCC Zone)",
    tag="Mechanical / HVAC",
    description=(
        "A real ASHRAE cooling load for a 250 m² Dubai office zone — west-facing, "
        "46°C ODB. The tool breaks out every heat gain component: solar, conduction, "
        "occupants, lighting, equipment, and ventilation. Applies the 1.1 safety factor "
        "and outputs 56.14 kW (15.96 TR) with an ASHRAE 90.1-2022 / DEWA compliance stamp."
    ),
    insight=(
        "Supply airflow, fresh air rate, and chiller power are all calculated simultaneously. "
        "Switch the region selector to Europe and the same room recalculates to EN 12831 — "
        "a completely different result because of different design conditions."
    ),
    img_filename="hvac_cooling_load_result.png",
)

tour_card(
    step=3,
    title="PDF Calculation Report — Letterhead, Workings & Sign-off",
    tag="Reports & Compliance",
    description=(
        "Every calculation can be exported to a professional A4 PDF in seconds. "
        "The report includes a project letterhead, design basis table, step-by-step "
        "calculation workings, a results summary block, and a sign-off section with "
        "approval stamp — ready to hand to a client or submit for authority approval."
    ),
    insight=(
        "The report is generated entirely server-side using ReportLab — no Word, "
        "no Excel, no external services. The same PDF structure is used for all 26 "
        "modules so your submittal packages look consistent across disciplines."
    ),
    img_filename="pdf_report_page.png",
)

tour_card(
    step=4,
    title="4-Region Comparison — Same Load, Four Different Answers",
    tag="Multi-Region",
    description=(
        "Run the same 30 kW three-phase load through all four regional standards "
        "databases and immediately see how ambient temperature, correction factors, "
        "and voltage drop limits differ by region. GCC and India both land on 10 mm². "
        "Europe technically fits 6 mm² on current capacity but fails the 5% voltage "
        "drop limit — so the engineer must upsize. Australia reaches the same 10 mm² "
        "conclusion via different tables."
    ),
    insight=(
        "This view is unique to OpenMEP — no commercial tool lets you compare all four "
        "regional standards side-by-side in a single run. Useful for multinational "
        "projects or checking whether a design that passes in one region is compliant in another."
    ),
    img_filename="four_region_comparison.png",
)

tour_card(
    step=5,
    title="Cable Sizing — Full BS 7671 Result with Derating Chain",
    tag="Electrical",
    description=(
        "45 kW motor, 80 m run, 40°C ambient. Selects 16 mm² XLPE copper "
        "(Iz = 92.8 A ≥ Ib = 76.4 A ✓), calculates voltage drop at 4.28% — "
        "within the 5% BS 7671 limit ✓ — and outputs protection device size, "
        "earth conductor size, and full compliance statements. Every derating "
        "factor (Ca, Cg, Ci) is shown with its source table reference."
    ),
    insight=(
        "All numerical tables — BS 7671 Table 4D5A, IS 3961, AS/NZS 3008 — are "
        "embedded directly in the code. There are no external database calls, "
        "no API keys required, and results are reproducible offline."
    ),
    img_filename="cable_sizing_result.png",
)

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, {TEAL}22 0%, {MID_GREY} 100%);
    border: 1px solid {TEAL}44;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    margin-top: 1rem;
">
    <h3 style="color:{WHITE}; margin: 0 0 0.5rem 0;">Ready to run your first calculation?</h3>
    <p style="color:{SILVER}; font-size:0.95rem; margin: 0 0 1rem 0;">
        Pick any module from the sidebar — region, inputs, result, and PDF export in under a minute.
    </p>
    <div style="display:flex; justify-content:center; gap:1.5rem; flex-wrap:wrap;">
        <div style="background:{TEAL}22; border:1px solid {TEAL}44; border-radius:8px; padding:0.5rem 1.25rem; color:{TEAL_L}; font-size:0.85rem;">
            ⚡ Electrical → Cable Sizing
        </div>
        <div style="background:{TEAL}22; border:1px solid {TEAL}44; border-radius:8px; padding:0.5rem 1.25rem; color:{TEAL_L}; font-size:0.85rem;">
            ❄️ HVAC → Cooling Load
        </div>
        <div style="background:{TEAL}22; border:1px solid {TEAL}44; border-radius:8px; padding:0.5rem 1.25rem; color:{TEAL_L}; font-size:0.85rem;">
            💧 Plumbing → Pipe Sizing
        </div>
        <div style="background:{TEAL}22; border:1px solid {TEAL}44; border-radius:8px; padding:0.5rem 1.25rem; color:{TEAL_L}; font-size:0.85rem;">
            🔥 Fire → Sprinkler Design
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

with st.expander("About the screenshots"):
    st.markdown(f"""
    <p style="color:{SILVER}; font-size:0.85rem; line-height:1.7;">
    All screenshots show real output from live OpenMEP calculations — no mock data, no post-processing.
    The HVAC result (56.14 kW / 15.96 TR) and cable sizing result (16 mm² at 4.28% VD) were produced
    by running the same inputs shown in the captions against the live FastAPI backend.
    Source files: <code>docs/screenshots/</code> in the repository.
    </p>
    """, unsafe_allow_html=True)
