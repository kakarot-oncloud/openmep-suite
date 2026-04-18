"""
OpenMEP Power Factor Correction Engine
========================================
Calculates required capacitor bank size to improve power factor
to a target value, per IEC 60831 / BS 7671 / IEEE 1036.

Supports all 4 regions with regional utility tariff penalty thresholds.
"""

import math
from dataclasses import dataclass
from typing import Optional
from backend.engines.adapters_factory import get_electrical_adapter


# Regional PF penalty thresholds (below which utility charges penalty)
REGIONAL_PF_THRESHOLDS = {
    "gcc": {"min_pf": 0.90, "target_pf": 0.95, "tariff_note": "DEWA/ADDC/KAHRAMAA: min PF 0.90, penalty applies below"},
    "europe": {"min_pf": 0.95, "target_pf": 0.98, "tariff_note": "UK/EU: min PF 0.95 for industrial tariffs"},
    "india": {"min_pf": 0.90, "target_pf": 0.95, "tariff_note": "CEA: min PF 0.90; MSEDCL/BESCOM incentive above 0.95"},
    "australia": {"min_pf": 0.90, "target_pf": 0.95, "tariff_note": "AS/NZS 3000: utilities require PF ≥ 0.90"},
}

# Standard capacitor bank sizes (kVAr)
STANDARD_KVAR_STEPS = [2.5, 5, 7.5, 10, 12.5, 15, 20, 25, 30, 40, 50, 60, 75, 100,
                        125, 150, 200, 250, 300, 400, 500, 600, 750, 1000]

# Switching steps for automatic PF correction panels
APFC_STEPS = [10, 12.5, 15, 20, 25, 30, 40, 50, 75, 100]


@dataclass
class PFCorrectionInput:
    region: str = "gcc"
    sub_region: str = ""

    # Load parameters
    active_power_kw: float = 0.0
    existing_pf: float = 0.80
    target_pf: float = 0.95
    supply_voltage_v: Optional[float] = None
    phases: int = 3
    frequency_hz: int = 50

    # System parameters
    num_transformers: int = 1
    transformer_kva: float = 1000.0
    apply_harmonic_derating: bool = False  # Derate for harmonic distortion

    project_name: str = ""
    description: str = ""


@dataclass
class PFCorrectionResult:
    status: str = "success"
    region: str = ""
    standard: str = ""

    # Input summary
    active_power_kw: float = 0.0
    existing_pf: float = 0.0
    target_pf: float = 0.0
    supply_voltage_v: float = 0.0

    # Existing condition
    existing_reactive_kvar: float = 0.0
    existing_apparent_kva: float = 0.0
    existing_current_a: float = 0.0

    # Required correction
    required_correction_kvar: float = 0.0
    standard_bank_kvar: float = 0.0       # Next standard size
    capacitor_current_a: float = 0.0

    # After correction
    corrected_reactive_kvar: float = 0.0
    corrected_apparent_kva: float = 0.0
    corrected_pf: float = 0.0
    corrected_current_a: float = 0.0

    # Current reduction
    current_reduction_a: float = 0.0
    current_reduction_pct: float = 0.0
    cable_saving_pct: float = 0.0

    # APFC panel recommendation
    apfc_steps: int = 0
    apfc_step_kvar: float = 0.0
    apfc_panel_kvar: float = 0.0

    # Utility compliance
    utility_min_pf: float = 0.90
    compliant: bool = True
    tariff_note: str = ""

    # Annual savings estimate
    annual_saving_kwh: float = 0.0
    loss_reduction_kw: float = 0.0

    summary: str = ""


def _next_standard_size(kvar: float) -> float:
    """Return the next standard capacitor bank size ≥ required kVAr."""
    for s in STANDARD_KVAR_STEPS:
        if s >= kvar:
            return s
    return round(kvar * 1.1 / 50) * 50  # Round up to next 50 kVAr


