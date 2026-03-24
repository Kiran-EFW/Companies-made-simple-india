"use client";

import { useState } from "react";
import Header from "@/components/header";
import Footer from "@/components/footer";
import ChatWidget from "@/components/chat-widget";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import FAQAccordion from "@/components/marketing/faq-accordion";
import {
  FileCheck,
  Receipt,
  Calculator,
  BookOpen,
  Pencil,
  Scale,
  Clock,
  Check,
} from "lucide-react";

/* ── Data ── */

const CATEGORIES = [
  { id: "all", label: "All Services", icon: <Check className="w-4 h-4" /> },
  { id: "registration", label: "Registration", icon: <FileCheck className="w-4 h-4" /> },
  { id: "compliance", label: "Compliance", icon: <BookOpen className="w-4 h-4" /> },
  { id: "tax", label: "Tax", icon: <Receipt className="w-4 h-4" /> },
  { id: "accounting", label: "Accounting", icon: <Calculator className="w-4 h-4" /> },
  { id: "amendments", label: "Amendments", icon: <Pencil className="w-4 h-4" /> },
  { id: "legal", label: "Legal", icon: <Scale className="w-4 h-4" /> },
] as const;

type CategoryId = (typeof CATEGORIES)[number]["id"];

interface Service {
  name: string;
  price: string;
  description: string;
  timeline: string;
  category: Exclude<CategoryId, "all">;
}

