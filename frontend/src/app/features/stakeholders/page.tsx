import { Metadata } from "next";
import Header from "@/components/header";
import Footer from "@/components/footer";
import HeroSection from "@/components/marketing/hero-section";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import { Users, UserCheck, Building2, Shield, Mail, FileText } from "lucide-react";

export const metadata: Metadata = {
  title: "Stakeholder Management — Anvils",
  description: "Manage shareholders, directors, auditors, and key contacts in one place. Track KYC, roles, and contact details for compliance.",
};

const FEATURES = [
  { icon: <Users className="w-5 h-5" />, title: "Shareholder Profiles", desc: "Complete profiles for every shareholder including PAN, address, contact details, and shareholding history." },
  { icon: <UserCheck className="w-5 h-5" />, title: "Director Management", desc: "Track directors with DIN, appointment dates, tenure, and board committee memberships." },
  { icon: <Building2 className="w-5 h-5" />, title: "Auditor Management", desc: "Maintain auditor appointment details, tenure tracking, and ADT-1 filing coordination." },
  { icon: <Shield className="w-5 h-5" />, title: "KYC & Compliance", desc: "Centralized KYC document storage for all stakeholders. Never scramble for PAN cards or address proofs again." },
  { icon: <Mail className="w-5 h-5" />, title: "Contact Directory", desc: "Email and phone details for all key people. Quick access when you need to reach shareholders or directors." },
  { icon: <FileText className="w-5 h-5" />, title: "Statutory Register Link", desc: "Stakeholder data feeds directly into statutory registers — members, directors, and charges registers stay in sync." },
];

export default function StakeholdersFeaturePage() {
  return (
    <div>
      <Header />

      <HeroSection
        badge="Product"
        title={<>Every stakeholder, <span className="gradient-text">one place</span></>}
        subtitle="Shareholders, directors, auditors, and key contacts. Complete profiles with KYC documents, roles, and contact details."
        primaryCTA={{ label: "Get Started", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Know your <span className="gradient-text">people</span></>}
            subtitle="A single source of truth for everyone connected to your company."
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
        title="Stop digging through emails for KYC documents"
        subtitle="Centralize all stakeholder information in one platform."
        primaryCTA={{ label: "Get Started", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <Footer />
    </div>
  );
}
