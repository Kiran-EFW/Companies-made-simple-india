"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import Link from "next/link";
import {
  getCompanies,
  getComplianceScore,
  getComplianceCalendar,
  getUpcomingDeadlines,
  getOverdueTasks,
  generateComplianceTasks,
  updateComplianceTask,
  getPenaltyEstimate,
  calculateTds,
} from "@/lib/api";
import NotificationBell from "@/components/notification-bell";

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
    if (s >= 90) return "#10B981";
    if (s >= 70) return "#F59E0B";
    if (s >= 50) return "#F97316";
    return "#EF4444";
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
          stroke="rgba(255,255,255,0.05)"
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
        <span className="text-xs font-semibold text-gray-400">{grade}</span>
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
    not_applicable: "bg-gray-500/10 text-gray-400 border-gray-500/30",
  };

  return (
    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${styles[status] || styles.upcoming}`}>
      {status.replace(/_/g, " ").toUpperCase()}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function ComplianceDashboard() {
  const { user, loading: authLoading } = useAuth();

  // Company selection
  const [companies, setCompanies] = useState<any[]>([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState<number | null>(null);

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

  // ── Fetch companies ───────────────────────────────────────────────
  useEffect(() => {
    if (authLoading || !user) return;
    getCompanies()
      .then((comps) => {
        setCompanies(comps);
        if (comps.length > 0) {
          setSelectedCompanyId(comps[0].id);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [user, authLoading]);

  // ── Fetch compliance data when company changes ────────────────────
  useEffect(() => {
    if (!selectedCompanyId) return;
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
      <div className="min-h-screen flex items-center justify-center glow-bg">
        <div className="animate-pulse-glow w-16 h-16 rounded-full bg-purple-500/20 flex items-center justify-center">
          <span className="text-2xl">&#9889;</span>
        </div>
      </div>
    );
  }

  // ── Render ────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen glow-bg">
      {/* Nav */}
      <nav className="glass-card sticky top-0 z-50 rounded-none border-t-0 border-x-0 border-b">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/dashboard" className="flex items-center gap-2">
            <span className="text-xl">&#9889;</span>
            <span className="font-bold hidden md:block" style={{ fontFamily: "var(--font-display)" }}>CMS Prime</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-xs font-medium transition-colors hover:text-purple-400" style={{ color: "var(--color-text-secondary)" }}>
              Dashboard
            </Link>
            {user && <NotificationBell />}
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 gap-4 animate-fade-in-up">
          <div>
            <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>
              Compliance Autopilot
            </h1>
            <p className="text-sm border-l-2 pl-3 border-purple-500" style={{ color: "var(--color-text-secondary)" }}>
              Track deadlines, filings, and compliance health for your companies.
            </p>
          </div>
          <div className="flex items-center gap-3">
            {companies.length > 1 && (
              <select
                className="glass-card text-sm px-3 py-2 rounded-lg border-none outline-none"
                style={{ background: "var(--color-bg-card)", color: "var(--color-text-primary)" }}
                value={selectedCompanyId || ""}
                onChange={(e) => setSelectedCompanyId(Number(e.target.value))}
              >
                {companies.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.approved_name || c.proposed_names?.[0] || `Company #${c.id}`}
                  </option>
                ))}
              </select>
            )}
            <button
              onClick={handleGenerate}
              disabled={generating || !selectedCompanyId}
              className="btn-primary text-sm !py-2 !px-4"
            >
              {generating ? "Generating..." : "Generate Tasks"}
            </button>
          </div>
        </div>

        {companies.length === 0 ? (
          <div className="glass-card p-12 text-center animate-fade-in-up">
            <div className="text-5xl mb-4">&#128203;</div>
            <h2 className="text-2xl font-bold mb-2">No companies found</h2>
            <p className="mb-8 max-w-sm mx-auto" style={{ color: "var(--color-text-secondary)" }}>
              Create a company first to start tracking compliance.
            </p>
            <Link href="/pricing" className="btn-primary">Get Started</Link>
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
                  <p className="text-3xl font-bold mt-2 text-emerald-400">{scoreData?.completed || 0}</p>
                </div>
                <div className="glass-card p-5">
                  <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Overdue</p>
                  <p className="text-3xl font-bold mt-2 text-red-400">{scoreData?.overdue || 0}</p>
                </div>
                <div className="glass-card p-5">
                  <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Due Soon</p>
                  <p className="text-3xl font-bold mt-2 text-amber-400">{scoreData?.due_soon || 0}</p>
                </div>
                <div className="glass-card p-5 md:col-span-2">
                  <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Penalty Exposure</p>
                  <p className="text-2xl font-bold mt-2 text-red-400">
                    Rs {(scoreData?.estimated_penalty_exposure || 0).toLocaleString("en-IN")}
                  </p>
                </div>
                <div className="glass-card p-5 md:col-span-2">
                  <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>In Progress</p>
                  <p className="text-3xl font-bold mt-2 text-purple-400">{scoreData?.in_progress || 0}</p>
                </div>
              </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-1 mb-6 animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
              {(["calendar", "overdue", "penalties", "tds"] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === tab
                      ? "bg-purple-500/20 text-purple-400 border border-purple-500/30"
                      : "hover:bg-white/5"
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
                              : "border-gray-800 bg-gray-900/30"
                          }`}
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="text-sm font-semibold">{entry.title}</h4>
                              <StatusBadge status={entry.status} />
                              <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-400">
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
                              <p className="text-[10px] mt-0.5 text-red-400 font-semibold">
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
                  <h3 className="text-lg font-bold mb-4 text-red-400">Overdue Tasks</h3>
                  {overdueTasks.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="text-4xl mb-3">&#10003;</div>
                      <p className="text-sm text-emerald-400 font-semibold">All clear! No overdue tasks.</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {overdueTasks.map((task) => (
                        <div
                          key={task.id}
                          className="p-4 rounded-lg border border-red-500/30 bg-red-500/5 flex flex-col md:flex-row justify-between items-start md:items-center gap-3"
                        >
                          <div className="flex-1">
                            <h4 className="text-sm font-semibold text-red-300">{task.title}</h4>
                            <p className="text-xs mt-1" style={{ color: "var(--color-text-secondary)" }}>
                              {task.description}
                            </p>
                            {task.due_date && (
                              <p className="text-[10px] mt-1 text-red-400">
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
                      <p className="text-sm text-emerald-400 font-semibold">No penalties! All filings are on time.</p>
                    </div>
                  ) : (
                    <>
                      <div className="p-4 rounded-lg border border-red-500/30 bg-red-500/5 mb-6">
                        <p className="text-xs font-semibold uppercase tracking-wider text-red-400 mb-1">
                          Total Estimated Penalty Exposure
                        </p>
                        <p className="text-3xl font-bold text-red-400">
                          Rs {penaltyData.total.toLocaleString("en-IN")}
                        </p>
                      </div>
                      <div className="space-y-3">
                        {penaltyData.details.map((p, idx) => (
                          <div key={idx} className="p-4 rounded-lg border border-gray-800 bg-gray-900/30 flex justify-between items-center">
                            <div>
                              <h4 className="text-sm font-semibold">{p.task_title}</h4>
                              <p className="text-xs text-gray-400 mt-0.5">
                                {p.days_overdue} days overdue {p.description && `- ${p.description}`}
                              </p>
                            </div>
                            <span className="text-lg font-bold text-red-400">
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
                          <p className="text-lg font-bold text-amber-400">Rs {(tdsResult.tds_amount || 0).toLocaleString("en-IN")}</p>
                        </div>
                        <div>
                          <p className="text-[10px] uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Net Payable</p>
                          <p className="text-lg font-bold text-emerald-400">Rs {(tdsResult.net_payable || 0).toLocaleString("en-IN")}</p>
                        </div>
                      </div>
                      {tdsResult.note && (
                        <p className="text-xs mt-3 p-2 rounded bg-gray-800/50" style={{ color: "var(--color-text-secondary)" }}>
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
