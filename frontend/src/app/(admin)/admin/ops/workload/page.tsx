"use client";

import { useEffect, useState } from "react";
import {
  getOpsWorkload,
  getAllPerformance,
  getUserPerformance,
  getOpsStaff,
  updateStaffHierarchy,
} from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface WorkloadEntry {
  user_id: number;
  full_name: string;
  email: string;
  department: string;
  seniority: string;
  active_tasks: number;
  completed_tasks: number;
  overdue_tasks: number;
  pending_reviews: number;
}

interface PerformanceEntry {
  user_id: number;
  full_name: string;
  tasks_completed: number;
  avg_turnaround_hours: number;
  sla_compliance: number;
  documents_reviewed: number;
  escalations_received: number;
  escalations_resolved: number;
}

interface StaffMember {
  id: number;
  full_name: string;
  email: string;
  role: string;
  department: string;
  seniority: string;
  reports_to: number | null;
}

type Tab = "workload" | "performance" | "hierarchy";
type PerfPeriod = 7 | 30 | 90;

const DEPARTMENTS = ["cs", "ca", "filing", "support", "admin"];
const SENIORITIES = ["junior", "mid", "senior", "lead", "head"];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function loadColor(active: number): string {
  if (active < 5) return "text-emerald-400";
  if (active <= 10) return "text-amber-400";
  return "text-red-400";
}

function loadBarColor(active: number): string {
  if (active < 5) return "bg-emerald-500";
  if (active <= 10) return "bg-amber-500";
  return "bg-red-500";
}

