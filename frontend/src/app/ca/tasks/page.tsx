"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { getCaAllTasks, markFilingComplete } from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Task {
  id: number;
  title: string;
  task_type: string;
  due_date: string;
  status: string;
  description: string;
  filing_reference?: string;
  company_id: number;
  company_name: string;
}

// ---------------------------------------------------------------------------
// Theme
// ---------------------------------------------------------------------------
const T = {
  accent: "#0d9488",
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

const STATUS_FILTERS = [
  { value: "", label: "All Tasks" },
  { value: "overdue", label: "Overdue" },
  { value: "due_soon", label: "Due Soon" },
  { value: "upcoming", label: "Upcoming" },
  { value: "completed", label: "Completed" },
];

function statusStyle(status: string) {
  switch (status) {
    case "overdue": return { bg: T.roseBg, color: T.rose };
    case "due_soon": return { bg: T.amberBg, color: T.amber };
    case "upcoming": return { bg: T.blueBg, color: T.blue };
    case "completed": return { bg: T.emeraldBg, color: T.emerald };
    default: return { bg: T.accentBg, color: T.accent };
  }
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

function daysUntil(d: string) {
  const diff = Math.ceil((new Date(d).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
  if (diff < 0) return `${Math.abs(diff)}d overdue`;
  if (diff === 0) return "Due today";
  if (diff === 1) return "Due tomorrow";
  return `${diff}d left`;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CaTasksPage() {
  const { user, loading: authLoading } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("");

  // Filing modal
  const [filingModal, setFilingModal] = useState<Task | null>(null);
  const [filingRef, setFilingRef] = useState("");
  const [filingLoading, setFilingLoading] = useState(false);
  const [filingError, setFilingError] = useState("");

  const fetchTasks = async (statusFilter?: string) => {
    try {
      const data = await getCaAllTasks(statusFilter || undefined);
      setTasks(Array.isArray(data) ? data : []);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to load tasks";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (authLoading || !user) return;
    fetchTasks(filter);
  }, [user, authLoading, filter]);

  const handleMarkComplete = async () => {
    if (!filingModal || !filingRef.trim()) return;
    setFilingLoading(true);
    setFilingError("");
    try {
      await markFilingComplete(filingModal.company_id, filingModal.id, filingRef.trim());
      await fetchTasks(filter);
      setFilingModal(null);
      setFilingRef("");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to mark filing complete";
      setFilingError(message);
    } finally {
      setFilingLoading(false);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: T.accent }} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-10">
        <div className="rounded-xl p-6 text-center text-sm" style={{ background: T.roseBg, color: T.rose, border: `1px solid rgba(220,38,38,0.15)` }}>
          {error}
        </div>
      </div>
    );
  }

  const overdueCount = tasks.filter((t) => t.status === "overdue").length;
  const dueSoonCount = tasks.filter((t) => t.status === "due_soon").length;

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 lg:py-10">
      {/* ── Header ──────────────────────────────────────────── */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-1" style={{ fontFamily: "var(--font-display)", color: T.textPrimary }}>
          All Compliance Tasks
        </h1>
        <p className="text-sm" style={{ color: T.textSecondary }}>
          {tasks.length} tasks across all assigned companies.
          {overdueCount > 0 && (
            <span style={{ color: T.rose, fontWeight: 600 }}> {overdueCount} overdue.</span>
          )}
          {dueSoonCount > 0 && (
            <span style={{ color: T.amber, fontWeight: 600 }}> {dueSoonCount} due soon.</span>
          )}
        </p>
      </div>

      {/* ── Filters ─────────────────────────────────────────── */}
      <div className="flex flex-wrap gap-2 mb-6">
        {STATUS_FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => { setFilter(f.value); setLoading(true); }}
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

      {/* ── Task List ───────────────────────────────────────── */}
      {tasks.length === 0 ? (
        <div className="rounded-xl p-12 text-center" style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}` }}>
          <p className="text-sm" style={{ color: T.textMuted }}>
            No tasks found{filter ? ` with status "${filter}"` : ""}.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {tasks.map((task) => {
            const s = statusStyle(task.status);
            return (
              <div
                key={task.id}
                className="rounded-xl p-4 flex items-center gap-4"
                style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}` }}
              >
                {/* Status indicator */}
                <div
                  className="w-2 h-2 rounded-full flex-shrink-0"
                  style={{ background: s.color }}
                />

                {/* Task info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-sm font-semibold truncate" style={{ color: T.textPrimary }}>
                      {task.title}
                    </span>
                    <span
                      className="text-[10px] font-semibold px-2 py-0.5 rounded-full capitalize flex-shrink-0"
                      style={{ background: s.bg, color: s.color }}
                    >
                      {task.status.replace(/_/g, " ")}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-xs" style={{ color: T.textMuted }}>
                    <Link
                      href={`/ca/companies/${task.company_id}`}
                      className="font-medium hover:underline"
                      style={{ color: T.accent }}
                    >
                      {task.company_name}
                    </Link>
                    <span>{task.task_type?.replace(/_/g, " ")}</span>
                    {task.filing_reference && (
                      <span className="font-mono">Ref: {task.filing_reference}</span>
                    )}
                  </div>
                </div>

                {/* Due date */}
                <div className="text-right flex-shrink-0">
                  {task.due_date && (
                    <>
                      <div className="text-xs font-medium" style={{ color: T.textSecondary }}>
                        {formatDate(task.due_date)}
                      </div>
                      <div
                        className="text-[11px] font-semibold"
                        style={{ color: task.status === "overdue" ? T.rose : task.status === "due_soon" ? T.amber : T.textMuted }}
                      >
                        {daysUntil(task.due_date)}
                      </div>
                    </>
                  )}
                </div>

                {/* Action */}
                <div className="flex-shrink-0">
                  {task.status !== "completed" ? (
                    <button
                      onClick={() => { setFilingModal(task); setFilingRef(""); }}
                      className="text-xs font-medium px-3 py-1.5 rounded-lg transition-colors"
                      style={{ background: T.accentBg, color: T.accent }}
                      onMouseEnter={(e) => { e.currentTarget.style.background = T.accent; e.currentTarget.style.color = "#fff"; }}
                      onMouseLeave={(e) => { e.currentTarget.style.background = T.accentBg; e.currentTarget.style.color = T.accent; }}
                    >
                      Complete
                    </button>
                  ) : (
                    <span className="text-xs font-medium px-3 py-1.5" style={{ color: T.emerald }}>
                      Done
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ── Filing Modal ────────────────────────────────────── */}
      {filingModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center px-4"
          style={{ background: "rgba(0,0,0,0.4)" }}
          role="dialog"
          aria-modal="true"
          aria-label="Mark filing complete"
          onClick={() => setFilingModal(null)}
          onKeyDown={(e) => { if (e.key === "Escape") setFilingModal(null); }}
        >
          <div
            className="rounded-xl p-6 w-full max-w-md"
            style={{ background: T.cardBg }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-lg font-semibold mb-1" style={{ color: T.textPrimary }}>
              Mark Filing Complete
            </h3>
            <p className="text-sm mb-1" style={{ color: T.textSecondary }}>
              {filingModal.title}
            </p>
            <p className="text-xs mb-5" style={{ color: T.textMuted }}>
              {filingModal.company_name}
            </p>

            {filingError && (
              <div className="p-3 rounded-lg mb-4 text-xs font-medium" style={{ background: T.roseBg, color: T.rose, border: `1px solid rgba(220,38,38,0.15)` }}>
                {filingError}
              </div>
            )}

            <label className="block text-sm font-medium mb-1.5" style={{ color: T.textSecondary }}>
              Filing Reference Number
            </label>
            <input
              type="text"
              value={filingRef}
              onChange={(e) => { setFilingRef(e.target.value); setFilingError(""); }}
              placeholder="e.g. ARN-12345678"
              className="w-full px-3 py-2.5 rounded-lg text-sm mb-5"
              style={{ background: T.pageBg, border: `1px solid ${T.cardBorder}`, color: T.textPrimary, outline: "none" }}
              onFocus={(e) => { e.currentTarget.style.borderColor = T.accent; }}
              onBlur={(e) => { e.currentTarget.style.borderColor = T.cardBorder; }}
              autoFocus
            />

            <div className="flex justify-end gap-3">
              <button
                onClick={() => setFilingModal(null)}
                className="px-4 py-2 rounded-lg text-sm font-medium"
                style={{ color: T.textSecondary, border: `1px solid ${T.cardBorder}` }}
              >
                Cancel
              </button>
              <button
                onClick={handleMarkComplete}
                disabled={!filingRef.trim() || filingLoading}
                className="px-4 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-50"
                style={{ background: T.accent }}
              >
                {filingLoading ? "Submitting..." : "Confirm"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
