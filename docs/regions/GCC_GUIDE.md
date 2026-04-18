# GCC Region Guide

**OpenMEP v0.1.0 | GCC / UAE / Saudi Arabia / Qatar / Kuwait**

---

## Overview

The GCC region covers the six Gulf Cooperation Council states: UAE, Saudi Arabia, Qatar, Kuwait, Bahrain, and Oman. OpenMEP implements the design standards mandated by each country's utility and Authority Having Jurisdiction (AHJ).

---

## Sub-Regions and Authorities

### United Arab Emirates

| Emirate | Authority | Code | Key Standard |
|---------|-----------|------|-------------|
| Dubai | Dubai Electricity & Water Authority | DEWA | DEWA Technical Requirements 2023 |
| Abu Dhabi (city) | Abu Dhabi Distribution Company | ADDC | ADDC Distribution Code |
| Sharjah | Sharjah Electricity & Water Authority | SEWA | SEWA Regulations |
| Northern Emirates | Federal Electricity & Water Authority | FEWA | FEWA Standards |
| Abu Dhabi (free zones) | TRANSCO / ADNOC | — | Abu Dhabi International Building Code |

### Saudi Arabia

| Zone | Authority | Code | Key Standard |
|------|-----------|------|-------------|
| National | Saudi Electricity Company | SEC | Saudi Building Code (SBC) 401 |
| Riyadh | SEC Riyadh | SEC-R | SBC 401 + SEC Distribution Code |

### Qatar

| Utility | Code | Key Standard |
|---------|------|-------------|
| Kahramaa | KAHRAMAA | Qatar General Electricity & Water Corporation Distribution Code |

### Kuwait

| Utility | Code | Key Standard |
|---------|------|-------------|
| MEW | MEW | Ministry of Electricity & Water — Technical Standards |

### Bahrain / Oman

Available as sub-region selections; follow BS 7671 with NFPA fire standards.

---

## Design Standards — Electrical

| Standard | Full Title | Edition | Used For |
|----------|-----------|---------|----------|
| BS 7671 | Requirements for Electrical Installations (IET Wiring Regulations) | 18th Edition, AMD2 | Cable sizing, protection, earthing |
| IEC 60364 | Low-Voltage Electrical Installations | 2015 | Supplementary reference |
| IEC 60909 | Short-Circuit Currents in Three-Phase AC Systems | 2016 | Fault level calculations |
| DEWA TR 2023 | DEWA Technical Requirements for Electrical Installations | 2023 | DEWA-specific requirements |
| SBC 401 | Saudi Building Code — Electrical | 2018 | Saudi-specific requirements |

**Ambient Temperature:** 40°C default (outdoor); 25°C for air-conditioned indoor spaces.

**Cable Types Supported:**
- XLPE/Cu (XLPE-insulated copper conductors) — most common in GCC
- PVC/Cu
- XLPE/Al (aluminium conductors)

**Cable Ratings:** Based on BS 7671 Appendix 4, Tables with 40°C ambient correction applied.

**Voltage Drop Limit:** 4% for power circuits, 3% for lighting (BS 7671 Section 525).

---

## Design Standards — HVAC

| Standard | Full Title | Edition | Used For |
|----------|-----------|---------|----------|
| ASHRAE 90.1 | Energy Standard for Buildings | 2022 | Cooling load calculation method |
| ASHRAE 62.1 | Ventilation for Acceptable Indoor Air Quality | 2022 | Outdoor air quantities |
| ASHRAE 55 | Thermal Environmental Conditions | 2020 | Indoor design conditions |
| SMACNA | HVAC Duct Construction Standards | 2nd Ed | Duct sizing and construction |

**Outdoor Design Conditions (typical GCC):**

| Location | Summer DB (°C) | Summer WB (°C) | Winter DB (°C) |
|----------|---------------|---------------|---------------|
| Dubai | 45 | 30 | 12 |
| Abu Dhabi | 46 | 30 | 11 |
| Riyadh | 46 | 18 | 5 |
| Doha | 45 | 29 | 12 |
| Kuwait City | 47 | 25 | 8 |

