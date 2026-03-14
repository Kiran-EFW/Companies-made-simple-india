"use client";

import { use, useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  getFilingTask,
  updateFilingTaskStatus,
  assignFilingTask,
  handoffFilingTask,
  deleteFilingTask,
  getOpsStaff,
} from "@/lib/api";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const STATUS_OPTIONS = [
  "unassigned",
  "assigned",
  "in_progress",
  "waiting_on_client",
  "waiting_on_government",
  "under_review",
  "completed",
  "blocked",
  "cancelled",
] as const;

const STATUS_BADGE_STYLES: Record<string, string> = {
  unassigned: "bg-gray-500/10 border-gray-500/20 text-gray-500",
  assigned: "bg-blue-500/10 border-blue-500/25 text-blue-400",
  in_progress: "bg-amber-500/10 border-amber-500/25 text-amber-400",
  waiting_on_client: "bg-orange-500/10 border-orange-500/25 text-orange-400",
  waiting_on_government: "bg-purple-500/10 border-purple-500/25 text-purple-400",
  under_review: "bg-cyan-500/10 border-cyan-500/25 text-cyan-400",
  completed: "bg-emerald-500/10 border-emerald-500/25 text-emerald-400",
  blocked: "bg-red-500/10 border-red-500/25 text-red-400",
  cancelled: "bg-gray-500/10 border-gray-600/20 text-gray-600",
};

const STATUS_COLORS: Record<string, string> = {
  unassigned: "text-gray-500",
  assigned: "text-blue-400",
  in_progress: "text-amber-400",
  waiting_on_client: "text-orange-400",
  waiting_on_government: "text-purple-400",
  under_review: "text-cyan-400",
  completed: "text-emerald-400",
  blocked: "text-red-400",
  cancelled: "text-gray-600",
};

const PRIORITY_BADGES: Record<string, { bg: string; text: string }> = {
  urgent: { bg: "bg-red-500/15 border-red-500/30", text: "text-red-400" },
  high: { bg: "bg-amber-500/15 border-amber-500/30", text: "text-amber-400" },
  normal: { bg: "bg-gray-500/15 border-gray-500/30", text: "text-gray-400" },
  low: { bg: "bg-gray-500/10 border-gray-500/20", text: "text-gray-500" },
};

