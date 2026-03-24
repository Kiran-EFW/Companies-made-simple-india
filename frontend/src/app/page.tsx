import Link from "next/link";
import Header from "@/components/header";
import Footer from "@/components/footer";
import ChatWidget from "@/components/chat-widget";
import FeatureCard from "@/components/marketing/feature-card";
import PersonaCard from "@/components/marketing/persona-card";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import StatsBar from "@/components/marketing/stats-bar";
import ProblemCard from "@/components/marketing/problem-card";
import ComparisonTable from "@/components/marketing/comparison-table";
import FAQAccordion from "@/components/marketing/faq-accordion";
import {
  BarChart3,
  Users,
  TrendingUp,
  Shield,
  Calculator,
  FileText,
  Rocket,
  Eye,
  Briefcase,
  Compass,
  GitCompare,
  Table2,
  IndianRupee,
  AlertTriangle,
  FileSpreadsheet,
  Check,
  ArrowRight,
} from "lucide-react";

/* ── Data ── */

const HERO_STATS = [
  { value: "7", label: "Entity Types" },
  { value: "28", label: "States Covered" },
  { value: "50+", label: "Compliance Tasks" },
  { value: "Rs 999", label: "Starting Price" },
];

const PROBLEMS = [
  {
    icon: <IndianRupee className="w-5 h-5" />,
    problem: "Opaque CA pricing",
    stat: "Traditional CAs charge Rs 15,000-50,000 for incorporation with no transparency on government fees vs. their markup.",
  },
  {
    icon: <AlertTriangle className="w-5 h-5" />,
    problem: "Compliance chaos",
    stat: "50+ regulatory deadlines per year for a simple Pvt Ltd. Miss one and face penalties, director disqualification, or worse.",
  },
  {
    icon: <FileSpreadsheet className="w-5 h-5" />,
    problem: "Scattered equity data",
    stat: "Cap tables in spreadsheets, ESOP plans on paper, investor documents in email threads. No single source of truth.",
  },
];

const PRODUCT_PILLARS = [
  {
    icon: <Briefcase className="w-5 h-5" />,
    title: "Company Incorporation",
    description:
      "Incorporate any of 7 entity types with transparent, state-wise pricing. AI-guided entity selection and a 25-stage tracking pipeline.",
    href: "/wizard",
    accentColor: "purple" as const,
  },
  {
    icon: <BarChart3 className="w-5 h-5" />,
    title: "Cap Table & Equity",
    description:
      "Track shareholders, model dilution, issue shares, and manage convertible instruments. One source of truth for your equity stack.",
    href: "/features/cap-table",
    accentColor: "blue" as const,
  },
  {
    icon: <Users className="w-5 h-5" />,
    title: "ESOP Management",
    description:
      "Create option plans, manage grants, automate vesting schedules, and handle exercise workflows with board resolution tracking.",
    href: "/features/esop",
    accentColor: "emerald" as const,
  },
  {
    icon: <TrendingUp className="w-5 h-5" />,
    title: "Fundraising",
    description:
      "Run funding rounds with SAFE, CCD, and CCPS instruments. Manage investors, closing rooms, and post-raise filings like PAS-3.",
    href: "/features/fundraising",
    accentColor: "purple" as const,
  },
  {
    icon: <Shield className="w-5 h-5" />,
    title: "Compliance Autopilot",
    description:
      "50+ deadlines auto-tracked with smart reminders at 30, 15, 7, 3, and 1 day. Real-time compliance health scoring and penalty alerts.",
    href: "/features/compliance",
    accentColor: "blue" as const,
  },
  {
    icon: <FileText className="w-5 h-5" />,
    title: "Legal Docs & E-Sign",
    description:
      "50+ professionally drafted templates with clause-by-clause customization. Multi-party e-signatures with full audit trail.",
    href: "/features/legal-docs",
    accentColor: "emerald" as const,
  },
];

