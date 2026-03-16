"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { apiCall, simulateRound, simulateExit, simulateExitWaterfall, getShareCertificate } from "@/lib/api";
import Footer from "@/components/footer";

interface ShareholderData {
  id: number;
  name: string;
  email: string | null;
  pan_number: string | null;
  shares: number;
  share_type: string;
  face_value: number;
  paid_up_value: number;
  percentage: number;
  date_of_allotment: string | null;
  is_promoter: boolean;
}

interface ESOPPoolData {
  total_pool_size: number;
  allocated: number;
  available: number;
  active_plans: number;
  total_grants: number;
}

interface CapTableData {
  company_id: number;
  total_shares: number;
  total_shareholders: number;
  shareholders: ShareholderData[];
  esop_pool: ESOPPoolData | null;
  summary: {
    equity_shares: number;
    preference_shares: number;
    promoter_shares: number;
    promoter_percentage: number;
  };
}

interface TransactionData {
  id: number;
  type: string;
  from_shareholder: string | null;
  to_shareholder: string | null;
  shares: number;
  price_per_share: number;
  total_amount: number;
  form_reference: string | null;
  date: string | null;
}

// CSS-based pie chart colors
const PIE_COLORS = [
  "rgb(139, 92, 246)",   // purple
  "rgb(59, 130, 246)",   // blue
  "rgb(16, 185, 129)",   // emerald
  "rgb(245, 158, 11)",   // amber
  "rgb(244, 63, 94)",    // rose
  "rgb(99, 102, 241)",   // indigo
  "rgb(236, 72, 153)",   // pink
  "rgb(34, 211, 238)",   // cyan
  "rgb(251, 146, 60)",   // orange
  "rgb(163, 230, 53)",   // lime
];

