import { Metadata } from "next";
import Header from "@/components/header";
import Footer from "@/components/footer";
import HeroSection from "@/components/marketing/hero-section";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import { Users, ClipboardList, Calendar, ArrowRightLeft, Calculator, FileText } from "lucide-react";

export const metadata: Metadata = {
  title: "ESOP Management — Anvils",
  description: "Create stock option plans, manage grants, automate vesting schedules, and handle exercise workflows with FMV compliance.",
};

const FEATURES = [
  { icon: <ClipboardList className="w-5 h-5" />, title: "Plan Creation", desc: "Create ESOP, SAR, or RSU plans with board resolution tracking. Define pool size, vesting terms, and eligibility criteria." },
  { icon: <Users className="w-5 h-5" />, title: "Grant Management", desc: "Issue option grants to employees with cliff periods, vesting frequency, and grant prices. Track every grant lifecycle." },
  { icon: <Calendar className="w-5 h-5" />, title: "Vesting Automation", desc: "Automatic monthly, quarterly, or annual vesting calculations. See vested, unvested, and exercisable options at a glance." },
  { icon: <ArrowRightLeft className="w-5 h-5" />, title: "Exercise Workflow", desc: "Handle option exercises with automatic share allotment to the cap table. Track exercise history and documentation." },
  { icon: <Calculator className="w-5 h-5" />, title: "FMV Compliance", desc: "Link exercise pricing to Rule 11UA fair market valuations. Ensure FEMA and income tax compliance." },
  { icon: <FileText className="w-5 h-5" />, title: "Grant Letters", desc: "Auto-generate ESOP grant letters and send them for e-signature directly from the platform." },
];

export default function ESOPFeaturePage() {
  return (
    <div>
      <Header />

      <HeroSection
        badge="Product"
        title={<>ESOP management, <span className="gradient-text">from plan to exercise</span></>}
        subtitle="Design stock option plans, manage grants, automate vesting, and handle exercises. Everything you need to use equity as a talent retention tool."
        primaryCTA={{ label: "Start Managing ESOPs", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>The complete <span className="gradient-text">ESOP lifecycle</span></>}
            subtitle="From plan creation to option exercise, managed in one place."
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
        title="Attract and retain top talent with equity"
        subtitle="Set up your ESOP plan and start issuing grants today."
        primaryCTA={{ label: "Get Started", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <Footer />
    </div>
  );
}
