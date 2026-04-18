"""
OpenMEP Cable Sizing Engine
============================
Implements cable current carrying capacity selection and verification
per the applicable regional standard, using the Standards Adapter pattern.

Supports: GCC (BS 7671), Europe (BS 7671), India (IS 3961/IS 732), Australia (AS/NZS 3008)
"""

import math
from dataclasses import dataclass, field
from typing import Optional
from backend.engines.adapters_factory import get_electrical_adapter
from backend.adapters.base_adapter import BaseElectricalAdapter


@dataclass
class CableSizingInput:
    """Input parameters for cable sizing calculation."""
    region: str                        # 'gcc', 'europe', 'india', 'australia'
    sub_region: str = ""               # e.g. 'dewa', 'uk', 'maharashtra', 'nsw'

    load_kw: float = 0.0               # Load in kilowatts
    power_factor: float = 0.85         # Power factor (0.1 – 1.0)
    phases: int = 3                    # Number of phases (1 or 3)
    voltage_v: Optional[float] = None  # Supply voltage (V) — auto-set from region if None

    cable_type: str = "XLPE_CU"       # Cable type key matching adapter's get_cable_types()
    installation_method: str = "C"     # Installation method key
    cable_length_m: float = 50.0       # Cable run length in metres
    number_of_runs: int = 1            # Parallel cable runs per circuit

    ambient_temp_c: Optional[float] = None  # Actual ambient °C — uses regional design value if None
    num_grouped_circuits: int = 1      # Number of cables grouped together
    cables_touching: bool = True       # Cables touching (True) or spaced

    circuit_type: str = "power"        # 'power' or 'lighting'
    demand_factor: float = 1.0         # Demand/diversity factor (0–1)
    starting_current_factor: float = 1.0  # Motor starting factor (1.0 = no motor)

    project_name: str = ""
    circuit_from: str = ""
    circuit_to: str = ""
    description: str = ""

    # For fault protection check
    fault_level_ka: Optional[float] = None  # Prospective fault level (kA)
    protection_time_s: float = 0.4    # Fault clearance time (s)


@dataclass
class CableSizingResult:
    """Complete output of a cable sizing calculation."""
    # Input summary
    region: str = ""
    standard: str = ""
    authority: str = ""
    project_name: str = ""
    circuit_from: str = ""
    circuit_to: str = ""

    # Electrical parameters
    load_kw: float = 0.0
    power_factor: float = 0.85
    phases: int = 3
    supply_voltage_v: float = 0.0
    design_current_ib_a: float = 0.0

    # Cable selection
    cable_type: str = ""
    cable_type_description: str = ""
    installation_method: str = ""
    installation_method_description: str = ""
    selected_size_mm2: float = 0.0
    tabulated_rating_it_a: float = 0.0
    ambient_temp_c: float = 0.0
    ca_factor: float = 1.0
    num_grouped: int = 1
    cg_factor: float = 1.0
    derated_rating_iz_a: float = 0.0

    # Voltage drop
    cable_length_m: float = 0.0
    voltage_drop_mv: float = 0.0
    voltage_drop_pct: float = 0.0
    voltage_drop_limit_pct: float = 0.0
    voltage_drop_pass: bool = True

    # Protection
    protection_device_a: float = 0.0
    protection_standard: str = ""

    # Earth conductor
    earth_conductor_mm2: float = 0.0
    earthing_standard: str = ""

    # Fault protection (if fault level provided)
    fault_level_ka: Optional[float] = None
    min_cpc_adiabatic_mm2: Optional[float] = None
    fault_protection_pass: Optional[bool] = None

    # Compliance
    current_check_pass: bool = True
    overall_compliant: bool = True
    compliance_statements: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    # Report sections
    calculation_summary: str = ""


