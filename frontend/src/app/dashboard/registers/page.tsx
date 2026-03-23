"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import Link from "next/link";
import FeatureGate from "@/components/feature-gate";
import {
  getCompanies,
  getRegistersSummary,
  getRegister,
  addRegisterEntry,
  updateRegisterEntry,
  exportRegister,
} from "@/lib/api";


// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface RegisterMeta {
  type: string;
  name: string;
  section: string;
  fields: { key: string; label: string; type: string }[];
}

interface RegisterEntry {
  id: number;
  entry_number: number;
  entry_date: string;
  data: Record<string, any>;
}

interface RegisterSummaryItem {
  register_type: string;
  entry_count: number;
  last_updated: string | null;
}

// ---------------------------------------------------------------------------
// Register definitions
// ---------------------------------------------------------------------------

const REGISTER_DEFS: RegisterMeta[] = [
  {
    type: "members",
    name: "Register of Members",
    section: "Section 88",
    fields: [
      { key: "name", label: "Name", type: "text" },
      { key: "shares", label: "Shares", type: "number" },
      { key: "share_class", label: "Share Class", type: "text" },
      { key: "folio", label: "Folio Number", type: "text" },
    ],
  },
  {
    type: "directors",
    name: "Register of Directors & KMP",
    section: "Section 170",
    fields: [
      { key: "name", label: "Name", type: "text" },
      { key: "din", label: "DIN", type: "text" },
      { key: "designation", label: "Designation", type: "text" },
      { key: "appointment_date", label: "Appointment Date", type: "date" },
    ],
  },
  {
    type: "directors_shareholding",
    name: "Register of Directors' Shareholding",
    section: "Section 170",
    fields: [
      { key: "director", label: "Director Name", type: "text" },
      { key: "shares", label: "Shares", type: "number" },
      { key: "transaction_date", label: "Transaction Date", type: "date" },
    ],
  },
  {
    type: "charges",
    name: "Register of Charges",
    section: "Section 85",
    fields: [
      { key: "charge_holder", label: "Charge Holder", type: "text" },
      { key: "amount", label: "Amount (Rs)", type: "number" },
      { key: "property", label: "Property Charged", type: "text" },
      { key: "creation_date", label: "Creation Date", type: "date" },
    ],
  },
  {
    type: "loans_guarantees",
    name: "Register of Loans & Guarantees",
    section: "Section 186",
    fields: [
      { key: "type", label: "Type (Loan/Guarantee/Security)", type: "text" },
      { key: "party", label: "Party", type: "text" },
      { key: "amount", label: "Amount (Rs)", type: "number" },
      { key: "date", label: "Date", type: "date" },
    ],
  },
  {
    type: "investments",
    name: "Register of Investments",
    section: "Section 186",
    fields: [
      { key: "type", label: "Investment Type", type: "text" },
      { key: "entity", label: "Entity", type: "text" },
      { key: "amount", label: "Amount (Rs)", type: "number" },
      { key: "shares", label: "Shares/Units", type: "number" },
    ],
  },
  {
    type: "related_party",
    name: "Register of Related Party Contracts",
    section: "Section 189",
    fields: [
      { key: "party", label: "Related Party", type: "text" },
      { key: "relationship", label: "Relationship", type: "text" },
      { key: "contract", label: "Contract Description", type: "text" },
      { key: "value", label: "Value (Rs)", type: "number" },
    ],
  },
  {
    type: "share_transfers",
    name: "Register of Share Transfers",
    section: "",
    fields: [
      { key: "transferor", label: "Transferor", type: "text" },
      { key: "transferee", label: "Transferee", type: "text" },
      { key: "shares", label: "Shares", type: "number" },
      { key: "consideration", label: "Consideration (Rs)", type: "number" },
    ],
  },
  {
    type: "debenture_holders",
    name: "Register of Debenture Holders",
    section: "",
    fields: [
      { key: "holder", label: "Holder Name", type: "text" },
      { key: "debentures", label: "Debentures", type: "number" },
      { key: "value", label: "Face Value (Rs)", type: "number" },
      { key: "date", label: "Date of Issue", type: "date" },
    ],
  },
];

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function RegistersPage() {
  const { user, loading: authLoading } = useAuth();

  const [companies, setCompanies] = useState<any[]>([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState<number | null>(null);
  const [summary, setSummary] = useState<RegisterSummaryItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Selected register
  const [activeRegister, setActiveRegister] = useState<string | null>(null);
  const [entries, setEntries] = useState<RegisterEntry[]>([]);
  const [entriesLoading, setEntriesLoading] = useState(false);

  // Add / Edit form
  const [showForm, setShowForm] = useState(false);
  const [editingEntry, setEditingEntry] = useState<RegisterEntry | null>(null);
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [formDate, setFormDate] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  // Fetch companies
  useEffect(() => {
    if (authLoading || !user) return;
    getCompanies()
      .then((comps) => {
        setCompanies(comps);
        if (comps.length > 0) setSelectedCompanyId(comps[0].id);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [user, authLoading]);

  // Fetch summary when company changes
  useEffect(() => {
    if (!selectedCompanyId) return;
    setLoading(true);
    getRegistersSummary(selectedCompanyId)
      .then((data) => setSummary(data?.registers || []))
      .catch(() => setSummary([]))
      .finally(() => setLoading(false));
  }, [selectedCompanyId]);

  // Fetch entries when register is selected
  useEffect(() => {
    if (!selectedCompanyId || !activeRegister) return;
    setEntriesLoading(true);
    getRegister(selectedCompanyId, activeRegister)
      .then((data) => setEntries(data?.entries || []))
      .catch(() => setEntries([]))
      .finally(() => setEntriesLoading(false));
  }, [selectedCompanyId, activeRegister]);

  const getRegisterDef = (type: string) => REGISTER_DEFS.find((r) => r.type === type);

  const getSummaryForType = (type: string) => summary.find((s) => s.register_type === type);

  const handleOpenForm = (entry?: RegisterEntry) => {
    const def = getRegisterDef(activeRegister || "");
    if (!def) return;
    if (entry) {
      setEditingEntry(entry);
      const fd: Record<string, string> = {};
      def.fields.forEach((f) => {
        fd[f.key] = String(entry.data[f.key] || "");
      });
      setFormData(fd);
      setFormDate(entry.entry_date || "");
    } else {
      setEditingEntry(null);
      const fd: Record<string, string> = {};
      def.fields.forEach((f) => {
        fd[f.key] = "";
      });
      setFormData(fd);
      setFormDate(new Date().toISOString().split("T")[0]);
    }
    setShowForm(true);
    setMessage("");
  };

  const handleSave = async () => {
    if (!selectedCompanyId || !activeRegister) return;
    setSaving(true);
    setMessage("");
    try {
      const payload = { entry_date: formDate, data: { ...formData } };
      if (editingEntry) {
        await updateRegisterEntry(selectedCompanyId, activeRegister, editingEntry.id, payload);
        setMessage("Entry updated successfully.");
      } else {
        await addRegisterEntry(selectedCompanyId, activeRegister, payload);
        setMessage("Entry added successfully.");
      }
      // Refresh entries
      const data = await getRegister(selectedCompanyId, activeRegister);
      setEntries(data?.entries || []);
      // Refresh summary
      const sumData = await getRegistersSummary(selectedCompanyId);
      setSummary(sumData?.registers || []);
      setShowForm(false);
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleExport = async (registerType: string) => {
    if (!selectedCompanyId) return;
    try {
      const data = await exportRegister(selectedCompanyId, registerType);
      if (data?.html) {
        const blob = new Blob([data.html], { type: "text/html" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${registerType}_register.html`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error("Export failed:", err);
    }
  };

  // Loading / Auth
  if (authLoading || (loading && !summary.length)) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="animate-pulse-glow w-16 h-16 rounded-full flex items-center justify-center" style={{ background: "var(--color-purple-bg)" }}>
          <img src="/logo-icon.png" alt="Anvils" className="w-7 h-7 object-contain" />
        </div>
      </div>
    );
  }

  return (
    <FeatureGate
      moduleKey="registers"
      featureName="Statutory Registers"
      featureDescription="Statutory registers for members, directors, charges, and share transfers."
    >
    <div>
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 gap-4 animate-fade-in-up">
          <div>
            <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>
              Statutory Registers
            </h1>
            <p className="text-sm border-l-2 pl-3 border-purple-500" style={{ color: "var(--color-text-secondary)" }}>
              Companies Act 2013 mandatory registers
            </p>
          </div>
          {companies.length > 1 && (
            <select
              className="glass-card text-sm px-3 py-2 rounded-lg border-none outline-none"
              style={{ background: "var(--color-bg-card)", color: "var(--color-text-primary)" }}
              value={selectedCompanyId || ""}
              onChange={(e) => {
                setSelectedCompanyId(Number(e.target.value));
                setActiveRegister(null);
              }}
            >
              {companies.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.approved_name || c.proposed_names?.[0] || `Company #${c.id}`}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Penalty warning */}
        <div className="p-4 rounded-lg border border-amber-500/30 bg-amber-500/5 mb-8 animate-fade-in-up" style={{ animationDelay: "0.05s" }}>
          <p className="text-xs" style={{ color: "var(--color-warning)" }}>
            <span className="font-semibold">Important:</span> These registers are mandatory under the Companies Act 2013. Non-maintenance attracts penalties up to Rs 3,00,000.
          </p>
        </div>

        {companies.length === 0 ? (
          <div className="p-12 text-center" style={{ background: "var(--color-bg-card)" }}>
            <h2 className="text-xl font-bold mb-2" style={{ color: "var(--color-text-primary)" }}>No company selected</h2>
            <p className="text-sm mb-6" style={{ color: "var(--color-text-secondary)" }}>
              Select a company from the sidebar to view statutory registers and filings.
            </p>
            <div className="flex items-center justify-center gap-3">
              <Link href="/pricing" className="px-5 py-2.5 rounded-lg text-sm font-semibold text-white" style={{ background: "var(--color-accent-purple-light)" }}>
                Incorporate a New Company
              </Link>
              <Link href="/dashboard/connect" className="px-5 py-2.5 rounded-lg text-sm font-semibold border" style={{ borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}>
                Connect Existing Company
              </Link>
            </div>
          </div>
        ) : (
          <>
            {/* Register Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8 animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
              {REGISTER_DEFS.map((reg) => {
                const s = getSummaryForType(reg.type);
                const isActive = activeRegister === reg.type;
                return (
                  <button
                    key={reg.type}
                    onClick={() => setActiveRegister(isActive ? null : reg.type)}
                    className={`glass-card p-5 text-left transition-all ${
                      isActive ? "!border-purple-500/50 !bg-purple-500/10" : ""
                    }`}
                    style={{ cursor: "pointer" }}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-sm font-semibold" style={{ color: "var(--color-text-primary)" }}>{reg.name}</h3>
                        {reg.section && (
                          <p className="text-[10px] text-purple-400 font-medium mt-0.5">{reg.section}</p>
                        )}
                      </div>
                      <svg className="w-5 h-5 text-purple-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                      </svg>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div>
                          <p className="text-lg font-bold">{s?.entry_count ?? 0}</p>
                          <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Entries</p>
                        </div>
                        <div>
                          <p className="text-xs font-mono" style={{ color: "var(--color-text-muted)" }}>
                            {s?.last_updated
                              ? new Date(s.last_updated).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })
                              : "No entries"}
                          </p>
                          <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Last Updated</p>
                        </div>
                      </div>
                      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                        isActive
                          ? "bg-purple-500/20 text-purple-400 border-purple-500/30"
                          : ""
                      }`} style={!isActive ? { background: "var(--color-hover-overlay)", color: "var(--color-text-secondary)", borderColor: "var(--color-text-muted)" } : {}}>
                        {isActive ? "VIEWING" : "VIEW"}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Register Detail View */}
            {activeRegister && (
              <div className="glass-card p-6 animate-fade-in-up" style={{ cursor: "default" }}>
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
                  <div>
                    <h3 className="text-lg font-bold">{getRegisterDef(activeRegister)?.name}</h3>
                    {getRegisterDef(activeRegister)?.section && (
                      <p className="text-xs text-purple-400">{getRegisterDef(activeRegister)?.section}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => handleExport(activeRegister)}
                      className="text-xs font-medium border px-3 py-1.5 rounded-lg transition-colors"
                      style={{ color: "var(--color-text-secondary)", borderColor: "var(--color-border)" }}
                    >
                      Export HTML
                    </button>
                    <button
                      onClick={() => handleOpenForm()}
                      className="btn-primary text-sm !py-2 !px-4"
                    >
                      + Add Entry
                    </button>
                  </div>
                </div>

                {/* Message */}
                {message && (
                  <div className={`p-3 mb-4 rounded-lg text-sm text-center border ${
                    message.startsWith("Error")
                      ? "border-red-500/30 bg-red-500/5 text-red-400"
                      : "border-emerald-500/30 bg-emerald-500/5 text-emerald-400"
                  }`}>
                    {message}
                  </div>
                )}

                {/* Add/Edit Form */}
                {showForm && (
                  <div className="p-5 rounded-lg border border-purple-500/20 bg-purple-500/5 mb-6">
                    <h4 className="text-sm font-semibold mb-4">
                      {editingEntry ? "Edit Entry" : "New Entry"}
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>
                          Entry Date
                        </label>
                        <input
                          type="date"
                          value={formDate}
                          onChange={(e) => setFormDate(e.target.value)}
                          className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                          style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                        />
                      </div>
                      {getRegisterDef(activeRegister)?.fields.map((field) => (
                        <div key={field.key}>
                          <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>
                            {field.label}
                          </label>
                          <input
                            type={field.type}
                            value={formData[field.key] || ""}
                            onChange={(e) => setFormData((prev) => ({ ...prev, [field.key]: e.target.value }))}
                            className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                            style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                          />
                        </div>
                      ))}
                    </div>
                    <div className="flex gap-3">
                      <button
                        onClick={handleSave}
                        disabled={saving}
                        className="btn-primary text-sm !py-2 !px-6"
                      >
                        {saving ? "Saving..." : editingEntry ? "Update" : "Save Entry"}
                      </button>
                      <button
                        onClick={() => { setShowForm(false); setMessage(""); }}
                        className="text-sm px-4 py-2 rounded-lg border transition-colors"
                        style={{ color: "var(--color-text-secondary)", borderColor: "var(--color-border)" }}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}

                {/* Entries Table */}
                {entriesLoading ? (
                  <div className="text-center py-12" style={{ color: "var(--color-text-muted)" }}>
                    Loading entries...
                  </div>
                ) : entries.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                      No entries in this register yet. Click &quot;Add Entry&quot; to begin.
                    </p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                          <th className="text-left p-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                            #
                          </th>
                          <th className="text-left p-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                            Date
                          </th>
                          {getRegisterDef(activeRegister)?.fields.map((f) => (
                            <th key={f.key} className="text-left p-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                              {f.label}
                            </th>
                          ))}
                          <th className="text-right p-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {entries.map((entry) => (
                          <tr key={entry.id} style={{ borderBottom: "1px solid var(--color-border)" }} className="transition-colors">
                            <td className="p-3 font-mono text-xs">{entry.entry_number}</td>
                            <td className="p-3 text-xs" style={{ color: "var(--color-text-muted)" }}>
                              {entry.entry_date ? new Date(entry.entry_date).toLocaleDateString("en-IN") : "-"}
                            </td>
                            {getRegisterDef(activeRegister)?.fields.map((f) => (
                              <td key={f.key} className="p-3 text-sm">
                                {f.type === "number"
                                  ? Number(entry.data[f.key] || 0).toLocaleString("en-IN")
                                  : (entry.data[f.key] || "-")}
                              </td>
                            ))}
                            <td className="p-3 text-right">
                              <button
                                onClick={() => handleOpenForm(entry)}
                                className="text-xs text-purple-400 hover:text-purple-300 font-medium transition-colors"
                              >
                                Edit
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
    </FeatureGate>
  );
}
