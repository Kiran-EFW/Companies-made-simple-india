import { Metadata } from "next";
import Header from "@/components/header";
import Footer from "@/components/footer";
import HeroSection from "@/components/marketing/hero-section";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import {
  BarChart3,
  Users,
  TrendingUp,
  Shield,
  Calculator,
  Calendar,
  FileText,
  FolderLock,
  BookOpen,
  Receipt,
  ShoppingBag,
  ClipboardList,
} from "lucide-react";

export const metadata: Metadata = {
  title: "Anvils for Founders — Equity, Compliance & Growth Tools",
  description: "Cap table management, ESOP administration, fundraising tools, compliance automation, valuations, and more. Purpose-built for Indian startup founders.",
};

const MAIN_FEATURES = [
  {
    icon: <BarChart3 className="w-6 h-6" />,
    title: "Cap Table Management",
    desc: "Track every shareholder, share type, and transaction. Model dilution before you raise. Compare multiple funding scenarios side by side. Generate share certificates and maintain a clean audit trail.",
    bullets: ["Shareholder register", "Dilution modeling", "Scenario comparison", "Share certificates", "Convertible tracking"],
    color: "purple",
    href: "/features/cap-table",
  },
  {
    icon: <Users className="w-6 h-6" />,
    title: "ESOP Management",
    desc: "Create stock option plans with board resolution tracking. Manage individual grants with cliff periods and vesting schedules. Handle exercise workflows with automatic cap table updates and FMV compliance.",
    bullets: ["Plan creation & activation", "Grant management", "Vesting schedules", "Exercise workflow", "FMV-linked pricing"],
    color: "blue",
    href: "/features/esop",
  },
  {
    icon: <TrendingUp className="w-6 h-6" />,
    title: "Fundraising",
    desc: "Create funding rounds for equity, SAFEs, or convertible notes. Track investors and manage closing rooms with document checklists. Auto-generate post-raise filings like PAS-3 and MGT-14.",
    bullets: ["Round management", "Investor tracking", "Closing room", "SHA/SSA generation", "Post-raise filings"],
    color: "emerald",
    href: "/features/fundraising",
  },
  {
    icon: <Shield className="w-6 h-6" />,
    title: "Compliance Calendar",
    desc: "Automated compliance task generation based on your incorporation date. Track ROC filings, board meetings, GST returns, and statutory audit deadlines. Escalation alerts when deadlines approach.",
    bullets: ["Auto-generated tasks", "ROC annual returns", "Board meeting scheduling", "GST deadline tracking", "Compliance scoring"],
    color: "purple",
    href: "/features/compliance",
  },
  {
    icon: <Calculator className="w-6 h-6" />,
    title: "Valuations",
    desc: "Rule 11UA-compliant fair market valuations using NAV and simplified DCF methods. Essential for ESOP exercise pricing, FEMA compliance, and investor reporting.",
    bullets: ["NAV method", "DCF method", "Valuation history", "ESOP FMV integration", "Audit-ready reports"],
    color: "blue",
  },
];

const MORE_TOOLS = [
  { icon: <Calendar className="w-5 h-5" />, title: "Board Meetings", desc: "Schedule, track attendance, generate minutes" },
  { icon: <ClipboardList className="w-5 h-5" />, title: "Statutory Registers", desc: "Members, directors, shares, charges" },
  { icon: <FileText className="w-5 h-5" />, title: "Legal Documents", desc: "AI-drafted contracts with e-signatures" },
  { icon: <FolderLock className="w-5 h-5" />, title: "Data Room", desc: "Secure, time-limited document sharing" },
  { icon: <BookOpen className="w-5 h-5" />, title: "Accounting Integration", desc: "Zoho Books & Tally sync" },
  { icon: <Receipt className="w-5 h-5" />, title: "GST & Tax", desc: "Returns, TDS, and tax overview" },
  { icon: <ShoppingBag className="w-5 h-5" />, title: "Services Marketplace", desc: "GST registration, trademark, DPIIT" },
];

const COLOR_MAP: Record<string, { bg: string; text: string; bullet: string }> = {
  purple: { bg: "bg-purple-50", text: "text-purple-600", bullet: "text-purple-400" },
  blue: { bg: "bg-blue-50", text: "text-blue-600", bullet: "text-blue-400" },
  emerald: { bg: "bg-emerald-50", text: "text-emerald-600", bullet: "text-emerald-400" },
};

export default function ForFoundersPage() {
  return (
    <div>
      <Header />

      <HeroSection
        badge="For Founders"
        title={<>Everything your startup needs to <span className="gradient-text">stay compliant and grow</span></>}
        subtitle="Cap table, ESOP, fundraising, compliance, valuations, legal documents, and more -- in one platform built for Indian startups."
        primaryCTA={{ label: "Get Started Free", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      {/* Feature Deep-Dives */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6 space-y-20">
          {MAIN_FEATURES.map((feature, i) => {
            const colors = COLOR_MAP[feature.color];
            const isReversed = i % 2 === 1;
            return (
              <div key={feature.title} className={`flex flex-col ${isReversed ? "md:flex-row-reverse" : "md:flex-row"} gap-10 items-center`}>
                <div className="flex-1">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${colors.bg}`}>
                    <div className={colors.text}>{feature.icon}</div>
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-3" style={{ fontFamily: "var(--font-display)" }}>
                    {feature.title}
                  </h3>
                  <p className="text-gray-500 leading-relaxed mb-4">{feature.desc}</p>
                  <ul className="space-y-2">
                    {feature.bullets.map((b) => (
                      <li key={b} className="flex items-center gap-2 text-sm text-gray-600">
                        <svg className={`w-4 h-4 shrink-0 ${colors.bullet}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                        {b}
                      </li>
                    ))}
                  </ul>
                  {feature.href && (
                    <a href={feature.href} className={`inline-flex items-center gap-1 mt-4 text-sm font-semibold ${colors.text} hover:underline`}>
                      Learn more &rarr;
                    </a>
                  )}
                </div>
                <div className="flex-1 w-full">
                  <div className="bg-gray-50 border border-gray-200 rounded-2xl h-64 flex items-center justify-center">
                    <div className={`${colors.text} opacity-20`}>
                      {/* Placeholder for future screenshots */}
                      <div className="w-16 h-16">{feature.icon}</div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* More Tools Grid */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>And <span className="gradient-text">even more</span> tools</>}
            subtitle="Everything else your back-office needs."
          />
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {MORE_TOOLS.map((tool) => (
              <div key={tool.title} className="card-static p-5">
                <div className="w-9 h-9 rounded-lg bg-purple-50 flex items-center justify-center text-purple-600 mb-3">
                  {tool.icon}
                </div>
                <h4 className="text-sm font-bold text-gray-900 mb-1">{tool.title}</h4>
                <p className="text-xs text-gray-500">{tool.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <CTASection
        title="Start managing your company today"
        subtitle="Free to get started. Upgrade as you grow."
        primaryCTA={{ label: "Get Started Free", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <Footer />
    </div>
  );
}
