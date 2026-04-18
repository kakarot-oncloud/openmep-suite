# OpenMEP User Guide

**Version 0.2.1 | March 2025 | Made by Luquman A**

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Region Selection](#2-region-selection)
3. [Electrical Modules](#3-electrical-modules)
4. [HVAC / Mechanical Modules](#4-hvac--mechanical-modules)
5. [Plumbing Modules](#5-plumbing-modules)
6. [Fire Protection Modules](#6-fire-protection-modules)
7. [Project Tools](#7-project-tools)
8. [Interpreting Results](#8-interpreting-results)
9. [Exporting Reports](#9-exporting-reports)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Getting Started

### Launch the Application

```bash
# Start the backend API (required for all calculations)
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Start the Streamlit UI (in a separate terminal)
streamlit run streamlit_app/app.py
```

Open `http://localhost:8501` in your browser. You will see the OpenMEP home page with the project logo and navigation sidebar.

### Navigation

The left sidebar lists all 26 modules grouped by discipline:

- **Electrical** — 8 modules
- **HVAC** — 4 modules
- **Plumbing** — 6 modules
- **Fire Protection** — 4 modules
- **Project Tools** — 4 modules

Click any module name to navigate to it.

---

## 2. Region Selection

Every calculation module begins with the **Region Selector** — a three-level dropdown:

| Level | Example |
|-------|---------|
| **Region** | GCC / UAE / Saudi / Qatar / Kuwait |
| **Country / State / Sub-Region** | UAE, Saudi Arabia, Qatar, Kuwait |
| **Utility / Authority Having Jurisdiction** | DEWA (Dubai), ADDC (Abu Dhabi), SEC (KSA) |

Selecting a region/utility automatically switches:
- The applicable design standard (e.g., BS 7671:2018 AMD2 for DEWA, IS 3961 for India)
- Ambient temperature defaults (e.g., 40°C for GCC, 25°C for UK)
- Currency and cost indices for BOQ export

**Important:** Always set the region before entering other parameters. Changing the region after entering parameters will reset the form.

### Region Quick Reference

| Selection | Standards Applied |
|-----------|-------------------|
| GCC → UAE → DEWA | BS 7671, NFPA 13, DEWA Technical Requirements |
| GCC → KSA → SEC | BS 7671, NFPA, Saudi Building Code (SBC) |
| Europe → UK | BS 7671:2018 AMD2, CIBSE Guides, BS EN 12056 |
| Europe → Germany | DIN VDE 0100, EN 12831, DIN 1988 |
| India → Maharashtra | IS 3961, IS SP7, NBC 2016, CPWD DSR |
| Australia → NSW | AS/NZS 3008, AS 1170, AS 3500, NCC Volume 1 |

---

## 3. Electrical Modules

### 3.1 Cable Sizing (Page 1)

Calculates the minimum cable cross-sectional area for a given load.

**Inputs:**
- Load power (kW), power factor, phases (1 or 3)
- Supply voltage (V)
- Cable type: XLPE/Cu, PVC/Cu, XLPE/Al
- Installation method: A1, A2, B1, B2, C, D1, D2, E, F (per BS 7671 Appendix 4 / AS/NZS 3008 Table column)
- Cable length (m)
- Ambient temperature (°C)
- Number of circuits in group (for grouping derating)

**Outputs:**
- Design current (A)
- Recommended cable size (mm²)
- Installed current capacity (A)
- Voltage drop (V and %)
- Applied derating factors
- Applicable standard and method

**Notes:**
- For Australia, installation methods are automatically mapped to AS/NZS 3008 column references (A1→col_6, C→col_22, etc.)
- Ambient temperature derating uses Correction Factor Ca per the applicable standard

---

### 3.2 Voltage Drop (Page 2)

Verifies that voltage drop along a cable run is within the permitted limit.

**Inputs:**
- Current (A), phases, cable length (m)
- Conductor size (mm²), material (Cu/Al)
- Supply voltage (V)

**Outputs:**
- Voltage drop (V)
- Voltage drop (%)
- Pass/Fail against standard limit (4% for power circuits, 3% for lighting per BS 7671 / IS)

---

### 3.3 Maximum Demand (Page 3)

Calculates the maximum demand at the supply intake using utility diversity factors.

**Inputs:**
- Load schedule: description, kW rating, demand factor, quantity
- Utility authority (for correct diversity table)

**Outputs:**
- Connected load (kW/kVA)
- Maximum demand (kW/kVA)
- Recommended main fuse/breaker (A)
- Applicable diversity table reference

---

### 3.4 Short Circuit Current (Page 4)

Calculates short circuit fault currents using IEC 60909.

**Inputs:**
- Transformer rating (kVA), impedance (%), X/R ratio
- Cable impedance to fault point
- Fault type: 3-phase, line-to-line, line-to-earth

**Outputs:**
- Peak short circuit current (kA)
- Symmetrical fault current (kA)
- Minimum fault current (for protection setting)
- Breaking capacity recommendation

---

### 3.5 Lighting Design (Page 5)

Calculates luminaire quantity for a target illuminance using the lumen method.

**Inputs:**
- Room dimensions (L × W × H), work plane height (m)
- Target illuminance (lux) — from CIBSE LG7 / AS 1680 table
- Luminaire flux (lm), luminaire efficiency
- Maintenance factor, Room Index calculation is automatic

**Outputs:**
- Room Index
- Utilisation factor (from standard table)
- Number of luminaires required
- Actual achieved illuminance (lux)
- Power density (W/m²)

---

### 3.6 Panel Schedule (Page 10)

Generates a formatted panel schedule with load balancing.

**Inputs:**
- Panel voltage (230 V single-phase or 415 V 3-phase)
- Circuit list: description, kW, power factor, breaker size, phase

**Outputs:**
- Per-phase load (kW and A)
- Load imbalance percentage
- Total panel kW, kVA, and recommended incomer size (A)
- Formatted panel schedule table (exportable)

---

### 3.7 Generator Sizing (Page 11)

Sizes a standby or prime power generator.

**Inputs:**
- Load schedule with starting method (VFD, Star-Delta, DOL, Soft-Start)
- Power factor, demand factor per load
- Required autonomy (hours), fuel type

**Outputs:**
- Running load (kW)
- Starting kVA per load (with starting method factor)
- Step load analysis (largest start-up block)
- Recommended generator rating (kVA)
- Estimated fuel consumption (L/hr)

---

### 3.8 Power Factor Correction (Page 12)

Sizes a capacitor bank to improve power factor.

**Inputs:**
- Active power (kW)
- Existing power factor, target power factor
- Supply voltage, phases
- Transformer kVA, number of transformers
- Apply harmonic derating (5th harmonic, 7th harmonic)

**Outputs:**
- Required capacitor bank (kVAr)
- Recommended standard capacitor size (kVAr steps)
- After-correction power factor
- Estimated kVA reduction
- Payback period (months) at current tariff

---

## 4. HVAC / Mechanical Modules

### 4.1 Cooling Load (Page 6)

Calculates design cooling load using ASHRAE CLTD/CLF method.

**Inputs:**
- Room dimensions and orientation
- Wall/roof construction (U-value or construction type)
- Window area, glazing type, shading coefficient
- Occupancy (people), lighting (W/m²), equipment (W)
- Outside/inside design temperatures

**Outputs:**
- Transmission cooling load (kW) — walls, roof, glass
- Internal gains (kW) — people, lighting, equipment
- Ventilation load (kW)
- Total sensible/latent/total cooling load (kW and tons)
- Safety margin applied per region

---

### 4.2 Duct Sizing (Page 7)

Sizes rectangular/circular ducts using the equal-friction method.

**Inputs:**
- Airflow (l/s or m³/hr)
- Desired friction rate (Pa/m)
- Duct material and shape
- Maximum velocity limit

**Outputs:**
- Circular equivalent diameter (mm)
- Rectangular duct size (mm × mm)
- Actual velocity (m/s) — checked against SMACNA limits
- Friction rate (Pa/m)
- Aspect ratio check

---

### 4.3 Heating Load (Page 17)

Calculates building heating load using EN 12831 (Europe) or CIBSE Guide A (UK/GCC).

**Inputs:**
- Room dimensions
- U-values for floor, walls, roof, windows, doors
- Design temperatures (inside and outside)
- Ventilation rate (ACH or l/s per person)
- Infiltration rate

**Outputs:**
- Transmission heat loss (W)
- Ventilation heat loss (W)
- Total heating load (W and kW)
- Design temperature difference
- Applicable standard and climate data source

---

### 4.4 Ventilation (Page 18)

Calculates outdoor air requirements using ASHRAE 62.1 or AS 1668.2.

**Inputs:**
- Occupancy type (office, classroom, retail, etc.)
- Floor area (m²) and design occupancy
- Required outdoor air per person and per area
- Heat recovery effectiveness (%)

**Outputs:**
- Outdoor air requirement (l/s and m³/hr)
- Air changes per hour
- Heat recovery energy saving (kW)
- Applicable ASHRAE 62.1 / AS 1668 table reference

---

## 5. Plumbing Modules

### 5.1 Pipe Sizing (Page 8)

Sizes water supply pipework using the loading unit method.

**Inputs:**
- Fixture schedule: WC, basin, shower, bath, urinal, etc.
- Water type: hot, cold, mixed
- Pipe material: copper, CPVC, GI, uPVC
- Supply pressure (bar)

**Outputs:**
- Total loading units
- Design flow rate (l/s)
- Recommended pipe diameter (mm)
- Velocity check (m/s)
- Pressure drop (kPa)

---

### 5.2 Drainage Sizing (Page 19)

Sizes soil and waste drainage stacks using BS EN 12056 discharge units.

**Inputs:**
- Fixture schedule (WC, washbasin, bath, shower, sink, etc.)
- Stack type: primary, secondary
- Gradient (1:40, 1:60, 1:80)

**Outputs:**
- Total discharge units (DU)
- Design flow rate (l/s)
- Recommended branch/stack diameter (mm)
- Gradient check

---

### 5.3 Pump Sizing (Page 20)

Sizes a water or HVAC circulating pump.

**Inputs:**
- Design flow rate (l/s)
- Pipe run details: lengths, diameters, fittings (expressed as equivalent lengths)
- Static head (m)
- Pipe material and fluid

**Outputs:**
- Friction head (m WG) using Darcy-Weisbach
- Total system head (m WG)
- Required pump duty: flow (l/s) × head (m)
- NPSH check for suction lift applications
- Motor power estimate (kW) at assumed efficiency

---

### 5.4 Hot Water System (Page 21)

Designs a centralised hot water system.

**Inputs:**
- Building type, number of fixtures
- Supply and storage temperatures (°C)
- Heat-up period (hours)
- Legionella pasteurisation requirements

**Outputs:**
- Simultaneous demand (l/min)
- Storage volume (litres)
- Heat-up energy (kW)
- Legionella pasteurisation schedule
- Applicable standard reference

---

### 5.5 Rainwater Harvesting (Page 25)

Sizes a rainwater harvesting tank.

**Inputs:**
- Roof catchment area (m²), runoff coefficient
- Annual rainfall (mm/year), dry spell (days)
- Demand: flushing, irrigation, laundry (l/day)
- Mains backup: yes/no

**Outputs:**
- Harvestable rainfall volume (m³/year)
- Tank size (m³)
- Mains water offset percentage
- Overflow pipe size (mm)
- Standard reference: BS 8515 / AS 3500.1 / NBC

---

### 5.6 Plumbing Tank Sizing (Page 26)

Sizes a break cistern / cold water storage tank.

**Inputs:**
- Occupancy type and number of occupants
- Per capita daily demand (l/person/day) — auto-populated from standard
- Storage period (hours): typically 24 hr for institutional, 12 hr for commercial
- Fire reserve requirement

**Outputs:**
- Domestic storage volume (m³)
- Fire reserve volume (m³)
- Combined tank volume (m³)
- Recommended tank dimensions
- Inlet and outlet pipe sizes

---

## 6. Fire Protection Modules

### 6.1 Sprinkler Design (Page 9)

Hydraulically calculates the sprinkler system for the most unfavourable head.

**Inputs:**
- Occupancy hazard: Light, Ordinary 1/2/3, Extra High (BS EN 12845) or Light/Ordinary/Extra (NFPA 13)
- Sprinkler K-factor (l/min/bar^0.5)
- Most unfavourable head pressure (bar)
- Number of heads in hydraulic remote area
- Pipe grid configuration

**Outputs:**
- Minimum head flow (l/min)
- Design area flow (l/min)
- System pressure at pump (bar)
- Pipe sizes to most unfavourable area
- Applicable standard and hazard class reference

---

### 6.2 Fire Pump (Page 22)

Sizes the fire pump set.

**Inputs:**
- Sprinkler system demand (l/min)
- Hose reel / hydrant demand (l/min)
- System pressure (bar)
- Friction and elevation losses (bar)
- Pump type: electric, diesel, jockey

**Outputs:**
- Rated duty flow (l/min) and pressure (bar)
- Jockey pump parameters
- Diesel prime mover fuel capacity
- Test loop return pipe size
- Applicable standard: BS EN 12845 / NFPA 20

---

### 6.3 Fire Tank (Page 23)

Calculates combined fire and domestic water storage.

**Inputs:**
- Operating duration (minutes) per standard
- System demand (l/min)
- Domestic daily demand (m³/day)

**Outputs:**
- Fire reserve volume (m³)
- Domestic reserve volume (m³)
- Combined tank volume (m³)
- Inlet flow rate required (l/s)
- Inlet and outlet pipe sizes

---

### 6.4 Standpipe / Wet Riser (Page 24)

Designs the standpipe or wet riser system.

**Inputs:**
- Class: I, II, or III (NFPA 14) / Dry Riser / Wet Riser (BS 9990)
- Number of outlets per floor
- Building height (m), number of floors
- Pressure at highest outlet (bar)

**Outputs:**
- Design flow (l/min)
- Riser pipe size (mm)
- Pump pressure (bar)
- Pressure-reducing valves required (yes/no, floor numbers)
- Applicable standard and class

---

## 7. Project Tools

### 7.1 BOQ Generator (Page 13)

Generates a Bill of Quantities in the regional standard format, exported as Excel.

**Steps:**
1. Select region (determines schema: FIDIC/NRM2/CPWD/AIQS)
2. Select discipline(s) and project type
3. Click **Generate BOQ**
4. Download the Excel workbook

**Output:** Multi-sheet Excel workbook with:
- Cover sheet (project title block)
- One sheet per discipline (Electrical, HVAC, Plumbing, Fire)
- Summary sheet with grand totals in local currency and USD
- FX rates sourced live from the API

---

### 7.2 Compliance Checker (Page 14)

Checks a set of design parameters against multiple regional standards simultaneously.

**Inputs:**
- Cable size, protective device, earthing arrangement
- Fire life safety: sprinkler coverage, exit signage, emergency lighting

**Outputs:**
- Pass/Fail table per standard
- Non-compliant items highlighted in red
- Reference clause for each check

---

### 7.3 PDF Reports (Page 15)

Generates a formatted A4 PDF calculation report.

**Steps:**
1. Select the calculation type (e.g., Cable Sizing, Cooling Load)
2. Enter parameters (same form as the standalone module)
3. Fill in the project title block (project, location, engineer, date, revision)
4. Click **Generate PDF Report**
5. Download the PDF

**Output:** A4 PDF with letterhead, calculation methodology, results table, and sign-off block.

---

### 7.4 Submittal Tracker (Page 16)

Tracks the status of project submittals, RFIs, and equipment lists.

**Features:**
- Add/edit/delete submittals with status: Pending, Submitted, Approved, Returned, Superseded
- Add RFIs with question, response, and response date
- Add equipment items linked to submittals
- Export to Excel

---

## 8. Interpreting Results

### Status Indicators

| Colour | Meaning |
|--------|---------|
| Green | Compliant / within limits |
| Amber | Marginal — review with designer |
| Red | Non-compliant — resize required |

### Units

All outputs use SI units unless the regional standard requires otherwise:
- Power: kW / kVA
- Current: A
- Voltage drop: V and %
- Flow: l/s, l/min, m³/hr
- Pressure: bar (fire), kPa (plumbing), Pa (HVAC)
- Cable: mm²

---

## 9. Exporting Reports

| Module | Export Format |
|--------|---------------|
| BOQ Generator | Excel (.xlsx) |
| Panel Schedule | Table (on-screen) |
| Submittal Tracker | Excel (.xlsx) |
| PDF Reports | PDF (A4) |
| Compliance Checker | PDF (A4) |

---

## 10. Troubleshooting

### "Connection refused" / API not available

The Streamlit app calls the FastAPI backend at `http://localhost:8000`. If this connection fails:

```bash
# Check the backend is running
curl http://localhost:8000/health

# If not, start it:
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Unexpected calculation results

1. Verify the correct region and utility authority are selected
2. Check that the ambient temperature matches your project location
3. For cable sizing, verify the installation method matches your actual installation (see BS 7671 Appendix 4 for method descriptions)

### Excel export not downloading

Ensure `openpyxl` is installed: `pip install openpyxl`

### PDF report blank

Ensure `reportlab` is installed: `pip install reportlab`

---

*For further assistance, open a GitHub issue at [github.com/kakarot-oncloud/openmep](https://github.com/kakarot-oncloud/openmep).*
