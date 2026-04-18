# src/ — Project Management API (TypeScript / Express)

This directory is **not** a React frontend. It is a **Node.js / Express** service that provides the project management layer sitting above the Python FastAPI calculation engine.

## What this is

The Python backend (`backend/`) handles pure engineering calculations — cable sizing, cooling loads, fire protection, etc. The `src/` layer handles everything around those calculations:

| Sub-directory | What it does |
|---------------|--------------|
| `engines/` | Business logic: compliance checking, PDF report generation with branding, submission packaging |
| `lib/` | Persistent stores: project metadata, version snapshots, branding configs, report templates |
| `routes/` | Express HTTP handlers: project CRUD, versioning, submission, branding |

## Features provided

- **Project Workspace** — store project metadata (name, region, floors, design conditions) once; all 26 calculation modules read from it
- **Version History** — every project snapshot is stored with a semantic version number and a BOQ delta comparison (cost change between versions in AED, INR, GBP, AUD)
- **Submission Packager** — one-click ZIP export with all calculation PDFs, compliance matrix, BOQ summary, and version log
- **Company Branding** — store logo, stamp, primary colour, and footer text per project; all PDF reports auto-inject branding
- **Report Templates** — per-client header/footer overrides for custom-branded deliverables

## Running locally

```bash
# From inside the src/ directory
npm install        # install Node.js dependencies (Node.js 20+ required)
npm run dev        # start the Express server (default port 8080)
```

## Testing

```bash
# From inside the src/ directory
npm install
npm test           # run all vitest tests

# Or to watch for changes during development:
npm run test:watch
```

## Directory structure

```
src/
├── engines/
│   ├── compliance-guardian.ts   # PASS/WARN/FAIL checker against regional limits
│   ├── pdf-generator.ts         # PDF generation with branding injection
│   └── submission-service.ts    # ZIP packager — assembles all deliverables
├── lib/
│   ├── branding-store.ts        # BrandingConfig + ReportTemplate CRUD
│   ├── calc-engine.ts           # Engineering parameter derivation
│   ├── logger.ts                # Minimal structured logger
│   ├── project-store.ts         # Project metadata persistence + version hooks
│   ├── version-store.ts         # Project version snapshots + BOQ delta comparison
│   └── __tests__/               # Vitest test suite
└── routes/
    ├── projects.ts              # /api/projects — CRUD + branding + templates
    └── submission.ts            # /api/submission — package + compliance-check
```

## Relationship to the Python backend

The Express API (`src/`) and the FastAPI engine (`backend/`) are separate services:

```
Browser / Streamlit UI
        │
        ├── GET/POST /api/electrical/...   → FastAPI (Python) on port 8000
        ├── GET/POST /api/mechanical/...   → FastAPI (Python) on port 8000
        │
        └── GET/POST /api/projects/...     → Express (TypeScript) on port 8080
            GET/POST /api/submission/...   → Express (TypeScript) on port 8080
```

See `docker-compose.yml` for the full service topology.

## Why TypeScript?

The project management layer involves file I/O (ZIP assembly, PDF injection), JSON state, and streaming downloads — workloads where Node.js streams are a natural fit. The calculation engines remain in Python where the scientific libraries (NumPy, etc.) live.
