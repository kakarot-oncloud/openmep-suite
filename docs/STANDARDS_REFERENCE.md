# OpenMEP Standards Reference

**Version 0.1.0 | Comprehensive table of all standards used in OpenMEP calculations**

---

## How to Read This Document

Each row identifies:
- **Standard number** — the formal designation
- **Full title** — official title of the document
- **Edition / Year** — edition currently implemented in OpenMEP
- **Region(s)** — which OpenMEP regions reference this standard
- **Used for** — which calculation module(s) use it and how

---

## Electrical Standards

| Standard | Full Title | Edition | Region(s) | Used For |
|----------|-----------|---------|-----------|---------|
| BS 7671 | Requirements for Electrical Installations (IET Wiring Regulations) | 18th Edition AMD2, 2022 | GCC, Europe/UK | Cable sizing (current carrying capacity tables), voltage drop limits, earthing systems, protective device coordination |
| IEC 60364-5-52 | Low-Voltage Electrical Installations — Selection and Erection of Electrical Equipment | 2009 | GCC, Europe | Cable installation methods, grouping factors, ambient temperature correction |
| IEC 60909-0 | Short-Circuit Currents in Three-Phase AC Systems — Calculation | 2016 | All regions | Symmetrical fault current calculation, peak current, minimum fault current |
| IS 3961 | Recommended Current Ratings for Cables | Part 1 (2011), Part 2 | India | Cable current carrying capacity (PVC, XLPE; Cu, Al); ambient temperature derating at 35/40/45/50°C |
| IS 732 | Code of Practice for Electrical Wiring Installations | 2019 | India | Voltage drop limits (5%); wiring methods |
| IS 3043 | Code of Practice for Earthing | 1987 (R2021) | India | Earthing systems (TT, TN); earth electrode sizing |
| AS/NZS 3008.1.1 | Electrical Installations — Selection of Cables — Cables for Alternating Voltages up to and Including 0.6/1 kV | 2017 | Australia | Cable current carrying capacity — installation method columns; AS/NZS cable type identifiers (X90, V75) |
| AS/NZS 3000 | Wiring Rules | 2018 Amdt 1 | Australia | Voltage drop limits (5% total); earthing (MEN); wiring installation methods |
| AS/NZS 5000.1 | Electric Cables — Polymeric Insulated | 2019 | Australia | Cable type designations (X-90 XLPE/Cu, V-75 PVC/Cu, etc.) |
| DEWA TR 2023 | Dubai Electricity & Water Authority Technical Requirements for Electrical Installations | 2023 | GCC → UAE → DEWA | DEWA-specific conductor sizing requirements, service connection |
| SBC 401 | Saudi Building Code — Electrical | 2018 | GCC → KSA → SEC | Saudi-specific requirements, earthing |
| CEA Regulations 2010 | Central Electricity Authority (Measures Relating to Safety and Electric Supply) Regulations | 2010 | India | Statutory compliance framework for LV/HV installations |
| CIBSE LG7 | Lighting for Offices | 2005 | Europe/UK | Target illuminance levels, UGR limits |
| IS 3646 | Code of Practice for Interior Illumination | 1992 | India | Target illuminance levels per room type |
| AS/NZS 1680 | Interior and Workplace Lighting | 2006 | Australia | Target illuminance levels and quality criteria |
| BS EN 1838 | Lighting Applications — Emergency Lighting | 2013 | GCC, Europe/UK | Minimum 1 lux on escape route; 0.5 lux in open area |
| IS 1648 | Code of Practice for Fire Safety of Buildings (Electrical Installations) | 1997 | India | Emergency lighting requirements |
| BS EN ISO 8528 | Reciprocating Internal Combustion Engine Driven Alternating Current Generating Sets | 2016 | All regions | Generator sizing, classification (Prime/Standby/Continuous) |
| IEC 60831-1 | Shunt Power Capacitors of the Self-Healing Type | 2014 | All regions | Capacitor bank specification, derating |

---

## HVAC / Mechanical Standards

