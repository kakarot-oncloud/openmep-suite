# Australia Region Guide

**OpenMEP v0.1.0 | Australia / New Zealand**

---

## Overview

Australia uses a national standards framework published by Standards Australia (SA) and the Australian Building Codes Board (ABCB). The National Construction Code (NCC), also known as the Building Code of Australia (BCA) for Class 2–9 buildings, is the overarching regulatory instrument. New Zealand is covered by the NZ Building Code (NZBC) and SNZ standards.

---

## Sub-Regions and Authorities

### Australian States and Territories

| State/Territory | Distribution Network Service Provider(s) | Region Code |
|----------------|------------------------------------------|-------------|
| New South Wales | Ausgrid, Endeavour Energy, Essential Energy | au_nsw |
| Victoria | AusNet Services, CitiPower, Powercor, United Energy | au_vic |
| Queensland | Energex (SEQ), Ergon Energy (regional) | au_qld |
| South Australia | SA Power Networks | au_sa |
| Western Australia | Western Power, Horizon Power | au_wa |
| Tasmania | TasNetworks | au_tas |
| ACT | ActewAGL | au_act |
| Northern Territory | Jacana Energy | au_nt |

### New Zealand

| Authority | Region Code |
|-----------|-------------|
| Vector (Auckland), Powerco, Wellington Electricity | nz |

---

## Design Standards — Electrical

| Standard | Full Title | Edition | Used For |
|----------|-----------|---------|----------|
| AS/NZS 3008.1.1 | Electrical Installations — Selection of Cables | 2017 | Cable sizing — LV |
| AS/NZS 3000 | Wiring Rules | 2018 Amdt 1 | Installation requirements |
| AS/NZS 3008.1.2 | Selection of Cables — NZ | 2017 | Cable sizing — NZ |
| AS 2067 | Substations and High-Voltage Installations | 2016 | HV systems |
| AS 61000.3.2 | Electromagnetic Compatibility — Harmonic Currents | 2014 | Harmonic limits |
| AS/NZS 3017 | Electrical Installations — Verification | 2022 | Testing and commissioning |
| NCC Volume 1 | National Construction Code | 2022 | Building compliance |

**Ambient Temperature:** 25°C (AS/NZS 3008.1.1 Table 1 basis). Correction factors provided for 35°C, 40°C, and 45°C for hot climates (northern QLD, NT, WA).

**AS/NZS 3008 Installation Method Mapping:**

OpenMEP maps universal installation methods to AS/NZS 3008 Table column references:

| Generic Method | AS/NZS 3008 Column | Description |
|---------------|-------------------|-------------|
| A1, A2 | col_6 | Enclosed in conduit in thermally insulating wall |
| B1, B2 | col_6 | Enclosed in conduit on wall |
| C | col_22 | Clipped direct to surface |
| D1 | col_13 | Single cable in ducts in concrete |
| D2 | col_9 | Multi-core cable directly buried |
| E | col_23 | Free air — single cable |
| F | col_24 | Free air — trefoil |

**Cable Type Mapping (AS/NZS 5000.1):**

| Generic Type | AS/NZS 3008 Type | Description |
|-------------|-----------------|-------------|
| XLPE_CU | X90_CU | X-90 XLPE-insulated, copper conductors |
| PVC_CU | V75_CU | V-75 PVC-insulated, copper conductors |
| XLPE_AL | X90_AL | X-90 XLPE-insulated, aluminium conductors |

**Voltage:** 415/230 V, 50 Hz (LV); 11 kV, 22 kV, 33 kV (MV).

**Voltage Drop Limit:** 5% total (AS/NZS 3000 Clause 3.6.2); recommended 2.5% for feeders and 2.5% for final subcircuits.

**Earthing:** MEN (Multiple Earthed Neutral) system — AS/NZS 3000.

---

## Design Standards — HVAC

| Standard | Full Title | Edition | Used For |
|----------|-----------|---------|----------|
| AS 1170.1 | Structural Design Actions — Permanent, Imposed & Other | 2002 | Design actions |
| AS 1668.1 | The Use of Ventilation and Air Conditioning in Buildings — Fire | 2015 | Fire mode ventilation |
| AS 1668.2 | The Use of Ventilation and Airconditioning — Ventilation | 2012 | Ventilation rates |
| ASHRAE 90.1 | Energy Standard for Buildings | 2022 | Cooling/energy |
| ASHRAE 62.1 | Ventilation for Acceptable IAQ | 2022 | Outdoor air requirements |
| AIRAH DA09 | Psychrometrics | 2009 | Design conditions |
| NCC Vol 1 J | Energy Efficiency — Commercial | 2022 | Mandatory energy efficiency |

**Australia Outdoor Design Conditions (AIRAH):**

