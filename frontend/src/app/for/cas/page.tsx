import { Metadata } from "next";
import Link from "next/link";
import Header from "@/components/header";
import Footer from "@/components/footer";
import HeroSection from "@/components/marketing/hero-section";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import {
  Briefcase,
  Shield,
  FileText,
  ClipboardCheck,
  Users,
  LayoutDashboard,
  Mail,
  CheckCircle2,
} from "lucide-react";

export const metadata: Metadata = {
  title: "Anvils for CAs & CSs — Multi-Client Compliance Dashboard",
  description: "Manage compliance tasks, filings, and documents for all your client companies in one dashboard. Get invited by founders, no setup needed.",
};

const FEATURES = [
  { icon: <LayoutDashboard className="w-5 h-5" />, title: "Multi-Client Dashboard", desc: "See all assigned companies at a glance with pending task counts and overdue alerts." },
  { icon: <Shield className="w-5 h-5" />, title: "Compliance Task Management", desc: "View compliance calendars for each client. Track ROC filings, board meetings, and GST deadlines." },
  { icon: <ClipboardCheck className="w-5 h-5" />, title: "Filing Tracker", desc: "Mark filings as completed and record reference numbers. Maintain a clear audit trail." },
  { icon: <FileText className="w-5 h-5" />, title: "Document Access", desc: "Read-only access to company documents. View incorporation papers, board minutes, and financial records." },
];

const HOW_IT_WORKS = [
  { step: "01", title: "Founder Invites You", desc: "A founder adds your email as their CA or CS from their Anvils dashboard.", icon: <Mail className="w-5 h-5" /> },
  { step: "02", title: "You See All Clients", desc: "Log in to see every company that has invited you, with compliance status at a glance.", icon: <Users className="w-5 h-5" /> },
  { step: "03", title: "Track and Manage", desc: "View tasks, mark filings as done, add reference numbers, and access company documents.", icon: <CheckCircle2 className="w-5 h-5" /> },
];

export default function ForCAsPage() {
  return (
    <div>
      <Header />

      <HeroSection
        badge="For Chartered Accountants & Company Secretaries"
        title={<>Manage all your clients from <span className="gradient-text">one dashboard</span></>}
        subtitle="When founders invite you, get instant access to their compliance calendar, filings, and documents -- all in a unified view."
        primaryCTA={{ label: "Log In to Your Dashboard", href: "/login" }}
        secondaryCTA={{ label: "Learn How It Works", href: "#how-it-works" }}
      />

      {/* How It Works */}
      <section id="how-it-works" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Getting started is <span className="gradient-text">simple</span></>}
            subtitle="No setup needed on your end. Founders invite you directly."
          />
          <div className="grid md:grid-cols-3 gap-8">
            {HOW_IT_WORKS.map((step) => (
              <div key={step.step} className="card-static p-8 text-center">
                <div className="w-12 h-12 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto mb-4">
                  {step.icon}
                </div>
                <div className="text-xs font-bold text-emerald-600 mb-2">STEP {step.step}</div>
                <h3 className="text-xl font-bold text-gray-900 mb-3" style={{ fontFamily: "var(--font-display)" }}>
                  {step.title}
                </h3>
                <p className="text-sm text-gray-500 leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Showcase */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Everything you need to <span className="gradient-text">serve your clients</span></>}
            subtitle="Compliance management designed for professionals."
          />
          <div className="grid md:grid-cols-2 gap-6">
            {FEATURES.map((f) => (
              <div key={f.title} className="card-static p-6 flex gap-4">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-emerald-50 shrink-0">
                  <div className="text-emerald-600">{f.icon}</div>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900 mb-1">{f.title}</h3>
                  <p className="text-sm text-gray-500 leading-relaxed">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* For Founders callout */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-3xl mx-auto px-6 text-center">
          <Briefcase className="w-8 h-8 text-purple-600 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-900 mb-2" style={{ fontFamily: "var(--font-display)" }}>
            Are you a founder looking to invite your CA?
          </h3>
          <p className="text-sm text-gray-500 mb-6">
            You can invite your chartered accountant or company secretary from your
            Anvils dashboard. They&apos;ll get access to your compliance calendar,
            documents, and filing tracker.
          </p>
          <Link href="/for/founders" className="text-sm font-semibold text-purple-600 hover:underline">
            Learn more about Anvils for Founders &rarr;
          </Link>
        </div>
      </section>

      <CTASection
        title="Your clients are already on Anvils"
        subtitle="Log in to see your assigned companies and start managing their compliance."
        primaryCTA={{ label: "Log In", href: "/login" }}
        secondaryCTA={{ label: "Contact Support", href: "mailto:support@anvils.in" }}
      />

      <Footer />
    </div>
  );
}
