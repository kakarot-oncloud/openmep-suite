import { XCircle } from "lucide-react";
import { useState } from "react";

import RowEditor, { type Column } from "../../components/RowEditor.tsx";
import { Badge, Button, Card, Field, Input, Select, Spinner, Stat } from "../../components/ui.tsx";
import { api, ApiError } from "../../lib/api.ts";
import { REGIONS } from "../../lib/regions.ts";

const COLS: Column[] = [
  { name: "circuit_reference", label: "Ref", type: "text" },
  { name: "description", label: "Description", type: "text" },
  { name: "cable_size_mm2", label: "Size (mm²)", type: "number" },
  { name: "phases", label: "Ph", type: "select", options: [{ value: 1, label: "1" }, { value: 3, label: "3" }] },
  { name: "cable_length_m", label: "Length (m)", type: "number" },
  { name: "runs", label: "Runs", type: "number" },
];
const BLANK = { circuit_reference: "", description: "", cable_size_mm2: 25, phases: 3, cable_length_m: 50, runs: 1 };

export default function BOQ() {
  const [region, setRegion] = useState("gcc");
  const [projectName, setProjectName] = useState("Tower A");
  const [cables, setCables] = useState<Record<string, string | number>[]>([
    { circuit_reference: "C1", description: "MDB feeder", cable_size_mm2: 95, phases: 3, cable_length_m: 60, runs: 1 },
    { circuit_reference: "C2", description: "Sub-main DB-1", cable_size_mm2: 25, phases: 3, cable_length_m: 40, runs: 1 },
  ]);
  const [res, setRes] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.post<Record<string, unknown>>("/api/boq/generate", {
        region,
        project_name: projectName,
        cables,
      });
      setRes(data);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Something went wrong");
      setRes(null);
    } finally {
      setLoading(false);
    }
  }

  const lc = res ? String(res.local_currency ?? "").toLowerCase() : "";
  const localTotal = res ? (res[`grand_total_${lc}`] as number | undefined) : undefined;
  const lineItems = (res?.line_items as Record<string, unknown>[]) ?? [];

  return (
    <div className="container-page py-12">
      <header className="mb-8">
        <Badge tone="brand" className="mb-3">📄 Reports</Badge>
        <h1 className="text-3xl font-bold tracking-tight">BOQ Generator</h1>
        <p className="mt-2 max-w-2xl text-muted">Priced electrical cable Bill of Quantities with regional unit rates and contingency.</p>
      </header>

      <Card className="p-6">
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Region"><Select value={region} onChange={(e) => setRegion(e.target.value)}>{REGIONS.map((r) => <option key={r.code} value={r.code}>{r.short}</option>)}</Select></Field>
          <Field label="Project name"><Input value={projectName} onChange={(e) => setProjectName(e.target.value)} /></Field>
        </div>
        <div className="mt-6">
          <div className="mb-2 text-sm font-medium">Cable take-off</div>
          <RowEditor columns={COLS} rows={cables} onChange={setCables} addLabel="Add cable" blank={BLANK} />
        </div>
        <Button onClick={generate} disabled={loading} size="lg" className="mt-6 w-full sm:w-auto">
          {loading ? <><Spinner /> Generating…</> : "Generate BOQ"}
        </Button>
      </Card>

      {error && (
        <Card className="mt-6 border-danger/40 p-6"><div className="flex items-center gap-2 text-danger"><XCircle size={18} /> <span className="font-semibold">{error}</span></div></Card>
      )}

      {res && (
        <div className="mt-6 grid gap-5">
          <Card className="p-6">
            <div className="text-sm text-muted">Grand total</div>
            <div className="text-4xl font-extrabold text-brand">
              ${Number(res.grand_total_usd).toLocaleString()}
              {localTotal !== undefined && <span className="ml-2 text-xl font-medium text-muted">≈ {Number(localTotal).toLocaleString()} {res.local_currency as string}</span>}
            </div>
          </Card>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Stat label="Cables" value={`$${Number(res.cable_total_usd).toLocaleString()}`} />
            <Stat label="Contingency" value={`$${Number(res.contingency_usd).toLocaleString()}`} />
            <Stat label="Cost index" value={Number(res.regional_cost_index)} />
            <Stat label="Line items" value={lineItems.length} />
          </div>
          <Card className="overflow-hidden p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-surface-2 text-left text-xs uppercase text-muted">
                  <tr>
                    <th className="px-4 py-2">Description</th>
                    <th className="px-4 py-2">Qty</th>
                    <th className="px-4 py-2 text-right">Amount (USD)</th>
                  </tr>
                </thead>
                <tbody>
                  {lineItems.map((li, i) => (
                    <tr key={i} className="border-t border-border">
                      <td className="px-4 py-2">{String(li.description ?? "")}</td>
                      <td className="px-4 py-2 text-muted">{li.quantity != null ? `${li.quantity} ${li.unit ?? ""}` : "—"}</td>
                      <td className="px-4 py-2 text-right font-medium">${Number(li.amount_usd ?? 0).toLocaleString()}</td>
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
