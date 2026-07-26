import { describe, it, expect, beforeEach } from "vitest";
import request from "supertest";
import app from "../index.js";
import { __resetProjectStore } from "../lib/project-store.js";
import { __resetVersionStore } from "../lib/version-store.js";
import { __resetBrandingStore } from "../lib/branding-store.js";

beforeEach(() => {
  __resetProjectStore();
  __resetVersionStore();
  __resetBrandingStore();
});

describe("health endpoints", () => {
  it("GET /health returns healthy", async () => {
    const res = await request(app).get("/health");
    expect(res.status).toBe(200);
    expect(res.body.status).toBe("healthy");
  });

  it("unknown routes return 404 JSON", async () => {
    const res = await request(app).get("/does-not-exist");
    expect(res.status).toBe(404);
    expect(res.body.status).toBe("error");
  });
});

describe("projects API", () => {
  it("rejects invalid project bodies", async () => {
    const res = await request(app).post("/api/projects").send({});
    expect(res.status).toBe(400);
    expect(res.body.error).toBe("validation_error");
  });

  it("creates and reads back a project, then lists versions", async () => {
    const create = await request(app)
      .post("/api/projects")
      .send({ name: "API Tower", region: "DEWA", totalFloors: 6 });
    expect(create.status).toBe(201);
    const id = create.body.id as string;

    const get = await request(app).get(`/api/projects/${id}`);
    expect(get.status).toBe(200);
    expect(get.body.name).toBe("API Tower");

    const versions = await request(app).get(`/api/projects/${id}/versions`);
    expect(versions.status).toBe(200);
    expect(versions.body.versions).toHaveLength(1);

    const refresh = await request(app).post(`/api/projects/${id}/refresh`);
    expect(refresh.status).toBe(200);
    expect(refresh.body.modules.length).toBeGreaterThan(0);
  });

  it("returns 400 for malformed project IDs", async () => {
    const res = await request(app).get("/api/projects/not-a-uuid");
    expect(res.status).toBe(400);
    expect(res.body.error).toBe("invalid_id");
  });
});

describe("submission API", () => {
  it("runs a compliance check and flags a voltage-drop error", async () => {
    const res = await request(app)
      .post("/api/submission/compliance-check")
      .send({
        moduleResults: [
          {
            module: "electrical",
            region: "DEWA",
            parameters: { voltage_drop_percent: 4.2 },
          },
        ],
      });
    expect(res.status).toBe(200);
    expect(res.body.hasErrors).toBe(true);
    expect(res.body.errorCount).toBeGreaterThanOrEqual(1);
  });

  it("builds a submission package ZIP with a sanitized filename", async () => {
    const res = await request(app)
      .post("/api/submission/package")
      .send({
        projectDetails: {
          projectName: "P",
          projectNumber: 'PRJ"001\r\nInjected',
          clientName: "Client",
          engineerName: "Eng",
          companyName: "Co",
          submissionDate: "2026-01-01",
          revisionNumber: "A",
        },
        moduleResults: [
          {
            module: "electrical",
            region: "DEWA",
            parameters: { voltage_drop_percent: 1.0 },
          },
        ],
      })
      .buffer(true)
      .parse((res2, cb) => {
        const chunks: Buffer[] = [];
        res2.on("data", (c: Buffer) => chunks.push(c));
        res2.on("end", () => cb(null, Buffer.concat(chunks)));
      });

    expect(res.status).toBe(200);
    expect(res.headers["content-type"]).toBe("application/zip");
    const disposition = res.headers["content-disposition"] as string;
    expect(disposition).not.toContain("\n");
    expect(disposition).not.toContain("\r");
    // ZIP files start with the "PK" local-file-header magic bytes.
    expect((res.body as Buffer).slice(0, 2).toString()).toBe("PK");
  });
});
