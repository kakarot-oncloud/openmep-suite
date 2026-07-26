import { AlertTriangle, CheckCircle2, XCircle } from "lucide-react";
import { useState } from "react";

import { Badge, Button, Card, Field, Input, Select, Spinner, Stat } from "../../components/ui.tsx";
import { api, ApiError, type CableSizingResult } from "../../lib/api.ts";
import { CABLE_TYPES, INSTALL_METHODS, REGIONS } from "../../lib/regions.ts";

const DEFAULTS = {
  region: "gcc",
  load_kw: 45,
  power_factor: 0.85,
  phases: 3,
  cable_type: "XLPE_CU",
  installation_method: "C",
  cable_length_m: 80,
  ambient_temp_c: 40,
  num_grouped_circuits: 1,
  circuit_type: "power",
};

export default function CableSizing() {
  const [form, setForm] = useState({ ...DEFAULTS });
  const [result, setResult] = useState<CableSizingResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const set = (k: string, v: string | number) => setForm((f) => ({ ...f, [k]: v }));
  const num = (k: string, v: string) => set(k, v === "" ? 0 : Number(v));

  async function calculate() {
    setLoading(true);
    setError(null);
    try {
      const r = await api.post<CableSizingResult>("/api/electrical/cable-sizing", {
        ...form,
        phases: Number(form.phases),
      });
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
        <Badge tone="brand" className="mb-3">⚡ Electrical</Badge>
        <h1 className="text-3xl font-bold tracking-tight">Cable Sizing</h1>
        <p className="mt-2 max-w-2xl text-muted">
          Current-carrying capacity, derating, voltage drop and protection to BS 7671 / IEC 60364 / IS 3961 / AS 3008.
        </p>
      </header>

      <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
        {/* Inputs */}
        <Card className="h-fit p-6">
          <div className="grid gap-4">
            <Field label="Region">
              <Select value={form.region} onChange={(e) => set("region", e.target.value)}>
                {REGIONS.map((r) => (
                  <option key={r.code} value={r.code}>{r.short} — {r.standard}</option>
                ))}
              </Select>
            </Field>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Load (kW)">
                <Input type="number" value={form.load_kw} onChange={(e) => num("load_kw", e.target.value)} />
              </Field>
              <Field label="Power factor">
                <Input type="number" step="0.01" value={form.power_factor} onChange={(e) => num("power_factor", e.target.value)} />
              </Field>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Phases">
                <Select value={form.phases} onChange={(e) => num("phases", e.target.value)}>
                  <option value={3}>3-phase</option>
                  <option value={1}>1-phase</option>
                </Select>
              </Field>
              <Field label="Length (m)">
                <Input type="number" value={form.cable_length_m} onChange={(e) => num("cable_length_m", e.target.value)} />
              </Field>
            </div>
            <Field label="Cable type">
              <Select value={form.cable_type} onChange={(e) => set("cable_type", e.target.value)}>
                {CABLE_TYPES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
              </Select>
            </Field>
            <Field label="Installation method">
              <Select value={form.installation_method} onChange={(e) => set("installation_method", e.target.value)}>
                {INSTALL_METHODS.map((m) => <option key={m.value} value={m.value}>{m.label}</option>)}
              </Select>
            </Field>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Ambient (°C)">
                <Input type="number" value={form.ambient_temp_c} onChange={(e) => num("ambient_temp_c", e.target.value)} />
              </Field>
              <Field label="Grouped circuits">
                <Input type="number" value={form.num_grouped_circuits} onChange={(e) => num("num_grouped_circuits", e.target.value)} />
              </Field>
            </div>
            <Field label="Circuit type">
              <Select value={form.circuit_type} onChange={(e) => set("circuit_type", e.target.value)}>
                <option value="power">Power</option>
                <option value="lighting">Lighting</option>
              </Select>
            </Field>
            <Button onClick={calculate} disabled={loading} size="lg" className="mt-1">
              {loading ? <><Spinner /> Calculating…</> : "Calculate"}
            </Button>
          </div>
        </Card>

        {/* Results */}
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
                <div className="text-4xl">⚡</div>
                <p className="mt-3 text-muted">Enter parameters and press <b>Calculate</b> to size the cable.</p>
              </div>
            </Card>
          )}

          {result && (
            <div className="grid gap-5">
              <Card className="p-6">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <div className="text-sm text-muted">Recommended cable</div>
                    <div className="text-4xl font-extrabold text-brand">{result.selected_size_mm2} mm²</div>
                    <div className="mt-1 text-sm text-muted">{result.cable_type_description}</div>
                  </div>
                  <Badge tone={result.overall_compliant ? "success" : "danger"} className="text-sm">
                    {result.overall_compliant ? <CheckCircle2 size={14} /> : <XCircle size={14} />}
                    {result.overall_compliant ? "Compliant" : "Non-compliant"}
                  </Badge>
                </div>
                <p className="mt-3 text-xs text-muted">{result.standard} · {result.authority}</p>
              </Card>

              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <Stat label="Design current Ib" value={result.design_current_ib_a} unit="A" />
                <Stat label="Derated rating Iz" value={result.derated_rating_iz_a} unit="A" />
                <Stat label="Supply voltage" value={result.supply_voltage_v} unit="V" />
                <Stat label="Ca × Cg" value={`${result.ca_factor} × ${result.cg_factor}`} />
                <Stat
                  label="Voltage drop"
                  value={<span className={result.voltage_drop_pass ? "text-success" : "text-danger"}>{result.voltage_drop_pct}%</span>}
                  unit={`/ ${result.voltage_drop_limit_pct}%`}
                />
                <Stat label="Protection device" value={result.protection_device_a} unit="A" />
              </div>

              {result.warnings.length > 0 && (
                <Card className="border-warn/40 p-5">
                  <div className="mb-2 flex items-center gap-2 font-semibold text-warn">
                    <AlertTriangle size={16} /> Warnings
                  </div>
                  <ul className="space-y-1.5 text-sm text-muted">
                    {result.warnings.map((w, i) => (
                      <li key={i}>{w.replace(/^⚠️\s*/, "")}</li>
                    ))}
                  </ul>
                </Card>
              )}

              <details className="rounded-2xl border border-border bg-surface p-5">
                <summary className="cursor-pointer text-sm font-semibold">Full calculation sheet</summary>
                <pre className="mt-3 overflow-x-auto whitespace-pre-wrap font-mono text-xs text-muted">
                  {result.calculation_summary}
                </pre>
              </details>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
