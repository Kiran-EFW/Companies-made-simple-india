"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import {
  getFilingTasks,
  createFilingTask,
  updateFilingTaskStatus,
  assignFilingTask,
  claimFilingTask,
  getOpsStaff,
  bulkAssignTasks,
  bulkUpdateTaskStatus,
} from "@/lib/api";

const STATUS_OPTIONS = ["unassigned","assigned","in_progress","waiting_on_client","waiting_on_government","under_review","completed","blocked","cancelled"] as const;
const STATUS_COLORS: Record<string, string> = { unassigned:"var(--color-text-muted)",assigned:"var(--color-info)",in_progress:"var(--color-warning)",waiting_on_client:"var(--color-warning)",waiting_on_government:"var(--color-accent-purple-light)",under_review:"var(--color-info)",completed:"var(--color-success)",blocked:"var(--color-error)",cancelled:"var(--color-text-muted)" };
const STATUS_BADGE_STYLES: Record<string, { bg: string; border: string; color: string }> = { unassigned:{bg:"bg-gray-500/10",border:"border-gray-500/20",color:"var(--color-text-muted)"},assigned:{bg:"bg-blue-500/10",border:"border-blue-500/25",color:"var(--color-info)"},in_progress:{bg:"bg-amber-500/10",border:"border-amber-500/25",color:"var(--color-warning)"},waiting_on_client:{bg:"bg-orange-500/10",border:"border-orange-500/25",color:"var(--color-warning)"},waiting_on_government:{bg:"bg-purple-500/10",border:"border-purple-500/25",color:"var(--color-accent-purple-light)"},under_review:{bg:"bg-cyan-500/10",border:"border-cyan-500/25",color:"var(--color-info)"},completed:{bg:"bg-emerald-500/10",border:"border-emerald-500/25",color:"var(--color-success)"},blocked:{bg:"bg-red-500/10",border:"border-red-500/25",color:"var(--color-error)"},cancelled:{bg:"bg-gray-500/10",border:"border-gray-600/20",color:"var(--color-text-muted)"} };
const PRIORITY_BADGES: Record<string, { bg: string; border: string; color: string }> = { urgent:{bg:"bg-red-500/15",border:"border-red-500/30",color:"var(--color-error)"},high:{bg:"bg-amber-500/15",border:"border-amber-500/30",color:"var(--color-warning)"},normal:{bg:"bg-gray-500/15",border:"border-gray-500/30",color:"var(--color-text-secondary)"},low:{bg:"bg-gray-500/10",border:"border-gray-500/20",color:"var(--color-text-muted)"} };
const PRIORITY_OPTIONS = ["urgent","high","normal","low"] as const;
const NEXT_STATUS_OPTIONS: Record<string, string[]> = { assigned:["in_progress","waiting_on_client","waiting_on_government","blocked"],in_progress:["completed","waiting_on_client","waiting_on_government","under_review","blocked"],waiting_on_client:["in_progress","blocked"],waiting_on_government:["in_progress","blocked"],under_review:["completed","in_progress","blocked"],blocked:["in_progress","cancelled"] };
const PAGE_SIZE = 20;
const TASK_TYPE_OPTIONS = ["dsc_application","din_application","name_reservation","spice_plus","moa_drafting","aoa_drafting","stamp_duty","pan_application","tan_application","gst_registration","bank_account","share_certificates","statutory_registers","iec_registration","esic_registration","pf_registration","professional_tax","shop_establishment","trademark_registration","inc20a_filing","aoc4_filing","mgt7_filing","adt1_filing","dir3_kyc","annual_gst_return","income_tax_return","other"] as const;

function formatDate(dateStr: string | null): string { if (!dateStr) return "--"; const d = new Date(dateStr); return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }); }
function isOverdue(dateStr: string | null): boolean { if (!dateStr) return false; return new Date(dateStr) < new Date(); }
function humanize(str: string): string { return str.replace(/_/g, " "); }

