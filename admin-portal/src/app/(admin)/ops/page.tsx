"use client";

import { useEffect, useState } from "react";
import { getMyQueue, updateFilingTaskStatus, claimFilingTask } from "@/lib/api";
import Link from "next/link";
import { useToast } from "@/components/toast";

const STATUS_COLORS: Record<string, string> = {
  assigned: "var(--color-info)",
  in_progress: "var(--color-warning)",
  waiting_on_client: "var(--color-warning)",
  waiting_on_government: "var(--color-accent-purple-light)",
  under_review: "var(--color-info)",
  blocked: "var(--color-error)",
  completed: "var(--color-success)",
};

const PRIORITY_BADGES: Record<string, { bg: string; border: string; text: string }> = {
  urgent: { bg: "bg-red-500/15", border: "border-red-500/30", text: "var(--color-error)" },
  high: { bg: "bg-amber-500/15", border: "border-amber-500/30", text: "var(--color-warning)" },
  normal: { bg: "bg-gray-500/15", border: "border-gray-500/30", text: "var(--color-text-secondary)" },
  low: { bg: "bg-gray-500/10", border: "border-gray-500/20", text: "var(--color-text-muted)" },
};

function timeUntil(dateStr: string): string {
  const now = new Date();
  const date = new Date(dateStr);
  const diff = date.getTime() - now.getTime();
  if (diff < 0) {
    const hours = Math.abs(Math.floor(diff / (1000 * 60 * 60)));
    return hours < 24 ? `${hours}h overdue` : `${Math.floor(hours / 24)}d overdue`;
  }
  const hours = Math.floor(diff / (1000 * 60 * 60));
  if (hours < 24) return `${hours}h left`;
  return `${Math.floor(hours / 24)}d left`;
}

