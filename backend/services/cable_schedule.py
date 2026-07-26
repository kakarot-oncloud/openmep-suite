"""
Batch cable-schedule sizing service.

Sizes a list of circuits in one call, applying a shared project *design basis*
so common assumptions (region, ambient, power factor, default cable type and
installation method) are entered once and inherited by every circuit. Returns
both per-circuit results and a flat table ready for CSV / Excel export.

Region-specific installation-method resolution is handled inside the adapters
(``resolve_installation_method``), so generic method codes never crash.
"""

from typing import Any

from backend.engines.electrical.cable_sizing import CableSizingInput, calculate_cable_sizing
from backend.models.project import BatchCircuit, DesignBasis

SCHEDULE_COLUMNS = [
    "Ref", "Description", "Load (kW)", "PF", "Phases", "Length (m)",
    "Ib (A)", "Cable (mm²)", "Cable Type", "Method", "VD (%)", "Compliant", "Warnings",
]


def size_circuit(basis: DesignBasis, circ: BatchCircuit) -> dict[str, Any]:
    """Size a single circuit, inheriting any unset values from the design basis."""
    inp = CableSizingInput(
        region=basis.region,
        sub_region=basis.sub_region,
        load_kw=circ.load_kw,
        power_factor=circ.power_factor if circ.power_factor is not None else basis.power_factor,
        phases=circ.phases,
        cable_type=circ.cable_type or basis.default_cable_type,
        installation_method=circ.installation_method or basis.default_installation_method,
        cable_length_m=circ.cable_length_m,
        ambient_temp_c=circ.ambient_temp_c if circ.ambient_temp_c is not None else basis.ambient_temp_c,
        circuit_type=circ.circuit_type,
        demand_factor=basis.safety_factor if basis.safety_factor <= 1.0 else 1.0,
        circuit_from=circ.circuit_ref,
        description=circ.description,
    )
    res = calculate_cable_sizing(inp)
    return {
        "circuit_ref": circ.circuit_ref,
        "description": circ.description,
        "load_kw": res.load_kw,
        "power_factor": res.power_factor,
        "phases": res.phases,
        "cable_length_m": res.cable_length_m,
        "design_current_ib_a": res.design_current_ib_a,
        "selected_size_mm2": res.selected_size_mm2,
        "cable_type": res.cable_type,
        "installation_method": res.installation_method,
        "voltage_drop_pct": res.voltage_drop_pct,
        # Coerce to native bool — comparisons involving numpy correction factors
        # can yield numpy.bool_, which is not JSON-serialisable by pydantic.
        "overall_compliant": bool(res.overall_compliant),
        "warnings": res.warnings,
        "standard": res.standard,
    }


def _row(r: dict[str, Any]) -> list[Any]:
    return [
        r["circuit_ref"],
        r["description"],
        r["load_kw"],
        r["power_factor"],
        r["phases"],
        r["cable_length_m"],
        r["design_current_ib_a"],
        r["selected_size_mm2"],
        r["cable_type"],
        r["installation_method"],
        r["voltage_drop_pct"],
        "Yes" if r["overall_compliant"] else "No",
        " | ".join(w.lstrip("⚠️ ").strip() for w in r["warnings"]),
    ]


def size_schedule(basis: DesignBasis, circuits: list[BatchCircuit]) -> dict[str, Any]:
    """Size every circuit and return per-circuit results plus an export table."""
    results = [size_circuit(basis, c) for c in circuits]
    rows = [_row(r) for r in results]
    non_compliant = sum(1 for r in results if not r["overall_compliant"])
    return {
        "region": basis.region,
        "sub_region": basis.sub_region,
        "circuit_count": len(results),
        "non_compliant_count": non_compliant,
        "all_compliant": non_compliant == 0,
        "circuits": results,
        "table": {"columns": SCHEDULE_COLUMNS, "rows": rows},
    }
