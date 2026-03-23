"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { useCompany } from "@/lib/company-context";
import Link from "next/link";
import UpsellBanner from "@/components/upsell-banner";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import {
  getComplianceScore,
  getComplianceCalendar,
  getUpcomingDeadlines,
  getOverdueTasks,
  generateComplianceTasks,
  updateComplianceTask,
  getPenaltyEstimate,
  calculateTds,
} from "@/lib/api";


// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ComplianceScoreData {
  score: number;
  grade: string;
  total_tasks: number;
  completed: number;
  overdue: number;
  due_soon: number;
  in_progress: number;
  upcoming: number;
  estimated_penalty_exposure: number;
  message: string;
}

interface CalendarEntry {
  type: string;
  title: string;
  description: string;
  frequency: string;
  due_date: string | null;
  days_remaining: number | null;
  status: string;
  financial_year: string;
}

interface ComplianceTaskItem {
  id: number;
  task_type: string;
  title: string;
  description: string;
  due_date: string | null;
  status: string;
  completed_date: string | null;
  filing_reference: string | null;
}

interface PenaltyDetail {
  task_type: string;
  task_title: string;
  days_overdue: number;
  estimated_penalty: number;
  description: string;
}

// ---------------------------------------------------------------------------
// Helper Components
// ---------------------------------------------------------------------------

