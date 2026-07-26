// Config-driven calculator registry.
//
// Every calculator is a plain config object: input fields, the API endpoint,
// an optional payload transform, and a function that maps the API response to a
// display view. The generic <CalculatorPage> renders any of them, so adding a
// calculator means adding a config here — no new page component.

import { REGIONS } from "../lib/regions.ts";

export type FieldType = "number" | "text" | "select";

export interface Field {
  name: string;
  label: string;
  type: FieldType;
  default: string | number;
  options?: { value: string | number; label: string }[];
  step?: number;
  hint?: string;
}

export interface RowsField {
  name: string;
  label: string;
  addLabel: string;
  itemFields: Field[];
  default: Record<string, string | number>[];
}

export interface ResultView {
  headline?: { label: string; value: React.ReactNode; unit?: string };
  badge?: { ok: boolean; text: string };
  stats?: { label: string; value: React.ReactNode; unit?: string }[];
  breakdown?: { title: string; items: { label: string; value: number }[] };
  warnings?: string[];
  note?: string;
}

export type Discipline = "Electrical" | "Mechanical" | "Plumbing" | "Fire" | "Reports";

export interface CalculatorConfig {
  slug: string;
  name: string;
  discipline: Discipline;
  icon: string;
  standard: string;
  blurb: string;
  endpoint: string;
  fields: Field[];
  rows?: RowsField;
  buildPayload?: (v: Record<string, unknown>) => unknown;
  result: (data: Record<string, unknown>) => ResultView;
}

// Helpers -------------------------------------------------------------------
const regionField: Field = {
  name: "region",
  label: "Region",
  type: "select",
  default: "gcc",
  options: REGIONS.map((r) => ({ value: r.code, label: `${r.short} — ${r.standard}` })),
};
const n = (v: unknown): number => (typeof v === "number" ? v : Number(v) || 0);

// ── Electrical ───────────────────────────────────────────────────────────────

const voltageDrop: CalculatorConfig = {
  slug: "voltage-drop",
  name: "Voltage Drop",
  discipline: "Electrical",
  icon: "⚡",
  standard: "IEC 60364-5-52 / BS 7671 App 4",
  blurb: "Voltage drop for a known cable size, with an upsize recommendation if it exceeds the regional limit.",
  endpoint: "/api/electrical/voltage-drop",
  fields: [
    regionField,
    { name: "conductor_size_mm2", label: "Conductor size (mm²)", type: "number", default: 16 },
    { name: "design_current_a", label: "Design current (A)", type: "number", default: 80 },
    { name: "cable_length_m", label: "Length (m)", type: "number", default: 100 },
    { name: "phases", label: "Phases", type: "select", default: 3, options: [{ value: 3, label: "3-phase" }, { value: 1, label: "1-phase" }] },
    { name: "cable_type", label: "Cable type", type: "select", default: "XLPE_CU", options: [{ value: "XLPE_CU", label: "XLPE Copper" }, { value: "PVC_CU", label: "PVC Copper" }] },
    { name: "circuit_type", label: "Circuit type", type: "select", default: "power", options: [{ value: "power", label: "Power" }, { value: "lighting", label: "Lighting" }] },
  ],
  result: (d) => ({
    headline: { label: "Voltage drop", value: <span className={d.compliant ? "text-success" : "text-danger"}>{n(d.vd_percent)}%</span>, unit: `/ ${n(d.vd_limit_percent)}%` },
    badge: { ok: Boolean(d.compliant), text: d.compliant ? "Within limit" : "Exceeds limit" },
    stats: [
      { label: "Total drop", value: n(d.vd_total_v), unit: "V" },
      { label: "Receiving-end V", value: n(d.receiving_end_voltage_v), unit: "V" },
      { label: "mV/A/m", value: n(d.vd_mv_am) },
      ...(d.recommended_size_mm2 ? [{ label: "Upsize to", value: n(d.recommended_size_mm2), unit: "mm²" }] : []),
    ],
    note: String(d.standard ?? ""),
  }),
};

const maximumDemand: CalculatorConfig = {
  slug: "maximum-demand",
  name: "Maximum Demand",
  discipline: "Electrical",
  icon: "⚡",
  standard: "IEE / DEWA / IS 18-1",
  blurb: "Maximum demand and recommended transformer size from a load schedule with diversity.",
  endpoint: "/api/electrical/maximum-demand",
  fields: [
    regionField,
    { name: "supply_voltage_lv", label: "Supply voltage (V)", type: "number", default: 400 },
    { name: "diversity_factor", label: "Diversity factor", type: "number", default: 1.0, step: 0.05 },
    { name: "future_expansion_pct", label: "Future expansion (%)", type: "number", default: 20 },
  ],
  rows: {
    name: "loads",
    label: "Load schedule",
    addLabel: "Add load",
    itemFields: [
      { name: "description", label: "Description", type: "text", default: "Lighting" },
      { name: "quantity", label: "Qty", type: "number", default: 1 },
      { name: "unit_kw", label: "kW each", type: "number", default: 10 },
      { name: "power_factor", label: "PF", type: "number", default: 0.9, step: 0.01 },
      { name: "demand_factor", label: "DF", type: "number", default: 0.8, step: 0.05 },
    ],
    default: [
      { description: "Lighting", quantity: 1, unit_kw: 12, power_factor: 0.95, demand_factor: 0.9 },
      { description: "Power / sockets", quantity: 3, unit_kw: 20, power_factor: 0.85, demand_factor: 0.7 },
      { description: "HVAC", quantity: 2, unit_kw: 30, power_factor: 0.85, demand_factor: 0.85 },
    ],
  },
  result: (d) => ({
    headline: { label: "Maximum demand", value: n(d.total_demand_kva), unit: "kVA" },
    stats: [
      { label: "Demand (kW)", value: n(d.total_demand_kw), unit: "kW" },
      { label: "Demand current", value: n(d.total_demand_current_a), unit: "A" },
      { label: "Main protection", value: n(d.main_protection_a), unit: "A" },
      { label: "Transformer", value: n(d.transformer_kva_recommended), unit: "kVA" },
      { label: "Overall PF", value: n(d.overall_power_factor) },
      { label: "Connected load", value: n(d.total_connected_kw), unit: "kW" },
    ],
  }),
};

