# Guide: Adding a New Calculator to OpenMEP

This guide walks through the full process of adding a new calculation module — a new engineering calculator that supports all 4 existing regions.

**Example:** We'll add a **UPS Sizing** calculator (uninterruptible power supply).

---

## Overview

A complete calculator consists of:

1. **Engine** — pure Python calculation function in `backend/engines/`
2. **API route** — FastAPI endpoint in `backend/api/routes/`
3. **Streamlit page** — user interface in `streamlit_app/pages/`
4. **Tests** — pytest tests in `tests/`

Estimated effort: **4–8 hours** for a well-defined calculation.

---

## Step 1: Write the Calculation Engine

The engine is **pure Python** — no FastAPI, no Streamlit, no I/O. It receives a typed input dataclass and returns a typed output dataclass.

**File:** `backend/engines/electrical/ups_sizing.py`

```python
"""
UPS (Uninterruptible Power Supply) Sizing Engine

Standards:
  - IEC 62040-3:2021 — UPS performance requirements and test methods
  - IEEE 446 — IEEE Recommended Practice for Emergency and Standby Power
  - BS EN 62040-3:2011 — UK/GCC reference

All 4 regions reference the same IEC standard.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import math


@dataclass
class UPSLoad:
    """A single load item connected to the UPS."""
    description: str
    kva: float
    power_factor: float = 0.9
    demand_factor: float = 1.0


@dataclass
class UPSSizingInput:
    """Inputs for UPS sizing calculation."""
    region: str
    sub_region: str = ""
    loads: List[UPSLoad] = field(default_factory=list)
    autonomy_minutes: int = 15
    battery_type: str = "VRLA"          # VRLA or Li-Ion
    efficiency_percent: float = 96.0
    design_margin_percent: float = 20.0
    project_name: str = ""


@dataclass
class UPSSizingResult:
    """Results of UPS sizing calculation."""
    total_load_kva: float
    total_load_kw: float
    design_load_kva: float              # after margin
    recommended_ups_kva: float          # next standard size
    battery_capacity_ah: float
    battery_voltage_v: float
    autonomy_minutes: int
    efficiency_percent: float
    standard_used: str
    warnings: List[str]


# Standard UPS kVA ratings (IEC commercial sizes)
_STANDARD_SIZES_KVA = [6, 10, 15, 20, 30, 40, 60, 80, 100, 120, 160, 200, 250, 300, 400, 500, 600, 800, 1000]


def calculate_ups_sizing(inp: UPSSizingInput) -> UPSSizingResult:
    """
    Size a UPS system for a given load schedule and autonomy.
    Standard: IEC 62040-3:2021
    """
    warnings: List[str] = []

    # Total connected load
    total_kva = sum(
        load.kva * load.demand_factor for load in inp.loads
    )
    total_kw = sum(
        load.kva * load.demand_factor * load.power_factor for load in inp.loads
    )

    if total_kva == 0:
        warnings.append("No loads defined — enter at least one load item.")

    # Apply design margin
    design_kva = total_kva * (1 + inp.design_margin_percent / 100)

    # Next standard UPS size
    recommended_kva = next(
        (s for s in _STANDARD_SIZES_KVA if s >= design_kva),
        math.ceil(design_kva / 100) * 100  # round up if larger than catalogue
    )

    # Battery capacity: C = (P × t) / (η × V × DoD)
    # VRLA: 48 V string typical for small UPS, 192 V for large
    battery_voltage = 192 if recommended_kva >= 60 else 48
    dod = 0.80  # 80% depth of discharge (VRLA standard)
    battery_ah = (
        recommended_kva * 1000 * (inp.autonomy_minutes / 60)
    ) / (inp.efficiency_percent / 100 * battery_voltage * dod)

    if inp.autonomy_minutes < 10:
        warnings.append("Autonomy below 10 minutes — consider at least 10 minutes for safe shutdown.")

    standard = {
        "gcc":          "IEC 62040-3:2021 / BS EN 62040-3:2011",
        "europe":       "BS EN 62040-3:2011",
        "india":        "IEC 62040-3:2021 / IS 16242",
        "australia":    "IEC 62040-3:2021 / AS/NZS 62040",
    }.get(inp.region.lower(), "IEC 62040-3:2021")

    return UPSSizingResult(
        total_load_kva=round(total_kva, 2),
        total_load_kw=round(total_kw, 2),
        design_load_kva=round(design_kva, 2),
        recommended_ups_kva=recommended_kva,
        battery_capacity_ah=round(battery_ah, 0),
        battery_voltage_v=battery_voltage,
        autonomy_minutes=inp.autonomy_minutes,
        efficiency_percent=inp.efficiency_percent,
        standard_used=standard,
        warnings=warnings,
    )
```

### Engine Design Rules

- **Pure functions only** — no global state, no file I/O, no HTTP calls
- **One docstring** — first line cites the standard and edition
- **Dataclasses for I/O** — use `@dataclass` for inputs and outputs
- **No magic numbers** — give constants names (`_STANDARD_SIZES_KVA`, `DOD = 0.80`)
- **Region-aware standard selection** — use a dict lookup per region, not `if/elif` chains
- **Warnings list** — never raise exceptions for soft validation failures; add to `warnings`

