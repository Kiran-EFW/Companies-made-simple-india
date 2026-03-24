import { Metadata } from "next";
import Link from "next/link";
import Header from "@/components/header";
import Footer from "@/components/footer";
import ChatWidget from "@/components/chat-widget";
import HeroSection from "@/components/marketing/hero-section";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import FAQAccordion from "@/components/marketing/faq-accordion";
import {
  LayoutDashboard,
  Calculator,
  FileText,
  CalendarCheck,
  BarChart3,
  Check,
  ArrowRight,
  FolderOpen,
  ShieldCheck,
  ClipboardList,
  AlertTriangle,
  CheckCircle2,
  MessageSquare,
  BookOpen,
  IndianRupee,
  Package,
  Star,
  Receipt,
} from "lucide-react";

export const metadata: Metadata = {
  title: "Anvils for CAs & Professionals — Multi-Client Compliance Dashboard",
  description:
    "Manage compliance, tax filings, and audit packs across all your client companies from a single dashboard. Built for practicing CAs and CS professionals.",
};

/* ── What the CA portal actually does ── */

const PORTAL_FEATURES = [
  {
    icon: <LayoutDashboard className="w-6 h-6" />,
    title: "Multi-Client Dashboard",
    description:
      "See all your assigned companies in one view. Each company shows its compliance grade, pending tasks, overdue filings, and penalty exposure — no more jumping between spreadsheets.",
    highlights: [
      "Compliance health grade (A+ to F) per company",
      "Pending, overdue, and upcoming task counts",
      "Penalty exposure calculated automatically",
      "One-click navigation to any company's details",
    ],
    color: "emerald" as const,
  },
  {
    icon: <ClipboardList className="w-6 h-6" />,
    title: "Filing & Task Management",
    description:
      "View all compliance tasks across your clients, filtered by status. Mark filings as complete with reference numbers — the founder gets notified automatically.",
    highlights: [
      "Filter tasks by overdue, due soon, upcoming, or completed",
      "Mark filings complete with filing reference number",
      "Automatic notification to company founders",
      "Due date tracking with days-until-due calculation",
    ],
    color: "blue" as const,
  },
  {
    icon: <Calculator className="w-6 h-6" />,
    title: "TDS Calculator",
    description:
      "Calculate TDS across 189 sections with accurate rates based on payee type and PAN status. Includes surcharge, cess, and quarterly due date reference.",
    highlights: [
      "189 TDS sections with current rates",
      "Payee type selection (Individual, Company, HUF)",
      "Higher rate calculation for no-PAN cases",
      "Quarterly due date reference with FY awareness",
    ],
    color: "purple" as const,
  },
  {
    icon: <BarChart3 className="w-6 h-6" />,
    title: "Tax Filing Tracker",
    description:
      "View ITR, TDS quarterly returns, advance tax installments, and GST filing status across all your clients. See what's been filed and what's pending at a glance.",
    highlights: [
      "ITR filing status by assessment year",
      "TDS quarterly return tracking (Q1-Q4)",
      "GST return status (GSTR-1, GSTR-3B, GSTR-9)",
      "Advance tax installment schedule",
    ],
    color: "emerald" as const,
  },
  {
    icon: <FolderOpen className="w-6 h-6" />,
    title: "Documents & Audit Packs",
    description:
      "Access all uploaded documents for each client company. Generate audit pack checklists and add notes to individual compliance tasks for your own records.",
    highlights: [
      "View all client-uploaded documents by category",
      "Audit pack generation with compliance checklists",
      "Task-level notes for your filing records",
      "Company-scoped document access",
    ],
    color: "blue" as const,
  },
  {
    icon: <CalendarCheck className="w-6 h-6" />,
    title: "Compliance Calendar",
    description:
      "Visual calendar view of all compliance deadlines across your client portfolio, grouped by month and financial year. Spot overdue and upcoming tasks quickly.",
    highlights: [
      "Financial year (Apr-Mar) based calendar view",
      "Monthly grouping with task counts",
      "Color-coded status indicators",
      "Cross-company deadline visibility",
    ],
    color: "purple" as const,
  },
];

const COLOR_MAP = {
  purple: { iconBg: "bg-purple-50", iconText: "text-purple-600", bullet: "text-purple-500" },
  blue: { iconBg: "bg-blue-50", iconText: "text-blue-600", bullet: "text-blue-500" },
  emerald: { iconBg: "bg-emerald-50", iconText: "text-emerald-600", bullet: "text-emerald-500" },
};

/* ── What compliance tasks are auto-tracked ── */

