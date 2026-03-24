"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import type { PricingResponse, StateOption } from "@/lib/api";
import Header from "@/components/header";
import Footer from "@/components/footer";
import ChatWidget from "@/components/chat-widget";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import FAQAccordion from "@/components/marketing/faq-accordion";
import { Check, ChevronDown } from "lucide-react";

// ─── Section Navigation ─────────────────────────────────────────────────────

const SECTIONS = [
  { id: "plans", label: "Platform Plans" },
  { id: "incorporation", label: "Incorporation" },
  { id: "faq", label: "FAQ" },
];

// ─── Platform Subscription Plans ────────────────────────────────────────────

const SUBSCRIPTION_PLANS = [
  {
    key: "free",
    name: "Free",
    tagline: "For every Indian company",
    monthlyPrice: 0,
    annualPrice: 0,
    highlighted: false,
    features: [
      "Company dashboard",
      "Compliance calendar & reminders",
      "Basic document storage",
      "Company overview & status",
    ],
  },
  {
    key: "growth",
    name: "Growth",
    tagline: "For funded startups",
    monthlyPrice: 2999,
    annualPrice: 29999,
    highlighted: true,
    features: [
      "Everything in Free, plus",
      "Full cap table management",
      "ESOP plans & grants",
      "Data room with secure sharing",
      "E-signatures (up to 10/mo)",
      "Investor portal",
      "Fundraising tools",
      "Valuations (Rule 11UA)",
    ],
  },
  {
    key: "scale",
    name: "Scale",
    tagline: "For scaling companies",
    monthlyPrice: 9999,
    annualPrice: 99999,
    highlighted: false,
    features: [
      "Everything in Growth, plus",
      "Board governance suite",
      "Statutory registers",
      "FEMA compliance tracking",
      "Unlimited e-signatures",
      "Investor reporting",
      "Closing room",
      "Dedicated account manager",
    ],
  },
];

// ─── Feature Comparison Table ────────────────────────────────────────────────
// [name, free, growth, scale] — true = check, false = dash, string = label
type FV = boolean | string;
const CMP: { cat: string; rows: [string, FV, FV, FV][] }[] = [
  { cat: "Core Platform", rows: [
    ["Company dashboard", true, true, true], ["Compliance calendar & reminders", true, true, true],
    ["Basic document storage", true, true, true], ["Company overview & status", true, true, true],
  ]},
  { cat: "Equity & Fundraising", rows: [
    ["Cap table management", false, true, true], ["Dilution modeling", false, true, true],
    ["ESOP plans & grants", false, true, true], ["Fundraising rounds (SAFE, CCD, CCPS, equity)", false, true, true],
    ["Investor portal", false, true, true], ["Valuations (Rule 11UA)", false, true, true],
    ["Closing room", false, false, true],
  ]},
  { cat: "Documents & Signatures", rows: [
    ["Document storage", "50 docs", "Unlimited", "Unlimited"],
    ["Data room with secure sharing", false, true, true], ["E-signatures", false, "10/mo", "Unlimited"],
  ]},
  { cat: "Governance & Compliance", rows: [
    ["Board meeting management", false, false, true], ["Statutory registers", false, false, true],
    ["FEMA compliance tracking", false, false, true], ["Investor reporting", false, false, true],
  ]},
  { cat: "Support", rows: [
    ["Email support", true, true, true], ["Priority support", false, true, true],
    ["Dedicated account manager", false, false, true],
  ]},
];

// ─── Incorporation Calculator Data ──────────────────────────────────────────

const ENTITY_TYPES = ([
  ["private_limited", "Private Limited"], ["public_limited", "Public Limited"], ["opc", "OPC"],
  ["llp", "LLP"], ["partnership", "Partnership"], ["section_8", "Section 8"],
  ["sole_proprietorship", "Sole Prop"],
] as const).map(([value, label]) => ({ value, label }));

