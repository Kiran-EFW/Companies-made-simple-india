"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import type { PricingResponse, StateOption } from "@/lib/api";
import Footer from "@/components/footer";

const ENTITY_TYPES = [
  { value: "private_limited", label: "Private Limited", emoji: "🏢" },
  { value: "public_limited", label: "Public Limited", emoji: "🏛️" },
  { value: "opc", label: "OPC", emoji: "👤" },
  { value: "llp", label: "LLP", emoji: "🤝" },
  { value: "partnership", label: "Partnership", emoji: "👥" },
  { value: "section_8", label: "Section 8", emoji: "💚" },
  { value: "sole_proprietorship", label: "Sole Prop", emoji: "📋" },
];

const PLAN_TIERS = [
  {
    value: "launch",
    label: "Launch",
    desc: "AI-guided incorporation + CS review",
    descByEntity: {
      sole_proprietorship: "GST + Udyam + Shop & Establishment registration",
      partnership: "Deed drafting + ROF registration + PAN",
    },
  },
  {
    value: "grow",
    label: "Grow",
    desc: "Launch + GST + DPIIT + 90-day compliance",
    descByEntity: {
      sole_proprietorship: "Launch + FSSAI/trade license + 90-day support",
      partnership: "Launch + GST + 90-day compliance",
    },
  },
  {
    value: "scale",
    label: "Scale",
    desc: "Grow + 1-year compliance + dedicated RM",
    descByEntity: {
      partnership: "Grow + 1-year compliance + dedicated RM",
    },
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

// Entity-type-specific configuration
const ENTITY_CONFIG: Record<string, {
  capitalLabel: string;
  personLabel: string;
  personLabelPlural: string;
  minPersons: number;
  maxPersons: number;
  showCapital: boolean;
  showPersonCount: boolean;
  showDSC: boolean;
  hasScale: boolean;
  filingLabel: string;
  rocLabel: string;
  nameResLabel: string;
  stampDutyLabel: string;
  panTanLabel: string;
  ctaLabel: string;
}> = {
  private_limited: {
    capitalLabel: "Authorized Capital",
    personLabel: "Director",
    personLabelPlural: "Directors",
    minPersons: 2,
    maxPersons: 15,
    showCapital: true,
    showPersonCount: true,
    showDSC: true,
    hasScale: true,
    filingLabel: "SPICe+ Filing",
    rocLabel: "ROC Registration",
    nameResLabel: "MCA Name Reservation",
    stampDutyLabel: "Stamp Duty (MOA + AOA)",
    panTanLabel: "PAN + TAN Application",
    ctaLabel: "Proceed to Incorporate",
  },
  public_limited: {
    capitalLabel: "Authorized Capital",
    personLabel: "Director",
    personLabelPlural: "Directors",
    minPersons: 3,
    maxPersons: 15,
    showCapital: true,
    showPersonCount: true,
    showDSC: true,
    hasScale: true,
    filingLabel: "SPICe+ Filing",
    rocLabel: "ROC Registration",
    nameResLabel: "MCA Name Reservation",
    stampDutyLabel: "Stamp Duty (MOA + AOA)",
    panTanLabel: "PAN + TAN Application",
    ctaLabel: "Proceed to Incorporate",
  },
  opc: {
    capitalLabel: "Authorized Capital",
    personLabel: "Director",
    personLabelPlural: "Director",
    minPersons: 1,
    maxPersons: 1,
    showCapital: true,
    showPersonCount: false,
    showDSC: true,
    hasScale: true,
    filingLabel: "SPICe+ Filing",
    rocLabel: "ROC Registration",
    nameResLabel: "MCA Name Reservation",
    stampDutyLabel: "Stamp Duty (MOA + AOA)",
    panTanLabel: "PAN + TAN Application",
    ctaLabel: "Proceed to Incorporate",
  },
  llp: {
    capitalLabel: "Capital Contribution",
    personLabel: "Partner",
    personLabelPlural: "Partners",
    minPersons: 2,
    maxPersons: 10,
    showCapital: true,
    showPersonCount: true,
    showDSC: true,
    hasScale: true,
    filingLabel: "FiLLiP Filing",
    rocLabel: "",
    nameResLabel: "RUN-LLP Name Reservation",
    stampDutyLabel: "Stamp Duty (LLP Agreement)",
    panTanLabel: "PAN + TAN Application",
    ctaLabel: "Proceed to Register",
  },
  partnership: {
    capitalLabel: "Capital Contribution",
    personLabel: "Partner",
    personLabelPlural: "Partners",
    minPersons: 2,
    maxPersons: 20,
    showCapital: true,
    showPersonCount: true,
    showDSC: false,
    hasScale: true,
    filingLabel: "",
    rocLabel: "Registrar of Firms Fee",
    nameResLabel: "",
    stampDutyLabel: "Stamp Duty (Partnership Deed)",
    panTanLabel: "PAN Application",
    ctaLabel: "Proceed to Register",
  },
  section_8: {
    capitalLabel: "Authorized Capital",
    personLabel: "Director",
    personLabelPlural: "Directors",
    minPersons: 2,
    maxPersons: 15,
    showCapital: true,
    showPersonCount: true,
    showDSC: true,
    hasScale: true,
    filingLabel: "SPICe+ Filing",
    rocLabel: "ROC Registration",
    nameResLabel: "MCA Name Reservation",
    stampDutyLabel: "Stamp Duty (MOA + AOA)",
    panTanLabel: "PAN + TAN Application",
    ctaLabel: "Proceed to Incorporate",
  },
  sole_proprietorship: {
    capitalLabel: "",
    personLabel: "Proprietor",
    personLabelPlural: "Proprietor",
    minPersons: 1,
    maxPersons: 1,
    showCapital: false,
    showPersonCount: false,
    showDSC: false,
    hasScale: false,
    filingLabel: "",
    rocLabel: "",
    nameResLabel: "",
    stampDutyLabel: "",
    panTanLabel: "PAN Application",
    ctaLabel: "Proceed to Register",
  },
};

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

  const config = ENTITY_CONFIG[entityType] || ENTITY_CONFIG.private_limited;

  // Reset dependent fields when entity type changes
  useEffect(() => {
    const cfg = ENTITY_CONFIG[entityType] || ENTITY_CONFIG.private_limited;
    // Clamp director count to valid range
    setNumDirectors((prev) => Math.max(cfg.minPersons, Math.min(prev, cfg.maxPersons)));
    // Reset DSC for entity types that don't use it
    if (!cfg.showDSC) setHasDSC(false);
    // Reset to Launch if currently on Scale for sole_prop
    if (!cfg.hasScale && planTier === "scale") setPlanTier("launch");
    // Reset capital for sole_prop
    if (!cfg.showCapital) setCapital(100000);
  }, [entityType]);

  useEffect(() => {
    calculatePricing();
  }, [entityType, planTier, state, capital, numDirectors, hasDSC]);

  const availablePlans = PLAN_TIERS.filter(
    (p) => config.hasScale || p.value !== "scale"
  );

  const personOptions: number[] = [];
  for (let i = config.minPersons; i <= config.maxPersons; i++) {
    personOptions.push(i);
  }

  async function calculatePricing() {
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const res = await fetch(`${baseUrl}/pricing/calculate`, {
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
                          : "var(--color-hover-overlay)",
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
                {availablePlans.map((p) => {
                  const desc = (p.descByEntity as Record<string, string>)?.[entityType] || p.desc;
                  return (
                    <button
                      key={p.value}
                      onClick={() => setPlanTier(p.value)}
                      className="w-full p-3 rounded-xl text-left transition-all"
                      style={{
                        background:
                          planTier === p.value
                            ? "rgba(139, 92, 246, 0.2)"
                            : "var(--color-hover-overlay)",
                        border: `1px solid ${planTier === p.value ? "rgba(139, 92, 246, 0.5)" : "var(--color-border)"}`,
                      }}
                    >
                      <div className="font-semibold text-sm">{p.label}</div>
                      <div className="text-xs mt-0.5" style={{ color: "var(--color-text-muted)" }}>
                        {desc}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* State */}
            <div className="glass-card p-6" style={{ cursor: "default" }}>
              <label className="text-sm font-semibold mb-3 block" style={{ color: "var(--color-text-secondary)" }}>
                {entityType === "partnership" ? "State (Principal Place of Business)" : "State of Registration"}
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

            {/* Capital & Person Count — only show if relevant */}
            {(config.showCapital || config.showPersonCount || config.showDSC) && (
              <div className="glass-card p-6" style={{ cursor: "default" }}>
                {(config.showCapital || config.showPersonCount) && (
                  <div className={`grid ${config.showCapital && config.showPersonCount ? "grid-cols-2" : "grid-cols-1"} gap-4`}>
                    {config.showCapital && (
                      <div>
                        <label className="text-sm font-semibold mb-2 block" style={{ color: "var(--color-text-secondary)" }}>
                          {config.capitalLabel}
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
                    )}
                    {config.showPersonCount && (
                      <div>
                        <label className="text-sm font-semibold mb-2 block" style={{ color: "var(--color-text-secondary)" }}>
                          {config.personLabelPlural}
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
                          {personOptions.map((n) => (
                            <option key={n} value={n}>{n}</option>
                          ))}
                        </select>
                      </div>
                    )}
                  </div>
                )}
                {config.showDSC && (
                  <div className={config.showCapital || config.showPersonCount ? "mt-4" : ""}>
                    <label className="flex items-center gap-3 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={hasDSC}
                        onChange={(e) => setHasDSC(e.target.checked)}
                        className="w-4 h-4 rounded accent-[var(--color-accent-purple)]"
                      />
                      <span className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
                        {config.personLabelPlural} already have valid DSC
                      </span>
                    </label>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* ─── Right: Cost Breakdown ─── */}
          <div className="lg:col-span-3">
            <div className="glass-card p-8 sticky top-8" style={{ cursor: "default" }}>
              <h2 className="text-xl font-bold mb-6" style={{ fontFamily: "var(--font-display)" }}>
                💰 Your {entityType === "sole_proprietorship" ? "Registration" : entityType === "partnership" ? "Registration" : "Incorporation"} Cost Breakdown
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
                      {/* Name Reservation — only for MCA-registered entities */}
                      {pricing.government_fees.name_reservation > 0 && (
                        <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
                          <span style={{ color: "var(--color-text-secondary)" }}>{config.nameResLabel}</span>
                          <span>{formatCurrency(pricing.government_fees.name_reservation)}</span>
                        </div>
                      )}

                      {/* Filing Fee — SPICe+ or FiLLiP */}
                      {pricing.government_fees.filing_fee > 0 && (
                        <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
                          <span style={{ color: "var(--color-text-secondary)" }}>{config.filingLabel}</span>
                          <span>{formatCurrency(pricing.government_fees.filing_fee)}</span>
                        </div>
                      )}

                      {/* ROC / ROF Registration */}
                      {pricing.government_fees.roc_registration > 0 && (
                        <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
                          <span style={{ color: "var(--color-text-secondary)" }}>{config.rocLabel || "ROC Registration"}</span>
                          <span>{formatCurrency(pricing.government_fees.roc_registration)}</span>
                        </div>
                      )}

                      {/* Section 8 License */}
                      {pricing.government_fees.section8_license > 0 && (
                        <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
                          <span style={{ color: "var(--color-text-secondary)" }}>INC-12 License Fee</span>
                          <span>{formatCurrency(pricing.government_fees.section8_license)}</span>
                        </div>
                      )}

                      {/* Stamp Duty — only show if > 0 */}
                      {pricing.government_fees.stamp_duty.total_stamp_duty > 0 && (
                        <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
                          <span style={{ color: "var(--color-text-secondary)" }}>
                            {config.stampDutyLabel} ({pricing.state_display})
                          </span>
                          <span>{formatCurrency(pricing.government_fees.stamp_duty.total_stamp_duty)}</span>
                        </div>
                      )}

                      {/* PAN / PAN+TAN */}
                      {pricing.government_fees.pan_tan > 0 && (
                        <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
                          <span style={{ color: "var(--color-text-secondary)" }}>{config.panTanLabel}</span>
                          <span>{formatCurrency(pricing.government_fees.pan_tan)}</span>
                        </div>
                      )}

                      {/* Government Subtotal */}
                      <div
                        className="flex justify-between p-2 rounded-lg font-medium mt-1"
                        style={{ background: "rgba(16, 185, 129, 0.1)" }}
                      >
                        <span>Government Subtotal</span>
                        <span>{formatCurrency(pricing.government_fees.subtotal)}</span>
                      </div>
                    </div>
                  </div>

                  {/* DSC — only for MCA-registered entities that need DSC */}
                  {config.showDSC && !hasDSC && pricing.dsc.total_dsc > 0 && (
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
                        <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
                          <span style={{ color: "var(--color-text-secondary)" }}>
                            DSC × {pricing.dsc.num_directors} (2-year)
                          </span>
                          <span>
                            {formatCurrency(pricing.dsc.dsc_per_unit * pricing.dsc.num_directors)}
                          </span>
                        </div>
                        <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
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

                  {/* Public Limited — recurring costs info */}
                  {entityType === "public_limited" && pricing.public_limited_recurring && (
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-semibold" style={{ color: "var(--color-accent-amber)" }}>
                          ANNUAL RECURRING COSTS
                        </span>
                        <span className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                          estimated
                        </span>
                      </div>
                      <div className="space-y-1">
                        <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
                          <span style={{ color: "var(--color-text-secondary)" }}>Secretarial Audit (annual)</span>
                          <span>{formatCurrency(pricing.public_limited_recurring.secretarial_audit_annual)}</span>
                        </div>
                        <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
                          <span style={{ color: "var(--color-text-secondary)" }}>CS Compliance (annual)</span>
                          <span>{formatCurrency(pricing.public_limited_recurring.cs_compliance_annual)}</span>
                        </div>
                        <div className="text-xs mt-1 px-1" style={{ color: "var(--color-text-muted)" }}>
                          {pricing.public_limited_recurring.note}
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
                    {config.showDSC && (
                      <div className="flex items-center gap-2 text-sm" style={{ color: "var(--color-accent-emerald-light)" }}>
                        <span>✅</span> DSC at wholesale rate
                      </div>
                    )}
                  </div>

                  {/* Optimization Tip — only for entities with stamp duty variance */}
                  {pricing.optimization_tip && pricing.optimization_tip.potential_saving > 0 && entityType !== "sole_proprietorship" && (
                    <div
                      className="p-4 rounded-xl mt-2"
                      style={{
                        background: "var(--color-warning-light)",
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
                    {config.ctaLabel} →
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
      <Footer />
    </div>
  );
}
