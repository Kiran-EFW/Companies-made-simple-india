"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { CompanyProvider, useCompany } from "@/lib/company-context";
import { apiCall } from "@/lib/api";

// ---------------------------------------------------------------------------
// Sidebar navigation structure — grouped with role visibility
// ---------------------------------------------------------------------------

interface NavItem {
  href: string;
  label: string;
  icon: string;
  roles?: readonly string[]; // undefined = all roles
}

interface NavGroup {
  label: string;
  items: NavItem[];
  roles?: readonly string[]; // undefined = all roles
}

import { FOUNDER_ROLES } from "@/lib/roles";

const NAV_GROUPS: NavGroup[] = [
  {
    label: "",
    items: [
      {
        href: "/dashboard",
        label: "Overview",
        icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0a1 1 0 01-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1",
      },
    ],
  },
  {
    label: "Equity",
    roles: FOUNDER_ROLES,
    items: [
      {
        href: "/dashboard/cap-table",
        label: "Cap Table",
        icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
      },
      {
        href: "/dashboard/esop",
        label: "ESOP",
        icon: "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z",
      },
      {
        href: "/dashboard/stakeholders",
        label: "Stakeholders",
        icon: "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z",
      },
    ],
  },
  {
    label: "Fundraising",
    roles: FOUNDER_ROLES,
    items: [
      {
        href: "/dashboard/fundraising",
        label: "Rounds",
        icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
      },
      {
        href: "/dashboard/valuations",
        label: "Valuations",
        icon: "M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z",
      },
    ],
  },
  {
    label: "Compliance",
    items: [
      {
        href: "/dashboard/compliance",
        label: "Calendar",
        icon: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z",
      },
      {
        href: "/dashboard/meetings",
        label: "Meetings",
        icon: "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z",
      },
      {
        href: "/dashboard/registers",
        label: "Registers",
        icon: "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253",
      },
    ],
  },
  {
    label: "Documents",
    items: [
      {
        href: "/dashboard/documents",
        label: "Legal Docs",
        icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
      },
      {
        href: "/dashboard/signatures",
        label: "E-Signatures",
        icon: "M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z",
      },
      {
        href: "/dashboard/data-room",
        label: "Data Room",
        icon: "M5 19a2 2 0 01-2-2V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1M5 19h14a2 2 0 002-2v-5a2 2 0 00-2-2H9a2 2 0 00-2 2v5a2 2 0 01-2 2z",
      },
    ],
  },
  {
    label: "Finance",
    items: [
      {
        href: "/dashboard/gst",
        label: "GST",
        icon: "M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2z",
      },
      {
        href: "/dashboard/tax",
        label: "Tax",
        icon: "M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z",
      },
      {
        href: "/dashboard/accounting",
        label: "Accounting",
        icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4",
        roles: FOUNDER_ROLES,
      },
    ],
  },
  {
    label: "Services",
    roles: FOUNDER_ROLES,
    items: [
      {
        href: "/dashboard/services",
        label: "Marketplace",
        icon: "M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z",
      },
      {
        href: "/dashboard/billing",
        label: "Billing",
        icon: "M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z",
      },
    ],
  },
];

// ---------------------------------------------------------------------------
// Company Selector Component
// ---------------------------------------------------------------------------

