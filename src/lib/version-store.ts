/**
 * version-store.ts — in-memory project version-snapshot store.
 *
 * Every create/update/restore of a project records an immutable snapshot here.
 * Map-based, process-memory only. The `dir` argument that callers pass
 * (the projects directory) is accepted for signature compatibility with the
 * on-disk design but is intentionally unused by this in-memory implementation.
 */
import type { Project } from "./project-store.js";

export interface VersionEntry {
  version: number;
  createdAt: string;
  label: string;
  project: Project;
}

export interface VersionSummary {
  version: number;
  createdAt: string;
  label: string;
}

export interface VersionComparison {
  projectId: string;
  from: number;
  to: number;
  changedFields: string[];
  changes: Record<string, { from: unknown; to: unknown }>;
  /**
   * BOQ (bill of quantities) cost delta. Honest placeholder: the Python
   * FastAPI backend is the authority for real BOQ costing, so this reports a
   * zero delta with the currencies the platform tracks rather than inventing
   * numbers.
   */
  boqDelta: Record<string, number>;
}

// projectId -> ordered list of version snapshots
const versionsByProject = new Map<string, VersionEntry[]>();

/**
 * Append a new snapshot for a project. Called by project-store on
 * create/update/restore. Returns the newly assigned version number.
 */
export function recordVersion(
  projectId: string,
  project: Project,
  label = "snapshot",
): number {
  const list = versionsByProject.get(projectId) ?? [];
  const version = list.length + 1;
  list.push({
    version,
    createdAt: new Date().toISOString(),
    label,
    project: structuredClone(project),
  });
  versionsByProject.set(projectId, list);
  return version;
}

export async function listVersions(
  projectId: string,
  _dir?: string,
): Promise<VersionSummary[]> {
  const list = versionsByProject.get(projectId) ?? [];
  return list.map((v) => ({
    version: v.version,
    createdAt: v.createdAt,
    label: v.label,
  }));
}

export async function getVersion(
  projectId: string,
  version: number,
  _dir?: string,
): Promise<VersionEntry | null> {
  const list = versionsByProject.get(projectId) ?? [];
  const found = list.find((v) => v.version === version);
  if (!found) return null;
  return { ...found, project: structuredClone(found.project) };
}

export async function compareVersions(
  projectId: string,
  from: number,
  to: number,
  _dir?: string,
): Promise<VersionComparison | null> {
  const list = versionsByProject.get(projectId) ?? [];
  const a = list.find((v) => v.version === from);
  const b = list.find((v) => v.version === to);
  if (!a || !b) return null;

  const changes: Record<string, { from: unknown; to: unknown }> = {};
  const aRec = a.project as unknown as Record<string, unknown>;
  const bRec = b.project as unknown as Record<string, unknown>;
  const keys = new Set<string>([...Object.keys(aRec), ...Object.keys(bRec)]);
  for (const key of keys) {
    if (key === "updatedAt" || key === "version") continue;
    const av = aRec[key];
    const bv = bRec[key];
    if (JSON.stringify(av) !== JSON.stringify(bv)) {
      changes[key] = { from: av, to: bv };
    }
  }

  return {
    projectId,
    from,
    to,
    changedFields: Object.keys(changes),
    changes,
    boqDelta: { AED: 0, INR: 0, GBP: 0, AUD: 0 },
  };
}

/** Test-only helper to reset store state between tests. */
export function __resetVersionStore(): void {
  versionsByProject.clear();
}
