"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import type { PricingResponse, StateOption } from "@/lib/api";

const ENTITY_TYPES = [
  { value: "private_limited", label: "Private Limited", emoji: "🏢" },
  { value: "opc", label: "OPC", emoji: "👤" },
  { value: "llp", label: "LLP", emoji: "🤝" },
  { value: "section_8", label: "Section 8", emoji: "💚" },
  { value: "sole_proprietorship", label: "Sole Proprietorship", emoji: "📋" },
];

const PLAN_TIERS = [
  {
    value: "launch",
    label: "Launch",
    desc: "AI-guided incorporation + CS review",
  },
  {
    value: "grow",
    label: "Grow",
    desc: "Launch + GST + DPIIT + 90-day compliance",
  },
  {
    value: "scale",
    label: "Scale",
    desc: "Grow + 1-year compliance + dedicated RM",
  },
];

const STATES: StateOption[] = [
  { value: "andhra_pradesh", label: "Andhra Pradesh" },
  { value: "arunachal_pradesh", label: "Arunachal Pradesh" },
  { value: "assam", label: "Assam" },
  { value: "bihar", label: "Bihar" },
  { value: "chhattisgarh", label: "Chhattisgarh" },
  { value: "delhi", label: "Delhi" },
  { value: "goa", label: "Goa" },
  { value: "gujarat", label: "Gujarat" },
  { value: "haryana", label: "Haryana" },
  { value: "himachal_pradesh", label: "Himachal Pradesh" },
  { value: "jammu_kashmir", label: "Jammu & Kashmir" },
  { value: "jharkhand", label: "Jharkhand" },
  { value: "karnataka", label: "Karnataka" },
  { value: "kerala", label: "Kerala" },
  { value: "ladakh", label: "Ladakh" },
  { value: "madhya_pradesh", label: "Madhya Pradesh" },
  { value: "maharashtra", label: "Maharashtra" },
  { value: "manipur", label: "Manipur" },
  { value: "meghalaya", label: "Meghalaya" },
  { value: "mizoram", label: "Mizoram" },
  { value: "nagaland", label: "Nagaland" },
  { value: "odisha", label: "Odisha" },
  { value: "punjab", label: "Punjab" },
  { value: "rajasthan", label: "Rajasthan" },
  { value: "sikkim", label: "Sikkim" },
  { value: "tamil_nadu", label: "Tamil Nadu" },
  { value: "telangana", label: "Telangana" },
  { value: "tripura", label: "Tripura" },
  { value: "uttar_pradesh", label: "Uttar Pradesh" },
  { value: "uttarakhand", label: "Uttarakhand" },
  { value: "west_bengal", label: "West Bengal" },
];

const CAPITAL_OPTIONS = [
  { value: 100000, label: "₹1,00,000" },
  { value: 500000, label: "₹5,00,000" },
  { value: 1000000, label: "₹10,00,000" },
  { value: 2500000, label: "₹25,00,000" },
  { value: 5000000, label: "₹50,00,000" },
];

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

