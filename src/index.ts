/**
 * index.ts — OpenMEP Node.js Project Management API
 *
 * Serves all project-level platform features:
 *   /api/projects/**   — project CRUD, versioning, branding, report templates
 *   /api/submission/** — compliance checks, submission package ZIP generation
 *
 * Calculation endpoints (electrical, mechanical, plumbing, fire) are handled
 * by the Python FastAPI service on port 8000.
 */
import express from "express";
import projectsRouter from "./routes/projects.js";
import submissionRouter from "./routes/submission.js";

const app = express();
const PORT = parseInt(process.env["PORT"] ?? "8080", 10);

// ── Middleware ────────────────────────────────────────────────────────────────
app.use(express.json({ limit: "50mb" }));
app.use(express.urlencoded({ extended: true }));

// ── Health & Status ───────────────────────────────────────────────────────────
app.get("/", (_req, res) => {
  res.json({
    name: "OpenMEP Node.js API",
    version: "0.2.0",
    status: "operational",
    endpoints: {
      projects: "/api/projects",
      submission: "/api/submission/compliance-check",
      package: "/api/submission/package",
    },
    calculationEngine: "http://api:8000 (FastAPI/Python)",
  });
});

app.get("/health", (_req, res) => {
  res.json({ status: "healthy", service: "openmep-node-api", version: "0.2.0" });
});

// ── Routers ───────────────────────────────────────────────────────────────────
app.use("/api", projectsRouter);
app.use("/api", submissionRouter);

// ── 404 catch-all ─────────────────────────────────────────────────────────────
app.use((_req, res) => {
  res.status(404).json({
    status: "error",
    message: "Endpoint not found. See GET / for available routes.",
  });
});

// ── Start ─────────────────────────────────────────────────────────────────────
app.listen(PORT, "0.0.0.0", () => {
  process.stdout.write(`OpenMEP Node.js API listening on http://0.0.0.0:${PORT}\n`);
});