const shortCircuit: CalculatorConfig = {
  slug: "short-circuit",
  name: "Short Circuit",
  discipline: "Electrical",
  icon: "⚡",
  standard: "IEC 60909",
  blurb: "Prospective short-circuit currents by the impedance method, with an adiabatic CPC check.",
  endpoint: "/api/electrical/short-circuit",
  fields: [
    regionField,
    { name: "transformer_kva", label: "Transformer (kVA)", type: "number", default: 1000 },
    { name: "transformer_impedance_pct", label: "Transformer Z (%)", type: "number", default: 5.5, step: 0.1 },
    { name: "lv_voltage", label: "LV voltage (V)", type: "number", default: 400 },
    { name: "cable_size_mm2", label: "Cable size (mm²)", type: "number", default: 150 },
    { name: "cable_length_m", label: "Cable length (m)", type: "number", default: 100 },
    { name: "cable_type", label: "Cable type", type: "select", default: "XLPE_CU", options: [{ value: "XLPE_CU", label: "XLPE Copper" }, { value: "PVC_CU", label: "PVC Copper" }] },
  ],
  result: (d) => ({
    headline: { label: "Fault at LV terminals (3-ph)", value: n(d.isc_tx_3ph_ka), unit: "kA" },
    stats: [
      { label: "End of cable (3-ph)", value: n(d.isc_end_3ph_ka), unit: "kA" },
      { label: "End of cable (1-ph)", value: n(d.isc_end_1ph_ka), unit: "kA" },
      { label: "Min earth fault", value: n(d.ief_min_ka), unit: "kA" },
      { label: "Min CPC (adiabatic)", value: n(d.min_cpc_adiabatic_mm2), unit: "mm²" },
      { label: "Max fault time", value: n(d.max_fault_duration_s), unit: "s" },
    ],
  }),
};

const lighting: CalculatorConfig = {
  slug: "lighting",
  name: "Lighting Design",
  discipline: "Electrical",
  icon: "⚡",
  standard: "EN 12464-1 / CIBSE",
  blurb: "Lumen-method luminaire count and lighting power density against the regional LPD limit.",
  endpoint: "/api/electrical/lighting",
  fields: [
    regionField,
    { name: "room_type", label: "Room type", type: "select", default: "office", options: ["office", "classroom", "corridor", "warehouse", "retail", "workshop"].map((v) => ({ value: v, label: v[0].toUpperCase() + v.slice(1) })) },
    { name: "length_m", label: "Length (m)", type: "number", default: 10 },
    { name: "width_m", label: "Width (m)", type: "number", default: 8 },
    { name: "height_m", label: "Height (m)", type: "number", default: 3 },
    { name: "target_lux", label: "Target lux", type: "number", default: 500 },
    { name: "luminaire_lumens", label: "Lumens / fitting", type: "number", default: 4000 },
    { name: "luminaire_watts", label: "Watts / fitting", type: "number", default: 40 },
  ],
  result: (d) => ({
    headline: { label: "Luminaires required", value: n(d.num_luminaires), unit: `(${n(d.luminaires_per_row)}×${n(d.num_rows)})` },
    badge: { ok: Boolean(d.lpd_compliant), text: d.lpd_compliant ? "LPD compliant" : "LPD exceeds limit" },
    stats: [
      { label: "Achieved lux", value: n(d.achieved_lux), unit: "lx" },
      { label: "Installed power", value: n(d.total_watts), unit: "W" },
      { label: "LPD", value: n(d.lpd_w_per_m2), unit: `/ ${n(d.lpd_limit_w_per_m2)} W/m²` },
      { label: "Room index K", value: n(d.room_index_k) },
      { label: "Utilisation UF", value: n(d.uf_coefficient) },
    ],
    warnings: (d.recommendations as string[]) ?? [],
  }),
};