def calculate_cable_sizing(inp: CableSizingInput) -> CableSizingResult:
    """
    Main cable sizing calculation function.

    Algorithm (BS 7671 / IS 732 / AS 3008 method):
    1. Calculate design current Ib from load
    2. Get tabulated current rating It from standard tables
    3. Apply derating: Ca (temperature) × Cg (grouping)
    4. Select smallest cable where Iz = It × Ca × Cg ≥ Ib
    5. Check voltage drop ≤ regional limit
    6. Check fault protection (if fault level given)
    7. Determine earth conductor size
    """
    result = CableSizingResult()

    # ── Initialise adapter ────────────────────────────────────────────────────
    adapter: BaseElectricalAdapter = get_electrical_adapter(inp.region, inp.sub_region)
    result.region = inp.region
    result.standard = adapter.cable_sizing_standard
    result.authority = getattr(adapter, "authority_name", adapter.standard_name)
    result.project_name = inp.project_name
    result.circuit_from = inp.circuit_from
    result.circuit_to = inp.circuit_to

    # ── Supply voltage ────────────────────────────────────────────────────────
    if inp.voltage_v:
        voltage = inp.voltage_v
    else:
        voltage = adapter.voltage_lv if inp.phases == 3 else adapter.voltage_phase
    result.supply_voltage_v = voltage

    # ── Design current Ib ─────────────────────────────────────────────────────
    if inp.phases == 3:
        ib = (inp.load_kw * 1000 * inp.demand_factor) / (math.sqrt(3) * voltage * inp.power_factor)
    else:
        ib = (inp.load_kw * 1000 * inp.demand_factor) / (voltage * inp.power_factor)

    # Account for number of parallel runs
    ib_per_run = ib / max(inp.number_of_runs, 1)
    result.design_current_ib_a = round(ib, 2)
    result.load_kw = inp.load_kw
    result.power_factor = inp.power_factor
    result.phases = inp.phases

    # ── Derating factors ──────────────────────────────────────────────────────
    ambient = inp.ambient_temp_c if inp.ambient_temp_c else adapter.design_ambient_temp_air
    ca = adapter.get_ambient_temp_correction(inp.cable_type, ambient)
    cg = adapter.get_grouping_correction(inp.num_grouped_circuits, inp.cables_touching)

    result.ambient_temp_c = ambient
    result.ca_factor = round(ca, 3)
    result.cg_factor = round(cg, 3)
    result.num_grouped = inp.num_grouped_circuits

    # ── Cable selection ───────────────────────────────────────────────────────
    standard_sizes = adapter.get_standard_cable_sizes()
    selected_size = None
    selected_it = None
    selected_iz = None

    for size in standard_sizes:
        try:
            it = adapter.get_current_rating(inp.cable_type, inp.installation_method, size)
        except (ValueError, IndexError):
            continue
        iz = it * ca * cg
        if iz >= ib_per_run:
            selected_size = size
            selected_it = it
            selected_iz = iz
            break

    if selected_size is None:
        # Use largest available
        selected_size = standard_sizes[-1]
        selected_it = adapter.get_current_rating(inp.cable_type, inp.installation_method, selected_size)
        selected_iz = selected_it * ca * cg
        result.warnings.append(
            f"⚠️ Design current {ib_per_run:.1f}A exceeds maximum cable rating. "
            f"Consider multiple parallel runs or higher-rated cable system."
        )

    result.cable_type = inp.cable_type
    result.cable_type_description = adapter.get_cable_types().get(inp.cable_type, inp.cable_type)
    result.installation_method = inp.installation_method
    result.installation_method_description = adapter.get_installation_methods().get(
        inp.installation_method, inp.installation_method
    )
    result.selected_size_mm2 = selected_size
    result.tabulated_rating_it_a = round(selected_it, 1)
    result.derated_rating_iz_a = round(selected_iz, 1)
    result.current_check_pass = selected_iz >= ib_per_run

    # ── Voltage drop ──────────────────────────────────────────────────────────
    vd_mv_am = adapter.get_voltage_drop_mv_am(inp.cable_type, selected_size, inp.phases)
    # Voltage drop (mV) = Ib × L × mV/A/m / 1000  (× 2 for single-phase already in table)
    vd_mv = ib_per_run * inp.cable_length_m * vd_mv_am / 1000  # in Volts
    vd_pct = (vd_mv / voltage) * 100

    vd_limit = adapter.get_voltage_drop_limit(inp.circuit_type)
    vd_pass = vd_pct <= vd_limit

    result.cable_length_m = inp.cable_length_m
    result.voltage_drop_mv = round(vd_mv * 1000, 1)  # Store in mV
    result.voltage_drop_pct = round(vd_pct, 2)
    result.voltage_drop_limit_pct = vd_limit
    result.voltage_drop_pass = vd_pass

    if not vd_pass:
        # Try next larger cable sizes to meet voltage drop
        for size in [s for s in standard_sizes if s > selected_size]:
            vd_mv_am_new = adapter.get_voltage_drop_mv_am(inp.cable_type, size, inp.phases)
            vd_mv_new = ib_per_run * inp.cable_length_m * vd_mv_am_new / 1000
            vd_pct_new = (vd_mv_new / voltage) * 100
            if vd_pct_new <= vd_limit:
                result.warnings.append(
                    f"⚠️ Voltage drop {vd_pct:.2f}% exceeds limit {vd_limit}%. "
                    f"Upsize to {size}mm² to achieve {vd_pct_new:.2f}% (within {vd_limit}% limit)."
                )
                break
        else:
            result.warnings.append(
                f"⚠️ Voltage drop {vd_pct:.2f}% exceeds {vd_limit}% limit even with largest cable. "
                f"Consider increasing number of parallel runs."
            )

    # ── Protection device ─────────────────────────────────────────────────────
    protection_a = adapter.get_next_protection_rating(ib)
    result.protection_device_a = protection_a
    result.protection_standard = adapter.protection_standard

    # ── Earth / CPC conductor ─────────────────────────────────────────────────
    earth_mm2 = adapter.get_earthing_conductor_size(selected_size)
    result.earth_conductor_mm2 = earth_mm2
    result.earthing_standard = adapter.wiring_standard

    # ── Fault protection (adiabatic) ──────────────────────────────────────────
    if inp.fault_level_ka:
        result.fault_level_ka = inp.fault_level_ka
        k = 143  # k factor for 90°C XLPE copper (BS 7671 / AS/NZS)
        if inp.region == "india":
            k = 143
        # S_min = sqrt(I²t) / k  where I in A, t in seconds
        i_fault = inp.fault_level_ka * 1000
        s_min = math.sqrt(i_fault**2 * inp.protection_time_s) / k
        result.min_cpc_adiabatic_mm2 = round(s_min, 1)
        result.fault_protection_pass = earth_mm2 >= s_min

    # ── Overall compliance ────────────────────────────────────────────────────
    result.overall_compliant = result.current_check_pass and result.voltage_drop_pass
    if result.fault_protection_pass is not None:
        result.overall_compliant = result.overall_compliant and result.fault_protection_pass

    # ── Compliance statements ─────────────────────────────────────────────────
    result.compliance_statements.append(
        adapter.format_compliance_statement(
            "Current Carrying Capacity",
            result.current_check_pass,
            f"Iz = {result.derated_rating_iz_a}A ≥ Ib = {result.design_current_ib_a}A "
            f"(Ca={ca:.3f} × Cg={cg:.3f} × It={selected_it:.1f}A)"
        )
    )
    result.compliance_statements.append(
        adapter.format_compliance_statement(
            "Voltage Drop",
            result.voltage_drop_pass,
            f"VD = {result.voltage_drop_pct}% {'≤' if vd_pass else '>'} {vd_limit}% "
            f"({result.voltage_drop_mv:.0f}mV over {inp.cable_length_m}m)"
        )
    )

    # ── Calculation summary ───────────────────────────────────────────────────
    result.calculation_summary = _build_summary(inp, result, adapter)

    return result


