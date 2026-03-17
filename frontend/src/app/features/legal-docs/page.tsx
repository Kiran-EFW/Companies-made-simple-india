import { Metadata } from "next";
import Header from "@/components/header";
import Footer from "@/components/footer";
import HeroSection from "@/components/marketing/hero-section";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import { FileText, PenTool, Sparkles, FolderOpen, Clock, Shield } from "lucide-react";

export const metadata: Metadata = {
  title: "Legal Documents & E-Signatures — Anvils",
  description: "AI-drafted legal documents with e-signatures. NDAs, employment agreements, SHA/SSA, board resolutions, and more for Indian companies.",
};

const FEATURES = [
  { icon: <Sparkles className="w-5 h-5" />, title: "AI-Drafted Documents", desc: "Generate NDAs, employment agreements, SHA/SSA, and board resolutions tailored to your company details and Indian law." },
  { icon: <PenTool className="w-5 h-5" />, title: "E-Signatures", desc: "Send documents for signing with secure, timestamped electronic signatures. Track signing status in real time." },
  { icon: <FileText className="w-5 h-5" />, title: "Template Library", desc: "Pre-built templates for common startup documents — founder agreements, consulting contracts, IP assignment, and more." },
  { icon: <FolderOpen className="w-5 h-5" />, title: "Document Storage", desc: "All generated and signed documents stored securely. Searchable archive with version history." },
  { icon: <Clock className="w-5 h-5" />, title: "Signing Workflows", desc: "Multi-party signing with defined order. Automatic reminders for pending signatories." },
  { icon: <Shield className="w-5 h-5" />, title: "Legal Compliance", desc: "Documents follow Indian contract law requirements. Proper stamp duty considerations and jurisdiction clauses." },
];

export default function LegalDocsFeaturePage() {
  return (
    <div>
      <Header />

      <HeroSection
        badge="Product"
        title={<>Legal documents, <span className="gradient-text">drafted and signed</span></>}
        subtitle="AI-generated contracts tailored to Indian law. Send for e-signatures, track status, and store everything securely."
        primaryCTA={{ label: "Get Started", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>From draft to <span className="gradient-text">signed</span> in minutes</>}
            subtitle="Generate, send, sign, and store — all without leaving the platform."
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
        title="Stop paying lawyers for template documents"
        subtitle="Generate compliant legal documents in seconds, not days."
        primaryCTA={{ label: "Get Started", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <Footer />
    </div>
  );
}
