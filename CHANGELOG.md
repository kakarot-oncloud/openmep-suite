# Changelog

All notable changes to OpenMEP are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.1] — 2026-04-10

### Fixed

- **README** — platform feature count corrected from 5 to 7; features 6 (Version History) and 7 (Company Branding) added to the Platform Features section; all Node.js API examples corrected to port 8080; Quick Start updated with Node.js service startup.
- **docker-compose.yml** — added `node-api` service (port 8080) for the TypeScript project management layer; Streamlit now depends on `node-api` health; added `projectdata` persistent volume.
- **Dockerfile.node** — new Docker image for the Node.js/Express service; runs as non-root `appuser`; uses tsx for TypeScript execution.
- **src/index.ts** — new Express entry point; mounts `/api/projects` and `/api/submission` routers; exposes `/health` for container health checks.
- **src/package.json** — `tsx` moved to `dependencies` (required at Docker runtime); `zod` bumped to `^3.23.0` (required for `zod/v4` subpath imports in routes).
- **src/lib/*** — added three missing TypeScript modules: `logger.ts`, `project-store.ts`, `calc-engine.ts`; TypeScript tests now pass.
- **.gitignore** — Replit-specific section labels removed; Node.js patterns scoped to root-only with `/` prefix.

---

## [0.2.0] — 2026-04-08

### Added — Platform Features

- **Project Workspace** — single source of truth for every project. Store name, region, floors, space types, and design conditions once; all 26 calculation modules read from the workspace automatically. Includes project CRUD API (`POST/GET/PUT /api/projects`) and Streamlit page.
- **Submission Packager** — one-click ZIP export containing all calculation PDFs, cover letter, cross-module compliance matrix, BOQ summary, and version log. Endpoint: `POST /api/submission/package`.
- **Compliance Guardian** — pre-submission check that validates every module result against regional authority limits and returns structured `PASS / WARN / FAIL` per module with the exact standard clause cited. Covers DEWA §4.3.2, IS 732 §6.4, NFPA 13 §8.6.3, AS/NZS 3500 §3.4, and more. Endpoint: `POST /api/submission/compliance-check`.
- **BIM / IFC & CSV Bridge** — import: parse an IFC file or Revit schedule CSV to auto-populate the Project Workspace; export: download results as CSV or IFC property sets ready to bring back into Revit or ArchiCAD. Endpoints: `POST /api/bim/import`, `GET /api/bim/export/csv`, `GET /api/bim/export/ifc`.
- **Value Engineering & Cost Optimizer** — after every calculation, returns ranked compliant alternatives with estimated cost savings in local currency (AED, INR, GBP, AUD). Rule-based — every suggestion cites the standard clause that makes it valid. Endpoint: `POST /api/optimize/electrical`.
- **Company Branding & Custom Report Templates** — firms can store a logo, stamp image, primary colour, and footer text once per project. All PDF calculation reports auto-inject the branding (letterhead, stamp block, coloured headings, branded footer). Custom report templates allow per-client header/footer overrides. REST endpoints: `POST/GET /api/projects/{id}/branding`, `POST/GET /api/projects/{id}/templates`. Streamlit pages 28 (Branding) and 29 (Report Templates) added.
- **Project Versioning & Version History** — full audit trail of project configuration snapshots with diff viewer. Endpoint: `POST/GET /api/projects/{id}/versions`. Streamlit page 27 (Version History) added.

### Added — Security & Reliability

- **Rate limiting** via `slowapi` — 60 req/min per IP globally; report and package endpoints capped at 10 req/min. Returns HTTP 429 with `Retry-After` header on breach.
- **CORS hardening** — replaced `allow_origins=["*"]` with configurable `ALLOWED_ORIGINS` environment variable (comma-separated). Defaults to `http://localhost:8501` in development. Methods restricted to GET and POST only.

### Added — Developer Experience

- **`requirements-dev.txt`** — separated dev and test dependencies (`pytest`, `pytest-asyncio`, `pytest-cov`, `httpx`, `ruff`) from runtime `requirements.txt`. Production installs no longer pull test tooling.
- **GitHub Actions CI** (`.github/workflows/ci.yml`) — runs on every push and pull request to `main`. Steps: install runtime + dev deps → `ruff check` linting → full `pytest` suite with coverage. Blocks merge on any failure.
- **`.env.example`** — fully documented with inline comments for every environment variable including the new `ALLOWED_ORIGINS`, `POSTGRES_PASSWORD`, and `SECRET_KEY`.

### Changed — Documentation

- **README** — restructured: "Who is this for?" moved to top, real screenshots embedded (2×2 grid), accurate 26-module table with standards per module, Platform Features section with API examples, all-region guide links, Standards Reference link, working release and CI badges, CHANGELOG / CODE_OF_CONDUCT / SECURITY links in footer.
- **CONTRIBUTING.md** — fixed clone URL (was missing username), added `ruff check` step to local dev workflow, updated setup instructions to use `requirements-dev.txt`.

### Fixed

- Clone URL in `CONTRIBUTING.md` was missing the GitHub username.
- `requirements.txt` incorrectly included `pytest` and `pytest-asyncio` as runtime dependencies.

---

## [0.1.0] — 2025-03-30

### Initial Release

#### Added — Backend (FastAPI)
- **Electrical engines**: cable sizing (BS 7671/IEC 60364/IS 3961/AS/NZS 3008), voltage drop, maximum demand, short circuit (IEC 60909), lighting design (CIBSE/SP 32/AS/NZS 1680), power factor correction, generator sizing, panel schedule, UPS sizing
- **HVAC engines**: cooling load (ASHRAE/CIBSE), duct sizing (SMACNA/CIBSE), heating load (EN 12831/CIBSE Guide A), ventilation (ASHRAE 62.1/AS 1668.2)
- **Plumbing engines**: pipe sizing, drainage sizing (BS EN 12056/IS 5329/AS 3500), pump sizing, hot water system (BS 8558/IS 2065), rainwater harvesting (BS 8515/IS 15797/AS 3500), plumbing tank sizing
- **Fire protection engines**: sprinkler design (NFPA 13/BS EN 12845/NBC/AS 2118.1), fire pump sizing (NFPA 20/BS EN 12845), fire tank sizing, standpipe design (NFPA 14/BS 9990)
- **Project tools**: BOQ generator (FIDIC/NRM2/CPWD DSR/AIQS with real FX rates), compliance checker, PDF report generator, submittal tracker
- 35+ FastAPI REST endpoints with full Pydantic v2 validation
- Region-specific standard selection: GCC (6 sub-regions with authority codes), Europe/UK (7 sub-regions), India (9 states), Australia/NZ (9 states/territories)

#### Added — Streamlit UI (26 pages)
- Premium red/black/white theme throughout
- 3-level region selector: Region → Country/State → Utility/Authority
- Functional grouped sidebar navigation with `st.page_link`
- BOQ Excel export with real FX conversion (AED/GBP/INR/AUD) from API
- PDF calculation reports routed to correct endpoint per report type
- Full submittal tracker with add/edit/delete for submittals, RFIs, and equipment

#### Added — Infrastructure
- Docker Compose with `${POSTGRES_PASSWORD}` env-var secrets (no hardcoded credentials)
- `.env.example` credential template
- Google Colab launcher notebook (`colab_launcher.ipynb`)
- `report_generator.py` for PDF output via ReportLab

#### Fixed
- Australia cable/installation method normalisation (AS/NZS 3008 column references)
- Heating-load payload uses flat fields matching `HeatingLoadRequest` schema
- Fire-pump payload uses correct field names (`sprinkler_demand_l_min`, `friction_loss_bar`, etc.)
- BOQ grand totals use `usd_fx_rate` from API, not a regional cost index multiplier
- BOQ column headers dynamically reflect local currency symbol per region

---

## [Unreleased]

### Planned
- React + Vite frontend (replacing Streamlit for production deployments)
- Expo React Native mobile app
- PostgreSQL persistent project storage
- Multi-user authentication (OAuth / LDAP)
- Additional regions: North America (NEC/NFPA 70), Singapore (SS 638), South Africa (SANS 10142)
- Arabic/Hindi UI translation

---

*Made by Luquman A — Copyright © 2025 Luquman A. MIT License.*
