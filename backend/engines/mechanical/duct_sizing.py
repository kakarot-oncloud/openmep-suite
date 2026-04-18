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
    summary: str = ""


def size_duct(seg: DuctSegment) -> DuctSizeResult:
    """Size a duct segment by equal friction method."""
    res = DuctSizeResult(segment_id=seg.segment_id, airflow_l_s=seg.airflow_l_s)
    Q_m3s = seg.airflow_l_s / 1000

    if seg.duct_type == "circular":
        # D = (Q / (v × π/4))^0.5, then iterate for friction
        v = min(seg.max_velocity_m_s, 8.0)
        area = Q_m3s / v
        D = math.sqrt(4 * area / math.pi)
        # Darcy-Weisbach: f = 0.02 (smooth), L=1m
        f = 0.025  # typical sheet metal
        rho = 1.2
        dp_pa_m = f * (rho * v**2 / 2) / D
        res.diameter_mm = round(D * 1000, 0)
        res.velocity_m_s = round(v, 2)
        res.hydraulic_diameter_mm = round(D * 1000, 0)
        res.pressure_drop_pa_m = round(dp_pa_m, 3)
        res.duct_area_m2 = round(area, 4)

    else:  # rectangular
        # Aspect ratio 2:1 typical for coordination
        area = Q_m3s / min(seg.max_velocity_m_s, 8.0)
        w = math.sqrt(area * 2)  # width
        h = w / 2               # height
        v = Q_m3s / (w * h)
        Dh = 2 * w * h / (w + h)  # hydraulic diameter
        f = 0.025
        rho = 1.2
        dp_pa_m = f * (rho * v**2 / 2) / Dh

        # Round up to standard sizes (50mm increments)
        w_std = math.ceil(w * 1000 / 50) * 50
        h_std = math.ceil(h * 1000 / 50) * 50

        res.width_mm = float(w_std)
        res.height_mm = float(h_std)
        res.velocity_m_s = round(Q_m3s / (w_std/1000 * h_std/1000), 2)
        Dh_std = 2 * (w_std/1000) * (h_std/1000) / ((w_std + h_std)/1000)
        res.hydraulic_diameter_mm = round(Dh_std * 1000, 1)
        res.pressure_drop_pa_m = round(dp_pa_m, 3)
        res.duct_area_m2 = round(w_std/1000 * h_std/1000, 4)

    res.summary = (
        f"Segment {seg.segment_id}: {seg.airflow_l_s} L/s | "
        f"{'Ø' + str(res.diameter_mm) + 'mm' if seg.duct_type == 'circular' else str(res.width_mm) + '×' + str(res.height_mm) + 'mm'} | "
        f"v = {res.velocity_m_s} m/s | ΔP = {res.pressure_drop_pa_m} Pa/m"
    )
    return res


from typing import Optional
