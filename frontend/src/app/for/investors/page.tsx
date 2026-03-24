"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/header";
import Footer from "@/components/footer";
import ChatWidget from "@/components/chat-widget";
import HeroSection from "@/components/marketing/hero-section";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import FeatureCard from "@/components/marketing/feature-card";
import {
  BarChart3,
  PieChart,
  TrendingUp,
  FolderOpen,
  Award,
  Search,
  Shield,
  KeyRound,
  ClipboardCheck,
  ArrowRight,
} from "lucide-react";

const HOW_IT_WORKS = [
  {
    step: "01",
    title: "Your founder adds you",
    desc: "They generate a secure, encrypted portal link from their Anvils dashboard. You receive it via email.",
  },
  {
    step: "02",
    title: "Open your dashboard",
    desc: "View your holdings, cap table position, funding round history, and documents. Everything in one place.",
  },
  {
    step: "03",
    title: "Stay updated",
    desc: "Get notified when new rounds open, documents are shared, or your holdings change. Always in the loop.",
  },
];

const FEATURES = [
  {
    icon: <BarChart3 className="w-5 h-5" />,
    title: "Portfolio Dashboard",
    description:
      "Total holdings, ownership percentages, and portfolio value across all companies on Anvils.",
    accentColor: "purple" as const,
  },
  {
    icon: <PieChart className="w-5 h-5" />,
    title: "Cap Table Transparency",
    description:
      "Real-time cap table with share classes, dilution events, and your exact position.",
    accentColor: "blue" as const,
  },
  {
    icon: <TrendingUp className="w-5 h-5" />,
    title: "Funding Round History",
    description:
      "Every round, instrument type, valuation, and investment — complete audit trail.",
    accentColor: "emerald" as const,
  },
  {
    icon: <FolderOpen className="w-5 h-5" />,
    title: "Document Access",
    description:
      "Data room files shared by founders: SHA, SSA, pitch decks, financials — organized by category.",
    accentColor: "purple" as const,
  },
  {
    icon: <Award className="w-5 h-5" />,
    title: "ESOP Visibility",
    description:
      "If you hold options, see your vesting schedule, exercise price, and grant details.",
    accentColor: "blue" as const,
  },
  {
    icon: <Search className="w-5 h-5" />,
    title: "Deal Discovery",
    description:
      "Browse companies actively raising on Anvils and express interest directly.",
    accentColor: "emerald" as const,
  },
];

const TRUST_SIGNALS = [
  {
    icon: <Shield className="w-6 h-6" />,
    title: "End-to-end encryption",
    desc: "All data encrypted in transit and at rest using industry-standard protocols.",
    color: "purple",
  },
  {
    icon: <KeyRound className="w-6 h-6" />,
    title: "Token-based access",
    desc: "Secure portal links with optional OTP verification. No passwords to manage.",
    color: "blue",
  },
  {
    icon: <ClipboardCheck className="w-6 h-6" />,
    title: "Full audit trail",
    desc: "Every access logged with IP address, timestamp, and user agent for complete accountability.",
    color: "emerald",
  },
];

const TRUST_COLOR_MAP: Record<string, { bg: string; text: string }> = {
  purple: { bg: "bg-purple-100", text: "text-purple-600" },
  blue: { bg: "bg-blue-100", text: "text-blue-600" },
  emerald: { bg: "bg-emerald-100", text: "text-emerald-600" },
};

