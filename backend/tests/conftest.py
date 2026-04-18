"""
Shared pytest fixtures for OpenMEP backend tests.
Uses both sync FastAPI TestClient and async httpx client for testing.
"""
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from backend.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Session-scoped TestClient — single FastAPI app instance for all tests."""
    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture
async def api_client():
    """Async HTTPX client that tests the FastAPI app in-process (no server required)."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client
