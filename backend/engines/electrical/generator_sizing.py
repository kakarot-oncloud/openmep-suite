"""
OpenMEP Generator Sizing Engine
=================================
Calculates standby / prime rated generator capacity from load schedule.
Applies regional derating for altitude and temperature per ISO 8528.
Supports: GCC (Cummins/FG Wilson practice), Europe (BS 7671),
          India (IS 4722 / CPWD), Australia (AS 3010).
"""

import math
from dataclasses import dataclass, field
from typing import List
from backend.engines.adapters_factory import get_electrical_adapter


# ISO 8528-1 derating: per 100m above 1000m ASL → 1% active, 2% reactive
# Per 5.5°C above 25°C → 1% active power derating
# GCC practice: site altitude typically <50m, but 45-50°C ambient
ALTITUDE_DERATING_PER_100M = 0.01    # 1% per 100m above 1000m ASL
TEMP_DERATING_PER_5C = 0.01          # 1% per 5°C above 25°C

# Motor starting kVA multipliers for transient analysis
MOTOR_STARTING_FACTORS = {
    "DOL": 6.0,     # Direct on line — highest inrush
    "STAR_DELTA": 2.5,
    "VFD": 1.5,     # Variable frequency drive
    "SOFT_STARTER": 2.0,
    "CAPACITOR": 2.5,
}

# Standard generator ratings (kVA) — typical Cummins/FG Wilson/Caterpillar
STANDARD_GEN_KVA = [
    20, 25, 30, 38, 45, 60, 75, 100, 125, 150, 175, 200, 250, 275, 300,
    350, 400, 450, 500, 600, 650, 750, 850, 1000, 1100, 1250, 1500, 1750,
    2000, 2250, 2500, 2750, 3000, 3500, 4000
]

# Typical subtransient reactance Xd'' for generators
TYPICAL_XD_PRIME_PRIME = 0.12  # 12% — used for fault calculation

# Regional standards and notes
REGIONAL_NOTES = {
    "gcc": {
        "standard": "ISO 8528 / BS 7671 / IEC 60034",
        "note": "GCC: Derate for 50°C site ambient. Fuel: diesel, LFO. Min 110% rating for emergency.",
        "freq": 50, "pf_rated": 0.8, "oversizing_factor": 1.25,
    },
    "europe": {
        "standard": "ISO 8528 / BS 7671 / EN 12601",
        "note": "UK/EU: IEC 60034 ratings. Part M of Building Regs for fire compliance.",
        "freq": 50, "pf_rated": 0.8, "oversizing_factor": 1.20,
    },
    "india": {
        "standard": "IS 4722 / IS 3043 / CPWD Spec 2019",
        "note": "India: IS 4722 for alternators. CPWD recommends 1.25× load for standby sets.",
        "freq": 50, "pf_rated": 0.8, "oversizing_factor": 1.25,
    },
    "australia": {
        "standard": "ISO 8528 / AS 3010 / AS/NZS 4509",
        "note": "Australia: AS 3010 generator wiring. NCC Section J energy requirements.",
        "freq": 50, "pf_rated": 0.8, "oversizing_factor": 1.20,
    },
}


@dataclass
class GeneratorLoad:
    description: str = ""
    kw: float = 0.0
    power_factor: float = 0.85
    demand_factor: float = 1.0
    load_type: str = "general"      # 'lighting', 'power', 'motor', 'hvac', 'ups'
    starting_method: str = "VFD"    # 'DOL', 'STAR_DELTA', 'VFD', 'SOFT_STARTER'
    is_largest_motor: bool = False


@dataclass
class GeneratorSizingInput:
    region: str = "gcc"
    sub_region: str = ""

    loads: List[GeneratorLoad] = field(default_factory=list)

    # Site conditions
    site_altitude_m: float = 0.0       # Metres above sea level
    ambient_temp_c: float = None        # Site ambient temperature

    # System preferences
    gen_voltage: int = 400             # Generator LV terminal voltage
    phases: int = 3
    frequency_hz: int = 50
    rated_pf: float = 0.8              # Generator nameplate PF (usually 0.8)
    supply_system: str = "standby"     # 'standby', 'prime', 'continuous'

    # Step load policy
    max_voltage_dip_pct: float = 15.0  # Max allowable voltage dip on motor start
    max_freq_dip_hz: float = 2.0       # Max frequency dip on step load

    project_name: str = ""
    description: str = ""


