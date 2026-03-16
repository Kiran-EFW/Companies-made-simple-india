import Link from "next/link";
import ChatWidget from "@/components/chat-widget";
import Footer from "@/components/footer";

const PLATFORM_FEATURES = [
  {
    title: "Compliance Tracking",
    desc: "ROC annual returns, board meetings, GST filings, and statutory deadlines — tracked automatically with real-time compliance scoring.",
    iconPath:
      "M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z",
    color: "purple",
  },
  {
    title: "Legal Documents",
    desc: "Board resolutions, share certificates, contracts, and statutory forms — AI-drafted and reviewed by a Company Secretary before you sign.",
    iconPath:
      "M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z",
    color: "blue",
  },
  {
    title: "GST & Tax Management",
    desc: "Track GST return deadlines, manage input tax credits, and get a clear view of your tax obligations — all from a single dashboard.",
    iconPath:
      "M15 8.25H9m6 3H9m3 6l-3-3h1.5a3 3 0 100-6M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
    color: "emerald",
  },
  {
    title: "Accounting Integration",
    desc: "Connect Zoho Books or Tally and sync financials automatically. Pull reports, reconcile ledgers, and stay audit-ready year-round.",
    iconPath:
      "M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z",
    color: "purple",
  },
  {
    title: "Secure Data Room",
    desc: "Incorporation certificates, board minutes, statutory registers, contracts — organized, versioned, and accessible to your team anytime.",
    iconPath:
      "M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z",
    color: "blue",
  },
  {
    title: "Services Marketplace",
    desc: "GST registration, trademark filing, DPIIT recognition, FSSAI, IEC — browse and purchase professional services as your business needs them.",
    iconPath:
      "M15.59 14.37a6 6 0 01-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 006.16-12.12A14.98 14.98 0 009.631 8.41m5.96 5.96a14.926 14.926 0 01-5.841 2.58m-.119-8.54a6 6 0 00-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 00-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 01-2.448-2.448 14.9 14.9 0 01.06-.312m-2.24 2.39a4.493 4.493 0 00-1.757 4.306 4.493 4.493 0 004.306-1.758M16.5 9a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z",
    color: "emerald",
  },
];

const HOW_IT_WORKS = [
  {
    num: "01",
    title: "Connect Your Company",
    desc: "Already incorporated? Enter your CIN and we pull your company details from MCA. Starting fresh? Our AI wizard helps you pick the right entity type and handles the filing.",
    iconPath:
      "M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m9.86-2.388a4.5 4.5 0 00-6.364-6.364L4.5 8.257a4.5 4.5 0 006.364 6.364z",
  },
  {
    num: "02",
    title: "Your Dashboard Goes Live",
    desc: "Compliance calendar, document vault, statutory registers, GST tracker, board meeting scheduler, and direct messaging with your assigned admin team.",
    iconPath:
      "M11.35 3.836c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m8.9-4.414c.376.023.75.05 1.124.08 1.131.094 1.976 1.057 1.976 2.192V16.5A2.25 2.25 0 0118 18.75h-2.25m-7.5-10.5H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V18.75m-7.5-10.5h6.375c.621 0 1.125.504 1.125 1.125v9.375m-8.25-3l1.5 1.5 3-3.75",
  },
  {
    num: "03",
    title: "We Handle the Back-Office",
    desc: "Add services as you grow — accounting integration, tax management, trademark filing, DPIIT recognition. Your entire regulatory and operational back-office, managed.",
    iconPath:
      "M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941",
  },
];

const COLOR_RGB: Record<string, string> = {
  purple: "139,92,246",
  blue: "59,130,246",
  emerald: "16,185,129",
};

