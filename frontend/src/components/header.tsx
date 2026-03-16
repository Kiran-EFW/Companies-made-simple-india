"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
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
  ShoppingBag,
  Compass,
  GitCompare,
  GraduationCap,
  Table2,
  Menu,
  X,
  ChevronDown,
} from "lucide-react";

const PRODUCTS = [
  {
    heading: "Equity & Governance",
    items: [
      { label: "Cap Table", desc: "Shareholders, dilution, certificates", href: "/features/cap-table", icon: BarChart3 },
      { label: "ESOP", desc: "Plans, grants, vesting & exercise", href: "/features/esop", icon: Users },
      { label: "Fundraising", desc: "Rounds, closing room, filings", href: "/features/fundraising", icon: TrendingUp },
      { label: "Valuations", desc: "NAV & DCF for Rule 11UA FMV", href: "/dashboard/valuations", icon: Calculator },
      { label: "Stakeholders", desc: "Investor & employee profiles", href: "/dashboard/stakeholders", icon: Briefcase },
    ],
  },
  {
    heading: "Compliance & Operations",
    items: [
      { label: "Compliance Calendar", desc: "ROC, board meetings, GST deadlines", href: "/features/compliance", icon: Shield },
      { label: "Board Meetings", desc: "Scheduling, minutes, resolutions", href: "/dashboard/meetings", icon: Calendar },
      { label: "Legal Documents", desc: "AI-drafted contracts & e-signatures", href: "/documents", icon: FileText },
      { label: "Data Room", desc: "Secure document sharing", href: "/dashboard/data-room", icon: FolderLock },
      { label: "GST & Tax", desc: "Returns, TDS, tax overview", href: "/dashboard/gst", icon: Receipt },
      { label: "Accounting", desc: "Zoho Books & Tally integration", href: "/settings/accounting", icon: BookOpen },
    ],
  },
  {
    heading: "Portals",
    items: [
      { label: "Investor Portal", desc: "Token-based portfolio dashboard", href: "/for/investors", icon: Eye },
      { label: "CA Dashboard", desc: "Multi-client compliance view", href: "/for/cas", icon: Briefcase },
      { label: "Incorporation", desc: "AI entity wizard & filing", href: "/wizard", icon: Rocket },
      { label: "Services Marketplace", desc: "GST, trademark, DPIIT & more", href: "/services", icon: ShoppingBag },
    ],
  },
];

const SOLUTIONS = [
  { label: "For Founders", desc: "Cap table, ESOP, fundraising, compliance", href: "/for/founders", icon: Rocket },
  { label: "For Investors", desc: "Portfolio dashboard & company discovery", href: "/for/investors", icon: Eye },
  { label: "For CAs & CSs", desc: "Multi-client compliance management", href: "/for/cas", icon: Briefcase },
];

const RESOURCES = [
  { label: "Entity Wizard", desc: "Find the right entity type", href: "/wizard", icon: Compass },
  { label: "Compare Entities", desc: "Side-by-side comparison", href: "/compare", icon: GitCompare },
  { label: "Learning Center", desc: "Guides & best practices", href: "/learn", icon: GraduationCap },
  { label: "Free Cap Table Tool", desc: "Build your cap table instantly", href: "/cap-table-setup", icon: Table2 },
];

type DropdownKey = "products" | "solutions" | "resources" | null;

