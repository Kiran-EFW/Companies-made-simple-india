"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { getPartnerEarnings, getPartnerDashboard } from "@/lib/api";
import Link from "next/link";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface EarningsHistoryItem {
  fulfillment_id: number;
  service_name: string;
  gross_amount: number;
  tds_amount: number;
  net_amount: number;
  status: string;
  completed_at: string | null;
  paid_at: string | null;
}

interface DashboardSummary {
  assigned: number;
  in_progress: number;
  completed: number;
  total_earned: number;
  avg_rating: number;
  pending_settlements: number;
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
  purple: "#7c3aed",
  purpleBg: "rgba(124, 58, 237, 0.06)",
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatCurrency(amount: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  })
    .format(amount)
    .replace("INR", "Rs")
    .replace(/\u00A0/, " ");
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "\u2014";
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function statusBadge(status: string) {
  const map: Record<string, { color: string; bg: string; label: string }> = {
    pending: { color: T.amber, bg: T.amberBg, label: "Pending" },
    invoice_received: { color: T.blue, bg: T.blueBg, label: "Invoice Received" },
    approved: { color: T.purple, bg: T.purpleBg, label: "Approved" },
    paid: { color: T.emerald, bg: T.emeraldBg, label: "Paid" },
  };
  const s = map[status] || { color: T.textMuted, bg: T.pageBg, label: status };
  return s;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function MarketplaceEarningsPage() {
  const { user, loading: authLoading } = useAuth();
  const [earnings, setEarnings] = useState<EarningsHistoryItem[]>([]);
  const [dashboard, setDashboard] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading || !user) return;

    (async () => {
      try {
        const [earningsData, dashboardData] = await Promise.all([
          getPartnerEarnings().catch(() => []),
          getPartnerDashboard().catch(() => null),
        ]);
        setEarnings(Array.isArray(earningsData) ? earningsData : []);
        setDashboard(dashboardData);
      } catch (err) {
        console.error("Failed to fetch earnings data:", err);
      } finally {
        setLoading(false);
      }
    })();
  }, [user, authLoading]);

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

  // Totals row
  const totals = earnings.reduce(
    (acc, e) => ({
      gross: acc.gross + e.gross_amount,
      tds: acc.tds + e.tds_amount,
      net: acc.net + e.net_amount,
    }),
    { gross: 0, tds: 0, net: 0 },
  );

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 lg:py-10">
      {/* ── Header + Breadcrumb ─────────────────────────────── */}
      <div className="mb-8">
        <div className="flex items-center gap-2 text-sm mb-2">
          <Link
            href="/ca/marketplace"
            className="transition-colors"
            style={{ color: T.accent }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = "#0f766e";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = T.accent;
            }}
          >
            Marketplace
          </Link>
          <span style={{ color: T.textMuted }}>/</span>
          <span style={{ color: T.textSecondary }}>Earnings</span>
        </div>
        <h1
          className="text-2xl font-bold"
          style={{
            fontFamily: "var(--font-display)",
            color: T.textPrimary,
          }}
        >
          Earnings &amp; Settlements
        </h1>
        <p className="text-sm mt-1" style={{ color: T.textSecondary }}>
          Track your marketplace income, TDS deductions, and settlement history.
        </p>
      </div>

      {/* ── Summary Cards ───────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        {/* Total Earned */}
        <div
          className="rounded-xl p-5"
          style={{
            background: T.cardBg,
            border: `1px solid ${T.cardBorder}`,
          }}
        >
          <div className="flex items-center gap-3 mb-3">
            <div
              className="w-9 h-9 rounded-lg flex items-center justify-center"
              style={{ background: T.emeraldBg, color: T.emerald }}
            >
              <svg
                className="w-[18px] h-[18px]"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={1.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z"
                />
              </svg>
            </div>
          </div>
          <div
            className="text-2xl font-bold"
            style={{ color: T.textPrimary }}
          >
            {formatCurrency(dashboard?.total_earned ?? 0)}
          </div>
          <div
            className="text-xs font-medium mt-0.5"
            style={{ color: T.textMuted }}
          >
            Total Earned
          </div>
        </div>

        {/* Pending Settlements */}
        <div
          className="rounded-xl p-5"
          style={{
            background: T.cardBg,
            border: `1px solid ${T.cardBorder}`,
          }}
        >
          <div className="flex items-center gap-3 mb-3">
            <div
              className="w-9 h-9 rounded-lg flex items-center justify-center"
              style={{ background: T.amberBg, color: T.amber }}
            >
              <svg
                className="w-[18px] h-[18px]"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={1.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
          </div>
          <div
            className="text-2xl font-bold"
            style={{ color: T.textPrimary }}
          >
            {dashboard?.pending_settlements ?? 0}
          </div>
          <div
            className="text-xs font-medium mt-0.5"
            style={{ color: T.textMuted }}
          >
            Pending Settlements
          </div>
        </div>

        {/* Avg Rating */}
        <div
          className="rounded-xl p-5"
          style={{
            background: T.cardBg,
            border: `1px solid ${T.cardBorder}`,
          }}
        >
          <div className="flex items-center gap-3 mb-3">
            <div
              className="w-9 h-9 rounded-lg flex items-center justify-center"
              style={{ background: T.accentBg, color: T.accent }}
            >
              <svg
                className="w-[18px] h-[18px]"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={1.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z"
                />
              </svg>
            </div>
          </div>
          <div
            className="text-2xl font-bold"
            style={{ color: T.textPrimary }}
          >
            {dashboard?.avg_rating != null
              ? `${dashboard.avg_rating.toFixed(1)} / 5`
              : "N/A"}
          </div>
          <div
            className="text-xs font-medium mt-0.5"
            style={{ color: T.textMuted }}
          >
            Avg Rating
          </div>
        </div>
      </div>

      {/* ── Earnings Breakdown Info ──────────────────────────── */}
      <div
        className="rounded-xl p-5 mb-8"
        style={{
          background: T.accentBg,
          border: `1px solid rgba(20, 184, 166, 0.15)`,
        }}
      >
        <div className="flex items-start gap-3">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
            style={{ background: "rgba(20, 184, 166, 0.12)", color: T.accent }}
          >
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z"
              />
            </svg>
          </div>
          <div>
            <h3
              className="text-sm font-semibold mb-1.5"
              style={{ color: T.accent }}
            >
              How Earnings Are Calculated
            </h3>
            <ul className="space-y-1 text-xs" style={{ color: T.textSecondary }}>
              <li>
                <span className="font-medium" style={{ color: T.textPrimary }}>
                  Your earnings
                </span>{" "}
                = 80% of service fee
              </li>
              <li>
                <span className="font-medium" style={{ color: T.textPrimary }}>
                  TDS at 10%
                </span>{" "}
                deducted under Section 194J
              </li>
              <li>
                <span className="font-medium" style={{ color: T.textPrimary }}>
                  Net payout
                </span>{" "}
                = Gross - TDS
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* ── Earnings Table ──────────────────────────────────── */}
      {earnings.length > 0 ? (
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
              Earnings History
            </h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full min-w-[700px]">
              <thead>
                <tr
                  style={{
                    borderBottom: `1px solid ${T.cardBorder}`,
                    background: T.pageBg,
                  }}
                >
                  {[
                    "Service Name",
                    "Gross Amount",
                    "TDS (10%)",
                    "Net Amount",
                    "Status",
                    "Completed",
                    "Paid",
                  ].map((col) => (
                    <th
                      key={col}
                      className="px-5 py-2.5 text-left text-xs font-semibold uppercase tracking-wider"
                      style={{ color: T.textMuted }}
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {earnings.map((e, idx) => {
                  const badge = statusBadge(e.status);
                  return (
                    <tr
                      key={e.fulfillment_id}
                      style={{
                        borderBottom:
                          idx < earnings.length - 1
                            ? `1px solid ${T.cardBorder}`
                            : undefined,
                      }}
                    >
                      <td className="px-5 py-3">
                        <span
                          className="text-sm font-semibold"
                          style={{ color: T.textPrimary }}
                        >
                          {e.service_name}
                        </span>
                      </td>
                      <td
                        className="px-5 py-3 text-sm"
                        style={{ color: T.textPrimary }}
                      >
                        {formatCurrency(e.gross_amount)}
                      </td>
                      <td
                        className="px-5 py-3 text-sm"
                        style={{ color: T.rose }}
                      >
                        -{formatCurrency(e.tds_amount)}
                      </td>
                      <td className="px-5 py-3">
                        <span
                          className="text-sm font-medium"
                          style={{ color: T.emerald }}
                        >
                          {formatCurrency(e.net_amount)}
                        </span>
                      </td>
                      <td className="px-5 py-3">
                        <span
                          className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                          style={{
                            background: badge.bg,
                            color: badge.color,
                          }}
                        >
                          {badge.label}
                        </span>
                      </td>
                      <td
                        className="px-5 py-3 text-sm"
                        style={{ color: T.textSecondary }}
                      >
                        {formatDate(e.completed_at)}
                      </td>
                      <td
                        className="px-5 py-3 text-sm"
                        style={{ color: T.textSecondary }}
                      >
                        {formatDate(e.paid_at)}
                      </td>
                    </tr>
                  );
                })}

                {/* Totals row */}
                <tr
                  style={{
                    borderTop: `2px solid ${T.cardBorder}`,
                    background: T.pageBg,
                  }}
                >
                  <td className="px-5 py-3">
                    <span
                      className="text-sm font-bold"
                      style={{ color: T.textPrimary }}
                    >
                      Total
                    </span>
                  </td>
                  <td className="px-5 py-3">
                    <span
                      className="text-sm font-bold"
                      style={{ color: T.textPrimary }}
                    >
                      {formatCurrency(totals.gross)}
                    </span>
                  </td>
                  <td className="px-5 py-3">
                    <span
                      className="text-sm font-bold"
                      style={{ color: T.rose }}
                    >
                      -{formatCurrency(totals.tds)}
                    </span>
                  </td>
                  <td className="px-5 py-3">
                    <span
                      className="text-sm font-bold"
                      style={{ color: T.emerald }}
                    >
                      {formatCurrency(totals.net)}
                    </span>
                  </td>
                  <td colSpan={3} />
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        /* ── Empty State ──────────────────────────────────────── */
        <div
          className="rounded-xl p-12 text-center"
          style={{
            background: T.cardBg,
            border: `1px solid ${T.cardBorder}`,
          }}
        >
          <div
            className="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4"
            style={{ background: T.accentBg, color: T.accent }}
          >
            <svg
              className="w-6 h-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z"
              />
            </svg>
          </div>
          <h3
            className="text-sm font-semibold mb-1"
            style={{ color: T.textPrimary }}
          >
            No earnings yet
          </h3>
          <p className="text-sm" style={{ color: T.textMuted }}>
            Complete marketplace assignments to start earning.
          </p>
          <Link
            href="/ca/marketplace"
            className="inline-flex items-center gap-2 mt-4 px-4 py-2.5 rounded-lg text-sm font-medium text-white transition-colors"
            style={{ background: T.accent }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "#0f766e";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = T.accent;
            }}
          >
            Browse Marketplace
          </Link>
        </div>
      )}
    </div>
  );
}
