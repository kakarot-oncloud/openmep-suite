import { Plus, Trash2, XCircle } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { Badge, Button, Card, Field, Input, Select, Spinner } from "../../components/ui.tsx";
import { api, ApiError } from "../../lib/api.ts";
import { REGIONS } from "../../lib/regions.ts";

interface Project {
  id: string;
  name: string;
  client: string;
  project_number: string;
  design_basis: Record<string, unknown>;
  result_count: number;
  updated_at: string;
}
interface SavedResult { id: number; module: string; title: string; compliant: boolean; created_at: string }

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selected, setSelected] = useState<Project | null>(null);
  const [results, setResults] = useState<SavedResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [form, setForm] = useState({ name: "", client: "", project_number: "", location: "", region: "gcc", ambient_temp_c: 45, power_factor: 0.85 });

  const load = useCallback(async () => {
    try {
      const d = await api.get<{ projects: Project[] }>("/api/projects");
      setProjects(d.projects);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Cannot load projects");
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  async function create() {
    if (!form.name.trim()) { setError("Project name is required"); return; }
    setBusy(true); setError(null);
    try {
      await api.post("/api/projects", {
        name: form.name, client: form.client, project_number: form.project_number, location: form.location,
        design_basis: { region: form.region, ambient_temp_c: form.ambient_temp_c, power_factor: form.power_factor },
      });
      setForm({ ...form, name: "", client: "", project_number: "", location: "" });
      await load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Create failed");
    } finally { setBusy(false); }
  }

  async function open(p: Project) {
    setSelected(p);
    try {
      const d = await api.get<{ results: SavedResult[] }>(`/api/projects/${p.id}/results`);
      setResults(d.results);
    } catch { setResults([]); }
  }

  async function remove(id: string) {
    await api.del(`/api/projects/${id}`).catch((e) => setError(e instanceof ApiError ? e.message : "Delete failed"));
    if (selected?.id === id) { setSelected(null); setResults([]); }
    await load();
  }

  const setF = (k: string, v: string | number) => setForm((s) => ({ ...s, [k]: v }));

  return (
    <div className="container-page py-12">
      <header className="mb-8">
        <Badge tone="brand" className="mb-3">🗂️ Workspace</Badge>
        <h1 className="text-3xl font-bold tracking-tight">Projects</h1>
        <p className="mt-2 max-w-2xl text-muted">Persistent project workspaces with a shared design basis and saved calculation results.</p>
      </header>

      {error && (
        <Card className="mb-6 border-danger/40 p-4"><div className="flex items-center gap-2 text-danger"><XCircle size={16} /> {error}</div></Card>
      )}

      <Card className="mb-6 p-6">
        <div className="mb-3 text-sm font-medium">New project</div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Field label="Name"><Input value={form.name} onChange={(e) => setF("name", e.target.value)} /></Field>
          <Field label="Client"><Input value={form.client} onChange={(e) => setF("client", e.target.value)} /></Field>
          <Field label="Project number"><Input value={form.project_number} onChange={(e) => setF("project_number", e.target.value)} /></Field>
          <Field label="Region"><Select value={form.region} onChange={(e) => setF("region", e.target.value)}>{REGIONS.map((r) => <option key={r.code} value={r.code}>{r.short}</option>)}</Select></Field>
        </div>
        <Button onClick={create} disabled={busy} className="mt-4">{busy ? <><Spinner /> Creating…</> : <><Plus size={16} /> Create project</>}</Button>
      </Card>

      <div className="grid gap-6 lg:grid-cols-[1fr_1fr]">
        <Card className="overflow-hidden p-0">
          <div className="border-b border-border px-4 py-3 font-semibold">Projects ({projects.length})</div>
          {projects.length === 0 ? (
            <p className="p-6 text-sm text-muted">No projects yet — create one above.</p>
          ) : (
            <ul>
              {projects.map((p) => (
                <li key={p.id} className={`flex items-center justify-between gap-3 border-t border-border px-4 py-3 ${selected?.id === p.id ? "bg-surface-2" : ""}`}>
                  <button className="min-w-0 flex-1 text-left" onClick={() => open(p)}>
                    <div className="truncate font-medium">{p.name}</div>
                    <div className="truncate text-xs text-muted">{p.client || "—"} · {String(p.design_basis.region ?? "")} · {p.result_count} results</div>
                  </button>
                  <button onClick={() => remove(p.id)} aria-label="Delete project" className="grid h-9 w-9 place-items-center rounded-lg text-muted hover:bg-surface hover:text-danger"><Trash2 size={16} /></button>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card className="p-6">
          {!selected ? (
            <div className="grid min-h-[160px] place-items-center text-center text-muted">Select a project to view its design basis and saved results.</div>
          ) : (
            <div>
              <div className="text-lg font-bold">{selected.name}</div>
              <div className="text-xs text-muted">{selected.project_number || "—"}</div>
              <div className="mt-4 text-sm font-medium">Design basis</div>
              <pre className="mt-1 overflow-x-auto rounded-lg bg-surface-2 p-3 text-xs text-muted">{JSON.stringify(selected.design_basis, null, 2)}</pre>
              <div className="mt-4 text-sm font-medium">Saved results ({results.length})</div>
              {results.length === 0 ? (
                <p className="mt-1 text-sm text-muted">No results saved to this project yet.</p>
              ) : (
                <ul className="mt-2 divide-y divide-border">
                  {results.map((r) => (
                    <li key={r.id} className="flex items-center justify-between py-2 text-sm">
                      <span>{r.title || r.module}</span>
                      <Badge tone={r.compliant ? "success" : "danger"}>{r.compliant ? "OK" : "Review"}</Badge>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