export default function PricingPage() {
  const router = useRouter();
  const [entityType, setEntityType] = useState("private_limited");
  const [planTier, setPlanTier] = useState("launch");
  const [state, setState] = useState("maharashtra");
  const [capital, setCapital] = useState(100000);
  const [numDirectors, setNumDirectors] = useState(2);
  const [hasDSC, setHasDSC] = useState(false);
  const [pricing, setPricing] = useState<PricingResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    calculatePricing();
  }, [entityType, planTier, state, capital, numDirectors, hasDSC]);

  async function calculatePricing() {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/pricing/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          entity_type: entityType,
          plan_tier: planTier,
          state: state,
          authorized_capital: capital,
          num_directors: numDirectors,
          has_existing_dsc: hasDSC,
          dsc_validity_years: 2,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setPricing(data);
      }
    } catch {
      // Silently fail if backend is not running — show UI anyway
    }
    setLoading(false);
  }

  return (
    <div className="glow-bg min-h-screen">
      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-5 max-w-7xl mx-auto">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-2xl">⚡</span>
          <span className="text-xl font-bold" style={{ fontFamily: "var(--font-display)" }}>
            <span className="gradient-text">CMS</span>{" "}
            <span style={{ color: "var(--color-text-secondary)" }}>India</span>
          </span>
        </Link>
        <Link href="/wizard" className="btn-secondary text-sm !py-2 !px-5">
          Not sure? Try our Entity Wizard →
        </Link>
      </nav>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        <h1
          className="text-4xl md:text-5xl font-bold text-center mb-3"
          style={{ fontFamily: "var(--font-display)" }}
        >
          <span className="gradient-text">Transparent</span> Pricing
        </h1>
        <p
          className="text-center mb-12 text-lg"
          style={{ color: "var(--color-text-secondary)" }}
        >
          Real costs, zero surprises. Government fees at exact cost — no markup.
        </p>

        <div className="grid lg:grid-cols-5 gap-8">
          {/* ─── Left: Configuration ─── */}
          <div className="lg:col-span-2 space-y-6">
            {/* Entity Type */}
            <div className="glass-card p-6" style={{ cursor: "default" }}>
              <label className="text-sm font-semibold mb-3 block" style={{ color: "var(--color-text-secondary)" }}>
                Entity Type
              </label>
              <div className="grid grid-cols-2 gap-2">
                {ENTITY_TYPES.map((e) => (
                  <button
                    key={e.value}
                    onClick={() => setEntityType(e.value)}
                    className="p-3 rounded-xl text-left transition-all text-sm"
                    style={{
                      background:
                        entityType === e.value
                          ? "rgba(139, 92, 246, 0.2)"
                          : "rgba(255,255,255,0.03)",
                      border: `1px solid ${entityType === e.value ? "rgba(139, 92, 246, 0.5)" : "var(--color-border)"}`,
                    }}
                  >
                    <span className="text-lg">{e.emoji}</span>
                    <div className="font-medium mt-1">{e.label}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Plan Tier */}
            <div className="glass-card p-6" style={{ cursor: "default" }}>
              <label className="text-sm font-semibold mb-3 block" style={{ color: "var(--color-text-secondary)" }}>
                Plan
              </label>
              <div className="space-y-2">
                {PLAN_TIERS.map((p) => (
                  <button
                    key={p.value}
                    onClick={() => setPlanTier(p.value)}
                    className="w-full p-3 rounded-xl text-left transition-all"
                    style={{
                      background:
                        planTier === p.value
                          ? "rgba(139, 92, 246, 0.2)"
                          : "rgba(255,255,255,0.03)",
                      border: `1px solid ${planTier === p.value ? "rgba(139, 92, 246, 0.5)" : "var(--color-border)"}`,
                    }}
                  >
                    <div className="font-semibold text-sm">{p.label}</div>
                    <div className="text-xs mt-0.5" style={{ color: "var(--color-text-muted)" }}>
                      {p.desc}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* State */}
            <div className="glass-card p-6" style={{ cursor: "default" }}>
              <label className="text-sm font-semibold mb-3 block" style={{ color: "var(--color-text-secondary)" }}>
                State of Registration
              </label>
              <select
                value={state}
                onChange={(e) => setState(e.target.value)}
                className="w-full p-3 rounded-xl text-sm"
                style={{
                  background: "var(--color-bg-card)",
                  border: "1px solid var(--color-border)",
                  color: "var(--color-text-primary)",
                }}
              >
                {STATES.map((s) => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>

            {/* Capital & Directors */}
            <div className="glass-card p-6" style={{ cursor: "default" }}>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-semibold mb-2 block" style={{ color: "var(--color-text-secondary)" }}>
                    {entityType === "llp" ? "Contribution" : "Authorized Capital"}
                  </label>
                  <select
                    value={capital}
                    onChange={(e) => setCapital(Number(e.target.value))}
                    className="w-full p-3 rounded-xl text-sm"
                    style={{
                      background: "var(--color-bg-card)",
                      border: "1px solid var(--color-border)",
                      color: "var(--color-text-primary)",
                    }}
                  >
                    {CAPITAL_OPTIONS.map((c) => (
                      <option key={c.value} value={c.value}>{c.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-sm font-semibold mb-2 block" style={{ color: "var(--color-text-secondary)" }}>
                    {entityType === "llp" ? "Partners" : "Directors"}
                  </label>
                  <select
                    value={numDirectors}
                    onChange={(e) => setNumDirectors(Number(e.target.value))}
                    className="w-full p-3 rounded-xl text-sm"
                    style={{
                      background: "var(--color-bg-card)",
                      border: "1px solid var(--color-border)",
                      color: "var(--color-text-primary)",
                    }}
                  >
                    {[1, 2, 3, 4, 5].map((n) => (
                      <option key={n} value={n}>{n}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="mt-4">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={hasDSC}
                    onChange={(e) => setHasDSC(e.target.checked)}
                    className="w-4 h-4 rounded accent-purple-500"
                  />
                  <span className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
                    Directors already have valid DSC
                  </span>
                </label>
              </div>
            </div>
          </div>

          {/* ─── Right: Cost Breakdown ─── */}
          <div className="lg:col-span-3">
            <div className="glass-card p-8 sticky top-8" style={{ cursor: "default" }}>
              <h2 className="text-xl font-bold mb-6" style={{ fontFamily: "var(--font-display)" }}>
                💰 Your Incorporation Cost Breakdown
              </h2>

              {pricing ? (
                <div className="space-y-6">
                  {/* Platform Fee */}
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-semibold" style={{ color: "var(--color-accent-purple-light)" }}>
                        PLATFORM FEE
                      </span>
                      <span className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                        our service
                      </span>
                    </div>
                    <div
                      className="flex justify-between items-center p-3 rounded-lg"
                      style={{ background: "rgba(139, 92, 246, 0.1)" }}
                    >
                      <span>
                        {PLAN_TIERS.find((p) => p.value === planTier)?.label} Package (
                        {ENTITY_TYPES.find((e) => e.value === entityType)?.label})
                      </span>
                      <span className="font-bold">{formatCurrency(pricing.platform_fee)}</span>
                    </div>
                  </div>

                  {/* Government Fees */}
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-semibold" style={{ color: "var(--color-accent-emerald-light)" }}>
                        GOVERNMENT FEES
                      </span>
                      <span className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                        pass-through, ₹0 markup
                      </span>
                    </div>
                    <div className="space-y-1">
                      {pricing.government_fees.name_reservation > 0 && (
                        <div className="flex justify-between p-2 rounded" style={{ background: "rgba(255,255,255,0.02)" }}>
                          <span style={{ color: "var(--color-text-secondary)" }}>MCA Name Reservation</span>
                          <span>{formatCurrency(pricing.government_fees.name_reservation)}</span>
                        </div>
                      )}
                      {pricing.government_fees.filing_fee > 0 && (
                        <div className="flex justify-between p-2 rounded" style={{ background: "rgba(255,255,255,0.02)" }}>
                          <span style={{ color: "var(--color-text-secondary)" }}>
                            {entityType === "llp" ? "FiLLiP Filing" : "SPICe+ Filing"}
                          </span>
                          <span>{formatCurrency(pricing.government_fees.filing_fee)}</span>
                        </div>
                      )}
                      {pricing.government_fees.roc_registration > 0 && (
                        <div className="flex justify-between p-2 rounded" style={{ background: "rgba(255,255,255,0.02)" }}>
                          <span style={{ color: "var(--color-text-secondary)" }}>ROC Registration</span>
                          <span>{formatCurrency(pricing.government_fees.roc_registration)}</span>
                        </div>
                      )}
                      {pricing.government_fees.section8_license > 0 && (
                        <div className="flex justify-between p-2 rounded" style={{ background: "rgba(255,255,255,0.02)" }}>
                          <span style={{ color: "var(--color-text-secondary)" }}>INC-12 License Fee</span>
                          <span>{formatCurrency(pricing.government_fees.section8_license)}</span>
                        </div>
                      )}
                      <div className="flex justify-between p-2 rounded" style={{ background: "rgba(255,255,255,0.02)" }}>
                        <span style={{ color: "var(--color-text-secondary)" }}>
                          Stamp Duty ({pricing.state_display})
                        </span>
                        <span>{formatCurrency(pricing.government_fees.stamp_duty.total_stamp_duty)}</span>
                      </div>
                      <div className="flex justify-between p-2 rounded" style={{ background: "rgba(255,255,255,0.02)" }}>
                        <span style={{ color: "var(--color-text-secondary)" }}>PAN + TAN Application</span>
                        <span>{formatCurrency(pricing.government_fees.pan_tan)}</span>
                      </div>
                      <div
                        className="flex justify-between p-2 rounded-lg font-medium mt-1"
                        style={{ background: "rgba(16, 185, 129, 0.1)" }}
                      >
                        <span>Government Subtotal</span>
                        <span>{formatCurrency(pricing.government_fees.subtotal)}</span>
                      </div>
                    </div>
                  </div>

                  {/* DSC */}
                  {!hasDSC && pricing.dsc.total_dsc > 0 && (
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-semibold" style={{ color: "var(--color-accent-blue)" }}>
                          DIGITAL SIGNATURE CERTIFICATES
                        </span>
                        <span className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                          wholesale rate
                        </span>
                      </div>
                      <div className="space-y-1">
                        <div className="flex justify-between p-2 rounded" style={{ background: "rgba(255,255,255,0.02)" }}>
                          <span style={{ color: "var(--color-text-secondary)" }}>
                            DSC × {pricing.dsc.num_directors} (2-year)
                          </span>
                          <span>
                            {formatCurrency(pricing.dsc.dsc_per_unit * pricing.dsc.num_directors)}
                          </span>
                        </div>
                        <div className="flex justify-between p-2 rounded" style={{ background: "rgba(255,255,255,0.02)" }}>
                          <span style={{ color: "var(--color-text-secondary)" }}>
                            USB Tokens × {pricing.dsc.num_directors}
                          </span>
                          <span>
                            {formatCurrency(pricing.dsc.token_per_unit * pricing.dsc.num_directors)}
                          </span>
                        </div>
                        <div className="flex justify-between p-2 rounded-lg font-medium mt-1" style={{ background: "rgba(59, 130, 246, 0.1)" }}>
                          <span>DSC Subtotal</span>
                          <span>{formatCurrency(pricing.dsc.total_dsc)}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Grand Total */}
                  <div
                    className="flex justify-between items-center p-4 rounded-xl mt-4"
                    style={{
                      background: "var(--gradient-primary)",
                    }}
                  >
                    <span className="text-lg font-bold">TOTAL</span>
                    <span className="text-2xl font-extrabold" style={{ fontFamily: "var(--font-display)" }}>
                      {formatCurrency(pricing.grand_total)}
                    </span>
                  </div>

                  {/* Guarantees */}
                  <div className="space-y-2 mt-4">
                    <div className="flex items-center gap-2 text-sm" style={{ color: "var(--color-accent-emerald-light)" }}>
                      <span>✅</span> No hidden fees
                    </div>
                    <div className="flex items-center gap-2 text-sm" style={{ color: "var(--color-accent-emerald-light)" }}>
                      <span>✅</span> Government fees at exact cost (₹0 markup)
                    </div>
                    <div className="flex items-center gap-2 text-sm" style={{ color: "var(--color-accent-emerald-light)" }}>
                      <span>✅</span> DSC at wholesale rate
                    </div>
                  </div>

                  {/* Optimization Tip */}
                  {pricing.optimization_tip && pricing.optimization_tip.potential_saving > 0 && (
                    <div
                      className="p-4 rounded-xl mt-2"
                      style={{
                        background: "rgba(245, 158, 11, 0.1)",
                        border: "1px solid rgba(245, 158, 11, 0.3)",
                      }}
                    >
                      <div className="text-sm font-semibold mb-1" style={{ color: "var(--color-accent-amber)" }}>
                        💡 Cost Optimization Tip
                      </div>
                      <div className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
                        Registering in{" "}
                        <strong style={{ color: "var(--color-text-primary)" }}>
                          {pricing.optimization_tip.cheapest_state_display}
                        </strong>{" "}
                        instead of{" "}
                        <strong style={{ color: "var(--color-text-primary)" }}>
                          {pricing.state_display}
                        </strong>{" "}
                        could save you{" "}
                        <strong style={{ color: "var(--color-accent-emerald-light)" }}>
                          {formatCurrency(pricing.optimization_tip.potential_saving)}
                        </strong>{" "}
                        in stamp duty.
                      </div>
                    </div>
                  )}

                  <button 
                    onClick={() => {
                      if (!pricing) return;
                      const draftConfig = {
                        entity_type: entityType,
                        plan_tier: planTier,
                        state: state,
                        authorized_capital: capital,
                        num_directors: numDirectors,
                        pricing_snapshot: pricing
                      };
                      localStorage.setItem("pending_company_draft", JSON.stringify(draftConfig));
                      router.push("/signup");
                    }} 
                    className="btn-primary w-full text-center justify-center mt-4 text-lg !py-4"
                  >
                    Proceed to Incorporate →
                  </button>
                </div>
              ) : (
                <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>
                  <div className="text-4xl mb-4">⏳</div>
                  <p>Start the backend to see real-time pricing</p>
                  <code className="text-xs mt-2 block" style={{ color: "var(--color-text-muted)" }}>
                    cd backend && uvicorn src.main:app --reload --port 8000
                  </code>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
