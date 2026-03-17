"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { getCompanies, getGstDashboard } from "@/lib/api";
import Link from "next/link";

const STATUS_STYLES: Record<string, { bg: string; color: string }> = {
  completed: { bg: "var(--color-success-light)", color: "var(--color-success)" },
  due_soon: { bg: "var(--color-warning-light)", color: "var(--color-warning)" },
  upcoming: { bg: "var(--color-purple-bg)", color: "var(--color-text-secondary)" },
  overdue: { bg: "var(--color-error-light)", color: "var(--color-error)" },
};

export default function GstDashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const [companies, setCompanies] = useState<any[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<number | null>(null);
  const [gstData, setGstData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState<"upcoming" | "gstr1" | "gstr3b" | "annual">("upcoming");

  useEffect(() => {
    if (authLoading || !user) return;
    getCompanies()
      .then((comps) => {
        const incorporated = comps.filter((c: any) =>
          ["incorporated", "fully_setup", "bank_account_pending", "bank_account_opened", "inc20a_pending"].includes(c.status)
        );
        setCompanies(incorporated);
        if (incorporated.length > 0) setSelectedCompany(incorporated[0].id);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [user, authLoading]);

  useEffect(() => {
    if (!selectedCompany) return;
    setLoading(true);
    getGstDashboard(selectedCompany)
      .then(setGstData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedCompany]);

  const getFilteredReturns = () => {
    if (!gstData?.all_returns) return [];
    switch (activeView) {
      case "upcoming":
        return gstData.upcoming_returns || [];
      case "gstr1":
        return gstData.all_returns.filter((r: any) => r.return_type === "GSTR-1");
      case "gstr3b":
        return gstData.all_returns.filter((r: any) => r.return_type === "GSTR-3B");
      case "annual":
        return gstData.all_returns.filter((r: any) => ["GSTR-9", "GSTR-9C"].includes(r.return_type));
      default:
        return gstData.upcoming_returns || [];
    }
  };

  if (authLoading || (!user && loading)) {
    return (
      <div className="min-h-screen flex items-center justify-center glow-bg">
        <div className="animate-pulse-glow w-16 h-16 rounded-full flex items-center justify-center" style={{ background: "var(--color-purple-bg)" }}>
          <img src="/logo-icon.png" alt="Anvils" className="w-7 h-7 object-contain" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen glow-bg">
      <nav className="glass-card sticky top-0 z-50 rounded-none border-t-0 border-x-0 border-b">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/dashboard" className="flex items-center gap-2">
            <img src="/logo-icon.png" alt="Anvils" className="w-5 h-5 object-contain" />
            <span className="font-bold hidden md:block" style={{ fontFamily: "var(--font-display)" }}>Anvils</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-xs font-medium transition-colors hover:text-purple-400" style={{ color: "var(--color-text-secondary)" }}>
              Dashboard
            </Link>
            <Link href="/dashboard/compliance" className="text-xs font-medium transition-colors hover:text-purple-400" style={{ color: "var(--color-text-secondary)" }}>
              Compliance
            </Link>
            <Link href="/dashboard/tax" className="text-xs font-medium transition-colors hover:text-purple-400" style={{ color: "var(--color-text-secondary)" }}>
              Tax Overview
            </Link>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>GST Filing Dashboard</h1>
            <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
              Track GST returns, deadlines, and filing status
            </p>
          </div>
          {companies.length > 1 && (
            <select
              value={selectedCompany || ""}
              onChange={(e) => setSelectedCompany(Number(e.target.value))}
              className="text-sm rounded-lg px-3 py-2"
              style={{ background: "var(--color-bg-input)", color: "var(--color-text-primary)", border: "1px solid var(--color-border)" }}
            >
              {companies.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.approved_name || c.proposed_names?.[0] || `Company #${c.id}`}
                </option>
              ))}
            </select>
          )}
        </div>

        {loading ? (
          <div className="text-center py-20" style={{ color: "var(--color-text-muted)" }}>Loading GST data...</div>
        ) : !gstData ? (
          <div className="glass-card p-12 text-center">
            <p className="text-lg font-semibold mb-2" style={{ color: "var(--color-text-primary)" }}>No GST data available</p>
            <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>Select an incorporated company to view GST filing dashboard.</p>
          </div>
        ) : (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <div className="glass-card rounded-xl p-5">
                <p className="text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>Total Returns (FY)</p>
                <p className="text-2xl font-bold" style={{ color: "var(--color-text-primary)" }}>
                  {gstData.gst_summary?.total_returns_fy || 0}
                </p>
              </div>
              <div className="glass-card rounded-xl p-5">
                <p className="text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>Completed</p>
                <p className="text-2xl font-bold" style={{ color: "var(--color-success)" }}>
                  {gstData.gst_summary?.completed || 0}
                </p>
              </div>
              <div className="glass-card rounded-xl p-5">
                <p className="text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>Due Soon</p>
                <p className="text-2xl font-bold" style={{ color: "var(--color-warning)" }}>
                  {gstData.gst_summary?.due_soon || 0}
                </p>
              </div>
              <div className="glass-card rounded-xl p-5">
                <p className="text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>Accounting</p>
                <p className="text-sm font-semibold" style={{ color: gstData.accounting_connected ? "var(--color-success)" : "var(--color-text-muted)" }}>
                  {gstData.accounting_connected ? "Connected" : "Not Connected"}
                </p>
                {!gstData.accounting_connected && (
                  <Link href="/dashboard/accounting" className="text-[10px] text-purple-400 hover:underline">Connect now</Link>
                )}
              </div>
            </div>

            {/* Zoho Books Data */}
            {gstData.zoho_data && !gstData.zoho_data.error && (
              <div className="glass-card rounded-xl p-5 mb-8">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-sm font-semibold" style={{ color: "var(--color-text-primary)" }}>
                    Zoho Books — {gstData.zoho_data.org_name}
                  </h2>
                  <span className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                    Last synced: {gstData.zoho_data.last_sync ? new Date(gstData.zoho_data.last_sync).toLocaleString("en-IN") : "Never"}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>Sales Invoices</p>
                    <p className="text-xl font-bold" style={{ color: "var(--color-text-primary)" }}>{gstData.zoho_data.total_invoices}</p>
                    <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Used for GSTR-1 outward supplies</p>
                  </div>
                  <div>
                    <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>Purchase Bills</p>
                    <p className="text-xl font-bold" style={{ color: "var(--color-text-primary)" }}>{gstData.zoho_data.total_bills}</p>
                    <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Used for GSTR-2B input credit</p>
                  </div>
                </div>
              </div>
            )}

            {/* Return Type Tabs */}
            <div className="flex gap-1 glass-card rounded-lg p-1 w-fit mb-6">
              {[
                { key: "upcoming" as const, label: "Upcoming" },
                { key: "gstr1" as const, label: "GSTR-1" },
                { key: "gstr3b" as const, label: "GSTR-3B" },
                { key: "annual" as const, label: "Annual" },
              ].map(tab => (
                <button
                  key={tab.key}
                  onClick={() => setActiveView(tab.key)}
                  className="px-4 py-2 rounded-md text-sm font-medium transition"
                  style={activeView === tab.key
                    ? { background: "var(--color-accent-purple)", color: "#fff" }
                    : { color: "var(--color-text-secondary)" }
                  }
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Returns Table */}
            <div className="glass-card rounded-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                    {["Return", "Period", "Due Date", "Days Left", "Status"].map(h => (
                      <th key={h} className="text-left px-4 py-3 text-xs font-medium" style={{ color: "var(--color-text-muted)" }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {getFilteredReturns().length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-4 py-8 text-center text-xs" style={{ color: "var(--color-text-muted)" }}>
                        No returns found for this view.
                      </td>
                    </tr>
                  ) : (
                    getFilteredReturns().map((r: any, i: number) => {
                      const style = STATUS_STYLES[r.status] || STATUS_STYLES.upcoming;
                      return (
                        <tr key={`${r.return_type}-${r.period}-${i}`} style={{ borderBottom: "1px solid var(--color-border)" }}>
                          <td className="px-4 py-3">
                            <span className="text-xs font-semibold" style={{ color: "var(--color-text-primary)" }}>{r.return_type}</span>
                            <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>{r.description}</p>
                          </td>
                          <td className="px-4 py-3 text-xs" style={{ color: "var(--color-text-primary)" }}>{r.period}</td>
                          <td className="px-4 py-3 text-xs" style={{ color: "var(--color-text-secondary)" }}>
                            {r.due_date ? new Date(r.due_date).toLocaleDateString("en-IN") : "-"}
                          </td>
                          <td className="px-4 py-3 text-xs font-semibold" style={{ color: r.days_remaining <= 7 ? "var(--color-error)" : "var(--color-text-primary)" }}>
                            {r.status === "completed" ? "-" : `${r.days_remaining}d`}
                          </td>
                          <td className="px-4 py-3">
                            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full" style={{ background: style.bg, color: style.color }}>
                              {r.status?.replace(/_/g, " ")}
                            </span>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>

            {/* Info Section */}
            <div className="glass-card rounded-xl p-5 mt-8">
              <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--color-text-primary)" }}>GST Return Filing Guide</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs" style={{ color: "var(--color-text-secondary)" }}>
                <div>
                  <p className="font-semibold mb-1" style={{ color: "var(--color-text-primary)" }}>GSTR-1 (Outward Supplies)</p>
                  <p>Monthly return for reporting sales. Due by the 11th of the next month. Auto-populated from Zoho Books invoices when connected.</p>
                </div>
                <div>
                  <p className="font-semibold mb-1" style={{ color: "var(--color-text-primary)" }}>GSTR-3B (Summary + Tax Payment)</p>
                  <p>Monthly summary return with tax payment. Due by the 20th of the next month. Shows total output tax, input credit, and net payable.</p>
                </div>
                <div>
                  <p className="font-semibold mb-1" style={{ color: "var(--color-text-primary)" }}>GSTR-9 (Annual Return)</p>
                  <p>Annual consolidation of all monthly returns. Due by 31st December of the next financial year.</p>
                </div>
                <div>
                  <p className="font-semibold mb-1" style={{ color: "var(--color-text-primary)" }}>GSTR-9C (Audit Reconciliation)</p>
                  <p>Required if turnover exceeds Rs 5 Crore. Reconciliation between GSTR-9 and audited financials. Due with GSTR-9.</p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
