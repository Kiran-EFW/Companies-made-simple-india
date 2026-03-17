import { Metadata } from "next";
import Header from "@/components/header";
import Footer from "@/components/footer";
import HeroSection from "@/components/marketing/hero-section";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import { Shield, Calendar, Bell, BarChart3, FileText, AlertTriangle } from "lucide-react";

export const metadata: Metadata = {
  title: "Compliance Calendar — Anvils",
  description: "Automated compliance tracking for Indian companies. ROC filings, board meetings, GST deadlines, and escalation alerts.",
};

const FEATURES = [
  { icon: <Calendar className="w-5 h-5" />, title: "Automated Task Generation", desc: "Compliance tasks are auto-generated based on your incorporation date, entity type, and regulatory requirements." },
  { icon: <FileText className="w-5 h-5" />, title: "ROC Annual Returns", desc: "Track all MCA/ROC filings including annual returns, financial statements, and change notifications." },
  { icon: <Shield className="w-5 h-5" />, title: "Board Meeting Scheduling", desc: "Schedule board meetings with notice generation, attendance tracking, and minutes drafting." },
  { icon: <Bell className="w-5 h-5" />, title: "GST Deadline Tracking", desc: "Never miss a GST return deadline. Track GSTR-1, GSTR-3B, and annual returns." },
  { icon: <AlertTriangle className="w-5 h-5" />, title: "Escalation Alerts", desc: "Automatic alerts when deadlines approach. Upgrade to have our team handle the filings for you." },
  { icon: <BarChart3 className="w-5 h-5" />, title: "Compliance Scoring", desc: "Real-time compliance score that shows your company's regulatory health at a glance." },
];

export default function ComplianceFeaturePage() {
  return (
    <div>
      <Header />

      <HeroSection
        badge="Product"
        title={<>Automated compliance for <span className="gradient-text">Indian companies</span></>}
        subtitle="Never miss a filing. Anvils tracks every ROC, GST, and TDS deadline — and our team can handle the filing for you."
        primaryCTA={{ label: "Automate Your Compliance", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Stay on top of <span className="gradient-text">every deadline</span></>}
            subtitle="A compliance calendar that works for you, not against you."
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

      <CTASection
        title="Zero missed deadlines, zero penalties"
        subtitle="See every deadline. Know your penalty exposure. Let our team file for you."
        primaryCTA={{ label: "Get Started", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <Footer />
    </div>
  );
}
