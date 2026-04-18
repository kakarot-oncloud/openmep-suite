"""
Short Circuit Analysis Engine
Calculates maximum and minimum prospective short circuit currents.
Methods: impedance method (IEC 60909 / BS 7671 / IS 13234 / AS 3000)
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class ShortCircuitInput:
    region: str = "gcc"
    transformer_kva: float = 1000.0
    transformer_impedance_pct: float = 5.5
    lv_voltage: float = 400.0
    cable_type: str = "XLPE_CU"
    cable_size_mm2: float = 150.0
    cable_length_m: float = 100.0
    cable_resistivity: float = 0.0193  # Ω·mm²/m for copper at 90°C
    upstream_fault_level_ka: Optional[float] = None


@dataclass
class ShortCircuitResult:
    transformer_kva: float = 0.0
    transformer_impedance_pct: float = 0.0
    lv_voltage: float = 0.0

    # Transformer LV terminals
    isc_tx_3ph_ka: float = 0.0
    isc_tx_1ph_ka: float = 0.0

    # After cable
    isc_end_3ph_ka: float = 0.0
    isc_end_1ph_ka: float = 0.0

    # Minimum fault (for earth fault, end-of-run)
    ief_min_ka: float = 0.0

    # Cable thermal check
    cable_size_mm2: float = 0.0
    cable_length_m: float = 0.0
    max_fault_duration_s: float = 0.0
    min_cpc_adiabatic_mm2: float = 0.0

    summary: str = ""


def calculate_short_circuit(inp: ShortCircuitInput) -> ShortCircuitResult:
    """
    Calculate prospective short circuit current by impedance method (IEC 60909).
    """
    res = ShortCircuitResult(
        transformer_kva=inp.transformer_kva,
        transformer_impedance_pct=inp.transformer_impedance_pct,
        lv_voltage=inp.lv_voltage,
        cable_size_mm2=inp.cable_size_mm2,
        cable_length_m=inp.cable_length_m,
    )

    # Transformer source impedance (referred to LV)
    s_tx = inp.transformer_kva * 1000  # VA
    v_base = inp.lv_voltage
    z_base = v_base**2 / s_tx
    z_tx = (inp.transformer_impedance_pct / 100.0) * z_base  # Ω

    # HV supply impedance (if upstream fault level given)
    z_source = 0.0
    if inp.upstream_fault_level_ka:
        z_source = v_base / (math.sqrt(3) * inp.upstream_fault_level_ka * 1000)

    z_total_source = z_tx + z_source

    # 3-phase fault at LV terminals
    isc_3ph_tx = v_base / (math.sqrt(3) * z_total_source)
    res.isc_tx_3ph_ka = round(isc_3ph_tx / 1000, 2)

    # 1-phase fault at LV terminals (approx: 0.87 × 3-phase for TN systems)
    res.isc_tx_1ph_ka = round(isc_3ph_tx * 0.87 / 1000, 2)

    # Cable impedance (phase + neutral/CPC loop, worst case double length)
    rho = inp.cable_resistivity  # Ω·mm²/m at operating temp
    r_cable_per_m = rho / inp.cable_size_mm2
    r_total = r_cable_per_m * inp.cable_length_m * 2  # line + return

    # 3-phase fault at end of cable
    z_end = math.sqrt(z_total_source**2 + r_total**2)
    isc_3ph_end = v_base / (math.sqrt(3) * z_end)
    res.isc_end_3ph_ka = round(isc_3ph_end / 1000, 2)
    res.isc_end_1ph_ka = round(isc_3ph_end * 0.87 / 1000, 2)

    # Minimum earth fault current (earth loop: line + CPC at higher resistance)
    # Earth CPC typically smaller — assume 50% cross section (1.5× resistance)
    r_cpc_per_m = rho * 1.5 / inp.cable_size_mm2
    r_loop = r_cable_per_m * inp.cable_length_m + r_cpc_per_m * inp.cable_length_m
    z_fault_loop = math.sqrt(z_total_source**2 + r_loop**2)
    ief_min = (v_base / math.sqrt(3)) / z_fault_loop
    res.ief_min_ka = round(ief_min / 1000, 3)

    # Adiabatic check on CPC (max duration before exceeding thermal limit)
    # t_max = (k × S)² / I²   where k=143 for XLPE-Cu
    k = 143
    # For the selected cable as CPC proxy:
    from backend.engines.adapters_factory import get_electrical_adapter
    adapter = get_electrical_adapter(inp.region)
    earth_mm2 = adapter.get_earthing_conductor_size(inp.cable_size_mm2)
    i_fault_a = isc_3ph_end
    if i_fault_a > 0:
        t_max = ((k * earth_mm2) / i_fault_a)**2
    else:
        t_max = 999.0
    res.max_fault_duration_s = round(min(t_max, 5.0), 3)

    s_min_adiabatic = math.sqrt(isc_3ph_end**2 * 0.4) / k
    res.min_cpc_adiabatic_mm2 = round(s_min_adiabatic, 1)

    # Summary
    lines = [
        "═══════════════════════════════════════════════════════════",
        "  SHORT CIRCUIT ANALYSIS  (IEC 60909 Impedance Method)",
        "───────────────────────────────────────────────────────────",
        f"  Transformer: {inp.transformer_kva} kVA, Z = {inp.transformer_impedance_pct}%",
        f"  LV Voltage:  {inp.lv_voltage} V",
        f"  Cable: {inp.cable_size_mm2}mm² × {inp.cable_length_m}m  (ρ = {rho} Ω·mm²/m)",
        "───────────────────────────────────────────────────────────",
        "  AT LV TERMINALS:",
        f"    Isc (3-phase): {res.isc_tx_3ph_ka} kA",
        f"    Isc (1-phase): {res.isc_tx_1ph_ka} kA",
        "  AT END OF CABLE:",
        f"    Isc (3-phase): {res.isc_end_3ph_ka} kA",
        f"    Isc (1-phase): {res.isc_end_1ph_ka} kA",
        f"    Min Earth Fault Current: {res.ief_min_ka} kA",
        "───────────────────────────────────────────────────────────",
        f"  CPC Thermal Check: Max fault duration = {res.max_fault_duration_s} s",
        f"  Min CPC (adiabatic, t=0.4s): {res.min_cpc_adiabatic_mm2} mm²",
        "═══════════════════════════════════════════════════════════",
    ]
    res.summary = "\n".join(lines)

    return res
