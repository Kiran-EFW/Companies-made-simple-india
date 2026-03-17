"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import type { PricingResponse, StateOption } from "@/lib/api";
import Header from "@/components/header";
import Footer from "@/components/footer";
import {
  BarChart3, Users, TrendingUp, Shield, Calculator, Calendar, FileText,
  FolderLock, BookOpen, Receipt, PenTool, UserCheck,
  Check, Star, Zap, Crown, Heart,
} from "lucide-react";

// ─── Section Navigation ─────────────────────────────────────────────────────

const SECTIONS = [
  { id: "platform", label: "Platform Features" },
  { id: "plans", label: "Compliance Plans" },
  { id: "incorporation", label: "Incorporation" },
  { id: "services", label: "Services & Add-Ons" },
];

// ─── Platform Features (included with every account) ────────────────────────

const PLATFORM_FEATURES = [
  { icon: <BarChart3 className="w-5 h-5" />, title: "Cap Table Management", desc: "Shareholders, dilution modeling, scenario comparison, share certificates", color: "purple" },
  { icon: <Users className="w-5 h-5" />, title: "ESOP Management", desc: "Plans, grants, vesting schedules, exercise workflows, FMV pricing", color: "blue" },
  { icon: <TrendingUp className="w-5 h-5" />, title: "Fundraising", desc: "Rounds, investor tracking, closing rooms, post-raise filings", color: "emerald" },
  { icon: <Shield className="w-5 h-5" />, title: "Compliance Calendar", desc: "Auto-generated tasks, deadline tracking, escalation alerts", color: "purple" },
  { icon: <Calculator className="w-5 h-5" />, title: "Valuations", desc: "Rule 11UA NAV & DCF methods, ESOP FMV integration", color: "blue" },
  { icon: <UserCheck className="w-5 h-5" />, title: "Stakeholder Management", desc: "Shareholders, directors, auditors, KYC documents", color: "emerald" },
  { icon: <Calendar className="w-5 h-5" />, title: "Board Meetings", desc: "Scheduling, notices, attendance, minutes, resolutions", color: "purple" },
  { icon: <FileText className="w-5 h-5" />, title: "Legal Documents & E-Sign", desc: "AI-drafted contracts, e-signatures, template library", color: "blue" },
  { icon: <FolderLock className="w-5 h-5" />, title: "Data Room", desc: "Secure sharing, time-limited links, access tracking", color: "emerald" },
  { icon: <Receipt className="w-5 h-5" />, title: "GST & Tax Dashboard", desc: "Returns tracking, TDS, advance tax, filing status", color: "purple" },
  { icon: <BookOpen className="w-5 h-5" />, title: "Accounting Integration", desc: "Zoho Books & Tally sync, financial dashboards", color: "blue" },
  { icon: <PenTool className="w-5 h-5" />, title: "Statutory Registers", desc: "Members, directors, shares, charges registers", color: "emerald" },
];

const USER_TYPES = [
  { label: "Founders", desc: "Full access to all platform features. Manage your company's equity, compliance, and back-office.", href: "/for/founders" },
  { label: "Investors", desc: "Token-based portal. View portfolio companies, cap tables, funding rounds, and documents — no login needed.", href: "/for/investors" },
  { label: "CAs & CSs", desc: "Multi-client dashboard. Track compliance tasks, filings, and deadlines across all your clients.", href: "/for/cas" },
];

// ─── Compliance Subscription Plans ──────────────────────────────────────────

const SUBSCRIPTION_PLANS = [
  {
    key: "starter",
    name: "Starter",
    icon: <Zap className="w-5 h-5" />,
    target: "Sole Proprietorship & Partnership",
    monthlyPrice: 999,
    annualPrice: 9999,
    highlighted: false,
    features: [
      "Income Tax Return filing",
      "GST return filing (if applicable)",
      "Basic bookkeeping (up to 50 txns/month)",
      "Compliance calendar with reminders",
      "Dedicated relationship manager",
    ],
  },
  {
    key: "growth",
    name: "Growth",
    icon: <Star className="w-5 h-5" />,
    target: "LLP & One Person Company",
    monthlyPrice: 2999,
    annualPrice: 29999,
    highlighted: true,
    features: [
      "All annual ROC/MCA filings",
      "Income Tax Return filing",
      "GST return filing (monthly)",
      "TDS quarterly returns",
      "DIR-3 KYC for all partners/directors",
      "Bookkeeping (up to 200 txns/month)",
      "Compliance calendar with email alerts",
      "Priority support",
    ],
  },
  {
    key: "scale",
    name: "Scale",
    icon: <TrendingUp className="w-5 h-5" />,
    target: "Private Limited Company",
    monthlyPrice: 4999,
    annualPrice: 49999,
    highlighted: false,
    features: [
      "All annual ROC filings (AOC-4, MGT-7)",
      "ADT-1 auditor appointment",
      "Income Tax Return (ITR-6)",
      "GST return filing (monthly)",
      "TDS quarterly returns",
      "DIR-3 KYC for all directors",
      "Statutory audit coordination",
      "Bookkeeping (up to 500 txns/month)",
      "Board meeting documentation (4/year)",
      "Compliance autopilot with penalty alerts",
      "Dedicated CA + relationship manager",
    ],
  },
  {
    key: "enterprise",
    name: "Enterprise",
    icon: <Crown className="w-5 h-5" />,
    target: "Public Limited & Section 8",
    monthlyPrice: 9999,
    annualPrice: 99999,
    highlighted: false,
    features: [
      "Everything in Scale plan",
      "Secretarial audit (MR-3)",
      "Company Secretary compliance",
      "Corporate governance reporting",
      "12A / 80G registration & renewal (Section 8)",
      "Bookkeeping (unlimited transactions)",
      "Payroll processing (up to 25 employees)",
      "Quarterly board meeting packs",
      "Dedicated CS + CA + relationship manager",
    ],
  },
  {
    key: "peace_of_mind",
    name: "Peace of Mind",
    icon: <Heart className="w-5 h-5" />,
    target: "All Entity Types",
    monthlyPrice: 9999,
    annualPrice: 99999,
    highlighted: false,
    features: [
      "All ROC / MCA annual filings",
      "Income Tax Return filing",
      "GST monthly + annual return filing",
      "TDS quarterly return filing",
      "DIR-3 KYC for all directors / partners",
      "ADT-1 auditor appointment filing",
      "Statutory audit coordination",
      "Board meeting documentation (4/year)",
      "INC-20A commencement filing",
      "MSME / Udyam registration included",
      "2 free event-based filings per year",
      "Zoho Books / Tally integration",
      "Compliance autopilot",
      "Tax planning advisory (quarterly)",
      "Penalty protection (up to ₹25,000/yr)",
      "Same-day response SLA",
      "Quarterly compliance health reports",
      "Dedicated CA + CS + relationship manager",
    ],
    note: "Bookkeeping, payroll, and trademark available as add-ons",
  },
];