const SERVICES: Service[] = [
  // Registration
  { name: "GST Registration", price: "Rs 499", description: "New GST registration for your business with GSTIN issuance", timeline: "5-7 days", category: "registration" },
  { name: "MSME / Udyam Registration", price: "Rs 499", description: "Udyam registration certificate for MSME benefits and government schemes", timeline: "1-2 days", category: "registration" },
  { name: "Trademark Registration", price: "Rs 3,499", description: "File trademark application with class selection and brand search", timeline: "1-2 days filing", category: "registration" },
  { name: "IEC (Import Export Code)", price: "Rs 1,999", description: "DGFT import-export code for international trade", timeline: "3-5 days", category: "registration" },
  { name: "FSSAI Registration", price: "Rs 2,499", description: "Food safety license for food-related businesses", timeline: "7-10 days", category: "registration" },
  { name: "DPIIT Startup Recognition", price: "Rs 2,999", description: "DPIIT startup recognition for tax benefits and compliance exemptions", timeline: "5-7 days", category: "registration" },
  { name: "Professional Tax Registration", price: "Rs 999", description: "State professional tax registration for employers", timeline: "3-5 days", category: "registration" },
  { name: "ESI Registration", price: "Rs 1,499", description: "ESIC registration for employee health insurance benefits", timeline: "5-7 days", category: "registration" },
  { name: "EPFO Registration", price: "Rs 1,499", description: "PF registration for employee provident fund", timeline: "5-7 days", category: "registration" },
  { name: "ISO Certification", price: "Rs 4,999", description: "ISO 9001/27001 certification support and documentation", timeline: "15-30 days", category: "registration" },

  // Compliance
  { name: "Annual ROC Filing (Pvt Ltd)", price: "Rs 7,999", description: "AOC-4 and MGT-7A annual return filing with ROC", timeline: "7-10 days", category: "compliance" },
  { name: "LLP Annual Filing", price: "Rs 4,999", description: "Form 8 and Form 11 annual filing for LLPs", timeline: "5-7 days", category: "compliance" },
  { name: "DIR-3 KYC (per director)", price: "Rs 499", description: "Annual KYC filing for each company director", timeline: "1-2 days", category: "compliance" },
  { name: "ADT-1 (Auditor Appointment)", price: "Rs 1,999", description: "Filing of auditor appointment form with ROC", timeline: "3-5 days", category: "compliance" },
  { name: "INC-20A (Business Commencement)", price: "Rs 2,999", description: "Declaration of business commencement within 180 days", timeline: "3-5 days", category: "compliance" },
  { name: "DPT-3 (Deposit Returns)", price: "Rs 3,999", description: "Annual return of deposits and outstanding loans", timeline: "5-7 days", category: "compliance" },
  { name: "MSME-1 (Delayed Payments)", price: "Rs 1,999", description: "Half-yearly return for outstanding MSME payments", timeline: "3-5 days", category: "compliance" },

  // Tax
  { name: "ITR Filing (Individual)", price: "Rs 999", description: "Income tax return filing for individuals (ITR-1/2/3)", timeline: "3-5 days", category: "tax" },
  { name: "ITR Filing (Company — ITR-6)", price: "Rs 4,999", description: "Corporate income tax return with computation and audit report", timeline: "7-10 days", category: "tax" },
  { name: "ITR Filing (LLP — ITR-5)", price: "Rs 2,999", description: "LLP income tax return with profit computation", timeline: "5-7 days", category: "tax" },
  { name: "GST Monthly Filing (GSTR-1 + 3B)", price: "Rs 799/mo", description: "Monthly GST return filing with input tax credit reconciliation", timeline: "Monthly", category: "tax" },
  { name: "GST Annual Return (GSTR-9)", price: "Rs 4,999", description: "Annual GST return filing with reconciliation", timeline: "7-10 days", category: "tax" },
  { name: "TDS Quarterly Filing", price: "Rs 2,499", description: "TDS return filing (24Q, 26Q) with challan verification", timeline: "Quarterly", category: "tax" },
  { name: "Tax Planning & Advisory", price: "Rs 4,999", description: "Comprehensive tax planning session with CA for optimized structure", timeline: "3-5 days", category: "tax" },

  // Accounting
  { name: "Monthly Bookkeeping", price: "Rs 2,999/mo", description: "Complete monthly bookkeeping with P&L, balance sheet, and cash flow", timeline: "Monthly", category: "accounting" },
  { name: "Payroll Processing", price: "Rs 1,999/mo", description: "Monthly payroll computation, payslips, and statutory deductions", timeline: "Monthly", category: "accounting" },
  { name: "Statutory Audit", price: "Rs 14,999", description: "Annual statutory audit by a practicing Chartered Accountant", timeline: "15-20 days", category: "accounting" },
  { name: "Internal Audit", price: "Rs 9,999", description: "Internal audit for process improvement and compliance validation", timeline: "10-15 days", category: "accounting" },

  // Amendments
  { name: "Director Addition/Removal", price: "Rs 4,999", description: "Add or remove a director with all ROC filings (DIR-12, MGT-14)", timeline: "7-10 days", category: "amendments" },
  { name: "Share Transfer", price: "Rs 7,999", description: "Transfer shares between shareholders with SH-4 and stamp duty", timeline: "7-10 days", category: "amendments" },
  { name: "Share Allotment", price: "Rs 8,999", description: "Fresh share allotment with PAS-3 filing and updated cap table", timeline: "10-15 days", category: "amendments" },
  { name: "Increase Authorized Capital", price: "Rs 5,999", description: "Increase authorized share capital with SH-7 filing", timeline: "7-10 days", category: "amendments" },
  { name: "Registered Office Change", price: "Rs 3,999", description: "Change registered office address (within state/between states)", timeline: "7-15 days", category: "amendments" },
  { name: "Company Name Change", price: "Rs 5,999", description: "Change company name with RUN approval and INC-24 filing", timeline: "10-15 days", category: "amendments" },
  { name: "Company Closure / Strike Off", price: "Rs 7,999", description: "Voluntary company closure with STK-2 filing and compliance", timeline: "30-45 days", category: "amendments" },

  // Legal
  { name: "Trademark Objection Reply", price: "Rs 3,999", description: "Draft and file reply to trademark examination report objection", timeline: "5-7 days", category: "legal" },
  { name: "Legal Notice Drafting", price: "Rs 2,999", description: "Draft and send legal notice for various business disputes", timeline: "3-5 days", category: "legal" },
  { name: "Virtual Office Address", price: "Rs 4,999/yr", description: "Registered office address with mail handling and GST eligibility", timeline: "1-2 days", category: "legal" },
  { name: "NDA / Contract Drafting", price: "Rs 1,999", description: "Custom NDA or business contract drafting by legal team", timeline: "3-5 days", category: "legal" },
];

const FAQ_ITEMS = [
  {
    question: "Who fulfills these services?",
    answer: "All services are fulfilled by verified, practicing Chartered Accountants and Company Secretaries on our platform. Each professional is vetted for qualifications, experience, and client satisfaction.",
  },
  {
    question: "How do I track my service order?",
    answer: "Once you order a service, you can track its status from your Anvils dashboard. You'll receive updates at every stage — from assignment to a professional, through document preparation, to final filing and completion.",
  },
  {
    question: "Can I get a bulk discount?",
    answer: "Yes. If you need multiple services (e.g., annual compliance bundle with ROC + ITR + DIR-3 KYC + GST), contact our team for customized package pricing.",
  },
  {
    question: "What if I already have a CA?",
    answer: "You can continue working with your existing CA. Our platform is designed to complement, not replace, your CA relationship. The marketplace is an option for founders who want transparent pricing and tracked fulfillment.",
  },
];

