import { CheckCircle2, XCircle } from "lucide-react";
import { useState } from "react";

import RowEditor, { type Column } from "../../components/RowEditor.tsx";
import { Badge, Button, Card, Field, Input, Select, Spinner, Stat } from "../../components/ui.tsx";
import { api, ApiError } from "../../lib/api.ts";
import { REGIONS } from "../../lib/regions.ts";

const COLS: Column[] = [
  { name: "section", label: "Section", type: "text" },
  { name: "reference", label: "Ref", type: "text" },
  { name: "description", label: "Description", type: "text" },
  { name: "standard", label: "Standard", type: "text" },
  { name: "compliant", label: "Compliant", type: "select", options: [{ value: "true", label: "Yes" }, { value: "false", label: "No" }] },
];
const BLANK = { section: "Electrical", reference: "", description: "", standard: "BS 7671", compliant: "true" };

export default function Report() {
  const [region, setRegion] = useState("gcc");
  const [projectName, setProjectName] = useState("Tower A");
  const [preparedBy, setPreparedBy] = useState("");
  const [title, setTitle] = useState("Engineering Calculation Report");
  const [rows, setRows] = useState<Record<string, string | number>[]>([
    { section: "Cable Sizing", reference: "C1", description: "MDB main feeder", standard: "BS 7671", compliant: "true" },
    { section: "Cooling Load", reference: "AHU-1", description: "Level 5 open plan", standard: "ASHRAE", compliant: "true" },
  ]);
  const [res, setRes] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.post<Record<string, unknown>>("/api/reports/calculation-report", {
        metadata: { project_name: projectName, prepared_by: preparedBy, region, report_title: title },
        calculations: rows.map((r) => ({
          section: r.section,
          reference: r.reference,
          description: r.description,
          standard: r.standard,
          compliant: String(r.compliant) === "true",
        })),
        include_appendix: true,
      });
      setRes(data);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Something went wrong");
      setRes(null);
    } finally {
      setLoading(false);
    }
  }

  const report = res?.report as Record<string, unknown> | undefined;
  const summary = report?.summary as Record<string, number | boolean> | undefined;
  const sections = (report?.sections as Record<string, Record<string, unknown>[]>) ?? {};

  return (
    <div className="container-page py-12">
      <header className="mb-8">
        <Badge tone="brand" className="mb-3">📄 Reports</Badge>
        <h1 className="text-3xl font-bold tracking-tight">Report Builder</h1>
        <p className="mt-2 max-w-2xl text-muted">Compile calculation entries into a structured, audit-ready report payload (render to PDF/Excel/HTML).</p>
      </header>

      <Card className="p-6">
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Region"><Select value={region} onChange={(e) => setRegion(e.target.value)}>{REGIONS.map((r) => <option key={r.code} value={r.code}>{r.short}</option>)}</Select></Field>
          <Field label="Report title"><Input value={title} onChange={(e) => setTitle(e.target.value)} /></Field>
          <Field label="Project name"><Input value={projectName} onChange={(e) => setProjectName(e.target.value)} /></Field>
          <Field label="Prepared by"><Input value={preparedBy} onChange={(e) => setPreparedBy(e.target.value)} /></Field>
        </div>
        <div className="mt-6">
          <div className="mb-2 text-sm font-medium">Calculation entries</div>
          <RowEditor columns={COLS} rows={rows} onChange={setRows} addLabel="Add entry" blank={BLANK} />
        </div>
        <Button onClick={generate} disabled={loading} size="lg" className="mt-6 w-full sm:w-auto">
          {loading ? <><Spinner /> Generating…</> : "Generate report"}
        </Button>
      </Card>

      {error && (
        <Card className="mt-6 border-danger/40 p-6"><div className="flex items-center gap-2 text-danger"><XCircle size={18} /> <span className="font-semibold">{error}</span></div></Card>
      )}

      {summary && (
        <div className="mt-6 grid gap-5">
          <Card className="p-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="text-sm text-muted">{title}</div>
                <div className="text-2xl font-bold">{projectName}</div>
              </div>
              <Badge tone={summary.overall_compliant ? "success" : "danger"} className="text-sm">
                {summary.overall_compliant ? <CheckCircle2 size={14} /> : <XCircle size={14} />} {summary.overall_compliant ? "All compliant" : "Issues found"}
              </Badge>
            </div>
          </Card>
          <div className="grid gap-4 sm:grid-cols-3">
            <Stat label="Calculations" value={Number(summary.total_calculations)} />
            <Stat label="Passed" value={<span className="text-success">{Number(summary.calculations_passed)}</span>} />
            <Stat label="Failed" value={<span className={Number(summary.calculations_failed) ? "text-danger" : ""}>{Number(summary.calculations_failed)}</span>} />
          </div>
          {Object.entries(sections).map(([name, entries]) => (
            <Card key={name} className="overflow-hidden p-0">
              <div className="border-b border-border px-4 py-3 font-semibold">{name}</div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <tbody>
                    {entries.map((e, i) => (
                      <tr key={i} className="border-t border-border">
                        <td className="px-4 py-2">{String(e.reference ?? "")}</td>
                        <td className="px-4 py-2">{String(e.description ?? "")}<div className="text-xs text-muted">{String(e.standard ?? "")}</div></td>
                        <td className="px-4 py-2 text-right">
                          {e.compliant ? <CheckCircle2 size={16} className="ml-auto text-success" /> : <XCircle size={16} className="ml-auto text-danger" />}
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
