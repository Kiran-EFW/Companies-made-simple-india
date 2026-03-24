"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { registerAsPartner } from "@/lib/api";

// ---------------------------------------------------------------------------
// Theme constants
// ---------------------------------------------------------------------------
const T = {
  accent: "#0d9488",
  accentLight: "#14b8a6",
  accentBg: "rgba(20, 184, 166, 0.08)",
  textPrimary: "#0f172a",
  textSecondary: "#475569",
  textMuted: "#94a3b8",
  cardBg: "#ffffff",
  cardBorder: "#e2e8f0",
  pageBg: "#f8fafc",
  rose: "#dc2626",
  roseBg: "rgba(220, 38, 38, 0.06)",
  amber: "#d97706",
  amberBg: "rgba(217, 119, 6, 0.06)",
  emerald: "#059669",
  emeraldBg: "rgba(5, 150, 105, 0.06)",
};

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const MEMBERSHIP_TYPES = [
  { value: "CA", label: "Chartered Accountant (CA)" },
  { value: "CS", label: "Company Secretary (CS)" },
  { value: "CMA", label: "Cost & Management Accountant (CMA)" },
];

const SPECIALIZATIONS = [
  { value: "registration", label: "Registration", description: "Company incorporation & registrations" },
  { value: "compliance", label: "Compliance", description: "Annual filings, ROC compliance" },
  { value: "tax", label: "Tax", description: "Income tax, GST, and tax planning" },
  { value: "accounting", label: "Accounting", description: "Bookkeeping, financial statements" },
  { value: "amendments", label: "Amendments", description: "Change in directors, address, etc." },
  { value: "legal", label: "Legal", description: "Legal documentation & advisory" },
];