const COMPARISON_FEATURES = [
  { name: "Company Incorporation", anvils: true, competitors: { "Traditional CAs": true, "Vakilsearch": true, "Carta / Trica": false } },
  { name: "Cap Table Management", anvils: true, competitors: { "Traditional CAs": false, "Vakilsearch": false, "Carta / Trica": true } },
  { name: "ESOP Administration", anvils: true, competitors: { "Traditional CAs": false, "Vakilsearch": false, "Carta / Trica": true } },
  { name: "Compliance Calendar", anvils: true, competitors: { "Traditional CAs": "partial", "Vakilsearch": "partial", "Carta / Trica": false } },
  { name: "Fundraising Tools", anvils: true, competitors: { "Traditional CAs": false, "Vakilsearch": false, "Carta / Trica": true } },
  { name: "Investor Portal", anvils: true, competitors: { "Traditional CAs": false, "Vakilsearch": false, "Carta / Trica": true } },
  { name: "India-Specific (MCA, SEBI)", anvils: true, competitors: { "Traditional CAs": true, "Vakilsearch": true, "Carta / Trica": false } },
  { name: "Transparent Pricing", anvils: true, competitors: { "Traditional CAs": false, "Vakilsearch": "partial", "Carta / Trica": "partial" } },
  { name: "Services Marketplace", anvils: true, competitors: { "Traditional CAs": false, "Vakilsearch": true, "Carta / Trica": false } },
  { name: "AI Copilot", anvils: true, competitors: { "Traditional CAs": false, "Vakilsearch": false, "Carta / Trica": false } },
];

const PLANS_PREVIEW = [
  {
    name: "Free",
    price: "Rs 0",
    period: "",
    tagline: "For every Indian company",
    features: ["Compliance calendar & reminders", "Basic document storage", "Company dashboard"],
    cta: "Start Free",
    highlighted: false,
  },
  {
    name: "Growth",
    price: "Rs 2,999",
    period: "/mo",
    tagline: "For funded startups",
    features: ["Full cap table & ESOP", "Data room & e-signatures", "Investor portal", "Fundraising tools"],
    cta: "Start Free Trial",
    highlighted: true,
  },
  {
    name: "Scale",
    price: "Rs 9,999",
    period: "/mo",
    tagline: "For scaling companies",
    features: ["Board governance suite", "Statutory registers", "FEMA compliance", "Dedicated account manager"],
    cta: "Contact Sales",
    highlighted: false,
  },
];

const HOW_IT_WORKS = [
  {
    step: "01",
    title: "Choose your entity",
    desc: "Answer 5 questions. Our AI recommends the right structure — Private Limited, LLP, OPC, or 4 other entity types.",
  },
  {
    step: "02",
    title: "We handle incorporation",
    desc: "Upload documents, pay transparent fees with government cost breakdown, and track every step of the 25-stage pipeline.",
  },
  {
    step: "03",
    title: "Manage and grow",
    desc: "Your dashboard goes live with compliance calendar, cap table, data room, and everything you need to scale.",
  },
];

const FREE_TOOLS = [
  { label: "Entity Wizard", desc: "AI-powered entity recommendation", href: "/wizard", icon: <Compass className="w-4 h-4" /> },
  { label: "Compare Entities", desc: "Side-by-side comparison", href: "/compare", icon: <GitCompare className="w-4 h-4" /> },
  { label: "Cap Table Builder", desc: "Build your cap table free", href: "/cap-table-setup", icon: <Table2 className="w-4 h-4" /> },
  { label: "Pricing Calculator", desc: "Transparent, itemized", href: "/pricing", icon: <Calculator className="w-4 h-4" /> },
];

