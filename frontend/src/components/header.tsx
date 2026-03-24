"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTheme } from "@/lib/theme-context";
import {
  BarChart3,
  Users,
  TrendingUp,
  Calculator,
  Shield,
  Calendar,
  FileText,
  FolderLock,
  Receipt,
  BookOpen,
  Eye,
  Briefcase,
  Rocket,
  Compass,
  GitCompare,
  GraduationCap,
  Table2,
  Building2,
  HelpCircle,
  Menu,
  X,
  ChevronDown,
  Sun,
  Moon,
} from "lucide-react";

const PRODUCTS = [
  {
    heading: "Equity & Governance",
    items: [
      { label: "Cap Table", desc: "Shareholders, dilution, certificates", href: "/features/cap-table", icon: BarChart3 },
      { label: "ESOP", desc: "Plans, grants, vesting & exercise", href: "/features/esop", icon: Users },
      { label: "Fundraising", desc: "Rounds, closing room, filings", href: "/features/fundraising", icon: TrendingUp },
      { label: "Valuations", desc: "NAV & DCF for Rule 11UA FMV", href: "/features/valuations", icon: Calculator },
      { label: "Stakeholders", desc: "Investor & employee profiles", href: "/features/stakeholders", icon: Briefcase },
    ],
  },
  {
    heading: "Compliance & Operations",
    items: [
      { label: "Compliance Calendar", desc: "ROC, board meetings, GST deadlines", href: "/features/compliance", icon: Shield },
      { label: "Board Meetings", desc: "Scheduling, minutes, resolutions", href: "/features/board-meetings", icon: Calendar },
      { label: "Legal Documents", desc: "Professional contracts & e-signatures", href: "/features/legal-docs", icon: FileText },
      { label: "Data Room", desc: "Secure document sharing", href: "/features/data-room", icon: FolderLock },
      { label: "GST & Tax", desc: "Returns, TDS, tax overview", href: "/features/gst-tax", icon: Receipt },
      { label: "Accounting", desc: "Zoho Books & Tally integration", href: "/features/accounting", icon: BookOpen },
    ],
  },
  {
    heading: "Portals",
    items: [
      { label: "Investor Portal", desc: "Token-based portfolio dashboard", href: "/for/investors", icon: Eye },
      { label: "Partner Portal", desc: "Multi-client compliance dashboard", href: "/for/cas", icon: Building2 },
      { label: "Incorporation", desc: "Guided entity wizard & filing", href: "/wizard", icon: Rocket },
    ],
  },
];

const SOLUTIONS = [
  { label: "For Founders", desc: "Cap table, ESOP, fundraising, compliance", href: "/for/founders", icon: Rocket },
  { label: "For Investors", desc: "Portfolio dashboard & company discovery", href: "/for/investors", icon: Eye },
  { label: "For CAs & Professionals", desc: "Multi-client dashboard & marketplace", href: "/for/cas", icon: Building2 },
];

const RESOURCES = [
  { label: "Entity Wizard", desc: "Find the right entity type", href: "/wizard", icon: Compass },
  { label: "Compare Entities", desc: "Side-by-side comparison", href: "/compare", icon: GitCompare },
  { label: "Learning Center", desc: "Guides & best practices", href: "/learn", icon: GraduationCap },
  { label: "Free Cap Table Tool", desc: "Build your cap table instantly", href: "/cap-table-setup", icon: Table2 },
  { label: "FAQ", desc: "Common questions answered", href: "/faq", icon: HelpCircle },
];

type DropdownKey = "products" | "solutions" | "resources" | null;

