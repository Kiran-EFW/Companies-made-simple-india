"use client";

import { useState, useEffect } from "react";
import { useCompany } from "@/lib/company-context";
import Link from "next/link";

import {
  getStakeholderPortfolio,
  getStakeholderProfiles,
  createStakeholderProfile,
  linkStakeholderToShareholder,
} from "@/lib/api";


interface StakeholderProfile {
  id: number;
  name: string;
  email: string;
  phone: string | null;
  stakeholder_type: string;
  entity_name: string | null;
  entity_type: string | null;
  pan_number: string | null;
  is_foreign: boolean;
  dashboard_access_token: string | null;
  linked_shareholder_ids: number[];
  created_at: string;
  updated_at: string;
}

interface PortfolioCompany {
  company_id: number;
  company_name: string;
  shares: number;
  percentage: number;
  share_type: string;
}

interface Portfolio {
  total_investments: number;
  total_shares: number;
  companies_count: number;
  companies: PortfolioCompany[];
}

const STAKEHOLDER_TYPE_COLORS: Record<string, { bg: string; text: string }> = {
  founder: { bg: "rgba(139, 92, 246, 0.15)", text: "rgb(139, 92, 246)" },
  investor: { bg: "rgba(59, 130, 246, 0.15)", text: "rgb(59, 130, 246)" },
  employee: { bg: "rgba(16, 185, 129, 0.15)", text: "rgb(16, 185, 129)" },
  advisor: { bg: "rgba(245, 158, 11, 0.15)", text: "rgb(245, 158, 11)" },
};

const ENTITY_TYPE_COLORS: Record<string, { bg: string; text: string }> = {
  fund: { bg: "rgba(99, 102, 241, 0.15)", text: "rgb(99, 102, 241)" },
  llp: { bg: "rgba(236, 72, 153, 0.15)", text: "rgb(236, 72, 153)" },
  company: { bg: "rgba(34, 211, 238, 0.15)", text: "rgb(34, 211, 238)" },
  individual: { bg: "rgba(163, 230, 53, 0.15)", text: "rgb(163, 230, 53)" },
};

function TypeBadge({ type, colorMap }: { type: string; colorMap: Record<string, { bg: string; text: string }> }) {
  const colors = colorMap[type] || { bg: "rgba(156, 163, 175, 0.15)", text: "rgb(156, 163, 175)" };
  return (
    <span
      className="text-xs px-2 py-0.5 rounded-full capitalize"
      style={{ background: colors.bg, color: colors.text }}
    >
      {type.replace(/_/g, " ")}
    </span>
  );
}