const COMPLIANCE_TYPES = [
  { name: "Annual ROC Filing", forms: "AOC-4, MGT-7A", entity: "Pvt Ltd" },
  { name: "LLP Annual Filing", forms: "Form 8, Form 11", entity: "LLP" },
  { name: "DIR-3 KYC", forms: "Per director, annual", entity: "All companies" },
  { name: "ADT-1", forms: "Auditor appointment", entity: "Pvt Ltd" },
  { name: "INC-20A", forms: "Business commencement", entity: "Pvt Ltd" },
  { name: "DPT-3", forms: "Deposit returns", entity: "Pvt Ltd" },
  { name: "MSME-1", forms: "Delayed payments", entity: "Pvt Ltd" },
  { name: "GST Returns", forms: "GSTR-1, GSTR-3B, GSTR-9", entity: "GST registered" },
  { name: "TDS Returns", forms: "24Q, 26Q quarterly", entity: "TDS applicable" },
  { name: "Income Tax Return", forms: "ITR-5, ITR-6", entity: "All companies" },
  { name: "Advance Tax", forms: "4 quarterly installments", entity: "All companies" },
  { name: "Board Meetings", forms: "Minutes & resolutions", entity: "Pvt Ltd" },
];

/* ── FAQ ── */

const FAQ_ITEMS = [
  {
    question: "How do companies get assigned to my CA dashboard?",
    answer:
      "Companies are assigned to CAs through the Anvils admin panel. When a company on Anvils designates you as their CA, you'll see them appear in your dashboard with their full compliance calendar, documents, and filing status.",
  },
  {
    question: "What compliance tasks does Anvils auto-generate?",
    answer:
      "Anvils generates 50+ compliance tasks per company based on entity type, incorporation date, financial year, and applicability (GST, TDS, etc.). This includes ROC filings (AOC-4, MGT-7A, DIR-3 KYC, ADT-1), tax returns (ITR, GST, TDS quarterly), board meetings, and statutory deadlines. Tasks include reminders at 30, 15, 7, 3, and 1 day before each deadline.",
  },
  {
    question: "Can I mark filings as complete from the dashboard?",
    answer:
      "Yes. From the Tasks page or any Company Detail page, you can mark a filing as complete and enter the filing reference number. The company's founder is automatically notified when you complete a filing. The compliance score updates in real-time.",
  },
  {
    question: "How is the compliance score calculated?",
    answer:
      "Each company gets a compliance grade from A+ to F based on the ratio of on-time filings to total filings, overdue tasks, and penalty exposure. The scoring system weighs recent filings more heavily and accounts for the severity of different compliance requirements.",
  },
  {
    question: "Can my existing clients use Anvils?",
    answer:
      "Yes. Your clients can create their company on Anvils and invite you as their CA by email. You'll automatically get access to their company in your multi-client dashboard. They get their own founder dashboard with compliance tracking, cap table, and document management.",
  },
  {
    question: "How does the services marketplace work?",
    answer:
      "When a company orders a service from our marketplace (GST filing, ROC filing, trademark, etc.), it gets assigned to a registered partner CA. You accept the assignment, complete the work, upload deliverables, and get paid after admin review. You receive 80% of the service fee, with settlements tracked including TDS deduction under Section 194J.",
  },
  {
    question: "How do I register as a marketplace partner?",
    answer:
      "Create an account with the CA/Professional role and register your partner profile with your ICAI/ICSI membership number, membership type (CA, CS, or CMA), firm name, and specializations. Once verified, you can start receiving service assignments based on your specializations and capacity.",
  },
];

/* ── Marketplace earnings (based on actual service prices and 80/20 split) ── */

const MARKETPLACE_SERVICES = [
  { service: "GST Monthly Filing", clientPays: 799, youEarn: 639, frequency: "/mo per client" },
  { service: "Annual ROC Filing (Pvt Ltd)", clientPays: 7999, youEarn: 6399, frequency: "per filing" },
  { service: "ITR Filing (Company)", clientPays: 4999, youEarn: 3999, frequency: "per filing" },
  { service: "Statutory Audit", clientPays: 14999, youEarn: 11999, frequency: "per audit" },
  { service: "TDS Quarterly Filing", clientPays: 2499, youEarn: 1999, frequency: "per quarter" },
  { service: "Share Allotment (PAS-3)", clientPays: 8999, youEarn: 7199, frequency: "per transaction" },
];

/* ── Page ── */