const FAQ_ITEMS = [
  {
    question: "What entity type should I choose?",
    answer: "It depends on your goals. Use our free Entity Wizard — answer 5 questions and get a personalized recommendation with pros, cons, and pricing for each entity type. Private Limited is most popular for funded startups, while LLP works well for service businesses.",
  },
  {
    question: "How long does incorporation take?",
    answer: "Typically 7-15 business days depending on the entity type and state. Private Limited and OPC take 7-10 days, LLPs take 10-12 days. We track every step through a 25-stage pipeline so you always know where things stand.",
  },
  {
    question: "What's included in the free plan?",
    answer: "Every company gets a free dashboard with compliance calendar, deadline reminders, basic document storage, and company overview. The free plan is designed to keep you compliant. Cap table, ESOP, fundraising, and data room features are available on Growth and Scale plans.",
  },
  {
    question: "How does the compliance calendar work?",
    answer: "We auto-generate 50+ compliance tasks based on your entity type, state, incorporation date, and GST/TDS applicability. You get reminders at 30, 15, 7, 3, and 1 day before each deadline. The system also tracks your compliance health score.",
  },
  {
    question: "Can I migrate my existing cap table?",
    answer: "Yes. You can enter your existing shareholders and share data manually, or contact our team for assisted migration. We support all share types, convertible instruments, and historical transaction import.",
  },
  {
    question: "Is my data secure?",
    answer: "Your data is encrypted in transit and at rest. We use role-based access controls, full audit logging with IP tracking, and token-based secure sharing for investor portals. Sensitive information like Aadhaar and PAN numbers are masked in logs.",
  },
  {
    question: "Do I still need a CA if I use Anvils?",
    answer: "Anvils automates tracking and reminders, but certain filings (like annual ROC filing, ITR, and statutory audit) require a practicing CA. You can hire your own or use our Services Marketplace where verified CAs fulfill work at transparent prices.",
  },
  {
    question: "What payment methods do you accept?",
    answer: "We accept all major payment methods via Razorpay — credit/debit cards, UPI, net banking, and wallets. All incorporation fees include a transparent breakdown of government fees, stamp duty, and platform fees.",
  },
];

/* ── Page ── */