export default function Header() {
  const [openDropdown, setOpenDropdown] = useState<DropdownKey>(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [mobileSection, setMobileSection] = useState<string | null>(null);
  const pathname = usePathname();
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const navRef = useRef<HTMLDivElement>(null);
  const { theme, toggleTheme } = useTheme();

  // Close dropdowns on route change
  useEffect(() => {
    setOpenDropdown(null);
    setMobileOpen(false);
    setMobileSection(null);
  }, [pathname]);

  // Close on click outside
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (navRef.current && !navRef.current.contains(e.target as Node)) {
        setOpenDropdown(null);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleMouseEnter = (key: DropdownKey) => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    setOpenDropdown(key);
  };

  const handleMouseLeave = () => {
    timeoutRef.current = setTimeout(() => setOpenDropdown(null), 150);
  };

  return (
    <header
      className="sticky top-0 z-50 backdrop-blur-sm border-b"
      style={{
        backgroundColor: theme === "dark" ? "rgba(26, 31, 53, 0.95)" : "rgba(255, 255, 255, 0.95)",
        borderColor: "var(--color-border)",
      }}
    >
      <div className="max-w-7xl mx-auto px-6" ref={navRef}>
        <nav className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 shrink-0">
            <img src="/logo-icon.png" alt="Anvils" className="w-7 h-7 object-contain" />
            <span
              className="text-lg font-bold"
              style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
            >
              Anvils
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden lg:flex items-center gap-1">
            {/* Products */}
            <div
              className="relative"
              onMouseEnter={() => handleMouseEnter("products")}
              onMouseLeave={handleMouseLeave}
            >
              <button
                onClick={() => setOpenDropdown(openDropdown === "products" ? null : "products")}
                className="flex items-center gap-1 px-3 py-2 text-sm font-medium rounded-lg transition-colors"
                style={{ color: "var(--color-text-secondary)" }}
              >
                Products
                <ChevronDown className={`w-3.5 h-3.5 transition-transform ${openDropdown === "products" ? "rotate-180" : ""}`} />
              </button>
              {openDropdown === "products" && (
                <div
                  className="absolute top-full left-1/2 -translate-x-1/2 mt-1 w-[780px] rounded-xl shadow-lg p-6"
                  style={{
                    backgroundColor: "var(--color-bg-card)",
                    border: "1px solid var(--color-border)",
                  }}
                  onMouseEnter={() => handleMouseEnter("products")}
                  onMouseLeave={handleMouseLeave}
                >
                  <div className="grid grid-cols-3 gap-6">
                    {PRODUCTS.map((group) => (
                      <div key={group.heading}>
                        <div
                          className="text-xs font-semibold uppercase tracking-wider mb-3"
                          style={{ color: "var(--color-text-muted)" }}
                        >
                          {group.heading}
                        </div>
                        <div className="space-y-1">
                          {group.items.map((item) => (
                            <Link
                              key={item.href}
                              href={item.href}
                              className="flex items-start gap-3 p-2 rounded-lg transition-colors group"
                              style={{ color: "var(--color-text-primary)" }}
                            >
                              <item.icon className="w-4 h-4 mt-0.5 shrink-0" style={{ color: "var(--color-accent-purple)" }} />
                              <div>
                                <div className="text-sm font-medium">{item.label}</div>
                                <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>{item.desc}</div>
                              </div>
                            </Link>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Solutions */}
            <div
              className="relative"
              onMouseEnter={() => handleMouseEnter("solutions")}
              onMouseLeave={handleMouseLeave}
            >
              <button
                onClick={() => setOpenDropdown(openDropdown === "solutions" ? null : "solutions")}
                className="flex items-center gap-1 px-3 py-2 text-sm font-medium rounded-lg transition-colors"
                style={{ color: "var(--color-text-secondary)" }}
              >
                Solutions
                <ChevronDown className={`w-3.5 h-3.5 transition-transform ${openDropdown === "solutions" ? "rotate-180" : ""}`} />
              </button>
              {openDropdown === "solutions" && (
                <div
                  className="absolute top-full left-1/2 -translate-x-1/2 mt-1 w-[320px] rounded-xl shadow-lg p-3"
                  style={{
                    backgroundColor: "var(--color-bg-card)",
                    border: "1px solid var(--color-border)",
                  }}
                  onMouseEnter={() => handleMouseEnter("solutions")}
                  onMouseLeave={handleMouseLeave}
                >
                  {SOLUTIONS.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      className="flex items-start gap-3 p-3 rounded-lg transition-colors group"
                      style={{ color: "var(--color-text-primary)" }}
                    >
                      <item.icon className="w-4 h-4 mt-0.5 shrink-0" style={{ color: "var(--color-accent-purple)" }} />
                      <div>
                        <div className="text-sm font-medium">{item.label}</div>
                        <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>{item.desc}</div>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </div>

            {/* Resources */}
            <div
              className="relative"
              onMouseEnter={() => handleMouseEnter("resources")}
              onMouseLeave={handleMouseLeave}
            >
              <button
                onClick={() => setOpenDropdown(openDropdown === "resources" ? null : "resources")}
                className="flex items-center gap-1 px-3 py-2 text-sm font-medium rounded-lg transition-colors"
                style={{ color: "var(--color-text-secondary)" }}
              >
                Resources
                <ChevronDown className={`w-3.5 h-3.5 transition-transform ${openDropdown === "resources" ? "rotate-180" : ""}`} />
              </button>
              {openDropdown === "resources" && (
                <div
                  className="absolute top-full left-1/2 -translate-x-1/2 mt-1 w-[320px] rounded-xl shadow-lg p-3"
                  style={{
                    backgroundColor: "var(--color-bg-card)",
                    border: "1px solid var(--color-border)",
                  }}
                  onMouseEnter={() => handleMouseEnter("resources")}
                  onMouseLeave={handleMouseLeave}
                >
                  {RESOURCES.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      className="flex items-start gap-3 p-3 rounded-lg transition-colors group"
                      style={{ color: "var(--color-text-primary)" }}
                    >
                      <item.icon className="w-4 h-4 mt-0.5 shrink-0" style={{ color: "var(--color-accent-purple)" }} />
                      <div>
                        <div className="text-sm font-medium">{item.label}</div>
                        <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>{item.desc}</div>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </div>

            {/* Pricing direct link */}
            <Link
              href="/pricing"
              className="px-3 py-2 text-sm font-medium rounded-lg transition-colors"
              style={{ color: "var(--color-text-secondary)" }}
            >
              Pricing
            </Link>

            {/* Services direct link */}
            <Link
              href="/services"
              className="px-3 py-2 text-sm font-medium rounded-lg transition-colors"
              style={{ color: "var(--color-text-secondary)" }}
            >
              Services
            </Link>
          </div>

          {/* Right side */}
          <div className="hidden lg:flex items-center gap-3">
            {/* Theme toggle */}
            <button
              onClick={toggleTheme}
              className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors"
              style={{
                color: "var(--color-text-secondary)",
                backgroundColor: "transparent",
              }}
              aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
            >
              {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
            <Link
              href="/login"
              className="text-sm font-medium transition-colors"
              style={{ color: "var(--color-text-secondary)" }}
            >
              Log in
            </Link>
            <Link href="/signup" className="btn-primary btn-sm">
              Get Started Free
            </Link>
          </div>

          {/* Mobile hamburger */}
          <div className="lg:hidden flex items-center gap-2">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg transition-colors"
              style={{ color: "var(--color-text-secondary)" }}
              aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
            >
              {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="p-2 rounded-lg"
              style={{ color: "var(--color-text-secondary)" }}
            >
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </nav>

        {/* Mobile Menu */}
        {mobileOpen && (
          <div
            className="lg:hidden py-4 space-y-1 max-h-[80vh] overflow-y-auto"
            style={{ borderTop: "1px solid var(--color-border)" }}
          >
            {/* Products accordion */}
            <button
              onClick={() => setMobileSection(mobileSection === "products" ? null : "products")}
              className="flex items-center justify-between w-full px-3 py-2.5 text-sm font-medium rounded-lg"
              style={{ color: "var(--color-text-primary)" }}
            >
              Products
              <ChevronDown className={`w-4 h-4 transition-transform ${mobileSection === "products" ? "rotate-180" : ""}`} />
            </button>
            {mobileSection === "products" && (
              <div className="pl-4 space-y-3 py-2">
                {PRODUCTS.map((group) => (
                  <div key={group.heading}>
                    <div
                      className="text-xs font-semibold uppercase tracking-wider px-3 mb-1"
                      style={{ color: "var(--color-text-muted)" }}
                    >
                      {group.heading}
                    </div>
                    {group.items.map((item) => (
                      <Link
                        key={item.href}
                        href={item.href}
                        className="flex items-center gap-2 px-3 py-2 text-sm rounded-lg"
                        style={{ color: "var(--color-text-secondary)" }}
                      >
                        <item.icon className="w-4 h-4 shrink-0" style={{ color: "var(--color-accent-purple)" }} />
                        {item.label}
                      </Link>
                    ))}
                  </div>
                ))}
              </div>
            )}

            {/* Solutions accordion */}
            <button
              onClick={() => setMobileSection(mobileSection === "solutions" ? null : "solutions")}
              className="flex items-center justify-between w-full px-3 py-2.5 text-sm font-medium rounded-lg"
              style={{ color: "var(--color-text-primary)" }}
            >
              Solutions
              <ChevronDown className={`w-4 h-4 transition-transform ${mobileSection === "solutions" ? "rotate-180" : ""}`} />
            </button>
            {mobileSection === "solutions" && (
              <div className="pl-4 py-2">
                {SOLUTIONS.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="flex items-center gap-2 px-3 py-2 text-sm rounded-lg"
                    style={{ color: "var(--color-text-secondary)" }}
                  >
                    <item.icon className="w-4 h-4 shrink-0" style={{ color: "var(--color-accent-purple)" }} />
                    {item.label}
                  </Link>
                ))}
              </div>
            )}

            {/* Resources accordion */}
            <button
              onClick={() => setMobileSection(mobileSection === "resources" ? null : "resources")}
              className="flex items-center justify-between w-full px-3 py-2.5 text-sm font-medium rounded-lg"
              style={{ color: "var(--color-text-primary)" }}
            >
              Resources
              <ChevronDown className={`w-4 h-4 transition-transform ${mobileSection === "resources" ? "rotate-180" : ""}`} />
            </button>
            {mobileSection === "resources" && (
              <div className="pl-4 py-2">
                {RESOURCES.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="flex items-center gap-2 px-3 py-2 text-sm rounded-lg"
                    style={{ color: "var(--color-text-secondary)" }}
                  >
                    <item.icon className="w-4 h-4 shrink-0" style={{ color: "var(--color-accent-purple)" }} />
                    {item.label}
                  </Link>
                ))}
              </div>
            )}

            <Link
              href="/pricing"
              className="block px-3 py-2.5 text-sm font-medium rounded-lg"
              style={{ color: "var(--color-text-primary)" }}
            >
              Pricing
            </Link>

            <Link
              href="/services"
              className="block px-3 py-2.5 text-sm font-medium rounded-lg"
              style={{ color: "var(--color-text-primary)" }}
            >
              Services
            </Link>

            <div className="pt-3 space-y-2 px-3" style={{ borderTop: "1px solid var(--color-border)" }}>
              <Link
                href="/login"
                className="block text-center text-sm font-medium py-2 rounded-lg"
                style={{ color: "var(--color-text-primary)" }}
              >
                Log in
              </Link>
              <Link href="/signup" className="btn-primary w-full text-center text-sm">
                Get Started Free
              </Link>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
