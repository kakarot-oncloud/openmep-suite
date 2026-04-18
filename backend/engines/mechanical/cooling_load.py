"""
HVAC Cooling Load Calculation Engine
Simplified Heat Balance Method — ASHRAE/CIBSE/ECBC/NCC aligned.
Supports all 4 OpenMEP regions with appropriate design conditions.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ZoneInput:
    """Input for a single HVAC zone / room."""
    zone_name: str = "Zone 1"
    zone_type: str = "office"      # 'office', 'retail', 'hotel_room', 'corridor', 'server_room', etc.

    # Geometry
    floor_area_m2: float = 100.0
    height_m: float = 3.0
    volume_m3: Optional[float] = None  # Calculated if None

    # Fabric
    glass_area_m2: float = 10.0
    glass_u_value: float = 2.8
    glass_shgc: float = 0.4         # Solar Heat Gain Coefficient
    glass_orientation: str = "W"   # N/NE/E/SE/S/SW/W/NW
    wall_area_m2: float = 80.0
    wall_u_value: float = 0.45
    roof_area_m2: float = 0.0       # only if top floor
    roof_u_value: float = 0.35
    floor_area_on_ground_m2: float = 0.0

    # Internal gains
    occupancy: int = 10
    metabolic_rate_w: float = 90.0  # Seated office work = 90W sensible
    equipment_w_m2: float = 20.0   # IT/office equipment
    lighting_w_m2: float = 10.0

    # Fresh air (ventilation)
    fresh_air_l_s_person: float = 10.0  # L/s per person (EN 15251 Cat II)

    # Efficiency
    cop: float = 3.0                # Chiller/DX COP


@dataclass
class CoolingLoadResult:
    zone_name: str = ""
    outdoor_db_c: float = 0.0
    outdoor_wb_c: float = 0.0
    indoor_db_c: float = 24.0
    indoor_rh_pct: float = 50.0

    # Load breakdown (W)
    solar_gain_w: float = 0.0
    conduction_glass_w: float = 0.0
    conduction_wall_w: float = 0.0
    conduction_roof_w: float = 0.0
    internal_occupants_w: float = 0.0
    internal_lighting_w: float = 0.0
    internal_equipment_w: float = 0.0
    ventilation_load_w: float = 0.0

    total_sensible_w: float = 0.0
    total_latent_w: float = 0.0
    total_cooling_w: float = 0.0
    total_cooling_kw: float = 0.0
    total_cooling_tr: float = 0.0  # Tons of Refrigeration

    floor_area_m2: float = 0.0
    cooling_w_per_m2: float = 0.0
    cooling_tr_per_100m2: float = 0.0

    supply_airflow_l_s: float = 0.0
    fresh_air_l_s: float = 0.0
    room_air_changes_per_hour: float = 0.0

    chiller_power_kw: float = 0.0
    cop: float = 3.0

    standard_reference: str = ""
    summary: str = ""


# Solar heat gain table by orientation (W/m² through clear glass, peak summer)
# GCC at peak solar: higher values; Europe/India/Australia adjusted
SOLAR_GAIN_W_M2 = {
    "gcc":       {"N": 90,  "NE": 320, "E": 480, "SE": 420, "S": 200, "SW": 420, "W": 480, "NW": 320, "H": 800},
    "europe":    {"N": 60,  "NE": 200, "E": 350, "SE": 320, "S": 250, "SW": 320, "W": 350, "NW": 200, "H": 650},
    "india":     {"N": 80,  "NE": 300, "E": 450, "SE": 400, "S": 250, "SW": 400, "W": 450, "NW": 300, "H": 750},
    "australia": {"N": 250, "NE": 380, "E": 450, "SE": 320, "S": 120, "SW": 320, "W": 450, "NW": 380, "H": 700},
}

DESIGN_CONDITIONS = {
    "gcc":       {"db": 46, "wb": 28, "indoor_db": 24, "indoor_rh": 50, "standard": "ASHRAE 55 / CIBSE A / DEWA"},
    "europe":    {"db": 32, "wb": 23, "indoor_db": 24, "indoor_rh": 50, "standard": "EN 15251 / CIBSE Guide A"},
    "india":     {"db": 42, "wb": 28, "indoor_db": 24, "indoor_rh": 55, "standard": "NBC 2016 Part 8 / ASHRAE 55"},
    "australia": {"db": 38, "wb": 27, "indoor_db": 24, "indoor_rh": 50, "standard": "AS 1668.2 / ASHRAE 55 / NCC"},
}


def calculate_cooling_load(
    zone: ZoneInput,
    region: str = "gcc",
    safety_factor: float = 1.10,
) -> CoolingLoadResult:
    """Calculate cooling load by simplified heat balance method."""
    cond = DESIGN_CONDITIONS.get(region, DESIGN_CONDITIONS["gcc"])
    res = CoolingLoadResult(
        zone_name=zone.zone_name,
        outdoor_db_c=cond["db"],
        outdoor_wb_c=cond["wb"],
        indoor_db_c=cond["indoor_db"],
        indoor_rh_pct=cond["indoor_rh"],
        floor_area_m2=zone.floor_area_m2,
        standard_reference=cond["standard"],
        cop=zone.cop,
    )

    dt = cond["db"] - cond["indoor_db"]  # ΔT outdoor-indoor

    # ── Solar gain ────────────────────────────────────────────────────────────
    solar_table = SOLAR_GAIN_W_M2.get(region, SOLAR_GAIN_W_M2["gcc"])
    isol = solar_table.get(zone.glass_orientation.upper(), 400)
    solar_w = zone.glass_area_m2 * isol * zone.glass_shgc
    res.solar_gain_w = round(solar_w, 1)

    # ── Conduction through glass ──────────────────────────────────────────────
    cond_glass_w = zone.glass_area_m2 * zone.glass_u_value * dt
    res.conduction_glass_w = round(cond_glass_w, 1)

    # ── Conduction through walls ──────────────────────────────────────────────
    wall_area_opaque = zone.wall_area_m2 - zone.glass_area_m2
    cond_wall_w = wall_area_opaque * zone.wall_u_value * dt
    res.conduction_wall_w = round(cond_wall_w, 1)

    # ── Conduction through roof ───────────────────────────────────────────────
    sol_air_temp = cond["db"] + 10  # Solar air temperature allowance for roof
    cond_roof_w = zone.roof_area_m2 * zone.roof_u_value * (sol_air_temp - cond["indoor_db"])
    res.conduction_roof_w = round(cond_roof_w, 1)

    # ── Internal gains — occupants ────────────────────────────────────────────
    occ_sensible_w = zone.occupancy * zone.metabolic_rate_w
    occ_latent_w = zone.occupancy * 55   # Latent from respiration/perspiration
    res.internal_occupants_w = round(occ_sensible_w, 1)

    # ── Internal gains — lighting ─────────────────────────────────────────────
    lighting_w = zone.floor_area_m2 * zone.lighting_w_m2
    res.internal_lighting_w = round(lighting_w, 1)

    # ── Internal gains — equipment ────────────────────────────────────────────
    equipment_w = zone.floor_area_m2 * zone.equipment_w_m2
    res.internal_equipment_w = round(equipment_w, 1)

    # ── Ventilation load ──────────────────────────────────────────────────────
    fresh_l_s = zone.occupancy * zone.fresh_air_l_s_person
    fresh_m3_s = fresh_l_s / 1000
    rho = 1.2  # kg/m³ air density
    cp = 1006  # J/kg·K specific heat of air
    vent_sensible_w = rho * fresh_m3_s * cp * dt
    # Latent ventilation load
    omega_out = 0.019  # humidity ratio outdoor (approx for GCC/India peaks)
    omega_in = 0.010
    vent_latent_w = rho * fresh_m3_s * 2501000 * (omega_out - omega_in)

    res.ventilation_load_w = round(vent_sensible_w + max(vent_latent_w, 0), 1)
    res.fresh_air_l_s = round(fresh_l_s, 1)

    # ── Totals ────────────────────────────────────────────────────────────────
    total_sensible_w = (
        solar_w + cond_glass_w + cond_wall_w + cond_roof_w +
        occ_sensible_w + lighting_w + equipment_w + vent_sensible_w
    )
    total_latent_w = occ_latent_w + max(vent_latent_w, 0)
    total_w = (total_sensible_w + total_latent_w) * safety_factor

    res.total_sensible_w = round(total_sensible_w, 0)
    res.total_latent_w = round(total_latent_w, 0)
    res.total_cooling_w = round(total_w, 0)
    res.total_cooling_kw = round(total_w / 1000, 2)
    res.total_cooling_tr = round(total_w / 3517, 2)  # 1 TR = 3517 W

    # ── Derived metrics ───────────────────────────────────────────────────────
    res.cooling_w_per_m2 = round(total_w / zone.floor_area_m2, 1)
    res.cooling_tr_per_100m2 = round((total_w / zone.floor_area_m2 * 100) / 3517, 2)
    res.chiller_power_kw = round(total_w / 1000 / zone.cop, 2)

    # Air flow
    vol = zone.volume_m3 or (zone.floor_area_m2 * zone.height_m)
    # Q = Q_sens / (ρ × Cp × ΔT_supply)  where ΔT_supply = 8°C typical
    dt_supply = 8.0
    supply_m3_s = total_sensible_w / (rho * cp * dt_supply)
    supply_l_s = supply_m3_s * 1000
    ach = (supply_m3_s * 3600) / vol
    res.supply_airflow_l_s = round(supply_l_s, 1)
    res.room_air_changes_per_hour = round(ach, 1)

    # Summary
    lines = [
        "═══════════════════════════════════════════════════════════",
        f"  COOLING LOAD CALCULATION — {zone.zone_name}",
        f"  Standard: {cond['standard']}",
        "───────────────────────────────────────────────────────────",
        f"  Design Conditions: ODB {cond['db']}°C / OWB {cond['wb']}°C",
        f"  Indoor: {cond['indoor_db']}°C / {cond['indoor_rh']}% RH",
        f"  Floor Area: {zone.floor_area_m2}m²  |  Height: {zone.height_m}m",
        "───────────────────────────────────────────────────────────",
        "  LOAD BREAKDOWN:",
        f"    Solar gain (glass):    {solar_w:>10,.0f} W",
        f"    Conduction (glass):    {cond_glass_w:>10,.0f} W",
        f"    Conduction (wall):     {cond_wall_w:>10,.0f} W",
        f"    Conduction (roof):     {cond_roof_w:>10,.0f} W",
        f"    Occupants (sensible):  {occ_sensible_w:>10,.0f} W",
        f"    Lighting:              {lighting_w:>10,.0f} W",
        f"    Equipment:             {equipment_w:>10,.0f} W",
        f"    Ventilation:           {res.ventilation_load_w:>10,.0f} W",
        f"    Safety factor ({safety_factor}):   applied",
        "───────────────────────────────────────────────────────────",
        f"  Total Sensible:  {res.total_sensible_w:>10,.0f} W",
        f"  Total Latent:    {res.total_latent_w:>10,.0f} W",
        f"  TOTAL COOLING:   {res.total_cooling_w:>10,.0f} W  =  {res.total_cooling_kw:.2f} kW  =  {res.total_cooling_tr:.2f} TR",
        f"  Cooling Density: {res.cooling_w_per_m2:.1f} W/m²  ({res.cooling_tr_per_100m2:.2f} TR/100m²)",
        "───────────────────────────────────────────────────────────",
        f"  Supply Air Flow: {res.supply_airflow_l_s:.1f} L/s  ({res.room_air_changes_per_hour:.1f} ACH)",
        f"  Fresh Air:       {res.fresh_air_l_s:.1f} L/s",
        f"  Chiller Power:   {res.chiller_power_kw:.2f} kW  (COP = {zone.cop})",
        "═══════════════════════════════════════════════════════════",
    ]
    res.summary = "\n".join(lines)

    return res