| City | Summer DB (°C) | Summer WB (°C) | Winter DB (°C) |
|------|---------------|---------------|---------------|
| Sydney | 35 | 24 | 4 |
| Melbourne | 38 | 26 | 2 |
| Brisbane | 37 | 25 | 5 |
| Perth | 40 | 25 | 5 |
| Adelaide | 40 | 25 | 3 |
| Darwin | 35 | 28 | 24 |
| Hobart | 28 | 20 | 0 |

---

## Design Standards — Plumbing

| Standard | Full Title | Edition | Used For |
|----------|-----------|---------|----------|
| AS 3500.1 | Plumbing and Drainage — Water Services | 2021 | Cold and hot water |
| AS 3500.2 | Plumbing and Drainage — Sanitary Plumbing | 2021 | Drainage |
| AS 3500.3 | Plumbing and Drainage — Stormwater Drainage | 2018 | Stormwater |
| AS 3500.4 | Plumbing and Drainage — Heated Water Services | 2018 | Hot water systems |
| AS 3500.1 App D | Rainwater Harvesting | 2021 | Tank sizing |
| NCC Vol 1 B6 | Plumbing Requirements | 2022 | Compliance framework |

**Per Capita Water Demand (AS 3500.1):**

| Building Type | L/person/day |
|--------------|-------------|
| Residential (metered) | 155 |
| Office | 50 |
| School | 30 |
| Hotel (per bed) | 220 |
| Hospital (per bed) | 400 |

---

## Design Standards — Fire Protection

| Standard | Full Title | Edition | Used For |
|----------|-----------|---------|----------|
| AS 2118.1 | Automatic Fire Sprinkler Systems — General | 2017 | Sprinkler design |
| AS 2118.4 | Automatic Fire Sprinkler Systems — Residential | 2012 | Residential sprinklers |
| AS 2941 | Fixed Fire Protection Installations — Pumpsets | 2013 | Fire pump sizing |
| AS 1851 | Maintenance of Fire Protection Systems | 2012 | Maintenance testing |
| AS 2419.1 | Fire Hydrant Installations — Systems Design | 2021 | Hydrant system |
| AS 1670.1 | Fire Detection, Warning, Control — Systems Design | 2018 | Fire detection |
| NCC Volume 1 Spec C2.3 | Sprinkler systems | 2022 | Mandatory sprinkler provisions |

**Australia Sprinkler Hazard Classification (AS 2118.1):**

| Class | Occupancy |
|-------|----------|
| Light Hazard | Offices, hotels, schools, churches |
| Ordinary Hazard 1 | Car parks, laundries, processing |
| Ordinary Hazard 2 | Libraries, showrooms, light manufacturing |
| Extra High Hazard | High-piled warehouses, paint spray |

---

## Input Parameters — Region-Specific Defaults

| Parameter | Australia Default | Note |
|-----------|-----------------|------|
| Supply voltage | 415/230 V, 50 Hz | |
| Ambient temperature | 25°C (AS/NZS 3008) | Increase for tropical zones |
| Cable type | X90_CU (XLPE/Cu) | AS/NZS 5000.1 |
| Earthing | MEN (AS/NZS 3000) | Multiple Earthed Neutral |
| Voltage drop | 5% total (AS/NZS 3000) | Feeder 2.5% + final 2.5% |
| Installation method | col_22 (clipped direct) | AS/NZS 3008 default |

---

## Output Format

### PDF Report Header (Australia)

```
PROJECT: [Name]                   REPORT No: [Ref]
CLIENT:  [Client]                 REVISION:  [Rev]
LOCATION:[City, State]            DATE:      [Date]
ENGINEER:[Name, CPEng]            STANDARD:  AS/NZS 3008:2017 / AS 3500:2021
CHECKED: [Name]                   AUTHORITY: [DNSP Reference]
```

### BOQ Schema

Australia BOQ follows **AIQS Cost Management Manual** (Australian Institute of Quantity Surveyors). OpenMEP generates:
- AIQS work section reference
- Description of works
- Unit, Quantity, Rate (AUD), Amount (AUD), Amount (USD)
- Preamble: "Rates inclusive of GST. Measured in accordance with AIQS Cost Management Manual."

---

## Known Limitations

1. **State-specific DNSP requirements** — Ausgrid, Powercor, etc. each publish Service & Installation Rules (SIR); these detailed requirements are not yet modelled
2. **NCC J-Section energy modelling** — full NCC Volume 1 Section J energy compliance calculations not yet implemented
3. **NZ-specific SNZ standards** — AS/NZS standards used; NZ-only deviations not modelled
4. **AS 4777 Grid Connection of Energy Systems via Inverters** — solar/battery inverter calculations not yet implemented

---

## References

- Standards Australia: [www.standards.org.au](https://www.standards.org.au)
- National Construction Code: [www.ncc.abcb.gov.au](https://www.ncc.abcb.gov.au)
- AIQS: [www.aiqs.com.au](https://www.aiqs.com.au)
- AIRAH: [www.airah.org.au](https://www.airah.org.au)
- AS/NZS 3000:2018 Wiring Rules: [Standards Australia](https://www.standards.org.au)
