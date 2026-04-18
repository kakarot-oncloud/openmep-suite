import { Router, type IRouter, type Request, type Response } from "express";
import { z } from "zod/v4";
import {
  runComplianceCheck,
  type ModuleResult,
} from "../engines/compliance-guardian.js";
import { buildSubmissionPackage } from "../engines/submission-service.js";
import { getBranding } from "../lib/branding-store.js";
import { isValidProjectId } from "../lib/project-store.js";

const ModuleTypeSchema = z.enum([
  "electrical",
  "hvac",
  "fire_protection",
  "plumbing",
  "structural",
]);

const RegionSchema = z.enum(["DEWA", "IS", "AS_NZS", "IEC", "NFPA"]);

const ModuleResultSchema = z.object({
  module: ModuleTypeSchema,
  region: RegionSchema,
  parameters: z.record(z.string(), z.union([z.number(), z.string()])),
});

const ComplianceCheckRequest = z.object({
  moduleResults: z.array(ModuleResultSchema),
});

const ComplianceCheckResponse = z.object({
  violations: z.array(z.any()),
  hasErrors: z.boolean(),
  errorCount: z.number(),
  warningCount: z.number(),
  infoCount: z.number(),
});

const ProjectDetailsSchema = z.object({
  projectName: z.string(),
  projectNumber: z.string(),
  clientName: z.string(),
  engineerName: z.string(),
  engineerLicense: z.string().optional(),
  companyName: z.string(),
  submissionDate: z.string(),
  revisionNumber: z.string(),
  notes: z.string().optional(),
});

const SubmissionPackageRequest = z.object({
  projectDetails: ProjectDetailsSchema,
  moduleResults: z.array(ModuleResultSchema),
  includedModules: z.array(z.string()).optional(),
  projectId: z.string().optional(),
  templateId: z.string().optional(),
});

const router: IRouter = Router();

router.post(
  "/submission/compliance-check",
  async (req: Request, res: Response) => {
    const parsed = ComplianceCheckRequest.safeParse(req.body);
    if (!parsed.success) {
      res.status(400).json({ error: "Invalid request", details: parsed.error.issues });
      return;
    }

    const violations = runComplianceCheck(
      parsed.data.moduleResults as ModuleResult[],
    );

    const response = ComplianceCheckResponse.parse({
      violations,
      hasErrors: violations.some((v) => v.severity === "error"),
      errorCount: violations.filter((v) => v.severity === "error").length,
      warningCount: violations.filter((v) => v.severity === "warning").length,
      infoCount: violations.filter((v) => v.severity === "info").length,
    });

    res.json(response);
  },
);

router.post(
  "/submission/package",
  async (req: Request, res: Response) => {
    const parsed = SubmissionPackageRequest.safeParse(req.body);
    if (!parsed.success) {
      res.status(400).json({ error: "Invalid request", details: parsed.error.issues });
      return;
    }

    const { projectId, includedModules, templateId } = parsed.data;

    let branding = undefined;
    if (projectId && isValidProjectId(projectId)) {
      branding = await getBranding(projectId);
      if (branding && Object.keys(branding).length === 0) {
        branding = undefined;
      }
    }

    let resolvedModules = includedModules ?? undefined;
    if (templateId && projectId && isValidProjectId(projectId)) {
      const { listTemplates } = await import("../lib/branding-store.js");
      const templates = await listTemplates(projectId);
      const tpl = templates.find((t) => t.id === templateId);
      if (tpl && tpl.includedModules.length > 0) {
        resolvedModules = tpl.includedModules;
      }
    }

    const result = await buildSubmissionPackage({
      projectDetails: parsed.data.projectDetails,
      moduleResults: parsed.data.moduleResults as ModuleResult[],
      includedModules: resolvedModules,
      branding,
    });

    const projectNum = parsed.data.projectDetails.projectNumber.replace(
      /[^a-zA-Z0-9-_]/g,
      "_",
    );
    const filename = `submission_${projectNum}_rev${parsed.data.projectDetails.revisionNumber}.zip`;

    res.setHeader("Content-Type", "application/zip");
    res.setHeader("Content-Disposition", `attachment; filename="${filename}"`);
    res.setHeader("X-Compliance-Has-Errors", String(result.hasErrors));
    res.setHeader("X-Compliance-Violation-Count", String(result.violations.length));

    result.zipStream.pipe(res);
  },
);

export default router;