const PLAN_TIERS = [
  { value: "launch", label: "Launch", desc: "Guided incorporation + CS review",
    descByEntity: { sole_proprietorship: "GST + Udyam + Shop & Establishment registration", partnership: "Deed drafting + ROF registration + PAN" } as Record<string, string> },
  { value: "grow", label: "Grow", desc: "Launch + GST + DPIIT + 90-day compliance",
    descByEntity: { sole_proprietorship: "Launch + FSSAI/trade license + 90-day support", partnership: "Launch + GST + 90-day compliance" } as Record<string, string> },
  { value: "scale", label: "Scale", desc: "Grow + 1-year compliance + dedicated RM",
    descByEntity: { partnership: "Grow + 1-year compliance + dedicated RM" } as Record<string, string> },
];

const STATES: StateOption[] = ([
  ["andhra_pradesh", "Andhra Pradesh"], ["arunachal_pradesh", "Arunachal Pradesh"], ["assam", "Assam"],
  ["bihar", "Bihar"], ["chhattisgarh", "Chhattisgarh"], ["delhi", "Delhi"], ["goa", "Goa"],
  ["gujarat", "Gujarat"], ["haryana", "Haryana"], ["himachal_pradesh", "Himachal Pradesh"],
  ["jammu_kashmir", "Jammu & Kashmir"], ["jharkhand", "Jharkhand"], ["karnataka", "Karnataka"],
  ["kerala", "Kerala"], ["ladakh", "Ladakh"], ["madhya_pradesh", "Madhya Pradesh"],
  ["maharashtra", "Maharashtra"], ["manipur", "Manipur"], ["meghalaya", "Meghalaya"],
  ["mizoram", "Mizoram"], ["nagaland", "Nagaland"], ["odisha", "Odisha"], ["punjab", "Punjab"],
  ["rajasthan", "Rajasthan"], ["sikkim", "Sikkim"], ["tamil_nadu", "Tamil Nadu"],
  ["telangana", "Telangana"], ["tripura", "Tripura"], ["uttar_pradesh", "Uttar Pradesh"],
  ["uttarakhand", "Uttarakhand"], ["west_bengal", "West Bengal"],
] as const).map(([value, label]) => ({ value, label }));

const CAPITAL_OPTIONS = [
  [100000, "\u20B91,00,000"], [500000, "\u20B95,00,000"], [1000000, "\u20B910,00,000"],
  [2500000, "\u20B925,00,000"], [5000000, "\u20B950,00,000"],
].map(([value, label]) => ({ value: value as number, label: label as string }));

type ECfg = { capitalLabel: string; personLabel: string; personLabelPlural: string; minPersons: number; maxPersons: number; showCapital: boolean; showPersonCount: boolean; showDSC: boolean; hasScale: boolean; filingLabel: string; rocLabel: string; nameResLabel: string; stampDutyLabel: string; panTanLabel: string; ctaLabel: string; };
const _co = (o: Partial<ECfg>): ECfg => ({ capitalLabel: "Authorized Capital", personLabel: "Director", personLabelPlural: "Directors", minPersons: 2, maxPersons: 15, showCapital: true, showPersonCount: true, showDSC: true, hasScale: true, filingLabel: "SPICe+ Filing", rocLabel: "ROC Registration", nameResLabel: "MCA Name Reservation", stampDutyLabel: "Stamp Duty (MOA + AOA)", panTanLabel: "PAN + TAN Application", ctaLabel: "Proceed to Incorporate", ...o });
const ENTITY_CONFIG: Record<string, ECfg> = {
  private_limited: _co({}),
  public_limited: _co({ minPersons: 3 }),
  opc: _co({ personLabelPlural: "Director", minPersons: 1, maxPersons: 1, showPersonCount: false }),
  llp: _co({ capitalLabel: "Capital Contribution", personLabel: "Partner", personLabelPlural: "Partners", maxPersons: 10, filingLabel: "FiLLiP Filing", rocLabel: "", nameResLabel: "RUN-LLP Name Reservation", stampDutyLabel: "Stamp Duty (LLP Agreement)", ctaLabel: "Proceed to Register" }),
  partnership: _co({ capitalLabel: "Capital Contribution", personLabel: "Partner", personLabelPlural: "Partners", maxPersons: 20, showDSC: false, filingLabel: "", rocLabel: "Registrar of Firms Fee", nameResLabel: "", stampDutyLabel: "Stamp Duty (Partnership Deed)", panTanLabel: "PAN Application", ctaLabel: "Proceed to Register" }),
  section_8: _co({}),
  sole_proprietorship: _co({ capitalLabel: "", personLabel: "Proprietor", personLabelPlural: "Proprietor", minPersons: 1, maxPersons: 1, showCapital: false, showPersonCount: false, showDSC: false, hasScale: false, filingLabel: "", rocLabel: "", nameResLabel: "", stampDutyLabel: "", panTanLabel: "PAN Application", ctaLabel: "Proceed to Register" }),
};