export default function FilingTasksPage() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [staff, setStaff] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [filterStatus, setFilterStatus] = useState("");
  const [filterPriority, setFilterPriority] = useState("");
  const [filterAssignee, setFilterAssignee] = useState("");
  const [overdueOnly, setOverdueOnly] = useState(false);
  const [page, setPage] = useState(0);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [assignModalTaskId, setAssignModalTaskId] = useState<number | null>(null);
  const [showBulkAssign, setShowBulkAssign] = useState(false);
  const [bulkAssignee, setBulkAssignee] = useState("");
  const [showBulkStatus, setShowBulkStatus] = useState(false);
  const [bulkStatus, setBulkStatus] = useState("");
  const [statusDropdownTaskId, setStatusDropdownTaskId] = useState<number | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createLoading, setCreateLoading] = useState(false);
  const [createForm, setCreateForm] = useState({ company_id: "", task_type: "other", title: "", description: "", priority: "normal", assigned_to: "", due_date: "", parent_task_id: "" });

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
    } catch (e) { console.error("Failed to fetch filing tasks:", e); }
    finally { setLoading(false); }
  }, [page, filterStatus, filterPriority, filterAssignee, overdueOnly]);

  const fetchStaff = async () => { try { const data = await getOpsStaff(); setStaff(data || []); } catch (e) { console.error("Failed to fetch ops staff:", e); } };
  useEffect(() => { fetchStaff(); }, []);
  useEffect(() => { fetchTasks(); }, [fetchTasks]);
  useEffect(() => { setPage(0); setSelectedIds(new Set()); }, [filterStatus, filterPriority, filterAssignee, overdueOnly]);

  const handleClaim = async (taskId: number) => { setActionLoading(taskId); try { await claimFilingTask(taskId); await fetchTasks(); } catch (e: any) { alert(e.message || "Failed to claim task"); } finally { setActionLoading(null); } };
  const handleStatusUpdate = async (taskId: number, newStatus: string) => { setActionLoading(taskId); setStatusDropdownTaskId(null); try { await updateFilingTaskStatus(taskId, { status: newStatus }); await fetchTasks(); } catch (e: any) { alert(e.message || "Failed to update status"); } finally { setActionLoading(null); } };
  const handleAssign = async (taskId: number, staffId: number) => { setActionLoading(taskId); setAssignModalTaskId(null); try { await assignFilingTask(taskId, staffId); await fetchTasks(); } catch (e: any) { alert(e.message || "Failed to assign task"); } finally { setActionLoading(null); } };
  const handleBulkAssign = async () => { if (!bulkAssignee) return; try { await bulkAssignTasks(Array.from(selectedIds), Number(bulkAssignee)); setSelectedIds(new Set()); setShowBulkAssign(false); setBulkAssignee(""); await fetchTasks(); } catch (e: any) { alert(e.message || "Bulk assign failed"); } };
  const handleBulkStatusUpdate = async () => { if (!bulkStatus) return; try { await bulkUpdateTaskStatus(Array.from(selectedIds), bulkStatus); setSelectedIds(new Set()); setShowBulkStatus(false); setBulkStatus(""); await fetchTasks(); } catch (e: any) { alert(e.message || "Bulk status update failed"); } };
  const handleCreateTask = async () => { if (!createForm.title.trim() || !createForm.company_id) return; setCreateLoading(true); try { const payload: any = { company_id: Number(createForm.company_id), task_type: createForm.task_type, title: createForm.title.trim(), description: createForm.description.trim() || undefined, priority: createForm.priority }; if (createForm.assigned_to) payload.assigned_to = Number(createForm.assigned_to); if (createForm.due_date) payload.due_date = createForm.due_date; if (createForm.parent_task_id) payload.parent_task_id = Number(createForm.parent_task_id); await createFilingTask(payload); setShowCreateModal(false); setCreateForm({ company_id: "", task_type: "other", title: "", description: "", priority: "normal", assigned_to: "", due_date: "", parent_task_id: "" }); await fetchTasks(); alert("Task created successfully."); } catch (e: any) { alert(e.message || "Failed to create task"); } finally { setCreateLoading(false); } };

  const toggleSelect = (id: number) => { setSelectedIds((prev) => { const next = new Set(prev); if (next.has(id)) next.delete(id); else next.add(id); return next; }); };
  const toggleSelectAll = () => { if (selectedIds.size === tasks.length) setSelectedIds(new Set()); else setSelectedIds(new Set(tasks.map((t) => t.id))); };
  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));

  return (
    <div className="p-6 lg:p-8 max-w-full relative">
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>Filing Tasks</h1>
          <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>Manage, assign, and track all filing tasks across companies.</p>
        </div>
        <button onClick={() => setShowCreateModal(true)} className="px-4 py-2 rounded-lg text-sm font-medium hover:bg-purple-500 transition-colors flex-shrink-0" style={{ background: "var(--color-accent-purple)", color: "var(--color-text-primary)" }}>+ Create Task</button>
      </div>

      <div className="glass-card p-4 mb-6">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex flex-col gap-1"><label className="text-[10px] uppercase tracking-wider font-medium" style={{ color: "var(--color-text-muted)" }}>Status</label><select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} className="rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-purple-500/50 min-w-[160px]" style={{ background: "var(--color-bg-secondary)", borderColor: "var(--color-border)", color: "var(--color-text-primary)", border: "1px solid var(--color-border)" }}><option value="">All Statuses</option>{STATUS_OPTIONS.map((s) => (<option key={s} value={s}>{humanize(s)}</option>))}</select></div>
          <div className="flex flex-col gap-1"><label className="text-[10px] uppercase tracking-wider font-medium" style={{ color: "var(--color-text-muted)" }}>Priority</label><select value={filterPriority} onChange={(e) => setFilterPriority(e.target.value)} className="rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-purple-500/50 min-w-[140px]" style={{ background: "var(--color-bg-secondary)", borderColor: "var(--color-border)", color: "var(--color-text-primary)", border: "1px solid var(--color-border)" }}><option value="">All Priorities</option>{PRIORITY_OPTIONS.map((p) => (<option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>))}</select></div>
          <div className="flex flex-col gap-1"><label className="text-[10px] uppercase tracking-wider font-medium" style={{ color: "var(--color-text-muted)" }}>Assigned To</label><select value={filterAssignee} onChange={(e) => setFilterAssignee(e.target.value)} className="rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-purple-500/50 min-w-[160px]" style={{ background: "var(--color-bg-secondary)", borderColor: "var(--color-border)", color: "var(--color-text-primary)", border: "1px solid var(--color-border)" }}><option value="">All Team Members</option>{staff.map((s: any) => (<option key={s.id} value={s.id}>{s.full_name || s.email}</option>))}</select></div>
          <div className="flex flex-col gap-1"><label className="text-[10px] uppercase tracking-wider font-medium" style={{ color: "var(--color-text-muted)" }}>Overdue Only</label><button onClick={() => setOverdueOnly(!overdueOnly)} className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors ${overdueOnly ? "bg-red-500/15 border-red-500/30" : "hover:border-gray-600"}`} style={overdueOnly ? { color: "var(--color-error)" } : { background: "var(--color-bg-secondary)", borderColor: "var(--color-border)", color: "var(--color-text-secondary)" }}>{overdueOnly ? "Showing Overdue" : "Off"}</button></div>
        </div>
      </div>

      <div className="rounded-xl overflow-hidden" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
        {loading ? (<div className="p-12 flex items-center justify-center"><div className="animate-pulse" style={{ color: "var(--color-text-muted)" }}>Loading tasks...</div></div>) : tasks.length === 0 ? (<div className="p-12 text-center" style={{ color: "var(--color-text-muted)" }}><p className="text-sm">No filing tasks match your filters.</p></div>) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr style={{ borderBottom: "1px solid var(--color-border)" }}><th className="px-4 py-3 text-left"><input type="checkbox" checked={selectedIds.size === tasks.length && tasks.length > 0} onChange={toggleSelectAll} className="rounded border-gray-600 text-purple-500 focus:ring-purple-500/30" style={{ background: "var(--color-bg-card)" }} /></th><th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Title</th><th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Company</th><th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Type</th><th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Priority</th><th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Status</th><th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Assignee</th><th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Due Date</th><th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Actions</th></tr></thead>
              <tbody className="divide-y divide-gray-700/50">
                {tasks.map((task: any) => {
                  const overdue = isOverdue(task.due_date) && task.status !== "completed" && task.status !== "cancelled";
                  const priorityBadge = PRIORITY_BADGES[task.priority] || PRIORITY_BADGES.normal;
                  const statusBadge = STATUS_BADGE_STYLES[task.status] || STATUS_BADGE_STYLES.unassigned;
                  const isTaskLoading = actionLoading === task.id;
                  const availableTransitions = NEXT_STATUS_OPTIONS[task.status] || [];
                  return (
                    <tr key={task.id} className={`transition-colors ${overdue ? "bg-red-500/[0.03]" : ""} ${selectedIds.has(task.id) ? "bg-purple-500/[0.05]" : ""}`}>
                      <td className="px-4 py-3"><input type="checkbox" checked={selectedIds.has(task.id)} onChange={() => toggleSelect(task.id)} className="rounded border-gray-600 text-purple-500 focus:ring-purple-500/30" style={{ background: "var(--color-bg-card)" }} /></td>
                      <td className="px-4 py-3"><Link href={`/ops/tasks/${task.id}`} className="text-sm font-medium hover:text-purple-400 transition-colors" style={{ color: "var(--color-text-primary)" }}>{task.title}</Link></td>
                      <td className="px-4 py-3"><span className="text-sm truncate max-w-[180px] block" style={{ color: "var(--color-text-primary)" }}>{task.company_name || "--"}</span></td>
                      <td className="px-4 py-3"><span className="text-xs capitalize" style={{ color: "var(--color-text-secondary)" }}>{humanize(task.task_type || "")}</span></td>
                      <td className="px-4 py-3"><span className={`text-[10px] font-semibold px-2 py-0.5 rounded border uppercase tracking-wide ${priorityBadge.bg} ${priorityBadge.border}`} style={{ color: priorityBadge.color }}>{task.priority}</span></td>
                      <td className="px-4 py-3"><span className={`text-[11px] font-medium px-2 py-0.5 rounded border capitalize ${statusBadge.bg} ${statusBadge.border}`} style={{ color: statusBadge.color }}>{humanize(task.status || "")}</span></td>
                      <td className="px-4 py-3">{task.assignee_name ? <span className="text-sm" style={{ color: "var(--color-text-primary)" }}>{task.assignee_name}</span> : <span className="text-xs italic" style={{ color: "var(--color-text-muted)" }}>Unassigned</span>}</td>
                      <td className="px-4 py-3"><span className={`text-xs font-mono ${overdue ? "font-semibold" : ""}`} style={{ color: overdue ? "var(--color-error)" : "var(--color-text-secondary)" }}>{formatDate(task.due_date)}{overdue && <span className="ml-1.5 text-[10px] bg-red-500/15 border border-red-500/30 px-1.5 py-0.5 rounded" style={{ color: "var(--color-error)" }}>OVERDUE</span>}</span></td>
                      <td className="px-4 py-3">
                        <div className="flex items-center justify-end gap-1.5 relative">
                          {isTaskLoading && <span className="text-[10px] animate-pulse mr-1" style={{ color: "var(--color-text-muted)" }}>...</span>}
                          {(task.status === "unassigned" || (!task.assigned_to && !task.assignee_name)) && task.status !== "completed" && task.status !== "cancelled" && <button onClick={() => handleClaim(task.id)} disabled={isTaskLoading} className="text-xs px-2.5 py-1 rounded bg-purple-500/15 hover:bg-purple-500/25 transition-colors disabled:opacity-40 border border-purple-500/20" style={{ color: "var(--color-accent-purple-light)" }}>Claim</button>}
                          {availableTransitions.length > 0 && (
                            <div className="relative">
                              <button onClick={() => setStatusDropdownTaskId(statusDropdownTaskId === task.id ? null : task.id)} disabled={isTaskLoading} className="text-xs px-2.5 py-1 rounded bg-white/5 hover:bg-white/10 transition-colors disabled:opacity-40" style={{ color: "var(--color-text-secondary)", borderColor: "var(--color-border)", border: "1px solid var(--color-border)" }}>Status</button>
                              {statusDropdownTaskId === task.id && <div className="absolute right-0 top-full mt-1 z-50 rounded-lg shadow-xl py-1 min-w-[180px]" style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)" }}>{availableTransitions.map((s) => <button key={s} onClick={() => handleStatusUpdate(task.id, s)} className="block w-full text-left px-3 py-2 text-xs transition-colors capitalize" style={{ color: STATUS_COLORS[s] || "var(--color-text-secondary)" }}>{humanize(s)}</button>)}</div>}
                            </div>
                          )}
                          {task.status !== "completed" && task.status !== "cancelled" && (
                            <div className="relative">
                              <button onClick={() => setAssignModalTaskId(assignModalTaskId === task.id ? null : task.id)} disabled={isTaskLoading} className="text-xs px-2.5 py-1 rounded bg-blue-500/10 hover:bg-blue-500/20 transition-colors disabled:opacity-40 border border-blue-500/20" style={{ color: "var(--color-info)" }}>Assign</button>
                              {assignModalTaskId === task.id && <div className="absolute right-0 top-full mt-1 z-50 rounded-lg shadow-xl py-1 min-w-[200px] max-h-[240px] overflow-y-auto" style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)" }}>{staff.length === 0 ? <p className="px-3 py-2 text-xs" style={{ color: "var(--color-text-muted)" }}>No staff available</p> : staff.map((s: any) => <button key={s.id} onClick={() => handleAssign(task.id, s.id)} className="block w-full text-left px-3 py-2 text-xs transition-colors" style={{ color: "var(--color-text-primary)" }}><span className="font-medium" style={{ color: "var(--color-text-primary)" }}>{s.full_name || s.email}</span>{s.department && <span className="ml-2" style={{ color: "var(--color-text-muted)" }}>{s.department}</span>}</button>)}</div>}
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

      {!loading && tasks.length > 0 && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>Showing {page * PAGE_SIZE + 1} - {Math.min((page + 1) * PAGE_SIZE, totalCount)} of {totalCount} tasks</p>
          <div className="flex items-center gap-1">
            <button onClick={() => setPage(0)} disabled={page === 0} className="px-2.5 py-1.5 rounded text-xs transition-colors disabled:opacity-30 disabled:cursor-not-allowed" style={{ color: "var(--color-text-secondary)", borderColor: "var(--color-border)", border: "1px solid var(--color-border)" }}>First</button>
            <button onClick={() => setPage((p) => Math.max(0, p - 1))} disabled={page === 0} className="px-2.5 py-1.5 rounded text-xs transition-colors disabled:opacity-30 disabled:cursor-not-allowed" style={{ color: "var(--color-text-secondary)", borderColor: "var(--color-border)", border: "1px solid var(--color-border)" }}>Prev</button>
            {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => { let pageNum: number; if (totalPages <= 5) pageNum = i; else if (page < 3) pageNum = i; else if (page > totalPages - 4) pageNum = totalPages - 5 + i; else pageNum = page - 2 + i; return (<button key={pageNum} onClick={() => setPage(pageNum)} className={`px-3 py-1.5 rounded text-xs font-medium transition-colors border ${page === pageNum ? "bg-purple-500/20 border-purple-500/30" : ""}`} style={page === pageNum ? { color: "var(--color-accent-purple-light)" } : { color: "var(--color-text-secondary)", borderColor: "var(--color-border)" }}>{pageNum + 1}</button>); })}
            <button onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))} disabled={page >= totalPages - 1} className="px-2.5 py-1.5 rounded text-xs transition-colors disabled:opacity-30 disabled:cursor-not-allowed" style={{ color: "var(--color-text-secondary)", borderColor: "var(--color-border)", border: "1px solid var(--color-border)" }}>Next</button>
            <button onClick={() => setPage(totalPages - 1)} disabled={page >= totalPages - 1} className="px-2.5 py-1.5 rounded text-xs transition-colors disabled:opacity-30 disabled:cursor-not-allowed" style={{ color: "var(--color-text-secondary)", borderColor: "var(--color-border)", border: "1px solid var(--color-border)" }}>Last</button>
          </div>
        </div>
      )}

      {selectedIds.size > 0 && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
          <div className="rounded-xl shadow-2xl shadow-black/50 px-6 py-3 flex items-center gap-4" style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)" }}>
            <span className="text-sm" style={{ color: "var(--color-text-primary)" }}><span className="font-bold" style={{ color: "var(--color-accent-purple-light)" }}>{selectedIds.size}</span> task{selectedIds.size > 1 ? "s" : ""} selected</span>
            <div className="w-px h-6" style={{ background: "var(--color-border)" }} />
            <div className="relative"><button onClick={() => { setShowBulkAssign(!showBulkAssign); setShowBulkStatus(false); }} className="text-xs px-3 py-1.5 rounded-lg bg-blue-500/15 hover:bg-blue-500/25 transition-colors border border-blue-500/25 font-medium" style={{ color: "var(--color-info)" }}>Bulk Assign</button>{showBulkAssign && <div className="absolute bottom-full mb-2 left-0 rounded-lg shadow-xl p-3 min-w-[240px]" style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)" }}><p className="text-xs mb-2 font-medium" style={{ color: "var(--color-text-secondary)" }}>Assign {selectedIds.size} task{selectedIds.size > 1 ? "s" : ""} to:</p><select value={bulkAssignee} onChange={(e) => setBulkAssignee(e.target.value)} className="w-full rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-purple-500/50 mb-2" style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}><option value="">Select team member...</option>{staff.map((s: any) => <option key={s.id} value={s.id}>{s.full_name || s.email}</option>)}</select><div className="flex gap-2"><button onClick={handleBulkAssign} disabled={!bulkAssignee} className="flex-1 text-xs px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-500 transition-colors disabled:opacity-40 font-medium" style={{ color: "var(--color-text-primary)" }}>Assign</button><button onClick={() => { setShowBulkAssign(false); setBulkAssignee(""); }} className="text-xs px-3 py-1.5 rounded transition-colors" style={{ background: "var(--color-bg-card)", color: "var(--color-text-secondary)" }}>Cancel</button></div></div>}</div>
            <div className="relative"><button onClick={() => { setShowBulkStatus(!showBulkStatus); setShowBulkAssign(false); }} className="text-xs px-3 py-1.5 rounded-lg bg-amber-500/15 hover:bg-amber-500/25 transition-colors border border-amber-500/25 font-medium" style={{ color: "var(--color-warning)" }}>Bulk Update Status</button>{showBulkStatus && <div className="absolute bottom-full mb-2 right-0 rounded-lg shadow-xl p-3 min-w-[240px]" style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)" }}><p className="text-xs mb-2 font-medium" style={{ color: "var(--color-text-secondary)" }}>Set status for {selectedIds.size} task{selectedIds.size > 1 ? "s" : ""}:</p><select value={bulkStatus} onChange={(e) => setBulkStatus(e.target.value)} className="w-full rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-purple-500/50 mb-2" style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}><option value="">Select status...</option>{STATUS_OPTIONS.map((s) => <option key={s} value={s}>{humanize(s)}</option>)}</select><div className="flex gap-2"><button onClick={handleBulkStatusUpdate} disabled={!bulkStatus} className="flex-1 text-xs px-3 py-1.5 rounded bg-amber-600 hover:bg-amber-500 transition-colors disabled:opacity-40 font-medium" style={{ color: "var(--color-text-primary)" }}>Update</button><button onClick={() => { setShowBulkStatus(false); setBulkStatus(""); }} className="text-xs px-3 py-1.5 rounded transition-colors" style={{ background: "var(--color-bg-card)", color: "var(--color-text-secondary)" }}>Cancel</button></div></div>}</div>
            <div className="w-px h-6" style={{ background: "var(--color-border)" }} />
            <button onClick={() => setSelectedIds(new Set())} className="text-xs transition-colors" style={{ color: "var(--color-text-muted)" }}>Clear</button>
          </div>
        </div>
      )}

      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center"><div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setShowCreateModal(false)} /><div className="relative rounded-xl shadow-2xl shadow-black/50 w-full max-w-lg mx-4 p-6 max-h-[90vh] overflow-y-auto" style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)" }}><h3 className="text-lg font-bold mb-1" style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}>Create Filing Task</h3><p className="text-sm mb-5" style={{ color: "var(--color-text-secondary)" }}>Fill in the details below to create a new filing task.</p><div className="space-y-4"><div><label className="text-[10px] uppercase tracking-wider font-medium block mb-1.5" style={{ color: "var(--color-text-muted)" }}>Company ID <span style={{ color: "var(--color-error)" }}>*</span></label><input type="number" value={createForm.company_id} onChange={(e) => setCreateForm({ ...createForm, company_id: e.target.value })} className="w-full rounded-lg px-3 py-2 text-sm placeholder-gray-600 focus:outline-none focus:border-purple-500/50" style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }} placeholder="e.g. 1" /></div><div><label className="text-[10px] uppercase tracking-wider font-medium block mb-1.5" style={{ color: "var(--color-text-muted)" }}>Task Type <span style={{ color: "var(--color-error)" }}>*</span></label><select value={createForm.task_type} onChange={(e) => setCreateForm({ ...createForm, task_type: e.target.value })} className="w-full rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-purple-500/50" style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}>{TASK_TYPE_OPTIONS.map((t) => <option key={t} value={t}>{humanize(t)}</option>)}</select></div><div><label className="text-[10px] uppercase tracking-wider font-medium block mb-1.5" style={{ color: "var(--color-text-muted)" }}>Title <span style={{ color: "var(--color-error)" }}>*</span></label><input type="text" value={createForm.title} onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })} className="w-full rounded-lg px-3 py-2 text-sm placeholder-gray-600 focus:outline-none focus:border-purple-500/50" style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }} placeholder="Task title" /></div><div><label className="text-[10px] uppercase tracking-wider font-medium block mb-1.5" style={{ color: "var(--color-text-muted)" }}>Description</label><textarea value={createForm.description} onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })} rows={3} className="w-full rounded-lg px-3 py-2 text-sm placeholder-gray-600 focus:outline-none focus:border-purple-500/50 resize-none" style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }} placeholder="Optional description" /></div><div><label className="text-[10px] uppercase tracking-wider font-medium block mb-1.5" style={{ color: "var(--color-text-muted)" }}>Priority</label><select value={createForm.priority} onChange={(e) => setCreateForm({ ...createForm, priority: e.target.value })} className="w-full rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-purple-500/50" style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}>{PRIORITY_OPTIONS.map((p) => <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>)}</select></div><div><label className="text-[10px] uppercase tracking-wider font-medium block mb-1.5" style={{ color: "var(--color-text-muted)" }}>Assigned To (optional)</label><select value={createForm.assigned_to} onChange={(e) => setCreateForm({ ...createForm, assigned_to: e.target.value })} className="w-full rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-purple-500/50" style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}><option value="">Unassigned</option>{staff.map((s: any) => <option key={s.id} value={s.id}>{s.full_name || s.email}</option>)}</select></div><div><label className="text-[10px] uppercase tracking-wider font-medium block mb-1.5" style={{ color: "var(--color-text-muted)" }}>Due Date (optional)</label><input type="date" value={createForm.due_date} onChange={(e) => setCreateForm({ ...createForm, due_date: e.target.value })} className="w-full rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-purple-500/50" style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }} /></div><div><label className="text-[10px] uppercase tracking-wider font-medium block mb-1.5" style={{ color: "var(--color-text-muted)" }}>Parent Task ID (optional)</label><input type="number" value={createForm.parent_task_id} onChange={(e) => setCreateForm({ ...createForm, parent_task_id: e.target.value })} className="w-full rounded-lg px-3 py-2 text-sm placeholder-gray-600 focus:outline-none focus:border-purple-500/50" style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }} placeholder="e.g. 5" /></div></div><div className="flex gap-3 justify-end mt-6"><button onClick={() => setShowCreateModal(false)} className="text-xs px-4 py-2 rounded-lg transition-colors font-medium" style={{ background: "var(--color-bg-card)", color: "var(--color-text-secondary)" }}>Cancel</button><button onClick={handleCreateTask} disabled={createLoading || !createForm.title.trim() || !createForm.company_id} className="text-xs px-4 py-2 rounded-lg hover:bg-purple-500 transition-colors disabled:opacity-40 font-medium" style={{ background: "var(--color-accent-purple)", color: "var(--color-text-primary)" }}>{createLoading ? "Creating..." : "Create Task"}</button></div></div></div>
      )}

      {(statusDropdownTaskId !== null || assignModalTaskId !== null) && <div className="fixed inset-0 z-40" onClick={() => { setStatusDropdownTaskId(null); setAssignModalTaskId(null); }} />}
    </div>
  );
}
