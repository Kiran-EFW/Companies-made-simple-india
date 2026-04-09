"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/lib/auth-context";
import { useCompany } from "@/lib/company-context";
import {
  getLetterheadDesigns,
  getLetterheadSettings,
  updateLetterheadSettings,
  previewLetterhead,
} from "@/lib/api";

// ---------------------------------------------------------------------------
// Design definitions
// ---------------------------------------------------------------------------

const DESIGN_OPTIONS: {
  key: string;
  label: string;
  description: string;
}[] = [
  { key: "classic", label: "Classic", description: "Centered header, serif typography, traditional Indian corporate style" },
  { key: "modern", label: "Modern", description: "Left-aligned with accent bar, contemporary clean look" },
  { key: "formal", label: "Formal", description: "Box-framed header, tabular layout, institutional" },
  { key: "minimal", label: "Minimal", description: "Lightweight text header, subtle separator, tech/startup" },
  { key: "executive", label: "Executive", description: "Premium dual-tone header, suited for board documents" },
];

// ---------------------------------------------------------------------------
// Shared styles (matching company-info page)
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
// Design icon SVGs (simple abstract representations)
// ---------------------------------------------------------------------------

function DesignIcon({ design, color }: { design: string; color: string }) {
  const base: React.CSSProperties = { width: 48, height: 56, borderRadius: 4, border: "1px solid var(--color-border, #E5E7EB)", background: "white", position: "relative", overflow: "hidden" };

  if (design === "classic") {
    return (
      <div style={base}>
        <div style={{ height: 14, background: color, opacity: 0.15 }} />
        <div style={{ margin: "4px auto", width: 20, height: 2, background: color, borderRadius: 1 }} />
        <div style={{ margin: "2px auto", width: 28, height: 1, background: "#D1D5DB", borderRadius: 1 }} />
        <div style={{ margin: "2px auto", width: 24, height: 1, background: "#D1D5DB", borderRadius: 1 }} />
      </div>
    );
  }

  if (design === "modern") {
    return (
      <div style={base}>
        <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: 4, background: color }} />
        <div style={{ marginLeft: 8, marginTop: 6, width: 20, height: 2, background: color, borderRadius: 1 }} />
        <div style={{ marginLeft: 8, marginTop: 3, width: 28, height: 1, background: "#D1D5DB", borderRadius: 1 }} />
        <div style={{ marginLeft: 8, marginTop: 2, width: 24, height: 1, background: "#D1D5DB", borderRadius: 1 }} />
      </div>
    );
  }

  if (design === "formal") {
    return (
      <div style={base}>
        <div style={{ margin: 4, border: `1px solid ${color}`, borderRadius: 2, padding: 3 }}>
          <div style={{ width: 16, height: 2, background: color, borderRadius: 1, marginBottom: 2 }} />
          <div style={{ width: 28, height: 1, background: "#D1D5DB", borderRadius: 1, marginBottom: 1 }} />
          <div style={{ width: 24, height: 1, background: "#D1D5DB", borderRadius: 1 }} />
        </div>
      </div>
    );
  }

  if (design === "minimal") {
    return (
      <div style={base}>
        <div style={{ marginLeft: 6, marginTop: 8, width: 22, height: 2, background: color, borderRadius: 1, opacity: 0.7 }} />
        <div style={{ margin: "4px 6px", height: 1, background: "#E5E7EB" }} />
      </div>
    );
  }

  // executive
  return (
    <div style={base}>
      <div style={{ height: 8, background: color }} />
      <div style={{ height: 4, background: color, opacity: 0.3 }} />
      <div style={{ marginLeft: 6, marginTop: 4, width: 20, height: 2, background: color, borderRadius: 1 }} />
      <div style={{ marginLeft: 6, marginTop: 2, width: 28, height: 1, background: "#D1D5DB", borderRadius: 1 }} />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function LetterheadSettingsPage() {
  const { user } = useAuth();
  const { selectedCompany } = useCompany();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [previewing, setPreviewing] = useState(false);
  const [saveMsg, setSaveMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Form state
  const [form, setForm] = useState({
    design: "classic",
    accent_color: "#1a3c6e",
    tagline: "",
    show_pan_tan: true,
    registered_office: "",
    phone: "",
    email: "",
    website: "",
  });

  // Fetch existing settings
  const fetchSettings = useCallback(async () => {
    if (!selectedCompany) return;
    setLoading(true);
    try {
      const settings = await getLetterheadSettings(selectedCompany.id);
      if (settings) {
        setForm((prev) => ({
          ...prev,
          design: settings.design || prev.design,
          accent_color: settings.accent_color || prev.accent_color,
          tagline: settings.tagline || "",
          show_pan_tan: settings.show_pan_tan !== undefined ? settings.show_pan_tan : prev.show_pan_tan,
          registered_office: settings.registered_office || "",
          phone: settings.phone || "",
          email: settings.email || "",
          website: settings.website || "",
        }));
      }
    } catch {
      // Settings may not exist yet -- use defaults
    } finally {
      setLoading(false);
    }
  }, [selectedCompany]);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  // Handle save
  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCompany) return;
    setSaving(true);
    setSaveMsg(null);
    try {
      await updateLetterheadSettings(selectedCompany.id, {
        design: form.design,
        accent_color: form.accent_color,
        tagline: form.tagline,
        show_pan_tan: form.show_pan_tan,
        registered_office: form.registered_office,
        phone: form.phone,
        email: form.email,
        website: form.website,
      });
      setSaveMsg({ type: "success", text: "Letterhead settings saved successfully." });
    } catch (err: any) {
      setSaveMsg({ type: "error", text: err?.message || "Failed to save settings. Please try again." });
    } finally {
      setSaving(false);
    }
  };

  // Handle preview
  const handlePreview = async () => {
    if (!selectedCompany) return;
    setPreviewing(true);
    try {
      const response = await previewLetterhead(selectedCompany.id, {
        design: form.design,
        accent_color: form.accent_color,
        tagline: form.tagline,
        show_pan_tan: form.show_pan_tan,
      });
      const html = await response.text();
      const newWindow = window.open("", "_blank");
      if (newWindow) {
        newWindow.document.write(html);
        newWindow.document.close();
      }
    } catch (err: any) {
      setSaveMsg({ type: "error", text: err?.message || "Failed to generate preview." });
    } finally {
      setPreviewing(false);
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
            Select a company from the sidebar to manage letterhead settings.
          </p>
        </div>
      </div>
    );
  }

  const companyName = selectedCompany.approved_name || selectedCompany.proposed_names?.[0] || "Unnamed Company";

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      {/* Page Header */}
      <div style={{ marginBottom: 32 }}>
        <h1
          className="text-3xl font-bold mb-2"
          style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
        >
          Letterhead Settings
        </h1>
        <p
          className="text-sm border-l-2 pl-3"
          style={{ color: "var(--color-text-secondary)", borderColor: "var(--color-accent-purple-light)" }}
        >
          Customize the letterhead design and details for {companyName}.
        </p>
      </div>

      {/* Loading state */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div
            className="animate-spin rounded-full h-8 w-8 border-b-2"
            style={{ borderColor: "var(--color-accent-purple-light)" }}
          />
        </div>
      ) : (
        <form onSubmit={handleSave}>
          {/* ================================================================ */}
          {/* Design Selection                                                 */}
          {/* ================================================================ */}
          <div
            className="glass-card p-6 mb-6"
            style={{ border: "1px solid var(--color-border)" }}
          >
            <h2
              className="text-sm font-semibold mb-4 uppercase tracking-wider"
              style={{ color: "var(--color-text-muted)" }}
            >
              Choose Design
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {DESIGN_OPTIONS.map((d) => {
                const isSelected = form.design === d.key;
                return (
                  <button
                    key={d.key}
                    type="button"
                    onClick={() => setForm((prev) => ({ ...prev, design: d.key }))}
                    style={{
                      display: "flex",
                      alignItems: "flex-start",
                      gap: 12,
                      padding: 16,
                      borderRadius: 12,
                      border: isSelected
                        ? "2px solid var(--color-accent-purple-light, #8B5CF6)"
                        : "1px solid var(--color-border, #E5E7EB)",
                      background: isSelected
                        ? "var(--color-purple-bg, rgba(139,92,246,0.06))"
                        : "var(--color-bg-card)",
                      cursor: "pointer",
                      textAlign: "left",
                      transition: "all 0.15s ease",
                    }}
                  >
                    <div style={{ flexShrink: 0 }}>
                      <DesignIcon design={d.key} color={form.accent_color} />
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                        <span
                          style={{
                            fontSize: 14,
                            fontWeight: 600,
                            color: isSelected
                              ? "var(--color-accent-purple-light, #8B5CF6)"
                              : "var(--color-text-primary, #111827)",
                          }}
                        >
                          {d.label}
                        </span>
                        {isSelected && (
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent-purple-light, #8B5CF6)" strokeWidth={2.5}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                          </svg>
                        )}
                      </div>
                      <p
                        style={{
                          fontSize: 12,
                          color: "var(--color-text-secondary, #6B7280)",
                          lineHeight: 1.4,
                          margin: 0,
                        }}
                      >
                        {d.description}
                      </p>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* ================================================================ */}
          {/* Customization                                                    */}
          {/* ================================================================ */}
          <div
            className="glass-card p-6 mb-6"
            style={{ border: "1px solid var(--color-border)" }}
          >
            <h2
              className="text-sm font-semibold mb-4 uppercase tracking-wider"
              style={{ color: "var(--color-text-muted)" }}
            >
              Customization
            </h2>
            <div className="flex flex-col gap-5">
              {/* Accent color */}
              <div>
                <label style={labelStyle}>Accent Color</label>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <input
                    type="color"
                    value={form.accent_color}
                    onChange={(e) => setForm((prev) => ({ ...prev, accent_color: e.target.value }))}
                    style={{
                      width: 44,
                      height: 44,
                      padding: 2,
                      borderRadius: 8,
                      border: "1px solid var(--color-border, #E5E7EB)",
                      background: "var(--color-bg-card)",
                      cursor: "pointer",
                    }}
                  />
                  <input
                    type="text"
                    value={form.accent_color}
                    onChange={(e) => setForm((prev) => ({ ...prev, accent_color: e.target.value }))}
                    placeholder="#1a3c6e"
                    style={{ ...inputStyle, maxWidth: 140, fontFamily: "monospace" }}
                  />
                  <span style={hintStyle}>Used for headers, borders, and accents in the letterhead</span>
                </div>
              </div>

              {/* Tagline */}
              <div>
                <label style={labelStyle}>Tagline</label>
                <input
                  type="text"
                  value={form.tagline}
                  onChange={(e) => setForm((prev) => ({ ...prev, tagline: e.target.value }))}
                  placeholder="e.g. Innovation Meets Excellence"
                  style={inputStyle}
                />
                <p style={hintStyle}>A short tagline displayed below the company name (optional)</p>
              </div>

              {/* Show PAN/TAN toggle */}
              <div>
                <label style={labelStyle}>Show PAN/TAN on Letterhead</label>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <button
                    type="button"
                    onClick={() => setForm((prev) => ({ ...prev, show_pan_tan: !prev.show_pan_tan }))}
                    style={{
                      width: 48,
                      height: 26,
                      borderRadius: 13,
                      padding: 2,
                      border: "none",
                      cursor: "pointer",
                      background: form.show_pan_tan
                        ? "var(--color-accent-purple-light, #8B5CF6)"
                        : "var(--color-border, #D1D5DB)",
                      transition: "background 0.2s ease",
                      display: "flex",
                      alignItems: "center",
                    }}
                  >
                    <div
                      style={{
                        width: 22,
                        height: 22,
                        borderRadius: "50%",
                        background: "white",
                        boxShadow: "0 1px 3px rgba(0,0,0,0.15)",
                        transition: "transform 0.2s ease",
                        transform: form.show_pan_tan ? "translateX(22px)" : "translateX(0)",
                      }}
                    />
                  </button>
                  <span style={{ fontSize: 13, color: "var(--color-text-secondary, #6B7280)" }}>
                    {form.show_pan_tan ? "Visible" : "Hidden"}
                  </span>
                </div>
                <p style={hintStyle}>Display PAN and TAN numbers in the letterhead footer</p>
              </div>
            </div>
          </div>

          {/* ================================================================ */}
          {/* Company Details                                                  */}
          {/* ================================================================ */}
          <div
            className="glass-card p-6 mb-6"
            style={{ border: "1px solid var(--color-border)" }}
          >
            <h2
              className="text-sm font-semibold mb-4 uppercase tracking-wider"
              style={{ color: "var(--color-text-muted)" }}
            >
              Company Details
            </h2>
            <div className="flex flex-col gap-5">
              <div>
                <label style={labelStyle}>Registered Office Address</label>
                <textarea
                  value={form.registered_office}
                  onChange={(e) => setForm((prev) => ({ ...prev, registered_office: e.target.value }))}
                  placeholder="Full registered office address as per MCA records..."
                  rows={3}
                  style={{ ...inputStyle, resize: "vertical" }}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label style={labelStyle}>Phone</label>
                  <input
                    type="text"
                    value={form.phone}
                    onChange={(e) => setForm((prev) => ({ ...prev, phone: e.target.value }))}
                    placeholder="e.g. +91 98765 43210"
                    style={inputStyle}
                  />
                </div>
                <div>
                  <label style={labelStyle}>Email</label>
                  <input
                    type="email"
                    value={form.email}
                    onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))}
                    placeholder="e.g. info@company.com"
                    style={inputStyle}
                  />
                </div>
              </div>

              <div>
                <label style={labelStyle}>Website</label>
                <input
                  type="text"
                  value={form.website}
                  onChange={(e) => setForm((prev) => ({ ...prev, website: e.target.value }))}
                  placeholder="e.g. www.company.com"
                  style={inputStyle}
                />
              </div>
            </div>
          </div>

          {/* Save / status message */}
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

          {/* Action buttons */}
          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={handlePreview}
              disabled={previewing}
              className="px-6 py-2.5 rounded-lg text-sm font-semibold transition-colors"
              style={{
                background: "var(--color-bg-card)",
                color: previewing ? "var(--color-text-muted)" : "var(--color-accent-purple-light)",
                border: "1px solid var(--color-border)",
                cursor: previewing ? "not-allowed" : "pointer",
              }}
            >
              {previewing ? "Generating..." : "Preview Letterhead"}
            </button>
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
    </div>
  );
}
