"use client";

import { useEffect, useState } from "react";
import {
  getAdminAnalytics,
  getAdminFunnel,
  getAdminRevenue,
  getSLAOverview,
  getSLABreaches,
} from "@/lib/api";

interface FunnelStage {
  stage: string;
  count: number;
  percentage: number;
}

export default function AdminAnalyticsPage() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [funnel, setFunnel] = useState<FunnelStage[]>([]);
  const [revenue, setRevenue] = useState<any>(null);
  const [slaOverview, setSLAOverview] = useState<any>(null);
  const [slaBreaches, setSLABreaches] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [analyticsRes, funnelRes, revenueRes, slaRes, breachesRes] = await Promise.allSettled([
          getAdminAnalytics(),
          getAdminFunnel(),
          getAdminRevenue(),
          getSLAOverview(),
          getSLABreaches(),
        ]);

        if (analyticsRes.status === "fulfilled") setAnalytics(analyticsRes.value);
        if (funnelRes.status === "fulfilled") {
          const funnelData = funnelRes.value;
          if (Array.isArray(funnelData)) {
            setFunnel(funnelData);
          } else if (funnelData?.stages) {
            setFunnel(funnelData.stages);
          }
        }
        if (revenueRes.status === "fulfilled") setRevenue(revenueRes.value);
        if (slaRes.status === "fulfilled") setSLAOverview(slaRes.value);
        if (breachesRes.status === "fulfilled") setSLABreaches(breachesRes.value || []);
      } catch (err) {
        console.error("Failed to fetch analytics:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchAll();
  }, []);

  if (loading) {
    return (
      <div className="p-12 flex items-center justify-center">
        <div className="animate-pulse" style={{ color: "var(--color-text-muted)" }}>Loading analytics...</div>
      </div>
    );
  }

  const entityDistribution = analytics?.entity_distribution || analytics?.entity_types || {};
  const entityEntries = Object.entries(entityDistribution).sort(
    (a, b) => (b[1] as number) - (a[1] as number)
  );
  const maxEntityCount = entityEntries.length > 0 ? Math.max(...entityEntries.map(([, v]) => v as number)) : 1;

  const stateDistribution = analytics?.state_distribution || analytics?.states || {};
  const stateEntries = Object.entries(stateDistribution).sort(
    (a, b) => (b[1] as number) - (a[1] as number)
  );

  const monthlyRevenue = revenue?.monthly || revenue?.payments_by_month || [];
  const funnelMax = funnel.length > 0 ? Math.max(...funnel.map((f) => f.count)) : 1;

  return (
    <div className="p-6 lg:p-8 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>Analytics</h1>
        <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>Performance metrics, funnel analysis, and revenue insights.</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        <div className="rounded-xl p-5" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <p className="text-xs uppercase tracking-wider font-medium mb-1" style={{ color: "var(--color-text-muted)" }}>Total Companies</p>
          <p className="text-3xl font-bold" style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}>
            {analytics?.total_companies ?? "--"}
          </p>
        </div>
        <div className="rounded-xl p-5" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <p className="text-xs uppercase tracking-wider font-medium mb-1" style={{ color: "var(--color-text-muted)" }}>Active</p>
          <p className="text-3xl font-bold" style={{ fontFamily: "var(--font-display)", color: "var(--color-info)" }}>
            {analytics?.filed_count ?? "--"}
          </p>
        </div>
        <div className="rounded-xl p-5" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <p className="text-xs uppercase tracking-wider font-medium mb-1" style={{ color: "var(--color-text-muted)" }}>Completed</p>
          <p className="text-3xl font-bold" style={{ fontFamily: "var(--font-display)", color: "var(--color-success)" }}>
            {analytics?.approved_count ?? "--"}
          </p>
        </div>
        <div className="rounded-xl p-5" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <p className="text-xs uppercase tracking-wider font-medium mb-1" style={{ color: "var(--color-text-muted)" }}>Revenue</p>
          <p className="text-3xl font-bold" style={{ fontFamily: "var(--font-display)", color: "var(--color-warning)" }}>
            {analytics?.revenue_total != null ? `₹${(analytics.revenue_total / 1000).toFixed(0)}K` : "--"}
          </p>
        </div>
        <div className="rounded-xl p-5" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <p className="text-xs uppercase tracking-wider font-medium mb-1" style={{ color: "var(--color-text-muted)" }}>SLA Rate</p>
          <p className="text-3xl font-bold" style={{
            fontFamily: "var(--font-display)",
            color: slaOverview?.on_time_percentage >= 90 ? "var(--color-success)" :
              slaOverview?.on_time_percentage >= 70 ? "var(--color-warning)" : "var(--color-error)"
          }}>
            {slaOverview?.on_time_percentage != null ? `${slaOverview.on_time_percentage}%` : "--"}
          </p>
        </div>
      </div>

      {/* Funnel Chart */}
      <div className="rounded-xl p-6 mb-8" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
        <h2 className="text-lg font-bold mb-6 flex items-center gap-2">
          <svg className="w-5 h-5" style={{ color: "var(--color-accent-purple-light)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25 0 01-.659 1.591l-5.432 5.432a2.25 2.25 0 00-.659 1.591v2.927a2.25 2.25 0 01-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 00-.659-1.591L3.659 7.409A2.25 2.25 0 013 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0112 3z" />
          </svg>
          Conversion Funnel
        </h2>
        {funnel.length > 0 ? (
          <div className="space-y-4">
            {funnel.map((stage, idx) => {
              const widthPercent = Math.max(8, (stage.count / funnelMax) * 100);
              const colors = ["bg-purple-500", "bg-blue-500", "bg-cyan-500", "bg-emerald-500", "bg-amber-500", "bg-rose-500"];
              const barColor = colors[idx % colors.length];

              return (
                <div key={stage.stage} className="flex items-center gap-4">
                  <div className="w-32 shrink-0">
                    <p className="text-xs font-medium" style={{ color: "var(--color-text-primary)" }}>{stage.stage}</p>
                  </div>
                  <div className="flex-1 relative">
                    <div className="h-8 rounded-lg overflow-hidden" style={{ background: "var(--color-bg-secondary)" }}>
                      <div
                        className={`h-full ${barColor} rounded-lg transition-all duration-500 flex items-center justify-end pr-3`}
                        style={{ width: `${widthPercent}%` }}
                      >
                        <span className="text-xs font-bold" style={{ color: "var(--color-text-primary)" }}>{stage.count}</span>
                      </div>
                    </div>
                  </div>
                  <div className="w-16 text-right shrink-0">
                    <span className="text-xs font-semibold" style={{
                      color: stage.percentage >= 80 ? "var(--color-success)" :
                        stage.percentage >= 50 ? "var(--color-warning)" : "var(--color-error)"
                    }}>
                      {stage.percentage}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-sm text-center py-4" style={{ color: "var(--color-text-muted)" }}>No funnel data available.</p>
        )}
      </div>

      {/* Revenue & Entity Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="rounded-xl overflow-hidden" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <div className="px-5 py-4" style={{ borderBottom: "1px solid var(--color-border)" }}>
            <h3 className="text-sm font-semibold">Revenue by Month</h3>
          </div>
          {Array.isArray(monthlyRevenue) && monthlyRevenue.length > 0 ? (
            <table className="w-full text-sm">
              <thead>
                <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                  <th className="text-left px-5 py-2.5 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Month</th>
                  <th className="text-right px-5 py-2.5 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Amount</th>
                  <th className="text-right px-5 py-2.5 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Count</th>
                </tr>
              </thead>
              <tbody>
                {monthlyRevenue.map((row: any, idx: number) => (
                  <tr key={idx} className="transition-colors">
                    <td className="px-5 py-2.5" style={{ color: "var(--color-text-primary)" }}>{row.month || row.period}</td>
                    <td className="px-5 py-2.5 text-right font-medium" style={{ color: "var(--color-text-primary)" }}>₹{(row.amount || row.revenue || 0).toLocaleString()}</td>
                    <td className="px-5 py-2.5 text-right" style={{ color: "var(--color-text-secondary)" }}>{row.count || row.transactions || "--"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-8 text-center text-sm" style={{ color: "var(--color-text-muted)" }}>No revenue data available.</div>
          )}
        </div>

        <div className="rounded-xl p-5" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <h3 className="text-sm font-semibold mb-4">Entity Type Distribution</h3>
          {entityEntries.length > 0 ? (
            <div className="space-y-3">
              {entityEntries.map(([type, count]) => {
                const percentage = Math.round(((count as number) / maxEntityCount) * 100);
                const colorMap: Record<string, string> = {
                  private_limited: "bg-purple-500",
                  opc: "bg-blue-500",
                  llp: "bg-emerald-500",
                  section_8: "bg-amber-500",
                };
                const barColor = colorMap[type] || "bg-gray-500";

                return (
                  <div key={type}>
                    <div className="flex justify-between mb-1">
                      <span className="text-xs font-medium" style={{ color: "var(--color-text-primary)" }}>{type.replace(/_/g, " ").toUpperCase()}</span>
                      <span className="text-xs" style={{ color: "var(--color-text-secondary)" }}>{count as number}</span>
                    </div>
                    <div className="h-3 rounded-full overflow-hidden" style={{ background: "var(--color-bg-secondary)" }}>
                      <div
                        className={`h-full ${barColor} rounded-full transition-all duration-500`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-sm text-center py-4" style={{ color: "var(--color-text-muted)" }}>No entity data available.</p>
          )}
        </div>
      </div>

      {/* State Distribution & SLA */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-xl overflow-hidden" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <div className="px-5 py-4" style={{ borderBottom: "1px solid var(--color-border)" }}>
            <h3 className="text-sm font-semibold">State-wise Distribution</h3>
          </div>
          {stateEntries.length > 0 ? (
            <div className="max-h-[400px] overflow-y-auto" style={{ scrollbarWidth: "thin" }}>
              <table className="w-full text-sm">
                <thead className="sticky top-0" style={{ background: "var(--color-bg-card)" }}>
                  <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                    <th className="text-left px-5 py-2.5 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>State</th>
                    <th className="text-right px-5 py-2.5 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Companies</th>
                    <th className="text-right px-5 py-2.5 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Share</th>
                  </tr>
                </thead>
                <tbody>
                  {stateEntries.map(([state, count]) => {
                    const total = stateEntries.reduce((sum, [, c]) => sum + (c as number), 0);
                    const share = total > 0 ? Math.round(((count as number) / total) * 100) : 0;
                    return (
                      <tr key={state} className="transition-colors">
                        <td className="px-5 py-2.5" style={{ color: "var(--color-text-primary)" }}>{state.toUpperCase()}</td>
                        <td className="px-5 py-2.5 text-right font-medium" style={{ color: "var(--color-text-primary)" }}>{count as number}</td>
                        <td className="px-5 py-2.5 text-right" style={{ color: "var(--color-text-secondary)" }}>{share}%</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center text-sm" style={{ color: "var(--color-text-muted)" }}>No state data available.</div>
          )}
        </div>

        <div className="rounded-xl overflow-hidden" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <div className="px-5 py-4" style={{ borderBottom: "1px solid var(--color-border)" }}>
            <h3 className="text-sm font-semibold flex items-center gap-2">
              <svg className="w-4 h-4" style={{ color: "var(--color-warning)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              SLA Tracking
            </h3>
          </div>
          <div className="p-5">
            {slaOverview ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-lg" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-secondary)" }}>
                  <span className="text-sm" style={{ color: "var(--color-text-secondary)" }}>Compliance Rate</span>
                  <span className="text-2xl font-bold" style={{
                    color: slaOverview.on_time_percentage >= 90 ? "var(--color-success)" :
                      slaOverview.on_time_percentage >= 70 ? "var(--color-warning)" : "var(--color-error)"
                  }}>
                    {slaOverview.on_time_percentage}%
                  </span>
                </div>
                {slaOverview.avg_processing_hours != null && (
                  <div className="flex items-center justify-between p-4 rounded-lg" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-secondary)" }}>
                    <span className="text-sm" style={{ color: "var(--color-text-secondary)" }}>Avg Processing Time</span>
                    <span className="text-lg font-bold" style={{ color: "var(--color-text-primary)" }}>{slaOverview.avg_processing_hours} days</span>
                  </div>
                )}
                {slaBreaches.length > 0 && (
                  <div className="flex items-center justify-between p-4 rounded-lg" style={{ border: "1px solid rgba(239, 68, 68, 0.2)", background: "rgba(239, 68, 68, 0.05)" }}>
                    <span className="text-sm" style={{ color: "var(--color-text-secondary)" }}>Active Breaches</span>
                    <span className="text-lg font-bold" style={{ color: "var(--color-error)" }}>{slaBreaches.length}</span>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-center py-4" style={{ color: "var(--color-text-muted)" }}>No SLA data available.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
