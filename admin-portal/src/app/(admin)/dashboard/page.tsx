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
      return { bg: "bg-amber-500/15 border-amber-500/30", text: "text-amber-400", label: "URGENT" };
    case "vip":
      return { bg: "bg-purple-500/15 border-purple-500/30", text: "text-purple-400", label: "VIP" };
    default:
      return null;
  }
}

function getStatusColor(status: string): string {
  if (["incorporated", "fully_setup", "bank_account_opened"].includes(status)) return "text-emerald-400";
  if (["draft", "entity_selected"].includes(status)) return "text-gray-400";
  if (status.includes("rejected") || status.includes("query")) return "text-red-400";
  if (status.includes("pending")) return "text-amber-400";
  return "text-blue-400";
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
        <div className="animate-pulse text-gray-500">Loading Operations Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-full">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>Operations Dashboard</h1>
        <p className="text-sm text-gray-400">Real-time overview of all company incorporations and operations.</p>
      </div>

      {/* Top Metrics Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-1">Total Companies</p>
          <p className="text-3xl font-bold text-white" style={{ fontFamily: "var(--font-display)" }}>{totalCompanies}</p>
        </div>
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-1">Active Incorporations</p>
          <p className="text-3xl font-bold text-blue-400" style={{ fontFamily: "var(--font-display)" }}>{activeIncorporations}</p>
        </div>
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-1">Completed This Month</p>
          <p className="text-3xl font-bold text-emerald-400" style={{ fontFamily: "var(--font-display)" }}>{completedThisMonth}</p>
        </div>
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-1">Revenue This Month</p>
          <p className="text-3xl font-bold text-amber-400" style={{ fontFamily: "var(--font-display)" }}>
            {analytics?.revenue_this_month != null ? `₹${(analytics.revenue_this_month / 1000).toFixed(0)}K` : "--"}
          </p>
        </div>
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-1">SLA Compliance</p>
          <p className={`text-3xl font-bold ${slaOverview?.compliance_rate >= 90 ? "text-emerald-400" : slaOverview?.compliance_rate >= 70 ? "text-amber-400" : "text-red-400"}`} style={{ fontFamily: "var(--font-display)" }}>
            {slaOverview?.compliance_rate != null ? `${slaOverview.compliance_rate}%` : "--"}
          </p>
        </div>
      </div>

      {/* Pipeline Kanban Board */}
      <div className="mb-8">
        <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
          <svg className="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25m18 0A2.25 2.25 0 0018.75 3H5.25A2.25 2.25 0 003 5.25m18 0V12a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 12V5.25" />
          </svg>
          Pipeline Board
        </h2>
        <div className="flex gap-3 overflow-x-auto pb-4" style={{ scrollbarWidth: "thin", scrollbarColor: "rgba(139, 92, 246, 0.3) transparent" }}>
          {kanbanData.map((col) => (
            <div key={col.key} className="min-w-[220px] w-[220px] shrink-0">
              <div className="rounded-t-lg px-3 py-2 border border-b-0 border-gray-700 bg-gray-800/80 flex items-center justify-between">
                <span className="text-xs font-semibold text-gray-300 uppercase tracking-wider">{col.label}</span>
                <span className="text-xs font-bold text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded-full">
                  {col.companies.length}
                </span>
              </div>
              <div className="rounded-b-lg border border-gray-700 bg-gray-900/50 p-2 min-h-[200px] max-h-[400px] overflow-y-auto space-y-2" style={{ scrollbarWidth: "thin", scrollbarColor: "rgba(139, 92, 246, 0.3) transparent" }}>
                {col.companies.length === 0 ? (
                  <div className="text-center py-8 text-gray-600 text-xs">No companies</div>
                ) : (
                  col.companies.map((comp) => {
                    const priorityBadge = getPriorityBadge(comp.priority);
                    const days = daysInStage(comp.updated_at || comp.created_at);
                    const displayName = comp.approved_name || (comp.proposed_names && comp.proposed_names[0]) || `Company #${comp.id}`;

                    return (
                      <Link
                        key={comp.id}
                        href={`/companies/${comp.id}`}
                        className="block rounded-lg border border-gray-700 bg-gray-800/60 p-3 hover:border-purple-500/40 hover:bg-gray-800 transition-all cursor-pointer group"
                      >
                        <div className="flex items-start justify-between gap-1 mb-1.5">
                          <p className="text-xs font-semibold text-white truncate group-hover:text-purple-300 transition-colors">
                            {displayName}
                          </p>
                          {priorityBadge && (
                            <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border shrink-0 ${priorityBadge.bg} ${priorityBadge.text}`}>
                              {priorityBadge.label}
                            </span>
                          )}
                        </div>
                        <p className="text-[10px] text-gray-500 mb-1.5">
                          {comp.entity_type?.replace(/_/g, " ").toUpperCase()}
                        </p>
                        <div className="flex items-center justify-between">
                          {comp.assigned_to_name ? (
                            <span className="text-[10px] text-gray-400 truncate">
                              {comp.assigned_to_name}
                            </span>
                          ) : (
                            <span className="text-[10px] text-gray-600 italic">Unassigned</span>
                          )}
                          <span className={`text-[10px] font-mono ${days > 3 ? "text-red-400" : days > 1 ? "text-amber-400" : "text-gray-500"}`}>
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
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-700 flex items-center justify-between">
            <h3 className="text-sm font-semibold">Recent Activity</h3>
            <span className="text-[10px] text-gray-500 uppercase tracking-wider">Last 10 changes</span>
          </div>
          <div className="divide-y divide-gray-700/50 max-h-[400px] overflow-y-auto" style={{ scrollbarWidth: "thin" }}>
            {recentActivity.length === 0 ? (
              <div className="p-8 text-center text-gray-500 text-sm">No recent activity</div>
            ) : (
              recentActivity.map((comp) => {
                const displayName = comp.approved_name || (comp.proposed_names && comp.proposed_names[0]) || `Company #${comp.id}`;
                return (
                  <Link
                    key={comp.id}
                    href={`/companies/${comp.id}`}
                    className="flex items-center gap-3 px-5 py-3 hover:bg-white/5 transition-colors"
                  >
                    <div className={`w-2 h-2 rounded-full shrink-0 ${getStatusColor(comp.status).replace("text-", "bg-")}`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-white truncate">{displayName}</p>
                      <p className="text-[10px] text-gray-500">
                        {comp.status.replace(/_/g, " ").toUpperCase()}
                      </p>
                    </div>
                    <span className="text-[10px] text-gray-600 shrink-0">
                      {timeAgo(comp.updated_at || comp.created_at)}
                    </span>
                  </Link>
                );
              })
            )}
          </div>
        </div>

        {/* Right: SLA Breaches */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-700 flex items-center justify-between">
            <h3 className="text-sm font-semibold flex items-center gap-2">
              <svg className="w-4 h-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
              SLA Breaches
            </h3>
            <Link href="/analytics" className="text-[10px] text-purple-400 hover:text-purple-300 font-medium transition-colors">
              View Details
            </Link>
          </div>
          <div className="divide-y divide-gray-700/50 max-h-[400px] overflow-y-auto" style={{ scrollbarWidth: "thin" }}>
            {slaBreaches.length === 0 ? (
              <div className="p-8 text-center">
                <svg className="w-8 h-8 text-emerald-500/40 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-sm text-gray-500">No SLA breaches. Great work!</p>
              </div>
            ) : (
              slaBreaches.map((breach, idx) => (
                <Link
                  key={idx}
                  href={`/companies/${breach.company_id}`}
                  className="flex items-center gap-3 px-5 py-3 hover:bg-white/5 transition-colors"
                >
                  <div className="w-2 h-2 rounded-full bg-red-500 shrink-0 animate-pulse" />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-white truncate">
                      {breach.company_name || `Company #${breach.company_id}`}
                    </p>
                    <p className="text-[10px] text-gray-500">
                      {breach.stage?.replace(/_/g, " ").toUpperCase()} - {breach.days_exceeded}d over SLA
                    </p>
                  </div>
                  <span className="text-[10px] text-red-400 font-bold shrink-0 bg-red-500/10 px-2 py-0.5 rounded-full border border-red-500/20">
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
