import Link from "next/link";
import Header from "@/components/header";
import Footer from "@/components/footer";
import ChatWidget from "@/components/chat-widget";
import FeatureCard from "@/components/marketing/feature-card";
import PersonaCard from "@/components/marketing/persona-card";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import {
  BarChart3,
  Users,
  TrendingUp,
  Shield,
  Calculator,
  FileText,
  Rocket,
  Eye,
  Compass,
  GitCompare,
  Table2,
} from "lucide-react";

const PRODUCT_PILLARS = [
  {
    icon: <BarChart3 className="w-5 h-5" />,
    title: "Cap Table Management",
    description: "Track shareholders, model dilution, compare scenarios, generate share certificates, and manage convertible instruments.",
    href: "/features/cap-table",
    accentColor: "purple" as const,
  },
  {
    icon: <Users className="w-5 h-5" />,
    title: "ESOP Management",
    description: "Create option plans, manage grants, automate vesting schedules, and handle exercise workflows with FMV compliance.",
    href: "/features/esop",
    accentColor: "blue" as const,
  },
  {
    icon: <TrendingUp className="w-5 h-5" />,
    title: "Fundraising",
    description: "Run funding rounds, manage closing rooms, track investors, and auto-generate post-raise filings like PAS-3 and MGT-14.",
    href: "/features/fundraising",
    accentColor: "emerald" as const,
  },
  {
    icon: <Shield className="w-5 h-5" />,
    title: "Compliance Calendar",
    description: "Automated ROC filings, board meeting scheduling, GST deadlines, statutory audit reminders, and real-time compliance scoring.",
    href: "/features/compliance",
    accentColor: "purple" as const,
  },
  {
    icon: <Calculator className="w-5 h-5" />,
    title: "Valuations",
    description: "Rule 11UA-compliant fair market valuations using NAV and DCF methods. Essential for ESOP exercise pricing.",
    accentColor: "blue" as const,
  },
  {
    icon: <FileText className="w-5 h-5" />,
    title: "Legal Documents & E-Signatures",
    description: "AI-drafted board resolutions, contracts, and statutory forms. Send for e-signature with full audit trail.",
    accentColor: "emerald" as const,
  },
];

const HOW_IT_WORKS = [
  {
    step: "01",
    title: "Connect or Incorporate",
    desc: "Enter your CIN to import an existing company, or use our AI wizard to pick the right entity type and file with MCA.",
  },
  {
    step: "02",
    title: "Your Dashboard Goes Live",
    desc: "Cap table, compliance calendar, document vault, board meetings, statutory registers, and GST tracker -- all automated.",
  },
  {
    step: "03",
    title: "Grow With the Platform",
    desc: "Add ESOP plans, run funding rounds, track compliance deadlines, share investor portals, and model valuations as your company scales.",
  },
];

const FREE_TOOLS = [
  { label: "Entity Wizard", desc: "Find the right entity type", href: "/wizard", icon: <Compass className="w-4 h-4" /> },
  { label: "Compare Entities", desc: "Side-by-side comparison", href: "/compare", icon: <GitCompare className="w-4 h-4" /> },
  { label: "Cap Table Builder", desc: "Build yours instantly", href: "/cap-table-setup", icon: <Table2 className="w-4 h-4" /> },
  { label: "Pricing Calculator", desc: "Transparent, itemized", href: "/pricing", icon: <Calculator className="w-4 h-4" /> },
];