// ─── Incorporation Calculator Data ──────────────────────────────────────────

const ENTITY_TYPES = [
  { value: "private_limited", label: "Private Limited" },
  { value: "public_limited", label: "Public Limited" },
  { value: "opc", label: "OPC" },
  { value: "llp", label: "LLP" },
  { value: "partnership", label: "Partnership" },
  { value: "section_8", label: "Section 8" },
  { value: "sole_proprietorship", label: "Sole Prop" },
];

const PLAN_TIERS = [
  {
    value: "launch", label: "Launch",
    desc: "AI-guided incorporation + CS review",
    descByEntity: {
      sole_proprietorship: "GST + Udyam + Shop & Establishment registration",
      partnership: "Deed drafting + ROF registration + PAN",
    } as Record<string, string>,
  },
  {
    value: "grow", label: "Grow",
    desc: "Launch + GST + DPIIT + 90-day compliance",
    descByEntity: {
      sole_proprietorship: "Launch + FSSAI/trade license + 90-day support",
      partnership: "Launch + GST + 90-day compliance",
    } as Record<string, string>,
  },
  {
    value: "scale", label: "Scale",
    desc: "Grow + 1-year compliance + dedicated RM",
    descByEntity: {
      partnership: "Grow + 1-year compliance + dedicated RM",
    } as Record<string, string>,
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

const ENTITY_CONFIG: Record<string, {
  capitalLabel: string; personLabel: string; personLabelPlural: string;
  minPersons: number; maxPersons: number; showCapital: boolean;
  showPersonCount: boolean; showDSC: boolean; hasScale: boolean;
  filingLabel: string; rocLabel: string; nameResLabel: string;
  stampDutyLabel: string; panTanLabel: string; ctaLabel: string;
}> = {
  private_limited: { capitalLabel: "Authorized Capital", personLabel: "Director", personLabelPlural: "Directors", minPersons: 2, maxPersons: 15, showCapital: true, showPersonCount: true, showDSC: true, hasScale: true, filingLabel: "SPICe+ Filing", rocLabel: "ROC Registration", nameResLabel: "MCA Name Reservation", stampDutyLabel: "Stamp Duty (MOA + AOA)", panTanLabel: "PAN + TAN Application", ctaLabel: "Proceed to Incorporate" },
  public_limited: { capitalLabel: "Authorized Capital", personLabel: "Director", personLabelPlural: "Directors", minPersons: 3, maxPersons: 15, showCapital: true, showPersonCount: true, showDSC: true, hasScale: true, filingLabel: "SPICe+ Filing", rocLabel: "ROC Registration", nameResLabel: "MCA Name Reservation", stampDutyLabel: "Stamp Duty (MOA + AOA)", panTanLabel: "PAN + TAN Application", ctaLabel: "Proceed to Incorporate" },
  opc: { capitalLabel: "Authorized Capital", personLabel: "Director", personLabelPlural: "Director", minPersons: 1, maxPersons: 1, showCapital: true, showPersonCount: false, showDSC: true, hasScale: true, filingLabel: "SPICe+ Filing", rocLabel: "ROC Registration", nameResLabel: "MCA Name Reservation", stampDutyLabel: "Stamp Duty (MOA + AOA)", panTanLabel: "PAN + TAN Application", ctaLabel: "Proceed to Incorporate" },
  llp: { capitalLabel: "Capital Contribution", personLabel: "Partner", personLabelPlural: "Partners", minPersons: 2, maxPersons: 10, showCapital: true, showPersonCount: true, showDSC: true, hasScale: true, filingLabel: "FiLLiP Filing", rocLabel: "", nameResLabel: "RUN-LLP Name Reservation", stampDutyLabel: "Stamp Duty (LLP Agreement)", panTanLabel: "PAN + TAN Application", ctaLabel: "Proceed to Register" },
  partnership: { capitalLabel: "Capital Contribution", personLabel: "Partner", personLabelPlural: "Partners", minPersons: 2, maxPersons: 20, showCapital: true, showPersonCount: true, showDSC: false, hasScale: true, filingLabel: "", rocLabel: "Registrar of Firms Fee", nameResLabel: "", stampDutyLabel: "Stamp Duty (Partnership Deed)", panTanLabel: "PAN Application", ctaLabel: "Proceed to Register" },
  section_8: { capitalLabel: "Authorized Capital", personLabel: "Director", personLabelPlural: "Directors", minPersons: 2, maxPersons: 15, showCapital: true, showPersonCount: true, showDSC: true, hasScale: true, filingLabel: "SPICe+ Filing", rocLabel: "ROC Registration", nameResLabel: "MCA Name Reservation", stampDutyLabel: "Stamp Duty (MOA + AOA)", panTanLabel: "PAN + TAN Application", ctaLabel: "Proceed to Incorporate" },
  sole_proprietorship: { capitalLabel: "", personLabel: "Proprietor", personLabelPlural: "Proprietor", minPersons: 1, maxPersons: 1, showCapital: false, showPersonCount: false, showDSC: false, hasScale: false, filingLabel: "", rocLabel: "", nameResLabel: "", stampDutyLabel: "", panTanLabel: "PAN Application", ctaLabel: "Proceed to Register" },
};

// ─── Services Catalog ───────────────────────────────────────────────────────

interface Service {
  name: string;
  desc: string;
  platformFee: number;
  govtFee: number;
  frequency: string;
  badge?: string;
}

const SERVICES_BY_CATEGORY: Record<string, { label: string; services: Service[] }> = {
  registration: {
    label: "Registration Services",
    services: [
      { name: "GST Registration", desc: "GSTIN allocation", platformFee: 1499, govtFee: 0, frequency: "one-time", badge: "popular" },
      { name: "MSME / Udyam Registration", desc: "MSME benefits & subsidies", platformFee: 499, govtFee: 0, frequency: "one-time", badge: "recommended" },
      { name: "Trademark Registration", desc: "Brand name & logo protection", platformFee: 4999, govtFee: 4500, frequency: "one-time", badge: "popular" },
      { name: "Import Export Code (IEC)", desc: "DGFT registration", platformFee: 1999, govtFee: 500, frequency: "one-time" },
      { name: "FSSAI Basic Registration", desc: "Food safety (turnover < ₹12L)", platformFee: 2499, govtFee: 100, frequency: "one-time" },
      { name: "FSSAI State License", desc: "Food license (₹12L–₹20Cr)", platformFee: 5999, govtFee: 2000, frequency: "one-time" },
      { name: "DPIIT Startup Recognition", desc: "Tax benefits & fast-track patents", platformFee: 2999, govtFee: 0, frequency: "one-time", badge: "recommended" },
      { name: "Professional Tax Registration", desc: "State-level employer registration", platformFee: 1499, govtFee: 0, frequency: "one-time" },
      { name: "ESI Registration", desc: "Employee State Insurance (10+ employees)", platformFee: 2499, govtFee: 0, frequency: "one-time" },
      { name: "EPFO / PF Registration", desc: "Provident Fund (20+ employees)", platformFee: 2499, govtFee: 0, frequency: "one-time" },
      { name: "ISO 9001 Certification", desc: "Quality management certification", platformFee: 19999, govtFee: 0, frequency: "one-time" },
    ],
  },
  compliance: {
    label: "Compliance Services",
    services: [
      { name: "Annual ROC Filing (AOC-4 + MGT-7)", desc: "Financial statements & annual return", platformFee: 7999, govtFee: 600, frequency: "annual", badge: "mandatory" },
      { name: "LLP Annual Filing (Form 8 + Form 11)", desc: "LLP accounts & annual return", platformFee: 5999, govtFee: 200, frequency: "annual", badge: "mandatory" },
      { name: "DIR-3 KYC (Per Director)", desc: "Annual DIN KYC filing", platformFee: 999, govtFee: 0, frequency: "annual", badge: "mandatory" },
      { name: "ADT-1 Auditor Appointment", desc: "Auditor appointment notice", platformFee: 1999, govtFee: 300, frequency: "annual" },
      { name: "INC-20A Commencement of Business", desc: "180-day mandatory filing", platformFee: 1999, govtFee: 500, frequency: "one-time", badge: "mandatory" },
    ],
  },
  tax: {
    label: "Tax Services",
    services: [
      { name: "ITR Filing (Company — ITR-6)", desc: "Company income tax return", platformFee: 9999, govtFee: 0, frequency: "annual", badge: "mandatory" },
      { name: "ITR Filing (LLP/Partnership — ITR-5)", desc: "LLP/partnership income tax", platformFee: 5999, govtFee: 0, frequency: "annual", badge: "mandatory" },
      { name: "ITR Filing (Individual/Sole Prop)", desc: "ITR-3 or ITR-4 filing", platformFee: 2499, govtFee: 0, frequency: "annual" },
      { name: "GST Monthly Return Filing", desc: "GSTR-1 + GSTR-3B monthly", platformFee: 1999, govtFee: 0, frequency: "monthly", badge: "popular" },
      { name: "TDS Quarterly Return Filing", desc: "Form 24Q/26Q quarterly", platformFee: 2499, govtFee: 0, frequency: "quarterly" },
      { name: "GST Annual Return (GSTR-9)", desc: "Annual GST consolidation", platformFee: 4999, govtFee: 0, frequency: "annual" },
      { name: "Statutory Audit", desc: "Annual financial audit by CA", platformFee: 14999, govtFee: 0, frequency: "annual" },
    ],
  },
  accounting: {
    label: "Accounting & Payroll",
    services: [
      { name: "Monthly Bookkeeping (Basic)", desc: "Up to 100 transactions/month", platformFee: 2999, govtFee: 0, frequency: "monthly", badge: "popular" },
      { name: "Monthly Bookkeeping (Standard)", desc: "100–500 transactions with reconciliation", platformFee: 5999, govtFee: 0, frequency: "monthly" },
      { name: "Payroll Processing", desc: "Salary slips, PF/ESI challans, Form 16", platformFee: 1999, govtFee: 0, frequency: "monthly" },
    ],
  },
  amendment: {
    label: "Amendments & Changes",
    services: [
      { name: "Director Appointment / Resignation", desc: "DIR-12 filing with ROC", platformFee: 3499, govtFee: 600, frequency: "one-time" },
      { name: "Share Transfer", desc: "SH-4 deed + PAS-3 filing", platformFee: 4999, govtFee: 400, frequency: "one-time" },
      { name: "Share Allotment (New Shares)", desc: "PAS-3 + updated certificates", platformFee: 5999, govtFee: 600, frequency: "one-time" },
      { name: "Increase Authorised Capital", desc: "SH-7 filing with ROC", platformFee: 5999, govtFee: 5000, frequency: "one-time" },
      { name: "Registered Office Change", desc: "INC-22 / INC-23 filing", platformFee: 3499, govtFee: 600, frequency: "one-time" },
      { name: "Company Name Change", desc: "Name change with ROC approval", platformFee: 5999, govtFee: 1000, frequency: "one-time" },
      { name: "Company Closure / Strike Off", desc: "Voluntary strike-off (STK-2)", platformFee: 7999, govtFee: 5000, frequency: "one-time" },
      { name: "LLP Partner Addition / Removal", desc: "Form 4 filing", platformFee: 3499, govtFee: 100, frequency: "one-time" },
    ],
  },
  legal: {
    label: "Legal Services",
    services: [
      { name: "Trademark Objection Reply", desc: "Reply to examination objection", platformFee: 4999, govtFee: 0, frequency: "one-time" },
      { name: "Legal Notice Drafting", desc: "Professional notice drafting & dispatch", platformFee: 3499, govtFee: 0, frequency: "one-time" },
      { name: "Virtual Registered Office", desc: "Virtual address with mail handling", platformFee: 7999, govtFee: 0, frequency: "annual" },
    ],
  },
};

// ─── Helpers ────────────────────────────────────────────────────────────────

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount);
}

