"use client";

import { useEffect, useState } from "react";
import { getReviewQueue, claimDocReview, verifyDocument } from "@/lib/api";
import { useToast } from "@/components/toast";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type Decision = "pending" | "approved" | "rejected" | "needs_reupload";
type FilterTab = Decision | "all";

interface ReviewItem {
  id: number;
  document_id: number;
  filename: string;
  doc_type: string;
  company_id: number;
  company_name: string;
  ai_confidence: number;
  ai_flags: string[];
  decision: Decision;
  reviewer_id: number | null;
  reviewer_name: string | null;
  review_notes: string | null;
  rejection_reason: string | null;
  created_at: string;
  reviewed_at: string | null;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const FILTER_TABS: { key: FilterTab; label: string }[] = [
  { key: "pending", label: "Pending" },
  { key: "approved", label: "Approved" },
  { key: "rejected", label: "Rejected" },
  { key: "all", label: "All" },
];

const DECISION_BADGES: Record<
  Decision,
  { color: string; bg: string; label: string }
> = {
  pending: {
    color: "var(--color-warning)",
    bg: "bg-amber-500/15",
    label: "Pending",
  },
  approved: {
    color: "var(--color-success)",
    bg: "bg-emerald-500/15",
    label: "Approved",
  },
  rejected: {
    color: "var(--color-error)",
    bg: "bg-red-500/15",
    label: "Rejected",
  },
  needs_reupload: {
    color: "var(--color-warning)",
    bg: "bg-orange-500/15",
    label: "Reupload",
  },
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function timeAgo(dateStr: string): string {
  const now = new Date();
  const date = new Date(dateStr);
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function confidenceColor(score: number): string {
  if (score >= 90) return "var(--color-success)";
  if (score >= 70) return "var(--color-warning)";
  return "var(--color-error)";
}

function confidenceBg(score: number): string {
  if (score >= 90) return "bg-emerald-500/15";
  if (score >= 70) return "bg-amber-500/15";
  return "bg-red-500/15";
}

function isToday(dateStr: string | null): boolean {
  if (!dateStr) return false;
  const d = new Date(dateStr);
  const now = new Date();
  return (
    d.getDate() === now.getDate() &&
    d.getMonth() === now.getMonth() &&
    d.getFullYear() === now.getFullYear()
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function DocumentReviewQueuePage() {
  const { toast } = useToast();
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<FilterTab>("pending");
  const [claimingId, setClaimingId] = useState<number | null>(null);
  const [actionTarget, setActionTarget] = useState<{
    item: ReviewItem;
    action: "approved" | "rejected" | "needs_reupload";
  } | null>(null);
  const [reviewNotes, setReviewNotes] = useState("");
  const [rejectionReason, setRejectionReason] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // -- Fetch --

  const fetchQueue = async () => {
    try {
      const params: any = {};
      if (activeTab !== "all") params.decision = activeTab;
      const data = await getReviewQueue(params);
      setItems(Array.isArray(data) ? data : data?.items ?? data?.reviews ?? []);
    } catch (e: any) {
      toast(e.message || "Failed to load review queue", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchQueue();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);

  // -- Actions --

  const handleClaim = async (item: ReviewItem) => {
    setClaimingId(item.document_id);
    try {
      await claimDocReview(item.document_id);
      toast("Review claimed", "success");
      await fetchQueue();
    } catch (e: any) {
      toast(e.message || "Claim failed", "error");
    } finally {
      setClaimingId(null);
    }
  };

  const openAction = (
    item: ReviewItem,
    action: "approved" | "rejected" | "needs_reupload",
  ) => {
    setActionTarget({ item, action });
    setReviewNotes("");
    setRejectionReason("");
  };

  const closeAction = () => {
    setActionTarget(null);
    setReviewNotes("");
    setRejectionReason("");
  };

  const handleSubmitVerification = async () => {
    if (!actionTarget) return;
    setSubmitting(true);
    try {
      await verifyDocument(actionTarget.item.document_id, {
        decision: actionTarget.action,
        review_notes: reviewNotes || undefined,
        rejection_reason:
          actionTarget.action !== "approved"
            ? rejectionReason || undefined
            : undefined,
      });
      toast("Document verified", "success");
      closeAction();
      await fetchQueue();
    } catch (e: any) {
      toast(e.message || "Verification failed", "error");
    } finally {
      setSubmitting(false);
    }
  };

  // -- Derived stats --

  const pendingCount = items.filter((i) => i.decision === "pending").length;
  const avgConfidence =
    items.length > 0
      ? Math.round(items.reduce((sum, i) => sum + (i.ai_confidence ?? 0), 0) / items.length)
      : 0;
  const reviewedToday = items.filter(
    (i) => i.decision !== "pending" && isToday(i.reviewed_at),
  ).length;

  // -- Render --

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 rounded w-64" style={{ background: "var(--color-bg-card)" }} />
          <div className="grid grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 rounded-lg" style={{ background: "var(--color-bg-card)" }} />
            ))}
          </div>
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 rounded-lg" style={{ background: "var(--color-bg-card)" }} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      {/* -- Header + Filter Tabs -- */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1
            className="text-2xl font-bold"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Document Review Queue
          </h1>
          <p className="text-sm mt-1" style={{ color: "var(--color-text-secondary)" }}>
            Verify uploaded documents with AI-assisted confidence scoring
          </p>
        </div>

        <div className="flex items-center gap-1 bg-white/5 rounded-lg p-1">
          {FILTER_TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                activeTab === tab.key
                  ? "bg-purple-500/20"
                  : "hover:bg-white/5"
              }`}
              style={{ color: activeTab === tab.key ? "var(--color-accent-purple-light)" : "var(--color-text-secondary)" }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* -- Stats Row -- */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div className="glass-card p-4">
          <p className="text-xs uppercase tracking-wider" style={{ color: "var(--color-text-secondary)" }}>
            Total Pending
          </p>
          <p className="text-2xl font-bold mt-1" style={{ color: "var(--color-warning)" }}>
            {pendingCount}
          </p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs uppercase tracking-wider" style={{ color: "var(--color-text-secondary)" }}>
            Avg AI Confidence
          </p>
          <p
            className="text-2xl font-bold mt-1"
            style={{ color: confidenceColor(avgConfidence) }}
          >
            {avgConfidence}%
          </p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs uppercase tracking-wider" style={{ color: "var(--color-text-secondary)" }}>
            Reviewed Today
          </p>
          <p className="text-2xl font-bold text-cyan-400 mt-1">
            {reviewedToday}
          </p>
        </div>
      </div>

      {/* -- Review Cards -- */}
      {items.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <svg
            className="w-10 h-10 mx-auto mb-3"
            style={{ color: "var(--color-text-muted)" }}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M10.125 2.25h-4.5c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125v-9M10.125 2.25h.375a9 9 0 019 9v.375M10.125 2.25A3.375 3.375 0 0113.5 5.625v1.5c0 .621.504 1.125 1.125 1.125h1.5a3.375 3.375 0 013.375 3.375M9 15l2.25 2.25L15 12"
            />
          </svg>
          <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
            No documents matching this filter.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => {
            const badge = DECISION_BADGES[item.decision] ?? DECISION_BADGES.pending;
            const isExpanded =
              actionTarget?.item.id === item.id;

            return (
              <div key={item.id} className="glass-card overflow-hidden">
                {/* Card body */}
                <div className="p-4">
                  <div className="flex flex-col sm:flex-row sm:items-start gap-4">
                    {/* Left: Document info */}
                    <div className="flex-1 min-w-0 space-y-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-sm font-semibold truncate" style={{ color: "var(--color-text-primary)" }}>
                          {item.filename}
                        </span>
                        <span
                          className={`text-[10px] px-2 py-0.5 rounded font-medium ${badge.bg}`}
                          style={{ color: badge.color }}
                        >
                          {badge.label}
                        </span>
                      </div>

                      <div className="flex items-center gap-3 text-xs flex-wrap" style={{ color: "var(--color-text-muted)" }}>
                        <span style={{ color: "var(--color-text-secondary)" }}>
                          {item.company_name}
                        </span>
                        <span style={{ color: "var(--color-text-muted)" }}>|</span>
                        <span>
                          {item.doc_type?.replace(/_/g, " ").toUpperCase()}
                        </span>
                        <span style={{ color: "var(--color-text-muted)" }}>|</span>
                        <span>{timeAgo(item.created_at)}</span>
                      </div>

                      {/* AI Flags */}
                      {item.ai_flags && item.ai_flags.length > 0 && (
                        <div className="flex items-center gap-1.5 flex-wrap">
                          {item.ai_flags.map((flag, idx) => (
                            <span
                              key={idx}
                              className="text-[10px] px-1.5 py-0.5 rounded bg-red-500/15 border border-red-500/20"
                              style={{ color: "var(--color-error)" }}
                            >
                              {flag}
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Reviewer */}
                      <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                        Reviewer:{" "}
                        {item.reviewer_name ? (
                          <span style={{ color: "var(--color-text-primary)" }}>
                            {item.reviewer_name}
                          </span>
                        ) : (
                          <span style={{ color: "var(--color-text-muted)", fontStyle: "italic" }}>
                            Unassigned
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Right: Confidence + Actions */}
                    <div className="flex flex-col items-end gap-3 shrink-0">
                      {/* Confidence score */}
                      <div
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg ${confidenceBg(item.ai_confidence)}`}
                      >
                        <span className="text-[10px] uppercase tracking-wider" style={{ color: "var(--color-text-secondary)" }}>
                          AI
                        </span>
                        <span
                          className="text-lg font-bold tabular-nums"
                          style={{ color: confidenceColor(item.ai_confidence) }}
                        >
                          {item.ai_confidence ?? "--"}
                        </span>
                      </div>

                      {/* Action buttons */}
                      <div className="flex items-center gap-1.5 flex-wrap justify-end">
                        {!item.reviewer_id && item.decision === "pending" && (
                          <button
                            onClick={() => handleClaim(item)}
                            disabled={claimingId === item.document_id}
                            className="text-xs px-2.5 py-1 rounded bg-purple-500/15 hover:bg-purple-500/25 transition-colors disabled:opacity-50"
                            style={{ color: "var(--color-accent-purple-light)" }}
                          >
                            {claimingId === item.document_id
                              ? "Claiming..."
                              : "Claim"}
                          </button>
                        )}
                        {item.decision === "pending" && (
                          <>
                            <button
                              onClick={() => openAction(item, "approved")}
                              className="text-xs px-2.5 py-1 rounded bg-emerald-500/15 hover:bg-emerald-500/25 transition-colors"
                              style={{ color: "var(--color-success)" }}
                            >
                              Approve
                            </button>
                            <button
                              onClick={() => openAction(item, "rejected")}
                              className="text-xs px-2.5 py-1 rounded bg-red-500/15 hover:bg-red-500/25 transition-colors"
                              style={{ color: "var(--color-error)" }}
                            >
                              Reject
                            </button>
                            <button
                              onClick={() =>
                                openAction(item, "needs_reupload")
                              }
                              className="text-xs px-2.5 py-1 rounded bg-orange-500/15 text-orange-400 hover:bg-orange-500/25 transition-colors"
                            >
                              Request Reupload
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* -- Inline Expansion for Approve / Reject / Reupload -- */}
                {isExpanded && actionTarget && (
                  <div className="bg-white/[0.02] px-4 py-4 space-y-3" style={{ borderTop: "1px solid var(--color-border)" }}>
                    <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-primary)" }}>
                      {actionTarget.action === "approved"
                        ? "Approve Document"
                        : actionTarget.action === "rejected"
                          ? "Reject Document"
                          : "Request Reupload"}
                    </p>

                    {/* Review notes */}
                    <div>
                      <label className="block text-xs mb-1" style={{ color: "var(--color-text-secondary)" }}>
                        Review Notes
                      </label>
                      <textarea
                        value={reviewNotes}
                        onChange={(e) => setReviewNotes(e.target.value)}
                        rows={3}
                        placeholder="Add any notes about this review..."
                        className="w-full bg-white/5 rounded-lg px-3 py-2 text-sm placeholder-gray-600 focus:outline-none focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/30 transition-colors resize-none"
                        style={{ border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                      />
                    </div>

                    {/* Rejection reason (only for reject / reupload) */}
                    {actionTarget.action !== "approved" && (
                      <div>
                        <label className="block text-xs mb-1" style={{ color: "var(--color-text-secondary)" }}>
                          {actionTarget.action === "rejected"
                            ? "Rejection Reason"
                            : "Reupload Reason"}
                        </label>
                        <input
                          type="text"
                          value={rejectionReason}
                          onChange={(e) => setRejectionReason(e.target.value)}
                          placeholder={
                            actionTarget.action === "rejected"
                              ? "Why is this document being rejected?"
                              : "Why does the client need to reupload?"
                          }
                          className="w-full bg-white/5 rounded-lg px-3 py-2 text-sm placeholder-gray-600 focus:outline-none focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/30 transition-colors"
                          style={{ border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                        />
                      </div>
                    )}

                    {/* Submit / Cancel */}
                    <div className="flex items-center gap-2 pt-1">
                      <button
                        onClick={handleSubmitVerification}
                        disabled={submitting}
                        className={`text-xs px-4 py-1.5 rounded font-medium transition-colors disabled:opacity-50 ${
                          actionTarget.action === "approved"
                            ? "bg-emerald-500/20 hover:bg-emerald-500/30"
                            : actionTarget.action === "rejected"
                              ? "bg-red-500/20 hover:bg-red-500/30"
                              : "bg-orange-500/20 text-orange-400 hover:bg-orange-500/30"
                        }`}
                        style={actionTarget.action === "approved"
                          ? { color: "var(--color-success)" }
                          : actionTarget.action === "rejected"
                            ? { color: "var(--color-error)" }
                            : undefined}
                      >
                        {submitting
                          ? "Submitting..."
                          : actionTarget.action === "approved"
                            ? "Confirm Approval"
                            : actionTarget.action === "rejected"
                              ? "Confirm Rejection"
                              : "Confirm Reupload Request"}
                      </button>
                      <button
                        onClick={closeAction}
                        className="text-xs px-3 py-1.5 rounded bg-white/5 hover:bg-white/10 transition-colors"
                        style={{ color: "var(--color-text-secondary)" }}
                      >
                        Cancel
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
