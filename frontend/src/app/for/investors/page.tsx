"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/header";
import Footer from "@/components/footer";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import {
  Eye,
  BarChart3,
  TrendingUp,
  Users,
  FileText,
  Search,
  ArrowRight,
  Link2,
  LayoutDashboard,
  ShieldCheck,
} from "lucide-react";

const FEATURES = [
  { icon: <LayoutDashboard className="w-5 h-5" />, title: "Portfolio Dashboard", desc: "See all your investments across multiple companies in one view." },
  { icon: <BarChart3 className="w-5 h-5" />, title: "Cap Table Transparency", desc: "Full cap table visibility with your holdings highlighted." },
  { icon: <TrendingUp className="w-5 h-5" />, title: "Funding Round History", desc: "Track every round, your participation, and share allotments." },
  { icon: <Users className="w-5 h-5" />, title: "ESOP Grant Visibility", desc: "View your option grants, vesting schedules, and exercised options." },
  { icon: <FileText className="w-5 h-5" />, title: "Document Access", desc: "Download SHA, SSA, pitch decks, and other investment documents." },
  { icon: <Search className="w-5 h-5" />, title: "Company Discovery", desc: "Browse startups on Anvils that are actively fundraising." },
];

const HOW_IT_WORKS = [
  {
    step: "01",
    title: "Founder Adds You",
    desc: "When a founder lists you as a stakeholder on Anvils, they generate a unique portal link for you.",
    icon: <Link2 className="w-5 h-5" />,
  },
  {
    step: "02",
    title: "Access Your Dashboard",
    desc: "Open the link to see your portfolio, cap tables, ESOP grants, funding rounds, and documents.",
    icon: <LayoutDashboard className="w-5 h-5" />,
  },
  {
    step: "03",
    title: "No Account Needed",
    desc: "Everything works with just your token link. No signup, no password, no login required.",
    icon: <ShieldCheck className="w-5 h-5" />,
  },
];

export default function ForInvestorsPage() {
  const router = useRouter();
  const [token, setToken] = useState("");

  const handleTokenSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (token.trim()) {
      router.push(`/investor/${token.trim()}`);
    }
  };

  return (
    <div>
      <Header />

      {/* Hero with Token Entry */}
      <section className="max-w-7xl mx-auto px-6 pt-20 pb-24 text-center">
        <div className="animate-fade-in-up max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-50 border border-blue-100 text-blue-700 text-xs font-semibold uppercase tracking-wider mb-6">
            For Investors
          </div>
          <h1
            className="text-4xl md:text-5xl lg:text-6xl font-extrabold leading-tight mb-6 text-gray-900"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Full visibility into your portfolio &mdash;{" "}
            <span className="gradient-text">no login needed</span>
          </h1>
          <p className="text-lg md:text-xl text-gray-500 leading-relaxed mb-10">
            Access your holdings, cap tables, funding history, and documents
            through a secure token-based portal. Discover new companies seeking investment.
          </p>

          {/* Token Entry */}
          <form onSubmit={handleTokenSubmit} className="max-w-md mx-auto">
            <div className="flex gap-2">
              <input
                type="text"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="Paste your portal token..."
                className="flex-1 px-4 py-3 rounded-xl border border-gray-200 bg-white text-sm focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-100"
              />
              <button
                type="submit"
                disabled={!token.trim()}
                className="btn-primary !py-3 !px-6 disabled:opacity-50"
              >
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-2">
              Your portal token was shared by a founder on Anvils.
            </p>
          </form>
        </div>
      </section>

      {/* How Token Access Works */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>How it <span className="gradient-text">works</span></>}
            subtitle="No signup required. Access your portfolio in three simple steps."
          />
          <div className="grid md:grid-cols-3 gap-8">
            {HOW_IT_WORKS.map((step) => (
              <div key={step.step} className="card-static p-8 text-center">
                <div className="w-12 h-12 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center mx-auto mb-4">
                  {step.icon}
                </div>
                <div className="text-xs font-bold text-blue-600 mb-2">STEP {step.step}</div>
                <h3 className="text-xl font-bold text-gray-900 mb-3" style={{ fontFamily: "var(--font-display)" }}>
                  {step.title}
                </h3>
                <p className="text-sm text-gray-500 leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* What You Can See */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Everything you need, <span className="gradient-text">at a glance</span></>}
            subtitle="Your investor portal gives you full transparency across all your portfolio companies."
          />
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((f) => (
              <div key={f.title} className="card-static p-6">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4 bg-blue-50">
                  <div className="text-blue-600">{f.icon}</div>
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{f.title}</h3>
                <p className="text-sm text-gray-500 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Discovery Section */}
      <section id="discover" className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-50 border border-emerald-100 text-emerald-700 text-xs font-semibold uppercase tracking-wider mb-6">
            Company Discovery
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4" style={{ fontFamily: "var(--font-display)" }}>
            Find your next investment
          </h2>
          <p className="text-lg text-gray-500 mb-8 max-w-2xl mx-auto">
            Browse companies on Anvils that are actively fundraising. Filter by sector,
            stage, and investment range. Express interest directly through your portal.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="#" className="btn-secondary !py-3 !px-6">
              Available in your investor portal
            </a>
          </div>
        </div>
      </section>

      <CTASection
        title="Ask your portfolio companies to add you on Anvils"
        subtitle="Once they do, you'll get a portal link with full transparency into your holdings."
        primaryCTA={{ label: "Learn More", href: "/for/founders" }}
        variant="white"
      />

      <Footer />
    </div>
  );
}
