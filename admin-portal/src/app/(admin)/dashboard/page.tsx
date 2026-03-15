"use client";

import { useEffect, useState } from "react";
import {
  getAdminCompanies,
  getAdminAnalytics,
  getSLAOverview,
  getSLABreaches,
} from "@/lib/api";
import Link from "next/link";

const KANBAN_COLUMNS = [
  { key: "draft", label: "Draft", statuses: ["draft", "entity_selected"] },
  { key: "payment", label: "Payment", statuses: ["payment_pending", "payment_completed"] },
  { key: "documents", label: "Documents", statuses: ["documents_pending", "documents_uploaded", "documents_verified"] },
  { key: "name", label: "Name Approval", statuses: ["name_pending", "name_reserved", "name_rejected"] },
  { key: "filing", label: "Filing", statuses: ["dsc_in_progress", "dsc_obtained", "filing_drafted", "filing_under_review", "filing_submitted"] },
  { key: "mca", label: "MCA", statuses: ["mca_processing", "mca_query"] },
  { key: "incorporated", label: "Incorporated", statuses: ["incorporated", "bank_account_pending", "bank_account_opened", "inc20a_pending", "fully_setup"] },
];

function getPriorityBadge(priority: string) {
  switch (priority) {
    case "urgent":
      return { bg: "rgba(245, 158, 11, 0.15)", borderColor: "rgba(245, 158, 11, 0.3)", color: "var(--color-warning)", label: "URGENT" };
    case "vip":
      return { bg: "rgba(139, 92, 246, 0.15)", borderColor: "rgba(139, 92, 246, 0.3)", color: "var(--color-accent-purple-light)", label: "VIP" };
    default:
      return null;
  }
}

function getStatusColor(status: string): string {
  if (["incorporated", "fully_setup", "bank_account_opened"].includes(status)) return "var(--color-success)";
  if (["draft", "entity_selected"].includes(status)) return "var(--color-text-secondary)";
  if (status.includes("rejected") || status.includes("query")) return "var(--color-error)";
  if (status.includes("pending")) return "var(--color-warning)";
  return "var(--color-info)";
}

