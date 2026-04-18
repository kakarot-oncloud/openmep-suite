import streamlit as st
import pandas as pd
import requests
from datetime import datetime

API_BASE = "http://localhost:8080/api"

st.set_page_config(page_title="Version History", page_icon="🕰️", layout="wide")
st.title("🕰️ Version History & Change Comparison")
st.markdown(
    "Browse auto-snapshots of your project, compare any two versions side-by-side "
    "across project fields, engineering results, compliance pass/fail checks, and "
    "BOQ cost estimates — then restore an earlier design in one click."
)

# ─── Semantic color helpers ────────────────────────────────────────────────────
LOWER_BETTER_CALC = {
    "Total Lighting Load",
    "Total Equipment Load",
    "Estimated Envelope Heat Gain",
    "Estimated Riser Length",
}
HIGHER_BETTER_CALC = {
    "Total Fresh Air Flow",
}

LOWER_BETTER_FIELDS: set[str] = set()
HIGHER_BETTER_FIELDS: set[str] = set()


def _delta_color(delta, lower_better=False, higher_better=False):
    """Return background CSS color based on delta and metric direction."""
    if delta is None or delta == 0:
        return "#f8f9fa"
    improved = (delta < 0 and lower_better) or (delta > 0 and higher_better)
    degraded = (delta > 0 and lower_better) or (delta < 0 and higher_better)
    if improved:
        return "#d4edda"
    if degraded:
        return "#f8d7da"
    return "#fff3cd"


def _sign(x):
    return "+" if x > 0 else ""


