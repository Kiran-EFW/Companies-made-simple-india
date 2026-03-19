"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { caTdsCalculate, getCaTdsSections, getCaTdsDueDates } from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface TdsSection {
  section: string;
  description: string;
  rate_individual: number;
  rate_company: number;
  rate_no_pan: number;
  threshold?: number;
}

interface TdsResult {
  section: string;
  amount: number;
  tds_rate: number;
  tds_amount: number;
  net_payable: number;
  surcharge?: number;
  cess?: number;
  total_with_cess?: number;
}

interface DueDate {
  quarter: string;
  period: string;
  due_date: string;
  return_due_date: string;
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
};

function formatCurrency(amount: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(amount);
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CaTdsPage() {
  const { user, loading: authLoading } = useAuth();

  // Calculator form
  const [sections, setSections] = useState<TdsSection[]>([]);
  const [selectedSection, setSelectedSection] = useState("");
  const [amount, setAmount] = useState("");
  const [payeeType, setPayeeType] = useState("individual");
  const [hasPan, setHasPan] = useState(true);
  const [result, setResult] = useState<TdsResult | null>(null);
  const [calculating, setCalculating] = useState(false);

  // Due dates
  const [selectedQuarter, setSelectedQuarter] = useState("Q1");
  const [dueDates, setDueDates] = useState<DueDate | null>(null);

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading || !user) return;

    (async () => {
      try {
        const [sectionsData, dueDatesData] = await Promise.all([
          getCaTdsSections().catch(() => []),
          getCaTdsDueDates("Q1").catch(() => null),
        ]);
        setSections(Array.isArray(sectionsData) ? sectionsData : []);
        setDueDates(dueDatesData);
        if (Array.isArray(sectionsData) && sectionsData.length > 0) {
          setSelectedSection(sectionsData[0].section);
        }
      } catch (err) {
        console.error("Failed to load TDS data:", err);
      } finally {
        setLoading(false);
      }
    })();
  }, [user, authLoading]);

  const handleQuarterChange = async (q: string) => {
    setSelectedQuarter(q);
    try {
      const data = await getCaTdsDueDates(q);
      setDueDates(data);
    } catch {
      setDueDates(null);
    }
  };

  const handleCalculate = async () => {
    if (!selectedSection || !amount) return;
    setCalculating(true);
    setResult(null);
    try {
      const data = await caTdsCalculate({
        section: selectedSection,
        amount: parseFloat(amount),
        payee_type: payeeType,
        has_pan: hasPan,
      });
      setResult(data);
    } catch (err: any) {
      alert(err.message || "Calculation failed");
    } finally {
      setCalculating(false);
    }
  };

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
          TDS Calculator
        </h1>
        <p className="text-sm" style={{ color: T.textSecondary }}>
          Calculate TDS deductions across sections. Reference rates and quarterly
          due dates below.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Calculator Form */}
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
            Calculate TDS
          </h2>

          <div className="space-y-4">
            {/* Section */}
            <div>
              <label
                className="block text-xs font-medium mb-1.5"
                style={{ color: T.textMuted }}
              >
                TDS Section
              </label>
              <select
                value={selectedSection}
                onChange={(e) => setSelectedSection(e.target.value)}
                className="w-full px-3 py-2.5 rounded-lg text-sm"
                style={{
                  background: T.pageBg,
                  border: `1px solid ${T.cardBorder}`,
                  color: T.textPrimary,
                  outline: "none",
                }}
              >
                {sections.map((s) => (
                  <option key={s.section} value={s.section}>
                    {s.section} — {s.description}
                  </option>
                ))}
              </select>
            </div>

            {/* Amount */}
            <div>
              <label
                className="block text-xs font-medium mb-1.5"
                style={{ color: T.textMuted }}
              >
                Amount (INR)
              </label>
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="e.g. 100000"
                className="w-full px-3 py-2.5 rounded-lg text-sm"
                style={{
                  background: T.pageBg,
                  border: `1px solid ${T.cardBorder}`,
                  color: T.textPrimary,
                  outline: "none",
                }}
              />
            </div>

            {/* Payee Type */}
            <div>
              <label
                className="block text-xs font-medium mb-1.5"
                style={{ color: T.textMuted }}
              >
                Payee Type
              </label>
              <div className="flex gap-2">
                {["individual", "company", "huf"].map((pt) => (
                  <button
                    key={pt}
                    onClick={() => setPayeeType(pt)}
                    className="px-3 py-2 rounded-lg text-xs font-medium capitalize transition-colors"
                    style={{
                      background:
                        payeeType === pt ? T.accentBg : T.pageBg,
                      color:
                        payeeType === pt ? T.accent : T.textSecondary,
                      border: `1px solid ${payeeType === pt ? T.accent : T.cardBorder}`,
                    }}
                  >
                    {pt === "huf" ? "HUF" : pt}
                  </button>
                ))}
              </div>
            </div>

            {/* Has PAN */}
            <div className="flex items-center gap-3">
              <button
                onClick={() => setHasPan(!hasPan)}
                className="relative w-10 h-5 rounded-full transition-colors"
                style={{
                  background: hasPan ? T.accent : T.cardBorder,
                }}
              >
                <div
                  className="absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform"
                  style={{
                    left: hasPan ? "calc(100% - 18px)" : "2px",
                  }}
                />
              </button>
              <span
                className="text-sm"
                style={{ color: T.textSecondary }}
              >
                Has PAN
              </span>
            </div>

            {/* Calculate Button */}
            <button
              onClick={handleCalculate}
              disabled={!selectedSection || !amount || calculating}
              className="w-full py-2.5 rounded-lg text-sm font-medium text-white transition-colors disabled:opacity-50"
              style={{ background: T.accent }}
            >
              {calculating ? "Calculating..." : "Calculate TDS"}
            </button>
          </div>
        </div>

        {/* Result */}
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
            Result
          </h2>

          {result ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div
                    className="text-xs mb-1"
                    style={{ color: T.textMuted }}
                  >
                    TDS Rate
                  </div>
                  <div
                    className="text-lg font-bold"
                    style={{ color: T.accent }}
                  >
                    {result.tds_rate}%
                  </div>
                </div>
                <div>
                  <div
                    className="text-xs mb-1"
                    style={{ color: T.textMuted }}
                  >
                    TDS Amount
                  </div>
                  <div
                    className="text-lg font-bold"
                    style={{ color: T.textPrimary }}
                  >
                    {formatCurrency(result.tds_amount)}
                  </div>
                </div>
              </div>

              <div
                className="h-px"
                style={{ background: T.cardBorder }}
              />

              <div className="space-y-2.5">
                <div className="flex justify-between text-sm">
                  <span style={{ color: T.textSecondary }}>
                    Gross Amount
                  </span>
                  <span
                    className="font-medium"
                    style={{ color: T.textPrimary }}
                  >
                    {formatCurrency(result.amount)}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span style={{ color: T.textSecondary }}>
                    TDS Deducted
                  </span>
                  <span
                    className="font-medium"
                    style={{ color: T.rose }}
                  >
                    -{formatCurrency(result.tds_amount)}
                  </span>
                </div>
                {(result.surcharge ?? 0) > 0 && (
                  <div className="flex justify-between text-sm">
                    <span style={{ color: T.textSecondary }}>
                      Surcharge
                    </span>
                    <span
                      className="font-medium"
                      style={{ color: T.textPrimary }}
                    >
                      {formatCurrency(result.surcharge!)}
                    </span>
                  </div>
                )}
                {(result.cess ?? 0) > 0 && (
                  <div className="flex justify-between text-sm">
                    <span style={{ color: T.textSecondary }}>
                      Health &amp; Education Cess
                    </span>
                    <span
                      className="font-medium"
                      style={{ color: T.textPrimary }}
                    >
                      {formatCurrency(result.cess!)}
                    </span>
                  </div>
                )}
                <div
                  className="h-px"
                  style={{ background: T.cardBorder }}
                />
                <div className="flex justify-between text-sm">
                  <span
                    className="font-semibold"
                    style={{ color: T.textPrimary }}
                  >
                    Net Payable
                  </span>
                  <span
                    className="font-bold text-base"
                    style={{ color: T.emerald }}
                  >
                    {formatCurrency(result.net_payable)}
                  </span>
                </div>
                {result.total_with_cess != null &&
                  result.total_with_cess !== result.tds_amount && (
                    <div className="flex justify-between text-sm">
                      <span style={{ color: T.textSecondary }}>
                        Total TDS with Cess
                      </span>
                      <span
                        className="font-medium"
                        style={{ color: T.textPrimary }}
                      >
                        {formatCurrency(result.total_with_cess)}
                      </span>
                    </div>
                  )}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center py-12">
              <p className="text-sm" style={{ color: T.textMuted }}>
                Enter details and click Calculate to see results.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Quarterly Due Dates */}
      <div
        className="rounded-xl p-5 mb-8"
        style={{
          background: T.cardBg,
          border: `1px solid ${T.cardBorder}`,
        }}
      >
        <div className="flex items-center justify-between mb-4">
          <h2
            className="text-sm font-semibold"
            style={{ color: T.textPrimary }}
          >
            TDS Quarterly Due Dates
          </h2>
          <div className="flex gap-1">
            {["Q1", "Q2", "Q3", "Q4"].map((q) => (
              <button
                key={q}
                onClick={() => handleQuarterChange(q)}
                className="px-3 py-1.5 rounded-md text-xs font-medium transition-colors"
                style={{
                  background:
                    selectedQuarter === q ? T.accent : T.pageBg,
                  color:
                    selectedQuarter === q ? "#ffffff" : T.textSecondary,
                }}
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {dueDates ? (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div
              className="rounded-lg p-3"
              style={{ background: T.pageBg }}
            >
              <div
                className="text-xs mb-1"
                style={{ color: T.textMuted }}
              >
                Period
              </div>
              <div
                className="text-sm font-medium"
                style={{ color: T.textPrimary }}
              >
                {dueDates.period}
              </div>
            </div>
            <div
              className="rounded-lg p-3"
              style={{ background: T.pageBg }}
            >
              <div
                className="text-xs mb-1"
                style={{ color: T.textMuted }}
              >
                TDS Deposit Due
              </div>
              <div
                className="text-sm font-medium"
                style={{ color: T.textPrimary }}
              >
                {dueDates.due_date}
              </div>
            </div>
            <div
              className="rounded-lg p-3"
              style={{ background: T.pageBg }}
            >
              <div
                className="text-xs mb-1"
                style={{ color: T.textMuted }}
              >
                Return Filing Due
              </div>
              <div
                className="text-sm font-medium"
                style={{ color: T.textPrimary }}
              >
                {dueDates.return_due_date}
              </div>
            </div>
          </div>
        ) : (
          <p className="text-sm" style={{ color: T.textMuted }}>
            No due date data available.
          </p>
        )}
      </div>

      {/* TDS Sections Reference Table */}
      {sections.length > 0 && (
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
              TDS Section Rates Reference
            </h2>
          </div>
          <div
            className="grid grid-cols-[80px_1fr_80px_80px_80px] gap-3 px-5 py-2.5 text-xs font-semibold uppercase tracking-wider"
            style={{
              color: T.textMuted,
              borderBottom: `1px solid ${T.cardBorder}`,
              background: T.pageBg,
            }}
          >
            <div>Section</div>
            <div>Description</div>
            <div>Individual</div>
            <div>Company</div>
            <div>No PAN</div>
          </div>
          {sections.map((s, idx) => (
            <div
              key={s.section}
              className="grid grid-cols-[80px_1fr_80px_80px_80px] gap-3 px-5 py-2.5 items-center text-sm"
              style={{
                borderBottom:
                  idx < sections.length - 1
                    ? `1px solid ${T.cardBorder}`
                    : undefined,
              }}
            >
              <div
                className="text-xs font-semibold"
                style={{ color: T.accent }}
              >
                {s.section}
              </div>
              <div
                className="text-xs truncate"
                style={{ color: T.textSecondary }}
              >
                {s.description}
              </div>
              <div
                className="text-xs font-medium"
                style={{ color: T.textPrimary }}
              >
                {s.rate_individual}%
              </div>
              <div
                className="text-xs font-medium"
                style={{ color: T.textPrimary }}
              >
                {s.rate_company}%
              </div>
              <div
                className="text-xs font-medium"
                style={{ color: T.rose }}
              >
                {s.rate_no_pan}%
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