function timeAgo(dateStr: string): string {
  const now = new Date();
  const date = new Date(dateStr);
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function daysInStage(lastUpdated: string): number {
  const now = new Date();
  const date = new Date(lastUpdated);
  return Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
}

export default function AdminDashboardPage() {
  const [companies, setCompanies] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [slaOverview, setSLAOverview] = useState<any>(null);
  const [slaBreaches, setSLABreaches] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [companiesData, analyticsData, slaData, breachesData] = await Promise.allSettled([
          getAdminCompanies({ limit: 200 }),
          getAdminAnalytics(),
          getSLAOverview(),
          getSLABreaches(),
        ]);

        if (companiesData.status === "fulfilled") {
          setCompanies(companiesData.value.companies || []);
        }
        if (analyticsData.status === "fulfilled") {
          setAnalytics(analyticsData.value);
        }
        if (slaData.status === "fulfilled") {
          setSLAOverview(slaData.value);
        }
        if (breachesData.status === "fulfilled") {
          setSLABreaches(breachesData.value || []);
        }
      } catch (err) {
        console.error("Failed to fetch dashboard data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchAll();
  }, []);

  // Group companies by kanban column
  const kanbanData = KANBAN_COLUMNS.map((col) => ({
    ...col,
    companies: companies.filter((c) => col.statuses.includes(c.status)),
  }));

  // Recent activity: last 10 status changes by updated_at
  const recentActivity = [...companies]
    .sort((a, b) => new Date(b.updated_at || b.created_at).getTime() - new Date(a.updated_at || a.created_at).getTime())
    .slice(0, 10);

  // Compute metrics
  const totalCompanies = companies.length;
  const activeIncorporations = companies.filter((c) => !["draft", "incorporated", "fully_setup"].includes(c.status)).length;
  const completedThisMonth = companies.filter((c) => {
    if (!["incorporated", "fully_setup"].includes(c.status)) return false;
    const d = new Date(c.updated_at || c.created_at);
    const now = new Date();
    return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
  }).length;

  if (loading) {
    return (
      <div className="p-12 flex items-center justify-center">
        <div className="animate-pulse" style={{ color: "var(--color-text-muted)" }}>Loading Operations Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-full">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>Operations Dashboard</h1>
        <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>Real-time overview of all company incorporations and operations.</p>
      </div>

      {/* Top Metrics Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        <div className="rounded-xl p-5" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <p className="text-xs uppercase tracking-wider font-medium mb-1" style={{ color: "var(--color-text-muted)" }}>Total Companies</p>
          <p className="text-3xl font-bold" style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}>{totalCompanies}</p>
        </div>
        <div className="rounded-xl p-5" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <p className="text-xs uppercase tracking-wider font-medium mb-1" style={{ color: "var(--color-text-muted)" }}>Active Incorporations</p>
          <p className="text-3xl font-bold" style={{ fontFamily: "var(--font-display)", color: "var(--color-info)" }}>{activeIncorporations}</p>
        </div>
        <div className="rounded-xl p-5" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <p className="text-xs uppercase tracking-wider font-medium mb-1" style={{ color: "var(--color-text-muted)" }}>Completed This Month</p>
          <p className="text-3xl font-bold" style={{ fontFamily: "var(--font-display)", color: "var(--color-success)" }}>{completedThisMonth}</p>
        </div>
        <div className="rounded-xl p-5" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <p className="text-xs uppercase tracking-wider font-medium mb-1" style={{ color: "var(--color-text-muted)" }}>Revenue This Month</p>
          <p className="text-3xl font-bold" style={{ fontFamily: "var(--font-display)", color: "var(--color-warning)" }}>
            {analytics?.revenue_total != null ? `₹${(analytics.revenue_total / 1000).toFixed(0)}K` : "--"}
          </p>
        </div>
        <div className="rounded-xl p-5" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <p className="text-xs uppercase tracking-wider font-medium mb-1" style={{ color: "var(--color-text-muted)" }}>SLA Compliance</p>
          <p className="text-3xl font-bold" style={{
            fontFamily: "var(--font-display)",
            color: slaOverview?.on_time_percentage >= 90 ? "var(--color-success)" : slaOverview?.on_time_percentage >= 70 ? "var(--color-warning)" : "var(--color-error)",
          }}>
            {slaOverview?.on_time_percentage != null ? `${slaOverview.on_time_percentage}%` : "--"}
          </p>
        </div>
      </div>

      {/* Pipeline Kanban Board */}
      <div className="mb-8">
        <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} style={{ color: "var(--color-accent-purple-light)" }}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25m18 0A2.25 2.25 0 0018.75 3H5.25A2.25 2.25 0 003 5.25m18 0V12a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 12V5.25" />
          </svg>
          Pipeline Board
        </h2>
        <div className="flex gap-3 overflow-x-auto pb-4" style={{ scrollbarWidth: "thin", scrollbarColor: "rgba(139, 92, 246, 0.3) transparent" }}>
          {kanbanData.map((col) => (
            <div key={col.key} className="min-w-[220px] w-[220px] shrink-0">
              <div className="rounded-t-lg px-3 py-2 flex items-center justify-between" style={{ border: "1px solid var(--color-border)", borderBottom: "none", background: "var(--color-bg-card)" }}>
                <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-primary)" }}>{col.label}</span>
                <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ color: "var(--color-accent-purple-light)", background: "rgba(139, 92, 246, 0.1)" }}>
                  {col.companies.length}
                </span>
              </div>
              <div className="rounded-b-lg p-2 min-h-[200px] max-h-[400px] overflow-y-auto space-y-2" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-secondary)", scrollbarWidth: "thin", scrollbarColor: "rgba(139, 92, 246, 0.3) transparent" }}>
                {col.companies.length === 0 ? (
                  <div className="text-center py-8 text-xs" style={{ color: "var(--color-text-muted)" }}>No companies</div>
                ) : (
                  col.companies.map((comp) => {
                    const priorityBadge = getPriorityBadge(comp.priority);
                    const days = daysInStage(comp.updated_at || comp.created_at);
                    const displayName = comp.approved_name || (comp.proposed_names && comp.proposed_names[0]) || `Company #${comp.id}`;

                    return (
                      <Link
                        key={comp.id}
                        href={`/companies/${comp.id}`}
                        className="block rounded-lg p-3 transition-all cursor-pointer group"
                        style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}
                      >
                        <div className="flex items-start justify-between gap-1 mb-1.5">
                          <p className="text-xs font-semibold truncate transition-colors" style={{ color: "var(--color-text-primary)" }}>
                            {displayName}
                          </p>
                          {priorityBadge && (
                            <span
                              className="text-[9px] font-bold px-1.5 py-0.5 rounded shrink-0"
                              style={{
                                background: priorityBadge.bg,
                                borderWidth: "1px",
                                borderStyle: "solid",
                                borderColor: priorityBadge.borderColor,
                                color: priorityBadge.color,
                              }}
                            >
                              {priorityBadge.label}
                            </span>
                          )}
                        </div>
                        <p className="text-[10px] mb-1.5" style={{ color: "var(--color-text-muted)" }}>
                          {comp.entity_type?.replace(/_/g, " ").toUpperCase()}
                        </p>
                        <div className="flex items-center justify-between">
                          {comp.assigned_to_name ? (
                            <span className="text-[10px] truncate" style={{ color: "var(--color-text-secondary)" }}>
                              {comp.assigned_to_name}
                            </span>
                          ) : (
                            <span className="text-[10px] italic" style={{ color: "var(--color-text-muted)" }}>Unassigned</span>
                          )}
                          <span
                            className="text-[10px] font-mono"
                            style={{ color: days > 3 ? "var(--color-error)" : days > 1 ? "var(--color-warning)" : "var(--color-text-muted)" }}
                          >
                            {days}d
                          </span>
                        </div>
                      </Link>
                    );
                  })
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Section: Two Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Recent Activity */}
        <div className="rounded-xl overflow-hidden" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <div className="px-5 py-4 flex items-center justify-between" style={{ borderBottom: "1px solid var(--color-border)" }}>
            <h3 className="text-sm font-semibold">Recent Activity</h3>
            <span className="text-[10px] uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Last 10 changes</span>
          </div>
          <div className="max-h-[400px] overflow-y-auto" style={{ scrollbarWidth: "thin" }}>
            {recentActivity.length === 0 ? (
              <div className="p-8 text-center text-sm" style={{ color: "var(--color-text-muted)" }}>No recent activity</div>
            ) : (
              recentActivity.map((comp) => {
                const displayName = comp.approved_name || (comp.proposed_names && comp.proposed_names[0]) || `Company #${comp.id}`;
                const statusColor = getStatusColor(comp.status);
                return (
                  <Link
                    key={comp.id}
                    href={`/companies/${comp.id}`}
                    className="flex items-center gap-3 px-5 py-3 transition-colors"
                    style={{ borderBottom: "1px solid rgba(var(--color-border-rgb, 55, 65, 81), 0.5)" }}
                  >
                    <div className="w-2 h-2 rounded-full shrink-0" style={{ background: statusColor }} />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium truncate" style={{ color: "var(--color-text-primary)" }}>{displayName}</p>
                      <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                        {comp.status.replace(/_/g, " ").toUpperCase()}
                      </p>
                    </div>
                    <span className="text-[10px] shrink-0" style={{ color: "var(--color-text-muted)" }}>
                      {timeAgo(comp.updated_at || comp.created_at)}
                    </span>
                  </Link>
                );
              })
            )}
          </div>
        </div>

        {/* Right: SLA Breaches */}
        <div className="rounded-xl overflow-hidden" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <div className="px-5 py-4 flex items-center justify-between" style={{ borderBottom: "1px solid var(--color-border)" }}>
            <h3 className="text-sm font-semibold flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} style={{ color: "var(--color-error)" }}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
              SLA Breaches
            </h3>
            <Link href="/analytics" className="text-[10px] font-medium transition-colors" style={{ color: "var(--color-accent-purple-light)" }}>
              View Details
            </Link>
          </div>
          <div className="max-h-[400px] overflow-y-auto" style={{ scrollbarWidth: "thin" }}>
            {slaBreaches.length === 0 ? (
              <div className="p-8 text-center">
                <svg className="w-8 h-8 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5} style={{ color: "rgba(16, 185, 129, 0.4)" }}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>No SLA breaches. Great work!</p>
              </div>
            ) : (
              slaBreaches.map((breach, idx) => (
                <Link
                  key={idx}
                  href={`/companies/${breach.company_id}`}
                  className="flex items-center gap-3 px-5 py-3 transition-colors"
                  style={{ borderBottom: "1px solid rgba(var(--color-border-rgb, 55, 65, 81), 0.5)" }}
                >
                  <div className="w-2 h-2 rounded-full shrink-0 animate-pulse" style={{ background: "rgb(239, 68, 68)" }} />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium truncate" style={{ color: "var(--color-text-primary)" }}>
                      {breach.company_name || `Company #${breach.company_id}`}
                    </p>
                    <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                      {breach.stage?.replace(/_/g, " ").toUpperCase()} - {breach.days_exceeded}d over SLA
                    </p>
                  </div>
                  <span className="text-[10px] font-bold shrink-0 px-2 py-0.5 rounded-full" style={{
                    color: "var(--color-error)",
                    background: "rgba(239, 68, 68, 0.1)",
                    border: "1px solid rgba(239, 68, 68, 0.2)",
                  }}>
                    {breach.days_exceeded}d
                  </span>
                </Link>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