const pfCorrection: CalculatorConfig = {
  slug: "pf-correction",
  name: "Power Factor Correction",
  discipline: "Electrical",
  icon: "⚡",
  standard: "IEC 60831",
  blurb: "Capacitor-bank kVAr to reach a target power factor, with current reduction and savings.",
  endpoint: "/api/electrical/pf-correction",
  fields: [
    regionField,
    { name: "active_power_kw", label: "Active power (kW)", type: "number", default: 500 },
    { name: "existing_pf", label: "Existing PF", type: "number", default: 0.8, step: 0.01 },
    { name: "target_pf", label: "Target PF", type: "number", default: 0.95, step: 0.01 },
    { name: "phases", label: "Phases", type: "select", default: 3, options: [{ value: 3, label: "3-phase" }, { value: 1, label: "1-phase" }] },
  ],
  result: (d) => ({
    headline: { label: "Capacitor bank", value: n(d.standard_bank_kvar), unit: "kVAr" },
    badge: { ok: Boolean(d.compliant), text: d.compliant ? "Meets utility PF" : "Below utility PF" },
    stats: [
      { label: "Required correction", value: n(d.required_correction_kvar), unit: "kVAr" },
      { label: "Corrected PF", value: n(d.corrected_pf) },
      { label: "Current reduction", value: n(d.current_reduction_pct), unit: "%" },
      { label: "APFC steps", value: n(d.apfc_steps) },
      { label: "Annual saving", value: Math.round(n(d.annual_saving_kwh)), unit: "kWh" },
    ],
    note: String(d.tariff_note ?? ""),
  }),
};

const generator: CalculatorConfig = {
  slug: "generator-sizing",
  name: "Generator Sizing",
  discipline: "Electrical",
  icon: "⚡",
  standard: "ISO 8528",
  blurb: "Standby/prime generator rating from a load schedule with altitude and temperature derating.",
  endpoint: "/api/electrical/generator-sizing",
  fields: [
    regionField,
    { name: "site_altitude_m", label: "Site altitude (m)", type: "number", default: 0 },
    { name: "ambient_temp_c", label: "Ambient (°C)", type: "number", default: 45 },
    { name: "rated_pf", label: "Rated PF", type: "number", default: 0.8, step: 0.05 },
    { name: "future_expansion_pct", label: "Future expansion (%)", type: "number", default: 20 },
  ],
  rows: {
    name: "loads",
    label: "Load schedule",
    addLabel: "Add load",
    itemFields: [
      { name: "description", label: "Description", type: "text", default: "Load" },
      { name: "kw", label: "kW", type: "number", default: 50 },
      { name: "power_factor", label: "PF", type: "number", default: 0.85, step: 0.01 },
      { name: "load_type", label: "Type", type: "select", default: "general", options: ["general", "motor", "lighting", "hvac"].map((v) => ({ value: v, label: v })) },
      { name: "starting_method", label: "Start", type: "select", default: "VFD", options: ["DOL", "STAR_DELTA", "VFD", "SOFT_STARTER"].map((v) => ({ value: v, label: v })) },
    ],
    default: [
      { description: "General power", kw: 120, power_factor: 0.85, load_type: "general", starting_method: "VFD" },
      { description: "Chiller motor", kw: 90, power_factor: 0.85, load_type: "motor", starting_method: "STAR_DELTA" },
    ],
  },
  result: (d) => ({
    headline: { label: "Selected generator", value: n(d.standard_kva), unit: "kVA" },
    badge: { ok: Boolean(d.step_load_ok), text: d.step_load_ok ? "Step load OK" : "Step load exceeds dip limit" },
    stats: [
      { label: "Rated power", value: n(d.standard_kw), unit: "kW" },
      { label: "Design kVA", value: n(d.design_kva), unit: "kVA" },
      { label: "Total demand", value: n(d.total_demand_kva), unit: "kVA" },
      { label: "Step-load dip", value: n(d.step_load_voltage_dip_pct), unit: "%" },
      { label: "Fuel @ 75%", value: n(d.fuel_consumption_l_hr), unit: "L/hr" },
      { label: "Fault level", value: n(d.subtransient_fault_ka), unit: "kA" },
    ],
  }),
};

const ups: CalculatorConfig = {
  slug: "ups-sizing",
  name: "UPS Sizing",
  discipline: "Electrical",
  icon: "⚡",
  standard: "IEC 62040",
  blurb: "UPS rating, redundancy and battery autonomy from a critical-load schedule.",
  endpoint: "/api/electrical/ups-sizing",
  fields: [
    regionField,
    { name: "required_autonomy_min", label: "Autonomy (min)", type: "number", default: 15 },
    { name: "battery_technology", label: "Battery", type: "select", default: "VRLA_AGM", options: [{ value: "VRLA_AGM", label: "VRLA AGM" }, { value: "VRLA_GEL", label: "VRLA Gel" }, { value: "LI_ION", label: "Li-Ion" }] },
    { name: "battery_voltage_dc", label: "Battery bank (V DC)", type: "number", default: 240 },
    { name: "redundancy", label: "Redundancy", type: "select", default: "N", options: [{ value: "N", label: "N (none)" }, { value: "N+1", label: "N+1" }, { value: "2N", label: "2N" }] },
  ],
  rows: {
    name: "loads",
    label: "Critical loads",
    addLabel: "Add load",
    itemFields: [
      { name: "description", label: "Description", type: "text", default: "Server rack" },
      { name: "kva", label: "kVA", type: "number", default: 20 },
      { name: "power_factor", label: "PF", type: "number", default: 0.9, step: 0.01 },
      { name: "quantity", label: "Qty", type: "number", default: 1 },
    ],
    default: [
      { description: "Server racks", kva: 40, power_factor: 0.9, quantity: 1 },
      { description: "Network / comms", kva: 15, power_factor: 0.9, quantity: 1 },
    ],
  },
  result: (d) => ({
    headline: { label: "UPS units", value: `${n(d.num_ups_units)} × ${n(d.selected_kva)}`, unit: "kVA" },
    badge: { ok: Boolean(d.autonomy_ok), text: d.autonomy_ok ? "Autonomy met" : "Autonomy insufficient" },
    stats: [
      { label: "Unit rating", value: n(d.selected_kw), unit: "kW" },
      { label: "Loading", value: n(d.loading_pct), unit: "%" },
      { label: "Battery capacity", value: n(d.battery_capacity_ah), unit: "Ah" },
      { label: "Achievable autonomy", value: n(d.achievable_autonomy_min), unit: "min" },
      { label: "Charger current", value: n(d.charger_current_a), unit: "A" },
    ],
  }),
};

