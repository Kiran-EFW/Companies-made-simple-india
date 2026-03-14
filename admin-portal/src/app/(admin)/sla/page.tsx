"use client";

import { useEffect, useState } from "react";
import { getSLAOverview, getSLABreaches } from "@/lib/api";
import { useToast } from "@/components/toast";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface SLAOverview {
  total_companies: number;
  compliance_rate: number;
  avg_processing_time: number | string;
  active_breaches: number;
}

interface SLABreach {
  id: number;
  company_name?: string;
  company_id?: number;
  step?: string;
  current_step?: string;
  status?: string;
  breach_status?: string;
  assigned_to?: string;
  assigned_to_name?: string;
  breach_duration?: number;
  breach_duration_hours?: number;
  started_at?: string;
  created_at?: string;
  is_resolved?: boolean;
  resolved_at?: string;
}

type FilterTab = "all" | "active" | "resolved";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDuration(hours: number | undefined | null): string {
  if (hours == null) return "--";
  if (hours < 1) return `${Math.round(hours * 60)}m`;
  if (hours < 24) return `${hours.toFixed(1)}h`;
  const days = Math.floor(hours / 24);
  const remaining = hours % 24;
  if (remaining === 0) return `${days}d`;
  return `${days}d ${Math.round(remaining)}h`;
}

