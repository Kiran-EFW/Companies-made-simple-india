import { Metadata } from "next";
import Header from "@/components/header";
import Footer from "@/components/footer";
import HeroSection from "@/components/marketing/hero-section";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import { Calendar, FileText, Users, Clock, CheckSquare, Bell } from "lucide-react";

export const metadata: Metadata = {
  title: "Board Meetings — Anvils",
  description: "Schedule board meetings, generate notices, track attendance, draft minutes, and manage resolutions. Companies Act compliant.",
};

const FEATURES = [
  { icon: <Calendar className="w-5 h-5" />, title: "Meeting Scheduling", desc: "Schedule board meetings and AGMs with automatic notice period calculation per Companies Act requirements." },
  { icon: <FileText className="w-5 h-5" />, title: "Notice Generation", desc: "Auto-generate meeting notices with agenda items, venue details, and director circulation list." },
  { icon: <Users className="w-5 h-5" />, title: "Attendance Tracking", desc: "Record quorum and attendance for every meeting. Track which directors were present, absent, or on leave." },
  { icon: <CheckSquare className="w-5 h-5" />, title: "Minutes & Resolutions", desc: "Draft meeting minutes with resolution tracking. Maintain a searchable history of all board decisions." },
  { icon: <Clock className="w-5 h-5" />, title: "Companies Act Compliance", desc: "Automatic gap calculations between meetings. Alerts when you're approaching the maximum allowed interval." },
  { icon: <Bell className="w-5 h-5" />, title: "Deadline Reminders", desc: "Automated reminders for upcoming meetings, notice deadlines, and minutes filing requirements." },
];

export default function BoardMeetingsFeaturePage() {
  return (
    <div>
      <Header />

      <HeroSection
        badge="Product"
        title={<>Board meetings, <span className="gradient-text">handled</span></>}
        subtitle="From scheduling to minutes. Notices, quorum tracking, resolutions, and compliance — all in one place."
        primaryCTA={{ label: "Get Started", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Every meeting, <span className="gradient-text">properly documented</span></>}
            subtitle="Schedule, conduct, and record board meetings per Companies Act requirements."
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
        title="Never miss a board meeting deadline"
        subtitle="Let Anvils handle the scheduling and paperwork."
        primaryCTA={{ label: "Get Started", href: "/signup" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
      />

      <Footer />
    </div>
  );
}
