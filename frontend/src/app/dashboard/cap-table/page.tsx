"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { apiCall } from "@/lib/api";

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

interface CapTableData {
  company_id: number;
  total_shares: number;
  total_shareholders: number;
  shareholders: ShareholderData[];
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
  const [activeTab, setActiveTab] = useState<"overview" | "add" | "transfer" | "history">("overview");

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

  return (
    <div className="glow-bg min-h-screen">
      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-5 max-w-7xl mx-auto">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-2xl">&#x26A1;</span>
          <span className="text-xl font-bold" style={{ fontFamily: "var(--font-display)" }}>
            <span className="gradient-text">CMS</span>{" "}
            <span style={{ color: "var(--color-text-secondary)" }}>India</span>
          </span>
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
          {(["overview", "add", "transfer", "history"] as const).map((tab) => (
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
    </div>
  );
}
