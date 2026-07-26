import { AlertTriangle, CheckCircle2, Plus, Trash2, XCircle } from "lucide-react";
import { useMemo, useState } from "react";
import { Navigate, useParams } from "react-router-dom";

import { api, ApiError } from "../lib/api.ts";
import type { CalculatorConfig, Field, ResultView } from "../data/calculators.tsx";
import { getCalculator } from "../data/calculators.tsx";
import { Badge, Button, Field as FieldWrap, Input, Select, Spinner, Stat } from "./ui.tsx";

type Values = Record<string, unknown>;

function coerce(field: Field, raw: string): string | number {
  if (field.type === "number") return raw === "" ? 0 : Number(raw);
  return raw;
}

function initialValues(cfg: CalculatorConfig): Values {
  const v: Values = {};
  for (const f of cfg.fields) v[f.name] = f.default;
  if (cfg.rows) v[cfg.rows.name] = cfg.rows.default.map((r) => ({ ...r }));
  return v;
}

function FieldInput({ field, value, onChange }: { field: Field; value: unknown; onChange: (v: string | number) => void }) {
  if (field.type === "select") {
    return (
      <Select value={String(value)} onChange={(e) => onChange(coerce(field, e.target.value))}>
        {field.options?.map((o) => (
          <option key={String(o.value)} value={String(o.value)}>{o.label}</option>
        ))}
      </Select>
    );
  }
  return (
    <Input
      type={field.type === "number" ? "number" : "text"}
      step={field.step}
      value={value as string | number}
      onChange={(e) => onChange(coerce(field, e.target.value))}
    />
  );
}

