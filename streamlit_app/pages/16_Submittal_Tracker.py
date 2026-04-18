"""Submittal Tracker — OpenMEP"""

import streamlit as st
import sys
import os
import io
import pandas as pd
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_theme_css, RED, BLACK, WHITE, DARK_GREY, LIGHT_GREY,
    page_header, section_title
)

st.set_page_config(page_title="Submittal Tracker — OpenMEP", page_icon="📎", layout="wide")
apply_theme_css()

page_header("Submittal Tracker", "MEP submittal log, RFI tracker, and equipment schedule manager", "📎")

STATUS_COLORS = {
    "Approved": "#00AA44",
    "Approved with Comments": "#FF8800",
    "Pending Review": "#0066CC",
    "Rejected": RED,
    "Superseded": "#888888",
    "Returned for Resubmission": "#CC4400",
}

PROCUREMENT_STATUSES = ["Pending", "Submitted", "Approved", "On Order", "Delivered", "Installed", "Commissioned"]
RFI_STATUSES = ["Pending", "Under Review", "Answered", "Closed"]
DISCIPLINES = ["Electrical", "HVAC", "Plumbing", "Fire", "Civil", "Structural"]

# ── Session state initialisation ───────────────────────────────────────────────
if "submittals" not in st.session_state:
    st.session_state.submittals = [
        {"ref": "SUB-E-001", "discipline": "Electrical", "description": "Main LV Switchboard — Technical Submittal", "submitted_date": "2024-01-15", "status": "Approved", "remarks": "Rev B approved."},
        {"ref": "SUB-E-002", "discipline": "Electrical", "description": "Transformer T01, T02 — Data Sheets", "submitted_date": "2024-01-20", "status": "Pending Review", "remarks": ""},
        {"ref": "SUB-M-001", "discipline": "HVAC", "description": "Chiller Plant — Technical Data Sheet", "submitted_date": "2024-01-18", "status": "Approved with Comments", "remarks": "EER to be confirmed with IFC"},
        {"ref": "SUB-P-001", "discipline": "Plumbing", "description": "Cold Water Booster Pump Set", "submitted_date": "2024-01-22", "status": "Pending Review", "remarks": ""},
        {"ref": "SUB-F-001", "discipline": "Fire", "description": "Sprinkler Head — Pentair VSR K80", "submitted_date": "2024-01-12", "status": "Approved", "remarks": "FM approved listing confirmed"},
    ]

if "rfis" not in st.session_state:
    st.session_state.rfis = [
        {"ref": "RFI-001", "discipline": "Electrical", "subject": "Cable route conflict at riser shaft B2", "raised_by": "MEP Contractor", "date_raised": "2024-02-01", "status": "Answered", "response": "Re-route via revised drawing E-042 Rev C"},
        {"ref": "RFI-002", "discipline": "HVAC", "subject": "AHU-L4-01 clearance for maintenance access", "raised_by": "MEP Contractor", "date_raised": "2024-02-05", "status": "Pending", "response": ""},
        {"ref": "RFI-003", "discipline": "Plumbing", "subject": "Cold water tank material specification", "raised_by": "Plumbing Contractor", "date_raised": "2024-02-08", "status": "Answered", "response": "GRP to BS 6920, grey colour"},
    ]

if "equipment" not in st.session_state:
    st.session_state.equipment = [
        {"tag": "T-01", "discipline": "Electrical", "description": "HV/LV Transformer", "make": "ABB", "model": "TMC 1000-11/0.4kV", "rating": "1000 kVA, Dyn11", "location": "Main Substation", "status": "On Order"},
        {"tag": "MDB-01", "discipline": "Electrical", "description": "Main Distribution Board", "make": "Schneider", "model": "Prisma G", "rating": "4000A, ACB, 415V", "location": "Substation LV Room", "status": "Submitted"},
        {"tag": "CH-01", "discipline": "HVAC", "description": "Air-Cooled Chiller", "make": "Carrier", "model": "30XA-402", "rating": "400TR, R134a", "location": "Roof Level 21", "status": "Approved"},
        {"tag": "FP-01", "discipline": "Fire", "description": "Electric Fire Pump", "make": "Grundfos", "model": "NK 100-250/268", "rating": "750 L/min, 70m", "location": "Fire Pump Room B1", "status": "Approved"},
        {"tag": "AHU-L3-01", "discipline": "HVAC", "description": "Air Handling Unit", "make": "Systemair", "model": "VEX 190", "rating": "15,000 m³/h, DX coil", "location": "L3 AHU Room", "status": "Pending"},
    ]

