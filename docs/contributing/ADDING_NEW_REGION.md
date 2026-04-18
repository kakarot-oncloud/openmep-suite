# Guide: Adding a New Region to OpenMEP

This guide walks through every step required to add a new region (e.g., **North America**, **Singapore**, **South Africa**) to OpenMEP.

---

## Overview

Adding a region involves four layers:

1. **Region configuration** — add the new region, sub-regions, and utility authorities to `utils.py`
2. **Engine overrides** — add region-specific correction factors and standard tables to each engine
3. **API route defaults** — ensure routes accept and handle the new region code
4. **Streamlit UI** — the 3-level region selector auto-populates from the config; verify each page

Estimated effort: **1–3 days** for a complete region with full standards implementation.

---

## Step 1: Region Configuration (`streamlit_app/utils.py`)

### 1.1 Add to the top-level REGIONS dict

```python
REGIONS = {
    "gcc":        "GCC / UAE / Saudi Arabia / Qatar / Kuwait",
    "europe":     "Europe / United Kingdom",
    "india":      "India",
    "australia":  "Australia / New Zealand",
    "north_america": "North America",   # <-- add this
}
```

### 1.2 Add sub-regions (Level 2)

```python
SUB_REGIONS_L2 = {
    # ... existing regions ...
    "north_america": {
        "usa":    "United States",
        "canada": "Canada",
    },
}
```

### 1.3 Add utility/authority (Level 3)

```python
SUB_REGIONS_L3 = {
    # ... existing regions ...
    "usa": {
        "pge":    "Pacific Gas & Electric (California)",
        "coned":  "Con Edison (New York)",
        "oncor":  "Oncor (Texas)",
    },
    "canada": {
        "hydro_on": "Hydro One (Ontario)",
        "bc_hydro": "BC Hydro (British Columbia)",
    },
}
```

### 1.4 Add currency mapping

```python
REGION_CURRENCY = {
    # ... existing ...
    "north_america": {"currency": "USD", "symbol": "$"},
}
```

---

## Step 2: Engine Overrides

### 2.1 Electrical — Cable Sizing (`backend/engines/electrical/cable_sizing.py`)

**a) Ambient temperature correction factors**

Add a correction factor table for the new region's ambient temperature basis. NEC (USA) uses 30°C as the basis temperature:

```python
# backend/engines/electrical/cable_sizing.py

AMBIENT_CORRECTION = {
    "gcc":        {25: 1.06, 30: 1.00, 35: 0.94, 40: 0.87, 45: 0.79, 50: 0.71},
    "europe":     {25: 1.06, 30: 1.00, 35: 0.94, 40: 0.87},
    "india":      {35: 1.00, 40: 0.91, 45: 0.82, 50: 0.71},
    "australia":  {25: 1.00, 30: 0.94, 35: 0.87, 40: 0.79, 45: 0.71},
    "north_america": {30: 1.00, 35: 0.94, 40: 0.88, 45: 0.82},  # NEC Table 310.15(B)(1)
}
```

**b) Standard reference**

```python
STANDARD_BY_REGION = {
    "gcc":       "BS 7671:2018 AMD2",
    "europe":    "BS 7671:2018 AMD2 / IEC 60364",
    "india":     "IS 3961",
    "australia": "AS/NZS 3008.1.1:2017",
    "north_america": "NEC NFPA 70:2023, Table 310.16",  # <-- add
}
```

**c) Voltage drop limit**

```python
VOLTAGE_DROP_LIMIT = {
    "gcc":       {"power": 4.0, "lighting": 3.0},
    "europe":    {"power": 4.0, "lighting": 3.0},
    "india":     {"power": 5.0, "lighting": 5.0},
    "australia": {"power": 5.0, "lighting": 5.0},
    "north_america": {"power": 3.0, "lighting": 3.0},  # NEC Informational Note
}
```

**d) Cable type mapping** (if the new region uses different designations)

```python
# NEC cable types
_NA_CABLE_MAP = {
    "XLPE_CU": "THWN-2",
    "PVC_CU":  "THHN",
    "XLPE_AL": "XHHW-2_AL",
}
```