export default function CalculatorPage() {
  const { slug } = useParams();
  const cfg = slug ? getCalculator(slug) : undefined;
  const [values, setValues] = useState<Values>(() => (cfg ? initialValues(cfg) : {}));
  const [result, setResult] = useState<ResultView | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const rowsData = useMemo(
    () => (cfg?.rows ? ((values[cfg.rows.name] as Record<string, unknown>[]) ?? []) : []),
    [cfg, values],
  );

  if (!cfg) return <Navigate to="/modules" replace />;

  const setField = (name: string, v: string | number) => setValues((s) => ({ ...s, [name]: v }));

  const setRow = (idx: number, name: string, v: string | number) =>
    setValues((s) => {
      const rows = [...((s[cfg.rows!.name] as Record<string, unknown>[]) ?? [])];
      rows[idx] = { ...rows[idx], [name]: v };
      return { ...s, [cfg.rows!.name]: rows };
    });

  const addRow = () =>
    setValues((s) => ({
      ...s,
      [cfg.rows!.name]: [...((s[cfg.rows!.name] as Record<string, unknown>[]) ?? []), { ...cfg.rows!.default[0] }],
    }));

  const removeRow = (idx: number) =>
    setValues((s) => ({
      ...s,
      [cfg.rows!.name]: ((s[cfg.rows!.name] as Record<string, unknown>[]) ?? []).filter((_, i) => i !== idx),
    }));

  async function calculate() {
    setLoading(true);
    setError(null);
    try {
      const payload = cfg!.buildPayload ? cfg!.buildPayload(values) : values;
      const data = await api.post<Record<string, unknown>>(cfg!.endpoint, payload);
      setResult(cfg!.result(data));
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
        <Badge tone="brand" className="mb-3">{cfg.icon} {cfg.discipline}</Badge>
        <h1 className="text-3xl font-bold tracking-tight">{cfg.name}</h1>
        <p className="mt-2 max-w-2xl text-muted">{cfg.blurb}</p>
        <p className="mt-1 text-xs text-muted">{cfg.standard}</p>
      </header>

      <div className={`grid gap-6 ${cfg.rows ? "" : "lg:grid-cols-[380px_1fr]"}`}>
        {/* Inputs */}
        <div className="rounded-2xl border border-border bg-surface p-6">
          <div className="grid gap-4 sm:grid-cols-2">
            {cfg.fields.map((f) => (
              <div key={f.name} className={f.type === "select" || f.name === "region" ? "sm:col-span-2" : ""}>
                <FieldWrap label={f.label} hint={f.hint}>
                  <FieldInput field={f} value={values[f.name]} onChange={(v) => setField(f.name, v)} />
                </FieldWrap>
              </div>
            ))}
          </div>

          {cfg.rows && (
            <div className="mt-6">
              <div className="mb-2 text-sm font-medium">{cfg.rows.label}</div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-xs text-muted">
                      {cfg.rows.itemFields.map((f) => (
                        <th key={f.name} className="px-1.5 pb-2 font-medium">{f.label}</th>
                      ))}
                      <th className="pb-2" />
                    </tr>
                  </thead>
                  <tbody>
                    {rowsData.map((row, i) => (
                      <tr key={i}>
                        {cfg.rows!.itemFields.map((f) => (
                          <td key={f.name} className="px-1 py-1 align-top">
                            <FieldInput field={f} value={row[f.name]} onChange={(v) => setRow(i, f.name, v)} />
                          </td>
                        ))}
                        <td className="px-1 py-1 align-middle">
                          <button
                            onClick={() => removeRow(i)}
                            aria-label="Remove row"
                            className="grid h-9 w-9 place-items-center rounded-lg text-muted hover:bg-surface-2 hover:text-danger"
                          >
                            <Trash2 size={16} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <Button variant="outline" size="sm" className="mt-3" onClick={addRow}>
                <Plus size={16} /> {cfg.rows.addLabel}
              </Button>
            </div>
          )}

          <Button onClick={calculate} disabled={loading} size="lg" className="mt-6 w-full">
            {loading ? <><Spinner /> Calculating…</> : "Calculate"}
          </Button>
        </div>

        {/* Results */}
        <div>
          {error && (
            <div className="rounded-2xl border border-danger/40 bg-surface p-6">
              <div className="flex items-center gap-2 text-danger">
                <XCircle size={18} /> <span className="font-semibold">{error}</span>
              </div>
            </div>
          )}

          {!error && !result && (
            <div className="grid min-h-[240px] place-items-center rounded-2xl border border-border bg-surface p-10 text-center">
              <div>
                <div className="text-4xl">{cfg.icon}</div>
                <p className="mt-3 text-muted">Enter parameters and press <b>Calculate</b>.</p>
              </div>
            </div>
          )}

          {result && <ResultBlock view={result} />}
        </div>
      </div>
    </div>
  );
}

function ResultBlock({ view }: { view: ResultView }) {
  return (
    <div className="grid gap-5">
      {view.headline && (
        <div className="rounded-2xl border border-border bg-surface p-6">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <div className="text-sm text-muted">{view.headline.label}</div>
              <div className="mt-0.5 text-4xl font-extrabold text-brand">
                {view.headline.value}
                {view.headline.unit && <span className="ml-1.5 text-xl font-medium text-muted">{view.headline.unit}</span>}
              </div>
            </div>
            {view.badge && (
              <Badge tone={view.badge.ok ? "success" : "danger"} className="text-sm">
                {view.badge.ok ? <CheckCircle2 size={14} /> : <XCircle size={14} />} {view.badge.text}
              </Badge>
            )}
          </div>
          {view.note && <p className="mt-3 text-xs text-muted">{view.note}</p>}
        </div>
      )}

      {view.stats && view.stats.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {view.stats.map((s, i) => (
            <Stat key={i} label={s.label} value={s.value} unit={s.unit} />
          ))}
        </div>
      )}

      {view.warnings && view.warnings.length > 0 && (
        <div className="rounded-2xl border border-warn/40 bg-surface p-5">
          <div className="mb-2 flex items-center gap-2 font-semibold text-warn">
            <AlertTriangle size={16} /> Notes
          </div>
          <ul className="space-y-1.5 text-sm text-muted">
            {view.warnings.map((w, i) => (
              <li key={i}>{w.replace(/^⚠️\s*/, "")}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
