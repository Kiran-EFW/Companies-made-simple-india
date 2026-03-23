"use client";

import Link from "next/link";

const PRODUCT_LINKS = [
  { label: "Cap Table", href: "/features/cap-table" },
  { label: "ESOP", href: "/features/esop" },
  { label: "Fundraising", href: "/features/fundraising" },
  { label: "Compliance", href: "/features/compliance" },
  { label: "Valuations", href: "/features/valuations" },
  { label: "Legal Documents", href: "/features/legal-docs" },
  { label: "Data Room", href: "/features/data-room" },
];

const SOLUTIONS_LINKS = [
  { label: "For Founders", href: "/for/founders" },
  { label: "For Investors", href: "/for/investors" },
  { label: "Pricing", href: "/pricing" },
  { label: "Compare Entities", href: "/compare" },
];

const RESOURCES_LINKS = [
  { label: "Learning Center", href: "/learn" },
  { label: "Entity Wizard", href: "/wizard" },
  { label: "Free Cap Table Tool", href: "/cap-table-setup" },
  { label: "Incorporation", href: "/wizard" },
  { label: "Support", href: "mailto:support@anvils.in" },
];

export default function Footer() {
  return (
    <footer className="border-t border-[var(--color-border)] bg-[var(--color-bg-card)]">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="flex items-center gap-2 mb-3">
              <img src="/logo-icon.png" alt="Anvils" className="w-6 h-6 object-contain" />
              <span className="text-lg font-bold text-[var(--color-text-primary)]" style={{ fontFamily: "var(--font-display)" }}>
                Anvils
              </span>
            </Link>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
              Equity &amp; governance platform for Indian startups.
            </p>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-3">Product</h4>
            <ul className="space-y-2">
              {PRODUCT_LINKS.map((link) => (
                <li key={link.href}>
                  <Link href={link.href} className="text-sm text-[var(--color-text-secondary)] hover:text-purple-600 transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Solutions */}
          <div>
            <h4 className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-3">Solutions</h4>
            <ul className="space-y-2">
              {SOLUTIONS_LINKS.map((link) => (
                <li key={link.href}>
                  <Link href={link.href} className="text-sm text-[var(--color-text-secondary)] hover:text-purple-600 transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-3">Resources</h4>
            <ul className="space-y-2">
              {RESOURCES_LINKS.map((link) => (
                <li key={link.href}>
                  {link.href.startsWith("mailto:") ? (
                    <a href={link.href} className="text-sm text-[var(--color-text-secondary)] hover:text-purple-600 transition-colors">
                      {link.label}
                    </a>
                  ) : (
                    <Link href={link.href} className="text-sm text-[var(--color-text-secondary)] hover:text-purple-600 transition-colors">
                      {link.label}
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-10 pt-6 border-t border-[var(--color-border)] flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-xs text-[var(--color-text-muted)]">
            &copy; {new Date().getFullYear()} Anvils. All rights reserved.
          </p>
          <div className="flex items-center gap-4">
            <a href="/privacy" className="text-xs text-[var(--color-text-muted)]">Privacy Policy</a>
            <a href="/terms" className="text-xs text-[var(--color-text-muted)]">Terms of Service</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