// ─── FAQ Data ────────────────────────────────────────────────────────────────

const FAQ_ITEMS = [
  { question: "Can I switch plans later?", answer: "Yes. You can upgrade or downgrade at any time. When upgrading, you get immediate access to new features. When downgrading, your current billing period will be honored." },
  { question: "What happens when my subscription expires?", answer: "You\u2019ll retain access to the free tier features \u2014 compliance calendar, reminders, and basic document storage. Premium features like cap table, ESOP, and data room will become read-only." },
  { question: "Are government fees included in the incorporation price?", answer: "Government fees (MCA filing fees, stamp duty, DSC charges) are passed through at exact cost with zero markup. Our incorporation calculator shows the complete breakdown." },
  { question: "Do you offer refunds?", answer: "Yes. If your incorporation application hasn\u2019t been submitted to MCA, we offer a full refund minus government fees already paid. For platform subscriptions, you can cancel anytime." },
  { question: "Is there a startup discount?", answer: "DPIIT-recognized startups get special pricing on select services. Contact our team for details on available discounts and benefits." },
  { question: "What payment methods do you accept?", answer: "We accept all major payment methods via Razorpay \u2014 credit/debit cards, UPI, net banking, and wallets." },
];

// ─── Helpers ────────────────────────────────────────────────────────────────

function fmt(amount: number): string {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount);
}

function CostRow({ label, amount, bg = "var(--color-stripe-alt)" }: { label: string; amount: number; bg?: string }) {
  if (amount <= 0) return null;
  return (
    <div className="flex justify-between p-2 rounded" style={{ background: bg }}>
      <span style={{ color: "var(--color-text-secondary)" }}>{label}</span><span>{fmt(amount)}</span>
    </div>
  );
}