function CompanySelector() {
  const { companies, selectedCompany, selectCompany } = useCompany();
  const [open, setOpen] = useState(false);

  if (companies.length === 0) return null;

  const displayName =
    selectedCompany?.approved_name ||
    selectedCompany?.proposed_names?.[0] ||
    "Select Company";

  if (companies.length === 1) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium" style={{ color: "var(--color-text-primary)" }}>
        <div className="w-2 h-2 rounded-full bg-emerald-500" />
        <span className="truncate max-w-[200px]">{displayName}</span>
      </div>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors hover:bg-gray-100"
        style={{ color: "var(--color-text-primary)" }}
      >
        <div className="w-2 h-2 rounded-full bg-emerald-500" />
        <span className="truncate max-w-[200px]">{displayName}</span>
        <svg className="w-4 h-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-30" onClick={() => setOpen(false)} />
          <div
            className="absolute left-0 top-full mt-1 w-72 rounded-xl shadow-lg z-40 py-1 border"
            style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
          >
            {companies.map((c) => {
              const name = c.approved_name || c.proposed_names?.[0] || `Company #${c.id}`;
              const isSelected = c.id === selectedCompany?.id;
              return (
                <button
                  key={c.id}
                  onClick={() => { selectCompany(c.id); setOpen(false); }}
                  className="w-full text-left px-4 py-2.5 flex items-center gap-3 transition-colors hover:bg-gray-50"
                  style={{ background: isSelected ? "rgba(139, 92, 246, 0.06)" : "transparent" }}
                >
                  <div className={`w-2 h-2 rounded-full ${isSelected ? "bg-purple-500" : "bg-gray-300"}`} />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium truncate" style={{ color: "var(--color-text-primary)" }}>{name}</div>
                    <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                      {c.entity_type.replace(/_/g, " ")} &middot; {c.status.replace(/_/g, " ")}
                    </div>
                  </div>
                </button>
              );
            })}
            <div className="border-t mt-1 pt-1" style={{ borderColor: "var(--color-border)" }}>
              <Link
                href="/onboarding"
                onClick={() => setOpen(false)}
                className="w-full text-left px-4 py-2 flex items-center gap-3 text-sm transition-colors hover:bg-gray-50"
                style={{ color: "rgb(139, 92, 246)" }}
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                </svg>
                Add Company
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Right Sidebar — contextual info panel
// ---------------------------------------------------------------------------

function RightSidebar() {
  const { selectedCompany } = useCompany();
  const [activity, setActivity] = useState<any[]>([]);
  const [deadlines, setDeadlines] = useState<any[]>([]);

  const fetchContext = useCallback(async () => {
    if (!selectedCompany) return;
    try {
      const [logs, tasks] = await Promise.allSettled([
        apiCall(`/companies/${selectedCompany.id}/logs`),
        apiCall(`/companies/${selectedCompany.id}/tasks`),
      ]);
      if (logs.status === "fulfilled") {
        setActivity(
          (Array.isArray(logs.value) ? logs.value : []).slice(0, 8)
        );
      }
      if (tasks.status === "fulfilled") {
        const upcoming = (Array.isArray(tasks.value) ? tasks.value : [])
          .filter((t: any) => t.status !== "completed" && t.due_date)
          .sort(
            (a: any, b: any) =>
              new Date(a.due_date).getTime() - new Date(b.due_date).getTime()
          )
          .slice(0, 5);
        setDeadlines(upcoming);
      }
    } catch {
      // silently fail — sidebar is supplementary
    }
  }, [selectedCompany]);

  useEffect(() => {
    fetchContext();
  }, [fetchContext]);

  const timeAgo = (iso: string) => {
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return "just now";
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    return `${days}d ago`;
  };

  const formatDate = (iso: string) =>
    new Date(iso).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
    });

  if (!selectedCompany) {
    return (
      <div className="p-5">
        <div className="text-center py-8">
          <svg className="w-8 h-8 mx-auto mb-2 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21m-3.75 3H21m-3.75 3H21" />
          </svg>
          <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
            No company selected
          </p>
        </div>
      </div>
    );
  }

  const statusLabel = selectedCompany.status?.replace(/_/g, " ") || "unknown";

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      {/* Company quick info */}
      <div className="px-4 py-4 border-b" style={{ borderColor: "var(--color-border)" }}>
        <div className="text-[10px] font-semibold uppercase tracking-wider mb-2" style={{ color: "var(--color-text-muted)" }}>
          Company
        </div>
        <div className="text-sm font-semibold mb-1" style={{ color: "var(--color-text-primary)" }}>
          {selectedCompany.approved_name || selectedCompany.proposed_names?.[0] || "Unnamed"}
        </div>
        <div className="flex items-center gap-2 text-[11px]" style={{ color: "var(--color-text-secondary)" }}>
          <span
            className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium capitalize"
            style={{ background: "rgba(139,92,246,0.08)", color: "rgb(139,92,246)" }}
          >
            {statusLabel}
          </span>
          <span>{selectedCompany.entity_type?.replace(/_/g, " ")}</span>
        </div>
        {selectedCompany.cin && (
          <div className="mt-1.5 text-[10px] font-mono" style={{ color: "var(--color-text-muted)" }}>
            CIN: {selectedCompany.cin}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="px-4 py-3 border-b" style={{ borderColor: "var(--color-border)" }}>
        <div className="text-[10px] font-semibold uppercase tracking-wider mb-2" style={{ color: "var(--color-text-muted)" }}>
          Quick Actions
        </div>
        <div className="flex flex-col gap-1">
          <Link
            href="/dashboard/documents"
            className="flex items-center gap-2 px-2 py-1.5 rounded text-xs transition-colors hover:bg-gray-50"
            style={{ color: "var(--color-text-secondary)" }}
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            Create Document
          </Link>
          <Link
            href="/dashboard/compliance"
            className="flex items-center gap-2 px-2 py-1.5 rounded text-xs transition-colors hover:bg-gray-50"
            style={{ color: "var(--color-text-secondary)" }}
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
            </svg>
            View Compliance
          </Link>
          <Link
            href="/dashboard/services"
            className="flex items-center gap-2 px-2 py-1.5 rounded text-xs transition-colors hover:bg-gray-50"
            style={{ color: "var(--color-text-secondary)" }}
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 21v-7.5a.75.75 0 01.75-.75h3a.75.75 0 01.75.75V21m-4.5 0H2.36m11.14 0H18m0 0h3.64m-1.39 0V9.349m-16.5 11.65V9.35m0 0a3.001 3.001 0 003.75-.615A2.993 2.993 0 009.75 9.75c.896 0 1.7-.393 2.25-1.016a2.993 2.993 0 002.25 1.016c.896 0 1.7-.393 2.25-1.016a3.001 3.001 0 003.75.614m-16.5 0a3.004 3.004 0 01-.621-4.72L4.318 3.44A1.5 1.5 0 015.378 3h13.243a1.5 1.5 0 011.06.44l1.19 1.189a3 3 0 01-.621 4.72m-13.5 8.65h3.75a.75.75 0 00.75-.75V13.5a.75.75 0 00-.75-.75H6.75a.75.75 0 00-.75.75v3.15c0 .415.336.75.75.75z" />
            </svg>
            Browse Services
          </Link>
        </div>
      </div>

      {/* Upcoming Deadlines */}
      <div className="px-4 py-3 border-b" style={{ borderColor: "var(--color-border)" }}>
        <div className="text-[10px] font-semibold uppercase tracking-wider mb-2" style={{ color: "var(--color-text-muted)" }}>
          Upcoming Deadlines
        </div>
        {deadlines.length === 0 ? (
          <p className="text-[11px] py-2" style={{ color: "var(--color-text-muted)" }}>
            No upcoming deadlines
          </p>
        ) : (
          <div className="flex flex-col gap-2">
            {deadlines.map((task: any, i: number) => (
              <div key={i} className="flex items-start gap-2">
                <div className="w-1 h-1 rounded-full mt-1.5 flex-shrink-0" style={{ background: "rgb(139,92,246)" }} />
                <div className="flex-1 min-w-0">
                  <div className="text-[11px] font-medium truncate" style={{ color: "var(--color-text-primary)" }}>
                    {task.title || task.task_type?.replace(/_/g, " ")}
                  </div>
                  <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                    Due {formatDate(task.due_date)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recent Activity */}
      <div className="px-4 py-3 flex-1">
        <div className="text-[10px] font-semibold uppercase tracking-wider mb-2" style={{ color: "var(--color-text-muted)" }}>
          Recent Activity
        </div>
        {activity.length === 0 ? (
          <p className="text-[11px] py-2" style={{ color: "var(--color-text-muted)" }}>
            No recent activity
          </p>
        ) : (
          <div className="flex flex-col gap-2.5">
            {activity.map((log: any, i: number) => (
              <div key={i} className="flex items-start gap-2">
                <div className="w-1 h-1 rounded-full mt-1.5 flex-shrink-0 bg-gray-300" />
                <div className="flex-1 min-w-0">
                  <div className="text-[11px] leading-snug" style={{ color: "var(--color-text-secondary)" }}>
                    {log.action || log.message || log.event_type}
                  </div>
                  <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                    {log.created_at ? timeAgo(log.created_at) : ""}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Inner Layout (needs CompanyProvider to be above it)
// ---------------------------------------------------------------------------

function DashboardInner({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  const userRole = user?.role || "user";

  const isActive = (href: string) =>
    href === "/dashboard"
      ? pathname === "/dashboard"
      : pathname.startsWith(href);

  // Filter nav groups by role
  const visibleGroups = NAV_GROUPS.filter((group) => {
    if (!group.roles) return true;
    return group.roles.includes(userRole);
  }).map((group) => ({
    ...group,
    items: group.items.filter((item) => {
      if (!item.roles) return true;
      return item.roles.includes(userRole);
    }),
  }));

  return (
    <div className="min-h-screen" style={{ background: "var(--color-bg-secondary)" }}>
      {/* ── Top Header Bar ────────────────────────────────────────── */}
      <header
        className="fixed top-0 left-0 right-0 z-50 h-14 flex items-center justify-between px-4 lg:px-6"
        style={{ background: "var(--color-bg-card)", borderBottom: "1px solid var(--color-border)" }}
      >
        {/* Left: Logo + Company Selector */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden p-1.5 rounded-lg hover:bg-gray-100"
            style={{ color: "var(--color-text-secondary)" }}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <Link href="/" className="flex items-center gap-2">
            <img src="/logo-icon.png" alt="Anvils" className="w-6 h-6 object-contain" />
            <span
              className="text-lg font-bold hidden sm:block"
              style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
            >
              Anvils
            </span>
          </Link>

          <div className="hidden sm:block h-5 w-px bg-gray-200" />
          <div className="hidden sm:block">
            <CompanySelector />
          </div>
        </div>

        {/* Right: Notifications + Profile */}
        <div className="flex items-center gap-2">
          <Link
            href="/dashboard/notifications"
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors relative"
            style={{ color: "var(--color-text-secondary)" }}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
            </svg>
          </Link>

          <div className="relative">
            <button
              onClick={() => setProfileOpen(!profileOpen)}
              className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div
                className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-white"
                style={{ background: "rgb(139, 92, 246)" }}
              >
                {user?.full_name?.charAt(0).toUpperCase() || "U"}
              </div>
              <span className="text-sm font-medium hidden md:block" style={{ color: "var(--color-text-primary)" }}>
                {user?.full_name}
              </span>
            </button>

            {profileOpen && (
              <>
                <div className="fixed inset-0 z-30" onClick={() => setProfileOpen(false)} />
                <div
                  className="absolute right-0 top-full mt-1 w-56 rounded-xl shadow-lg z-40 py-1 border"
                  style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
                >
                  <div className="px-4 py-3 border-b" style={{ borderColor: "var(--color-border)" }}>
                    <div className="text-sm font-medium" style={{ color: "var(--color-text-primary)" }}>{user?.full_name}</div>
                    <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>{user?.email}</div>
                  </div>
                  <Link
                    href="/dashboard/profile"
                    onClick={() => setProfileOpen(false)}
                    className="block px-4 py-2 text-sm hover:bg-gray-50 transition-colors"
                    style={{ color: "var(--color-text-secondary)" }}
                  >
                    Profile & Settings
                  </Link>
                  <Link
                    href="/dashboard/notifications"
                    onClick={() => setProfileOpen(false)}
                    className="block px-4 py-2 text-sm hover:bg-gray-50 transition-colors"
                    style={{ color: "var(--color-text-secondary)" }}
                  >
                    Notifications
                  </Link>
                  <div className="border-t" style={{ borderColor: "var(--color-border)" }}>
                    <button
                      onClick={() => { setProfileOpen(false); logout(); }}
                      className="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition-colors"
                      style={{ color: "var(--color-text-secondary)" }}
                    >
                      Log Out
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </header>

      {/* ── Mobile Overlay ────────────────────────────────────────── */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 lg:hidden"
          style={{ background: "rgba(0,0,0,0.3)" }}
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* ── Sidebar ───────────────────────────────────────────────── */}
      <aside
        className={`fixed top-14 left-0 z-40 h-[calc(100vh-3.5rem)] w-56 transition-transform duration-200 lg:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
        style={{ background: "var(--color-bg-card)", borderRight: "1px solid var(--color-border)" }}
      >
        <div className="flex flex-col h-full">
          {/* Mobile company selector */}
          <div className="sm:hidden px-3 pt-3">
            <CompanySelector />
          </div>

          {/* Nav groups */}
          <nav className="flex-1 overflow-y-auto py-3 px-3">
            {visibleGroups.map((group, gIdx) => (
              <div key={gIdx} className={gIdx > 0 ? "mt-5" : ""}>
                {group.label && (
                  <div
                    className="px-3 mb-1 text-[10px] font-semibold uppercase tracking-wider"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    {group.label}
                  </div>
                )}
                {group.items.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setSidebarOpen(false)}
                    className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm mb-0.5 transition-colors"
                    style={{
                      background: isActive(item.href)
                        ? "rgba(139, 92, 246, 0.08)"
                        : "transparent",
                      color: isActive(item.href)
                        ? "rgb(139, 92, 246)"
                        : "var(--color-text-secondary)",
                      fontWeight: isActive(item.href) ? 600 : 400,
                    }}
                  >
                    <svg
                      className="w-4 h-4 flex-shrink-0"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={1.5}
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
                    </svg>
                    {item.label}
                  </Link>
                ))}
              </div>
            ))}
          </nav>

          {/* Bottom help link */}
          <div className="px-3 py-3 border-t" style={{ borderColor: "var(--color-border)" }}>
            <Link
              href="/learn"
              className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors hover:bg-gray-50"
              style={{ color: "var(--color-text-muted)" }}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
              </svg>
              Help & Learning
            </Link>
          </div>
        </div>
      </aside>

      {/* ── Main Content + Right Sidebar ─────────────────────────── */}
      <div className="lg:pl-56 pt-14 min-h-screen flex">
        <main className="flex-1 min-w-0">
          {children}
        </main>

        {/* ── Right Sidebar (xl+ only) ───────────────────────────── */}
        <aside
          className="hidden xl:block w-64 flex-shrink-0 h-[calc(100vh-3.5rem)] sticky top-14"
          style={{ background: "var(--color-bg-card)", borderLeft: "1px solid var(--color-border)" }}
        >
          <RightSidebar />
        </aside>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Exported Layout
// ---------------------------------------------------------------------------

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    if (!user) {
      router.push("/login");
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: "var(--color-bg-secondary)" }}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: "rgb(139, 92, 246)" }} />
      </div>
    );
  }

  if (!user) return null;

  return (
    <CompanyProvider>
      <DashboardInner>{children}</DashboardInner>
    </CompanyProvider>
  );
}
