"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import {
  getPartnerAssignments,
  acceptAssignment,
  startAssignment,
  deliverAssignment,
} from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Assignment {
  id: number;
  service_request_id: number;
  partner_id: number;
  assigned_by: number | null;
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
  gray: "#64748b",
  grayBg: "rgba(100, 116, 139, 0.06)",
};

// ---------------------------------------------------------------------------
// Status Filters
// ---------------------------------------------------------------------------

const STATUS_FILTERS = [
  { value: "", label: "All" },
  { value: "assigned", label: "Assigned" },
  { value: "accepted", label: "Accepted" },
  { value: "in_progress", label: "In Progress" },
  { value: "deliverables_uploaded", label: "Delivered" },
  { value: "completed", label: "Completed" },
  { value: "revision_needed", label: "Revision Needed" },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function statusStyle(status: string): { bg: string; color: string; label: string } {
  switch (status) {
    case "assigned":
      return { bg: T.amberBg, color: T.amber, label: "Assigned" };
    case "accepted":
      return { bg: T.blueBg, color: T.blue, label: "Accepted" };
    case "in_progress":
      return { bg: T.accentBg, color: T.accent, label: "In Progress" };
    case "deliverables_uploaded":
      return { bg: T.purpleBg, color: T.purple, label: "Delivered" };
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

function formatDate(d: string | null) {
  if (!d) return null;
  return new Date(d).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function formatCurrency(amount: number) {
  return new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: 0,
  }).format(amount);
}

function StarRating({ rating }: { rating: number }) {
  return (
    <span className="inline-flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        <svg
          key={star}
          className="w-3.5 h-3.5"
          fill={star <= rating ? "#f59e0b" : "none"}
          viewBox="0 0 24 24"
          stroke={star <= rating ? "#f59e0b" : T.textMuted}
          strokeWidth={1.5}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z"
          />
        </svg>
      ))}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CaMarketplaceAssignmentsPage() {
  const { user, loading: authLoading } = useAuth();
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("");

  // Action state
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [toast, setToast] = useState<{ type: "success" | "error"; message: string } | null>(null);

  // Delivery note form
  const [deliveryFormId, setDeliveryFormId] = useState<number | null>(null);
  const [deliveryNote, setDeliveryNote] = useState("");

  const showToast = useCallback((type: "success" | "error", message: string) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 4000);
  }, []);

  const fetchAssignments = useCallback(
    async (statusFilter?: string) => {
      try {
        setError("");
        const data = await getPartnerAssignments(statusFilter || undefined);
        setAssignments(Array.isArray(data) ? data : []);
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Failed to load assignments";
        setError(message);
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  useEffect(() => {
    if (authLoading || !user) return;
    fetchAssignments(filter);
  }, [user, authLoading, filter, fetchAssignments]);

  // ── Action Handlers ─────────────────────────────────────────────────────

  const handleAccept = async (id: number) => {
    setActionLoading(id);
    try {
      await acceptAssignment(id);
      showToast("success", "Assignment accepted. You can now start working.");
      await fetchAssignments(filter);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to accept assignment";
      showToast("error", message);
    } finally {
      setActionLoading(null);
    }
  };

  const handleStartWork = async (id: number) => {
    setActionLoading(id);
    try {
      await startAssignment(id);
      showToast("success", "Work started. Good luck!");
      await fetchAssignments(filter);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to start assignment";
      showToast("error", message);
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeliver = async (id: number) => {
    setActionLoading(id);
    try {
      await deliverAssignment(id, deliveryNote.trim() || undefined);
      showToast("success", "Deliverables submitted for review.");
      setDeliveryFormId(null);
      setDeliveryNote("");
      await fetchAssignments(filter);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to submit deliverables";
      showToast("error", message);
    } finally {
      setActionLoading(null);
    }
  };

  // ── Loading / Error States ──────────────────────────────────────────────

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

  if (error) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-10">
        <div
          className="rounded-xl p-6 text-center text-sm"
          style={{
            background: T.roseBg,
            color: T.rose,
            border: "1px solid rgba(220,38,38,0.15)",
          }}
        >
          {error}
        </div>
      </div>
    );
  }

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 lg:py-10">
      {/* ── Toast ──────────────────────────────────────────────── */}
      {toast && (
        <div
          className="fixed top-4 right-4 z-50 px-4 py-3 rounded-xl shadow-lg text-sm font-medium max-w-sm"
          style={{
            background: toast.type === "success" ? T.emeraldBg : T.roseBg,
            color: toast.type === "success" ? T.emerald : T.rose,
            border: `1px solid ${toast.type === "success" ? "rgba(5,150,105,0.2)" : "rgba(220,38,38,0.2)"}`,
          }}
        >
          <div className="flex items-center gap-2">
            {toast.type === "success" ? (
              <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            ) : (
              <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
              </svg>
            )}
            {toast.message}
          </div>
        </div>
      )}

      {/* ── Breadcrumb + Header ────────────────────────────────── */}
      <div className="mb-6">
        <Link
          href="/ca/marketplace"
          className="inline-flex items-center gap-1.5 text-xs font-medium mb-3 transition-colors"
          style={{ color: T.accent }}
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
          </svg>
          Back to Marketplace
        </Link>
        <h1
          className="text-2xl font-bold mb-1"
          style={{ fontFamily: "var(--font-display)", color: T.textPrimary }}
        >
          My Assignments
        </h1>
        <p className="text-sm" style={{ color: T.textSecondary }}>
          {assignments.length} assignment{assignments.length !== 1 ? "s" : ""} total.
          Manage your service fulfillment work below.
        </p>
      </div>

      {/* ── Status Filter Tabs ─────────────────────────────────── */}
      <div className="flex flex-wrap gap-2 mb-6">
        {STATUS_FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => {
              setFilter(f.value);
              setLoading(true);
            }}
            className="px-3.5 py-1.5 rounded-lg text-xs font-medium transition-colors"
            style={{
              background: filter === f.value ? T.accent : T.cardBg,
              color: filter === f.value ? "#fff" : T.textSecondary,
              border: `1px solid ${filter === f.value ? T.accent : T.cardBorder}`,
            }}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* ── Assignments List ───────────────────────────────────── */}
      {assignments.length === 0 ? (
        <div
          className="rounded-xl p-12 text-center"
          style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}` }}
        >
          <svg
            className="w-12 h-12 mx-auto mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke={T.textMuted}
            strokeWidth={1}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 00.75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 00-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0112 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 01-.673-.38m0 0A2.18 2.18 0 013 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 013.413-.387m7.5 0V5.25A2.25 2.25 0 0013.5 3h-3a2.25 2.25 0 00-2.25 2.25v.894m7.5 0a48.667 48.667 0 00-7.5 0M12 12.75h.008v.008H12v-.008z"
            />
          </svg>
          <p className="text-sm font-medium mb-1" style={{ color: T.textPrimary }}>
            No assignments yet
          </p>
          <p className="text-xs mb-4" style={{ color: T.textMuted }}>
            {filter
              ? `No assignments with status "${STATUS_FILTERS.find((f) => f.value === filter)?.label || filter}".`
              : "Once you register as a partner and get matched, your assignments will appear here."}
          </p>
          {!filter && (
            <Link
              href="/ca/marketplace"
              className="inline-flex items-center gap-1.5 text-xs font-medium px-4 py-2 rounded-lg transition-colors"
              style={{ background: T.accentBg, color: T.accent }}
            >
              Go to Marketplace
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
              </svg>
            </Link>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {assignments.map((a) => {
            const s = statusStyle(a.status);
            const isActioning = actionLoading === a.id;
            const showDeliveryForm = deliveryFormId === a.id;

            return (
              <div key={a.id}>
                <div
                  className="rounded-xl p-5"
                  style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}` }}
                >
                  {/* Top row: Service name + badges */}
                  <div className="flex flex-col sm:flex-row sm:items-start gap-3 mb-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2 mb-1">
                        <h3
                          className="text-sm font-semibold"
                          style={{ color: T.textPrimary }}
                        >
                          {a.service_name}
                        </h3>
                        <span
                          className="text-[10px] font-medium px-2 py-0.5 rounded-full capitalize"
                          style={{ background: T.accentBg, color: T.accent }}
                        >
                          {a.category}
                        </span>
                        <span
                          className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
                          style={{ background: s.bg, color: s.color }}
                        >
                          {s.label}
                        </span>
                      </div>
                      <p className="text-xs" style={{ color: T.textMuted }}>
                        Assignment #{a.id} &middot; Request #{a.service_request_id}
                      </p>
                    </div>

                    {/* Fee */}
                    <div className="flex-shrink-0 text-right">
                      <div
                        className="text-lg font-bold"
                        style={{ color: T.textPrimary }}
                      >
                        Rs {formatCurrency(a.fulfillment_fee)}
                      </div>
                      <div className="text-[10px]" style={{ color: T.textMuted }}>
                        Your fee (80% share)
                      </div>
                    </div>
                  </div>

                  {/* Dates row */}
                  <div className="flex flex-wrap gap-x-5 gap-y-1 mb-3">
                    <DateItem label="Assigned" date={a.created_at} />
                    {a.accepted_at && <DateItem label="Accepted" date={a.accepted_at} />}
                    {a.started_at && <DateItem label="Started" date={a.started_at} />}
                    {a.completed_at && <DateItem label="Completed" date={a.completed_at} />}
                  </div>

                  {/* Revision note callout */}
                  {a.status === "revision_needed" && a.review_note && (
                    <div
                      className="rounded-lg p-3 mb-3 text-xs"
                      style={{
                        background: T.roseBg,
                        border: "1px solid rgba(220,38,38,0.15)",
                        color: T.rose,
                      }}
                    >
                      <div className="flex items-start gap-2">
                        <svg
                          className="w-4 h-4 flex-shrink-0 mt-0.5"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                          strokeWidth={2}
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
                          />
                        </svg>
                        <div>
                          <span className="font-semibold">Revision requested: </span>
                          {a.review_note}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Client rating (completed) */}
                  {a.status === "completed" && a.client_rating != null && (
                    <div className="flex items-center gap-2 mb-3">
                      <StarRating rating={a.client_rating} />
                      {a.client_review && (
                        <span className="text-xs italic" style={{ color: T.textSecondary }}>
                          &ldquo;{a.client_review}&rdquo;
                        </span>
                      )}
                    </div>
                  )}

                  {/* Action buttons */}
                  <div className="flex items-center gap-2 pt-1">
                    {a.status === "assigned" && (
                      <button
                        onClick={() => handleAccept(a.id)}
                        disabled={isActioning}
                        className="text-xs font-medium px-4 py-2 rounded-lg text-white transition-opacity disabled:opacity-50"
                        style={{ background: T.accent }}
                      >
                        {isActioning ? "Accepting..." : "Accept"}
                      </button>
                    )}

                    {a.status === "accepted" && (
                      <button
                        onClick={() => handleStartWork(a.id)}
                        disabled={isActioning}
                        className="text-xs font-medium px-4 py-2 rounded-lg text-white transition-opacity disabled:opacity-50"
                        style={{ background: T.blue }}
                      >
                        {isActioning ? "Starting..." : "Start Work"}
                      </button>
                    )}

                    {a.status === "in_progress" && (
                      <button
                        onClick={() => {
                          setDeliveryFormId(a.id);
                          setDeliveryNote("");
                        }}
                        className="text-xs font-medium px-4 py-2 rounded-lg text-white transition-opacity"
                        style={{ background: T.emerald }}
                      >
                        Mark as Delivered
                      </button>
                    )}

                    {(a.status === "deliverables_uploaded" || a.status === "under_review") && (
                      <span
                        className="inline-flex items-center gap-1.5 text-xs font-medium px-4 py-2 rounded-lg"
                        style={{ background: T.purpleBg, color: T.purple }}
                      >
                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Under Review
                      </span>
                    )}

                    {a.status === "revision_needed" && (
                      <button
                        onClick={() => handleStartWork(a.id)}
                        disabled={isActioning}
                        className="text-xs font-medium px-4 py-2 rounded-lg text-white transition-opacity disabled:opacity-50"
                        style={{ background: T.blue }}
                      >
                        {isActioning ? "Starting..." : "Start Work"}
                      </button>
                    )}

                    {a.status === "completed" && (
                      <span
                        className="inline-flex items-center gap-1.5 text-xs font-medium px-4 py-2 rounded-lg"
                        style={{ background: T.emeraldBg, color: T.emerald }}
                      >
                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Completed
                      </span>
                    )}

                    {a.status === "cancelled" && (
                      <span
                        className="inline-flex items-center gap-1.5 text-xs font-medium px-4 py-2 rounded-lg"
                        style={{ background: T.grayBg, color: T.gray }}
                      >
                        Cancelled
                      </span>
                    )}
                  </div>
                </div>

                {/* ── Delivery Note Inline Form ─────────────────── */}
                {showDeliveryForm && (
                  <div
                    className="rounded-b-xl p-4 -mt-1"
                    style={{
                      background: T.emeraldBg,
                      border: `1px solid rgba(5,150,105,0.15)`,
                      borderTop: "none",
                    }}
                  >
                    <label
                      className="block text-xs font-medium mb-1.5"
                      style={{ color: T.textSecondary }}
                    >
                      Delivery Note (optional)
                    </label>
                    <textarea
                      value={deliveryNote}
                      onChange={(e) => setDeliveryNote(e.target.value)}
                      placeholder="Describe what you have delivered, any notes for the client..."
                      rows={3}
                      className="w-full px-3 py-2.5 rounded-lg text-sm resize-none"
                      style={{
                        background: T.cardBg,
                        border: `1px solid ${T.cardBorder}`,
                        color: T.textPrimary,
                        outline: "none",
                      }}
                      onFocus={(e) => {
                        e.currentTarget.style.borderColor = T.emerald;
                      }}
                      onBlur={(e) => {
                        e.currentTarget.style.borderColor = T.cardBorder;
                      }}
                      autoFocus
                    />
                    <div className="flex justify-end gap-2 mt-3">
                      <button
                        onClick={() => {
                          setDeliveryFormId(null);
                          setDeliveryNote("");
                        }}
                        className="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                        style={{
                          color: T.textSecondary,
                          border: `1px solid ${T.cardBorder}`,
                          background: T.cardBg,
                        }}
                      >
                        Cancel
                      </button>
                      <button
                        onClick={() => handleDeliver(a.id)}
                        disabled={isActioning}
                        className="px-4 py-1.5 rounded-lg text-xs font-medium text-white transition-opacity disabled:opacity-50"
                        style={{ background: T.emerald }}
                      >
                        {isActioning ? "Submitting..." : "Submit Deliverables"}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function DateItem({ label, date }: { label: string; date: string | null }) {
  const formatted = formatDate(date);
  if (!formatted) return null;
  return (
    <div className="text-[11px]" style={{ color: T.textMuted }}>
      <span className="font-medium" style={{ color: T.textSecondary }}>
        {label}:
      </span>{" "}
      {formatted}
    </div>
  );
}