export default function ForInvestorsPage() {
  const router = useRouter();
  const [token, setToken] = useState("");

  const handleTokenSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (token.trim()) {
      router.push(`/investor-portal?token=${token.trim()}`);
    }
  };

  return (
    <div className="glow-bg">
      <Header />

      {/* ══════ Section 1: Hero ══════ */}
      <HeroSection
        badge="For Investors"
        title={
          <>
            See your entire portfolio{" "}
            <span className="gradient-text">in one place</span>
          </>
        }
        subtitle="Access cap tables, holdings, data rooms, and funding history across all your portfolio companies — with a secure link, no account required."
        primaryCTA={{ label: "Access Your Portfolio", href: "#token-entry" }}
        secondaryCTA={{ label: "Learn More", href: "#how-it-works" }}
      />

      {/* ══════ Section 2: How It Works ══════ */}
      <section id="how-it-works" className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={
              <>
                How it <span className="gradient-text">works</span>
              </>
            }
            subtitle="Three steps to full portfolio visibility."
          />
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {HOW_IT_WORKS.map((step, i) => (
              <div
                key={step.step}
                className="card-static p-8 text-center relative"
              >
                <div className="w-12 h-12 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center mx-auto mb-4 text-sm font-bold">
                  {step.step}
                </div>
                <h3
                  className="text-xl font-bold text-[var(--color-text-primary)] mb-3"
                  style={{ fontFamily: "var(--font-display)" }}
                >
                  {step.title}
                </h3>
                <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                  {step.desc}
                </p>
                {i < HOW_IT_WORKS.length - 1 && (
                  <ArrowRight className="hidden md:block absolute -right-5 top-1/2 -translate-y-1/2 w-5 h-5 text-[var(--color-text-muted)]" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════ Section 3: Token Entry ══════ */}
      <section
        id="token-entry"
        className="py-20 bg-[var(--color-bg-secondary)]"
      >
        <div className="max-w-lg mx-auto px-6">
          <div className="card-static p-8 md:p-10">
            <h2
              className="text-2xl md:text-3xl font-bold text-[var(--color-text-primary)] mb-3 text-center"
              style={{ fontFamily: "var(--font-display)" }}
            >
              Access your investor portal
            </h2>
            <p className="text-[var(--color-text-secondary)] text-center mb-8">
              Paste the secure token your founder shared with you.
            </p>
            <form onSubmit={handleTokenSubmit} className="space-y-4">
              <input
                type="text"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="Paste your portal token..."
                className="input-field w-full"
              />
              <button
                type="submit"
                disabled={!token.trim()}
                className="btn-primary w-full !py-3 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Access Portfolio
              </button>
            </form>
            <p className="text-xs text-[var(--color-text-muted)] text-center mt-4">
              Don&apos;t have a token? Ask your founder to invite you from their
              Anvils dashboard.
            </p>
            <div className="flex items-center justify-center gap-2 mt-6 pt-6 border-t border-[var(--color-border)]">
              <Shield className="w-4 h-4 text-[var(--color-text-muted)]" />
              <p className="text-xs text-[var(--color-text-muted)]">
                Your data is encrypted end-to-end. We never share investor
                information.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ══════ Section 4: What You Can Access ══════ */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={
              <>
                Everything you need to{" "}
                <span className="gradient-text">see</span>
              </>
            }
            subtitle="Full transparency into your portfolio companies."
          />
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((feature) => (
              <FeatureCard
                key={feature.title}
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
                accentColor={feature.accentColor}
              />
            ))}
          </div>
        </div>
      </section>

      {/* ══════ Section 5: Security & Trust ══════ */}
      <section className="py-20 bg-[var(--color-bg-secondary)]">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={
              <>
                Your portfolio data is{" "}
                <span className="gradient-text">safe</span>
              </>
            }
          />
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {TRUST_SIGNALS.map((signal) => {
              const colors = TRUST_COLOR_MAP[signal.color];
              return (
                <div
                  key={signal.title}
                  className="card-static p-8 text-center"
                >
                  <div
                    className={`w-14 h-14 rounded-full ${colors.bg} ${colors.text} flex items-center justify-center mx-auto mb-5`}
                  >
                    {signal.icon}
                  </div>
                  <h3
                    className="text-lg font-bold text-[var(--color-text-primary)] mb-2"
                    style={{ fontFamily: "var(--font-display)" }}
                  >
                    {signal.title}
                  </h3>
                  <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                    {signal.desc}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ══════ Section 6: CTA ══════ */}
      <CTASection
        title="Get started in 30 seconds"
        subtitle="No account, no password, no friction. Just paste your token and see your portfolio."
        primaryCTA={{ label: "Access Portfolio", href: "#token-entry" }}
        secondaryCTA={{ label: "Learn More", href: "/for/founders" }}
        variant="purple"
      />

      <Footer />
      <ChatWidget />
    </div>
  );
}
