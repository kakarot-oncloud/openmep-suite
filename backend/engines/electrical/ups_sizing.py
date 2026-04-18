"""
OpenMEP UPS Sizing Engine
===========================
Sizes an Uninterruptible Power Supply (UPS) from a critical load schedule.
Outputs: kVA rating, autonomy verification, battery Ah, charger sizing.

Standards: IEC 62040-1/3, IEEE 446, BS 6290 / regional adaptations.
Regions: GCC / Europe / India / Australia.
"""

import math
from dataclasses import dataclass, field
from typing import List
from backend.engines.adapters_factory import get_electrical_adapter


# Standard UPS ratings (kVA) — typical 3-phase online double-conversion
STANDARD_UPS_KVA = [
    1, 2, 3, 5, 6, 8, 10, 15, 20, 30, 40, 60, 80, 100, 120, 160, 200,
    250, 300, 400, 500, 600, 800, 1000, 1200, 1600, 2000, 2500, 3000,
]

# Battery technology characteristics
BATTERY_TECH = {
    "VRLA_AGM": {
        "cell_voltage": 2.0,       # V per cell (discharge mid)
        "cells_per_12v": 6,
        "efficiency": 0.92,
        "depth_of_discharge": 0.80,
        "typical_temp_c": 25.0,
        "standard": "IEC 60896-21",
        "description": "Valve Regulated Lead Acid — AGM (standard UPS)",
    },
    "VRLA_GEL": {
        "cell_voltage": 2.0,
        "cells_per_12v": 6,
        "efficiency": 0.90,
        "depth_of_discharge": 0.80,
        "typical_temp_c": 25.0,
        "standard": "IEC 60896-21",
        "description": "Valve Regulated Lead Acid — Gel",
    },
    "LI_ION": {
        "cell_voltage": 3.6,
        "cells_per_12v": None,  # LiIon uses custom battery modules
        "efficiency": 0.96,
        "depth_of_discharge": 0.90,
        "typical_temp_c": 25.0,
        "standard": "IEC 62133",
        "description": "Lithium Ion — LFP or NMC",
    },
}

# Regional standards and installation notes
REGIONAL_UPS = {
    "gcc": {
        "standard": "IEC 62040-1 / IEC 62040-3 / BS 6290",
        "note": "GCC: Data centres often require N+1 redundancy. DEWA: 50Hz. "
                "Battery room ventilation per BS 6290.",
        "autonomy_min_min": 10,
    },
    "europe": {
        "standard": "IEC 62040-1 / IEC 62040-3 / EN 50171",
        "note": "EU: EN 50171 for central battery systems. BS 6290 for lead-acid rooms. "
                "CE marking required.",
        "autonomy_min_min": 10,
    },
    "india": {
        "standard": "IS 1885 / IEC 62040-1 / IS 16282",
        "note": "India: IS 16282 for UPS systems. NBC 2016 recommends min 30 min autonomy "
                "for critical healthcare loads.",
        "autonomy_min_min": 30,
    },
    "australia": {
        "standard": "AS/NZS 62040.1 / AS 3011",
        "note": "Australia: AS 3011 for secondary batteries. Min 10 min for office, "
                "60 min recommended for data centres.",
        "autonomy_min_min": 10,
    },
}


@dataclass
class UPSLoad:
    description: str = ""
    kva: float = 0.0
    power_factor: float = 0.9
    quantity: int = 1
    is_critical: bool = True    # False = nice-to-have, excluded if overloaded


@dataclass
class UPSSizingInput:
    region: str = "gcc"
    sub_region: str = ""

    loads: List[UPSLoad] = field(default_factory=list)

    # System requirements
    required_autonomy_min: int = 15          # Backup time in minutes
    input_voltage_v: int = 400              # UPS input voltage
    output_voltage_v: int = 400             # UPS output voltage
    phases: int = 3
    frequency_hz: int = 50

    # Battery
    battery_technology: str = "VRLA_AGM"   # 'VRLA_AGM', 'VRLA_GEL', 'LI_ION'
    battery_voltage_dc: float = 240.0       # Battery bank nominal voltage
    redundancy: str = "N"                   # 'N', 'N+1', '2N'

    # Design margins
    future_expansion_pct: float = 20.0
    efficiency_assumption: float = 0.92     # UPS conversion efficiency
    power_factor_ups: float = 0.9           # UPS rated power factor

    project_name: str = ""
    location: str = ""


