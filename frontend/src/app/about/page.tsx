import Header from "@/components/header";
import Footer from "@/components/footer";
import ChatWidget from "@/components/chat-widget";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import StatsBar from "@/components/marketing/stats-bar";
import {
  Building2,
  Users,
  Shield,
  Lightbulb,
  Eye,
  ArrowRight,
  Target,
  Layers,
} from "lucide-react";

const STATS = [
  { value: "7", label: "Entity Types Supported" },
  { value: "28", label: "Indian States Covered" },
  { value: "50+", label: "Compliance Tasks Tracked" },
  { value: "50+", label: "Service Marketplace Items" },
];

const PRINCIPLES = [
  {
    icon: <Building2 className="w-5 h-5" />,
    title: "Company-scoped everything",
    description:
      "Every feature, every data point, every workflow is scoped to a company. No cross-contamination, no confusion.",
  },
  {
    icon: <Users className="w-5 h-5" />,
    title: "Role-based, not app-based",
    description:
      "Founders, CAs, investors, and admins all use the same platform with experiences tailored to their role.",
  },
  {
    icon: <ArrowRight className="w-5 h-5" />,
    title: "No dead ends",
    description:
      "Every screen leads somewhere. Every status has a next step. Every workflow has a clear path forward.",
  },
  {
    icon: <Target className="w-5 h-5" />,
    title: "Payment where the intent is",
    description:
      "Pricing is transparent and shown at the point of decision — not hidden behind calls or negotiations.",
  },
  {
    icon: <Layers className="w-5 h-5" />,
    title: "Progressive disclosure",
    description:
      "Start simple. Reveal complexity only when needed. A first-time founder and a Series B CFO both feel at home.",
  },
  {
    icon: <Eye className="w-5 h-5" />,
    title: "Clean, professional aesthetic",
    description:
      "No clutter, no gimmicks. A calm, credible interface that treats founders as professionals, not leads.",
  },
];