/* ── Page ── */

export default function ServicesPage() {
  const [activeCategory, setActiveCategory] = useState<CategoryId>("all");

  const filteredServices =
    activeCategory === "all"
      ? SERVICES
      : SERVICES.filter((s) => s.category === activeCategory);

  return (
    <div className="glow-bg">
      <Header />

      {/* ── Hero ── */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-12 text-center">
        <div className="animate-fade-in-up max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-purple-50 border border-purple-100 text-purple-700 text-xs font-semibold uppercase tracking-wider mb-6">
            Services Marketplace
          </div>
          <h1
            className="text-4xl md:text-5xl font-extrabold leading-tight mb-4 text-[var(--color-text-primary)]"
            style={{ fontFamily: "var(--font-display)" }}
          >
            50+ professional services at{" "}
            <span className="gradient-text">transparent prices</span>
          </h1>
          <p className="text-lg text-[var(--color-text-secondary)] leading-relaxed">
            Registration, compliance, tax, accounting, amendments, and legal
            services — fulfilled by verified CAs at fixed, upfront prices.
          </p>
        </div>
      </section>

      {/* ── Category Tabs ── */}
      <section className="pb-8 sticky top-0 z-20 bg-[var(--color-bg-primary)]/95 backdrop-blur-sm border-b border-[var(--color-border)]">
        <div className="max-w-7xl mx-auto px-6 pt-4">
          <div className="flex flex-wrap gap-2 justify-center">
            {CATEGORIES.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                className={`inline-flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  activeCategory === cat.id
                    ? "bg-purple-600 text-white"
                    : "bg-[var(--color-bg-secondary)] text-[var(--color-text-secondary)] hover:bg-purple-50 hover:text-purple-600 border border-[var(--color-border)]"
                }`}
              >
                {cat.icon}
                {cat.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* ── Service Cards ── */}
      <section className="py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="mb-4 text-sm text-[var(--color-text-muted)]">
            Showing {filteredServices.length} services
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredServices.map((service) => (
              <div
                key={service.name}
                className="card-static p-5 flex flex-col hover:border-purple-200 transition-colors"
              >
                <div className="flex items-start justify-between gap-3 mb-3">
                  <h3 className="text-sm font-bold text-[var(--color-text-primary)] leading-tight">
                    {service.name}
                  </h3>
                  <span className="text-sm font-extrabold text-purple-600 whitespace-nowrap">
                    {service.price}
                  </span>
                </div>
                <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed flex-1 mb-3">
                  {service.description}
                </p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1 text-xs text-[var(--color-text-muted)]">
                    <Clock className="w-3 h-3" />
                    {service.timeline}
                  </div>
                  <button className="btn-sm btn-secondary !py-1.5 !px-3 text-xs">
                    Order
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section className="py-16 bg-[var(--color-bg-secondary)]">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>How the marketplace <span className="gradient-text">works</span></>}
            subtitle="Three steps from order to completion."
          />
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {[
              { step: "01", title: "Choose a service", desc: "Browse our catalog, select the service you need, and place your order at a fixed, transparent price." },
              { step: "02", title: "We assign a professional", desc: "A verified CA or CS is assigned to your order within 24 hours. You can track progress from your dashboard." },
              { step: "03", title: "Work gets done", desc: "The professional completes the work, files the necessary forms, and you get notified at every stage." },
            ].map((s) => (
              <div key={s.step} className="card-static p-8 text-center">
                <div className="w-12 h-12 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center mx-auto mb-4 text-sm font-bold">
                  {s.step}
                </div>
                <h3
                  className="text-lg font-bold text-[var(--color-text-primary)] mb-2"
                  style={{ fontFamily: "var(--font-display)" }}
                >
                  {s.title}
                </h3>
                <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                  {s.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FAQ ── */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={<>Marketplace <span className="gradient-text">FAQ</span></>}
          />
          <div className="max-w-3xl mx-auto">
            <FAQAccordion items={FAQ_ITEMS} />
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <CTASection
        title="Need a service not listed here?"
        subtitle="Contact our team for custom quotes on specialized services."
        primaryCTA={{ label: "Contact Us", href: "/contact" }}
        secondaryCTA={{ label: "See Pricing", href: "/pricing" }}
        variant="white"
      />

      <Footer />
      <ChatWidget />
    </div>
  );
}
