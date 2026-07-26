import { Github, Menu, X } from "lucide-react";
import { useState } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";

import { Button } from "./ui.tsx";
import ThemeToggle from "./ThemeToggle.tsx";

const LINKS = [
  { to: "/", label: "Home" },
  { to: "/modules", label: "Modules" },
  { to: "/tools/cable-schedule", label: "Batch" },
  { to: "/tools/projects", label: "Projects" },
];

const REPO = "https://github.com/kakarot-oncloud/openmep-suite";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const loc = useLocation();

  return (
    <header className="sticky top-0 z-40 border-b border-border/70 bg-bg/80 backdrop-blur-xl">
      <nav className="container-page flex h-16 items-center justify-between gap-4">
        <Link to="/" className="flex items-center gap-2.5" onClick={() => setOpen(false)}>
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-brand text-brand-fg font-black">M</span>
          <span className="text-lg font-extrabold tracking-tight">
            Open<span className="text-brand">MEP</span>
          </span>
        </Link>

        <div className="hidden items-center gap-1 md:flex">
          {LINKS.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) =>
                `rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive ? "bg-surface-2 text-fg" : "text-muted hover:text-fg"
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <a
            href={REPO}
            target="_blank"
            rel="noreferrer"
            aria-label="GitHub repository"
            className="hidden h-10 w-10 place-items-center rounded-xl border border-border bg-surface text-fg transition hover:bg-surface-2 sm:grid"
          >
            <Github size={18} />
          </a>
          <ThemeToggle />
          <button
            className="grid h-10 w-10 place-items-center rounded-xl border border-border bg-surface md:hidden"
            aria-label="Toggle menu"
            onClick={() => setOpen((o) => !o)}
          >
            {open ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>
      </nav>

      {open && (
        <div className="border-t border-border bg-surface md:hidden">
          <div className="container-page flex flex-col py-2">
            {LINKS.map((l) => (
              <Link
                key={l.to}
                to={l.to}
                onClick={() => setOpen(false)}
                className={`rounded-lg px-3 py-3 text-sm font-medium ${
                  loc.pathname === l.to ? "bg-surface-2 text-fg" : "text-muted"
                }`}
              >
                {l.label}
              </Link>
            ))}
            <a href={REPO} target="_blank" rel="noreferrer" className="px-3 py-3">
              <Button variant="outline" size="sm" className="w-full">
                <Github size={16} /> GitHub
              </Button>
            </a>
          </div>
        </div>
      )}
    </header>
  );
}
