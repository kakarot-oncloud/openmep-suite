"""
Duct Sizing Engine
Equal friction method — ASHRAE / CIBSE
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class DuctSegment:
    """Input for a single duct segment."""
    segment_id: str
    airflow_l_s: float          # Flow rate in L/s
    duct_type: str = "rectangular"  # 'rectangular' or 'circular'
    max_velocity_m_s: float = 8.0   # Max design velocity (m/s)
    friction_rate_pa_m: float = 0.8  # Design friction rate (Pa/m) — typical 0.8–1.0 ASHRAE


@dataclass
class DuctSizeResult:
    segment_id: str = ""
    airflow_l_s: float = 0.0
    velocity_m_s: float = 0.0
    diameter_mm: Optional[float] = None
    width_mm: Optional[float] = None
    height_mm: Optional[float] = None
    hydraulic_diameter_mm: float = 0.0
    pressure_drop_pa_m: float = 0.0
    duct_area_m2: float = 0.0
    velocity_limited: bool = False
    note: str = ""
    summary: str = ""


def size_duct(seg: DuctSegment) -> DuctSizeResult:
    """Size a duct segment by the equal friction method (ASHRAE / CIBSE).

    The equal-friction diameter is derived from the target friction rate
    (Pa/m). If the resulting velocity exceeds the segment's design maximum,
    the duct is resized to the velocity limit and the *actual* friction rate
    is recomputed from Darcy-Weisbach.
    """
    res = DuctSizeResult(segment_id=seg.segment_id, airflow_l_s=seg.airflow_l_s)

    Q = seg.airflow_l_s / 1000.0        # m³/s
    rho = 1.2                           # kg/m³ air density
    f = 0.02                            # Darcy friction factor (typical sheet metal)
    friction_rate = seg.friction_rate_pa_m

    # Equal-friction round-duct diameter:
    #   ΔP/L = f * rho * 8 * Q² / (π² * D⁵)  ->  D = (f*rho*8*Q² / (π²*ΔP/L))^(1/5)
    D = (f * rho * 8 * Q**2 / (math.pi**2 * friction_rate)) ** (1.0 / 5.0)
    v = Q / (math.pi * D**2 / 4.0)

    if v > seg.max_velocity_m_s:
        # Velocity-limited: cap velocity and resize, then recompute friction rate
        res.velocity_limited = True
        v = seg.max_velocity_m_s
        D = math.sqrt(4 * Q / (math.pi * v))
        pressure_drop = f * rho * v**2 / (2 * D)
        res.note = (
            f"Velocity-limited to {seg.max_velocity_m_s} m/s; duct enlarged, so "
            f"actual friction rate {pressure_drop:.3f} Pa/m differs from target "
            f"{friction_rate} Pa/m."
        )
    else:
        pressure_drop = friction_rate

    area_round = math.pi * D**2 / 4.0

    if seg.duct_type == "circular":
        res.diameter_mm = round(D * 1000, 0)
        res.velocity_m_s = round(v, 2)
        res.hydraulic_diameter_mm = round(D * 1000, 0)
        res.pressure_drop_pa_m = round(pressure_drop, 3)
        res.duct_area_m2 = round(area_round, 4)

    else:  # rectangular — 2:1 aspect ratio, keep the same cross-sectional area
        w = math.sqrt(area_round * 2)   # width
        h = w / 2                       # height
        # Round up to standard sizes (50mm increments)
        w_std = math.ceil(w * 1000 / 50) * 50
        h_std = math.ceil(h * 1000 / 50) * 50

        w_m = w_std / 1000.0
        h_m = h_std / 1000.0
        area_rect = w_m * h_m
        v_actual = Q / area_rect
        Dh = 2 * w_m * h_m / (w_m + h_m)   # hydraulic diameter
        dp_actual = f * rho * v_actual**2 / (2 * Dh)

        res.width_mm = float(w_std)
        res.height_mm = float(h_std)
        res.velocity_m_s = round(v_actual, 2)
        res.hydraulic_diameter_mm = round(Dh * 1000, 1)
        res.pressure_drop_pa_m = round(dp_actual, 3)
        res.duct_area_m2 = round(area_rect, 4)

    dim_str = (
        f"Ø{res.diameter_mm}mm" if seg.duct_type == "circular"
        else f"{res.width_mm}×{res.height_mm}mm"
    )
    res.summary = (
        f"Segment {seg.segment_id}: {seg.airflow_l_s} L/s | {dim_str} | "
        f"v = {res.velocity_m_s} m/s | ΔP = {res.pressure_drop_pa_m} Pa/m"
        + (f" | ⚠ {res.note}" if res.velocity_limited else "")
    )
    return res
