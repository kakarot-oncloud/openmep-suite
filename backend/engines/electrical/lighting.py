"""
Lighting Calculation Engine
Lumen method (CIE / CIBSE) — illuminance calculation for interior spaces.
Supports GCC (DEWA/DCD standards), Europe (EN 12464), India (SP:72), Australia (AS/NZS 1680).
"""

import math
import numpy as np
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LightingInput:
    """Input for interior lighting calculation."""
    region: str = "gcc"
    room_name: str = "Office"
    room_type: str = "office"          # 'office', 'classroom', 'corridor', 'warehouse', etc.

    length_m: float = 10.0
    width_m: float = 8.0
    height_m: float = 3.0             # Ceiling height
    work_plane_height_m: float = 0.85  # Desk/work surface height (0.85m typical)

    # Target illuminance
    target_lux: Optional[float] = None  # Auto-set from room type if None
    maintained_lux: float = 500.0      # Maintained average illuminance (Em)

    # Luminaire data
    luminaire_type: str = "LED Panel"
    luminaire_lumens: float = 4000.0   # Initial lamp lumens per luminaire
    luminaire_efficiency: float = 1.0  # Luminaire efficiency (0–1)
    luminaire_length_m: float = 0.6
    luminaire_width_m: float = 0.6
    luminaire_watts: float = 40.0

    # Room reflectances (%)
    ceiling_reflectance: float = 0.70  # ρc
    wall_reflectance: float = 0.50     # ρw
    floor_reflectance: float = 0.20    # ρf

    # Maintenance
    llf: float = 0.80   # Light Loss Factor (LLF) — includes LLMF, LSF, LMF, RSMF
    # Specific loss factors:
    lamp_lumen_maintenance: float = 0.90
    luminaire_survival: float = 0.97
    luminaire_maintenance: float = 0.95
    room_surface_maintenance: float = 0.97

    uniformity_required: float = 0.60  # U0 minimum (En 12464 general)


@dataclass
class LightingResult:
    room_name: str = ""
    room_area_m2: float = 0.0
    room_index_k: float = 0.0
    uf_coefficient: float = 0.0
    llf: float = 0.0
    target_lux_em: float = 0.0
    num_luminaires: int = 0
    luminaires_per_row: int = 0
    num_rows: int = 0
    achieved_lux: float = 0.0
    uniformity_achieved: float = 0.0
    total_watts: float = 0.0
    lux_per_watt: float = 0.0
    lpd_w_per_m2: float = 0.0         # Lighting Power Density
    lpd_limit_w_per_m2: float = 0.0   # Regional LPD limit
    lpd_compliant: bool = True
    standard_reference: str = ""
    recommendations: list = field(default_factory=list)
    summary: str = ""


# Illuminance targets by space type (lux) — EN 12464-1 / CIBSE SLL Code for Lighting
ILLUMINANCE_TARGETS = {
    "office": 500,
    "open_plan_office": 500,
    "meeting_room": 300,
    "reception": 300,
    "corridor": 100,
    "staircase": 150,
    "toilet_wc": 200,
    "lobby": 200,
    "loading_bay": 150,
    "warehouse": 200,
    "workshop": 300,
    "classroom": 300,
    "library": 500,
    "hospital_ward": 100,
    "hospital_icu": 500,
    "hospital_theatre": 1000,
    "retail": 500,
    "supermarket": 750,
    "car_park_indoor": 75,
    "car_park_ramp": 300,
    "kitchen_commercial": 500,
}

# LPD limits (W/m²) by region and space type — ASHRAE 90.1 / EN 15193 / ECBC 2017 / NCC J6
LPD_LIMITS = {
    "gcc": {"office": 10.7, "classroom": 10.7, "corridor": 7.6, "warehouse": 8.0, "default": 11.0},
    "europe": {"office": 9.0, "classroom": 9.0, "corridor": 6.0, "warehouse": 7.0, "default": 10.0},
    "india": {"office": 10.7, "classroom": 10.7, "corridor": 7.6, "warehouse": 8.0, "default": 11.0},
    "australia": {"office": 9.0, "classroom": 9.0, "corridor": 6.0, "warehouse": 7.0, "default": 10.0},
}