def calculate_pf_correction(inp: PFCorrectionInput) -> PFCorrectionResult:
    """
    Calculate required power factor correction capacitor bank.

    Method per IEC 60831-1:
        Q_c = P × (tan φ₁ − tan φ₂)
    where:
        φ₁ = arccos(existing PF)
        φ₂ = arccos(target PF)
        Q_c = required capacitive reactive power (kVAr)
    """
    result = PFCorrectionResult(region=inp.region)

    adapter = get_electrical_adapter(inp.region, inp.sub_region)
    result.standard = adapter.cable_sizing_standard
    supply_v = inp.supply_voltage_v or (adapter.voltage_lv if inp.phases == 3 else adapter.voltage_phase)
    result.supply_voltage_v = supply_v
    result.active_power_kw = inp.active_power_kw
    result.existing_pf = inp.existing_pf
    result.target_pf = inp.target_pf

    # Existing reactive / apparent power
    phi1 = math.acos(inp.existing_pf)
    phi2 = math.acos(inp.target_pf)
    tan_phi1 = math.tan(phi1)
    tan_phi2 = math.tan(phi2)

    existing_q = inp.active_power_kw * tan_phi1          # kVAr
    existing_s = inp.active_power_kw / inp.existing_pf   # kVA
    inp.active_power_kw / inp.target_pf       # kVA

    result.existing_reactive_kvar = round(existing_q, 2)
    result.existing_apparent_kva = round(existing_s, 2)

    # Current before correction
    sqrt3 = 3 ** 0.5
    if inp.phases == 3:
        existing_i = (existing_s * 1000) / (sqrt3 * supply_v)
    else:
        existing_i = (existing_s * 1000) / supply_v
    result.existing_current_a = round(existing_i, 2)

    # Required capacitor kVAr
    q_c = inp.active_power_kw * (tan_phi1 - tan_phi2)
    result.required_correction_kvar = round(q_c, 2)

    # Harmonic derating (if THD > 10%, derate by 15%)
    if inp.apply_harmonic_derating:
        q_c *= 1.15

    std_bank = _next_standard_size(q_c)
    result.standard_bank_kvar = std_bank

    # Capacitor current
    if inp.phases == 3:
        cap_i = (std_bank * 1000) / (sqrt3 * supply_v)
    else:
        cap_i = (std_bank * 1000) / supply_v
    result.capacitor_current_a = round(cap_i, 2)

    # After correction
    corrected_q = max(0, existing_q - std_bank)
    corrected_s = math.sqrt(inp.active_power_kw**2 + corrected_q**2)
    corrected_pf = inp.active_power_kw / corrected_s if corrected_s > 0 else 1.0
    corrected_pf = min(1.0, corrected_pf)

    result.corrected_reactive_kvar = round(corrected_q, 2)
    result.corrected_apparent_kva = round(corrected_s, 2)
    result.corrected_pf = round(corrected_pf, 4)

    if inp.phases == 3:
        corrected_i = (corrected_s * 1000) / (sqrt3 * supply_v)
    else:
        corrected_i = (corrected_s * 1000) / supply_v
    result.corrected_current_a = round(corrected_i, 2)

    result.current_reduction_a = round(existing_i - corrected_i, 2)
    result.current_reduction_pct = round((existing_i - corrected_i) / existing_i * 100, 1) if existing_i > 0 else 0
    result.cable_saving_pct = round(result.current_reduction_pct, 1)

    # APFC steps recommendation
    num_steps = 1
    step_kvar = std_bank
    for step in APFC_STEPS:
        if std_bank / step >= 6:
            step_kvar = step
            num_steps = int(std_bank / step)
            break
    if num_steps < 4:
        # Minimum 4 steps for APFC panel
        step_kvar = max(10, std_bank / 6)
        step_kvar = _next_standard_size(step_kvar)
        num_steps = max(4, int(std_bank / step_kvar))

    result.apfc_steps = num_steps
    result.apfc_step_kvar = step_kvar
    result.apfc_panel_kvar = round(num_steps * step_kvar, 1)

    # Utility compliance
    regional = REGIONAL_PF_THRESHOLDS.get(inp.region, REGIONAL_PF_THRESHOLDS["gcc"])
    result.utility_min_pf = regional["min_pf"]
    result.tariff_note = regional["tariff_note"]
    result.compliant = corrected_pf >= regional["min_pf"]

    # Estimated transformer loss reduction (I²R loss)
    loss_reduction_kw = 0
    if inp.transformer_kva > 0:
        # Approx transformer copper loss ≈ 1% of kVA
        tx_loss_factor = 0.01
        loss_reduction_kw = (existing_s - corrected_s) * tx_loss_factor
    result.loss_reduction_kw = round(loss_reduction_kw, 2)

    # Annual energy savings (operating 6000 h/year at 0.10 $/kWh — indicative only)
    result.annual_saving_kwh = round(loss_reduction_kw * 6000, 0)

    result.summary = _build_summary(inp, result)
    return result


def _build_summary(inp: PFCorrectionInput, r: PFCorrectionResult) -> str:
    lines = [
        "=== POWER FACTOR CORRECTION CALCULATION ===",
        f"Standard: {r.standard}",
        f"Active Power (P): {r.active_power_kw:.1f} kW",
        f"Existing PF: {r.existing_pf:.3f} | Target PF: {r.target_pf:.3f}",
        "",
        "--- EXISTING CONDITION ---",
        f"Reactive Power (Q1): {r.existing_reactive_kvar:.1f} kVAr",
        f"Apparent Power (S1): {r.existing_apparent_kva:.1f} kVA",
        f"Current (I1): {r.existing_current_a:.1f} A",
        "",
        "--- CORRECTION REQUIRED ---",
        f"Required Q_c: {r.required_correction_kvar:.1f} kVAr  [P × (tan φ₁ − tan φ₂)]",
        f"Standard Bank: {r.standard_bank_kvar:.1f} kVAr  (IEC 60831)",
        f"APFC Panel: {r.apfc_steps} × {r.apfc_step_kvar:.0f} kVAr steps = {r.apfc_panel_kvar:.0f} kVAr total",
        "",
        "--- AFTER CORRECTION ---",
        f"Corrected PF: {r.corrected_pf:.4f}",
        f"Corrected S: {r.corrected_apparent_kva:.1f} kVA",
        f"Corrected Current: {r.corrected_current_a:.1f} A",
        f"Current Reduction: {r.current_reduction_a:.1f} A ({r.current_reduction_pct:.1f}%)",
        "",
        "--- UTILITY COMPLIANCE ---",
        f"Min PF Required: {r.utility_min_pf:.2f}  |  Compliant: {'YES' if r.compliant else 'NO'}",
        f"{r.tariff_note}",
        "",
        f"Loss Reduction: ~{r.loss_reduction_kw:.2f} kW  |  Annual Saving: ~{r.annual_saving_kwh:.0f} kWh",
    ]
    return "\n".join(lines)
