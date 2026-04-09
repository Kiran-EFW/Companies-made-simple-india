"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { useCompany } from "@/lib/company-context";
import Link from "next/link";
import UpsellBanner from "@/components/upsell-banner";
import {
  getPostIncorporationChecklist,
  getPostIncorporationDeadlines,
  completePostIncorporationTask,
  triggerComplianceEvent,
  getComplianceEventTypes,
  checkComplianceThresholds,
} from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ChecklistTask {
  task_type: string;
  title: string;
  description: string;
  deadline: string | null;
  deadline_days: number;
  days_remaining: number | null;
  is_overdue: boolean;
  category: string;
  priority: number;
  status?: string; // added locally when task is completed
}

interface DeadlineItem {
  task_type: string;
  title: string;
  deadline: string;
  days_remaining: number;
  is_overdue: boolean;
}

interface EventType {
  event_name: string;
  tasks: {
    type: string;
    title: string;
    form: string;
    section: string;
    deadline_days: number;
  }[];
}

interface ThresholdTask {
  id: number;
  type: string;
  title: string;
  due_date: string | null;
}

interface ThresholdResult {
  thresholds_triggered: number;
  tasks: ThresholdTask[];
}

// ---------------------------------------------------------------------------
// Helper Components
// ---------------------------------------------------------------------------

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    overdue: "bg-red-500/10 text-red-400 border-red-500/30",
    pending: "bg-amber-500/10 text-amber-400 border-amber-500/30",
    completed: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
    due_soon: "bg-amber-500/10 text-amber-400 border-amber-500/30",
  };

  return (
    <span
      className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${styles[status] || styles.pending}`}
    >
      {status.replace(/_/g, " ").toUpperCase()}
    </span>
  );
}

function UrgencyIndicator({ deadline, status }: { deadline: string | null; status: string }) {
  if (status === "completed") {
    return (
      <div
        className="w-1.5 rounded-full self-stretch shrink-0"
        style={{ background: "var(--color-success)" }}
      />
    );
  }
  if (!deadline) {
    return (
      <div
        className="w-1.5 rounded-full self-stretch shrink-0"
        style={{ background: "var(--color-border)" }}
      />
    );
  }
  const now = new Date();
  const due = new Date(deadline);
  const daysLeft = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  if (daysLeft < 0) {
    return <div className="w-1.5 rounded-full self-stretch shrink-0 bg-red-500" />;
  }
  if (daysLeft <= 7) {
    return <div className="w-1.5 rounded-full self-stretch shrink-0 bg-amber-500" />;
  }
  return (
    <div
      className="w-1.5 rounded-full self-stretch shrink-0"
      style={{ background: "var(--color-info)" }}
    />
  );
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function PostIncorporationPage() {
  const { user, loading: authLoading } = useAuth();
  const { selectedCompany } = useCompany();

  const selectedCompanyId = selectedCompany?.id ?? null;

  // Tab 1: Checklist
  const [checklist, setChecklist] = useState<ChecklistTask[]>([]);
  const [deadlines, setDeadlines] = useState<DeadlineItem[]>([]);

  // Tab 2: Event Triggers
  const [eventTypes, setEventTypes] = useState<EventType[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<EventType | null>(null);
  const [eventDate, setEventDate] = useState("");
  const [eventNotes, setEventNotes] = useState("");
  const [triggerResult, setTriggerResult] = useState<any>(null);
  const [triggering, setTriggering] = useState(false);

  // Tab 3: Thresholds
  const [thresholdResults, setThresholdResults] = useState<ThresholdResult | null>(null);
  const [checkingThresholds, setCheckingThresholds] = useState(false);

  // UI
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"checklist" | "events" | "thresholds">("checklist");
  const [completingTaskId, setCompletingTaskId] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // ── Fetch data when company changes ──────────────────────────────
  useEffect(() => {
    if (!selectedCompanyId) {
      setLoading(false);
      return;
    }
    const fetchAll = async () => {
      setLoading(true);
      try {
        const [checklistRes, deadlinesRes, eventTypesRes] = await Promise.all([
          getPostIncorporationChecklist(selectedCompanyId).catch(() => ({ checklist: [] })),
          getPostIncorporationDeadlines(selectedCompanyId).catch(() => ({ deadlines: [] })),
          getComplianceEventTypes(selectedCompanyId).catch(() => ({ events: [] })),
        ]);
        setChecklist(checklistRes?.checklist || []);
        setDeadlines(deadlinesRes?.deadlines || []);
        setEventTypes(eventTypesRes?.events || []);
      } catch (err) {
        console.error("Failed to fetch post-incorporation data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, [selectedCompanyId]);

  // ── Auto-clear messages ──────────────────────────────────────────
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  useEffect(() => {
    if (errorMessage) {
      const timer = setTimeout(() => setErrorMessage(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [errorMessage]);

  // ── Mark task complete ───────────────────────────────────────────
  const handleCompleteTask = async (taskId: string) => {
    if (!selectedCompanyId) return;
    setCompletingTaskId(taskId);
    setErrorMessage(null);
    try {
      await completePostIncorporationTask(selectedCompanyId, taskId);
      setSuccessMessage("Task marked as complete.");
      // Refresh checklist
      const [checklistRes, deadlinesRes] = await Promise.all([
        getPostIncorporationChecklist(selectedCompanyId).catch(() => ({ checklist: [] })),
        getPostIncorporationDeadlines(selectedCompanyId).catch(() => ({ deadlines: [] })),
      ]);
      setChecklist(checklistRes?.checklist || []);
      setDeadlines(deadlinesRes?.deadlines || []);
    } catch (err) {
      console.error("Failed to complete task:", err);
      setErrorMessage("Failed to complete task. Please try again.");
    } finally {
      setCompletingTaskId(null);
    }
  };

  // ── Trigger compliance event ─────────────────────────────────────
  const handleTriggerEvent = async () => {
    if (!selectedCompanyId || !selectedEvent) return;
    setTriggering(true);
    setErrorMessage(null);
    try {
      const result = await triggerComplianceEvent(selectedCompanyId, {
        event_name: selectedEvent.event_name,
        event_date: eventDate || undefined,
        notes: eventNotes || undefined,
      });
      setTriggerResult(result);
      setEventDate("");
      setEventNotes("");
      setSuccessMessage("Compliance event triggered successfully.");
    } catch (err) {
      console.error("Failed to trigger event:", err);
      setErrorMessage("Failed to trigger event. Please try again.");
    } finally {
      setTriggering(false);
    }
  };

  // ── Check thresholds ─────────────────────────────────────────────
  const handleCheckThresholds = async () => {
    if (!selectedCompanyId) return;
    setCheckingThresholds(true);
    setErrorMessage(null);
    try {
      const result = await checkComplianceThresholds(selectedCompanyId);
      setThresholdResults(result);
      if (result?.thresholds_triggered > 0) {
        setSuccessMessage(`Threshold check complete. ${result.thresholds_triggered} threshold(s) triggered — ${result.tasks?.length || 0} tasks created.`);
      } else {
        setSuccessMessage("Threshold check complete. All metrics within limits.");
      }
    } catch (err) {
      console.error("Failed to check thresholds:", err);
      setErrorMessage("Failed to check thresholds. Please try again.");
    } finally {
      setCheckingThresholds(false);
    }
  };

  // ── Helpers ──────────────────────────────────────────────────────
  const getTaskBorderStyle = (task: ChecklistTask) => {
    if (task.status === "completed") {
      return { borderColor: "rgba(16, 185, 129, 0.3)", background: "rgba(16, 185, 129, 0.05)" };
    }
    if (task.is_overdue) {
      return { borderColor: "rgba(244, 63, 94, 0.3)", background: "rgba(244, 63, 94, 0.05)" };
    }
    if (!task.deadline) {
      return { borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" };
    }
    const now = new Date();
    const due = new Date(task.deadline);
    const daysLeft = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    if (daysLeft < 0) {
      return { borderColor: "rgba(244, 63, 94, 0.3)", background: "rgba(244, 63, 94, 0.05)" };
    }
    if (daysLeft <= 7) {
      return { borderColor: "rgba(245, 158, 11, 0.3)", background: "rgba(245, 158, 11, 0.05)" };
    }
    return { borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" };
  };

  const pendingCount = checklist.filter((t) => t.status !== "completed").length;
  const completedCount = checklist.filter((t) => t.status === "completed").length;
  const overdueCount = checklist.filter((t) => {
    if (t.status === "completed" || !t.deadline) return false;
    return new Date(t.deadline) < new Date();
  }).length;

  // ── Loading / Auth ───────────────────────────────────────────────
  if (authLoading || (loading && checklist.length === 0)) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="animate-pulse-glow w-16 h-16 rounded-full flex items-center justify-center" style={{ background: "var(--color-purple-bg)" }}>
          <img src="/logo-icon.png" alt="Anvils" className="h-7 w-auto" />
        </div>
      </div>
    );
  }

  // ── Render ───────────────────────────────────────────────────────
  return (
    <div>
      <div className="max-w-7xl mx-auto px-6 py-8">
        {selectedCompany && <UpsellBanner pageKey="compliance" companyId={selectedCompany.id} />}

        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 gap-4 animate-fade-in-up">
          <div>
            <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>
              Post-Incorporation
            </h1>
            <p className="text-sm border-l-2 pl-3 border-purple-500" style={{ color: "var(--color-text-secondary)" }}>
              Track mandatory post-incorporation tasks, deadlines, and compliance events.
            </p>
          </div>
        </div>

        {!selectedCompany ? (
          <div className="p-12 text-center" style={{ background: "var(--color-bg-card)" }}>
            <h2 className="text-xl font-bold mb-2" style={{ color: "var(--color-text-primary)" }}>No company selected</h2>
            <p className="text-sm mb-6" style={{ color: "var(--color-text-secondary)" }}>
              Select a company from the header to view post-incorporation tasks.
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
            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
              <div className="glass-card p-5">
                <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Total Tasks</p>
                <p className="text-3xl font-bold mt-2">{checklist.length}</p>
              </div>
              <div className="glass-card p-5">
                <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Completed</p>
                <p className="text-3xl font-bold mt-2" style={{ color: "var(--color-success)" }}>{completedCount}</p>
              </div>
              <div className="glass-card p-5">
                <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Pending</p>
                <p className="text-3xl font-bold mt-2" style={{ color: "var(--color-warning)" }}>{pendingCount}</p>
              </div>
              <div className="glass-card p-5">
                <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Overdue</p>
                <p className="text-3xl font-bold mt-2" style={{ color: "var(--color-error)" }}>{overdueCount}</p>
              </div>
            </div>

            {/* Progress Bar */}
            {checklist.length > 0 && (
              <div className="glass-card p-5 mb-8 animate-fade-in-up" style={{ animationDelay: "0.15s" }}>
                <div className="flex justify-between items-center mb-2">
                  <h3 className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                    Completion Progress
                  </h3>
                  <span className="text-sm font-bold" style={{ color: "var(--color-accent-purple-light)" }}>
                    {Math.round((completedCount / checklist.length) * 100)}%
                  </span>
                </div>
                <div className="w-full h-2 rounded-full" style={{ background: "var(--color-hover-overlay)" }}>
                  <div
                    className="h-2 rounded-full transition-all duration-700"
                    style={{
                      width: `${(completedCount / checklist.length) * 100}%`,
                      background: completedCount === checklist.length
                        ? "var(--color-success)"
                        : "var(--color-accent-purple-light)",
                    }}
                  />
                </div>
              </div>
            )}

            {/* Success / Error Messages */}
            {successMessage && (
              <div
                className="mb-6 p-4 rounded-lg border flex items-center justify-between animate-fade-in-up"
                style={{ borderColor: "rgba(16, 185, 129, 0.3)", background: "rgba(16, 185, 129, 0.08)" }}
              >
                <p className="text-sm font-medium" style={{ color: "var(--color-success)" }}>{successMessage}</p>
                <button onClick={() => setSuccessMessage(null)} className="text-xs ml-4" style={{ color: "var(--color-success)" }}>Dismiss</button>
              </div>
            )}
            {errorMessage && (
              <div
                className="mb-6 p-4 rounded-lg border flex items-center justify-between animate-fade-in-up"
                style={{ borderColor: "rgba(244, 63, 94, 0.3)", background: "rgba(244, 63, 94, 0.08)" }}
              >
                <p className="text-sm font-medium" style={{ color: "var(--color-error)" }}>{errorMessage}</p>
                <button onClick={() => setErrorMessage(null)} className="text-xs ml-4" style={{ color: "var(--color-error)" }}>Dismiss</button>
              </div>
            )}

            {/* Tabs */}
            <div className="flex gap-1 p-1 rounded-lg mb-6 animate-fade-in-up" style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)", animationDelay: "0.2s" }}>
              {([
                { key: "checklist" as const, label: "Post-Incorporation Checklist" },
                { key: "events" as const, label: "Event Triggers" },
                { key: "thresholds" as const, label: "Threshold Monitor" },
              ]).map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className="flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors"
                  style={{
                    background: activeTab === tab.key ? "var(--color-bg-card)" : "transparent",
                    color: activeTab === tab.key ? "var(--color-accent-purple-light)" : "var(--color-text-secondary)",
                    boxShadow: activeTab === tab.key ? "var(--shadow-card)" : "none",
                  }}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="animate-fade-in-up" style={{ animationDelay: "0.3s" }}>

              {/* ── Tab 1: Checklist ───────────────────────────────────────── */}
              {activeTab === "checklist" && (
                <div className="glass-card p-6">
                  <h3 className="text-lg font-bold mb-4">Post-Incorporation Checklist</h3>
                  {checklist.length === 0 ? (
                    <div className="text-center py-12">
                      <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                        No checklist items found. Post-incorporation tasks will appear here after your company is incorporated.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {checklist.map((task) => {
                        const borderStyle = getTaskBorderStyle(task);
                        const isOverdue = task.status !== "completed" && task.deadline && new Date(task.deadline) < new Date();
                        const daysLeft = task.deadline
                          ? Math.ceil((new Date(task.deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
                          : null;

                        return (
                          <div
                            key={task.task_type}
                            className="p-4 rounded-lg border flex gap-3"
                            style={borderStyle}
                          >
                            <UrgencyIndicator deadline={task.deadline} status={task.status || "pending"} />
                            <div className="flex-1 flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <h4
                                    className="text-sm font-semibold"
                                    style={task.status === "completed" ? { textDecoration: "line-through", color: "var(--color-text-secondary)" } : {}}
                                  >
                                    {task.title}
                                  </h4>
                                  <StatusBadge status={isOverdue ? "overdue" : (task.status || "pending")} />
                                </div>
                                <p className="text-xs" style={{ color: "var(--color-text-secondary)" }}>
                                  {task.description}
                                </p>
                              </div>
                              <div className="flex items-center gap-3 shrink-0">
                                <div className="text-right">
                                  {task.deadline && (
                                    <p className="text-sm font-mono font-semibold">
                                      {new Date(task.deadline).toLocaleDateString("en-IN", {
                                        day: "2-digit",
                                        month: "short",
                                        year: "numeric",
                                      })}
                                    </p>
                                  )}
                                  {task.status !== "completed" && daysLeft !== null && (
                                    <p
                                      className="text-[10px] mt-0.5 font-semibold"
                                      style={{
                                        color: isOverdue
                                          ? "var(--color-error)"
                                          : daysLeft <= 7
                                          ? "var(--color-warning)"
                                          : "var(--color-text-muted)",
                                      }}
                                    >
                                      {isOverdue
                                        ? `${Math.abs(daysLeft)} days overdue`
                                        : `${daysLeft} days remaining`}
                                    </p>
                                  )}
                                </div>
                                {task.status !== "completed" && (
                                  <button
                                    onClick={() => handleCompleteTask(task.task_type)}
                                    disabled={completingTaskId === task.task_type}
                                    className="text-xs font-bold text-emerald-400 hover:text-emerald-300 border border-emerald-500/30 px-3 py-1.5 rounded-lg hover:bg-emerald-500/10 transition-colors"
                                  >
                                    {completingTaskId === task.task_type ? "Saving..." : "Mark Complete"}
                                  </button>
                                )}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {/* Key Milestones Reference */}
                  <div className="mt-8 pt-6" style={{ borderTop: "1px solid var(--color-border)" }}>
                    <h4 className="text-xs font-semibold uppercase tracking-wider mb-4" style={{ color: "var(--color-text-muted)" }}>
                      Key Post-Incorporation Milestones
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {[
                        { title: "INC-20A Declaration", deadline: "180 days from incorporation", icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" },
                        { title: "Bank Account Opening", deadline: "As soon as possible", icon: "M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" },
                        { title: "First Board Meeting", deadline: "30 days from incorporation", icon: "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" },
                        { title: "Auditor Appointment", deadline: "30 days of first AGM", icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" },
                        { title: "GST Registration", deadline: "If applicable (turnover threshold)", icon: "M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2z" },
                        { title: "PF/ESI Registration", deadline: "If applicable (employee threshold)", icon: "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" },
                      ].map((milestone, idx) => (
                        <div
                          key={idx}
                          className="p-3 rounded-lg border flex items-start gap-3"
                          style={{ borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" }}
                        >
                          <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" style={{ background: "var(--color-purple-bg)" }}>
                            <svg className="w-4 h-4" fill="none" stroke="var(--color-accent-purple-light)" viewBox="0 0 24 24" strokeWidth={1.5}>
                              <path strokeLinecap="round" strokeLinejoin="round" d={milestone.icon} />
                            </svg>
                          </div>
                          <div>
                            <p className="text-sm font-semibold">{milestone.title}</p>
                            <p className="text-[10px] mt-0.5" style={{ color: "var(--color-text-secondary)" }}>{milestone.deadline}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* ── Tab 2: Event Triggers ──────────────────────────────────── */}
              {activeTab === "events" && (
                <div className="glass-card p-6">
                  <h3 className="text-lg font-bold mb-4">Compliance Event Triggers</h3>
                  <p className="text-xs mb-6" style={{ color: "var(--color-text-secondary)" }}>
                    Trigger a compliance event to automatically generate related tasks and deadlines.
                  </p>

                  {eventTypes.length === 0 ? (
                    <div className="text-center py-12">
                      <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                        No event types available. Compliance events will appear here once configured.
                      </p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {eventTypes.map((evt) => (
                        <button
                          key={evt.event_name}
                          onClick={() => {
                            setSelectedEvent(evt);
                            setTriggerResult(null);
                          }}
                          className="p-4 rounded-lg border text-left transition-colors hover:border-purple-500/40"
                          style={{
                            borderColor: selectedEvent?.event_name === evt.event_name
                              ? "rgba(139, 92, 246, 0.5)"
                              : "var(--color-border)",
                            background: selectedEvent?.event_name === evt.event_name
                              ? "rgba(139, 92, 246, 0.08)"
                              : "var(--color-bg-secondary)",
                          }}
                        >
                          <h4 className="text-sm font-semibold mb-2">
                            {evt.event_name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                          </h4>
                          {evt.tasks.length > 0 && (
                            <div className="space-y-1.5">
                              {evt.tasks.map((t) => (
                                <div key={t.type} className="flex items-start gap-2">
                                  <span
                                    className="text-[10px] px-1.5 py-0.5 rounded font-mono shrink-0"
                                    style={{ background: "var(--color-bg-card)", color: "var(--color-text-secondary)" }}
                                  >
                                    {t.form}
                                  </span>
                                  <span className="text-[10px]" style={{ color: "var(--color-text-secondary)" }}>
                                    {t.title} ({t.deadline_days}d)
                                  </span>
                                </div>
                              ))}
                            </div>
                          )}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Event Trigger Modal / Panel */}
                  {selectedEvent && (
                    <div className="mt-6 p-5 rounded-lg border" style={{ borderColor: "rgba(139, 92, 246, 0.3)", background: "rgba(139, 92, 246, 0.05)" }}>
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h4 className="text-sm font-bold">
                            {selectedEvent.event_name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                          </h4>
                          <p className="text-xs mt-0.5" style={{ color: "var(--color-text-secondary)" }}>
                            {selectedEvent.tasks.length} compliance task(s) will be created
                          </p>
                        </div>
                        <button
                          onClick={() => {
                            setSelectedEvent(null);
                            setTriggerResult(null);
                          }}
                          className="text-xs px-2 py-1 rounded hover:bg-white/5 transition-colors"
                          style={{ color: "var(--color-text-secondary)" }}
                        >
                          Close
                        </button>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                          <label className="text-xs font-semibold uppercase tracking-wider block mb-2" style={{ color: "var(--color-text-muted)" }}>
                            Event Date
                          </label>
                          <input
                            type="date"
                            value={eventDate}
                            onChange={(e) => setEventDate(e.target.value)}
                            className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                            style={{
                              background: "var(--color-bg-card)",
                              borderColor: "var(--color-border)",
                              color: "var(--color-text-primary)",
                            }}
                          />
                        </div>
                        <div>
                          <label className="text-xs font-semibold uppercase tracking-wider block mb-2" style={{ color: "var(--color-text-muted)" }}>
                            Notes
                          </label>
                          <textarea
                            value={eventNotes}
                            onChange={(e) => setEventNotes(e.target.value)}
                            placeholder="Optional notes..."
                            rows={1}
                            className="w-full px-3 py-2 rounded-lg border text-sm outline-none resize-none"
                            style={{
                              background: "var(--color-bg-card)",
                              borderColor: "var(--color-border)",
                              color: "var(--color-text-primary)",
                            }}
                          />
                        </div>
                      </div>
                      <button
                        onClick={handleTriggerEvent}
                        disabled={triggering}
                        className="btn-primary text-sm !py-2 !px-6"
                      >
                        {triggering ? "Triggering..." : "Trigger Event"}
                      </button>

                      {/* Trigger Result */}
                      {triggerResult && (
                        <div className="mt-4 p-4 rounded-lg border border-emerald-500/30 bg-emerald-500/5">
                          <h5 className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: "var(--color-success)" }}>
                            Event Triggered Successfully
                          </h5>
                          {triggerResult.tasks_created && triggerResult.tasks_created.length > 0 ? (
                            <div className="space-y-2">
                              {triggerResult.tasks_created.map((task: any, idx: number) => (
                                <div
                                  key={idx}
                                  className="p-3 rounded-lg border flex justify-between items-center"
                                  style={{ borderColor: "var(--color-border)", background: "var(--color-bg-card)" }}
                                >
                                  <div>
                                    <p className="text-sm font-semibold">{task.title || task.task_title}</p>
                                    {task.due_date && (
                                      <p className="text-[10px] mt-0.5" style={{ color: "var(--color-text-secondary)" }}>
                                        Due: {new Date(task.due_date).toLocaleDateString("en-IN", {
                                          day: "2-digit",
                                          month: "short",
                                          year: "numeric",
                                        })}
                                      </p>
                                    )}
                                  </div>
                                  <StatusBadge status={task.status || "pending"} />
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-xs" style={{ color: "var(--color-text-secondary)" }}>
                              {triggerResult.message || "Event has been processed."}
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* ── Tab 3: Threshold Monitor ───────────────────────────────── */}
              {activeTab === "thresholds" && (
                <div className="glass-card p-6">
                  <div className="flex justify-between items-center mb-6">
                    <div>
                      <h3 className="text-lg font-bold">Threshold Monitor</h3>
                      <p className="text-xs mt-1" style={{ color: "var(--color-text-secondary)" }}>
                        Monitor company metrics against compliance thresholds (e.g., employee count for PF/ESI registration).
                      </p>
                    </div>
                    <button
                      onClick={handleCheckThresholds}
                      disabled={checkingThresholds}
                      className="btn-primary text-sm !py-2 !px-4"
                    >
                      {checkingThresholds ? "Checking..." : "Check Thresholds"}
                    </button>
                  </div>

                  {!thresholdResults ? (
                    <div className="text-center py-12">
                      <div className="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center" style={{ background: "var(--color-bg-secondary)" }}>
                        <svg className="w-8 h-8" fill="none" stroke="var(--color-text-muted)" viewBox="0 0 24 24" strokeWidth={1.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
                        </svg>
                      </div>
                      <p className="text-sm font-semibold" style={{ color: "var(--color-text-secondary)" }}>
                        No threshold data yet
                      </p>
                      <p className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
                        Click &quot;Check Thresholds&quot; to evaluate your company metrics against compliance requirements.
                      </p>
                    </div>
                  ) : thresholdResults.thresholds_triggered === 0 ? (
                    <div className="text-center py-12">
                      <div className="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center" style={{ background: "rgba(16, 185, 129, 0.1)" }}>
                        <svg className="w-8 h-8" fill="none" stroke="var(--color-success)" viewBox="0 0 24 24" strokeWidth={1.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <p className="text-sm font-semibold" style={{ color: "var(--color-success)" }}>
                        All metrics within limits
                      </p>
                      <p className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
                        No compliance thresholds have been crossed. Your company metrics are within regulatory limits.
                      </p>
                    </div>
                  ) : (
                    <div>
                      <div className="p-4 rounded-lg border mb-4" style={{ borderColor: "rgba(244, 63, 94, 0.3)", background: "rgba(244, 63, 94, 0.05)" }}>
                        <div className="flex justify-between items-center">
                          <h4 className="text-sm font-semibold">Thresholds Crossed</h4>
                          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full border bg-red-500/10 text-red-400 border-red-500/30">
                            {thresholdResults.thresholds_triggered} TRIGGERED
                          </span>
                        </div>
                      </div>
                      {thresholdResults.tasks.length > 0 && (
                        <div>
                          <p className="text-[10px] font-semibold uppercase tracking-wider mb-3" style={{ color: "var(--color-text-muted)" }}>
                            Tasks Created
                          </p>
                          <div className="space-y-2">
                            {thresholdResults.tasks.map((task) => (
                              <div
                                key={task.id}
                                className="p-3 rounded-lg border flex justify-between items-center"
                                style={{ borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" }}
                              >
                                <div>
                                  <p className="text-sm font-semibold">{task.title}</p>
                                  <p className="text-[10px] mt-0.5 font-mono" style={{ color: "var(--color-text-muted)" }}>
                                    {task.type}
                                  </p>
                                </div>
                                {task.due_date && (
                                  <p className="text-xs font-mono" style={{ color: "var(--color-text-secondary)" }}>
                                    Due: {new Date(task.due_date).toLocaleDateString("en-IN", {
                                      day: "2-digit",
                                      month: "short",
                                      year: "numeric",
                                    })}
                                  </p>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
