"""
OpenMEP Compliance Checking Route
====================================
Checks a set of MEP calculation results against regional regulatory requirements.
Returns a structured compliance report with pass/fail status for each check.

Disciplines covered:
  - Electrical (cable CCC, voltage drop, earth fault loop)
  - Lighting (illuminance, uniformity, LPD)
  - Mechanical / HVAC (fresh air, ACH, cooling density)
  - Plumbing (velocity, pressure, backflow, legionella)
  - Fire (sprinkler density, pressure, pump test, tank volume)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, List, Optional

router = APIRouter(prefix="/compliance", tags=["Compliance & Standards"])


# ─── Request models ───────────────────────────────────────────────────────────

class CableComplianceCheck(BaseModel):
    circuit_reference: str = ""
    region: str = "gcc"
    sub_region: str = ""
    design_current_a: float = 0.0
    derated_rating_iz_a: float = 0.0
    voltage_drop_pct: float = 0.0
    vd_limit_pct: float = 5.0
    cable_size_mm2: float = 0.0
    earth_size_mm2: float = 0.0


class LightingComplianceCheck(BaseModel):
    region: str = "gcc"
    room_type: str = "office"
    achieved_lux: float = 0.0
    target_lux: float = 500.0
    lpd_w_per_m2: float = 0.0
    lpd_limit_w_per_m2: float = 0.0
    uniformity_ratio: float = 0.0


class MechanicalComplianceCheck(BaseModel):
    region: str = "gcc"
    zone_type: str = "office"
    fresh_air_l_s_person: float = 0.0
    supply_air_ach: float = 0.0
    cooling_w_per_m2: float = 0.0


class PlumbingComplianceCheck(BaseModel):
    region: str = "gcc"
    system_type: str = "cold_water"        # cold_water | hot_water | drainage
    pipe_velocity_m_s: float = 0.0
    design_pressure_bar: float = 0.0
    min_pressure_bar: float = 0.5
    max_pressure_bar: float = 10.0
    storage_temp_c: float = 0.0            # for hot water legionella check
    distribution_temp_c: float = 0.0
    has_backflow_preventer: bool = False
    has_tmax_valve: bool = False


class FireComplianceCheck(BaseModel):
    region: str = "gcc"
    system_type: str = "sprinkler"         # sprinkler | wet_riser | fire_pump | fire_tank
    hazard_class: str = "OH1"
    design_density_mm_min: float = 0.0     # sprinkler application rate
    min_density_mm_min: float = 0.0
    design_pressure_bar: float = 0.0
    min_pressure_bar: float = 0.0
    pump_rated_flow_l_min: float = 0.0
    required_flow_l_min: float = 0.0
    tank_volume_m3: float = 0.0
    required_volume_m3: float = 0.0
    has_duty_standby: bool = False
    has_jockey_pump: bool = False
    last_test_date: Optional[str] = None


class ComplianceReportRequest(BaseModel):
    project_name: str = ""
    project_reference: str = ""
    region: str = "gcc"
    sub_region: str = ""
    discipline: str = "electrical"     # 'electrical', 'mechanical', 'plumbing', 'fire', 'all'

    cable_checks: List[CableComplianceCheck] = []
    lighting_checks: List[LightingComplianceCheck] = []
    mechanical_checks: List[MechanicalComplianceCheck] = []
    plumbing_checks: List[PlumbingComplianceCheck] = []
    fire_checks: List[FireComplianceCheck] = []


# ─── Regional standards reference data ───────────────────────────────────────

LIGHTING_REQUIREMENTS = {
    "gcc": {
        "office": {"min_lux": 500, "uniformity": 0.6, "lpd_limit": 12.0, "standard": "EN 12464-1 / DEWA Green Bldg"},
        "meeting_room": {"min_lux": 300, "uniformity": 0.6, "lpd_limit": 10.0, "standard": "EN 12464-1"},
        "corridor": {"min_lux": 100, "uniformity": 0.4, "lpd_limit": 5.0, "standard": "EN 12464-1"},
        "lobby": {"min_lux": 200, "uniformity": 0.4, "lpd_limit": 8.0, "standard": "EN 12464-1"},
        "warehouse": {"min_lux": 200, "uniformity": 0.4, "lpd_limit": 6.0, "standard": "EN 12464-1"},
        "retail": {"min_lux": 500, "uniformity": 0.6, "lpd_limit": 18.0, "standard": "EN 12464-1"},
        "car_park": {"min_lux": 75, "uniformity": 0.25, "lpd_limit": 3.0, "standard": "EN 12464-1"},
        "general": {"min_lux": 300, "uniformity": 0.5, "lpd_limit": 12.0, "standard": "EN 12464-1"},
    },
    "europe": {
        "office": {"min_lux": 500, "uniformity": 0.6, "lpd_limit": 12.0, "standard": "EN 12464-1:2021"},
        "meeting_room": {"min_lux": 300, "uniformity": 0.6, "lpd_limit": 10.0, "standard": "EN 12464-1:2021"},
        "corridor": {"min_lux": 100, "uniformity": 0.4, "lpd_limit": 5.0, "standard": "EN 12464-1:2021"},
        "car_park": {"min_lux": 75, "uniformity": 0.25, "lpd_limit": 3.0, "standard": "EN 12464-1:2021"},
        "general": {"min_lux": 300, "uniformity": 0.5, "lpd_limit": 12.0, "standard": "EN 12464-1:2021"},
    },
    "india": {
        "office": {"min_lux": 500, "uniformity": 0.6, "lpd_limit": 12.0, "standard": "NBC 2016 / SP 72"},
        "meeting_room": {"min_lux": 300, "uniformity": 0.6, "lpd_limit": 10.0, "standard": "NBC 2016"},
        "corridor": {"min_lux": 100, "uniformity": 0.4, "lpd_limit": 5.0, "standard": "NBC 2016"},
        "general": {"min_lux": 300, "uniformity": 0.5, "lpd_limit": 10.0, "standard": "NBC 2016"},
    },
    "australia": {
        "office": {"min_lux": 400, "uniformity": 0.6, "lpd_limit": 12.0, "standard": "AS 1680.1 / NCC Section J"},
        "meeting_room": {"min_lux": 320, "uniformity": 0.6, "lpd_limit": 10.0, "standard": "AS 1680.1"},
        "corridor": {"min_lux": 80, "uniformity": 0.4, "lpd_limit": 5.0, "standard": "AS 1680.1"},
        "general": {"min_lux": 320, "uniformity": 0.5, "lpd_limit": 12.0, "standard": "AS 1680.1"},
    },
}

VENTILATION_REQUIREMENTS = {
    "gcc": {
        "office": {"min_fresh_air_l_s": 10, "min_ach": 4, "standard": "ASHRAE 62.1 / DEWA"},
        "meeting_room": {"min_fresh_air_l_s": 10, "min_ach": 6, "standard": "ASHRAE 62.1"},
        "data_centre": {"min_fresh_air_l_s": 0, "min_ach": 0, "standard": "ASHRAE TC 9.9"},
        "general": {"min_fresh_air_l_s": 8, "min_ach": 4, "standard": "ASHRAE 62.1"},
    },
    "europe": {
        "office": {"min_fresh_air_l_s": 10, "min_ach": 3, "standard": "EN 16798-1"},
        "meeting_room": {"min_fresh_air_l_s": 10, "min_ach": 6, "standard": "EN 16798-1"},
        "general": {"min_fresh_air_l_s": 8, "min_ach": 3, "standard": "EN 16798-1"},
    },
    "india": {
        "office": {"min_fresh_air_l_s": 8, "min_ach": 3, "standard": "NBC 2016 Part 8"},
        "meeting_room": {"min_fresh_air_l_s": 8, "min_ach": 5, "standard": "NBC 2016 Part 8"},
        "general": {"min_fresh_air_l_s": 6, "min_ach": 3, "standard": "NBC 2016"},
    },
    "australia": {
        "office": {"min_fresh_air_l_s": 10, "min_ach": 3, "standard": "AS 1668.2"},
        "meeting_room": {"min_fresh_air_l_s": 10, "min_ach": 6, "standard": "AS 1668.2"},
        "general": {"min_fresh_air_l_s": 8, "min_ach": 3, "standard": "AS 1668.2"},
    },
}

PLUMBING_VELOCITY_LIMITS = {
    "cold_water": {"min_m_s": 0.2, "max_m_s": 3.0, "standard_gcc": "BS EN 806-3 / DEWA", "standard_eu": "BS EN 806-3", "standard_in": "IS 1172", "standard_au": "AS 3500.1"},
    "hot_water":  {"min_m_s": 0.2, "max_m_s": 2.5, "standard_gcc": "BS EN 806-3 / DEWA", "standard_eu": "BS EN 806-3", "standard_in": "IS 1172", "standard_au": "AS 3500.1"},
    "drainage":   {"min_m_s": 0.7, "max_m_s": 4.0, "standard_gcc": "BS EN 12056 / DEWA", "standard_eu": "BS EN 12056", "standard_in": "IS 1742",  "standard_au": "AS 3500.2"},
}

SPRINKLER_DENSITY = {
    "LH":  {"min_density_mm_min": 2.25, "min_pressure_bar": 0.35, "standard_gcc": "BS EN 12845", "standard_eu": "BS EN 12845", "standard_in": "NBC Part 4", "standard_au": "AS 2118.1"},
    "OH1": {"min_density_mm_min": 5.0,  "min_pressure_bar": 0.35, "standard_gcc": "BS EN 12845", "standard_eu": "BS EN 12845", "standard_in": "NBC Part 4", "standard_au": "AS 2118.1"},
    "OH2": {"min_density_mm_min": 5.0,  "min_pressure_bar": 0.50, "standard_gcc": "BS EN 12845", "standard_eu": "BS EN 12845", "standard_in": "NBC Part 4", "standard_au": "AS 2118.1"},
    "EH1": {"min_density_mm_min": 7.5,  "min_pressure_bar": 0.50, "standard_gcc": "BS EN 12845", "standard_eu": "BS EN 12845", "standard_in": "NBC Part 4", "standard_au": "AS 2118.1"},
    "EH2": {"min_density_mm_min": 10.0, "min_pressure_bar": 0.70, "standard_gcc": "BS EN 12845", "standard_eu": "BS EN 12845", "standard_in": "NBC Part 4", "standard_au": "AS 2118.1"},
}


# ─── Check functions ──────────────────────────────────────────────────────────

def _check_cable(check: CableComplianceCheck) -> dict:
    results = []
    ccc_ok = check.derated_rating_iz_a >= check.design_current_a
    clause_ccc = "BS 7671 Reg 523.1 / IEC 60364-5-52" if check.region in ("gcc", "europe") else ("IS 732 Cl.5.3" if check.region == "india" else "AS/NZS 3000 Cl.3.5")
    results.append({
        "check": "Current Carrying Capacity",
        "clause": clause_ccc,
        "actual": f"Iz = {check.derated_rating_iz_a:.1f} A",
        "limit": f"Ib = {check.design_current_a:.1f} A",
        "passed": ccc_ok,
        "note": "Derated rating must exceed design current." if not ccc_ok else "",
    })

    vd_ok = check.voltage_drop_pct <= check.vd_limit_pct
    clause_vd = "BS 7671 App.12" if check.region in ("gcc", "europe") else ("IS 732 Sec.6" if check.region == "india" else "AS/NZS 3000 Cl.3.6")
    results.append({
        "check": "Voltage Drop",
        "clause": clause_vd,
        "actual": f"{check.voltage_drop_pct:.2f}%",
        "limit": f"{check.vd_limit_pct:.1f}%",
        "passed": vd_ok,
        "note": f"Voltage drop {check.voltage_drop_pct:.2f}% exceeds limit." if not vd_ok else "",
    })

    earth_ratio_ok = (check.earth_size_mm2 >= check.cable_size_mm2 * 0.5) if check.cable_size_mm2 else True
    results.append({
        "check": "Earth Conductor Size",
        "clause": "BS 7671 Table 54.7" if check.region in ("gcc", "europe") else "IS 3043",
        "actual": f"{check.earth_size_mm2:.1f} mm²",
        "limit": f"≥ {check.cable_size_mm2 * 0.5:.1f} mm²",
        "passed": earth_ratio_ok,
        "note": "Earth conductor under-sized." if not earth_ratio_ok else "",
    })

    passed = all(r["passed"] for r in results)
    return {"circuit_reference": check.circuit_reference, "checks": results, "overall_passed": passed}


def _check_lighting(check: LightingComplianceCheck) -> dict:
    reg_data = LIGHTING_REQUIREMENTS.get(check.region, LIGHTING_REQUIREMENTS["gcc"])
    room_data = reg_data.get(check.room_type, reg_data.get("general", {}))
    min_lux = room_data.get("min_lux", check.target_lux)
    uniformity_req = room_data.get("uniformity", 0.6)
    lpd_lim = room_data.get("lpd_limit", 12.0)
    standard = room_data.get("standard", "EN 12464-1")

    results = [
        {
            "check": "Maintained Illuminance (Em)",
            "clause": standard,
            "actual": f"{check.achieved_lux:.0f} lux",
            "limit": f"≥ {min_lux:.0f} lux",
            "passed": check.achieved_lux >= min_lux,
            "note": "" if check.achieved_lux >= min_lux else "Increase luminaire count or lumen output.",
        },
        {
            "check": "Uniformity Ratio (U0)",
            "clause": standard,
            "actual": f"{check.uniformity_ratio:.2f}",
            "limit": f"≥ {uniformity_req:.2f}",
            "passed": check.uniformity_ratio >= uniformity_req,
            "note": "" if check.uniformity_ratio >= uniformity_req else "Improve luminaire spacing ratio.",
        },
        {
            "check": "Lighting Power Density (LPD)",
            "clause": f"{standard} / Energy Code",
            "actual": f"{check.lpd_w_per_m2:.1f} W/m²",
            "limit": f"≤ {lpd_lim:.0f} W/m²",
            "passed": check.lpd_w_per_m2 <= lpd_lim,
            "note": "" if check.lpd_w_per_m2 <= lpd_lim else "Use more efficient luminaires.",
        },
    ]
    return {
        "room_type": check.room_type,
        "region": check.region,
        "standard": standard,
        "checks": results,
        "overall_passed": all(r["passed"] for r in results),
    }


def _check_mechanical(check: MechanicalComplianceCheck) -> dict:
    reg_data = VENTILATION_REQUIREMENTS.get(check.region, VENTILATION_REQUIREMENTS["gcc"])
    zone_data = reg_data.get(check.zone_type, reg_data.get("general", {}))
    min_fresh = zone_data.get("min_fresh_air_l_s", 8)
    min_ach = zone_data.get("min_ach", 4)
    standard = zone_data.get("standard", "ASHRAE 62.1")

    cooling_limit = {"gcc": 120.0, "europe": 90.0, "india": 100.0, "australia": 90.0}.get(check.region, 100.0)

    results = [
        {
            "check": "Fresh Air Rate",
            "clause": standard,
            "actual": f"{check.fresh_air_l_s_person:.1f} L/s/person",
            "limit": f"≥ {min_fresh} L/s/person",
            "passed": check.fresh_air_l_s_person >= min_fresh,
            "note": "" if check.fresh_air_l_s_person >= min_fresh else "Increase outdoor air flow.",
        },
        {
            "check": "Air Changes per Hour (ACH)",
            "clause": standard,
            "actual": f"{check.supply_air_ach:.1f} ACH",
            "limit": f"≥ {min_ach} ACH",
            "passed": check.supply_air_ach >= min_ach,
            "note": "" if check.supply_air_ach >= min_ach else "Increase supply air quantity.",
        },
        {
            "check": "Cooling Power Density",
            "clause": "ASHRAE 90.1 / ECBC" if check.region in ("gcc", "india") else "NCC Section J",
            "actual": f"{check.cooling_w_per_m2:.0f} W/m²",
            "limit": f"≤ {cooling_limit:.0f} W/m²",
            "passed": check.cooling_w_per_m2 <= cooling_limit or check.cooling_w_per_m2 == 0.0,
            "note": "" if check.cooling_w_per_m2 <= cooling_limit or check.cooling_w_per_m2 == 0.0 else "Cooling density exceeds energy code limit.",
        },
    ]
    return {
        "zone_type": check.zone_type,
        "region": check.region,
        "standard": standard,
        "checks": results,
        "overall_passed": all(r["passed"] for r in results),
    }


def _check_plumbing(check: PlumbingComplianceCheck) -> dict:
    lims = PLUMBING_VELOCITY_LIMITS.get(check.system_type, PLUMBING_VELOCITY_LIMITS["cold_water"])
    std_key = {"gcc": "standard_gcc", "europe": "standard_eu", "india": "standard_in", "australia": "standard_au"}.get(check.region, "standard_gcc")
    standard = lims[std_key]

    results = []

    # Velocity range
    vel_ok = lims["min_m_s"] <= check.pipe_velocity_m_s <= lims["max_m_s"] if check.pipe_velocity_m_s > 0 else True
    results.append({
        "check": "Pipe Flow Velocity",
        "clause": f"{standard} — velocity limits",
        "actual": f"{check.pipe_velocity_m_s:.2f} m/s",
        "limit": f"{lims['min_m_s']}–{lims['max_m_s']} m/s",
        "passed": vel_ok,
        "note": "" if vel_ok else "Velocity outside acceptable range. Resize pipe.",
    })

    # Design pressure
    if check.design_pressure_bar > 0:
        press_ok = check.min_pressure_bar <= check.design_pressure_bar <= check.max_pressure_bar
        results.append({
            "check": "Working Pressure",
            "clause": f"{standard} — pressure class",
            "actual": f"{check.design_pressure_bar:.2f} bar",
            "limit": f"{check.min_pressure_bar}–{check.max_pressure_bar} bar",
            "passed": press_ok,
            "note": "" if press_ok else "Pressure outside permitted range. Check PRV or pipe class.",
        })

    # Backflow prevention
    results.append({
        "check": "Backflow Prevention",
        "clause": "BS EN 1717" if check.region in ("gcc", "europe") else ("IS 1239" if check.region == "india" else "AS 3500.1"),
        "actual": "Fitted" if check.has_backflow_preventer else "Not fitted",
        "limit": "Required",
        "passed": check.has_backflow_preventer,
        "note": "" if check.has_backflow_preventer else "Install BS EN 1717 / RPZ backflow preventer.",
    })

    # Hot water legionella (if hot water system)
    if check.system_type == "hot_water":
        legionella_storage_ok = check.storage_temp_c >= 60.0
        results.append({
            "check": "Legionella — Storage Temp",
            "clause": "HSE L8 / WHO Guidelines / AS 3666" if check.region != "india" else "NBC 2016 / IS 2065",
            "actual": f"{check.storage_temp_c:.1f}°C",
            "limit": "≥ 60°C",
            "passed": legionella_storage_ok,
            "note": "" if legionella_storage_ok else "Storage temp must be ≥ 60°C to prevent Legionella growth.",
        })
        legionella_dist_ok = check.distribution_temp_c >= 50.0 if check.distribution_temp_c > 0 else True
        results.append({
            "check": "Legionella — Distribution Temp",
            "clause": "HSE L8 / WHO" if check.region != "india" else "NBC 2016",
            "actual": f"{check.distribution_temp_c:.1f}°C",
            "limit": "≥ 50°C at all outlets",
            "passed": legionella_dist_ok,
            "note": "" if legionella_dist_ok else "Distribution temp must remain ≥ 50°C. Check dead legs.",
        })
        tmax_ok = check.has_tmax_valve
        results.append({
            "check": "Scalding Protection (TMV/Tmax)",
            "clause": "BS EN 15091 / TMV3 Scheme",
            "actual": "Fitted" if tmax_ok else "Not fitted",
            "limit": "Required at all user outlets",
            "passed": tmax_ok,
            "note": "" if tmax_ok else "Install thermostatic mixing valve (TMV) at all user outlets.",
        })

    return {
        "system_type": check.system_type,
        "region": check.region,
        "standard": standard,
        "checks": results,
        "overall_passed": all(r["passed"] for r in results),
    }


def _check_fire(check: FireComplianceCheck) -> dict:
    std_key = {"gcc": "standard_gcc", "europe": "standard_eu", "india": "standard_in", "australia": "standard_au"}.get(check.region, "standard_gcc")
    hazard_data = SPRINKLER_DENSITY.get(check.hazard_class, SPRINKLER_DENSITY["OH1"])
    standard = hazard_data.get(std_key, "BS EN 12845")

    results = []

    if check.system_type == "sprinkler":
        density_ok = check.design_density_mm_min >= check.min_density_mm_min if check.min_density_mm_min > 0 else check.design_density_mm_min >= hazard_data["min_density_mm_min"]
        results.append({
            "check": "Sprinkler Design Density",
            "clause": f"{standard} Table 2",
            "actual": f"{check.design_density_mm_min:.2f} mm/min",
            "limit": f"≥ {hazard_data['min_density_mm_min']:.2f} mm/min",
            "passed": density_ok,
            "note": "" if density_ok else "Increase water flow / reduce sprinkler spacing.",
        })

    if check.design_pressure_bar > 0:
        press_ok = check.design_pressure_bar >= (check.min_pressure_bar if check.min_pressure_bar > 0 else hazard_data["min_pressure_bar"])
        results.append({
            "check": "Design Pressure at Sprinkler Head",
            "clause": f"{standard} Cl.11",
            "actual": f"{check.design_pressure_bar:.2f} bar",
            "limit": f"≥ {hazard_data['min_pressure_bar']:.2f} bar",
            "passed": press_ok,
            "note": "" if press_ok else "Insufficient pressure. Upsize pump or reduce system resistance.",
        })

    if check.pump_rated_flow_l_min > 0:
        pump_ok = check.pump_rated_flow_l_min >= check.required_flow_l_min
        results.append({
            "check": "Pump Rated Flow vs Demand",
            "clause": f"{'BS EN 12845 Cl.10' if check.region in ('gcc','europe') else 'NFPA 20 / NBC Part 4'}",
            "actual": f"{check.pump_rated_flow_l_min:.0f} L/min",
            "limit": f"≥ {check.required_flow_l_min:.0f} L/min",
            "passed": pump_ok,
            "note": "" if pump_ok else "Increase pump capacity to meet system demand.",
        })

    if check.tank_volume_m3 > 0:
        tank_ok = check.tank_volume_m3 >= check.required_volume_m3
        results.append({
            "check": "Fire Water Tank Volume",
            "clause": f"{'BS EN 12845 Cl.9' if check.region in ('gcc','europe') else 'NFPA 22 / NBC Part 4'}",
            "actual": f"{check.tank_volume_m3:.1f} m³",
            "limit": f"≥ {check.required_volume_m3:.1f} m³",
            "passed": tank_ok,
            "note": "" if tank_ok else "Tank volume insufficient. Increase storage capacity.",
        })

    results.append({
        "check": "Duty/Standby Pump Arrangement",
        "clause": f"{'BS EN 12845 Cl.10.3' if check.region in ('gcc','europe') else 'NFPA 20 Cl.4.13'}",
        "actual": "Duty+Standby" if check.has_duty_standby else "Duty only",
        "limit": "Duty + Standby required",
        "passed": check.has_duty_standby,
        "note": "" if check.has_duty_standby else "Standby pump required by standard.",
    })

    results.append({
        "check": "Jockey (Pressure Maintenance) Pump",
        "clause": f"{'BS EN 12845 Cl.10.4' if check.region in ('gcc','europe') else 'NFPA 20 Cl.4.17'}",
        "actual": "Fitted" if check.has_jockey_pump else "Not fitted",
        "limit": "Recommended",
        "passed": check.has_jockey_pump,
        "note": "" if check.has_jockey_pump else "Jockey pump strongly recommended to maintain system pressure.",
    })

    return {
        "system_type": check.system_type,
        "hazard_class": check.hazard_class,
        "region": check.region,
        "standard": standard,
        "checks": results,
        "overall_passed": all(r["passed"] for r in results),
    }


@router.post("/check", summary="Run MEP Compliance Report")
async def compliance_check(req: ComplianceReportRequest) -> Any:
    """
    Run a structured compliance check against regional MEP standards.
    Covers electrical, lighting, mechanical, plumbing, and fire disciplines.
    Returns pass/fail status for each check with standard clause references.
    """
    try:
        cable_results = [_check_cable(c) for c in req.cable_checks]
        lighting_results = [_check_lighting(c) for c in req.lighting_checks]
        mechanical_results = [_check_mechanical(c) for c in req.mechanical_checks]
        plumbing_results = [_check_plumbing(c) for c in req.plumbing_checks]
        fire_results = [_check_fire(c) for c in req.fire_checks]

        all_checks = (
            [c for r in cable_results for c in r["checks"]] +
            [c for r in lighting_results for c in r["checks"]] +
            [c for r in mechanical_results for c in r["checks"]] +
            [c for r in plumbing_results for c in r["checks"]] +
            [c for r in fire_results for c in r["checks"]]
        )
        total = len(all_checks)
        passed = sum(1 for c in all_checks if c["passed"])
        failed = total - passed

        return {
            "status": "success",
            "project_name": req.project_name,
            "project_reference": req.project_reference,
            "region": req.region,
            "sub_region": req.sub_region,
            "discipline": req.discipline,
            "total_checks": total,
            "checks_passed": passed,
            "checks_failed": failed,
            "overall_compliant": failed == 0,
            "electrical": {"cable_circuits": cable_results},
            "lighting": {"rooms": lighting_results},
            "mechanical": {"zones": mechanical_results},
            "plumbing": {"systems": plumbing_results},
            "fire": {"systems": fire_results},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/standards-reference", summary="Regional Standards Reference (GET)")
async def standards_reference() -> Any:
    """Return the complete cross-regional standards reference matrix for all MEP disciplines."""
    return {
        "electrical": {
            "gcc": "BS 7671:2018+A2:2022 / IEC 60364 / DEWA/ADDC/KAHRAMAA/SEC regulations",
            "europe": "BS 7671:2018+A2:2022 (UK) / IEC 60364 (EU) / EN 50110",
            "india": "IS 732:2019 / IS 3961 / IS 7098 / CEA Regulations 2010",
            "australia": "AS/NZS 3000:2018 / AS/NZS 3008.1.1:2017 / AS 3439",
        },
        "lighting": {
            "gcc": "EN 12464-1:2021 / DEWA Green Building Regulations",
            "europe": "EN 12464-1:2021 / SLL Code for Lighting",
            "india": "NBC 2016 Part 8 / SP 72",
            "australia": "AS 1680.1:2006 / NCC Section J",
        },
        "mechanical": {
            "gcc": "ASHRAE 62.1 / ASHRAE 55 / DEWA Sustainability Regulations",
            "europe": "EN 16798-1 / BS EN ISO 7730 / EN 15251",
            "india": "NBC 2016 Part 8 / ECBC 2017",
            "australia": "AS 1668.2 / AS 1668.4 / NCC Section J",
        },
        "plumbing": {
            "gcc": "BS EN 806 / BS 8558 / DEWA regulations / HSE L8 (Legionella)",
            "europe": "BS EN 806-3 / BS 6700 / DIN 1988 / WRAS / BS EN 1717",
            "india": "IS 1172 / IS 2065 / NBC 2016 Part 9 / IS 1239",
            "australia": "AS 3500.1 / AS 3500.4 / AS 3666 (Legionella) / WaterMark",
        },
        "fire": {
            "gcc": "BS EN 12845 / NFPA 13 / NFPA 20 / Civil Defence requirements",
            "europe": "BS EN 12845:2015+A1:2019 / BS 9251 / BS 5306",
            "india": "NBC 2016 Part 4 / IS 15105 / IS 2190 / TAC guidelines",
            "australia": "AS 2118.1 / AS 2118.4 / AS 2941 / BCA Section E",
        },
    }