---

## Step 2: Add the API Route

**File:** `backend/api/routes/electrical.py` (add to existing file, or create a new router)

```python
# In backend/api/routes/electrical.py

from backend.engines.electrical.ups_sizing import UPSSizingInput, UPSLoad, calculate_ups_sizing

class UPSLoadItem(BaseModel):
    description: str = ""
    kva: float = Field(gt=0)
    power_factor: float = Field(default=0.9, ge=0.1, le=1.0)
    demand_factor: float = Field(default=1.0, ge=0.1, le=1.0)

class UPSSizingRequest(BaseModel):
    region: str = "gcc"
    sub_region: str = ""
    loads: List[UPSLoadItem] = Field(default_factory=list)
    autonomy_minutes: int = Field(default=15, ge=5, le=480)
    battery_type: str = "VRLA"
    efficiency_percent: float = Field(default=96.0, ge=80, le=100)
    design_margin_percent: float = Field(default=20.0, ge=0, le=50)
    project_name: str = ""

@router.post("/ups-sizing")
def ups_sizing(req: UPSSizingRequest):
    """Size a UPS system. Standard: IEC 62040-3:2021."""
    loads = [
        UPSLoad(
            description=l.description,
            kva=l.kva,
            power_factor=l.power_factor,
            demand_factor=l.demand_factor,
        )
        for l in req.loads
    ]
    inp = UPSSizingInput(
        region=req.region,
        sub_region=req.sub_region,
        loads=loads,
        autonomy_minutes=req.autonomy_minutes,
        battery_type=req.battery_type,
        efficiency_percent=req.efficiency_percent,
        design_margin_percent=req.design_margin_percent,
        project_name=req.project_name,
    )
    result = calculate_ups_sizing(inp)
    return result
```

### Route Design Rules

- **One route per calculator** — keep the route function thin; all logic in the engine
- **Use `Field()` validators** — `gt=0`, `ge=0.1`, `le=1.0`, etc. for every numeric field
- **POST, not GET** — calculation inputs are too complex for query strings
- **Return the dataclass directly** — FastAPI serialises dataclasses automatically via `response_model`

---

## Step 3: Create the Streamlit Page

Name the file with the next sequential page number. If 26 pages exist, this becomes page 27:

**File:** `streamlit_app/pages/27_UPS_Sizing.py`

```python
"""
OpenMEP — UPS Sizing
Standard: IEC 62040-3:2021
"""
import streamlit as st
import requests
from streamlit_app.utils import region_selector, API_BASE

st.set_page_config(page_title="UPS Sizing | OpenMEP", page_icon="🔋", layout="wide")
st.title("UPS Sizing")
st.caption("Standard: IEC 62040-3:2021")

# ── Region selector ────────────────────────────────────────────────────────────
region_code, sub_region_code = region_selector()

# ── Load schedule ──────────────────────────────────────────────────────────────
st.subheader("Load Schedule")
if "ups_loads" not in st.session_state:
    st.session_state.ups_loads = [
        {"description": "Servers", "kva": 40, "power_factor": 0.9, "demand_factor": 1.0},
        {"description": "Network equipment", "kva": 10, "power_factor": 0.9, "demand_factor": 1.0},
    ]

# Render editable table
for i, load in enumerate(st.session_state.ups_loads):
    c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 0.5])
    load["description"]   = c1.text_input("Description", load["description"], key=f"desc_{i}")
    load["kva"]           = c2.number_input("kVA", 0.1, 5000.0, load["kva"], key=f"kva_{i}")
    load["power_factor"]  = c3.number_input("PF", 0.1, 1.0, load["power_factor"], step=0.01, key=f"pf_{i}")
    load["demand_factor"] = c4.number_input("DF", 0.1, 1.0, load["demand_factor"], step=0.01, key=f"df_{i}")
    if c5.button("✕", key=f"del_{i}"):
        st.session_state.ups_loads.pop(i)
        st.rerun()

if st.button("+ Add Load"):
    st.session_state.ups_loads.append({"description": "", "kva": 10, "power_factor": 0.9, "demand_factor": 1.0})
    st.rerun()

# ── UPS parameters ─────────────────────────────────────────────────────────────
st.subheader("UPS Parameters")
c1, c2, c3 = st.columns(3)
autonomy     = c1.number_input("Autonomy (minutes)", 5, 480, 15)
battery_type = c2.selectbox("Battery type", ["VRLA", "Li-Ion"])
margin       = c3.number_input("Design margin (%)", 0, 50, 20)

# ── Calculate ──────────────────────────────────────────────────────────────────
if st.button("Calculate UPS Size", type="primary"):
    payload = {
        "region": region_code,
        "sub_region": sub_region_code,
        "loads": st.session_state.ups_loads,
        "autonomy_minutes": autonomy,
        "battery_type": battery_type,
        "design_margin_percent": margin,
    }
    try:
        r = requests.post(f"{API_BASE}/api/electrical/ups-sizing", json=payload, timeout=15)
        r.raise_for_status()
        res = r.json()

        st.success(f"Recommended UPS: **{res['recommended_ups_kva']} kVA**")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total load", f"{res['total_load_kva']} kVA")
        col2.metric("Design load", f"{res['design_load_kva']} kVA")
        col3.metric("Battery", f"{res['battery_capacity_ah']:.0f} Ah @ {res['battery_voltage_v']} V")
        col4.metric("Autonomy", f"{res['autonomy_minutes']} min")

        st.caption(f"Standard: {res['standard_used']}")
        for w in res.get("warnings", []):
            st.warning(w)

    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend. Ensure the API server is running on port 8000.")
    except Exception as e:
        st.error(f"Calculation error: {e}")
```