function slaColor(pct: number): string {
  if (pct >= 90) return "text-emerald-400";
  if (pct >= 70) return "text-amber-400";
  return "text-red-400";
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function WorkloadPage() {
  const [tab, setTab] = useState<Tab>("workload");

  // Workload state
  const [workload, setWorkload] = useState<WorkloadEntry[]>([]);
  const [workloadLoading, setWorkloadLoading] = useState(true);

  // Performance state
  const [performance, setPerformance] = useState<PerformanceEntry[]>([]);
  const [perfPeriod, setPerfPeriod] = useState<PerfPeriod>(30);
  const [perfLoading, setPerfLoading] = useState(false);

  // Staff hierarchy state
  const [staff, setStaff] = useState<StaffMember[]>([]);
  const [staffLoading, setStaffLoading] = useState(false);
  const [editedStaff, setEditedStaff] = useState<Record<number, Partial<StaffMember>>>({});
  const [savingId, setSavingId] = useState<number | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<number | null>(null);

  // ── Fetch workload ──
  useEffect(() => {
    if (tab !== "workload") return;
    let cancelled = false;

    const fetch = async () => {
      setWorkloadLoading(true);
      try {
        const data = await getOpsWorkload();
        if (!cancelled) {
          const items = Array.isArray(data) ? data : data?.workload || data?.team || [];
          setWorkload(items);
        }
      } catch (e) {
        console.error("Failed to load workload:", e);
      } finally {
        if (!cancelled) setWorkloadLoading(false);
      }
    };

    fetch();
    return () => { cancelled = true; };
  }, [tab]);

  // ── Fetch performance ──
  useEffect(() => {
    if (tab !== "performance") return;
    let cancelled = false;

    const fetch = async () => {
      setPerfLoading(true);
      try {
        const data = await getAllPerformance(perfPeriod);
        if (!cancelled) {
          const items = Array.isArray(data) ? data : data?.performance || data?.team || [];
          setPerformance(items);
        }
      } catch (e) {
        console.error("Failed to load performance:", e);
      } finally {
        if (!cancelled) setPerfLoading(false);
      }
    };

    fetch();
    return () => { cancelled = true; };
  }, [tab, perfPeriod]);

  // ── Fetch staff ──
  useEffect(() => {
    if (tab !== "hierarchy") return;
    let cancelled = false;

    const fetch = async () => {
      setStaffLoading(true);
      try {
        const data = await getOpsStaff();
        if (!cancelled) {
          const items = Array.isArray(data) ? data : data?.staff || data?.members || [];
          setStaff(items);
          setEditedStaff({});
        }
      } catch (e) {
        console.error("Failed to load staff:", e);
      } finally {
        if (!cancelled) setStaffLoading(false);
      }
    };

    fetch();
    return () => { cancelled = true; };
  }, [tab]);

  // ── Staff edit helpers ──
  const getStaffField = (member: StaffMember, field: keyof StaffMember) => {
    const edits = editedStaff[member.id];
    if (edits && field in edits) return edits[field as keyof typeof edits];
    return member[field];
  };

  const setStaffField = (id: number, field: string, value: string | number | null) => {
    setEditedStaff((prev) => ({
      ...prev,
      [id]: { ...prev[id], [field]: value },
    }));
  };

  const handleSaveStaff = async (member: StaffMember) => {
    const edits = editedStaff[member.id];
    if (!edits) return;

    setSavingId(member.id);
    try {
      const payload: { department?: string; seniority?: string; reports_to?: number } = {};
      if (edits.department !== undefined) payload.department = edits.department as string;
      if (edits.seniority !== undefined) payload.seniority = edits.seniority as string;
      if (edits.reports_to !== undefined) payload.reports_to = edits.reports_to as number;

      await updateStaffHierarchy(member.id, payload);

      // Update local state
      setStaff((prev) =>
        prev.map((s) =>
          s.id === member.id ? { ...s, ...payload } : s
        )
      );
      setEditedStaff((prev) => {
        const next = { ...prev };
        delete next[member.id];
        return next;
      });

      setSaveSuccess(member.id);
      setTimeout(() => setSaveSuccess(null), 2000);
    } catch (e) {
      console.error("Failed to update staff:", e);
    } finally {
      setSavingId(null);
    }
  };

  // ── Workload summary ──
  const totalActive = workload.reduce((s, w) => s + (w.active_tasks || 0), 0);
  const totalOverdue = workload.reduce((s, w) => s + (w.overdue_tasks || 0), 0);
  const totalUnassigned = workload.reduce((s, w) => {
    // unassigned is typically items with no user or a special marker
    return s;
  }, 0);
  // We compute max active for bar width
  const maxActive = Math.max(1, ...workload.map((w) => w.active_tasks || 0));

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  const tabs: { key: Tab; label: string }[] = [
    { key: "workload", label: "Workload" },
    { key: "performance", label: "Performance" },
    { key: "hierarchy", label: "Staff Hierarchy" },
  ];

  return (
    <div className="p-6 lg:p-8 max-w-7xl space-y-6">
      {/* ── Header ── */}
      <div>
        <h1
          className="text-3xl font-bold mb-1"
          style={{ fontFamily: "var(--font-display)" }}
        >
          Team Workload &amp; Performance
        </h1>
        <p className="text-sm text-gray-400">
          Monitor team capacity, track individual performance, and manage staff hierarchy.
        </p>
      </div>

      {/* ── Tabs ── */}
      <div className="flex gap-1 bg-white/5 rounded-lg p-1 w-fit">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              tab === t.key
                ? "bg-purple-500/20 text-purple-400 border border-purple-500/30"
                : "text-gray-400 hover:text-gray-200 hover:bg-white/5 border border-transparent"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* ================================================================== */}
      {/* WORKLOAD TAB                                                       */}
      {/* ================================================================== */}
      {tab === "workload" && (
        <>
          {workloadLoading ? (
            <div className="animate-pulse space-y-4">
              <div className="grid grid-cols-3 gap-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-20 bg-gray-800 rounded-lg" />
                ))}
              </div>
              <div className="h-64 bg-gray-800 rounded-lg" />
            </div>
          ) : (
            <>
              {/* Summary bar */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="glass-card p-5">
                  <p className="text-xs text-gray-400 uppercase tracking-wider font-medium">
                    Total Active Tasks
                  </p>
                  <p
                    className="text-3xl font-bold text-cyan-400 mt-1"
                    style={{ fontFamily: "var(--font-display)" }}
                  >
                    {totalActive}
                  </p>
                </div>
                <div className="glass-card p-5">
                  <p className="text-xs text-gray-400 uppercase tracking-wider font-medium">
                    Total Overdue
                  </p>
                  <p
                    className={`text-3xl font-bold mt-1 ${totalOverdue > 0 ? "text-red-400" : "text-emerald-400"}`}
                    style={{ fontFamily: "var(--font-display)" }}
                  >
                    {totalOverdue}
                  </p>
                </div>
                <div className="glass-card p-5">
                  <p className="text-xs text-gray-400 uppercase tracking-wider font-medium">
                    Unassigned Tasks
                  </p>
                  <p
                    className="text-3xl font-bold text-amber-400 mt-1"
                    style={{ fontFamily: "var(--font-display)" }}
                  >
                    {totalUnassigned}
                  </p>
                </div>
              </div>

              {/* Team workload table */}
              <div className="glass-card overflow-hidden">
                <div className="px-5 py-4 border-b border-gray-700/50">
                  <h2 className="text-sm font-semibold text-gray-200">
                    Team Workload ({workload.length} members)
                  </h2>
                </div>

                {workload.length === 0 ? (
                  <div className="p-10 text-center text-gray-500 text-sm">
                    No workload data available.
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-gray-700/50">
                          <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                            Name
                          </th>
                          <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                            Department
                          </th>
                          <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                            Seniority
                          </th>
                          <th className="text-center px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                            Active
                          </th>
                          <th className="text-center px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                            Completed
                          </th>
                          <th className="text-center px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                            Overdue
                          </th>
                          <th className="text-center px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                            Pending Reviews
                          </th>
                          <th className="px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider text-left">
                            Load
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-700/30">
                        {workload.map((w) => (
                          <tr
                            key={w.user_id}
                            className="hover:bg-white/[0.03] transition-colors"
                          >
                            <td className="px-5 py-3 text-gray-200 font-medium whitespace-nowrap">
                              {w.full_name}
                            </td>
                            <td className="px-5 py-3 text-gray-400 whitespace-nowrap">
                              <span className="px-2 py-0.5 rounded text-xs bg-purple-500/10 text-purple-400 border border-purple-500/20">
                                {w.department?.toUpperCase() || "--"}
                              </span>
                            </td>
                            <td className="px-5 py-3 text-gray-400 capitalize whitespace-nowrap">
                              {w.seniority || "--"}
                            </td>
                            <td className="px-5 py-3 text-center">
                              <span className={`font-bold ${loadColor(w.active_tasks)}`}>
                                {w.active_tasks}
                              </span>
                            </td>
                            <td className="px-5 py-3 text-center text-gray-300">
                              {w.completed_tasks}
                            </td>
                            <td className="px-5 py-3 text-center">
                              <span
                                className={`font-bold ${
                                  w.overdue_tasks > 0 ? "text-red-400" : "text-gray-500"
                                }`}
                              >
                                {w.overdue_tasks}
                              </span>
                            </td>
                            <td className="px-5 py-3 text-center text-gray-300">
                              {w.pending_reviews}
                            </td>
                            <td className="px-5 py-3">
                              <div className="flex items-center gap-2 min-w-[120px]">
                                <div className="flex-1 h-2.5 bg-gray-800 rounded-full overflow-hidden">
                                  <div
                                    className={`h-full rounded-full transition-all duration-500 ${loadBarColor(
                                      w.active_tasks
                                    )}`}
                                    style={{
                                      width: `${Math.min(
                                        100,
                                        Math.max(4, (w.active_tasks / maxActive) * 100)
                                      )}%`,
                                    }}
                                  />
                                </div>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </>
          )}
        </>
      )}

      {/* ================================================================== */}
      {/* PERFORMANCE TAB                                                    */}
      {/* ================================================================== */}
      {tab === "performance" && (
        <>
          {/* Period selector */}
          <div className="flex gap-2">
            {([7, 30, 90] as PerfPeriod[]).map((d) => (
              <button
                key={d}
                onClick={() => setPerfPeriod(d)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  perfPeriod === d
                    ? "bg-cyan-500/15 text-cyan-400 border border-cyan-500/30"
                    : "bg-white/5 text-gray-400 hover:text-gray-200 hover:bg-white/10 border border-transparent"
                }`}
              >
                {d} days
              </button>
            ))}
          </div>

          {perfLoading ? (
            <div className="animate-pulse space-y-4">
              <div className="h-64 bg-gray-800 rounded-lg" />
            </div>
          ) : (
            <div className="glass-card overflow-hidden">
              <div className="px-5 py-4 border-b border-gray-700/50">
                <h2 className="text-sm font-semibold text-gray-200">
                  Performance Leaderboard &mdash; Last {perfPeriod} Days
                </h2>
              </div>

              {performance.length === 0 ? (
                <div className="p-10 text-center text-gray-500 text-sm">
                  No performance data available for this period.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-700/50">
                        <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                          #
                        </th>
                        <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                          Name
                        </th>
                        <th className="text-center px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                          Completed
                        </th>
                        <th className="text-center px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                          Avg Turnaround
                        </th>
                        <th className="text-center px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                          SLA Compliance
                        </th>
                        <th className="text-center px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                          Docs Reviewed
                        </th>
                        <th className="text-center px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                          Escalations (R/Res)
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-700/30">
                      {performance.map((p, idx) => (
                        <tr
                          key={p.user_id}
                          className="hover:bg-white/[0.03] transition-colors"
                        >
                          <td className="px-5 py-3 text-gray-500 font-medium">
                            {idx + 1}
                          </td>
                          <td className="px-5 py-3 text-gray-200 font-medium whitespace-nowrap">
                            {p.full_name}
                          </td>
                          <td className="px-5 py-3 text-center">
                            <span className="font-bold text-emerald-400">
                              {p.tasks_completed}
                            </span>
                          </td>
                          <td className="px-5 py-3 text-center text-gray-300">
                            {p.avg_turnaround_hours != null
                              ? `${p.avg_turnaround_hours.toFixed(1)}h`
                              : "--"}
                          </td>
                          <td className="px-5 py-3 text-center">
                            <span
                              className={`font-bold ${slaColor(
                                p.sla_compliance ?? 0
                              )}`}
                            >
                              {p.sla_compliance != null
                                ? `${p.sla_compliance.toFixed(1)}%`
                                : "--"}
                            </span>
                          </td>
                          <td className="px-5 py-3 text-center text-gray-300">
                            {p.documents_reviewed ?? 0}
                          </td>
                          <td className="px-5 py-3 text-center whitespace-nowrap">
                            <span
                              className={
                                (p.escalations_received ?? 0) > 0
                                  ? "text-amber-400"
                                  : "text-gray-500"
                              }
                            >
                              {p.escalations_received ?? 0}
                            </span>
                            <span className="text-gray-600 mx-1">/</span>
                            <span
                              className={
                                (p.escalations_resolved ?? 0) > 0
                                  ? "text-emerald-400"
                                  : "text-gray-500"
                              }
                            >
                              {p.escalations_resolved ?? 0}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* ================================================================== */}
      {/* STAFF HIERARCHY TAB                                                */}
      {/* ================================================================== */}
      {tab === "hierarchy" && (
        <>
          {staffLoading ? (
            <div className="animate-pulse space-y-4">
              <div className="h-64 bg-gray-800 rounded-lg" />
            </div>
          ) : (
            <div className="glass-card overflow-hidden">
              <div className="px-5 py-4 border-b border-gray-700/50">
                <h2 className="text-sm font-semibold text-gray-200">
                  Staff Hierarchy ({staff.length} members)
                </h2>
              </div>

              {staff.length === 0 ? (
                <div className="p-10 text-center text-gray-500 text-sm">
                  No staff data available.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-700/50">
                        <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                          Name
                        </th>
                        <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                          Email
                        </th>
                        <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                          Role
                        </th>
                        <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                          Department
                        </th>
                        <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                          Seniority
                        </th>
                        <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                          Reports To
                        </th>
                        <th className="px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider" />
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-700/30">
                      {staff.map((member) => {
                        const hasEdits =
                          editedStaff[member.id] &&
                          Object.keys(editedStaff[member.id]).length > 0;
                        const isSaving = savingId === member.id;
                        const justSaved = saveSuccess === member.id;

                        return (
                          <tr
                            key={member.id}
                            className="hover:bg-white/[0.03] transition-colors"
                          >
                            <td className="px-5 py-3 text-gray-200 font-medium whitespace-nowrap">
                              {member.full_name}
                            </td>
                            <td className="px-5 py-3 text-gray-400 whitespace-nowrap">
                              {member.email}
                            </td>
                            <td className="px-5 py-3 text-gray-400 capitalize whitespace-nowrap">
                              {member.role?.replace(/_/g, " ") || "--"}
                            </td>
                            <td className="px-5 py-3">
                              <select
                                value={
                                  (getStaffField(member, "department") as string) || ""
                                }
                                onChange={(e) =>
                                  setStaffField(member.id, "department", e.target.value)
                                }
                                className="bg-gray-800 border border-gray-700 rounded-md px-2 py-1.5 text-xs text-gray-200 focus:outline-none focus:border-purple-500/50 transition-colors w-full min-w-[90px]"
                              >
                                <option value="">--</option>
                                {DEPARTMENTS.map((d) => (
                                  <option key={d} value={d}>
                                    {d.toUpperCase()}
                                  </option>
                                ))}
                              </select>
                            </td>
                            <td className="px-5 py-3">
                              <select
                                value={
                                  (getStaffField(member, "seniority") as string) || ""
                                }
                                onChange={(e) =>
                                  setStaffField(member.id, "seniority", e.target.value)
                                }
                                className="bg-gray-800 border border-gray-700 rounded-md px-2 py-1.5 text-xs text-gray-200 focus:outline-none focus:border-purple-500/50 transition-colors w-full min-w-[90px]"
                              >
                                <option value="">--</option>
                                {SENIORITIES.map((s) => (
                                  <option key={s} value={s}>
                                    {s.charAt(0).toUpperCase() + s.slice(1)}
                                  </option>
                                ))}
                              </select>
                            </td>
                            <td className="px-5 py-3">
                              <select
                                value={
                                  String(
                                    getStaffField(member, "reports_to") ?? ""
                                  )
                                }
                                onChange={(e) =>
                                  setStaffField(
                                    member.id,
                                    "reports_to",
                                    e.target.value ? Number(e.target.value) : null
                                  )
                                }
                                className="bg-gray-800 border border-gray-700 rounded-md px-2 py-1.5 text-xs text-gray-200 focus:outline-none focus:border-purple-500/50 transition-colors w-full min-w-[130px]"
                              >
                                <option value="">None</option>
                                {staff
                                  .filter((s) => s.id !== member.id)
                                  .map((s) => (
                                    <option key={s.id} value={s.id}>
                                      {s.full_name}
                                    </option>
                                  ))}
                              </select>
                            </td>
                            <td className="px-5 py-3">
                              {justSaved ? (
                                <span className="text-xs text-emerald-400 font-medium px-3 py-1.5">
                                  Saved
                                </span>
                              ) : (
                                <button
                                  onClick={() => handleSaveStaff(member)}
                                  disabled={!hasEdits || isSaving}
                                  className={`text-xs px-3 py-1.5 rounded-md font-medium transition-colors ${
                                    hasEdits && !isSaving
                                      ? "bg-purple-500/15 text-purple-400 border border-purple-500/30 hover:bg-purple-500/25 cursor-pointer"
                                      : "bg-white/5 text-gray-600 border border-transparent cursor-not-allowed"
                                  }`}
                                >
                                  {isSaving ? "Saving..." : "Save"}
                                </button>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