def _build_summary(inp: CableSizingInput, res: CableSizingResult, adapter: BaseElectricalAdapter) -> str:
    lines = [
        "═══════════════════════════════════════════════════════════",
        "  CABLE SIZING CALCULATION SHEET",
        f"  Standard: {res.standard}",
        f"  Authority: {res.authority}",
    ]
    if res.project_name:
        lines.append(f"  Project: {res.project_name}")
    if res.circuit_from or res.circuit_to:
        lines.append(f"  Circuit: {res.circuit_from} → {res.circuit_to}")
    lines += [
        "───────────────────────────────────────────────────────────",
        f"  Load: {res.load_kw} kW  |  PF: {res.power_factor}  |  "
        f"Voltage: {res.supply_voltage_v}V {'3-Phase' if res.phases == 3 else '1-Phase'}",
        f"  Design Current (Ib): {res.design_current_ib_a} A",
        "───────────────────────────────────────────────────────────",
        f"  Cable: {res.selected_size_mm2}mm² — {res.cable_type_description}",
        f"  Install Method: {res.installation_method_description}",
        f"  Ambient Temp: {res.ambient_temp_c}°C  |  Ca = {res.ca_factor}",
        f"  Grouped Circuits: {res.num_grouped}  |  Cg = {res.cg_factor}",
        f"  Tabulated Rating (It): {res.tabulated_rating_it_a} A",
        f"  Derated Rating (Iz): {res.derated_rating_iz_a} A  "
        f"{'✅' if res.current_check_pass else '❌'} {'≥' if res.current_check_pass else '<'} Ib",
        "───────────────────────────────────────────────────────────",
        f"  Cable Length: {res.cable_length_m} m",
        f"  Voltage Drop: {res.voltage_drop_pct}% ({res.voltage_drop_mv:.0f} mV)  "
        f"{'✅' if res.voltage_drop_pass else '❌'} "
        f"{'≤' if res.voltage_drop_pass else '>'} {res.voltage_drop_limit_pct}% limit",
        "───────────────────────────────────────────────────────────",
        f"  Protection Device: {res.protection_device_a:.0f}A  ({res.protection_standard})",
        f"  Earth Conductor: {res.earth_conductor_mm2}mm²  ({res.earthing_standard})",
    ]
    if res.fault_level_ka:
        lines.append(
            f"  Fault Level: {res.fault_level_ka}kA  |  Min CPC: {res.min_cpc_adiabatic_mm2}mm²  "
            f"{'✅' if res.fault_protection_pass else '❌'}"
        )
    lines += [
        "═══════════════════════════════════════════════════════════",
        f"  OVERALL: {'✅ COMPLIANT' if res.overall_compliant else '❌ NON-COMPLIANT'} "
        f"with {res.standard}",
        "═══════════════════════════════════════════════════════════",
    ]
    if res.warnings:
        lines.append("\n  WARNINGS:")
        for w in res.warnings:
            lines.append(f"  {w}")

    return "\n".join(lines)