| Standard | Full Title | Edition | Region(s) | Used For |
|----------|-----------|---------|-----------|---------|
| ASHRAE 90.1 | Energy Standard for Buildings Except Low-Rise Residential Buildings | 2022 | GCC, Australia | Cooling load calculation (CLTD/CLF method); envelope U-value requirements |
| ASHRAE 62.1 | Ventilation and Acceptable Indoor Air Quality in Commercial Buildings | 2022 | All regions | Outdoor air per person and per unit floor area; occupancy categories |
| ASHRAE 55 | Thermal Environmental Conditions for Human Occupancy | 2020 | All regions | Indoor design temperature/humidity criteria |
| CIBSE Guide A | Environmental Design | 2015 | Europe/UK, GCC | Outdoor design conditions (UK climate); heating and cooling load methods |
| CIBSE TM37 | Design for Improved Solar Shading | 2006 | Europe/UK | Solar gain factors, glazing shading coefficient |
| EN 12831 | Heating Systems in Buildings — Method for Calculation of the Design Heat Load | 2017 | Europe | Transmission heat loss; ventilation heat loss; degree days |
| BS EN 15251 | Indoor Environmental Input Parameters for Design and Assessment of Energy Performance of Buildings | 2007 | Europe/UK | Thermal comfort categories I, II, III |
| IS 8695 | Code of Practice for Conservation of Energy in Air-Conditioning Systems | 1978 (R2018) | India | Cooling load method; shading factors for Indian climate |
| ECBC 2017 | Energy Conservation Building Code | 2017 | India | Building envelope, HVAC system, lighting energy performance |
| AS 1668.1 | The Use of Ventilation and Air Conditioning in Buildings — Fire and Smoke Control | 2015 | Australia | Fire/smoke mode operation of HVAC |
| AS 1668.2 | The Use of Ventilation and Airconditioning in Buildings — Mechanical Ventilation in Buildings | 2012 | Australia | Outdoor air rates by occupancy type |
| SMACNA HVAC Duct Construction | HVAC Duct Construction Standards, Metal and Flexible | 2nd Edition 1995 | All regions | Equal-friction duct sizing; velocity limits per duct class; duct construction |
| NBC 2016 Part 8 Sec 3 | National Building Code of India 2016 — Part 8: Building Services, Section 3 (Air Conditioning, Heating & Mechanical Ventilation) | 2016 | India | HVAC design framework |

---

## Plumbing Standards

| Standard | Full Title | Edition | Region(s) | Used For |
|----------|-----------|---------|-----------|---------|
| BS EN 806 | Specifications for Installations Inside Buildings Conveying Water for Human Consumption | 2012 | GCC, Europe/UK | General plumbing system design |
| BS EN 806-3 | Inside Buildings Conveying Water — Pipe Sizing: Simplified Method | 2006 | GCC, Europe/UK | Loading unit method for cold and hot water pipe sizing |
| BS EN 12056 | Gravity Drainage Systems Inside Buildings | Parts 1–5, 2000 | GCC, Europe/UK | Discharge unit method for drainage sizing; stack and branch sizing |
| BS 8515 | Rainwater Harvesting Systems — Code of Practice | 2009+A1:2013 | Europe/UK | Rainfall data; yield-demand algorithm; tank sizing |
| BS 8558 | Guide to the Design, Installation, Testing and Maintenance of Services Supplying Water | 2015 | Europe/UK | Hot and cold water system design |
| IS 1172 | Code of Basic Requirements for Water Supply, Drainage and Sanitation | 1983 (R2019) | India | Per capita daily demand (litres/person/day) by building type |
| IS 5329 | Code of Practice for Sanitary Pipework above Ground for Buildings | 2005 | India | Drainage unit method; stack sizing |
| IS 2065 | Code of Practice for Water Supply in Buildings | 1983 | India | Hot water demand; cold water storage |
| AS 3500.1 | Plumbing and Drainage — Water Services | 2021 | Australia | Cold and hot water pipe sizing; pressure/flow |
| AS 3500.2 | Plumbing and Drainage — Sanitary Plumbing and Drainage | 2021 | Australia | Drainage unit method; stack sizing |
| AS 3500.4 | Plumbing and Drainage — Heated Water Services | 2018 | Australia | Hot water temperature; legionella; storage sizing |
| AS 3500.1 Appendix D | Rainwater Harvesting | 2021 | Australia | Tank sizing; overflow; water quality |
| NCC Volume 1 B6 | National Construction Code — Plumbing Requirements | 2022 | Australia | Compliance framework |

---

## Fire Protection Standards

