"""
Tests for the persistent project workspace (SQLite-backed) and design basis.

Each test runs against a temporary database file via the ``temp_db`` fixture,
which points ``OPENMEP_DB_PATH`` at a fresh file so nothing touches the real store.
"""

import os

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture()
def client(tmp_path):
    os.environ["OPENMEP_DB_PATH"] = str(tmp_path / "test_projects.db")
    with TestClient(app) as c:
        yield c
    os.environ.pop("OPENMEP_DB_PATH", None)


def _create(client, name="Tower A"):
    return client.post("/api/projects", json={
        "name": name,
        "client": "ACME",
        "location": "Dubai",
        "project_number": "P-001",
        "design_basis": {"region": "gcc", "sub_region": "dewa", "ambient_temp_c": 45, "power_factor": 0.9},
    })


class TestProjectCrud:
    def test_create_and_get(self, client):
        r = _create(client)
        assert r.status_code == 201
        proj = r.json()
        assert proj["id"].startswith("proj_")
        assert proj["design_basis"]["ambient_temp_c"] == 45
        assert proj["result_count"] == 0

        got = client.get(f"/api/projects/{proj['id']}")
        assert got.status_code == 200
        assert got.json()["name"] == "Tower A"

    def test_list(self, client):
        _create(client, "A")
        _create(client, "B")
        r = client.get("/api/projects")
        assert r.status_code == 200
        assert r.json()["count"] == 2

    def test_update(self, client):
        pid = _create(client).json()["id"]
        r = client.put(f"/api/projects/{pid}", json={"name": "Renamed", "design_basis": {"region": "india", "power_factor": 0.85}})
        assert r.status_code == 200
        body = r.json()
        assert body["name"] == "Renamed"
        assert body["design_basis"]["region"] == "india"

    def test_delete(self, client):
        pid = _create(client).json()["id"]
        assert client.delete(f"/api/projects/{pid}").status_code == 200
        assert client.get(f"/api/projects/{pid}").status_code == 404

    def test_get_missing_returns_404(self, client):
        assert client.get("/api/projects/proj_does_not_exist").status_code == 404

    def test_persistence_survives_new_client(self, client, tmp_path):
        """A project written by one client is readable by a fresh app instance
        pointed at the same database file — i.e. it is truly persisted."""
        pid = _create(client, "Persisted").json()["id"]
        # New TestClient, same OPENMEP_DB_PATH (set by the fixture)
        with TestClient(app) as c2:
            assert c2.get(f"/api/projects/{pid}").json()["name"] == "Persisted"


class TestSavedResults:
    def test_save_and_list_results(self, client):
        pid = _create(client).json()["id"]
        r = client.post(f"/api/projects/{pid}/results", json={
            "module": "cable_sizing",
            "title": "MDB-DB1 feeder",
            "compliant": True,
            "payload": {"selected_size_mm2": 25, "voltage_drop_pct": 3.1},
        })
        assert r.status_code == 201
        assert r.json()["payload"]["selected_size_mm2"] == 25

        listed = client.get(f"/api/projects/{pid}/results")
        assert listed.status_code == 200
        assert listed.json()["count"] == 1

        # result_count reflected on the project
        assert client.get(f"/api/projects/{pid}").json()["result_count"] == 1

    def test_save_result_to_missing_project_404(self, client):
        r = client.post("/api/projects/proj_missing/results", json={"module": "x", "payload": {}})
        assert r.status_code == 404

    def test_deleting_project_removes_results(self, client):
        pid = _create(client).json()["id"]
        client.post(f"/api/projects/{pid}/results", json={"module": "x", "payload": {}})
        client.delete(f"/api/projects/{pid}")
        assert client.get(f"/api/projects/{pid}/results").status_code == 404
