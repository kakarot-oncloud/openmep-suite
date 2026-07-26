import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="border-t border-border bg-surface/50">
      <div className="container-page flex flex-col gap-6 py-10 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand text-brand-fg font-black">M</span>
            <span className="text-base font-extrabold">
              Open<span className="text-brand">MEP</span>
            </span>
          </div>
          <p className="mt-2 max-w-sm text-sm text-muted">
            Open-source, standards-cited MEP engineering calculations for GCC, Europe, India and Australia.
          </p>
        </div>
        <div className="flex flex-wrap gap-x-8 gap-y-2 text-sm">
          <Link to="/modules" className="text-muted hover:text-fg">Modules</Link>
          <Link to="/calc/cable-sizing" className="text-muted hover:text-fg">Cable Sizing</Link>
          <a href="https://github.com/kakarot-oncloud/openmep-suite" className="text-muted hover:text-fg" target="_blank" rel="noreferrer">GitHub</a>
          <a href="https://github.com/kakarot-oncloud/openmep-suite/releases" className="text-muted hover:text-fg" target="_blank" rel="noreferrer">Releases</a>
        </div>
      </div>
      <div className="border-t border-border py-4">
        <p className="container-page text-center text-xs text-muted">
          © {new Date().getFullYear()} OpenMEP · MIT License · Not a substitute for professional engineering judgement.
        </p>
      </div>
    </footer>
  );
}
