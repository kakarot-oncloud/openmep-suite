"""
Project Workspace Routes (persistent).

Stores projects, their design basis, and saved calculation results in SQLite so
they survive restarts. This is the persistent counterpart to the stateless
calculation endpoints — run a calculation, then POST the result here to keep it
under a project.
"""

from typing import Any

from fastapi import APIRouter, HTTPException

from backend import db
from backend.models.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    SavedResult,
    SavedResultCreate,
    SavedResultList,
)

router = APIRouter(prefix="/projects", tags=["Project Workspace"])


@router.post("", summary="Create a project", response_model=Project, status_code=201)
async def create_project(req: ProjectCreate) -> Any:
    db.init_db()
    return db.create_project(
        name=req.name,
        client=req.client,
        location=req.location,
        project_number=req.project_number,
        design_basis=req.design_basis.model_dump(),
    )


@router.get("", summary="List all projects")
async def list_projects() -> Any:
    db.init_db()
    projects = db.list_projects()
    return {"count": len(projects), "projects": projects}


@router.get("/{project_id}", summary="Get a project", response_model=Project)
async def get_project(project_id: str) -> Any:
    db.init_db()
    project = db.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
    return project


@router.put("/{project_id}", summary="Update a project", response_model=Project)
async def update_project(project_id: str, req: ProjectUpdate) -> Any:
    db.init_db()
    fields = req.model_dump(exclude_none=True)
    if "design_basis" in fields and req.design_basis is not None:
        fields["design_basis"] = req.design_basis.model_dump()
    updated = db.update_project(project_id, fields)
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
    return updated


@router.delete("/{project_id}", summary="Delete a project")
async def delete_project(project_id: str) -> Any:
    db.init_db()
    if not db.delete_project(project_id):
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
    return {"status": "deleted", "project_id": project_id}


@router.post("/{project_id}/results", summary="Save a calculation result to a project",
             response_model=SavedResult, status_code=201)
async def add_result(project_id: str, req: SavedResultCreate) -> Any:
    db.init_db()
    saved = db.add_result(
        project_id=project_id,
        module=req.module,
        title=req.title,
        compliant=req.compliant,
        payload=req.payload,
    )
    if saved is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
    return saved


@router.get("/{project_id}/results", summary="List saved results for a project",
            response_model=SavedResultList)
async def list_results(project_id: str) -> Any:
    db.init_db()
    results = db.list_results(project_id)
    if results is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
    return {"project_id": project_id, "count": len(results), "results": results}
