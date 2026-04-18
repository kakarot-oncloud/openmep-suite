"""Pydantic models for Plumbing API endpoints."""

from pydantic import BaseModel, Field
from .electrical import RegionEnum


class PipeSizingRequest(BaseModel):
    region: RegionEnum = RegionEnum.gcc
    system: str = Field(default="CWDS", description="CWDS / DHWS / drainage")
    flow_units: float = Field(gt=0, description="Fixture/Discharge units (DU)")
    pipe_material: str = Field(default="copper", description="copper/pvc/ppr/gi/hdpe")
    max_velocity_m_s: float = Field(default=2.0, gt=0)

    model_config = {"json_schema_extra": {
        "example": {
            "region": "gcc",
            "system": "CWDS",
            "flow_units": 25,
            "pipe_material": "copper",
            "max_velocity_m_s": 2.0,
        }
    }}


class DrainageSizingRequest(BaseModel):
    region: RegionEnum = RegionEnum.gcc
    discharge_units: float = Field(gt=0)
    pipe_material: str = "pvc"
    gradient: float = Field(default=0.01, gt=0, le=0.25)
