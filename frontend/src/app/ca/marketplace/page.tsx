"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import {
  getPartnerDashboard,
  getPartnerAssignments,
  getPartnerEarnings,
} from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface DashboardStats {
  assigned: number;
  in_progress: number;
  completed: number;
  total_earned: number;
  avg_rating: number;
  pending_settlements: number;
}

interface Assignment {
  id: number;
  service_request_id: number;
  partner_id: number;
  assigned_by: number;
  status: string;
  fulfillment_fee: number;
  platform_margin: number;
  accepted_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  deliverables_note: string | null;
  review_note: string | null;
  client_rating: number | null;
  client_review: string | null;
  service_name: string;
  service_key: string;
  category: string;
  company_id: number;
  partner_name: string;
  created_at: string;
  updated_at: string;
}

interface Earning {
  fulfillment_id: number;
  service_name: string;
  gross_amount: number;
  tds_amount: number;
  net_amount: number;
  status: string;
  completed_at: string | null;
  paid_at: string | null;
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
  blue: "#2563eb",
  blueBg: "rgba(37, 99, 235, 0.06)",
  purple: "#7c3aed",
  purpleBg: "rgba(124, 58, 237, 0.06)",
  gray: "#64748b",
  grayBg: "rgba(100, 116, 139, 0.06)",
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatRupees(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  })
    .format(amount)
    .replace("₹", "Rs ");
}

