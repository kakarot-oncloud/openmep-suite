"""
29_Report_Templates.py — Report Templates
Create and manage named report templates that control which modules are included,
page order, and the cover page introduction text. Templates are applied when
generating submission packages.
"""
import streamlit as st
import requests

API = "http://localhost:3000/api"

AVAILABLE_MODULES = ["electrical", "hvac", "fire_protection", "plumbing", "structural"]

st.set_page_config(page_title="Report Templates", page_icon="📄", layout="wide")
st.title("Report Templates")
st.caption(
    "Save named templates that control which modules to include and in what order, "
    "plus a custom cover page introduction. Apply a template when generating a submission package."
)

# ── Project selector ──────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def fetch_projects():
    try:
        r = requests.get(f"{API}/projects", timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []

projects = fetch_projects()
if not projects:
    st.warning("No projects found. Create a project first in the Project Workspace page.")
    st.stop()

options = {f"{p['name']} ({p['id'][:8]}…)": p["id"] for p in projects}
selection = st.selectbox("Project", list(options.keys()))
project_id = options[selection]

# ── Load templates ────────────────────────────────────────────────────────────
@st.cache_data(ttl=10)
def fetch_templates(pid):
    try:
        r = requests.get(f"{API}/projects/{pid}/templates", timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []

templates = fetch_templates(project_id)

st.markdown("---")

# ── Create new template ───────────────────────────────────────────────────────
st.subheader("Create New Template")

with st.form("new_template_form", clear_on_submit=True):
    tpl_name = st.text_input("Template Name", placeholder="e.g. DEWA Full Submission")

    st.write("Included Modules (check to include, order determines page sequence):")
    module_cols = st.columns(len(AVAILABLE_MODULES))
    selected_modules = []
    for i, mod in enumerate(AVAILABLE_MODULES):
        with module_cols[i]:
            if st.checkbox(mod.replace("_", " ").title(), key=f"new_mod_{mod}"):
                selected_modules.append(mod)

    cover_intro = st.text_area(
        "Cover Page Introduction",
        placeholder="Optional: custom introduction text for the cover letter...",
        height=100,
    )

    submitted = st.form_submit_button("Create Template", type="primary")
    if submitted:
        if not tpl_name.strip():
            st.error("Template name is required.")
        else:
            try:
                payload = {
                    "name": tpl_name.strip(),
                    "includedModules": selected_modules,
                    "coverIntro": cover_intro.strip() if cover_intro.strip() else None,
                }
                r = requests.post(
                    f"{API}/projects/{project_id}/templates",
                    json=payload,
                    timeout=10,
                )
                r.raise_for_status()
                st.success(f"Template '{tpl_name}' created.")
                fetch_templates.clear()
                st.rerun()
            except Exception as exc:
                st.error(f"Failed to create template: {exc}")

st.markdown("---")

# ── Existing templates ────────────────────────────────────────────────────────
st.subheader("Saved Templates")

if not templates:
    st.info("No templates yet. Create one above.")
else:
    for tpl in templates:
        with st.expander(f"📄 {tpl['name']}  (ID: `{tpl['id'][:8]}…`)"):
            st.caption(f"Created: {tpl['createdAt'][:10]}   Updated: {tpl['updatedAt'][:10]}")

            modules_str = ", ".join(tpl.get("includedModules", [])) if tpl.get("includedModules") else "All modules"
            st.write(f"**Included Modules:** {modules_str}")

            if tpl.get("coverIntro"):
                st.write("**Cover Intro:**")
                st.info(tpl["coverIntro"])

            st.write(f"**Template ID for submission packager:** `{tpl['id']}`")

            with st.form(f"edit_{tpl['id']}"):
                st.write("Edit Template")
                new_name = st.text_input("Name", value=tpl["name"], key=f"name_{tpl['id']}")
                st.write("Included Modules:")
                edit_cols = st.columns(len(AVAILABLE_MODULES))
                edit_modules = []
                for i, mod in enumerate(AVAILABLE_MODULES):
                    with edit_cols[i]:
                        checked = mod in (tpl.get("includedModules") or [])
                        if st.checkbox(
                            mod.replace("_", " ").title(),
                            value=checked,
                            key=f"edit_mod_{tpl['id']}_{mod}",
                        ):
                            edit_modules.append(mod)
                new_intro = st.text_area(
                    "Cover Intro",
                    value=tpl.get("coverIntro", ""),
                    height=80,
                    key=f"intro_{tpl['id']}",
                )
                col_save, col_del = st.columns([3, 1])
                with col_save:
                    if st.form_submit_button("Save Changes"):
                        try:
                            payload = {
                                "name": new_name.strip(),
                                "includedModules": edit_modules,
                                "coverIntro": new_intro.strip() if new_intro.strip() else None,
                            }
                            r = requests.put(
                                f"{API}/projects/{project_id}/templates/{tpl['id']}",
                                json=payload,
                                timeout=10,
                            )
                            r.raise_for_status()
                            st.success("Template updated.")
                            fetch_templates.clear()
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Update failed: {exc}")
                with col_del:
                    if st.form_submit_button("Delete", type="secondary"):
                        try:
                            r = requests.delete(
                                f"{API}/projects/{project_id}/templates/{tpl['id']}",
                                timeout=10,
                            )
                            r.raise_for_status()
                            st.success("Template deleted.")
                            fetch_templates.clear()
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Delete failed: {exc}")

st.markdown("---")
st.info(
    "**How to use a template:** In the Submission Packager page, provide the Template ID "
    "(shown above) in the 'Template ID' field. The packager will use the template's module "
    "selection. Your branding from the Branding Settings page is applied automatically "
    "when a Project ID is provided."
)