export default function HomePage() {
  return (
    <div className="glow-bg">
      <Header />

      {/* ══════ Hero ══════ */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-24 text-center">
        <div className="animate-fade-in-up max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-purple-50 border border-purple-100 text-purple-700 text-xs font-semibold uppercase tracking-wider mb-6">
            Equity &amp; Governance Platform
          </div>
          <h1
            className="text-4xl md:text-5xl lg:text-6xl font-extrabold leading-tight mb-6 text-[var(--color-text-primary)]"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Stop managing your company{" "}
            <span className="gradient-text">in spreadsheets.</span>
          </h1>
          <p className="text-lg md:text-xl text-[var(--color-text-secondary)] leading-relaxed mb-10">
            Anvils is the operating system for Indian companies &mdash; from
            incorporation to fundraising, compliance to cap table, all in one
            place. Purpose-built for Indian regulations.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/signup" className="btn-primary text-lg !py-3.5 !px-8">
              Start Free
            </Link>
            <Link href="/pricing" className="btn-secondary text-lg !py-3.5 !px-8">
              See Pricing
            </Link>
          </div>
          <StatsBar stats={HERO_STATS} />
        </div>
      </section>

      {/* ══════ Problem Statement ══════ */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>The problem every Indian <span className="gradient-text">founder faces</span></>}
            subtitle="Incorporation is just the beginning. The real challenge is what comes after."
          />
          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {PROBLEMS.map((p) => (
              <ProblemCard key={p.problem} {...p} />
            ))}
          </div>
        </div>
      </section>

      <div className="section-divider" />

      {/* ══════ Solution: Product Pillars ══════ */}
      <section className="py-20 bg-[var(--color-bg-secondary)]">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>One platform. Every stage of <span className="gradient-text">your company.</span></>}
            subtitle="From incorporation to IPO — equity, compliance, and operations in a single dashboard."
          />
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {PRODUCT_PILLARS.map((feature) => (
              <FeatureCard key={feature.title} {...feature} />
            ))}
          </div>
        </div>
      </section>

      {/* ══════ Competitive Comparison ══════ */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>How Anvils <span className="gradient-text">compares</span></>}
            subtitle="The only platform that combines incorporation, equity management, and compliance in one place."
          />
          <div className="max-w-5xl mx-auto">
            <ComparisonTable features={COMPARISON_FEATURES} />
            <p className="text-center text-sm text-[var(--color-text-muted)] mt-4">
              Anvils is 75-80% cheaper than Vakilsearch on incorporation and 70% cheaper than Trica Equity for cap table management.
            </p>
          </div>
        </div>
      </section>

      <div className="section-divider" />

      {/* ══════ Persona Routing ══════ */}
      <section className="py-20 bg-[var(--color-bg-secondary)]">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Built for everyone in the <span className="gradient-text">ecosystem</span></>}
            subtitle="Whether you're a founder, investor, or CA — Anvils has a dedicated experience for you."
          />
          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            <PersonaCard
              icon={<Rocket className="w-6 h-6" />}
              persona="Founders"
              headline="From idea to IPO"
              bullets={[
                "Incorporate in days, not weeks",
                "Auto-generated compliance calendar",
                "Cap table, ESOP & fundraising",
                "Investor-ready data room",
              ]}
              href="/for/founders"
              accentColor="purple"
            />
            <PersonaCard
              icon={<Eye className="w-6 h-6" />}
              persona="Investors"
              headline="Portfolio visibility without friction"
              bullets={[
                "Secure token-based access",
                "Holdings across all companies",
                "Data room & document access",
                "Deal discovery & interest",
              ]}
              href="/for/investors"
              accentColor="blue"
            />
            <PersonaCard
              icon={<Briefcase className="w-6 h-6" />}
              persona="CAs & Professionals"
              headline="All your clients, one dashboard"
              bullets={[
                "Cross-company compliance calendar",
                "Filing tracker & deadline alerts",
                "Marketplace fulfillment",
                "Earn Rs 1-2.5L+ annually",
              ]}
              href="/for/cas"
              accentColor="emerald"
            />
          </div>
        </div>
      </section>

      {/* ══════ How It Works ══════ */}
      <section id="how-it-works" className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Up and running in <span className="gradient-text">three steps</span></>}
            subtitle="Existing company or new incorporation — your dashboard is live almost instantly."
          />
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {HOW_IT_WORKS.map((step, i) => (
              <div key={step.step} className="card-static p-8 text-center relative">
                <div className="w-12 h-12 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center mx-auto mb-4 text-sm font-bold">
                  {step.step}
                </div>
                <h3
                  className="text-xl font-bold text-[var(--color-text-primary)] mb-3"
                  style={{ fontFamily: "var(--font-display)" }}
                >
                  {step.title}
                </h3>
                <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">{step.desc}</p>
                {i < HOW_IT_WORKS.length - 1 && (
                  <ArrowRight className="hidden md:block absolute -right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-[var(--color-text-muted)]" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      <div className="section-divider" />

      {/* ══════ Free Tools ══════ */}
      <section className="py-16 bg-[var(--color-bg-secondary)]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-8">
            <h3
              className="text-lg font-bold text-[var(--color-text-primary)] mb-1"
              style={{ fontFamily: "var(--font-display)" }}
            >
              Try our free tools &mdash; no signup required
            </h3>
            <p className="text-sm text-[var(--color-text-muted)]">Explore before you commit.</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
            {FREE_TOOLS.map((tool) => (
              <Link
                key={tool.href}
                href={tool.href}
                className="card-static p-4 flex items-center gap-3 hover:bg-purple-50 hover:border-purple-200 transition-colors group"
              >
                <div className="w-9 h-9 rounded-lg bg-[var(--color-bg-secondary)] group-hover:bg-purple-100 flex items-center justify-center text-[var(--color-text-muted)] group-hover:text-purple-600 transition-colors shrink-0">
                  {tool.icon}
                </div>
                <div>
                  <div className="text-sm font-semibold text-[var(--color-text-primary)]">{tool.label}</div>
                  <div className="text-xs text-[var(--color-text-muted)]">{tool.desc}</div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ══════ Pricing Teaser ══════ */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Transparent pricing. <span className="gradient-text">No surprises.</span></>}
            subtitle="Start free. Upgrade when you raise funding."
          />
          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {PLANS_PREVIEW.map((plan) => (
              <div
                key={plan.name}
                className={`card-static p-6 flex flex-col ${
                  plan.highlighted ? "border-purple-300 ring-2 ring-purple-100" : ""
                }`}
              >
                {plan.highlighted && (
                  <div className="badge badge-purple mb-3 self-start">Most Popular</div>
                )}
                <h3 className="text-lg font-bold text-[var(--color-text-primary)]">{plan.name}</h3>
                <div className="mt-2 mb-1">
                  <span className="text-2xl font-extrabold text-[var(--color-text-primary)]">{plan.price}</span>
                  {plan.period && <span className="text-sm text-[var(--color-text-muted)]">{plan.period}</span>}
                </div>
                <p className="text-xs text-[var(--color-text-muted)] mb-4">{plan.tagline}</p>
                <ul className="space-y-2 flex-1 mb-6">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm text-[var(--color-text-secondary)]">
                      <Check className="w-4 h-4 mt-0.5 shrink-0 text-emerald-500" />
                      {f}
                    </li>
                  ))}
                </ul>
                <Link
                  href="/pricing"
                  className={plan.highlighted ? "btn-primary btn-sm w-full" : "btn-secondary btn-sm w-full"}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
          <p className="text-center text-sm text-[var(--color-text-muted)] mt-6">
            Incorporation from <span className="font-semibold text-[var(--color-text-primary)]">Rs 999</span>.{" "}
            <Link href="/pricing" className="text-purple-600 hover:underline">See full pricing &rarr;</Link>
          </p>
        </div>
      </section>

      <div className="section-divider" />

      {/* ══════ Social Proof / Stats ══════ */}
      <section className="py-20 bg-[var(--color-bg-secondary)]">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Built for the Indian <span className="gradient-text">startup ecosystem</span></>}
            subtitle="India's startup landscape is booming. Anvils is purpose-built for it."
          />
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto text-center">
            <div className="card-static p-6">
              <div
                className="text-3xl font-extrabold text-[var(--color-accent-purple)] mb-2"
                style={{ fontFamily: "var(--font-display)" }}
              >
                2 Lakh+
              </div>
              <p className="text-sm text-[var(--color-text-secondary)]">Companies incorporated in India every year</p>
            </div>
            <div className="card-static p-6">
              <div
                className="text-3xl font-extrabold text-[var(--color-accent-blue)] mb-2"
                style={{ fontFamily: "var(--font-display)" }}
              >
                1,00,000+
              </div>
              <p className="text-sm text-[var(--color-text-secondary)]">DPIIT-recognized startups and growing</p>
            </div>
            <div className="card-static p-6">
              <div
                className="text-3xl font-extrabold text-[var(--color-accent-emerald)] mb-2"
                style={{ fontFamily: "var(--font-display)" }}
              >
                Rs 50K-2L
              </div>
              <p className="text-sm text-[var(--color-text-secondary)]">Average annual compliance spend per company</p>
            </div>
          </div>
        </div>
      </section>

      {/* ══════ FAQ ══════ */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Frequently asked <span className="gradient-text">questions</span></>}
            subtitle="Everything you need to know about getting started with Anvils."
          />
          <div className="max-w-3xl mx-auto">
            <FAQAccordion items={FAQ_ITEMS} />
          </div>
        </div>
      </section>

      {/* ══════ Bottom CTA ══════ */}
      <CTASection
        title="Ready to build your company the right way?"
        subtitle="Join thousands of Indian founders who manage their companies on Anvils. Start free — no credit card required."
        primaryCTA={{ label: "Get Started Free", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <Footer />
      <ChatWidget />
    </div>
  );
}
