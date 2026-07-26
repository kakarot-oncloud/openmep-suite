import { ArrowUpRight } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { Badge, Card } from "../components/ui.tsx";
import { DISCIPLINE_META, DISCIPLINES, MODULES } from "../data/modules.ts";

export default function Modules() {
  const [filter, setFilter] = useState<string>("All");
  const shown = filter === "All" ? MODULES : MODULES.filter((m) => m.discipline === filter);

  return (
    <div className="container-page py-14">
      <header className="mb-8 max-w-2xl">
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Calculation modules</h1>
        <p className="mt-3 text-muted">
          26 standards-cited calculators across five disciplines. Live modules open in this app; the rest are
          available today in the OpenMEP API and being ported to the web UI.
        </p>
      </header>

      <div className="mb-6 flex flex-wrap gap-2">
        {["All", ...DISCIPLINES].map((d) => (
          <button
            key={d}
            onClick={() => setFilter(d)}
            className={`rounded-full px-4 py-1.5 text-sm font-medium transition ${
              filter === d ? "bg-brand text-brand-fg" : "border border-border bg-surface text-muted hover:text-fg"
            }`}
          >
            {d === "All" ? "All" : `${DISCIPLINE_META[d].icon} ${d}`}
          </button>
        ))}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {shown.map((m) => {
          const live = Boolean(m.path);
          const inner = (
            <Card
              className={`flex h-full flex-col p-5 transition ${
                live ? "hover:-translate-y-0.5 hover:shadow-glow cursor-pointer" : "opacity-80"
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <span className="text-2xl">{DISCIPLINE_META[m.discipline].icon}</span>
                {live ? (
                  <Badge tone="success">Live <ArrowUpRight size={12} /></Badge>
                ) : (
                  <Badge>API</Badge>
                )}
              </div>
              <h3 className="mt-3 font-bold">{m.name}</h3>
              <p className="mt-1 text-sm text-muted">{m.standard}</p>
              <div className="mt-auto pt-3 text-xs text-muted">{m.discipline}</div>
            </Card>
          );
          return live ? (
            <Link key={m.id} to={m.path!}>
              {inner}
            </Link>
          ) : (
            <div key={m.id}>{inner}</div>
          );
        })}
      </div>
    </div>
  );
}