# ─── Data fetchers ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=5)
def fetch_projects():
    try:
        r = requests.get(f"{API_BASE}/projects", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Could not load projects: {e}")
        return []


@st.cache_data(ttl=5)
def fetch_versions(pid):
    try:
        r = requests.get(f"{API_BASE}/projects/{pid}/versions", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Could not load versions: {e}")
        return {}


projects = fetch_projects()
if not projects:
    st.warning("No projects found. Create one in the Project Workspace page first.")
    st.stop()

project_options = {f"{p['name']} ({p['id'][:8]}...)": p["id"] for p in projects}
selected_label = st.selectbox("Select project", list(project_options.keys()))
project_id = project_options[selected_label]

version_data = fetch_versions(project_id)
versions = version_data.get("versions", [])

if not versions:
    st.info("No version history yet — save or update the project to create snapshots.")
    st.stop()

# ─── Version timeline ──────────────────────────────────────────────────────────
st.subheader(f"Version timeline — {version_data.get('projectName', '')}")
st.markdown(f"**{len(versions)}** snapshot(s) recorded")

rows = []
for v in reversed(versions):
    ts = v.get("timestamp", "")
    try:
        ts_fmt = datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
    except Exception:
        ts_fmt = ts[:19]
    err = v.get("complianceErrorCount", 0)
    warn = v.get("complianceWarningCount", 0)
    if err > 0:
        compliance_cell = f"🔴 {err} error(s)"
    elif warn > 0:
        compliance_cell = f"🟡 {warn} warning(s)"
    else:
        compliance_cell = "✅ Pass"
    currency = v.get("boqCurrency", "")
    rows.append({
        "Version": f"v{v['version']}",
        "Saved At": ts_fmt,
        "Compliance": compliance_cell,
        f"BOQ Total ({currency})": f"{v.get('boqGrandTotal', 0):,.0f}",
        "Summary": v.get("summary", "")[:120],
    })

st.dataframe(rows, use_container_width=True, hide_index=True)

# ─── Side-by-side compare ──────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Compare two versions")

version_nums = [v["version"] for v in versions]
col_from, col_to = st.columns(2)
with col_from:
    from_v = st.selectbox("From version", version_nums, index=0, key="from_ver")
with col_to:
    to_v = st.selectbox("To version", version_nums, index=min(1, len(version_nums) - 1), key="to_ver")

if st.button("🔍 Compare versions", type="primary", disabled=(from_v == to_v)):
    try:
        r = requests.get(
            f"{API_BASE}/projects/{project_id}/compare?from={from_v}&to={to_v}",
            timeout=15,
        )
        r.raise_for_status()
        diff = r.json()
    except Exception as e:
        st.error(f"Compare failed: {e}")
        st.stop()

    st.markdown(f"**v{from_v} summary:** {diff.get('summaryFrom', '')}")
    st.markdown(f"**v{to_v} summary:** {diff.get('summaryTo', '')}")

    tab_fields, tab_calcs, tab_compliance, tab_boq = st.tabs([
        "📋 Project Fields",
        "🔢 Calculated Results",
        "🛡️ Compliance Checks",
        "💰 BOQ Estimates",
    ])

    # ── Tab 1: Project Fields ──────────────────────────────────────────────────
    with tab_fields:
        all_fields = diff.get("projectFields", [])
        changed = [f for f in all_fields if f.get("changed")]
        unchanged = [f for f in all_fields if not f.get("changed")]

        if not changed:
            st.success("No project field changes between these versions.")
        else:
            st.markdown(f"**{len(changed)} field(s) changed** — neutral fields shown in amber")
            frows = []
            for f in changed:
                delta = f.get("delta")
                pct = f.get("deltaPercent")
                if delta is not None:
                    pct_str = f" ({_sign(delta)}{pct}%)" if pct is not None else ""
                    delta_str = f"{_sign(delta)}{delta}{pct_str}"
                else:
                    delta_str = "—"
                lower_b = f["label"] in LOWER_BETTER_FIELDS
                higher_b = f["label"] in HIGHER_BETTER_FIELDS
                frows.append({
                    "Field": f["label"],
                    f"v{from_v}": str(f.get("fromValue", "—")),
                    f"v{to_v}": str(f.get("toValue", "—")),
                    "Delta": delta_str,
                    "_delta": delta,
                    "_lower_better": lower_b,
                    "_higher_better": higher_b,
                })
            df_f = pd.DataFrame(frows)
            display_f = df_f.drop(columns=["_delta", "_lower_better", "_higher_better"])

            def _field_style(row):
                r = frows[row.name]
                bg = _delta_color(r["_delta"], r["_lower_better"], r["_higher_better"])
                return [f"background-color: {bg}"] * len(row)

            st.dataframe(display_f.style.apply(_field_style, axis=1), use_container_width=True, hide_index=True)

        with st.expander(f"Unchanged fields ({len(unchanged)}) — grey = no change"):
            st.dataframe(
                pd.DataFrame([{"Field": f["label"], "Value": str(f.get("fromValue", "—"))} for f in unchanged])
                .style.applymap(lambda _: "background-color: #f8f9fa"),
                use_container_width=True, hide_index=True,
            )

    # ── Tab 2: Calculated Results ──────────────────────────────────────────────
    with tab_calcs:
        all_calcs = diff.get("calcResults", [])
        changed_calcs = [c for c in all_calcs if c.get("changed")]
        unchanged_calcs = [c for c in all_calcs if not c.get("changed")]

        st.caption(
            "🟢 Green = improvement (load/cost reduced, ventilation increased)  "
            "🔴 Red = degradation  "
            "🟡 Amber = neutral metric changed  "
            "⚪ Grey = unchanged"
        )

        if not changed_calcs:
            st.success("All calculated values are identical between these versions.")
        else:
            crows = []
            for c in changed_calcs:
                delta = c.get("delta")
                pct = c.get("deltaPercent")
                unit = c.get("unit", "")
                if delta is not None:
                    pct_str = f" ({_sign(delta)}{pct}%)" if pct is not None else ""
                    delta_str = f"{_sign(delta)}{delta} {unit}{pct_str}".strip()
                else:
                    delta_str = "—"
                lower_b = c["label"] in LOWER_BETTER_CALC
                higher_b = c["label"] in HIGHER_BETTER_CALC
                crows.append({
                    "Module": c["module"].upper(),
                    "Metric": c["label"],
                    f"v{from_v}": f"{c.get('fromValue', '—')} {unit}".strip(),
                    f"v{to_v}": f"{c.get('toValue', '—')} {unit}".strip(),
                    "Change": delta_str,
                    "_delta": delta,
                    "_lower_better": lower_b,
                    "_higher_better": higher_b,
                })
            df_c = pd.DataFrame(crows)
            display_c = df_c.drop(columns=["_delta", "_lower_better", "_higher_better"])

            def _calc_style(row):
                r = crows[row.name]
                bg = _delta_color(r["_delta"], r["_lower_better"], r["_higher_better"])
                return [f"background-color: {bg}"] * len(row)

            st.dataframe(display_c.style.apply(_calc_style, axis=1), use_container_width=True, hide_index=True)

        with st.expander(f"Unchanged metrics ({len(unchanged_calcs)})"):
            st.dataframe(
                pd.DataFrame([{
                    "Module": c["module"].upper(),
                    "Metric": c["label"],
                    "Value": f"{c.get('fromValue', '—')} {c.get('unit', '')}".strip(),
                } for c in unchanged_calcs]).style.applymap(lambda _: "background-color: #f8f9fa"),
                use_container_width=True, hide_index=True,
            )

    # ── Tab 3: Compliance Checks ───────────────────────────────────────────────
    with tab_compliance:
        cc = diff.get("complianceChanges", {})
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Errors (from)", cc.get("errorsFrom", 0))
        c2.metric(
            "Errors (to)", cc.get("errorsTo", 0),
            delta=cc.get("errorsTo", 0) - cc.get("errorsFrom", 0),
        )
        c3.metric("Warnings (from)", cc.get("warningsFrom", 0))
        c4.metric(
            "Warnings (to)", cc.get("warningsTo", 0),
            delta=cc.get("warningsTo", 0) - cc.get("warningsFrom", 0),
        )

        st.info(
            "ℹ️ Compliance inputs are estimated from project design conditions "
            "(floors, ambient temperature, region). For precise compliance, run the "
            "dedicated Compliance Guardian page with full module calculation results."
        )

        appeared = cc.get("appeared", [])
        resolved = cc.get("resolved", [])
        if appeared:
            st.warning(f"💥 {len(appeared)} new violation(s) in v{to_v}")
            for vio in appeared:
                st.error(f"**{vio['severity'].upper()}** — {vio['parameter']}: {vio['message']} ({vio['standardClause']})")
        if resolved:
            st.success(f"✅ {len(resolved)} violation(s) resolved in v{to_v}")
            for vio in resolved:
                st.info(f"Resolved — {vio['parameter']}: {vio['message']}")
        if not appeared and not resolved:
            st.info("No compliance status changes between these versions.")

        per_check = cc.get("perCheckTransitions", [])
        if per_check:
            st.markdown("#### Per-check status — all evaluated rules")
            st.caption("🟢 = pass (improved or unchanged)  🔴 = fail  Grey = pass→pass (no change)")
            pc_rows = []
            for t in per_check:
                pc_rows.append({
                    "Check": t["parameter"],
                    "Clause": t["standardClause"],
                    "Severity": t["severity"].upper(),
                    f"v{from_v} Status": t["fromStatus"].upper(),
                    f"v{to_v} Status": t["toStatus"].upper(),
                    "_changed": t["changed"],
                    "_fromStatus": t["fromStatus"],
                    "_toStatus": t["toStatus"],
                })
            df_pc = pd.DataFrame(pc_rows)
            display_pc = df_pc.drop(columns=["_changed", "_fromStatus", "_toStatus"])

            def _compliance_style(row):
                r = pc_rows[row.name]
                from_s = r["_fromStatus"]
                to_s = r["_toStatus"]
                if from_s == "fail" and to_s == "pass":
                    bg = "#d4edda"
                elif to_s == "fail":
                    bg = "#f8d7da"
                else:
                    bg = "#f8f9fa"
                return [f"background-color: {bg}"] * len(row)

            st.dataframe(display_pc.style.apply(_compliance_style, axis=1), use_container_width=True, hide_index=True)

    # ── Tab 4: BOQ Estimates ───────────────────────────────────────────────────
    with tab_boq:
        currency_from = diff.get("boqCurrencyFrom", "")
        currency_to = diff.get("boqCurrencyTo", "")
        currencies_differ = diff.get("boqCurrenciesDiffer", False)
        grand_from = diff.get("boqGrandTotalFrom", 0)
        grand_to = diff.get("boqGrandTotalTo", 0)
        grand_delta = diff.get("boqGrandTotalDelta")

        if currencies_differ:
            st.warning(
                f"⚠️ Currencies differ between versions: **v{from_v} = {currency_from}**, "
                f"**v{to_v} = {currency_to}**. Cost deltas cannot be meaningfully computed "
                f"without currency conversion. Totals shown separately per version."
            )
        else:
            st.caption("Lower BOQ total = lower cost = improved. 🟢 = cost reduced  🔴 = cost increased")

        c_from_m, c_to_m = st.columns(2)
        c_from_m.metric(f"v{from_v} Total ({currency_from})", f"{grand_from:,.0f}")
        c_to_m.metric(f"v{to_v} Total ({currency_to})", f"{grand_to:,.0f}")
        if not currencies_differ and grand_delta is not None:
            st.metric(
                f"Grand Total Change ({currency_to})",
                f"{grand_to:,.0f}",
                delta=f"{_sign(grand_delta)}{grand_delta:,.0f}",
            )

        brows = []
        for item in diff.get("boqChanges", []):
            delta_b = item.get("delta")
            pct_b = item.get("deltaPercent")
            if delta_b is not None:
                pct_str_b = f" ({_sign(delta_b)}{pct_b}%)" if pct_b is not None else ""
                change_str = f"{_sign(delta_b)}{delta_b:,.0f}{pct_str_b}"
            else:
                change_str = "n/a (currency mismatch)"
            brows.append({
                "Line Item": item["description"],
                "Unit": item["unit"],
                f"v{from_v} ({currency_from})": f"{item.get('fromTotal', 0):,.0f}",
                f"v{to_v} ({currency_to})": f"{item.get('toTotal', 0):,.0f}",
                "Change": change_str,
                "_delta": delta_b,
            })
        df_b = pd.DataFrame(brows)
        display_b = df_b.drop(columns=["_delta"])

        def _boq_style(row):
            delta = brows[row.name]["_delta"]
            if delta is None:
                return ["background-color: #f8f9fa"] * len(row)
            bg = _delta_color(delta, lower_better=True)
            return [f"background-color: {bg}"] * len(row)

        st.dataframe(display_b.style.apply(_boq_style, axis=1), use_container_width=True, hide_index=True)

# ─── Restore ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Restore a version")
st.markdown(
    "Restoring re-applies the **exact inputs** from a historical snapshot as a **new** "
    "version — the history is never overwritten."
)

restore_v = st.selectbox("Version to restore", version_nums, index=0, key="restore_ver")
restore_summary = next(
    (v.get("summary", "") for v in versions if v["version"] == restore_v), ""
)
st.caption(restore_summary[:200])

if st.button(f"🔄 Restore v{restore_v}", type="secondary"):
    try:
        r = requests.post(
            f"{API_BASE}/projects/{project_id}/restore/{restore_v}",
            timeout=15,
        )
        r.raise_for_status()
        result = r.json()
        new_v = result.get("newVersion", "?")
        st.success(
            f"✅ v{restore_v} restored as new snapshot v{new_v}. "
            "Navigate to the **Project Workspace** page to review the restored design."
        )
        st.cache_data.clear()
        try:
            st.switch_page("pages/20_Project_Workspace.py")
        except Exception:
            st.info("👉 Open the **Project Workspace** page from the sidebar to review the restored design.")
    except Exception as e:
        st.error(f"Restore failed: {e}")
