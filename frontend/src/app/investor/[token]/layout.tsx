"use client";

import { ReactNode } from "react";
import Link from "next/link";
import Image from "next/image";
import { useParams, usePathname } from "next/navigation";

export default function InvestorPortalLayout({ children }: { children: ReactNode }) {
  const params = useParams();
  const pathname = usePathname();
  const token = params.token as string;

  const navItems = [
    { href: `/investor/${token}`, label: "Portfolio", exact: true },
    { href: `/investor/${token}/discover`, label: "Deals" },
  ];

  return (
    <div className="min-h-screen" style={{ background: "var(--color-bg-secondary)" }}>
      {/* Header */}
      <header
        className="sticky top-0 z-30 backdrop-blur-md border-b"
        style={{
          background: "var(--color-bg-glass)",
          borderColor: "var(--color-border)",
        }}
      >
        <div className="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image src="/logo-icon.png" alt="Anvils" width={43} height={28} className="object-contain" />
            <span
              className="text-lg font-semibold"
              style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
            >
              Anvils
            </span>
            <span
              className="text-xs font-medium px-2.5 py-1 rounded-full"
              style={{
                background: "rgba(124, 58, 237, 0.08)",
                color: "var(--color-accent-purple)",
              }}
            >
              Investor Portal
            </span>
          </div>

          <nav className="flex items-center gap-1">
            {navItems.map((item) => {
              const isActive = item.exact
                ? pathname === item.href
                : pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
                  style={{
                    color: isActive ? "var(--color-accent-purple)" : "var(--color-text-secondary)",
                    background: isActive ? "rgba(124, 58, 237, 0.06)" : "transparent",
                  }}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">{children}</main>

      <footer
        className="border-t px-6 py-4 mt-12"
        style={{
          background: "var(--color-bg-primary)",
          borderColor: "var(--color-border)",
        }}
      >
        <div
          className="max-w-6xl mx-auto text-center text-xs"
          style={{ color: "var(--color-text-muted)" }}
        >
          Powered by Anvils — Equity & Governance Platform
        </div>
      </footer>
    </div>
  );
}
