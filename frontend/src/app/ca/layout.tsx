"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

// ---------------------------------------------------------------------------
// CA Portal — Teal / Navy professional theme
// Completely separate visual identity from the founder dashboard.
// ---------------------------------------------------------------------------

const CA_NAV = [
  {
    href: "/ca",
    label: "Dashboard",
    icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0a1 1 0 01-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1",
  },
  {
    href: "/ca/tasks",
    label: "Tasks",
    icon: "M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25z",
  },
  {
    href: "/ca/calendar",
    label: "Calendar",
    icon: "M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5",
  },
  {
    href: "/ca/tax",
    label: "Tax",
    icon: "M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z",
  },
  {
    href: "/ca/tds",
    label: "TDS Calc",
    icon: "M15.75 15.75V18m-7.5-6.75h.008v.008H8.25v-.008zm0 2.25h.008v.008H8.25V13.5zm0 2.25h.008v.008H8.25v-.008zm0 2.25h.008v.008H8.25V18zm2.498-6.75h.007v.008h-.007v-.008zm0 2.25h.007v.008h-.007V13.5zm0 2.25h.007v.008h-.007v-.008zm0 2.25h.007v.008h-.007V18zm2.504-6.75h.008v.008h-.008v-.008zm0 2.25h.008v.008h-.008V13.5zm0 2.25h.008v.008h-.008v-.008zm0 2.25h.008v.008h-.008V18zm2.498-6.75h.008v.008h-.008v-.008zm0 2.25h.008v.008h-.008V13.5zM8.25 6h7.5v2.25h-7.5V6zM12 2.25c-1.892 0-3.758.11-5.593.322C5.307 2.7 4.5 3.65 4.5 4.757V19.5a2.25 2.25 0 002.25 2.25h10.5a2.25 2.25 0 002.25-2.25V4.757c0-1.108-.806-2.057-1.907-2.185A48.507 48.507 0 0012 2.25z",
  },
  {
    href: "/ca/companies",
    label: "Companies",
    icon: "M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21m-3.75 3H21m-3.75 3H21",
  },
];

// ---------------------------------------------------------------------------
// Theme constants — teal/navy palette
// ---------------------------------------------------------------------------
const CA = {
  sidebarBg: "#0f172a",
  sidebarText: "#94a3b8",
  sidebarTextActive: "#ffffff",
  sidebarAccent: "#14b8a6",
  sidebarHover: "#1e293b",
  sidebarActiveBg: "rgba(20, 184, 166, 0.12)",
  headerBg: "#ffffff",
  headerBorder: "#e2e8f0",
  pageBg: "#f8fafc",
  textPrimary: "#0f172a",
  textMuted: "#64748b",
  accent: "#0d9488",
};

// ---------------------------------------------------------------------------
// Layout component
// ---------------------------------------------------------------------------

export default function CaLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (loading) return;
    if (!user) {
      router.push("/login");
      return;
    }
    if (user.role !== "ca_lead") {
      router.push("/dashboard");
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: CA.pageBg }}>
        <div
          className="animate-spin rounded-full h-8 w-8 border-b-2"
          style={{ borderColor: CA.accent }}
        />
      </div>
    );
  }

  if (!user || user.role !== "ca_lead") return null;

  const isActive = (href: string) =>
    href === "/ca" ? pathname === "/ca" : pathname.startsWith(href);

  return (
    <div className="min-h-screen" style={{ background: CA.pageBg }}>
      {/* ── Dark Sidebar (persistent on lg, drawer on mobile) ─── */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 lg:hidden"
          style={{ background: "rgba(0,0,0,0.5)" }}
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        role="navigation"
        aria-label="CA Portal navigation"
        className={`fixed top-0 left-0 z-40 h-screen w-60 flex flex-col transition-transform duration-200 lg:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
        style={{ background: CA.sidebarBg }}
      >
        {/* Sidebar header / brand */}
        <div className="h-16 flex items-center gap-3 px-5" style={{ borderBottom: "1px solid rgba(255,255,255,0.08)" }}>
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold text-white"
            style={{ background: CA.sidebarAccent }}
          >
            A
          </div>
          <div>
            <div className="text-sm font-semibold text-white leading-tight">Anvils</div>
            <div className="text-[10px] font-medium uppercase tracking-widest" style={{ color: CA.sidebarAccent }}>
              CA Portal
            </div>
          </div>
        </div>

        {/* Nav links */}
        <nav className="flex-1 py-4 px-3 space-y-1">
          {CA_NAV.map((item) => {
            const active = isActive(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setSidebarOpen(false)}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors"
                style={{
                  background: active ? CA.sidebarActiveBg : "transparent",
                  color: active ? CA.sidebarTextActive : CA.sidebarText,
                  fontWeight: active ? 600 : 400,
                }}
                onMouseEnter={(e) => {
                  if (!active) e.currentTarget.style.background = CA.sidebarHover;
                }}
                onMouseLeave={(e) => {
                  if (!active) e.currentTarget.style.background = "transparent";
                }}
              >
                <svg className="w-[18px] h-[18px] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
                </svg>
                {item.label}
                {active && (
                  <div
                    className="ml-auto w-1.5 h-1.5 rounded-full"
                    style={{ background: CA.sidebarAccent }}
                  />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Sidebar footer — user info */}
        <div className="px-4 py-4" style={{ borderTop: "1px solid rgba(255,255,255,0.08)" }}>
          <div className="flex items-center gap-3">
            <div
              className="w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
              style={{ background: CA.sidebarAccent }}
            >
              {user.full_name?.charAt(0).toUpperCase() || "C"}
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-sm font-medium text-white truncate">{user.full_name}</div>
              <div className="text-[11px] truncate" style={{ color: CA.sidebarText }}>
                Chartered Accountant
              </div>
            </div>
            <button
              onClick={logout}
              className="p-1.5 rounded-md transition-colors flex-shrink-0"
              style={{ color: CA.sidebarText }}
              title="Log out"
              aria-label="Log out"
              onMouseEnter={(e) => { e.currentTarget.style.color = "#f87171"; e.currentTarget.style.background = "rgba(248,113,113,0.1)"; }}
              onMouseLeave={(e) => { e.currentTarget.style.color = CA.sidebarText; e.currentTarget.style.background = "transparent"; }}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
              </svg>
            </button>
          </div>
        </div>
      </aside>

      {/* ── Top Bar (mobile only — hamburger) ─────────────────── */}
      <header
        className="lg:hidden fixed top-0 left-0 right-0 z-30 h-14 flex items-center px-4"
        style={{ background: CA.headerBg, borderBottom: `1px solid ${CA.headerBorder}` }}
      >
        <button
          onClick={() => setSidebarOpen(true)}
          className="p-2 rounded-lg"
          style={{ color: CA.textPrimary }}
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <div className="ml-3 flex items-center gap-2">
          <div
            className="w-6 h-6 rounded flex items-center justify-center text-[10px] font-bold text-white"
            style={{ background: CA.sidebarAccent }}
          >
            A
          </div>
          <span className="text-sm font-semibold" style={{ color: CA.textPrimary }}>Anvils</span>
          <span
            className="text-[9px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded"
            style={{ background: "rgba(20,184,166,0.1)", color: CA.accent }}
          >
            CA
          </span>
        </div>
      </header>

      {/* ── Main Content ──────────────────────────────────────── */}
      <div className="lg:pl-60 pt-14 lg:pt-0 min-h-screen">
        <main className="flex-1 min-w-0">
          {children}
        </main>
      </div>
    </div>
  );
}
