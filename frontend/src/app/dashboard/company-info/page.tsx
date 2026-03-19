"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useAuth } from "@/lib/auth-context";
import { useCompany } from "@/lib/company-context";
import { updateCompanyInfo, getCompanyDocuments, uploadDocument } from "@/lib/api";

// ---------------------------------------------------------------------------
// KYB document definitions
// ---------------------------------------------------------------------------

const KYB_DOCUMENTS = [
  { key: "incorporation_certificate", label: "Incorporation Certificate", required: true, hint: "Certificate of Incorporation (COI) issued by MCA" },
  { key: "moa", label: "Memorandum of Association (MOA)", required: true, hint: "Signed MOA registered with the Registrar of Companies" },
  { key: "aoa", label: "Articles of Association (AOA)", required: true, hint: "Signed AOA registered with the Registrar of Companies" },
  { key: "company_pan", label: "Company PAN Card", required: true, hint: "PAN card issued in the name of the company" },
  { key: "gst_certificate", label: "GST Registration Certificate", required: false, hint: "GST certificate if applicable to your business" },
  { key: "board_resolution", label: "Board Resolution", required: false, hint: "Board resolution for bank account opening or other purposes" },
  { key: "address_proof", label: "Address Proof", required: false, hint: "Utility bill, rent agreement, or NOC from property owner" },
];

const INDIAN_STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
  "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
  "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
  "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
  "Delhi", "Jammu and Kashmir", "Ladakh", "Chandigarh", "Puducherry",
];

// ---------------------------------------------------------------------------
// Shared styles
// ---------------------------------------------------------------------------

const inputStyle: React.CSSProperties = {
  width: "100%",
  fontSize: 14,
  padding: "10px 14px",
  borderRadius: 8,
  border: "1px solid var(--color-border, #E5E7EB)",
  background: "var(--color-bg-card)",
  color: "var(--color-text-primary, #111827)",
  outline: "none",
};

const readOnlyInputStyle: React.CSSProperties = {
  ...inputStyle,
  background: "var(--color-bg-secondary, #F9FAFB)",
  color: "var(--color-text-muted, #9CA3AF)",
  cursor: "not-allowed",
};

const labelStyle: React.CSSProperties = {
  display: "block",
  fontSize: 13,
  fontWeight: 600,
  marginBottom: 6,
  color: "var(--color-text-primary, #111827)",
};

