/**
 * branding-store.ts — in-memory company-branding and report-template store.
 *
 * Holds one BrandingConfig plus a list of ReportTemplates per project.
 * This is a simple, honest Map-based implementation: state lives in process
 * memory only and is not persisted to disk. It exists to satisfy the HTTP
 * contract used by routes/projects.ts and routes/submission.ts.
 */
import { randomUUID } from "node:crypto";

export interface BrandingConfig {
  companyName?: string;
  engineerName?: string;
  licenceNumber?: string;
  footerText?: string;
  primaryColor?: string;
  logoBase64?: string;
  letterheadBase64?: string;
  stampBase64?: string;
}

export type BrandingAssetField = "logoBase64" | "letterheadBase64" | "stampBase64";

export interface ReportTemplate {
  id: string;
  name: string;
  includedModules: string[];
  coverIntro?: string;
  createdAt: string;
  updatedAt: string;
}

export interface TemplateInput {
  name: string;
  includedModules?: string[];
  coverIntro?: string;
}

// projectId -> branding config
const brandingByProject = new Map<string, BrandingConfig>();
// projectId -> templates
const templatesByProject = new Map<string, ReportTemplate[]>();

export async function getBranding(projectId: string): Promise<BrandingConfig> {
  return { ...(brandingByProject.get(projectId) ?? {}) };
}

export async function saveBranding(
  projectId: string,
  partial: Partial<BrandingConfig>,
): Promise<BrandingConfig> {
  const current = brandingByProject.get(projectId) ?? {};
  const merged: BrandingConfig = { ...current };
  for (const [key, value] of Object.entries(partial)) {
    if (value === undefined || value === null) continue;
    (merged as Record<string, unknown>)[key] = value;
  }
  brandingByProject.set(projectId, merged);
  return { ...merged };
}

export async function deleteBrandingAsset(
  projectId: string,
  field: BrandingAssetField | string,
): Promise<BrandingConfig> {
  const current = brandingByProject.get(projectId) ?? {};
  const next: BrandingConfig = { ...current };
  delete (next as Record<string, unknown>)[field];
  brandingByProject.set(projectId, next);
  return { ...next };
}

export async function listTemplates(projectId: string): Promise<ReportTemplate[]> {
  return (templatesByProject.get(projectId) ?? []).map((t) => ({ ...t }));
}

export async function createTemplate(
  projectId: string,
  data: TemplateInput,
): Promise<ReportTemplate> {
  const now = new Date().toISOString();
  const template: ReportTemplate = {
    id: randomUUID(),
    name: data.name,
    includedModules: data.includedModules ?? [],
    coverIntro: data.coverIntro,
    createdAt: now,
    updatedAt: now,
  };
  const list = templatesByProject.get(projectId) ?? [];
  list.push(template);
  templatesByProject.set(projectId, list);
  return { ...template };
}

export async function updateTemplate(
  projectId: string,
  templateId: string,
  data: Partial<TemplateInput>,
): Promise<ReportTemplate | null> {
  const list = templatesByProject.get(projectId);
  if (!list) return null;
  const idx = list.findIndex((t) => t.id === templateId);
  if (idx === -1) return null;
  const existing = list[idx]!;
  const updated: ReportTemplate = {
    ...existing,
    name: data.name ?? existing.name,
    includedModules: data.includedModules ?? existing.includedModules,
    coverIntro: data.coverIntro ?? existing.coverIntro,
    updatedAt: new Date().toISOString(),
  };
  list[idx] = updated;
  return { ...updated };
}

export async function deleteTemplate(
  projectId: string,
  templateId: string,
): Promise<boolean> {
  const list = templatesByProject.get(projectId);
  if (!list) return false;
  const idx = list.findIndex((t) => t.id === templateId);
  if (idx === -1) return false;
  list.splice(idx, 1);
  return true;
}

/** Test-only helper to reset store state between tests. */
export function __resetBrandingStore(): void {
  brandingByProject.clear();
  templatesByProject.clear();
}
