"""
OpenMEP API Authentication
===========================
Optional API key authentication via X-API-Key header.

When the API_KEY environment variable is set, every request (except the paths
listed in _EXEMPT_PATHS) must include the header:

    X-API-Key: <your-key>

When API_KEY is not set (the default), authentication is disabled and the API
is accessible without credentials. This is appropriate for:
  - Local development
  - Deployments already protected by a reverse-proxy or VPN
  - Internal company networks

To enable API key auth, add API_KEY=<secret> to your .env file.
See SECURITY.md for the full security model.
"""

import logging
from fastapi import Header, HTTPException, Request
from backend.config import settings

logger = logging.getLogger(__name__)

# Paths that are always accessible regardless of API_KEY setting.
# Health checks and API documentation must never require auth.
_EXEMPT_PATHS = frozenset({
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
})


async def verify_api_key(
    request: Request,
    x_api_key: str | None = Header(default=None),
) -> None:
    """
    FastAPI dependency — validates X-API-Key header when API_KEY env var is set.

    Exempt paths (/, /health, /docs, /redoc, /openapi.json) always pass through
    so health checks and documentation remain accessible without credentials.

    Register as a global dependency in the FastAPI app:
        app = FastAPI(dependencies=[Depends(verify_api_key)])
    """
    if settings.api_key is None:
        # Auth disabled — development / private-network mode
        return

    if request.url.path in _EXEMPT_PATHS:
        return

    if x_api_key is None or x_api_key != settings.api_key:
        logger.warning(
            "Rejected request to %s — invalid or missing API key (remote: %s)",
            request.url.path,
            request.client.host if request.client else "unknown",
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Supply the X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
