"""
28_Branding.py — Company Branding Settings
Upload logo, letterhead, and digital stamp; set company name, engineer details,
footer text, and primary colour. All PDFs and ZIP packages will use these assets.
"""
import streamlit as st
import requests
import base64
from io import BytesIO

API = "http://localhost:3000/api"

st.set_page_config(page_title="Branding Settings", page_icon="🎨", layout="wide")
st.title("Company Branding Settings")
st.caption("Configure how your company appears on every PDF report and submission package.")

# ── Project selector ─────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def fetch_projects():
    try:
        r = requests.get(f"{API}/projects", timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        return []

projects = fetch_projects()
if not projects:
    st.warning("No projects found. Create a project first in the Project Workspace page.")
    st.stop()

options = {f"{p['name']} ({p['id'][:8]}…)": p["id"] for p in projects}
selection = st.selectbox("Project", list(options.keys()))
project_id = options[selection]

# ── Load current branding ─────────────────────────────────────────────────────
@st.cache_data(ttl=10)
def fetch_branding(pid):
    try:
        r = requests.get(f"{API}/projects/{pid}/branding", timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}

branding = fetch_branding(project_id)

st.markdown("---")

# ── Text fields ───────────────────────────────────────────────────────────────
st.subheader("Identity")
col_a, col_b = st.columns(2)
with col_a:
    company_name = st.text_input("Company Name", value=branding.get("companyName", ""))
    engineer_name = st.text_input("Engineer Name", value=branding.get("engineerName", ""))
with col_b:
    licence_number = st.text_input("Licence / Registration Number", value=branding.get("licenceNumber", ""))
    footer_text = st.text_input("Footer Text (on all PDFs)", value=branding.get("footerText", ""))

st.subheader("Primary Colour")
primary_color = st.color_picker(
    "Header background colour",
    value=branding.get("primaryColor", "#1a365d"),
)

if st.button("Save Identity & Colour", type="primary"):
    payload = {
        "companyName": company_name,
        "engineerName": engineer_name,
        "licenceNumber": licence_number,
        "footerText": footer_text,
        "primaryColor": primary_color,
    }
    try:
        r = requests.put(f"{API}/projects/{project_id}/branding", json=payload, timeout=10)
        r.raise_for_status()
        st.success("Branding saved successfully.")
        fetch_branding.clear()
    except Exception as exc:
        st.error(f"Failed to save: {exc}")

st.markdown("---")

# ── Image assets ──────────────────────────────────────────────────────────────
st.subheader("Image Assets")
st.caption("Upload PNG or JPG images (max 4 MB each). Images are stored securely per project.")

ASSET_CONFIG = {
    "logoBase64": {
        "label": "Company Logo",
        "hint": "Displayed top-right in all PDF headers.",
        "recommended": "Recommended: 300 × 80 px, transparent PNG.",
    },
    "letterheadBase64": {
        "label": "Letterhead / Watermark",
        "hint": "Used as a background band or header image where supported.",
        "recommended": "Recommended: Full A4 width, 1–2 cm tall, light PNG.",
    },
    "stampBase64": {
        "label": "Digital Stamp / Signature",
        "hint": "Placed on the sign-off block of the cover letter.",
        "recommended": "Recommended: 200 × 100 px, transparent PNG.",
    },
}

for field, cfg in ASSET_CONFIG.items():
    with st.expander(cfg["label"]):
        current_status = branding.get(field)
        if current_status == "[set]":
            st.success(f"{cfg['label']} is uploaded.")
        else:
            st.info(f"{cfg['label']} is not set.")

        st.caption(cfg["hint"])
        st.caption(cfg["recommended"])

        uploaded = st.file_uploader(
            f"Upload {cfg['label']}",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"upload_{field}",
        )
        col_u, col_d = st.columns([2, 1])
        with col_u:
            if uploaded and st.button(f"Save {cfg['label']}", key=f"save_{field}"):
                try:
                    files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
                    data = {"field": field}
                    r = requests.post(
                        f"{API}/projects/{project_id}/branding/upload",
                        files=files,
                        data=data,
                        timeout=30,
                    )
                    r.raise_for_status()
                    st.success(f"{cfg['label']} uploaded.")
                    fetch_branding.clear()
                    st.rerun()
                except Exception as exc:
                    st.error(f"Upload failed: {exc}")
        with col_d:
            if current_status == "[set]" and st.button(f"Remove", key=f"del_{field}"):
                try:
                    r = requests.delete(
                        f"{API}/projects/{project_id}/branding/{field}",
                        timeout=10,
                    )
                    r.raise_for_status()
                    st.success(f"{cfg['label']} removed.")
                    fetch_branding.clear()
                    st.rerun()
                except Exception as exc:
                    st.error(f"Remove failed: {exc}")

st.markdown("---")

# ── Live header preview ───────────────────────────────────────────────────────
st.subheader("PDF Header Preview")
st.caption("Approximate preview of how your header will look on generated PDFs.")

preview_company = company_name or "Your Company Name"
preview_color = primary_color
preview_engineer = engineer_name or "Engineer Name"
preview_licence = licence_number or "REG-0000"
preview_footer = footer_text or "Generated by OpenMEP Submission Packager"

header_html = f"""
<div style="background:{preview_color}; padding:12px 20px; border-radius:4px 4px 0 0; display:flex; justify-content:space-between; align-items:center;">
  <div>
    <div style="color:white; font-size:20px; font-weight:bold; font-family:sans-serif;">{preview_company}</div>
    <div style="color:rgba(255,255,255,0.75); font-size:11px; font-family:sans-serif;">Engineering Submission System</div>
  </div>
  <div style="text-align:right;">
    <div style="color:white; font-size:14px; font-weight:bold; font-family:sans-serif;">SUBMISSION COVER LETTER</div>
    <div style="color:rgba(255,255,255,0.75); font-size:11px; font-family:sans-serif;">PRJ-2026-001</div>
  </div>
</div>
<div style="background:#2b6cb0; height:3px; border-radius:0 0 2px 2px;"></div>
<div style="padding:10px 20px; font-size:11px; color:#718096; font-family:sans-serif; border:1px solid #e2e8f0; border-top:none; border-radius:0 0 4px 4px;">
  <span>{preview_footer}</span>
  <span style="float:right;">2026-04-09</span>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

st.markdown("---")
st.info(
    "Once branding is set here, go to **Submission Packager** and enter the same **Project ID** "
    "to have your branding automatically applied to all PDFs in the ZIP package. "
    "Report templates (module selection and cover intro) can be configured in the "
    "**Report Templates** page."
)