function formatDate(d: string | null): string {
  if (!d) return "-";
  return new Date(d).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function statusBadgeStyle(status: string): { bg: string; color: string; label: string } {
  switch (status) {
    case "assigned":
      return { bg: T.amberBg, color: T.amber, label: "Assigned" };
    case "accepted":
      return { bg: T.blueBg, color: T.blue, label: "Accepted" };
    case "in_progress":
      return { bg: T.blueBg, color: T.blue, label: "In Progress" };
    case "deliverables_uploaded":
      return { bg: T.purpleBg, color: T.purple, label: "Deliverables Uploaded" };
    case "under_review":
      return { bg: T.purpleBg, color: T.purple, label: "Under Review" };
    case "revision_needed":
      return { bg: T.roseBg, color: T.rose, label: "Revision Needed" };
    case "completed":
      return { bg: T.emeraldBg, color: T.emerald, label: "Completed" };
    case "cancelled":
      return { bg: T.grayBg, color: T.gray, label: "Cancelled" };
    default:
      return { bg: T.grayBg, color: T.gray, label: status.replace(/_/g, " ") };
  }
}

function earningStatusStyle(status: string): { bg: string; color: string } {
  switch (status) {
    case "paid":
      return { bg: T.emeraldBg, color: T.emerald };
    case "pending":
      return { bg: T.amberBg, color: T.amber };
    case "processing":
      return { bg: T.blueBg, color: T.blue };
    default:
      return { bg: T.grayBg, color: T.gray };
  }
}

function renderStars(rating: number): string {
  const full = Math.floor(rating);
  const half = rating - full >= 0.5;
  let stars = "";
  for (let i = 0; i < full; i++) stars += "\u2605";
  if (half) stars += "\u00BD";
  const empty = 5 - full - (half ? 1 : 0);
  for (let i = 0; i < empty; i++) stars += "\u2606";
  return stars;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CaMarketplacePage() {
  const { user, loading: authLoading } = useAuth();

  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [earnings, setEarnings] = useState<Earning[]>([]);
  const [loading, setLoading] = useState(true);
  const [notRegistered, setNotRegistered] = useState(false);

  useEffect(() => {
    if (authLoading || !user) return;

    (async () => {
      try {
        const [dashData, assignData, earnData] = await Promise.all([
          getPartnerDashboard(),
          getPartnerAssignments().catch(() => []),
          getPartnerEarnings().catch(() => []),
        ]);
        setStats(dashData);
        setAssignments(Array.isArray(assignData) ? assignData : []);
        setEarnings(Array.isArray(earnData) ? earnData : []);
      } catch (err: any) {
        // If the API returns 404 or a "not registered" error, show the CTA
        if (
          err?.status === 404 ||
          err?.message?.toLowerCase().includes("not found") ||
          err?.message?.toLowerCase().includes("not registered")
        ) {
          setNotRegistered(true);
        } else {
          console.error("Failed to fetch marketplace dashboard:", err);
        }
      } finally {
        setLoading(false);
      }
    })();
  }, [user, authLoading]);

  // ── Loading State ────────────────────────────────────────────────────────
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

  // ── Not Registered CTA ──────────────────────────────────────────────────
  if (notRegistered) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-8 lg:py-10">
        <div className="mb-8">
          <h1
            className="text-2xl font-bold"
            style={{ fontFamily: "var(--font-display)", color: T.textPrimary }}
          >
            Marketplace
          </h1>
        </div>

        <div
          className="rounded-xl p-8 text-center"
          style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}` }}
        >
          <div
            className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-5"
            style={{ background: T.accentBg, color: T.accent }}
          >
            <svg
              className="w-8 h-8"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M13.5 21v-7.5a.75.75 0 01.75-.75h3a.75.75 0 01.75.75V21m-4.5 0H2.36m11.14 0H18m0 0h3.64m-1.39 0V9.349m-16.5 11.65V9.35m0 0a3.001 3.001 0 003.75-.615A2.993 2.993 0 009.75 9.75c.896 0 1.7-.393 2.25-1.016a2.993 2.993 0 002.25 1.016c.896 0 1.7-.393 2.25-1.016a3.001 3.001 0 003.75.614m-16.5 0a3.004 3.004 0 01-.621-4.72L4.318 3.44A1.5 1.5 0 015.378 3h13.243a1.5 1.5 0 011.06.44l1.19 1.189a3 3 0 01-.621 4.72m-13.5 8.65h3.75a.75.75 0 00.75-.75V13.5a.75.75 0 00-.75-.75H6.75a.75.75 0 00-.75.75v3.15c0 .415.336.75.75.75z"
              />
            </svg>
          </div>
          <h2
            className="text-lg font-semibold mb-2"
            style={{ color: T.textPrimary }}
          >
            Join the Marketplace
          </h2>
          <p
            className="text-sm mb-6 max-w-md mx-auto"
            style={{ color: T.textSecondary }}
          >
            Register as a marketplace partner to receive service assignments,
            fulfill client requests, and earn revenue through the platform.
          </p>
          <Link
            href="/ca/register-partner"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg text-sm font-semibold text-white transition-colors"
            style={{ background: T.accent }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "#0f766e";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = T.accent;
            }}
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
                d="M12 4.5v15m7.5-7.5h-15"
              />
            </svg>
            Register as Partner
          </Link>
        </div>
      </div>
    );
  }

  // ── Stat cards config ───────────────────────────────────────────────────
  const statCards = [
    {
      label: "Assigned",
      value: stats?.assigned ?? 0,
      color: T.amber,
      bg: T.amberBg,
      icon: "M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25z",
    },
    {
      label: "In Progress",
      value: stats?.in_progress ?? 0,
      color: T.blue,
      bg: T.blueBg,
      icon: "M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182M2.985 19.644V14.652",
    },
    {
      label: "Completed",
      value: stats?.completed ?? 0,
      color: T.emerald,
      bg: T.emeraldBg,
      icon: "M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
    },
    {
      label: "Total Earned",
      value: formatRupees(stats?.total_earned ?? 0),
      color: T.accent,
      bg: T.accentBg,
      icon: "M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z",
    },
    {
      label: "Avg Rating",
      value:
        (stats?.avg_rating ?? 0) > 0
          ? `${(stats?.avg_rating ?? 0).toFixed(1)} ${renderStars(stats?.avg_rating ?? 0)}`
          : "-",
      color: T.amber,
      bg: T.amberBg,
      icon: "M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z",
    },
    {
      label: "Pending Settlements",
      value: stats?.pending_settlements ?? 0,
      color: T.rose,
      bg: T.roseBg,
      icon: "M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z",
    },
  ];

  const recentAssignments = assignments.slice(0, 5);
  const recentEarnings = earnings.slice(0, 5);

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 lg:py-10">
      {/* ── Page Header ─────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1
            className="text-2xl font-bold"
            style={{
              fontFamily: "var(--font-display)",
              color: T.textPrimary,
            }}
          >
            Marketplace
          </h1>
          <p className="text-sm mt-1" style={{ color: T.textSecondary }}>
            Your marketplace assignments, earnings, and performance overview.
          </p>
        </div>
        <span
          className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold"
          style={{ background: T.emeraldBg, color: T.emerald }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full"
            style={{ background: T.emerald }}
          />
          Registered Partner
        </span>
      </div>

      {/* ── Stat Cards ──────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4 mb-8">
        {statCards.map((s) => (
          <div
            key={s.label}
            className="rounded-xl p-5"
            style={{
              background: T.cardBg,
              border: `1px solid ${T.cardBorder}`,
            }}
          >
            <div className="flex items-center gap-3 mb-3">
              <div
                className="w-9 h-9 rounded-lg flex items-center justify-center"
                style={{ background: s.bg, color: s.color }}
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
                    d={s.icon}
                  />
                </svg>
              </div>
            </div>
            <div
              className="text-2xl font-bold truncate"
              style={{ color: T.textPrimary }}
            >
              {s.value}
            </div>
            <div
              className="text-xs font-medium mt-0.5"
              style={{ color: T.textMuted }}
            >
              {s.label}
            </div>
          </div>
        ))}
      </div>

      {/* ── Recent Assignments ──────────────────────────────────────────── */}
      <div
        className="rounded-xl mb-8"
        style={{
          background: T.cardBg,
          border: `1px solid ${T.cardBorder}`,
        }}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b"
          style={{ borderColor: T.cardBorder }}
        >
          <h2
            className="text-sm font-semibold"
            style={{ color: T.textPrimary }}
          >
            Recent Assignments
          </h2>
          <Link
            href="/ca/marketplace/assignments"
            className="text-xs font-medium transition-colors"
            style={{ color: T.accent }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = "#0f766e";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = T.accent;
            }}
          >
            View All &rarr;
          </Link>
        </div>

        {recentAssignments.length === 0 ? (
          <div className="px-6 py-10 text-center">
            <p className="text-sm" style={{ color: T.textMuted }}>
              No assignments yet. New assignments will appear here once they are
              allocated to you.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr style={{ borderBottom: `1px solid ${T.cardBorder}` }}>
                  <th
                    className="text-left px-6 py-3 text-xs font-semibold uppercase tracking-wider"
                    style={{ color: T.textMuted }}
                  >
                    Service
                  </th>
                  <th
                    className="text-left px-6 py-3 text-xs font-semibold uppercase tracking-wider"
                    style={{ color: T.textMuted }}
                  >
                    Status
                  </th>
                  <th
                    className="text-right px-6 py-3 text-xs font-semibold uppercase tracking-wider"
                    style={{ color: T.textMuted }}
                  >
                    Fee
                  </th>
                  <th
                    className="text-right px-6 py-3 text-xs font-semibold uppercase tracking-wider"
                    style={{ color: T.textMuted }}
                  >
                    Date
                  </th>
                </tr>
              </thead>
              <tbody>
                {recentAssignments.map((a, idx) => {
                  const badge = statusBadgeStyle(a.status);
                  return (
                    <tr
                      key={a.id}
                      style={{
                        borderBottom:
                          idx < recentAssignments.length - 1
                            ? `1px solid ${T.cardBorder}`
                            : undefined,
                        background: idx % 2 === 1 ? T.pageBg : T.cardBg,
                      }}
                    >
                      <td className="px-6 py-3.5">
                        <div
                          className="font-medium truncate max-w-[200px]"
                          style={{ color: T.textPrimary }}
                        >
                          {a.service_name}
                        </div>
                        <div
                          className="text-xs mt-0.5 capitalize"
                          style={{ color: T.textMuted }}
                        >
                          {a.category?.replace(/_/g, " ")}
                        </div>
                      </td>
                      <td className="px-6 py-3.5">
                        <span
                          className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold"
                          style={{
                            background: badge.bg,
                            color: badge.color,
                          }}
                        >
                          {badge.label}
                        </span>
                      </td>
                      <td
                        className="px-6 py-3.5 text-right font-medium"
                        style={{ color: T.textPrimary }}
                      >
                        {formatRupees(a.fulfillment_fee)}
                      </td>
                      <td
                        className="px-6 py-3.5 text-right"
                        style={{ color: T.textSecondary }}
                      >
                        {formatDate(a.created_at)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Recent Earnings ─────────────────────────────────────────────── */}
      <div
        className="rounded-xl"
        style={{
          background: T.cardBg,
          border: `1px solid ${T.cardBorder}`,
        }}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b"
          style={{ borderColor: T.cardBorder }}
        >
          <h2
            className="text-sm font-semibold"
            style={{ color: T.textPrimary }}
          >
            Recent Earnings
          </h2>
          <Link
            href="/ca/marketplace/earnings"
            className="text-xs font-medium transition-colors"
            style={{ color: T.accent }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = "#0f766e";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = T.accent;
            }}
          >
            View All &rarr;
          </Link>
        </div>

        {recentEarnings.length === 0 ? (
          <div className="px-6 py-10 text-center">
            <p className="text-sm" style={{ color: T.textMuted }}>
              No earnings recorded yet. Complete assignments to start earning.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr style={{ borderBottom: `1px solid ${T.cardBorder}` }}>
                  <th
                    className="text-left px-6 py-3 text-xs font-semibold uppercase tracking-wider"
                    style={{ color: T.textMuted }}
                  >
                    Service
                  </th>
                  <th
                    className="text-right px-6 py-3 text-xs font-semibold uppercase tracking-wider"
                    style={{ color: T.textMuted }}
                  >
                    Gross
                  </th>
                  <th
                    className="text-right px-6 py-3 text-xs font-semibold uppercase tracking-wider"
                    style={{ color: T.textMuted }}
                  >
                    TDS
                  </th>
                  <th
                    className="text-right px-6 py-3 text-xs font-semibold uppercase tracking-wider"
                    style={{ color: T.textMuted }}
                  >
                    Net
                  </th>
                  <th
                    className="text-left px-6 py-3 text-xs font-semibold uppercase tracking-wider"
                    style={{ color: T.textMuted }}
                  >
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {recentEarnings.map((e, idx) => {
                  const es = earningStatusStyle(e.status);
                  return (
                    <tr
                      key={e.fulfillment_id}
                      style={{
                        borderBottom:
                          idx < recentEarnings.length - 1
                            ? `1px solid ${T.cardBorder}`
                            : undefined,
                        background: idx % 2 === 1 ? T.pageBg : T.cardBg,
                      }}
                    >
                      <td className="px-6 py-3.5">
                        <div
                          className="font-medium truncate max-w-[200px]"
                          style={{ color: T.textPrimary }}
                        >
                          {e.service_name}
                        </div>
                      </td>
                      <td
                        className="px-6 py-3.5 text-right font-medium"
                        style={{ color: T.textPrimary }}
                      >
                        {formatRupees(e.gross_amount)}
                      </td>
                      <td
                        className="px-6 py-3.5 text-right"
                        style={{ color: T.rose }}
                      >
                        -{formatRupees(e.tds_amount)}
                      </td>
                      <td
                        className="px-6 py-3.5 text-right font-semibold"
                        style={{ color: T.emerald }}
                      >
                        {formatRupees(e.net_amount)}
                      </td>
                      <td className="px-6 py-3.5">
                        <span
                          className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold capitalize"
                          style={{
                            background: es.bg,
                            color: es.color,
                          }}
                        >
                          {e.status}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