@dataclass
class UPSSizingResult:
    status: str = "success"
    region: str = ""
    standard: str = ""

    # Load summary
    total_load_kva: float = 0.0
    total_load_kw: float = 0.0
    weighted_pf: float = 0.0

    # UPS selection
    design_kva: float = 0.0
    selected_kva: float = 0.0
    selected_kw: float = 0.0
    num_ups_units: int = 1
    redundancy: str = "N"
    loading_pct: float = 0.0

    # Battery
    battery_technology: str = ""
    battery_voltage_dc: float = 0.0
    battery_capacity_ah: float = 0.0
    num_battery_strings: int = 1
    num_cells_per_string: int = 0
    battery_room_note: str = ""

    # Charger
    charger_current_a: float = 0.0
    recharge_time_h: float = 0.0    # Time to recharge from 0% to 100% (10hr rate)

    # Autonomy verification
    required_autonomy_min: int = 15
    achievable_autonomy_min: float = 0.0
    autonomy_ok: bool = True

    # Compliance
    regional_min_autonomy_min: int = 10
    compliant: bool = True
    note: str = ""

    summary: str = ""


def _next_standard_ups(kva: float) -> float:
    for s in STANDARD_UPS_KVA:
        if s >= kva:
            return float(s)
    return round(kva * 1.1 / 100) * 100


def calculate_ups_sizing(inp: UPSSizingInput) -> UPSSizingResult:
    """Size a UPS system from a critical load schedule per IEC 62040."""

    result = UPSSizingResult(region=inp.region, redundancy=inp.redundancy)
    regional = REGIONAL_UPS.get(inp.region, REGIONAL_UPS["gcc"])
    get_electrical_adapter(inp.region, inp.sub_region)
    result.standard = regional["standard"]
    result.note = regional["note"]
    result.regional_min_autonomy_min = regional["autonomy_min_min"]

    # ── Load analysis ──────────────────────────────────────────────────────
    total_kva = 0.0
    total_kw = 0.0
    for ld in inp.loads:
        kva = ld.kva * ld.quantity
        kw = kva * ld.power_factor
        total_kva += kva
        total_kw += kw

    weighted_pf = total_kw / total_kva if total_kva > 0 else 0.9
    result.total_load_kva = round(total_kva, 3)
    result.total_load_kw = round(total_kw, 3)
    result.weighted_pf = round(weighted_pf, 4)

    # ── Design kVA with expansion margin ──────────────────────────────────
    design_kva = total_kva * (1 + inp.future_expansion_pct / 100)
    result.design_kva = round(design_kva, 2)

    # UPS count based on redundancy
    if inp.redundancy == "2N":
        num_units = 2
    elif inp.redundancy == "N+1":
        num_units = 2   # will size each unit at N+1
    else:
        num_units = 1

    unit_kva = design_kva / (num_units - (1 if inp.redundancy == "N+1" else 0)) if num_units > 1 else design_kva
    selected_kva_per_unit = _next_standard_ups(unit_kva)
    total_selected_kva = selected_kva_per_unit * num_units

    result.selected_kva = selected_kva_per_unit
    result.selected_kw = round(selected_kva_per_unit * inp.power_factor_ups, 2)
    result.num_ups_units = num_units
    result.loading_pct = round(total_kva / total_selected_kva * 100, 1)

    # ── Battery sizing ─────────────────────────────────────────────────────
    batt_tech = BATTERY_TECH.get(inp.battery_technology, BATTERY_TECH["VRLA_AGM"])
    result.battery_technology = batt_tech["description"]
    result.battery_voltage_dc = inp.battery_voltage_dc

    # Power required from battery = UPS output / efficiency
    battery_power_kw = total_kw / inp.efficiency_assumption
    battery_power_w = battery_power_kw * 1000

    # Ah required: E = P × t / V_battery
    t_hours = inp.required_autonomy_min / 60.0
    raw_ah = (battery_power_w * t_hours) / (inp.battery_voltage_dc * batt_tech["depth_of_discharge"])
    # Add 10% for temperature and aging derating
    design_ah = raw_ah * 1.15
    result.battery_capacity_ah = round(design_ah, 0)

    # Number of cells per string (VRLA: 2V cells)
    if inp.battery_technology in ("VRLA_AGM", "VRLA_GEL"):
        cells = int(math.ceil(inp.battery_voltage_dc / batt_tech["cell_voltage"]))
        result.num_cells_per_string = cells
        result.num_battery_strings = 1   # Can parallel for Ah
        result.battery_room_note = f"{cells} × 2V cells in series ({inp.battery_voltage_dc:.0f}V string)"
    else:
        result.battery_room_note = "LiIon modules — consult manufacturer for string configuration"

    # Achievable autonomy at full load
    achievable = (design_ah * inp.battery_voltage_dc * batt_tech["depth_of_discharge"] / battery_power_w) * 60
    result.achievable_autonomy_min = round(achievable, 1)
    result.required_autonomy_min = inp.required_autonomy_min
    result.autonomy_ok = achievable >= inp.required_autonomy_min

    # ── Charger sizing ─────────────────────────────────────────────────────
    # Recharge from 0% to 100% in ~10 hours (C10 rate)
    charger_a = design_ah / 10.0  # A at battery voltage
    result.charger_current_a = round(charger_a, 2)
    result.recharge_time_h = round(design_ah / charger_a, 1)

    result.compliant = achievable >= regional["autonomy_min_min"]
    result.summary = _build_summary(inp, result)
    return result


