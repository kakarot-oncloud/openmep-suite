"""
Lightweight SQLite persistence for OpenMEP project workspaces.

Uses the Python standard-library ``sqlite3`` module only — no ORM, no extra
dependency. Projects and their saved calculation results survive process
restarts. The database file location is resolved at call time from the
``OPENMEP_DB_PATH`` environment variable (default: ``openmep_data.db`` next to
the repository root), which lets tests point at a temporary file.

Concurrency: a fresh connection is opened per operation with WAL journalling,
which is safe for the low write volume of a calculation tool served by
Uvicorn workers.
"""

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_DEFAULT_DB = Path(__file__).resolve().parent.parent / "openmep_data.db"


def _db_path() -> str:
    return os.environ.get("OPENMEP_DB_PATH", str(_DEFAULT_DB))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create tables if they do not exist. Safe to call repeatedly."""
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id             TEXT PRIMARY KEY,
                name           TEXT NOT NULL,
                client         TEXT NOT NULL DEFAULT '',
                location       TEXT NOT NULL DEFAULT '',
                project_number TEXT NOT NULL DEFAULT '',
                design_basis   TEXT NOT NULL DEFAULT '{}',
                created_at     TEXT NOT NULL,
                updated_at     TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS saved_results (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                module     TEXT NOT NULL,
                title      TEXT NOT NULL DEFAULT '',
                compliant  INTEGER NOT NULL DEFAULT 1,
                payload    TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_results_project
                ON saved_results(project_id);
            """
        )


# ── Project CRUD ──────────────────────────────────────────────────────────────

def _project_row_to_dict(row: sqlite3.Row, result_count: int = 0) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "client": row["client"],
        "location": row["location"],
        "project_number": row["project_number"],
        "design_basis": json.loads(row["design_basis"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "result_count": result_count,
    }


def create_project(name: str, client: str, location: str, project_number: str, design_basis: dict) -> dict:
    pid = f"proj_{uuid.uuid4().hex[:12]}"
    now = _now()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO projects (id, name, client, location, project_number, design_basis, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (pid, name, client, location, project_number, json.dumps(design_basis), now, now),
        )
    return get_project(pid)  # type: ignore[return-value]


def list_projects() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM projects ORDER BY updated_at DESC").fetchall()
        counts = dict(
            conn.execute("SELECT project_id, COUNT(*) FROM saved_results GROUP BY project_id").fetchall()
        )
    return [_project_row_to_dict(r, counts.get(r["id"], 0)) for r in rows]


def get_project(project_id: str) -> Optional[dict]:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if row is None:
            return None
        count = conn.execute(
            "SELECT COUNT(*) FROM saved_results WHERE project_id = ?", (project_id,)
        ).fetchone()[0]
    return _project_row_to_dict(row, count)


def update_project(project_id: str, fields: dict) -> Optional[dict]:
    """Update only the provided (non-None) columns. ``fields`` may contain a
    ``design_basis`` dict which is JSON-encoded automatically."""
    existing = get_project(project_id)
    if existing is None:
        return None
    allowed = {"name", "client", "location", "project_number", "design_basis"}
    sets, values = [], []
    for key, val in fields.items():
        if key not in allowed or val is None:
            continue
        sets.append(f"{key} = ?")
        values.append(json.dumps(val) if key == "design_basis" else val)
    if sets:
        sets.append("updated_at = ?")
        values.append(_now())
        values.append(project_id)
        with _connect() as conn:
            conn.execute(f"UPDATE projects SET {', '.join(sets)} WHERE id = ?", values)
    return get_project(project_id)


def delete_project(project_id: str) -> bool:
    with _connect() as conn:
        cur = conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    return cur.rowcount > 0


# ── Saved results ─────────────────────────────────────────────────────────────

def add_result(project_id: str, module: str, title: str, compliant: bool, payload: dict) -> Optional[dict]:
    if get_project(project_id) is None:
        return None
    now = _now()
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO saved_results (project_id, module, title, compliant, payload, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (project_id, module, title, 1 if compliant else 0, json.dumps(payload), now),
        )
        # Touch the parent project so ordering reflects activity.
        conn.execute("UPDATE projects SET updated_at = ? WHERE id = ?", (now, project_id))
        rid = cur.lastrowid
    return {
        "id": rid,
        "project_id": project_id,
        "module": module,
        "title": title,
        "compliant": compliant,
        "payload": payload,
        "created_at": now,
    }


def list_results(project_id: str) -> Optional[list[dict]]:
    if get_project(project_id) is None:
        return None
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM saved_results WHERE project_id = ? ORDER BY id DESC", (project_id,)
        ).fetchall()
    return [
        {
            "id": r["id"],
            "project_id": r["project_id"],
            "module": r["module"],
            "title": r["title"],
            "compliant": bool(r["compliant"]),
            "payload": json.loads(r["payload"]),
            "created_at": r["created_at"],
        }
        for r in rows
    ]
