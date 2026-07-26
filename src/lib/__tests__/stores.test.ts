import { describe, it, expect, beforeEach } from "vitest";
import {
  createProject,
  getProject,
  listProjects,
  updateProject,
  deleteProject,
  restoreProject,
  isValidProjectId,
  getProjectsDir,
  __resetProjectStore,
} from "../project-store.js";
import {
  listVersions,
  getVersion,
  compareVersions,
  __resetVersionStore,
} from "../version-store.js";
import {
  getBranding,
  saveBranding,
  deleteBrandingAsset,
  createTemplate,
  listTemplates,
  updateTemplate,
  deleteTemplate,
  __resetBrandingStore,
} from "../branding-store.js";
import { runAllCalcs } from "../calc-engine.js";

beforeEach(() => {
  __resetProjectStore();
  __resetVersionStore();
  __resetBrandingStore();
});

describe("project-store", () => {
  it("validates UUIDs", () => {
    expect(isValidProjectId("not-a-uuid")).toBe(false);
    expect(isValidProjectId("12345678-1234-1234-1234-123456789abc")).toBe(true);
  });

  it("creates, gets, lists, updates and deletes a project", async () => {
    const created = await createProject({ name: "Tower A", region: "DEWA" });
    expect(isValidProjectId(created.id)).toBe(true);
    expect(created.version).toBe(1);

    const fetched = await getProject(created.id);
    expect(fetched?.name).toBe("Tower A");

    const all = await listProjects();
    expect(all).toHaveLength(1);

    const updated = await updateProject(created.id, { name: "Tower B" });
    expect(updated?.name).toBe("Tower B");
    expect(updated?.version).toBe(2);

    const deleted = await deleteProject(created.id);
    expect(deleted).toBe(true);
    expect(await getProject(created.id)).toBeNull();
    expect(await deleteProject(created.id)).toBe(false);
  });

  it("returns null when updating a missing project", async () => {
    expect(
      await updateProject("12345678-1234-1234-1234-123456789abc", { name: "x" }),
    ).toBeNull();
  });
});

describe("version-store", () => {
  it("records a version per create/update and compares them", async () => {
    const dir = getProjectsDir();
    const project = await createProject({ name: "V1", totalFloors: 3 });
    await updateProject(project.id, { totalFloors: 5 });

    const versions = await listVersions(project.id, dir);
    expect(versions.map((v) => v.version)).toEqual([1, 2]);

    const v1 = await getVersion(project.id, 1, dir);
    expect(v1?.project.totalFloors).toBe(3);

    const diff = await compareVersions(project.id, 1, 2, dir);
    expect(diff?.changedFields).toContain("totalFloors");
    expect(diff?.changes["totalFloors"]).toEqual({ from: 3, to: 5 });
    expect(diff?.boqDelta).toHaveProperty("AED");
  });

  it("restores a prior version as a new snapshot", async () => {
    const dir = getProjectsDir();
    const project = await createProject({ name: "R", totalFloors: 1 });
    await updateProject(project.id, { totalFloors: 9 });
    const v1 = await getVersion(project.id, 1, dir);
    const restored = await restoreProject(project.id, v1!.project);
    expect(restored?.totalFloors).toBe(1);
    expect(restored?.version).toBe(3);
    const versions = await listVersions(project.id, dir);
    expect(versions).toHaveLength(3);
  });

  it("returns null comparing non-existent versions", async () => {
    const project = await createProject({ name: "N" });
    expect(await compareVersions(project.id, 1, 99, getProjectsDir())).toBeNull();
  });
});

describe("branding-store", () => {
  it("saves, reads and deletes branding assets", async () => {
    const id = "12345678-1234-1234-1234-123456789abc";
    expect(await getBranding(id)).toEqual({});

    await saveBranding(id, { companyName: "ACME", logoBase64: "AAA" });
    let branding = await getBranding(id);
    expect(branding.companyName).toBe("ACME");
    expect(branding.logoBase64).toBe("AAA");

    branding = await deleteBrandingAsset(id, "logoBase64");
    expect(branding.logoBase64).toBeUndefined();
    expect(branding.companyName).toBe("ACME");
  });

  it("manages report templates", async () => {
    const id = "12345678-1234-1234-1234-123456789abc";
    const tpl = await createTemplate(id, {
      name: "Client A",
      includedModules: ["electrical"],
    });
    expect((await listTemplates(id))).toHaveLength(1);

    const updated = await updateTemplate(id, tpl.id, { name: "Client B" });
    expect(updated?.name).toBe("Client B");
    expect(await updateTemplate(id, "missing", { name: "x" })).toBeNull();

    expect(await deleteTemplate(id, tpl.id)).toBe(true);
    expect(await deleteTemplate(id, tpl.id)).toBe(false);
    expect(await listTemplates(id)).toHaveLength(0);
  });
});

describe("calc-engine", () => {
  it("returns labelled placeholder results echoing project inputs", async () => {
    const project = await createProject({
      name: "Calc",
      region: "DEWA",
      totalFloors: 4,
    });
    const result = runAllCalcs(project);
    expect(result.projectId).toBe(project.id);
    expect(result.authority).toContain("python");
    expect(result.modules.length).toBeGreaterThan(0);
    for (const m of result.modules) {
      expect(m.status).toBe("placeholder");
      expect(m.inputsEcho.totalFloors).toBe(4);
    }
  });
});
