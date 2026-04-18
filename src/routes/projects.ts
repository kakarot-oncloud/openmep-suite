import { Router, type IRouter } from "express";
import multer from "multer";
import { z } from "zod/v4";
import {
  listProjects,
  getProject,
  createProject,
  updateProject,
  deleteProject,
  restoreProject,
  isValidProjectId,
  getProjectsDir,
} from "../lib/project-store";
import { runAllCalcs } from "../lib/calc-engine";
import {
  listVersions,
  getVersion,
  compareVersions,
} from "../lib/version-store";
import {
  getBranding,
  saveBranding,
  deleteBrandingAsset,
  listTemplates,
  createTemplate,
  updateTemplate,
  deleteTemplate,
} from "../lib/branding-store";

const router: IRouter = Router();

const designConditionsSchema = z.object({
  ambientTempC: z.number().optional(),
  occupancyDensity: z.number().optional(),
  lightingLoadWpm2: z.number().optional(),
  equipmentLoadWpm2: z.number().optional(),
  freshAirLps: z.number().optional(),
});

const spaceSchema = z.object({
  id: z.string(),
  name: z.string(),
  floorNumber: z.number().int(),
  areaM2: z.number(),
  occupancy: z.number().int().optional(),
  spaceType: z.string().optional(),
});

const createProjectSchema = z.object({
  name: z.string().min(1, "Project name is required"),
  client: z.string().optional(),
  engineer: z.string().optional(),
  date: z.string().optional(),
  region: z.string().optional(),
  subRegion: z.string().optional(),
  buildingType: z.string().optional(),
  totalFloors: z.number().int().positive().optional(),
  totalAreaM2: z.number().positive().optional(),
  occupancy: z.number().int().nonnegative().optional(),
  designConditions: designConditionsSchema.optional(),
  spaces: z.array(spaceSchema).optional(),
  customFields: z.record(z.string(), z.unknown()).optional(),
});

const updateProjectSchema = createProjectSchema.partial();

function formatError(err: z.ZodError): string {
  return err.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; ");
}

function validateId(id: string | undefined): string | null {
  if (!id || !isValidProjectId(id)) return null;
  return id;
}

router.get("/projects", async (_req, res) => {
  const projects = await listProjects();
  res.json(projects);
});

router.post("/projects", async (req, res) => {
  const result = createProjectSchema.safeParse(req.body);
  if (!result.success) {
    res.status(400).json({ error: "validation_error", message: formatError(result.error) });
    return;
  }
  const project = await createProject(result.data);
  res.status(201).json(project);
});

router.get("/projects/:id", async (req, res) => {
  const id = validateId(req.params["id"]);
  if (!id) {
    res.status(400).json({ error: "invalid_id", message: "Project ID must be a valid UUID" });
    return;
  }
  const project = await getProject(id);
  if (!project) {
    res.status(404).json({ error: "not_found", message: "Project not found" });
    return;
  }
  res.json(project);
});

router.put("/projects/:id", async (req, res) => {
  const id = validateId(req.params["id"]);
  if (!id) {
    res.status(400).json({ error: "invalid_id", message: "Project ID must be a valid UUID" });
    return;
  }
  const result = updateProjectSchema.safeParse(req.body);
  if (!result.success) {
    res.status(400).json({ error: "validation_error", message: formatError(result.error) });
    return;
  }
  const project = await updateProject(id, result.data);
  if (!project) {
    res.status(404).json({ error: "not_found", message: "Project not found" });
    return;
  }
  res.json(project);
});

router.delete("/projects/:id", async (req, res) => {
  const id = validateId(req.params["id"]);
  if (!id) {
    res.status(400).json({ error: "invalid_id", message: "Project ID must be a valid UUID" });
    return;
  }
  const deleted = await deleteProject(id);
  if (!deleted) {
    res.status(404).json({ error: "not_found", message: "Project not found" });
    return;
  }
  res.status(204).send();
});

router.post("/projects/:id/refresh", async (req, res) => {
  const id = validateId(req.params["id"]);
  if (!id) {
    res.status(400).json({ error: "invalid_id", message: "Project ID must be a valid UUID" });
    return;
  }
  const project = await getProject(id);
  if (!project) {
    res.status(404).json({ error: "not_found", message: "Project not found" });
    return;
  }
  const calcResults = runAllCalcs(project);
  res.json(calcResults);
});

router.get("/projects/:id/versions", async (req, res) => {
  const id = validateId(req.params["id"]);
  if (!id) {
    res.status(400).json({ error: "invalid_id", message: "Project ID must be a valid UUID" });
    return;
  }
  const project = await getProject(id);
  if (!project) {
    res.status(404).json({ error: "not_found", message: "Project not found" });
    return;
  }
  const versions = await listVersions(id, getProjectsDir());
  res.json({ projectId: id, projectName: project.name, versions });
});