export default function ForCAsPage() {
  return (
    <div className="glow-bg">
      <Header />

      {/* ── Hero ── */}
      <HeroSection
        badge="For CAs & Professionals"
        title={
          <>
            One dashboard for{" "}
            <span className="gradient-text">all your clients</span>
          </>
        }
        subtitle="Track compliance deadlines, mark filings complete, calculate TDS, and monitor penalty exposure across every company you manage — from a single portal."
        primaryCTA={{ label: "Get Started", href: "/signup?role=ca" }}
        secondaryCTA={{ label: "See Features", href: "#features" }}
      />

      {/* ── What you actually get ── */}
      <section className="py-16 bg-[var(--color-bg-secondary)]">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={
              <>
                What the CA portal{" "}
                <span className="gradient-text">actually does</span>
              </>
            }
            subtitle="Real tools for managing multi-client compliance. No fluff."
          />
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {PORTAL_FEATURES.map((feature) => {
              const colors = COLOR_MAP[feature.color];
              return (
                <div key={feature.title} className="card-static p-6">
                  <div
                    className={`w-10 h-10 rounded-xl ${colors.iconBg} flex items-center justify-center mb-4`}
                  >
                    <div className={colors.iconText}>{feature.icon}</div>
                  </div>
                  <h3
                    className="text-base font-bold text-[var(--color-text-primary)] mb-2"
                    style={{ fontFamily: "var(--font-display)" }}
                  >
                    {feature.title}
                  </h3>
                  <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed mb-4">
                    {feature.description}
                  </p>
                  <ul className="space-y-2">
                    {feature.highlights.map((h) => (
                      <li
                        key={h}
                        className="flex items-start gap-2 text-xs text-[var(--color-text-secondary)]"
                      >
                        <Check className={`w-3.5 h-3.5 shrink-0 mt-0.5 ${colors.bullet}`} />
                        {h}
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── How it works (honest version) ── */}
      <section id="features" className="py-16 scroll-mt-24">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={
              <>
                How it <span className="gradient-text">works</span>
              </>
            }
            subtitle="Your workflow on Anvils."
          />
          <div className="grid md:grid-cols-4 gap-6 max-w-5xl mx-auto">
            {[
              {
                step: "01",
                title: "Client joins Anvils",
                desc: "Your client creates their company on Anvils and designates you as their CA.",
              },
              {
                step: "02",
                title: "Tasks auto-generate",
                desc: "50+ compliance tasks are created based on entity type, state, and financial year.",
              },
              {
                step: "03",
                title: "You track & file",
                desc: "View deadlines, prepare filings, and mark tasks complete with reference numbers.",
              },
              {
                step: "04",
                title: "Founders stay informed",
                desc: "Founders see real-time compliance scores and get notified when filings are done.",
              },
            ].map((step, i) => (
              <div key={step.step} className="card-static p-6 text-center relative">
                <div className="w-10 h-10 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center mx-auto mb-3 text-sm font-bold">
                  {step.step}
                </div>
                <h3
                  className="text-sm font-bold text-[var(--color-text-primary)] mb-2"
                  style={{ fontFamily: "var(--font-display)" }}
                >
                  {step.title}
                </h3>
                <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">
                  {step.desc}
                </p>
                {i < 3 && (
                  <ArrowRight className="hidden md:block absolute -right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-text-muted)]" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Compliance tasks tracked ── */}
      <section className="py-16 bg-[var(--color-bg-secondary)]">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={
              <>
                50+ compliance tasks{" "}
                <span className="gradient-text">auto-tracked</span>
              </>
            }
            subtitle="Generated automatically based on entity type and applicability."
          />
          <div className="max-w-4xl mx-auto">
            <div className="card-static overflow-hidden">
              <div className="grid grid-cols-3 gap-0 text-xs font-semibold uppercase tracking-wider px-5 py-3 border-b"
                style={{ color: "var(--color-text-muted)", borderColor: "var(--color-border)" }}>
                <div>Task</div>
                <div>Forms / Details</div>
                <div>Applies To</div>
              </div>
              {COMPLIANCE_TYPES.map((ct, i) => (
                <div
                  key={ct.name}
                  className="grid grid-cols-3 gap-0 px-5 py-3 text-sm border-b last:border-b-0"
                  style={{ borderColor: "var(--color-border)" }}
                >
                  <div className="font-medium text-[var(--color-text-primary)]">{ct.name}</div>
                  <div className="text-[var(--color-text-secondary)]">{ct.forms}</div>
                  <div className="text-[var(--color-text-muted)]">{ct.entity}</div>
                </div>
              ))}
            </div>
            <p className="text-center text-xs text-[var(--color-text-muted)] mt-4">
              Plus board meetings, statutory registers, annual general meetings, and more based on entity configuration.
            </p>
          </div>
        </div>
      </section>

      {/* ── Key workflows ── */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={
              <>
                Built for your{" "}
                <span className="gradient-text">daily workflow</span>
              </>
            }
          />
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Workflow 1: Filing completion */}
            <div className="card-static p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                </div>
                <h3
                  className="text-base font-bold text-[var(--color-text-primary)]"
                  style={{ fontFamily: "var(--font-display)" }}
                >
                  Mark filings complete
                </h3>
              </div>
              <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed mb-4">
                Select any compliance task, enter the filing reference number, and mark it done. The company&apos;s compliance score updates instantly and the founder receives a notification.
              </p>
              <div className="flex items-center gap-2 text-xs text-emerald-600 font-medium">
                <Check className="w-3.5 h-3.5" />
                Filing updates persist and are auditable
              </div>
            </div>

            {/* Workflow 2: Penalty tracking */}
            <div className="card-static p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center">
                  <AlertTriangle className="w-5 h-5 text-amber-600" />
                </div>
                <h3
                  className="text-base font-bold text-[var(--color-text-primary)]"
                  style={{ fontFamily: "var(--font-display)" }}
                >
                  Penalty exposure tracking
                </h3>
              </div>
              <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed mb-4">
                Each company shows estimated penalty exposure for overdue filings. See which clients need immediate attention and prioritize your work based on financial risk.
              </p>
              <div className="flex items-center gap-2 text-xs text-amber-600 font-medium">
                <AlertTriangle className="w-3.5 h-3.5" />
                Calculated automatically from overdue tasks
              </div>
            </div>

            {/* Workflow 3: TDS calculation */}
            <div className="card-static p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
                  <Calculator className="w-5 h-5 text-blue-600" />
                </div>
                <h3
                  className="text-base font-bold text-[var(--color-text-primary)]"
                  style={{ fontFamily: "var(--font-display)" }}
                >
                  TDS calculation
                </h3>
              </div>
              <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed mb-4">
                Select from 189 TDS sections, enter the amount, choose payee type and PAN status. Get the exact TDS amount with surcharge, cess, and quarterly due dates.
              </p>
              <div className="flex items-center gap-2 text-xs text-blue-600 font-medium">
                <Check className="w-3.5 h-3.5" />
                Rates updated for current financial year
              </div>
            </div>

            {/* Workflow 4: Task notes */}
            <div className="card-static p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center">
                  <MessageSquare className="w-5 h-5 text-purple-600" />
                </div>
                <h3
                  className="text-base font-bold text-[var(--color-text-primary)]"
                  style={{ fontFamily: "var(--font-display)" }}
                >
                  Task notes & audit trail
                </h3>
              </div>
              <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed mb-4">
                Add notes to any compliance task for your own records. Track what was filed, when, and any issues encountered. Notes persist and create a full audit trail per company.
              </p>
              <div className="flex items-center gap-2 text-xs text-purple-600 font-medium">
                <BookOpen className="w-3.5 h-3.5" />
                Company-scoped, task-level notes
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Marketplace ── */}
      <section className="py-16 bg-[var(--color-bg-secondary)]">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={
              <>
                Earn from the{" "}
                <span className="gradient-text">services marketplace</span>
              </>
            }
            subtitle="Companies order services at fixed prices. You fulfill the work and earn 80% of the service fee."
          />

          {/* How marketplace works */}
          <div className="max-w-4xl mx-auto mb-12">
            <div className="card-static p-6 md:p-8">
              <h3
                className="text-base font-bold text-[var(--color-text-primary)] mb-4"
                style={{ fontFamily: "var(--font-display)" }}
              >
                How it works
              </h3>
              <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { icon: <Package className="w-4 h-4" />, step: "Company orders a service", detail: "GST filing, ROC filing, trademark, etc." },
                  { icon: <ClipboardList className="w-4 h-4" />, step: "You get assigned", detail: "Based on your specializations and capacity" },
                  { icon: <CheckCircle2 className="w-4 h-4" />, step: "You deliver the work", detail: "Complete the filing, upload deliverables" },
                  { icon: <IndianRupee className="w-4 h-4" />, step: "You get paid", detail: "80% of service fee, TDS deducted at 10%" },
                ].map((item, i) => (
                  <div key={i} className="text-center">
                    <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto mb-2">
                      {item.icon}
                    </div>
                    <div className="text-xs font-semibold text-[var(--color-text-primary)] mb-1">{item.step}</div>
                    <div className="text-xs text-[var(--color-text-muted)]">{item.detail}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Earnings table */}
          <div className="max-w-4xl mx-auto mb-8">
            <div className="card-static overflow-hidden">
              <div className="grid grid-cols-4 gap-0 text-xs font-semibold uppercase tracking-wider px-5 py-3 border-b"
                style={{ color: "var(--color-text-muted)", borderColor: "var(--color-border)" }}>
                <div className="col-span-1">Service</div>
                <div className="text-right">Client Pays</div>
                <div className="text-right">You Earn (80%)</div>
                <div className="text-right">Frequency</div>
              </div>
              {MARKETPLACE_SERVICES.map((s) => (
                <div
                  key={s.service}
                  className="grid grid-cols-4 gap-0 px-5 py-3 text-sm border-b last:border-b-0"
                  style={{ borderColor: "var(--color-border)" }}
                >
                  <div className="col-span-1 font-medium text-[var(--color-text-primary)]">{s.service}</div>
                  <div className="text-right text-[var(--color-text-secondary)]">Rs {s.clientPays.toLocaleString("en-IN")}</div>
                  <div className="text-right font-semibold text-emerald-600">Rs {s.youEarn.toLocaleString("en-IN")}</div>
                  <div className="text-right text-[var(--color-text-muted)]">{s.frequency}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Settlement details */}
          <div className="max-w-4xl mx-auto grid sm:grid-cols-3 gap-4 mb-10">
            <div className="card-static p-5 text-center">
              <div className="w-10 h-10 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto mb-3">
                <IndianRupee className="w-5 h-5" />
              </div>
              <div className="text-sm font-bold text-[var(--color-text-primary)] mb-1">80/20 split</div>
              <div className="text-xs text-[var(--color-text-secondary)]">
                You receive 80% of the service fee. Anvils retains 20% as platform margin.
              </div>
            </div>
            <div className="card-static p-5 text-center">
              <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-3">
                <Receipt className="w-5 h-5" />
              </div>
              <div className="text-sm font-bold text-[var(--color-text-primary)] mb-1">TDS at 10%</div>
              <div className="text-xs text-[var(--color-text-secondary)]">
                TDS deducted under Section 194J (professional fees). You receive net amount after TDS.
              </div>
            </div>
            <div className="card-static p-5 text-center">
              <div className="w-10 h-10 rounded-full bg-purple-50 text-purple-600 flex items-center justify-center mx-auto mb-3">
                <Star className="w-5 h-5" />
              </div>
              <div className="text-sm font-bold text-[var(--color-text-primary)] mb-1">Rating system</div>
              <div className="text-xs text-[var(--color-text-secondary)]">
                Clients rate completed work (1-5 stars). Higher ratings improve assignment priority.
              </div>
            </div>
          </div>

          {/* Register as partner CTA */}
          <div className="max-w-4xl mx-auto">
            <div className="card-static p-6 md:p-8 text-center border-emerald-200">
              <h3
                className="text-lg font-bold text-[var(--color-text-primary)] mb-2"
                style={{ fontFamily: "var(--font-display)" }}
              >
                Ready to start earning?
              </h3>
              <p className="text-sm text-[var(--color-text-secondary)] mb-5 max-w-lg mx-auto">
                Register as a marketplace partner with your ICAI, ICSI, or ICMAI membership. Once verified, you can start accepting assignments.
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Link
                  href="/signup?role=ca"
                  className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg bg-emerald-600 text-white text-sm font-semibold hover:bg-emerald-700 transition-colors"
                >
                  Sign Up as CA
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <Link
                  href="/ca/register-partner"
                  className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg border text-sm font-semibold transition-colors"
                  style={{ borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                >
                  Already have an account? Register as Partner
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── FAQ ── */}
      <section className="py-16">
        <div className="max-w-3xl mx-auto px-6">
          <SectionHeader
            title={
              <>
                Common <span className="gradient-text">questions</span>
              </>
            }
          />
          <FAQAccordion items={FAQ_ITEMS} />
        </div>
      </section>

      {/* ── CTA ── */}
      <CTASection
        variant="purple"
        title="Manage your clients on Anvils"
        subtitle="One dashboard. Every deadline. Every company."
        primaryCTA={{ label: "Get Started", href: "/signup?role=ca" }}
        secondaryCTA={{ label: "Log in to Partner Portal", href: "/login?portal=ca" }}
      />

      <Footer />
      <ChatWidget />
    </div>
  );
}
