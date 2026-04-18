"""Pydantic models for Electrical API endpoints."""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class RegionEnum(str, Enum):
    gcc = "gcc"
    europe = "europe"
    india = "india"
    australia = "australia"


class CircuitTypeEnum(str, Enum):
    power = "power"
    lighting = "lighting"


class PhasesEnum(int, Enum):
    single = 1
    three = 3


# ─── Cable Sizing ───────────────────────────────────────────────────────────
class CableSizingRequest(BaseModel):
    region: RegionEnum = RegionEnum.gcc
    sub_region: str = Field(default="", description="e.g. 'dewa', 'uk', 'maharashtra', 'nsw'")

    load_kw: float = Field(gt=0, le=10000, description="Load in kW")
    power_factor: float = Field(default=0.85, ge=0.1, le=1.0)
    phases: PhasesEnum = PhasesEnum.three
    voltage_v: Optional[float] = Field(default=None, description="Override supply voltage")

    cable_type: str = Field(default="XLPE_CU")
    installation_method: str = Field(default="C")
    cable_length_m: float = Field(gt=0, le=10000)
    number_of_runs: int = Field(default=1, ge=1, le=10)

    ambient_temp_c: Optional[float] = Field(default=None, description="Actual ambient °C")
    num_grouped_circuits: int = Field(default=1, ge=1, le=50)
    cables_touching: bool = True

    circuit_type: CircuitTypeEnum = CircuitTypeEnum.power
    demand_factor: float = Field(default=1.0, ge=0.1, le=1.0)

    project_name: str = ""
    circuit_from: str = ""
    circuit_to: str = ""

    fault_level_ka: Optional[float] = Field(default=None, ge=0, le=100)
    protection_time_s: float = Field(default=0.4, ge=0.001, le=5.0)

    model_config = {"json_schema_extra": {
        "example": {
            "region": "gcc",
            "sub_region": "dewa",
            "load_kw": 45,
            "power_factor": 0.85,
            "phases": 3,
            "cable_type": "XLPE_CU",
            "installation_method": "E",
            "cable_length_m": 120,
            "ambient_temp_c": 50,
            "num_grouped_circuits": 3,
            "circuit_type": "power",
            "project_name": "Dubai Office Tower",
            "circuit_from": "MLVSB",
            "circuit_to": "DB-LVL04",
        }
    }}


class CableSizingResponse(BaseModel):
    status: str = "success"
    region: str
    standard: str
    authority: str
    project_name: str = ""
    circuit_from: str = ""
    circuit_to: str = ""
    load_kw: float
    power_factor: float
    phases: int
    supply_voltage_v: float
    design_current_ib_a: float
    cable_type: str
    cable_type_description: str
    installation_method: str
    installation_method_description: str
    selected_size_mm2: float
    tabulated_rating_it_a: float
    ca_factor: float
    cg_factor: float
    derated_rating_iz_a: float
    cable_length_m: float
    voltage_drop_mv: float
    voltage_drop_pct: float
    voltage_drop_limit_pct: float
    voltage_drop_pass: bool
    protection_device_a: float
    earth_conductor_mm2: float
    fault_level_ka: Optional[float] = None
    min_cpc_adiabatic_mm2: Optional[float] = None
    fault_protection_pass: Optional[bool] = None
    current_check_pass: bool
    overall_compliant: bool
    compliance_statements: List[str]
    warnings: List[str]
    calculation_summary: str


# ─── Voltage Drop ────────────────────────────────────────────────────────────
class VoltageDropRequest(BaseModel):
    region: RegionEnum
    sub_region: str = ""
    cable_type: str = "XLPE_CU"
    conductor_size_mm2: float = Field(gt=0)
    cable_length_m: float = Field(gt=0)
    design_current_a: float = Field(gt=0)
    phases: PhasesEnum = PhasesEnum.three
    circuit_type: CircuitTypeEnum = CircuitTypeEnum.power


# ─── Maximum Demand ─────────────────────────────────────────────────────────
class LoadItemModel(BaseModel):
    description: str
    quantity: int = Field(ge=1)
    unit_kw: float = Field(gt=0)
    power_factor: float = Field(default=0.85, ge=0.1, le=1.0)
    demand_factor: float = Field(default=1.0, ge=0.0, le=1.0)
    load_type: str = "power"
    phases: int = Field(default=3, ge=1, le=3)


class MaxDemandRequest(BaseModel):
    region: RegionEnum = RegionEnum.gcc
    supply_voltage_lv: float = Field(default=400.0, gt=0)
    diversity_factor: float = Field(default=1.0, ge=0.1, le=1.0)
    future_expansion_pct: float = Field(default=20.0, ge=0, le=100)
    loads: List[LoadItemModel]


# ─── Short Circuit ─────────────────────────────────────────────────────────
class ShortCircuitRequest(BaseModel):
    region: RegionEnum = RegionEnum.gcc
    transformer_kva: float = Field(gt=0)
    transformer_impedance_pct: float = Field(default=5.5, ge=1, le=20)
    lv_voltage: float = Field(default=400.0, gt=0)
    cable_type: str = "XLPE_CU"
    cable_size_mm2: float = Field(gt=0)
    cable_length_m: float = Field(gt=0)
    upstream_fault_level_ka: Optional[float] = None


# ─── Lighting ───────────────────────────────────────────────────────────────
class LightingRequest(BaseModel):
    region: RegionEnum = RegionEnum.gcc
    room_name: str = "Office"
    room_type: str = "office"
    length_m: float = Field(gt=0)
    width_m: float = Field(gt=0)
    height_m: float = Field(gt=0)
    work_plane_height_m: float = Field(default=0.85, ge=0)
    target_lux: Optional[float] = Field(default=None, ge=1)
    luminaire_type: str = "LED Panel"
    luminaire_lumens: float = Field(default=4000, gt=0)
    luminaire_watts: float = Field(default=40, gt=0)
    luminaire_efficiency: float = Field(default=1.0, ge=0.1, le=1.0)
    ceiling_reflectance: float = Field(default=0.70, ge=0, le=1)
    wall_reflectance: float = Field(default=0.50, ge=0, le=1)
    floor_reflectance: float = Field(default=0.20, ge=0, le=1)
    llf: float = Field(default=0.80, ge=0.1, le=1.0)
