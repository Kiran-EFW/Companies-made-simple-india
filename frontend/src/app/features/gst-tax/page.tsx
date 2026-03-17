import { Metadata } from "next";
import Header from "@/components/header";
import Footer from "@/components/footer";
import HeroSection from "@/components/marketing/hero-section";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import { Receipt, Calendar, FileText, BarChart3, AlertTriangle, IndianRupee } from "lucide-react";

export const metadata: Metadata = {
  title: "GST & Tax — Anvils",
  description: "Track GST returns, TDS filings, advance tax, and tax overview for Indian companies. Deadline alerts and filing status tracking.",
};

const FEATURES = [
  { icon: <Receipt className="w-5 h-5" />, title: "GST Return Tracking", desc: "Track GSTR-1, GSTR-3B, GSTR-9, and annual returns. See filing status, due dates, and pending actions at a glance." },
  { icon: <Calendar className="w-5 h-5" />, title: "TDS Filing Calendar", desc: "Monthly and quarterly TDS return deadlines. Track Form 26Q, 24Q, and 27Q filing status." },
  { icon: <IndianRupee className="w-5 h-5" />, title: "Advance Tax Reminders", desc: "Quarterly advance tax installment reminders for June, September, December, and March deadlines." },
  { icon: <BarChart3 className="w-5 h-5" />, title: "Tax Overview Dashboard", desc: "See all tax obligations in one view — GST, TDS, advance tax, and income tax filing status." },
  { icon: <AlertTriangle className="w-5 h-5" />, title: "Deadline Alerts", desc: "Automatic alerts before due dates. Escalation to your CA when filings are approaching or overdue." },
  { icon: <FileText className="w-5 h-5" />, title: "Filing History", desc: "Complete record of all filings with dates, amounts, and acknowledgment numbers for audit readiness." },
];

export default function GstTaxFeaturePage() {
  return (
    <div>
      <Header />

      <HeroSection
        badge="Product"
        title={<>GST and tax, <span className="gradient-text">simplified</span></>}
        subtitle="Track every GST return, TDS filing, and advance tax deadline. Automatic reminders so you never miss a due date."
        primaryCTA={{ label: "Get Started", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Every tax deadline, <span className="gradient-text">tracked</span></>}
            subtitle="GST, TDS, advance tax, and income tax filings — all in one dashboard."
          />
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((f) => (
              <div key={f.title} className="card-static p-6">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4 bg-emerald-50">
                  <div className="text-emerald-600">{f.icon}</div>
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{f.title}</h3>
                <p className="text-sm text-gray-500 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <CTASection
        title="Zero missed tax deadlines"
        subtitle="Let Anvils track your GST and tax obligations automatically."
        primaryCTA={{ label: "Get Started", href: "/signup" }}
        secondaryCTA={{ label: "Invite Your CA", href: "/for/cas" }}
      />

      <Footer />
    </div>
  );
}
