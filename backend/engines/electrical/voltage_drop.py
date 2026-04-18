"""
Voltage Drop Analysis Engine
Supports dedicated voltage drop calculation with upsize recommendation.
"""

from dataclasses import dataclass
from typing import Optional
from ..adapters_factory import get_electrical_adapter


@dataclass
class VoltageDrop:
    """Calculate voltage drop for a known cable size."""
    region: str
    sub_region: str = ""
    cable_type: str = "XLPE_CU"
    conductor_size_mm2: float = 16.0
    cable_length_m: float = 100.0
    design_current_a: float = 50.0
    phases: int = 3
    voltage_v: Optional[float] = None
    circuit_type: str = "power"


@dataclass
class VoltageDropResult:
    conductor_size_mm2: float = 0.0
    cable_length_m: float = 0.0
    design_current_a: float = 0.0
    supply_voltage_v: float = 0.0
    vd_mv_am: float = 0.0
    vd_total_mv: float = 0.0
    vd_total_v: float = 0.0
    vd_percent: float = 0.0
    vd_limit_percent: float = 0.0
    receiving_end_voltage_v: float = 0.0
    compliant: bool = True
    recommended_size_mm2: Optional[float] = None
    recommended_vd_pct: Optional[float] = None
    standard: str = ""


def calculate_voltage_drop(inp: VoltageDrop) -> VoltageDropResult:
    adapter = get_electrical_adapter(inp.region, inp.sub_region)
    voltage = inp.voltage_v or (adapter.voltage_lv if inp.phases == 3 else adapter.voltage_phase)

    vd_mv_am = adapter.get_voltage_drop_mv_am(inp.cable_type, inp.conductor_size_mm2, inp.phases)
    vd_total_mv = inp.design_current_a * inp.cable_length_m * vd_mv_am
    vd_total_v = vd_total_mv / 1000
    vd_pct = (vd_total_v / voltage) * 100
    vd_limit = adapter.get_voltage_drop_limit(inp.circuit_type)
    compliant = bool(vd_pct <= vd_limit)

    result = VoltageDropResult(
        conductor_size_mm2=inp.conductor_size_mm2,
        cable_length_m=inp.cable_length_m,
        design_current_a=inp.design_current_a,
        supply_voltage_v=voltage,
        vd_mv_am=round(vd_mv_am, 3),
        vd_total_mv=round(vd_total_mv, 1),
        vd_total_v=round(vd_total_v, 3),
        vd_percent=round(vd_pct, 2),
        vd_limit_percent=vd_limit,
        receiving_end_voltage_v=round(voltage - vd_total_v, 1),
        compliant=compliant,
        standard=adapter.cable_sizing_standard,
    )

    if not compliant:
        sizes = adapter.get_standard_cable_sizes()
        for s in [x for x in sizes if x > inp.conductor_size_mm2]:
            vd_new = inp.design_current_a * inp.cable_length_m * adapter.get_voltage_drop_mv_am(inp.cable_type, s, inp.phases)
            vd_new_pct = (vd_new / 1000 / voltage) * 100
            if vd_new_pct <= vd_limit:
                result.recommended_size_mm2 = s
                result.recommended_vd_pct = round(vd_new_pct, 2)
                break

    return result
