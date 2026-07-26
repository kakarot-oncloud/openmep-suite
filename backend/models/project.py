"""
Pydantic models for project workspaces, design basis, and saved results.

These back the persistent project store (see ``backend/db.py`` and
``backend/api/routes/projects.py``). A *design basis* captures the shared
engineering assumptions for a project (region, ambient temperature, power
factor, safety factors) so every calculation can inherit them instead of
re-entering the same values.
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class DesignBasis(BaseModel):
    """Project-wide default engineering assumptions inherited by every module."""

    region: str = Field(default="gcc", description="gcc | europe | india | australia")
    sub_region: str = Field(default="", description="e.g. 'dewa', 'uk', 'maharashtra', 'nsw'")

    ambient_temp_c: Optional[float] = Field(
        default=None, ge=-20, le=80, description="Design ambient °C (region default if unset)"
    )
    power_factor: float = Field(default=0.85, ge=0.1, le=1.0)
    safety_factor: float = Field(default=1.10, ge=1.0, le=2.0)

    default_cable_type: str = Field(default="XLPE_CU")
    default_installation_method: str = Field(default="C")

    vd_limit_power_pct: Optional[float] = Field(default=None, ge=0.5, le=10)
    vd_limit_lighting_pct: Optional[float] = Field(default=None, ge=0.5, le=10)

    notes: str = ""


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    client: str = ""
    location: str = ""
    project_number: str = ""
    design_basis: DesignBasis = Field(default_factory=DesignBasis)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    client: Optional[str] = None
    location: Optional[str] = None
    project_number: Optional[str] = None
    design_basis: Optional[DesignBasis] = None


class Project(BaseModel):
    id: str
    name: str
    client: str = ""
    location: str = ""
    project_number: str = ""
    design_basis: DesignBasis
    created_at: str
    updated_at: str
    result_count: int = 0


class SavedResultCreate(BaseModel):
    module: str = Field(min_length=1, max_length=100, description="e.g. 'cable_sizing'")
    title: str = Field(default="", max_length=200)
    compliant: bool = True
    payload: dict = Field(default_factory=dict, description="Full calculation result JSON")


class SavedResult(BaseModel):
    id: int
    project_id: str
    module: str
    title: str
    compliant: bool
    payload: dict
    created_at: str


class SavedResultList(BaseModel):
    project_id: str
    count: int
    results: List[SavedResult]


class BatchCircuit(BaseModel):
    """One circuit row in a cable-schedule batch. Inherits design-basis defaults."""

    circuit_ref: str = Field(default="", max_length=100)
    description: str = ""
    load_kw: float = Field(gt=0, le=10000)
    power_factor: Optional[float] = Field(default=None, ge=0.1, le=1.0)
    phases: int = Field(default=3, description="1 or 3")
    cable_length_m: float = Field(gt=0, le=10000)
    circuit_type: str = Field(default="power", description="power | lighting")
    cable_type: Optional[str] = None
    installation_method: Optional[str] = None
    ambient_temp_c: Optional[float] = None


class CableScheduleBatchRequest(BaseModel):
    design_basis: DesignBasis = Field(default_factory=DesignBasis)
    circuits: List[BatchCircuit] = Field(min_length=1, max_length=500)


class TableExportRequest(BaseModel):
    """Generic tabular export payload used by the CSV/Excel export endpoints."""

    title: str = "OpenMEP Export"
    columns: List[str] = Field(min_length=1)
    rows: List[List[Any]] = Field(default_factory=list)