export default function HomePage() {
  return (
    <div>
      <Header />

      {/* ── Hero ── */}
      <section className="max-w-7xl mx-auto px-6 pt-20 pb-24 text-center">
        <div className="animate-fade-in-up max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-purple-50 border border-purple-100 text-purple-700 text-xs font-semibold uppercase tracking-wider mb-6">
            Equity &amp; Governance Platform
          </div>
          <h1
            className="text-4xl md:text-5xl lg:text-6xl font-extrabold leading-tight mb-6 text-gray-900"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Build, fund, and manage your company.{" "}
            <span className="gradient-text">All in one place.</span>
          </h1>
          <p className="text-lg md:text-xl text-gray-500 leading-relaxed mb-10">
            Cap table management, ESOP administration, fundraising tools,
            compliance automation, and investor portals &mdash; purpose-built
            for Indian startups and the professionals who advise them.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/signup" className="btn-primary text-lg !py-3.5 !px-8">
              Get Started Free
            </Link>
            <Link href="#how-it-works" className="btn-secondary text-lg !py-3.5 !px-8">
              See How It Works
            </Link>
          </div>
        </div>
      </section>

      {/* ── Product Pillars ── */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Everything your startup <span className="gradient-text">needs to scale</span></>}
            subtitle="The equity, governance, and operational tools that Indian startups need, in one dashboard."
          />
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {PRODUCT_PILLARS.map((feature) => (
              <FeatureCard key={feature.title} {...feature} />
            ))}
          </div>
        </div>
      </section>

      {/* ── Persona Routing ── */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Built for everyone in the <span className="gradient-text">ecosystem</span></>}
            subtitle="Whether you're a founder or investor, Anvils has a dedicated experience for you."
          />
          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            <PersonaCard
              icon={<Rocket className="w-6 h-6" />}
              persona="Founders"
              headline="Run your back-office on autopilot"
              bullets={[
                "Cap table & shareholder management",
                "ESOP plans, grants & vesting",
                "Fundraising with closing room",
                "Automated compliance calendar",
                "Valuations & legal documents",
                "Data room & accounting integration",
              ]}
              href="/for/founders"
              accentColor="purple"
            />
            <PersonaCard
              icon={<Eye className="w-6 h-6" />}
              persona="Investors"
              headline="Full portfolio transparency, no login needed"
              bullets={[
                "Token-based portfolio dashboard",
                "Holdings & cap table view",
                "Funding round history",
                "ESOP grant visibility",
                "Document access (SHA, SSA, pitch decks)",
                "Discover companies & express interest",
              ]}
              href="/for/investors"
              accentColor="blue"
            />
          </div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section id="how-it-works" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Up and running in <span className="gradient-text">minutes</span></>}
            subtitle="Existing company or new incorporation -- your dashboard is live almost instantly."
          />
          <div className="grid md:grid-cols-3 gap-8">
            {HOW_IT_WORKS.map((step) => (
              <div key={step.step} className="card-static p-8 text-center">
                <div className="w-12 h-12 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center mx-auto mb-4 text-sm font-bold">
                  {step.step}
                </div>
                <h3
                  className="text-xl font-bold text-gray-900 mb-3"
                  style={{ fontFamily: "var(--font-display)" }}
                >
                  {step.title}
                </h3>
                <p className="text-sm text-gray-500 leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Free Tools Strip ── */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-8">
            <h3 className="text-lg font-bold text-gray-900 mb-1">Try our free tools &mdash; no signup required</h3>
            <p className="text-sm text-gray-500">Explore before you commit.</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {FREE_TOOLS.map((tool) => (
              <Link
                key={tool.href}
                href={tool.href}
                className="card-static p-4 flex items-center gap-3 hover:bg-purple-50 hover:border-purple-200 transition-colors group"
              >
                <div className="w-9 h-9 rounded-lg bg-gray-100 group-hover:bg-purple-100 flex items-center justify-center text-gray-500 group-hover:text-purple-600 transition-colors shrink-0">
                  {tool.icon}
                </div>
                <div>
                  <div className="text-sm font-semibold text-gray-900">{tool.label}</div>
                  <div className="text-xs text-gray-500">{tool.desc}</div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <CTASection
        title="Ready to simplify your company's back-office?"
        subtitle="Get started for free. No credit card required."
        primaryCTA={{ label: "Get Started Free", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <Footer />
      <ChatWidget />
    </div>
  );
}