tabs = st.tabs(["📋 Submittals", "❓ RFIs", "🔧 Equipment Schedule"])

# ── Submittals Tab ─────────────────────────────────────────────────────────────
with tabs[0]:
    section_title("Submittal Log")

    col1, col2 = st.columns([4, 1])
    with col1:
        filter_disc_s = st.multiselect("Filter by Discipline", DISCIPLINES[:4], default=DISCIPLINES[:4], key="fds")
    with col2:
        filter_status_s = st.selectbox("Status Filter", ["All"] + list(STATUS_COLORS.keys()), key="fss")

    filtered_s = [s for s in st.session_state.submittals
                  if s["discipline"] in filter_disc_s and
                  (filter_status_s == "All" or s["status"] == filter_status_s)]

    if filtered_s:
        st.dataframe(pd.DataFrame(filtered_s), use_container_width=True, hide_index=True)

    section_title("Edit / Update Submittal Status")
    st.markdown(f"<span style='color:{LIGHT_GREY}; font-size:0.85rem;'>Select a submittal by reference to update its status or remarks inline.</span>", unsafe_allow_html=True)

    sub_refs = [s["ref"] for s in st.session_state.submittals]
    edit_ref = st.selectbox("Select Submittal to Edit", ["— select —"] + sub_refs, key="edit_sub_ref")
    if edit_ref != "— select —":
        idx = next((i for i, s in enumerate(st.session_state.submittals) if s["ref"] == edit_ref), None)
        if idx is not None:
            record = st.session_state.submittals[idx]
            with st.form(f"edit_sub_{edit_ref}"):
                ec1, ec2, ec3 = st.columns(3)
                with ec1:
                    new_disc = st.selectbox("Discipline", DISCIPLINES, index=DISCIPLINES.index(record["discipline"]) if record["discipline"] in DISCIPLINES else 0)
                    new_desc = st.text_input("Description", value=record["description"])
                with ec2:
                    new_date = st.text_input("Submitted Date (YYYY-MM-DD)", value=record["submitted_date"])
                    new_status = st.selectbox("Status", list(STATUS_COLORS.keys()),
                                              index=list(STATUS_COLORS.keys()).index(record["status"]) if record["status"] in STATUS_COLORS else 0)
                with ec3:
                    new_remarks = st.text_area("Remarks / Review Comments", value=record.get("remarks", ""), height=100)
                c_save, c_del = st.columns(2)
                with c_save:
                    if st.form_submit_button("💾 Save Changes"):
                        st.session_state.submittals[idx] = {
                            "ref": edit_ref, "discipline": new_disc, "description": new_desc,
                            "submitted_date": new_date, "status": new_status, "remarks": new_remarks,
                        }
                        st.success(f"Submittal {edit_ref} updated to '{new_status}'")
                        st.rerun()
                with c_del:
                    if st.form_submit_button("🗑 Delete Submittal"):
                        st.session_state.submittals.pop(idx)
                        st.success(f"Submittal {edit_ref} deleted.")
                        st.rerun()

    section_title("Add New Submittal")
    with st.form("add_submittal"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_ref = st.text_input("Reference No.", placeholder="SUB-E-010")
            new_disc = st.selectbox("Discipline", DISCIPLINES[:4])
        with col2:
            new_desc = st.text_input("Description", placeholder="Equipment datasheet, material submittal, etc.")
            new_date = st.date_input("Submitted Date", value=date.today())
        with col3:
            new_status = st.selectbox("Status", list(STATUS_COLORS.keys()))
            new_remarks = st.text_input("Remarks", placeholder="Review comments")
        if st.form_submit_button("Add Submittal"):
            st.session_state.submittals.append({
                "ref": new_ref, "discipline": new_disc, "description": new_desc,
                "submitted_date": str(new_date), "status": new_status, "remarks": new_remarks,
            })
            st.rerun()

    if st.button("Export Submittals to Excel", key="exp_sub"):
        buf = io.BytesIO()
        pd.DataFrame(st.session_state.submittals).to_excel(buf, index=False, sheet_name="Submittals")
        buf.seek(0)
        st.download_button("⬇️ Download Submittal Log", data=buf.getvalue(),
                           file_name=f"Submittal_Log_{date.today()}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── RFIs Tab ──────────────────────────────────────────────────────────────────
with tabs[1]:
    section_title("RFI Log — Request for Information")
    if st.session_state.rfis:
        st.dataframe(pd.DataFrame(st.session_state.rfis), use_container_width=True, hide_index=True)

    section_title("Edit / Answer Existing RFI")
    rfi_refs = [r["ref"] for r in st.session_state.rfis]
    edit_rfi_ref = st.selectbox("Select RFI to Edit", ["— select —"] + rfi_refs, key="edit_rfi_ref")
    if edit_rfi_ref != "— select —":
        ridx = next((i for i, r in enumerate(st.session_state.rfis) if r["ref"] == edit_rfi_ref), None)
        if ridx is not None:
            rrecord = st.session_state.rfis[ridx]
            with st.form(f"edit_rfi_{edit_rfi_ref}"):
                rc1, rc2 = st.columns(2)
                with rc1:
                    r_disc = st.selectbox("Discipline", DISCIPLINES,
                                          index=DISCIPLINES.index(rrecord["discipline"]) if rrecord["discipline"] in DISCIPLINES else 0)
                    r_subject = st.text_input("Subject", value=rrecord["subject"])
                    r_by = st.text_input("Raised By", value=rrecord["raised_by"])
                with rc2:
                    r_date = st.text_input("Date Raised (YYYY-MM-DD)", value=rrecord["date_raised"])
                    r_status = st.selectbox("Status", RFI_STATUSES,
                                            index=RFI_STATUSES.index(rrecord["status"]) if rrecord["status"] in RFI_STATUSES else 0)
                    r_response = st.text_area("Response / Answer", value=rrecord.get("response", ""), height=80)
                rs1, rs2 = st.columns(2)
                with rs1:
                    if st.form_submit_button("💾 Save RFI Changes"):
                        st.session_state.rfis[ridx] = {
                            "ref": edit_rfi_ref, "discipline": r_disc, "subject": r_subject,
                            "raised_by": r_by, "date_raised": r_date, "status": r_status, "response": r_response,
                        }
                        st.success(f"RFI {edit_rfi_ref} updated to '{r_status}'")
                        st.rerun()
                with rs2:
                    if st.form_submit_button("🗑 Delete RFI"):
                        st.session_state.rfis.pop(ridx)
                        st.success(f"RFI {edit_rfi_ref} deleted.")
                        st.rerun()

    section_title("Raise New RFI")
    with st.form("add_rfi"):
        col1, col2 = st.columns(2)
        with col1:
            rfi_ref = st.text_input("RFI Reference", placeholder="RFI-004")
            rfi_disc = st.selectbox("Discipline", DISCIPLINES)
            rfi_subject = st.text_input("Subject / Query")
        with col2:
            rfi_by = st.text_input("Raised By", placeholder="Contractor / Sub-contractor name")
            rfi_date = st.date_input("Date Raised", value=date.today())
            rfi_status = st.selectbox("Status", RFI_STATUSES)
        rfi_response = st.text_area("Response (if answered)", height=80)
        if st.form_submit_button("Add RFI"):
            st.session_state.rfis.append({
                "ref": rfi_ref, "discipline": rfi_disc, "subject": rfi_subject,
                "raised_by": rfi_by, "date_raised": str(rfi_date),
                "status": rfi_status, "response": rfi_response,
            })
            st.rerun()

    if st.button("Export RFI Log to Excel", key="exp_rfi"):
        buf = io.BytesIO()
        pd.DataFrame(st.session_state.rfis).to_excel(buf, index=False, sheet_name="RFIs")
        buf.seek(0)
        st.download_button("⬇️ Download", data=buf.getvalue(), file_name=f"RFI_Log_{date.today()}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── Equipment Schedule Tab ─────────────────────────────────────────────────────
with tabs[2]:
    section_title("MEP Equipment Schedule")
    if st.session_state.equipment:
        st.dataframe(pd.DataFrame(st.session_state.equipment), use_container_width=True, hide_index=True)

    section_title("Edit / Update Equipment Status")
    eq_tags = [e["tag"] for e in st.session_state.equipment]
    edit_eq_tag = st.selectbox("Select Equipment Tag to Edit", ["— select —"] + eq_tags, key="edit_eq_tag")
    if edit_eq_tag != "— select —":
        eidx = next((i for i, e in enumerate(st.session_state.equipment) if e["tag"] == edit_eq_tag), None)
        if eidx is not None:
            erecord = st.session_state.equipment[eidx]
            with st.form(f"edit_eq_{edit_eq_tag}"):
                ec1, ec2, ec3 = st.columns(3)
                with ec1:
                    e_disc = st.selectbox("Discipline", DISCIPLINES[:4],
                                          index=DISCIPLINES[:4].index(erecord["discipline"]) if erecord["discipline"] in DISCIPLINES[:4] else 0)
                    e_desc = st.text_input("Description", value=erecord["description"])
                with ec2:
                    e_make = st.text_input("Manufacturer", value=erecord["make"])
                    e_model = st.text_input("Model / Type", value=erecord["model"])
                    e_rating = st.text_input("Rating / Capacity", value=erecord["rating"])
                with ec3:
                    e_loc = st.text_input("Location", value=erecord["location"])
                    e_status = st.selectbox("Procurement Status", PROCUREMENT_STATUSES,
                                            index=PROCUREMENT_STATUSES.index(erecord["status"]) if erecord["status"] in PROCUREMENT_STATUSES else 0)
                es1, es2 = st.columns(2)
                with es1:
                    if st.form_submit_button("💾 Save Equipment Changes"):
                        st.session_state.equipment[eidx] = {
                            "tag": edit_eq_tag, "discipline": e_disc, "description": e_desc,
                            "make": e_make, "model": e_model, "rating": e_rating,
                            "location": e_loc, "status": e_status,
                        }
                        st.success(f"Equipment {edit_eq_tag} updated to '{e_status}'")
                        st.rerun()
                with es2:
                    if st.form_submit_button("🗑 Delete Equipment"):
                        st.session_state.equipment.pop(eidx)
                        st.success(f"Equipment {edit_eq_tag} deleted.")
                        st.rerun()

    section_title("Add Equipment Item")
    with st.form("add_equipment"):
        col1, col2, col3 = st.columns(3)
        with col1:
            eq_tag = st.text_input("Equipment Tag", placeholder="T-03, AHU-L5-01")
            eq_disc = st.selectbox("Discipline", DISCIPLINES[:4])
            eq_desc = st.text_input("Description")
        with col2:
            eq_make = st.text_input("Manufacturer")
            eq_model = st.text_input("Model / Type")
            eq_rating = st.text_input("Rating / Capacity")
        with col3:
            eq_loc = st.text_input("Location")
            eq_status = st.selectbox("Procurement Status", PROCUREMENT_STATUSES)

        if st.form_submit_button("Add Equipment"):
            st.session_state.equipment.append({
                "tag": eq_tag, "discipline": eq_disc, "description": eq_desc,
                "make": eq_make, "model": eq_model, "rating": eq_rating,
                "location": eq_loc, "status": eq_status,
            })
            st.rerun()

    if st.button("Export Equipment Schedule to Excel", key="exp_eq"):
        buf = io.BytesIO()
        pd.DataFrame(st.session_state.equipment).to_excel(buf, index=False, sheet_name="Equipment Schedule")
        buf.seek(0)
        st.download_button("⬇️ Download", data=buf.getvalue(), file_name=f"Equipment_Schedule_{date.today()}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
