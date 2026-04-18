# India Region Guide

**OpenMEP v0.1.0 | India**

---

## Overview

India follows the Bureau of Indian Standards (BIS) national standards for all MEP disciplines, with the National Building Code (NBC 2016) as the overarching regulatory framework. State Electricity Boards (SEBs) and local Distribution Companies (DISCOMs) may impose additional requirements.

---

## Sub-Regions and Authorities

### States and Distribution Companies

| State | DISCOM(s) | Region Code |
|-------|-----------|-------------|
| Maharashtra | MSEDCL (MAHADISCOM), BEST (Mumbai) | india_mh |
| Karnataka | BESCOM (Bengaluru), CESC, HESCOM | india_ka |
| Tamil Nadu | TANGEDCO | india_tn |
| Delhi NCT | BSES Rajdhani, BSES Yamuna, TPDDL | india_dl |
| Gujarat | DGVCL, MGVCL, PGVCL, UGVCL | india_gj |
| Rajasthan | JDVVNL, AVVNL, JVVNL | india_rj |
| Uttar Pradesh | DVVNL, MVVNL, PaVVNL, PUVVNL | india_up |
| West Bengal | WBSEDCL, CESC | india_wb |
| Telangana | TSSPDCL, TSNPDCL | india_tg |

---

## Design Standards — Electrical

| Standard | Full Title | Edition | Used For |
|----------|-----------|---------|----------|
| IS 3961 | Recommended Current Ratings for Cables | 2011 | Cable sizing (main standard) |
| IS 1646 | Code of Practice for Fire Safety of Buildings (Electrical Installations) | 1997 | Electrical fire safety |
| IS 732 | Code of Practice for Electrical Wiring Installations | 2019 | Wiring method |
| IS 3043 | Code of Practice for Earthing | 1987 (R2021) | Earthing systems |
| IS 5613 | Code of Practice for Design, Installation and Maintenance of Overhead Lines | Part 1–3 | HV lines |
| IS 9537 | Conduits for Electrical Installations | Parts 1–4 | Conduit sizing |
| SP 7 | National Building Code (NBC) 2016, Part 8 — Electrical | 2016 | Overall compliance framework |
| CEA Regulations | Central Electricity Authority Regulations on Safety | 2010 | Statutory compliance |

**Ambient Temperature:** 35°C (IS 3961 basis); correction factors available for 40°C, 45°C, and 50°C for outdoor/hot-climate installations.

**Cable Types Supported (IS 3961):**
- PVC/Cu (most common)
- XLPE/Cu (HV and important circuits)
- PVC/Al (distribution mains)
- XLPE/Al (MV distribution)

**Supply Voltage:** 415/240 V, 50 Hz (LT); 11 kV, 33 kV (HT).

**Voltage Drop Limit:** 5% from supply terminal to farthest point (IS 732 Clause 12); 3% for lighting recommended by SP 7.

---

## Design Standards — HVAC

| Standard | Full Title | Edition | Used For |
|----------|-----------|---------|----------|
| IS 8695 | Code of Practice for Conservation of Energy in Air-Conditioning Systems | 1978 (R2018) | Cooling load reference |
| ECBC 2017 | Energy Conservation Building Code | 2017 | Energy efficiency compliance |
| NBC 2016 Part 8 Sec 3 | HVAC | 2016 | HVAC design |
| ASHRAE 62.1 | Ventilation for Acceptable IAQ | 2022 | Outdoor air rates |
| SP 7 NBC 2016 | National Building Code | 2016 | Overall framework |

**India Outdoor Design Conditions (IS climatological data):**

| City | Summer DB (°C) | Summer WB (°C) | Monsoon (°C) | Winter (°C) |
|------|---------------|---------------|-------------|------------|
| Mumbai | 35 | 28 | 32 / 95%RH | 23 |
| Delhi | 44 | 26 | 38 | 5 |
| Bengaluru | 35 | 22 | 28 | 16 |
| Chennai | 38 | 28 | 36 | 25 |
| Kolkata | 38 | 28 | 34 | 13 |
| Hyderabad | 40 | 26 | 32 | 18 |
| Ahmedabad | 44 | 27 | 34 | 12 |
| Pune | 38 | 24 | 30 | 14 |

---

## Design Standards — Plumbing

