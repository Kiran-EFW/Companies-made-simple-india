"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import {
  getCaCompanies,
  getCaTaxOverview,
  getCaGstDashboard,
  markFilingComplete,
} from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Company {
  id: number;
  name: string;
  entity_type: string;
}

interface TdsQuarter {
  quarter: string;
  status: string;
  due_date: string;
  return_type?: string;
}

interface AdvanceTaxInstallment {
  quarter: string;
  due_date: string;
  cumulative_percent: number;
  status: string;
}

interface TaxOverview {
  itr: {
    status: string;
    due_date: string;
    filing_reference?: string;
    assessment_year?: string;
  };
  tds_quarterly: TdsQuarter[];
  advance_tax: AdvanceTaxInstallment[];
  penalty_exposure: number;
}

interface GstReturn {
  return_type: string;
  period: string;
  due_date: string;
  status: string;
  filing_reference?: string;
}

interface GstDashboard {
  gstr1: GstReturn[];
  gstr3b: GstReturn[];
  gstr9?: GstReturn;
  gstin?: string;
}

// ---------------------------------------------------------------------------
// Theme
// ---------------------------------------------------------------------------
const T = {
  accent: "#0d9488",
  accentLight: "#14b8a6",
  accentBg: "rgba(20, 184, 166, 0.08)",
  textPrimary: "#0f172a",
  textSecondary: "#475569",
  textMuted: "#94a3b8",
  cardBg: "#ffffff",
  cardBorder: "#e2e8f0",
  pageBg: "#f8fafc",
  rose: "#dc2626",
  roseBg: "rgba(220, 38, 38, 0.06)",
  amber: "#d97706",
  amberBg: "rgba(217, 119, 6, 0.06)",
  emerald: "#059669",
  emeraldBg: "rgba(5, 150, 105, 0.06)",
  blue: "#2563eb",
  blueBg: "rgba(37, 99, 235, 0.06)",
};

