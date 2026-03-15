"use client";

import { useState, useEffect } from "react";
import {
  getAdminServiceRequests,
  getAdminSubscriptions,
  getServicesStats,
  updateServiceRequestStatus,
} from "@/lib/api";

const STATUS_OPTIONS = [
  { value: "", label: "All" },
  { value: "pending", label: "Pending" },
  { value: "accepted", label: "Accepted" },
  { value: "in_progress", label: "In Progress" },
  { value: "documents_needed", label: "Docs Needed" },
  { value: "completed", label: "Completed" },
  { value: "cancelled", label: "Cancelled" },
];

const STATUS_STYLES: Record<string, string> = {
  pending: "background: var(--color-warning-light); color: var(--color-warning)",
  accepted: "background: var(--color-info-light); color: var(--color-info)",
  in_progress: "background: var(--color-info-light); color: var(--color-info)",
  documents_needed: "background: var(--color-warning-light); color: var(--color-warning)",
  completed: "background: var(--color-success-light); color: var(--color-success)",
  cancelled: "background: rgba(148,163,184,0.1); color: var(--color-text-muted)",
  active: "background: var(--color-success-light); color: var(--color-success)",
  past_due: "background: var(--color-error-light); color: var(--color-error)",
};

export default function ServicesAdminPage() {
  const [activeTab, setActiveTab] = useState<"requests" | "subscriptions">("requests");
  const [requests, setRequests] = useState<any[]>([]);
  const [subscriptions, setSubscriptions] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [totalRequests, setTotalRequests] = useState(0);
  const [totalSubs, setTotalSubs] = useState(0);
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [reqData, subData, statsData] = await Promise.all([
        getAdminServiceRequests({ status: statusFilter || undefined }),
        getAdminSubscriptions(),
        getServicesStats(),
      ]);
      setRequests(reqData.requests);
      setTotalRequests(reqData.total);
      setSubscriptions(subData.subscriptions);
      setTotalSubs(subData.total);
      setStats(statsData);
    } catch (err) {
      console.error("Failed to load services data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, [statusFilter]);

  const handleStatusUpdate = async (requestId: number, newStatus: string) => {
    setUpdatingId(requestId);
    try {
      await updateServiceRequestStatus(requestId, newStatus);
      await loadData();
    } catch (err) {
      console.error("Status update failed:", err);
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="p-6 lg:p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold" style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}>
          Services & Compliance
        </h1>
        <p className="text-sm mt-1" style={{ color: "var(--color-text-secondary)" }}>
          Manage service requests, subscriptions, and compliance workflow
        </p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          {[
            { label: "Pending Requests", value: stats.service_requests?.pending || 0, color: "var(--color-warning)" },
            { label: "In Progress", value: stats.service_requests?.in_progress || 0, color: "var(--color-info)" },
            { label: "Completed", value: stats.service_requests?.completed || 0, color: "var(--color-success)" },
            { label: "Active Subs", value: stats.subscriptions?.active || 0, color: "var(--color-accent-purple)" },
            { label: "Connected Accounts", value: stats.accounting_connections || 0, color: "var(--color-accent-emerald)" },
          ].map((card, i) => (
            <div key={i} className="glass-card rounded-xl p-4">
              <p className="text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>{card.label}</p>
              <p className="text-2xl font-bold" style={{ color: card.color }}>{card.value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Revenue card */}
      {stats?.revenue && (
        <div className="glass-card rounded-xl p-5 mb-8">
          <h2 className="text-sm font-semibold mb-3" style={{ color: "var(--color-text-primary)" }}>Services Revenue</h2>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>Paid Services</p>
              <p className="text-xl font-bold" style={{ color: "var(--color-success)" }}>
                Rs {(stats.revenue.services_paid || 0).toLocaleString("en-IN")}
              </p>
            </div>
            <div>
              <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>Subscription ARR</p>
              <p className="text-xl font-bold" style={{ color: "var(--color-accent-purple)" }}>
                Rs {(stats.revenue.subscription_arr || 0).toLocaleString("en-IN")}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 glass-card rounded-lg p-1 w-fit mb-6">
        {[
          { key: "requests" as const, label: "Service Requests", count: totalRequests },
          { key: "subscriptions" as const, label: "Subscriptions", count: totalSubs },
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
            <span className="ml-2 text-xs opacity-70">({tab.count})</span>
          </button>
        ))}
      </div>

      {activeTab === "requests" && (
        <>
          {/* Status filter */}
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

          {/* Requests table */}
          {loading ? (
            <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>Loading...</div>
          ) : requests.length === 0 ? (
            <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>
              No service requests found
            </div>
          ) : (
            <div className="glass-card rounded-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                    {["ID", "Company", "Service", "Category", "Amount", "Status", "Date", "Actions"].map(h => (
                      <th key={h} className="text-left px-4 py-3 text-xs font-medium" style={{ color: "var(--color-text-muted)" }}>
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {requests.map(req => (
                    <tr key={req.id} style={{ borderBottom: "1px solid var(--color-border)" }}>
                      <td className="px-4 py-3 text-xs" style={{ color: "var(--color-text-muted)" }}>#{req.id}</td>
                      <td className="px-4 py-3">
                        <p className="font-medium text-xs" style={{ color: "var(--color-text-primary)" }}>{req.company_name}</p>
                        <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>{req.user_email}</p>
                      </td>
                      <td className="px-4 py-3 text-xs" style={{ color: "var(--color-text-primary)" }}>{req.service_name}</td>
                      <td className="px-4 py-3 text-xs capitalize" style={{ color: "var(--color-text-secondary)" }}>{req.category}</td>
                      <td className="px-4 py-3 text-xs font-semibold" style={{ color: "var(--color-text-primary)" }}>
                        Rs {(req.total_amount || 0).toLocaleString("en-IN")}
                        {req.is_paid && <span className="ml-1 text-[10px]" style={{ color: "var(--color-success)" }}>Paid</span>}
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full" style={
                          STATUS_STYLES[req.status]
                            ? Object.fromEntries(STATUS_STYLES[req.status].split("; ").map(s => { const [k,v] = s.split(": "); return [k, v]; }))
                            : {}
                        }>
                          {req.status?.replace(/_/g, " ")}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                        {req.created_at ? new Date(req.created_at).toLocaleDateString("en-IN") : "—"}
                      </td>
                      <td className="px-4 py-3">
                        <select
                          value=""
                          onChange={e => { if (e.target.value) handleStatusUpdate(req.id, e.target.value); }}
                          disabled={updatingId === req.id}
                          className="text-[10px] rounded px-1 py-0.5"
                          style={{ background: "var(--color-bg-input)", color: "var(--color-text-primary)", border: "1px solid var(--color-border)" }}
                        >
                          <option value="">Update...</option>
                          <option value="accepted">Accept</option>
                          <option value="in_progress">In Progress</option>
                          <option value="documents_needed">Docs Needed</option>
                          <option value="completed">Complete</option>
                          <option value="cancelled">Cancel</option>
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {activeTab === "subscriptions" && (
        <>
          {loading ? (
            <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>Loading...</div>
          ) : subscriptions.length === 0 ? (
            <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>
              No subscriptions found
            </div>
          ) : (
            <div className="glass-card rounded-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                    {["ID", "Company", "Plan", "Interval", "Amount", "Status", "Period", "Created"].map(h => (
                      <th key={h} className="text-left px-4 py-3 text-xs font-medium" style={{ color: "var(--color-text-muted)" }}>
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {subscriptions.map(sub => (
                    <tr key={sub.id} style={{ borderBottom: "1px solid var(--color-border)" }}>
                      <td className="px-4 py-3 text-xs" style={{ color: "var(--color-text-muted)" }}>#{sub.id}</td>
                      <td className="px-4 py-3">
                        <p className="font-medium text-xs" style={{ color: "var(--color-text-primary)" }}>{sub.company_name}</p>
                        <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>{sub.user_email}</p>
                      </td>
                      <td className="px-4 py-3 text-xs font-medium" style={{ color: "var(--color-text-primary)" }}>{sub.plan_name}</td>
                      <td className="px-4 py-3 text-xs capitalize" style={{ color: "var(--color-text-secondary)" }}>{sub.interval}</td>
                      <td className="px-4 py-3 text-xs font-semibold" style={{ color: "var(--color-text-primary)" }}>
                        Rs {(sub.amount || 0).toLocaleString("en-IN")}/{sub.interval === "annual" ? "yr" : "mo"}
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full" style={
                          STATUS_STYLES[sub.status]
                            ? Object.fromEntries(STATUS_STYLES[sub.status].split("; ").map((s: string) => { const [k,v] = s.split(": "); return [k, v]; }))
                            : {}
                        }>
                          {sub.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                        {sub.current_period_end
                          ? `Renews ${new Date(sub.current_period_end).toLocaleDateString("en-IN")}`
                          : "—"}
                      </td>
                      <td className="px-4 py-3 text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                        {sub.created_at ? new Date(sub.created_at).toLocaleDateString("en-IN") : "—"}
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
