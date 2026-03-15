"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { apiCall } from "@/lib/api";
import Footer from "@/components/footer";

interface EntitySummary {
  entity_type: string;
  name: string;
  governing_law: string;
  liability: string;
  min_members: number | string;
  max_members: number | string;
  can_raise_equity: boolean;
  mandatory_audit: boolean;
  compliance_level: string;
  typical_cost: string;
  time_to_incorporate: string;
  ideal_for: string;
  separate_entity: boolean;
}

interface ComparisonData {
  entity_types: string[];
  entities: Record<string, EntityDetail>;
  comparison_rows: ComparisonRow[];
  total_compared: number;
}

interface EntityDetail {
  name: string;
  governing_law: string;
  min_members: number | string;
  max_members: number | string;
  min_directors: number | string;
  max_directors: number | string;
  liability: string;
  separate_entity: boolean;
  perpetual_succession: boolean;
  can_raise_equity: boolean;
  mandatory_audit: boolean;
  transferability_of_shares: string;
  foreign_ownership_allowed: boolean;
  annual_filings: string[];
  compliance_level: string;
  typical_cost: string;
  time_to_incorporate: string;
  tax_rate: string;
  minimum_capital: string;
  ideal_for: string;
  advantages: string[];
  disadvantages: string[];
}

interface ComparisonRow {
  field: string;
  label: string;
  values: Record<string, any>;
}

const ALL_ENTITY_TYPES = [
  { key: "private_limited", label: "Private Limited", emoji: "🏢" },
  { key: "opc", label: "OPC", emoji: "👤" },
  { key: "llp", label: "LLP", emoji: "🤝" },
  { key: "section_8", label: "Section 8", emoji: "💚" },
  { key: "sole_proprietorship", label: "Sole Prop", emoji: "🧑‍💼" },
  { key: "partnership", label: "Partnership", emoji: "👥" },
  { key: "public_limited", label: "Public Ltd", emoji: "🏛️" },
];

const DISPLAY_ROWS = [
  { field: "min_members", label: "Min Members" },
  { field: "max_members", label: "Max Members" },
  { field: "min_directors", label: "Min Directors" },
  { field: "liability", label: "Liability" },
  { field: "separate_entity", label: "Separate Entity" },
  { field: "perpetual_succession", label: "Perpetual Succession" },
  { field: "can_raise_equity", label: "Can Raise Funding" },
  { field: "mandatory_audit", label: "Mandatory Audit" },
  { field: "foreign_ownership_allowed", label: "Foreign Ownership" },
  { field: "compliance_level", label: "Compliance Level" },
  { field: "annual_filings", label: "Annual Filings" },
  { field: "typical_cost", label: "Typical Cost" },
  { field: "time_to_incorporate", label: "Time to Incorporate" },
  { field: "tax_rate", label: "Tax Rate" },
  { field: "minimum_capital", label: "Minimum Capital" },
  { field: "ideal_for", label: "Ideal For" },
];

function getCellColor(field: string, value: any): string {
  // Green for advantages
  if (field === "liability" && value === "Limited") return "rgba(16, 185, 129, 0.15)";
  if (field === "separate_entity" && value === true) return "rgba(16, 185, 129, 0.15)";
  if (field === "perpetual_succession" && value === true) return "rgba(16, 185, 129, 0.15)";
  if (field === "can_raise_equity" && value === true) return "rgba(16, 185, 129, 0.15)";
  if (field === "foreign_ownership_allowed" && value === true) return "rgba(16, 185, 129, 0.15)";
  if (field === "mandatory_audit" && value === false) return "rgba(16, 185, 129, 0.15)";
  if (field === "compliance_level" && (value === "Low" || value === "Very Low" || value === "Low-Medium")) return "rgba(16, 185, 129, 0.15)";

  // Red for disadvantages
  if (field === "liability" && value === "Unlimited" || field === "liability" && value === "Unlimited (joint and several)") return "rgba(244, 63, 94, 0.15)";
  if (field === "separate_entity" && value === false) return "rgba(244, 63, 94, 0.15)";
  if (field === "perpetual_succession" && value === false) return "rgba(244, 63, 94, 0.15)";
  if (field === "can_raise_equity" && value === false) return "rgba(244, 63, 94, 0.15)";
  if (field === "compliance_level" && (value === "Very High" || value === "High")) return "rgba(244, 63, 94, 0.15)";

  return "transparent";
}