@dataclass
class GeneratorSizingResult:
    status: str = "success"
    region: str = ""
    standard: str = ""
    supply_system: str = ""

    # Load summary
    total_connected_kw: float = 0.0
    total_demand_kw: float = 0.0
    total_demand_kva: float = 0.0
    weighted_pf: float = 0.0

    # Derating
    site_altitude_m: float = 0.0
    site_ambient_c: float = 0.0
    altitude_derating_pct: float = 0.0
    temp_derating_pct: float = 0.0
    total_derating_pct: float = 0.0
    derated_demand_kva: float = 0.0

    # Generator selection
    required_kva_running: float = 0.0
    required_kva_starting: float = 0.0
    design_kva: float = 0.0           # Larger of running / starting
    standard_kva: float = 0.0        # Next standard unit size
    standard_kw: float = 0.0

    # Motor starting
    largest_motor_kw: float = 0.0
    largest_motor_start_kva: float = 0.0
    motor_start_method: str = ""
    step_load_voltage_dip_pct: float = 0.0
    step_load_ok: bool = True

    # Fuel
    fuel_consumption_l_hr: float = 0.0   # At 75% load, litres/hour
    tank_capacity_24h_l: float = 0.0     # 24-hour operational autonomy

    # Fault level
    subtransient_fault_ka: float = 0.0

    note: str = ""
    summary: str = ""


def _next_standard_kva(kva: float) -> float:
    for s in STANDARD_GEN_KVA:
        if s >= kva:
            return float(s)
    return round(kva * 1.1 / 250) * 250


def calculate_generator_sizing(inp: GeneratorSizingInput) -> GeneratorSizingResult:
    """Calculate required standby/prime generator rating from load schedule."""

    result = GeneratorSizingResult(region=inp.region, supply_system=inp.supply_system)
    regional = REGIONAL_NOTES.get(inp.region, REGIONAL_NOTES["gcc"])
    adapter = get_electrical_adapter(inp.region, inp.sub_region)

    result.standard = regional["standard"]
    result.note = regional["note"]

    ambient = inp.ambient_temp_c if inp.ambient_temp_c is not None else adapter.design_ambient_temp_air
    result.site_altitude_m = inp.site_altitude_m
    result.site_ambient_c = ambient

    # ── Load analysis ──────────────────────────────────────────────────────
    total_kw = 0.0
    total_kvar = 0.0
    largest_motor_kw = 0.0
    largest_motor_method = "VFD"

    for ld in inp.loads:
        kw = ld.kw * ld.demand_factor
        pf = max(0.1, min(1.0, ld.power_factor))
        phi = math.acos(pf)
        kvar = kw * math.tan(phi)
        total_kw += kw
        total_kvar += kvar
        if ld.load_type == "motor" and kw > largest_motor_kw:
            largest_motor_kw = kw
            largest_motor_method = ld.starting_method

    total_kva = math.sqrt(total_kw**2 + total_kvar**2) if (total_kw**2 + total_kvar**2) > 0 else 1.0
    weighted_pf = total_kw / total_kva if total_kva > 0 else 0.85

    result.total_demand_kw = round(total_kw, 2)
    result.total_demand_kva = round(total_kva, 2)
    result.weighted_pf = round(weighted_pf, 4)

    # Running kVA at generator rated PF
    running_kva = total_kw / inp.rated_pf

    # ── Derating ──────────────────────────────────────────────────────────
    alt_above_1000 = max(0, inp.site_altitude_m - 1000)
    alt_derating = (alt_above_1000 / 100) * ALTITUDE_DERATING_PER_100M
    temp_above_25 = max(0, ambient - 25)
    temp_derating = (temp_above_25 / 5.0) * TEMP_DERATING_PER_5C
    total_derating = alt_derating + temp_derating

    result.altitude_derating_pct = round(alt_derating * 100, 2)
    result.temp_derating_pct = round(temp_derating * 100, 2)
    result.total_derating_pct = round(total_derating * 100, 2)

    # Derated demand: increase required kVA to compensate for derating
    derated_kva = running_kva / (1 - total_derating) if total_derating < 1 else running_kva * 1.5
    result.derated_demand_kva = round(derated_kva, 2)
    result.required_kva_running = round(derated_kva, 2)

    # ── Motor starting analysis ────────────────────────────────────────────
    start_factor = MOTOR_STARTING_FACTORS.get(largest_motor_method, 2.0)
    largest_motor_kva_start = (largest_motor_kw / 0.85) * start_factor  # assume PF 0.85 for motor
    required_kva_start = (total_kva - largest_motor_kw / 0.85) + largest_motor_kva_start

    result.largest_motor_kw = round(largest_motor_kw, 2)
    result.largest_motor_start_kva = round(largest_motor_kva_start, 2)
    result.motor_start_method = largest_motor_method
    result.required_kva_starting = round(required_kva_start, 2)

    # Voltage dip on step load (approx): ΔV% ≈ (ΔkVA / Gen kVA) × 100 × Xd''
    if derated_kva > 0:
        step_dip = (largest_motor_kva_start / derated_kva) * 100 * TYPICAL_XD_PRIME_PRIME / 0.12
        result.step_load_voltage_dip_pct = round(step_dip, 1)
        result.step_load_ok = step_dip <= inp.max_voltage_dip_pct

    # ── Design kVA = max(running, starting) × oversizing ──────────────────
    base_kva = max(derated_kva, required_kva_start)
    design_kva = base_kva * regional["oversizing_factor"]
    result.design_kva = round(design_kva, 2)

    std_kva = _next_standard_kva(design_kva)
    result.standard_kva = std_kva
    result.standard_kw = round(std_kva * inp.rated_pf, 2)

    # ── Fuel consumption ──────────────────────────────────────────────────
    # Typical diesel consumption at 75% load: ~0.21 L/kWh
    fuel_per_kwh = 0.21
    actual_kw_75 = result.standard_kw * 0.75
    result.fuel_consumption_l_hr = round(actual_kw_75 * fuel_per_kwh, 2)
    result.tank_capacity_24h_l = round(result.fuel_consumption_l_hr * 24 * 1.1, 0)  # +10% reserve

    # ── Fault level ───────────────────────────────────────────────────────
    sqrt3 = 3 ** 0.5
    gen_z_pu = TYPICAL_XD_PRIME_PRIME
    vbase = inp.gen_voltage
    zbase = (vbase**2) / (std_kva * 1000)
    z_ohm = gen_z_pu * zbase
    fault_a = vbase / (sqrt3 * z_ohm) / 1000  # kA
    result.subtransient_fault_ka = round(fault_a, 2)

    result.summary = _build_summary(inp, result)
    return result


