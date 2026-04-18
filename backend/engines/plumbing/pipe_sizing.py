"""
Plumbing Pipe Sizing Engine
Hunter method / Loading Units method — BS EN 806 / IS 1172 / AS/NZS 3500
"""

import math
from dataclasses import dataclass


@dataclass
class PlumbingInput:
    region: str = "gcc"
    system: str = "DHWS"           # 'CWDS', 'DHWS', 'drainage', 'fire'
    flow_units: float = 20.0       # Total fixture units (DU - Discharge Units)
    pipe_material: str = "copper"  # 'copper', 'pvc', 'ppr', 'gi', 'hdpe'
    max_velocity_m_s: float = 2.0
    residual_pressure_kpa: float = 100.0  # Minimum residual pressure at end


@dataclass
class PipeSizingResult:
    pipe_material: str = ""
    flow_rate_l_s: float = 0.0
    velocity_m_s: float = 0.0
    pipe_diameter_mm: float = 0.0
    pipe_nominal_dn: int = 0
    pressure_drop_kpa_m: float = 0.0
    standard: str = ""
    summary: str = ""


# Fixture unit to flow rate conversion (EN 806-3 / IS 1172)
# DU to L/s  — EN 806-3 Table B.3
def du_to_flow_l_s(du: float) -> float:
    """Convert fixture units (DU) to design flow rate (L/s) via EN 806-3 formula."""
    if du <= 0:
        return 0.0
    if du <= 1:
        return 0.25
    # Qc = 0.682 × √DU  (simplified Simpson/Hunter formula for mixed usage)
    return 0.682 * math.sqrt(du)


# Pipe friction loss — Hazen-Williams  ΔP (Pa/m)
def hazen_williams_pressure_drop(Q_l_s: float, D_m: float, C: float = 130) -> float:
    """Hazen-Williams head loss in Pa/m."""
    if Q_l_s <= 0 or D_m <= 0:
        return 0.0
    # V = C × R^0.63 × S^0.54  → solve for S (slope = Pa_per_m / 9810)
    # Using friction factor form: hf/L = 10.67 × Q^1.852 / (C^1.852 × D^4.87)
    Q_m3s = Q_l_s / 1000
    hf_per_m = 10.67 * (Q_m3s**1.852) / ((C**1.852) * (D_m**4.87))
    return hf_per_m * 9810  # Convert m/m to Pa/m


HW_C = {"copper": 140, "pvc": 150, "ppr": 140, "gi": 100, "hdpe": 150, "stainless": 145}

STANDARD_DN = [15, 20, 25, 32, 40, 50, 65, 80, 100, 125, 150, 200, 250, 300]
DN_TO_ID_MM = {15: 14, 20: 19, 25: 23, 32: 30, 40: 37, 50: 50, 65: 62, 80: 77, 100: 100, 125: 122, 150: 145, 200: 192, 250: 242, 300: 290}

PLUMBING_STANDARDS = {
    "gcc": "BS EN 806 / DEWA Plumbing Regulations",
    "europe": "BS EN 806 / BS 6700",
    "india": "IS 1172:2011 / NBC 2016 Part 9",
    "australia": "AS/NZS 3500.1:2021",
}


def calculate_pipe_sizing(inp: PlumbingInput) -> PipeSizingResult:
    """Size a pipe segment given fixture unit load."""
    res = PipeSizingResult(pipe_material=inp.pipe_material)
    res.standard = PLUMBING_STANDARDS.get(inp.region, "BS EN 806")

    Q_l_s = du_to_flow_l_s(inp.flow_units)
    res.flow_rate_l_s = round(Q_l_s, 3)

    C = HW_C.get(inp.pipe_material, 130)

    # Find smallest DN where v ≤ max and ΔP is reasonable
    selected_dn = None
    for dn in STANDARD_DN:
        D_m = DN_TO_ID_MM[dn] / 1000
        area = math.pi * (D_m / 2)**2
        v = (Q_l_s / 1000) / area
        if v <= inp.max_velocity_m_s:
            selected_dn = dn
            D_selected = D_m
            v_selected = v
            dp = hazen_williams_pressure_drop(Q_l_s, D_m, C)
            break
    else:
        selected_dn = STANDARD_DN[-1]
        D_selected = DN_TO_ID_MM[selected_dn] / 1000
        v_selected = (Q_l_s / 1000) / (math.pi * (D_selected/2)**2)
        dp = hazen_williams_pressure_drop(Q_l_s, D_selected, C)

    res.pipe_nominal_dn = selected_dn
    res.pipe_diameter_mm = DN_TO_ID_MM[selected_dn]
    res.velocity_m_s = round(v_selected, 2)
    res.pressure_drop_kpa_m = round(dp / 1000, 4)

    res.summary = (
        f"Plumbing Pipe Sizing [{inp.region.upper()}]\n"
        f"  Standard: {res.standard}\n"
        f"  Fixture Units: {inp.flow_units} DU → Flow: {Q_l_s:.3f} L/s\n"
        f"  Pipe: DN{selected_dn} {inp.pipe_material.upper()}\n"
        f"  Velocity: {v_selected:.2f} m/s (max {inp.max_velocity_m_s} m/s)\n"
        f"  Friction Loss: {res.pressure_drop_kpa_m:.4f} kPa/m"
    )
    return res
