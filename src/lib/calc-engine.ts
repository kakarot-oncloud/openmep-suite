/**
 * calc-engine.ts — project calculation orchestration (Node side).
 *
 * IMPORTANT: This is NOT the real engineering calculation authority. The Python
 * FastAPI service (backend/, port 8000) performs the actual electrical /
 * mechanical / plumbing / fire calculations. This module returns clearly
 * labelled, structured placeholder/echo results derived only from the project's
 * stored inputs, so the Node API has a coherent shape to return from the
 * `/projects/:id/refresh` endpoint without duplicating (and risking drift from)
 * the Python math.
 */
import type { Project } from "./project-store.js";

export interface CalcModuleResult {
  module: string;
  status: "placeholder";
  note: string;
  inputsEcho: Record<string, unknown>;
}

export interface CalcRunResult {
  projectId: string;
  projectName: string;
  generatedAt: string;
  authority: string;
  modules: CalcModuleResult[];
}

const NOTE =
  "Placeholder result. Authoritative calculation is performed by the Python " +
  "FastAPI backend on port 8000; this Node endpoint only echoes stored project " +
  "inputs.";

export function runAllCalcs(project: Project): CalcRunResult {
  const dc = project.designConditions ?? {};
  const commonInputs = {
    region: project.region,
    subRegion: project.subRegion,
    buildingType: project.buildingType,
    totalFloors: project.totalFloors,
    totalAreaM2: project.totalAreaM2,
    occupancy: project.occupancy,
    designConditions: dc,
    spaceCount: project.spaces?.length ?? 0,
  };

  const modules: CalcModuleResult[] = [
    "electrical",
    "hvac",
    "plumbing",
    "fire_protection",
  ].map((module) => ({
    module,
    status: "placeholder",
    note: NOTE,
    inputsEcho: commonInputs,
  }));

  return {
    projectId: project.id,
    projectName: project.name,
    generatedAt: new Date().toISOString(),
    authority: "python-fastapi:8000",
    modules,
  };
}
