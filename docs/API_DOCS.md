# OpenMEP REST API Documentation

**Version 0.2.1 | Base URL: `http://localhost:8000`**

Interactive docs (Swagger UI): `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`
OpenAPI JSON: `http://localhost:8000/openapi.json`

> This file is generated from the live `/openapi.json` spec. Every field name, type, and default value matches the actual API. Run `curl http://localhost:8000/docs` for the authoritative interactive version.

---

## Authentication

Version 0.2.1 has no authentication. Do not expose the API publicly without adding a reverse proxy with authentication (e.g., nginx + basic auth, or an API gateway).

---

## Health Check

### GET /health

Returns service liveness status.

**Response 200:**
```json
{
  "status": "healthy",
  "service": "openmep-api"
}
```

**curl:**
```bash
curl http://localhost:8000/health
```

---

## Electrical Endpoints — `/api/electrical`

### POST /api/electrical/cable-sizing

**Summary:** Cable Sizing — All Regions (BS 7671 / IEC 60364 / NBC / AS/NZS 3008)

**Request fields** (`CableSizingRequest`):

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `region` | string | no | `"gcc"` | `gcc`, `europe`, `india`, `australia` |
| `sub_region` | string | no | `""` | e.g. `dewa`, `uk`, `msedcl`, `nsw` |
| `load_kw` | number | **yes** | — | Active load in kW |
| `power_factor` | number | no | `0.85` | — |
| `phases` | integer | no | `3` | `1` or `3` |
| `voltage_v` | number\|null | no | null | Defaults to region standard (e.g. 415V GCC) |
| `cable_type` | string | no | `"XLPE_CU"` | See `/api/electrical/cable-sizing/options` |
| `installation_method` | string | no | `"C"` | A1, A2, B1, B2, C, D1, D2, E, F |
| `cable_length_m` | number | **yes** | — | One-way route length |
| `number_of_runs` | integer | no | `1` | Parallel cable runs |
| `ambient_temp_c` | number\|null | no | null | Defaults to region standard (e.g. 40°C GCC) |
| `num_grouped_circuits` | integer | no | `1` | Circuits in the same group for derating |
| `cables_touching` | boolean | no | `true` | Applies Cg factor for touching cables |
| `circuit_type` | string | no | `"power"` | `power`, `lighting`, `motor`, `critical` |
| `demand_factor` | number | no | `1.0` | Diversity / demand factor |
| `project_name` | string | no | `""` | For report metadata |
| `circuit_from` | string | no | `""` | Panel / DB reference |
| `circuit_to` | string | no | `""` | Load reference |
| `fault_level_ka` | number\|null | no | null | Required for earth fault protection check |
| `protection_time_s` | number | no | `0.4` | Protective device disconnection time (s) |

**Example request:**
```json
{
  "region": "gcc",
  "sub_region": "dewa",
  "load_kw": 45,
  "power_factor": 0.85,
  "phases": 3,
  "cable_type": "XLPE_CU",
  "installation_method": "C",
  "cable_length_m": 80,
  "ambient_temp_c": 40
}
```

**Example response (key fields):**
```json
{
  "status": "success",
  "region": "gcc",
  "standard": "BS 7671:2018+A2:2022 Table 4D5A (XLPE) / 4D2A (PVC)",
  "authority": "DEWA (Dubai Electricity and Water Authority)",
  "load_kw": 45.0,
  "power_factor": 0.85,
  "phases": 3,
  "supply_voltage_v": 415.0,
  "design_current_ib_a": 73.65,
  "cable_type": "XLPE_CU",
  "installation_method": "C",
  "selected_size_mm2": 16,
  "tabulated_rating_it_a": 102.0,
  "ambient_temp_c": 40.0,
  "ca_factor": 0.91,
  "num_grouped_circuits": 1,
  "cg_factor": 1.0,
  "derated_rating_iz_a": 92.8,
  "cable_length_m": 80.0,
  "voltage_drop_mv": 16498.1,
  "voltage_drop_pct": 3.98,
  "voltage_drop_limit_pct": 4.0,
  "voltage_drop_pass": true,
  "protection_device_a": 80.0,
  "earth_conductor_mm2": 6.0,
  "current_check_pass": true,
  "overall_compliant": true,
  "compliance_statements": ["✅ COMPLIANT | Current Carrying Capacity ..."],
  "warnings": []
}
```

