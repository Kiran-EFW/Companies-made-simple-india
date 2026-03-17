import { Metadata } from "next";
import Header from "@/components/header";
import Footer from "@/components/footer";
import HeroSection from "@/components/marketing/hero-section";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import { Calculator, FileText, TrendingUp, History, Shield, BarChart3 } from "lucide-react";

export const metadata: Metadata = {
  title: "Valuations — Anvils",
  description: "Rule 11UA-compliant fair market valuations using NAV and DCF methods. Essential for ESOP pricing, FEMA compliance, and fundraising.",
};

const FEATURES = [
  { icon: <Calculator className="w-5 h-5" />, title: "NAV Method", desc: "Net Asset Value calculation using your latest balance sheet data. Auto-computed based on assets, liabilities, and outstanding shares." },
  { icon: <TrendingUp className="w-5 h-5" />, title: "DCF Method", desc: "Simplified discounted cash flow valuation with configurable growth rates, discount rates, and projection periods." },
  { icon: <History className="w-5 h-5" />, title: "Valuation History", desc: "Maintain a timeline of all valuations performed. Compare changes over time and track how your FMV evolves." },
  { icon: <Shield className="w-5 h-5" />, title: "ESOP FMV Integration", desc: "Valuations flow directly into ESOP exercise pricing. Ensure every grant and exercise uses a compliant fair market value." },
  { icon: <FileText className="w-5 h-5" />, title: "Audit-Ready Reports", desc: "Generate valuation reports that satisfy auditor requirements and regulatory scrutiny for ROC and FEMA filings." },
  { icon: <BarChart3 className="w-5 h-5" />, title: "Rule 11UA Compliance", desc: "Built specifically for Indian tax regulations. Valuations follow Rule 11UA methodology required for share allotments and transfers." },
];

const BENEFITS = [
  { title: "No more spreadsheets", desc: "Stop calculating FMV manually in Excel. Anvils automates the entire valuation process." },
  { title: "Always compliant", desc: "Valuations follow Rule 11UA so you never face issues during audits or regulatory reviews." },
  { title: "Connected to your cap table", desc: "Valuation data flows into ESOP pricing and fundraising rounds automatically." },
];

export default function ValuationsFeaturePage() {
  return (
    <div>
      <Header />

      <HeroSection
        badge="Product"
        title={<>Fair market valuations, <span className="gradient-text">built for India</span></>}
        subtitle="Rule 11UA-compliant NAV and DCF valuations for ESOP exercise pricing, share transfers, FEMA compliance, and investor reporting."
        primaryCTA={{ label: "Get Started", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Valuations that <span className="gradient-text">stand up to scrutiny</span></>}
            subtitle="From NAV calculations to full DCF models, everything your auditor needs."
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

      <section className="py-20">
        <div className="max-w-4xl mx-auto px-6">
          <SectionHeader title={<>Why founders use <span className="gradient-text">Anvils</span> for valuations</>} />
          <div className="grid md:grid-cols-3 gap-6">
            {BENEFITS.map((b) => (
              <div key={b.title} className="text-center">
                <h4 className="text-lg font-bold text-gray-900 mb-2">{b.title}</h4>
                <p className="text-sm text-gray-500">{b.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <CTASection
        title="Know your company's worth"
        subtitle="Compliant valuations in minutes, not weeks."
        primaryCTA={{ label: "Get Started", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <Footer />
    </div>
  );
}
