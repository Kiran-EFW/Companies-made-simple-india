import { Metadata } from "next";
import Header from "@/components/header";
import Footer from "@/components/footer";
import HeroSection from "@/components/marketing/hero-section";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import { BookOpen, RefreshCw, BarChart3, FileText, Link as LinkIcon, Database } from "lucide-react";

export const metadata: Metadata = {
  title: "Accounting Integration — Anvils",
  description: "Connect Zoho Books and Tally to Anvils. Sync financial data for valuations, compliance, and investor reporting.",
};

const FEATURES = [
  { icon: <LinkIcon className="w-5 h-5" />, title: "Zoho Books Integration", desc: "Connect your Zoho Books account and pull in financial data automatically. Balance sheets and P&L sync for valuations." },
  { icon: <Database className="w-5 h-5" />, title: "Tally Sync", desc: "Import data from Tally ERP for companies using desktop accounting. Upload Tally exports for seamless data flow." },
  { icon: <RefreshCw className="w-5 h-5" />, title: "Auto-Sync", desc: "Financial data refreshes automatically. Valuations and reports always use your latest numbers." },
  { icon: <BarChart3 className="w-5 h-5" />, title: "Financial Dashboard", desc: "View your connection status and synced financial data. Key metrics feed into valuations and compliance tracking." },
  { icon: <FileText className="w-5 h-5" />, title: "Valuation Input", desc: "Accounting data feeds directly into NAV and DCF valuations. No manual data entry between systems." },
  { icon: <BookOpen className="w-5 h-5" />, title: "Audit Preparation", desc: "Financial records organized alongside corporate documents. Everything your auditor needs, in one place." },
];

export default function AccountingFeaturePage() {
  return (
    <div>
      <Header />

      <HeroSection
        badge="Product"
        title={<>Your books, <span className="gradient-text">connected</span></>}
        subtitle="Sync Zoho Books or Tally with Anvils. Financial data syncs with your valuations, compliance tracking, and investor reports."
        primaryCTA={{ label: "Get Started", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Financial data, <span className="gradient-text">where you need it</span></>}
            subtitle="Connect your accounting software and stop re-entering numbers."
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

      <CTASection
        title="Connect your books in two clicks"
        subtitle="Zoho Books and Tally integration — no migration needed."
        primaryCTA={{ label: "Get Started", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <Footer />
    </div>
  );
}
