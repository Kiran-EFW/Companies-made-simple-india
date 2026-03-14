"use client";

import { useEffect, useState, useCallback } from "react";
import {
  getFilingTasks,
  updateFilingTaskStatus,
  assignFilingTask,
  claimFilingTask,
  getOpsStaff,
  bulkAssignTasks,
  bulkUpdateTaskStatus,
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

const PRIORITY_BADGES: Record<string, { bg: string; text: string }> = {
  urgent: { bg: "bg-red-500/15 border-red-500/30", text: "text-red-400" },
  high: { bg: "bg-amber-500/15 border-amber-500/30", text: "text-amber-400" },
  normal: { bg: "bg-gray-500/15 border-gray-500/30", text: "text-gray-400" },
  low: { bg: "bg-gray-500/10 border-gray-500/20", text: "text-gray-500" },
};

const PRIORITY_OPTIONS = ["urgent", "high", "normal", "low"] as const;

const NEXT_STATUS_OPTIONS: Record<string, string[]> = {
  assigned: ["in_progress", "waiting_on_client", "waiting_on_government", "blocked"],
  in_progress: ["completed", "waiting_on_client", "waiting_on_government", "under_review", "blocked"],
  waiting_on_client: ["in_progress", "blocked"],
  waiting_on_government: ["in_progress", "blocked"],
  under_review: ["completed", "in_progress", "blocked"],
  blocked: ["in_progress", "cancelled"],
};

const PAGE_SIZE = 20;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "--";
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

function isOverdue(dateStr: string | null): boolean {
  if (!dateStr) return false;
  return new Date(dateStr) < new Date();
}

function humanize(str: string): string {
  return str.replace(/_/g, " ");
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function FilingTasksPage() {
  // -- Data state --
  const [tasks, setTasks] = useState<any[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [staff, setStaff] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  // -- Filter state --
  const [filterStatus, setFilterStatus] = useState("");
  const [filterPriority, setFilterPriority] = useState("");
  const [filterAssignee, setFilterAssignee] = useState("");
  const [overdueOnly, setOverdueOnly] = useState(false);

  // -- Pagination --
  const [page, setPage] = useState(0);

  // -- Selection / Bulk --
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());

  // -- Inline assign modal --
  const [assignModalTaskId, setAssignModalTaskId] = useState<number | null>(null);

  // -- Bulk modals --
  const [showBulkAssign, setShowBulkAssign] = useState(false);
  const [bulkAssignee, setBulkAssignee] = useState("");
  const [showBulkStatus, setShowBulkStatus] = useState(false);
  const [bulkStatus, setBulkStatus] = useState("");

  // -- Inline status dropdown --
  const [statusDropdownTaskId, setStatusDropdownTaskId] = useState<number | null>(null);

  // ------------------------------------------------------------------
  // Data fetching
  // ------------------------------------------------------------------

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    try {
      const params: any = { skip: page * PAGE_SIZE, limit: PAGE_SIZE };
      if (filterStatus) params.status = filterStatus;
      if (filterPriority) params.priority = filterPriority;
      if (filterAssignee) params.assigned_to = Number(filterAssignee);
      if (overdueOnly) params.overdue_only = true;

      const data = await getFilingTasks(params);
      setTasks(data?.tasks || data || []);
      setTotalCount(data?.total ?? (data?.tasks?.length || 0));
    } catch (e) {
      console.error("Failed to fetch filing tasks:", e);
    } finally {
      setLoading(false);
    }
  }, [page, filterStatus, filterPriority, filterAssignee, overdueOnly]);

  const fetchStaff = async () => {
    try {
      const data = await getOpsStaff();
      setStaff(data || []);
    } catch (e) {
      console.error("Failed to fetch ops staff:", e);
    }
  };

  useEffect(() => {
    fetchStaff();
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Reset page when filters change
  useEffect(() => {
    setPage(0);
    setSelectedIds(new Set());
  }, [filterStatus, filterPriority, filterAssignee, overdueOnly]);

  // ------------------------------------------------------------------
  // Actions
  // ------------------------------------------------------------------

  const handleClaim = async (taskId: number) => {
    setActionLoading(taskId);
    try {
      await claimFilingTask(taskId);
      await fetchTasks();
    } catch (e: any) {
      console.error(e);
      alert(e.message || "Failed to claim task");
    } finally {
      setActionLoading(null);
    }
  };

  const handleStatusUpdate = async (taskId: number, newStatus: string) => {
    setActionLoading(taskId);
    setStatusDropdownTaskId(null);
    try {
      await updateFilingTaskStatus(taskId, { status: newStatus });
      await fetchTasks();
    } catch (e: any) {
      console.error(e);
      alert(e.message || "Failed to update status");
    } finally {
      setActionLoading(null);
    }
  };

  const handleAssign = async (taskId: number, staffId: number) => {
    setActionLoading(taskId);
    setAssignModalTaskId(null);
    try {
      await assignFilingTask(taskId, staffId);
      await fetchTasks();
    } catch (e: any) {
      console.error(e);
      alert(e.message || "Failed to assign task");
    } finally {
      setActionLoading(null);
    }
  };

  const handleBulkAssign = async () => {
    if (!bulkAssignee) return;
    try {
      await bulkAssignTasks(Array.from(selectedIds), Number(bulkAssignee));
      setSelectedIds(new Set());
      setShowBulkAssign(false);
      setBulkAssignee("");
      await fetchTasks();
    } catch (e: any) {
      console.error(e);
      alert(e.message || "Bulk assign failed");
    }
  };

  const handleBulkStatusUpdate = async () => {
    if (!bulkStatus) return;
    try {
      await bulkUpdateTaskStatus(Array.from(selectedIds), bulkStatus);
      setSelectedIds(new Set());
      setShowBulkStatus(false);
      setBulkStatus("");
      await fetchTasks();
    } catch (e: any) {
      console.error(e);
      alert(e.message || "Bulk status update failed");
    }
  };

  // ------------------------------------------------------------------
  // Selection helpers
  // ------------------------------------------------------------------

  const toggleSelect = (id: number) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === tasks.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(tasks.map((t) => t.id)));
    }
  };

  // ------------------------------------------------------------------
  // Pagination
  // ------------------------------------------------------------------

  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));

  // ------------------------------------------------------------------
  // Render
  // ------------------------------------------------------------------

  return (
    <div className="p-6 lg:p-8 max-w-full relative">
      {/* ── Page Header ── */}
      <div className="mb-6">
        <h1
          className="text-3xl font-bold mb-2"
          style={{ fontFamily: "var(--font-display)" }}
        >
          Filing Tasks
        </h1>
        <p className="text-sm text-gray-400">
          Manage, assign, and track all filing tasks across companies.
        </p>
      </div>

      {/* ── Filter Bar ── */}
      <div className="glass-card p-4 mb-6">
        <div className="flex flex-wrap items-center gap-3">
          {/* Status */}
          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-gray-500 uppercase tracking-wider font-medium">
              Status
            </label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="bg-gray-900/60 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500/50 min-w-[160px]"
            >
              <option value="">All Statuses</option>
              {STATUS_OPTIONS.map((s) => (
                <option key={s} value={s} className="bg-gray-900">
                  {humanize(s)}
                </option>
              ))}
            </select>
          </div>

          {/* Priority */}
          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-gray-500 uppercase tracking-wider font-medium">
              Priority
            </label>
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="bg-gray-900/60 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500/50 min-w-[140px]"
            >
              <option value="">All Priorities</option>
              {PRIORITY_OPTIONS.map((p) => (
                <option key={p} value={p} className="bg-gray-900">
                  {p.charAt(0).toUpperCase() + p.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Assigned To */}
          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-gray-500 uppercase tracking-wider font-medium">
              Assigned To
            </label>
            <select
              value={filterAssignee}
              onChange={(e) => setFilterAssignee(e.target.value)}
              className="bg-gray-900/60 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500/50 min-w-[160px]"
            >
              <option value="">All Team Members</option>
              {staff.map((s: any) => (
                <option key={s.id} value={s.id} className="bg-gray-900">
                  {s.full_name || s.email}
                </option>
              ))}
            </select>
          </div>

          {/* Overdue toggle */}
          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-gray-500 uppercase tracking-wider font-medium">
              Overdue Only
            </label>
            <button
              onClick={() => setOverdueOnly(!overdueOnly)}
              className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors ${
                overdueOnly
                  ? "bg-red-500/15 border-red-500/30 text-red-400"
                  : "bg-gray-900/60 border-gray-700 text-gray-400 hover:border-gray-600"
              }`}
            >
              {overdueOnly ? "Showing Overdue" : "Off"}
            </button>
          </div>
        </div>
      </div>

      {/* ── Task Table ── */}
      <div className="rounded-xl border border-gray-700 bg-gray-800/50 overflow-hidden">
        {loading ? (
          <div className="p-12 flex items-center justify-center">
            <div className="animate-pulse text-gray-500">Loading tasks...</div>
          </div>
        ) : tasks.length === 0 ? (
          <div className="p-12 text-center text-gray-500">
            <p className="text-sm">No filing tasks match your filters.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="px-4 py-3 text-left">
                    <input
                      type="checkbox"
                      checked={selectedIds.size === tasks.length && tasks.length > 0}
                      onChange={toggleSelectAll}
                      className="rounded border-gray-600 bg-gray-800 text-purple-500 focus:ring-purple-500/30"
                    />
                  </th>
                  <th className="px-4 py-3 text-left text-xs text-gray-500 font-medium uppercase tracking-wider">
                    Title
                  </th>
                  <th className="px-4 py-3 text-left text-xs text-gray-500 font-medium uppercase tracking-wider">
                    Company
                  </th>
                  <th className="px-4 py-3 text-left text-xs text-gray-500 font-medium uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-4 py-3 text-left text-xs text-gray-500 font-medium uppercase tracking-wider">
                    Priority
                  </th>
                  <th className="px-4 py-3 text-left text-xs text-gray-500 font-medium uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs text-gray-500 font-medium uppercase tracking-wider">
                    Assignee
                  </th>
                  <th className="px-4 py-3 text-left text-xs text-gray-500 font-medium uppercase tracking-wider">
                    Due Date
                  </th>
                  <th className="px-4 py-3 text-right text-xs text-gray-500 font-medium uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700/50">
                {tasks.map((task: any) => {
                  const overdue = isOverdue(task.due_date) && task.status !== "completed" && task.status !== "cancelled";
                  const priorityBadge = PRIORITY_BADGES[task.priority] || PRIORITY_BADGES.normal;
                  const statusBadge = STATUS_BADGE_STYLES[task.status] || STATUS_BADGE_STYLES.unassigned;
                  const isTaskLoading = actionLoading === task.id;
                  const availableTransitions = NEXT_STATUS_OPTIONS[task.status] || [];

                  return (
                    <tr
                      key={task.id}
                      className={`hover:bg-white/5 transition-colors ${
                        overdue ? "bg-red-500/[0.03]" : ""
                      } ${selectedIds.has(task.id) ? "bg-purple-500/[0.05]" : ""}`}
                    >
                      {/* Checkbox */}
                      <td className="px-4 py-3">
                        <input
                          type="checkbox"
                          checked={selectedIds.has(task.id)}
                          onChange={() => toggleSelect(task.id)}
                          className="rounded border-gray-600 bg-gray-800 text-purple-500 focus:ring-purple-500/30"
                        />
                      </td>

                      {/* Title */}
                      <td className="px-4 py-3">
                        <span className="text-sm font-medium text-white">
                          {task.title}
                        </span>
                      </td>

                      {/* Company */}
                      <td className="px-4 py-3">
                        <span className="text-sm text-gray-300 truncate max-w-[180px] block">
                          {task.company_name || "--"}
                        </span>
                      </td>

                      {/* Type */}
                      <td className="px-4 py-3">
                        <span className="text-xs text-gray-400 capitalize">
                          {humanize(task.task_type || "")}
                        </span>
                      </td>

                      {/* Priority */}
                      <td className="px-4 py-3">
                        <span
                          className={`text-[10px] font-semibold px-2 py-0.5 rounded border uppercase tracking-wide ${priorityBadge.bg} ${priorityBadge.text}`}
                        >
                          {task.priority}
                        </span>
                      </td>

                      {/* Status */}
                      <td className="px-4 py-3">
                        <span
                          className={`text-[11px] font-medium px-2 py-0.5 rounded border capitalize ${statusBadge}`}
                        >
                          {humanize(task.status || "")}
                        </span>
                      </td>

                      {/* Assignee */}
                      <td className="px-4 py-3">
                        {task.assignee_name ? (
                          <span className="text-sm text-gray-300">
                            {task.assignee_name}
                          </span>
                        ) : (
                          <span className="text-xs text-gray-600 italic">
                            Unassigned
                          </span>
                        )}
                      </td>

                      {/* Due Date */}
                      <td className="px-4 py-3">
                        <span
                          className={`text-xs font-mono ${
                            overdue ? "text-red-400 font-semibold" : "text-gray-400"
                          }`}
                        >
                          {formatDate(task.due_date)}
                          {overdue && (
                            <span className="ml-1.5 text-[10px] bg-red-500/15 border border-red-500/30 text-red-400 px-1.5 py-0.5 rounded">
                              OVERDUE
                            </span>
                          )}
                        </span>
                      </td>

                      {/* Actions */}
                      <td className="px-4 py-3">
                        <div className="flex items-center justify-end gap-1.5 relative">
                          {isTaskLoading && (
                            <span className="text-[10px] text-gray-500 animate-pulse mr-1">
                              ...
                            </span>
                          )}

                          {/* Claim button for unassigned tasks */}
                          {(task.status === "unassigned" || (!task.assigned_to && !task.assignee_name)) && task.status !== "completed" && task.status !== "cancelled" && (
                            <button
                              onClick={() => handleClaim(task.id)}
                              disabled={isTaskLoading}
                              className="text-xs px-2.5 py-1 rounded bg-purple-500/15 text-purple-400 hover:bg-purple-500/25 transition-colors disabled:opacity-40 border border-purple-500/20"
                            >
                              Claim
                            </button>
                          )}

                          {/* Status update dropdown */}
                          {availableTransitions.length > 0 && (
                            <div className="relative">
                              <button
                                onClick={() =>
                                  setStatusDropdownTaskId(
                                    statusDropdownTaskId === task.id ? null : task.id
                                  )
                                }
                                disabled={isTaskLoading}
                                className="text-xs px-2.5 py-1 rounded bg-white/5 text-gray-400 hover:bg-white/10 transition-colors disabled:opacity-40 border border-gray-700"
                              >
                                Status
                              </button>
                              {statusDropdownTaskId === task.id && (
                                <div className="absolute right-0 top-full mt-1 z-50 bg-gray-900 border border-gray-700 rounded-lg shadow-xl py-1 min-w-[180px]">
                                  {availableTransitions.map((s) => (
                                    <button
                                      key={s}
                                      onClick={() => handleStatusUpdate(task.id, s)}
                                      className={`block w-full text-left px-3 py-2 text-xs hover:bg-white/5 transition-colors capitalize ${STATUS_COLORS[s] || "text-gray-400"}`}
                                    >
                                      {humanize(s)}
                                    </button>
                                  ))}
                                </div>
                              )}
                            </div>
                          )}

                          {/* Assign button */}
                          {task.status !== "completed" && task.status !== "cancelled" && (
                            <div className="relative">
                              <button
                                onClick={() =>
                                  setAssignModalTaskId(
                                    assignModalTaskId === task.id ? null : task.id
                                  )
                                }
                                disabled={isTaskLoading}
                                className="text-xs px-2.5 py-1 rounded bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 transition-colors disabled:opacity-40 border border-blue-500/20"
                              >
                                Assign
                              </button>
                              {assignModalTaskId === task.id && (
                                <div className="absolute right-0 top-full mt-1 z-50 bg-gray-900 border border-gray-700 rounded-lg shadow-xl py-1 min-w-[200px] max-h-[240px] overflow-y-auto">
                                  {staff.length === 0 ? (
                                    <p className="px-3 py-2 text-xs text-gray-500">
                                      No staff available
                                    </p>
                                  ) : (
                                    staff.map((s: any) => (
                                      <button
                                        key={s.id}
                                        onClick={() => handleAssign(task.id, s.id)}
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
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Pagination ── */}
      {!loading && tasks.length > 0 && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-xs text-gray-500">
            Showing {page * PAGE_SIZE + 1}
            {" - "}
            {Math.min((page + 1) * PAGE_SIZE, totalCount)} of {totalCount} tasks
          </p>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setPage(0)}
              disabled={page === 0}
              className="px-2.5 py-1.5 rounded text-xs text-gray-400 hover:bg-white/5 transition-colors disabled:opacity-30 disabled:cursor-not-allowed border border-gray-700"
            >
              First
            </button>
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-2.5 py-1.5 rounded text-xs text-gray-400 hover:bg-white/5 transition-colors disabled:opacity-30 disabled:cursor-not-allowed border border-gray-700"
            >
              Prev
            </button>
            {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
              let pageNum: number;
              if (totalPages <= 5) {
                pageNum = i;
              } else if (page < 3) {
                pageNum = i;
              } else if (page > totalPages - 4) {
                pageNum = totalPages - 5 + i;
              } else {
                pageNum = page - 2 + i;
              }
              return (
                <button
                  key={pageNum}
                  onClick={() => setPage(pageNum)}
                  className={`px-3 py-1.5 rounded text-xs font-medium transition-colors border ${
                    page === pageNum
                      ? "bg-purple-500/20 text-purple-400 border-purple-500/30"
                      : "text-gray-400 hover:bg-white/5 border-gray-700"
                  }`}
                >
                  {pageNum + 1}
                </button>
              );
            })}
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1}
              className="px-2.5 py-1.5 rounded text-xs text-gray-400 hover:bg-white/5 transition-colors disabled:opacity-30 disabled:cursor-not-allowed border border-gray-700"
            >
              Next
            </button>
            <button
              onClick={() => setPage(totalPages - 1)}
              disabled={page >= totalPages - 1}
              className="px-2.5 py-1.5 rounded text-xs text-gray-400 hover:bg-white/5 transition-colors disabled:opacity-30 disabled:cursor-not-allowed border border-gray-700"
            >
              Last
            </button>
          </div>
        </div>
      )}

      {/* ── Floating Bulk Action Bar ── */}
      {selectedIds.size > 0 && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
          <div className="bg-gray-900 border border-gray-700 rounded-xl shadow-2xl shadow-black/50 px-6 py-3 flex items-center gap-4">
            <span className="text-sm text-gray-300">
              <span className="font-bold text-purple-400">{selectedIds.size}</span>{" "}
              task{selectedIds.size > 1 ? "s" : ""} selected
            </span>

            <div className="w-px h-6 bg-gray-700" />

            {/* Bulk Assign */}
            <div className="relative">
              <button
                onClick={() => {
                  setShowBulkAssign(!showBulkAssign);
                  setShowBulkStatus(false);
                }}
                className="text-xs px-3 py-1.5 rounded-lg bg-blue-500/15 text-blue-400 hover:bg-blue-500/25 transition-colors border border-blue-500/25 font-medium"
              >
                Bulk Assign
              </button>
              {showBulkAssign && (
                <div className="absolute bottom-full mb-2 left-0 bg-gray-900 border border-gray-700 rounded-lg shadow-xl p-3 min-w-[240px]">
                  <p className="text-xs text-gray-400 mb-2 font-medium">
                    Assign {selectedIds.size} task{selectedIds.size > 1 ? "s" : ""} to:
                  </p>
                  <select
                    value={bulkAssignee}
                    onChange={(e) => setBulkAssignee(e.target.value)}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500/50 mb-2"
                  >
                    <option value="">Select team member...</option>
                    {staff.map((s: any) => (
                      <option key={s.id} value={s.id} className="bg-gray-900">
                        {s.full_name || s.email}
                      </option>
                    ))}
                  </select>
                  <div className="flex gap-2">
                    <button
                      onClick={handleBulkAssign}
                      disabled={!bulkAssignee}
                      className="flex-1 text-xs px-3 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-500 transition-colors disabled:opacity-40 font-medium"
                    >
                      Assign
                    </button>
                    <button
                      onClick={() => {
                        setShowBulkAssign(false);
                        setBulkAssignee("");
                      }}
                      className="text-xs px-3 py-1.5 rounded bg-gray-800 text-gray-400 hover:bg-gray-700 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Bulk Update Status */}
            <div className="relative">
              <button
                onClick={() => {
                  setShowBulkStatus(!showBulkStatus);
                  setShowBulkAssign(false);
                }}
                className="text-xs px-3 py-1.5 rounded-lg bg-amber-500/15 text-amber-400 hover:bg-amber-500/25 transition-colors border border-amber-500/25 font-medium"
              >
                Bulk Update Status
              </button>
              {showBulkStatus && (
                <div className="absolute bottom-full mb-2 right-0 bg-gray-900 border border-gray-700 rounded-lg shadow-xl p-3 min-w-[240px]">
                  <p className="text-xs text-gray-400 mb-2 font-medium">
                    Set status for {selectedIds.size} task{selectedIds.size > 1 ? "s" : ""}:
                  </p>
                  <select
                    value={bulkStatus}
                    onChange={(e) => setBulkStatus(e.target.value)}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500/50 mb-2"
                  >
                    <option value="">Select status...</option>
                    {STATUS_OPTIONS.map((s) => (
                      <option key={s} value={s} className="bg-gray-900">
                        {humanize(s)}
                      </option>
                    ))}
                  </select>
                  <div className="flex gap-2">
                    <button
                      onClick={handleBulkStatusUpdate}
                      disabled={!bulkStatus}
                      className="flex-1 text-xs px-3 py-1.5 rounded bg-amber-600 text-white hover:bg-amber-500 transition-colors disabled:opacity-40 font-medium"
                    >
                      Update
                    </button>
                    <button
                      onClick={() => {
                        setShowBulkStatus(false);
                        setBulkStatus("");
                      }}
                      className="text-xs px-3 py-1.5 rounded bg-gray-800 text-gray-400 hover:bg-gray-700 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>

            <div className="w-px h-6 bg-gray-700" />

            <button
              onClick={() => setSelectedIds(new Set())}
              className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
            >
              Clear
            </button>
          </div>
        </div>
      )}

      {/* ── Click-outside dismiss for dropdowns ── */}
      {(statusDropdownTaskId !== null || assignModalTaskId !== null) && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => {
            setStatusDropdownTaskId(null);
            setAssignModalTaskId(null);
          }}
        />
      )}
    </div>
  );
}
