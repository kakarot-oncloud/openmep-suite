import { Download, XCircle } from "lucide-react";
import { useState } from "react";

import RowEditor, { type Column } from "../../components/RowEditor.tsx";
import { Badge, Button, Card, Field, Input, Select, Spinner, Stat } from "../../components/ui.tsx";
import { api, ApiError } from "../../lib/api.ts";
import { CABLE_TYPES, INSTALL_METHODS, REGIONS } from "../../lib/regions.ts";

const COLS: Column[] = [
  { name: "circuit_ref", label: "Ref", type: "text" },
  { name: "description", label: "Description", type: "text" },
  { name: "load_kw", label: "Load (kW)", type: "number" },
  { name: "phases", label: "Ph", type: "select", options: [{ value: 3, label: "3" }, { value: 1, label: "1" }] },
  { name: "cable_length_m", label: "Length (m)", type: "number" },
  { name: "circuit_type", label: "Type", type: "select", options: [{ value: "power", label: "Power" }, { value: "lighting", label: "Lighting" }] },
];
const BLANK = { circuit_ref: "", description: "", load_kw: 20, phases: 3, cable_length_m: 50, circuit_type: "power" };

interface TableData { columns: string[]; rows: (string | number)[][] }

export default function BatchSchedule() {
  const [basis, setBasis] = useState({ region: "gcc", ambient_temp_c: 45, power_factor: 0.85, default_cable_type: "XLPE_CU", default_installation_method: "C" });
  const [circuits, setCircuits] = useState<Record<string, string | number>[]>([
    { circuit_ref: "C1", description: "AHU-1", load_kw: 45, phases: 3, cable_length_m: 80, circuit_type: "power" },
    { circuit_ref: "C2", description: "Lighting DB", load_kw: 6, phases: 1, cable_length_m: 40, circuit_type: "lighting" },
    { circuit_ref: "C3", description: "Chiller", load_kw: 160, phases: 3, cable_length_m: 120, circuit_type: "power" },
  ]);
  const [res, setRes] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setB = (k: string, v: string | number) => setBasis((s) => ({ ...s, [k]: v }));

  async function size() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.post<Record<string, unknown>>("/api/electrical/cable-schedule", { design_basis: basis, circuits });
      setRes(data);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Something went wrong");
      setRes(null);
    } finally {
      setLoading(false);
    }
  }

  const table = res?.table as TableData | undefined;

  async function exportFile(kind: "xlsx" | "csv") {
    if (!table) return;
    await api.download(`/api/exports/table.${kind}`, { title: "Cable_Schedule", columns: table.columns, rows: table.rows }, `cable_schedule.${kind}`)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Export failed"));
  }

  return (
    <div className="container-page py-12">
      <header className="mb-8">
        <Badge tone="brand" className="mb-3">⚡ Batch tool</Badge>
        <h1 className="text-3xl font-bold tracking-tight">Cable Schedule — Batch Sizing</h1>
        <p className="mt-2 max-w-2xl text-muted">Size a whole load schedule against one design basis, then export to Excel or CSV.</p>
      </header>

      <Card className="p-6">
        <div className="mb-2 text-sm font-medium">Design basis</div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <Field label="Region"><Select value={basis.region} onChange={(e) => setB("region", e.target.value)}>{REGIONS.map((r) => <option key={r.code} value={r.code}>{r.short}</option>)}</Select></Field>
          <Field label="Ambient °C"><Input type="number" value={basis.ambient_temp_c} onChange={(e) => setB("ambient_temp_c", Number(e.target.value))} /></Field>
          <Field label="Power factor"><Input type="number" step="0.01" value={basis.power_factor} onChange={(e) => setB("power_factor", Number(e.target.value))} /></Field>
          <Field label="Cable type"><Select value={basis.default_cable_type} onChange={(e) => setB("default_cable_type", e.target.value)}>{CABLE_TYPES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}</Select></Field>
          <Field label="Install method"><Select value={basis.default_installation_method} onChange={(e) => setB("default_installation_method", e.target.value)}>{INSTALL_METHODS.map((m) => <option key={m.value} value={m.value}>{m.value}</option>)}</Select></Field>
        </div>
        <div className="mt-6">
          <div className="mb-2 text-sm font-medium">Circuits</div>
          <RowEditor columns={COLS} rows={circuits} onChange={setCircuits} addLabel="Add circuit" blank={BLANK} />
        </div>
        <Button onClick={size} disabled={loading} size="lg" className="mt-6 w-full sm:w-auto">
          {loading ? <><Spinner /> Sizing…</> : "Size all circuits"}
        </Button>
      </Card>

      {error && (
        <Card className="mt-6 border-danger/40 p-6"><div className="flex items-center gap-2 text-danger"><XCircle size={18} /> <span className="font-semibold">{error}</span></div></Card>
      )}

      {res && table && (
        <div className="mt-6 grid gap-5">
          <div className="flex flex-wrap items-center gap-4">
            <Stat label="Circuits" value={Number(res.circuit_count)} />
            <Stat label="Non-compliant" value={Number(res.non_compliant_count)} />
            <Badge tone={res.all_compliant ? "success" : "danger"} className="text-sm">{res.all_compliant ? "All compliant" : "Review flagged circuits"}</Badge>
            <div className="ml-auto flex gap-2">
              <Button variant="outline" size="sm" onClick={() => exportFile("xlsx")}><Download size={16} /> Excel</Button>
              <Button variant="outline" size="sm" onClick={() => exportFile("csv")}><Download size={16} /> CSV</Button>
            </div>
          </div>
          <Card className="overflow-hidden p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-surface-2 text-left text-xs uppercase text-muted">
                  <tr>{table.columns.map((c) => <th key={c} className="whitespace-nowrap px-3 py-2">{c}</th>)}</tr>
                </thead>
                <tbody>
                  {table.rows.map((row, i) => (
                    <tr key={i} className="border-t border-border">
                      {row.map((cell, j) => <td key={j} className="whitespace-nowrap px-3 py-2">{String(cell)}</td>)}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