**curl:**
```bash
curl -X POST http://localhost:8000/api/electrical/cable-sizing \
  -H "Content-Type: application/json" \
  -d '{"region":"gcc","sub_region":"dewa","load_kw":45,"cable_length_m":80}'
```

---

### GET /api/electrical/cable-sizing

**Summary:** Cable Sizing — Quick Calculation via Query Parameters

Accepts the same fields as the POST endpoint but as URL query parameters. Useful for simple one-off lookups.

**Example:**
```bash
curl "http://localhost:8000/api/electrical/cable-sizing?region=gcc&load_kw=45&cable_length_m=80"
```

---

### GET /api/electrical/cable-sizing/options

**Summary:** Cable Sizing Input Options — returns all valid enum values (no query params required)

**Response:**
```json
{
  "cable_types": {
    "XLPE_CU": "XLPE Copper (90°C) — BS 7671 Table 4D5A",
    "PVC_CU": "PVC Copper (70°C) — BS 7671 Table 4D2A",
    "XLPE_AL": "XLPE Aluminium (90°C)",
    "FRLS_CU": "FRLS XLPE Copper (India IS 7098)",
    "X90_CU": "X-90 XLPE Copper (Australia AS/NZS 3008)"
  },
  "installation_methods": {
    "A1": "Enclosed in conduit in thermally insulating wall",
    "A2": "Enclosed in conduit in masonry wall",
    "B1": "Enclosed in conduit on wall / in trunking",
    "B2": "Enclosed in cable trunking",
    "C": "Direct clipped to surface / wall",
    "D1": "In conduit in ground",
    "D2": "Direct buried in ground",
    "E": "Free-air — single layer on perforated cable tray",
    "F": "Free-air — touching cables on horizontal cable tray"
  },
  "regions": ["gcc", "europe", "india", "australia"],
  "sub_regions": {"gcc": ["dewa", "addc", ...], ...}
}
```

---

### GET /api/electrical/standards

**Summary:** List Available Electrical Standards by Region

**Query params:** `region` (required)

**Example:** `GET /api/electrical/standards?region=gcc`

---

### POST /api/electrical/voltage-drop

**Summary:** Voltage Drop Analysis (BS 7671 / IEC 60364)