const panelSchedule: CalculatorConfig = {
  slug: "panel-schedule",
  name: "Panel Schedule",
  discipline: "Electrical",
  icon: "⚡",
  standard: "BS 7671 / IS 732 / AS 3000",
  blurb: "Distribution-board schedule with per-circuit cable sizing and phase balancing.",
  endpoint: "/api/electrical/panel-schedule",
  fields: [
    regionField,
    { name: "panel_name", label: "Panel name", type: "text", default: "DB-01" },
    { name: "supply_voltage_lv", label: "Supply voltage (V)", type: "number", default: 400 },
    { name: "incoming_cable_size_mm2", label: "Incoming cable (mm²)", type: "number", default: 150 },
  ],
  rows: {
    name: "circuits",
    label: "Circuits",
    addLabel: "Add circuit",
    itemFields: [
      { name: "circuit_no", label: "No.", type: "text", default: "1" },
      { name: "description", label: "Description", type: "text", default: "Lighting" },
      { name: "load_kw", label: "kW", type: "number", default: 3 },
      { name: "phases", label: "Ph", type: "select", default: 1, options: [{ value: 1, label: "1" }, { value: 3, label: "3" }] },
      { name: "cable_length_m", label: "Length (m)", type: "number", default: 30 },
    ],
    default: [
      { circuit_no: "1", description: "Lighting L1", load_kw: 3, phases: 1, cable_length_m: 25 },
      { circuit_no: "2", description: "Sockets L1", load_kw: 5, phases: 1, cable_length_m: 30 },
      { circuit_no: "3", description: "AHU", load_kw: 15, phases: 3, cable_length_m: 40 },
    ],
  },
  result: (d) => ({
    headline: { label: "Panel demand", value: n(d.total_demand_kva), unit: "kVA" },
    badge: { ok: Boolean(d.phase_balanced), text: d.phase_balanced ? "Phases balanced" : "Phase imbalance high" },
    stats: [
      { label: "Incomer current", value: n(d.incomer_current_a), unit: "A" },
      { label: "Incomer protection", value: n(d.incomer_protection_a), unit: "A" },
      { label: "Circuits", value: n(d.num_circuits) },
      { label: "Phase imbalance", value: n(d.phase_imbalance_pct), unit: "%" },
      { label: "Overall PF", value: n(d.overall_pf) },
      { label: "Spare ways", value: n(d.spare_pct), unit: "%" },
    ],
  }),
};

// ── Mechanical ───────────────────────────────────────────────────────────────

const ductSizing: CalculatorConfig = {
  slug: "duct-sizing",
  name: "Duct Sizing",
  discipline: "Mechanical",
  icon: "❄️",
  standard: "ASHRAE / CIBSE — equal friction",
  blurb: "Equal-friction duct sizing with a velocity limit and resulting pressure gradient.",
  endpoint: "/api/mechanical/duct-sizing",
  fields: [
    { name: "airflow_l_s", label: "Airflow (L/s)", type: "number", default: 500 },
    { name: "duct_type", label: "Duct type", type: "select", default: "rectangular", options: [{ value: "rectangular", label: "Rectangular" }, { value: "round", label: "Round" }] },
    { name: "max_velocity_m_s", label: "Max velocity (m/s)", type: "number", default: 8, step: 0.5 },
    { name: "friction_rate_pa_m", label: "Friction rate (Pa/m)", type: "number", default: 0.8, step: 0.1 },
  ],
  result: (d) => ({
    headline: { label: "Duct size", value: d.duct_type === "round" ? `Ø${n(d.diameter_mm)}` : `${n(d.width_mm)}×${n(d.height_mm)}`, unit: "mm" },
    stats: [
      { label: "Velocity", value: n(d.velocity_m_s), unit: "m/s" },
      { label: "Equiv. diameter", value: n(d.diameter_mm), unit: "mm" },
      { label: "Hydraulic dia.", value: n(d.hydraulic_diameter_mm), unit: "mm" },
      { label: "Pressure drop", value: n(d.pressure_drop_pa_m), unit: "Pa/m" },
      { label: "Duct area", value: n(d.duct_area_m2), unit: "m²" },
    ],
  }),
};