function formatCellValue(field: string, value: any): string {
  if (value === true) return "Yes";
  if (value === false) return "No";
  if (Array.isArray(value)) return value.join(", ");
  if (value === null || value === undefined) return "N/A";
  return String(value);
}

export default function ComparePage() {
  const [selected, setSelected] = useState<string[]>(["private_limited", "llp", "opc"]);
  const [comparison, setComparison] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (selected.length >= 2) {
      fetchComparison();
    }
  }, [selected]);

  async function fetchComparison() {
    setLoading(true);
    try {
      const data = await apiCall(`/entities/compare?types=${selected.join(",")}`);
      setComparison(data);
    } catch {
      // Silently fail if backend not available
    }
    setLoading(false);
  }

  function toggleEntity(key: string) {
    setSelected((prev) => {
      if (prev.includes(key)) {
        if (prev.length <= 2) return prev; // Keep at least 2
        return prev.filter((k) => k !== key);
      }
      return [...prev, key];
    });
  }

  return (
    <div className="glow-bg min-h-screen">
      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-5 max-w-7xl mx-auto">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-2xl">&#x26A1;</span>
          <span className="text-xl font-bold" style={{ fontFamily: "var(--font-display)" }}>
            <span className="gradient-text">CMS</span>{" "}
            <span style={{ color: "var(--color-text-secondary)" }}>India</span>
          </span>
        </Link>
        <div className="flex gap-3">
          <Link href="/wizard" className="btn-secondary text-sm !py-2 !px-5">
            Entity Wizard
          </Link>
          <Link href="/pricing" className="btn-secondary text-sm !py-2 !px-5">
            Pricing
          </Link>
        </div>
      </nav>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="badge badge-purple mb-4 mx-auto w-fit">Compare Entity Types</div>
          <h1
            className="text-3xl md:text-4xl font-bold mb-3"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Side-by-Side <span className="gradient-text">Comparison</span>
          </h1>
          <p className="text-lg max-w-2xl mx-auto" style={{ color: "var(--color-text-secondary)" }}>
            Compare different business entity types to find the best fit for your needs.
            Select at least 2 entities to compare.
          </p>
        </div>

        {/* Entity Selection */}
        <div className="flex flex-wrap gap-3 justify-center mb-8">
          {ALL_ENTITY_TYPES.map((entity) => {
            const isSelected = selected.includes(entity.key);
            return (
              <button
                key={entity.key}
                onClick={() => toggleEntity(entity.key)}
                className="glass-card px-4 py-2.5 text-sm font-medium transition-all"
                style={{
                  borderColor: isSelected ? "rgba(139, 92, 246, 0.6)" : "var(--color-border)",
                  background: isSelected ? "rgba(139, 92, 246, 0.15)" : "transparent",
                }}
              >
                <span className="mr-2">{entity.emoji}</span>
                {entity.label}
                {isSelected && <span className="ml-2 text-xs">&#x2713;</span>}
              </button>
            );
          })}
        </div>

        {/* Comparison Table */}
        {comparison && comparison.entities && (
          <div className="glass-card overflow-hidden" style={{ cursor: "default" }}>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                    <th
                      className="text-left p-4 font-semibold sticky left-0"
                      style={{
                        background: "var(--color-bg-card)",
                        color: "var(--color-text-muted)",
                        minWidth: "160px",
                      }}
                    >
                      Feature
                    </th>
                    {comparison.entity_types.map((et) => (
                      <th
                        key={et}
                        className="text-center p-4 font-semibold"
                        style={{
                          minWidth: "150px",
                          color: "var(--color-text-primary)",
                        }}
                      >
                        <div className="text-base mb-1">
                          {ALL_ENTITY_TYPES.find((e) => e.key === et)?.emoji}
                        </div>
                        {comparison.entities[et]?.name || et}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {DISPLAY_ROWS.map((row, idx) => (
                    <tr
                      key={row.field}
                      style={{
                        borderBottom: "1px solid var(--color-border)",
                        background: idx % 2 === 0 ? "transparent" : "var(--color-stripe-alt)",
                      }}
                    >
                      <td
                        className="p-4 font-medium sticky left-0"
                        style={{
                          background: idx % 2 === 0 ? "var(--color-bg-card)" : "var(--color-bg-card)",
                          color: "var(--color-text-secondary)",
                        }}
                      >
                        {row.label}
                      </td>
                      {comparison.entity_types.map((et) => {
                        const entity = comparison.entities[et];
                        const value = entity ? (entity as any)[row.field] : "N/A";
                        const bgColor = getCellColor(row.field, value);
                        return (
                          <td
                            key={et}
                            className="p-4 text-center"
                            style={{ background: bgColor }}
                          >
                            {formatCellValue(row.field, value)}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div className="text-center py-12" style={{ color: "var(--color-text-muted)" }}>
            Loading comparison data...
          </div>
        )}

        {/* CTA Buttons */}
        {comparison && comparison.entities && (
          <div className="mt-8">
            <h3
              className="text-center text-sm font-semibold mb-4"
              style={{ color: "var(--color-text-muted)" }}
            >
              READY TO START? CHOOSE YOUR ENTITY TYPE
            </h3>
            <div className="flex flex-wrap gap-4 justify-center">
              {comparison.entity_types.map((et) => (
                <Link
                  key={et}
                  href={`/pricing?entity=${et}`}
                  className="btn-primary text-sm !py-2.5 !px-6"
                >
                  Register {comparison.entities[et]?.name || et} &rarr;
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Advantages / Disadvantages Section */}
        {comparison && comparison.entities && (
          <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {comparison.entity_types.map((et) => {
              const entity = comparison.entities[et];
              if (!entity) return null;
              return (
                <div key={et} className="glass-card p-6" style={{ cursor: "default" }}>
                  <h3 className="font-bold text-lg mb-1">{entity.name}</h3>
                  <p className="text-xs mb-4" style={{ color: "var(--color-text-muted)" }}>
                    {entity.governing_law}
                  </p>

                  <div className="mb-4">
                    <div
                      className="text-xs font-semibold mb-2"
                      style={{ color: "var(--color-accent-emerald-light)" }}
                    >
                      Advantages
                    </div>
                    <ul className="space-y-1">
                      {entity.advantages?.map((adv: string, i: number) => (
                        <li
                          key={i}
                          className="text-xs flex gap-2"
                          style={{ color: "var(--color-text-secondary)" }}
                        >
                          <span style={{ color: "var(--color-accent-emerald)" }}>+</span>{" "}
                          {adv}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="mb-4">
                    <div
                      className="text-xs font-semibold mb-2"
                      style={{ color: "var(--color-accent-amber)" }}
                    >
                      Disadvantages
                    </div>
                    <ul className="space-y-1">
                      {entity.disadvantages?.map((dis: string, i: number) => (
                        <li
                          key={i}
                          className="text-xs flex gap-2"
                          style={{ color: "var(--color-text-secondary)" }}
                        >
                          <span style={{ color: "var(--color-accent-amber)" }}>-</span>{" "}
                          {dis}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <Link
                    href={`/pricing?entity=${et}`}
                    className="btn-primary w-full text-center justify-center text-sm mt-2"
                  >
                    Start Registration &rarr;
                  </Link>
                </div>
              );
            })}
          </div>
        )}

        {/* Legend */}
        <div className="mt-8 text-center">
          <div className="inline-flex gap-6 text-xs" style={{ color: "var(--color-text-muted)" }}>
            <span className="flex items-center gap-2">
              <span
                className="inline-block w-3 h-3 rounded"
                style={{ background: "rgba(16, 185, 129, 0.3)" }}
              />
              Advantage
            </span>
            <span className="flex items-center gap-2">
              <span
                className="inline-block w-3 h-3 rounded"
                style={{ background: "rgba(244, 63, 94, 0.3)" }}
              />
              Disadvantage
            </span>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}