export default function Header() {
  const [openDropdown, setOpenDropdown] = useState<DropdownKey>(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [mobileSection, setMobileSection] = useState<string | null>(null);
  const pathname = usePathname();
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const navRef = useRef<HTMLDivElement>(null);

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
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-6" ref={navRef}>
        <nav className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 shrink-0">
            <img src="/logo-icon.png" alt="Anvils" className="w-7 h-7 object-contain" />
            <span className="text-lg font-bold text-gray-900" style={{ fontFamily: "var(--font-display)" }}>
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
                className="flex items-center gap-1 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Products
                <ChevronDown className={`w-3.5 h-3.5 transition-transform ${openDropdown === "products" ? "rotate-180" : ""}`} />
              </button>
              {openDropdown === "products" && (
                <div
                  className="absolute top-full left-1/2 -translate-x-1/2 mt-1 w-[780px] bg-white rounded-xl border border-gray-200 shadow-lg p-6"
                  onMouseEnter={() => handleMouseEnter("products")}
                  onMouseLeave={handleMouseLeave}
                >
                  <div className="grid grid-cols-3 gap-6">
                    {PRODUCTS.map((group) => (
                      <div key={group.heading}>
                        <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                          {group.heading}
                        </div>
                        <div className="space-y-1">
                          {group.items.map((item) => (
                            <Link
                              key={item.href}
                              href={item.href}
                              className="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors group"
                            >
                              <item.icon className="w-4 h-4 text-purple-600 mt-0.5 shrink-0" />
                              <div>
                                <div className="text-sm font-medium text-gray-900 group-hover:text-purple-700">{item.label}</div>
                                <div className="text-xs text-gray-500">{item.desc}</div>
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
                className="flex items-center gap-1 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Solutions
                <ChevronDown className={`w-3.5 h-3.5 transition-transform ${openDropdown === "solutions" ? "rotate-180" : ""}`} />
              </button>
              {openDropdown === "solutions" && (
                <div
                  className="absolute top-full left-1/2 -translate-x-1/2 mt-1 w-[320px] bg-white rounded-xl border border-gray-200 shadow-lg p-3"
                  onMouseEnter={() => handleMouseEnter("solutions")}
                  onMouseLeave={handleMouseLeave}
                >
                  {SOLUTIONS.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors group"
                    >
                      <item.icon className="w-4 h-4 text-purple-600 mt-0.5 shrink-0" />
                      <div>
                        <div className="text-sm font-medium text-gray-900 group-hover:text-purple-700">{item.label}</div>
                        <div className="text-xs text-gray-500">{item.desc}</div>
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
                className="flex items-center gap-1 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Resources
                <ChevronDown className={`w-3.5 h-3.5 transition-transform ${openDropdown === "resources" ? "rotate-180" : ""}`} />
              </button>
              {openDropdown === "resources" && (
                <div
                  className="absolute top-full left-1/2 -translate-x-1/2 mt-1 w-[320px] bg-white rounded-xl border border-gray-200 shadow-lg p-3"
                  onMouseEnter={() => handleMouseEnter("resources")}
                  onMouseLeave={handleMouseLeave}
                >
                  {RESOURCES.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors group"
                    >
                      <item.icon className="w-4 h-4 text-purple-600 mt-0.5 shrink-0" />
                      <div>
                        <div className="text-sm font-medium text-gray-900 group-hover:text-purple-700">{item.label}</div>
                        <div className="text-xs text-gray-500">{item.desc}</div>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </div>

            {/* Pricing direct link */}
            <Link
              href="/pricing"
              className="px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Pricing
            </Link>
          </div>

          {/* Right side */}
          <div className="hidden lg:flex items-center gap-3">
            <Link href="/login" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">
              Log in
            </Link>
            <Link href="/signup" className="btn-primary btn-sm">
              Get Started Free
            </Link>
          </div>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="lg:hidden p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-50"
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </nav>

        {/* Mobile Menu */}
        {mobileOpen && (
          <div className="lg:hidden border-t border-gray-100 py-4 space-y-1 max-h-[80vh] overflow-y-auto">
            {/* Products accordion */}
            <button
              onClick={() => setMobileSection(mobileSection === "products" ? null : "products")}
              className="flex items-center justify-between w-full px-3 py-2.5 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Products
              <ChevronDown className={`w-4 h-4 transition-transform ${mobileSection === "products" ? "rotate-180" : ""}`} />
            </button>
            {mobileSection === "products" && (
              <div className="pl-4 space-y-3 py-2">
                {PRODUCTS.map((group) => (
                  <div key={group.heading}>
                    <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 mb-1">{group.heading}</div>
                    {group.items.map((item) => (
                      <Link
                        key={item.href}
                        href={item.href}
                        className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 rounded-lg hover:bg-gray-50"
                      >
                        <item.icon className="w-4 h-4 text-purple-600 shrink-0" />
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
              className="flex items-center justify-between w-full px-3 py-2.5 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-50"
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
                    className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    <item.icon className="w-4 h-4 text-purple-600 shrink-0" />
                    {item.label}
                  </Link>
                ))}
              </div>
            )}

            {/* Resources accordion */}
            <button
              onClick={() => setMobileSection(mobileSection === "resources" ? null : "resources")}
              className="flex items-center justify-between w-full px-3 py-2.5 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-50"
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
                    className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    <item.icon className="w-4 h-4 text-purple-600 shrink-0" />
                    {item.label}
                  </Link>
                ))}
              </div>
            )}

            <Link href="/pricing" className="block px-3 py-2.5 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-50">
              Pricing
            </Link>

            <div className="pt-3 border-t border-gray-100 space-y-2 px-3">
              <Link href="/login" className="block text-center text-sm font-medium text-gray-700 py-2 rounded-lg hover:bg-gray-50">
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
