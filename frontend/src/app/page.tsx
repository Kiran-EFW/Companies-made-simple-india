import Link from "next/link";
import ChatWidget from "@/components/chat-widget";

const ENTITY_CARDS = [
  {
    type: "Private Limited",
    emoji: "🏢",
    desc: "Best for startups seeking funding. Most popular in India.",
    from: "₹4,999",
    badge: "Most Popular",
    color: "purple",
  },
  {
    type: "OPC",
    emoji: "👤",
    desc: "Solo founders with limited liability. One person, full control.",
    from: "₹3,499",
    badge: "Solo Founder",
    color: "blue",
  },
  {
    type: "LLP",
    emoji: "🤝",
    desc: "Partners with limited liability. Best for services & consulting.",
    from: "₹3,999",
    badge: "Low Compliance",
    color: "emerald",
  },
  {
    type: "Section 8",
    emoji: "💚",
    desc: "Non-profit company for social impact. Tax exemptions available.",
    from: "₹7,999",
    badge: "Non-Profit",
    color: "amber",
  },
];

const STEPS = [
  {
    num: "01",
    title: "Choose Your Entity",
    desc: "Our AI wizard asks 5 smart questions to recommend the perfect company type for your situation.",
    icon: "🎯",
  },
  {
    num: "02",
    title: "See Real Costs",
    desc: "Transparent pricing with zero hidden fees. State-wise stamp duty, DSC, government fees — all itemized before you pay.",
    icon: "💰",
  },
  {
    num: "03",
    title: "We Handle Everything",
    desc: "AI processes your documents, drafts filings, and our CS team verifies everything. Track progress in real-time.",
    icon: "🚀",
  },
];

const TRUST_SIGNALS = [
  { metric: "31", label: "States Supported" },
  { metric: "5", label: "Entity Types" },
  { metric: "0", label: "Hidden Fees" },
  { metric: "100%", label: "Transparent" },
];