function formatDate(dateStr: string | undefined | null): string {
  if (!dateStr) return "--";
  return new Date(dateStr).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getSeverityColor(hours: number | undefined | null): string {
  if (hours == null) return "text-gray-400";
  if (hours > 48) return "text-red-400";
  if (hours > 24) return "text-amber-400";
  return "text-yellow-400";
}

function getSeverityBg(hours: number | undefined | null): string {
  if (hours == null) return "bg-gray-500/10 border-gray-500/20";
  if (hours > 48) return "bg-red-500/10 border-red-500/20";
  if (hours > 24) return "bg-amber-500/10 border-amber-500/20";
  return "bg-yellow-500/10 border-yellow-500/20";
}

function getComplianceColor(rate: number | undefined | null): string {
  if (rate == null) return "text-gray-400";
  if (rate >= 90) return "text-emerald-400";
  if (rate >= 70) return "text-amber-400";
  return "text-red-400";
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function SLATrackingPage() {
  const { toast } = useToast();
  const [overview, setOverview] = useState<SLAOverview | null>(null);
  const [breaches, setBreaches] = useState<SLABreach[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<FilterTab>("all");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [overviewRes, breachesRes] = await Promise.allSettled([
          getSLAOverview(),
          getSLABreaches(),
        ]);

        // Parse overview -- handle data, data.overview, or top-level
        if (overviewRes.status === "fulfilled") {
          const raw = overviewRes.value;
          const o = raw?.overview ?? raw?.data?.overview ?? raw?.data ?? raw;
          setOverview({
            total_companies: o?.total_companies ?? o?.total ?? 0,
            compliance_rate: o?.compliance_rate ?? o?.compliance_percentage ?? 0,
            avg_processing_time:
              o?.avg_processing_time ?? o?.average_processing_time ?? 0,
            active_breaches: o?.active_breaches ?? o?.breaches_count ?? 0,
          });
        } else {
          toast("Failed to load SLA overview", "error");
        }

        // Parse breaches -- handle data, data.breaches, or array
        if (breachesRes.status === "fulfilled") {
          const raw = breachesRes.value;
          let list: SLABreach[] = [];
          if (Array.isArray(raw)) {
            list = raw;
          } else if (Array.isArray(raw?.breaches)) {
            list = raw.breaches;
          } else if (Array.isArray(raw?.data?.breaches)) {
            list = raw.data.breaches;
          } else if (Array.isArray(raw?.data)) {
            list = raw.data;
          }
          setBreaches(list);
        } else {
          toast("Failed to load SLA breaches", "error");
        }
      } catch (e: any) {
        toast(e.message || "Failed to load SLA data", "error");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filtered breaches
  const filteredBreaches = breaches.filter((b) => {
    if (filter === "active") return !b.is_resolved;
    if (filter === "resolved") return b.is_resolved;
    return true;
  });

  // Loading skeleton
  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-800 rounded w-56" />
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-28 bg-gray-800 rounded-xl" />
            ))}
          </div>
          <div className="h-6 bg-gray-800 rounded w-40" />
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-gray-800 rounded-lg" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  const tabs: { key: FilterTab; label: string }[] = [
    { key: "all", label: "All" },
    { key: "active", label: "Active Only" },
    { key: "resolved", label: "Resolved" },
  ];

  return (
    <div className="p-6 lg:p-8 max-w-6xl space-y-8">
      {/* Header */}
      <div>
        <h1
          className="text-2xl font-bold"
          style={{ fontFamily: "var(--font-display)" }}
        >
          SLA Tracking
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          Monitor service-level compliance and identify breaches across all
          companies.
        </p>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Companies Tracked */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-1">
            Companies Tracked
          </p>
          <p
            className="text-3xl font-bold text-white"
            style={{ fontFamily: "var(--font-display)" }}
          >
            {overview?.total_companies ?? "--"}
          </p>
        </div>

        {/* Compliance Rate */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-1">
            SLA Compliance
          </p>
          <p
            className={`text-3xl font-bold ${getComplianceColor(
              overview?.compliance_rate
            )}`}
            style={{ fontFamily: "var(--font-display)" }}
          >
            {overview?.compliance_rate != null
              ? `${overview.compliance_rate}%`
              : "--"}
          </p>
          {overview?.compliance_rate != null && (
            <div className="mt-2 h-1.5 bg-gray-900/60 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-700 ${
                  overview.compliance_rate >= 90
                    ? "bg-emerald-500"
                    : overview.compliance_rate >= 70
                    ? "bg-amber-500"
                    : "bg-red-500"
                }`}
                style={{ width: `${Math.min(overview.compliance_rate, 100)}%` }}
              />
            </div>
          )}
        </div>

        {/* Avg Processing Time */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-1">
            Avg Processing Time
          </p>
          <p
            className="text-3xl font-bold text-white"
            style={{ fontFamily: "var(--font-display)" }}
          >
            {overview?.avg_processing_time != null
              ? typeof overview.avg_processing_time === "number"
                ? `${overview.avg_processing_time}d`
                : overview.avg_processing_time
              : "--"}
          </p>
        </div>

        {/* Active Breaches */}
        <div
          className={`rounded-xl border p-5 ${
            (overview?.active_breaches ?? 0) > 0
              ? "border-red-500/30 bg-red-500/5"
              : "border-gray-700 bg-gray-800/50"
          }`}
        >
          <p className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-1">
            Active Breaches
          </p>
          <p
            className={`text-3xl font-bold ${
              (overview?.active_breaches ?? 0) > 0
                ? "text-red-400"
                : "text-emerald-400"
            }`}
            style={{ fontFamily: "var(--font-display)" }}
          >
            {overview?.active_breaches ?? 0}
          </p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-1">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={`px-4 py-2 text-sm rounded-lg transition-colors ${
              filter === tab.key
                ? "bg-purple-500/15 text-purple-400 border border-purple-500/30"
                : "text-gray-400 hover:text-gray-300 hover:bg-white/5"
            }`}
          >
            {tab.label}
            {tab.key === "active" && (
              <span className="ml-1.5 text-xs opacity-70">
                ({breaches.filter((b) => !b.is_resolved).length})
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Breaches Table */}
      <div className="rounded-xl border border-gray-700 bg-gray-800/50 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-700 flex items-center justify-between">
          <h2 className="text-sm font-semibold flex items-center gap-2">
            <svg
              className="w-4 h-4 text-amber-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
              />
            </svg>
            SLA Breaches
          </h2>
          <span className="text-xs text-gray-500">
            {filteredBreaches.length}{" "}
            {filteredBreaches.length === 1 ? "breach" : "breaches"}
          </span>
        </div>

        {filteredBreaches.length === 0 ? (
          <div className="p-12 text-center">
            <svg
              className="w-10 h-10 text-gray-600 mx-auto mb-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <p className="text-sm text-gray-500">
              {filter === "active"
                ? "No active SLA breaches. All systems operating within SLA."
                : filter === "resolved"
                ? "No resolved breaches found."
                : "No SLA breaches recorded."}
            </p>
          </div>
        ) : (
          <div
            className="overflow-x-auto"
            style={{ scrollbarWidth: "thin", scrollbarColor: "rgba(139, 92, 246, 0.3) transparent" }}
          >
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                    Company
                  </th>
                  <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                    Step
                  </th>
                  <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                    Status
                  </th>
                  <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                    Assigned To
                  </th>
                  <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                    Breach Duration
                  </th>
                  <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">
                    Started At
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700/50">
                {filteredBreaches.map((breach, idx) => {
                  const durationHours =
                    breach.breach_duration ??
                    breach.breach_duration_hours ??
                    null;
                  const severityColor = getSeverityColor(durationHours);
                  const severityBg = getSeverityBg(durationHours);
                  const companyLabel =
                    breach.company_name ??
                    (breach.company_id
                      ? `Company #${breach.company_id}`
                      : "--");
                  const step =
                    breach.step ?? breach.current_step ?? "--";
                  const status =
                    breach.status ?? breach.breach_status ?? "--";
                  const assignee =
                    breach.assigned_to_name ?? breach.assigned_to ?? "--";
                  const startedAt =
                    breach.started_at ?? breach.created_at ?? null;

                  return (
                    <tr
                      key={breach.id ?? idx}
                      className={`hover:bg-white/5 transition-colors ${
                        breach.is_resolved ? "opacity-50" : ""
                      }`}
                    >
                      <td className="px-5 py-3 text-gray-200 font-medium">
                        {companyLabel}
                      </td>
                      <td className="px-5 py-3 text-gray-300">
                        {String(step).replace(/_/g, " ")}
                      </td>
                      <td className="px-5 py-3">
                        <span
                          className={`inline-flex items-center text-[11px] px-2 py-0.5 rounded border font-medium ${
                            breach.is_resolved
                              ? "bg-emerald-500/15 border-emerald-500/30 text-emerald-400"
                              : "bg-red-500/15 border-red-500/30 text-red-400"
                          }`}
                        >
                          {breach.is_resolved
                            ? "RESOLVED"
                            : String(status)
                                .replace(/_/g, " ")
                                .toUpperCase()}
                        </span>
                      </td>
                      <td className="px-5 py-3 text-gray-300">
                        {assignee}
                      </td>
                      <td className="px-5 py-3">
                        <span
                          className={`inline-flex items-center text-xs px-2 py-0.5 rounded border font-semibold ${severityBg} ${severityColor}`}
                        >
                          {formatDuration(durationHours)}
                        </span>
                      </td>
                      <td className="px-5 py-3 text-gray-400 text-xs">
                        {formatDate(startedAt)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