export default function AboutPage() {
  return (
    <div className="glow-bg">
      <Header />

      {/* ── Hero ── */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-16 text-center">
        <div className="animate-fade-in-up max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-purple-50 border border-purple-100 text-purple-700 text-xs font-semibold uppercase tracking-wider mb-6">
            About Anvils
          </div>
          <h1
            className="text-4xl md:text-5xl lg:text-6xl font-extrabold leading-tight mb-6 text-[var(--color-text-primary)]"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Building the operating system for{" "}
            <span className="gradient-text">Indian companies</span>
          </h1>
          <p className="text-lg md:text-xl text-[var(--color-text-secondary)] leading-relaxed mb-10 max-w-2xl mx-auto">
            Anvils combines the product polish of Stripe Atlas, the lifecycle
            approach of SeedLegals, and deep India-specific regulatory expertise
            into a single platform for founders, investors, and professionals.
          </p>
        </div>
      </section>

      {/* ── Mission ── */}
      <section className="py-16 bg-[var(--color-bg-secondary)]">
        <div className="max-w-4xl mx-auto px-6">
          <div className="card-static p-8 md:p-12">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center">
                <Lightbulb className="w-5 h-5 text-purple-600" />
              </div>
              <h2
                className="text-2xl font-bold text-[var(--color-text-primary)]"
                style={{ fontFamily: "var(--font-display)" }}
              >
                Our Mission
              </h2>
            </div>
            <p className="text-[var(--color-text-secondary)] leading-relaxed mb-4">
              Every year, over 2 lakh companies are incorporated in India. Over
              1 lakh startups are recognized by DPIIT. Yet most founders still
              manage their equity in spreadsheets, track compliance through
              WhatsApp reminders from their CA, and have no single source of
              truth for their company&apos;s legal and financial health.
            </p>
            <p className="text-[var(--color-text-secondary)] leading-relaxed mb-4">
              Traditional CAs charge Rs 15,000-50,000 for incorporation with
              zero transparency. Online platforms handle registration but leave
              you on your own for equity, compliance, and governance. Global
              tools like Carta aren&apos;t built for Indian regulations — MCA
              filings, SEBI rules, state-wise stamp duty, Rule 11UA valuations.
            </p>
            <p className="text-[var(--color-text-secondary)] leading-relaxed font-medium">
              Anvils exists to change this. We&apos;re building a single platform
              that takes a company from incorporation through fundraising,
              compliance, and governance — with transparent pricing, automated
              tracking, and purpose-built tools for Indian regulations.
            </p>
          </div>
        </div>
      </section>

      {/* ── Stats ── */}
      <section className="py-16">
        <div className="max-w-5xl mx-auto px-6">
          <StatsBar stats={STATS} />
        </div>
      </section>

      {/* ── The Market ── */}
      <section className="py-16 bg-[var(--color-bg-secondary)]">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>The Indian startup <span className="gradient-text">opportunity</span></>}
            subtitle="India's entrepreneurial ecosystem is massive — and underserved by technology."
          />
          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="card-static p-6 text-center">
              <div
                className="text-3xl font-extrabold text-[var(--color-accent-purple)] mb-2"
                style={{ fontFamily: "var(--font-display)" }}
              >
                2 Lakh+
              </div>
              <p className="text-sm text-[var(--color-text-secondary)]">
                Companies incorporated annually via MCA
              </p>
            </div>
            <div className="card-static p-6 text-center">
              <div
                className="text-3xl font-extrabold text-[var(--color-accent-blue)] mb-2"
                style={{ fontFamily: "var(--font-display)" }}
              >
                10 Lakh+
              </div>
              <p className="text-sm text-[var(--color-text-secondary)]">
                Active LLPs and partnerships in India
              </p>
            </div>
            <div className="card-static p-6 text-center">
              <div
                className="text-3xl font-extrabold text-[var(--color-accent-emerald)] mb-2"
                style={{ fontFamily: "var(--font-display)" }}
              >
                1,00,000+
              </div>
              <p className="text-sm text-[var(--color-text-secondary)]">
                DPIIT-recognized startups and growing
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Design Principles ── */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>How we <span className="gradient-text">build</span></>}
            subtitle="The design principles that guide every feature we ship."
          />
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {PRINCIPLES.map((p) => (
              <div key={p.title} className="card-static p-6">
                <div className="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center mb-4">
                  <div className="text-purple-600">{p.icon}</div>
                </div>
                <h3 className="text-base font-bold text-[var(--color-text-primary)] mb-2">
                  {p.title}
                </h3>
                <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                  {p.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── What We Cover ── */}
      <section className="py-16 bg-[var(--color-bg-secondary)]">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Who we <span className="gradient-text">serve</span></>}
            subtitle="One platform, three audiences, seamless collaboration."
          />
          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="card-static p-6">
              <div className="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center mb-4">
                <Shield className="w-5 h-5 text-purple-600" />
              </div>
              <h3 className="text-base font-bold text-[var(--color-text-primary)] mb-2">
                Founders
              </h3>
              <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                Incorporate, manage equity, track compliance, raise funding, and
                run your back-office from a single dashboard. Transparent pricing
                starting at Rs 999.
              </p>
            </div>
            <div className="card-static p-6">
              <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center mb-4">
                <Eye className="w-5 h-5 text-blue-600" />
              </div>
              <h3 className="text-base font-bold text-[var(--color-text-primary)] mb-2">
                Investors
              </h3>
              <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                View portfolio holdings, access cap tables, browse data rooms,
                and discover deals — all with a secure token link, no account
                required.
              </p>
            </div>
            <div className="card-static p-6">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center mb-4">
                <Building2 className="w-5 h-5 text-emerald-600" />
              </div>
              <h3 className="text-base font-bold text-[var(--color-text-primary)] mb-2">
                CAs & Professionals
              </h3>
              <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                Manage all your clients from one dashboard with cross-company
                compliance calendars, filing trackers, and marketplace
                fulfillment earning Rs 1-2.5L+ annually.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <CTASection
        title="Ready to get started?"
        subtitle="Join the growing ecosystem of Indian companies, investors, and professionals on Anvils."
        primaryCTA={{ label: "Start Free", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <Footer />
      <ChatWidget />
    </div>
  );
}
