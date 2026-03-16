import { Metadata } from "next";
import Header from "@/components/header";
import Footer from "@/components/footer";
import HeroSection from "@/components/marketing/hero-section";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import { BarChart3, Users, GitBranch, FileCheck, TrendingDown, Repeat } from "lucide-react";

export const metadata: Metadata = {
  title: "Cap Table Management — Anvils",
  description: "Track shareholders, model dilution, compare scenarios, and generate share certificates. Purpose-built for Indian startups.",
};

const FEATURES = [
  { icon: <Users className="w-5 h-5" />, title: "Shareholder Register", desc: "Complete record of every shareholder, share type, allotment date, and transaction history." },
  { icon: <TrendingDown className="w-5 h-5" />, title: "Dilution Modeling", desc: "Preview how a new round will affect every shareholder's percentage before you commit." },
  { icon: <GitBranch className="w-5 h-5" />, title: "Scenario Comparison", desc: "Save and compare multiple funding scenarios side by side to find the best terms." },
  { icon: <FileCheck className="w-5 h-5" />, title: "Share Certificates", desc: "Generate professional share certificates with company details and allotment information." },
  { icon: <Repeat className="w-5 h-5" />, title: "Convertible Instruments", desc: "Track SAFEs, convertible notes, and CCDs. Preview and execute conversion to equity." },
  { icon: <BarChart3 className="w-5 h-5" />, title: "Exit Waterfall", desc: "Model liquidation scenarios and see how proceeds distribute across share classes." },
];

const BENEFITS = [
  { title: "Real-time ownership view", desc: "Always know who owns what percentage of your company." },
  { title: "Model before you dilute", desc: "Never be surprised by the impact of a new round on your ownership." },
  { title: "Investor-ready cap table", desc: "Clean, professional cap table you can share with investors and legal counsel." },
];

export default function CapTableFeaturePage() {
  return (
    <div>
      <Header />

      <HeroSection
        badge="Product"
        title={<>Cap table management that <span className="gradient-text">grows with you</span></>}
        subtitle="From your first shareholders to complex multi-round funding structures. Track everything, model anything, share with confidence."
        primaryCTA={{ label: "Set Up Your Cap Table", href: "/cap-table-setup" }}
        secondaryCTA={{ label: "Get Started", href: "/signup" }}
      />

      {/* Features Grid */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Everything you need to <span className="gradient-text">manage equity</span></>}
            subtitle="A complete cap table solution built for Indian company law."
          />
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((f) => (
              <div key={f.title} className="card-static p-6">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4 bg-purple-50">
                  <div className="text-purple-600">{f.icon}</div>
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{f.title}</h3>
                <p className="text-sm text-gray-500 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-6">
          <SectionHeader title={<>Why founders choose <span className="gradient-text">Anvils</span></>} />
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
        title="Try our free cap table builder"
        subtitle="No signup required. Build your cap table in 2 minutes."
        primaryCTA={{ label: "Build Cap Table Free", href: "/cap-table-setup" }}
        secondaryCTA={{ label: "Get Started", href: "/signup" }}
      />

      <Footer />
    </div>
  );
}
