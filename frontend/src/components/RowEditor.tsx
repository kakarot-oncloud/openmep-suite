import { Plus, Trash2 } from "lucide-react";

import { Button, Input, Select } from "./ui.tsx";

export interface Column {
  name: string;
  label: string;
  type: "number" | "text" | "select";
  step?: number;
  options?: { value: string | number; label: string }[];
}

type Row = Record<string, string | number>;

export default function RowEditor({
  columns,
  rows,
  onChange,
  addLabel,
  blank,
}: {
  columns: Column[];
  rows: Row[];
  onChange: (rows: Row[]) => void;
  addLabel: string;
  blank: Row;
}) {
  const setCell = (i: number, name: string, v: string | number) => {
    const next = rows.map((r, idx) => (idx === i ? { ...r, [name]: v } : r));
    onChange(next);
  };
  const coerce = (col: Column, raw: string): string | number =>
    col.type === "number" ? (raw === "" ? 0 : Number(raw)) : raw;

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-muted">
              {columns.map((c) => (
                <th key={c.name} className="px-1.5 pb-2 font-medium">{c.label}</th>
              ))}
              <th className="pb-2" />
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i}>
                {columns.map((c) => (
                  <td key={c.name} className="px-1 py-1 align-top">
                    {c.type === "select" ? (
                      <Select value={String(row[c.name])} onChange={(e) => setCell(i, c.name, coerce(c, e.target.value))}>
                        {c.options?.map((o) => (
                          <option key={String(o.value)} value={String(o.value)}>{o.label}</option>
                        ))}
                      </Select>
                    ) : (
                      <Input
                        type={c.type === "number" ? "number" : "text"}
                        step={c.step}
                        value={row[c.name]}
                        onChange={(e) => setCell(i, c.name, coerce(c, e.target.value))}
                      />
                    )}
                  </td>
                ))}
                <td className="px-1 py-1">
                  <button
                    onClick={() => onChange(rows.filter((_, idx) => idx !== i))}
                    aria-label="Remove row"
                    className="grid h-9 w-9 place-items-center rounded-lg text-muted hover:bg-surface-2 hover:text-danger"
                  >
                    <Trash2 size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Button variant="outline" size="sm" className="mt-3" onClick={() => onChange([...rows, { ...blank }])}>
        <Plus size={16} /> {addLabel}
      </Button>
    </div>
  );
}