function statusStyle(status: string) {
  switch (status) {
    case "overdue":
      return { bg: T.roseBg, color: T.rose };
    case "due_soon":
      return { bg: T.amberBg, color: T.amber };
    case "upcoming":
      return { bg: T.blueBg, color: T.blue };
    case "completed":
    case "filed":
      return { bg: T.emeraldBg, color: T.emerald };
    default:
      return { bg: T.accentBg, color: T.accent };
  }
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function formatCurrency(amount: number) {
  if (amount === 0) return "None";
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CaTaxPage() {
  const { user, loading: authLoading } = useAuth();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<number | null>(null);
  const [taxData, setTaxData] = useState<TaxOverview | null>(null);
  const [gstData, setGstData] = useState<GstDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [dataLoading, setDataLoading] = useState(false);

  // Load companies
  useEffect(() => {
    if (authLoading || !user) return;

    (async () => {
      try {
        const data = await getCaCompanies();
        const list = Array.isArray(data) ? data : data.companies || [];
        setCompanies(list);
        if (list.length > 0) {
          setSelectedCompany(list[0].id);
        }
      } catch (err) {
        console.error("Failed to load companies:", err);
      } finally {
        setLoading(false);
      }
    })();
  }, [user, authLoading]);

  // Load tax data when company changes
  useEffect(() => {
    if (!selectedCompany) return;

    setDataLoading(true);
    (async () => {
      try {
        const [tax, gst] = await Promise.all([
          getCaTaxOverview(selectedCompany).catch(() => null),
          getCaGstDashboard(selectedCompany).catch(() => null),
        ]);
        setTaxData(tax);
        setGstData(gst);
      } catch (err) {
        console.error("Failed to load tax data:", err);
      } finally {
        setDataLoading(false);
      }
    })();
  }, [selectedCompany]);

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <div
          className="animate-spin rounded-full h-8 w-8 border-b-2"
          style={{ borderColor: T.accent }}
        />
      </div>
    );
  }

  const advanceTaxLabels: Record<string, string> = {
    Q1: "15%",
    Q2: "45%",
    Q3: "75%",
    Q4: "100%",
  };

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 lg:py-10">
      {/* Header */}
      <div className="mb-6">
        <h1
          className="text-2xl font-bold mb-1"
          style={{
            fontFamily: "var(--font-display)",
            color: T.textPrimary,
          }}
        >
          Tax Filing Tracker
        </h1>
        <p className="text-sm" style={{ color: T.textSecondary }}>
          Track ITR, TDS, advance tax installments, and GST return status across
          companies.
        </p>
      </div>

      {/* Company Selector */}
      <div className="mb-6">
        <label
          className="block text-xs font-medium mb-1.5"
          style={{ color: T.textMuted }}
        >
          Select Company
        </label>
        <select
          value={selectedCompany || ""}
          onChange={(e) => setSelectedCompany(Number(e.target.value))}
          className="px-3 py-2.5 rounded-lg text-sm w-full max-w-sm"
          style={{
            background: T.cardBg,
            border: `1px solid ${T.cardBorder}`,
            color: T.textPrimary,
            outline: "none",
          }}
        >
          {companies.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>

      {dataLoading ? (
        <div className="flex items-center justify-center py-20">
          <div
            className="animate-spin rounded-full h-6 w-6 border-b-2"
            style={{ borderColor: T.accent }}
          />
        </div>
      ) : !taxData ? (
        <div
          className="rounded-xl p-8 text-center text-sm"
          style={{
            background: T.cardBg,
            border: `1px solid ${T.cardBorder}`,
            color: T.textMuted,
          }}
        >
          No tax data available for this company.
        </div>
      ) : (
        <div className="space-y-6">
          {/* ITR Filing Status */}
          <div
            className="rounded-xl p-5"
            style={{
              background: T.cardBg,
              border: `1px solid ${T.cardBorder}`,
            }}
          >
            <h2
              className="text-sm font-semibold mb-4"
              style={{ color: T.textPrimary }}
            >
              ITR Filing Status
            </h2>
            <div className="flex flex-wrap items-center gap-4">
              {(() => {
                const s = statusStyle(taxData.itr?.status || "upcoming");
                return (
                  <span
                    className="inline-flex text-xs font-semibold px-2.5 py-1 rounded-full capitalize"
                    style={{ background: s.bg, color: s.color }}
                  >
                    {(taxData.itr?.status || "upcoming").replace(/_/g, " ")}
                  </span>
                );
              })()}
              {taxData.itr?.assessment_year && (
                <span
                  className="text-xs"
                  style={{ color: T.textSecondary }}
                >
                  AY {taxData.itr.assessment_year}
                </span>
              )}
              {taxData.itr?.due_date && (
                <span
                  className="text-xs"
                  style={{ color: T.textSecondary }}
                >
                  Due: {formatDate(taxData.itr.due_date)}
                </span>
              )}
              {taxData.itr?.filing_reference && (
                <span
                  className="text-xs font-mono"
                  style={{ color: T.textMuted }}
                >
                  Ref: {taxData.itr.filing_reference}
                </span>
              )}
            </div>
          </div>

          {/* TDS Quarterly Returns */}
          {taxData.tds_quarterly && taxData.tds_quarterly.length > 0 && (
            <div
              className="rounded-xl overflow-hidden"
              style={{
                background: T.cardBg,
                border: `1px solid ${T.cardBorder}`,
              }}
            >
              <div className="px-5 pt-5 pb-3">
                <h2
                  className="text-sm font-semibold"
                  style={{ color: T.textPrimary }}
                >
                  TDS Quarterly Returns
                </h2>
              </div>
              <div
                className="grid grid-cols-[1fr_100px_100px_90px] gap-3 px-5 py-2.5 text-xs font-semibold uppercase tracking-wider"
                style={{
                  color: T.textMuted,
                  borderBottom: `1px solid ${T.cardBorder}`,
                  background: T.pageBg,
                }}
              >
                <div>Quarter</div>
                <div>Due Date</div>
                <div>Status</div>
                <div>Return</div>
              </div>
              {taxData.tds_quarterly.map((q, idx) => {
                const s = statusStyle(q.status);
                return (
                  <div
                    key={q.quarter}
                    className="grid grid-cols-[1fr_100px_100px_90px] gap-3 px-5 py-3 items-center text-sm"
                    style={{
                      borderBottom:
                        idx < taxData.tds_quarterly.length - 1
                          ? `1px solid ${T.cardBorder}`
                          : undefined,
                    }}
                  >
                    <div
                      className="font-medium"
                      style={{ color: T.textPrimary }}
                    >
                      {q.quarter}
                    </div>
                    <div
                      className="text-xs"
                      style={{ color: T.textSecondary }}
                    >
                      {formatDate(q.due_date)}
                    </div>
                    <div>
                      <span
                        className="inline-flex text-[11px] font-semibold px-2 py-0.5 rounded-full capitalize"
                        style={{ background: s.bg, color: s.color }}
                      >
                        {q.status.replace(/_/g, " ")}
                      </span>
                    </div>
                    <div
                      className="text-xs"
                      style={{ color: T.textMuted }}
                    >
                      {q.return_type || "26Q"}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Advance Tax Installments */}
          {taxData.advance_tax && taxData.advance_tax.length > 0 && (
            <div
              className="rounded-xl overflow-hidden"
              style={{
                background: T.cardBg,
                border: `1px solid ${T.cardBorder}`,
              }}
            >
              <div className="px-5 pt-5 pb-3">
                <h2
                  className="text-sm font-semibold"
                  style={{ color: T.textPrimary }}
                >
                  Advance Tax Installments
                </h2>
              </div>
              <div
                className="grid grid-cols-[1fr_100px_100px_100px] gap-3 px-5 py-2.5 text-xs font-semibold uppercase tracking-wider"
                style={{
                  color: T.textMuted,
                  borderBottom: `1px solid ${T.cardBorder}`,
                  background: T.pageBg,
                }}
              >
                <div>Quarter</div>
                <div>Due Date</div>
                <div>Cumulative</div>
                <div>Status</div>
              </div>
              {taxData.advance_tax.map((inst, idx) => {
                const s = statusStyle(inst.status);
                return (
                  <div
                    key={inst.quarter}
                    className="grid grid-cols-[1fr_100px_100px_100px] gap-3 px-5 py-3 items-center text-sm"
                    style={{
                      borderBottom:
                        idx < taxData.advance_tax.length - 1
                          ? `1px solid ${T.cardBorder}`
                          : undefined,
                    }}
                  >
                    <div
                      className="font-medium"
                      style={{ color: T.textPrimary }}
                    >
                      {inst.quarter}
                    </div>
                    <div
                      className="text-xs"
                      style={{ color: T.textSecondary }}
                    >
                      {formatDate(inst.due_date)}
                    </div>
                    <div className="text-xs font-semibold" style={{ color: T.accent }}>
                      {advanceTaxLabels[inst.quarter] ||
                        `${inst.cumulative_percent}%`}
                    </div>
                    <div>
                      <span
                        className="inline-flex text-[11px] font-semibold px-2 py-0.5 rounded-full capitalize"
                        style={{ background: s.bg, color: s.color }}
                      >
                        {inst.status.replace(/_/g, " ")}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* GST Returns */}
          {gstData && (
            <div
              className="rounded-xl overflow-hidden"
              style={{
                background: T.cardBg,
                border: `1px solid ${T.cardBorder}`,
              }}
            >
              <div className="px-5 pt-5 pb-3 flex items-center justify-between">
                <h2
                  className="text-sm font-semibold"
                  style={{ color: T.textPrimary }}
                >
                  GST Returns
                </h2>
                {gstData.gstin && (
                  <span
                    className="text-xs font-mono"
                    style={{ color: T.textMuted }}
                  >
                    GSTIN: {gstData.gstin}
                  </span>
                )}
              </div>

              {/* GSTR-1 */}
              {gstData.gstr1 && gstData.gstr1.length > 0 && (
                <>
                  <div
                    className="px-5 py-2 text-xs font-semibold uppercase tracking-wider"
                    style={{
                      color: T.accent,
                      background: T.accentBg,
                      borderTop: `1px solid ${T.cardBorder}`,
                    }}
                  >
                    GSTR-1 (Outward Supplies)
                  </div>
                  {gstData.gstr1.map((r, idx) => {
                    const s = statusStyle(r.status);
                    return (
                      <div
                        key={`gstr1-${idx}`}
                        className="grid grid-cols-[1fr_100px_100px] gap-3 px-5 py-2.5 items-center text-sm"
                        style={{
                          borderBottom: `1px solid ${T.cardBorder}`,
                        }}
                      >
                        <div
                          className="text-xs"
                          style={{ color: T.textPrimary }}
                        >
                          {r.period}
                        </div>
                        <div
                          className="text-xs"
                          style={{ color: T.textSecondary }}
                        >
                          {formatDate(r.due_date)}
                        </div>
                        <div>
                          <span
                            className="inline-flex text-[11px] font-semibold px-2 py-0.5 rounded-full capitalize"
                            style={{ background: s.bg, color: s.color }}
                          >
                            {r.status.replace(/_/g, " ")}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </>
              )}

              {/* GSTR-3B */}
              {gstData.gstr3b && gstData.gstr3b.length > 0 && (
                <>
                  <div
                    className="px-5 py-2 text-xs font-semibold uppercase tracking-wider"
                    style={{
                      color: T.accent,
                      background: T.accentBg,
                      borderTop: `1px solid ${T.cardBorder}`,
                    }}
                  >
                    GSTR-3B (Summary Return)
                  </div>
                  {gstData.gstr3b.map((r, idx) => {
                    const s = statusStyle(r.status);
                    return (
                      <div
                        key={`gstr3b-${idx}`}
                        className="grid grid-cols-[1fr_100px_100px] gap-3 px-5 py-2.5 items-center text-sm"
                        style={{
                          borderBottom: `1px solid ${T.cardBorder}`,
                        }}
                      >
                        <div
                          className="text-xs"
                          style={{ color: T.textPrimary }}
                        >
                          {r.period}
                        </div>
                        <div
                          className="text-xs"
                          style={{ color: T.textSecondary }}
                        >
                          {formatDate(r.due_date)}
                        </div>
                        <div>
                          <span
                            className="inline-flex text-[11px] font-semibold px-2 py-0.5 rounded-full capitalize"
                            style={{ background: s.bg, color: s.color }}
                          >
                            {r.status.replace(/_/g, " ")}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </>
              )}

              {/* GSTR-9 Annual */}
              {gstData.gstr9 && (
                <>
                  <div
                    className="px-5 py-2 text-xs font-semibold uppercase tracking-wider"
                    style={{
                      color: T.accent,
                      background: T.accentBg,
                      borderTop: `1px solid ${T.cardBorder}`,
                    }}
                  >
                    GSTR-9 (Annual Return)
                  </div>
                  <div
                    className="grid grid-cols-[1fr_100px_100px] gap-3 px-5 py-2.5 items-center text-sm"
                    style={{ borderBottom: `1px solid ${T.cardBorder}` }}
                  >
                    <div
                      className="text-xs"
                      style={{ color: T.textPrimary }}
                    >
                      {gstData.gstr9.period}
                    </div>
                    <div
                      className="text-xs"
                      style={{ color: T.textSecondary }}
                    >
                      {formatDate(gstData.gstr9.due_date)}
                    </div>
                    <div>
                      {(() => {
                        const s = statusStyle(gstData.gstr9!.status);
                        return (
                          <span
                            className="inline-flex text-[11px] font-semibold px-2 py-0.5 rounded-full capitalize"
                            style={{ background: s.bg, color: s.color }}
                          >
                            {gstData.gstr9!.status.replace(/_/g, " ")}
                          </span>
                        );
                      })()}
                    </div>
                  </div>
                </>
              )}
            </div>
          )}

          {/* Penalty Exposure */}
          {taxData.penalty_exposure > 0 && (
            <div
              className="rounded-xl p-5 flex items-center justify-between"
              style={{
                background: T.roseBg,
                border: "1px solid rgba(220,38,38,0.15)",
              }}
            >
              <div className="flex items-center gap-3">
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center"
                  style={{
                    background: "rgba(220,38,38,0.1)",
                    color: T.rose,
                  }}
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={1.5}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
                    />
                  </svg>
                </div>
                <div>
                  <div
                    className="text-sm font-semibold"
                    style={{ color: T.rose }}
                  >
                    Estimated Penalty Exposure
                  </div>
                  <div
                    className="text-xs"
                    style={{ color: T.textSecondary }}
                  >
                    Based on overdue filings for this company
                  </div>
                </div>
              </div>
              <div
                className="text-xl font-bold"
                style={{ color: T.rose }}
              >
                {formatCurrency(taxData.penalty_exposure)}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
