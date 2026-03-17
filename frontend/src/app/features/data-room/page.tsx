import { Metadata } from "next";
import Header from "@/components/header";
import Footer from "@/components/footer";
import HeroSection from "@/components/marketing/hero-section";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import { FolderLock, Link as LinkIcon, Clock, Eye, Upload, Shield } from "lucide-react";

export const metadata: Metadata = {
  title: "Data Room — Anvils",
  description: "Secure, time-limited document sharing for due diligence, investor access, and regulatory filings. Built for Indian startups.",
};

const FEATURES = [
  { icon: <FolderLock className="w-5 h-5" />, title: "Secure Document Storage", desc: "Upload and organize company documents in encrypted storage. Cap table exports, financials, contracts, and compliance records." },
  { icon: <LinkIcon className="w-5 h-5" />, title: "Shareable Links", desc: "Generate secure, unique links for each document or folder. Share with investors, lawyers, or auditors without creating accounts." },
  { icon: <Clock className="w-5 h-5" />, title: "Time-Limited Access", desc: "Set expiration dates on shared links. Automatic revocation after the deadline passes — no manual cleanup needed." },
  { icon: <Eye className="w-5 h-5" />, title: "Access Tracking", desc: "See who viewed which documents and when. Know exactly which investors have reviewed your materials." },
  { icon: <Upload className="w-5 h-5" />, title: "Bulk Upload", desc: "Drag and drop multiple files at once. Organize into folders by category — legal, financial, corporate, tax." },
  { icon: <Shield className="w-5 h-5" />, title: "Due Diligence Ready", desc: "Pre-organized folder structure for investor due diligence. Financial statements, corporate records, IP, and compliance documents." },
];

export default function DataRoomFeaturePage() {
  return (
    <div>
      <Header />

      <HeroSection
        badge="Product"
        title={<>Secure document sharing, <span className="gradient-text">no fuss</span></>}
        subtitle="Share company documents with investors, auditors, and legal counsel. Time-limited links, access tracking, and organized folders."
        primaryCTA={{ label: "Get Started", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Your documents, <span className="gradient-text">under control</span></>}
            subtitle="Share what you need, revoke when you want, track who's seen what."
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
        title="Stop emailing sensitive documents"
        subtitle="A proper data room for your next fundraise or audit."
        primaryCTA={{ label: "Get Started", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <Footer />
    </div>
  );
}