function formatFrequency(f: string): string {
  switch (f) {
    case "monthly": return "/mo";
    case "quarterly": return "/qtr";
    case "annual": return "/yr";
    default: return "";
  }
}

const COLOR_BG: Record<string, string> = { purple: "bg-purple-50", blue: "bg-blue-50", emerald: "bg-emerald-50" };
const COLOR_TEXT: Record<string, string> = { purple: "text-purple-600", blue: "text-blue-600", emerald: "text-emerald-600" };

// ─── Page Component ─────────────────────────────────────────────────────────

export default function PricingPage() {
  const router = useRouter();
  const [activeSection, setActiveSection] = useState("platform");
  const [billingCycle, setBillingCycle] = useState<"monthly" | "annual">("annual");

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
    } catch { /* Backend offline — show UI anyway */ }
  }

  function scrollToSection(id: string) {
    setActiveSection(id);
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  return (
    <div className="min-h-screen">
      <Header />

      {/* ─── Hero ─── */}
      <div className="max-w-7xl mx-auto px-6 pt-12 pb-6 text-center">
        <h1 className="text-4xl md:text-5xl font-bold mb-3" style={{ fontFamily: "var(--font-display)" }}>
          <span className="gradient-text">Transparent</span> Pricing
        </h1>
        <p className="text-lg max-w-2xl mx-auto" style={{ color: "var(--color-text-secondary)" }}>
          Platform features, compliance plans, incorporation costs, and add-on services.
          Government fees at exact cost — zero markup.
        </p>
      </div>

      {/* ─── Section Nav ─── */}
      <div className="sticky top-16 z-40 backdrop-blur-sm border-b" style={{ backgroundColor: "var(--color-bg-primary)", borderColor: "var(--color-border)" }}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1 overflow-x-auto py-2">
            {SECTIONS.map((s) => (
              <button
                key={s.id}
                onClick={() => scrollToSection(s.id)}
                className="px-4 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-colors"
                style={{
                  backgroundColor: activeSection === s.id ? "rgba(139, 92, 246, 0.15)" : "transparent",
                  color: activeSection === s.id ? "var(--color-accent-purple)" : "var(--color-text-secondary)",
                }}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ═══════════════════════════════════════════════════════════════════════
          SECTION 1: Platform Features
          ═══════════════════════════════════════════════════════════════════════ */}
      <section id="platform" className="py-16 scroll-mt-28">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-10">
            <h2 className="text-2xl md:text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>
              Platform Features — <span className="gradient-text">Included Free</span>
            </h2>
            <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
              Every Anvils account includes the full platform. No per-feature charges.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mb-12">
            {PLATFORM_FEATURES.map((f) => (
              <div key={f.title} className="card-static p-5">
                <div className={`w-9 h-9 rounded-lg flex items-center justify-center mb-3 ${COLOR_BG[f.color]}`}>
                  <div className={COLOR_TEXT[f.color]}>{f.icon}</div>
                </div>
                <h3 className="text-sm font-bold text-gray-900 mb-1">{f.title}</h3>
                <p className="text-xs text-gray-500">{f.desc}</p>
              </div>
            ))}
          </div>

          {/* User Types */}
          <div className="text-center mb-6">
            <h3 className="text-lg font-bold text-gray-900 mb-1" style={{ fontFamily: "var(--font-display)" }}>
              Built for everyone in the ecosystem
            </h3>
          </div>
          <div className="grid md:grid-cols-3 gap-4">
            {USER_TYPES.map((u) => (
              <a key={u.label} href={u.href} className="card-static p-5 group">
                <h4 className="text-sm font-bold text-gray-900 mb-1 group-hover:text-purple-600 transition-colors">{u.label}</h4>
                <p className="text-xs text-gray-500">{u.desc}</p>
              </a>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════════
          SECTION 2: Compliance Subscription Plans
          ═══════════════════════════════════════════════════════════════════════ */}
      <section id="plans" className="py-16 bg-gray-50 scroll-mt-28">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-8">
            <h2 className="text-2xl md:text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>
              Compliance <span className="gradient-text">Subscription Plans</span>
            </h2>
            <p className="text-sm mb-6" style={{ color: "var(--color-text-muted)" }}>
              Ongoing compliance handled by verified CAs. Filings, returns, bookkeeping — on autopilot.
            </p>

            {/* Billing toggle */}
            <div className="inline-flex items-center rounded-xl p-1" style={{ border: "1px solid var(--color-border)", backgroundColor: "var(--color-bg-card)" }}>
              <button
                onClick={() => setBillingCycle("monthly")}
                className="px-4 py-2 text-sm font-medium rounded-lg transition-colors"
                style={{
                  backgroundColor: billingCycle === "monthly" ? "rgba(139, 92, 246, 0.15)" : "transparent",
                  color: billingCycle === "monthly" ? "var(--color-accent-purple)" : "var(--color-text-secondary)",
                }}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingCycle("annual")}
                className="px-4 py-2 text-sm font-medium rounded-lg transition-colors"
                style={{
                  backgroundColor: billingCycle === "annual" ? "rgba(139, 92, 246, 0.15)" : "transparent",
                  color: billingCycle === "annual" ? "var(--color-accent-purple)" : "var(--color-text-secondary)",
                }}
              >
                Annual <span className="text-xs ml-1" style={{ color: "var(--color-accent-emerald-light)" }}>Save ~17%</span>
              </button>
            </div>
          </div>

          {/* Plan Cards — first 4 plans */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
            {SUBSCRIPTION_PLANS.slice(0, 4).map((plan) => (
              <div
                key={plan.key}
                className="rounded-2xl p-6 flex flex-col"
                style={{
                  backgroundColor: "var(--color-bg-card)",
                  border: plan.highlighted ? "2px solid var(--color-accent-purple)" : "1px solid var(--color-border)",
                }}
              >
                {plan.highlighted && (
                  <div className="text-xs font-semibold mb-3 px-2 py-1 rounded-full self-start" style={{ backgroundColor: "rgba(139, 92, 246, 0.15)", color: "var(--color-accent-purple)" }}>
                    Most Popular
                  </div>
                )}
                <div className="flex items-center gap-2 mb-1">
                  <div style={{ color: "var(--color-accent-purple)" }}>{plan.icon}</div>
                  <h3 className="text-lg font-bold text-gray-900">{plan.name}</h3>
                </div>
                <p className="text-xs text-gray-500 mb-4">{plan.target}</p>

                <div className="mb-4">
                  <span className="text-3xl font-bold text-gray-900" style={{ fontFamily: "var(--font-display)" }}>
                    {formatCurrency(billingCycle === "annual" ? plan.annualPrice : plan.monthlyPrice)}
                  </span>
                  <span className="text-sm text-gray-500">
                    {billingCycle === "annual" ? "/year" : "/month"}
                  </span>
                  {billingCycle === "annual" && (
                    <div className="text-xs text-gray-400 mt-0.5">
                      {formatCurrency(Math.round(plan.annualPrice / 12))}/month billed annually
                    </div>
                  )}
                </div>

                <ul className="space-y-2 flex-1 mb-6">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-xs text-gray-600">
                      <Check className="w-3.5 h-3.5 mt-0.5 shrink-0 text-emerald-500" />
                      {f}
                    </li>
                  ))}
                </ul>

                <a
                  href="/signup"
                  className={plan.highlighted ? "btn-primary w-full text-center text-sm" : "block text-center text-sm font-medium py-2.5 rounded-xl transition-colors"}
                  style={plan.highlighted ? {} : { border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                >
                  Get Started
                </a>
              </div>
            ))}
          </div>

          {/* Peace of Mind — Full Width Card */}
          {SUBSCRIPTION_PLANS.filter((p) => p.key === "peace_of_mind").map((plan) => (
            <div
              key={plan.key}
              className="rounded-2xl p-8"
              style={{ background: "var(--gradient-primary)", border: "1px solid var(--color-border)" }}
            >
              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <div style={{ color: "var(--color-accent-purple)" }}>{plan.icon}</div>
                    <h3 className="text-xl font-bold" style={{ fontFamily: "var(--font-display)" }}>{plan.name}</h3>
                  </div>
                  <p className="text-sm text-gray-500 mb-4">{plan.target} — Total Compliance Coverage</p>
                  <div className="mb-4">
                    <span className="text-3xl font-bold text-gray-900" style={{ fontFamily: "var(--font-display)" }}>
                      {formatCurrency(billingCycle === "annual" ? plan.annualPrice : plan.monthlyPrice)}
                    </span>
                    <span className="text-sm text-gray-500">{billingCycle === "annual" ? "/year" : "/month"}</span>
                  </div>
                  {plan.note && <p className="text-xs text-gray-400 mb-4">{plan.note}</p>}
                  <a href="/signup" className="btn-primary inline-block text-center text-sm">Get Peace of Mind</a>
                </div>
                <div>
                  <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {plan.features.map((f) => (
                      <li key={f} className="flex items-start gap-2 text-xs text-gray-600">
                        <Check className="w-3.5 h-3.5 mt-0.5 shrink-0 text-emerald-500" />
                        {f}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════════
          SECTION 3: Incorporation Calculator
          ═══════════════════════════════════════════════════════════════════════ */}
      <section id="incorporation" className="py-16 scroll-mt-28">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-10">
            <h2 className="text-2xl md:text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>
              Incorporation <span className="gradient-text">Cost Calculator</span>
            </h2>
            <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
              Real costs, zero surprises. Configure your entity and see the exact breakdown.
            </p>
          </div>

          <div className="grid lg:grid-cols-5 gap-8">
            {/* Left: Configuration */}
            <div className="lg:col-span-2 space-y-6">
              <div className="glass-card p-6" style={{ cursor: "default" }}>
                <label className="text-sm font-semibold mb-3 block" style={{ color: "var(--color-text-secondary)" }}>Entity Type</label>
                <div className="grid grid-cols-2 gap-2">
                  {ENTITY_TYPES.map((e) => (
                    <button key={e.value} onClick={() => setEntityType(e.value)} className="p-3 rounded-xl text-left transition-all text-sm" style={{ background: entityType === e.value ? "rgba(139, 92, 246, 0.2)" : "var(--color-hover-overlay)", border: `1px solid ${entityType === e.value ? "rgba(139, 92, 246, 0.5)" : "var(--color-border)"}` }}>
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
                      <button key={p.value} onClick={() => setPlanTier(p.value)} className="w-full p-3 rounded-xl text-left transition-all" style={{ background: planTier === p.value ? "rgba(139, 92, 246, 0.2)" : "var(--color-hover-overlay)", border: `1px solid ${planTier === p.value ? "rgba(139, 92, 246, 0.5)" : "var(--color-border)"}` }}>
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
                <select value={state} onChange={(e) => setState(e.target.value)} className="w-full p-3 rounded-xl text-sm" style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}>
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
                          <select value={capital} onChange={(e) => setCapital(Number(e.target.value))} className="w-full p-3 rounded-xl text-sm" style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}>
                            {CAPITAL_OPTIONS.map((c) => (<option key={c.value} value={c.value}>{c.label}</option>))}
                          </select>
                        </div>
                      )}
                      {config.showPersonCount && (
                        <div>
                          <label className="text-sm font-semibold mb-2 block" style={{ color: "var(--color-text-secondary)" }}>{config.personLabelPlural}</label>
                          <select value={numDirectors} onChange={(e) => setNumDirectors(Number(e.target.value))} className="w-full p-3 rounded-xl text-sm" style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}>
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
                <h2 className="text-xl font-bold mb-6" style={{ fontFamily: "var(--font-display)" }}>
                  Your {entityType === "sole_proprietorship" || entityType === "partnership" ? "Registration" : "Incorporation"} Cost Breakdown
                </h2>

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
                        <span className="font-bold">{formatCurrency(pricing.platform_fee)}</span>
                      </div>
                    </div>

                    {/* Government Fees */}
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-semibold" style={{ color: "var(--color-accent-emerald-light)" }}>GOVERNMENT FEES</span>
                        <span className="text-sm" style={{ color: "var(--color-text-muted)" }}>pass-through, ₹0 markup</span>
                      </div>
                      <div className="space-y-1">
                        {pricing.government_fees.name_reservation > 0 && (
                          <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
                            <span style={{ color: "var(--color-text-secondary)" }}>{config.nameResLabel}</span>
                            <span>{formatCurrency(pricing.government_fees.name_reservation)}</span>
                          </div>
                        )}
                        {pricing.government_fees.filing_fee > 0 && (
                          <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
                            <span style={{ color: "var(--color-text-secondary)" }}>{config.filingLabel}</span>
                            <span>{formatCurrency(pricing.government_fees.filing_fee)}</span>
                          </div>
                        )}
                        {pricing.government_fees.roc_registration > 0 && (
                          <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
                            <span style={{ color: "var(--color-text-secondary)" }}>{config.rocLabel || "ROC Registration"}</span>
                            <span>{formatCurrency(pricing.government_fees.roc_registration)}</span>
                          </div>
                        )}
                        {pricing.government_fees.section8_license > 0 && (
                          <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
                            <span style={{ color: "var(--color-text-secondary)" }}>INC-12 License Fee</span>
                            <span>{formatCurrency(pricing.government_fees.section8_license)}</span>
                          </div>
                        )}
                        {pricing.government_fees.stamp_duty.total_stamp_duty > 0 && (
                          <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
                            <span style={{ color: "var(--color-text-secondary)" }}>{config.stampDutyLabel} ({pricing.state_display})</span>
                            <span>{formatCurrency(pricing.government_fees.stamp_duty.total_stamp_duty)}</span>
                          </div>
                        )}
                        {pricing.government_fees.pan_tan > 0 && (
                          <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
                            <span style={{ color: "var(--color-text-secondary)" }}>{config.panTanLabel}</span>
                            <span>{formatCurrency(pricing.government_fees.pan_tan)}</span>
                          </div>
                        )}
                        <div className="flex justify-between p-2 rounded-lg font-medium mt-1" style={{ background: "rgba(16, 185, 129, 0.1)" }}>
                          <span>Government Subtotal</span>
                          <span>{formatCurrency(pricing.government_fees.subtotal)}</span>
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
                          <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
                            <span style={{ color: "var(--color-text-secondary)" }}>DSC × {pricing.dsc.num_directors} (2-year)</span>
                            <span>{formatCurrency(pricing.dsc.dsc_per_unit * pricing.dsc.num_directors)}</span>
                          </div>
                          <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
                            <span style={{ color: "var(--color-text-secondary)" }}>USB Tokens × {pricing.dsc.num_directors}</span>
                            <span>{formatCurrency(pricing.dsc.token_per_unit * pricing.dsc.num_directors)}</span>
                          </div>
                          <div className="flex justify-between p-2 rounded-lg font-medium mt-1" style={{ background: "rgba(59, 130, 246, 0.1)" }}>
                            <span>DSC Subtotal</span>
                            <span>{formatCurrency(pricing.dsc.total_dsc)}</span>
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
                          <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
                            <span style={{ color: "var(--color-text-secondary)" }}>Secretarial Audit (annual)</span>
                            <span>{formatCurrency(pricing.public_limited_recurring.secretarial_audit_annual)}</span>
                          </div>
                          <div className="flex justify-between p-2 rounded" style={{ background: "var(--color-stripe-alt)" }}>
                            <span style={{ color: "var(--color-text-secondary)" }}>CS Compliance (annual)</span>
                            <span>{formatCurrency(pricing.public_limited_recurring.cs_compliance_annual)}</span>
                          </div>
                          <div className="text-xs mt-1 px-1" style={{ color: "var(--color-text-muted)" }}>{pricing.public_limited_recurring.note}</div>
                        </div>
                      </div>
                    )}

                    {/* Grand Total */}
                    <div className="flex justify-between items-center p-4 rounded-xl mt-4" style={{ background: "var(--gradient-primary)" }}>
                      <span className="text-lg font-bold">TOTAL</span>
                      <span className="text-2xl font-extrabold" style={{ fontFamily: "var(--font-display)" }}>{formatCurrency(pricing.grand_total)}</span>
                    </div>

                    {/* Guarantees */}
                    <div className="space-y-2 mt-4">
                      {["No hidden fees", "Government fees at exact cost (₹0 markup)", ...(config.showDSC ? ["DSC at wholesale rate"] : [])].map((g) => (
                        <div key={g} className="flex items-center gap-2 text-sm" style={{ color: "var(--color-accent-emerald-light)" }}>
                          <Check className="w-4 h-4 shrink-0" />
                          {g}
                        </div>
                      ))}
                    </div>

                    {/* Optimization Tip */}
                    {pricing.optimization_tip && pricing.optimization_tip.potential_saving > 0 && entityType !== "sole_proprietorship" && (
                      <div className="p-4 rounded-xl mt-2" style={{ background: "var(--color-warning-light)", border: "1px solid rgba(245, 158, 11, 0.3)" }}>
                        <div className="text-sm font-semibold mb-1" style={{ color: "var(--color-accent-amber)" }}>Cost Optimization Tip</div>
                        <div className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
                          Registering in <strong style={{ color: "var(--color-text-primary)" }}>{pricing.optimization_tip.cheapest_state_display}</strong> instead of <strong style={{ color: "var(--color-text-primary)" }}>{pricing.state_display}</strong> could save you <strong style={{ color: "var(--color-accent-emerald-light)" }}>{formatCurrency(pricing.optimization_tip.potential_saving)}</strong> in stamp duty.
                        </div>
                      </div>
                    )}

                    <button
                      onClick={() => {
                        if (!pricing) return;
                        localStorage.setItem("pending_company_draft", JSON.stringify({ entity_type: entityType, plan_tier: planTier, state, authorized_capital: capital, num_directors: numDirectors, pricing_snapshot: pricing }));
                        router.push("/signup");
                      }}
                      className="btn-primary w-full text-center justify-center mt-4 text-lg !py-4"
                    >
                      {config.ctaLabel} →
                    </button>
                  </div>
                ) : (
                  <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>
                    <div className="mb-4">
                      <svg className="w-10 h-10 mx-auto" style={{ color: "var(--color-text-muted)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <p>Start the backend to see real-time pricing</p>
                    <code className="text-xs mt-2 block" style={{ color: "var(--color-text-muted)" }}>cd backend && uvicorn src.main:app --reload --port 8000</code>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════════
          SECTION 4: Services & Add-Ons Catalog
          ═══════════════════════════════════════════════════════════════════════ */}
      <section id="services" className="py-16 bg-gray-50 scroll-mt-28">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-10">
            <h2 className="text-2xl md:text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>
              Services & <span className="gradient-text">Add-Ons</span>
            </h2>
            <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
              One-time registrations, filings, amendments, and professional services. Order from your dashboard.
            </p>
          </div>

          {Object.entries(SERVICES_BY_CATEGORY).map(([catKey, category]) => (
            <div key={catKey} className="mb-10">
              <h3 className="text-lg font-bold text-gray-900 mb-4" style={{ fontFamily: "var(--font-display)" }}>
                {category.label}
              </h3>
              <div className="rounded-xl overflow-hidden" style={{ border: "1px solid var(--color-border)" }}>
                {/* Table header */}
                <div className="hidden md:grid grid-cols-12 gap-4 px-5 py-3 text-xs font-semibold uppercase tracking-wider" style={{ backgroundColor: "var(--color-bg-secondary)", color: "var(--color-text-muted)" }}>
                  <div className="col-span-5">Service</div>
                  <div className="col-span-2 text-right">Platform Fee</div>
                  <div className="col-span-2 text-right">Govt Fee</div>
                  <div className="col-span-2 text-right">Total</div>
                  <div className="col-span-1 text-right">Freq.</div>
                </div>
                {/* Rows */}
                {category.services.map((svc, i) => (
                  <div
                    key={svc.name}
                    className="grid grid-cols-1 md:grid-cols-12 gap-2 md:gap-4 px-5 py-4 items-center"
                    style={{
                      backgroundColor: i % 2 === 0 ? "var(--color-bg-card)" : "var(--color-bg-secondary)",
                      borderTop: i > 0 ? "1px solid var(--color-border)" : undefined,
                    }}
                  >
                    <div className="md:col-span-5">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-900">{svc.name}</span>
                        {svc.badge && (
                          <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-full" style={{
                            backgroundColor: svc.badge === "mandatory" ? "rgba(239, 68, 68, 0.12)" : svc.badge === "popular" ? "rgba(139, 92, 246, 0.12)" : "rgba(16, 185, 129, 0.12)",
                            color: svc.badge === "mandatory" ? "#ef4444" : svc.badge === "popular" ? "var(--color-accent-purple)" : "#10b981",
                          }}>
                            {svc.badge}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 mt-0.5">{svc.desc}</p>
                    </div>
                    <div className="md:col-span-2 md:text-right">
                      <span className="md:hidden text-xs text-gray-400">Platform: </span>
                      <span className="text-sm font-medium text-gray-900">{formatCurrency(svc.platformFee)}</span>
                    </div>
                    <div className="md:col-span-2 md:text-right">
                      <span className="md:hidden text-xs text-gray-400">Govt: </span>
                      <span className="text-sm text-gray-500">{svc.govtFee > 0 ? formatCurrency(svc.govtFee) : "₹0"}</span>
                    </div>
                    <div className="md:col-span-2 md:text-right">
                      <span className="md:hidden text-xs text-gray-400">Total: </span>
                      <span className="text-sm font-bold text-gray-900">{formatCurrency(svc.platformFee + svc.govtFee)}{formatFrequency(svc.frequency)}</span>
                    </div>
                    <div className="md:col-span-1 md:text-right">
                      <span className="text-xs text-gray-400 capitalize">{svc.frequency.replace("_", "-")}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* Bottom note */}
          <div className="text-center mt-8 p-6 rounded-xl" style={{ backgroundColor: "var(--color-bg-card)", border: "1px solid var(--color-border)" }}>
            <p className="text-sm text-gray-500">
              All services are handled by verified CAs, CSs, and legal professionals.
              Government fees are passed through at exact cost with zero markup.
            </p>
            <a href="/services" className="inline-block mt-3 text-sm font-semibold" style={{ color: "var(--color-accent-purple)" }}>
              Browse all services on your dashboard →
            </a>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