function PieChart({ shareholders }: { shareholders: ShareholderData[] }) {
  if (shareholders.length === 0) return null;

  // Build conic-gradient
  let gradientParts: string[] = [];
  let cumulative = 0;

  shareholders.forEach((sh, idx) => {
    const color = PIE_COLORS[idx % PIE_COLORS.length];
    const start = cumulative;
    const end = cumulative + sh.percentage;
    gradientParts.push(`${color} ${start}% ${end}%`);
    cumulative = end;
  });

  // Fill remaining if percentages don't sum to 100
  if (cumulative < 100) {
    gradientParts.push(`rgba(255,255,255,0.1) ${cumulative}% 100%`);
  }

  const gradient = `conic-gradient(${gradientParts.join(", ")})`;

  return (
    <div className="flex flex-col items-center gap-4">
      <div
        style={{
          width: "200px",
          height: "200px",
          borderRadius: "50%",
          background: gradient,
          boxShadow: "0 0 30px rgba(139, 92, 246, 0.2)",
        }}
      />
      <div className="flex flex-wrap gap-3 justify-center max-w-md">
        {shareholders.map((sh, idx) => (
          <div key={sh.id} className="flex items-center gap-2 text-xs">
            <span
              className="inline-block w-3 h-3 rounded-sm"
              style={{ background: PIE_COLORS[idx % PIE_COLORS.length] }}
            />
            <span style={{ color: "var(--color-text-secondary)" }}>
              {sh.name} ({sh.percentage}%)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function CapTablePage() {
  const [companyId, setCompanyId] = useState<number>(1);
  const [capTable, setCapTable] = useState<CapTableData | null>(null);
  const [transactions, setTransactions] = useState<TransactionData[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"overview" | "add" | "transfer" | "history" | "simulator" | "exit" | "waterfall">("overview");

  // Add shareholder form
  const [newName, setNewName] = useState("");
  const [newShares, setNewShares] = useState("");
  const [newShareType, setNewShareType] = useState("equity");
  const [newFaceValue, setNewFaceValue] = useState("10");
  const [newEmail, setNewEmail] = useState("");
  const [newPan, setNewPan] = useState("");
  const [newIsPromoter, setNewIsPromoter] = useState(false);

  // Transfer form
  const [fromId, setFromId] = useState("");
  const [toId, setToId] = useState("");
  const [transferShares, setTransferShares] = useState("");
  const [transferPrice, setTransferPrice] = useState("10");

  const [message, setMessage] = useState("");

  // Round simulator state
  const [simPreMoney, setSimPreMoney] = useState("10000000");
  const [simInvestment, setSimInvestment] = useState("2500000");
  const [simEsopPct, setSimEsopPct] = useState("10");
  const [simRoundName, setSimRoundName] = useState("Seed Round");
  const [simInvestors, setSimInvestors] = useState<{ name: string; amount: string }[]>([
    { name: "Investor 1", amount: "2500000" },
  ]);
  const [simResult, setSimResult] = useState<any>(null);
  const [simLoading, setSimLoading] = useState(false);

  // Exit scenario state
  const [exitValuation, setExitValuation] = useState("50000000");
  const [exitLiqPref, setExitLiqPref] = useState("1");
  const [exitResult, setExitResult] = useState<any>(null);
  const [exitLoading, setExitLoading] = useState(false);

  // Waterfall state
  const [wfValuation, setWfValuation] = useState("50000000");
  const [wfParticipating, setWfParticipating] = useState(false);
  const [wfLiqPrefs, setWfLiqPrefs] = useState<{ shareholder_id: string; multiple: string; invested_amount: string }[]>([]);
  const [wfResult, setWfResult] = useState<any>(null);
  const [wfLoading, setWfLoading] = useState(false);

  // Certificate state
  const [certLoading, setCertLoading] = useState<number | null>(null);

  useEffect(() => {
    fetchCapTable();
    fetchTransactions();
  }, [companyId]);

  async function fetchCapTable() {
    setLoading(true);
    try {
      const data = await apiCall(`/companies/${companyId}/cap-table`);
      setCapTable(data);
    } catch {
      // Backend may not be running
    }
    setLoading(false);
  }

  async function fetchTransactions() {
    try {
      const data = await apiCall(`/companies/${companyId}/cap-table/transactions`);
      setTransactions(data);
    } catch {
      // Silently fail
    }
  }

  async function handleAddShareholder(e: React.FormEvent) {
    e.preventDefault();
    setMessage("");
    try {
      await apiCall(`/companies/${companyId}/cap-table/shareholders`, {
        method: "POST",
        body: JSON.stringify({
          name: newName,
          shares: parseInt(newShares),
          share_type: newShareType,
          face_value: parseFloat(newFaceValue),
          paid_up_value: parseFloat(newFaceValue),
          email: newEmail || null,
          pan_number: newPan || null,
          is_promoter: newIsPromoter,
        }),
      });
      setMessage("Shareholder added successfully!");
      setNewName("");
      setNewShares("");
      setNewEmail("");
      setNewPan("");
      setNewIsPromoter(false);
      fetchCapTable();
      fetchTransactions();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleTransfer(e: React.FormEvent) {
    e.preventDefault();
    setMessage("");
    try {
      const result = await apiCall(`/companies/${companyId}/cap-table/transfer`, {
        method: "POST",
        body: JSON.stringify({
          from_shareholder_id: parseInt(fromId),
          to_shareholder_id: parseInt(toId),
          shares: parseInt(transferShares),
          price_per_share: parseFloat(transferPrice),
        }),
      });
      if (result.error) {
        setMessage(`Error: ${result.error}`);
      } else {
        setMessage("Transfer recorded successfully!");
        setFromId("");
        setToId("");
        setTransferShares("");
        fetchCapTable();
        fetchTransactions();
      }
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleSimulateRound() {
    setSimLoading(true);
    setSimResult(null);
    try {
      const totalInvestment = simInvestors.reduce((s, i) => s + (parseFloat(i.amount) || 0), 0);
      const result = await simulateRound(companyId, {
        pre_money_valuation: parseFloat(simPreMoney) || 0,
        investment_amount: totalInvestment,
        esop_pool_pct: parseFloat(simEsopPct) || 0,
        investors: simInvestors.map(i => ({ name: i.name, amount: parseFloat(i.amount) || 0 })),
        round_name: simRoundName,
      });
      setSimResult(result);
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
    setSimLoading(false);
  }

  async function handleSimulateExit() {
    setExitLoading(true);
    setExitResult(null);
    try {
      const result = await simulateExit(companyId, {
        exit_valuation: parseFloat(exitValuation) || 0,
        liquidation_preference: parseFloat(exitLiqPref) || 1,
      });
      setExitResult(result);
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
    setExitLoading(false);
  }

  function addInvestor() {
    setSimInvestors([...simInvestors, { name: `Investor ${simInvestors.length + 1}`, amount: "" }]);
  }

  function removeInvestor(idx: number) {
    setSimInvestors(simInvestors.filter((_, i) => i !== idx));
  }

  function updateInvestor(idx: number, field: "name" | "amount", value: string) {
    const updated = [...simInvestors];
    updated[idx] = { ...updated[idx], [field]: value };
    setSimInvestors(updated);
  }

  async function handleWaterfall() {
    setWfLoading(true);
    setWfResult(null);
    try {
      const lps = wfLiqPrefs
        .filter(lp => lp.shareholder_id && lp.invested_amount)
        .map(lp => ({
          shareholder_id: parseInt(lp.shareholder_id),
          multiple: parseFloat(lp.multiple) || 1,
          invested_amount: parseFloat(lp.invested_amount) || 0,
        }));
      const result = await simulateExitWaterfall(companyId, {
        exit_valuation: parseFloat(wfValuation) || 0,
        liquidation_preferences: lps.length > 0 ? lps : undefined,
        participating_preferred: wfParticipating,
      });
      setWfResult(result);
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
    setWfLoading(false);
  }

  function addLiqPref() {
    setWfLiqPrefs([...wfLiqPrefs, { shareholder_id: "", multiple: "1", invested_amount: "" }]);
  }

  function removeLiqPref(idx: number) {
    setWfLiqPrefs(wfLiqPrefs.filter((_, i) => i !== idx));
  }

  function updateLiqPref(idx: number, field: string, value: string) {
    const updated = [...wfLiqPrefs];
    updated[idx] = { ...updated[idx], [field]: value };
    setWfLiqPrefs(updated);
  }

  async function handleCertificate(shareholderId: number) {
    setCertLoading(shareholderId);
    try {
      const result = await getShareCertificate(companyId, shareholderId);
      if (result.html) {
        const blob = new Blob([result.html], { type: "text/html" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `share-certificate-${result.certificate_number}.html`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
        setMessage("Certificate downloaded!");
      }
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
    setCertLoading(null);
  }

  function formatCurrency(val: number): string {
    if (val >= 10000000) return `Rs ${(val / 10000000).toFixed(2)} Cr`;
    if (val >= 100000) return `Rs ${(val / 100000).toFixed(2)} L`;
    return `Rs ${val.toLocaleString()}`;
  }

  return (
    <div className="glow-bg min-h-screen">
      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-5 max-w-7xl mx-auto">
        <Link href="/" className="flex items-center gap-2.5">
          <img src="/logo-icon.png" alt="Anvils" className="w-6 h-6 object-contain" />
          <span className="text-xl font-bold gradient-text" style={{ fontFamily: "var(--font-display)" }}>Anvils</span>
        </Link>
        <div className="flex gap-3">
          <Link href="/dashboard" className="btn-secondary text-sm !py-2 !px-5">
            Dashboard
          </Link>
          <Link href="/compare" className="btn-secondary text-sm !py-2 !px-5">
            Compare
          </Link>
        </div>
      </nav>

      <div className="relative z-10 max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="badge badge-purple mb-4 mx-auto w-fit">Cap Table Management</div>
          <h1
            className="text-3xl md:text-4xl font-bold mb-3"
            style={{ fontFamily: "var(--font-display)" }}
          >
            <span className="gradient-text">Cap Table</span>
          </h1>
          <p className="text-base" style={{ color: "var(--color-text-secondary)" }}>
            Track shareholding, record transfers, and manage allotments.
          </p>
        </div>

        {/* Company selector */}
        <div className="flex justify-center mb-6">
          <div className="flex items-center gap-3">
            <label className="text-sm" style={{ color: "var(--color-text-muted)" }}>
              Company ID:
            </label>
            <input
              type="number"
              value={companyId}
              onChange={(e) => setCompanyId(parseInt(e.target.value) || 1)}
              className="glass-card px-3 py-1.5 text-sm w-20 text-center"
              style={{
                background: "var(--color-bg-card)",
                border: "1px solid var(--color-border)",
                color: "var(--color-text-primary)",
                cursor: "text",
              }}
              min={1}
            />
          </div>
        </div>

        {/* Message */}
        {message && (
          <div
            className="glass-card p-3 mb-6 text-center text-sm"
            style={{
              borderColor: message.startsWith("Error")
                ? "rgba(244, 63, 94, 0.5)"
                : "rgba(16, 185, 129, 0.5)",
              cursor: "default",
            }}
          >
            {message}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-8 justify-center flex-wrap">
          {(["overview", "add", "transfer", "history", "simulator", "exit", "waterfall"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className="glass-card px-4 py-2 text-sm font-medium transition-all"
              style={{
                borderColor: activeTab === tab ? "rgba(139, 92, 246, 0.6)" : "var(--color-border)",
                background: activeTab === tab ? "rgba(139, 92, 246, 0.15)" : "transparent",
              }}
            >
              {tab === "overview" && "Overview"}
              {tab === "add" && "Add Shareholder"}
              {tab === "transfer" && "Record Transfer"}
              {tab === "history" && "Transaction History"}
              {tab === "simulator" && "Round Simulator"}
              {tab === "exit" && "Exit Scenarios"}
              {tab === "waterfall" && "Waterfall Analysis"}
            </button>
          ))}
        </div>

        {/* Loading */}
        {loading && (
          <div className="text-center py-12" style={{ color: "var(--color-text-muted)" }}>
            Loading cap table...
          </div>
        )}

        {/* Overview Tab */}
        {activeTab === "overview" && capTable && (
          <div>
            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <div className="glass-card p-4 text-center" style={{ cursor: "default" }}>
                <div className="text-2xl font-bold">{capTable.total_shareholders}</div>
                <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                  Shareholders
                </div>
              </div>
              <div className="glass-card p-4 text-center" style={{ cursor: "default" }}>
                <div className="text-2xl font-bold">{capTable.total_shares.toLocaleString()}</div>
                <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                  Total Shares
                </div>
              </div>
              <div className="glass-card p-4 text-center" style={{ cursor: "default" }}>
                <div className="text-2xl font-bold">{capTable.summary.equity_shares.toLocaleString()}</div>
                <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                  Equity Shares
                </div>
              </div>
              <div className="glass-card p-4 text-center" style={{ cursor: "default" }}>
                <div className="text-2xl font-bold">{capTable.summary.promoter_percentage}%</div>
                <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                  Promoter Holding
                </div>
              </div>
            </div>

            {/* ESOP Pool Summary */}
            {capTable.esop_pool && capTable.esop_pool.total_pool_size > 0 && (
              <div className="glass-card p-6 mb-8" style={{ cursor: "default" }}>
                <h3 className="font-semibold mb-4">ESOP Pool</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-xl font-bold">{(capTable.esop_pool.total_pool_size || 0).toLocaleString()}</div>
                    <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Total Pool</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold" style={{ color: "rgb(245, 158, 11)" }}>
                      {(capTable.esop_pool.allocated || 0).toLocaleString()}
                    </div>
                    <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Allocated</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold" style={{ color: "var(--color-accent-emerald)" }}>
                      {(capTable.esop_pool.available || 0).toLocaleString()}
                    </div>
                    <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Available</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold">{capTable.esop_pool.active_plans || 0}</div>
                    <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Active Plans</div>
                  </div>
                </div>
                {/* Pool utilization bar */}
                <div className="mt-4">
                  <div className="flex justify-between text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>
                    <span>Pool Utilization</span>
                    <span>
                      {capTable.esop_pool.total_pool_size > 0
                        ? Math.round((capTable.esop_pool.allocated / capTable.esop_pool.total_pool_size) * 100)
                        : 0}%
                    </span>
                  </div>
                  <div className="w-full h-2 rounded-full" style={{ background: "rgba(255,255,255,0.1)" }}>
                    <div
                      className="h-2 rounded-full transition-all"
                      style={{
                        width: `${capTable.esop_pool.total_pool_size > 0
                          ? (capTable.esop_pool.allocated / capTable.esop_pool.total_pool_size) * 100
                          : 0}%`,
                        background: "linear-gradient(90deg, rgb(139, 92, 246), rgb(59, 130, 246))",
                      }}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Pie Chart */}
            {capTable.shareholders.length > 0 && (
              <div className="glass-card p-8 mb-8" style={{ cursor: "default" }}>
                <h3 className="text-center font-semibold mb-6">Shareholding Pattern</h3>
                <PieChart shareholders={capTable.shareholders} />
              </div>
            )}

            {/* Shareholders Table */}
            <div className="glass-card overflow-hidden" style={{ cursor: "default" }}>
              <div className="p-4" style={{ borderBottom: "1px solid var(--color-border)" }}>
                <h3 className="font-semibold">Shareholders</h3>
              </div>
              {capTable.shareholders.length === 0 ? (
                <div className="p-8 text-center" style={{ color: "var(--color-text-muted)" }}>
                  No shareholders found. Add your first shareholder using the "Add Shareholder" tab.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                        <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Name</th>
                        <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Shares</th>
                        <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Type</th>
                        <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Face Value</th>
                        <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>%</th>
                        <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Date</th>
                        <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Promoter</th>
                        <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {capTable.shareholders.map((sh) => (
                        <tr
                          key={sh.id}
                          style={{ borderBottom: "1px solid var(--color-border)" }}
                        >
                          <td className="p-3 font-medium">
                            {sh.name}
                            {sh.email && (
                              <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                                {sh.email}
                              </div>
                            )}
                          </td>
                          <td className="p-3 text-right font-mono">{sh.shares.toLocaleString()}</td>
                          <td className="p-3 text-center">
                            <span
                              className="text-xs px-2 py-0.5 rounded-full"
                              style={{
                                background: sh.share_type === "equity"
                                  ? "rgba(139, 92, 246, 0.15)"
                                  : "rgba(245, 158, 11, 0.15)",
                                color: sh.share_type === "equity"
                                  ? "rgb(139, 92, 246)"
                                  : "rgb(245, 158, 11)",
                              }}
                            >
                              {sh.share_type}
                            </span>
                          </td>
                          <td className="p-3 text-right font-mono">Rs {sh.face_value}</td>
                          <td className="p-3 text-right font-bold">{sh.percentage}%</td>
                          <td className="p-3 text-center text-xs" style={{ color: "var(--color-text-muted)" }}>
                            {sh.date_of_allotment ? new Date(sh.date_of_allotment).toLocaleDateString() : "-"}
                          </td>
                          <td className="p-3 text-center">
                            {sh.is_promoter ? (
                              <span style={{ color: "var(--color-accent-emerald)" }}>Yes</span>
                            ) : (
                              <span style={{ color: "var(--color-text-muted)" }}>No</span>
                            )}
                          </td>
                          <td className="p-3 text-center">
                            <button
                              onClick={() => handleCertificate(sh.id)}
                              disabled={certLoading === sh.id}
                              className="text-xs px-2 py-1 rounded transition-all"
                              style={{
                                background: "rgba(16, 185, 129, 0.15)",
                                color: "rgb(16, 185, 129)",
                                border: "1px solid rgba(16, 185, 129, 0.3)",
                              }}
                            >
                              {certLoading === sh.id ? "..." : "Certificate"}
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Add Shareholder Tab */}
        {activeTab === "add" && (
          <div className="max-w-lg mx-auto">
            <div className="glass-card p-6" style={{ cursor: "default" }}>
              <h3 className="font-semibold mb-4">Add New Shareholder</h3>
              <form onSubmit={handleAddShareholder} className="space-y-4">
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                    Name *
                  </label>
                  <input
                    type="text"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    required
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{
                      background: "var(--color-bg-card)",
                      border: "1px solid var(--color-border)",
                      color: "var(--color-text-primary)",
                    }}
                    placeholder="Shareholder name"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                      Shares *
                    </label>
                    <input
                      type="number"
                      value={newShares}
                      onChange={(e) => setNewShares(e.target.value)}
                      required
                      min={1}
                      className="w-full px-3 py-2 rounded-lg text-sm"
                      style={{
                        background: "var(--color-bg-card)",
                        border: "1px solid var(--color-border)",
                        color: "var(--color-text-primary)",
                      }}
                      placeholder="Number of shares"
                    />
                  </div>
                  <div>
                    <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                      Share Type
                    </label>
                    <select
                      value={newShareType}
                      onChange={(e) => setNewShareType(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg text-sm"
                      style={{
                        background: "var(--color-bg-card)",
                        border: "1px solid var(--color-border)",
                        color: "var(--color-text-primary)",
                      }}
                    >
                      <option value="equity">Equity</option>
                      <option value="preference">Preference</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                    Face Value (Rs)
                  </label>
                  <input
                    type="number"
                    value={newFaceValue}
                    onChange={(e) => setNewFaceValue(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{
                      background: "var(--color-bg-card)",
                      border: "1px solid var(--color-border)",
                      color: "var(--color-text-primary)",
                    }}
                    placeholder="10"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                      Email
                    </label>
                    <input
                      type="email"
                      value={newEmail}
                      onChange={(e) => setNewEmail(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg text-sm"
                      style={{
                        background: "var(--color-bg-card)",
                        border: "1px solid var(--color-border)",
                        color: "var(--color-text-primary)",
                      }}
                      placeholder="email@example.com"
                    />
                  </div>
                  <div>
                    <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                      PAN Number
                    </label>
                    <input
                      type="text"
                      value={newPan}
                      onChange={(e) => setNewPan(e.target.value.toUpperCase())}
                      maxLength={10}
                      className="w-full px-3 py-2 rounded-lg text-sm"
                      style={{
                        background: "var(--color-bg-card)",
                        border: "1px solid var(--color-border)",
                        color: "var(--color-text-primary)",
                      }}
                      placeholder="ABCDE1234F"
                    />
                  </div>
                </div>
                <label className="flex items-center gap-2 text-sm" style={{ color: "var(--color-text-secondary)" }}>
                  <input
                    type="checkbox"
                    checked={newIsPromoter}
                    onChange={(e) => setNewIsPromoter(e.target.checked)}
                  />
                  Promoter shareholder
                </label>
                <button type="submit" className="btn-primary w-full text-center justify-center">
                  Add Shareholder
                </button>
              </form>
            </div>
          </div>
        )}

        {/* Transfer Tab */}
        {activeTab === "transfer" && (
          <div className="max-w-lg mx-auto">
            <div className="glass-card p-6" style={{ cursor: "default" }}>
              <h3 className="font-semibold mb-4">Record Share Transfer</h3>
              {capTable && capTable.shareholders.length >= 2 ? (
                <form onSubmit={handleTransfer} className="space-y-4">
                  <div>
                    <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                      From (Transferor) *
                    </label>
                    <select
                      value={fromId}
                      onChange={(e) => setFromId(e.target.value)}
                      required
                      className="w-full px-3 py-2 rounded-lg text-sm"
                      style={{
                        background: "var(--color-bg-card)",
                        border: "1px solid var(--color-border)",
                        color: "var(--color-text-primary)",
                      }}
                    >
                      <option value="">Select transferor</option>
                      {capTable.shareholders.map((sh) => (
                        <option key={sh.id} value={sh.id}>
                          {sh.name} ({sh.shares.toLocaleString()} shares)
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                      To (Transferee) *
                    </label>
                    <select
                      value={toId}
                      onChange={(e) => setToId(e.target.value)}
                      required
                      className="w-full px-3 py-2 rounded-lg text-sm"
                      style={{
                        background: "var(--color-bg-card)",
                        border: "1px solid var(--color-border)",
                        color: "var(--color-text-primary)",
                      }}
                    >
                      <option value="">Select transferee</option>
                      {capTable.shareholders
                        .filter((sh) => String(sh.id) !== fromId)
                        .map((sh) => (
                          <option key={sh.id} value={sh.id}>
                            {sh.name} ({sh.shares.toLocaleString()} shares)
                          </option>
                        ))}
                    </select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                        Shares to Transfer *
                      </label>
                      <input
                        type="number"
                        value={transferShares}
                        onChange={(e) => setTransferShares(e.target.value)}
                        required
                        min={1}
                        className="w-full px-3 py-2 rounded-lg text-sm"
                        style={{
                          background: "var(--color-bg-card)",
                          border: "1px solid var(--color-border)",
                          color: "var(--color-text-primary)",
                        }}
                        placeholder="Number of shares"
                      />
                    </div>
                    <div>
                      <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                        Price per Share (Rs)
                      </label>
                      <input
                        type="number"
                        value={transferPrice}
                        onChange={(e) => setTransferPrice(e.target.value)}
                        className="w-full px-3 py-2 rounded-lg text-sm"
                        style={{
                          background: "var(--color-bg-card)",
                          border: "1px solid var(--color-border)",
                          color: "var(--color-text-primary)",
                        }}
                        placeholder="10"
                      />
                    </div>
                  </div>
                  <button type="submit" className="btn-primary w-full text-center justify-center">
                    Record Transfer (SH-4)
                  </button>
                </form>
              ) : (
                <div className="text-center py-4" style={{ color: "var(--color-text-muted)" }}>
                  Add at least 2 shareholders before recording transfers.
                </div>
              )}
            </div>
          </div>
        )}

        {/* Transaction History Tab */}
        {activeTab === "history" && (
          <div className="glass-card overflow-hidden" style={{ cursor: "default" }}>
            <div className="p-4" style={{ borderBottom: "1px solid var(--color-border)" }}>
              <h3 className="font-semibold">Transaction History</h3>
            </div>
            {transactions.length === 0 ? (
              <div className="p-8 text-center" style={{ color: "var(--color-text-muted)" }}>
                No transactions recorded yet.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                      <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Date</th>
                      <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Type</th>
                      <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>From</th>
                      <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>To</th>
                      <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Shares</th>
                      <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Amount</th>
                      <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Form</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((tx) => (
                      <tr
                        key={tx.id}
                        style={{ borderBottom: "1px solid var(--color-border)" }}
                      >
                        <td className="p-3 text-xs" style={{ color: "var(--color-text-muted)" }}>
                          {tx.date ? new Date(tx.date).toLocaleDateString() : "-"}
                        </td>
                        <td className="p-3 text-center">
                          <span
                            className="text-xs px-2 py-0.5 rounded-full"
                            style={{
                              background:
                                tx.type === "allotment"
                                  ? "rgba(16, 185, 129, 0.15)"
                                  : tx.type === "transfer"
                                    ? "rgba(59, 130, 246, 0.15)"
                                    : "rgba(244, 63, 94, 0.15)",
                              color:
                                tx.type === "allotment"
                                  ? "rgb(16, 185, 129)"
                                  : tx.type === "transfer"
                                    ? "rgb(59, 130, 246)"
                                    : "rgb(244, 63, 94)",
                            }}
                          >
                            {tx.type}
                          </span>
                        </td>
                        <td className="p-3">{tx.from_shareholder || "-"}</td>
                        <td className="p-3">{tx.to_shareholder || "-"}</td>
                        <td className="p-3 text-right font-mono">{tx.shares.toLocaleString()}</td>
                        <td className="p-3 text-right font-mono">
                          Rs {tx.total_amount.toLocaleString()}
                        </td>
                        <td className="p-3 text-center text-xs" style={{ color: "var(--color-text-muted)" }}>
                          {tx.form_reference || "-"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Round Simulator Tab */}
        {activeTab === "simulator" && (
          <div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Input Panel */}
              <div className="glass-card p-6" style={{ cursor: "default" }}>
                <h3 className="font-semibold mb-4">Round Parameters</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                      Round Name
                    </label>
                    <input
                      type="text"
                      value={simRoundName}
                      onChange={(e) => setSimRoundName(e.target.value)}
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
                      Pre-Money Valuation (Rs)
                    </label>
                    <input
                      type="number"
                      value={simPreMoney}
                      onChange={(e) => setSimPreMoney(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg text-sm"
                      style={{
                        background: "var(--color-bg-card)",
                        border: "1px solid var(--color-border)",
                        color: "var(--color-text-primary)",
                      }}
                    />
                    <div className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
                      {formatCurrency(parseFloat(simPreMoney) || 0)}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                      ESOP Pool (% pre-round)
                    </label>
                    <div className="flex items-center gap-3">
                      <input
                        type="range"
                        min="0"
                        max="25"
                        step="0.5"
                        value={simEsopPct}
                        onChange={(e) => setSimEsopPct(e.target.value)}
                        className="flex-1"
                        style={{ accentColor: "rgb(139, 92, 246)" }}
                      />
                      <span className="text-sm font-mono w-12 text-right">{simEsopPct}%</span>
                    </div>
                  </div>

                  {/* Investors */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm" style={{ color: "var(--color-text-muted)" }}>Investors</label>
                      <button
                        onClick={addInvestor}
                        className="text-xs px-2 py-1 rounded"
                        style={{ background: "rgba(139, 92, 246, 0.15)", color: "rgb(139, 92, 246)" }}
                      >
                        + Add Investor
                      </button>
                    </div>
                    <div className="space-y-2">
                      {simInvestors.map((inv, idx) => (
                        <div key={idx} className="flex gap-2 items-center">
                          <input
                            type="text"
                            value={inv.name}
                            onChange={(e) => updateInvestor(idx, "name", e.target.value)}
                            placeholder="Name"
                            className="flex-1 px-3 py-2 rounded-lg text-sm"
                            style={{
                              background: "var(--color-bg-card)",
                              border: "1px solid var(--color-border)",
                              color: "var(--color-text-primary)",
                            }}
                          />
                          <input
                            type="number"
                            value={inv.amount}
                            onChange={(e) => updateInvestor(idx, "amount", e.target.value)}
                            placeholder="Amount (Rs)"
                            className="w-36 px-3 py-2 rounded-lg text-sm"
                            style={{
                              background: "var(--color-bg-card)",
                              border: "1px solid var(--color-border)",
                              color: "var(--color-text-primary)",
                            }}
                          />
                          {simInvestors.length > 1 && (
                            <button
                              onClick={() => removeInvestor(idx)}
                              className="text-xs px-2 py-2 rounded"
                              style={{ color: "rgb(244, 63, 94)" }}
                            >
                              X
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                    <div className="text-xs mt-2" style={{ color: "var(--color-text-muted)" }}>
                      Total Investment: {formatCurrency(simInvestors.reduce((s, i) => s + (parseFloat(i.amount) || 0), 0))}
                    </div>
                  </div>

                  <button
                    onClick={handleSimulateRound}
                    disabled={simLoading}
                    className="btn-primary w-full text-center justify-center"
                  >
                    {simLoading ? "Simulating..." : "Run Simulation"}
                  </button>
                </div>
              </div>

              {/* Results Panel */}
              <div>
                {!simResult && !simLoading && (
                  <div className="glass-card p-8 text-center" style={{ cursor: "default" }}>
                    <div className="text-4xl mb-4">&#x1F4CA;</div>
                    <h3 className="text-lg font-semibold mb-2">Round Simulator</h3>
                    <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                      Configure your round parameters and click &quot;Run Simulation&quot; to see how
                      the new investment will affect ownership.
                    </p>
                  </div>
                )}

                {simLoading && (
                  <div className="glass-card p-8 text-center" style={{ cursor: "default" }}>
                    <div className="text-sm" style={{ color: "var(--color-text-muted)" }}>Calculating...</div>
                  </div>
                )}

                {simResult && (
                  <div className="space-y-4">
                    {/* Valuation Summary */}
                    <div className="grid grid-cols-3 gap-3">
                      <div className="glass-card p-3 text-center" style={{ cursor: "default" }}>
                        <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Pre-Money</div>
                        <div className="text-sm font-bold">{formatCurrency(simResult.pre_money_valuation)}</div>
                      </div>
                      <div className="glass-card p-3 text-center" style={{ cursor: "default" }}>
                        <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Investment</div>
                        <div className="text-sm font-bold" style={{ color: "rgb(16, 185, 129)" }}>
                          {formatCurrency(simResult.investment_amount)}
                        </div>
                      </div>
                      <div className="glass-card p-3 text-center" style={{ cursor: "default" }}>
                        <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Post-Money</div>
                        <div className="text-sm font-bold">{formatCurrency(simResult.post_money_valuation)}</div>
                      </div>
                    </div>

                    <div className="glass-card p-3 text-center" style={{ cursor: "default" }}>
                      <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Price Per Share</div>
                      <div className="text-sm font-bold">Rs {simResult.price_per_share?.toFixed(2)}</div>
                    </div>

                    {/* Before/After Comparison */}
                    <div className="glass-card overflow-hidden" style={{ cursor: "default" }}>
                      <div className="p-4" style={{ borderBottom: "1px solid var(--color-border)" }}>
                        <h3 className="font-semibold text-sm">Ownership Comparison</h3>
                      </div>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                              <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Shareholder</th>
                              <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Before</th>
                              <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>After</th>
                              <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Dilution</th>
                            </tr>
                          </thead>
                          <tbody>
                            {simResult.after_round?.map((holder: any, idx: number) => {
                              const before = simResult.before_round?.find((b: any) => b.name === holder.name);
                              return (
                                <tr key={idx} style={{ borderBottom: "1px solid var(--color-border)" }}>
                                  <td className="p-3 font-medium">{holder.name}</td>
                                  <td className="p-3 text-right font-mono">
                                    {before ? `${before.percentage.toFixed(1)}%` : "-"}
                                  </td>
                                  <td className="p-3 text-right font-mono">{holder.percentage.toFixed(1)}%</td>
                                  <td className="p-3 text-right font-mono" style={{
                                    color: holder.dilution_pct > 0 ? "rgb(244, 63, 94)" : "rgb(16, 185, 129)"
                                  }}>
                                    {holder.dilution_pct > 0 ? `-${holder.dilution_pct.toFixed(1)}%` : holder.dilution_pct === 0 ? "New" : `+${Math.abs(holder.dilution_pct).toFixed(1)}%`}
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Post-Round Pie Chart */}
                    {simResult.after_round && simResult.after_round.length > 0 && (
                      <div className="glass-card p-6" style={{ cursor: "default" }}>
                        <h3 className="text-center font-semibold mb-4 text-sm">Post-Round Ownership</h3>
                        <div className="flex flex-col items-center gap-4">
                          <div
                            style={{
                              width: "180px",
                              height: "180px",
                              borderRadius: "50%",
                              background: `conic-gradient(${simResult.after_round.map((h: any, i: number) => {
                                const colors = [
                                  "rgb(139, 92, 246)", "rgb(59, 130, 246)", "rgb(16, 185, 129)",
                                  "rgb(245, 158, 11)", "rgb(244, 63, 94)", "rgb(99, 102, 241)",
                                  "rgb(236, 72, 153)", "rgb(34, 211, 238)", "rgb(251, 146, 60)", "rgb(163, 230, 53)"
                                ];
                                const cumBefore = simResult.after_round.slice(0, i).reduce((s: number, x: any) => s + x.percentage, 0);
                                return `${colors[i % colors.length]} ${cumBefore}% ${cumBefore + h.percentage}%`;
                              }).join(", ")})`,
                              boxShadow: "0 0 30px rgba(139, 92, 246, 0.2)",
                            }}
                          />
                          <div className="flex flex-wrap gap-3 justify-center max-w-md">
                            {simResult.after_round.map((h: any, i: number) => {
                              const colors = [
                                "rgb(139, 92, 246)", "rgb(59, 130, 246)", "rgb(16, 185, 129)",
                                "rgb(245, 158, 11)", "rgb(244, 63, 94)", "rgb(99, 102, 241)",
                                "rgb(236, 72, 153)", "rgb(34, 211, 238)", "rgb(251, 146, 60)", "rgb(163, 230, 53)"
                              ];
                              return (
                                <div key={i} className="flex items-center gap-2 text-xs">
                                  <span
                                    className="inline-block w-3 h-3 rounded-sm"
                                    style={{ background: colors[i % colors.length] }}
                                  />
                                  <span style={{ color: "var(--color-text-secondary)" }}>
                                    {h.name} ({h.percentage.toFixed(1)}%)
                                  </span>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Exit Scenarios Tab */}
        {activeTab === "exit" && (
          <div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Input Panel */}
              <div className="glass-card p-6" style={{ cursor: "default" }}>
                <h3 className="font-semibold mb-4">Exit Parameters</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                      Exit Valuation (Rs)
                    </label>
                    <input
                      type="number"
                      value={exitValuation}
                      onChange={(e) => setExitValuation(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg text-sm"
                      style={{
                        background: "var(--color-bg-card)",
                        border: "1px solid var(--color-border)",
                        color: "var(--color-text-primary)",
                      }}
                    />
                    <div className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
                      {formatCurrency(parseFloat(exitValuation) || 0)}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                      Liquidation Preference
                    </label>
                    <select
                      value={exitLiqPref}
                      onChange={(e) => setExitLiqPref(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg text-sm"
                      style={{
                        background: "var(--color-bg-card)",
                        border: "1px solid var(--color-border)",
                        color: "var(--color-text-primary)",
                      }}
                    >
                      <option value="0">None (Common)</option>
                      <option value="1">1x</option>
                      <option value="1.5">1.5x</option>
                      <option value="2">2x</option>
                    </select>
                  </div>

                  {/* Quick scenario buttons */}
                  <div>
                    <label className="block text-sm mb-2" style={{ color: "var(--color-text-muted)" }}>
                      Quick Scenarios
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {[10000000, 25000000, 50000000, 100000000, 500000000].map((val) => (
                        <button
                          key={val}
                          onClick={() => setExitValuation(String(val))}
                          className="text-xs px-3 py-1.5 rounded-lg transition-all"
                          style={{
                            background: exitValuation === String(val)
                              ? "rgba(139, 92, 246, 0.2)"
                              : "rgba(255,255,255,0.05)",
                            border: `1px solid ${exitValuation === String(val) ? "rgba(139, 92, 246, 0.5)" : "var(--color-border)"}`,
                            color: "var(--color-text-secondary)",
                          }}
                        >
                          {formatCurrency(val)}
                        </button>
                      ))}
                    </div>
                  </div>

                  <button
                    onClick={handleSimulateExit}
                    disabled={exitLoading}
                    className="btn-primary w-full text-center justify-center"
                  >
                    {exitLoading ? "Calculating..." : "Calculate Payouts"}
                  </button>
                </div>
              </div>

              {/* Results Panel */}
              <div>
                {!exitResult && !exitLoading && (
                  <div className="glass-card p-8 text-center" style={{ cursor: "default" }}>
                    <div className="text-4xl mb-4">&#x1F4B0;</div>
                    <h3 className="text-lg font-semibold mb-2">Exit Scenarios</h3>
                    <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                      Model different exit valuations to see how proceeds would be
                      distributed among shareholders.
                    </p>
                  </div>
                )}

                {exitLoading && (
                  <div className="glass-card p-8 text-center" style={{ cursor: "default" }}>
                    <div className="text-sm" style={{ color: "var(--color-text-muted)" }}>Calculating payouts...</div>
                  </div>
                )}

                {exitResult && (
                  <div className="space-y-4">
                    {/* Summary */}
                    <div className="grid grid-cols-2 gap-3">
                      <div className="glass-card p-3 text-center" style={{ cursor: "default" }}>
                        <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Exit Valuation</div>
                        <div className="text-sm font-bold">{formatCurrency(exitResult.exit_valuation)}</div>
                      </div>
                      <div className="glass-card p-3 text-center" style={{ cursor: "default" }}>
                        <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Value / Share</div>
                        <div className="text-sm font-bold">Rs {exitResult.value_per_share?.toFixed(2)}</div>
                      </div>
                    </div>

                    {/* Payout Table */}
                    <div className="glass-card overflow-hidden" style={{ cursor: "default" }}>
                      <div className="p-4" style={{ borderBottom: "1px solid var(--color-border)" }}>
                        <h3 className="font-semibold text-sm">Shareholder Payouts</h3>
                      </div>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                              <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Shareholder</th>
                              <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Shares</th>
                              <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Ownership</th>
                              <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Payout</th>
                              <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>ROI</th>
                            </tr>
                          </thead>
                          <tbody>
                            {exitResult.payouts?.map((p: any, idx: number) => (
                              <tr key={idx} style={{ borderBottom: "1px solid var(--color-border)" }}>
                                <td className="p-3 font-medium">
                                  {p.name}
                                  {p.is_promoter && (
                                    <span
                                      className="ml-2 text-xs px-1.5 py-0.5 rounded-full"
                                      style={{ background: "rgba(139, 92, 246, 0.15)", color: "rgb(139, 92, 246)" }}
                                    >
                                      Promoter
                                    </span>
                                  )}
                                </td>
                                <td className="p-3 text-right font-mono">{p.shares?.toLocaleString()}</td>
                                <td className="p-3 text-right font-mono">{p.percentage?.toFixed(1)}%</td>
                                <td className="p-3 text-right font-mono font-bold" style={{ color: "rgb(16, 185, 129)" }}>
                                  {formatCurrency(p.payout_amount)}
                                </td>
                                <td className="p-3 text-right font-mono" style={{
                                  color: p.roi_multiple >= 10 ? "rgb(16, 185, 129)" :
                                         p.roi_multiple >= 2 ? "rgb(245, 158, 11)" : "var(--color-text-secondary)"
                                }}>
                                  {p.roi_multiple?.toFixed(1)}x
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Total Summary */}
                    <div className="glass-card p-4" style={{ cursor: "default" }}>
                      <div className="flex justify-between items-center">
                        <span className="text-sm" style={{ color: "var(--color-text-muted)" }}>Total Distributed</span>
                        <span className="font-bold">{formatCurrency(exitResult.summary?.total_distributed || 0)}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Waterfall Analysis Tab */}
        {activeTab === "waterfall" && (
          <div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Input Panel */}
              <div className="glass-card p-6" style={{ cursor: "default" }}>
                <h3 className="font-semibold mb-4">Waterfall Parameters</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                      Exit Valuation (Rs)
                    </label>
                    <input
                      type="number"
                      value={wfValuation}
                      onChange={(e) => setWfValuation(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg text-sm"
                      style={{
                        background: "var(--color-bg-card)",
                        border: "1px solid var(--color-border)",
                        color: "var(--color-text-primary)",
                      }}
                    />
                    <div className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
                      {formatCurrency(parseFloat(wfValuation) || 0)}
                    </div>
                  </div>

                  <label className="flex items-center gap-2 text-sm" style={{ color: "var(--color-text-secondary)" }}>
                    <input
                      type="checkbox"
                      checked={wfParticipating}
                      onChange={(e) => setWfParticipating(e.target.checked)}
                    />
                    Participating preferred (investors share in remaining after liq pref)
                  </label>

                  {/* Liquidation Preferences */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                        Liquidation Preferences
                      </label>
                      <button
                        onClick={addLiqPref}
                        className="text-xs px-2 py-1 rounded"
                        style={{ background: "rgba(139, 92, 246, 0.15)", color: "rgb(139, 92, 246)" }}
                      >
                        + Add Preference
                      </button>
                    </div>
                    {wfLiqPrefs.length === 0 && (
                      <div className="text-xs py-2" style={{ color: "var(--color-text-muted)" }}>
                        No liquidation preferences. All proceeds distributed pro-rata.
                      </div>
                    )}
                    <div className="space-y-2">
                      {wfLiqPrefs.map((lp, idx) => (
                        <div key={idx} className="flex gap-2 items-center">
                          <select
                            value={lp.shareholder_id}
                            onChange={(e) => updateLiqPref(idx, "shareholder_id", e.target.value)}
                            className="flex-1 px-2 py-2 rounded-lg text-sm"
                            style={{
                              background: "var(--color-bg-card)",
                              border: "1px solid var(--color-border)",
                              color: "var(--color-text-primary)",
                            }}
                          >
                            <option value="">Shareholder</option>
                            {capTable?.shareholders.map((sh) => (
                              <option key={sh.id} value={sh.id}>{sh.name}</option>
                            ))}
                          </select>
                          <input
                            type="number"
                            value={lp.multiple}
                            onChange={(e) => updateLiqPref(idx, "multiple", e.target.value)}
                            placeholder="1x"
                            className="w-16 px-2 py-2 rounded-lg text-sm text-center"
                            style={{
                              background: "var(--color-bg-card)",
                              border: "1px solid var(--color-border)",
                              color: "var(--color-text-primary)",
                            }}
                          />
                          <input
                            type="number"
                            value={lp.invested_amount}
                            onChange={(e) => updateLiqPref(idx, "invested_amount", e.target.value)}
                            placeholder="Invested (Rs)"
                            className="w-32 px-2 py-2 rounded-lg text-sm"
                            style={{
                              background: "var(--color-bg-card)",
                              border: "1px solid var(--color-border)",
                              color: "var(--color-text-primary)",
                            }}
                          />
                          <button
                            onClick={() => removeLiqPref(idx)}
                            className="text-xs px-2 py-2 rounded"
                            style={{ color: "rgb(244, 63, 94)" }}
                          >
                            X
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Quick scenario buttons */}
                  <div>
                    <label className="block text-sm mb-2" style={{ color: "var(--color-text-muted)" }}>
                      Quick Scenarios
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {[10000000, 25000000, 50000000, 100000000, 500000000].map((val) => (
                        <button
                          key={val}
                          onClick={() => setWfValuation(String(val))}
                          className="text-xs px-3 py-1.5 rounded-lg transition-all"
                          style={{
                            background: wfValuation === String(val)
                              ? "rgba(139, 92, 246, 0.2)"
                              : "rgba(255,255,255,0.05)",
                            border: `1px solid ${wfValuation === String(val) ? "rgba(139, 92, 246, 0.5)" : "var(--color-border)"}`,
                            color: "var(--color-text-secondary)",
                          }}
                        >
                          {formatCurrency(val)}
                        </button>
                      ))}
                    </div>
                  </div>

                  <button
                    onClick={handleWaterfall}
                    disabled={wfLoading}
                    className="btn-primary w-full text-center justify-center"
                  >
                    {wfLoading ? "Calculating..." : "Run Waterfall Analysis"}
                  </button>
                </div>
              </div>

              {/* Results Panel */}
              <div>
                {!wfResult && !wfLoading && (
                  <div className="glass-card p-8 text-center" style={{ cursor: "default" }}>
                    <div className="text-4xl mb-4">&#x1F4CA;</div>
                    <h3 className="text-lg font-semibold mb-2">Waterfall Analysis</h3>
                    <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                      Model exit scenarios with liquidation preferences to see
                      how proceeds flow through the waterfall.
                    </p>
                  </div>
                )}

                {wfLoading && (
                  <div className="glass-card p-8 text-center" style={{ cursor: "default" }}>
                    <div className="text-sm" style={{ color: "var(--color-text-muted)" }}>Calculating waterfall...</div>
                  </div>
                )}

                {wfResult && !wfResult.error && (
                  <div className="space-y-4">
                    {/* Summary */}
                    <div className="grid grid-cols-3 gap-3">
                      <div className="glass-card p-3 text-center" style={{ cursor: "default" }}>
                        <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Exit Valuation</div>
                        <div className="text-sm font-bold">{formatCurrency(wfResult.exit_valuation)}</div>
                      </div>
                      <div className="glass-card p-3 text-center" style={{ cursor: "default" }}>
                        <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Liq Pref Total</div>
                        <div className="text-sm font-bold" style={{ color: "rgb(245, 158, 11)" }}>
                          {formatCurrency(wfResult.summary?.total_lp_amount || 0)}
                        </div>
                      </div>
                      <div className="glass-card p-3 text-center" style={{ cursor: "default" }}>
                        <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Distributed</div>
                        <div className="text-sm font-bold" style={{ color: "rgb(16, 185, 129)" }}>
                          {formatCurrency(wfResult.summary?.total_distributed || 0)}
                        </div>
                      </div>
                    </div>

                    {/* Waterfall Steps */}
                    {wfResult.waterfall_steps?.map((step: any, idx: number) => (
                      <div key={idx} className="glass-card p-4" style={{ cursor: "default" }}>
                        <div className="flex justify-between items-center mb-2">
                          <h4 className="text-sm font-semibold">Step {idx + 1}: {step.step}</h4>
                          <span className="text-xs font-mono" style={{ color: "var(--color-text-muted)" }}>
                            {formatCurrency(step.amount)}
                          </span>
                        </div>
                        {step.details?.map((d: any, di: number) => (
                          <div key={di} className="flex justify-between text-xs py-1"
                            style={{ borderTop: di > 0 ? "1px solid var(--color-border)" : "none" }}>
                            <span>{d.name}</span>
                            <span className="font-mono">{formatCurrency(d.payout)}</span>
                          </div>
                        ))}
                      </div>
                    ))}

                    {/* Final Payouts */}
                    <div className="glass-card overflow-hidden" style={{ cursor: "default" }}>
                      <div className="p-4" style={{ borderBottom: "1px solid var(--color-border)" }}>
                        <h3 className="font-semibold text-sm">Final Payouts</h3>
                      </div>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                              <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Shareholder</th>
                              <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Liq Pref</th>
                              <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Pro-Rata</th>
                              <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Total</th>
                              <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>ROI</th>
                            </tr>
                          </thead>
                          <tbody>
                            {wfResult.payouts?.map((p: any) => (
                              <tr key={p.shareholder_id} style={{ borderBottom: "1px solid var(--color-border)" }}>
                                <td className="p-3 font-medium">
                                  {p.name}
                                  {p.is_promoter && (
                                    <span className="ml-2 text-xs px-1.5 py-0.5 rounded-full"
                                      style={{ background: "rgba(139, 92, 246, 0.15)", color: "rgb(139, 92, 246)" }}>
                                      Promoter
                                    </span>
                                  )}
                                </td>
                                <td className="p-3 text-right font-mono" style={{ color: "rgb(245, 158, 11)" }}>
                                  {p.lp_payout > 0 ? formatCurrency(p.lp_payout) : "-"}
                                </td>
                                <td className="p-3 text-right font-mono">
                                  {formatCurrency(p.pro_rata_payout)}
                                </td>
                                <td className="p-3 text-right font-mono font-bold" style={{ color: "rgb(16, 185, 129)" }}>
                                  {formatCurrency(p.total_payout)}
                                </td>
                                <td className="p-3 text-right font-mono" style={{
                                  color: p.roi_multiple >= 10 ? "rgb(16, 185, 129)" :
                                         p.roi_multiple >= 2 ? "rgb(245, 158, 11)" : "var(--color-text-secondary)"
                                }}>
                                  {p.roi_multiple?.toFixed(1)}x
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Empty state when no cap table */}
        {!loading && !capTable && activeTab === "overview" && (
          <div className="text-center py-16">
            <div className="text-4xl mb-4">&#128202;</div>
            <h3 className="text-lg font-semibold mb-2">No Cap Table Data</h3>
            <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
              Start by adding shareholders to build your cap table.
            </p>
            <button
              onClick={() => setActiveTab("add")}
              className="btn-primary mt-4"
            >
              Add First Shareholder
            </button>
          </div>
        )}
      </div>
      <Footer />
    </div>
  );
}
