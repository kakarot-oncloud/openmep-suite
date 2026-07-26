import { CheckCircle2, XCircle } from "lucide-react";
import { useState } from "react";

import RowEditor, { type Column } from "../../components/RowEditor.tsx";
import { Badge, Button, Card, Field, Select, Spinner, Stat } from "../../components/ui.tsx";
import { api, ApiError } from "../../lib/api.ts";
import { REGIONS } from "../../lib/regions.ts";

const COLS: Column[] = [
  { name: "circuit_reference", label: "Ref", type: "text" },
  { name: "design_current_a", label: "Ib (A)", type: "number" },
  { name: "derated_rating_iz_a", label: "Iz (A)", type: "number" },
  { name: "voltage_drop_pct", label: "VD (%)", type: "number", step: 0.1 },
  { name: "cable_size_mm2", label: "Size (mm²)", type: "number" },
  { name: "earth_size_mm2", label: "Earth (mm²)", type: "number" },
];
const BLANK = { circuit_reference: "", design_current_a: 80, derated_rating_iz_a: 95, voltage_drop_pct: 2.5, cable_size_mm2: 25, earth_size_mm2: 16 };

interface Check { check: string; clause: string; actual: string; limit: string; passed: boolean }
interface Circuit { circuit_reference: string; checks: Check[]; overall_passed: boolean }

export default function Compliance() {
  const [region, setRegion] = useState("gcc");
  const [rows, setRows] = useState<Record<string, string | number>[]>([
    { circuit_reference: "C1", design_current_a: 80, derated_rating_iz_a: 95, voltage_drop_pct: 2.5, cable_size_mm2: 25, earth_size_mm2: 16 },
    { circuit_reference: "C2", design_current_a: 120, derated_rating_iz_a: 110, voltage_drop_pct: 5.4, cable_size_mm2: 35, earth_size_mm2: 16 },
  ]);
  const [res, setRes] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function check() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.post<Record<string, unknown>>("/api/compliance/check", {
        region,
        cable_checks: rows,
      });
      setRes(data);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Something went wrong");
      setRes(null);
    } finally {
      setLoading(false);
    }
  }

  const circuits = ((res?.electrical as Record<string, unknown>)?.cable_circuits as Circuit[]) ?? [];

  return (
    <div className="container-page py-12">
      <header className="mb-8">
        <Badge tone="brand" className="mb-3">📄 Reports</Badge>
        <h1 className="text-3xl font-bold tracking-tight">Compliance Checker</h1>
        <p className="mt-2 max-w-2xl text-muted">Validate cable circuits against regional limits (Iz ≥ Ib, voltage drop, earth conductor) with the failing clause.</p>
      </header>

      <Card className="p-6">
        <Field label="Region"><Select value={region} onChange={(e) => setRegion(e.target.value)}>{REGIONS.map((r) => <option key={r.code} value={r.code}>{r.short}</option>)}</Select></Field>
        <div className="mt-6">
          <div className="mb-2 text-sm font-medium">Cable circuits</div>
          <RowEditor columns={COLS} rows={rows} onChange={setRows} addLabel="Add circuit" blank={BLANK} />
        </div>
        <Button onClick={check} disabled={loading} size="lg" className="mt-6 w-full sm:w-auto">
          {loading ? <><Spinner /> Checking…</> : "Run compliance check"}
        </Button>
      </Card>

      {error && (
        <Card className="mt-6 border-danger/40 p-6"><div className="flex items-center gap-2 text-danger"><XCircle size={18} /> <span className="font-semibold">{error}</span></div></Card>
      )}

      {res && (
        <div className="mt-6 grid gap-5">
          <Card className="p-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="text-sm text-muted">Overall</div>
                <div className="text-3xl font-extrabold">{Number(res.checks_passed)} / {Number(res.total_checks)} passed</div>
              </div>
              <Badge tone={res.overall_compliant ? "success" : "danger"} className="text-sm">
                {res.overall_compliant ? <CheckCircle2 size={14} /> : <XCircle size={14} />} {res.overall_compliant ? "Compliant" : "Non-compliant"}
              </Badge>
            </div>
          </Card>
          <div className="grid gap-4 sm:grid-cols-3">
            <Stat label="Total checks" value={Number(res.total_checks)} />
            <Stat label="Passed" value={<span className="text-success">{Number(res.checks_passed)}</span>} />
            <Stat label="Failed" value={<span className={Number(res.checks_failed) ? "text-danger" : ""}>{Number(res.checks_failed)}</span>} />
          </div>
          {circuits.map((c, ci) => (
            <Card key={ci} className="overflow-hidden p-0">
              <div className="flex items-center justify-between border-b border-border px-4 py-3">
                <span className="font-semibold">{c.circuit_reference || `Circuit ${ci + 1}`}</span>
                <Badge tone={c.overall_passed ? "success" : "danger"}>{c.overall_passed ? "Pass" : "Fail"}</Badge>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <tbody>
                    {c.checks.map((ck, k) => (
                      <tr key={k} className="border-t border-border">
                        <td className="px-4 py-2">{ck.check}<div className="text-xs text-muted">{ck.clause}</div></td>
                        <td className="px-4 py-2 text-muted">{ck.actual} <span className="text-xs">vs {ck.limit}</span></td>
                        <td className="px-4 py-2 text-right">
                          {ck.passed ? <CheckCircle2 size={16} className="ml-auto text-success" /> : <XCircle size={16} className="ml-auto text-danger" />}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