| Standard | Full Title | Edition | Used For |
|----------|-----------|---------|----------|
| IS 1172 | Code of Basic Requirements for Water Supply, Drainage and Sanitation | 1983 (R2019) | Per capita water demand |
| IS 4111 | Code of Practice for Ancillary Structures in Sewerage Systems | Part 1, 2013 | Manholes and inspection chambers |
| IS 5329 | Code of Practice for Sanitary Pipework above Ground for Buildings | 2005 | Drainage sizing |
| IS 1239 | Mild Steel Tubes, Tubulars and Other Wrought Steel Fittings | Part 1, 2004 | GI pipe selection |
| NBC 2016 Part 9 | Plumbing Services | 2016 | Overall plumbing framework |

**Per Capita Daily Demand (IS 1172):**

| Building Type | Litres/person/day |
|--------------|------------------|
| Residential (municipal) | 135 |
| Residential (premium) | 200 |
| Hotels (per bed) | 180 |
| Offices | 45 |
| Hospitals (per bed) | 340 |
| Schools (per pupil) | 45 |
| Industrial | 30–45 |

---

## Design Standards — Fire Protection

| Standard | Full Title | Edition | Used For |
|----------|-----------|---------|----------|
| NBC 2016 Part 4 | Fire and Life Safety | 2016 | Overall fire framework |
| IS 15105 | Design and Installation of Fixed Automatic Sprinkler Fire Extinguishing Systems | 2002 | Sprinkler design |
| TAC Guidelines | Tariff Advisory Committee Guidelines | 2012 | Insurance authority sprinkler requirements |
| IS 3844 | Code of Practice for Installation and Maintenance of Hydrant Systems | 1989 (R2021) | Hydrant and hose reel |
| IS 9668 | Provision and Maintenance of Water Supplies | 1990 | Fire water storage |

**India Fire Hazard Classification (NBC 2016):**

| Hazard Class | Occupancy |
|-------------|----------|
| Low Hazard | Offices, hotels, hospitals, assembly |
| Moderate Hazard | Retail, storage (non-hazardous), workshops |
| High Hazard | Warehouses, paint shops, timber yards |

---

## Input Parameters — Region-Specific Defaults

| Parameter | India Default | Note |
|-----------|--------------|------|
| Supply voltage | 415/240 V, 50 Hz | LT supply |
| Ambient temperature | 35°C (IS 3961 Table 1) | Increase to 40–45°C in hot zones |
| Cable type | PVC/Cu | Most common; XLPE for important circuits |
| Earthing | TN-S (IS 3043) | Separate N and PE at HV/LV transformer |
| Voltage drop limit | 5% (IS 732) | 3% lighting recommended |
| Per capita water | 135 l/p/day | Municipal; 200 for premium |
| Fire storage duration | 30 min (NBC Cl 6.9) | For wet riser systems |

---

## Output Format

### PDF Report Header (India)

```
PROJECT: [Name]                   REPORT No: [Ref]
CLIENT:  [Client]                 REVISION:  [Rev]
LOCATION:[City, State]            DATE:      [Date]
ENGINEER:[Name, Chartered Engr]   STANDARD:  IS 3961 / NBC 2016
CHECKED: [Name]                   AUTHORITY: [MSEDCL/BESCOM/TANGEDCO]
```

### BOQ Schema

India BOQ follows **CPWD Schedule of Rates / DSR** (Directorate General of Works, Central Public Works Department). OpenMEP generates:
- CPWD DSR item number
- Description
- Unit, Quantity, Rate (INR), Amount (INR), Amount (USD)
- Preamble: "Rates as per CPWD DSR [year] with applicable State factor. Contractor to verify current DSR rates."

---

## Known Limitations

1. **State-specific DISCOM requirements** — detailed sub-region requirements not yet modelled; IS standards used as the base
2. **ECBC 2017 compliance check** — energy efficiency compliance check not yet implemented
3. **IS 16046 (Arc Fault Detection)** — not yet implemented
4. **Seismic zone MEP supports** — IS 1893 seismic requirements for MEP supports not calculated

---

## References

- Bureau of Indian Standards: [www.bis.gov.in](https://www.bis.gov.in)
- National Building Code 2016: [SP 7:2016 via BIS](https://www.bis.gov.in)
- CPWD Schedule of Rates: [www.cpwd.gov.in](https://www.cpwd.gov.in)
- ECBC 2017: [www.beeindia.gov.in](https://www.beeindia.gov.in)
- Central Electricity Authority: [www.cea.nic.in](https://www.cea.nic.in)
