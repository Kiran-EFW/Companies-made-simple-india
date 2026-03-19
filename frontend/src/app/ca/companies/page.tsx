"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { getCaCompanies } from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface CaCompany {
  id: number;
  name: string;
  entity_type: string;
  cin: string;
  status: string;
  pending_tasks: number;
}

// ---------------------------------------------------------------------------
// Theme
// ---------------------------------------------------------------------------
const T = {
  accent: "#0d9488",
  accentBg: "rgba(20, 184, 166, 0.08)",
  textPrimary: "#0f172a",
  textSecondary: "#475569",
  textMuted: "#94a3b8",
  cardBg: "#ffffff",
  cardBorder: "#e2e8f0",
  rose: "#dc2626",
  roseBg: "rgba(220, 38, 38, 0.06)",
  emerald: "#059669",
  emeraldBg: "rgba(5, 150, 105, 0.06)",
};

function formatEntityType(raw: string): string {
  return raw.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CaCompaniesPage() {
  const { user, loading: authLoading } = useAuth();
  const [companies, setCompanies] = useState<CaCompany[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (authLoading || !user) return;

    (async () => {
      try {
        const data = await getCaCompanies();
        setCompanies(data);
      } catch (err: any) {
        setError(err.message || "Failed to load companies");
      } finally {
        setLoading(false);
      }
    })();
  }, [user, authLoading]);

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: T.accent }} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-10">
        <div className="rounded-xl p-6 text-center text-sm" style={{ background: T.roseBg, color: T.rose, border: `1px solid rgba(220,38,38,0.15)` }}>
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 lg:py-10">
      {/* ── Header ──────────────────────────────────────────── */}
      <div className="mb-6">
        <h1
          className="text-2xl font-bold mb-1"
          style={{ fontFamily: "var(--font-display)", color: T.textPrimary }}
        >
          Assigned Companies
        </h1>
        <p className="text-sm" style={{ color: T.textSecondary }}>
          {companies.length} {companies.length === 1 ? "company" : "companies"} assigned to you for compliance management.
        </p>
      </div>

      {/* ── Empty State ─────────────────────────────────────── */}
      {companies.length === 0 ? (
        <div
          className="rounded-xl p-12 text-center"
          style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}` }}
        >
          <svg
            className="w-12 h-12 mx-auto mb-4"
            style={{ color: T.textMuted }}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21m-3.75 3H21m-3.75 3H21" />
          </svg>
          <p className="text-base font-medium mb-1" style={{ color: T.textPrimary }}>
            No companies assigned yet
          </p>
          <p className="text-sm" style={{ color: T.textMuted }}>
            Contact your administrator to get started.
          </p>
        </div>
      ) : (
        /* ── Companies Table ─────────────────────────────── */
        <div
          className="rounded-xl overflow-hidden"
          style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}` }}
        >
          {/* Table header */}
          <div
            className="grid grid-cols-[1fr_140px_100px_120px] gap-4 px-5 py-3 text-xs font-semibold uppercase tracking-wider"
            style={{ color: T.textMuted, borderBottom: `1px solid ${T.cardBorder}`, background: "#f8fafc" }}
          >
            <div>Company</div>
            <div>Entity Type</div>
            <div>Status</div>
            <div className="text-right">Tasks</div>
          </div>

          {/* Rows */}
          {companies.map((company, idx) => (
            <Link
              key={company.id}
              href={`/ca/companies/${company.id}`}
              className="grid grid-cols-[1fr_140px_100px_120px] gap-4 px-5 py-4 items-center transition-colors"
              style={{
                borderBottom: idx < companies.length - 1 ? `1px solid ${T.cardBorder}` : undefined,
                color: T.textPrimary,
              }}
              onMouseEnter={(e) => { e.currentTarget.style.background = "#f8fafc"; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}
            >
              {/* Company name + CIN */}
              <div className="min-w-0">
                <div className="text-sm font-semibold truncate" style={{ color: T.textPrimary }}>
                  {company.name}
                </div>
                {company.cin && (
                  <div className="text-[11px] font-mono truncate mt-0.5" style={{ color: T.textMuted }}>
                    {company.cin}
                  </div>
                )}
              </div>

              {/* Entity type */}
              <div className="text-xs" style={{ color: T.textSecondary }}>
                {formatEntityType(company.entity_type)}
              </div>

              {/* Status */}
              <div>
                <span
                  className="inline-flex text-[11px] font-medium px-2 py-0.5 rounded-full capitalize"
                  style={{ background: T.accentBg, color: T.accent }}
                >
                  {company.status.replace(/_/g, " ")}
                </span>
              </div>

              {/* Pending tasks */}
              <div className="text-right">
                {company.pending_tasks > 0 ? (
                  <span
                    className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full"
                    style={{ background: T.roseBg, color: T.rose }}
                  >
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126z" />
                    </svg>
                    {company.pending_tasks} pending
                  </span>
                ) : (
                  <span
                    className="inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full"
                    style={{ background: T.emeraldBg, color: T.emerald }}
                  >
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    All clear
                  </span>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