const NEXT_STATUS_OPTIONS: Record<string, string[]> = {
  unassigned: ["assigned"],
  assigned: ["in_progress", "waiting_on_client", "waiting_on_government", "blocked"],
  in_progress: ["completed", "waiting_on_client", "waiting_on_government", "under_review", "blocked"],
  waiting_on_client: ["in_progress", "blocked"],
  waiting_on_government: ["in_progress", "blocked"],
  under_review: ["completed", "in_progress", "blocked"],
  blocked: ["in_progress", "cancelled"],
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "--";
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function formatDateTime(dateStr: string | null | undefined): string {
  if (!dateStr) return "--";
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function isOverdue(dateStr: string | null | undefined): boolean {
  if (!dateStr) return false;
  return new Date(dateStr) < new Date();
}

function humanize(str: string): string {
  return str.replace(/_/g, " ");
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function FilingTaskDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const taskId = Number(id);
  const router = useRouter();

  // -- Data --
  const [task, setTask] = useState<any>(null);
  const [staff, setStaff] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // -- Action states --
  const [actionLoading, setActionLoading] = useState(false);
  const [statusDropdownOpen, setStatusDropdownOpen] = useState(false);
  const [assignDropdownOpen, setAssignDropdownOpen] = useState(false);
  const [showHandoffModal, setShowHandoffModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // -- Editable fields --
  const [notes, setNotes] = useState("");
  const [completionNotes, setCompletionNotes] = useState("");
  const [notesSaving, setNotesSaving] = useState(false);
  const [completionNotesSaving, setCompletionNotesSaving] = useState(false);

  // -- Handoff form --
  const [handoffReassignTo, setHandoffReassignTo] = useState("");
  const [handoffReason, setHandoffReason] = useState("");

  // ------------------------------------------------------------------
  // Data fetching
  // ------------------------------------------------------------------

  const fetchTask = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getFilingTask(taskId);
      setTask(data);
      setNotes(data.notes || "");
      setCompletionNotes(data.completion_notes || "");
    } catch (e: any) {
      console.error("Failed to fetch task:", e);
      setError(e.message || "Failed to load task");
    } finally {
      setLoading(false);
    }
  }, [taskId]);

  const fetchStaff = async () => {
    try {
      const data = await getOpsStaff();
      setStaff(data || []);
    } catch (e) {
      console.error("Failed to fetch ops staff:", e);
    }
  };

  useEffect(() => {
    fetchTask();
    fetchStaff();
  }, [fetchTask]);

  // ------------------------------------------------------------------
  // Actions
  // ------------------------------------------------------------------

  const handleStatusUpdate = async (newStatus: string) => {
    setActionLoading(true);
    setStatusDropdownOpen(false);
    try {
      await updateFilingTaskStatus(taskId, { status: newStatus });
      await fetchTask();
    } catch (e: any) {
      console.error(e);
      alert(e.message || "Failed to update status");
    } finally {
      setActionLoading(false);
    }
  };

  const handleAssign = async (staffId: number) => {
    setActionLoading(true);
    setAssignDropdownOpen(false);
    try {
      await assignFilingTask(taskId, staffId);
      await fetchTask();
    } catch (e: any) {
      console.error(e);
      alert(e.message || "Failed to assign task");
    } finally {
      setActionLoading(false);
    }
  };

  const handleSaveNotes = async () => {
    if (!task) return;
    setNotesSaving(true);
    try {
      await updateFilingTaskStatus(taskId, {
        status: task.status,
        notes,
      });
      await fetchTask();
    } catch (e: any) {
      console.error(e);
      alert(e.message || "Failed to save notes");
    } finally {
      setNotesSaving(false);
    }
  };

  const handleSaveCompletionNotes = async () => {
    if (!task) return;
    setCompletionNotesSaving(true);
    try {
      await updateFilingTaskStatus(taskId, {
        status: task.status,
        completion_notes: completionNotes,
      });
      await fetchTask();
    } catch (e: any) {
      console.error(e);
      alert(e.message || "Failed to save completion notes");
    } finally {
      setCompletionNotesSaving(false);
    }
  };

  const handleHandoff = async () => {
    setActionLoading(true);
    try {
      await handoffFilingTask(taskId, {
        reassign_to: handoffReassignTo ? Number(handoffReassignTo) : undefined,
        reason: handoffReason || undefined,
      });
      setShowHandoffModal(false);
      setHandoffReassignTo("");
      setHandoffReason("");
      await fetchTask();
    } catch (e: any) {
      console.error(e);
      alert(e.message || "Handoff failed");
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    setActionLoading(true);
    try {
      await deleteFilingTask(taskId);
      router.push("/ops/tasks");
    } catch (e: any) {
      console.error(e);
      alert(e.message || "Failed to delete task");
      setActionLoading(false);
    }
  };

  // ------------------------------------------------------------------
  // Render: Loading / Error
  // ------------------------------------------------------------------

  if (loading) {
    return (
      <div className="p-6 lg:p-8 max-w-5xl">
        <div className="animate-pulse text-gray-500 text-center py-20">
          Loading task...
        </div>
      </div>
    );
  }

  if (error || !task) {
    return (
      <div className="p-6 lg:p-8 max-w-5xl">
        <div className="glass-card p-8 text-center">
          <p className="text-red-400 mb-4">{error || "Task not found"}</p>
          <Link
            href="/ops/tasks"
            className="text-sm text-purple-400 hover:text-purple-300 underline"
          >
            Back to Tasks
          </Link>
        </div>
      </div>
    );
  }

  // ------------------------------------------------------------------
  // Derived values
  // ------------------------------------------------------------------

  const priorityBadge = PRIORITY_BADGES[task.priority] || PRIORITY_BADGES.normal;
  const statusBadge = STATUS_BADGE_STYLES[task.status] || STATUS_BADGE_STYLES.unassigned;
  const availableTransitions = NEXT_STATUS_OPTIONS[task.status] || [];
  const overdue =
    isOverdue(task.due_date) &&
    task.status !== "completed" &&
    task.status !== "cancelled";
  const isTerminal = task.status === "completed" || task.status === "cancelled";

  // ------------------------------------------------------------------
  // Render
  // ------------------------------------------------------------------

  return (
    <div className="p-6 lg:p-8 max-w-5xl relative">
      {/* ── Breadcrumb ── */}
      <div className="mb-4 flex items-center gap-2 text-sm text-gray-500">
        <Link
          href="/ops/tasks"
          className="hover:text-purple-400 transition-colors"
        >
          Filing Tasks
        </Link>
        <span>/</span>
        <span className="text-gray-400">Task #{task.id}</span>
      </div>

      {/* ── Page Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-6">
        <div className="flex-1 min-w-0">
          <h1
            className="text-2xl font-bold text-white mb-2 break-words"
            style={{ fontFamily: "var(--font-display)" }}
          >
            {task.title}
          </h1>
          {task.description && (
            <p className="text-sm text-gray-400 leading-relaxed">
              {task.description}
            </p>
          )}
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {actionLoading && (
            <span className="text-xs text-gray-500 animate-pulse">
              Processing...
            </span>
          )}

          {/* Status dropdown */}
          {availableTransitions.length > 0 && (
            <div className="relative">
              <button
                onClick={() => {
                  setStatusDropdownOpen(!statusDropdownOpen);
                  setAssignDropdownOpen(false);
                }}
                disabled={actionLoading}
                className="text-xs px-3 py-1.5 rounded-lg bg-white/5 text-gray-400 hover:bg-white/10 transition-colors disabled:opacity-40 border border-gray-700 font-medium"
              >
                Update Status
              </button>
              {statusDropdownOpen && (
                <div className="absolute right-0 top-full mt-1 z-50 bg-gray-900 border border-gray-700 rounded-lg shadow-xl py-1 min-w-[200px]">
                  {availableTransitions.map((s) => (
                    <button
                      key={s}
                      onClick={() => handleStatusUpdate(s)}
                      className={`block w-full text-left px-3 py-2 text-xs hover:bg-white/5 transition-colors capitalize ${
                        STATUS_COLORS[s] || "text-gray-400"
                      }`}
                    >
                      {humanize(s)}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Assign dropdown */}
          {!isTerminal && (
            <div className="relative">
              <button
                onClick={() => {
                  setAssignDropdownOpen(!assignDropdownOpen);
                  setStatusDropdownOpen(false);
                }}
                disabled={actionLoading}
                className="text-xs px-3 py-1.5 rounded-lg bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 transition-colors disabled:opacity-40 border border-blue-500/20 font-medium"
              >
                Assign
              </button>
              {assignDropdownOpen && (
                <div className="absolute right-0 top-full mt-1 z-50 bg-gray-900 border border-gray-700 rounded-lg shadow-xl py-1 min-w-[220px] max-h-[260px] overflow-y-auto">
                  {staff.length === 0 ? (
                    <p className="px-3 py-2 text-xs text-gray-500">
                      No staff available
                    </p>
                  ) : (
                    staff.map((s: any) => (
                      <button
                        key={s.id}
                        onClick={() => handleAssign(s.id)}
                        className="block w-full text-left px-3 py-2 text-xs text-gray-300 hover:bg-white/5 transition-colors"
                      >
                        <span className="font-medium text-white">
                          {s.full_name || s.email}
                        </span>
                        {s.department && (
                          <span className="ml-2 text-gray-500">
                            {s.department}
                          </span>
                        )}
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>
          )}

          {/* Handoff button */}
          {!isTerminal && (
            <button
              onClick={() => setShowHandoffModal(true)}
              disabled={actionLoading}
              className="text-xs px-3 py-1.5 rounded-lg bg-amber-500/10 text-amber-400 hover:bg-amber-500/20 transition-colors disabled:opacity-40 border border-amber-500/20 font-medium"
            >
              Handoff
            </button>
          )}

          {/* Delete button */}
          <button
            onClick={() => setShowDeleteConfirm(true)}
            disabled={actionLoading}
            className="text-xs px-3 py-1.5 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors disabled:opacity-40 border border-red-500/20 font-medium"
          >
            Delete
          </button>
        </div>
      </div>

      {/* ── Main Content Grid ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column: Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Status & Priority row */}
          <div className="glass-card p-5">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {/* Status */}
              <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider font-medium mb-1.5">
                  Status
                </p>
                <span
                  className={`text-xs font-medium px-2.5 py-1 rounded border capitalize inline-block ${statusBadge}`}
                >
                  {humanize(task.status || "")}
                </span>
              </div>

              {/* Priority */}
              <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider font-medium mb-1.5">
                  Priority
                </p>
                <span
                  className={`text-[10px] font-semibold px-2.5 py-1 rounded border uppercase tracking-wide inline-block ${priorityBadge.bg} ${priorityBadge.text}`}
                >
                  {task.priority}
                </span>
              </div>

              {/* Task Type */}
              <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider font-medium mb-1.5">
                  Task Type
                </p>
                <span className="text-sm text-gray-300 capitalize">
                  {humanize(task.task_type || "")}
                </span>
              </div>

              {/* Company */}
              <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider font-medium mb-1.5">
                  Company
                </p>
                {task.company_id ? (
                  <Link
                    href={`/companies/${task.company_id}`}
                    className="text-sm text-purple-400 hover:text-purple-300 transition-colors underline underline-offset-2"
                  >
                    {task.company_name || `Company #${task.company_id}`}
                  </Link>
                ) : (
                  <span className="text-sm text-gray-500">--</span>
                )}
              </div>
            </div>
          </div>

          {/* Assignment & Timing */}
          <div className="glass-card p-5">
            <h3 className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-4">
              Assignment & Timing
            </h3>
            <div className="grid grid-cols-2 gap-x-6 gap-y-4">
              <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider font-medium mb-1">
                  Assigned To
                </p>
                <p className="text-sm text-white">
                  {task.assignee_name || (
                    <span className="text-gray-600 italic">Unassigned</span>
                  )}
                </p>
              </div>
              <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider font-medium mb-1">
                  Assigned By
                </p>
                <p className="text-sm text-gray-300">
                  {task.assigned_by ? `User #${task.assigned_by}` : "--"}
                </p>
              </div>
              <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider font-medium mb-1">
                  Assigned At
                </p>
                <p className="text-sm text-gray-300 font-mono">
                  {formatDateTime(task.assigned_at)}
                </p>
              </div>
              <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider font-medium mb-1">
                  Due Date
                </p>
                <p className="text-sm font-mono">
                  <span className={overdue ? "text-red-400 font-semibold" : "text-gray-300"}>
                    {formatDate(task.due_date)}
                  </span>
                  {overdue && (
                    <span className="ml-2 text-[10px] bg-red-500/15 border border-red-500/30 text-red-400 px-1.5 py-0.5 rounded">
                      OVERDUE
                    </span>
                  )}
                </p>
              </div>
              <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider font-medium mb-1">
                  Started At
                </p>
                <p className="text-sm text-gray-300 font-mono">
                  {formatDateTime(task.started_at)}
                </p>
              </div>
              <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider font-medium mb-1">
                  Completed At
                </p>
                <p className="text-sm text-gray-300 font-mono">
                  {formatDateTime(task.completed_at)}
                </p>
              </div>
            </div>
          </div>

          {/* Escalation info */}
          <div className="glass-card p-5">
            <h3 className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-4">
              Escalation
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-4">
              <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider font-medium mb-1">
                  Escalation Level
                </p>
                <p className="text-sm text-white">
                  {task.escalation_level ?? 0}
                  {(task.escalation_level ?? 0) > 0 && (
                    <span className="ml-2 text-[10px] bg-red-500/15 border border-red-500/30 text-red-400 px-1.5 py-0.5 rounded">
                      ESCALATED
                    </span>
                  )}
                </p>
              </div>
              <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider font-medium mb-1">
                  Escalated To
                </p>
                <p className="text-sm text-gray-300">
                  {task.escalated_to ? `User #${task.escalated_to}` : "--"}
                </p>
              </div>
              <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider font-medium mb-1">
                  Escalated At
                </p>
                <p className="text-sm text-gray-300 font-mono">
                  {formatDateTime(task.escalated_at)}
                </p>
              </div>
            </div>
          </div>

          {/* Parent Task */}
          {task.parent_task_id && (
            <div className="glass-card p-5">
              <h3 className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-3">
                Parent Task
              </h3>
              <Link
                href={`/ops/tasks/${task.parent_task_id}`}
                className="text-sm text-purple-400 hover:text-purple-300 transition-colors underline underline-offset-2"
              >
                Task #{task.parent_task_id}
              </Link>
            </div>
          )}

          {/* Notes (editable) */}
          <div className="glass-card p-5">
            <h3 className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-3">
              Notes
            </h3>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={4}
              className="w-full bg-gray-900/60 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-purple-500/50 resize-y"
              placeholder="Add notes..."
            />
            <div className="flex justify-end mt-2">
              <button
                onClick={handleSaveNotes}
                disabled={notesSaving || notes === (task.notes || "")}
                className="text-xs px-4 py-1.5 rounded-lg bg-purple-600/80 text-white hover:bg-purple-600 transition-colors disabled:opacity-40 font-medium"
              >
                {notesSaving ? "Saving..." : "Save Notes"}
              </button>
            </div>
          </div>

          {/* Completion Notes (editable if completed) */}
          {task.status === "completed" && (
            <div className="glass-card p-5">
              <h3 className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-3">
                Completion Notes
              </h3>
              <textarea
                value={completionNotes}
                onChange={(e) => setCompletionNotes(e.target.value)}
                rows={3}
                className="w-full bg-gray-900/60 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-purple-500/50 resize-y"
                placeholder="Add completion notes..."
              />
              <div className="flex justify-end mt-2">
                <button
                  onClick={handleSaveCompletionNotes}
                  disabled={
                    completionNotesSaving ||
                    completionNotes === (task.completion_notes || "")
                  }
                  className="text-xs px-4 py-1.5 rounded-lg bg-purple-600/80 text-white hover:bg-purple-600 transition-colors disabled:opacity-40 font-medium"
                >
                  {completionNotesSaving ? "Saving..." : "Save Completion Notes"}
                </button>
              </div>
            </div>
          )}

          {/* Task Metadata */}
          {task.task_metadata &&
            Object.keys(task.task_metadata).length > 0 && (
              <div className="glass-card p-5">
                <h3 className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-3">
                  Task Metadata
                </h3>
                <pre className="bg-gray-900/60 border border-gray-700 rounded-lg px-4 py-3 text-xs text-gray-300 overflow-x-auto font-mono leading-relaxed">
                  {JSON.stringify(task.task_metadata, null, 2)}
                </pre>
              </div>
            )}
        </div>

        {/* Right column: Quick info sidebar */}
        <div className="space-y-6">
          {/* Quick Reference */}
          <div className="glass-card p-5">
            <h3 className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-4">
              Quick Reference
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-500">Task ID</span>
                <span className="text-sm text-white font-mono">#{task.id}</span>
              </div>
              <div className="w-full h-px bg-gray-700/50" />
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-500">Created</span>
                <span className="text-xs text-gray-400 font-mono">
                  {formatDate(task.created_at)}
                </span>
              </div>
              <div className="w-full h-px bg-gray-700/50" />
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-500">Updated</span>
                <span className="text-xs text-gray-400 font-mono">
                  {formatDate(task.updated_at)}
                </span>
              </div>
              {task.company_id && (
                <>
                  <div className="w-full h-px bg-gray-700/50" />
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500">Company ID</span>
                    <span className="text-sm text-white font-mono">
                      #{task.company_id}
                    </span>
                  </div>
                </>
              )}
              {task.parent_task_id && (
                <>
                  <div className="w-full h-px bg-gray-700/50" />
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500">Parent Task</span>
                    <Link
                      href={`/ops/tasks/${task.parent_task_id}`}
                      className="text-sm text-purple-400 hover:text-purple-300 font-mono"
                    >
                      #{task.parent_task_id}
                    </Link>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Status Timeline */}
          <div className="glass-card p-5">
            <h3 className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-4">
              Timeline
            </h3>
            <div className="space-y-3">
              {/* Created */}
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-gray-500 mt-1.5 flex-shrink-0" />
                <div>
                  <p className="text-xs text-gray-400">Created</p>
                  <p className="text-[11px] text-gray-500 font-mono">
                    {formatDateTime(task.created_at)}
                  </p>
                </div>
              </div>

              {/* Assigned */}
              {task.assigned_at && (
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-blue-400 mt-1.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs text-blue-400">Assigned</p>
                    <p className="text-[11px] text-gray-500 font-mono">
                      {formatDateTime(task.assigned_at)}
                    </p>
                  </div>
                </div>
              )}

              {/* Started */}
              {task.started_at && (
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-amber-400 mt-1.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs text-amber-400">Started</p>
                    <p className="text-[11px] text-gray-500 font-mono">
                      {formatDateTime(task.started_at)}
                    </p>
                  </div>
                </div>
              )}

              {/* Escalated */}
              {task.escalated_at && (
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-red-400 mt-1.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs text-red-400">Escalated (Level {task.escalation_level})</p>
                    <p className="text-[11px] text-gray-500 font-mono">
                      {formatDateTime(task.escalated_at)}
                    </p>
                  </div>
                </div>
              )}

              {/* Completed */}
              {task.completed_at && (
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs text-emerald-400">Completed</p>
                    <p className="text-[11px] text-gray-500 font-mono">
                      {formatDateTime(task.completed_at)}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── Handoff Modal ── */}
      {showHandoffModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setShowHandoffModal(false)}
          />
          <div className="relative bg-gray-900 border border-gray-700 rounded-xl shadow-2xl shadow-black/50 w-full max-w-md mx-4 p-6">
            <h3
              className="text-lg font-bold text-white mb-4"
              style={{ fontFamily: "var(--font-display)" }}
            >
              Hand Off Task
            </h3>
            <p className="text-sm text-gray-400 mb-4">
              Optionally reassign this task to another team member and provide a
              reason.
            </p>

            {/* Reassign to */}
            <div className="mb-4">
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-medium block mb-1.5">
                Reassign To (optional)
              </label>
              <select
                value={handoffReassignTo}
                onChange={(e) => setHandoffReassignTo(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500/50"
              >
                <option value="">No reassignment</option>
                {staff.map((s: any) => (
                  <option key={s.id} value={s.id} className="bg-gray-900">
                    {s.full_name || s.email}
                  </option>
                ))}
              </select>
            </div>

            {/* Reason */}
            <div className="mb-5">
              <label className="text-[10px] text-gray-500 uppercase tracking-wider font-medium block mb-1.5">
                Reason (optional)
              </label>
              <textarea
                value={handoffReason}
                onChange={(e) => setHandoffReason(e.target.value)}
                rows={3}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-purple-500/50 resize-none"
                placeholder="Why is this task being handed off?"
              />
            </div>

            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowHandoffModal(false);
                  setHandoffReassignTo("");
                  setHandoffReason("");
                }}
                className="text-xs px-4 py-2 rounded-lg bg-gray-800 text-gray-400 hover:bg-gray-700 transition-colors font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleHandoff}
                disabled={actionLoading}
                className="text-xs px-4 py-2 rounded-lg bg-amber-600 text-white hover:bg-amber-500 transition-colors disabled:opacity-40 font-medium"
              >
                {actionLoading ? "Processing..." : "Confirm Handoff"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Delete Confirmation Modal ── */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setShowDeleteConfirm(false)}
          />
          <div className="relative bg-gray-900 border border-gray-700 rounded-xl shadow-2xl shadow-black/50 w-full max-w-sm mx-4 p-6">
            <h3
              className="text-lg font-bold text-white mb-2"
              style={{ fontFamily: "var(--font-display)" }}
            >
              Delete Task
            </h3>
            <p className="text-sm text-gray-400 mb-5">
              Are you sure you want to delete{" "}
              <span className="text-white font-medium">
                &quot;{task.title}&quot;
              </span>
              ? This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="text-xs px-4 py-2 rounded-lg bg-gray-800 text-gray-400 hover:bg-gray-700 transition-colors font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={actionLoading}
                className="text-xs px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-500 transition-colors disabled:opacity-40 font-medium"
              >
                {actionLoading ? "Deleting..." : "Delete Task"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Click-outside dismiss for dropdowns ── */}
      {(statusDropdownOpen || assignDropdownOpen) && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => {
            setStatusDropdownOpen(false);
            setAssignDropdownOpen(false);
          }}
        />
      )}
    </div>
  );
}