def _build_summary(inp: UPSSizingInput, r: UPSSizingResult) -> str:
    lines = [
        "=== UPS SIZING CALCULATION ===",
        f"Standard: {r.standard}",
        f"Project: {inp.project_name}  |  Location: {inp.location}",
        "",
        "--- LOAD ---",
        f"Total Load: {r.total_load_kva:.2f} kVA / {r.total_load_kw:.2f} kW",
        f"Weighted PF: {r.weighted_pf:.3f}",
        f"Design kVA (with {inp.future_expansion_pct:.0f}% expansion): {r.design_kva:.2f} kVA",
        "",
        "--- UPS SELECTION ---",
        f"Redundancy: {r.redundancy}",
        f"Selected: {r.num_ups_units} × {r.selected_kva:.0f} kVA UPS",
        f"Unit Rating: {r.selected_kva:.0f} kVA / {r.selected_kw:.0f} kW @ {inp.power_factor_ups} PF",
        f"Loading: {r.loading_pct:.1f}%",
        "",
        "--- BATTERY ---",
        f"Technology: {r.battery_technology}",
        f"Battery Voltage: {r.battery_voltage_dc:.0f} V DC",
        f"Capacity Required: {r.battery_capacity_ah:.0f} Ah",
        f"String Config: {r.battery_room_note}",
        f"Required Autonomy: {r.required_autonomy_min} min",
        f"Achievable Autonomy: {r.achievable_autonomy_min:.1f} min  ({'OK' if r.autonomy_ok else 'INSUFFICIENT'})",
        "",
        "--- CHARGER ---",
        f"Charger Current: {r.charger_current_a:.1f} A (C10 rate)",
        f"Recharge Time: {r.recharge_time_h:.1f} hours (0→100%)",
        "",
        "--- COMPLIANCE ---",
        f"Regional Min Autonomy: {r.regional_min_autonomy_min} min",
        f"Compliant: {'YES' if r.compliant else 'NO'}",
        r.note,
    ]
    return "\n".join(lines)
