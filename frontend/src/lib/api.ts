// Typed client for the OpenMEP FastAPI backend.
//
// In development, requests to /api are proxied to the backend by Vite (see
// vite.config.ts). In production, set VITE_API_BASE to the backend origin
// (e.g. https://api.example.com); it defaults to same-origin so a reverse
// proxy that serves the SPA and forwards /api also works with no config.

const BASE = (import.meta.env.VITE_API_BASE ?? "").replace(/\/$/, "");

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function post<T>(path: string, body: unknown): Promise<T> {
  let resp: Response;
  try {
    resp = await fetch(`${BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new ApiError("Cannot reach the calculation engine. Is the API running?", 0);
  }
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    const detail = (data && (data.detail || data.message)) || `Request failed (${resp.status})`;
    throw new ApiError(typeof detail === "string" ? detail : JSON.stringify(detail), resp.status);
  }
  return data as T;
}

async function get<T>(path: string): Promise<T> {
  const resp = await fetch(`${BASE}${path}`);
  if (!resp.ok) throw new ApiError(`Request failed (${resp.status})`, resp.status);
  return (await resp.json()) as T;
}

async function del(path: string): Promise<void> {
  const resp = await fetch(`${BASE}${path}`, { method: "DELETE" });
  if (!resp.ok) throw new ApiError(`Request failed (${resp.status})`, resp.status);
}

// POST that returns a binary file (CSV/Excel), triggering a browser download.
async function download(path: string, body: unknown, filename: string): Promise<void> {
  const resp = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok) throw new ApiError(`Export failed (${resp.status})`, resp.status);
  const blob = await resp.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export const api = { post, get, del, download, base: BASE };

// ── Response shapes (subset of fields the UI uses) ───────────────────────────

export interface CableSizingResult {
  status: string;
  standard: string;
  authority: string;
  supply_voltage_v: number;
  design_current_ib_a: number;
  selected_size_mm2: number;
  cable_type_description: string;
  installation_method_description: string;
  tabulated_rating_it_a: number;
  ca_factor: number;
  cg_factor: number;
  derated_rating_iz_a: number;
  voltage_drop_pct: number;
  voltage_drop_limit_pct: number;
  voltage_drop_pass: boolean;
  protection_device_a: number;
  earth_conductor_mm2: number;
  overall_compliant: boolean;
  warnings: string[];
  calculation_summary: string;
}

export interface CoolingLoadResult {
  status: string;
  standard_reference: string;
  outdoor_db_c: number;
  indoor_db_c: number;
  total_cooling_kw: number;
  total_cooling_tr: number;
  cooling_w_per_m2: number;
  chiller_power_kw: number;
  supply_airflow_l_s: number;
  room_air_changes_per_hour: number;
  load_breakdown_w: Record<string, number>;
}
