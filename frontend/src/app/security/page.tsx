import Header from "@/components/header";
import Footer from "@/components/footer";
import ChatWidget from "@/components/chat-widget";
import SectionHeader from "@/components/marketing/section-header";
import CTASection from "@/components/marketing/cta-section";
import FAQAccordion from "@/components/marketing/faq-accordion";
import {
  Shield,
  Lock,
  Eye,
  Activity,
  Key,
  Server,
  ShieldCheck,
  FileCheck,
  Fingerprint,
  CheckCircle2,
} from "lucide-react";

const SECURITY_PILLARS = [
  {
    icon: <Lock className="w-5 h-5" />,
    title: "Encryption",
    description:
      "All data encrypted in transit (TLS 1.2+) and at rest. Sensitive fields like Aadhaar and PAN are additionally masked in the database.",
    color: "purple",
  },
  {
    icon: <Shield className="w-5 h-5" />,
    title: "Access Control",
    description:
      "Role-based access controls (RBAC) ensure founders, investors, CAs, and admins only see what they're authorized to access.",
    color: "blue",
  },
  {
    icon: <Activity className="w-5 h-5" />,
    title: "Audit Logging",
    description:
      "Every action is logged with user identity, IP address, timestamp, and user agent. Full audit trails for compliance and accountability.",
    color: "emerald",
  },
  {
    icon: <Eye className="w-5 h-5" />,
    title: "Rate Limiting",
    description:
      "API rate limiting at 300 requests/minute for authenticated users. Protection against brute-force and abuse.",
    color: "purple",
  },
  {
    icon: <Key className="w-5 h-5" />,
    title: "Token-Based Access",
    description:
      "Investor portal uses encrypted, time-limited tokens. Founders control access and can revoke tokens at any time.",
    color: "blue",
  },
  {
    icon: <Server className="w-5 h-5" />,
    title: "Security Headers",
    description:
      "HSTS, X-Frame-Options, X-Content-Type-Options, and XSS protection headers on all responses. CORS policies restrict cross-origin access.",
    color: "emerald",
  },
];

const DATA_PROTECTION_CARDS = [
  {
    icon: <Fingerprint className="w-5 h-5" />,
    title: "PII Masking",
    description:
      "Aadhaar numbers, PAN cards, and other personally identifiable information are masked in the database and only revealed to authorized users.",
  },
  {
    icon: <FileCheck className="w-5 h-5" />,
    title: "Document Security",
    description:
      "Data room files shared via token-based links with optional password protection, expiry dates, and download limits. Every access is logged.",
  },
  {
    icon: <ShieldCheck className="w-5 h-5" />,
    title: "E-Signature Integrity",
    description:
      "Digital signatures include IP address, timestamp, and user agent logging. OTP verification available for additional security.",
  },
];

const INFRA_ITEMS = [
  "HTTPS enforced on all endpoints",
  "CORS restricted to authorized domains",
  "SQL injection protection via parameterized queries (SQLAlchemy ORM)",
  "XSS protection with content security headers",
  "CSRF protection on all state-changing operations",
  "Secure session management with HttpOnly cookies",
  "Regular dependency updates and vulnerability scanning",
  "Database backups with point-in-time recovery",
];

const SECURITY_FAQS = [
  {
    question: "Is my data encrypted?",
    answer:
      "Yes. All data is encrypted in transit using TLS 1.2+ and encrypted at rest. Sensitive fields such as Aadhaar numbers and PAN cards receive an additional layer of masking in the database, ensuring they are never stored in plain text. Only authorized users with the correct role-based permissions can view unmasked data.",
  },
  {
    question: "Who can access my company data?",
    answer:
      "Only authenticated users with the correct role can access your company data. We use role-based access controls (RBAC) so founders, investors, CAs, and admins each see only what they are authorized to access. Every action is logged with full audit trails. Investor portal access is controlled by time-limited, encrypted tokens that founders can revoke at any time.",
  },
  {
    question: "How do you handle PII (Aadhaar, PAN)?",
    answer:
      "Personally identifiable information like Aadhaar and PAN numbers are masked in the database and only revealed to authorized users on a need-to-know basis. We follow data minimization principles \u2014 we only collect what is necessary for regulatory compliance and business operations. Access to PII is logged and auditable.",
  },
  {
    question: "Can I request data deletion?",
    answer:
      "Yes. You can request deletion of your personal data by contacting our support team. We will process your request in accordance with applicable data protection regulations. Note that certain data may need to be retained for legal and regulatory compliance purposes (e.g., MCA filings, tax records), but all non-essential personal data will be permanently deleted.",
  },
];

