import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    api_delete,
    api_get,
    api_post,
    apply_theme_css,
    page_header,
    region_selector,
    section_title,
)

st.set_page_config(page_title="Projects — OpenMEP", page_icon="🗂️", layout="wide")
apply_theme_css()

page_header("Project Workspaces",
            "Persistent projects with a shared design basis and saved calculation results", "🗂️")

# ── Create a project ──────────────────────────────────────────────────────────
with st.expander("➕ New project", expanded=False):
    section_title("Design Basis")
    region, sub_region = region_selector("proj")
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Project name", value="")
        client = st.text_input("Client", value="")
    with c2:
        number = st.text_input("Project number", value="")
        location = st.text_input("Location", value="")
    c3, c4 = st.columns(2)
    with c3:
        ambient = st.number_input("Design ambient °C", value=45.0, step=1.0)
    with c4:
        pf = st.number_input("Design power factor", min_value=0.1, max_value=1.0, value=0.85, step=0.01)

    if st.button("Create project", type="primary"):
        if not name.strip():
            st.warning("Project name is required.")
        else:
            created = api_post("/api/projects", {
                "name": name, "client": client, "location": location, "project_number": number,
                "design_basis": {"region": region, "sub_region": sub_region,
                                 "ambient_temp_c": ambient, "power_factor": pf},
            })
            if created:
                st.success(f"Created {created['name']} ({created['id']})")
                st.rerun()

# ── Project list ──────────────────────────────────────────────────────────────
section_title("Projects")
data = api_get("/api/projects")
if data is None:
    st.stop()

projects = data.get("projects", [])
if not projects:
    st.info("No projects yet — create one above.")
    st.stop()

df = pd.DataFrame([{
    "ID": p["id"], "Name": p["name"], "Client": p["client"],
    "Region": p["design_basis"].get("region", ""), "Results": p["result_count"],
    "Updated": p["updated_at"],
} for p in projects])
st.dataframe(df, use_container_width=True, hide_index=True)

# ── Inspect a project ─────────────────────────────────────────────────────────
labels = {f"{p['name']} · {p['id']}": p["id"] for p in projects}
choice = st.selectbox("Open a project", list(labels.keys()))
pid = labels[choice]
proj = next(p for p in projects if p["id"] == pid)

section_title("Design Basis")
st.json(proj["design_basis"])

section_title("Saved Results")
res = api_get(f"/api/projects/{pid}/results")
if res and res["count"]:
    st.dataframe(
        pd.DataFrame([{
            "ID": r["id"], "Module": r["module"], "Title": r["title"],
            "Compliant": "✅" if r["compliant"] else "❌", "Saved": r["created_at"],
        } for r in res["results"]]),
        use_container_width=True, hide_index=True,
    )
else:
    st.caption("No results saved to this project yet.")

if st.button("🗑️ Delete this project", type="secondary"):
    if api_delete(f"/api/projects/{pid}"):
        st.success("Project deleted.")
        st.rerun()
