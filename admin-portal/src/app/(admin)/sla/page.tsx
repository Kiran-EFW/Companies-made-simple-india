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

function getSeverityColorValue(hours: number | undefined | null): string {
  if (hours == null) return "var(--color-text-secondary)";
  if (hours > 48) return "var(--color-error)";
  if (hours > 24) return "var(--color-warning)";
  return "var(--color-warning)";
}

function getSeverityBgStyle(hours: number | undefined | null): React.CSSProperties {
  if (hours == null) return { background: "rgba(107, 114, 128, 0.1)", borderColor: "rgba(107, 114, 128, 0.2)" };
  if (hours > 48) return { background: "var(--color-error-light)", borderColor: "rgba(239, 68, 68, 0.2)" };
  if (hours > 24) return { background: "var(--color-warning-light)", borderColor: "rgba(245, 158, 11, 0.2)" };
  return { background: "rgba(234, 179, 8, 0.1)", borderColor: "rgba(234, 179, 8, 0.2)" };
}

function getComplianceColorValue(rate: number | undefined | null): string {
  if (rate == null) return "var(--color-text-secondary)";
  if (rate >= 90) return "var(--color-success)";
  if (rate >= 70) return "var(--color-warning)";
  return "var(--color-error)";
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
            compliance_rate: o?.on_time_percentage ?? o?.compliance_rate ?? o?.compliance_percentage ?? 0,
            avg_processing_time:
              o?.avg_processing_hours ?? o?.avg_processing_time ?? o?.average_processing_time ?? 0,
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
          <div className="h-8 rounded w-56" style={{ background: "var(--color-bg-card)" }} />
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-28 rounded-xl" style={{ background: "var(--color-bg-card)" }} />
            ))}
          </div>
          <div className="h-6 rounded w-40" style={{ background: "var(--color-bg-card)" }} />
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 rounded-lg" style={{ background: "var(--color-bg-card)" }} />
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
        <p className="text-sm mt-1" style={{ color: "var(--color-text-secondary)" }}>
          Monitor service-level compliance and identify breaches across all
          companies.
        </p>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Companies Tracked */}
        <div className="rounded-xl p-5" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <p className="text-xs uppercase tracking-wider font-medium mb-1" style={{ color: "var(--color-text-muted)" }}>
            Companies Tracked
          </p>
          <p
            className="text-3xl font-bold"
            style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
          >
            {overview?.total_companies ?? "--"}
          </p>
        </div>

        {/* Compliance Rate */}
        <div className="rounded-xl p-5" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <p className="text-xs uppercase tracking-wider font-medium mb-1" style={{ color: "var(--color-text-muted)" }}>
            SLA Compliance
          </p>
          <p
            className="text-3xl font-bold"
            style={{ fontFamily: "var(--font-display)", color: getComplianceColorValue(overview?.compliance_rate) }}
          >
            {overview?.compliance_rate != null
              ? `${overview.compliance_rate}%`
              : "--"}
          </p>
          {overview?.compliance_rate != null && (
            <div className="mt-2 h-1.5 rounded-full overflow-hidden" style={{ background: "var(--color-bg-secondary)" }}>
              <div
                className="h-full rounded-full transition-all duration-700"
                style={{
                  width: `${Math.min(overview.compliance_rate, 100)}%`,
                  background: overview.compliance_rate >= 90
                    ? "var(--color-success)"
                    : overview.compliance_rate >= 70
                    ? "var(--color-warning)"
                    : "var(--color-error)",
                }}
              />
            </div>
          )}
        </div>

        {/* Avg Processing Time */}
        <div className="rounded-xl p-5" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <p className="text-xs uppercase tracking-wider font-medium mb-1" style={{ color: "var(--color-text-muted)" }}>
            Avg Processing Time
          </p>
          <p
            className="text-3xl font-bold"
            style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
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
          className="rounded-xl p-5"
          style={{
            border: (overview?.active_breaches ?? 0) > 0
              ? "1px solid rgba(239, 68, 68, 0.3)"
              : "1px solid var(--color-border)",
            background: (overview?.active_breaches ?? 0) > 0
              ? "rgba(239, 68, 68, 0.05)"
              : "var(--color-bg-card)",
          }}
        >
          <p className="text-xs uppercase tracking-wider font-medium mb-1" style={{ color: "var(--color-text-muted)" }}>
            Active Breaches
          </p>
          <p
            className="text-3xl font-bold"
            style={{
              fontFamily: "var(--font-display)",
              color: (overview?.active_breaches ?? 0) > 0
                ? "var(--color-error)"
                : "var(--color-success)",
            }}
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
            className="px-4 py-2 text-sm rounded-lg transition-colors"
            style={filter === tab.key
              ? { background: "rgba(139, 92, 246, 0.15)", color: "var(--color-accent-purple-light)", border: "1px solid rgba(139, 92, 246, 0.3)" }
              : { color: "var(--color-text-secondary)", border: "1px solid transparent" }
            }
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
      <div className="rounded-xl overflow-hidden" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
        <div className="px-5 py-4 flex items-center justify-between" style={{ borderBottom: "1px solid var(--color-border)" }}>
          <h2 className="text-sm font-semibold flex items-center gap-2">
            <svg
              className="w-4 h-4"
              style={{ color: "var(--color-warning)" }}
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
          <span className="text-xs" style={{ color: "var(--color-text-muted)" }}>
            {filteredBreaches.length}{" "}
            {filteredBreaches.length === 1 ? "breach" : "breaches"}
          </span>
        </div>

        {filteredBreaches.length === 0 ? (
          <div className="p-12 text-center">
            <svg
              className="w-10 h-10 mx-auto mb-3"
              style={{ color: "var(--color-text-muted)" }}
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
            <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
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
                <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                  <th className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                    Company
                  </th>
                  <th className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                    Step
                  </th>
                  <th className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                    Status
                  </th>
                  <th className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                    Assigned To
                  </th>
                  <th className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                    Breach Duration
                  </th>
                  <th className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                    Started At
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredBreaches.map((breach, idx) => {
                  const durationHours =
                    breach.breach_duration ??
                    breach.breach_duration_hours ??
                    null;
                  const severityColor = getSeverityColorValue(durationHours);
                  const severityBgStyle = getSeverityBgStyle(durationHours);
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
                      className={`transition-colors ${
                        breach.is_resolved ? "opacity-50" : ""
                      }`}
                    >
                      <td className="px-5 py-3 font-medium" style={{ color: "var(--color-text-primary)" }}>
                        {companyLabel}
                      </td>
                      <td className="px-5 py-3" style={{ color: "var(--color-text-primary)" }}>
                        {String(step).replace(/_/g, " ")}
                      </td>
                      <td className="px-5 py-3">
                        <span
                          className="inline-flex items-center text-[11px] px-2 py-0.5 rounded font-medium"
                          style={breach.is_resolved
                            ? { background: "rgba(16, 185, 129, 0.15)", border: "1px solid rgba(16, 185, 129, 0.3)", color: "var(--color-success)" }
                            : { background: "rgba(239, 68, 68, 0.15)", border: "1px solid rgba(239, 68, 68, 0.3)", color: "var(--color-error)" }
                          }
                        >
                          {breach.is_resolved
                            ? "RESOLVED"
                            : String(status)
                                .replace(/_/g, " ")
                                .toUpperCase()}
                        </span>
                      </td>
                      <td className="px-5 py-3" style={{ color: "var(--color-text-primary)" }}>
                        {assignee}
                      </td>
                      <td className="px-5 py-3">
                        <span
                          className="inline-flex items-center text-xs px-2 py-0.5 rounded font-semibold"
                          style={{ ...severityBgStyle, color: severityColor, border: `1px solid ${severityBgStyle.borderColor}` }}
                        >
                          {formatDuration(durationHours)}
                        </span>
                      </td>
                      <td className="px-5 py-3 text-xs" style={{ color: "var(--color-text-secondary)" }}>
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
