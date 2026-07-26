/**
 * project-store.ts — in-memory project metadata store.
 *
 * Simple, honest Map-based persistence for project workspaces. State lives in
 * process memory only. Every create/update/restore records a version snapshot
 * via version-store (the "version hooks" referenced in the README).
 */
import { randomUUID } from "node:crypto";
import { recordVersion } from "./version-store.js";

export interface DesignConditions {
  ambientTempC?: number;
  occupancyDensity?: number;
  lightingLoadWpm2?: number;
  equipmentLoadWpm2?: number;
  freshAirLps?: number;
}

export interface Space {
  id: string;
  name: string;
  floorNumber: number;
  areaM2: number;
  occupancy?: number;
  spaceType?: string;
}

export interface ProjectInput {
  name: string;
  client?: string;
  engineer?: string;
  date?: string;
  region?: string;
  subRegion?: string;
  buildingType?: string;
  totalFloors?: number;
  totalAreaM2?: number;
  occupancy?: number;
  designConditions?: DesignConditions;
  spaces?: Space[];
  customFields?: Record<string, unknown>;
}

export interface Project extends ProjectInput {
  id: string;
  version: number;
  createdAt: string;
  updatedAt: string;
}

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

// projectId -> project
const projects = new Map<string, Project>();

// Location where an on-disk implementation would keep project files. The
// in-memory store does not write here; it is exposed only because route
// handlers thread it through to the version-store functions.
const PROJECTS_DIR = process.env["OPENMEP_PROJECTS_DIR"] ?? "./data/projects";

export function getProjectsDir(): string {
  return PROJECTS_DIR;
}

export function isValidProjectId(id: string): boolean {
  return typeof id === "string" && UUID_RE.test(id);
}

export async function listProjects(): Promise<Project[]> {
  return [...projects.values()].map((p) => ({ ...p }));
}

export async function getProject(id: string): Promise<Project | null> {
  const p = projects.get(id);
  return p ? { ...p } : null;
}

export async function createProject(data: ProjectInput): Promise<Project> {
  const now = new Date().toISOString();
  const project: Project = {
    ...data,
    id: randomUUID(),
    version: 1,
    createdAt: now,
    updatedAt: now,
  };
  projects.set(project.id, project);
  recordVersion(project.id, project, "created");
  return { ...project };
}

export async function updateProject(
  id: string,
  data: Partial<ProjectInput>,
): Promise<Project | null> {
  const existing = projects.get(id);
  if (!existing) return null;
  const updated: Project = {
    ...existing,
    ...data,
    id: existing.id,
    version: existing.version + 1,
    createdAt: existing.createdAt,
    updatedAt: new Date().toISOString(),
  };
  projects.set(id, updated);
  recordVersion(id, updated, "updated");
  return { ...updated };
}

export async function deleteProject(id: string): Promise<boolean> {
  return projects.delete(id);
}

/**
 * Restore a project's metadata from a previous snapshot. Produces a fresh
 * version so history stays append-only.
 */
export async function restoreProject(
  id: string,
  snapshot: Project,
): Promise<Project | null> {
  const existing = projects.get(id);
  if (!existing) return null;
  const restored: Project = {
    ...snapshot,
    id: existing.id,
    version: existing.version + 1,
    createdAt: existing.createdAt,
    updatedAt: new Date().toISOString(),
  };
  projects.set(id, restored);
  recordVersion(id, restored, "restored");
  return { ...restored };
}

/** Test-only helper to reset store state between tests. */
export function __resetProjectStore(): void {
  projects.clear();
}
