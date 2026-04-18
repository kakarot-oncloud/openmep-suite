"""
OpenMEP Panel Schedule Engine
================================
Generates a complete distribution board / panelboard schedule
including circuit breaker sizing, load balancing, and full
engineering summary per BS 7671 / IS 732 / AS/NZS 3000.
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional
from backend.engines.adapters_factory import get_electrical_adapter


# Standard MCB/MCCB ratings available universally
MCB_RATINGS = [6, 10, 13, 16, 20, 25, 32, 40, 50, 63]
MCCB_RATINGS = [63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600]
ACB_RATINGS = [800, 1000, 1250, 1600, 2000, 2500, 3200, 4000]


def _next_protection(ib_a: float) -> float:
    """Select next standard CB rating at or above Ib."""
    all_ratings = sorted(MCB_RATINGS + MCCB_RATINGS + ACB_RATINGS)
    for r in all_ratings:
        if r >= ib_a:
            return float(r)
    return round(ib_a * 1.25 / 100) * 100


@dataclass
class CircuitItem:
    circuit_no: str = ""
    description: str = ""
    load_kw: float = 0.0
    power_factor: float = 0.85
    demand_factor: float = 1.0
    phases: int = 1               # 1 or 3
    circuit_type: str = "power"   # 'power', 'lighting', 'motor', 'hvac'
    cable_type: str = "XLPE_CU"
    installation_method: str = "C"
    cable_length_m: float = 30.0
    space_reserved: bool = False  # Space (no load) in panel


@dataclass
class CircuitResult:
    circuit_no: str = ""
    description: str = ""
    load_kw: float = 0.0
    demand_kw: float = 0.0
    demand_kva: float = 0.0
    current_a: float = 0.0
    protection_a: float = 0.0
    cable_size_mm2: float = 0.0
    vd_percent: float = 0.0
    phases: int = 1
    space_reserved: bool = False
    compliant: bool = True
    notes: str = ""


@dataclass
class PanelScheduleInput:
    region: str = "gcc"
    sub_region: str = ""

    panel_name: str = "Distribution Board DB-01"
    panel_reference: str = "DB-01"
    location: str = ""
    fed_from: str = "MLVDB"
    supply_voltage_lv: float = 400.0
    incoming_cable_size_mm2: float = 150.0

    circuits: List[CircuitItem] = field(default_factory=list)

    future_spare_pct: float = 20.0    # Spare capacity %
    panel_kva_limit: Optional[float] = None   # If incomer is rated

    project_name: str = ""
    engineer: str = ""
    drawing_ref: str = ""


@dataclass
class PanelScheduleResult:
    status: str = "success"
    region: str = ""
    standard: str = ""

    panel_name: str = ""
    panel_reference: str = ""

    # Circuits
    circuits: List[CircuitResult] = field(default_factory=list)
    num_circuits: int = 0
    num_ways: int = 0         # Including spares

    # Load summary
    total_connected_kw: float = 0.0
    total_demand_kw: float = 0.0
    total_demand_kva: float = 0.0
    overall_pf: float = 0.0
    incomer_current_a: float = 0.0
    incomer_protection_a: float = 0.0

    # Phase balancing (for 3-phase panels with 1-phase circuits)
    phase_a_kw: float = 0.0
    phase_b_kw: float = 0.0
    phase_c_kw: float = 0.0
    phase_imbalance_pct: float = 0.0
    phase_balanced: bool = True

    # Spare capacity
    spare_pct: float = 0.0
    compliant: bool = True

    summary: str = ""


def calculate_panel_schedule(inp: PanelScheduleInput) -> PanelScheduleResult:
    """Generate a full distribution board / panelboard schedule."""

    result = PanelScheduleResult(region=inp.region)
    adapter = get_electrical_adapter(inp.region, inp.sub_region)
    result.standard = adapter.wiring_standard
    result.panel_name = inp.panel_name
    result.panel_reference = inp.panel_reference

    sqrt3 = 3 ** 0.5
    supply_v_3ph = inp.supply_voltage_lv
    supply_v_1ph = inp.supply_voltage_lv / sqrt3

    total_kw = 0.0
    total_kvar = 0.0
    total_connected = 0.0

    # Phase tracking for balancing
    phase_kw = [0.0, 0.0, 0.0]  # A, B, C
    phase_idx = 0   # next phase to assign for 1-phase circuits

    circuit_results = []

    for cir in inp.circuits:
        cr = CircuitResult(
            circuit_no=cir.circuit_no,
            description=cir.description,
            load_kw=cir.load_kw,
            phases=cir.phases,
            space_reserved=cir.space_reserved,
        )

        if cir.space_reserved or cir.load_kw <= 0:
            cr.notes = "Space reserved"
            circuit_results.append(cr)
            continue

        demand_kw = cir.load_kw * cir.demand_factor
        pf = max(0.1, min(1.0, cir.power_factor))
        phi = math.acos(pf)
        demand_kva = demand_kw / pf
        demand_kvar = demand_kw * math.tan(phi)

        # Design current
        if cir.phases == 3:
            ib = (demand_kva * 1000) / (sqrt3 * supply_v_3ph)
            v = supply_v_3ph
        else:
            ib = (demand_kva * 1000) / supply_v_1ph
            v = supply_v_1ph

        # Cable size selection via adapter
        standard_sizes = adapter.get_standard_cable_sizes()
        selected_size = standard_sizes[0]
        for size in standard_sizes:
            it = adapter.get_current_rating(cir.cable_type, cir.installation_method, size)
            if it >= ib:
                selected_size = size
                break

        # Voltage drop check
        vd_mv_am = adapter.get_voltage_drop_mv_am(cir.cable_type, selected_size, cir.phases)
        vd_v = (vd_mv_am * ib * cir.cable_length_m) / 1000
        vd_pct = (vd_v / v) * 100
        vd_limit = adapter.get_voltage_drop_limit(cir.circuit_type)

        # Upsize cable if VD exceeds limit
        if vd_pct > vd_limit and len(standard_sizes) > 1:
            for size in standard_sizes:
                if size <= selected_size:
                    continue
                vd_mv_am2 = adapter.get_voltage_drop_mv_am(cir.cable_type, size, cir.phases)
                vd_v2 = (vd_mv_am2 * ib * cir.cable_length_m) / 1000
                vd_pct2 = (vd_v2 / v) * 100
                if vd_pct2 <= vd_limit:
                    selected_size = size
                    vd_pct = vd_pct2
                    break

        protection = _next_protection(ib)

        cr.demand_kw = round(demand_kw, 3)
        cr.demand_kva = round(demand_kva, 3)
        cr.current_a = round(ib, 2)
        cr.protection_a = protection
        cr.cable_size_mm2 = float(selected_size)
        cr.vd_percent = round(float(vd_pct), 2)
        cr.compliant = bool(vd_pct <= vd_limit)

        # Phase assignment for 1-phase circuits
        if cir.phases == 1:
            phase_kw[phase_idx % 3] += demand_kw
            phase_idx += 1
        else:
            for i in range(3):
                phase_kw[i] += demand_kw / 3

        total_kw += demand_kw
        total_kvar += demand_kvar
        total_connected += cir.load_kw
        circuit_results.append(cr)

    result.circuits = circuit_results
    result.num_circuits = len([c for c in circuit_results if not c.space_reserved])
    result.num_ways = len(circuit_results)

    result.total_connected_kw = round(total_connected, 2)
    result.total_demand_kw = round(total_kw, 2)
    total_kva = math.sqrt(total_kw**2 + total_kvar**2) if (total_kw**2 + total_kvar**2) > 0 else 0
    result.total_demand_kva = round(total_kva, 2)
    result.overall_pf = round(total_kw / total_kva, 4) if total_kva > 0 else 1.0

    # Incomer
    incomer_i = (total_kva * 1000) / (sqrt3 * supply_v_3ph) if total_kva > 0 else 0
    result.incomer_current_a = round(incomer_i, 2)
    result.incomer_protection_a = _next_protection(incomer_i)

    # Phase imbalance
    if max(phase_kw) > 0:
        avg = sum(phase_kw) / 3
        max_dev = max(abs(p - avg) for p in phase_kw)
        imbalance = (max_dev / avg * 100) if avg > 0 else 0
    else:
        imbalance = 0
    result.phase_a_kw = round(phase_kw[0], 2)
    result.phase_b_kw = round(phase_kw[1], 2)
    result.phase_c_kw = round(phase_kw[2], 2)
    result.phase_imbalance_pct = round(imbalance, 1)
    result.phase_balanced = bool(imbalance <= 10.0)  # <10% considered balanced

    # Spare capacity
    if inp.panel_kva_limit:
        result.spare_pct = round((1 - total_kva / inp.panel_kva_limit) * 100, 1)
    else:
        result.spare_pct = round(inp.future_spare_pct, 1)
    result.compliant = bool(all(c.compliant for c in circuit_results if not c.space_reserved))

    result.summary = _build_summary(inp, result)
    return result


def _build_summary(inp: PanelScheduleInput, r: PanelScheduleResult) -> str:
    lines = [
        f"=== DISTRIBUTION BOARD SCHEDULE: {r.panel_name} ===",
        f"Standard: {r.standard}",
        f"Project: {inp.project_name}  |  Engineer: {inp.engineer}  |  Ref: {inp.drawing_ref}",
        "",
        "--- INCOMER ---",
        f"Fed From: {inp.fed_from}",
        f"Total Demand: {r.total_demand_kw:.1f} kW / {r.total_demand_kva:.1f} kVA",
        f"Overall PF: {r.overall_pf:.3f}",
        f"Incomer Current: {r.incomer_current_a:.1f} A",
        f"Incomer Protection: {r.incomer_protection_a:.0f} A",
        "",
        "--- PHASE BALANCING ---",
        f"Phase A: {r.phase_a_kw:.1f} kW",
        f"Phase B: {r.phase_b_kw:.1f} kW",
        f"Phase C: {r.phase_c_kw:.1f} kW",
        f"Imbalance: {r.phase_imbalance_pct:.1f}%  ({'OK' if r.phase_balanced else 'REBALANCE REQUIRED'})",
        "",
        f"Circuits: {r.num_circuits} active + {r.num_ways - r.num_circuits} spare = {r.num_ways} ways",
        f"Compliance: {'PASS' if r.compliant else 'FAIL — check VD on flagged circuits'}",
    ]
    return "\n".join(lines)
