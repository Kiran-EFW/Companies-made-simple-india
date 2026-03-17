import { Metadata } from "next";
import Header from "@/components/header";
import Footer from "@/components/footer";
import HeroSection from "@/components/marketing/hero-section";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import { ShoppingBag, Receipt, Award, Building2, FileText, Shield } from "lucide-react";

export const metadata: Metadata = {
  title: "Services Marketplace — Anvils",
  description: "GST registration, trademark filing, DPIIT recognition, MSME registration, and more. Professional services for Indian startups.",
};

const SERVICES = [
  { icon: <Receipt className="w-5 h-5" />, title: "GST Registration", desc: "Complete GST registration with ARN tracking. Get your GSTIN issued through our network of verified professionals." },
  { icon: <Award className="w-5 h-5" />, title: "Trademark Filing", desc: "Trademark search, application filing, and status tracking. Protect your brand name and logo across all classes." },
  { icon: <Building2 className="w-5 h-5" />, title: "DPIIT Recognition", desc: "Apply for DPIIT startup recognition to unlock tax benefits, self-certification, and government scheme eligibility." },
  { icon: <ShoppingBag className="w-5 h-5" />, title: "MSME Registration", desc: "Udyam registration for MSME benefits including priority sector lending, subsidy schemes, and government tenders." },
  { icon: <FileText className="w-5 h-5" />, title: "Import-Export Code", desc: "IEC registration for companies planning to import or export goods and services." },
  { icon: <Shield className="w-5 h-5" />, title: "Professional Tax & Shops Act", desc: "State-level registrations including professional tax, shops & establishment act, and labour law compliance." },
];

export default function ServicesFeaturePage() {
  return (
    <div>
      <Header />

      <HeroSection
        badge="Marketplace"
        title={<>Professional services, <span className="gradient-text">on demand</span></>}
        subtitle="GST registration, trademark filing, DPIIT recognition, MSME registration, and more. Handled by verified professionals, tracked on your dashboard."
        primaryCTA={{ label: "Browse Services", href: "/services" }}
        secondaryCTA={{ label: "Get Started", href: "/signup" }}
      />

      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Everything your startup <span className="gradient-text">needs to register</span></>}
            subtitle="From GST to trademarks — order, track, and manage from your Anvils dashboard."
          />
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {SERVICES.map((f) => (
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
        title="All your registrations, handled"
        subtitle="Focus on building your company. We'll handle the paperwork."
        primaryCTA={{ label: "Browse Services", href: "/services" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <Footer />
    </div>
  );
}