| Standard | Full Title | Edition | Region(s) | Used For |
|----------|-----------|---------|-----------|---------|
| NFPA 13 | Standard for the Installation of Sprinkler Systems | 2022 | GCC, Australia, India | Sprinkler system design; hazard classification (LH/OH/EH); hydraulic calculation method; density/area method |
| NFPA 14 | Standard for the Installation of Standpipe and Hose Systems | 2019 | GCC | Standpipe class (I/II/III); flow requirements; riser sizing |
| NFPA 20 | Standard for the Installation of Stationary Pumps for Fire Protection | 2022 | GCC, Australia | Fire pump duty point; jockey pump; pressure relief; testing |
| NFPA 22 | Standard for Water Tanks for Private Fire Protection | 2018 | GCC | Fire storage tank sizing; gravity versus pressurised tanks |
| BS EN 12845 | Fixed Firefighting Systems — Automatic Sprinkler Systems — Design, Installation and Maintenance | 2015+A1:2019 | GCC, Europe/UK, India | Sprinkler system design; hazard classification (LH, OH1/2/3, EH); remote area sizing |
| BS 9990 | Code of Practice for Non-automatic Fire-fighting Systems in Buildings | 2015 | Europe/UK | Wet and dry riser; hose reels; fire hydrants |
| BS 9251 | Fire Sprinkler Systems for Domestic and Residential Occupancies — Code of Practice | 2021 | Europe/UK | Residential sprinkler coverage; flow rates |
| Civil Defence UAE Code | UAE Fire & Life Safety Code of Practice | 2011 Rev | GCC → UAE | Overarching UAE fire code; sprinkler, detection, egress |
| QCDD Regulations | Qatar Civil Defence Department Fire Protection Regulations | 2022 | GCC → Qatar | Overarching Qatar fire code |
| NBC 2016 Part 4 | National Building Code of India — Part 4: Fire and Life Safety | 2016 | India | Overall fire framework; occupancy hazard classification |
| IS 15105 | Design and Installation of Fixed Automatic Sprinkler Fire Extinguishing Systems | 2002 | India | Sprinkler design for India |
| IS 3844 | Code of Practice for Installation and Maintenance of Internal Hydrant System | 1989 (R2021) | India | Internal hydrant and hose reel |
| AS 2118.1 | Automatic Fire Sprinkler Systems — General Systems | 2017 | Australia | Sprinkler system design; hazard classification; hydraulic calculation |
| AS 2941 | Fixed Fire Protection Installations — Pumpsets | 2013 | Australia | Fire pump duty; electric and diesel; testing |
| AS 2419.1 | Fire Hydrant Installations — Systems Design, Installation and Commissioning | 2021 | Australia | Hydrant system design; flow and pressure |
| Approved Document B | Building Regulations — Fire Safety (England and Wales) | 2019 | Europe → UK | Fire compartmentation; means of escape |

---

## Structural / Loading Standards (Referenced)

| Standard | Full Title | Edition | Region(s) | Used For |
|----------|-----------|---------|-----------|---------|
| AS 1170.1 | Structural Design Actions — Permanent, Imposed and Other Actions | 2002 | Australia | Referenced for equipment and plant loading |
| IS 875 | Code of Practice for Design Loads (Other than Earthquake) | 2015 | India | Referenced for MEP equipment loading on structures |

---

## Regional Cost / Measurement Standards

| Standard | Full Title | Edition | Region(s) | Used For |
|----------|-----------|---------|-----------|---------|
| FIDIC Red Book | Conditions of Contract for Construction | 2017 | GCC | BOQ measurement rules; bill format |
| RICS NRM2 | New Rules of Measurement — Detailed Measurement for Building Works | 2nd Ed, 2012 | Europe/UK | BOQ work section breakdown; preamble |
| CPWD DSR | Central Public Works Department Schedule of Rates | Annual | India | Item rates for electrical, HVAC, plumbing, fire work |
| AIQS Cost Management Manual | Australian Institute of Quantity Surveyors Cost Management Manual | 2021 | Australia | BOQ format; trade package breakdown |

---

## Standard Availability Note

The following standards are referenced in design but not yet implemented as calculation engines in OpenMEP v0.1.0:

- BS EN 62305 (Lightning Protection) — planned v0.2.0
- IEC 62271 (High Voltage Switchgear) — planned v0.3.0
- NFPA 72 (Fire Alarm) — planned v0.2.0
- AS/NZS 3014 (Swimming Pools) — planned v0.3.0
- NEC (NFPA 70, North America) — planned v0.2.0 with North America region

---

*Standard editions and references were verified as of March 2024. Always confirm you are working with the latest published edition of any standard before using for a real project.*
