"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { createDraftCompany } from "@/lib/api";
import { useCompany } from "@/lib/company-context";

const ENTITY_OPTIONS = [
  { value: "private_limited", label: "Private Limited Company" },
  { value: "opc", label: "One Person Company (OPC)" },
  { value: "llp", label: "Limited Liability Partnership (LLP)" },
  { value: "section_8", label: "Section 8 Company" },
  { value: "partnership", label: "Partnership Firm" },
  { value: "sole_proprietorship", label: "Sole Proprietorship" },
  { value: "public_limited", label: "Public Limited Company" },
];

const INDIAN_STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
  "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
  "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
  "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
  "Delhi", "Jammu and Kashmir", "Ladakh", "Chandigarh", "Puducherry",
];

export default function ConnectCompanyPage() {
  const router = useRouter();
  const { user } = useAuth();
  const { refreshCompanies } = useCompany();

  const [form, setForm] = useState({
    company_name: "",
    cin: "",
    entity_type: "private_limited",
    state: "Karnataka",
    authorized_capital: 100000,
    num_directors: 2,
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const update = (field: string, value: string | number) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.company_name.trim()) {
      setError("Company name is required.");
      return;
    }
    setError("");
    setSubmitting(true);

    try {
      await createDraftCompany({
        entity_type: form.entity_type,
        plan_tier: "launch",
        state: form.state,
        authorized_capital: form.authorized_capital,
        num_directors: form.num_directors,
        pricing_snapshot: {
          connected_existing: true,
          company_name: form.company_name.trim(),
          cin: form.cin.trim() || null,
        },
      });
      await refreshCompanies();
      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.message || "Failed to connect company. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const inputStyle: React.CSSProperties = {
    width: "100%",
    fontSize: 14,
    padding: "10px 14px",
    borderRadius: 8,
    border: "1px solid var(--color-border, #E5E7EB)",
    background: "#fff",
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

  return (
    <div style={{ maxWidth: 640, margin: "0 auto", padding: "32px 24px" }}>
      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <h1
          style={{
            fontSize: 28,
            fontWeight: 700,
            marginBottom: 6,
            fontFamily: "var(--font-display)",
            color: "var(--color-text-primary, #111827)",
          }}
        >
          Connect an Existing Company
        </h1>
        <p
          style={{
            fontSize: 13,
            color: "var(--color-text-secondary, #6B7280)",
            borderLeft: "2px solid #8B5CF6",
            paddingLeft: 12,
          }}
        >
          Already have an incorporated company? Add it to Anvils to manage
          compliance, cap table, ESOP, and more.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit}>
        <div
          style={{
            background: "#fff",
            border: "1px solid var(--color-border, #E5E7EB)",
            borderRadius: 12,
            padding: 24,
            display: "flex",
            flexDirection: "column",
            gap: 20,
          }}
        >
          {/* Company Name */}
          <div>
            <label style={labelStyle}>Company Name *</label>
            <input
              type="text"
              value={form.company_name}
              onChange={(e) => update("company_name", e.target.value)}
              placeholder="e.g. Acme Technologies Private Limited"
              style={inputStyle}
              required
            />
          </div>

          {/* CIN */}
          <div>
            <label style={labelStyle}>CIN (Corporate Identification Number)</label>
            <input
              type="text"
              value={form.cin}
              onChange={(e) => update("cin", e.target.value.toUpperCase())}
              placeholder="e.g. U72900KA2025PTC123456"
              style={inputStyle}
              maxLength={21}
            />
            <p style={hintStyle}>
              Optional. You can find this on your Certificate of Incorporation or
              the MCA portal.
            </p>
          </div>

          {/* Entity Type */}
          <div>
            <label style={labelStyle}>Entity Type *</label>
            <select
              value={form.entity_type}
              onChange={(e) => update("entity_type", e.target.value)}
              style={inputStyle}
              required
            >
              {ENTITY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* State */}
          <div>
            <label style={labelStyle}>State of Registration *</label>
            <select
              value={form.state}
              onChange={(e) => update("state", e.target.value)}
              style={inputStyle}
              required
            >
              {INDIAN_STATES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>

          {/* Two columns: Capital + Directors */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <div>
              <label style={labelStyle}>Authorized Capital (Rs)</label>
              <input
                type="number"
                value={form.authorized_capital}
                onChange={(e) =>
                  update("authorized_capital", parseInt(e.target.value) || 0)
                }
                style={inputStyle}
                min={0}
              />
            </div>
            <div>
              <label style={labelStyle}>Number of Directors</label>
              <input
                type="number"
                value={form.num_directors}
                onChange={(e) =>
                  update("num_directors", parseInt(e.target.value) || 1)
                }
                style={inputStyle}
                min={1}
                max={15}
              />
            </div>
          </div>

          {/* Error */}
          {error && (
            <div
              style={{
                fontSize: 13,
                color: "#DC2626",
                background: "#FEF2F2",
                border: "1px solid #FECACA",
                borderRadius: 8,
                padding: "10px 14px",
              }}
            >
              {error}
            </div>
          )}

          {/* Actions */}
          <div
            style={{
              display: "flex",
              justifyContent: "flex-end",
              gap: 12,
              paddingTop: 8,
            }}
          >
            <button
              type="button"
              onClick={() => router.push("/dashboard")}
              style={{
                fontSize: 13,
                fontWeight: 600,
                padding: "10px 20px",
                borderRadius: 8,
                border: "1px solid var(--color-border, #E5E7EB)",
                background: "#fff",
                color: "var(--color-text-primary, #111827)",
                cursor: "pointer",
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              style={{
                fontSize: 13,
                fontWeight: 600,
                padding: "10px 24px",
                borderRadius: 8,
                border: "none",
                background: submitting ? "#C4B5FD" : "#8B5CF6",
                color: "#fff",
                cursor: submitting ? "not-allowed" : "pointer",
              }}
            >
              {submitting ? "Connecting..." : "Connect Company"}
            </button>
          </div>
        </div>
      </form>

      {/* Info card */}
      <div
        style={{
          marginTop: 24,
          background: "rgba(139, 92, 246, 0.05)",
          border: "1px solid rgba(139, 92, 246, 0.15)",
          borderRadius: 12,
          padding: "16px 20px",
        }}
      >
        <h3
          style={{
            fontSize: 13,
            fontWeight: 600,
            marginBottom: 8,
            color: "var(--color-text-primary, #111827)",
          }}
        >
          What happens next?
        </h3>
        <ul
          style={{
            fontSize: 12,
            color: "var(--color-text-secondary, #6B7280)",
            lineHeight: 1.8,
            paddingLeft: 18,
            margin: 0,
          }}
        >
          <li>Your company will appear on the dashboard immediately</li>
          <li>Set up your cap table, add directors & shareholders</li>
          <li>Track compliance deadlines and filings automatically</li>
          <li>Explore ESOP, fundraising, and governance tools</li>
        </ul>
      </div>
    </div>
  );
}