def _build_summary(inp: GeneratorSizingInput, r: GeneratorSizingResult) -> str:
    lines = [
        f"=== GENERATOR SIZING CALCULATION ({r.supply_system.upper()}) ===",
        f"Standard: {r.standard}",
        f"Project: {inp.project_name}",
        "",
        "--- SITE CONDITIONS ---",
        f"Site Altitude: {r.site_altitude_m:.0f} m ASL",
        f"Site Ambient: {r.site_ambient_c:.0f}°C",
        f"Altitude Derating: {r.altitude_derating_pct:.1f}%",
        f"Temperature Derating: {r.temp_derating_pct:.1f}%",
        f"Total Derating: {r.total_derating_pct:.1f}%",
        "",
        "--- LOAD SUMMARY ---",
        f"Total Demand (kW): {r.total_demand_kw:.1f} kW",
        f"Total Demand (kVA): {r.total_demand_kva:.1f} kVA",
        f"Weighted PF: {r.weighted_pf:.3f}",
        f"Derated Running kVA: {r.derated_demand_kva:.1f} kVA",
        "",
        "--- MOTOR STARTING ---",
        f"Largest Motor: {r.largest_motor_kw:.1f} kW ({r.motor_start_method})",
        f"Starting kVA: {r.largest_motor_start_kva:.1f} kVA",
        f"Step Load Voltage Dip: {r.step_load_voltage_dip_pct:.1f}% ({'OK' if r.step_load_ok else 'EXCEEDS LIMIT'})",
        "",
        "--- GENERATOR SELECTION ---",
        f"Design kVA: {r.design_kva:.1f} kVA",
        f"Selected Generator: {r.standard_kva:.0f} kVA / {r.standard_kw:.0f} kW @ 0.8 PF",
        f"Subtransient Fault: {r.subtransient_fault_ka:.2f} kA",
        "",
        "--- FUEL ---",
        f"Fuel Consumption @ 75%: {r.fuel_consumption_l_hr:.1f} L/hr",
        f"24-Hour Tank Capacity: {r.tank_capacity_24h_l:.0f} L (incl. 10% reserve)",
        "",
        r.note,
    ]
    return "\n".join(lines)