const hintStyle: React.CSSProperties = {
  fontSize: 11,
  color: "var(--color-text-secondary, #6B7280)",
  marginTop: 4,
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CompanyInfoPage() {
  const { user } = useAuth();
  const { selectedCompany, refreshCompanies } = useCompany();

  const [activeTab, setActiveTab] = useState<"info" | "documents">("info");

  // Business info form state
  const [form, setForm] = useState({
    business_description: "",
    address_line_1: "",
    address_line_2: "",
    city: "",
    pincode: "",
    district: "",
    authorized_capital: 0,
  });
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // KYB documents state
  const [documents, setDocuments] = useState<any[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [uploadingDoc, setUploadingDoc] = useState<string | null>(null);
  const [uploadMsg, setUploadMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const fileInputRefs = useRef<Record<string, HTMLInputElement | null>>({});

  // Load company data into form
  useEffect(() => {
    if (!selectedCompany) return;
    const data = selectedCompany.data || {};
    setForm({
      business_description: data.business_description || "",
      address_line_1: data.address_line_1 || "",
      address_line_2: data.address_line_2 || "",
      city: data.city || "",
      pincode: data.pincode || "",
      district: data.district || "",
      authorized_capital: selectedCompany.authorized_capital || 0,
    });
  }, [selectedCompany]);

  // Fetch uploaded documents
  const fetchDocuments = useCallback(async () => {
    if (!selectedCompany) return;
    setLoadingDocs(true);
    try {
      const docs = await getCompanyDocuments(selectedCompany.id);
      setDocuments(Array.isArray(docs) ? docs : docs?.documents || []);
    } catch {
      setDocuments([]);
    } finally {
      setLoadingDocs(false);
    }
  }, [selectedCompany]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  // Check if a KYB doc type has been uploaded
  const getDocByType = (docType: string) =>
    documents.find((d: any) => d.doc_type === docType);

  const uploadedCount = KYB_DOCUMENTS.filter((d) => getDocByType(d.key)).length;

  // Handle business info save
  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCompany) return;
    setSaving(true);
    setSaveMsg(null);
    try {
      await updateCompanyInfo(selectedCompany.id, {
        authorized_capital: form.authorized_capital,
        data: {
          ...selectedCompany.data,
          business_description: form.business_description,
          address_line_1: form.address_line_1,
          address_line_2: form.address_line_2,
          city: form.city,
          pincode: form.pincode,
          district: form.district,
        },
      });
      await refreshCompanies();
      setSaveMsg({ type: "success", text: "Company information updated successfully." });
    } catch (err: any) {
      setSaveMsg({ type: "error", text: err?.message || "Failed to save. Please try again." });
    } finally {
      setSaving(false);
    }
  };

  // Handle document upload
  const handleUpload = async (docType: string, file: File) => {
    if (!selectedCompany) return;
    setUploadingDoc(docType);
    setUploadMsg(null);
    try {
      await uploadDocument(selectedCompany.id, docType, file);
      await fetchDocuments();
      setUploadMsg({ type: "success", text: `${KYB_DOCUMENTS.find((d) => d.key === docType)?.label} uploaded successfully.` });
    } catch (err: any) {
      setUploadMsg({ type: "error", text: err?.message || "Upload failed. Please try again." });
    } finally {
      setUploadingDoc(null);
    }
  };

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  if (!selectedCompany) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-16 text-center">
        <div className="glass-card p-12">
          <svg className="w-12 h-12 mx-auto mb-4 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21m-3.75 3H21m-3.75 3H21" />
          </svg>
          <h2 className="text-lg font-semibold mb-2" style={{ color: "var(--color-text-primary)" }}>
            No company selected
          </h2>
          <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
            Select a company from the sidebar to view and manage its details.
          </p>
        </div>
      </div>
    );
  }

  const companyName = selectedCompany.approved_name || selectedCompany.proposed_names?.[0] || "Unnamed Company";
  const entityLabel = selectedCompany.entity_type?.replace(/_/g, " ") || "—";
  const statusLabel = selectedCompany.status?.replace(/_/g, " ") || "—";

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      {/* Page Header */}
      <div style={{ marginBottom: 32 }}>
        <h1
          className="text-3xl font-bold mb-2"
          style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
        >
          Company Information
        </h1>
        <p
          className="text-sm border-l-2 pl-3"
          style={{ color: "var(--color-text-secondary)", borderColor: "var(--color-accent-purple-light)" }}
        >
          Manage your business details and upload KYB documents for {companyName}.
        </p>
      </div>

      {/* Tab Switcher */}
      <div
        className="flex gap-1 p-1 rounded-lg mb-6"
        style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)" }}
      >
        {[
          { key: "info" as const, label: "Business Details" },
          { key: "documents" as const, label: `KYB Documents (${uploadedCount}/${KYB_DOCUMENTS.length})` },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className="flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors"
            style={{
              background: activeTab === tab.key ? "var(--color-bg-card)" : "transparent",
              color: activeTab === tab.key ? "var(--color-accent-purple-light)" : "var(--color-text-secondary)",
              boxShadow: activeTab === tab.key ? "var(--shadow-card, 0 1px 3px rgba(0,0,0,0.1))" : "none",
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ================================================================== */}
      {/* TAB: Business Details                                              */}
      {/* ================================================================== */}
      {activeTab === "info" && (
        <form onSubmit={handleSave}>
          {/* Read-only identifiers card */}
          <div
            className="glass-card p-6 mb-6"
            style={{ border: "1px solid var(--color-border)" }}
          >
            <h2
              className="text-sm font-semibold mb-4 uppercase tracking-wider"
              style={{ color: "var(--color-text-muted)" }}
            >
              Company Identifiers
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label style={labelStyle}>Company Name</label>
                <input type="text" value={companyName} readOnly style={readOnlyInputStyle} />
              </div>
              <div>
                <label style={labelStyle}>Entity Type</label>
                <input type="text" value={entityLabel} readOnly style={{ ...readOnlyInputStyle, textTransform: "capitalize" }} />
              </div>
              <div>
                <label style={labelStyle}>Status</label>
                <input type="text" value={statusLabel} readOnly style={{ ...readOnlyInputStyle, textTransform: "capitalize" }} />
              </div>
              <div>
                <label style={labelStyle}>State of Registration</label>
                <input type="text" value={selectedCompany.state || "—"} readOnly style={readOnlyInputStyle} />
              </div>
              {selectedCompany.cin && (
                <div>
                  <label style={labelStyle}>CIN</label>
                  <input type="text" value={selectedCompany.cin} readOnly style={{ ...readOnlyInputStyle, fontFamily: "monospace" }} />
                </div>
              )}
              {selectedCompany.pan && (
                <div>
                  <label style={labelStyle}>PAN</label>
                  <input type="text" value={selectedCompany.pan} readOnly style={{ ...readOnlyInputStyle, fontFamily: "monospace" }} />
                </div>
              )}
              {selectedCompany.tan && (
                <div>
                  <label style={labelStyle}>TAN</label>
                  <input type="text" value={selectedCompany.tan} readOnly style={{ ...readOnlyInputStyle, fontFamily: "monospace" }} />
                </div>
              )}
            </div>
          </div>

          {/* Editable details card */}
          <div
            className="glass-card p-6 mb-6"
            style={{ border: "1px solid var(--color-border)" }}
          >
            <h2
              className="text-sm font-semibold mb-4 uppercase tracking-wider"
              style={{ color: "var(--color-text-muted)" }}
            >
              Business Details
            </h2>
            <div className="flex flex-col gap-5">
              <div>
                <label style={labelStyle}>Business Description</label>
                <textarea
                  value={form.business_description}
                  onChange={(e) => setForm((p) => ({ ...p, business_description: e.target.value }))}
                  placeholder="Brief description of your business activities..."
                  rows={3}
                  style={{ ...inputStyle, resize: "vertical" }}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label style={labelStyle}>Authorized Capital (Rs)</label>
                  <input
                    type="number"
                    value={form.authorized_capital}
                    onChange={(e) => setForm((p) => ({ ...p, authorized_capital: parseInt(e.target.value) || 0 }))}
                    style={inputStyle}
                    min={0}
                  />
                </div>
              </div>

              <div>
                <label style={labelStyle}>Address Line 1</label>
                <input
                  type="text"
                  value={form.address_line_1}
                  onChange={(e) => setForm((p) => ({ ...p, address_line_1: e.target.value }))}
                  placeholder="e.g. C/O Prema Kailas"
                  style={inputStyle}
                />
              </div>

              <div>
                <label style={labelStyle}>Address Line 2</label>
                <input
                  type="text"
                  value={form.address_line_2}
                  onChange={(e) => setForm((p) => ({ ...p, address_line_2: e.target.value }))}
                  placeholder="e.g. Thannirankadu, Mathur"
                  style={inputStyle}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label style={labelStyle}>City</label>
                  <input
                    type="text"
                    value={form.city}
                    onChange={(e) => setForm((p) => ({ ...p, city: e.target.value }))}
                    placeholder="e.g. Alathur"
                    style={inputStyle}
                  />
                </div>
                <div>
                  <label style={labelStyle}>Pincode</label>
                  <input
                    type="text"
                    value={form.pincode}
                    onChange={(e) => setForm((p) => ({ ...p, pincode: e.target.value }))}
                    placeholder="e.g. 678571"
                    style={inputStyle}
                    maxLength={6}
                  />
                </div>
                <div>
                  <label style={labelStyle}>District</label>
                  <input
                    type="text"
                    value={form.district}
                    onChange={(e) => setForm((p) => ({ ...p, district: e.target.value }))}
                    placeholder="e.g. Palakkad"
                    style={inputStyle}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Save message */}
          {saveMsg && (
            <div
              className="p-3 rounded-lg mb-4 text-sm"
              style={{
                background: saveMsg.type === "success" ? "var(--color-success-light, #ECFDF5)" : "var(--color-error-light, #FEF2F2)",
                color: saveMsg.type === "success" ? "var(--color-accent-emerald-light, #059669)" : "var(--color-error, #DC2626)",
                border: `1px solid ${saveMsg.type === "success" ? "var(--color-accent-emerald-light, #059669)" : "var(--color-error, #DC2626)"}`,
                borderColor: saveMsg.type === "success"
                  ? "color-mix(in srgb, var(--color-accent-emerald-light, #059669) 25%, transparent)"
                  : "color-mix(in srgb, var(--color-error, #DC2626) 25%, transparent)",
              }}
            >
              {saveMsg.text}
            </div>
          )}

          {/* Save button */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-2.5 rounded-lg text-sm font-semibold text-white transition-colors"
              style={{
                background: saving ? "var(--color-accent-purple)" : "var(--color-accent-purple-light)",
                cursor: saving ? "not-allowed" : "pointer",
                border: "none",
              }}
            >
              {saving ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </form>
      )}

      {/* ================================================================== */}
      {/* TAB: KYB Documents                                                 */}
      {/* ================================================================== */}
      {activeTab === "documents" && (
        <div>
          {/* Progress bar */}
          <div className="glass-card p-5 mb-6" style={{ border: "1px solid var(--color-border)" }}>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold" style={{ color: "var(--color-text-primary)" }}>
                KYB Completion
              </h2>
              <span className="text-sm font-medium" style={{ color: "var(--color-accent-purple-light)" }}>
                {uploadedCount} of {KYB_DOCUMENTS.length} uploaded
              </span>
            </div>
            <div
              className="w-full h-2 rounded-full overflow-hidden"
              style={{ background: "var(--color-bg-secondary, #F3F4F6)" }}
            >
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${(uploadedCount / KYB_DOCUMENTS.length) * 100}%`,
                  background: uploadedCount === KYB_DOCUMENTS.length
                    ? "var(--color-accent-emerald-light, #10B981)"
                    : "var(--color-accent-purple-light, #8B5CF6)",
                }}
              />
            </div>
          </div>

          {/* Upload message */}
          {uploadMsg && (
            <div
              className="p-3 rounded-lg mb-4 text-sm"
              style={{
                background: uploadMsg.type === "success" ? "var(--color-success-light, #ECFDF5)" : "var(--color-error-light, #FEF2F2)",
                color: uploadMsg.type === "success" ? "var(--color-accent-emerald-light, #059669)" : "var(--color-error, #DC2626)",
                borderColor: uploadMsg.type === "success"
                  ? "color-mix(in srgb, var(--color-accent-emerald-light, #059669) 25%, transparent)"
                  : "color-mix(in srgb, var(--color-error, #DC2626) 25%, transparent)",
                border: "1px solid",
              }}
            >
              {uploadMsg.text}
            </div>
          )}

          {/* Document cards grid */}
          {loadingDocs ? (
            <div className="flex items-center justify-center py-16">
              <div
                className="animate-spin rounded-full h-8 w-8 border-b-2"
                style={{ borderColor: "var(--color-accent-purple-light)" }}
              />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {KYB_DOCUMENTS.map((doc) => {
                const uploaded = getDocByType(doc.key);
                const isUploading = uploadingDoc === doc.key;

                return (
                  <div
                    key={doc.key}
                    className="glass-card p-5 transition-colors"
                    style={{
                      border: `1px solid ${uploaded ? "var(--color-accent-emerald-light, #10B981)" : "var(--color-border)"}`,
                    }}
                  >
                    {/* Header row */}
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="text-sm font-semibold truncate" style={{ color: "var(--color-text-primary)" }}>
                            {doc.label}
                          </h3>
                          {doc.required && (
                            <span
                              className="text-[10px] font-medium px-1.5 py-0.5 rounded"
                              style={{
                                background: "var(--color-error-light, #FEF2F2)",
                                color: "var(--color-error, #DC2626)",
                              }}
                            >
                              Required
                            </span>
                          )}
                        </div>
                        <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                          {doc.hint}
                        </p>
                      </div>

                      {/* Status indicator */}
                      <div className="flex-shrink-0 ml-3">
                        {uploaded ? (
                          <div
                            className="w-8 h-8 rounded-full flex items-center justify-center"
                            style={{ background: "var(--color-success-light, #ECFDF5)" }}
                          >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="var(--color-accent-emerald-light, #10B981)" strokeWidth={2.5}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                            </svg>
                          </div>
                        ) : (
                          <div
                            className="w-8 h-8 rounded-full flex items-center justify-center"
                            style={{ background: "var(--color-bg-secondary, #F3F4F6)" }}
                          >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="var(--color-text-muted, #9CA3AF)" strokeWidth={1.5}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                            </svg>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Uploaded file info */}
                    {uploaded && (
                      <div
                        className="text-xs py-2 px-3 rounded-md mb-3 flex items-center gap-2"
                        style={{ background: "var(--color-bg-secondary, #F3F4F6)", color: "var(--color-text-secondary)" }}
                      >
                        <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                        </svg>
                        <span className="truncate">
                          {uploaded.original_filename || uploaded.filename || doc.key}
                        </span>
                        {uploaded.created_at && (
                          <span className="flex-shrink-0 ml-auto" style={{ color: "var(--color-text-muted)" }}>
                            {new Date(uploaded.created_at).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })}
                          </span>
                        )}
                      </div>
                    )}

                    {/* Upload / Re-upload button */}
                    <input
                      ref={(el) => { fileInputRefs.current[doc.key] = el; }}
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                      className="hidden"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) handleUpload(doc.key, file);
                        e.target.value = "";
                      }}
                    />
                    <button
                      onClick={() => fileInputRefs.current[doc.key]?.click()}
                      disabled={isUploading}
                      className="w-full py-2 rounded-lg text-xs font-medium transition-colors"
                      style={{
                        border: "1px solid var(--color-border)",
                        background: isUploading ? "var(--color-bg-secondary)" : "var(--color-bg-card)",
                        color: isUploading ? "var(--color-text-muted)" : "var(--color-accent-purple-light)",
                        cursor: isUploading ? "not-allowed" : "pointer",
                      }}
                    >
                      {isUploading
                        ? "Uploading..."
                        : uploaded
                          ? "Re-upload"
                          : "Upload Document"}
                    </button>
                  </div>
                );
              })}
            </div>
          )}

          {/* Info card */}
          <div
            className="mt-6 p-4 rounded-xl"
            style={{
              background: "var(--color-purple-bg)",
              border: "1px solid var(--color-accent-purple-light)",
            }}
          >
            <h3 className="text-sm font-semibold mb-2" style={{ color: "var(--color-text-primary)" }}>
              Why upload these documents?
            </h3>
            <ul
              className="text-xs leading-relaxed pl-4 m-0"
              style={{ color: "var(--color-text-secondary)", listStyleType: "disc" }}
            >
              <li>Completes your KYB (Know Your Business) verification</li>
              <li>Required for compliance tracking and regulatory filings</li>
              <li>Securely stored and accessible in your data room</li>
              <li>Shared with investors and advisors when needed</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
