"""FastAPI Plumbing/Drainage Calculation Routes."""

from fastapi import APIRouter, HTTPException
from typing import Any

from backend.models.plumbing import PipeSizingRequest
from backend.engines.plumbing.pipe_sizing import PlumbingInput, calculate_pipe_sizing

router = APIRouter(prefix="/plumbing", tags=["Plumbing & Drainage"])


@router.post("/pipe-sizing", summary="Cold/Hot Water Pipe Sizing (Hunter Method)")
async def pipe_sizing(req: PipeSizingRequest) -> Any:
    """Size a water supply pipe based on fixture unit loading (BS EN 806 / IS 1172 / AS/NZS 3500)."""
    try:
        inp = PlumbingInput(
            region=req.region.value,
            system=req.system,
            flow_units=req.flow_units,
            pipe_material=req.pipe_material,
            max_velocity_m_s=req.max_velocity_m_s,
        )
        result = calculate_pipe_sizing(inp)
        return {
            "status": "success",
            "standard": result.standard,
            "flow_rate_l_s": result.flow_rate_l_s,
            "pipe_nominal_dn": result.pipe_nominal_dn,
            "pipe_diameter_mm": result.pipe_diameter_mm,
            "pipe_material": result.pipe_material,
            "velocity_m_s": result.velocity_m_s,
            "pressure_drop_kpa_m": result.pressure_drop_kpa_m,
            "summary": result.summary,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Additional Plumbing Endpoints ────────────────────────────────────────────

from pydantic import BaseModel
import math

class DrainageSizingRequest(BaseModel):
    region: str = "gcc"
    system_type: str = "sanitary"  # sanitary | rainwater | combined
    discharge_units: float = 50.0   # BS EN 12056 discharge units
    roof_area_m2: float = 0.0       # for rainwater
    rainfall_intensity_mm_hr: float = 100.0
    gradient_percent: float = 1.0   # pipe gradient %
    pipe_material: str = "uPVC"
    simultaneous_use_factor: float = 0.7

@router.post("/drainage-sizing", summary="Drainage Pipe Sizing (BS EN 12056 / IS 1742 / AS/NZS 3500.2)")
async def drainage_sizing(req: DrainageSizingRequest) -> Any:
    """Size gravity drainage pipes by discharge unit loading or rainfall intensity."""
    try:
        standards = {
            "gcc": "BS EN 12056 / UAE Civil Defence Regs",
            "europe": "BS EN 12056-2:2000 / EN 12056-3",
            "india": "IS 1742:1983 / NBC 2016 Part 9",
            "australia": "AS/NZS 3500.2:2021 / NCC",
        }

        if req.system_type == "rainwater" and req.roof_area_m2 > 0:
            flow_l_s = (req.roof_area_m2 * req.rainfall_intensity_mm_hr) / 3600.0
            du = 0
        else:
            du = req.discharge_units
            flow_l_s = req.simultaneous_use_factor * math.sqrt(du)

        # Manning equation for pipe full bore at gradient
        # Q = (1/n) * A * R^(2/3) * S^(1/2); target: find DN
        n = 0.011  # uPVC/PVC smooth pipe
        s = req.gradient_percent / 100.0
        # Try standard DN sizes
        dns = [50, 75, 100, 150, 200, 250, 300]
        selected_dn = 100
        capacity_l_s = 0.0
        velocity_m_s = 0.0
        for dn in dns:
            r_m = (dn / 1000.0) / 4.0
            a_m2 = math.pi * (dn / 1000.0)**2 / 4.0
            q = (1 / n) * a_m2 * r_m**(2/3) * s**0.5
            cap = q * 1000.0
            v = q / a_m2
            if cap >= flow_l_s * 1.1:
                selected_dn = dn
                capacity_l_s = round(cap, 2)
                velocity_m_s = round(v, 2)
                break

        min_velocity = 0.75  # self-cleaning velocity
        self_cleaning = velocity_m_s >= min_velocity

        return {
            "status": "success",
            "region": req.region,
            "standard": standards.get(req.region, "BS EN 12056"),
            "system_type": req.system_type,
            "discharge_units": du,
            "design_flow_l_s": round(flow_l_s, 2),
            "gradient_percent": req.gradient_percent,
            "pipe_material": req.pipe_material,
            "selected_dn": selected_dn,
            "pipe_capacity_l_s": capacity_l_s,
            "pipe_velocity_m_s": velocity_m_s,
            "self_cleaning_velocity": self_cleaning,
            "min_velocity_m_s": min_velocity,
            "compliant": self_cleaning and capacity_l_s >= flow_l_s,
            "summary": (
                f"DN{selected_dn} {req.pipe_material} at {req.gradient_percent}% gradient | "
                f"Flow: {flow_l_s:.2f} L/s | Capacity: {capacity_l_s:.2f} L/s | "
                f"Velocity: {velocity_m_s:.2f} m/s {'✓ Self-cleaning' if self_cleaning else '⚠ Check gradient'} | "
                f"{standards.get(req.region, 'BS EN 12056')}"
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PumpSizingRequest(BaseModel):
    region: str = "gcc"
    system_type: str = "cold_water"  # cold_water | hot_water | chilled_water | condenser_water
    flow_rate_l_s: float = 2.0
    static_head_m: float = 20.0
    pipe_friction_loss_m: float = 10.0
    velocity_head_m: float = 0.5
    pump_efficiency: float = 0.75
    motor_efficiency: float = 0.92
    safety_factor: float = 1.15
    duty_standby: bool = True

@router.post("/pump-sizing", summary="Pump Sizing (CIBSE C / ASHRAE / IS 1011 / AS 2941)")
async def pump_sizing(req: PumpSizingRequest) -> Any:
    """Size a centrifugal pump — determines TDH, shaft power, and motor selection."""
    try:
        standards = {
            "gcc": "CIBSE Guide C / ASHRAE Applications / BS EN 806",
            "europe": "CIBSE Guide C / BS EN 806-3 / BREEAM",
            "india": "IS 1011 / NBC 2016 / BIS Standards",
            "australia": "AS 2941:2013 / AS/NZS 3500 / AIRAH DA",
        }
        tdh_m = req.static_head_m + req.pipe_friction_loss_m + req.velocity_head_m
        flow_m3_s = req.flow_rate_l_s / 1000.0
        hydraulic_power_kw = (1000 * 9.81 * flow_m3_s * tdh_m) / 1000.0
        shaft_power_kw = hydraulic_power_kw / req.pump_efficiency
        motor_power_kw = shaft_power_kw / req.motor_efficiency * req.safety_factor

        # Standard motor sizes (kW)
        std_motors = [0.18, 0.25, 0.37, 0.55, 0.75, 1.1, 1.5, 2.2, 3.0, 4.0,
                      5.5, 7.5, 11, 15, 18.5, 22, 30, 37, 45, 55, 75, 90, 110]
        selected_motor_kw = next((m for m in std_motors if m >= motor_power_kw), std_motors[-1])

        return {
            "status": "success",
            "region": req.region,
            "standard": standards.get(req.region, "CIBSE Guide C"),
            "system_type": req.system_type,
            "flow_rate_l_s": req.flow_rate_l_s,
            "flow_rate_m3_h": round(req.flow_rate_l_s * 3.6, 1),
            "static_head_m": req.static_head_m,
            "pipe_friction_loss_m": req.pipe_friction_loss_m,
            "total_dynamic_head_m": round(tdh_m, 1),
            "hydraulic_power_kw": round(hydraulic_power_kw, 2),
            "shaft_power_kw": round(shaft_power_kw, 2),
            "motor_power_kw": round(motor_power_kw, 2),
            "selected_motor_kw": selected_motor_kw,
            "pump_efficiency": req.pump_efficiency,
            "motor_efficiency": req.motor_efficiency,
            "duty_standby": req.duty_standby,
            "num_pumps": 2 if req.duty_standby else 1,
            "summary": (
                f"TDH: {tdh_m:.1f} m | Flow: {req.flow_rate_l_s:.2f} L/s | "
                f"Motor: {selected_motor_kw} kW selected | Duty+Standby: {'Yes' if req.duty_standby else 'No'} | "
                f"{standards.get(req.region, 'CIBSE Guide C')}"
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class HotWaterSystemRequest(BaseModel):
    region: str = "gcc"
    system_type: str = "domestic"  # domestic | solar_assisted | heat_pump | centralized
    num_occupants: int = 50
    hot_water_l_person_day: float = 60.0
    inlet_water_temp_c: float = 15.0
    storage_temp_c: float = 60.0
    delivery_temp_c: float = 55.0
    legionella_pasteurisation: bool = True
    recovery_time_hr: float = 4.0
    standby_loss_pct: float = 5.0

@router.post("/hot-water-system", summary="Hot Water System Design (CIBSE W / AS/NZS 3500.4 / IS 2065)")
async def hot_water_system(req: HotWaterSystemRequest) -> Any:
    """Size domestic hot water storage and heater/boiler output."""
    try:
        standards = {
            "gcc": "CIBSE TM13 / Dubai Municipality / BS 6700",
            "europe": "CIBSE Guide W / BS EN 806-2 / L8 Legionella",
            "india": "IS 2065:1983 / NBC 2016 Part 9 / BEE Star Rating",
            "australia": "AS/NZS 3500.4:2021 / NCC Volume One / WELS",
        }
        daily_demand_l = req.num_occupants * req.hot_water_l_person_day
        # Energy to heat tank
        delta_t = req.storage_temp_c - req.inlet_water_temp_c
        energy_kwh = (daily_demand_l * 4.186 * delta_t) / 3600.0
        energy_with_standby = energy_kwh * (1 + req.standby_loss_pct / 100.0)
        storage_l = daily_demand_l * 0.6  # store 60% of daily demand
        heater_kw = energy_kwh / req.recovery_time_hr

        # Std tank sizes
        std_tanks = [100, 150, 200, 300, 400, 500, 750, 1000, 1500, 2000, 3000]
        selected_tank_l = next((t for t in std_tanks if t >= storage_l), std_tanks[-1])

        return {
            "status": "success",
            "region": req.region,
            "standard": standards.get(req.region, "CIBSE Guide W"),
            "system_type": req.system_type,
            "num_occupants": req.num_occupants,
            "daily_demand_l": round(daily_demand_l, 0),
            "peak_hourly_demand_l": round(daily_demand_l / 8, 0),
            "delta_t_k": round(delta_t, 1),
            "energy_required_kwh_day": round(energy_with_standby, 1),
            "storage_volume_l": round(storage_l, 0),
            "selected_tank_l": selected_tank_l,
            "heater_output_kw": round(heater_kw, 1),
            "storage_temp_c": req.storage_temp_c,
            "delivery_temp_c": req.delivery_temp_c,
            "legionella_pasteurisation": req.legionella_pasteurisation,
            "legionella_risk": "LOW" if req.storage_temp_c >= 60 and req.legionella_pasteurisation else "HIGH",
            "summary": (
                f"Daily demand: {daily_demand_l:.0f} L | Storage: {selected_tank_l} L tank | "
                f"Heater: {heater_kw:.1f} kW | Energy: {energy_with_standby:.1f} kWh/day | "
                f"Legionella: {'Controlled' if req.storage_temp_c >= 60 else 'CHECK!'} | "
                f"{standards.get(req.region, 'CIBSE Guide W')}"
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Rainwater Harvesting ───────────────────────────────────────────────────────

class RainwaterHarvestingRequest(BaseModel):
    region: str = "gcc"
    sub_region: str = ""
    roof_area_m2: float = 1000.0
    annual_rainfall_mm: float = 120.0
    runoff_coefficient: float = 0.85
    filter_efficiency_pct: float = 90.0
    num_occupants: int = 200
    non_potable_l_person_day: float = 40.0
    storage_days: int = 7

class PlumbingTankSizingRequest(BaseModel):
    region: str = "gcc"
    sub_region: str = ""
    tank_type: str = "cold_water"
    num_occupants: int = 500
    dwelling_units: int = 0
    daily_demand_l_person: float = 200.0
    storage_hours: float = 24.0
    fire_reserve_l: float = 0.0
    tank_material: str = "GRP"
    operating_pressure_bar: float = 3.0


@router.post("/rainwater-harvesting", summary="Rainwater Harvesting System Sizing (BS 8515 / AS 3959 / NBC)")
async def rainwater_harvesting(req: RainwaterHarvestingRequest) -> Any:
    """Size a rainwater harvesting system: roof collection, first-flush, storage tank, and demand balance."""
    try:
        standards = {
            "gcc": "BS 8515:2009+A1:2013 / Dubai Green Building Regulations / Estidama Pearl",
            "europe": "BS 8515:2009+A1:2013 / BS EN 16941-1:2018 / CIRIA C626",
            "india": "NBC 2016 Part 9 / IS 15797 / CGWB Rainwater Harvesting Manual",
            "australia": "AS/NZS 3500.1 / NCC Volume One / BASIX / AS 4020",
        }
        rainfall_requirements = {
            "gcc": {"min_catchment_m2": 500, "min_storage_days": 5, "wq_filter": True},
            "europe": {"min_catchment_m2": 200, "min_storage_days": 21, "wq_filter": True},
            "india": {"min_catchment_m2": 100, "min_storage_days": 14, "wq_filter": True},
            "australia": {"min_catchment_m2": 150, "min_storage_days": 30, "wq_filter": True},
        }
        req_region = req.region.lower()
        reqs = rainfall_requirements.get(req_region, rainfall_requirements["gcc"])
        std = standards.get(req_region, standards["gcc"])

        # Annual harvestable volume
        annual_harvestable_m3 = (
            req.roof_area_m2 * (req.annual_rainfall_mm / 1000.0)
            * req.runoff_coefficient * (req.filter_efficiency_pct / 100.0)
        )
        monthly_harvestable_m3 = annual_harvestable_m3 / 12.0

        # Non-potable daily demand
        daily_non_potable_l = req.num_occupants * req.non_potable_l_person_day
        annual_non_potable_m3 = daily_non_potable_l * 365.0 / 1000.0

        # Demand offset
        demand_offset_pct = min(100.0, (annual_harvestable_m3 / annual_non_potable_m3) * 100.0) if annual_non_potable_m3 > 0 else 0.0

        # Storage tank sizing: cover n days of non-potable demand
        storage_volume_m3 = (daily_non_potable_l * req.storage_days) / 1000.0
        # Roof catchment check
        catchment_adequate = req.roof_area_m2 >= reqs["min_catchment_m2"]

        # First-flush volume: 2mm per m² of roof area
        first_flush_l = req.roof_area_m2 * 2.0

        # Pump sizing: peak flow = 1.5× average daily demand / 8 peak hours
        peak_flow_l_s = (daily_non_potable_l * 1.5) / (8.0 * 3600.0)

        # Standard tank sizes (m³)
        std_tanks_m3 = [2, 3, 5, 7.5, 10, 15, 20, 25, 30, 40, 50, 75, 100]
        selected_tank_m3 = next((t for t in std_tanks_m3 if t >= storage_volume_m3), std_tanks_m3[-1])

        compliance_checks = [
            {"check": "Catchment area adequate", "required": f"≥{reqs['min_catchment_m2']} m²", "actual": f"{req.roof_area_m2:.0f} m²", "status": "PASS" if catchment_adequate else "FAIL"},
            {"check": "Storage days", "required": f"≥{reqs['min_storage_days']} days", "actual": f"{req.storage_days} days", "status": "PASS" if req.storage_days >= reqs["min_storage_days"] else "INFO"},
            {"check": "First-flush diverter", "required": "2 mm/m² roof", "actual": f"{first_flush_l:.0f} L", "status": "PASS"},
            {"check": "WQ filtration", "required": "Required", "actual": "Included", "status": "PASS"},
            {"check": "Annual demand offset", "required": "≥30%", "actual": f"{demand_offset_pct:.1f}%", "status": "PASS" if demand_offset_pct >= 30 else "REVIEW"},
        ]

        return {
            "status": "success",
            "region": req.region,
            "sub_region": req.sub_region,
            "standard": std,
            "roof_area_m2": req.roof_area_m2,
            "annual_rainfall_mm": req.annual_rainfall_mm,
            "runoff_coefficient": req.runoff_coefficient,
            "filter_efficiency_pct": req.filter_efficiency_pct,
            "annual_harvestable_m3": round(annual_harvestable_m3, 1),
            "monthly_harvestable_m3": round(monthly_harvestable_m3, 1),
            "daily_non_potable_demand_l": round(daily_non_potable_l, 0),
            "annual_non_potable_demand_m3": round(annual_non_potable_m3, 1),
            "demand_offset_pct": round(demand_offset_pct, 1),
            "storage_volume_required_m3": round(storage_volume_m3, 1),
            "selected_tank_m3": selected_tank_m3,
            "first_flush_volume_l": round(first_flush_l, 0),
            "peak_flow_l_s": round(peak_flow_l_s, 3),
            "compliance_checks": compliance_checks,
            "summary": (
                f"Annual harvest: {annual_harvestable_m3:.1f} m³ | Demand: {annual_non_potable_m3:.1f} m³/yr | "
                f"Offset: {demand_offset_pct:.0f}% | Tank: {selected_tank_m3} m³ | "
                f"Standard: {std}"
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plumbing-tank-sizing", summary="Cold/Fire Water Tank Sizing (BS EN 806 / AS 3500 / NBC)")
async def plumbing_tank_sizing(req: PlumbingTankSizingRequest) -> Any:
    """Size cold water, fire reserve, or combined storage tanks for MEP projects."""
    try:
        standards = {
            "gcc": "BS EN 806-2 / Dubai Municipality Guidelines / NFPA 22 / CIBSE Guide G",
            "europe": "BS EN 806-2:2005 / BS 6700 / WRAS / BS EN 12845",
            "india": "IS 1172:1993 / NBC 2016 Part 9 / IS 9668 / CPWD Plumbing Manual",
            "australia": "AS/NZS 3500.1:2018 / NCC Volume One / AS 2118.1",
        }
        per_capita_l = {
            "gcc": 250, "europe": 150, "india": 135, "australia": 180,
        }
        req_region = req.region.lower()
        std = standards.get(req_region, standards["gcc"])
        default_pc = per_capita_l.get(req_region, 200)

        # Override if custom daily demand provided
        daily_demand_l = req.num_occupants * req.daily_demand_l_person
        dwelling_demand_l = req.dwelling_units * 450.0  # 450 L/dwelling/day per BS EN 806
        total_daily_demand_l = max(daily_demand_l, dwelling_demand_l)

        # Cold water storage volume
        cold_storage_l = total_daily_demand_l * (req.storage_hours / 24.0)

        # Fire reserve (if specified, taken as given)
        fire_reserve_l = req.fire_reserve_l

        # Gross tank volume
        total_volume_l = cold_storage_l + fire_reserve_l
        usable_pct = 0.90  # allow 10% unusable at bottom
        gross_volume_l = total_volume_l / usable_pct

        # Peak flow: 10% of daily demand per hour (diversity factor)
        peak_flow_l_min = (total_daily_demand_l * 0.10) / 60.0

        # Inlet (ball valve) flow — refill in 12 hours
        inlet_flow_l_s = cold_storage_l / (12.0 * 3600.0)

        # Standard tank sizes (litres)
        std_tanks_l = [1000, 1500, 2000, 3000, 5000, 7500, 10000, 15000, 20000,
                       25000, 30000, 40000, 50000, 75000, 100000, 150000, 200000]
        selected_tank_l = next((t for t in std_tanks_l if t >= gross_volume_l), std_tanks_l[-1])

        # Overflow pipe sizing (nominal bore)
        overflow_dn = 50 if gross_volume_l < 5000 else (80 if gross_volume_l < 25000 else 100)

        # Compliance checks
        storage_hrs_check = req.storage_hours >= (24.0 if req_region in ("gcc", "india") else 12.0)
        checks = [
            {"check": "Cold water storage adequacy", "required": f"≥{default_pc} L/person/day", "actual": f"{req.daily_demand_l_person:.0f} L/person", "status": "PASS" if req.daily_demand_l_person >= default_pc else "REVIEW"},
            {"check": "Storage duration", "required": "≥24 h (GCC/India) / ≥12 h (Eur/Aus)", "actual": f"{req.storage_hours:.0f} h", "status": "PASS" if storage_hrs_check else "REVIEW"},
            {"check": "Fire reserve separation", "required": "Dedicated zone or separate tank", "actual": "Included" if fire_reserve_l > 0 else "Not required", "status": "PASS"},
            {"check": "Overflow pipe", "required": "DN≥50 / unrestricted gravity discharge", "actual": f"DN{overflow_dn}", "status": "PASS"},
            {"check": "Tank material", "required": "Food-grade / WRAS approved", "actual": req.tank_material, "status": "PASS" if req.tank_material in ("GRP", "MDPE", "Stainless Steel", "Concrete") else "REVIEW"},
        ]

        return {
            "status": "success",
            "region": req.region,
            "sub_region": req.sub_region,
            "standard": std,
            "tank_type": req.tank_type,
            "num_occupants": req.num_occupants,
            "total_daily_demand_l": round(total_daily_demand_l, 0),
            "cold_storage_l": round(cold_storage_l, 0),
            "fire_reserve_l": round(fire_reserve_l, 0),
            "total_volume_required_l": round(total_volume_l, 0),
            "gross_tank_volume_l": round(gross_volume_l, 0),
            "selected_tank_l": selected_tank_l,
            "selected_tank_m3": round(selected_tank_l / 1000.0, 1),
            "peak_flow_l_min": round(peak_flow_l_min, 1),
            "inlet_flow_l_s": round(inlet_flow_l_s, 3),
            "overflow_pipe_dn_mm": overflow_dn,
            "tank_material": req.tank_material,
            "compliance_checks": checks,
            "summary": (
                f"Daily demand: {total_daily_demand_l:.0f} L | Cold storage: {cold_storage_l:.0f} L | "
                f"Fire reserve: {fire_reserve_l:.0f} L | Tank: {selected_tank_l:,} L ({selected_tank_l/1000:.1f} m³) | "
                f"Standard: {std}"
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