const heatingLoad: CalculatorConfig = {
  slug: "heating-load",
  name: "Heating Load",
  discipline: "Mechanical",
  icon: "❄️",
  standard: "EN 12831 / CIBSE Guide A",
  blurb: "Space heating load from fabric and infiltration losses at the design temperature difference.",
  endpoint: "/api/mechanical/heating-load",
  fields: [
    regionField,
    { name: "floor_area_m2", label: "Floor area (m²)", type: "number", default: 100 },
    { name: "wall_area_m2", label: "Wall area (m²)", type: "number", default: 80 },
    { name: "wall_u_value", label: "Wall U (W/m²K)", type: "number", default: 0.3, step: 0.05 },
    { name: "roof_area_m2", label: "Roof area (m²)", type: "number", default: 100 },
    { name: "roof_u_value", label: "Roof U (W/m²K)", type: "number", default: 0.2, step: 0.05 },
    { name: "window_area_m2", label: "Window area (m²)", type: "number", default: 20 },
    { name: "window_u_value", label: "Window U (W/m²K)", type: "number", default: 1.4, step: 0.1 },
    { name: "infiltration_ach", label: "Infiltration (ACH)", type: "number", default: 0.5, step: 0.1 },
    { name: "outdoor_design_temp_c", label: "Outdoor design (°C)", type: "number", default: -5 },
    { name: "indoor_design_temp_c", label: "Indoor design (°C)", type: "number", default: 21 },
  ],
  result: (d) => ({
    headline: { label: "Heating load", value: n(d.total_heat_loss_kw), unit: "kW" },
    stats: [
      { label: "Total loss", value: n(d.total_heat_loss_w), unit: "W" },
      { label: "Per m²", value: n(d.heat_load_w_per_m2), unit: "W/m²" },
      { label: "Fabric loss", value: n(d.fabric_heat_loss_w), unit: "W" },
      { label: "Infiltration loss", value: n(d.infiltration_heat_loss_w), unit: "W" },
      { label: "ΔT", value: n(d.delta_t_k), unit: "K" },
    ],
    note: String(d.standard ?? ""),
  }),
};

const ventilation: CalculatorConfig = {
  slug: "ventilation",
  name: "Ventilation",
  discipline: "Mechanical",
  icon: "❄️",
  standard: "ASHRAE 62.1 / AS 1668.2",
  blurb: "Fresh-air and supply-air requirements by occupancy, air changes, or floor area.",
  endpoint: "/api/mechanical/ventilation",
  fields: [
    regionField,
    { name: "floor_area_m2", label: "Floor area (m²)", type: "number", default: 200 },
    { name: "height_m", label: "Height (m)", type: "number", default: 3 },
    { name: "occupancy", label: "Occupancy", type: "number", default: 20 },
    { name: "fresh_air_method", label: "Method", type: "select", default: "occupancy", options: [{ value: "occupancy", label: "Per person" }, { value: "ach", label: "Air changes" }, { value: "area", label: "Per m²" }] },
    { name: "fresh_air_l_s_person", label: "Fresh air (L/s·person)", type: "number", default: 10 },
    { name: "cooling_load_kw", label: "Cooling load (kW)", type: "number", default: 10 },
  ],
  result: (d) => ({
    headline: { label: "Fresh air", value: n(d.fresh_air_l_s), unit: "L/s" },
    stats: [
      { label: "Fresh air", value: n(d.fresh_air_m3_h), unit: "m³/h" },
      { label: "Air changes", value: n(d.ach_achieved), unit: "ACH" },
      { label: "Total supply", value: n(d.total_supply_air_m3_h), unit: "m³/h" },
      { label: "Per person", value: n(d.fresh_air_l_s_person), unit: "L/s" },
    ],
    note: String(d.method_description ?? ""),
  }),
};

// ── Plumbing ─────────────────────────────────────────────────────────────────

const pipeSizing: CalculatorConfig = {
  slug: "pipe-sizing",
  name: "Pipe Sizing",
  discipline: "Plumbing",
  icon: "🚰",
  standard: "BS EN 806 / IS 1172",
  blurb: "Water pipe size from loading (fixture) units with a velocity limit.",
  endpoint: "/api/plumbing/pipe-sizing",
  fields: [
    regionField,
    { name: "flow_units", label: "Loading units", type: "number", default: 40 },
    { name: "system", label: "System", type: "select", default: "CWDS", options: [{ value: "CWDS", label: "Cold water" }, { value: "DHWS", label: "Hot water" }] },
    { name: "pipe_material", label: "Material", type: "select", default: "copper", options: ["copper", "pvc", "ppr", "gi", "hdpe"].map((v) => ({ value: v, label: v.toUpperCase() })) },
    { name: "max_velocity_m_s", label: "Max velocity (m/s)", type: "number", default: 2, step: 0.1 },
  ],
  result: (d) => ({
    headline: { label: "Pipe size", value: `DN${n(d.pipe_nominal_dn)}`, unit: `(${n(d.pipe_diameter_mm)} mm)` },
    stats: [
      { label: "Flow rate", value: n(d.flow_rate_l_s), unit: "L/s" },
      { label: "Velocity", value: n(d.velocity_m_s), unit: "m/s" },
      { label: "Pressure drop", value: n(d.pressure_drop_kpa_m), unit: "kPa/m" },
    ],
    note: String(d.standard ?? ""),
  }),
};