# Utilisation factor table (simplified CIE/CIBSE Zonal Cavity method)
# Index: Room Index K; Values for ceiling/wall/floor reflectances ~70/50/20%
UF_TABLE_K = [0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
UF_DIRECT_INDIRECT = [0.33, 0.40, 0.46, 0.52, 0.57, 0.64, 0.69, 0.73, 0.79, 0.82]

LIGHTING_STANDARDS = {
    "gcc": "EN 12464-1:2021 / DEWA Circular / CIBSE LG Series",
    "europe": "EN 12464-1:2021 (CEN) / CIBSE Lighting Guide",
    "india": "NBC 2016 Part 8 / SP:72 (S&T):2010 / IS 3646",
    "australia": "AS/NZS 1680 Interior Lighting / NCC Section J6",
}


def calculate_lighting(inp: LightingInput) -> LightingResult:
    """Lumen method calculation for interior lighting."""
    res = LightingResult(room_name=inp.room_name)

    # Room geometry
    area = inp.length_m * inp.width_m
    hm = inp.height_m - inp.work_plane_height_m  # Mounting height above work plane
    res.room_area_m2 = round(area, 2)

    # Room Index K (CIE method)
    K = (inp.length_m * inp.width_m) / (hm * (inp.length_m + inp.width_m))
    res.room_index_k = round(K, 2)

    # Utilisation Factor (UF) — interpolated from simplified table
    uf = float(np.interp(K, UF_TABLE_K, UF_DIRECT_INDIRECT))
    # Adjust slightly for reflectances vs reference 70/50/20
    ref_adj = ((inp.ceiling_reflectance - 0.70) * 0.1 +
               (inp.wall_reflectance - 0.50) * 0.05 +
               (inp.floor_reflectance - 0.20) * 0.02)
    uf = max(0.2, min(0.95, uf + ref_adj))
    res.uf_coefficient = round(uf, 3)

    # Light Loss Factor
    llf = inp.lamp_lumen_maintenance * inp.luminaire_survival * inp.luminaire_maintenance * inp.room_surface_maintenance
    res.llf = round(llf, 3)

    # Target illuminance
    target_lux = inp.target_lux or ILLUMINANCE_TARGETS.get(inp.room_type, inp.maintained_lux)
    res.target_lux_em = target_lux

    # Number of luminaires  N = (Em × A) / (Φ × UF × LLF)
    phi = inp.luminaire_lumens * inp.luminaire_efficiency
    n_exact = (target_lux * area) / (phi * uf * llf)
    n = math.ceil(n_exact)
    if n < 1:
        n = 1

    # Arrange in grid: rows × columns
    aspect = inp.length_m / inp.width_m
    cols = max(1, round(math.sqrt(n * aspect)))
    rows = max(1, math.ceil(n / cols))
    n_actual = rows * cols

    res.num_luminaires = n_actual
    res.luminaires_per_row = cols
    res.num_rows = rows

    # Achieved illuminance
    achieved_lux = (n_actual * phi * uf * llf) / area
    res.achieved_lux = round(achieved_lux, 0)

    # Uniformity (simplified: 0.7 for regular grids, less for corridors)
    if inp.room_type in ("corridor", "staircase"):
        res.uniformity_achieved = round(min(0.70, 0.40 * K), 2)
    else:
        res.uniformity_achieved = round(min(0.80, 0.60 + 0.02 * K), 2)

    # Power calculations
    total_w = n_actual * inp.luminaire_watts
    res.total_watts = round(total_w, 1)
    res.lux_per_watt = round(achieved_lux / total_w, 2) if total_w > 0 else 0.0
    lpd = total_w / area
    res.lpd_w_per_m2 = round(lpd, 2)

    # LPD compliance
    lpd_limits = LPD_LIMITS.get(inp.region, LPD_LIMITS["gcc"])
    lpd_limit = lpd_limits.get(inp.room_type, lpd_limits["default"])
    res.lpd_limit_w_per_m2 = lpd_limit
    res.lpd_compliant = lpd <= lpd_limit

    res.standard_reference = LIGHTING_STANDARDS.get(inp.region, "EN 12464-1")

    # Recommendations
    if achieved_lux < target_lux:
        res.recommendations.append(
            f"Achieved lux {achieved_lux:.0f} < Target {target_lux:.0f} lux. "
            f"Consider higher lumen output luminaires or reduce spacing."
        )
    if not res.lpd_compliant:
        res.recommendations.append(
            f"LPD {lpd:.2f} W/m² exceeds limit {lpd_limit} W/m². "
            f"Switch to more efficient luminaires (higher lm/W)."
        )

    # Summary
    lines = [
        "═══════════════════════════════════════════════════════════",
        f"  LIGHTING CALCULATION — {inp.room_name}",
        f"  Standard: {res.standard_reference}",
        "───────────────────────────────────────────────────────────",
        f"  Room: {inp.length_m}m × {inp.width_m}m × {inp.height_m}m H",
        f"  Area: {area:.1f} m²   |   Work Plane Height: {inp.work_plane_height_m}m",
        f"  Room Index (K):  {res.room_index_k}",
        f"  Utilisation Factor (UF): {res.uf_coefficient}",
        f"  Light Loss Factor (LLF): {res.llf}",
        f"  Reflectances: ρc={inp.ceiling_reflectance} / ρw={inp.wall_reflectance} / ρf={inp.floor_reflectance}",
        "───────────────────────────────────────────────────────────",
        f"  Luminaire: {inp.luminaire_type}  ({inp.luminaire_watts}W / {inp.luminaire_lumens} lm)",
        f"  Target Illuminance (Em): {target_lux} lux",
        f"  Number of Luminaires: {n_actual}  ({rows} rows × {cols}/row)",
        f"  Achieved Illuminance: {achieved_lux:.0f} lux  {'✅' if achieved_lux >= target_lux else '❌'}",
        f"  Uniformity (U0): {res.uniformity_achieved}  {'✅' if res.uniformity_achieved >= inp.uniformity_required else '⚠️'}",
        "───────────────────────────────────────────────────────────",
        f"  Total Power: {total_w:.1f} W",
        f"  Luminous Efficacy (system): {res.lux_per_watt:.1f} lux/W",
        f"  LPD: {lpd:.2f} W/m²  {'✅' if res.lpd_compliant else '❌'} (limit {lpd_limit} W/m²)",
        "═══════════════════════════════════════════════════════════",
    ]
    if res.recommendations:
        lines.append("\n  RECOMMENDATIONS:")
        for r in res.recommendations:
            lines.append(f"  • {r}")

    res.summary = "\n".join(lines)
    return res