export default function HomePage() {
  return (
    <div className="glow-bg">
      {/* ── Navigation ── */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-5 max-w-7xl mx-auto">
        <Link href="/" className="flex items-center gap-2.5">
          <img
            src="/logo-icon.png"
            alt="Anvils"
            className="w-8 h-8 object-contain"
          />
          <span
            className="text-xl font-bold"
            style={{ fontFamily: "var(--font-display)" }}
          >
            <span className="gradient-text">Anvils</span>
          </span>
        </Link>
        <div className="hidden md:flex items-center gap-8">
          <Link
            href="/pricing"
            className="text-sm font-medium transition-colors"
            style={{ color: "var(--color-text-secondary)" }}
          >
            Pricing
          </Link>
          <Link
            href="/compare"
            className="text-sm font-medium transition-colors"
            style={{ color: "var(--color-text-secondary)" }}
          >
            Compare
          </Link>
          <Link
            href="/documents"
            className="text-sm font-medium transition-colors"
            style={{ color: "var(--color-text-secondary)" }}
          >
            Legal Docs
          </Link>
          <Link
            href="/login"
            className="text-sm font-medium transition-colors"
            style={{ color: "var(--color-text-secondary)" }}
          >
            Log in
          </Link>
          <Link href="/signup" className="btn-primary text-sm !py-2 !px-5">
            Get Started
          </Link>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 pt-16 pb-24 text-center">
        <div className="animate-fade-in-up">
          <div className="mb-8">
            <img
              src="/logo-wordmark.png"
              alt="Anvils — Companies Made Simple"
              className="h-16 md:h-20 mx-auto object-contain"
            />
          </div>
          <h1
            className="text-4xl md:text-6xl font-extrabold leading-tight mb-6"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Your Company&apos;s{" "}
            <span className="gradient-text">Back-Office.</span>
            <br />
            Managed.
          </h1>
          <p
            className="text-lg md:text-xl max-w-2xl mx-auto mb-10 leading-relaxed"
            style={{ color: "var(--color-text-secondary)" }}
          >
            Compliance tracking, legal documents, GST management, accounting
            integration, and a services marketplace &mdash; whether you&apos;re
            incorporating a new company or managing an existing one. One
            platform for everything that keeps your company running.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/signup"
              className="btn-primary text-lg !py-4 !px-8"
            >
              Connect Your Company
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"
                />
              </svg>
            </Link>
            <Link
              href="/wizard"
              className="btn-secondary text-lg !py-4 !px-8"
            >
              Incorporating? Start Here
            </Link>
          </div>
        </div>
      </section>

      {/* ── Platform Features ── */}
      <section
        className="relative z-10 py-24"
        style={{ background: "var(--color-bg-secondary)" }}
      >
        <div className="max-w-7xl mx-auto px-6">
          <h2
            className="text-3xl md:text-4xl font-bold text-center mb-4"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Everything Your Company{" "}
            <span className="gradient-text">Needs to Stay Compliant</span>
          </h2>
          <p
            className="text-center mb-12 max-w-xl mx-auto"
            style={{ color: "var(--color-text-secondary)" }}
          >
            The regulatory and operational tools that Indian companies need,
            in one dashboard. No spreadsheets, no missed deadlines.
          </p>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {PLATFORM_FEATURES.map((feature, i) => (
              <div
                key={feature.title}
                className={`glass-card p-6 animate-fade-in-up animate-delay-${Math.min((i + 1) * 100, 400)}`}
              >
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center mb-4"
                  style={{
                    background: `rgba(${COLOR_RGB[feature.color]}, 0.15)`,
                  }}
                >
                  <svg
                    className="w-5 h-5"
                    style={{
                      color: `var(--color-accent-${feature.color})`,
                    }}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={1.5}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d={feature.iconPath}
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-bold mb-2">{feature.title}</h3>
                <p
                  className="text-sm leading-relaxed"
                  style={{ color: "var(--color-text-secondary)" }}
                >
                  {feature.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 py-24">
        <h2
          className="text-3xl md:text-4xl font-bold text-center mb-4"
          style={{ fontFamily: "var(--font-display)" }}
        >
          How It <span className="gradient-text">Works</span>
        </h2>
        <p
          className="text-center mb-16 max-w-xl mx-auto"
          style={{ color: "var(--color-text-secondary)" }}
        >
          Existing company or new incorporation &mdash; you&apos;re set up
          and running in minutes.
        </p>
        <div className="grid md:grid-cols-3 gap-8">
          {HOW_IT_WORKS.map((step) => (
            <div key={step.num} className="glass-card p-8 text-center">
              <div
                className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-4"
                style={{ background: "rgba(139, 92, 246, 0.15)" }}
              >
                <svg
                  className="w-7 h-7"
                  style={{
                    color: "var(--color-accent-purple-light)",
                  }}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d={step.iconPath}
                  />
                </svg>
              </div>
              <div
                className="text-sm font-bold mb-2"
                style={{ color: "var(--color-accent-purple-light)" }}
              >
                STEP {step.num}
              </div>
              <h3 className="text-xl font-bold mb-3">{step.title}</h3>
              <p
                className="text-sm leading-relaxed"
                style={{ color: "var(--color-text-secondary)" }}
              >
                {step.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Two Paths CTA ── */}
      <section
        className="relative z-10 py-24"
        style={{ background: "var(--color-bg-secondary)" }}
      >
        <div className="max-w-7xl mx-auto px-6">
          <h2
            className="text-3xl md:text-4xl font-bold text-center mb-16"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Ready to{" "}
            <span className="gradient-text">Get Started?</span>
          </h2>
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Existing Company */}
            <div className="glass-card p-8 text-center">
              <div
                className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-4"
                style={{ background: "rgba(16, 185, 129, 0.15)" }}
              >
                <svg
                  className="w-7 h-7"
                  style={{ color: "var(--color-accent-emerald-light)" }}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m9.86-2.388a4.5 4.5 0 00-6.364-6.364L4.5 8.257a4.5 4.5 0 006.364 6.364z"
                  />
                </svg>
              </div>
              <h3
                className="text-xl font-bold mb-3"
                style={{ fontFamily: "var(--font-display)" }}
              >
                Already Have a Company?
              </h3>
              <p
                className="text-sm mb-6 leading-relaxed"
                style={{ color: "var(--color-text-secondary)" }}
              >
                Connect your existing Pvt Ltd, LLP, or OPC.
                Import your company details and start managing compliance,
                documents, and services from day one.
              </p>
              <Link
                href="/signup"
                className="btn-primary w-full text-center justify-center"
              >
                Connect Your Company
                <svg
                  className="w-4 h-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"
                  />
                </svg>
              </Link>
            </div>

            {/* New Incorporation */}
            <div className="glass-card p-8 text-center">
              <div
                className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-4"
                style={{ background: "rgba(139, 92, 246, 0.15)" }}
              >
                <svg
                  className="w-7 h-7"
                  style={{ color: "var(--color-accent-purple-light)" }}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 4.5v15m7.5-7.5h-15"
                  />
                </svg>
              </div>
              <h3
                className="text-xl font-bold mb-3"
                style={{ fontFamily: "var(--font-display)" }}
              >
                Starting a New Company?
              </h3>
              <p
                className="text-sm mb-6 leading-relaxed"
                style={{ color: "var(--color-text-secondary)" }}
              >
                Incorporate a Private Limited, OPC, LLP, or Section 8 company.
                Our AI wizard picks the right entity, and we handle MCA filing
                with transparent, itemized pricing.
              </p>
              <Link
                href="/wizard"
                className="btn-secondary w-full text-center justify-center"
              >
                Find Your Entity Type
                <svg
                  className="w-4 h-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"
                  />
                </svg>
              </Link>
            </div>
          </div>
        </div>
      </section>

      <Footer />

      <ChatWidget />
    </div>
  );
}