router.get("/projects/:id/versions/:version", async (req, res) => {
  const id = validateId(req.params["id"]);
  if (!id) {
    res.status(400).json({ error: "invalid_id", message: "Project ID must be a valid UUID" });
    return;
  }
  const versionNum = parseInt(req.params["version"] ?? "", 10);
  if (isNaN(versionNum) || versionNum < 1) {
    res.status(400).json({ error: "invalid_version", message: "Version must be a positive integer" });
    return;
  }
  const versionData = await getVersion(id, versionNum, getProjectsDir());
  if (!versionData) {
    res.status(404).json({ error: "not_found", message: `Version ${versionNum} not found` });
    return;
  }
  res.json(versionData);
});

router.get("/projects/:id/compare", async (req, res) => {
  const id = validateId(req.params["id"]);
  if (!id) {
    res.status(400).json({ error: "invalid_id", message: "Project ID must be a valid UUID" });
    return;
  }
  const from = parseInt(String(req.query["from"] ?? ""), 10);
  const to = parseInt(String(req.query["to"] ?? ""), 10);
  if (isNaN(from) || isNaN(to) || from < 1 || to < 1) {
    res.status(400).json({ error: "invalid_params", message: "Query params 'from' and 'to' must be positive integers" });
    return;
  }
  if (from === to) {
    res.status(400).json({ error: "invalid_params", message: "'from' and 'to' must be different versions" });
    return;
  }
  const project = await getProject(id);
  if (!project) {
    res.status(404).json({ error: "not_found", message: "Project not found" });
    return;
  }
  const diff = await compareVersions(id, from, to, getProjectsDir());
  if (!diff) {
    res.status(404).json({ error: "not_found", message: `One or both versions (${from}, ${to}) not found` });
    return;
  }
  res.json(diff);
});

router.post("/projects/:id/restore/:version", async (req, res) => {
  const id = validateId(req.params["id"]);
  if (!id) {
    res.status(400).json({ error: "invalid_id", message: "Project ID must be a valid UUID" });
    return;
  }
  const versionNum = parseInt(req.params["version"] ?? "", 10);
  if (isNaN(versionNum) || versionNum < 1) {
    res.status(400).json({ error: "invalid_version", message: "Version must be a positive integer" });
    return;
  }
  const versionData = await getVersion(id, versionNum, getProjectsDir());
  if (!versionData) {
    res.status(404).json({ error: "not_found", message: `Version ${versionNum} not found` });
    return;
  }
  const currentProject = await getProject(id);
  if (!currentProject) {
    res.status(404).json({ error: "not_found", message: "Project not found" });
    return;
  }
  const restoredProject = await restoreProject(id, versionData.project);
  if (!restoredProject) {
    res.status(404).json({ error: "not_found", message: "Project not found" });
    return;
  }
  const newVersions = await listVersions(id, getProjectsDir());
  const newVersion = newVersions[newVersions.length - 1]?.version;
  res.json({ restored: true, fromVersion: versionNum, newVersion, project: restoredProject });
});

const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 4 * 1024 * 1024 } });

const ALLOWED_ASSET_FIELDS = ["logoBase64", "letterheadBase64", "stampBase64"] as const;
type AssetField = typeof ALLOWED_ASSET_FIELDS[number];

function isAssetField(f: unknown): f is AssetField {
  return ALLOWED_ASSET_FIELDS.includes(f as AssetField);
}

const brandingBodySchema = z.object({
  companyName: z.string().optional(),
  engineerName: z.string().optional(),
  licenceNumber: z.string().optional(),
  footerText: z.string().optional(),
  primaryColor: z.string().optional(),
});

router.get("/projects/:id/branding", async (req, res) => {
  const id = validateId(req.params["id"]);
  if (!id) { res.status(400).json({ error: "invalid_id" }); return; }
  const project = await getProject(id);
  if (!project) { res.status(404).json({ error: "not_found" }); return; }
  const branding = await getBranding(id);
  const sanitised = { ...branding, logoBase64: branding.logoBase64 ? "[set]" : undefined, letterheadBase64: branding.letterheadBase64 ? "[set]" : undefined, stampBase64: branding.stampBase64 ? "[set]" : undefined };
  res.json(sanitised);
});

