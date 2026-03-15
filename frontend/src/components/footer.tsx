"use client";

import Link from "next/link";

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <span className="font-semibold" style={{ color: "var(--color-text-secondary)" }}>
            CMS India
          </span>
          <span style={{ color: "var(--color-text-muted)" }}>
            &copy; {new Date().getFullYear()} Companies Made Simple India
          </span>
        </div>
        <div className="flex items-center gap-6">
          <Link href="/pricing" className="nav-link">Pricing</Link>
          <Link href="/compare" className="nav-link">Compare</Link>
          <Link href="/documents" className="nav-link">Legal Docs</Link>
          <Link href="/learn" className="nav-link">Learn</Link>
          <a href="mailto:support@companiesmade.in" className="nav-link">Support</a>
        </div>
      </div>
    </footer>
  );
}
