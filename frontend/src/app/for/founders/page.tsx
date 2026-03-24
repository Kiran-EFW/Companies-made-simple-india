import { Metadata } from "next";
import Link from "next/link";
import Header from "@/components/header";
import Footer from "@/components/footer";
import ChatWidget from "@/components/chat-widget";
import HeroSection from "@/components/marketing/hero-section";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import FeatureCard from "@/components/marketing/feature-card";
import ProblemCard from "@/components/marketing/problem-card";
import {
  IndianRupee,
  FileSpreadsheet,
  AlertTriangle,
  FolderSearch,
  Building2,
  BarChart3,
  Gift,
  Shield,
  TrendingUp,
  FolderLock,
  Check,
  ArrowRight,
  Calculator,
  Users,
  FileText,
  PenTool,
  BookOpen,
  Bot,
  Briefcase,
  Layers,
  UserPlus,
  Award,
  Target,
  LineChart,
  Handshake,
  DoorOpen,
  FolderTree,
  History,
  Share2,
  Timer,
} from "lucide-react";

export const metadata: Metadata = {
  title: "Anvils for Founders — Equity, Compliance & Growth Tools",
  description:
    "Cap table management, ESOP administration, fundraising tools, compliance tracking, valuations, and more. Purpose-built for Indian startup founders.",
};

/* ------------------------------------------------------------------ */
/*  Pain Points                                                        */
/* ------------------------------------------------------------------ */
const PAIN_POINTS = [
  {
    icon: <IndianRupee className="w-5 h-5" />,
    problem:
      "Your CA charges Rs 50K but you have no idea what\u2019s been filed",
    stat: "Traditional CAs offer zero visibility into filing status or government fee breakdowns.",
  },
  {
    icon: <FileSpreadsheet className="w-5 h-5" />,
    problem:
      "Your cap table is a Google Sheet that 3 people edit differently",
    stat: "No version control, no audit trail, no way to model dilution or run scenarios.",
  },
  {
    icon: <AlertTriangle className="w-5 h-5" />,
    problem:
      "You missed an ROC filing deadline and got a penalty notice",
    stat: "50+ compliance deadlines per year. Miss one and face fines, director disqualification, or strike-off.",
  },
  {
    icon: <FolderSearch className="w-5 h-5" />,
    problem:
      "Investors asked for a data room and you spent 2 weeks assembling PDFs",
    stat: "Documents scattered across email, Drive, and WhatsApp. No structure, no access control.",
  },
];

/* ------------------------------------------------------------------ */
/*  Feature Deep-Dives                                                 */
/* ------------------------------------------------------------------ */
const COLOR_MAP: Record<
  string,
  { iconBg: string; iconText: string; bullet: string; accent: string }
> = {
  purple: {
    iconBg: "bg-purple-50",
    iconText: "text-purple-600",
    bullet: "text-purple-500",
    accent: "text-purple-600",
  },
  blue: {
    iconBg: "bg-blue-50",
    iconText: "text-blue-600",
    bullet: "text-blue-500",
    accent: "text-blue-600",
  },
  emerald: {
    iconBg: "bg-emerald-50",
    iconText: "text-emerald-600",
    bullet: "text-emerald-500",
    accent: "text-emerald-600",
  },
};

interface SubFeature {
  icon: React.ReactNode;
  label: string;
}

interface Feature {
  id: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  bullets: string[];
  color: "purple" | "blue" | "emerald";
  subFeatures: SubFeature[];
  href: string;
}