### 2.2 Mechanical — Cooling Load

Add outdoor design conditions to the climate lookup table:

```python
DESIGN_CONDITIONS = {
    # ... existing ...
    "north_america": {
        "usa_new_york":   {"summer_db": 34, "summer_wb": 25, "winter_db": -15},
        "usa_los_angeles": {"summer_db": 36, "summer_wb": 22, "winter_db": 5},
        "usa_chicago":    {"summer_db": 35, "summer_wb": 26, "winter_db": -18},
        "canada_toronto": {"summer_db": 33, "summer_wb": 24, "winter_db": -20},
    },
}
```

### 2.3 Plumbing — Per Capita Demand

```python
PER_CAPITA_DEMAND = {
    # ... existing ...
    "north_america": {
        "residential":  250,  # l/person/day (AWWA guidelines)
        "office":        50,
        "school":        40,
        "hotel":        220,
    },
}
```

### 2.4 Fire Protection — Hazard Classification

```python
HAZARD_CLASSIFICATION = {
    # ... existing ...
    "north_america": "NFPA 13:2022",  # Same NFPA classes as GCC/Australia
}
```

---

## Step 3: API Routes

In each route file (e.g., `backend/api/routes/electrical.py`), verify that the new region code passes Pydantic validation. If region is validated against a list:

```python
class CableSizingRequest(BaseModel):
    region: str = "gcc"
    # If there is a literal validator, add "north_america":
    # region: Literal["gcc", "europe", "india", "australia", "north_america"] = "gcc"
```

---

## Step 4: Tests

Add tests in `tests/` for the new region. Each test must include a source reference:

```python
# tests/test_cable_sizing_na.py

def test_cable_sizing_north_america_nec():
    """
    Reference: NEC 2023 Table 310.16, 30°C ambient, Cu THWN-2, conduit,
    45 kW, PF 0.85, 3-phase, 208 V → #2 AWG = 66 mm² (approx)
    """
    result = calculate_cable_sizing(CableSizingInput(
        region="north_america",
        sub_region="usa",
        load_kw=45,
        power_factor=0.85,
        phases="3",
        voltage_v=208,
        cable_type="THWN-2",
        installation_method="conduit",
        cable_length_m=30,
        ambient_temp_c=30,
    ))
    assert result.recommended_cable_size_mm2 == 66  # AWG #2
    assert result.standard_used.startswith("NEC")
```

Run: `pytest tests/test_cable_sizing_na.py -v`

---

## Step 5: Documentation

1. Create `docs/regions/NORTH_AMERICA_GUIDE.md` following the same structure as the other region guides
2. Add the new region to the **Region Support** table in `README.md`
3. Add new standards to `docs/STANDARDS_REFERENCE.md`
4. Update `CHANGELOG.md` under `[Unreleased]`

---

## Step 6: Pull Request

1. Ensure all tests pass: `pytest tests/ -v`
2. Update `CHANGELOG.md`
3. Open a PR with the title format: `feat(region): add North America (NEC NFPA 70)`
4. In the PR description, list:
   - Standards implemented
   - Standards deferred (planned for a follow-up PR)
   - Known limitations
   - Source references for correction factors

---

## Checklist

- [ ] `utils.py` — REGIONS, SUB_REGIONS_L2, SUB_REGIONS_L3, REGION_CURRENCY
- [ ] `cable_sizing.py` — ambient correction factors, voltage drop limits, standard name
- [ ] `cooling_load.py` — outdoor design conditions
- [ ] `plumbing/` — per capita demand
- [ ] `fire/` — hazard classification standard reference
- [ ] API routes — region accepted without 422 error
- [ ] Tests — at least 2 per engine with standard reference comments
- [ ] `docs/regions/REGION_GUIDE.md` — region-specific guide
- [ ] `README.md` — region support table updated
- [ ] `docs/STANDARDS_REFERENCE.md` — new standards listed
- [ ] `CHANGELOG.md` — entry under `[Unreleased]`
