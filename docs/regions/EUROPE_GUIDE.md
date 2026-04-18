# Europe / UK Region Guide

**OpenMEP v0.1.0 | Europe / United Kingdom**

---

## Overview

The Europe/UK region covers the United Kingdom, Ireland, and Western/Northern Europe (Germany, France, Netherlands, Nordic countries). The UK continues to use BS 7671 post-Brexit; Continental Europe follows the harmonised IEC/EN standards.

---

## Sub-Regions and Authorities

| Sub-Region | Authority | Primary Standard |
|-----------|-----------|-----------------|
| UK | Engineering Networks Ltd / DNOs | BS 7671:2018 AMD2 |
| Ireland | ESB Networks | ET 101 (BS 7671 variant) |
| Germany | VDE | DIN VDE 0100 (IEC 60364 implementation) |
| France | EDF / Enedis | NFC 15-100 |
| Netherlands | Stedin / Enexis | NEN 1010 |
| Sweden, Norway, Denmark | Respective national authorities | SS 437, NEK 400 |

---

## Design Standards — Electrical

| Standard | Full Title | Edition | Used For |
|----------|-----------|---------|----------|
| BS 7671 | Requirements for Electrical Installations (IET Wiring Regulations) | 18th Ed, AMD2 (2022) | All UK electrical installations |
| IEC 60364 | Low-Voltage Electrical Installations | 2015–2020 | Continental Europe base standard |
| IEC 60909 | Short-Circuit Currents | 2016 | Fault level calculations |
| CIBSE Guide B | Heating, Ventilating, Air Conditioning and Refrigeration | 2016 | HVAC system design |
| CIBSE LG7 | Lighting for Offices | 2005 | Lighting design |
| BS EN 1838 | Lighting Applications — Emergency Lighting | 2013 | Emergency lighting |

**Ambient Temperature:** 25°C default (indoor conditioned); 20°C for temperate outdoor.

**Cable Ratings:** BS 7671 Appendix 4 Tables at 25°C ambient.

**Voltage Drop Limit:** 4% for power, 3% for lighting (BS 7671:2018 AMD2, Section 525.8.1).

**Earthing Systems:** TN-C-S (PME) most common in UK domestic; TN-S for commercial; IT for hospitals.

---

## Design Standards — HVAC

| Standard | Full Title | Edition | Used For |
|----------|-----------|---------|----------|
| CIBSE Guide A | Environmental Design | 2015 | Cooling/heating load design data |
| CIBSE TM37 | Design for Improved Solar Shading | 2006 | Solar gain, glazing |
| EN 12831 | Heating Systems — Heat Load Calculation | 2017 | Heating load (Continental Europe) |
| BS EN 15251 | Indoor Environmental Input Parameters | 2007 | Thermal comfort criteria |
| ASHRAE 62.1 | Ventilation for Acceptable IAQ | 2022 | Ventilation rates |
| SMACNA | HVAC Duct Construction Standards | 2nd Ed | Duct design |

**UK Outdoor Design Conditions (CIBSE Guide A):**

| City | Summer DB (°C) | Summer WB (°C) | Winter DB (°C) |
|------|---------------|---------------|---------------|
| London | 31.5 | 22 | -4 |
| Manchester | 28 | 20 | -6 |
| Edinburgh | 25 | 18 | -7 |
| Birmingham | 30 | 21 | -5 |

**Germany — DIN 4710 Design Temperatures:**

| City | Summer (°C) | Winter (°C) |
|------|------------|------------|
| Berlin | 32 | -14 |
| Frankfurt | 33 | -12 |
| Munich | 32 | -16 |

---

## Design Standards — Plumbing

| Standard | Full Title | Edition | Used For |
|----------|-----------|---------|----------|
| BS EN 806 | Specifications for Installations Inside Buildings Conveying Water | 2012 | Pipe sizing |
| BS EN 806-3 | Pipe Sizing: Simplified Method | 2006 | Loading unit method |
| BS EN 12056 | Gravity Drainage Systems Inside Buildings | 2000 | Drainage sizing |
| BS 8515 | Rainwater Harvesting Systems | 2009+A1 | Rainwater tank sizing |
| BS 8558 | Guide to the Design, Installation, Testing and Maintenance of Services Supplying Water | 2015 | Hot and cold water |
| BS EN 806-4 | Installation | 2010 | Installation requirements |

