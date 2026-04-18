"""
OpenMEP FastAPI Application
============================
Open-source MEP Engineering Calculation Suite
Supports: GCC, Europe/UK, India, Australia

Run: uvicorn backend.main:app --reload --port 8000
"""

import logging
import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from backend.api.auth import verify_api_key
from backend.api.routes import electrical, mechanical, plumbing, fire, boq, compliance, reports

# ---------------------------------------------------------------------------
# Rate limiter — 60 req/min per IP globally; report endpoints are heavier
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

app = FastAPI(
    title="OpenMEP API",
    description="""
## OpenMEP — Open-Source MEP Engineering Calculation Suite

A comprehensive multi-regional engineering calculation platform supporting:

### Supported Regions
| Region | Standard | Authority |
|--------|----------|-----------|
| **GCC** (UAE/Saudi/Qatar/Kuwait) | BS 7671 / IEC 60364 | DEWA, ADDC, KAHRAMAA, SEC, MEW |
| **Europe / UK** | BS 7671:2018+A2:2022 | DNO / Distribution Networks |
| **India** | IS 732 / IS 3961 / IS 7098 | CEA, MSEDCL, BESCOM, TANGEDCO |
| **Australia** | AS/NZS 3000:2018 / AS/NZS 3008 | Ausgrid, Energex, Western Power |

### Disciplines
- Electrical: Cable sizing, voltage drop, maximum demand, short circuit, lighting
- Mechanical/HVAC: Cooling load, duct sizing, ventilation
- Plumbing: Pipe sizing, drainage, hot water
- Fire Protection: Sprinkler design, fire pump sizing

### Architecture
Built on the **Standards Adapter Pattern** — same calculation logic, swappable regional standards data.

### Authentication
Optional API key authentication via `X-API-Key` header.
Set `API_KEY` in your environment to require authentication on all endpoints.
Health check (`/health`) and documentation (`/docs`, `/redoc`) are always public.

### Rate Limiting
All endpoints: 60 requests/minute per IP.
Report generation endpoints: 10 requests/minute per IP.
Exceeded limits return HTTP 429 with a `Retry-After` header.
Configure allowed origins via the `ALLOWED_ORIGINS` environment variable.
""",
    version="0.2.0",
    contact={
        "name": "OpenMEP Engineering Suite",
        "url": "https://github.com/kakarot-oncloud/openmep",
        "email": "info@openmep.engineering",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    dependencies=[Depends(verify_api_key)],
)

# ---------------------------------------------------------------------------
# Rate limiting middleware
# ---------------------------------------------------------------------------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ---------------------------------------------------------------------------
# CORS — configure via ALLOWED_ORIGINS env var (comma-separated).
# Default: localhost only. In production set ALLOWED_ORIGINS to your domain.
# ---------------------------------------------------------------------------
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501,http://localhost:8000")
allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Accept", "X-API-Key"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(electrical.router, prefix="/api")
app.include_router(mechanical.router, prefix="/api")
app.include_router(plumbing.router, prefix="/api")
app.include_router(fire.router, prefix="/api")
app.include_router(boq.router, prefix="/api")
app.include_router(compliance.router, prefix="/api")
app.include_router(reports.router, prefix="/api")


@app.get("/", tags=["Status"])
async def root():
    """OpenMEP API status — always public, no authentication required."""
    return {
        "name": "OpenMEP API",
        "version": "0.2.0",
        "status": "operational",
        "regions": ["gcc", "europe", "india", "australia"],
        "disciplines": ["electrical", "mechanical", "plumbing", "fire"],
        "docs": "/docs",
        "redoc": "/redoc",
        "message": "Open-Source MEP Engineering Calculation Suite — Multi-Regional Standards",
    }


@app.get("/health", tags=["Status"])
async def health():
    """Health check — always public, no authentication required."""
    return {"status": "healthy", "service": "openmep-api"}


_logger = logging.getLogger(__name__)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    _logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    from backend.config import settings
    if settings.debug:
        content = {"status": "error", "message": str(exc), "type": type(exc).__name__}
    else:
        content = {"status": "error", "message": "An internal error occurred. Please try again."}
    return JSONResponse(status_code=500, content=content)
