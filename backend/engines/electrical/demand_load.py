"""
Electrical Demand Load / Maximum Demand Calculator
Follows the respective regional standard for demand factors.
"""

import math
from dataclasses import dataclass, field


@dataclass
class LoadItem:
    """Single electrical load item."""
    description: str
    quantity: int
    unit_kw: float
    power_factor: float = 0.85
    demand_factor: float = 1.0
    load_type: str = "power"  # 'power', 'lighting', 'motor', 'hvac', 'emergency'
    phases: int = 3


@dataclass
class DemandLoadResult:
    """Maximum demand calculation result."""
    total_connected_kw: float = 0.0
    total_connected_kva: float = 0.0
    total_demand_kw: float = 0.0
    total_demand_kva: float = 0.0
    overall_power_factor: float = 0.85
    total_demand_current_a: float = 0.0
    main_protection_a: float = 0.0
    transformer_kva_min: float = 0.0
    transformer_kva_recommended: float = 0.0
    breakdown_by_type: dict = field(default_factory=dict)
    calculation_summary: str = ""


# Standard transformer sizes (kVA) — IEC / IEEE common
TRANSFORMER_SIZES = [50, 100, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150]


def calculate_maximum_demand(
    loads: list[LoadItem],
    region: str = "gcc",
    supply_voltage_lv: float = 400.0,
    diversity_factor: float = 1.0,
    future_expansion_pct: float = 20.0,
) -> DemandLoadResult:
    """
    Calculate maximum demand for a project.

    Diversity factor: overall building diversity (typically 0.6–0.9)
    future_expansion_pct: design margin added to result
    """
    result = DemandLoadResult()
    by_type: dict[str, float] = {}

    total_connected_kw = 0.0
    total_demand_kw = 0.0
    total_kvar = 0.0

    for load in loads:
        connected_kw = load.quantity * load.unit_kw
        demand_kw = connected_kw * load.demand_factor
        total_connected_kw += connected_kw
        total_demand_kw += demand_kw
        sin_phi = math.sqrt(1 - load.power_factor**2)
        total_kvar += demand_kw * (sin_phi / load.power_factor)

        ltype = load.load_type
        by_type[ltype] = by_type.get(ltype, 0.0) + demand_kw

    # Apply overall diversity factor
    total_demand_kw *= diversity_factor

    # Add expansion margin
    design_kw = total_demand_kw * (1 + future_expansion_pct / 100)
    design_kvar = total_kvar * diversity_factor * (1 + future_expansion_pct / 100)
    design_kva = math.sqrt(design_kw**2 + design_kvar**2)
    pf = design_kw / design_kva if design_kva > 0 else 0.85

    # Maximum demand current
    id_a = (design_kva * 1000) / (math.sqrt(3) * supply_voltage_lv)

    # Protection device (next standard rating above 1.25 × Id)
    from backend.engines.adapters_factory import get_electrical_adapter
    adapter = get_electrical_adapter(region)
    protection_a = adapter.get_next_protection_rating(id_a * 1.25)

    # Transformer sizing
    for size in TRANSFORMER_SIZES:
        if size >= design_kva:
            tx_min = size
            break
    else:
        tx_min = TRANSFORMER_SIZES[-1]

    for size in TRANSFORMER_SIZES:
        if size >= design_kva * 1.15:  # 15% margin on transformer
            tx_rec = size
            break
    else:
        tx_rec = TRANSFORMER_SIZES[-1]

    result.total_connected_kw = round(total_connected_kw, 2)
    result.total_connected_kva = round(total_connected_kw / 0.85, 2)
    result.total_demand_kw = round(design_kw, 2)
    result.total_demand_kva = round(design_kva, 2)
    result.overall_power_factor = round(pf, 3)
    result.total_demand_current_a = round(id_a, 1)
    result.main_protection_a = protection_a
    result.transformer_kva_min = tx_min
    result.transformer_kva_recommended = tx_rec
    result.breakdown_by_type = {k: round(v, 2) for k, v in by_type.items()}

    summary = [
        "═══════════════════════════════════════════════════════════",
        "  MAXIMUM DEMAND CALCULATION",
        f"  Region: {region.upper()}  |  Supply: {supply_voltage_lv}V 3-phase",
        "───────────────────────────────────────────────────────────",
        f"  Total Connected Load: {result.total_connected_kw} kW",
        f"  Diversity Factor:     {diversity_factor}",
        f"  Future Expansion:     {future_expansion_pct}%",
        f"  Design Demand:        {result.total_demand_kw} kW / {result.total_demand_kva} kVA",
        f"  Overall PF:           {result.overall_power_factor}",
        f"  Maximum Demand Current: {result.total_demand_current_a} A",
        "───────────────────────────────────────────────────────────",
        "  Load Breakdown by Type:",
    ]
    for ltype, kw in result.breakdown_by_type.items():
        summary.append(f"    {ltype.capitalize():15s}: {kw:.2f} kW")
    summary += [
        "───────────────────────────────────────────────────────────",
        f"  Main Protection Device: {result.main_protection_a:.0f} A",
        f"  Min Transformer Size:  {result.transformer_kva_min} kVA",
        f"  Recommended Transformer: {result.transformer_kva_recommended} kVA",
        "═══════════════════════════════════════════════════════════",
    ]
    result.calculation_summary = "\n".join(summary)

    return result