**Request fields** (`VoltageDropRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `region` | string | **yes** | — |
| `sub_region` | string | no | `""` |
| `cable_type` | string | no | `"XLPE_CU"` |
| `conductor_size_mm2` | number | **yes** | — |
| `cable_length_m` | number | **yes** | — |
| `design_current_a` | number | **yes** | — |
| `phases` | integer | no | `3` |
| `circuit_type` | string | no | `"power"` |

**Example request:**
```json
{
  "region": "gcc",
  "sub_region": "dewa",
  "cable_type": "XLPE_CU",
  "conductor_size_mm2": 35,
  "cable_length_m": 80,
  "design_current_a": 73.5,
  "phases": 3,
  "circuit_type": "power"
}
```

**Example response:**
```json
{
  "status": "success",
  "conductor_size_mm2": 35.0,
  "cable_length_m": 80.0,
  "design_current_a": 73.5,
  "supply_voltage_v": 400,
  "vd_mv_am": 1.25,
  "vd_total_mv": 7350.0,
  "vd_total_v": 7.35,
  "vd_percent": 1.84,
  "vd_limit_percent": 4.0,
  "receiving_end_voltage_v": 392.6,
  "compliant": true,
  "recommended_size_mm2": null,
  "standard": "BS 7671:2018+A2:2022 Table 4D5A (XLPE) / 4D2A (PVC)"
}
```

---

### POST /api/electrical/maximum-demand

**Summary:** Maximum Demand / Load Schedule

**Request fields** (`MaxDemandRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `region` | string | no | `"gcc"` |
| `supply_voltage_lv` | number | no | `400.0` |
| `diversity_factor` | number | no | `1.0` |
| `future_expansion_pct` | number | no | `20.0` |
| `loads` | array | **yes** | — |

**Example request:**
```json
{
  "region": "gcc",
  "supply_voltage_lv": 415,
  "diversity_factor": 0.85,
  "future_expansion_pct": 20,
  "loads": [
    {"description": "Lighting", "kw": 50, "power_factor": 1.0, "quantity": 1},
    {"description": "Power sockets", "kw": 120, "power_factor": 0.85, "quantity": 1},
    {"description": "AHUs", "kw": 250, "power_factor": 0.85, "quantity": 3}
  ]
}
```

---

### POST /api/electrical/short-circuit

**Summary:** Short Circuit Analysis (IEC 60909)

**Request fields** (`ShortCircuitRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `region` | string | no | `"gcc"` |
| `transformer_kva` | number | **yes** | — |
| `transformer_impedance_pct` | number | no | `5.5` |
| `lv_voltage` | number | no | `400.0` |
| `cable_type` | string | no | `"XLPE_CU"` |
| `cable_size_mm2` | number | **yes** | — |
| `cable_length_m` | number | **yes** | — |
| `upstream_fault_level_ka` | number\|null | no | null |

**Example request:**
```json
{
  "region": "gcc",
  "transformer_kva": 1000,
  "transformer_impedance_pct": 6.0,
  "lv_voltage": 415,
  "cable_type": "XLPE_CU",
  "cable_size_mm2": 35,
  "cable_length_m": 80
}
```

---

### POST /api/electrical/lighting

**Summary:** Interior Lighting Calculation (Lumen Method — CIBSE LG7 / AS/NZS 1680 / NBC)

**Request fields** (`LightingRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `region` | string | no | `"gcc"` |
| `room_name` | string | no | `"Office"` |
| `room_type` | string | no | `"office"` |
| `length_m` | number | **yes** | — |
| `width_m` | number | **yes** | — |
| `height_m` | number | **yes** | — |
| `work_plane_height_m` | number | no | `0.85` |
| `target_lux` | number\|null | no | null | Defaults from room_type |
| `luminaire_type` | string | no | `"LED Panel"` |
| `luminaire_lumens` | number | no | `4000` |
| `luminaire_watts` | number | no | `40` |
| `luminaire_efficiency` | number | no | `1.0` |
| `ceiling_reflectance` | number | no | `0.7` |
| `wall_reflectance` | number | no | `0.5` |
| `floor_reflectance` | number | no | `0.2` |
| `llf` | number | no | `0.8` | Light Loss Factor (maintenance factor) |

**Example request:**
```json
{
  "region": "europe",
  "sub_region": "uk",
  "room_type": "office",
  "length_m": 12,
  "width_m": 8,
  "height_m": 3.0,
  "target_lux": 500,
  "luminaire_lumens": 4000,
  "luminaire_watts": 40,
  "llf": 0.8
}
```

---

### POST /api/electrical/pf-correction

**Summary:** Power Factor Correction — Capacitor Bank Sizing (IEC 60831-1)

**Request fields** (`PFCorrectionRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `region` | string | no | `"gcc"` |
| `sub_region` | string | no | `""` |
| `active_power_kw` | number | **yes** | — |
| `existing_pf` | number | no | `0.8` |
| `target_pf` | number | no | `0.95` |
| `supply_voltage_v` | number\|null | no | null |
| `phases` | integer | no | `3` |
| `num_transformers` | integer | no | `1` |
| `transformer_kva` | number | no | `1000.0` |
| `apply_harmonic_derating` | boolean | no | `false` |
| `project_name` | string | no | `""` |

---

### POST /api/electrical/generator-sizing

**Summary:** Standby / Prime Generator Sizing (ISO 8528)

**Request fields** (`GeneratorSizingRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `region` | string | no | `"gcc"` |
| `sub_region` | string | no | `""` |
| `loads` | array | **yes** | — |
| `site_altitude_m` | number | no | `0.0` |
| `ambient_temp_c` | number\|null | no | null |
| `gen_voltage` | integer | no | `400` |
| `phases` | integer | no | `3` |
| `rated_pf` | number | no | `0.8` |
| `supply_system` | string | no | `"standby"` | `standby` or `prime` |
| `max_voltage_dip_pct` | number | no | `15.0` |
| `future_expansion_pct` | number | no | `20.0` |
| `project_name` | string | no | `""` |

---

### POST /api/electrical/panel-schedule

**Summary:** Distribution Board / Panelboard Schedule

**Request fields** (`PanelScheduleRequest`): submits a list of circuit items.

Each item in `circuits`:
- `circuit_no` — string
- `description` — string
- `load_kw` — number
- `power_factor` — number
- *(additional fields per circuit)*

---

### POST /api/electrical/ups-sizing

**Summary:** UPS Sizing — IEC 62040 Battery Autonomy

Accepts a list of UPS loads and autonomy requirements. Returns recommended UPS kVA, battery capacity in Ah, and autonomy confirmation.

---

## HVAC / Mechanical Endpoints — `/api/mechanical`

### POST /api/mechanical/cooling-load

**Summary:** HVAC Cooling Load Calculation (ASHRAE / CIBSE / NBC)

**Request fields** (`CoolingLoadRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `region` | string | no | `"gcc"` |
| `zone_name` | string | no | `"Zone 1"` |
| `zone_type` | string | no | `"office"` |
| `floor_area_m2` | number | **yes** | — |
| `height_m` | number | no | `3.0` |
| `glass_area_m2` | number | no | `10.0` |
| `glass_u_value` | number | no | `2.8` |
| `glass_shgc` | number | no | `0.4` | Solar heat gain coefficient |
| `glass_orientation` | string | no | `"W"` | N, S, E, W, NE, NW, SE, SW |
| `wall_area_m2` | number | no | `60.0` |
| `wall_u_value` | number | no | `0.45` |
| `roof_area_m2` | number | no | `0.0` |
| `roof_u_value` | number | no | `0.35` |
| `occupancy` | integer | no | `10` |
| `metabolic_rate_w` | number | no | `90.0` |
| `equipment_w_m2` | number | no | `20.0` |
| `lighting_w_m2` | number | no | `10.0` |
| `fresh_air_l_s_person` | number | no | `10.0` |
| `cop` | number | no | `3.0` |
| `safety_factor` | number | no | `1.1` |

**Example request:**
```json
{
  "region": "gcc",
  "zone_name": "Open Plan Office",
  "zone_type": "office",
  "floor_area_m2": 300,
  "height_m": 3.5,
  "glass_area_m2": 60,
  "glass_u_value": 2.8,
  "glass_shgc": 0.4,
  "glass_orientation": "W",
  "wall_area_m2": 120,
  "wall_u_value": 0.45,
  "occupancy": 40,
  "equipment_w_m2": 20,
  "lighting_w_m2": 12,
  "fresh_air_l_s_person": 10
}
```

---

### POST /api/mechanical/duct-sizing

**Summary:** Duct Sizing — Equal Friction Method (SMACNA)

Each segment is sized individually. Request contains a list of `DuctSegmentRequest` objects:

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `segment_id` | string | no | `"S1"` |
| `airflow_l_s` | number | **yes** | — |
| `duct_type` | string | no | `"rectangular"` | `rectangular` or `circular` |
| `max_velocity_m_s` | number | no | `8.0` |
| `friction_rate_pa_m` | number | no | `0.8` |

**Example request:**
```json
{
  "region": "gcc",
  "segments": [
    {"segment_id": "S1", "airflow_l_s": 2500, "duct_type": "rectangular", "max_velocity_m_s": 8.0, "friction_rate_pa_m": 0.8},
    {"segment_id": "S2", "airflow_l_s": 1200, "duct_type": "rectangular", "max_velocity_m_s": 6.0, "friction_rate_pa_m": 0.8}
  ]
}
```

---

### POST /api/mechanical/multi-zone-cooling

**Summary:** Multi-Zone Cooling Load Summary

**Request fields** (`MultiZoneCoolingRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `region` | string | no | `"gcc"` |
| `zones` | array | **yes** | — | Each zone = `CoolingLoadRequest` fields |
| `chiller_cop` | number | no | varies by region |
| `diversity_factor` | number | no | `1.0` |

**Example request:**
```json
{
  "region": "gcc",
  "zones": [
    {"zone_name": "Office", "floor_area_m2": 300, "occupancy": 40, "glass_area_m2": 60, "glass_shgc": 0.4, "glass_orientation": "W"},
    {"zone_name": "Reception", "floor_area_m2": 50, "occupancy": 5, "glass_area_m2": 20, "glass_shgc": 0.4, "glass_orientation": "S"}
  ],
  "diversity_factor": 0.9
}
```

---

### POST /api/mechanical/heating-load

**Summary:** HVAC Heating Load Calculation (EN 12831 / CIBSE Guide A)

**Request fields** (`HeatingLoadRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `region` | string | no | `"europe"` |
| `zone_name` | string | no | `"Zone 1"` |
| `zone_type` | string | no | `"office"` |
| `floor_area_m2` | number | no | `100.0` |
| `height_m` | number | no | `3.0` |
| `wall_area_m2` | number | no | `80.0` |
| `wall_u_value` | number | no | `0.3` |
| `roof_area_m2` | number | no | `100.0` |
| `roof_u_value` | number | no | `0.2` |
| `window_area_m2` | number | no | `20.0` |
| `window_u_value` | number | no | `1.4` |
| `floor_area_m2_uninsulated` | number | no | `0.0` |
| `floor_u_value` | number | no | `0.25` |
| `infiltration_ach` | number | no | `0.5` |

---

### POST /api/mechanical/ventilation

**Summary:** Mechanical Ventilation Design (ASHRAE 62.1 / CIBSE Guide B / AS 1668.2)

**Request fields** (`VentilationRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `region` | string | no | `"europe"` |
| `zone_name` | string | no | `"Zone 1"` |
| `zone_type` | string | no | `"office"` |
| `floor_area_m2` | number | no | `200.0` |
| `height_m` | number | no | `3.0` |
| `occupancy` | integer | no | `20` |
| `fresh_air_method` | string | no | `"occupancy"` | `occupancy`, `ach`, or `area` |
| `fresh_air_l_s_person` | number | no | `10.0` |
| `fresh_air_ach` | number | no | `6.0` |
| `fresh_air_l_s_m2` | number | no | `1.5` |
| `supply_air_temp_c` | number | no | `18.0` |
| `room_temp_c` | number | no | `22.0` |
| `cooling_load_kw` | number | no | `10.0` |

---

## Plumbing Endpoints — `/api/plumbing`

### POST /api/plumbing/pipe-sizing

**Summary:** Cold/Hot Water Pipe Sizing (Hunter / Loading Unit Method)

Accepts a list of fixture demand units and returns recommended pipe diameters.

---

### POST /api/plumbing/drainage-sizing

**Summary:** Drainage Pipe Sizing (BS EN 12056 / IS 1742 / AS/NZS 3500.2)

**Request fields** (`DrainageSizingRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `region` | string | no | `"gcc"` |
| `system_type` | string | no | `"sanitary"` |
| `discharge_units` | number | no | `50.0` |
| `roof_area_m2` | number | no | `0.0` |
| `rainfall_intensity_mm_hr` | number | no | `100.0` |
| `gradient_percent` | number | no | `1.0` |
| `pipe_material` | string | no | `"uPVC"` |
| `simultaneous_use_factor` | number | no | `0.7` |

---

### POST /api/plumbing/pump-sizing

**Summary:** Pump Sizing (CIBSE C / ASHRAE / IS 1011 / AS 2941)

**Request fields** (`PumpSizingRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `region` | string | no | `"gcc"` |
| `system_type` | string | no | `"cold_water"` |
| `flow_rate_l_s` | number | no | `2.0` |
| `static_head_m` | number | no | `20.0` |
| `pipe_friction_loss_m` | number | no | `10.0` |
| `velocity_head_m` | number | no | `0.5` |
| `pump_efficiency` | number | no | `0.75` |
| `motor_efficiency` | number | no | `0.92` |
| `safety_factor` | number | no | `1.15` |
| `duty_standby` | boolean | no | `true` |

---

### POST /api/plumbing/hot-water-system

**Summary:** Hot Water System Design (CIBSE W / AS/NZS 3500.4 / IS 2065)

Accepts building type, occupancy, storage temperature, and heat-up time. Returns storage volume, heater kW, and daily energy (kWh).

---

### POST /api/plumbing/rainwater-harvesting

**Summary:** Rainwater Harvesting System Sizing (BS 8515 / AS 3959 / NBC)

**Request fields** (`RainwaterHarvestingRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `region` | string | no | `"gcc"` |
| `sub_region` | string | no | `""` |
| `roof_area_m2` | number | no | `1000.0` |
| `annual_rainfall_mm` | number | no | `120.0` |
| `runoff_coefficient` | number | no | `0.85` |
| `filter_efficiency_pct` | number | no | `90.0` |
| `num_occupants` | integer | no | `200` |
| `non_potable_l_person_day` | number | no | `40.0` |
| `storage_days` | integer | no | `7` |

---

### POST /api/plumbing/plumbing-tank-sizing

**Summary:** Cold/Fire Water Tank Sizing (BS EN 806 / AS 3500 / NBC)

Accepts building type, occupancy, storage hours, and fire reserve requirements. Returns recommended tank volume in m³ with compartment breakdown.

**Key request fields:**

| Field | Type | Notes |
|-------|------|-------|
| `region` | string | |
| `num_occupants` | integer | default `500` |
| `dwelling_units` | integer | default `0` |
| `daily_demand_l_person` | number | default `200.0` |
| `storage_hours` | number | default `24.0` |
| `fire_reserve_l` | number | default `0.0` |
| `tank_material` | string | default `"GRP"` |
| `operating_pressure_bar` | number | default `3.0` |

---

## Fire Protection Endpoints — `/api/fire`

### POST /api/fire/sprinkler

**Summary:** Sprinkler System Design (BS EN 12845 / NFPA 13)

**Request fields** (`SprinklerRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `region` | string | no | `"gcc"` |
| `occupancy_hazard` | string | no | `"OH1"` | LH, OH1, OH2, OH3, HH |
| `area_protected_m2` | number | **yes** | — |
| `ceiling_height_m` | number | no | `4.0` |
| `sprinkler_coverage_m2` | number | no | `9.0` |
| `sprinkler_k_factor` | number | no | `80.0` |
| `design_area_m2` | number\|null | no | null | Overrides default from hazard class |
| `design_density_mm_min` | number\|null | no | null | Overrides default from hazard class |
| `hose_allowance_l_min` | number | no | `500.0` |

**Example request:**
```json
{
  "region": "gcc",
  "sub_region": "dewa",
  "occupancy_hazard": "OH2",
  "area_protected_m2": 2000,
  "ceiling_height_m": 4.0,
  "sprinkler_k_factor": 80,
  "hose_allowance_l_min": 500
}
```

**curl:**
```bash
curl -X POST http://localhost:8000/api/fire/sprinkler \
  -H "Content-Type: application/json" \
  -d '{"region":"gcc","occupancy_hazard":"OH2","area_protected_m2":2000}'
```

---

### POST /api/fire/fire-pump

**Summary:** Fire Pump Sizing (BS EN 12845 / NFPA 20 / NBC / AS 2941)

**Request fields** (`FirePumpRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `region` | string | no | `"gcc"` |
| `system_type` | string | no | `"wet_riser"` |
| `sprinkler_demand_l_min` | number | no | `2000.0` |
| `hose_reel_demand_l_min` | number | no | `600.0` |
| `hydrant_demand_l_min` | number | no | `0.0` |
| `static_pressure_required_bar` | number | no | `6.5` |
| `friction_loss_bar` | number | no | `1.5` |
| `elevation_loss_bar` | number | no | `2.0` |
| `pump_efficiency` | number | no | `0.72` |
| `motor_efficiency` | number | no | `0.9` |
| `duty_standby_jockey` | boolean | no | `true` |

---

### POST /api/fire/fire-tank

**Summary:** Fire Water Storage Tank Sizing (BS EN 12845 / NFPA 22 / NBC / AS 2118)

**Request fields** (`FireTankRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `region` | string | no | `"gcc"` |
| `system_type` | string | no | `"sprinkler"` |
| `total_flow_l_min` | number | no | `2000.0` |
| `supply_duration_min` | number | no | `60.0` |
| `hose_allowance_l` | number | no | `3000.0` |
| `additional_allowance_pct` | number | no | `10.0` |
| `number_of_compartments` | integer | no | `2` |
| `refill_time_hr` | number | no | `4.0` |

---

### POST /api/fire/standpipe

**Summary:** Standpipe / Wet Riser System (NFPA 14 / BS 5306 / NBC / AS 2118.1)

**Request fields** (`StandpipeRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `region` | string | no | `"gcc"` |
| `system_class` | string | no | `"III"` | I, II, III |
| `building_height_m` | number | no | `30.0` |
| `num_floors` | integer | no | `10` |
| `floor_height_m` | number | no | `3.0` |
| `hose_connection_spacing_m` | number | no | `30.0` |
| `pressure_at_outlet_bar` | number | no | `6.5` |
| `flow_per_standpipe_l_min` | number | no | `950.0` |
| `num_operating_standpipes` | integer | no | `2` |
| `pipe_material` | string | no | `"steel_galvanised"` |

---

## BOQ Endpoints — `/api/boq`

### POST /api/boq/generate

**Summary:** Generate MEP Bill of Quantities

**Request fields** (`MepBoQRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `project_name` | string | no | `""` |
| `project_reference` | string | no | `""` |
| `region` | string | no | `"gcc"` |
| `sub_region` | string | no | `""` |
| `currency` | string | no | `"USD"` | `USD`, `AED`, `SAR`, `QAR`, `KWD`, `GBP`, `EUR`, `INR`, `AUD` |
| `cables` | array | no | `[]` | List of `CableBoQItem` |
| `ducts` | array | no | `[]` | List of `DuctBoQItem` |
| `pipes` | array | no | `[]` | List of pipe items |

Each `CableBoQItem`:

| Field | Type | Default |
|-------|------|---------|
| `circuit_reference` | string | `""` |
| `description` | string | `""` |
| `cable_type` | string | `"XLPE_CU"` |
| `cable_size_mm2` | number | `0.0` |
| `phases` | integer | `3` |
| `cable_length_m` | number | `0.0` |
| `runs` | integer | `1` |
| `conduit_diameter_mm` | number\|null | null |
| `tray_width_mm` | number\|null | null |

**Example request:**
```json
{
  "project_name": "Mixed-Use Tower",
  "region": "gcc",
  "sub_region": "dewa",
  "currency": "AED",
  "cables": [
    {
      "circuit_reference": "C-DB-L1-01",
      "description": "Feeder cable to DB-L1",
      "cable_type": "XLPE_CU",
      "cable_size_mm2": 16,
      "phases": 3,
      "cable_length_m": 80,
      "runs": 1
    }
  ]
}
```

---

### GET /api/boq/rates

**Summary:** Get Indicative Unit Rates by Region and Discipline

**Query params:** `region` (optional), `discipline` (optional — `electrical`, `hvac`, `plumbing`, `fire`)

Returns JSON with indicative material and labour unit rates in the local currency for the selected region.

---

## Compliance Endpoints — `/api/compliance`

### POST /api/compliance/check

**Summary:** Run MEP Compliance Report

**Request fields** (`ComplianceReportRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `project_name` | string | no | `""` |
| `project_reference` | string | no | `""` |
| `region` | string | no | `"gcc"` |
| `sub_region` | string | no | `""` |
| `discipline` | string | no | `"electrical"` |
| `cable_checks` | array | no | `[]` | List of `CableComplianceCheck` |
| `lighting_checks` | array | no | `[]` |
| `mechanical_checks` | array | no | `[]` |
| `plumbing_checks` | array | no | `[]` |
| `fire_checks` | array | no | `[]` |

Each `CableComplianceCheck`:

| Field | Type |
|-------|------|
| `circuit_reference` | string |
| `region` | string |
| `sub_region` | string |
| `design_current_a` | number |
| `derated_rating_iz_a` | number |
| `voltage_drop_pct` | number |
| `vd_limit_pct` | number |
| `cable_size_mm2` | number |
| `earth_size_mm2` | number |

---

### GET /api/compliance/standards-reference

**Summary:** Regional Standards Reference Table

**Query params:** `region` (optional)

Returns a table of applicable standards by discipline for the requested region.

---

## Report Endpoints — `/api/reports`

### POST /api/reports/calculation-report

**Summary:** Generate Calculation Report Data

**Request fields** (`CalculationReportRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `metadata` | `ReportMetadata` | **yes** | — |
| `calculations` | array | no | `[]` | List of `CalculationEntry` |
| `include_appendix` | boolean | no | `true` |

`ReportMetadata` fields:

| Field | Type | Default |
|-------|------|---------|
| `project_name` | string | `""` |
| `project_number` | string | `""` |
| `client` | string | `""` |
| `location` | string | `""` |
| `prepared_by` | string | `""` |
| `checked_by` | string | `""` |
| `approved_by` | string | `""` |
| `revision` | string | `"P1"` |
| `date` | string\|null | null |
| `discipline` | string | `"MEP"` |
| `region` | string | `"gcc"` |
| `report_title` | string | `"Engineering Calculation Report"` |

Each `CalculationEntry`:

| Field | Type |
|-------|------|
| `section` | string |
| `reference` | string |
| `description` | string |
| `result_summary` | object |
| `standard` | string |
| `compliant` | boolean |
| `notes` | string |

**Example request:**
```json
{
  "metadata": {
    "project_name": "Office Tower Block A",
    "project_number": "2024-MEP-001",
    "location": "Dubai, UAE",
    "prepared_by": "J. Smith CEng MIET",
    "checked_by": "M. Ahmed",
    "revision": "P1",
    "discipline": "Electrical",
    "region": "gcc"
  },
  "calculations": [
    {
      "section": "4.1",
      "reference": "CS-01",
      "description": "Cable sizing — Feeder to DB-L1",
      "result_summary": {"selected_size_mm2": 16, "overall_compliant": true},
      "standard": "BS 7671:2018+A2:2022",
      "compliant": true,
      "notes": "XLPE Cu, Method C, 80m run"
    }
  ],
  "include_appendix": true
}
```

---

### GET /api/reports/templates

**Summary:** List Available Report Templates

Returns a list of calculation report types with their required metadata and calculation entry formats.

**curl:** `curl http://localhost:8000/api/reports/templates`

---

### GET /api/reports/standards-data

**Summary:** Embedded Standards Reference Data

**Query params:** `region` (optional), `discipline` (optional)

Returns the standards reference data used internally by OpenMEP calculation engines.

---

## Error Responses

All endpoints use standard HTTP status codes:

| Code | Meaning | Common Cause |
|------|---------|-------------|
| 200 | OK | Success |
| 422 | Unprocessable Entity | Missing required field or invalid value — check `detail` array |
| 404 | Not Found | Unknown endpoint |
| 500 | Internal Server Error | Calculation engine error — check server logs |

**422 Example (missing required field):**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "area_protected_m2"],
      "msg": "Field required",
      "input": {"region": "gcc", "occupancy_hazard": "OH2"}
    }
  ]
}
```

---

## Complete Endpoint Reference

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health — returns `{"status":"healthy","service":"openmep-api"}` |
| GET | `/` | API root / welcome |
| POST | `/api/electrical/cable-sizing` | Cable size (BS 7671 / AS/NZS 3008 / IS 3961) |
| GET | `/api/electrical/cable-sizing` | Cable sizing via query params |
| GET | `/api/electrical/cable-sizing/options` | Valid cable types, installation methods, regions |
| GET | `/api/electrical/standards` | Electrical standards list by region |
| POST | `/api/electrical/voltage-drop` | Voltage drop check |
| POST | `/api/electrical/maximum-demand` | Maximum demand with load schedule |
| POST | `/api/electrical/short-circuit` | Short-circuit current (IEC 60909) |
| POST | `/api/electrical/lighting` | Lighting design (lumen method) |
| POST | `/api/electrical/pf-correction` | Capacitor bank sizing (IEC 60831-1) |
| POST | `/api/electrical/generator-sizing` | Generator sizing (ISO 8528) |
| POST | `/api/electrical/panel-schedule` | Panel schedule with load balance |
| POST | `/api/electrical/ups-sizing` | UPS sizing (IEC 62040) |
| POST | `/api/mechanical/cooling-load` | HVAC cooling load |
| POST | `/api/mechanical/duct-sizing` | Duct sizing (SMACNA equal-friction) |
| POST | `/api/mechanical/multi-zone-cooling` | Multi-zone cooling summary |
| POST | `/api/mechanical/heating-load` | Heating load (EN 12831 / CIBSE A) |
| POST | `/api/mechanical/ventilation` | Ventilation design (ASHRAE 62.1 / AS 1668.2) |
| POST | `/api/plumbing/pipe-sizing` | Pipe sizing (loading unit method) |
| POST | `/api/plumbing/drainage-sizing` | Drainage sizing (DU method) |
| POST | `/api/plumbing/pump-sizing` | Pump sizing (Darcy-Weisbach) |
| POST | `/api/plumbing/hot-water-system` | Hot water storage and heater design |
| POST | `/api/plumbing/rainwater-harvesting` | Rainwater harvesting tank |
| POST | `/api/plumbing/plumbing-tank-sizing` | Cold water break cistern with fire reserve |
| POST | `/api/fire/sprinkler` | Sprinkler hydraulics (NFPA 13 / BS EN 12845) |
| POST | `/api/fire/fire-pump` | Fire pump sizing (NFPA 20 / BS EN 12845) |
| POST | `/api/fire/fire-tank` | Fire water storage volume |
| POST | `/api/fire/standpipe` | Wet riser / standpipe design |
| POST | `/api/boq/generate` | Generate MEP Bill of Quantities |
| GET | `/api/boq/rates` | Indicative unit rates by region / discipline |
| POST | `/api/compliance/check` | Multi-standard compliance matrix |
| GET | `/api/compliance/standards-reference` | Standards reference by region |
| POST | `/api/reports/calculation-report` | Generate calculation report data |
| GET | `/api/reports/templates` | List available report templates |
| GET | `/api/reports/standards-data` | Embedded standards reference data |

*Total: 35 endpoints. For full interactive request/response schema explorer, visit `http://localhost:8000/docs`.*
