"use client";

import { useState } from "react";
import Link from "next/link";
import { Twitter, Linkedin, Youtube, ArrowRight } from "lucide-react";

/* ------------------------------------------------------------------ */
/*  Link data                                                          */
/* ------------------------------------------------------------------ */

const PLATFORM_LINKS = [
  { label: "Incorporation", href: "/wizard" },
  { label: "Cap Table", href: "/features/cap-table" },
  { label: "ESOP", href: "/features/esop" },
  { label: "Compliance", href: "/features/compliance" },
  { label: "Fundraising", href: "/features/fundraising" },
  { label: "Valuations", href: "/features/valuations" },
  { label: "Data Room", href: "/features/data-room" },
];

const SOLUTIONS_LINKS = [
  { label: "For Founders", href: "/for/founders" },
  { label: "For Investors", href: "/for/investors" },
  { label: "For CAs", href: "/for/cas" },
  { label: "Partner Portal Login", href: "/login?portal=ca" },
  { label: "Partner Sign Up", href: "/signup?role=ca" },
  { label: "Pricing", href: "/pricing" },
  { label: "Services", href: "/services" },
];

const RESOURCES_LINKS = [
  { label: "Entity Wizard", href: "/wizard" },
  { label: "Compare Entities", href: "/compare" },
  { label: "Free Cap Table Tool", href: "/cap-table-setup" },
  { label: "Learning Center", href: "/learn" },
  { label: "FAQ", href: "/faq" },
];

const COMPANY_LINKS = [
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
  { label: "Security", href: "/security" },
  { label: "Privacy Policy", href: "/privacy" },
  { label: "Terms of Service", href: "/terms" },
];

const SOCIAL_LINKS = [
  { label: "Twitter / X", href: "https://twitter.com/anvilsindia", icon: Twitter },
  { label: "LinkedIn", href: "https://linkedin.com/company/anvils-india", icon: Linkedin },
  { label: "YouTube", href: "https://youtube.com/@anvilsindia", icon: Youtube },
];

/* ------------------------------------------------------------------ */
/*  Reusable column component                                          */
/* ------------------------------------------------------------------ */

function FooterColumn({
  title,
  links,
}: {
  title: string;
  links: { label: string; href: string }[];
}) {
  return (
    <div>
      <h4
        className="text-xs font-semibold uppercase tracking-wider mb-4"
        style={{ color: "var(--color-text-muted)" }}
      >
        {title}
      </h4>
      <ul className="space-y-2.5">
        {links.map((link) => (
          <li key={link.href + link.label}>
            <Link
              href={link.href}
              className="text-sm transition-colors hover:text-purple-600"
              style={{ color: "var(--color-text-secondary)" }}
            >
              {link.label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Footer                                                             */
/* ------------------------------------------------------------------ */

export default function Footer() {
  const [email, setEmail] = useState("");
  const [subscribed, setSubscribed] = useState(false);

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    // TODO: wire up to API
    setSubscribed(true);
    setEmail("");
  };

  return (
    <footer
      className="border-t"
      style={{
        borderColor: "var(--color-border)",
        backgroundColor: "var(--color-bg-secondary)",
      }}
    >
      {/* ---- Newsletter strip ---- */}
      <div
        className="border-b"
        style={{ borderColor: "var(--color-border)" }}
      >
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-5">
            <div className="max-w-md">
              <h3
                className="text-base font-semibold mb-1"
                style={{
                  fontFamily: "var(--font-display)",
                  color: "var(--color-text-primary)",
                }}
              >
                Stay updated on Indian startup compliance
              </h3>
              <p
                className="text-sm"
                style={{ color: "var(--color-text-muted)" }}
              >
                Monthly insights on RBI, MCA and SEBI changes that affect your company.
              </p>
            </div>

            {subscribed ? (
              <p className="text-sm font-medium text-green-600">
                Thanks for subscribing!
              </p>
            ) : (
              <form
                onSubmit={handleSubscribe}
                className="flex w-full md:w-auto items-center gap-2"
              >
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@company.com"
                  className="w-full md:w-64 rounded-lg border px-3.5 py-2 text-sm outline-none transition-colors focus:ring-2 focus:ring-purple-500/40"
                  style={{
                    borderColor: "var(--color-border)",
                    backgroundColor: "var(--color-bg-card)",
                    color: "var(--color-text-primary)",
                  }}
                />
                <button
                  type="submit"
                  className="shrink-0 inline-flex items-center gap-1.5 rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-purple-700"
                >
                  Subscribe
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </form>
            )}
          </div>
        </div>
      </div>

      {/* ---- Main link grid ---- */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-10 lg:gap-8">
          {/* Brand column */}
          <div className="sm:col-span-2 lg:col-span-1">
            <Link href="/" className="flex items-center gap-2.5 mb-3">
              <img
                src="/logo-icon.png"
                alt="Anvils"
                className="w-7 h-7 object-contain"
              />
              <span
                className="text-lg font-bold"
                style={{
                  fontFamily: "var(--font-display)",
                  color: "var(--color-text-primary)",
                }}
              >
                Anvils
              </span>
            </Link>

            <p
              className="text-sm leading-relaxed mb-5"
              style={{ color: "var(--color-text-secondary)" }}
            >
              The operating system for Indian companies.
            </p>

            <div className="flex items-center gap-3">
              {SOCIAL_LINKS.map(({ label, href, icon: Icon }) => (
                <a
                  key={label}
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={label}
                  className="flex items-center justify-center w-8 h-8 rounded-lg transition-colors hover:bg-purple-600/10"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  <Icon className="w-4 h-4" />
                </a>
              ))}
            </div>
          </div>

          {/* Platform */}
          <FooterColumn title="Platform" links={PLATFORM_LINKS} />

          {/* Solutions */}
          <FooterColumn title="Solutions" links={SOLUTIONS_LINKS} />

          {/* Resources */}
          <FooterColumn title="Resources" links={RESOURCES_LINKS} />

          {/* Company */}
          <FooterColumn title="Company" links={COMPANY_LINKS} />
        </div>
      </div>

      {/* ---- Bottom bar ---- */}
      <div
        className="border-t"
        style={{ borderColor: "var(--color-border)" }}
      >
        <div className="max-w-7xl mx-auto px-6 py-5 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p
            className="text-xs"
            style={{ color: "var(--color-text-muted)" }}
          >
            &copy; 2024&ndash;2026 Anvils. All rights reserved.
          </p>

          <p
            className="text-xs flex items-center gap-1.5"
            style={{ color: "var(--color-text-muted)" }}
          >
            Made in
            <span
              className="inline-block text-base leading-none"
              role="img"
              aria-label="India"
            >
              &#127470;&#127475;
            </span>
            India
          </p>
        </div>
      </div>
    </footer>
  );
}