export default function HomePage() {
  return (
    <div className="glow-bg">
      {/* ── Navigation ── */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-5 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <span className="text-2xl">⚡</span>
          <span
            className="text-xl font-bold"
            style={{ fontFamily: "var(--font-display)" }}
          >
            <span className="gradient-text">CMS</span>{" "}
            <span style={{ color: "var(--color-text-secondary)" }}>India</span>
          </span>
        </div>
        <div className="hidden md:flex items-center gap-8">
          <Link
            href="/pricing"
            className="text-sm font-medium hover:text-white transition-colors"
            style={{ color: "var(--color-text-secondary)" }}
          >
            Pricing
          </Link>
          <Link
            href="/wizard"
            className="text-sm font-medium hover:text-white transition-colors"
            style={{ color: "var(--color-text-secondary)" }}
          >
            Entity Wizard
          </Link>
          <button className="btn-primary text-sm !py-2 !px-5">
            Get Started
          </button>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 pt-16 pb-24 text-center">
        <div className="animate-fade-in-up">
          <div className="badge badge-purple mb-6 mx-auto w-fit">
            ✨ AI-Powered • Expert-Verified
          </div>
          <h1
            className="text-5xl md:text-7xl font-extrabold leading-tight mb-6"
            style={{ fontFamily: "var(--font-display)" }}
          >
            From Idea to
            <br />
            <span className="gradient-text">Incorporated Company</span>
            <br />
            in Days, Not Months
          </h1>
          <p
            className="text-lg md:text-xl max-w-2xl mx-auto mb-10 leading-relaxed"
            style={{ color: "var(--color-text-secondary)" }}
          >
            India&#39;s first AI-native company incorporation platform. Transparent
            pricing, zero hidden fees, and a CS team that verifies every filing.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/wizard" className="btn-primary text-lg !py-4 !px-8">
              Find Your Entity Type →
            </Link>
            <Link
              href="/pricing"
              className="btn-secondary text-lg !py-4 !px-8"
            >
              See Pricing
            </Link>
          </div>
        </div>

        {/* Trust Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-20 animate-fade-in-up animate-delay-200">
          {TRUST_SIGNALS.map((s) => (
            <div key={s.label} className="text-center">
              <div
                className="text-3xl md:text-4xl font-bold gradient-text"
                style={{ fontFamily: "var(--font-display)" }}
              >
                {s.metric}
              </div>
              <div
                className="text-sm mt-1"
                style={{ color: "var(--color-text-muted)" }}
              >
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Entity Cards ── */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 pb-24">
        <h2
          className="text-3xl md:text-4xl font-bold text-center mb-4"
          style={{ fontFamily: "var(--font-display)" }}
        >
          Choose Your <span className="gradient-text">Company Type</span>
        </h2>
        <p
          className="text-center mb-12 max-w-xl mx-auto"
          style={{ color: "var(--color-text-secondary)" }}
        >
          Not sure which one? Our{" "}
          <Link
            href="/wizard"
            className="underline"
            style={{ color: "var(--color-accent-purple-light)" }}
          >
            AI wizard
          </Link>{" "}
          will recommend the best fit in 60 seconds.
        </p>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {ENTITY_CARDS.map((card, i) => (
            <Link
              key={card.type}
              href={`/pricing?entity=${card.type.toLowerCase().replace(/\s+/g, "_")}`}
              className={`glass-card p-6 block animate-fade-in-up animate-delay-${(i + 1) * 100}`}
            >
              <div className="text-4xl mb-4">{card.emoji}</div>
              <div
                className={`badge mb-3 ${card.color === "purple" ? "badge-purple" : card.color === "emerald" ? "badge-emerald" : "badge-purple"}`}
              >
                {card.badge}
              </div>
              <h3 className="text-xl font-bold mb-2">{card.type}</h3>
              <p
                className="text-sm mb-4 leading-relaxed"
                style={{ color: "var(--color-text-secondary)" }}
              >
                {card.desc}
              </p>
              <div className="flex items-baseline gap-1">
                <span
                  className="text-sm"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  Platform fee from
                </span>
                <span
                  className="text-lg font-bold"
                  style={{ color: "var(--color-accent-emerald-light)" }}
                >
                  {card.from}
                </span>
              </div>
              <div
                className="text-xs mt-1"
                style={{ color: "var(--color-text-muted)" }}
              >
                + government fees (shown before payment)
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* ── How It Works ── */}
      <section
        className="relative z-10 py-24"
        style={{ background: "var(--color-bg-secondary)" }}
      >
        <div className="max-w-7xl mx-auto px-6">
          <h2
            className="text-3xl md:text-4xl font-bold text-center mb-16"
            style={{ fontFamily: "var(--font-display)" }}
          >
            How It <span className="gradient-text">Works</span>
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {STEPS.map((step) => (
              <div key={step.num} className="glass-card p-8 text-center">
                <div className="text-5xl mb-4">{step.icon}</div>
                <div
                  className="text-sm font-bold mb-2"
                  style={{ color: "var(--color-accent-purple-light)" }}
                >
                  STEP {step.num}
                </div>
                <h3 className="text-xl font-bold mb-3">{step.title}</h3>
                <p
                  className="text-sm leading-relaxed"
                  style={{ color: "var(--color-text-secondary)" }}
                >
                  {step.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Transparency CTA ── */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 py-24 text-center">
        <div className="glass-card p-12 md:p-16 max-w-4xl mx-auto">
          <div className="text-5xl mb-6">🔍</div>
          <h2
            className="text-3xl md:text-4xl font-bold mb-4"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Zero Hidden Fees. <span className="gradient-text">Period.</span>
          </h2>
          <p
            className="text-lg mb-8 max-w-2xl mx-auto leading-relaxed"
            style={{ color: "var(--color-text-secondary)" }}
          >
            Unlike other platforms that advertise ₹999 and charge ₹15,000+, we
            show you the{" "}
            <strong style={{ color: "var(--color-text-primary)" }}>
              complete itemized breakdown
            </strong>{" "}
            — platform fee, government fees, stamp duty, DSC — all before you
            pay a single rupee.
          </p>
          <Link href="/pricing" className="btn-primary text-lg !py-4 !px-10">
            See Your Real Cost →
          </Link>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer
        className="relative z-10 py-12 border-t"
        style={{ borderColor: "var(--color-border)" }}
      >
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-lg">⚡</span>
            <span className="font-bold gradient-text">CMS India</span>
          </div>
          <p style={{ color: "var(--color-text-muted)" }} className="text-sm">
            © 2025 Companies Made Simple India. All rights reserved.
          </p>
        </div>
      </footer>

      <ChatWidget />
    </div>
  );
}