**Water Supply Temperature:** Cold 10°C (winter), 20°C (summer). Hot water storage 60°C, distribution 55°C.

**Legionella Control:** BS 8558 requires pasteurisation at 70°C. Storage at 60°C minimum.

---

## Design Standards — Fire Protection

| Standard | Full Title | Edition | Used For |
|----------|-----------|---------|----------|
| BS EN 12845 | Fixed Firefighting Systems — Automatic Sprinkler | 2015+A1 | Sprinkler design |
| BSEN 12845 Table 1 | Hazard Classification | 2015 | LH, OH1/2/3, EH1/2 |
| BS 9990 | Non-automatic Fire-fighting Systems | 2015 | Dry/wet riser, hose reels |
| BS 9251 | Fire Sprinkler Systems for Domestic and Residential | 2021 | Residential sprinklers |
| BS 5588 | Fire Precautions in the Design, Construction and Use of Buildings | — | Fire compartmentation |
| BS 5839 | Fire Detection and Fire Alarm Systems | Part 1, 2017 | Fire alarm |
| Approved Document B | Building Regulations — Fire Safety | 2019 | UK Building Regulations |

**UK Sprinkler Hazard Classification (BS EN 12845):**

| Class | Typical Occupancy |
|-------|------------------|
| Light Hazard (LH) | Hotels, offices, hospitals, schools |
| Ordinary Hazard 1 (OH1) | Car parks, laundries, dairy processing |
| Ordinary Hazard 2 (OH2) | Assembly halls, libraries, cold stores |
| Ordinary Hazard 3 (OH3) | Timber processing, paint spraying |
| Extra High Hazard (EH) | High-piled storage, flammable liquids |

---

## Input Parameters — Region-Specific Defaults

| Parameter | UK Default | Continental EU Default |
|-----------|-----------|----------------------|
| Supply voltage | 415/230 V, 50 Hz | 400/230 V, 50 Hz |
| Ambient temperature | 25°C | 25°C |
| Cable type | XLPE/Cu or PVC/Cu | XLPE/Cu |
| Earthing system | TN-C-S (PME) | TN-C-S |
| Voltage drop limit | 4% power, 3% lighting | 4% (IEC 60364-5-52) |
| Design winter temp | -4°C (London) | -14°C (Berlin) |

---

## Output Format

### PDF Report Header (UK)

```
PROJECT: [Name]                   REPORT No: [Ref]
CLIENT:  [Client]                 REVISION:  [Rev]
LOCATION:[City, UK]               DATE:      [Date]
ENGINEER:[Name, C.Eng MIEt]       STANDARD:  BS 7671:2018 AMD2
CHECKED: [Name]                   AUTHORITY: [DNO Reference]
```

### BOQ Schema

UK/Europe BOQ follows **RICS NRM2** (New Rules of Measurement). OpenMEP generates:
- NRM2 work section reference (e.g., V — Mechanical, cooling and refrigeration plant)
- Description, Unit, Quantity, Rate (£), Amount (£), Amount (USD)
- Summary with preliminaries (12%), design & management (5%), contingency (10%)

---

## Known Limitations

1. **Part P Building Regulations** — domestic compliance checks not yet implemented
2. **RIBA Plan of Works** — integration with stage-gated design submissions not yet available
3. **French NFC 15-100 / German DIN VDE 0100** — calculations use IEC 60364 as the underlying base; country-specific deviations are not yet modelled
4. **Scottish Building Regulations** — treated as England/Wales Approved Document B

---

## References

- IET BS 7671:2018 AMD2: [electrical.theiet.org](https://electrical.theiet.org)
- CIBSE Guides: [www.cibse.org](https://www.cibse.org)
- Building Regulations Approved Document B: [www.gov.uk/government/publications](https://www.gov.uk/government/publications/fire-safety-approved-document-b)
- BS EN 12845: British Standards Online [www.bsigroup.com](https://www.bsigroup.com)
- RICS NRM2: [www.rics.org](https://www.rics.org)
