"use client";

import { useState, useEffect } from "react";
import { getComplianceOverview, getComplianceTasks, adminUpdateComplianceTask } from "@/lib/api";

const STATUS_OPTIONS = [
  { value: "", label: "All" },
  { value: "overdue", label: "Overdue" },
  { value: "due_soon", label: "Due Soon" },
  { value: "in_progress", label: "In Progress" },
  { value: "upcoming", label: "Upcoming" },
  { value: "completed", label: "Completed" },
];

const STATUS_STYLES: Record<string, string> = {
  overdue: "background: var(--color-error-light); color: var(--color-error)",
  due_soon: "background: var(--color-warning-light); color: var(--color-warning)",
  in_progress: "background: var(--color-info-light); color: var(--color-info)",
  upcoming: "background: rgba(139, 92, 246, 0.08); color: var(--color-text-secondary)",
  completed: "background: var(--color-success-light); color: var(--color-success)",
  not_applicable: "background: rgba(148,163,184,0.1); color: var(--color-text-muted)",
};

const TASK_STATUS_UPDATE_OPTIONS = [
  { value: "in_progress", label: "In Progress" },
  { value: "completed", label: "Completed" },
  { value: "not_applicable", label: "N/A" },
];

export default function ComplianceWorkflowPage() {
  const [overview, setOverview] = useState<any>(null);
  const [tasks, setTasks] = useState<any[]>([]);
  const [totalTasks, setTotalTasks] = useState(0);
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "tasks">("overview");

  const loadOverview = async () => {
    try {
      const data = await getComplianceOverview();
      setOverview(data);
    } catch (err) {
      console.error("Failed to load compliance overview:", err);
    }
  };

  const loadTasks = async () => {
    try {
      const data = await getComplianceTasks({ status: statusFilter || undefined, limit: 100 });
      setTasks(data.tasks);
      setTotalTasks(data.total);
    } catch (err) {
      console.error("Failed to load compliance tasks:", err);
    }
  };

  const loadAll = async () => {
    setLoading(true);
    await Promise.all([loadOverview(), loadTasks()]);
    setLoading(false);
  };

  useEffect(() => { loadAll(); }, []);
  useEffect(() => { loadTasks(); }, [statusFilter]);

  const handleStatusUpdate = async (taskId: number, newStatus: string) => {
    setUpdatingId(taskId);
    try {
      await adminUpdateComplianceTask(taskId, { status: newStatus });
      await loadAll();
    } catch (err) {
      console.error("Task update failed:", err);
    } finally {
      setUpdatingId(null);
    }
  };

  const parseStyleString = (str: string) => {
    if (!str) return {};
    return Object.fromEntries(str.split("; ").map(s => { const [k, v] = s.split(": "); return [k, v]; }));
  };

  return (
    <div className="p-6 lg:p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold" style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}>
          Compliance Workflow
        </h1>
        <p className="text-sm mt-1" style={{ color: "var(--color-text-secondary)" }}>
          Cross-company compliance tracking, deadlines, and penalty management
        </p>
      </div>

      {/* Summary Cards */}
      {overview?.summary && (
        <div className="grid grid-cols-2 lg:grid-cols-4 xl:grid-cols-7 gap-4 mb-8">
          {[
            { label: "Total Tasks", value: overview.summary.total_tasks, color: "var(--color-text-primary)" },
            { label: "Overdue", value: overview.summary.overdue, color: "var(--color-error)" },
            { label: "Due Soon", value: overview.summary.due_soon, color: "var(--color-warning)" },
            { label: "In Progress", value: overview.summary.in_progress, color: "var(--color-info)" },
            { label: "Completed", value: overview.summary.completed, color: "var(--color-success)" },
            { label: "Companies", value: overview.summary.companies_tracked, color: "var(--color-accent-purple)" },
            { label: "Penalty Exposure", value: `Rs ${(overview.summary.total_penalty_exposure || 0).toLocaleString("en-IN")}`, color: overview.summary.total_penalty_exposure > 0 ? "var(--color-error)" : "var(--color-success)" },
          ].map((card, i) => (
            <div key={i} className="glass-card rounded-xl p-4">
              <p className="text-[10px] mb-1" style={{ color: "var(--color-text-muted)" }}>{card.label}</p>
              <p className="text-xl font-bold" style={{ color: card.color }}>{card.value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 glass-card rounded-lg p-1 w-fit mb-6">
        {[
          { key: "overview" as const, label: "Company Scores" },
          { key: "tasks" as const, label: `All Tasks (${totalTasks})` },
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className="px-4 py-2 rounded-md text-sm font-medium transition"
            style={activeTab === tab.key
              ? { background: "var(--color-accent-purple)", color: "#fff" }
              : { color: "var(--color-text-secondary)" }
            }
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "overview" && (
        <>
          {/* Overdue by Company */}
          {overview?.overdue_by_company && overview.overdue_by_company.length > 0 && (
            <div className="glass-card rounded-xl p-5 mb-6">
              <h2 className="text-sm font-semibold mb-3" style={{ color: "var(--color-error)" }}>
                Overdue Tasks by Company ({overview.overdue_by_company.length} companies)
              </h2>
              <div className="space-y-3">
                {overview.overdue_by_company.map((group: any) => (
                  <div key={group.company_id} className="p-3 rounded-lg" style={{ background: "rgba(239, 68, 68, 0.03)", border: "1px solid rgba(239, 68, 68, 0.15)" }}>
                    <p className="text-xs font-semibold mb-2" style={{ color: "var(--color-text-primary)" }}>
                      {group.company_name}
                      <span className="ml-2 text-[10px] font-normal" style={{ color: "var(--color-text-muted)" }}>
                        ({group.tasks.length} overdue)
                      </span>
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {group.tasks.map((task: any) => (
                        <div key={task.id} className="text-[10px] px-2 py-1 rounded" style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)" }}>
                          <span style={{ color: "var(--color-text-primary)" }}>{task.title}</span>
                          <span className="ml-1 font-bold" style={{ color: "var(--color-error)" }}>({task.days_overdue}d overdue)</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Company Compliance Scores */}
          {overview?.company_scores && overview.company_scores.length > 0 && (
            <div className="glass-card rounded-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                    {["Company", "Entity Type", "Score", "Grade", "Overdue", "Penalty Exposure"].map(h => (
                      <th key={h} className="text-left px-4 py-3 text-xs font-medium" style={{ color: "var(--color-text-muted)" }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {overview.company_scores.map((cs: any) => (
                    <tr key={cs.company_id} style={{ borderBottom: "1px solid var(--color-border)" }}>
                      <td className="px-4 py-3">
                        <p className="text-xs font-medium" style={{ color: "var(--color-text-primary)" }}>{cs.company_name}</p>
                        <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>#{cs.company_id}</p>
                      </td>
                      <td className="px-4 py-3 text-xs capitalize" style={{ color: "var(--color-text-secondary)" }}>
                        {cs.entity_type?.replace(/_/g, " ")}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-1.5 rounded-full overflow-hidden" style={{ background: "var(--color-border)" }}>
                            <div
                              className="h-full rounded-full"
                              style={{
                                width: `${cs.score}%`,
                                background: cs.score >= 80 ? "var(--color-success)" : cs.score >= 50 ? "var(--color-warning)" : "var(--color-error)",
                              }}
                            />
                          </div>
                          <span className="text-xs font-bold" style={{
                            color: cs.score >= 80 ? "var(--color-success)" : cs.score >= 50 ? "var(--color-warning)" : "var(--color-error)",
                          }}>
                            {cs.score}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm font-bold" style={{
                        color: cs.grade.startsWith("A") ? "var(--color-success)" : cs.grade === "F" ? "var(--color-error)" : "var(--color-warning)",
                      }}>
                        {cs.grade}
                      </td>
                      <td className="px-4 py-3 text-xs font-semibold" style={{ color: cs.overdue_count > 0 ? "var(--color-error)" : "var(--color-text-muted)" }}>
                        {cs.overdue_count}
                      </td>
                      <td className="px-4 py-3 text-xs font-semibold" style={{ color: cs.penalty_exposure > 0 ? "var(--color-error)" : "var(--color-success)" }}>
                        Rs {(cs.penalty_exposure || 0).toLocaleString("en-IN")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {loading && (
            <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>Loading...</div>
          )}

          {!loading && (!overview?.company_scores || overview.company_scores.length === 0) && (
            <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>
              No compliance tasks found. Tasks are generated when companies are incorporated.
            </div>
          )}
        </>
      )}

      {activeTab === "tasks" && (
        <>
          {/* Status Filter */}
          <div className="flex flex-wrap gap-2 mb-4">
            {STATUS_OPTIONS.map(opt => (
              <button
                key={opt.value}
                onClick={() => setStatusFilter(opt.value)}
                className="px-3 py-1.5 rounded-full text-xs font-medium transition"
                style={statusFilter === opt.value
                  ? { background: "var(--color-accent-purple)", color: "#fff" }
                  : { background: "var(--color-bg-card)", color: "var(--color-text-secondary)", border: "1px solid var(--color-border)" }
                }
              >
                {opt.label}
              </button>
            ))}
          </div>

          {/* Tasks Table */}
          {loading ? (
            <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>Loading...</div>
          ) : tasks.length === 0 ? (
            <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>
              No compliance tasks found for this filter.
            </div>
          ) : (
            <div className="glass-card rounded-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                    {["ID", "Company", "Task", "Type", "Due Date", "Status", "Actions"].map(h => (
                      <th key={h} className="text-left px-4 py-3 text-xs font-medium" style={{ color: "var(--color-text-muted)" }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {tasks.map(task => (
                    <tr key={task.id} style={{ borderBottom: "1px solid var(--color-border)" }}>
                      <td className="px-4 py-3 text-xs" style={{ color: "var(--color-text-muted)" }}>#{task.id}</td>
                      <td className="px-4 py-3">
                        <p className="font-medium text-xs" style={{ color: "var(--color-text-primary)" }}>{task.company_name}</p>
                      </td>
                      <td className="px-4 py-3">
                        <p className="text-xs font-medium" style={{ color: "var(--color-text-primary)" }}>{task.title}</p>
                        {task.description && (
                          <p className="text-[10px] mt-0.5 truncate max-w-[200px]" style={{ color: "var(--color-text-muted)" }}>{task.description}</p>
                        )}
                      </td>
                      <td className="px-4 py-3 text-xs" style={{ color: "var(--color-text-secondary)" }}>
                        {task.task_type?.replace(/_/g, " ")}
                      </td>
                      <td className="px-4 py-3 text-xs" style={{ color: "var(--color-text-secondary)" }}>
                        {task.due_date ? new Date(task.due_date).toLocaleDateString("en-IN") : "-"}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
                          style={STATUS_STYLES[task.status] ? parseStyleString(STATUS_STYLES[task.status]) : {}}
                        >
                          {task.status?.replace(/_/g, " ")}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        {task.status !== "completed" && task.status !== "not_applicable" && (
                          <select
                            value=""
                            onChange={e => { if (e.target.value) handleStatusUpdate(task.id, e.target.value); }}
                            disabled={updatingId === task.id}
                            className="text-[10px] rounded px-1 py-0.5"
                            style={{ background: "var(--color-bg-input)", color: "var(--color-text-primary)", border: "1px solid var(--color-border)" }}
                          >
                            <option value="">Update...</option>
                            {TASK_STATUS_UPDATE_OPTIONS.map(opt => (
                              <option key={opt.value} value={opt.value}>{opt.label}</option>
                            ))}
                          </select>
                        )}
                        {task.filing_reference && (
                          <p className="text-[10px] mt-1" style={{ color: "var(--color-success)" }}>
                            Ref: {task.filing_reference}
                          </p>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}
