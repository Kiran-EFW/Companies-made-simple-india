"use client";

import { useState } from "react";
import Header from "@/components/header";
import Footer from "@/components/footer";
import ChatWidget from "@/components/chat-widget";
import SectionHeader from "@/components/marketing/section-header";
import FAQAccordion from "@/components/marketing/faq-accordion";
import CTASection from "@/components/marketing/cta-section";

const CATEGORIES = [
  "All",
  "General",
  "Incorporation",
  "Pricing",
  "Platform",
  "Security",
  "Investors",
  "CAs",
] as const;

type Category = (typeof CATEGORIES)[number];

interface FAQ {
  question: string;
  answer: string;
  category: Exclude<Category, "All">;
}

const FAQ_DATA: FAQ[] = [
  // General
  {
    question: "What is Anvils?",
    answer:
      "Anvils is an equity, governance, and compliance platform for Indian companies. It combines company incorporation, cap table management, ESOP administration, compliance tracking, fundraising tools, and legal documents into a single dashboard — purpose-built for Indian regulations (MCA, SEBI, Rule 11UA, state-wise stamp duty).",
    category: "General",
  },
  {
    question: "Who is Anvils for?",
    answer:
      "Anvils serves three audiences: Founders (incorporate and manage their company), Investors (view portfolio holdings via token-based access), and CAs/Professionals (manage multiple clients from one dashboard). The platform supports all 7 entity types recognized in India.",
    category: "General",
  },
  {
    question: "How is Anvils different from Vakilsearch or IndiaFilings?",
    answer:
      "Online incorporation platforms handle registration but leave you on your own for equity, compliance, and governance. Anvils is a full lifecycle platform — we start with incorporation and continue with cap table, ESOP, fundraising, compliance calendar, data room, and more. We're also 75-80% cheaper on incorporation (starting at Rs 999 vs Rs 6,499+).",
    category: "General",
  },
  {
    question: "How is Anvils different from Carta or Trica Equity?",
    answer:
      "Carta and Trica are equity management tools. Anvils starts earlier (with incorporation) and goes wider (compliance, legal docs, services marketplace). We're also built specifically for Indian regulations — MCA filings, SEBI rules, Rule 11UA valuations, and state-specific stamp duty. Pricing is 60-85% lower than Carta and 40-70% lower than Trica.",
    category: "General",
  },
  {
    question: "What entity types does Anvils support?",
    answer:
      "Anvils supports all 7 entity types: Private Limited Company, One Person Company (OPC), Limited Liability Partnership (LLP), Section 8 Company (non-profit), Partnership Firm, Sole Proprietorship, and Public Limited Company. Each entity type has tailored workflows, pricing, and compliance tracking.",
    category: "General",
  },
  // Incorporation
  {
    question: "How long does incorporation take?",
    answer:
      "Typically 7-15 business days depending on entity type and state. Private Limited and OPC take 7-10 days, LLPs take 10-12 days, and Section 8 Companies take 15-20 days due to additional approvals. We track progress through a 25-stage pipeline with real-time status updates.",
    category: "Incorporation",
  },
  {
    question: "What documents do I need for incorporation?",
    answer:
      "For a Private Limited Company: PAN and Aadhaar of all directors, address proof of registered office (utility bill + NOC from owner), passport-size photos, and Digital Signature Certificates (DSC). Our platform guides you through document collection with AI-powered verification and cross-validation.",
    category: "Incorporation",
  },
  {
    question: "How does the AI Entity Wizard work?",
    answer:
      "Our Entity Wizard asks you 5 questions about your business goals — whether you're solo or have co-founders, your funding plans, revenue expectations, and whether it's a non-profit. Based on your answers, it recommends the best entity type with a match score, pros/cons, and pricing comparison.",
    category: "Incorporation",
  },
  {
    question: "Can I incorporate in any Indian state?",
    answer:
      "Yes. We support incorporation in all 28 states and union territories. Our pricing calculator shows state-specific costs including stamp duty variations. Some states like Madhya Pradesh, Rajasthan, and Jharkhand have lower stamp duty, which our optimizer highlights.",
    category: "Incorporation",
  },
  // Pricing
  {
    question: "What's included in the free plan?",
    answer:
      "Every company gets a free dashboard with: compliance calendar with 50+ auto-generated tasks, deadline reminders at 30/15/7/3/1 days, basic document storage, and company overview. The free plan is designed to keep you compliant. Cap table, ESOP, fundraising, and data room features are available on Growth and Scale plans.",
    category: "Pricing",
  },
  {
    question: "Can I switch plans later?",
    answer:
      "Yes. You can upgrade or downgrade at any time. When upgrading, you get immediate access to new features. When downgrading, your current billing period is honored and premium features become read-only afterwards.",
    category: "Pricing",
  },
  {
    question: "Are government fees included in the incorporation price?",
    answer:
      "Government fees (MCA filing fees, stamp duty, DSC charges) are passed through at exact cost with zero markup. Our incorporation calculator shows the complete breakdown — you see exactly what goes to the government vs. what is our platform fee.",
    category: "Pricing",
  },
  {
    question: "Do you offer refunds?",
    answer:
      "If your incorporation application hasn't been submitted to MCA, we offer a full refund minus government fees already paid. For platform subscriptions, you can cancel anytime and your access continues until the end of the billing period.",
    category: "Pricing",
  },
  {
    question: "Is there a startup discount?",
    answer:
      "DPIIT-recognized startups get special pricing on select services. Contact our team for details. We also offer annual billing at 17% savings compared to monthly plans.",
    category: "Pricing",
  },
  {
    question: "What payment methods do you accept?",
    answer:
      "We accept all major payment methods via Razorpay — credit/debit cards, UPI, net banking, and wallets. For annual subscriptions and large services, we also support bank transfers.",
    category: "Pricing",
  },
  // Platform
  {
    question: "How does the compliance calendar work?",
    answer:
      "We auto-generate 50+ compliance tasks based on your entity type, state, incorporation date, financial year end, and GST/TDS applicability. You get reminders at 30, 15, 7, 3, and 1 day before each deadline. The system tracks your compliance health score and estimates penalty exposure for overdue tasks.",
    category: "Platform",
  },
  {
    question: "Can I migrate my existing cap table?",
    answer:
      "Yes. You can enter existing shareholders, share classes, and transaction history manually. For larger cap tables, contact our team for assisted migration. We support all share types, convertible instruments (SAFE, CCD, CCPS), and historical events.",
    category: "Platform",
  },
  {
    question: "How does the data room work?",
    answer:
      "Your data room has hierarchical folders with pre-built categories (Incorporation, Compliance, Financials, Agreements, Cap Table, Board Meetings, IP, HR, Tax). You can upload documents with version tracking, set retention policies, and share securely via token-based links with optional passwords, expiry dates, and download limits.",
    category: "Platform",
  },
  {
    question: "Do I still need a CA if I use Anvils?",
    answer:
      "Anvils automates tracking, reminders, and document management, but certain filings (annual ROC filing, ITR, statutory audit) legally require a practicing CA. You can use your own CA or hire one through our Services Marketplace where verified CAs fulfill work at transparent prices.",
    category: "Platform",
  },
  {
    question: "How does e-signature work?",
    answer:
      "You can send documents for multi-party e-signature — parallel or sequential signing. Signers can draw, type, or upload their signature. Optional OTP verification adds an extra layer of security. Every signing event is logged with IP address, timestamp, and user agent for a complete audit trail.",
    category: "Platform",
  },
  // Security
  {
    question: "Is my data secure?",
    answer:
      "Your data is encrypted in transit (TLS) and at rest. We use role-based access controls, PII masking for sensitive data (Aadhaar, PAN), full audit logging with IP tracking, and rate limiting (300 req/min authenticated). Security headers include HSTS, X-Frame-Options, and XSS protection.",
    category: "Security",
  },
  {
    question: "Who can access my company data?",
    answer:
      "Only authenticated users with the correct role can access your company data. Every action is logged. Investor portal access is controlled by token-based links that founders generate and can revoke at any time. Our admin team only accesses data when necessary for support, with full audit trails.",
    category: "Security",
  },
  // Investors
  {
    question: "How do I access my investor portal?",
    answer:
      "Your founder generates a secure token link from their Anvils dashboard and shares it with you via email. Paste the token on our investor portal page to instantly access your holdings, cap table position, documents, and funding history. No account or password needed.",
    category: "Investors",
  },
  {
    question: "Can I see all my portfolio companies in one place?",
    answer:
      "Yes — if your portfolio companies use Anvils. Each company that adds you as an investor generates a separate token. Your investor dashboard aggregates holdings across all companies that have shared access with you.",
    category: "Investors",
  },
  // CAs
  {
    question: "How does the CA portal work?",
    answer:
      "CAs get a dedicated dashboard showing all assigned companies with compliance scores, deadline alerts, filing status, and penalty exposure. You can manage compliance calendars, track tax filings (GST, TDS, ITR), and prepare audit packs — all from one interface.",
    category: "CAs",
  },
  {
    question: "How much can I earn from the marketplace?",
    answer:
      "CAs earn a service margin of 15-20% on each marketplace transaction. Typical annual earnings range from Rs 1.26 lakh to Rs 2.52 lakh depending on client volume. Services include GST filing (Rs 799/mo), ROC filing (Rs 7,999), ITR (Rs 4,999), statutory audit (Rs 14,999), and many more.",
    category: "CAs",
  },
];