const FEATURES: Feature[] = [
  {
    id: "incorporation",
    icon: <Building2 className="w-6 h-6" />,
    title: "Incorporation",
    description:
      "Incorporate any of 7 entity types with transparent pricing. Our AI-guided wizard recommends the best structure for your business, and you can track every step of the 25-stage pipeline in real time.",
    bullets: [
      "AI-guided entity selection wizard",
      "25-stage tracking pipeline",
      "Government fees at exact cost (\u20B90 markup)",
    ],
    color: "purple",
    subFeatures: [
      { icon: <Briefcase className="w-4 h-4" />, label: "Private Limited" },
      { icon: <Handshake className="w-4 h-4" />, label: "LLP" },
      { icon: <UserPlus className="w-4 h-4" />, label: "OPC" },
      { icon: <Award className="w-4 h-4" />, label: "Section 8" },
    ],
    href: "/features/incorporation",
  },
  {
    id: "cap-table",
    icon: <BarChart3 className="w-6 h-6" />,
    title: "Cap Table",
    description:
      "Your equity stack in one place. Track every shareholder, share class, and transaction with real-time ownership calculations. Model dilution scenarios before you raise so there are no surprises at closing.",
    bullets: [
      "Shareholder registry with real-time ownership %",
      "Dilution modeling and scenario comparison",
      "Share issuance and transaction history",
    ],
    color: "blue",
    subFeatures: [
      { icon: <Users className="w-4 h-4" />, label: "Shareholders" },
      { icon: <LineChart className="w-4 h-4" />, label: "Dilution" },
      { icon: <Layers className="w-4 h-4" />, label: "Scenarios" },
      { icon: <FileText className="w-4 h-4" />, label: "Certificates" },
    ],
    href: "/features/cap-table",
  },
  {
    id: "esop",
    icon: <Gift className="w-6 h-6" />,
    title: "ESOP",
    description:
      "Stock options that actually work. Create plans with configurable vesting, manage individual grants with board resolution tracking, and run exercise workflows that stay compliant with FMV requirements.",
    bullets: [
      "Plan creation with configurable vesting (monthly, quarterly, annual)",
      "Grant management with board resolution tracking",
      "Exercise workflows with FMV compliance",
    ],
    color: "emerald",
    subFeatures: [
      { icon: <FileText className="w-4 h-4" />, label: "Plans" },
      { icon: <Award className="w-4 h-4" />, label: "Grants" },
      { icon: <Timer className="w-4 h-4" />, label: "Vesting" },
      { icon: <Target className="w-4 h-4" />, label: "Exercise" },
    ],
    href: "/features/esop",
  },
  {
    id: "compliance",
    icon: <Shield className="w-6 h-6" />,
    title: "Compliance",
    description:
      "Never miss a deadline again. Anvils auto-generates 50+ compliance tasks based on your entity type, state of registration, and financial year. Smart reminders keep you ahead of every filing.",
    bullets: [
      "50+ auto-generated tasks based on entity, state, and FY",
      "Smart reminders at 30, 15, 7, 3, and 1 day",
      "Real-time compliance health score",
    ],
    color: "purple",
    subFeatures: [
      { icon: <FileText className="w-4 h-4" />, label: "ROC Filings" },
      { icon: <IndianRupee className="w-4 h-4" />, label: "GST" },
      { icon: <Calculator className="w-4 h-4" />, label: "TDS" },
      { icon: <Users className="w-4 h-4" />, label: "Board Meetings" },
    ],
    href: "/features/compliance",
  },
  {
    id: "fundraising",
    icon: <TrendingUp className="w-6 h-6" />,
    title: "Fundraising",
    description:
      "From term sheet to closing. Track funding rounds with support for SAFE, CCD, and CCPS instruments. Manage investor pipelines, commitment tracking, and closing rooms with multi-party e-signatures.",
    bullets: [
      "Funding round tracking with SAFE, CCD, CCPS instruments",
      "Investor management and commitment tracking",
      "Closing room with multi-party e-signatures",
    ],
    color: "blue",
    subFeatures: [
      { icon: <Target className="w-4 h-4" />, label: "Rounds" },
      { icon: <Layers className="w-4 h-4" />, label: "Instruments" },
      { icon: <Users className="w-4 h-4" />, label: "Investors" },
      { icon: <DoorOpen className="w-4 h-4" />, label: "Closing Room" },
    ],
    href: "/features/fundraising",
  },
  {
    id: "data-room",
    icon: <FolderLock className="w-6 h-6" />,
    title: "Data Room",
    description:
      "Investor-ready in seconds. Organize documents in hierarchical folders with pre-built categories. Every file has version control and metadata. Share securely with token-based links, passwords, and expiry dates.",
    bullets: [
      "Hierarchical folders with pre-built categories",
      "Version control and file metadata",
      "Token-based secure sharing with password and expiry",
    ],
    color: "emerald",
    subFeatures: [
      { icon: <FolderTree className="w-4 h-4" />, label: "Folders" },
      { icon: <History className="w-4 h-4" />, label: "Versioning" },
      { icon: <Share2 className="w-4 h-4" />, label: "Sharing" },
      { icon: <Timer className="w-4 h-4" />, label: "Retention" },
    ],
    href: "/features/data-room",
  },
];