const drainageSizing: CalculatorConfig = {
  slug: "drainage-sizing",
  name: "Drainage Sizing",
  discipline: "Plumbing",
  icon: "🚰",
  standard: "BS EN 12056",
  blurb: "Sanitary or rainwater drain size from discharge units or roof area, with self-cleaning velocity.",
  endpoint: "/api/plumbing/drainage-sizing",
  fields: [
    regionField,
    { name: "system_type", label: "System", type: "select", default: "sanitary", options: [{ value: "sanitary", label: "Sanitary" }, { value: "rainwater", label: "Rainwater" }, { value: "combined", label: "Combined" }] },
    { name: "discharge_units", label: "Discharge units", type: "number", default: 50 },
    { name: "roof_area_m2", label: "Roof area (m²)", type: "number", default: 0 },
    { name: "rainfall_intensity_mm_hr", label: "Rainfall (mm/hr)", type: "number", default: 100 },
    { name: "gradient_percent", label: "Gradient (%)", type: "number", default: 1.0, step: 0.5 },
  ],
  result: (d) => ({
    headline: { label: "Drain size", value: `DN${n(d.selected_dn)}` },
    badge: { ok: Boolean(d.compliant), text: d.compliant ? "Compliant" : "Review velocity" },
    stats: [
      { label: "Design flow", value: n(d.design_flow_l_s), unit: "L/s" },
      { label: "Pipe capacity", value: n(d.pipe_capacity_l_s), unit: "L/s" },
      { label: "Velocity", value: n(d.pipe_velocity_m_s), unit: "m/s" },
      { label: "Self-cleaning", value: d.self_cleaning_velocity ? "Yes" : "No" },
    ],
  }),
};

const pumpSizing: CalculatorConfig = {
  slug: "pump-sizing",
  name: "Pump Sizing",
  discipline: "Plumbing",
  icon: "🚰",
  standard: "Darcy-Weisbach",
  blurb: "Pump duty head and motor power from flow, static head and friction losses.",
  endpoint: "/api/plumbing/pump-sizing",
  fields: [
    regionField,
    { name: "system_type", label: "System", type: "select", default: "cold_water", options: ["cold_water", "hot_water", "chilled_water", "condenser_water"].map((v) => ({ value: v, label: v.replace(/_/g, " ") })) },
    { name: "flow_rate_l_s", label: "Flow rate (L/s)", type: "number", default: 5, step: 0.5 },
    { name: "static_head_m", label: "Static head (m)", type: "number", default: 20 },
    { name: "pipe_friction_loss_m", label: "Friction loss (m)", type: "number", default: 10 },
    { name: "pump_efficiency", label: "Pump efficiency", type: "number", default: 0.75, step: 0.05 },
  ],
  result: (d) => ({
    headline: { label: "Selected motor", value: n(d.selected_motor_kw), unit: "kW" },
    stats: [
      { label: "Total dynamic head", value: n(d.total_dynamic_head_m), unit: "m" },
      { label: "Flow rate", value: n(d.flow_rate_m3_h), unit: "m³/h" },
      { label: "Shaft power", value: n(d.shaft_power_kw), unit: "kW" },
      { label: "Motor power", value: n(d.motor_power_kw), unit: "kW" },
      { label: "Pumps", value: n(d.num_pumps) },
    ],
  }),
};

const hotWater: CalculatorConfig = {
  slug: "hot-water-system",
  name: "Hot Water System",
  discipline: "Plumbing",
  icon: "🚰",
  standard: "BS EN 806-3",
  blurb: "Storage volume and heater output for domestic hot water with legionella check.",
  endpoint: "/api/plumbing/hot-water-system",
  fields: [
    regionField,
    { name: "system_type", label: "System", type: "select", default: "domestic", options: ["domestic", "solar_assisted", "heat_pump", "centralized"].map((v) => ({ value: v, label: v.replace(/_/g, " ") })) },
    { name: "num_occupants", label: "Occupants", type: "number", default: 50 },
    { name: "hot_water_l_person_day", label: "HW (L/person·day)", type: "number", default: 60 },
    { name: "inlet_water_temp_c", label: "Inlet temp (°C)", type: "number", default: 15 },
    { name: "storage_temp_c", label: "Storage temp (°C)", type: "number", default: 60 },
    { name: "recovery_time_hr", label: "Recovery time (hr)", type: "number", default: 4, step: 0.5 },
  ],
  result: (d) => ({
    headline: { label: "Storage tank", value: n(d.selected_tank_l), unit: "L" },
    badge: { ok: String(d.legionella_risk) === "LOW", text: `Legionella risk: ${d.legionella_risk ?? "—"}` },
    stats: [
      { label: "Daily demand", value: n(d.daily_demand_l), unit: "L" },
      { label: "Heater output", value: n(d.heater_output_kw), unit: "kW" },
      { label: "Energy / day", value: n(d.energy_required_kwh_day), unit: "kWh" },
      { label: "Peak hourly", value: n(d.peak_hourly_demand_l), unit: "L" },
    ],
  }),
};

