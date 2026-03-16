"use client";

import { useEffect, useState } from "react";
import { calculateNAV, calculateDCF, createValuation, listValuations } from "@/lib/api";

type Method = "nav" | "dcf";

export default function ValuationsPage() {
  const [companyId, setCompanyId] = useState<number | null>(null);
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
    // Get company ID from localStorage
    const stored = localStorage.getItem("selected_company_id");
    if (stored) {
      const id = parseInt(stored);
      setCompanyId(id);
      loadHistory(id);
    }
  }, []);

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

  if (!companyId) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Valuations</h1>
        <p className="text-gray-500">Please select a company from the dashboard first.</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">FMV / Valuation Calculator</h1>
      <p className="text-gray-600 mb-6">
        Rule 11UA-compliant fair market value for ESOP exercise pricing.
      </p>

      {/* Method tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-6">
          {(["nav", "dcf"] as Method[]).map((m) => (
            <button
              key={m}
              onClick={() => { setMethod(m); setResult(null); }}
              className={`pb-3 text-sm font-medium border-b-2 transition-colors uppercase ${
                method === m
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {m === "nav" ? "Net Asset Value" : "Discounted Cash Flow"}
            </button>
          ))}
        </nav>
      </div>

      {/* Input forms */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        {method === "nav" ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Total Assets (Rs)</label>
              <input
                type="number"
                value={totalAssets}
                onChange={(e) => setTotalAssets(e.target.value)}
                placeholder="e.g. 50,00,000"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Total Liabilities (Rs)</label>
              <input
                type="number"
                value={totalLiabilities}
                onChange={(e) => setTotalLiabilities(e.target.value)}
                placeholder="e.g. 10,00,000"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Current Annual Revenue (Rs)</label>
              <input
                type="number"
                value={currentRevenue}
                onChange={(e) => setCurrentRevenue(e.target.value)}
                placeholder="e.g. 1,00,00,000"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Growth Rate (%)</label>
              <input
                type="number"
                value={growthRate}
                onChange={(e) => setGrowthRate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Profit Margin (%)</label>
              <input
                type="number"
                value={profitMargin}
                onChange={(e) => setProfitMargin(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Discount Rate (%)</label>
              <input
                type="number"
                value={discountRate}
                onChange={(e) => setDiscountRate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        )}

        <button
          onClick={handleCalculate}
          disabled={loading}
          className="mt-4 bg-blue-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {loading ? "Calculating..." : "Calculate FMV"}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-6 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Valuation Result</h2>
            <button
              onClick={handleSave}
              disabled={saving}
              className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 transition-colors"
            >
              {saving ? "Saving..." : "Save as Finalized"}
            </button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="text-sm text-blue-600 font-medium">FMV per Share</p>
              <p className="text-2xl font-bold text-blue-900 mt-1">
                Rs {result.fair_market_value?.toLocaleString()}
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 font-medium">Enterprise Value</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                Rs {result.total_enterprise_value?.toLocaleString()}
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 font-medium">Method</p>
              <p className="text-2xl font-bold text-gray-900 mt-1 uppercase">{result.method}</p>
            </div>
          </div>

          {/* DCF projections table */}
          {result.projections && (
            <div className="mt-4 overflow-hidden rounded-lg border border-gray-200">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left px-4 py-2 font-medium text-gray-600">Year</th>
                    <th className="text-right px-4 py-2 font-medium text-gray-600">Revenue</th>
                    <th className="text-right px-4 py-2 font-medium text-gray-600">Cash Flow</th>
                    <th className="text-right px-4 py-2 font-medium text-gray-600">Present Value</th>
                  </tr>
                </thead>
                <tbody>
                  {result.projections.map((p: any) => (
                    <tr key={p.year} className="border-b border-gray-100">
                      <td className="px-4 py-2">{p.year}</td>
                      <td className="px-4 py-2 text-right">Rs {p.revenue?.toLocaleString()}</td>
                      <td className="px-4 py-2 text-right">Rs {p.cash_flow?.toLocaleString()}</td>
                      <td className="px-4 py-2 text-right">Rs {p.present_value?.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* History */}
      {history.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Valuation History</h2>
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Date</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Method</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-600">FMV/Share</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-600">Enterprise Value</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
                </tr>
              </thead>
              <tbody>
                {history.map((v: any) => (
                  <tr key={v.id} className="border-b border-gray-100">
                    <td className="px-4 py-3">{v.valuation_date?.split("T")[0]}</td>
                    <td className="px-4 py-3 uppercase">{v.method}</td>
                    <td className="px-4 py-3 text-right">Rs {v.fair_market_value?.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right">Rs {v.total_enterprise_value?.toLocaleString()}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        v.status === "finalized"
                          ? "bg-green-100 text-green-700"
                          : "bg-gray-100 text-gray-600"
                      }`}>
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
    </div>
  );
}