### Page Design Rules

- **`st.set_page_config`** must be the first Streamlit call — `page_title` and `page_icon` required
- **`region_selector()`** always first — returns `(region_code, sub_region_code)`
- **Session state** for editable tables — use `st.session_state` to persist rows
- **Wrap API calls** in `try/except` — show `st.error()` for `ConnectionError`, not a traceback
- **`st.caption`** for standard reference — always show which standard was used

---

## Step 4: Write Tests

**File:** `tests/test_ups_sizing.py`

```python
"""Tests for UPS sizing engine."""
import pytest
from backend.engines.electrical.ups_sizing import (
    UPSSizingInput, UPSLoad, calculate_ups_sizing
)

def make_loads():
    return [
        UPSLoad("Servers", kva=40, power_factor=0.9, demand_factor=1.0),
        UPSLoad("Network", kva=10, power_factor=0.9, demand_factor=1.0),
    ]

def test_ups_sizing_basic():
    """
    Reference: 50 kVA load + 20% margin = 60 kVA → IEC standard size: 60 kVA.
    """
    result = calculate_ups_sizing(UPSSizingInput(
        region="gcc", loads=make_loads(), autonomy_minutes=15
    ))
    assert result.total_load_kva == 50.0
    assert result.design_load_kva == 60.0
    assert result.recommended_ups_kva == 60

def test_ups_sizing_standard_name_by_region():
    """Standard name switches by region."""
    for region, expected_fragment in [
        ("gcc", "BS EN 62040-3"),
        ("india", "IS 16242"),
        ("australia", "AS/NZS 62040"),
    ]:
        result = calculate_ups_sizing(UPSSizingInput(
            region=region, loads=make_loads(), autonomy_minutes=15
        ))
        assert expected_fragment in result.standard_used, \
            f"Region {region}: expected '{expected_fragment}' in '{result.standard_used}'"

def test_ups_sizing_warns_short_autonomy():
    """Autonomy below 10 minutes should generate a warning."""
    result = calculate_ups_sizing(UPSSizingInput(
        region="gcc", loads=make_loads(), autonomy_minutes=5
    ))
    assert any("10 minutes" in w for w in result.warnings)

def test_ups_sizing_empty_loads():
    """Empty load list should warn, not crash."""
    result = calculate_ups_sizing(UPSSizingInput(
        region="europe", loads=[], autonomy_minutes=15
    ))
    assert result.total_load_kva == 0.0
    assert len(result.warnings) > 0
```

Run: `pytest tests/test_ups_sizing.py -v`

---

## Step 5: Register the Route (if creating a new router)

If you added the route to an existing router (e.g., `electrical.py`), no registration is needed.

If you created a new router file:

```python
# backend/main.py
from backend.api.routes import electrical, mechanical, plumbing, fire, boq, compliance, reports, ups

app.include_router(ups.router, prefix="/api")
```

---

## Step 6: Add to Sidebar Navigation

The sidebar in `streamlit_app/app.py` uses `st.page_link()` to list pages. Add the new page:

```python
# In app.py sidebar section — Electrical group:
st.page_link("pages/27_UPS_Sizing.py", label="⚡ UPS Sizing")
```

---

## Step 7: Documentation

1. Add to `docs/USER_GUIDE.md` — a section under the appropriate discipline
2. Add to `docs/API_DOCS.md` — the endpoint with request/response example
3. Add any new standards to `docs/STANDARDS_REFERENCE.md`
4. Update `CHANGELOG.md` under `[Unreleased]`

---

## Step 8: Pull Request

PR title format: `feat(electrical): add UPS sizing calculator (IEC 62040-3)`

In the PR description:
- Standards implemented and editions
- Reference values used for tests
- Any known limitations or deferred features

---

## Checklist

- [ ] `backend/engines/<discipline>/<calculator>.py` — pure engine
- [ ] `backend/api/routes/<discipline>.py` — route added
- [ ] `streamlit_app/pages/<N>_<Name>.py` — Streamlit page
- [ ] `tests/test_<calculator>.py` — at least 4 tests with reference comments
- [ ] `streamlit_app/app.py` — sidebar link added
- [ ] `docs/USER_GUIDE.md` — section added
- [ ] `docs/API_DOCS.md` — endpoint documented
- [ ] `docs/STANDARDS_REFERENCE.md` — new standards listed
- [ ] `CHANGELOG.md` — entry under `[Unreleased]`
- [ ] All tests pass: `pytest tests/ -v`
