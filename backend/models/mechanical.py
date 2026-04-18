"""Pydantic models for Mechanical/HVAC API endpoints."""

from pydantic import BaseModel, Field
from typing import List
from .electrical import RegionEnum


class CoolingLoadRequest(BaseModel):
    region: RegionEnum = RegionEnum.gcc
    zone_name: str = "Zone 1"
    zone_type: str = "office"
    floor_area_m2: float = Field(gt=0)
    height_m: float = Field(default=3.0, gt=0)
    glass_area_m2: float = Field(default=10.0, ge=0)
    glass_u_value: float = Field(default=2.8, gt=0)
    glass_shgc: float = Field(default=0.4, ge=0, le=1)
    glass_orientation: str = "W"
    wall_area_m2: float = Field(default=60.0, ge=0)
    wall_u_value: float = Field(default=0.45, gt=0)
    roof_area_m2: float = Field(default=0.0, ge=0)
    roof_u_value: float = Field(default=0.35, gt=0)
    occupancy: int = Field(default=10, ge=0)
    metabolic_rate_w: float = Field(default=90.0, gt=0)
    equipment_w_m2: float = Field(default=20.0, ge=0)
    lighting_w_m2: float = Field(default=10.0, ge=0)
    fresh_air_l_s_person: float = Field(default=10.0, ge=0)
    cop: float = Field(default=3.0, gt=0)
    safety_factor: float = Field(default=1.10, ge=1.0, le=2.0)

    model_config = {"json_schema_extra": {
        "example": {
            "region": "gcc",
            "zone_name": "Open Plan Office - Level 3",
            "zone_type": "office",
            "floor_area_m2": 800,
            "height_m": 3.2,
            "glass_area_m2": 120,
            "glass_u_value": 2.0,
            "glass_shgc": 0.25,
            "glass_orientation": "W",
            "wall_area_m2": 300,
            "wall_u_value": 0.35,
            "occupancy": 80,
            "equipment_w_m2": 25,
            "lighting_w_m2": 10,
            "cop": 3.5,
        }
    }}


class DuctSegmentRequest(BaseModel):
    segment_id: str = "S1"
    airflow_l_s: float = Field(gt=0)
    duct_type: str = "rectangular"
    max_velocity_m_s: float = Field(default=8.0, gt=0)
    friction_rate_pa_m: float = Field(default=0.8, gt=0)


class MultiZoneCoolingRequest(BaseModel):
    region: RegionEnum = RegionEnum.gcc
    zones: List[CoolingLoadRequest]
    chiller_cop: float = Field(default=3.0, gt=0)
    diversity_factor: float = Field(default=0.85, ge=0.1, le=1.0)
