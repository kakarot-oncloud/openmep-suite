<div align="center">

```
 ██████╗ ██████╗ ███████╗███╗   ██╗███╗   ███╗███████╗██████╗
██╔═══██╗██╔══██╗██╔════╝████╗  ██║████╗ ████║██╔════╝██╔══██╗
██║   ██║██████╔╝█████╗  ██╔██╗ ██║██╔████╔██║█████╗  ██████╔╝
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║██║╚██╔╝██║██╔══╝  ██╔═══╝
╚██████╔╝██║     ███████╗██║ ╚████║██║ ╚═╝ ██║███████╗██║
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝╚═╝     ╚═╝╚══════╝╚═╝
```

# OpenMEP Suite

**Open-source, standards-cited MEP engineering calculation platform — 4 regions · 26 modules · audit-ready reports**

[![CI](https://github.com/kakarot-oncloud/openmep-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/kakarot-oncloud/openmep-suite/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/kakarot-oncloud/openmep-suite/graph/badge.svg)](https://codecov.io/gh/kakarot-oncloud/openmep-suite)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776ab?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-16a34a)](LICENSE)

[Project Website](https://kakarot-oncloud.github.io/openmep-suite/) ·
[API Docs](docs/API_DOCS.md) ·
[Deployment](docs/DEPLOYMENT.md) ·
[User Guide](docs/USER_GUIDE.md) ·
[Standards Reference](docs/STANDARDS_REFERENCE.md)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Why OpenMEP](#why-openmep)
- [Modules](#modules)
- [Region Support](#region-support)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Usage](#api-usage)
- [Project & Reporting Features](#project--reporting-features)
- [Configuration](#configuration)
- [Security](#security)
- [Testing](#testing)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

OpenMEP is a calculation engine for **Mechanical, Electrical, Plumbing, and Fire-protection**
design, built for consultants, design engineers, contractors, and BIM coordinators working
across **GCC, Europe/UK, India, and Australia/NZ**.

It replaces spreadsheets with a standards-compliant, API-driven engine:

- **Region-aware** — design codes switch automatically (BS 7671 / IEC 60364 for GCC & Europe,
  IS 3961 / IS 732 for India, AS/NZS 3008 / AS/NZS 3000 for Australia).
- **Standard-cited** — every result references the exact clause and table used. Full numerical
  tables (ampacity, correction factors, voltage drop, sprinkler densities…) are embedded in the
  codebase — no external lookups.
- **Audit-ready** — one-click PDF reports with letterhead, step-by-step workings, and an
  engineer sign-off block.

It ships as three cooperating services:

| Service | Tech | Port | Responsibility |
|---------|------|------|----------------|
| **Calculation API** | FastAPI (Python 3.11) | `8000` | All 26 engineering calculations |
| **Web UI** | Streamlit | `8501` | Interactive calculators + report generation |
| **Project API** | Node.js / Express (TypeScript) | `8080` | Project workspaces, versioning, submission packaging, branding |

The Web UI and Project API both call the Calculation API — the Python service is the single
source of truth for engineering results.

---

## Why OpenMEP

Commercial MEP tools cost thousands per seat and lock results in proprietary formats. OpenMEP
is built on three principles:

- **Transparency** — the standards tables live in the repo (`backend/standards_data/` and the
  regional adapters). You can read exactly which value drove every result.
- **Portability** — plain JSON in, plain JSON out. Results export to PDF, Excel, and CSV.
- **Extensibility** — the **Standards Adapter pattern** keeps calculation logic identical across
  regions; adding a country means adding a data adapter, not rewriting engines. See
  [`docs/contributing/ADDING_NEW_REGION.md`](docs/contributing/ADDING_NEW_REGION.md).

---

## Modules

### Electrical (9)

| # | Module | Standards |
|---|--------|-----------|
| 1 | Cable Sizing | BS 7671 / IEC 60364 / IS 3961 / AS/NZS 3008 |
| 2 | Voltage Drop | IEC 60364-5-52 |
| 3 | Maximum Demand | IEE / DEWA / IS 18–1 |
| 4 | Short Circuit | IEC 60909 |
| 5 | Lighting Design | EN 12464-1 / CIBSE / IS 3646 |
| 6 | Power Factor Correction | IEC 60831 / IEEE 1459 |
| 7 | Generator Sizing | ISO 8528 / IEC 60034 |
| 8 | UPS Sizing | IEC 62040 |
| 9 | Panel Schedule | Multi-region |

### Mechanical / HVAC (4)

| # | Module | Standards |
|---|--------|-----------|
| 10 | Cooling Load | ASHRAE / CIBSE Guide A |
| 11 | Duct Sizing (equal friction) | ASHRAE / CIBSE Guide C |
| 12 | Heating Load | EN 12831 / CIBSE Guide A |
| 13 | Ventilation | ASHRAE 62.1 / AS 1668.2 |

### Plumbing (6)

| # | Module | Standards |
|---|--------|-----------|
| 14 | Pipe Sizing | BS EN 806 / IS 1172 |
| 15 | Drainage Sizing | BS EN 12056 |
| 16 | Pump Sizing | Darcy-Weisbach |
| 17 | Hot Water System | BS EN 806-3 |
| 18 | Rainwater Harvesting | BS 8515 / AS 3500 |
| 19 | Tank Sizing | BS EN 806 / IS 1172 |

### Fire Protection (4)

| # | Module | Standards |
|---|--------|-----------|
| 20 | Sprinkler Design | BS EN 12845 / NFPA 13 |
| 21 | Fire Pump Sizing | BS EN 12845 / NFPA 20 |
| 22 | Fire Storage Tank | BS 9251 / NBC 2016 |
| 23 | Standpipe System | NFPA 14 / BS 9990 |

### Reports & Compliance (3)

| # | Module | What it does |
|---|--------|-------------|
| 24 | BOQ Generator | Bill of Quantities in FIDIC / NRM2 / CPWD / AIQS format |
| 25 | Compliance Checker | Validates module results against regional limits, flags the failing clause |
| 26 | PDF Reports + Submittal Tracker | A4 calc sheets with letterhead and sign-off; submittal log |

---

## Region Support

| Region | Coverage | Standards | Design Ambient |
|--------|----------|-----------|----------------|
| [**GCC**](docs/regions/GCC_GUIDE.md) | UAE · KSA · Qatar · Kuwait · Bahrain · Oman | BS 7671, IEC 60364, DEWA / ADDC / SEC / KAHRAMAA, NFPA | 50 °C air |
| [**Europe / UK**](docs/regions/EUROPE_GUIDE.md) | UK · Ireland · Germany · France | BS 7671:2018+A2:2022, IEC 60364, CIBSE, EN 12831 | 30 °C air |
| [**India**](docs/regions/INDIA_GUIDE.md) | 8 utility zones | IS 3961, IS 732, IS 7098, NBC 2016, CPWD | 45 °C air |
| [**Australia / NZ**](docs/regions/AUSTRALIA_GUIDE.md) | All states + New Zealand | AS/NZS 3008, AS/NZS 3000, AS 3500, NCC | 40 °C air |

Nominal LV supply is 400 V / 230 V for GCC, Europe and Australia (IEC 60038 harmonised) and
415 V / 240 V for India. A three-level selector resolves **Region → Country/State → Utility/Authority**.

---

## Architecture

OpenMEP is built on the **Standards Adapter pattern**: calculation engines contain the
region-independent physics, and each regional adapter supplies the standard's numerical tables
and limits.

```
                 ┌──────────────────┐        ┌──────────────────┐
   Streamlit UI  │                  │        │  Node.js Project │
   (port 8501) ──┤  FastAPI engine  │◄───────┤  API (port 8080) │
                 │   (port 8000)    │  HTTP  │  projects/versions│
   curl / SDK ──►│                  │        │  branding/submit  │
                 └────────┬─────────┘        └──────────────────┘
                          │
              ┌───────────┴────────────┐
              │  calculation engines   │   region-independent physics
              └───────────┬────────────┘
                          │  resolves standard tables via
              ┌───────────┴────────────┐
              │  regional adapters      │   gcc · europe · india · australia
              │  + standards_data/*.json│
              └────────────────────────┘
```

Adding a new calculation means adding an engine + a Pydantic model + a route. Adding a new
region means adding an adapter. Neither touches the other. Guides:
[Adding a calculator](docs/contributing/ADDING_NEW_CALCULATOR.md) ·
[Adding a region](docs/contributing/ADDING_NEW_REGION.md).

---

## Quick Start

### Local (Python)

```bash
git clone https://github.com/kakarot-oncloud/openmep-suite.git
cd openmep-suite
pip install -r requirements.txt

# Terminal 1 — Calculation API
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — Web UI
streamlit run streamlit_app/app.py
```

| Service | URL |
|---------|-----|
| Web UI | http://localhost:8501 |
| API (Swagger) | http://localhost:8000/docs |
| API (ReDoc) | http://localhost:8000/redoc |

The optional Project API (workspaces, versioning, submission packaging):

```bash
cd src && npm install && npm run dev   # http://localhost:8080
```

### Docker (all services)

```bash
cp .env.example .env
# review .env, then:
docker-compose up -d
```

| Service | URL | Description |
|---------|-----|-------------|
| Streamlit UI | http://localhost:8501 | Main web interface |
| Calculation API | http://localhost:8000/docs | Engineering engine — Swagger UI |
| Project API | http://localhost:8080 | Project management API |

### Google Colab — zero install

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kakarot-oncloud/openmep-suite/blob/main/colab_launcher.ipynb)

---

## API Usage

All calculation endpoints accept and return JSON. Full reference → [**docs/API_DOCS.md**](docs/API_DOCS.md).
The examples below are validated against the current API schema.

```bash
# Cable sizing — GCC/DEWA, 45 kW, XLPE/Cu, 80 m run
curl -X POST http://localhost:8000/api/electrical/cable-sizing \
  -H "Content-Type: application/json" \
  -d '{"region":"gcc","sub_region":"dewa","load_kw":45,"power_factor":0.85,
       "phases":3,"cable_type":"XLPE_CU","installation_method":"C",
       "cable_length_m":80,"ambient_temp_c":40}'

# Cooling load — 500 m² open-plan office
curl -X POST http://localhost:8000/api/mechanical/cooling-load \
  -H "Content-Type: application/json" \
  -d '{"region":"gcc","zone_name":"Open Plan L5","floor_area_m2":500,
       "glass_area_m2":80,"occupancy":40}'

# Sprinkler design — Ordinary Hazard 1, BS EN 12845
curl -X POST http://localhost:8000/api/fire/sprinkler \
  -H "Content-Type: application/json" \
  -d '{"occupancy_hazard":"OH1","area_protected_m2":600}'

# Maximum demand from a load schedule
curl -X POST http://localhost:8000/api/electrical/maximum-demand \
  -H "Content-Type: application/json" \
  -d '{"region":"gcc","loads":[{"description":"Lighting","quantity":1,
       "unit_kw":10,"power_factor":0.9}]}'

# Water pipe sizing — copper, 120 loading units
curl -X POST http://localhost:8000/api/plumbing/pipe-sizing \
  -H "Content-Type: application/json" \
  -d '{"region":"gcc","flow_units":120,"pipe_material":"copper"}'

# Batch cable schedule — size many circuits against one design basis
curl -X POST http://localhost:8000/api/electrical/cable-schedule \
  -H "Content-Type: application/json" \
  -d '{"design_basis":{"region":"gcc","sub_region":"dewa","ambient_temp_c":45},
       "circuits":[{"circuit_ref":"C1","load_kw":45,"cable_length_m":80},
                   {"circuit_ref":"C2","load_kw":160,"cable_length_m":120}]}'

# Export any table to Excel (returns an .xlsx download)
curl -X POST http://localhost:8000/api/exports/table.xlsx -o schedule.xlsx \
  -H "Content-Type: application/json" \
  -d '{"title":"Cable Schedule","columns":["Ref","Cable"],"rows":[["C1","25 mm²"]]}'

# Persistent project workspace (survives restarts)
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name":"Tower A","design_basis":{"region":"gcc","sub_region":"dewa","ambient_temp_c":45}}'
```

### Persistence, design basis & batch (new in v0.3)

- **Project workspaces** — `POST/GET/PUT/DELETE /api/projects` store a project, its
  **design basis** (region, ambient, PF, defaults), and saved calculation results in SQLite so
  they survive restarts. Save a result with `POST /api/projects/{id}/results`.
- **Batch cable schedule** — `POST /api/electrical/cable-schedule` sizes a whole load schedule
  in one call, each circuit inheriting the design basis unless it overrides a value.
- **CSV / Excel export** — `POST /api/exports/table.{xlsx,csv}` exports any `{columns, rows}`
  table; `POST /api/exports/cable-schedule.xlsx` sizes a batch and returns the spreadsheet.
- In the Web UI these are the **Cable Schedule (Batch)** and **Projects** pages.

**Rate limits:** 60 requests/min per IP on calculation endpoints, 10/min on report generation.
Exceeded limits return HTTP 429 with a `Retry-After` header.

---

## Project & Reporting Features

The Node.js Project API (port 8080) turns individual calculations into a project workflow.
The following are implemented today:

### Project Workspace
Store building data once (region, floors, space types, design conditions); every module reads
from it. `GET/POST /api/projects`, `GET/PUT/DELETE /api/projects/{id}`, `POST /api/projects/{id}/refresh`.

### Version History
Append-only snapshots of each project state with a diff/compare endpoint.
`GET /api/projects/{id}/versions`, `GET /api/projects/{id}/versions/{n}`,
`GET /api/projects/{id}/compare`, `POST /api/projects/{id}/restore/{n}`.

### Company Branding & Report Templates
Per-project logo, stamp, colour and footer, auto-injected into PDF reports; custom templates.
`GET/PUT /api/projects/{id}/branding`, `POST /api/projects/{id}/branding/upload`,
`GET/POST/PUT/DELETE /api/projects/{id}/templates`.

### Compliance Guardian
Checks module results against regional authority limits and returns `PASS` / `WARN` / `FAIL`
per module with the standard clause. `POST /api/submission/compliance-check`.

### Submission Packager
Generates a ready-to-send ZIP (calculation PDFs, compliance matrix, branding) for a project.
`POST /api/submission/package`.

> **Two project stores exist.** The **Calculation API** (port 8000) has a persistent,
> SQLite-backed project store (`/api/projects`, see [above](#persistence-design-basis--batch-new-in-v03))
> — this is the one the Web UI uses. The **Node.js Project API** (port 8080) provides the
> submission/branding/versioning workflow and keeps its data in-memory for evaluation.
> See the [Roadmap](#roadmap) for the planned BIM/IFC bridge and value-engineering optimizer.

---

## Configuration

All settings are environment variables (see [`.env.example`](.env.example) for the full list).

| Variable | Default | Purpose |
|----------|---------|---------|
| `API_KEY` | *(unset)* | If set, requires `X-API-Key` on all calculation endpoints |
| `ALLOWED_ORIGINS` | `http://localhost:8501,http://localhost:8000` | Comma-separated CORS allow-list |
| `API_BASE` | `http://localhost:8000` | Base URL the Streamlit UI calls |
| `DEBUG` | `false` | Verbose error payloads (never enable in production) |
| `OPENMEP_DB_PATH` | `openmep_data.db` | SQLite file for the persistent project store |
| `PORT` | `8080` | Node.js Project API port |

---

## Security

### Optional API-key authentication

Set `API_KEY` to require the `X-API-Key` header on every calculation endpoint. Health checks
(`/health`) and documentation (`/docs`, `/redoc`, `/openapi.json`) remain public.

```bash
# Generate a key and add it to .env
echo "API_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env

# Authenticated request
curl -X POST http://localhost:8000/api/electrical/cable-sizing \
  -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  -d '{"region":"gcc","load_kw":45,"cable_length_m":80}'
```

When `API_KEY` is unset (the default), the API is open — appropriate for local development or
deployments already behind a reverse proxy / VPN.

### Other hardening
- CORS is closed by default to localhost; widen it explicitly with `ALLOWED_ORIGINS`.
- Error responses hide internals unless `DEBUG=true`.
- Docker containers run as a non-root user.

Full disclosure policy → [SECURITY.md](SECURITY.md).

---

## Testing

The backend ships **167 automated tests** (~84 % line coverage), run in CI on every push and PR.

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest                                         # all tests
pytest --cov=backend --cov-report=term-missing # with coverage
ruff check backend/ streamlit_app/             # lint
```

| Test file | Scope |
|-----------|-------|
| `test_cable_sizing.py` | Cable sizing against BS 7671 / IS 3961 / AS/NZS 3008 reference values, all 4 regions |
| `test_electrical_endpoints.py` | Voltage drop, max demand, short circuit, lighting, generator, PF correction, UPS, panel schedule |
| `test_hvac.py` | Cooling load (4 regions), duct sizing, heating, ventilation |
| `test_plumbing.py` | Pipe sizing, drainage, pump, hot water, rainwater, tank |
| `test_fire.py` | Sprinkler design flow, fire pump, fire tank |
| `test_projects.py` | Persistent project store CRUD, saved results, design basis |
| `test_batch_and_exports.py` | Batch cable schedule + CSV/Excel export |

The Node.js Project API has its own Vitest suite (`cd src && npm test`).

---

## Deployment

| Platform | Best For | Effort |
|----------|----------|--------|
| Local | Development, evaluation | Easiest |
| Google Colab | Zero-install, one-off calcs | Easiest |
| Streamlit Cloud | Free hosted UI | Easiest |
| Docker Compose | Teams, self-hosted | Easy |
| Ubuntu VPS + HTTPS | Production | Intermediate |

Full instructions → [**docs/DEPLOYMENT.md**](docs/DEPLOYMENT.md).

---

## Project Structure

```
openmep-suite/
├── backend/                          # FastAPI calculation service
│   ├── main.py                       # App entry — rate limiting, CORS, auth
│   ├── config.py                     # Settings, regional sub-region maps
│   ├── api/routes/                   # REST endpoints (electrical, mechanical, …)
│   ├── engines/                      # Pure-Python calculation engines
│   │   ├── electrical/               # cable_sizing, voltage_drop, short_circuit, …
│   │   ├── mechanical/               # cooling_load, duct_sizing
│   │   ├── plumbing/                 # pipe_sizing
│   │   └── fire/                     # sprinkler_calc
│   ├── adapters/                     # Regional standards adapters (adapter pattern)
│   │   ├── gcc/ · europe/ · india/ · australia/
│   │   └── base_adapter.py           # Abstract interface shared by all regions
│   ├── standards_data/               # Embedded standards tables (JSON)
│   ├── models/                       # Pydantic v2 request/response models
│   └── tests/                        # Pytest suite (149 tests)
├── streamlit_app/                    # Web UI
│   ├── app.py                        # Entry + sidebar navigation
│   ├── utils.py                      # API client, region maps
│   └── pages/                        # Calculator + feature pages
├── src/                              # Node.js/TypeScript Project API
│   ├── index.ts                      # Express app + error middleware
│   ├── routes/                       # /api/projects, /api/submission
│   ├── engines/                      # compliance, PDF, submission packaging
│   └── lib/                          # project/version/branding stores
├── docs/                             # API, deployment, user & standards guides
├── .github/workflows/ci.yml          # CI — ruff + pytest (Python) & vitest (Node)
├── Dockerfile · docker-compose.yml
├── requirements.txt · requirements-dev.txt · pyproject.toml
└── .env.example
```

---

## Roadmap

**Implemented (v0.3)**
- [x] 26 calculation modules across 4 regions
- [x] Optional `X-API-Key` authentication
- [x] **Persistent project workspaces + design basis** (SQLite) with saved results
- [x] **Batch cable-schedule sizing** from a load schedule
- [x] **CSV / Excel export** for schedules and tables
- [x] Version history, branding, submission packaging (Node API)

**Planned (v0.4)**
- [ ] Postgres backend option for multi-instance deployments
- [ ] BIM / IFC & Revit-CSV import/export bridge
- [ ] Value-engineering / cost-optimization suggestions
- [ ] North America — NEC / CEC / ASHRAE 90.1

**Planned (v1.0)**
- [ ] Multi-user team workspaces
- [ ] React/TypeScript production frontend

---

## Contributing

```bash
git clone https://github.com/kakarot-oncloud/openmep-suite.git
cd openmep-suite
git checkout -b feature/my-feature
pip install -r requirements.txt -r requirements-dev.txt

pytest backend/tests/ -v            # all tests must pass
ruff check backend/ streamlit_app/  # lint must pass

git push origin feature/my-feature  # then open a Pull Request
```

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
Report bugs with the [issue template](.github/ISSUE_TEMPLATE/bug_report.md) (include module,
inputs, and expected vs actual). Security issues: see [SECURITY.md](SECURITY.md) — do not open a
public issue.

---

## License

Released under the [MIT License](LICENSE).

<div align="center">
<sub>OpenMEP Suite · built for MEP engineers · standards-cited, open source</sub>
</div>