const rainwater: CalculatorConfig = {
  slug: "rainwater-harvesting",
  name: "Rainwater Harvesting",
  discipline: "Plumbing",
  icon: "🚰",
  standard: "BS 8515 / AS 3500",
  blurb: "Harvestable volume, demand offset and storage tank from roof area and rainfall.",
  endpoint: "/api/plumbing/rainwater-harvesting",
  fields: [
    regionField,
    { name: "roof_area_m2", label: "Roof area (m²)", type: "number", default: 1000 },
    { name: "annual_rainfall_mm", label: "Annual rainfall (mm)", type: "number", default: 120 },
    { name: "runoff_coefficient", label: "Runoff coefficient", type: "number", default: 0.85, step: 0.05 },
    { name: "num_occupants", label: "Occupants", type: "number", default: 200 },
    { name: "non_potable_l_person_day", label: "Non-potable (L/p·day)", type: "number", default: 40 },
    { name: "storage_days", label: "Storage (days)", type: "number", default: 7 },
  ],
  result: (d) => ({
    headline: { label: "Storage tank", value: n(d.selected_tank_m3), unit: "m³" },
    stats: [
      { label: "Annual harvest", value: n(d.annual_harvestable_m3), unit: "m³" },
      { label: "Demand offset", value: n(d.demand_offset_pct), unit: "%" },
      { label: "Storage required", value: n(d.storage_volume_required_m3), unit: "m³" },
      { label: "First flush", value: n(d.first_flush_volume_l), unit: "L" },
      { label: "Peak flow", value: n(d.peak_flow_l_s), unit: "L/s" },
    ],
    warnings: complianceNotes(d.compliance_checks),
  }),
};

const tankSizing: CalculatorConfig = {
  slug: "tank-sizing",
  name: "Tank Sizing",
  discipline: "Plumbing",
  icon: "🚰",
  standard: "BS EN 806 / IS 1172",
  blurb: "Cold-water storage and gross tank volume with overflow and peak-flow sizing.",
  endpoint: "/api/plumbing/plumbing-tank-sizing",
  fields: [
    regionField,
    { name: "tank_type", label: "Tank type", type: "select", default: "cold_water", options: [{ value: "cold_water", label: "Cold water" }, { value: "domestic", label: "Domestic" }] },
    { name: "num_occupants", label: "Occupants", type: "number", default: 500 },
    { name: "daily_demand_l_person", label: "Demand (L/person)", type: "number", default: 200 },
    { name: "storage_hours", label: "Storage (hours)", type: "number", default: 24 },
    { name: "fire_reserve_l", label: "Fire reserve (L)", type: "number", default: 0 },
    { name: "tank_material", label: "Material", type: "select", default: "GRP", options: ["GRP", "MDPE", "Stainless Steel", "Concrete"].map((v) => ({ value: v, label: v })) },
  ],
  result: (d) => ({
    headline: { label: "Selected tank", value: n(d.selected_tank_l), unit: `L (${n(d.selected_tank_m3)} m³)` },
    stats: [
      { label: "Daily demand", value: n(d.total_daily_demand_l), unit: "L" },
      { label: "Cold storage", value: n(d.cold_storage_l), unit: "L" },
      { label: "Gross volume", value: n(d.gross_tank_volume_l), unit: "L" },
      { label: "Peak flow", value: n(d.peak_flow_l_min), unit: "L/min" },
      { label: "Overflow", value: `DN${n(d.overflow_pipe_dn_mm)}` },
    ],
    warnings: complianceNotes(d.compliance_checks),
  }),
};

// Turn a compliance_checks array into human notes for any non-PASS item.
function complianceNotes(checks: unknown): string[] {
  if (!Array.isArray(checks)) return [];
  return checks
    .filter((c) => c && typeof c === "object" && String((c as Record<string, unknown>).status).toUpperCase() !== "PASS")
    .map((c) => {
      const o = c as Record<string, unknown>;
      return `${o.check}: ${o.actual} (required ${o.required}) — ${o.status}`;
    });
}

// ── Fire ─────────────────────────────────────────────────────────────────────

const sprinkler: CalculatorConfig = {
  slug: "sprinkler",
  name: "Sprinkler Design",
  discipline: "Fire",
  icon: "🔥",
  standard: "BS EN 12845 / NFPA 13",
  blurb: "Sprinkler design flow, system flow and pump/tank duty from hazard class and protected area.",
  endpoint: "/api/fire/sprinkler",
  fields: [
    regionField,
    { name: "occupancy_hazard", label: "Hazard class", type: "select", default: "OH1", options: ["LH", "OH1", "OH2", "EH1", "EH2"].map((v) => ({ value: v, label: v })) },
    { name: "area_protected_m2", label: "Protected area (m²)", type: "number", default: 2500 },
    { name: "ceiling_height_m", label: "Ceiling height (m)", type: "number", default: 4, step: 0.5 },
    { name: "hose_allowance_l_min", label: "Hose allowance (L/min)", type: "number", default: 500 },
  ],
  result: (d) => ({
    headline: { label: "Total system flow", value: n(d.total_system_flow_l_min), unit: "L/min" },
    stats: [
      { label: "Design flow", value: n(d.design_flow_l_min), unit: "L/min" },
      { label: "Residual pressure", value: n(d.residual_pressure_bar), unit: "bar" },
      { label: "Pump power", value: n(d.pump_power_kw), unit: "kW" },
      { label: "Tank capacity", value: n(d.tank_capacity_m3), unit: "m³" },
      { label: "Sprinklers (design area)", value: n(d.num_sprinklers_design_area) },
    ],
    note: `${d.hazard_class ?? ""} · ${d.design_standard ?? ""}`,
  }),
};