const COLOR_MAP: Record<string, { bg: string; text: string }> = {
  purple: { bg: "bg-purple-50", text: "text-purple-600" },
  blue: { bg: "bg-blue-50", text: "text-blue-600" },
  emerald: { bg: "bg-emerald-50", text: "text-emerald-600" },
};

export default function SecurityPage() {
  return (
    <div className="glow-bg">
      <Header />

      {/* -- Hero -- */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-16 text-center">
        <div className="animate-fade-in-up max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-purple-50 border border-purple-100 text-purple-700 text-xs font-semibold uppercase tracking-wider mb-6">
            Security &amp; Privacy
          </div>
          <h1
            className="text-4xl md:text-5xl lg:text-6xl font-extrabold leading-tight mb-6 text-[var(--color-text-primary)]"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Your company data is{" "}
            <span className="gradient-text">safe with us</span>
          </h1>
          <p className="text-lg md:text-xl text-[var(--color-text-secondary)] leading-relaxed mb-10 max-w-2xl mx-auto">
            Enterprise-grade security built into every layer of the Anvils
            platform. Your equity, compliance, and financial data is protected
            with industry-standard practices.
          </p>
        </div>
      </section>

      {/* -- Security Pillars -- */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={
              <>
                Security at <span className="gradient-text">every layer</span>
              </>
            }
            subtitle="Six pillars that protect your data around the clock."
          />
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {SECURITY_PILLARS.map((pillar) => {
              const colors = COLOR_MAP[pillar.color];
              return (
                <div key={pillar.title} className="card-static p-6">
                  <div
                    className={`w-10 h-10 rounded-xl ${colors.bg} flex items-center justify-center mb-4`}
                  >
                    <div className={colors.text}>{pillar.icon}</div>
                  </div>
                  <h3 className="text-base font-bold text-[var(--color-text-primary)] mb-2">
                    {pillar.title}
                  </h3>
                  <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                    {pillar.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* -- Data Protection -- */}
      <section className="py-16 bg-[var(--color-bg-secondary)]">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={
              <>
                How we protect your{" "}
                <span className="gradient-text">sensitive data</span>
              </>
            }
            subtitle="Purpose-built for handling financial and legal information."
          />
          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {DATA_PROTECTION_CARDS.map((card) => (
              <div key={card.title} className="card-static p-6">
                <div className="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center mb-4">
                  <div className="text-purple-600">{card.icon}</div>
                </div>
                <h3 className="text-base font-bold text-[var(--color-text-primary)] mb-2">
                  {card.title}
                </h3>
                <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                  {card.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* -- Infrastructure & Compliance -- */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={
              <>
                Infrastructure you can{" "}
                <span className="gradient-text">trust</span>
              </>
            }
            subtitle="Industry-standard protections across the entire stack."
          />
          <div className="max-w-3xl mx-auto">
            <div className="card-static p-8">
              <ul className="space-y-4">
                {INFRA_ITEMS.map((item) => (
                  <li key={item} className="flex items-start gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
                    <span className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                      {item}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* -- FAQ -- */}
      <section className="py-16 bg-[var(--color-bg-secondary)]">
        <div className="max-w-7xl mx-auto px-6">
          <SectionHeader
            title={
              <>
                Security <span className="gradient-text">FAQ</span>
              </>
            }
            subtitle="Common questions about how we keep your data safe."
          />
          <div className="max-w-3xl mx-auto">
            <FAQAccordion items={SECURITY_FAQS} />
          </div>
        </div>
      </section>

      {/* -- CTA -- */}
      <CTASection
        title="Questions about security?"
        subtitle="Our team is happy to discuss our security practices in detail."
        primaryCTA={{ label: "Contact Us", href: "/contact" }}
        secondaryCTA={{ label: "Read FAQ", href: "/faq" }}
        variant="white"
      />

      <Footer />
      <ChatWidget />
    </div>
  );
}
