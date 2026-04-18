"""FastAPI Mechanical/HVAC Calculation Routes."""

from fastapi import APIRouter, HTTPException
from typing import Any

from backend.models.mechanical import CoolingLoadRequest, DuctSegmentRequest, MultiZoneCoolingRequest
from backend.engines.mechanical.cooling_load import ZoneInput, calculate_cooling_load
from backend.engines.mechanical.duct_sizing import DuctSegment, size_duct

router = APIRouter(prefix="/mechanical", tags=["Mechanical / HVAC"])


@router.post("/cooling-load", summary="HVAC Cooling Load Calculation")
async def cooling_load(req: CoolingLoadRequest) -> Any:
    """
    Calculate HVAC cooling load for a single zone using simplified heat balance method.
    Standards: ASHRAE / CIBSE / ECBC / NCC depending on region.
    """
    try:
        zone = ZoneInput(
            zone_name=req.zone_name,
            zone_type=req.zone_type,
            floor_area_m2=req.floor_area_m2,
            height_m=req.height_m,
            glass_area_m2=req.glass_area_m2,
            glass_u_value=req.glass_u_value,
            glass_shgc=req.glass_shgc,
            glass_orientation=req.glass_orientation,
            wall_area_m2=req.wall_area_m2,
            wall_u_value=req.wall_u_value,
            roof_area_m2=req.roof_area_m2,
            roof_u_value=req.roof_u_value,
            occupancy=req.occupancy,
            metabolic_rate_w=req.metabolic_rate_w,
            equipment_w_m2=req.equipment_w_m2,
            lighting_w_m2=req.lighting_w_m2,
            fresh_air_l_s_person=req.fresh_air_l_s_person,
            cop=req.cop,
        )
        result = calculate_cooling_load(zone, region=req.region.value, safety_factor=req.safety_factor)
        return {
            "status": "success",
            "zone_name": result.zone_name,
            "standard_reference": result.standard_reference,
            "outdoor_db_c": result.outdoor_db_c,
            "outdoor_wb_c": result.outdoor_wb_c,
            "indoor_db_c": result.indoor_db_c,
            "indoor_rh_pct": result.indoor_rh_pct,
            "floor_area_m2": result.floor_area_m2,
            "load_breakdown_w": {
                "solar_gain": result.solar_gain_w,
                "conduction_glass": result.conduction_glass_w,
                "conduction_wall": result.conduction_wall_w,
                "conduction_roof": result.conduction_roof_w,
                "occupants": result.internal_occupants_w,
                "lighting": result.internal_lighting_w,
                "equipment": result.internal_equipment_w,
                "ventilation": result.ventilation_load_w,
            },
            "total_sensible_w": result.total_sensible_w,
            "total_latent_w": result.total_latent_w,
            "total_cooling_w": result.total_cooling_w,
            "total_cooling_kw": result.total_cooling_kw,
            "total_cooling_tr": result.total_cooling_tr,
            "cooling_w_per_m2": result.cooling_w_per_m2,
            "cooling_tr_per_100m2": result.cooling_tr_per_100m2,
            "supply_airflow_l_s": result.supply_airflow_l_s,
            "fresh_air_l_s": result.fresh_air_l_s,
            "room_air_changes_per_hour": result.room_air_changes_per_hour,
            "chiller_power_kw": result.chiller_power_kw,
            "summary": result.summary,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/duct-sizing", summary="Duct Sizing — Equal Friction Method")
async def duct_sizing(req: DuctSegmentRequest) -> Any:
    """Size a duct segment using the equal friction method (ASHRAE / CIBSE)."""
    try:
        seg = DuctSegment(
            segment_id=req.segment_id,
            airflow_l_s=req.airflow_l_s,
            duct_type=req.duct_type,
            max_velocity_m_s=req.max_velocity_m_s,
            friction_rate_pa_m=req.friction_rate_pa_m,
        )
        result = size_duct(seg)
        return {
            "status": "success",
            "segment_id": result.segment_id,
            "airflow_l_s": result.airflow_l_s,
            "duct_type": req.duct_type,
            "velocity_m_s": result.velocity_m_s,
            "diameter_mm": result.diameter_mm,
            "width_mm": result.width_mm,
            "height_mm": result.height_mm,
            "hydraulic_diameter_mm": result.hydraulic_diameter_mm,
            "pressure_drop_pa_m": result.pressure_drop_pa_m,
            "duct_area_m2": result.duct_area_m2,
            "summary": result.summary,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/multi-zone-cooling", summary="Multi-Zone Cooling Load Summary")
async def multi_zone_cooling(req: MultiZoneCoolingRequest) -> Any:
    """Calculate cooling loads for all zones and summarise building total."""
    try:
        zone_results = []
        total_kw = 0.0
        total_tr = 0.0
        for z in req.zones:
            zone = ZoneInput(
                zone_name=z.zone_name,
                zone_type=z.zone_type,
                floor_area_m2=z.floor_area_m2,
                height_m=z.height_m,
                glass_area_m2=z.glass_area_m2,
                glass_u_value=z.glass_u_value,
                glass_shgc=z.glass_shgc,
                glass_orientation=z.glass_orientation,
                wall_area_m2=z.wall_area_m2,
                wall_u_value=z.wall_u_value,
                roof_area_m2=z.roof_area_m2,
                occupancy=z.occupancy,
                equipment_w_m2=z.equipment_w_m2,
                lighting_w_m2=z.lighting_w_m2,
                fresh_air_l_s_person=z.fresh_air_l_s_person,
                cop=req.chiller_cop,
            )
            r = calculate_cooling_load(zone, region=req.region.value, safety_factor=z.safety_factor)
            zone_results.append({
                "zone_name": r.zone_name,
                "floor_area_m2": r.floor_area_m2,
                "total_cooling_kw": r.total_cooling_kw,
                "total_cooling_tr": r.total_cooling_tr,
                "cooling_w_per_m2": r.cooling_w_per_m2,
            })
            total_kw += r.total_cooling_kw
            total_tr += r.total_cooling_tr

        total_kw_div = total_kw * req.diversity_factor
        total_tr_div = total_tr * req.diversity_factor

        return {
            "status": "success",
            "region": req.region.value,
            "num_zones": len(zone_results),
            "zones": zone_results,
            "total_cooling_kw_undiversified": round(total_kw, 2),
            "total_cooling_tr_undiversified": round(total_tr, 2),
            "diversity_factor": req.diversity_factor,
            "total_cooling_kw_diversified": round(total_kw_div, 2),
            "total_cooling_tr_diversified": round(total_tr_div, 2),
            "chiller_power_kw": round(total_kw_div / req.chiller_cop, 2),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Heating Load ─────────────────────────────────────────────────────────────

from pydantic import BaseModel

class HeatingLoadRequest(BaseModel):
    region: str = "europe"
    zone_name: str = "Zone 1"
    zone_type: str = "office"
    floor_area_m2: float = 100.0
    height_m: float = 3.0
    wall_area_m2: float = 80.0
    wall_u_value: float = 0.30
    roof_area_m2: float = 100.0
    roof_u_value: float = 0.20
    window_area_m2: float = 20.0
    window_u_value: float = 1.4
    floor_area_m2_uninsulated: float = 0.0
    floor_u_value: float = 0.25
    infiltration_ach: float = 0.5
    outdoor_design_temp_c: float = -5.0
    indoor_design_temp_c: float = 21.0
    safety_factor: float = 1.15

@router.post("/heating-load", summary="HVAC Heating Load Calculation (CIBSE/EN 12831)")
async def heating_load(req: HeatingLoadRequest) -> Any:
    """Calculate space heating load per EN 12831 / CIBSE Guide A / IS SP7."""
    try:
        dt = req.indoor_design_temp_c - req.outdoor_design_temp_c
        fabric_w = (
            req.wall_area_m2 * req.wall_u_value +
            req.roof_area_m2 * req.roof_u_value +
            req.window_area_m2 * req.window_u_value +
            req.floor_area_m2_uninsulated * req.floor_u_value
        ) * dt
        volume_m3 = req.floor_area_m2 * req.height_m
        infiltration_w = req.infiltration_ach * volume_m3 * 0.33 * dt
        total_w = (fabric_w + infiltration_w) * req.safety_factor
        total_kw = total_w / 1000.0
        standards = {
            "gcc": "ASHRAE 90.1 / ADM Guidelines",
            "europe": "EN 12831:2017 / CIBSE Guide A",
            "india": "NBC 2016 Part 8 / IS SP7",
            "australia": "NCC 2022 Section J / AS/NZS 4600",
        }
        return {
            "status": "success",
            "zone_name": req.zone_name,
            "zone_type": req.zone_type,
            "region": req.region,
            "standard": standards.get(req.region, "EN 12831:2017"),
            "outdoor_design_temp_c": req.outdoor_design_temp_c,
            "indoor_design_temp_c": req.indoor_design_temp_c,
            "delta_t_k": round(dt, 1),
            "fabric_heat_loss_w": round(fabric_w, 0),
            "infiltration_heat_loss_w": round(infiltration_w, 0),
            "total_heat_loss_w": round(total_w, 0),
            "total_heat_loss_kw": round(total_kw, 2),
            "heat_load_w_per_m2": round(total_w / max(req.floor_area_m2, 1), 1),
            "safety_factor": req.safety_factor,
            "summary": (
                f"Heating load: {total_kw:.2f} kW ({total_w/max(req.floor_area_m2,1):.0f} W/m²) | "
                f"Fabric: {fabric_w:.0f} W | Infiltration: {infiltration_w:.0f} W | "
                f"ΔT = {dt:.1f} K | {standards.get(req.region, 'EN 12831')}"
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Ventilation / Fresh Air ──────────────────────────────────────────────────

class VentilationRequest(BaseModel):
    region: str = "europe"
    zone_name: str = "Zone 1"
    zone_type: str = "office"
    floor_area_m2: float = 200.0
    height_m: float = 3.0
    occupancy: int = 20
    fresh_air_method: str = "occupancy"  # occupancy | ach | area
    fresh_air_l_s_person: float = 10.0
    fresh_air_ach: float = 6.0
    fresh_air_l_s_m2: float = 1.5
    supply_air_temp_c: float = 18.0
    room_temp_c: float = 22.0
    cooling_load_kw: float = 10.0

@router.post("/ventilation", summary="Mechanical Ventilation Design (ASHRAE 62.1 / CIBSE Guide B / IS 3103)")
async def ventilation(req: VentilationRequest) -> Any:
    """Calculate ventilation and supply air requirements per regional standards."""
    try:
        volume_m3 = req.floor_area_m2 * req.height_m
        if req.fresh_air_method == "occupancy":
            fresh_air_l_s = req.occupancy * req.fresh_air_l_s_person
            method_desc = f"{req.occupancy} persons × {req.fresh_air_l_s_person} L/s·person"
        elif req.fresh_air_method == "ach":
            fresh_air_l_s = req.fresh_air_ach * volume_m3 / 3.6
            method_desc = f"{req.fresh_air_ach} ACH × {volume_m3:.0f} m³"
        else:
            fresh_air_l_s = req.fresh_air_l_s_m2 * req.floor_area_m2
            method_desc = f"{req.fresh_air_l_s_m2} L/s·m² × {req.floor_area_m2:.0f} m²"

        fresh_air_m3_h = fresh_air_l_s * 3.6
        ach_achieved = fresh_air_m3_h / max(volume_m3, 1)

        # Supply air from cooling
        delta_t = max(req.room_temp_c - req.supply_air_temp_c, 2)
        supply_air_m3_h = (req.cooling_load_kw * 3600) / (1.2 * 1.005 * delta_t)
        total_supply_m3_h = max(supply_air_m3_h, fresh_air_m3_h)

        standards = {
            "gcc": "ASHRAE 62.1 / DEWA / ADDC Guidelines",
            "europe": "CIBSE Guide B2 / BS EN 15251 / BS EN 16798",
            "india": "NBC 2016 / IS 3103 / ECBC 2017",
            "australia": "AS 1668.2 / NCC 2022 / AIRAH DA19",
        }
        return {
            "status": "success",
            "zone_name": req.zone_name,
            "region": req.region,
            "standard": standards.get(req.region, "ASHRAE 62.1"),
            "fresh_air_method": req.fresh_air_method,
            "method_description": method_desc,
            "fresh_air_l_s": round(fresh_air_l_s, 1),
            "fresh_air_m3_h": round(fresh_air_m3_h, 0),
            "ach_achieved": round(ach_achieved, 2),
            "supply_air_delta_t_k": round(delta_t, 1),
            "supply_air_from_cooling_m3_h": round(supply_air_m3_h, 0),
            "total_supply_air_m3_h": round(total_supply_m3_h, 0),
            "fresh_air_l_s_person": round(fresh_air_l_s / max(req.occupancy, 1), 1),
            "fresh_air_l_s_m2": round(fresh_air_l_s / max(req.floor_area_m2, 1), 2),
            "summary": (
                f"Fresh air: {fresh_air_m3_h:.0f} m³/h ({fresh_air_l_s:.0f} L/s) via {req.fresh_air_method} method | "
                f"ACH: {ach_achieved:.1f} | Supply: {total_supply_m3_h:.0f} m³/h | "
                f"{standards.get(req.region, 'ASHRAE 62.1')}"
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