router.put("/projects/:id/branding", async (req, res) => {
  const id = validateId(req.params["id"]);
  if (!id) { res.status(400).json({ error: "invalid_id" }); return; }
  const project = await getProject(id);
  if (!project) { res.status(404).json({ error: "not_found" }); return; }
  const parsed = brandingBodySchema.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "validation_error", message: formatError(parsed.error) });
    return;
  }
  try {
    const branding = await saveBranding(id, parsed.data);
    const sanitised = { ...branding, logoBase64: branding.logoBase64 ? "[set]" : undefined, letterheadBase64: branding.letterheadBase64 ? "[set]" : undefined, stampBase64: branding.stampBase64 ? "[set]" : undefined };
    res.json(sanitised);
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : "Unknown error";
    res.status(400).json({ error: "invalid_input", message: msg });
  }
});

router.post("/projects/:id/branding/upload", upload.single("file"), async (req, res) => {
  const id = validateId(req.params["id"]);
  if (!id) { res.status(400).json({ error: "invalid_id" }); return; }
  const project = await getProject(id);
  if (!project) { res.status(404).json({ error: "not_found" }); return; }

  const field = req.body?.["field"] as unknown;
  if (!isAssetField(field)) {
    res.status(400).json({ error: "invalid_field", message: `field must be one of: ${ALLOWED_ASSET_FIELDS.join(", ")}` });
    return;
  }

  if (!req.file) {
    res.status(400).json({ error: "missing_file", message: "No file uploaded" });
    return;
  }

  const mimeOk = ["image/png", "image/jpeg", "image/jpg", "image/webp"].includes(req.file.mimetype);
  if (!mimeOk) {
    res.status(400).json({ error: "invalid_file_type", message: "Only PNG, JPG, JPEG, and WebP images are supported" });
    return;
  }

  const base64 = req.file.buffer.toString("base64");
  const branding = await saveBranding(id, { [field]: base64 });
  const sanitised = { ...branding, logoBase64: branding.logoBase64 ? "[set]" : undefined, letterheadBase64: branding.letterheadBase64 ? "[set]" : undefined, stampBase64: branding.stampBase64 ? "[set]" : undefined };
  res.json({ uploaded: field, branding: sanitised });
});

router.delete("/projects/:id/branding/:field", async (req, res) => {
  const id = validateId(req.params["id"]);
  if (!id) { res.status(400).json({ error: "invalid_id" }); return; }
  const field = req.params["field"] as unknown;
  if (!isAssetField(field)) {
    res.status(400).json({ error: "invalid_field" });
    return;
  }
  const project = await getProject(id);
  if (!project) { res.status(404).json({ error: "not_found" }); return; }
  const branding = await deleteBrandingAsset(id, field);
  res.json(branding);
});

router.get("/projects/:id/templates", async (req, res) => {
  const id = validateId(req.params["id"]);
  if (!id) { res.status(400).json({ error: "invalid_id" }); return; }
  const project = await getProject(id);
  if (!project) { res.status(404).json({ error: "not_found" }); return; }
  const templates = await listTemplates(id);
  res.json(templates);
});

const templateBodySchema = z.object({
  name: z.string().min(1),
  includedModules: z.array(z.string()).optional(),
  coverIntro: z.string().optional(),
});

router.post("/projects/:id/templates", async (req, res) => {
  const id = validateId(req.params["id"]);
  if (!id) { res.status(400).json({ error: "invalid_id" }); return; }
  const project = await getProject(id);
  if (!project) { res.status(404).json({ error: "not_found" }); return; }
  const parsed = templateBodySchema.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "validation_error", message: formatError(parsed.error) });
    return;
  }
  const template = await createTemplate(id, parsed.data);
  res.status(201).json(template);
});

router.put("/projects/:id/templates/:tid", async (req, res) => {
  const id = validateId(req.params["id"]);
  if (!id) { res.status(400).json({ error: "invalid_id" }); return; }
  const tid = req.params["tid"];
  if (!tid) { res.status(400).json({ error: "invalid_template_id" }); return; }
  const project = await getProject(id);
  if (!project) { res.status(404).json({ error: "not_found" }); return; }
  const parsed = templateBodySchema.partial().safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "validation_error", message: formatError(parsed.error) });
    return;
  }
  const updated = await updateTemplate(id, tid, parsed.data);
  if (!updated) { res.status(404).json({ error: "not_found", message: "Template not found" }); return; }
  res.json(updated);
});

router.delete("/projects/:id/templates/:tid", async (req, res) => {
  const id = validateId(req.params["id"]);
  if (!id) { res.status(400).json({ error: "invalid_id" }); return; }
  const tid = req.params["tid"];
  if (!tid) { res.status(400).json({ error: "invalid_template_id" }); return; }
  const project = await getProject(id);
  if (!project) { res.status(404).json({ error: "not_found" }); return; }
  const deleted = await deleteTemplate(id, tid);
  if (!deleted) { res.status(404).json({ error: "not_found", message: "Template not found" }); return; }
  res.status(204).send();
});

export default router;

