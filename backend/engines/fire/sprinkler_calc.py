"""
Fire Sprinkler System Calculation Engine
Supports: NFPA 13, BS EN 12845, IS 15105, AS 2118.1
"""

import math
from dataclasses import dataclass


@dataclass
class SprinklerInput:
    region: str = "gcc"
    occupancy_hazard: str = "OH1"   # LH, OH1, OH2, EH1, EH2 (BS EN 12845) / Light/Ordinary/Extra (NFPA)
    area_protected_m2: float = 3000.0
    ceiling_height_m: float = 4.0
    sprinkler_coverage_m2: float = 9.0  # Max area per sprinkler head
    sprinkler_k_factor: float = 80.0    # K-factor (L/min/bar^0.5) — K80 standard
    design_area_m2: float = 216.0       # Hydraulically remote design area
    design_density_mm_min: float = 5.0  # Discharge density (mm/min = L/min/m²)
    hose_allowance_l_min: float = 500.0 # Hose stream allowance


@dataclass
class SprinklerResult:
    hazard_class: str = ""
    design_standard: str = ""
    num_sprinklers_design_area: int = 0
    design_flow_l_min: float = 0.0
    hose_allowance_l_min: float = 0.0
    total_system_flow_l_min: float = 0.0
    residual_pressure_bar: float = 0.0
    pump_flow_l_min: float = 0.0
    pump_head_m: float = 0.0
    pump_power_kw: float = 0.0
    tank_capacity_m3: float = 0.0
    supply_duration_min: int = 60
    summary: str = ""


SPRINKLER_STANDARDS = {
    "gcc": "BS EN 12845:2015 / NFPA 13 (2022 Ed.) / Civil Defence",
    "europe": "BS EN 12845:2015 / BS 9251",
    "india": "IS 15105:2002 / NBC 2016 Part 4 / TAC",
    "australia": "AS 2118.1:2017 / AS 2118.6",
}

HAZARD_PARAMS = {
    "LH":  {"density_mm_min": 2.25, "area_m2": 84,  "duration_min": 30},
    "OH1": {"density_mm_min": 5.0,  "area_m2": 216, "duration_min": 60},
    "OH2": {"density_mm_min": 5.0,  "area_m2": 360, "duration_min": 60},
    "EH1": {"density_mm_min": 7.5,  "area_m2": 260, "duration_min": 90},
    "EH2": {"density_mm_min": 10.0, "area_m2": 260, "duration_min": 90},
}


def calculate_sprinkler(inp: SprinklerInput) -> SprinklerResult:
    """Calculate fire sprinkler system — BS EN 12845 / NFPA 13 method."""
    res = SprinklerResult(
        hazard_class=inp.occupancy_hazard,
        design_standard=SPRINKLER_STANDARDS.get(inp.region, "BS EN 12845"),
    )

    params = HAZARD_PARAMS.get(inp.occupancy_hazard.upper(), HAZARD_PARAMS["OH1"])
    design_density = params["density_mm_min"]  # L/min/m²
    design_area = inp.design_area_m2 or params["area_m2"]
    duration = params["duration_min"]
    res.supply_duration_min = duration

    # Number of sprinklers in design area
    n_sprinklers = math.ceil(design_area / inp.sprinkler_coverage_m2)
    res.num_sprinklers_design_area = n_sprinklers

    # Design flow rate  Q = density × area
    Q_design_l_min = design_density * design_area
    res.design_flow_l_min = round(Q_design_l_min, 1)
    res.hose_allowance_l_min = inp.hose_allowance_l_min

    # Total flow including hose allowance
    Q_total = Q_design_l_min + inp.hose_allowance_l_min
    res.total_system_flow_l_min = round(Q_total, 1)

    # Sprinkler residual pressure (at most remote sprinkler)
    # P = (Q/K)²  where Q = flow per sprinkler (L/min)
    q_per_sprinkler = Q_design_l_min / n_sprinklers
    p_residual = (q_per_sprinkler / inp.sprinkler_k_factor) ** 2  # bar
    res.residual_pressure_bar = round(max(p_residual, 0.5), 2)

    # Fire pump sizing
    # Total head = static head + friction losses + residual pressure
    # Assume static head 30m, friction 20% of flow head
    static_head_m = max(inp.ceiling_height_m * 1.5, 30)
    pump_head_m = static_head_m + (p_residual * 10.2) + 10  # 10.2 m per bar
    pump_head_m = round(pump_head_m, 1)
    res.pump_head_m = pump_head_m

    Q_pump_l_s = Q_total / 60
    rho = 1000  # water kg/m³
    g = 9.81
    efficiency = 0.65
    pump_kw = (Q_pump_l_s * rho * g * pump_head_m) / (1000 * efficiency)

    res.pump_flow_l_min = round(Q_total, 1)
    res.pump_power_kw = round(pump_kw, 2)

    # Tank capacity
    tank_m3 = (Q_total * duration) / 1000
    res.tank_capacity_m3 = round(tank_m3 * 1.1, 1)  # 10% safety margin

    # Summary
    lines = [
        "═══════════════════════════════════════════════════════════",
        f"  FIRE SPRINKLER SYSTEM — {inp.occupancy_hazard} Hazard",
        f"  Standard: {res.design_standard}",
        "───────────────────────────────────────────────────────────",
        f"  Design Area: {design_area} m²  |  {n_sprinklers} sprinklers",
        f"  Design Density: {design_density} mm/min",
        f"  Design Flow: {Q_design_l_min:.1f} L/min",
        f"  Hose Allowance: {inp.hose_allowance_l_min:.1f} L/min",
        f"  TOTAL SYSTEM FLOW: {Q_total:.1f} L/min",
        f"  Residual Pressure (remote): {p_residual:.2f} bar",
        "───────────────────────────────────────────────────────────",
        f"  Fire Pump: {Q_total:.0f} L/min @ {pump_head_m:.1f} m TDH",
        f"  Pump Power: {pump_kw:.2f} kW (η = {efficiency:.0%})",
        f"  Fire Tank: {res.tank_capacity_m3:.1f} m³ ({duration} min supply)",
        "═══════════════════════════════════════════════════════════",
    ]
    res.summary = "\n".join(lines)

    return res