---

## Design Standards — Plumbing

| Standard | Full Title | Used For |
|----------|-----------|---------|
| BS EN 806 | Specifications for Installations Inside Buildings Conveying Water | Pipe sizing, storage |
| BS EN 806-3 | Inside Buildings — Pipe Sizing: Simplified Method | Loading unit method |
| BS EN 12056 | Gravity Drainage Systems Inside Buildings | Drainage sizing |
| DEWA Water Regulations | DEWA Technical Requirements — Water | DEWA-specific |

**Water Supply Temperature:** Cold water 30°C (summer), 20°C (winter). Hot water storage 60°C minimum.

---

## Design Standards — Fire Protection

| Standard | Full Title | Edition | Used For |
|----------|-----------|---------|----------|
| NFPA 13 | Standard for the Installation of Sprinkler Systems | 2022 | Sprinkler design |
| NFPA 20 | Standard for the Installation of Stationary Pumps | 2022 | Fire pump sizing |
| NFPA 14 | Standard for the Installation of Standpipe Systems | 2019 | Wet riser / standpipe |
| BS EN 12845 | Fixed Firefighting Systems — Automatic Sprinkler Systems | 2015+A1 | Alternative to NFPA 13 |
| Civil Defence UAE | UAE Fire & Life Safety Code of Practice | 2011 Rev | All fire systems in UAE |
| QCDD | Qatar Civil Defence Department Regulations | 2022 | All fire systems in Qatar |

**Note:** In the UAE, the Civil Defence code is mandatory. NFPA is referenced within it; where conflicts exist, the Civil Defence code takes precedence.

---

## Input Parameters — Region-Specific Defaults

| Parameter | GCC Default | Note |
|-----------|------------|------|
| Supply voltage | 415/240 V, 50 Hz | 3-phase / single-phase |
| Ambient temperature | 40°C | Outdoor; 25°C conditioned |
| Cable type | XLPE/Cu | Preferred for GCC |
| Installation method | C (clipped direct) | Most common exposed installation |
| Earthing system | TN-S | Utility provision |
| Voltage drop limit | 4% (power), 3% (lighting) | BS 7671 Section 525 |

---

## Output Format

### PDF Report Header (GCC)

```
PROJECT: [Name]                   REPORT No: [Ref]
CLIENT:  [Client]                 REVISION:  [Rev]
LOCATION:[City, Country]          DATE:      [Date]
ENGINEER:[Name]                   STANDARD:  BS 7671:2018 AMD2
CHECKED: [Name]                   AUTHORITY: [DEWA/ADDC/SEC/KAHRAMAA]
```

### BOQ Schema

GCC BOQ follows the **FIDIC Conditions of Contract** (Red Book or Yellow Book). OpenMEP generates:
- Item reference in FIDIC format
- Description of works
- Unit, Quantity, Rate (AED), Amount (AED), Amount (USD)
- Subtotals and grand total with civil works, M&E, and contingency

---

## Known Limitations

1. **DEWA Smart Building requirements** (DB/SR/2022) — not yet implemented; only core BS 7671 calculations
2. **Abu Dhabi Estidama Pearl Rating** — not yet a compliance check
3. **Saudi Aramco Engineering Standards (SAES)** — not implemented (industrial/petrochemical)
4. **Bahrain / Oman** — treated as generic GCC; no authority-specific requirements yet

---

## References

- DEWA Technical Requirements: [www.dewa.gov.ae](https://www.dewa.gov.ae)
- IET BS 7671: [www.theiet.org](https://electrical.theiet.org)
- NFPA 13 (2022): [www.nfpa.org](https://www.nfpa.org)
- UAE Civil Defence Code: [www.cdd.gov.ae](https://www.cdd.gov.ae)
- Saudi Building Code SBC 401: [www.sbc.gov.sa](https://www.sbc.gov.sa)
- KAHRAMAA Distribution Code: [www.km.com.qa](https://www.km.com.qa)
