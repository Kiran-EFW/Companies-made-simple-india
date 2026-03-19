"use client";

import { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { getCaAllTasks } from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Task {
  id: number;
  title: string;
  task_type: string;
  due_date: string;
  status: string;
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

function statusColor(status: string) {
  switch (status) {
    case "overdue": return T.rose;
    case "due_soon": return T.amber;
    case "upcoming": return T.blue;
    case "completed": return T.emerald;
    default: return T.accent;
  }
}

function statusBg(status: string) {
  switch (status) {
    case "overdue": return T.roseBg;
    case "due_soon": return T.amberBg;
    case "upcoming": return T.blueBg;
    case "completed": return T.emeraldBg;
    default: return T.accentBg;
  }
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CaCalendarPage() {
  const { user, loading: authLoading } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Current FY: Apr-Mar
  const today = new Date();
  const currentFyStart = today.getMonth() >= 3 ? today.getFullYear() : today.getFullYear() - 1;
  const [fyYear, setFyYear] = useState(currentFyStart);

  useEffect(() => {
    if (authLoading || !user) return;

    (async () => {
      try {
        const data = await getCaAllTasks();
        setTasks(Array.isArray(data) ? data : []);
      } catch (err: any) {
        setError(err.message || "Failed to load tasks");
      } finally {
        setLoading(false);
      }
    })();
  }, [user, authLoading]);

  // Group tasks by month (Apr-Mar of selected FY)
  const monthlyTasks = useMemo(() => {
    const fyStart = new Date(fyYear, 3, 1); // Apr 1
    const fyEnd = new Date(fyYear + 1, 2, 31); // Mar 31

    const months: { month: number; year: number; label: string; tasks: Task[] }[] = [];
    for (let i = 0; i < 12; i++) {
      const m = ((3 + i) % 12); // Apr=3, May=4, ..., Mar=2
      const y = m >= 3 ? fyYear : fyYear + 1;
      months.push({
        month: m,
        year: y,
        label: `${MONTHS[m]} ${y}`,
        tasks: [],
      });
    }

    for (const task of tasks) {
      if (!task.due_date) continue;
      const d = new Date(task.due_date);
      if (d < fyStart || d > fyEnd) continue;
      const idx = months.findIndex((mo) => mo.month === d.getMonth() && mo.year === d.getFullYear());
      if (idx >= 0) {
        months[idx].tasks.push(task);
      }
    }

    // Sort tasks within each month by due date
    for (const mo of months) {
      mo.tasks.sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime());
    }

    return months;
  }, [tasks, fyYear]);

  const todayStr = today.toISOString().split("T")[0];
  const currentMonthIdx = monthlyTasks.findIndex(
    (mo) => mo.month === today.getMonth() && mo.year === today.getFullYear()
  );

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

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 lg:py-10">
      {/* ── Header ──────────────────────────────────────────── */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold mb-1" style={{ fontFamily: "var(--font-display)", color: T.textPrimary }}>
            Compliance Calendar
          </h1>
          <p className="text-sm" style={{ color: T.textSecondary }}>
            FY {fyYear}-{fyYear + 1} deadline overview across all companies.
          </p>
        </div>

        {/* FY selector */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setFyYear(fyYear - 1)}
            className="p-1.5 rounded-lg transition-colors"
            style={{ color: T.textMuted, border: `1px solid ${T.cardBorder}` }}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
            </svg>
          </button>
          <span className="text-sm font-semibold px-2" style={{ color: T.textPrimary }}>
            FY {fyYear}-{String(fyYear + 1).slice(-2)}
          </span>
          <button
            onClick={() => setFyYear(fyYear + 1)}
            className="p-1.5 rounded-lg transition-colors"
            style={{ color: T.textMuted, border: `1px solid ${T.cardBorder}` }}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
            </svg>
          </button>
        </div>
      </div>

      {/* ── Timeline ────────────────────────────────────────── */}
      <div className="space-y-1">
        {monthlyTasks.map((mo, idx) => {
          const isCurrent = idx === currentMonthIdx;
          const hasOverdue = mo.tasks.some((t) => t.status === "overdue");
          const taskCount = mo.tasks.length;

          return (
            <div key={mo.label}>
              {/* Month header */}
              <div
                className="flex items-center gap-3 px-4 py-3 rounded-t-xl"
                style={{
                  background: isCurrent ? T.accentBg : taskCount > 0 ? T.cardBg : "transparent",
                  borderLeft: isCurrent ? `3px solid ${T.accent}` : hasOverdue ? `3px solid ${T.rose}` : `3px solid ${T.cardBorder}`,
                }}
              >
                <span
                  className="text-sm font-semibold w-20"
                  style={{ color: isCurrent ? T.accent : T.textPrimary }}
                >
                  {mo.label}
                </span>

                {taskCount > 0 && (
                  <div className="flex items-center gap-2">
                    <span
                      className="text-[11px] font-medium px-2 py-0.5 rounded-full"
                      style={{
                        background: hasOverdue ? T.roseBg : T.accentBg,
                        color: hasOverdue ? T.rose : T.accent,
                      }}
                    >
                      {taskCount} {taskCount === 1 ? "task" : "tasks"}
                    </span>
                  </div>
                )}

                {isCurrent && (
                  <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded" style={{ background: T.accent, color: "#fff" }}>
                    Current
                  </span>
                )}
              </div>

              {/* Task list for this month */}
              {mo.tasks.length > 0 && (
                <div
                  className="rounded-b-xl mb-3 overflow-hidden"
                  style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}`, borderTop: "none" }}
                >
                  {mo.tasks.map((task, tIdx) => {
                    const dueDay = new Date(task.due_date).getDate();
                    return (
                      <div
                        key={task.id}
                        className="flex items-center gap-3 px-4 py-2.5"
                        style={{
                          borderBottom: tIdx < mo.tasks.length - 1 ? `1px solid ${T.cardBorder}` : undefined,
                        }}
                      >
                        {/* Day */}
                        <span
                          className="text-xs font-bold w-6 text-center"
                          style={{ color: statusColor(task.status) }}
                        >
                          {dueDay}
                        </span>

                        {/* Dot */}
                        <div
                          className="w-2 h-2 rounded-full flex-shrink-0"
                          style={{ background: statusColor(task.status) }}
                        />

                        {/* Info */}
                        <div className="flex-1 min-w-0">
                          <span className="text-sm font-medium truncate block" style={{ color: T.textPrimary }}>
                            {task.title}
                          </span>
                          <Link
                            href={`/ca/companies/${task.company_id}`}
                            className="text-[11px] hover:underline"
                            style={{ color: T.accent }}
                          >
                            {task.company_name}
                          </Link>
                        </div>

                        {/* Status badge */}
                        <span
                          className="text-[10px] font-semibold px-2 py-0.5 rounded-full capitalize flex-shrink-0"
                          style={{ background: statusBg(task.status), color: statusColor(task.status) }}
                        >
                          {task.status.replace(/_/g, " ")}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Empty month — just a thin line */}
              {mo.tasks.length === 0 && <div className="mb-1" />}
            </div>
          );
        })}
      </div>
    </div>
  );
}
