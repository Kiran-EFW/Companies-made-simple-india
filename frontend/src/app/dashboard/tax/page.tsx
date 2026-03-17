"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { getCompanies, getTaxOverview, getAuditPack } from "@/lib/api";
import Link from "next/link";

const STATUS_COLORS: Record<string, { bg: string; color: string }> = {
  completed: { bg: "rgba(16, 185, 129, 0.1)", color: "var(--color-success)" },
  due_soon: { bg: "rgba(245, 158, 11, 0.1)", color: "var(--color-warning)" },
  upcoming: { bg: "rgba(139, 92, 246, 0.08)", color: "var(--color-text-secondary)" },
  overdue: { bg: "rgba(239, 68, 68, 0.1)", color: "var(--color-error)" },
  in_progress: { bg: "rgba(59, 130, 246, 0.1)", color: "var(--color-info)" },
  not_generated: { bg: "rgba(148, 163, 184, 0.1)", color: "var(--color-text-muted)" },
};

export default function TaxOverviewPage() {
  const { user, loading: authLoading } = useAuth();
  const [companies, setCompanies] = useState<any[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<number | null>(null);
  const [taxData, setTaxData] = useState<any>(null);
  const [auditPack, setAuditPack] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showAuditPack, setShowAuditPack] = useState(false);
  const [loadingAudit, setLoadingAudit] = useState(false);

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
    getTaxOverview(selectedCompany)
      .then(setTaxData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedCompany]);

  const handleGenerateAuditPack = async () => {
    if (!selectedCompany) return;
    setLoadingAudit(true);
    try {
      const pack = await getAuditPack(selectedCompany);
      setAuditPack(pack);
      setShowAuditPack(true);
    } catch (err) {
      console.error("Failed to generate audit pack:", err);
    } finally {
      setLoadingAudit(false);
    }
  };

  if (authLoading || (!user && loading)) {
    return (
      <div className="min-h-screen flex items-center justify-center glow-bg">
        <div className="animate-pulse-glow w-16 h-16 rounded-full flex items-center justify-center" style={{ background: "rgba(139, 92, 246, 0.2)" }}>
          <img src="/logo-icon.png" alt="Anvils" className="w-7 h-7 object-contain" />
        </div>
      </div>
    );
  }

  const getStatusBadge = (status: string) => {
    const s = STATUS_COLORS[status] || STATUS_COLORS.not_generated;
    return (
      <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full" style={{ background: s.bg, color: s.color }}>
        {status.replace(/_/g, " ")}
      </span>
    );
  };

  return (
    <div className="min-h-screen glow-bg">
      <nav className="glass-card sticky top-0 z-50 rounded-none border-t-0 border-x-0 border-b">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/dashboard" className="flex items-center gap-2">
            <img src="/logo-icon.png" alt="Anvils" className="w-5 h-5 object-contain" />
            <span className="font-bold hidden md:block" style={{ fontFamily: "var(--font-display)" }}>Anvils</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-xs font-medium transition-colors hover:text-purple-400" style={{ color: "var(--color-text-secondary)" }}>Dashboard</Link>
            <Link href="/dashboard/compliance" className="text-xs font-medium transition-colors hover:text-purple-400" style={{ color: "var(--color-text-secondary)" }}>Compliance</Link>
            <Link href="/dashboard/gst" className="text-xs font-medium transition-colors hover:text-purple-400" style={{ color: "var(--color-text-secondary)" }}>GST</Link>
            <Link href="/dashboard/accounting" className="text-xs font-medium transition-colors hover:text-purple-400" style={{ color: "var(--color-text-secondary)" }}>Accounting</Link>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>Tax Overview</h1>
            <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
              {taxData ? `FY ${taxData.financial_year}` : "ITR, TDS, advance tax, and financial summary"}
            </p>
          </div>
          <div className="flex items-center gap-3">
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
            <button
              onClick={handleGenerateAuditPack}
              disabled={loadingAudit || !selectedCompany}
              className="px-4 py-2 rounded-lg text-xs font-medium transition-colors disabled:opacity-50"
              style={{ background: "var(--color-accent-purple)", color: "#fff" }}
            >
              {loadingAudit ? "Generating..." : "Generate Audit Pack"}
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-20" style={{ color: "var(--color-text-muted)" }}>Loading tax data...</div>
        ) : !taxData ? (
          <div className="glass-card p-12 text-center">
            <p className="text-lg font-semibold mb-2" style={{ color: "var(--color-text-primary)" }}>No tax data available</p>
            <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>Select an incorporated company to view tax overview.</p>
          </div>
        ) : (
          <>
            {/* Summary Row */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <div className="glass-card rounded-xl p-5">
                <p className="text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>ITR Status</p>
                <div className="mt-1">{getStatusBadge(taxData.itr?.status || "not_generated")}</div>
                {taxData.itr?.due_date && (
                  <p className="text-[10px] mt-2" style={{ color: "var(--color-text-muted)" }}>
                    Due: {new Date(taxData.itr.due_date).toLocaleDateString("en-IN")}
                  </p>
                )}
              </div>
              <div className="glass-card rounded-xl p-5">
                <p className="text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>TDS Returns Filed</p>
                <p className="text-2xl font-bold" style={{ color: "var(--color-text-primary)" }}>
                  {taxData.tds_returns?.filter((t: any) => t.status === "completed").length || 0}/{taxData.tds_returns?.length || 4}
                </p>
              </div>
              <div className="glass-card rounded-xl p-5">
                <p className="text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>Advance Tax Paid</p>
                <p className="text-2xl font-bold" style={{ color: "var(--color-text-primary)" }}>
                  {taxData.advance_tax?.filter((t: any) => t.status === "completed").length || 0}/{taxData.advance_tax?.length || 4}
                </p>
              </div>
              <div className="glass-card rounded-xl p-5">
                <p className="text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>Penalty Exposure</p>
                <p className="text-2xl font-bold" style={{ color: taxData.penalty_exposure > 0 ? "var(--color-error)" : "var(--color-success)" }}>
                  Rs {(taxData.penalty_exposure || 0).toLocaleString("en-IN")}
                </p>
              </div>
            </div>

            {/* ITR Section */}
            <div className="glass-card rounded-xl p-5 mb-6">
              <h2 className="text-sm font-semibold mb-4" style={{ color: "var(--color-text-primary)" }}>Income Tax Return (ITR)</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>Status</p>
                  <div className="mt-1">{getStatusBadge(taxData.itr?.status || "not_generated")}</div>
                </div>
                <div>
                  <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>Due Date</p>
                  <p className="text-sm font-medium" style={{ color: "var(--color-text-primary)" }}>
                    {taxData.itr?.due_date ? new Date(taxData.itr.due_date).toLocaleDateString("en-IN") : "Not set"}
                  </p>
                </div>
                <div>
                  <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>Filed On</p>
                  <p className="text-sm font-medium" style={{ color: "var(--color-text-primary)" }}>
                    {taxData.itr?.completed_date ? new Date(taxData.itr.completed_date).toLocaleDateString("en-IN") : "-"}
                  </p>
                </div>
                <div>
                  <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>Acknowledgement</p>
                  <p className="text-sm font-medium" style={{ color: "var(--color-text-primary)" }}>
                    {taxData.itr?.filing_reference || "-"}
                  </p>
                </div>
              </div>
              {taxData.accounting_connected && (
                <p className="text-[10px] mt-3 px-2 py-1 rounded" style={{ background: "rgba(16, 185, 129, 0.05)", color: "var(--color-success)" }}>
                  Financial data auto-populated from accounting integration
                </p>
              )}
            </div>

            {/* TDS Returns */}
            <div className="glass-card rounded-xl p-5 mb-6">
              <h2 className="text-sm font-semibold mb-4" style={{ color: "var(--color-text-primary)" }}>TDS Quarterly Returns</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                {(taxData.tds_returns || []).map((tds: any, i: number) => (
                  <div key={i} className="p-3 rounded-lg" style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)" }}>
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-xs font-semibold" style={{ color: "var(--color-text-primary)" }}>{tds.quarter}</p>
                      {getStatusBadge(tds.status)}
                    </div>
                    <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                      Due: {tds.due_date ? new Date(tds.due_date).toLocaleDateString("en-IN") : "Not set"}
                    </p>
                    {tds.completed_date && (
                      <p className="text-[10px]" style={{ color: "var(--color-success)" }}>
                        Filed: {new Date(tds.completed_date).toLocaleDateString("en-IN")}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Advance Tax */}
            <div className="glass-card rounded-xl p-5 mb-6">
              <h2 className="text-sm font-semibold mb-4" style={{ color: "var(--color-text-primary)" }}>Advance Tax Installments</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                {(taxData.advance_tax || []).map((at: any, i: number) => (
                  <div key={i} className="p-3 rounded-lg" style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)" }}>
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-xs font-semibold" style={{ color: "var(--color-text-primary)" }}>{at.quarter}</p>
                      {getStatusBadge(at.status)}
                    </div>
                    <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                      Due: {at.due_date ? new Date(at.due_date).toLocaleDateString("en-IN") : "Not set"}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Financial Summary from Zoho */}
            {taxData.financial_summary && !taxData.financial_summary.error && (
              <div className="glass-card rounded-xl p-5 mb-6">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-sm font-semibold" style={{ color: "var(--color-text-primary)" }}>Financial Summary</h2>
                  <span className="text-[10px] px-2 py-0.5 rounded-full" style={{ background: "rgba(16, 185, 129, 0.1)", color: "var(--color-success)" }}>
                    from {taxData.financial_summary.org_name}
                  </span>
                </div>
                <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                  Profit & Loss and Balance Sheet data pulled from your connected accounting platform for FY {taxData.financial_year}.
                </p>
              </div>
            )}

            {/* TDS Sections Reference */}
            {taxData.tds_sections && taxData.tds_sections.length > 0 && (
              <div className="glass-card rounded-xl p-5">
                <h2 className="text-sm font-semibold mb-3" style={{ color: "var(--color-text-primary)" }}>TDS Section Reference</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {taxData.tds_sections.slice(0, 9).map((sec: any) => (
                    <div key={sec.section} className="flex justify-between items-center px-3 py-2 rounded text-xs" style={{ background: "var(--color-bg-secondary)" }}>
                      <div>
                        <span className="font-semibold" style={{ color: "var(--color-text-primary)" }}>{sec.section}</span>
                        <span className="ml-2" style={{ color: "var(--color-text-muted)" }}>{sec.description}</span>
                      </div>
                      <span className="font-bold" style={{ color: "var(--color-accent-purple-light)" }}>{sec.rate}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {/* Audit Pack Modal */}
        {showAuditPack && auditPack && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "rgba(0,0,0,0.6)" }}>
            <div className="glass-card rounded-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold" style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}>
                  Audit Pack — {auditPack.company_name}
                </h2>
                <button onClick={() => setShowAuditPack(false)} className="text-xs" style={{ color: "var(--color-text-muted)" }}>Close</button>
              </div>

              <p className="text-xs mb-4" style={{ color: "var(--color-text-secondary)" }}>
                FY {auditPack.financial_year} | Generated {new Date(auditPack.generated_at).toLocaleString("en-IN")}
              </p>

              {/* Compliance Score */}
              <div className="p-4 rounded-lg mb-4" style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)" }}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>Compliance Score</p>
                    <p className="text-3xl font-bold" style={{ color: auditPack.compliance_score?.score >= 80 ? "var(--color-success)" : auditPack.compliance_score?.score >= 50 ? "var(--color-warning)" : "var(--color-error)" }}>
                      {auditPack.compliance_score?.score}/100
                    </p>
                  </div>
                  <span className="text-2xl font-bold" style={{ color: "var(--color-text-muted)" }}>
                    {auditPack.compliance_score?.grade}
                  </span>
                </div>
              </div>

              {/* Checklist */}
              <div className="p-4 rounded-lg mb-4" style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)" }}>
                <h3 className="text-xs font-semibold mb-3" style={{ color: "var(--color-text-primary)" }}>Audit Readiness Checklist</h3>
                <div className="space-y-2">
                  {Object.entries(auditPack.checklist || {}).map(([key, done]) => (
                    <div key={key} className="flex items-center gap-2 text-xs">
                      <span style={{ color: done ? "var(--color-success)" : "var(--color-error)" }}>
                        {done ? "&#10003;" : "&#10007;"}
                      </span>
                      <span style={{ color: "var(--color-text-primary)" }}>
                        {key.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {auditPack.accounting_connected && (
                <p className="text-[10px] px-3 py-2 rounded" style={{ background: "rgba(16, 185, 129, 0.05)", color: "var(--color-success)" }}>
                  Financial reports included from connected accounting platform
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
