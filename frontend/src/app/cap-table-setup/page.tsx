"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { quickCapTableSetup } from "@/lib/api";

interface ShareholderRow {
  name: string;
  shares: number;
  email: string;
  is_promoter: boolean;
}

export default function CapTableSetupPage() {
  const router = useRouter();
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [companyName, setCompanyName] = useState("");
  const [shareholders, setShareholders] = useState<ShareholderRow[]>([
    { name: "", shares: 0, email: "", is_promoter: true },
    { name: "", shares: 0, email: "", is_promoter: false },
  ]);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const totalShares = shareholders.reduce((sum, s) => sum + (s.shares || 0), 0);

  const updateShareholder = (index: number, field: keyof ShareholderRow, value: any) => {
    const updated = [...shareholders];
    (updated[index] as any)[field] = value;
    setShareholders(updated);
  };

  const addRow = () => {
    setShareholders([...shareholders, { name: "", shares: 0, email: "", is_promoter: false }]);
  };

  const removeRow = (index: number) => {
    if (shareholders.length <= 1) return;
    setShareholders(shareholders.filter((_, i) => i !== index));
  };

  const handleGenerate = async () => {
    setError(null);
    setLoading(true);
    try {
      const data = await quickCapTableSetup({
        company_name: companyName,
        shareholders: shareholders
          .filter((s) => s.name && s.shares > 0)
          .map((s) => ({
            name: s.name,
            shares: s.shares,
            email: s.email || undefined,
            is_promoter: s.is_promoter,
          })),
      });
      setResult(data);
      setStep(3);
    } catch (err: any) {
      setError(err.message || "Failed to create cap table");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">A</span>
          </div>
          <span className="text-xl font-semibold text-gray-900">Anvils</span>
          <span className="text-sm text-gray-500 ml-2">Free Cap Table</span>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-10">
        {step === 1 && (
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Create your cap table in 60 seconds
            </h1>
            <p className="text-gray-600 mb-8">
              Enter your company name to get started. No payment required.
            </p>
            <div className="bg-white rounded-lg border border-gray-200 p-6 max-w-md">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Company Name
              </label>
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="e.g. Acme Technologies Pvt Ltd"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={() => companyName.trim() && setStep(2)}
                disabled={!companyName.trim()}
                className="mt-4 w-full bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Next: Add Shareholders
              </button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Add shareholders for {companyName}
            </h1>
            <p className="text-gray-600 mb-6">
              Enter each shareholder and their number of shares. Percentages are calculated automatically.
            </p>

            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden mb-4">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Name</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Shares</th>
                    <th className="text-right px-4 py-3 font-medium text-gray-600">%</th>
                    <th className="text-center px-4 py-3 font-medium text-gray-600">Promoter</th>
                    <th className="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody>
                  {shareholders.map((sh, i) => (
                    <tr key={i} className="border-b border-gray-100">
                      <td className="px-4 py-2">
                        <input
                          type="text"
                          value={sh.name}
                          onChange={(e) => updateShareholder(i, "name", e.target.value)}
                          placeholder="Shareholder name"
                          className="w-full px-2 py-1.5 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                        />
                      </td>
                      <td className="px-4 py-2">
                        <input
                          type="number"
                          value={sh.shares || ""}
                          onChange={(e) => updateShareholder(i, "shares", parseInt(e.target.value) || 0)}
                          placeholder="10000"
                          className="w-24 px-2 py-1.5 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                        />
                      </td>
                      <td className="px-4 py-2 text-right font-medium text-gray-700">
                        {totalShares > 0 ? ((sh.shares / totalShares) * 100).toFixed(2) : "0.00"}%
                      </td>
                      <td className="px-4 py-2 text-center">
                        <input
                          type="checkbox"
                          checked={sh.is_promoter}
                          onChange={(e) => updateShareholder(i, "is_promoter", e.target.checked)}
                          className="w-4 h-4 text-blue-600"
                        />
                      </td>
                      <td className="px-4 py-2">
                        <button
                          onClick={() => removeRow(i)}
                          className="text-red-500 hover:text-red-700 text-xs"
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="flex items-center justify-between mb-6">
              <button
                onClick={addRow}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                + Add Shareholder
              </button>
              <p className="text-sm text-gray-500">
                Total: {totalShares.toLocaleString()} shares
              </p>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4 text-sm text-red-700">
                {error}
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={() => setStep(1)}
                className="px-6 py-2.5 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
              >
                Back
              </button>
              <button
                onClick={handleGenerate}
                disabled={loading || shareholders.filter((s) => s.name && s.shares > 0).length === 0}
                className="flex-1 bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? "Generating..." : "Generate Cap Table"}
              </button>
            </div>
          </div>
        )}

        {step === 3 && result && (
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Cap Table for {result.company_name}
            </h1>
            <p className="text-gray-600 mb-6">
              Your cap table is ready. Explore what else you can do with Anvils.
            </p>

            {/* Cap table visualization */}
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden mb-8">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Shareholder</th>
                    <th className="text-right px-4 py-3 font-medium text-gray-600">Shares</th>
                    <th className="text-right px-4 py-3 font-medium text-gray-600">Ownership</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Type</th>
                  </tr>
                </thead>
                <tbody>
                  {result.cap_table?.shareholders?.map((sh: any, i: number) => (
                    <tr key={i} className="border-b border-gray-100">
                      <td className="px-4 py-3">
                        {sh.name}
                        {sh.is_promoter && (
                          <span className="ml-2 text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">
                            Promoter
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right">{sh.shares?.toLocaleString()}</td>
                      <td className="px-4 py-3 text-right">{sh.percentage?.toFixed(2)}%</td>
                      <td className="px-4 py-3 capitalize">{sh.share_type || "equity"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Upsell cards */}
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Continue building with Anvils
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={() => router.push("/dashboard/esop")}
                className="bg-white rounded-lg border border-gray-200 p-5 text-left hover:border-blue-400 hover:shadow-sm transition-all"
              >
                <h3 className="font-semibold text-gray-900">Add ESOP Pool</h3>
                <p className="text-sm text-gray-500 mt-1">
                  Create an employee stock option plan and issue grants.
                </p>
              </button>
              <button
                onClick={() => router.push("/dashboard/fundraising")}
                className="bg-white rounded-lg border border-gray-200 p-5 text-left hover:border-blue-400 hover:shadow-sm transition-all"
              >
                <h3 className="font-semibold text-gray-900">Model a Fundraise</h3>
                <p className="text-sm text-gray-500 mt-1">
                  Simulate funding rounds and see dilution impact.
                </p>
              </button>
              <button
                onClick={() => router.push("/dashboard")}
                className="bg-white rounded-lg border border-gray-200 p-5 text-left hover:border-blue-400 hover:shadow-sm transition-all"
              >
                <h3 className="font-semibold text-gray-900">Full Dashboard</h3>
                <p className="text-sm text-gray-500 mt-1">
                  Compliance, data room, e-signatures, and more.
                </p>
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