function ScoreGauge({ score, grade }: { score: number; grade: string }) {
  const getColor = (s: number) => {
    if (s >= 90) return "var(--color-accent-emerald-light)";
    if (s >= 70) return "var(--color-accent-amber)";
    if (s >= 50) return "var(--color-accent-amber)";
    return "var(--color-accent-rose)";
  };

  const color = getColor(score);
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="relative w-36 h-36 mx-auto">
      <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
        <circle
          cx="60" cy="60" r="54"
          fill="none"
          stroke="var(--color-hover-overlay)"
          strokeWidth="10"
        />
        <circle
          cx="60" cy="60" r="54"
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 1s ease-in-out" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold" style={{ color }}>{score}</span>
        <span className="text-xs font-semibold" style={{ color: "var(--color-text-secondary)" }}>{grade}</span>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    overdue: "bg-red-500/10 text-red-400 border-red-500/30",
    due_soon: "bg-amber-500/10 text-amber-400 border-amber-500/30",
    upcoming: "bg-blue-500/10 text-blue-400 border-blue-500/30",
    completed: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
    in_progress: "bg-purple-500/10 text-purple-400 border-purple-500/30",
    not_applicable: "bg-gray-500/10 border-gray-500/30",
  };

  return (
    <span
      className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${styles[status] || styles.upcoming}`}
      style={status === "not_applicable" ? { color: "var(--color-text-secondary)" } : {}}
    >
      {status.replace(/_/g, " ").toUpperCase()}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function ComplianceDashboard() {
  const { user, loading: authLoading } = useAuth();
  const { selectedCompany } = useCompany();

  const selectedCompanyId = selectedCompany?.id ?? null;

  // Data
  const [scoreData, setScoreData] = useState<ComplianceScoreData | null>(null);
  const [calendar, setCalendar] = useState<CalendarEntry[]>([]);
  const [upcomingTasks, setUpcomingTasks] = useState<ComplianceTaskItem[]>([]);
  const [overdueTasks, setOverdueTasks] = useState<ComplianceTaskItem[]>([]);
  const [penaltyData, setPenaltyData] = useState<{ total: number; details: PenaltyDetail[] } | null>(null);

  // TDS Calculator
  const [tdsSection, setTdsSection] = useState("194J");
  const [tdsAmount, setTdsAmount] = useState("");
  const [tdsResult, setTdsResult] = useState<any>(null);

  // UI
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [activeTab, setActiveTab] = useState<"calendar" | "overdue" | "penalties" | "tds">("calendar");

  // ── Fetch compliance data when company changes ────────────────────
  useEffect(() => {
    if (!selectedCompanyId) {
      setLoading(false);
      return;
    }
    const fetchAll = async () => {
      setLoading(true);
      try {
        const [scoreRes, calRes, upRes, ovRes, penRes] = await Promise.all([
          getComplianceScore(selectedCompanyId).catch(() => null),
          getComplianceCalendar(selectedCompanyId).catch(() => ({ calendar: [] })),
          getUpcomingDeadlines(selectedCompanyId).catch(() => ({ tasks: [] })),
          getOverdueTasks(selectedCompanyId).catch(() => ({ tasks: [] })),
          getPenaltyEstimate(selectedCompanyId).catch(() => null),
        ]);
        setScoreData(scoreRes);
        setCalendar(calRes?.calendar || []);
        setUpcomingTasks(upRes?.tasks || []);
        setOverdueTasks(ovRes?.tasks || []);
        if (penRes) {
          setPenaltyData({
            total: penRes.total_estimated_penalty || 0,
            details: penRes.penalty_details || [],
          });
        }
      } catch (err) {
        console.error("Failed to fetch compliance data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, [selectedCompanyId]);

  // ── Generate compliance tasks ─────────────────────────────────────
  const handleGenerate = async () => {
    if (!selectedCompanyId) return;
    setGenerating(true);
    try {
      await generateComplianceTasks(selectedCompanyId);
      // Refresh data
      const [scoreRes, calRes, upRes, ovRes] = await Promise.all([
        getComplianceScore(selectedCompanyId).catch(() => null),
        getComplianceCalendar(selectedCompanyId).catch(() => ({ calendar: [] })),
        getUpcomingDeadlines(selectedCompanyId).catch(() => ({ tasks: [] })),
        getOverdueTasks(selectedCompanyId).catch(() => ({ tasks: [] })),
      ]);
      setScoreData(scoreRes);
      setCalendar(calRes?.calendar || []);
      setUpcomingTasks(upRes?.tasks || []);
      setOverdueTasks(ovRes?.tasks || []);
    } catch (err) {
      console.error("Failed to generate tasks:", err);
    } finally {
      setGenerating(false);
    }
  };

  // ── Mark task complete ────────────────────────────────────────────
  const handleCompleteTask = async (taskId: number) => {
    if (!selectedCompanyId) return;
    try {
      await updateComplianceTask(selectedCompanyId, taskId, { status: "completed" });
      // Refresh
      const [scoreRes, upRes, ovRes] = await Promise.all([
        getComplianceScore(selectedCompanyId).catch(() => null),
        getUpcomingDeadlines(selectedCompanyId).catch(() => ({ tasks: [] })),
        getOverdueTasks(selectedCompanyId).catch(() => ({ tasks: [] })),
      ]);
      setScoreData(scoreRes);
      setUpcomingTasks(upRes?.tasks || []);
      setOverdueTasks(ovRes?.tasks || []);
    } catch (err) {
      console.error("Failed to complete task:", err);
    }
  };

  // ── TDS Calculator ────────────────────────────────────────────────
  const handleTdsCalc = async () => {
    if (!selectedCompanyId || !tdsAmount) return;
    try {
      const result = await calculateTds(selectedCompanyId, {
        section: tdsSection,
        amount: parseFloat(tdsAmount),
      });
      setTdsResult(result);
    } catch (err) {
      console.error("TDS calc failed:", err);
    }
  };

  // ── Loading / Auth ────────────────────────────────────────────────
  if (authLoading || (loading && !scoreData)) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="animate-pulse-glow w-16 h-16 rounded-full flex items-center justify-center" style={{ background: "var(--color-purple-bg)" }}>
          <img src="/logo-icon.png" alt="Anvils" className="w-7 h-7 object-contain" />
        </div>
      </div>
    );
  }

  // ── Render ────────────────────────────────────────────────────────
  return (
    <div>
      <div className="max-w-7xl mx-auto px-6 py-8">
        {selectedCompany && <UpsellBanner pageKey="compliance" companyId={selectedCompany.id} />}
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 gap-4 animate-fade-in-up">
          <div>
            <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>
              Compliance Dashboard
            </h1>
            <p className="text-sm border-l-2 pl-3 border-purple-500" style={{ color: "var(--color-text-secondary)" }}>
              Track deadlines, filings, and compliance health for your companies.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleGenerate}
              disabled={generating || !selectedCompanyId}
              className="btn-primary text-sm !py-2 !px-4"
            >
              {generating ? "Generating..." : "Generate Tasks"}
            </button>
          </div>
        </div>

        {!selectedCompany ? (
          <div className="p-12 text-center" style={{ background: "var(--color-bg-card)" }}>
            <h2 className="text-xl font-bold mb-2" style={{ color: "var(--color-text-primary)" }}>No company selected</h2>
            <p className="text-sm mb-6" style={{ color: "var(--color-text-secondary)" }}>
              Select a company from the header to view compliance calendar and deadlines.
            </p>
            <div className="flex items-center justify-center gap-3">
              <Link href="/pricing" className="px-5 py-2.5 rounded-lg text-sm font-semibold text-white" style={{ background: "var(--color-accent-purple-light)" }}>
                Incorporate a New Company
              </Link>
              <Link href="/dashboard/connect" className="px-5 py-2.5 rounded-lg text-sm font-semibold border" style={{ borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}>
                Connect Existing Company
              </Link>
            </div>
          </div>
        ) : (
          <>
            {/* Score + Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8 animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
              {/* Score Card */}
              <div className="glass-card p-6 md:col-span-1">
                <h3 className="text-xs font-semibold uppercase tracking-wider mb-4" style={{ color: "var(--color-text-muted)" }}>
                  Compliance Score
                </h3>
                {scoreData ? (
                  <>
                    <ScoreGauge score={scoreData.score} grade={scoreData.grade} />
                    <p className="text-xs text-center mt-3" style={{ color: "var(--color-text-secondary)" }}>
                      {scoreData.message}
                    </p>
                  </>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>No data yet</p>
                    <p className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>Generate tasks to see your score</p>
                  </div>
                )}
              </div>

              {/* Stats */}
              <div className="md:col-span-3 grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="glass-card p-5">
                  <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Total Tasks</p>
                  <p className="text-3xl font-bold mt-2">{scoreData?.total_tasks || 0}</p>
                </div>
                <div className="glass-card p-5">
                  <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Completed</p>
                  <p className="text-3xl font-bold mt-2" style={{ color: "var(--color-success)" }}>{scoreData?.completed || 0}</p>
                </div>
                <div className="glass-card p-5">
                  <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Overdue</p>
                  <p className="text-3xl font-bold mt-2" style={{ color: "var(--color-error)" }}>{scoreData?.overdue || 0}</p>
                </div>
                <div className="glass-card p-5">
                  <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Due Soon</p>
                  <p className="text-3xl font-bold mt-2" style={{ color: "var(--color-warning)" }}>{scoreData?.due_soon || 0}</p>
                </div>
                <div className="glass-card p-5 md:col-span-2">
                  <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Penalty Exposure</p>
                  <p className="text-2xl font-bold mt-2" style={{ color: "var(--color-error)" }}>
                    Rs {(scoreData?.estimated_penalty_exposure || 0).toLocaleString("en-IN")}
                  </p>
                </div>
                <div className="glass-card p-5 md:col-span-2">
                  <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>In Progress</p>
                  <p className="text-3xl font-bold mt-2" style={{ color: "var(--color-info)" }}>{scoreData?.in_progress || 0}</p>
                </div>
              </div>
            </div>

            {/* Task Status Distribution Chart */}
            {scoreData && (
              <div className="glass-card p-6 mb-8 animate-fade-in-up" style={{ animationDelay: "0.15s" }}>
                <h3 className="text-xs font-semibold uppercase tracking-wider mb-4" style={{ color: "var(--color-text-muted)" }}>
                  Task Status Distribution
                </h3>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart
                    layout="vertical"
                    data={[
                      { name: "Completed", value: scoreData.completed, fill: "#10B981" },
                      { name: "Overdue", value: scoreData.overdue, fill: "#F43F5E" },
                      { name: "Due Soon", value: scoreData.due_soon, fill: "#F59E0B" },
                      { name: "In Progress", value: scoreData.in_progress, fill: "#3B82F6" },
                      { name: "Upcoming", value: scoreData.upcoming, fill: "#8B5CF6" },
                    ]}
                    margin={{ top: 0, right: 30, left: 20, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={false} />
                    <XAxis
                      type="number"
                      allowDecimals={false}
                      tick={{ fill: "#9CA3AF", fontSize: 12 }}
                      axisLine={{ stroke: "#374151" }}
                      tickLine={{ stroke: "#374151" }}
                    />
                    <YAxis
                      type="category"
                      dataKey="name"
                      width={90}
                      tick={{ fill: "#9CA3AF", fontSize: 12 }}
                      axisLine={{ stroke: "#374151" }}
                      tickLine={false}
                    />
                    <Tooltip
                      contentStyle={{
                        background: "#1a1a2e",
                        border: "1px solid rgba(255,255,255,0.1)",
                        borderRadius: 8,
                      }}
                      labelStyle={{ color: "#9CA3AF" }}
                      cursor={{ fill: "rgba(255,255,255,0.05)" }}
                    />
                    <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={24}>
                      {[
                        { name: "Completed", fill: "#10B981" },
                        { name: "Overdue", fill: "#F43F5E" },
                        { name: "Due Soon", fill: "#F59E0B" },
                        { name: "In Progress", fill: "#3B82F6" },
                        { name: "Upcoming", fill: "#8B5CF6" },
                      ].map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Tabs */}
            <div className="flex gap-1 mb-6 animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
              {(["calendar", "overdue", "penalties", "tds"] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === tab
                      ? "bg-purple-500/20 text-purple-400 border border-purple-500/30"
                      : ""
                  }`}
                  style={activeTab !== tab ? { color: "var(--color-text-secondary)" } : {}}
                >
                  {tab === "calendar" && "Compliance Calendar"}
                  {tab === "overdue" && `Overdue (${overdueTasks.length})`}
                  {tab === "penalties" && "Penalty Calculator"}
                  {tab === "tds" && "TDS Calculator"}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="animate-fade-in-up" style={{ animationDelay: "0.3s" }}>
              {/* Calendar Tab */}
              {activeTab === "calendar" && (
                <div className="glass-card p-6">
                  <h3 className="text-lg font-bold mb-4">Compliance Calendar</h3>
                  {calendar.length === 0 ? (
                    <div className="text-center py-12">
                      <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                        No calendar entries. Click &quot;Generate Tasks&quot; to populate.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {calendar.map((entry, idx) => (
                        <div
                          key={idx}
                          className={`p-4 rounded-lg border flex flex-col md:flex-row justify-between items-start md:items-center gap-3 ${
                            entry.status === "overdue"
                              ? "border-red-500/30 bg-red-500/5"
                              : entry.status === "due_soon"
                              ? "border-amber-500/30 bg-amber-500/5"
                              : ""
                          }`}
                          style={entry.status !== "overdue" && entry.status !== "due_soon" ? { borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" } : {}}
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="text-sm font-semibold">{entry.title}</h4>
                              <StatusBadge status={entry.status} />
                              <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: "var(--color-bg-card)", color: "var(--color-text-secondary)" }}>
                                {entry.frequency}
                              </span>
                            </div>
                            <p className="text-xs" style={{ color: "var(--color-text-secondary)" }}>
                              {entry.description}
                            </p>
                          </div>
                          <div className="text-right shrink-0">
                            {entry.due_date && (
                              <p className="text-sm font-mono font-semibold">
                                {new Date(entry.due_date).toLocaleDateString("en-IN", {
                                  day: "2-digit",
                                  month: "short",
                                  year: "numeric",
                                })}
                              </p>
                            )}
                            {entry.days_remaining !== null && entry.status !== "overdue" && (
                              <p className="text-[10px] mt-0.5" style={{ color: "var(--color-text-muted)" }}>
                                {entry.days_remaining} days remaining
                              </p>
                            )}
                            {entry.status === "overdue" && (
                              <p className="text-[10px] mt-0.5 font-semibold" style={{ color: "var(--color-error)" }}>
                                OVERDUE
                              </p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Overdue Tab */}
              {activeTab === "overdue" && (
                <div className="glass-card p-6">
                  <h3 className="text-lg font-bold mb-4" style={{ color: "var(--color-error)" }}>Overdue Tasks</h3>
                  {overdueTasks.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="text-4xl mb-3">&#10003;</div>
                      <p className="text-sm font-semibold" style={{ color: "var(--color-success)" }}>All clear! No overdue tasks.</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {overdueTasks.map((task) => (
                        <div
                          key={task.id}
                          className="p-4 rounded-lg border border-red-500/30 bg-red-500/5 flex flex-col md:flex-row justify-between items-start md:items-center gap-3"
                        >
                          <div className="flex-1">
                            <h4 className="text-sm font-semibold" style={{ color: "var(--color-error)" }}>{task.title}</h4>
                            <p className="text-xs mt-1" style={{ color: "var(--color-text-secondary)" }}>
                              {task.description}
                            </p>
                            {task.due_date && (
                              <p className="text-[10px] mt-1" style={{ color: "var(--color-error)" }}>
                                Was due: {new Date(task.due_date).toLocaleDateString("en-IN", {
                                  day: "2-digit",
                                  month: "short",
                                  year: "numeric",
                                })}
                              </p>
                            )}
                          </div>
                          <button
                            onClick={() => handleCompleteTask(task.id)}
                            className="text-xs font-bold text-emerald-400 hover:text-emerald-300 border border-emerald-500/30 px-3 py-1.5 rounded-lg hover:bg-emerald-500/10 transition-colors"
                          >
                            Mark Complete
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Penalties Tab */}
              {activeTab === "penalties" && (
                <div className="glass-card p-6">
                  <h3 className="text-lg font-bold mb-4">Penalty Estimates</h3>
                  {!penaltyData || penaltyData.details.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="text-4xl mb-3">&#128170;</div>
                      <p className="text-sm font-semibold" style={{ color: "var(--color-success)" }}>No penalties! All filings are on time.</p>
                    </div>
                  ) : (
                    <>
                      <div className="p-4 rounded-lg border border-red-500/30 bg-red-500/5 mb-6">
                        <p className="text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-error)" }}>
                          Total Estimated Penalty Exposure
                        </p>
                        <p className="text-3xl font-bold" style={{ color: "var(--color-error)" }}>
                          Rs {penaltyData.total.toLocaleString("en-IN")}
                        </p>
                      </div>
                      {/* Penalty Exposure Bar Chart */}
                      <div className="glass-card p-6 mb-6">
                        <h4 className="text-xs font-semibold uppercase tracking-wider mb-4" style={{ color: "var(--color-text-muted)" }}>
                          Penalty Exposure by Task
                        </h4>
                        <ResponsiveContainer width="100%" height={Math.max(180, penaltyData.details.length * 50)}>
                          <BarChart
                            layout="vertical"
                            data={penaltyData.details.map((p) => ({
                              name: p.task_title.length > 30 ? p.task_title.slice(0, 27) + "..." : p.task_title,
                              fullName: p.task_title,
                              penalty: p.estimated_penalty,
                              daysOverdue: p.days_overdue,
                            }))}
                            margin={{ top: 0, right: 30, left: 20, bottom: 0 }}
                          >
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={false} />
                            <XAxis
                              type="number"
                              tick={{ fill: "#9CA3AF", fontSize: 12 }}
                              axisLine={{ stroke: "#374151" }}
                              tickLine={{ stroke: "#374151" }}
                              tickFormatter={(v: number) => `Rs ${v.toLocaleString("en-IN")}`}
                            />
                            <YAxis
                              type="category"
                              dataKey="name"
                              width={160}
                              tick={{ fill: "#9CA3AF", fontSize: 11 }}
                              axisLine={{ stroke: "#374151" }}
                              tickLine={false}
                            />
                            <Tooltip
                              contentStyle={{
                                background: "#1a1a2e",
                                border: "1px solid rgba(255,255,255,0.1)",
                                borderRadius: 8,
                              }}
                              labelStyle={{ color: "#9CA3AF" }}
                              formatter={(value: any, _name: any, props: any) => [
                                `Rs ${Number(value).toLocaleString("en-IN")}`,
                                `${props.payload.daysOverdue} days overdue`,
                              ]}
                              labelFormatter={(_label: any, payload: any) =>
                                payload?.[0]?.payload?.fullName || _label
                              }
                              cursor={{ fill: "rgba(255,255,255,0.05)" }}
                            />
                            <Bar dataKey="penalty" radius={[0, 6, 6, 0]} barSize={24}>
                              {penaltyData.details.map((p, index) => {
                                const severity = Math.min(p.days_overdue / 90, 1);
                                const r = Math.round(244 + (220 - 244) * severity);
                                const g = Math.round(63 - 63 * severity);
                                const b = Math.round(94 - 60 * severity);
                                return (
                                  <Cell
                                    key={`penalty-cell-${index}`}
                                    fill={`rgb(${r}, ${g}, ${b})`}
                                  />
                                );
                              })}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      </div>

                      <div className="space-y-3">
                        {penaltyData.details.map((p, idx) => (
                          <div key={idx} className="p-4 rounded-lg border flex justify-between items-center" style={{ borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" }}>
                            <div>
                              <h4 className="text-sm font-semibold">{p.task_title}</h4>
                              <p className="text-xs mt-0.5" style={{ color: "var(--color-text-secondary)" }}>
                                {p.days_overdue} days overdue {p.description && `- ${p.description}`}
                              </p>
                            </div>
                            <span className="text-lg font-bold" style={{ color: "var(--color-error)" }}>
                              Rs {p.estimated_penalty.toLocaleString("en-IN")}
                            </span>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              )}

              {/* TDS Calculator Tab */}
              {activeTab === "tds" && (
                <div className="glass-card p-6">
                  <h3 className="text-lg font-bold mb-4">TDS Calculator</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div>
                      <label className="text-xs font-semibold uppercase tracking-wider block mb-2" style={{ color: "var(--color-text-muted)" }}>
                        Section
                      </label>
                      <select
                        value={tdsSection}
                        onChange={(e) => setTdsSection(e.target.value)}
                        className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                        style={{
                          background: "var(--color-bg-card)",
                          borderColor: "var(--color-border)",
                          color: "var(--color-text-primary)",
                        }}
                      >
                        <option value="194A">194A - Interest (non-securities)</option>
                        <option value="194C">194C - Contractors</option>
                        <option value="194H">194H - Commission/Brokerage</option>
                        <option value="194I">194I - Rent</option>
                        <option value="194J">194J - Professional/Technical</option>
                        <option value="194Q">194Q - Purchase of goods</option>
                        <option value="192">192 - Salary</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-xs font-semibold uppercase tracking-wider block mb-2" style={{ color: "var(--color-text-muted)" }}>
                        Amount (Rs)
                      </label>
                      <input
                        type="number"
                        value={tdsAmount}
                        onChange={(e) => setTdsAmount(e.target.value)}
                        placeholder="Enter amount"
                        className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                        style={{
                          background: "var(--color-bg-card)",
                          borderColor: "var(--color-border)",
                          color: "var(--color-text-primary)",
                        }}
                      />
                    </div>
                    <div className="flex items-end">
                      <button
                        onClick={handleTdsCalc}
                        disabled={!tdsAmount}
                        className="btn-primary text-sm !py-2 !px-6 w-full"
                      >
                        Calculate
                      </button>
                    </div>
                  </div>

                  {tdsResult && (
                    <div className="p-5 rounded-lg border border-purple-500/30 bg-purple-500/5">
                      <h4 className="text-sm font-bold mb-3">
                        Section {tdsResult.section}: {tdsResult.description}
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-[10px] uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Gross Amount</p>
                          <p className="text-lg font-bold">Rs {(tdsResult.amount || 0).toLocaleString("en-IN")}</p>
                        </div>
                        <div>
                          <p className="text-[10px] uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>TDS Rate</p>
                          <p className="text-lg font-bold">{tdsResult.tds_rate}%</p>
                        </div>
                        <div>
                          <p className="text-[10px] uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>TDS Amount</p>
                          <p className="text-lg font-bold" style={{ color: "var(--color-warning)" }}>Rs {(tdsResult.tds_amount || 0).toLocaleString("en-IN")}</p>
                        </div>
                        <div>
                          <p className="text-[10px] uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Net Payable</p>
                          <p className="text-lg font-bold" style={{ color: "var(--color-success)" }}>Rs {(tdsResult.net_payable || 0).toLocaleString("en-IN")}</p>
                        </div>
                      </div>
                      {tdsResult.note && (
                        <p className="text-xs mt-3 p-2 rounded" style={{ color: "var(--color-text-secondary)", background: "var(--color-bg-card)" }}>
                          {tdsResult.note}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Upcoming Deadlines Section */}
            {upcomingTasks.length > 0 && (
              <div className="mt-8 glass-card p-6 animate-fade-in-up" style={{ animationDelay: "0.4s" }}>
                <h3 className="text-lg font-bold mb-4">Upcoming Deadlines (Next 30 Days)</h3>
                <div className="space-y-3">
                  {upcomingTasks.map((task) => (
                    <div
                      key={task.id}
                      className="p-4 rounded-lg border border-amber-500/20 bg-amber-500/5 flex flex-col md:flex-row justify-between items-start md:items-center gap-3"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="text-sm font-semibold">{task.title}</h4>
                          <StatusBadge status={task.status} />
                        </div>
                        <p className="text-xs" style={{ color: "var(--color-text-secondary)" }}>
                          {task.description}
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        {task.due_date && (
                          <span className="text-xs font-mono">
                            {new Date(task.due_date).toLocaleDateString("en-IN", {
                              day: "2-digit",
                              month: "short",
                            })}
                          </span>
                        )}
                        <button
                          onClick={() => handleCompleteTask(task.id)}
                          className="text-xs font-bold text-emerald-400 hover:text-emerald-300 border border-emerald-500/30 px-3 py-1.5 rounded-lg hover:bg-emerald-500/10 transition-colors"
                        >
                          Done
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
