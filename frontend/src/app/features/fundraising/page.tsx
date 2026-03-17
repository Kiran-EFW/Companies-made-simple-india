import { Metadata } from "next";
import Header from "@/components/header";
import Footer from "@/components/footer";
import HeroSection from "@/components/marketing/hero-section";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import { TrendingUp, Users, FolderOpen, FileText, ClipboardCheck, BarChart3 } from "lucide-react";

export const metadata: Metadata = {
  title: "Fundraising — Anvils",
  description: "Run funding rounds, manage closing rooms, track investors, and generate post-raise filing drafts. Purpose-built for Indian startup fundraising.",
};

const FEATURES = [
  { icon: <TrendingUp className="w-5 h-5" />, title: "Round Management", desc: "Create equity, SAFE, or convertible note rounds. Set valuations, target amounts, and track progress." },
  { icon: <Users className="w-5 h-5" />, title: "Investor Tracking", desc: "Add investors, track commitments, manage term sheets, and communicate through the platform." },
  { icon: <FolderOpen className="w-5 h-5" />, title: "Closing Room", desc: "Organized workspace with document checklists, signature tracking, and closing timelines." },
  { icon: <FileText className="w-5 h-5" />, title: "SHA & SSA Generation", desc: "Generate Shareholders Agreement and Share Subscription Agreement drafts for your round." },
  { icon: <ClipboardCheck className="w-5 h-5" />, title: "Post-Raise Filings", desc: "Generate draft PAS-3 (Return of Allotment), MGT-14, SH-7, and other mandatory forms from your round data." },
  { icon: <BarChart3 className="w-5 h-5" />, title: "Convertible Conversion", desc: "Preview and execute SAFE/CCD to equity conversion with automatic cap table updates." },
];

export default function FundraisingFeaturePage() {
  return (
    <div>
      <Header />

      <HeroSection
        badge="Product"
        title={<>Close your funding round <span className="gradient-text">with confidence</span></>}
        subtitle="From term sheet to share allotment. Manage your entire fundraise, generate legal documents, and track post-raise compliance."
        primaryCTA={{ label: "Start Your Fundraise", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Everything you need to <span className="gradient-text">close your round</span></>}
            subtitle="A structured workflow from round creation to post-raise filings."
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
        title="Ready to raise your next round?"
        subtitle="Set up your fundraise and start tracking investors today."
        primaryCTA={{ label: "Get Started", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <Footer />
    </div>
  );
}
