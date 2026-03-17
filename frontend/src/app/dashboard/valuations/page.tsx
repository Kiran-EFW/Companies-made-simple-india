"use client";

import { useEffect, useState } from "react";
import { calculateNAV, calculateDCF, createValuation, listValuations } from "@/lib/api";
import { useCompany } from "@/lib/company-context";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  Legend,
} from "recharts";

type Method = "nav" | "dcf";

export default function ValuationsPage() {
  const { selectedCompany } = useCompany();
  const companyId = selectedCompany?.id ?? null;

  const [method, setMethod] = useState<Method>("nav");
  const [result, setResult] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // NAV inputs
  const [totalAssets, setTotalAssets] = useState("");
  const [totalLiabilities, setTotalLiabilities] = useState("");

  // DCF inputs
  const [currentRevenue, setCurrentRevenue] = useState("");
  const [growthRate, setGrowthRate] = useState("20");
  const [profitMargin, setProfitMargin] = useState("15");
  const [discountRate, setDiscountRate] = useState("15");

  useEffect(() => {
    if (companyId) {
      loadHistory(companyId);
    }
  }, [companyId]);

  const loadHistory = async (cid: number) => {
    try {
      const data = await listValuations(cid);
      setHistory(Array.isArray(data) ? data : []);
    } catch {
      // ignore
    }
  };

  const handleCalculate = async () => {
    if (!companyId) return;
    setError(null);
    setLoading(true);
    try {
      let data;
      if (method === "nav") {
        data = await calculateNAV(companyId, {
          total_assets: parseFloat(totalAssets) || 0,
          total_liabilities: parseFloat(totalLiabilities) || 0,
        });
      } else {
        data = await calculateDCF(companyId, {
          current_revenue: parseFloat(currentRevenue) || 0,
          growth_rate: parseFloat(growthRate) || 20,
          profit_margin: parseFloat(profitMargin) || 15,
          discount_rate: parseFloat(discountRate) || 15,
        });
      }
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Calculation failed");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!companyId || !result) return;
    setSaving(true);
    try {
      const payload: any = { method, status: "finalized" };
      if (method === "nav") {
        payload.total_assets = parseFloat(totalAssets) || 0;
        payload.total_liabilities = parseFloat(totalLiabilities) || 0;
      } else {
        payload.current_revenue = parseFloat(currentRevenue) || 0;
        payload.growth_rate = parseFloat(growthRate) || 20;
        payload.profit_margin = parseFloat(profitMargin) || 15;
        payload.discount_rate = parseFloat(discountRate) || 15;
      }
      await createValuation(companyId, payload);
      await loadHistory(companyId);
      setResult(null);
    } catch (err: any) {
      setError(err.message || "Failed to save valuation");
    } finally {
      setSaving(false);
    }
  };

  function formatCurrency(val: number): string {
    if (val >= 10000000) return `Rs ${(val / 10000000).toFixed(2)} Cr`;
    if (val >= 100000) return `Rs ${(val / 100000).toFixed(2)} L`;
    return `Rs ${val.toLocaleString()}`;
  }

  if (!companyId) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="text-center mb-8">
          <div className="badge badge-purple mb-4 mx-auto w-fit">Valuation Engine</div>
          <h1
            className="text-3xl md:text-4xl font-bold mb-3"
            style={{ fontFamily: "var(--font-display)" }}
          >
            <span className="gradient-text">Valuations</span>
          </h1>
          <p className="text-base" style={{ color: "var(--color-text-secondary)" }}>
            Please select a company from the dashboard first.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="badge badge-purple mb-4 mx-auto w-fit">Valuation Engine</div>
          <h1
            className="text-3xl md:text-4xl font-bold mb-3"
            style={{ fontFamily: "var(--font-display)" }}
          >
            <span className="gradient-text">FMV / Valuation Calculator</span>
          </h1>
          <p className="text-base" style={{ color: "var(--color-text-secondary)" }}>
            Rule 11UA-compliant fair market value for ESOP exercise pricing.
          </p>
        </div>

        {/* Method tabs */}
        <div className="flex gap-2 mb-8 justify-center">
          {(["nav", "dcf"] as Method[]).map((m) => (
            <button
              key={m}
              onClick={() => { setMethod(m); setResult(null); }}
              className="glass-card px-4 py-2 text-sm font-medium transition-all uppercase"
              style={{
                borderColor: method === m ? "var(--color-accent-purple-light)" : "var(--color-border)",
                background: method === m ? "var(--color-purple-bg)" : "transparent",
              }}
            >
              {m === "nav" ? "Net Asset Value" : "Discounted Cash Flow"}
            </button>
          ))}
        </div>

        {/* Input forms */}
        <div className="glass-card p-6 mb-6" style={{ cursor: "default" }}>
          {method === "nav" ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                  Total Assets (Rs)
                </label>
                <input
                  type="number"
                  value={totalAssets}
                  onChange={(e) => setTotalAssets(e.target.value)}
                  placeholder="e.g. 50,00,000"
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{
                    background: "var(--color-bg-card)",
                    border: "1px solid var(--color-border)",
                    color: "var(--color-text-primary)",
                  }}
                />
              </div>
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                  Total Liabilities (Rs)
                </label>
                <input
                  type="number"
                  value={totalLiabilities}
                  onChange={(e) => setTotalLiabilities(e.target.value)}
                  placeholder="e.g. 10,00,000"
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{
                    background: "var(--color-bg-card)",
                    border: "1px solid var(--color-border)",
                    color: "var(--color-text-primary)",
                  }}
                />
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                  Current Annual Revenue (Rs)
                </label>
                <input
                  type="number"
                  value={currentRevenue}
                  onChange={(e) => setCurrentRevenue(e.target.value)}
                  placeholder="e.g. 1,00,00,000"
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{
                    background: "var(--color-bg-card)",
                    border: "1px solid var(--color-border)",
                    color: "var(--color-text-primary)",
                  }}
                />
              </div>
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                  Growth Rate (%)
                </label>
                <input
                  type="number"
                  value={growthRate}
                  onChange={(e) => setGrowthRate(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{
                    background: "var(--color-bg-card)",
                    border: "1px solid var(--color-border)",
                    color: "var(--color-text-primary)",
                  }}
                />
              </div>
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                  Profit Margin (%)
                </label>
                <input
                  type="number"
                  value={profitMargin}
                  onChange={(e) => setProfitMargin(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{
                    background: "var(--color-bg-card)",
                    border: "1px solid var(--color-border)",
                    color: "var(--color-text-primary)",
                  }}
                />
              </div>
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                  Discount Rate (%)
                </label>
                <input
                  type="number"
                  value={discountRate}
                  onChange={(e) => setDiscountRate(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{
                    background: "var(--color-bg-card)",
                    border: "1px solid var(--color-border)",
                    color: "var(--color-text-primary)",
                  }}
                />
              </div>
            </div>
          )}

          <button
            onClick={handleCalculate}
            disabled={loading}
            className="btn-primary mt-4"
          >
            {loading ? "Calculating..." : "Calculate FMV"}
          </button>
        </div>

        {/* Error */}
        {error && (
          <div
            className="glass-card p-3 mb-6 text-sm text-center"
            style={{
              borderColor: "var(--color-accent-rose)",
              color: "var(--color-accent-rose)",
              cursor: "default",
            }}
          >
            {error}
          </div>
        )}

        {/* Result */}
        {result && (
          <div className="glass-card p-6 mb-6" style={{ cursor: "default" }}>
            <div className="flex items-center justify-between mb-4">
              <h2
                className="text-lg font-semibold"
                style={{ color: "var(--color-text-primary)" }}
              >
                Valuation Result
              </h2>
              <button
                onClick={handleSave}
                disabled={saving}
                className="text-sm px-4 py-2 rounded-lg font-medium transition-all"
                style={{
                  background: "var(--color-success-light)",
                  color: "var(--color-accent-emerald)",
                  border: "1px solid var(--color-accent-emerald-light)",
                }}
              >
                {saving ? "Saving..." : "Save as Finalized"}
              </button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="glass-card p-4 text-center" style={{ cursor: "default" }}>
                <p className="text-sm font-medium" style={{ color: "var(--color-accent-purple)" }}>
                  FMV per Share
                </p>
                <p className="text-2xl font-bold mt-1" style={{ color: "var(--color-text-primary)" }}>
                  Rs {result.fair_market_value?.toLocaleString()}
                </p>
              </div>
              <div className="glass-card p-4 text-center" style={{ cursor: "default" }}>
                <p className="text-sm font-medium" style={{ color: "var(--color-text-secondary)" }}>
                  Enterprise Value
                </p>
                <p className="text-2xl font-bold mt-1" style={{ color: "var(--color-text-primary)" }}>
                  Rs {result.total_enterprise_value?.toLocaleString()}
                </p>
              </div>
              <div className="glass-card p-4 text-center" style={{ cursor: "default" }}>
                <p className="text-sm font-medium" style={{ color: "var(--color-text-secondary)" }}>
                  Method
                </p>
                <p className="text-2xl font-bold mt-1 uppercase" style={{ color: "var(--color-text-primary)" }}>
                  {result.method}
                </p>
              </div>
            </div>

            {/* DCF Projections Area Chart */}
            {result.projections && result.projections.length >= 2 && (
              <div className="mt-4 glass-card p-6" style={{ cursor: "default" }}>
                <h3
                  className="text-sm font-semibold mb-4"
                  style={{ color: "var(--color-text-secondary)" }}
                >
                  Revenue vs Present Value Projections
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart
                    data={result.projections}
                    margin={{ top: 5, right: 20, bottom: 5, left: 10 }}
                  >
                    <defs>
                      <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="colorPV" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis
                      dataKey="year"
                      tick={{ fill: "#9CA3AF", fontSize: 12 }}
                      axisLine={{ stroke: "#374151" }}
                      tickLine={{ stroke: "#374151" }}
                    />
                    <YAxis
                      tick={{ fill: "#9CA3AF", fontSize: 12 }}
                      axisLine={{ stroke: "#374151" }}
                      tickLine={{ stroke: "#374151" }}
                      tickFormatter={(val: number) => formatCurrency(val)}
                    />
                    <Tooltip
                      contentStyle={{
                        background: "#1a1a2e",
                        border: "1px solid rgba(255,255,255,0.1)",
                        borderRadius: 8,
                      }}
                      labelStyle={{ color: "#9CA3AF" }}
                      formatter={(value: any, name: any) => [
                        formatCurrency(Number(value)),
                        name === "revenue" ? "Revenue" : "Present Value",
                      ]}
                    />
                    <Legend
                      wrapperStyle={{ color: "#9CA3AF", fontSize: 12 }}
                      formatter={(value: string) =>
                        value === "revenue" ? "Revenue" : "Present Value"
                      }
                    />
                    <Area
                      type="monotone"
                      dataKey="revenue"
                      stroke="#8B5CF6"
                      strokeWidth={2}
                      fill="url(#colorRevenue)"
                    />
                    <Area
                      type="monotone"
                      dataKey="present_value"
                      stroke="#10B981"
                      strokeWidth={2}
                      fill="url(#colorPV)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* DCF projections table */}
            {result.projections && (
              <div className="mt-4 glass-card overflow-hidden" style={{ cursor: "default" }}>
                <table className="w-full text-sm">
                  <thead>
                    <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                      <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Year</th>
                      <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Revenue</th>
                      <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Cash Flow</th>
                      <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Present Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.projections.map((p: any) => (
                      <tr key={p.year} style={{ borderBottom: "1px solid var(--color-border)" }}>
                        <td className="p-3" style={{ color: "var(--color-text-primary)" }}>{p.year}</td>
                        <td className="p-3 text-right font-mono" style={{ color: "var(--color-text-primary)" }}>
                          Rs {p.revenue?.toLocaleString()}
                        </td>
                        <td className="p-3 text-right font-mono" style={{ color: "var(--color-text-primary)" }}>
                          Rs {p.cash_flow?.toLocaleString()}
                        </td>
                        <td className="p-3 text-right font-mono" style={{ color: "var(--color-text-primary)" }}>
                          Rs {p.present_value?.toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* FMV Trend Line Chart */}
        {history.length >= 2 && (
          <div className="glass-card p-6 mb-6" style={{ cursor: "default" }}>
            <h3
              className="text-sm font-semibold mb-4"
              style={{ color: "var(--color-text-secondary)" }}
            >
              FMV per Share Trend
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart
                data={[...history]
                  .sort(
                    (a, b) =>
                      new Date(a.valuation_date).getTime() -
                      new Date(b.valuation_date).getTime()
                  )
                  .map((v) => ({
                    date: v.valuation_date?.split("T")[0],
                    fmv: v.fair_market_value,
                    tev: v.total_enterprise_value,
                    method: v.method,
                  }))}
                margin={{ top: 5, right: 20, bottom: 5, left: 10 }}
              >
                <defs>
                  <linearGradient id="colorFmv" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="date"
                  tick={{ fill: "#9CA3AF", fontSize: 12 }}
                  axisLine={{ stroke: "#374151" }}
                  tickLine={{ stroke: "#374151" }}
                />
                <YAxis
                  tick={{ fill: "#9CA3AF", fontSize: 12 }}
                  axisLine={{ stroke: "#374151" }}
                  tickLine={{ stroke: "#374151" }}
                  tickFormatter={(val: number) => formatCurrency(val)}
                />
                <Tooltip
                  contentStyle={{
                    background: "#1a1a2e",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: 8,
                  }}
                  labelStyle={{ color: "#9CA3AF" }}
                  formatter={(value: any) => [formatCurrency(Number(value)), "FMV per Share"]}
                />
                <Line
                  type="monotone"
                  dataKey="fmv"
                  stroke="#8B5CF6"
                  strokeWidth={2}
                  dot={{ fill: "#8B5CF6", r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* History */}
        {history.length > 0 && (
          <div>
            <h2
              className="text-lg font-semibold mb-3"
              style={{ color: "var(--color-text-primary)" }}
            >
              Valuation History
            </h2>
            <div className="glass-card overflow-hidden" style={{ cursor: "default" }}>
              <table className="w-full text-sm">
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                    <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Date</th>
                    <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Method</th>
                    <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>FMV/Share</th>
                    <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Enterprise Value</th>
                    <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((v: any) => (
                    <tr key={v.id} style={{ borderBottom: "1px solid var(--color-border)" }}>
                      <td className="p-3" style={{ color: "var(--color-text-primary)" }}>
                        {v.valuation_date?.split("T")[0]}
                      </td>
                      <td className="p-3 uppercase" style={{ color: "var(--color-text-primary)" }}>
                        {v.method}
                      </td>
                      <td className="p-3 text-right font-mono" style={{ color: "var(--color-text-primary)" }}>
                        Rs {v.fair_market_value?.toLocaleString()}
                      </td>
                      <td className="p-3 text-right font-mono" style={{ color: "var(--color-text-primary)" }}>
                        Rs {v.total_enterprise_value?.toLocaleString()}
                      </td>
                      <td className="p-3">
                        <span
                          className="text-xs px-2 py-0.5 rounded-full"
                          style={{
                            background: v.status === "finalized"
                              ? "var(--color-success-light)"
                              : "var(--color-overlay)",
                            color: v.status === "finalized"
                              ? "var(--color-accent-emerald)"
                              : "var(--color-text-secondary)",
                          }}
                        >
                          {v.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Empty state when no history and no result */}
        {history.length === 0 && !result && !loading && (
          <div className="text-center py-16">
            <h3
              className="text-lg font-semibold mb-2"
              style={{ color: "var(--color-text-primary)" }}
            >
              No Valuations Yet
            </h3>
            <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
              Use the calculator above to generate your first Rule 11UA-compliant valuation.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
