import { forwardRef } from "react";

type Div = React.HTMLAttributes<HTMLDivElement>;

function cx(...parts: (string | false | undefined)[]) {
  return parts.filter(Boolean).join(" ");
}

export function Card({ className, ...props }: Div) {
  return (
    <div
      className={cx(
        "rounded-2xl border border-border bg-surface shadow-card",
        className,
      )}
      {...props}
    />
  );
}

export function Badge({
  children,
  tone = "muted",
  className,
}: {
  children: React.ReactNode;
  tone?: "muted" | "brand" | "success" | "danger" | "warn";
  className?: string;
}) {
  const tones: Record<string, string> = {
    muted: "bg-surface-2 text-muted",
    brand: "bg-brand/10 text-brand",
    success: "bg-success/15 text-success",
    danger: "bg-danger/15 text-danger",
    warn: "bg-warn/15 text-warn",
  };
  return (
    <span
      className={cx(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium",
        tones[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost" | "outline";
  size?: "sm" | "md" | "lg";
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { variant = "primary", size = "md", className, ...props },
  ref,
) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition-all duration-150 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand/50 disabled:opacity-60 disabled:cursor-not-allowed";
  const variants: Record<string, string> = {
    primary: "bg-brand text-brand-fg hover:brightness-110 active:brightness-95 shadow-sm",
    outline: "border border-border bg-surface hover:bg-surface-2 text-fg",
    ghost: "hover:bg-surface-2 text-fg",
  };
  const sizes: Record<string, string> = {
    sm: "h-9 px-3 text-sm",
    md: "h-11 px-5 text-sm",
    lg: "h-12 px-7 text-base",
  };
  return <button ref={ref} className={cx(base, variants[variant], sizes[size], className)} {...props} />;
});

export function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-sm font-medium text-fg">{label}</span>
      {children}
      {hint && <span className="text-xs text-muted">{hint}</span>}
    </label>
  );
}

const inputCls =
  "h-11 w-full rounded-xl border border-border bg-surface px-3.5 text-sm text-fg outline-none transition focus:border-brand focus:ring-2 focus:ring-brand/30 placeholder:text-muted/70";

export const Input = forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  function Input({ className, ...props }, ref) {
    return <input ref={ref} className={cx(inputCls, className)} {...props} />;
  },
);

export const Select = forwardRef<HTMLSelectElement, React.SelectHTMLAttributes<HTMLSelectElement>>(
  function Select({ className, children, ...props }, ref) {
    return (
      <select ref={ref} className={cx(inputCls, "appearance-none cursor-pointer", className)} {...props}>
        {children}
      </select>
    );
  },
);

export function Stat({ label, value, unit }: { label: string; value: React.ReactNode; unit?: string }) {
  return (
    <div className="rounded-xl border border-border bg-surface-2 p-4">
      <div className="text-xs uppercase tracking-wide text-muted">{label}</div>
      <div className="mt-1 text-2xl font-bold text-fg">
        {value}
        {unit && <span className="ml-1 text-base font-medium text-muted">{unit}</span>}
      </div>
    </div>
  );
}

export function Spinner({ className }: { className?: string }) {
  return (
    <span
      className={cx(
        "inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent",
        className,
      )}
    />
  );
}