export default function FAQPage() {
  const [activeCategory, setActiveCategory] = useState<Category>("All");

  const filteredFAQs =
    activeCategory === "All"
      ? FAQ_DATA
      : FAQ_DATA.filter((f) => f.category === activeCategory);

  return (
    <div className="glow-bg">
      <Header />

      {/* ── Hero ── */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-12 text-center">
        <div className="animate-fade-in-up max-w-3xl mx-auto">
          <h1
            className="text-4xl md:text-5xl font-extrabold leading-tight mb-4 text-[var(--color-text-primary)]"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Frequently asked{" "}
            <span className="gradient-text">questions</span>
          </h1>
          <p className="text-lg text-[var(--color-text-secondary)] leading-relaxed">
            Everything you need to know about Anvils, incorporation, pricing,
            and the platform.
          </p>
        </div>
      </section>

      {/* ── Category Filters ── */}
      <section className="pb-8">
        <div className="max-w-3xl mx-auto px-6">
          <div className="flex flex-wrap gap-2 justify-center">
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
                  activeCategory === cat
                    ? "bg-purple-600 text-white"
                    : "bg-[var(--color-bg-secondary)] text-[var(--color-text-secondary)] hover:bg-purple-50 hover:text-purple-600 border border-[var(--color-border)]"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* ── FAQ List ── */}
      <section className="py-8 pb-20">
        <div className="max-w-3xl mx-auto px-6">
          <FAQAccordion
            items={filteredFAQs.map((f) => ({
              question: f.question,
              answer: f.answer,
            }))}
          />
          {filteredFAQs.length === 0 && (
            <p className="text-center text-[var(--color-text-muted)] py-8">
              No questions found for this category.
            </p>
          )}
        </div>
      </section>

      {/* ── CTA ── */}
      <CTASection
        title="Still have questions?"
        subtitle="Reach out to our team. We're here to help."
        primaryCTA={{ label: "Contact Us", href: "/contact" }}
        secondaryCTA={{ label: "Start Free", href: "/signup" }}
        variant="white"
      />

      <Footer />
      <ChatWidget />
    </div>
  );
}
