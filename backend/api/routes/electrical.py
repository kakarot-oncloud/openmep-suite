"""
FastAPI Electrical Engineering Calculation Routes
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Any, List, Optional

from backend.models.electrical import (
    CableSizingRequest, VoltageDropRequest, MaxDemandRequest, ShortCircuitRequest, LightingRequest,
)
from backend.engines.electrical.cable_sizing import CableSizingInput, calculate_cable_sizing
from backend.engines.electrical.voltage_drop import VoltageDrop, calculate_voltage_drop
from backend.engines.electrical.demand_load import LoadItem, calculate_maximum_demand
from backend.engines.electrical.short_circuit import ShortCircuitInput, calculate_short_circuit
from backend.engines.electrical.lighting import LightingInput, calculate_lighting
from backend.engines.electrical.pf_correction import PFCorrectionInput, calculate_pf_correction
from backend.engines.electrical.generator_sizing import (
    GeneratorSizingInput, GeneratorLoad, calculate_generator_sizing,
)
from backend.engines.electrical.panel_schedule import (
    PanelScheduleInput, CircuitItem, calculate_panel_schedule,
)
from backend.engines.electrical.ups_sizing import UPSSizingInput, UPSLoad, calculate_ups_sizing

router = APIRouter(prefix="/electrical", tags=["Electrical Engineering"])


# ─── Australia method/cable type normalization ─────────────────────────────────
# AS/NZS 3008 uses column references for installation methods and unique cable
# type identifiers. This mapping normalises generic BS 7671 / generic codes so
# all 4 regions can use the same default inputs without triggering 422 errors.
_AU_METHOD_MAP = {
    "A1": "col_6", "A2": "col_6", "B1": "col_6", "B2": "col_6",
    "C": "col_22", "D1": "col_13", "D2": "col_9",
    "E": "col_23", "F": "col_24",
}
_AU_CABLE_MAP = {
    "XLPE_CU": "X90_CU",
    "PVC_CU": "V75_CU",   # V-75 PVC Copper Multicore — AS/NZS 5000.1
    "XLPE_AL": "X90_AL",
}


def _normalise_australia(region: str, installation_method: str, cable_type: str):
    """Return (installation_method, cable_type) normalised for Australia region."""
    if region.lower() == "australia":
        installation_method = _AU_METHOD_MAP.get(installation_method.upper(), installation_method)
        cable_type = _AU_CABLE_MAP.get(cable_type.upper(), cable_type)
    return installation_method, cable_type


# ─── Pydantic request models for new engines ──────────────────────────────────

class PFCorrectionRequest(BaseModel):
    region: str = "gcc"
    sub_region: str = ""
    active_power_kw: float = Field(gt=0)
    existing_pf: float = Field(default=0.80, ge=0.1, le=1.0)
    target_pf: float = Field(default=0.95, ge=0.1, le=1.0)
    supply_voltage_v: Optional[float] = None
    phases: int = Field(default=3, description="1 or 3")
    num_transformers: int = 1
    transformer_kva: float = 1000.0
    apply_harmonic_derating: bool = False
    project_name: str = ""


class GeneratorLoadItem(BaseModel):
    description: str = ""
    kw: float = Field(gt=0)
    power_factor: float = Field(default=0.85, ge=0.1, le=1.0)
    demand_factor: float = Field(default=1.0, ge=0.1, le=1.0)
    load_type: str = "general"
    starting_method: str = "VFD"


class GeneratorSizingRequest(BaseModel):
    region: str = "gcc"
    sub_region: str = ""
    loads: List[GeneratorLoadItem]
    site_altitude_m: float = 0.0
    ambient_temp_c: Optional[float] = None
    gen_voltage: int = 400
    phases: int = 3
    rated_pf: float = 0.8
    supply_system: str = "standby"
    max_voltage_dip_pct: float = 15.0
    future_expansion_pct: float = 20.0
    project_name: str = ""


class PanelCircuitItem(BaseModel):
    circuit_no: str = ""
    description: str = ""
    load_kw: float = Field(default=0.0, ge=0)
    power_factor: float = Field(default=0.85, ge=0.1, le=1.0)
    demand_factor: float = Field(default=1.0, ge=0.1, le=1.0)
    phases: int = Field(default=1, description="1 or 3")
    circuit_type: str = "power"
    cable_type: str = "XLPE_CU"
    installation_method: str = "C"
    cable_length_m: float = Field(default=30.0, gt=0)
    space_reserved: bool = False


class PanelScheduleRequest(BaseModel):
    region: str = "gcc"
    sub_region: str = ""
    panel_name: str = "Distribution Board DB-01"
    panel_reference: str = "DB-01"
    location: str = ""
    fed_from: str = "MLVDB"
    supply_voltage_lv: float = 400.0
    incoming_cable_size_mm2: float = 150.0
    circuits: List[PanelCircuitItem]
    future_spare_pct: float = 20.0
    panel_kva_limit: Optional[float] = None
    project_name: str = ""
    engineer: str = ""
    drawing_ref: str = ""


class UPSLoadItem(BaseModel):
    description: str = ""
    kva: float = Field(gt=0)
    power_factor: float = Field(default=0.9, ge=0.1, le=1.0)
    quantity: int = 1
    is_critical: bool = True


class UPSSizingRequest(BaseModel):
    region: str = "gcc"
    sub_region: str = ""
    loads: List[UPSLoadItem]
    required_autonomy_min: int = Field(default=15, ge=1)
    input_voltage_v: int = 400
    output_voltage_v: int = 400
    phases: int = 3
    battery_technology: str = "VRLA_AGM"
    battery_voltage_dc: float = 240.0
    redundancy: str = "N"
    future_expansion_pct: float = 20.0
    efficiency_assumption: float = 0.92
    project_name: str = ""
    location: str = ""


@router.post("/cable-sizing", summary="Cable Sizing — All Regions")
async def cable_sizing(req: CableSizingRequest) -> Any:
    """
    Calculate cable size based on load, installation conditions, and regional standard.

    **Regions:**
    - `gcc`: BS 7671 / IEC 60364 — GCC (DEWA, ADDC, KAHRAMAA, SEC, MEW)
    - `europe`: BS 7671:2018+A2:2022 — UK & Europe
    - `india`: IS 3961 / IS 732 / IS 7098 — India (FRLS mandatory)
    - `australia`: AS/NZS 3008.1.1 / AS/NZS 3000 — Australia/NZ (MEN earthing)
    """
    eff_method, eff_cable = _normalise_australia(
        req.region.value, req.installation_method, req.cable_type
    )
    try:
        inp = CableSizingInput(
            region=req.region.value,
            sub_region=req.sub_region,
            load_kw=req.load_kw,
            power_factor=req.power_factor,
            phases=req.phases.value,
            voltage_v=req.voltage_v,
            cable_type=eff_cable,
            installation_method=eff_method,
            cable_length_m=req.cable_length_m,
            number_of_runs=req.number_of_runs,
            ambient_temp_c=req.ambient_temp_c,
            num_grouped_circuits=req.num_grouped_circuits,
            cables_touching=req.cables_touching,
            circuit_type=req.circuit_type.value,
            demand_factor=req.demand_factor,
            project_name=req.project_name,
            circuit_from=req.circuit_from,
            circuit_to=req.circuit_to,
            fault_level_ka=req.fault_level_ka,
            protection_time_s=req.protection_time_s,
        )
        result = calculate_cable_sizing(inp)
        return {
            "status": "success",
            "region": result.region,
            "standard": result.standard,
            "authority": result.authority,
            "project_name": result.project_name,
            "circuit_from": result.circuit_from,
            "circuit_to": result.circuit_to,
            "load_kw": result.load_kw,
            "power_factor": result.power_factor,
            "phases": result.phases,
            "supply_voltage_v": result.supply_voltage_v,
            "design_current_ib_a": result.design_current_ib_a,
            "cable_type": result.cable_type,
            "cable_type_description": result.cable_type_description,
            "installation_method": result.installation_method,
            "installation_method_description": result.installation_method_description,
            "selected_size_mm2": result.selected_size_mm2,
            "tabulated_rating_it_a": result.tabulated_rating_it_a,
            "ambient_temp_c": result.ambient_temp_c,
            "ca_factor": result.ca_factor,
            "num_grouped_circuits": result.num_grouped,
            "cg_factor": result.cg_factor,
            "derated_rating_iz_a": result.derated_rating_iz_a,
            "cable_length_m": result.cable_length_m,
            "voltage_drop_mv": result.voltage_drop_mv,
            "voltage_drop_pct": result.voltage_drop_pct,
            "voltage_drop_limit_pct": result.voltage_drop_limit_pct,
            "voltage_drop_pass": result.voltage_drop_pass,
            "protection_device_a": result.protection_device_a,
            "protection_standard": result.protection_standard,
            "earth_conductor_mm2": result.earth_conductor_mm2,
            "earthing_standard": result.earthing_standard,
            "fault_level_ka": result.fault_level_ka,
            "min_cpc_adiabatic_mm2": result.min_cpc_adiabatic_mm2,
            "fault_protection_pass": result.fault_protection_pass,
            "current_check_pass": result.current_check_pass,
            "overall_compliant": result.overall_compliant,
            "compliance_statements": result.compliance_statements,
            "warnings": result.warnings,
            "calculation_summary": result.calculation_summary,
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.post("/voltage-drop", summary="Voltage Drop Analysis")
async def voltage_drop(req: VoltageDropRequest) -> Any:
    """Check voltage drop for a known cable size."""
    _, eff_cable_vd = _normalise_australia(req.region.value, "C", req.cable_type)
    try:
        inp = VoltageDrop(
            region=req.region.value,
            sub_region=req.sub_region,
            cable_type=eff_cable_vd,
            conductor_size_mm2=req.conductor_size_mm2,
            cable_length_m=req.cable_length_m,
            design_current_a=req.design_current_a,
            phases=req.phases.value,
            circuit_type=req.circuit_type.value,
        )
        result = calculate_voltage_drop(inp)
        return {
            "status": "success",
            "conductor_size_mm2": result.conductor_size_mm2,
            "cable_length_m": result.cable_length_m,
            "design_current_a": result.design_current_a,
            "supply_voltage_v": result.supply_voltage_v,
            "vd_mv_am": result.vd_mv_am,
            "vd_total_mv": result.vd_total_mv,
            "vd_total_v": result.vd_total_v,
            "vd_percent": result.vd_percent,
            "vd_limit_percent": result.vd_limit_percent,
            "receiving_end_voltage_v": result.receiving_end_voltage_v,
            "compliant": result.compliant,
            "recommended_size_mm2": result.recommended_size_mm2,
            "recommended_vd_pct": result.recommended_vd_pct,
            "standard": result.standard,
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/maximum-demand", summary="Maximum Demand / Load Schedule")
async def maximum_demand(req: MaxDemandRequest) -> Any:
    """Calculate maximum demand from a load schedule."""
    try:
        loads = [
            LoadItem(
                description=item.description,
                quantity=item.quantity,
                unit_kw=item.unit_kw,
                power_factor=item.power_factor,
                demand_factor=item.demand_factor,
                load_type=item.load_type,
                phases=item.phases,
            )
            for item in req.loads
        ]
        result = calculate_maximum_demand(
            loads=loads,
            region=req.region.value,
            supply_voltage_lv=req.supply_voltage_lv,
            diversity_factor=req.diversity_factor,
            future_expansion_pct=req.future_expansion_pct,
        )
        return {
            "status": "success",
            "total_connected_kw": result.total_connected_kw,
            "total_connected_kva": result.total_connected_kva,
            "total_demand_kw": result.total_demand_kw,
            "total_demand_kva": result.total_demand_kva,
            "overall_power_factor": result.overall_power_factor,
            "total_demand_current_a": result.total_demand_current_a,
            "main_protection_a": result.main_protection_a,
            "transformer_kva_min": result.transformer_kva_min,
            "transformer_kva_recommended": result.transformer_kva_recommended,
            "breakdown_by_type": result.breakdown_by_type,
            "calculation_summary": result.calculation_summary,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/short-circuit", summary="Short Circuit Analysis (IEC 60909)")
async def short_circuit(req: ShortCircuitRequest) -> Any:
    """Calculate prospective short circuit currents by impedance method."""
    try:
        inp = ShortCircuitInput(
            region=req.region.value,
            transformer_kva=req.transformer_kva,
            transformer_impedance_pct=req.transformer_impedance_pct,
            lv_voltage=req.lv_voltage,
            cable_type=req.cable_type,
            cable_size_mm2=req.cable_size_mm2,
            cable_length_m=req.cable_length_m,
            upstream_fault_level_ka=req.upstream_fault_level_ka,
        )
        result = calculate_short_circuit(inp)
        return {
            "status": "success",
            "transformer_kva": result.transformer_kva,
            "isc_tx_3ph_ka": result.isc_tx_3ph_ka,
            "isc_tx_1ph_ka": result.isc_tx_1ph_ka,
            "isc_end_3ph_ka": result.isc_end_3ph_ka,
            "isc_end_1ph_ka": result.isc_end_1ph_ka,
            "ief_min_ka": result.ief_min_ka,
            "max_fault_duration_s": result.max_fault_duration_s,
            "min_cpc_adiabatic_mm2": result.min_cpc_adiabatic_mm2,
            "summary": result.summary,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lighting", summary="Interior Lighting Calculation (Lumen Method)")
async def lighting_calc(req: LightingRequest) -> Any:
    """Calculate interior lighting by the lumen method (CIE/CIBSE)."""
    try:
        inp = LightingInput(
            region=req.region.value,
            room_name=req.room_name,
            room_type=req.room_type,
            length_m=req.length_m,
            width_m=req.width_m,
            height_m=req.height_m,
            work_plane_height_m=req.work_plane_height_m,
            target_lux=req.target_lux,
            luminaire_type=req.luminaire_type,
            luminaire_lumens=req.luminaire_lumens,
            luminaire_watts=req.luminaire_watts,
            luminaire_efficiency=req.luminaire_efficiency,
            ceiling_reflectance=req.ceiling_reflectance,
            wall_reflectance=req.wall_reflectance,
            floor_reflectance=req.floor_reflectance,
            llf=req.llf,
        )
        result = calculate_lighting(inp)
        return {
            "status": "success",
            "room_name": result.room_name,
            "room_area_m2": result.room_area_m2,
            "room_index_k": result.room_index_k,
            "uf_coefficient": result.uf_coefficient,
            "llf": result.llf,
            "target_lux_em": result.target_lux_em,
            "num_luminaires": result.num_luminaires,
            "luminaires_per_row": result.luminaires_per_row,
            "num_rows": result.num_rows,
            "achieved_lux": result.achieved_lux,
            "uniformity_achieved": result.uniformity_achieved,
            "total_watts": result.total_watts,
            "lux_per_watt": result.lux_per_watt,
            "lpd_w_per_m2": result.lpd_w_per_m2,
            "lpd_limit_w_per_m2": result.lpd_limit_w_per_m2,
            "lpd_compliant": result.lpd_compliant,
            "standard_reference": result.standard_reference,
            "recommendations": result.recommendations,
            "summary": result.summary,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/standards", summary="List Available Standards by Region")
async def list_standards() -> Any:
    """Return all supported regional standards and installation methods."""
    return {
        "regions": {
            "gcc": {
                "name": "GCC (Gulf Cooperation Council)",
                "electrical_standard": "BS 7671:2018+A2:2022 / IEC 60364",
                "authorities": ["DEWA", "ADDC", "KAHRAMAA", "SEC/SBC", "MEW"],
                "cable_standard": "BS 7671 Table 4D5A (XLPE) / 4D2A (PVC)",
                "vd_limits": {"dewa_lighting": "3%", "dewa_power": "4%", "general": "3%/5%"},
                "ambient_air": "50°C (design)", "ambient_ground": "35°C (design)",
                "frequency": "50Hz", "voltage": "400/230V",
            },
            "europe": {
                "name": "Europe / United Kingdom",
                "electrical_standard": "BS 7671:2018+A2:2022 (18th Edition)",
                "authorities": ["DNO/DSO", "UKPN", "Western Power", "Eirgrid"],
                "cable_standard": "BS 7671 Appendix 4 Tables",
                "vd_limits": {"lighting": "3%", "power": "5%"},
                "ambient_air": "30°C (reference)", "ambient_ground": "20°C (reference)",
                "frequency": "50Hz", "voltage": "400/230V",
            },
            "india": {
                "name": "India",
                "electrical_standard": "IS 732:2019 / IS 3961:2011 / IS 7098",
                "authorities": ["CEA", "MSEDCL", "BESCOM", "TANGEDCO"],
                "cable_standard": "IS 3961 Part 2 / IS 7098 Part 1 (XLPE FRLS)",
                "vd_limits": {"lighting": "2.5%", "power": "5%"},
                "ambient_air": "45°C (reference)", "ambient_ground": "30°C (reference)",
                "frequency": "50Hz", "voltage": "415/240V",
                "notes": "3.5-core cables; FRLS mandatory per NBC 2016 Part 4",
            },
            "australia": {
                "name": "Australia / New Zealand",
                "electrical_standard": "AS/NZS 3000:2018 (Wiring Rules)",
                "authorities": ["Ausgrid", "Energex", "Western Power", "Vector NZ"],
                "cable_standard": "AS/NZS 3008.1.1:2017",
                "vd_limits": {"total": "5%"},
                "ambient_air": "40°C (reference)", "ambient_ground": "25°C (reference)",
                "frequency": "50Hz", "voltage": "400/230V",
                "notes": "MEN (TN-CS) earthing system; X-90 XLPE preferred",
            },
        }
    }


@router.get("/cable-sizing", summary="Cable Sizing — Quick Calculation via Query Params (GET)")
async def cable_sizing_get(
    region: str = Query(default="gcc", description="Region: gcc | europe | india | australia"),
    sub_region: str = Query(default="general", description="Sub-authority (e.g. dewa, sec, nsw)"),
    load_kw: float = Query(default=10.0, description="Connected load in kilowatts"),
    power_factor: float = Query(default=0.85, description="Load power factor (0.0–1.0)"),
    phases: int = Query(default=3, description="Number of phases: 1 or 3"),
    voltage_v: float = Query(default=415.0, description="Supply voltage in volts"),
    cable_type: str = Query(default="XLPE_CU", description="Cable insulation type"),
    installation_method: str = Query(default="C", description="BS 7671 installation reference method"),
    cable_length_m: float = Query(default=50.0, description="Cable run length in metres"),
    ambient_temp_c: float = Query(default=40.0, description="Ambient temperature in °C"),
    num_grouped_circuits: int = Query(default=1, description="Number of cables grouped together"),
) -> Any:
    """
    Quick cable sizing via HTTP GET with query parameters.
    Performs the full BS 7671 / regional standards calculation and returns
    the recommended cable size, current ratings, and voltage drop results.

    Supports all four regions:
    - `gcc`: BS 7671 / IEC 60364 — GCC countries (DEWA, ADDC, KAHRAMAA, SEC, MEW)
    - `europe`: BS 7671:2018+A2:2022 — UK & Europe
    - `india`: IS 3961 / IS 732 — India (FRLS mandatory)
    - `australia`: AS/NZS 3008.1.1 — Australia/NZ (MEN earthing)
    """
    # Normalise Australia-specific method codes and cable type names.
    effective_method, effective_cable_type = _normalise_australia(
        region, installation_method, cable_type
    )

    try:
        inp = CableSizingInput(
            region=region,
            sub_region=sub_region,
            load_kw=load_kw,
            power_factor=power_factor,
            phases=phases,
            voltage_v=voltage_v,
            cable_type=effective_cable_type,
            installation_method=effective_method,
            cable_length_m=cable_length_m,
            number_of_runs=1,
            ambient_temp_c=ambient_temp_c,
            num_grouped_circuits=num_grouped_circuits,
            cables_touching=True,
            circuit_type="power",
        )
        result = calculate_cable_sizing(inp)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cable sizing calculation error: {str(e)}")


@router.get("/cable-sizing/options", summary="Cable Sizing Input Options (GET)")
async def cable_sizing_options() -> Any:
    """Return all valid cable types, installation methods, and regions for cable sizing."""
    return {
        "cable_types": {
            "XLPE_CU": "XLPE Copper (90°C) — BS 7671 Table 4D5A",
            "PVC_CU": "PVC Copper (70°C) — BS 7671 Table 4D2A",
            "XLPE_AL": "XLPE Aluminium (90°C)",
            "FRLS_CU": "FRLS XLPE Copper (India IS 7098)",
            "X90_CU": "X-90 XLPE Copper (Australia AS/NZS 3008)",
        },
        "installation_methods": {
            "A1": "Enclosed in conduit in thermally insulating wall",
            "A2": "Enclosed in conduit in masonry wall",
            "B1": "Enclosed in conduit on wall / in trunking",
            "B2": "Enclosed in cable trunking",
            "C": "Direct clipped to surface / wall",
            "D1": "In conduit in ground",
            "D2": "Direct buried in ground",
            "E": "Free-air — single layer on perforated cable tray",
            "F": "Free-air — touching cables on horizontal cable tray",
        },
        "regions": ["gcc", "europe", "india", "australia"],
        "sub_regions": {
            "gcc": ["dewa", "addc", "kahramaa", "sec", "mew", "general"],
            "europe": ["uk", "ie", "de", "fr", "general"],
            "india": ["maharashtra", "karnataka", "tamil_nadu", "delhi", "general"],
            "australia": ["nsw", "qld", "vic", "wa", "sa", "general"],
        },
        "circuit_types": ["power", "lighting"],
        "standard_sizes_mm2": [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 630],
    }


@router.post("/pf-correction", summary="Power Factor Correction — Capacitor Bank Sizing")
async def pf_correction(req: PFCorrectionRequest) -> Any:
    """Calculate required capacitor bank kVAr to achieve target power factor."""
    try:
        inp = PFCorrectionInput(
            region=req.region,
            sub_region=req.sub_region,
            active_power_kw=req.active_power_kw,
            existing_pf=req.existing_pf,
            target_pf=req.target_pf,
            supply_voltage_v=req.supply_voltage_v,
            phases=req.phases,
            num_transformers=req.num_transformers,
            transformer_kva=req.transformer_kva,
            apply_harmonic_derating=req.apply_harmonic_derating,
            project_name=req.project_name,
        )
        result = calculate_pf_correction(inp)
        return {
            "status": "success",
            "region": result.region,
            "standard": result.standard,
            "active_power_kw": result.active_power_kw,
            "existing_pf": result.existing_pf,
            "target_pf": result.target_pf,
            "supply_voltage_v": result.supply_voltage_v,
            "existing_reactive_kvar": result.existing_reactive_kvar,
            "existing_apparent_kva": result.existing_apparent_kva,
            "existing_current_a": result.existing_current_a,
            "required_correction_kvar": result.required_correction_kvar,
            "standard_bank_kvar": result.standard_bank_kvar,
            "capacitor_current_a": result.capacitor_current_a,
            "corrected_pf": result.corrected_pf,
            "corrected_apparent_kva": result.corrected_apparent_kva,
            "corrected_current_a": result.corrected_current_a,
            "current_reduction_a": result.current_reduction_a,
            "current_reduction_pct": result.current_reduction_pct,
            "apfc_steps": result.apfc_steps,
            "apfc_step_kvar": result.apfc_step_kvar,
            "apfc_panel_kvar": result.apfc_panel_kvar,
            "utility_min_pf": result.utility_min_pf,
            "compliant": result.compliant,
            "tariff_note": result.tariff_note,
            "loss_reduction_kw": result.loss_reduction_kw,
            "annual_saving_kwh": result.annual_saving_kwh,
            "summary": result.summary,
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generator-sizing", summary="Standby / Prime Generator Sizing (ISO 8528)")
async def generator_sizing(req: GeneratorSizingRequest) -> Any:
    """Calculate required generator kVA rating from a load schedule with site derating."""
    try:
        loads = [
            GeneratorLoad(
                description=ld.description,
                kw=ld.kw,
                power_factor=ld.power_factor,
                demand_factor=ld.demand_factor,
                load_type=ld.load_type,
                starting_method=ld.starting_method,
            )
            for ld in req.loads
        ]
        inp = GeneratorSizingInput(
            region=req.region,
            sub_region=req.sub_region,
            loads=loads,
            site_altitude_m=req.site_altitude_m,
            ambient_temp_c=req.ambient_temp_c,
            gen_voltage=req.gen_voltage,
            phases=req.phases,
            rated_pf=req.rated_pf,
            supply_system=req.supply_system,
            max_voltage_dip_pct=req.max_voltage_dip_pct,
            project_name=req.project_name,
        )
        result = calculate_generator_sizing(inp)
        return {
            "status": "success",
            "region": result.region,
            "standard": result.standard,
            "supply_system": result.supply_system,
            "total_demand_kw": result.total_demand_kw,
            "total_demand_kva": result.total_demand_kva,
            "weighted_pf": result.weighted_pf,
            "site_altitude_m": result.site_altitude_m,
            "site_ambient_c": result.site_ambient_c,
            "altitude_derating_pct": result.altitude_derating_pct,
            "temp_derating_pct": result.temp_derating_pct,
            "total_derating_pct": result.total_derating_pct,
            "derated_demand_kva": result.derated_demand_kva,
            "required_kva_running": result.required_kva_running,
            "required_kva_starting": result.required_kva_starting,
            "design_kva": result.design_kva,
            "standard_kva": result.standard_kva,
            "standard_kw": result.standard_kw,
            "largest_motor_kw": result.largest_motor_kw,
            "largest_motor_start_kva": result.largest_motor_start_kva,
            "motor_start_method": result.motor_start_method,
            "step_load_voltage_dip_pct": result.step_load_voltage_dip_pct,
            "step_load_ok": result.step_load_ok,
            "fuel_consumption_l_hr": result.fuel_consumption_l_hr,
            "tank_capacity_24h_l": result.tank_capacity_24h_l,
            "subtransient_fault_ka": result.subtransient_fault_ka,
            "note": result.note,
            "summary": result.summary,
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/panel-schedule", summary="Distribution Board / Panelboard Schedule")
async def panel_schedule(req: PanelScheduleRequest) -> Any:
    """Generate a complete distribution board schedule with cable sizing and load balancing."""
    try:
        circuits = []
        for c in req.circuits:
            eff_method, eff_cable = _normalise_australia(
                req.region, c.installation_method, c.cable_type
            )
            circuits.append(CircuitItem(
                circuit_no=c.circuit_no,
                description=c.description,
                load_kw=c.load_kw,
                power_factor=c.power_factor,
                demand_factor=c.demand_factor,
                phases=c.phases,
                circuit_type=c.circuit_type,
                cable_type=eff_cable,
                installation_method=eff_method,
                cable_length_m=c.cable_length_m,
                space_reserved=c.space_reserved,
            ))
        inp = PanelScheduleInput(
            region=req.region,
            sub_region=req.sub_region,
            panel_name=req.panel_name,
            panel_reference=req.panel_reference,
            location=req.location,
            fed_from=req.fed_from,
            supply_voltage_lv=req.supply_voltage_lv,
            incoming_cable_size_mm2=req.incoming_cable_size_mm2,
            circuits=circuits,
            future_spare_pct=req.future_spare_pct,
            panel_kva_limit=req.panel_kva_limit,
            project_name=req.project_name,
            engineer=req.engineer,
            drawing_ref=req.drawing_ref,
        )
        result = calculate_panel_schedule(inp)
        return {
            "status": "success",
            "region": result.region,
            "standard": result.standard,
            "panel_name": result.panel_name,
            "panel_reference": result.panel_reference,
            "num_circuits": result.num_circuits,
            "num_ways": result.num_ways,
            "total_connected_kw": result.total_connected_kw,
            "total_demand_kw": result.total_demand_kw,
            "total_demand_kva": result.total_demand_kva,
            "overall_pf": result.overall_pf,
            "incomer_current_a": result.incomer_current_a,
            "incomer_protection_a": result.incomer_protection_a,
            "phase_a_kw": result.phase_a_kw,
            "phase_b_kw": result.phase_b_kw,
            "phase_c_kw": result.phase_c_kw,
            "phase_imbalance_pct": result.phase_imbalance_pct,
            "phase_balanced": result.phase_balanced,
            "spare_pct": result.spare_pct,
            "compliant": result.compliant,
            "circuits": [
                {
                    "circuit_no": c.circuit_no,
                    "description": c.description,
                    "load_kw": c.load_kw,
                    "demand_kw": c.demand_kw,
                    "demand_kva": c.demand_kva,
                    "current_a": c.current_a,
                    "protection_a": c.protection_a,
                    "cable_size_mm2": c.cable_size_mm2,
                    "vd_percent": c.vd_percent,
                    "phases": c.phases,
                    "space_reserved": bool(c.space_reserved),
                    "compliant": bool(c.compliant),
                    "notes": c.notes,
                }
                for c in result.circuits
            ],
            "summary": result.summary,
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ups-sizing", summary="UPS Sizing — IEC 62040 Battery Autonomy")
async def ups_sizing(req: UPSSizingRequest) -> Any:
    """Size a UPS system and verify battery autonomy for critical loads."""
    try:
        loads = [
            UPSLoad(
                description=ld.description,
                kva=ld.kva,
                power_factor=ld.power_factor,
                quantity=ld.quantity,
                is_critical=ld.is_critical,
            )
            for ld in req.loads
        ]
        inp = UPSSizingInput(
            region=req.region,
            sub_region=req.sub_region,
            loads=loads,
            required_autonomy_min=req.required_autonomy_min,
            input_voltage_v=req.input_voltage_v,
            output_voltage_v=req.output_voltage_v,
            phases=req.phases,
            battery_technology=req.battery_technology,
            battery_voltage_dc=req.battery_voltage_dc,
            redundancy=req.redundancy,
            future_expansion_pct=req.future_expansion_pct,
            efficiency_assumption=req.efficiency_assumption,
            project_name=req.project_name,
            location=req.location,
        )
        result = calculate_ups_sizing(inp)
        return {
            "status": "success",
            "region": result.region,
            "standard": result.standard,
            "total_load_kva": result.total_load_kva,
            "total_load_kw": result.total_load_kw,
            "weighted_pf": result.weighted_pf,
            "design_kva": result.design_kva,
            "selected_kva": result.selected_kva,
            "selected_kw": result.selected_kw,
            "num_ups_units": result.num_ups_units,
            "redundancy": result.redundancy,
            "loading_pct": result.loading_pct,
            "battery_technology": result.battery_technology,
            "battery_voltage_dc": result.battery_voltage_dc,
            "battery_capacity_ah": result.battery_capacity_ah,
            "num_battery_strings": result.num_battery_strings,
            "num_cells_per_string": result.num_cells_per_string,
            "battery_room_note": result.battery_room_note,
            "charger_current_a": result.charger_current_a,
            "recharge_time_h": result.recharge_time_h,
            "required_autonomy_min": result.required_autonomy_min,
            "achievable_autonomy_min": result.achievable_autonomy_min,
            "autonomy_ok": result.autonomy_ok,
            "regional_min_autonomy_min": result.regional_min_autonomy_min,
            "compliant": result.compliant,
            "note": result.note,
            "summary": result.summary,
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