export default function StakeholderDashboardPage() {
  const { companies, selectedCompany, selectCompany, loading: companyLoading } = useCompany();
  const [activeTab, setActiveTab] = useState<"profiles" | "portfolio">("profiles");
  const [profiles, setProfiles] = useState<StakeholderProfile[]>([]);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  // Create profile modal
  const [showCreateProfile, setShowCreateProfile] = useState(false);
  const [profileForm, setProfileForm] = useState({
    name: "",
    email: "",
    phone: "",
    stakeholder_type: "founder",
    entity_name: "",
    entity_type: "individual",
    pan_number: "",
    is_foreign: false,
  });

  // Link to shareholder
  const [linkingProfileId, setLinkingProfileId] = useState<number | null>(null);
  const [shareholderIdInput, setShareholderIdInput] = useState("");

  // Share investor link
  const [copiedId, setCopiedId] = useState<number | null>(null);

  const handleCopyInvestorLink = (profile: StakeholderProfile) => {
    if (!profile.dashboard_access_token) return;
    const url = `${window.location.origin}/investor/${profile.dashboard_access_token}`;
    navigator.clipboard.writeText(url);
    setCopiedId(profile.id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  useEffect(() => {
    if (selectedCompany?.id) {
      fetchProfiles();
    }
  }, [selectedCompany?.id]);

  useEffect(() => {
    if (activeTab === "portfolio") {
      fetchPortfolio();
    }
  }, [activeTab]);

  async function fetchProfiles() {
    setLoading(true);
    try {
      const data = await getStakeholderProfiles(selectedCompany!.id);
      setProfiles(data);
    } catch {
      // Backend may not be running
    }
    setLoading(false);
  }

  async function fetchPortfolio() {
    setLoading(true);
    try {
      const data = await getStakeholderPortfolio();
      setPortfolio(data);
    } catch {
      // Backend may not be running
    }
    setLoading(false);
  }

  async function handleCreateProfile(e: React.FormEvent) {
    e.preventDefault();
    setMessage("");
    try {
      await createStakeholderProfile({
        name: profileForm.name,
        email: profileForm.email,
        phone: profileForm.phone || undefined,
        stakeholder_type: profileForm.stakeholder_type,
        entity_name: profileForm.entity_name || undefined,
        entity_type: profileForm.entity_type || undefined,
        pan_number: profileForm.pan_number || undefined,
        is_foreign: profileForm.is_foreign,
      });
      setMessage("Stakeholder profile created successfully!");
      setShowCreateProfile(false);
      setProfileForm({
        name: "",
        email: "",
        phone: "",
        stakeholder_type: "founder",
        entity_name: "",
        entity_type: "individual",
        pan_number: "",
        is_foreign: false,
      });
      fetchProfiles();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleLinkShareholder(e: React.FormEvent) {
    e.preventDefault();
    if (!linkingProfileId) return;
    setMessage("");
    try {
      await linkStakeholderToShareholder(linkingProfileId, parseInt(shareholderIdInput));
      setMessage("Stakeholder linked to shareholder successfully!");
      setLinkingProfileId(null);
      setShareholderIdInput("");
      fetchProfiles();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  return (
    <div>
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="badge badge-purple mb-4 mx-auto w-fit">Stakeholder Management</div>
          <h1
            className="text-3xl md:text-4xl font-bold mb-3"
            style={{ fontFamily: "var(--font-display)" }}
          >
            <span className="gradient-text">Stakeholder Dashboard</span>
          </h1>
          <p className="text-base" style={{ color: "var(--color-text-secondary)" }}>
            Manage stakeholder profiles, track investments, and link to cap table shareholders.
          </p>
        </div>

        {/* Company selector */}
        {companies.length > 1 && (
          <div className="flex justify-center mb-6">
            <select
              className="glass-card text-sm px-3 py-2 rounded-lg border-none outline-none"
              style={{ background: "var(--color-bg-card)", color: "var(--color-text-primary)" }}
              value={selectedCompany?.id || ""}
              onChange={(e) => selectCompany(Number(e.target.value))}
            >
              {companies.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.approved_name || c.proposed_names?.[0] || `Company #${c.id}`}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* No company guard */}
        {!selectedCompany && !companyLoading && (
          <div className="glass-card p-12 text-center" style={{ cursor: "default" }}>
            <h2 className="text-xl font-bold mb-2" style={{ color: "var(--color-text-primary)" }}>No company selected</h2>
            <p className="text-sm mb-6" style={{ color: "var(--color-text-secondary)" }}>
              Select a company from the sidebar to view stakeholder management.
            </p>
            <div className="flex items-center justify-center gap-3">
              <Link href="/pricing" className="px-5 py-2.5 rounded-lg text-sm font-semibold text-white" style={{ background: "#8B5CF6" }}>
                Incorporate a New Company
              </Link>
              <Link href="/dashboard/connect" className="px-5 py-2.5 rounded-lg text-sm font-semibold border" style={{ borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}>
                Connect Existing Company
              </Link>
            </div>
          </div>
        )}

        {companyLoading && (
          <div className="flex items-center justify-center py-24">
            <div className="animate-pulse-glow w-16 h-16 rounded-full flex items-center justify-center" style={{ background: "rgba(139, 92, 246, 0.2)" }}>
              <img src="/logo-icon.png" alt="Anvils" className="w-7 h-7 object-contain" />
            </div>
          </div>
        )}

        {selectedCompany && (
          <>
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
          {(["profiles", "portfolio"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className="glass-card px-4 py-2 text-sm font-medium transition-all"
              style={{
                borderColor: activeTab === tab ? "rgba(139, 92, 246, 0.6)" : "var(--color-border)",
                background: activeTab === tab ? "rgba(139, 92, 246, 0.15)" : "transparent",
              }}
            >
              {tab === "profiles" && "Profiles"}
              {tab === "portfolio" && "Portfolio"}
            </button>
          ))}
        </div>

        {loading && (
          <div className="text-center py-12" style={{ color: "var(--color-text-muted)" }}>
            Loading stakeholder data...
          </div>
        )}

        {/* ====== PROFILES TAB ====== */}
        {activeTab === "profiles" && !loading && (
          <div>
            <div className="flex justify-end mb-4">
              <button
                onClick={() => setShowCreateProfile(true)}
                className="btn-primary text-sm"
              >
                + Create Profile
              </button>
            </div>

            {profiles.length === 0 ? (
              <div className="text-center py-16">
                <div className="text-4xl mb-4">&#128101;</div>
                <h3 className="text-lg font-semibold mb-2">No Stakeholder Profiles</h3>
                <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                  Create your first stakeholder profile to start tracking founders, investors, employees, and advisors.
                </p>
                <button
                  onClick={() => setShowCreateProfile(true)}
                  className="btn-primary mt-4"
                >
                  Create First Profile
                </button>
              </div>
            ) : (
              <div className="glass-card overflow-hidden" style={{ cursor: "default" }}>
                <div className="p-4" style={{ borderBottom: "1px solid var(--color-border)" }}>
                  <h3 className="font-semibold">Stakeholder Profiles ({profiles.length})</h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                        <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Name</th>
                        <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Email</th>
                        <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Type</th>
                        <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Entity</th>
                        <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>PAN</th>
                        <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Foreign</th>
                        <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {profiles.map((profile) => (
                        <tr
                          key={profile.id}
                          style={{ borderBottom: "1px solid var(--color-border)" }}
                        >
                          <td className="p-3">
                            <div className="font-medium">{profile.name}</div>
                            {profile.phone && (
                              <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                                {profile.phone}
                              </div>
                            )}
                          </td>
                          <td className="p-3 text-sm" style={{ color: "var(--color-text-secondary)" }}>
                            {profile.email}
                          </td>
                          <td className="p-3 text-center">
                            <TypeBadge type={profile.stakeholder_type} colorMap={STAKEHOLDER_TYPE_COLORS} />
                          </td>
                          <td className="p-3">
                            {profile.entity_name ? (
                              <div>
                                <div className="text-sm">{profile.entity_name}</div>
                                {profile.entity_type && (
                                  <div className="mt-1">
                                    <TypeBadge type={profile.entity_type} colorMap={ENTITY_TYPE_COLORS} />
                                  </div>
                                )}
                              </div>
                            ) : (
                              <span style={{ color: "var(--color-text-muted)" }}>-</span>
                            )}
                          </td>
                          <td className="p-3 text-center font-mono text-xs">
                            {profile.pan_number || (
                              <span style={{ color: "var(--color-text-muted)" }}>-</span>
                            )}
                          </td>
                          <td className="p-3 text-center">
                            {profile.is_foreign ? (
                              <span style={{ color: "rgb(245, 158, 11)" }}>Yes</span>
                            ) : (
                              <span style={{ color: "var(--color-text-muted)" }}>No</span>
                            )}
                          </td>
                          <td className="p-3 text-right">
                            <div className="flex gap-1 justify-end">
                              {linkingProfileId === profile.id ? (
                                <form
                                  onSubmit={handleLinkShareholder}
                                  className="flex items-center gap-1"
                                  onClick={(e) => e.stopPropagation()}
                                >
                                  <input
                                    type="number"
                                    value={shareholderIdInput}
                                    onChange={(e) => setShareholderIdInput(e.target.value)}
                                    required
                                    min={1}
                                    placeholder="SH ID"
                                    className="w-20 px-2 py-1 rounded text-xs"
                                    style={{
                                      background: "var(--color-bg-card)",
                                      border: "1px solid var(--color-border)",
                                      color: "var(--color-text-primary)",
                                    }}
                                  />
                                  <button
                                    type="submit"
                                    className="text-[11px] px-2 py-1 rounded"
                                    style={{ background: "rgba(16, 185, 129, 0.1)", color: "rgb(16, 185, 129)" }}
                                  >
                                    Link
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => { setLinkingProfileId(null); setShareholderIdInput(""); }}
                                    className="text-[11px] px-2 py-1 rounded"
                                    style={{ color: "var(--color-text-muted)" }}
                                  >
                                    Cancel
                                  </button>
                                </form>
                              ) : (
                                <>
                                  <button
                                    onClick={() => setLinkingProfileId(profile.id)}
                                    className="text-[11px] px-2 py-1 rounded"
                                    style={{ background: "rgba(139, 92, 246, 0.1)", color: "rgb(139, 92, 246)" }}
                                  >
                                    Link Shareholder
                                  </button>
                                  {profile.dashboard_access_token && (
                                    <button
                                      onClick={() => handleCopyInvestorLink(profile)}
                                      className="text-[11px] px-2 py-1 rounded"
                                      style={{
                                        background: copiedId === profile.id ? "rgba(16, 185, 129, 0.1)" : "rgba(59, 130, 246, 0.1)",
                                        color: copiedId === profile.id ? "rgb(16, 185, 129)" : "rgb(59, 130, 246)",
                                      }}
                                    >
                                      {copiedId === profile.id ? "Copied!" : "Share Portal Link"}
                                    </button>
                                  )}
                                </>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ====== PORTFOLIO TAB ====== */}
        {activeTab === "portfolio" && !loading && (
          <div>
            {!portfolio || portfolio.companies_count === 0 ? (
              <div className="text-center py-16">
                <div className="text-4xl mb-4">&#128188;</div>
                <h3 className="text-lg font-semibold mb-2">No Portfolio Data</h3>
                <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                  Link stakeholder profiles to shareholders to see portfolio information.
                </p>
              </div>
            ) : (
              <div>
                {/* Portfolio Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                  <div className="glass-card p-4 text-center" style={{ cursor: "default" }}>
                    <div className="text-2xl font-bold">{portfolio.total_investments}</div>
                    <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                      Total Investments
                    </div>
                  </div>
                  <div className="glass-card p-4 text-center" style={{ cursor: "default" }}>
                    <div className="text-2xl font-bold">{portfolio.total_shares.toLocaleString()}</div>
                    <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                      Total Shares
                    </div>
                  </div>
                  <div className="glass-card p-4 text-center" style={{ cursor: "default" }}>
                    <div className="text-2xl font-bold" style={{ color: "var(--color-accent-emerald)" }}>
                      {portfolio.companies_count}
                    </div>
                    <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                      Companies
                    </div>
                  </div>
                </div>

                {/* Companies List */}
                <div className="glass-card overflow-hidden" style={{ cursor: "default" }}>
                  <div className="p-4" style={{ borderBottom: "1px solid var(--color-border)" }}>
                    <h3 className="font-semibold">Portfolio Companies</h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                          <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Company</th>
                          <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Shares</th>
                          <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Type</th>
                          <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Ownership %</th>
                        </tr>
                      </thead>
                      <tbody>
                        {portfolio.companies.map((company) => (
                          <tr
                            key={company.company_id}
                            style={{ borderBottom: "1px solid var(--color-border)" }}
                          >
                            <td className="p-3 font-medium">{company.company_name}</td>
                            <td className="p-3 text-right font-mono">{company.shares.toLocaleString()}</td>
                            <td className="p-3 text-center">
                              <span
                                className="text-xs px-2 py-0.5 rounded-full"
                                style={{
                                  background: company.share_type === "equity"
                                    ? "rgba(139, 92, 246, 0.15)"
                                    : "rgba(245, 158, 11, 0.15)",
                                  color: company.share_type === "equity"
                                    ? "rgb(139, 92, 246)"
                                    : "rgb(245, 158, 11)",
                                }}
                              >
                                {company.share_type}
                              </span>
                            </td>
                            <td className="p-3 text-right font-bold">{company.percentage}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
          </>
        )}
      </div>

      {/* ====== MODALS ====== */}

      {/* Create Profile Modal */}
      {showCreateProfile && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "rgba(0,0,0,0.6)" }}>
          <div
            className="glass-card p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto"
            style={{ cursor: "default", background: "var(--color-bg-card)" }}
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Create Stakeholder Profile</h3>
              <button onClick={() => setShowCreateProfile(false)} className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                Close
              </button>
            </div>
            <form onSubmit={handleCreateProfile} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Name *</label>
                  <input
                    type="text"
                    required
                    value={profileForm.name}
                    onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="Full name"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Email *</label>
                  <input
                    type="email"
                    required
                    value={profileForm.email}
                    onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="email@example.com"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Phone</label>
                  <input
                    type="text"
                    value={profileForm.phone}
                    onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="+91 9876543210"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Stakeholder Type *</label>
                  <select
                    value={profileForm.stakeholder_type}
                    onChange={(e) => setProfileForm({ ...profileForm, stakeholder_type: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  >
                    <option value="founder">Founder</option>
                    <option value="investor">Investor</option>
                    <option value="employee">Employee</option>
                    <option value="advisor">Advisor</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Entity Name</label>
                  <input
                    type="text"
                    value={profileForm.entity_name}
                    onChange={(e) => setProfileForm({ ...profileForm, entity_name: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="Fund or entity name"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Entity Type</label>
                  <select
                    value={profileForm.entity_type}
                    onChange={(e) => setProfileForm({ ...profileForm, entity_type: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  >
                    <option value="individual">Individual</option>
                    <option value="fund">Fund</option>
                    <option value="llp">LLP</option>
                    <option value="company">Company</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>PAN Number</label>
                <input
                  type="text"
                  value={profileForm.pan_number}
                  onChange={(e) => setProfileForm({ ...profileForm, pan_number: e.target.value.toUpperCase() })}
                  maxLength={10}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  placeholder="ABCDE1234F"
                />
              </div>
              <label className="flex items-center gap-2 text-sm" style={{ color: "var(--color-text-secondary)" }}>
                <input
                  type="checkbox"
                  checked={profileForm.is_foreign}
                  onChange={(e) => setProfileForm({ ...profileForm, is_foreign: e.target.checked })}
                />
                Foreign stakeholder (non-Indian resident)
              </label>
              <button type="submit" className="btn-primary w-full text-center justify-center">
                Create Profile
              </button>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
