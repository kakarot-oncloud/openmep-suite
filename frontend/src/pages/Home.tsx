import { ArrowRight, CheckCircle2, FileText, Globe2, ShieldCheck, Zap } from "lucide-react";
import { Link } from "react-router-dom";

import { Badge, Button, Card } from "../components/ui.tsx";
import { DISCIPLINE_META, DISCIPLINES } from "../data/modules.ts";
import { REGIONS } from "../lib/regions.ts";

const FEATURES = [
  {
    icon: Globe2,
    title: "Region-aware",
    body: "Design codes switch automatically — BS 7671 for GCC/UK, IS 3961 for India, AS/NZS 3008 for Australia. Three-level Region → Country → Authority selector.",
  },
  {
    icon: ShieldCheck,
    title: "Standard-cited",
    body: "Every result references the exact clause and table used. Full numerical tables are embedded in the engine — no black boxes, no external lookups.",
  },
  {
    icon: FileText,
    title: "Audit-ready",
    body: "One-click PDF and Excel outputs with letterhead, step-by-step workings and an engineer sign-off block. Batch a whole cable schedule at once.",
  },
];

export default function Home() {
  return (
    <div>
      {/* ── Hero ─────────────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 grid-bg opacity-60 [mask-image:radial-gradient(ellipse_at_top,black,transparent_70%)]" />
        <div className="pointer-events-none absolute left-1/2 top-[-10%] h-[420px] w-[820px] -translate-x-1/2 rounded-full bg-brand/20 blur-[120px]" />
        <div className="container-page relative py-20 sm:py-28 lg:py-32">
          <div className="mx-auto max-w-3xl text-center">
            <div className="animate-fade-up">
              <Badge tone="brand" className="mb-5">
                <span className="h-1.5 w-1.5 rounded-full bg-brand" /> v0.4 · Open source · MIT
              </Badge>
            </div>
            <h1 className="animate-fade-up text-4xl font-extrabold leading-[1.08] tracking-tight sm:text-5xl lg:text-6xl">
              MEP engineering calculations,
              <br className="hidden sm:block" /> <span className="text-gradient">done right.</span>
            </h1>
            <p className="animate-fade-up mx-auto mt-6 max-w-2xl text-lg text-muted">
              Size cables, calculate cooling loads, design pipe and fire systems — standards-compliant across
              GCC, Europe, India and Australia. Cited to the clause. Print-ready. Free.
            </p>
            <div className="animate-fade-up mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Link to="/calc/cable-sizing">
                <Button size="lg" className="w-full sm:w-auto">
                  Try Cable Sizing <ArrowRight size={18} />
                </Button>
              </Link>
              <Link to="/modules">
                <Button size="lg" variant="outline" className="w-full sm:w-auto">
                  Explore 26 modules
                </Button>
              </Link>
            </div>
            <div className="mt-8 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm text-muted">
              {["4 regions", "26 modules", "Standards-cited", "PDF & Excel export"].map((t) => (
                <span key={t} className="inline-flex items-center gap-1.5">
                  <CheckCircle2 size={15} className="text-success" /> {t}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── Features ─────────────────────────────────────────────────────── */}
      <section className="container-page pb-8">
        <div className="grid gap-5 md:grid-cols-3">
          {FEATURES.map((f) => (
            <Card key={f.title} className="p-6">
              <div className="grid h-11 w-11 place-items-center rounded-xl bg-brand/10 text-brand">
                <f.icon size={22} />
              </div>
              <h3 className="mt-4 text-lg font-bold">{f.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted">{f.body}</p>
            </Card>
          ))}
        </div>
      </section>

      {/* ── Disciplines ──────────────────────────────────────────────────── */}
      <section className="container-page py-16">
        <div className="mb-8 text-center">
          <h2 className="text-2xl font-bold sm:text-3xl">Every discipline, one engine</h2>
          <p className="mt-2 text-muted">26 calculation modules across the full MEP scope.</p>
        </div>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
          {DISCIPLINES.map((d) => (
            <Card key={d} className="flex flex-col items-center gap-2 p-6 text-center transition hover:-translate-y-0.5 hover:shadow-glow">
              <span className="text-3xl">{DISCIPLINE_META[d].icon}</span>
              <span className="font-semibold">{d}</span>
              <Badge>{DISCIPLINE_META[d].count} modules</Badge>
            </Card>
          ))}
        </div>
      </section>

      {/* ── Regions ──────────────────────────────────────────────────────── */}
      <section className="container-page pb-20">
        <Card className="overflow-hidden">
          <div className="grid gap-px bg-border sm:grid-cols-2 lg:grid-cols-4">
            {REGIONS.map((r) => (
              <div key={r.code} className="bg-surface p-6">
                <div className="text-3xl">{r.flag}</div>
                <div className="mt-3 font-bold">{r.short}</div>
                <div className="mt-1 text-sm text-muted">{r.standard}</div>
              </div>
            ))}
          </div>
        </Card>
      </section>

      {/* ── CTA ──────────────────────────────────────────────────────────── */}
      <section className="container-page pb-24">
        <div className="relative overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-brand/10 via-surface to-surface p-10 text-center sm:p-14">
          <Zap className="mx-auto mb-4 text-brand" size={32} />
          <h2 className="text-2xl font-bold sm:text-3xl">Start calculating in seconds</h2>
          <p className="mx-auto mt-3 max-w-xl text-muted">
            No sign-up. Runs against the open OpenMEP API. Self-host the whole stack on any VPS.
          </p>
          <div className="mt-7 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link to="/calc/cable-sizing">
              <Button size="lg">Open a calculator <ArrowRight size={18} /></Button>
            </Link>
            <a href="https://github.com/kakarot-oncloud/openmep-suite" target="_blank" rel="noreferrer">
              <Button size="lg" variant="outline">View on GitHub</Button>
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
