"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { getCaDashboardSummary, getCaAllScores } from "@/lib/api";
import Link from "next/link";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface DashboardSummary {
  total_companies: number;
  pending_tasks: number;
  overdue_tasks: number;
  upcoming_tasks: number;
}

interface CompanyScore {
  company_id: number;
  company_name: string;
  entity_type: string;
  score: number;
  grade: string;
  total_tasks: number;
  completed: number;
  overdue: number;
  due_soon: number;
  upcoming: number;
  estimated_penalty_exposure: number;
  message: string;
}

// ---------------------------------------------------------------------------
// Theme constants
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

function gradeColor(grade: string) {
  if (grade.startsWith("A")) return T.emerald;
  if (grade.startsWith("B")) return T.accent;
  if (grade === "C") return T.amber;
  return T.rose;
}

function gradeBg(grade: string) {
  if (grade.startsWith("A")) return T.emeraldBg;
  if (grade.startsWith("B")) return T.accentBg;
  if (grade === "C") return T.amberBg;
  return T.roseBg;
}

function formatCurrency(amount: number) {
  if (amount === 0) return "None";
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount);
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CaDashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary>({
    total_companies: 0, pending_tasks: 0, overdue_tasks: 0, upcoming_tasks: 0,
  });
  const [scores, setScores] = useState<CompanyScore[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading || !user) return;

    (async () => {
      try {
        const [summaryData, scoresData] = await Promise.all([
          getCaDashboardSummary(),
          getCaAllScores().catch(() => []),
        ]);
        setSummary(summaryData);
        setScores(Array.isArray(scoresData) ? scoresData : []);
      } catch (err) {
        console.error("Failed to fetch CA dashboard:", err);
      } finally {
        setLoading(false);
      }
    })();
  }, [user, authLoading]);

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: T.accent }} />
      </div>
    );
  }

  const totalPenalty = scores.reduce((sum, s) => sum + (s.estimated_penalty_exposure || 0), 0);

  const stats = [
    {
      label: "Companies",
      value: summary.total_companies,
      color: T.accent,
      bg: T.accentBg,
      icon: "M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21m-3.75 3H21m-3.75 3H21",
    },
    {
      label: "Pending",
      value: summary.pending_tasks,
      color: T.amber,
      bg: T.amberBg,
      icon: "M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z",
    },
    {
      label: "Overdue",
      value: summary.overdue_tasks,
      color: T.rose,
      bg: T.roseBg,
      icon: "M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z",
    },
    {
      label: "Upcoming",
      value: summary.upcoming_tasks,
      color: T.emerald,
      bg: T.emeraldBg,
      icon: "M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5",
    },
  ];

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 lg:py-10">
      {/* ── Page Header ─────────────────────────────────────── */}
      <div className="mb-8">
        <p className="text-sm font-medium mb-1" style={{ color: T.accent }}>
          Welcome back
        </p>
        <h1 className="text-2xl font-bold" style={{ fontFamily: "var(--font-display)", color: T.textPrimary }}>
          {user?.full_name || "CA"}
        </h1>
        <p className="text-sm mt-1" style={{ color: T.textSecondary }}>
          Here&apos;s an overview of your assigned companies and compliance workload.
        </p>
      </div>

      {/* ── Stat Cards ──────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((s) => (
          <div key={s.label} className="rounded-xl p-5" style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}` }}>
            <div className="flex items-center gap-3 mb-3">
              <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: s.bg, color: s.color }}>
                <svg className="w-[18px] h-[18px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d={s.icon} />
                </svg>
              </div>
            </div>
            <div className="text-2xl font-bold" style={{ color: T.textPrimary }}>{s.value}</div>
            <div className="text-xs font-medium mt-0.5" style={{ color: T.textMuted }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* ── Penalty Exposure Banner ─────────────────────────── */}
      {totalPenalty > 0 && (
        <div
          className="rounded-xl p-5 mb-8 flex items-center justify-between"
          style={{ background: T.roseBg, border: `1px solid rgba(220,38,38,0.15)` }}
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: "rgba(220,38,38,0.1)", color: T.rose }}>
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
            </div>
            <div>
              <div className="text-sm font-semibold" style={{ color: T.rose }}>Estimated Penalty Exposure</div>
              <div className="text-xs" style={{ color: T.textSecondary }}>Across all assigned companies with overdue filings</div>
            </div>
          </div>
          <div className="text-xl font-bold" style={{ color: T.rose }}>
            {formatCurrency(totalPenalty)}
          </div>
        </div>
      )}

      {/* ── Company Compliance Scores ───────────────────────── */}
      {scores.length > 0 && (
        <div className="mb-8">
          <h2 className="text-sm font-semibold mb-4" style={{ color: T.textPrimary }}>
            Company Compliance Health
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {scores.map((s) => (
              <Link
                key={s.company_id}
                href={`/ca/companies/${s.company_id}`}
                className="rounded-xl p-5 transition-colors block"
                style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}` }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = T.accent; }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = T.cardBorder; }}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-semibold truncate" style={{ color: T.textPrimary }}>
                      {s.company_name}
                    </div>
                    <div className="text-xs capitalize mt-0.5" style={{ color: T.textMuted }}>
                      {s.entity_type?.replace(/_/g, " ")}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0 ml-3">
                    <span
                      className="text-lg font-bold"
                      style={{ color: gradeColor(s.grade) }}
                    >
                      {s.grade}
                    </span>
                    <span
                      className="text-xs font-semibold px-2 py-0.5 rounded-full"
                      style={{ background: gradeBg(s.grade), color: gradeColor(s.grade) }}
                    >
                      {s.score}%
                    </span>
                  </div>
                </div>

                {/* Score bar */}
                <div className="w-full h-2 rounded-full mb-3" style={{ background: "#f1f5f9" }}>
                  <div
                    className="h-2 rounded-full transition-all"
                    style={{ width: `${s.score}%`, background: gradeColor(s.grade) }}
                  />
                </div>

                {/* Breakdown */}
                <div className="flex items-center gap-4 text-[11px]">
                  <span style={{ color: T.emerald }}>
                    <strong>{s.completed}</strong> done
                  </span>
                  {s.overdue > 0 && (
                    <span style={{ color: T.rose }}>
                      <strong>{s.overdue}</strong> overdue
                    </span>
                  )}
                  {s.due_soon > 0 && (
                    <span style={{ color: T.amber }}>
                      <strong>{s.due_soon}</strong> due soon
                    </span>
                  )}
                  <span style={{ color: T.textMuted }}>
                    <strong>{s.upcoming}</strong> upcoming
                  </span>
                  {s.estimated_penalty_exposure > 0 && (
                    <span className="ml-auto font-semibold" style={{ color: T.rose }}>
                      {formatCurrency(s.estimated_penalty_exposure)} penalty
                    </span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* ── Quick Actions ───────────────────────────────────── */}
      <div className="rounded-xl p-6" style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}` }}>
        <h2 className="text-sm font-semibold mb-4" style={{ color: T.textPrimary }}>
          Quick Actions
        </h2>
        <div className="flex flex-wrap gap-3">
          <Link
            href="/ca/tasks"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium text-white transition-colors"
            style={{ background: T.accent }}
            onMouseEnter={(e) => { e.currentTarget.style.background = "#0f766e"; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = T.accent; }}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25z" />
            </svg>
            All Tasks
          </Link>
          <Link
            href="/ca/calendar"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors"
            style={{ background: T.accentBg, color: T.accent, border: `1px solid rgba(20,184,166,0.15)` }}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
            </svg>
            Compliance Calendar
          </Link>
          <Link
            href="/ca/companies"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors"
            style={{ color: T.textSecondary, border: `1px solid ${T.cardBorder}` }}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21m-3.75 3H21m-3.75 3H21" />
            </svg>
            View Companies
          </Link>
          {summary.overdue_tasks > 0 && (
            <Link
              href="/ca/tasks?status=overdue"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors"
              style={{ background: T.roseBg, color: T.rose, border: `1px solid rgba(220,38,38,0.15)` }}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
              {summary.overdue_tasks} Overdue
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}
