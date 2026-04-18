"""FastAPI Fire Protection Calculation Routes."""

from fastapi import APIRouter, HTTPException
from typing import Any

from backend.models.fire import SprinklerRequest
from backend.engines.fire.sprinkler_calc import SprinklerInput, calculate_sprinkler

router = APIRouter(prefix="/fire", tags=["Fire Protection"])


@router.post("/sprinkler", summary="Sprinkler System Design (BS EN 12845 / NFPA 13)")
async def sprinkler_calc(req: SprinklerRequest) -> Any:
    """
    Calculate fire sprinkler system design — BS EN 12845 / NFPA 13 method.
    Returns design flow, pump sizing, and tank capacity.
    """
    try:
        inp = SprinklerInput(
            region=req.region.value,
            occupancy_hazard=req.occupancy_hazard,
            area_protected_m2=req.area_protected_m2,
            ceiling_height_m=req.ceiling_height_m,
            sprinkler_coverage_m2=req.sprinkler_coverage_m2,
            sprinkler_k_factor=req.sprinkler_k_factor,
            design_area_m2=req.design_area_m2 or 0,
            hose_allowance_l_min=req.hose_allowance_l_min,
        )
        result = calculate_sprinkler(inp)
        return {
            "status": "success",
            "hazard_class": result.hazard_class,
            "design_standard": result.design_standard,
            "num_sprinklers_design_area": result.num_sprinklers_design_area,
            "design_flow_l_min": result.design_flow_l_min,
            "hose_allowance_l_min": result.hose_allowance_l_min,
            "total_system_flow_l_min": result.total_system_flow_l_min,
            "residual_pressure_bar": result.residual_pressure_bar,
            "pump_flow_l_min": result.pump_flow_l_min,
            "pump_head_m": result.pump_head_m,
            "pump_power_kw": result.pump_power_kw,
            "tank_capacity_m3": result.tank_capacity_m3,
            "supply_duration_min": result.supply_duration_min,
            "summary": result.summary,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Additional Fire Protection Endpoints ─────────────────────────────────────

from pydantic import BaseModel
import math

class FirePumpRequest(BaseModel):
    region: str = "gcc"
    system_type: str = "wet_riser"  # wet_riser | combined | deluge | foam
    sprinkler_demand_l_min: float = 2000.0
    hose_reel_demand_l_min: float = 600.0
    hydrant_demand_l_min: float = 0.0
    static_pressure_required_bar: float = 6.5
    friction_loss_bar: float = 1.5
    elevation_loss_bar: float = 2.0
    pump_efficiency: float = 0.72
    motor_efficiency: float = 0.90
    duty_standby_jockey: bool = True

@router.post("/fire-pump", summary="Fire Pump Sizing (BS EN 12845 / NFPA 20 / NBC / AS 2941)")
async def fire_pump(req: FirePumpRequest) -> Any:
    """Size fire pump set including duty, standby and jockey pumps."""
    try:
        standards = {
            "gcc": "BS EN 12845 / NFPA 13/20 / UAE Civil Defence SOP",
            "europe": "BS EN 12845:2015+A1:2019 / BS EN 12259 / FM Global",
            "india": "NBC 2016 Part 4 / IS 908 / NFPA 13 / TAC",
            "australia": "AS 2941:2013 / AS/NZS 1221 / NCC Spec C2.3",
        }
        total_flow_l_min = req.sprinkler_demand_l_min + req.hose_reel_demand_l_min + req.hydrant_demand_l_min
        total_head_bar = req.static_pressure_required_bar + req.friction_loss_bar + req.elevation_loss_bar
        total_head_m = total_head_bar * 10.2

        flow_m3_s = total_flow_l_min / 60000.0
        hydraulic_kw = (1000 * 9.81 * flow_m3_s * total_head_m) / 1000.0
        shaft_kw = hydraulic_kw / req.pump_efficiency
        motor_kw = shaft_kw / req.motor_efficiency

        # Jockey pump: 10% of main flow at full head
        jockey_flow_l_min = max(total_flow_l_min * 0.05, 100)
        jockey_kw = motor_kw * 0.08

        std_motors = [1.5, 2.2, 3.0, 4.0, 5.5, 7.5, 11, 15, 18.5, 22, 30, 37, 45, 55, 75, 90, 110, 132]
        selected_motor_kw = next((m for m in std_motors if m >= motor_kw), std_motors[-1])
        jockey_motor_kw = next((m for m in std_motors if m >= jockey_kw), std_motors[0])

        return {
            "status": "success",
            "region": req.region,
            "standard": standards.get(req.region, "BS EN 12845"),
            "system_type": req.system_type,
            "total_flow_l_min": round(total_flow_l_min, 0),
            "total_flow_m3_h": round(total_flow_l_min * 0.06, 1),
            "total_dynamic_head_bar": round(total_head_bar, 2),
            "total_dynamic_head_m": round(total_head_m, 1),
            "hydraulic_power_kw": round(hydraulic_kw, 2),
            "duty_pump_kw": round(motor_kw, 2),
            "selected_motor_kw": selected_motor_kw,
            "jockey_pump_flow_l_min": round(jockey_flow_l_min, 0),
            "jockey_pump_kw": round(jockey_kw, 2),
            "jockey_motor_kw": jockey_motor_kw,
            "duty_standby_jockey": req.duty_standby_jockey,
            "pump_set_description": f"1 Duty + 1 Standby {selected_motor_kw} kW + 1 Jockey {jockey_motor_kw} kW" if req.duty_standby_jockey else f"1 Duty {selected_motor_kw} kW + 1 Jockey {jockey_motor_kw} kW",
            "summary": (
                f"Flow: {total_flow_l_min:.0f} L/min | TDH: {total_head_m:.1f} m ({total_head_bar:.1f} bar) | "
                f"Motor: {selected_motor_kw} kW | Jockey: {jockey_motor_kw} kW | "
                f"{standards.get(req.region, 'BS EN 12845')}"
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class FireTankRequest(BaseModel):
    region: str = "gcc"
    system_type: str = "sprinkler"  # sprinkler | wet_riser | combined | foam
    total_flow_l_min: float = 2000.0
    supply_duration_min: float = 60.0
    hose_allowance_l: float = 3000.0
    additional_allowance_pct: float = 10.0
    number_of_compartments: int = 2
    refill_time_hr: float = 4.0

@router.post("/fire-tank", summary="Fire Water Storage Tank Sizing (BS EN 12845 / NFPA 22 / NBC Part 4)")
async def fire_tank(req: FireTankRequest) -> Any:
    """Calculate fire water storage tank capacity including compartmentation."""
    try:
        standards = {
            "gcc": "BS EN 12845 / NFPA 22 / UAE Civil Defence SOP 2021",
            "europe": "BS EN 12845:2015+A1 / FM Global DS 10-2",
            "india": "NBC 2016 Part 4 / IS 3844 / TAC Guidelines",
            "australia": "AS 2118 series / NCC Spec C2.3 / AS 2941",
        }
        base_volume_l = req.total_flow_l_min * req.supply_duration_min
        with_hose = base_volume_l + req.hose_allowance_l
        with_allowance = with_hose * (1 + req.additional_allowance_pct / 100.0)
        total_volume_l = with_allowance
        total_volume_m3 = total_volume_l / 1000.0
        per_compartment_m3 = total_volume_m3 / req.number_of_compartments

        # Standard tank sizes (m³)
        std_tanks = [5, 10, 15, 20, 25, 30, 40, 50, 60, 75, 100, 125, 150, 200, 250, 300, 400, 500]
        selected_per_m3 = next((t for t in std_tanks if t >= per_compartment_m3), std_tanks[-1])
        total_selected_m3 = selected_per_m3 * req.number_of_compartments

        return {
            "status": "success",
            "region": req.region,
            "standard": standards.get(req.region, "BS EN 12845"),
            "system_type": req.system_type,
            "design_flow_l_min": req.total_flow_l_min,
            "supply_duration_min": req.supply_duration_min,
            "base_volume_l": round(base_volume_l, 0),
            "hose_allowance_l": req.hose_allowance_l,
            "additional_allowance_pct": req.additional_allowance_pct,
            "total_volume_required_l": round(total_volume_l, 0),
            "total_volume_required_m3": round(total_volume_m3, 1),
            "number_of_compartments": req.number_of_compartments,
            "volume_per_compartment_m3": round(per_compartment_m3, 1),
            "selected_tank_per_compartment_m3": selected_per_m3,
            "total_tank_capacity_m3": total_selected_m3,
            "refill_time_hr": req.refill_time_hr,
            "inlet_flow_l_min": round(total_selected_m3 * 1000 / (req.refill_time_hr * 60), 0),
            "summary": (
                f"Required: {total_volume_m3:.1f} m³ | {req.number_of_compartments} × {selected_per_m3} m³ tanks | "
                f"Duration: {req.supply_duration_min} min at {req.total_flow_l_min:.0f} L/min | "
                f"Refill: {req.refill_time_hr} hr | {standards.get(req.region, 'BS EN 12845')}"
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class StandpipeRequest(BaseModel):
    region: str = "gcc"
    system_class: str = "III"   # I | II | III (NFPA) or BS wet riser / dry riser
    building_height_m: float = 30.0
    num_floors: int = 10
    floor_height_m: float = 3.0
    hose_connection_spacing_m: float = 30.0
    pressure_at_outlet_bar: float = 6.5
    flow_per_standpipe_l_min: float = 950.0
    num_operating_standpipes: int = 2
    pipe_material: str = "steel_galvanised"

@router.post("/standpipe", summary="Standpipe / Wet Riser System (NFPA 14 / BS 5306 / NBC / AS 2118.1)")
async def standpipe(req: StandpipeRequest) -> Any:
    """Design a wet riser / standpipe system for a multi-storey building."""
    try:
        standards = {
            "gcc": "NFPA 14 / UAE Civil Defence SOP / BS 5306-1",
            "europe": "BS 5306-1:2016 / BS EN 671 / PD 7974-1",
            "india": "NBC 2016 Part 4 / IS 3844 / NFPA 14",
            "australia": "AS 2118.1:2017 / NCC Spec C2.3 / AFAC",
        }
        total_flow_l_min = req.flow_per_standpipe_l_min * req.num_operating_standpipes
        num_hose_stations = math.ceil(req.building_height_m / req.hose_connection_spacing_m) * 2

        # Friction loss — approximate 0.1 bar/m rise for water column + 0.05 bar/30m friction
        elevation_bar = req.building_height_m * 0.0981
        friction_bar = (req.building_height_m / 30.0) * 0.05
        total_pressure_bar = req.pressure_at_outlet_bar + elevation_bar + friction_bar

        # Pipe sizing — use Hazen-Williams C=120 for galvanised steel
        flow_m3_s = total_flow_l_min / 60000.0
        # d = [(10.67 * L * Q^1.852) / (C^1.852 * hf)]^(1/4.87) — simplified for riser main
        # Use velocity approach: target 2-3 m/s
        target_vel = 2.5
        area_m2 = flow_m3_s / target_vel
        diameter_m = math.sqrt(4 * area_m2 / math.pi)
        diameter_mm = diameter_m * 1000

        std_pipes = [50, 65, 80, 100, 125, 150, 200]
        selected_dn = next((d for d in std_pipes if d >= diameter_mm), std_pipes[-1])

        return {
            "status": "success",
            "region": req.region,
            "standard": standards.get(req.region, "NFPA 14"),
            "system_class": req.system_class,
            "building_height_m": req.building_height_m,
            "num_floors": req.num_floors,
            "total_flow_l_min": round(total_flow_l_min, 0),
            "total_flow_m3_h": round(total_flow_l_min * 0.06, 1),
            "num_operating_standpipes": req.num_operating_standpipes,
            "num_hose_stations": num_hose_stations,
            "elevation_head_bar": round(elevation_bar, 2),
            "friction_loss_bar": round(friction_bar, 2),
            "total_pressure_required_bar": round(total_pressure_bar, 2),
            "riser_main_diameter_mm": round(diameter_mm, 1),
            "selected_dn": selected_dn,
            "pipe_material": req.pipe_material,
            "summary": (
                f"DN{selected_dn} {req.pipe_material} riser | Flow: {total_flow_l_min:.0f} L/min | "
                f"System pressure: {total_pressure_bar:.1f} bar | {num_hose_stations} hose stations | "
                f"Class {req.system_class} | {standards.get(req.region, 'NFPA 14')}"
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
