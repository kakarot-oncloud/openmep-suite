"""Pydantic models for Fire Protection API endpoints."""

from pydantic import BaseModel, Field
from typing import Optional
from .electrical import RegionEnum


class SprinklerRequest(BaseModel):
    region: RegionEnum = RegionEnum.gcc
    occupancy_hazard: str = Field(default="OH1", description="LH/OH1/OH2/EH1/EH2")
    area_protected_m2: float = Field(gt=0)
    ceiling_height_m: float = Field(default=4.0, gt=0)
    sprinkler_coverage_m2: float = Field(default=9.0, gt=0)
    sprinkler_k_factor: float = Field(default=80.0, gt=0)
    design_area_m2: Optional[float] = Field(default=None)
    design_density_mm_min: Optional[float] = Field(default=None)
    hose_allowance_l_min: float = Field(default=500.0, ge=0)

    model_config = {"json_schema_extra": {
        "example": {
            "region": "gcc",
            "occupancy_hazard": "OH1",
            "area_protected_m2": 2500,
            "ceiling_height_m": 4.5,
            "sprinkler_coverage_m2": 9,
            "sprinkler_k_factor": 80,
        }
    }}
