"use client";

import { Check, X, Minus } from "lucide-react";

interface ComparisonFeature {
  name: string;
  anvils: string | boolean;
  competitors: Record<string, string | boolean>;
}

interface ComparisonTableProps {
  features: ComparisonFeature[];
  competitorNames?: string[];
}

function CellValue({ value }: { value: string | boolean }) {
  if (value === true)
    return <Check className="w-5 h-5 text-emerald-500 mx-auto" />;
  if (value === false)
    return <X className="w-5 h-5 text-red-400 mx-auto" />;
  if (value === "partial")
    return <Minus className="w-5 h-5 text-amber-400 mx-auto" />;
  return (
    <span className="text-sm text-[var(--color-text-secondary)]">{value}</span>
  );
}

export default function ComparisonTable({
  features,
  competitorNames,
}: ComparisonTableProps) {
  const cols =
    competitorNames ||
    (features.length > 0 ? Object.keys(features[0].competitors) : []);

  return (
    <div className="overflow-x-auto rounded-xl border border-[var(--color-border)]">
      <table className="w-full text-left">
        <thead>
          <tr className="border-b border-[var(--color-border)] bg-[var(--color-bg-secondary)]">
            <th className="px-4 py-3 text-sm font-semibold text-[var(--color-text-primary)] min-w-[180px]">
              Feature
            </th>
            <th className="px-4 py-3 text-sm font-bold text-center text-purple-600 min-w-[130px] bg-purple-50/50">
              Anvils
            </th>
            {cols.map((col) => (
              <th
                key={col}
                className="px-4 py-3 text-sm font-semibold text-center text-[var(--color-text-muted)] min-w-[130px]"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {features.map((f, i) => (
            <tr
              key={i}
              className={`border-b border-[var(--color-border)] last:border-b-0 ${
                i % 2 === 0 ? "" : "bg-[var(--color-bg-secondary)]/50"
              }`}
            >
              <td className="px-4 py-3 text-sm font-medium text-[var(--color-text-primary)]">
                {f.name}
              </td>
              <td className="px-4 py-3 text-center bg-purple-50/30">
                <CellValue value={f.anvils} />
              </td>
              {cols.map((col) => (
                <td key={col} className="px-4 py-3 text-center">
                  <CellValue value={f.competitors[col]} />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
