import { XCircle } from "lucide-react";
import { useState } from "react";

import { Badge, Button, Card, Field, Input, Select, Spinner, Stat } from "../../components/ui.tsx";
import { api, ApiError, type CoolingLoadResult } from "../../lib/api.ts";
import { REGIONS } from "../../lib/regions.ts";

const DEFAULTS = {
  region: "gcc",
  zone_name: "Open Plan Office",
  floor_area_m2: 200,
  glass_area_m2: 40,
  glass_orientation: "W",
  occupancy: 20,
  equipment_w_m2: 20,
  lighting_w_m2: 10,
  cop: 3.0,
};

const ORIENTATIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"];

export default function CoolingLoad() {
  const [form, setForm] = useState({ ...DEFAULTS });
  const [result, setResult] = useState<CoolingLoadResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const set = (k: string, v: string | number) => setForm((f) => ({ ...f, [k]: v }));
  const num = (k: string, v: string) => set(k, v === "" ? 0 : Number(v));

  async function calculate() {
    setLoading(true);
    setError(null);
    try {
      const r = await api.post<CoolingLoadResult>("/api/mechanical/cooling-load", form);
      setResult(r);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Something went wrong");
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container-page py-12">
      <header className="mb-8">
        <Badge tone="brand" className="mb-3">❄️ Mechanical</Badge>
        <h1 className="text-3xl font-bold tracking-tight">Cooling Load</h1>
        <p className="mt-2 max-w-2xl text-muted">
          Simplified heat-balance cooling load with solar, fabric, internal and ventilation gains (ASHRAE / CIBSE).
        </p>
      </header>

      <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
        <Card className="h-fit p-6">
          <div className="grid gap-4">
            <Field label="Region">
              <Select value={form.region} onChange={(e) => set("region", e.target.value)}>
                {REGIONS.map((r) => <option key={r.code} value={r.code}>{r.short}</option>)}
              </Select>
            </Field>
            <Field label="Zone name">
              <Input value={form.zone_name} onChange={(e) => set("zone_name", e.target.value)} />
            </Field>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Floor area (m²)">
                <Input type="number" value={form.floor_area_m2} onChange={(e) => num("floor_area_m2", e.target.value)} />
              </Field>
              <Field label="Glass area (m²)">
                <Input type="number" value={form.glass_area_m2} onChange={(e) => num("glass_area_m2", e.target.value)} />
              </Field>
            </div>
            <Field label="Glass orientation">
              <Select value={form.glass_orientation} onChange={(e) => set("glass_orientation", e.target.value)}>
                {ORIENTATIONS.map((o) => <option key={o} value={o}>{o}</option>)}
              </Select>
            </Field>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Occupancy">
                <Input type="number" value={form.occupancy} onChange={(e) => num("occupancy", e.target.value)} />
              </Field>
              <Field label="Chiller COP">
                <Input type="number" step="0.1" value={form.cop} onChange={(e) => num("cop", e.target.value)} />
              </Field>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Equipment (W/m²)">
                <Input type="number" value={form.equipment_w_m2} onChange={(e) => num("equipment_w_m2", e.target.value)} />
              </Field>
              <Field label="Lighting (W/m²)">
                <Input type="number" value={form.lighting_w_m2} onChange={(e) => num("lighting_w_m2", e.target.value)} />
              </Field>
            </div>
            <Button onClick={calculate} disabled={loading} size="lg" className="mt-1">
              {loading ? <><Spinner /> Calculating…</> : "Calculate"}
            </Button>
          </div>
        </Card>

        <div>
          {error && (
            <Card className="border-danger/40 p-6">
              <div className="flex items-center gap-2 text-danger">
                <XCircle size={18} /> <span className="font-semibold">{error}</span>
              </div>
            </Card>
          )}

          {!error && !result && (
            <Card className="grid min-h-[300px] place-items-center p-10 text-center">
              <div>
                <div className="text-4xl">❄️</div>
                <p className="mt-3 text-muted">Enter zone data and press <b>Calculate</b>.</p>
              </div>
            </Card>
          )}

          {result && (
            <div className="grid gap-5">
              <Card className="p-6">
                <div className="text-sm text-muted">Total cooling load</div>
                <div className="text-4xl font-extrabold text-brand">
                  {result.total_cooling_kw} <span className="text-2xl text-muted">kW</span>
                </div>
                <div className="mt-1 text-sm text-muted">
                  {result.total_cooling_tr} TR · {result.cooling_w_per_m2} W/m² · {result.standard_reference}
                </div>
              </Card>

              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <Stat label="Outdoor / Indoor" value={`${result.outdoor_db_c} / ${result.indoor_db_c}`} unit="°C" />
                <Stat label="Chiller power" value={result.chiller_power_kw} unit="kW" />
                <Stat label="Supply air" value={result.supply_airflow_l_s} unit="L/s" />
                <Stat label="Air changes" value={result.room_air_changes_per_hour} unit="ACH" />
                <Stat label="Cooling in TR" value={result.total_cooling_tr} unit="TR" />
                <Stat label="Density" value={result.cooling_w_per_m2} unit="W/m²" />
              </div>

              <Card className="p-6">
                <h3 className="mb-4 font-semibold">Load breakdown</h3>
                <div className="space-y-2">
                  {Object.entries(result.load_breakdown_w).map(([k, v]) => {
                    const total = Object.values(result.load_breakdown_w).reduce((a, b) => a + Math.max(b, 0), 0) || 1;
                    const pct = Math.max(0, (v / total) * 100);
                    return (
                      <div key={k}>
                        <div className="mb-1 flex justify-between text-sm">
                          <span className="capitalize text-muted">{k.replace(/_/g, " ")}</span>
                          <span className="font-medium">{Math.round(v)} W</span>
                        </div>
                        <div className="h-2 overflow-hidden rounded-full bg-surface-2">
                          <div className="h-full rounded-full bg-brand" style={{ width: `${pct}%` }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
