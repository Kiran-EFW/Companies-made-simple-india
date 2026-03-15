"use client";

import { useEffect, useState } from "react";
import { getEscalations, resolveEscalation, getEscalationRules } from "@/lib/api";
import { useToast } from "@/components/toast";

const ACTION_COLORS: Record<string, string> = {
  notify: "var(--color-info)",
  reassign: "var(--color-warning)",
  notify_and_reassign: "var(--color-warning)",
  escalate_to_lead: "var(--color-error)",
};

function formatTimestamp(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

  if (diffHours < 1) {
    const diffMins = Math.floor(diffMs / (1000 * 60));
    return `${diffMins}m ago`;
  }
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function EscalationsPage() {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState<"escalations" | "rules">("escalations");
  const [escalations, setEscalations] = useState<any[]>([]);
  const [rules, setRules] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [rulesLoading, setRulesLoading] = useState(false);
  const [showResolved, setShowResolved] = useState(false);
  const [resolvingId, setResolvingId] = useState<number | null>(null);
  const [resolutionNotes, setResolutionNotes] = useState<Record<number, string>>({});

  const fetchEscalations = async () => {
    try {
      const data = await getEscalations(
        showResolved ? undefined : { is_resolved: false }
      );
      setEscalations(Array.isArray(data) ? data : data?.escalations || []);
    } catch (e: any) {
      toast(e.message || "Failed to load escalations", "error");
    } finally {
      setLoading(false);
    }
  };

  const fetchRules = async () => {
    setRulesLoading(true);
    try {
      const data = await getEscalationRules();
      setRules(Array.isArray(data) ? data : data?.rules || []);
    } catch (e: any) {
      toast(e.message || "Failed to load escalation rules", "error");
    } finally {
      setRulesLoading(false);
    }
  };

  useEffect(() => {
    fetchEscalations();
  }, [showResolved]);

  useEffect(() => {
    if (activeTab === "rules" && rules.length === 0) {
      fetchRules();
    }
  }, [activeTab]);

  const handleResolve = async (escalationId: number) => {
    const notes = resolutionNotes[escalationId] || "";
    setResolvingId(escalationId);
    try {
      await resolveEscalation(escalationId, notes);
      setResolutionNotes((prev) => {
        const next = { ...prev };
        delete next[escalationId];
        return next;
      });
      toast("Escalation resolved", "success");
      fetchEscalations();
    } catch (e: any) {
      toast(e.message || "Failed to resolve escalation", "error");
    } finally {
      setResolvingId(null);
    }
  };

  // Stats
  const activeEscalations = escalations.filter((e) => !e.is_resolved);
  const resolvedToday = escalations.filter((e) => {
    if (!e.is_resolved || !e.resolved_at) return false;
    const resolved = new Date(e.resolved_at);
    const today = new Date();
    return (
      resolved.getDate() === today.getDate() &&
      resolved.getMonth() === today.getMonth() &&
      resolved.getFullYear() === today.getFullYear()
    );
  });

  const avgResolutionTime = (() => {
    const resolved = escalations.filter((e) => e.is_resolved && e.resolved_at && e.created_at);
    if (resolved.length === 0) return "N/A";
    const totalMs = resolved.reduce((sum, e) => {
      return sum + (new Date(e.resolved_at).getTime() - new Date(e.created_at).getTime());
    }, 0);
    const avgHours = totalMs / resolved.length / (1000 * 60 * 60);
    if (avgHours < 1) return `${Math.round(avgHours * 60)}m`;
    if (avgHours < 24) return `${avgHours.toFixed(1)}h`;
    return `${(avgHours / 24).toFixed(1)}d`;
  })();

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 rounded w-48" style={{ background: "var(--color-bg-card)" }} />
          <div className="grid grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 rounded-lg" style={{ background: "var(--color-bg-card)" }} />
            ))}
          </div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 rounded-lg" style={{ background: "var(--color-bg-card)" }} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1
          className="text-2xl font-bold"
          style={{ fontFamily: "var(--font-display)" }}
        >
          Escalations
        </h1>
        <div className="flex items-center gap-1 mt-3">
          <button
            onClick={() => setActiveTab("escalations")}
            className={`px-4 py-2 text-sm rounded-lg transition-colors ${
              activeTab === "escalations"
                ? "bg-purple-500/15 border border-purple-500/30"
                : ""
            }`}
            style={{ color: activeTab === "escalations" ? "var(--color-accent-purple-light)" : "var(--color-text-secondary)" }}
          >
            Active Escalations
          </button>
          <button
            onClick={() => setActiveTab("rules")}
            className={`px-4 py-2 text-sm rounded-lg transition-colors ${
              activeTab === "rules"
                ? "bg-cyan-500/15 text-cyan-400 border border-cyan-500/30"
                : ""
            }`}
            style={{ color: activeTab === "rules" ? undefined : "var(--color-text-secondary)" }}
          >
            Escalation Rules
          </button>
        </div>
      </div>

      {/* Active Escalations Tab */}
      {activeTab === "escalations" && (
        <>
          {/* Stats */}
          <div className="grid grid-cols-3 gap-4">
            <div className="glass-card p-4">
              <p className="text-xs uppercase tracking-wider" style={{ color: "var(--color-text-secondary)" }}>
                Total Active
              </p>
              <p className="text-2xl font-bold mt-1" style={{ color: "var(--color-warning)" }}>
                {activeEscalations.length}
              </p>
            </div>
            <div className="glass-card p-4">
              <p className="text-xs uppercase tracking-wider" style={{ color: "var(--color-text-secondary)" }}>
                Resolved Today
              </p>
              <p className="text-2xl font-bold mt-1" style={{ color: "var(--color-success)" }}>
                {resolvedToday.length}
              </p>
            </div>
            <div className="glass-card p-4">
              <p className="text-xs uppercase tracking-wider" style={{ color: "var(--color-text-secondary)" }}>
                Avg Resolution Time
              </p>
              <p className="text-2xl font-bold text-cyan-400 mt-1">
                {avgResolutionTime}
              </p>
            </div>
          </div>

          {/* Filter Toggle */}
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-primary)" }}>
              {showResolved ? "All Escalations" : "Active Escalations"} (
              {escalations.length})
            </h2>
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <span className="text-xs" style={{ color: "var(--color-text-secondary)" }}>Show Resolved</span>
              <button
                onClick={() => setShowResolved(!showResolved)}
                className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                  showResolved ? "bg-purple-500/40" : ""
                }`}
                style={!showResolved ? { background: "var(--color-border-light)" } : undefined}
              >
                <span
                  className={`inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform ${
                    showResolved ? "translate-x-[18px]" : "translate-x-[3px]"
                  }`}
                />
              </button>
            </label>
          </div>

          {/* Escalation List */}
          <div className="space-y-3">
            {escalations.length === 0 ? (
              <div className="glass-card p-8 text-center" style={{ color: "var(--color-text-muted)" }}>
                <p>
                  {showResolved
                    ? "No escalations found."
                    : "No active escalations. Everything is under control."}
                </p>
              </div>
            ) : (
              escalations.map((esc) => {
                const isResolved = esc.is_resolved;
                const borderColor = isResolved
                  ? "border-emerald-500/30"
                  : "border-amber-500/30";
                const actionColor =
                  ACTION_COLORS[esc.action] || "var(--color-text-secondary)";

                return (
                  <div
                    key={esc.id}
                    className={`glass-card p-4 ${borderColor} ${
                      isResolved ? "opacity-60" : ""
                    }`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0 space-y-2">
                        {/* Rule name and status */}
                        <div className="flex items-center gap-2 flex-wrap">
                          <span
                            className="text-sm font-medium"
                            style={{ color: isResolved ? "var(--color-text-secondary)" : "var(--color-text-primary)" }}
                          >
                            {esc.rule_name || esc.escalation_rule?.name || "Unknown Rule"}
                          </span>
                          {isResolved && (
                            <span className="text-[10px] px-1.5 py-0.5 rounded border bg-emerald-500/15 border-emerald-500/30" style={{ color: "var(--color-success)" }}>
                              RESOLVED
                            </span>
                          )}
                        </div>

                        {/* Details grid */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-x-4 gap-y-1 text-xs">
                          <div>
                            <span style={{ color: "var(--color-text-muted)" }}>Target: </span>
                            <span style={{ color: "var(--color-text-primary)" }}>
                              {esc.target_type?.replace(/_/g, " ")}
                            </span>
                          </div>
                          <div>
                            <span style={{ color: "var(--color-text-muted)" }}>Target ID: </span>
                            <span className="font-mono" style={{ color: "var(--color-text-primary)" }}>
                              {esc.target_id}
                            </span>
                          </div>
                          <div>
                            <span style={{ color: "var(--color-text-muted)" }}>Company: </span>
                            <span className="font-mono" style={{ color: "var(--color-text-primary)" }}>
                              {esc.company_id}
                            </span>
                          </div>
                          <div>
                            <span style={{ color: "var(--color-text-muted)" }}>Action: </span>
                            <span style={{ color: actionColor }}>
                              {esc.action?.replace(/_/g, " ")}
                            </span>
                          </div>
                        </div>

                        {/* Timestamp */}
                        <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                          Created {formatTimestamp(esc.created_at)}{" "}
                          <span style={{ color: "var(--color-text-muted)" }}>
                            ({formatDate(esc.created_at)})
                          </span>
                        </div>

                        {/* Resolution notes if resolved */}
                        {isResolved && esc.resolution_notes && (
                          <div className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
                            <span style={{ color: "var(--color-text-muted)" }}>Resolution: </span>
                            {esc.resolution_notes}
                          </div>
                        )}
                      </div>

                      {/* Resolve controls */}
                      {!isResolved && (
                        <div className="flex flex-col items-end gap-2 shrink-0">
                          <input
                            type="text"
                            placeholder="Resolution notes..."
                            value={resolutionNotes[esc.id] || ""}
                            onChange={(e) =>
                              setResolutionNotes((prev) => ({
                                ...prev,
                                [esc.id]: e.target.value,
                              }))
                            }
                            className="w-48 text-xs px-2.5 py-1.5 rounded bg-white/5 border border-white/10 placeholder-gray-600 focus:outline-none focus:border-purple-500/40"
                            style={{ color: "var(--color-text-primary)" }}
                          />
                          <button
                            onClick={() => handleResolve(esc.id)}
                            disabled={resolvingId === esc.id}
                            className="text-xs px-3 py-1.5 rounded bg-emerald-500/15 hover:bg-emerald-500/25 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            style={{ color: "var(--color-success)" }}
                          >
                            {resolvingId === esc.id ? "Resolving..." : "Resolve"}
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </>
      )}

      {/* Escalation Rules Tab */}
      {activeTab === "rules" && (
        <>
          <h2 className="text-sm font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-primary)" }}>
            Escalation Rules ({rules.length})
          </h2>

          {rulesLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="h-28 rounded-lg animate-pulse"
                  style={{ background: "var(--color-bg-card)" }}
                />
              ))}
            </div>
          ) : rules.length === 0 ? (
            <div className="glass-card p-8 text-center" style={{ color: "var(--color-text-muted)" }}>
              <p>No escalation rules configured.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {rules.map((rule) => {
                const actionColor =
                  ACTION_COLORS[rule.action] || "var(--color-text-secondary)";

                return (
                  <div
                    key={rule.id}
                    className={`glass-card p-4 ${
                      rule.is_active
                        ? "border-purple-500/20"
                        : "border-gray-700/30 opacity-50"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0 space-y-2">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-medium" style={{ color: "var(--color-text-primary)" }}>
                            {rule.name}
                          </span>
                          <span
                            className={`text-[10px] px-1.5 py-0.5 rounded border ${
                              rule.is_active
                                ? "bg-emerald-500/15 border-emerald-500/30"
                                : "bg-gray-500/15 border-gray-500/30"
                            }`}
                            style={{ color: rule.is_active ? "var(--color-success)" : "var(--color-text-muted)" }}
                          >
                            {rule.is_active ? "ACTIVE" : "INACTIVE"}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-x-4 gap-y-1 text-xs">
                          <div>
                            <span style={{ color: "var(--color-text-muted)" }}>Trigger: </span>
                            <span style={{ color: "var(--color-text-primary)" }}>
                              {rule.trigger_type?.replace(/_/g, " ")}
                            </span>
                          </div>
                          <div>
                            <span style={{ color: "var(--color-text-muted)" }}>Threshold: </span>
                            <span className="text-cyan-400">
                              {rule.threshold_hours}h
                            </span>
                          </div>
                          <div>
                            <span style={{ color: "var(--color-text-muted)" }}>Action: </span>
                            <span style={{ color: actionColor }}>
                              {rule.action?.replace(/_/g, " ")}
                            </span>
                          </div>
                          <div>
                            <span style={{ color: "var(--color-text-muted)" }}>Escalate to: </span>
                            <span style={{ color: "var(--color-accent-purple-light)" }}>
                              {rule.escalate_to_role?.replace(/_/g, " ") || "N/A"}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}