const INFO_ITEMS = [
  {
    icon: "M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 00.75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 00-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0112 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 01-.673-.38m0 0A2.18 2.18 0 013 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 013.413-.387m7.5 0V5.25A2.25 2.25 0 0013.5 3h-3a2.25 2.25 0 00-2.25 2.25v.894m7.5 0a48.667 48.667 0 00-7.5 0M12 12.75h.008v.008H12v-.008z",
    title: "Receive Service Assignments",
    description: "Get matched with clients who need your expertise. Accept assignments from the Anvils marketplace based on your specializations.",
  },
  {
    icon: "M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z",
    title: "80/20 Fee Split",
    description: "You earn 80% of the service fee for every completed assignment. Anvils retains 20% as the platform fee.",
  },
  {
    icon: "M9 14.25l3-3m0 0l3 3m-3-3v8.25M3 16.811V8.69c0-.864.933-1.405 1.683-.977l7.108 4.062a1.125 1.125 0 010 1.953l-7.108 4.062A1.125 1.125 0 013 16.811z",
    title: "TDS at 10% (Section 194J)",
    description: "Tax Deducted at Source is applied at 10% on professional fees under Section 194J of the Income Tax Act. TDS certificates are provided quarterly.",
  },
  {
    icon: "M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z",
    title: "Client Rating System",
    description: "Clients rate your service on a 1-5 star scale. Maintain high ratings to receive priority assignments and build your reputation on the platform.",
  },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function RegisterPartnerPage() {
  const { user, loading: authLoading } = useAuth();

  // Form state
  const [membershipNumber, setMembershipNumber] = useState("");
  const [membershipType, setMembershipType] = useState("CA");
  const [firmName, setFirmName] = useState("");
  const [selectedSpecs, setSelectedSpecs] = useState<string[]>([]);

  // Submission state
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  const toggleSpec = (value: string) => {
    setSelectedSpecs((prev) =>
      prev.includes(value)
        ? prev.filter((s) => s !== value)
        : [...prev, value]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!membershipNumber.trim()) {
      setError("Membership number is required.");
      return;
    }

    setSubmitting(true);

    try {
      await registerAsPartner({
        membership_number: membershipNumber.trim(),
        membership_type: membershipType,
        firm_name: firmName.trim() || undefined,
        specializations: selectedSpecs.length > 0 ? selectedSpecs : undefined,
      });
      setSuccess(true);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Registration failed. You may already be registered as a partner.";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  // Loading state
  if (authLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <div
          className="animate-spin rounded-full h-8 w-8 border-b-2"
          style={{ borderColor: T.accent }}
        />
      </div>
    );
  }

  // Success state
  if (success) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-16 lg:py-20">
        <div
          className="rounded-xl p-8 text-center"
          style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}` }}
        >
          <div
            className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-5"
            style={{ background: T.emeraldBg, color: T.emerald }}
          >
            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2
            className="text-xl font-bold mb-2"
            style={{ fontFamily: "var(--font-display)", color: T.textPrimary }}
          >
            Registration Successful
          </h2>
          <p className="text-sm mb-6" style={{ color: T.textSecondary }}>
            You have been registered as a marketplace partner. You can now receive and manage service assignments from clients.
          </p>
          <Link
            href="/ca/marketplace"
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-medium text-white transition-colors"
            style={{ background: T.accent }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "#0f766e";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = T.accent;
            }}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
            Go to Marketplace
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 lg:py-10">
      {/* ── Page Header ─────────────────────────────────────── */}
      <div className="mb-8">
        <p className="text-sm font-medium mb-1" style={{ color: T.accent }}>
          Marketplace
        </p>
        <h1
          className="text-2xl font-bold"
          style={{ fontFamily: "var(--font-display)", color: T.textPrimary }}
        >
          Register as a Partner
        </h1>
        <p className="text-sm mt-1" style={{ color: T.textSecondary }}>
          Join the Anvils marketplace to receive service assignments and grow your practice.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* ── Registration Form (left column) ──────────────── */}
        <div className="lg:col-span-3">
          <form onSubmit={handleSubmit}>
            <div
              className="rounded-xl p-6"
              style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}` }}
            >
              <h2
                className="text-sm font-semibold mb-5"
                style={{ color: T.textPrimary }}
              >
                Partner Details
              </h2>

              {/* Error banner */}
              {error && (
                <div
                  className="rounded-lg px-4 py-3 mb-5 flex items-start gap-3 text-sm"
                  style={{ background: T.roseBg, border: "1px solid rgba(220,38,38,0.15)" }}
                >
                  <svg
                    className="w-5 h-5 flex-shrink-0 mt-0.5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={1.5}
                    style={{ color: T.rose }}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
                    />
                  </svg>
                  <span style={{ color: T.rose }}>{error}</span>
                </div>
              )}

              {/* Membership Number */}
              <div className="mb-5">
                <label
                  htmlFor="membershipNumber"
                  className="block text-sm font-medium mb-1.5"
                  style={{ color: T.textPrimary }}
                >
                  Membership Number <span style={{ color: T.rose }}>*</span>
                </label>
                <input
                  id="membershipNumber"
                  type="text"
                  value={membershipNumber}
                  onChange={(e) => setMembershipNumber(e.target.value)}
                  placeholder="e.g. 123456"
                  required
                  className="w-full px-3.5 py-2.5 rounded-lg text-sm outline-none transition-shadow"
                  style={{
                    border: `1px solid ${T.cardBorder}`,
                    color: T.textPrimary,
                    background: T.cardBg,
                  }}
                  onFocus={(e) => {
                    e.currentTarget.style.borderColor = T.accent;
                    e.currentTarget.style.boxShadow = `0 0 0 3px rgba(13, 148, 136, 0.15)`;
                  }}
                  onBlur={(e) => {
                    e.currentTarget.style.borderColor = T.cardBorder;
                    e.currentTarget.style.boxShadow = "none";
                  }}
                />
                <p className="text-xs mt-1" style={{ color: T.textMuted }}>
                  Your ICAI / ICSI / ICMAI membership number
                </p>
              </div>

              {/* Membership Type */}
              <div className="mb-5">
                <label
                  htmlFor="membershipType"
                  className="block text-sm font-medium mb-1.5"
                  style={{ color: T.textPrimary }}
                >
                  Membership Type
                </label>
                <select
                  id="membershipType"
                  value={membershipType}
                  onChange={(e) => setMembershipType(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-lg text-sm outline-none transition-shadow appearance-none cursor-pointer"
                  style={{
                    border: `1px solid ${T.cardBorder}`,
                    color: T.textPrimary,
                    background: T.cardBg,
                    backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2394a3b8' stroke-width='1.5'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19.5 8.25l-7.5 7.5-7.5-7.5'/%3E%3C/svg%3E")`,
                    backgroundRepeat: "no-repeat",
                    backgroundPosition: "right 12px center",
                    backgroundSize: "18px",
                    paddingRight: "40px",
                  }}
                  onFocus={(e) => {
                    e.currentTarget.style.borderColor = T.accent;
                    e.currentTarget.style.boxShadow = `0 0 0 3px rgba(13, 148, 136, 0.15)`;
                  }}
                  onBlur={(e) => {
                    e.currentTarget.style.borderColor = T.cardBorder;
                    e.currentTarget.style.boxShadow = "none";
                  }}
                >
                  {MEMBERSHIP_TYPES.map((mt) => (
                    <option key={mt.value} value={mt.value}>
                      {mt.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Firm Name */}
              <div className="mb-6">
                <label
                  htmlFor="firmName"
                  className="block text-sm font-medium mb-1.5"
                  style={{ color: T.textPrimary }}
                >
                  Firm Name{" "}
                  <span className="font-normal" style={{ color: T.textMuted }}>
                    (optional)
                  </span>
                </label>
                <input
                  id="firmName"
                  type="text"
                  value={firmName}
                  onChange={(e) => setFirmName(e.target.value)}
                  placeholder="e.g. ABC & Associates"
                  className="w-full px-3.5 py-2.5 rounded-lg text-sm outline-none transition-shadow"
                  style={{
                    border: `1px solid ${T.cardBorder}`,
                    color: T.textPrimary,
                    background: T.cardBg,
                  }}
                  onFocus={(e) => {
                    e.currentTarget.style.borderColor = T.accent;
                    e.currentTarget.style.boxShadow = `0 0 0 3px rgba(13, 148, 136, 0.15)`;
                  }}
                  onBlur={(e) => {
                    e.currentTarget.style.borderColor = T.cardBorder;
                    e.currentTarget.style.boxShadow = "none";
                  }}
                />
              </div>

              {/* Specializations */}
              <div className="mb-6">
                <label
                  className="block text-sm font-medium mb-1.5"
                  style={{ color: T.textPrimary }}
                >
                  Specializations
                </label>
                <p className="text-xs mb-3" style={{ color: T.textMuted }}>
                  Select the service categories you want to receive assignments for.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {SPECIALIZATIONS.map((spec) => {
                    const isChecked = selectedSpecs.includes(spec.value);
                    return (
                      <label
                        key={spec.value}
                        className="flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-colors"
                        style={{
                          border: `1px solid ${isChecked ? T.accent : T.cardBorder}`,
                          background: isChecked ? T.accentBg : T.cardBg,
                        }}
                        onMouseEnter={(e) => {
                          if (!isChecked) e.currentTarget.style.borderColor = T.textMuted;
                        }}
                        onMouseLeave={(e) => {
                          if (!isChecked) e.currentTarget.style.borderColor = T.cardBorder;
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => toggleSpec(spec.value)}
                          className="mt-0.5 w-4 h-4 rounded border-gray-300 text-teal-600 focus:ring-teal-500/40"
                          style={{ accentColor: T.accent }}
                        />
                        <div className="min-w-0">
                          <div
                            className="text-sm font-medium"
                            style={{ color: T.textPrimary }}
                          >
                            {spec.label}
                          </div>
                          <div
                            className="text-xs mt-0.5"
                            style={{ color: T.textMuted }}
                          >
                            {spec.description}
                          </div>
                        </div>
                      </label>
                    );
                  })}
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={submitting}
                className="w-full flex items-center justify-center gap-2 px-5 py-3 rounded-lg text-sm font-medium text-white transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                style={{ background: submitting ? T.textMuted : T.accent }}
                onMouseEnter={(e) => {
                  if (!submitting) e.currentTarget.style.background = "#0f766e";
                }}
                onMouseLeave={(e) => {
                  if (!submitting) e.currentTarget.style.background = T.accent;
                }}
              >
                {submitting ? (
                  <>
                    <div
                      className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"
                    />
                    Registering...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Register as Partner
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* ── Info Sidebar (right column) ──────────────────── */}
        <div className="lg:col-span-2 space-y-4">
          {/* How it works card */}
          <div
            className="rounded-xl p-5"
            style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}` }}
          >
            <div className="flex items-center gap-2.5 mb-4">
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center"
                style={{ background: T.accentBg, color: T.accent }}
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
                </svg>
              </div>
              <h3
                className="text-sm font-semibold"
                style={{ color: T.textPrimary }}
              >
                How It Works
              </h3>
            </div>

            <div className="space-y-4">
              {INFO_ITEMS.map((item, idx) => (
                <div key={idx} className="flex items-start gap-3">
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                    style={{ background: T.accentBg, color: T.accent }}
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
                    </svg>
                  </div>
                  <div className="min-w-0">
                    <div
                      className="text-sm font-medium"
                      style={{ color: T.textPrimary }}
                    >
                      {item.title}
                    </div>
                    <div
                      className="text-xs mt-0.5 leading-relaxed"
                      style={{ color: T.textSecondary }}
                    >
                      {item.description}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Already registered? */}
          <div
            className="rounded-xl p-5"
            style={{ background: T.accentBg, border: `1px solid rgba(20,184,166,0.15)` }}
          >
            <p className="text-sm font-medium mb-2" style={{ color: T.accent }}>
              Already registered?
            </p>
            <p className="text-xs mb-3" style={{ color: T.textSecondary }}>
              If you have already registered as a partner, head to your marketplace dashboard to view assignments and earnings.
            </p>
            <Link
              href="/ca/marketplace"
              className="inline-flex items-center gap-1.5 text-sm font-medium transition-colors"
              style={{ color: T.accent }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = "#0f766e";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = T.accent;
              }}
            >
              Go to Marketplace
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
              </svg>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