const selectStyle = { background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" } as const;
const activeBtn = (active: boolean) => ({ background: active ? "rgba(139, 92, 246, 0.2)" : "var(--color-hover-overlay)", border: `1px solid ${active ? "rgba(139, 92, 246, 0.5)" : "var(--color-border)"}` });

// ─── Page Component ─────────────────────────────────────────────────────────

export default function PricingPage() {
  const router = useRouter();
  const [activeSection, setActiveSection] = useState("plans");
  const [billingCycle, setBillingCycle] = useState<"monthly" | "annual">("annual");
  const [showComparison, setShowComparison] = useState(false);

  // Incorporation calculator state
  const [entityType, setEntityType] = useState("private_limited");
  const [planTier, setPlanTier] = useState("launch");
  const [state, setState] = useState("maharashtra");
  const [capital, setCapital] = useState(100000);
  const [numDirectors, setNumDirectors] = useState(2);
  const [hasDSC, setHasDSC] = useState(false);
  const [pricing, setPricing] = useState<PricingResponse | null>(null);

  const config = ENTITY_CONFIG[entityType] || ENTITY_CONFIG.private_limited;

  useEffect(() => {
    const cfg = ENTITY_CONFIG[entityType] || ENTITY_CONFIG.private_limited;
    setNumDirectors((prev) => Math.max(cfg.minPersons, Math.min(prev, cfg.maxPersons)));
    if (!cfg.showDSC) setHasDSC(false);
    if (!cfg.hasScale && planTier === "scale") setPlanTier("launch");
    if (!cfg.showCapital) setCapital(100000);
  }, [entityType]);

  useEffect(() => { calculatePricing(); }, [entityType, planTier, state, capital, numDirectors, hasDSC]);

  const availablePlans = PLAN_TIERS.filter((p) => config.hasScale || p.value !== "scale");
  const personOptions: number[] = [];
  for (let i = config.minPersons; i <= config.maxPersons; i++) personOptions.push(i);

  async function calculatePricing() {
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const res = await fetch(`${baseUrl}/pricing/calculate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ entity_type: entityType, plan_tier: planTier, state, authorized_capital: capital, num_directors: numDirectors, has_existing_dsc: hasDSC, dsc_validity_years: 2 }),
      });
      if (res.ok) setPricing(await res.json());
    } catch { /* Backend offline -- show UI anyway */ }
  }

  function scrollToSection(id: string) {
    setActiveSection(id);
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  return (
    <div className="min-h-screen">
      <Header />

      {/* ─── Hero ─── */}
      <div className="max-w-7xl mx-auto px-6 pt-16 pb-8 text-center">
        <h1 className="text-4xl md:text-5xl font-bold mb-4" style={{ fontFamily: "var(--font-display)" }}>
          Simple, <span className="gradient-text">transparent pricing</span>
        </h1>
        <p className="text-lg max-w-2xl mx-auto" style={{ color: "var(--color-text-secondary)" }}>
          Start free. Upgrade when you raise funding.
        </p>
      </div>

      {/* ─── Section Nav ─── */}
      <div className="sticky top-16 z-40 backdrop-blur-sm border-b" style={{ backgroundColor: "var(--color-bg-primary)", borderColor: "var(--color-border)" }}>
        <div className="max-w-7xl mx-auto px-6 flex gap-1 overflow-x-auto py-2">
          {SECTIONS.map((s) => (
            <button key={s.id} onClick={() => scrollToSection(s.id)} className="px-4 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-colors"
              style={{ backgroundColor: activeSection === s.id ? "rgba(139, 92, 246, 0.15)" : "transparent", color: activeSection === s.id ? "var(--color-accent-purple)" : "var(--color-text-secondary)" }}>
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* ── SECTION 1: Platform Subscription Plans ── */}
      <section id="plans" className="py-16 scroll-mt-28">
        <div className="max-w-7xl mx-auto px-6">
          {/* Billing Toggle */}
          <div className="flex justify-center mb-10">
            <div className="inline-flex items-center rounded-xl p-1" style={{ border: "1px solid var(--color-border)", backgroundColor: "var(--color-bg-card)" }}>
              {(["monthly", "annual"] as const).map((cycle) => (
                <button key={cycle} onClick={() => setBillingCycle(cycle)}
                  className={`px-5 py-2.5 text-sm font-medium rounded-lg transition-colors ${cycle === "annual" ? "flex items-center gap-2" : ""}`}
                  style={{ backgroundColor: billingCycle === cycle ? "rgba(139, 92, 246, 0.15)" : "transparent", color: billingCycle === cycle ? "var(--color-accent-purple)" : "var(--color-text-secondary)" }}>
                  {cycle === "monthly" ? "Monthly" : "Annual"}
                  {cycle === "annual" && <span className="text-xs font-semibold px-2 py-0.5 rounded-full" style={{ backgroundColor: "rgba(16, 185, 129, 0.15)", color: "var(--color-accent-emerald-light)" }}>Save 17%</span>}
                </button>
              ))}
            </div>
          </div>

          {/* Plan Cards */}
          <div className="grid md:grid-cols-3 gap-6 mb-10">
            {SUBSCRIPTION_PLANS.map((plan) => (
              <div key={plan.key} className="rounded-2xl p-7 flex flex-col relative" style={{ backgroundColor: "var(--color-bg-card)", border: plan.highlighted ? "2px solid var(--color-accent-purple)" : "1px solid var(--color-border)", boxShadow: plan.highlighted ? "0 0 0 4px rgba(139, 92, 246, 0.1)" : undefined }}>
                {plan.highlighted && <div className="text-xs font-semibold mb-4 px-3 py-1 rounded-full self-start" style={{ backgroundColor: "rgba(139, 92, 246, 0.15)", color: "var(--color-accent-purple)" }}>Most Popular</div>}
                <h3 className="text-xl font-bold" style={{ color: "var(--color-text-primary)", fontFamily: "var(--font-display)" }}>{plan.name}</h3>
                <div className="mt-3 mb-1">
                  <span className="text-4xl font-bold" style={{ color: "var(--color-text-primary)", fontFamily: "var(--font-display)" }}>{plan.monthlyPrice === 0 ? "\u20B90" : fmt(billingCycle === "annual" ? plan.annualPrice : plan.monthlyPrice)}</span>
                  <span className="text-sm ml-1" style={{ color: "var(--color-text-muted)" }}>{plan.monthlyPrice === 0 ? "/forever" : billingCycle === "annual" ? "/year" : "/month"}</span>
                  {plan.monthlyPrice > 0 && billingCycle === "annual" && <div className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>{fmt(Math.round(plan.annualPrice / 12))}/month billed annually</div>}
                </div>
                <p className="text-sm mb-5" style={{ color: "var(--color-text-secondary)" }}>{plan.tagline}</p>
                <ul className="space-y-2.5 flex-1 mb-7">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2.5 text-sm" style={{ color: "var(--color-text-secondary)" }}><Check className="w-4 h-4 mt-0.5 shrink-0 text-emerald-500" />{f}</li>
                  ))}
                </ul>
                <a href="/signup" className={plan.highlighted ? "btn-primary w-full text-center text-sm" : "block text-center text-sm font-medium py-2.5 rounded-xl transition-colors hover:bg-[var(--color-bg-secondary)]"} style={plan.highlighted ? {} : { border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}>
                  {plan.monthlyPrice === 0 ? "Get Started Free" : "Get Started"}
                </a>
              </div>
            ))}
          </div>

          {/* Compare All Features (expandable) */}
          <div className="rounded-2xl overflow-hidden" style={{ border: "1px solid var(--color-border)", backgroundColor: "var(--color-bg-card)" }}>
            <button
              onClick={() => setShowComparison(!showComparison)}
              className="w-full flex items-center justify-center gap-2 px-6 py-4 text-sm font-semibold transition-colors hover:bg-[var(--color-bg-secondary)]"
              style={{ color: "var(--color-accent-purple)" }}
            >
              Compare all features
              <ChevronDown className={`w-4 h-4 transition-transform duration-300 ${showComparison ? "rotate-180" : ""}`} />
            </button>

            <div className={`overflow-hidden transition-all duration-500 ${showComparison ? "max-h-[2000px] opacity-100" : "max-h-0 opacity-0"}`}>
              <div className="px-6 pb-6">
                {/* Table header */}
                <div className="grid grid-cols-4 gap-4 py-3 border-b" style={{ borderColor: "var(--color-border)" }}>
                  <div className="text-sm font-semibold" style={{ color: "var(--color-text-muted)" }}>Feature</div>
                  <div className="text-sm font-semibold text-center" style={{ color: "var(--color-text-muted)" }}>Free</div>
                  <div className="text-sm font-semibold text-center" style={{ color: "var(--color-accent-purple)" }}>Growth</div>
                  <div className="text-sm font-semibold text-center" style={{ color: "var(--color-text-muted)" }}>Scale</div>
                </div>

                {CMP.map((cat) => (
                  <div key={cat.cat}>
                    <div className="py-3 mt-2"><span className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>{cat.cat}</span></div>
                    {cat.rows.map(([name, ...vals]) => (
                      <div key={name as string} className="grid grid-cols-4 gap-4 py-2.5 border-b last:border-b-0" style={{ borderColor: "var(--color-border)" }}>
                        <div className="text-sm" style={{ color: "var(--color-text-secondary)" }}>{name}</div>
                        {vals.map((val, i) => (
                          <div key={i} className="text-center">
                            {val === true ? <Check className="w-4 h-4 mx-auto text-emerald-500" />
                              : val === false ? <span className="text-sm" style={{ color: "var(--color-text-muted)" }}>&mdash;</span>
                              : <span className="text-xs font-medium" style={{ color: "var(--color-text-secondary)" }}>{val}</span>}
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── SECTION 2: Incorporation Calculator ── */}
      <section id="incorporation" className="py-16 scroll-mt-28" style={{ backgroundColor: "var(--color-bg-secondary)" }}>
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Calculate your <span className="gradient-text">incorporation cost</span></>}
            subtitle="Transparent pricing with government fees at exact cost. \u20B90 markup."
          />

          <div className="grid lg:grid-cols-5 gap-8">
            {/* Left: Configuration */}
            <div className="lg:col-span-2 space-y-5">
              <div className="glass-card p-6" style={{ cursor: "default" }}>
                <label className="text-sm font-semibold mb-3 block" style={{ color: "var(--color-text-secondary)" }}>Entity Type</label>
                <div className="grid grid-cols-2 gap-2">
                  {ENTITY_TYPES.map((e) => (
                    <button key={e.value} onClick={() => setEntityType(e.value)} className="p-3 rounded-xl text-left transition-all text-sm" style={activeBtn(entityType === e.value)}>
                      <div className="font-medium">{e.label}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="glass-card p-6" style={{ cursor: "default" }}>
                <label className="text-sm font-semibold mb-3 block" style={{ color: "var(--color-text-secondary)" }}>Plan</label>
                <div className="space-y-2">
                  {availablePlans.map((p) => {
                    const desc = p.descByEntity?.[entityType] || p.desc;
                    return (
                      <button key={p.value} onClick={() => setPlanTier(p.value)} className="w-full p-3 rounded-xl text-left transition-all" style={activeBtn(planTier === p.value)}>
                        <div className="font-semibold text-sm">{p.label}</div>
                        <div className="text-xs mt-0.5" style={{ color: "var(--color-text-muted)" }}>{desc}</div>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="glass-card p-6" style={{ cursor: "default" }}>
                <label className="text-sm font-semibold mb-3 block" style={{ color: "var(--color-text-secondary)" }}>
                  {entityType === "partnership" ? "State (Principal Place of Business)" : "State of Registration"}
                </label>
                <select value={state} onChange={(e) => setState(e.target.value)} className="w-full p-3 rounded-xl text-sm" style={selectStyle}>
                  {STATES.map((s) => (<option key={s.value} value={s.value}>{s.label}</option>))}
                </select>
              </div>

              {(config.showCapital || config.showPersonCount || config.showDSC) && (
                <div className="glass-card p-6" style={{ cursor: "default" }}>
                  {(config.showCapital || config.showPersonCount) && (
                    <div className={`grid ${config.showCapital && config.showPersonCount ? "grid-cols-2" : "grid-cols-1"} gap-4`}>
                      {config.showCapital && (
                        <div>
                          <label className="text-sm font-semibold mb-2 block" style={{ color: "var(--color-text-secondary)" }}>{config.capitalLabel}</label>
                          <select value={capital} onChange={(e) => setCapital(Number(e.target.value))} className="w-full p-3 rounded-xl text-sm" style={selectStyle}>
                            {CAPITAL_OPTIONS.map((c) => (<option key={c.value} value={c.value}>{c.label}</option>))}
                          </select>
                        </div>
                      )}
                      {config.showPersonCount && (
                        <div>
                          <label className="text-sm font-semibold mb-2 block" style={{ color: "var(--color-text-secondary)" }}>{config.personLabelPlural}</label>
                          <select value={numDirectors} onChange={(e) => setNumDirectors(Number(e.target.value))} className="w-full p-3 rounded-xl text-sm" style={selectStyle}>
                            {personOptions.map((n) => (<option key={n} value={n}>{n}</option>))}
                          </select>
                        </div>
                      )}
                    </div>
                  )}
                  {config.showDSC && (
                    <div className={config.showCapital || config.showPersonCount ? "mt-4" : ""}>
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input type="checkbox" checked={hasDSC} onChange={(e) => setHasDSC(e.target.checked)} className="w-4 h-4 rounded accent-[var(--color-accent-purple)]" />
                        <span className="text-sm" style={{ color: "var(--color-text-secondary)" }}>{config.personLabelPlural} already have valid DSC</span>
                      </label>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Right: Cost Breakdown */}
            <div className="lg:col-span-3">
              <div className="glass-card p-8 sticky top-32" style={{ cursor: "default" }}>
                <h3 className="text-xl font-bold mb-6" style={{ fontFamily: "var(--font-display)" }}>
                  Your {entityType === "sole_proprietorship" || entityType === "partnership" ? "Registration" : "Incorporation"} Cost Breakdown
                </h3>

                {pricing ? (
                  <div className="space-y-6">
                    {/* Platform Fee */}
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-semibold" style={{ color: "var(--color-accent-purple-light)" }}>PLATFORM FEE</span>
                        <span className="text-sm" style={{ color: "var(--color-text-muted)" }}>our service</span>
                      </div>
                      <div className="flex justify-between items-center p-3 rounded-lg" style={{ background: "rgba(139, 92, 246, 0.1)" }}>
                        <span>{PLAN_TIERS.find((p) => p.value === planTier)?.label} Package ({ENTITY_TYPES.find((e) => e.value === entityType)?.label})</span>
                        <span className="font-bold">{fmt(pricing.platform_fee)}</span>
                      </div>
                    </div>

                    {/* Government Fees */}
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-semibold" style={{ color: "var(--color-accent-emerald-light)" }}>GOVERNMENT FEES</span>
                        <span className="text-sm" style={{ color: "var(--color-text-muted)" }}>pass-through, {"\u20B9"}0 markup</span>
                      </div>
                      <div className="space-y-1">
                        <CostRow label={config.nameResLabel} amount={pricing.government_fees.name_reservation} />
                        <CostRow label={config.filingLabel} amount={pricing.government_fees.filing_fee} />
                        <CostRow label={config.rocLabel || "ROC Registration"} amount={pricing.government_fees.roc_registration} />
                        <CostRow label="INC-12 License Fee" amount={pricing.government_fees.section8_license} />
                        <CostRow label={`${config.stampDutyLabel} (${pricing.state_display})`} amount={pricing.government_fees.stamp_duty.total_stamp_duty} />
                        <CostRow label={config.panTanLabel} amount={pricing.government_fees.pan_tan} />
                        <div className="flex justify-between p-2 rounded-lg font-medium mt-1" style={{ background: "rgba(16, 185, 129, 0.1)" }}>
                          <span>Government Subtotal</span><span>{fmt(pricing.government_fees.subtotal)}</span>
                        </div>
                      </div>
                    </div>

                    {/* DSC */}
                    {config.showDSC && !hasDSC && pricing.dsc.total_dsc > 0 && (
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-semibold" style={{ color: "var(--color-accent-blue)" }}>DIGITAL SIGNATURE CERTIFICATES</span>
                          <span className="text-sm" style={{ color: "var(--color-text-muted)" }}>wholesale rate</span>
                        </div>
                        <div className="space-y-1">
                          <CostRow label={`DSC x ${pricing.dsc.num_directors} (2-year)`} amount={pricing.dsc.dsc_per_unit * pricing.dsc.num_directors} />
                          <CostRow label={`USB Tokens x ${pricing.dsc.num_directors}`} amount={pricing.dsc.token_per_unit * pricing.dsc.num_directors} />
                          <div className="flex justify-between p-2 rounded-lg font-medium mt-1" style={{ background: "rgba(59, 130, 246, 0.1)" }}>
                            <span>DSC Subtotal</span><span>{fmt(pricing.dsc.total_dsc)}</span>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Public Limited recurring */}
                    {entityType === "public_limited" && pricing.public_limited_recurring && (
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-semibold" style={{ color: "var(--color-accent-amber)" }}>ANNUAL RECURRING COSTS</span>
                          <span className="text-sm" style={{ color: "var(--color-text-muted)" }}>estimated</span>
                        </div>
                        <div className="space-y-1">
                          <CostRow label="Secretarial Audit (annual)" amount={pricing.public_limited_recurring.secretarial_audit_annual} />
                          <CostRow label="CS Compliance (annual)" amount={pricing.public_limited_recurring.cs_compliance_annual} />
                          <p className="text-xs mt-1 px-1" style={{ color: "var(--color-text-muted)" }}>{pricing.public_limited_recurring.note}</p>
                        </div>
                      </div>
                    )}

                    {/* Grand Total */}
                    <div className="flex justify-between items-center p-4 rounded-xl mt-4" style={{ background: "var(--gradient-primary)" }}>
                      <span className="text-lg font-bold">TOTAL</span>
                      <span className="text-2xl font-extrabold" style={{ fontFamily: "var(--font-display)" }}>{fmt(pricing.grand_total)}</span>
                    </div>

                    {/* Guarantees */}
                    <div className="space-y-2 mt-4">
                      {["No hidden fees", "Government fees at exact cost (\u20B90 markup)", ...(config.showDSC ? ["DSC at wholesale rate"] : [])].map((g) => (
                        <div key={g} className="flex items-center gap-2 text-sm" style={{ color: "var(--color-accent-emerald-light)" }}><Check className="w-4 h-4 shrink-0" />{g}</div>
                      ))}
                    </div>

                    {/* Competitive comparison */}
                    <div className="p-4 rounded-xl" style={{ background: "rgba(139, 92, 246, 0.06)", border: "1px solid rgba(139, 92, 246, 0.15)" }}>
                      <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}><strong style={{ color: "var(--color-text-primary)" }}>Compare:</strong> Vakilsearch charges {"\u20B9"}6,499&ndash;15,999 for the same incorporation.</p>
                    </div>

                    {/* Optimization Tip */}
                    {pricing.optimization_tip && pricing.optimization_tip.potential_saving > 0 && entityType !== "sole_proprietorship" && (
                      <div className="p-4 rounded-xl" style={{ background: "var(--color-warning-light)", border: "1px solid rgba(245, 158, 11, 0.3)" }}>
                        <p className="text-sm font-semibold mb-1" style={{ color: "var(--color-accent-amber)" }}>Cost Optimization Tip</p>
                        <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>Registering in <strong style={{ color: "var(--color-text-primary)" }}>{pricing.optimization_tip.cheapest_state_display}</strong> instead of <strong style={{ color: "var(--color-text-primary)" }}>{pricing.state_display}</strong> could save you <strong style={{ color: "var(--color-accent-emerald-light)" }}>{fmt(pricing.optimization_tip.potential_saving)}</strong> in stamp duty.</p>
                      </div>
                    )}

                    <button onClick={() => { localStorage.setItem("pending_company_draft", JSON.stringify({ entity_type: entityType, plan_tier: planTier, state, authorized_capital: capital, num_directors: numDirectors, pricing_snapshot: pricing })); router.push("/signup"); }}
                      className="btn-primary w-full text-center justify-center mt-4 text-lg !py-4">
                      {config.ctaLabel} &rarr;
                    </button>
                  </div>
                ) : (
                  <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>
                    <svg className="w-10 h-10 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    <p>Start the backend to see real-time pricing</p>
                    <code className="text-xs mt-2 block">cd backend && uvicorn src.main:app --reload --port 8000</code>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── SECTION 3: FAQ ── */}
      <section id="faq" className="py-16 scroll-mt-28">
        <div className="max-w-3xl mx-auto px-6">
          <SectionHeader
            title={<>Pricing <span className="gradient-text">FAQ</span></>}
          />
          <FAQAccordion items={FAQ_ITEMS} />
        </div>
      </section>

      {/* ─── Bottom CTA ─── */}
      <CTASection
        variant="purple"
        title="Start building today"
        subtitle="No credit card required. Get your compliance dashboard free."
        primaryCTA={{ label: "Get Started Free", href: "/signup" }}
      />

      <Footer />
      <ChatWidget />
    </div>
  );
}