/* ------------------------------------------------------------------ */
/*  Additional Tools                                                   */
/* ------------------------------------------------------------------ */
const ADDITIONAL_TOOLS = [
  {
    icon: <Calculator className="w-5 h-5" />,
    title: "Valuations",
    description:
      "Rule 11UA FMV calculations using NAV and DCF methods",
    color: "purple" as const,
  },
  {
    icon: <Users className="w-5 h-5" />,
    title: "Board Meetings",
    description:
      "Schedule, send notices, draft minutes, track resolutions",
    color: "blue" as const,
  },
  {
    icon: <FileText className="w-5 h-5" />,
    title: "Legal Documents",
    description:
      "50+ templates with clause-by-clause customization",
    color: "emerald" as const,
  },
  {
    icon: <PenTool className="w-5 h-5" />,
    title: "E-Signatures",
    description:
      "Multi-party signing with full audit trail and OTP verification",
    color: "purple" as const,
  },
  {
    icon: <BookOpen className="w-5 h-5" />,
    title: "Statutory Registers",
    description:
      "Members, directors, charges, contracts \u2014 all maintained",
    color: "blue" as const,
  },
  {
    icon: <Bot className="w-5 h-5" />,
    title: "AI Copilot",
    description:
      "Context-aware assistant that knows your company\u2019s data",
    color: "emerald" as const,
  },
];

/* ------------------------------------------------------------------ */
/*  Pricing Plans                                                      */
/* ------------------------------------------------------------------ */
const PRICING_PLANS = [
  { name: "Free", price: "\u20B90", period: "forever", highlight: false },
  { name: "Growth", price: "\u20B92,999", period: "/mo", highlight: true },
  { name: "Scale", price: "\u20B99,999", period: "/mo", highlight: false },
];

