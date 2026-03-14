"use client";

import { useEffect, useState } from "react";
import { getMyQueue, updateFilingTaskStatus, claimFilingTask } from "@/lib/api";
import Link from "next/link";
import { useToast } from "@/components/toast";

const STATUS_COLORS: Record<string, string> = {
  assigned: "text-blue-400",
  in_progress: "text-amber-400",
  waiting_on_client: "text-orange-400",
  waiting_on_government: "text-purple-400",
  under_review: "text-cyan-400",
  blocked: "text-red-400",
  completed: "text-emerald-400",
};

const PRIORITY_BADGES: Record<string, { bg: string; text: string }> = {
  urgent: { bg: "bg-red-500/15 border-red-500/30", text: "text-red-400" },
  high: { bg: "bg-amber-500/15 border-amber-500/30", text: "text-amber-400" },
  normal: { bg: "bg-gray-500/15 border-gray-500/30", text: "text-gray-400" },
  low: { bg: "bg-gray-500/10 border-gray-500/20", text: "text-gray-500" },
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
          <div className="h-8 bg-gray-800 rounded w-48" />
          <div className="grid grid-cols-4 gap-4">
            {[1, 2, 3, 4].map(i => <div key={i} className="h-24 bg-gray-800 rounded-lg" />)}
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
        <p className="text-gray-400 text-sm mt-1">Your assigned tasks and pending items</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-card p-4">
          <p className="text-xs text-gray-400 uppercase tracking-wider">In Progress</p>
          <p className="text-2xl font-bold text-amber-400 mt-1">{stats.in_progress || 0}</p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs text-gray-400 uppercase tracking-wider">Assigned</p>
          <p className="text-2xl font-bold text-blue-400 mt-1">{stats.assigned || 0}</p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs text-gray-400 uppercase tracking-wider">Doc Reviews</p>
          <p className="text-2xl font-bold text-cyan-400 mt-1">{queue?.review_items_count || 0}</p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs text-gray-400 uppercase tracking-wider">Escalations</p>
          <p className="text-2xl font-bold text-red-400 mt-1">{queue?.escalations_count || 0}</p>
        </div>
      </div>

      {/* Overdue Alert */}
      {overdueTasks.length > 0 && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
          <p className="text-red-400 font-medium text-sm">
            {overdueTasks.length} overdue task{overdueTasks.length > 1 ? "s" : ""} require immediate attention
          </p>
        </div>
      )}

      {/* Task List */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Active Tasks ({tasks.length})</h2>
        {tasks.length === 0 ? (
          <div className="glass-card p-8 text-center text-gray-500">
            <p>No tasks in your queue. Check the <Link href="/ops/tasks" className="text-purple-400 hover:underline">task board</Link> for unassigned work.</p>
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
                        <span className="text-sm font-medium text-white">{task.title}</span>
                        <span className={`text-[10px] px-1.5 py-0.5 rounded border ${priorityBadge.bg} ${priorityBadge.text}`}>
                          {task.priority?.toUpperCase()}
                        </span>
                        <span className={`text-xs ${STATUS_COLORS[task.status] || "text-gray-400"}`}>
                          {task.status?.replace(/_/g, " ")}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                        {task.company_name && <span>{task.company_name}</span>}
                        <span>{task.task_type?.replace(/_/g, " ")}</span>
                        {task.due_date && (
                          <span className={isOverdue ? "text-red-400" : "text-gray-400"}>
                            {timeUntil(task.due_date)}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5 shrink-0">
                      {task.status === "assigned" && (
                        <button
                          onClick={() => handleStatusUpdate(task.id, "in_progress")}
                          className="text-xs px-2.5 py-1 rounded bg-amber-500/15 text-amber-400 hover:bg-amber-500/25 transition-colors"
                        >
                          Start
                        </button>
                      )}
                      {task.status === "in_progress" && (
                        <button
                          onClick={() => handleStatusUpdate(task.id, "completed")}
                          className="text-xs px-2.5 py-1 rounded bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/25 transition-colors"
                        >
                          Complete
                        </button>
                      )}
                      <Link
                        href={`/ops/tasks?task=${task.id}`}
                        className="text-xs px-2.5 py-1 rounded bg-white/5 text-gray-400 hover:bg-white/10 transition-colors"
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
        <Link href="/ops/tasks" className="glass-card p-4 text-center hover:bg-white/5 transition-colors">
          <p className="text-sm text-gray-300">All Tasks</p>
        </Link>
        <Link href="/ops/documents" className="glass-card p-4 text-center hover:bg-white/5 transition-colors">
          <p className="text-sm text-gray-300">Doc Reviews</p>
        </Link>
        <Link href="/ops/escalations" className="glass-card p-4 text-center hover:bg-white/5 transition-colors">
          <p className="text-sm text-gray-300">Escalations</p>
        </Link>
        <Link href="/ops/workload" className="glass-card p-4 text-center hover:bg-white/5 transition-colors">
          <p className="text-sm text-gray-300">Team Workload</p>
        </Link>
      </div>
    </div>
  );
}