export default function MyQueuePage() {
  const { toast } = useToast();
  const [queue, setQueue] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchQueue = async () => {
    try {
      const data = await getMyQueue();
      setQueue(data);
    } catch (e: any) {
      toast(e.message || "Something went wrong", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchQueue(); }, []);

  const handleStatusUpdate = async (taskId: number, newStatus: string) => {
    try {
      await updateFilingTaskStatus(taskId, { status: newStatus });
      toast("Task status updated", "success");
      fetchQueue();
    } catch (e: any) {
      toast(e.message || "Something went wrong", "error");
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 rounded w-48" style={{ background: "var(--color-bg-card)" }} />
          <div className="grid grid-cols-4 gap-4">
            {[1, 2, 3, 4].map(i => <div key={i} className="h-24 rounded-lg" style={{ background: "var(--color-bg-card)" }} />)}
          </div>
        </div>
      </div>
    );
  }

  const stats = queue?.stats || {};
  const tasks = queue?.filing_tasks || [];
  const overdueTasks = tasks.filter((t: any) => t.due_date && new Date(t.due_date) < new Date());

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold" style={{ fontFamily: "var(--font-display)" }}>My Queue</h1>
        <p className="text-sm mt-1" style={{ color: "var(--color-text-secondary)" }}>Your assigned tasks and pending items</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-card p-4">
          <p className="text-xs uppercase tracking-wider" style={{ color: "var(--color-text-secondary)" }}>In Progress</p>
          <p className="text-2xl font-bold mt-1" style={{ color: "var(--color-warning)" }}>{stats.in_progress || 0}</p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs uppercase tracking-wider" style={{ color: "var(--color-text-secondary)" }}>Assigned</p>
          <p className="text-2xl font-bold mt-1" style={{ color: "var(--color-info)" }}>{stats.assigned || 0}</p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs uppercase tracking-wider" style={{ color: "var(--color-text-secondary)" }}>Doc Reviews</p>
          <p className="text-2xl font-bold text-cyan-400 mt-1">{queue?.review_items_count || 0}</p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs uppercase tracking-wider" style={{ color: "var(--color-text-secondary)" }}>Escalations</p>
          <p className="text-2xl font-bold mt-1" style={{ color: "var(--color-error)" }}>{queue?.escalations_count || 0}</p>
        </div>
      </div>

      {/* Overdue Alert */}
      {overdueTasks.length > 0 && (
        <div className="rounded-lg p-4" style={{ background: "var(--color-error-light)", border: "1px solid rgba(239, 68, 68, 0.3)" }}>
          <p className="font-medium text-sm" style={{ color: "var(--color-error)" }}>
            {overdueTasks.length} overdue task{overdueTasks.length > 1 ? "s" : ""} require immediate attention
          </p>
        </div>
      )}

      {/* Task List */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-primary)" }}>Active Tasks ({tasks.length})</h2>
        {tasks.length === 0 ? (
          <div className="glass-card p-8 text-center" style={{ color: "var(--color-text-muted)" }}>
            <p>No tasks in your queue. Check the <Link href="/ops/tasks" className="hover:underline" style={{ color: "var(--color-accent-purple-light)" }}>task board</Link> for unassigned work.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {tasks.map((task: any) => {
              const isOverdue = task.due_date && new Date(task.due_date) < new Date();
              const priorityBadge = PRIORITY_BADGES[task.priority] || PRIORITY_BADGES.normal;
              return (
                <div key={task.id} className={`glass-card p-4 ${isOverdue ? "border-red-500/30" : ""}`}>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-sm font-medium" style={{ color: "var(--color-text-primary)" }}>{task.title}</span>
                        <span className={`text-[10px] px-1.5 py-0.5 rounded border ${priorityBadge.bg} ${priorityBadge.border}`} style={{ color: priorityBadge.text }}>
                          {task.priority?.toUpperCase()}
                        </span>
                        <span className="text-xs" style={{ color: STATUS_COLORS[task.status] || "var(--color-text-secondary)" }}>
                          {task.status?.replace(/_/g, " ")}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 mt-1 text-xs" style={{ color: "var(--color-text-muted)" }}>
                        {task.company_name && <span>{task.company_name}</span>}
                        <span>{task.task_type?.replace(/_/g, " ")}</span>
                        {task.due_date && (
                          <span style={{ color: isOverdue ? "var(--color-error)" : "var(--color-text-secondary)" }}>
                            {timeUntil(task.due_date)}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5 shrink-0">
                      {task.status === "assigned" && (
                        <button
                          onClick={() => handleStatusUpdate(task.id, "in_progress")}
                          className="text-xs px-2.5 py-1 rounded bg-amber-500/15 hover:bg-amber-500/25 transition-colors"
                          style={{ color: "var(--color-warning)" }}
                        >
                          Start
                        </button>
                      )}
                      {task.status === "in_progress" && (
                        <button
                          onClick={() => handleStatusUpdate(task.id, "completed")}
                          className="text-xs px-2.5 py-1 rounded bg-emerald-500/15 hover:bg-emerald-500/25 transition-colors"
                          style={{ color: "var(--color-success)" }}
                        >
                          Complete
                        </button>
                      )}
                      <Link
                        href={`/ops/tasks?task=${task.id}`}
                        className="text-xs px-2.5 py-1 rounded bg-white/5 hover:bg-white/10 transition-colors"
                        style={{ color: "var(--color-text-secondary)" }}
                      >
                        Details
                      </Link>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-4">
        <Link href="/ops/tasks" className="glass-card p-4 text-center transition-colors">
          <p className="text-sm" style={{ color: "var(--color-text-primary)" }}>All Tasks</p>
        </Link>
        <Link href="/ops/documents" className="glass-card p-4 text-center transition-colors">
          <p className="text-sm" style={{ color: "var(--color-text-primary)" }}>Doc Reviews</p>
        </Link>
        <Link href="/ops/escalations" className="glass-card p-4 text-center transition-colors">
          <p className="text-sm" style={{ color: "var(--color-text-primary)" }}>Escalations</p>
        </Link>
        <Link href="/ops/workload" className="glass-card p-4 text-center transition-colors">
          <p className="text-sm" style={{ color: "var(--color-text-primary)" }}>Team Workload</p>
        </Link>
      </div>
    </div>
  );
}