const firePump: CalculatorConfig = {
  slug: "fire-pump",
  name: "Fire Pump Sizing",
  discipline: "Fire",
  icon: "🔥",
  standard: "BS EN 12845 / NFPA 20",
  blurb: "Fire pump duty head, motor and jockey pump from sprinkler, hose-reel and hydrant demand.",
  endpoint: "/api/fire/fire-pump",
  fields: [
    regionField,
    { name: "system_type", label: "System", type: "select", default: "wet_riser", options: ["wet_riser", "combined", "deluge", "foam"].map((v) => ({ value: v, label: v.replace(/_/g, " ") })) },
    { name: "sprinkler_demand_l_min", label: "Sprinkler demand (L/min)", type: "number", default: 2000 },
    { name: "hose_reel_demand_l_min", label: "Hose-reel demand (L/min)", type: "number", default: 600 },
    { name: "static_pressure_required_bar", label: "Static pressure (bar)", type: "number", default: 6.5, step: 0.5 },
    { name: "pump_efficiency", label: "Pump efficiency", type: "number", default: 0.72, step: 0.01 },
  ],
  result: (d) => ({
    headline: { label: "Selected motor", value: n(d.selected_motor_kw), unit: "kW" },
    stats: [
      { label: "Total flow", value: n(d.total_flow_l_min), unit: "L/min" },
      { label: "Dynamic head", value: n(d.total_dynamic_head_m), unit: "m" },
      { label: "Duty pump", value: n(d.duty_pump_kw), unit: "kW" },
      { label: "Jockey motor", value: n(d.jockey_motor_kw), unit: "kW" },
    ],
    note: String(d.pump_set_description ?? ""),
  }),
};

const fireTank: CalculatorConfig = {
  slug: "fire-tank",
  name: "Fire Storage Tank",
  discipline: "Fire",
  icon: "🔥",
  standard: "BS EN 12845 / NFPA 22",
  blurb: "Fire water storage volume, compartmentation and inlet flow for the required supply duration.",
  endpoint: "/api/fire/fire-tank",
  fields: [
    regionField,
    { name: "system_type", label: "System", type: "select", default: "sprinkler", options: ["sprinkler", "wet_riser", "combined", "foam"].map((v) => ({ value: v, label: v.replace(/_/g, " ") })) },
    { name: "total_flow_l_min", label: "Total flow (L/min)", type: "number", default: 2000 },
    { name: "supply_duration_min", label: "Supply duration (min)", type: "number", default: 60 },
    { name: "number_of_compartments", label: "Compartments", type: "number", default: 2 },
    { name: "refill_time_hr", label: "Refill time (hr)", type: "number", default: 4, step: 0.5 },
  ],
  result: (d) => ({
    headline: { label: "Total tank capacity", value: n(d.total_tank_capacity_m3), unit: "m³" },
    stats: [
      { label: "Volume required", value: n(d.total_volume_required_m3), unit: "m³" },
      { label: "Per compartment", value: n(d.selected_tank_per_compartment_m3), unit: "m³" },
      { label: "Compartments", value: n(d.number_of_compartments) },
      { label: "Inlet flow", value: n(d.inlet_flow_l_min), unit: "L/min" },
    ],
  }),
};

const standpipe: CalculatorConfig = {
  slug: "standpipe",
  name: "Standpipe System",
  discipline: "Fire",
  icon: "🔥",
  standard: "NFPA 14 / BS 9990",
  blurb: "Wet/dry riser flow, pressure and riser diameter by system class and building height.",
  endpoint: "/api/fire/standpipe",
  fields: [
    regionField,
    { name: "system_class", label: "System class", type: "select", default: "III", options: ["I", "II", "III"].map((v) => ({ value: v, label: `Class ${v}` })) },
    { name: "building_height_m", label: "Building height (m)", type: "number", default: 30 },
    { name: "num_floors", label: "Floors", type: "number", default: 10 },
    { name: "num_operating_standpipes", label: "Operating standpipes", type: "number", default: 2 },
    { name: "flow_per_standpipe_l_min", label: "Flow / standpipe (L/min)", type: "number", default: 950 },
  ],
  result: (d) => ({
    headline: { label: "Riser main", value: `DN${n(d.selected_dn)}`, unit: `(${n(d.riser_main_diameter_mm)} mm)` },
    stats: [
      { label: "Total flow", value: n(d.total_flow_l_min), unit: "L/min" },
      { label: "Pressure required", value: n(d.total_pressure_required_bar), unit: "bar" },
      { label: "Hose stations", value: n(d.num_hose_stations) },
      { label: "Standpipes", value: n(d.num_operating_standpipes) },
    ],
  }),
};

export const ELECTRICAL_CALCS: CalculatorConfig[] = [
  voltageDrop, maximumDemand, shortCircuit, lighting, pfCorrection, generator, ups, panelSchedule,
];
const FIRE_CALCS: CalculatorConfig[] = [sprinkler, firePump, fireTank, standpipe];
const MECHANICAL_CALCS: CalculatorConfig[] = [ductSizing, heatingLoad, ventilation];
const PLUMBING_CALCS: CalculatorConfig[] = [pipeSizing, drainageSizing, pumpSizing, hotWater, rainwater, tankSizing];

export const CALCULATORS: CalculatorConfig[] = [
  ...ELECTRICAL_CALCS,
  ...MECHANICAL_CALCS,
  ...PLUMBING_CALCS,
  ...FIRE_CALCS,
];

export function getCalculator(slug: string): CalculatorConfig | undefined {
  return CALCULATORS.find((c) => c.slug === slug);
}