/* ================================================================== */
/*  Page Component                                                     */
/* ================================================================== */
export default function ForFoundersPage() {
  return (
    <div className="glow-bg">
      <Header />

      {/* ---------------------------------------------------------- */}
      {/*  Section 1 — Hero                                           */}
      {/* ---------------------------------------------------------- */}
      <HeroSection
        badge="For Founders"
        title={
          <>
            Stop losing sleep over compliance deadlines and{" "}
            <span className="gradient-text">cap table spreadsheets</span>
          </>
        }
        subtitle="Anvils gives you a single dashboard to incorporate, manage equity, track compliance, and raise funding — purpose-built for Indian companies."
        primaryCTA={{ label: "Start Free", href: "/signup" }}
        secondaryCTA={{ label: "See How It Works", href: "#features" }}
      />

      {/* ---------------------------------------------------------- */}
      {/*  Section 2 — Pain Points                                    */}
      {/* ---------------------------------------------------------- */}
      <section className="py-20" style={{ background: "var(--color-bg-secondary)" }}>
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={
              <>
                Sound <span className="gradient-text">familiar</span>?
              </>
            }
            subtitle="These are the problems that drain founders' time and money."
          />
          <div className="grid md:grid-cols-2 gap-6">
            {PAIN_POINTS.map((p) => (
              <ProblemCard
                key={p.problem}
                icon={p.icon}
                problem={p.problem}
                stat={p.stat}
              />
            ))}
          </div>
        </div>
      </section>

      {/* ---------------------------------------------------------- */}
      {/*  Section 3 — Feature Deep-Dives                             */}
      {/* ---------------------------------------------------------- */}
      <section id="features" className="py-20 scroll-mt-24">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={
              <>
                Everything you need to{" "}
                <span className="gradient-text">run your company</span>
              </>
            }
          />

          <div className="space-y-24">
            {FEATURES.map((feature, i) => {
              const colors = COLOR_MAP[feature.color];
              const isReversed = i % 2 === 1;

              return (
                <div
                  id={feature.id}
                  key={feature.id}
                  className={`flex flex-col ${
                    isReversed ? "md:flex-row-reverse" : "md:flex-row"
                  } gap-12 items-center scroll-mt-24`}
                >
                  {/* Text side */}
                  <div className="flex-1">
                    <div
                      className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${colors.iconBg}`}
                    >
                      <div className={colors.iconText}>{feature.icon}</div>
                    </div>

                    <h3
                      className="text-2xl font-bold text-[var(--color-text-primary)] mb-3"
                      style={{ fontFamily: "var(--font-display)" }}
                    >
                      {feature.title}
                    </h3>

                    <p className="text-[var(--color-text-secondary)] leading-relaxed mb-5">
                      {feature.description}
                    </p>

                    <ul className="space-y-3 mb-6">
                      {feature.bullets.map((b) => (
                        <li
                          key={b}
                          className="flex items-start gap-2.5 text-sm text-[var(--color-text-secondary)]"
                        >
                          <Check
                            className={`w-4 h-4 shrink-0 mt-0.5 ${colors.bullet}`}
                          />
                          {b}
                        </li>
                      ))}
                    </ul>

                    <Link
                      href={feature.href}
                      className={`inline-flex items-center gap-1.5 text-sm font-semibold ${colors.accent} hover:underline`}
                    >
                      Explore <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>

                  {/* Card side — sub-feature highlights */}
                  <div className="flex-1 w-full">
                    <div
                      className="rounded-2xl p-6 border"
                      style={{
                        background: "var(--color-bg-card)",
                        borderColor: "var(--color-border)",
                      }}
                    >
                      <div className="grid grid-cols-2 gap-4">
                        {feature.subFeatures.map((sf) => (
                          <div
                            key={sf.label}
                            className="flex items-center gap-3 rounded-xl p-3"
                            style={{
                              background: "var(--color-bg-secondary)",
                            }}
                          >
                            <div
                              className={`w-8 h-8 rounded-lg flex items-center justify-center ${colors.iconBg}`}
                            >
                              <div className={colors.iconText}>{sf.icon}</div>
                            </div>
                            <span className="text-sm font-medium text-[var(--color-text-primary)]">
                              {sf.label}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ---------------------------------------------------------- */}
      {/*  Section 4 — Additional Tools Grid                          */}
      {/* ---------------------------------------------------------- */}
      <section className="py-20" style={{ background: "var(--color-bg-secondary)" }}>
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={
              <>
                And there&apos;s <span className="gradient-text">more</span>
              </>
            }
            subtitle="Every tool you need for running a compliant, well-governed company."
          />
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {ADDITIONAL_TOOLS.map((tool) => (
              <FeatureCard
                key={tool.title}
                icon={tool.icon}
                title={tool.title}
                description={tool.description}
                accentColor={tool.color}
              />
            ))}
          </div>
        </div>
      </section>

      {/* ---------------------------------------------------------- */}
      {/*  Section 5 — Pricing Teaser                                 */}
      {/* ---------------------------------------------------------- */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <SectionHeader
            title={
              <>
                Transparent pricing.{" "}
                <span className="gradient-text">No surprises.</span>
              </>
            }
          />

          <div className="grid sm:grid-cols-3 gap-6 mb-8">
            {PRICING_PLANS.map((plan) => (
              <div
                key={plan.name}
                className={`rounded-2xl p-6 border text-center transition-shadow ${
                  plan.highlight ? "shadow-lg ring-2 ring-purple-200" : ""
                }`}
                style={{
                  background: "var(--color-bg-card)",
                  borderColor: plan.highlight
                    ? "rgb(168 85 247)"
                    : "var(--color-border)",
                }}
              >
                <p className="text-sm font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider mb-2">
                  {plan.name}
                </p>
                <p
                  className="text-3xl font-extrabold text-[var(--color-text-primary)] mb-1"
                  style={{ fontFamily: "var(--font-display)" }}
                >
                  {plan.price}
                </p>
                <p className="text-sm text-[var(--color-text-muted)]">
                  {plan.period}
                </p>
              </div>
            ))}
          </div>

          <div className="space-y-2">
            <Link
              href="/pricing"
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-purple-600 hover:underline"
            >
              See full pricing <ArrowRight className="w-3.5 h-3.5" />
            </Link>
            <p className="text-sm text-[var(--color-text-muted)]">
              Incorporation from {"\u20B9"}999 &middot; No hidden fees
            </p>
          </div>
        </div>
      </section>

      {/* ---------------------------------------------------------- */}
      {/*  Section 6 — CTA                                            */}
      {/* ---------------------------------------------------------- */}
      <CTASection
        variant="purple"
        title="Your company deserves better than spreadsheets"
        subtitle="Join thousands of Indian founders managing equity, compliance, and fundraising on Anvils."
        primaryCTA={{ label: "Start Free Today", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <Footer />
      <ChatWidget />
    </div>
  );
}
