"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getInvestorProfile, getInvestorPortfolio, getInvestorESOPSummary } from "@/lib/api";

/* eslint-disable @typescript-eslint/no-explicit-any */

export default function InvestorPortfolioPage() {
  const params = useParams();
  const router = useRouter();
  const token = params.token as string;

  const [profile, setProfile] = useState<any>(null);
  const [portfolio, setPortfolio] = useState<any[]>([]);
  const [esopSummary, setEsopSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [profileData, portfolioData] = await Promise.all([
          getInvestorProfile(token),
          getInvestorPortfolio(token),
        ]);
        setProfile(profileData);
        setPortfolio(portfolioData.portfolio || []);
        try {
          const esopData = await getInvestorESOPSummary(token);
          if (esopData.total_options > 0) setEsopSummary(esopData);
        } catch {
          // No ESOP grants
        }
      } catch {
        setError("Invalid or expired investor portal link.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [token]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div
          className="animate-spin rounded-full h-8 w-8 border-b-2"
          style={{ borderColor: "var(--color-accent-purple)" }}
        />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-20">
        <div
          className="w-14 h-14 mx-auto mb-4 rounded-2xl flex items-center justify-center"
          style={{ background: "rgba(225, 29, 72, 0.08)" }}
        >
          <svg className="w-7 h-7" style={{ color: "var(--color-accent-rose)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
        </div>
        <h2
          className="text-lg font-semibold mb-1"
          style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
        >
          Access Denied
        </h2>
        <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>{error}</p>
      </div>
    );
  }

  const totalShares = portfolio.reduce((sum: number, p: any) => sum + (Number(p.shares) || 0), 0);
  const promoterCount = portfolio.filter((p: any) => p.is_promoter).length;

  return (
    <div>
      {/* Investor header */}
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1
            className="text-2xl font-bold"
            style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
          >
            Welcome, {profile?.name as string}
          </h1>
          <p className="mt-1 text-sm" style={{ color: "var(--color-text-secondary)" }}>
            {profile?.stakeholder_type === "investor" ? "Investor" : String(profile?.stakeholder_type || "")}
            {profile?.entity_name && ` at ${profile.entity_name}`}
          </p>
        </div>
        <button
          onClick={() => router.push(`/investor/${token}/discover`)}
          className="px-4 py-2 text-white text-sm font-medium rounded-lg transition-colors"
          style={{ background: "var(--color-accent-purple)" }}
          onMouseEnter={(e) => { e.currentTarget.style.opacity = "0.9"; }}
          onMouseLeave={(e) => { e.currentTarget.style.opacity = "1"; }}
        >
          Discover Companies
        </button>
      </div>

      {/* Portfolio summary */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        {[
          { label: "Companies", value: portfolio.length, icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" },
          { label: "Total Shares", value: totalShares.toLocaleString(), icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" },
          { label: "Promoter Holdings", value: promoterCount, icon: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" },
        ].map((stat) => (
          <div
            key={stat.label}
            className="rounded-xl p-5 border"
            style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
          >
            <div className="flex items-center gap-3 mb-2">
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center"
                style={{ background: "rgba(124, 58, 237, 0.08)" }}
              >
                <svg className="w-4 h-4" style={{ color: "var(--color-accent-purple)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d={stat.icon} />
                </svg>
              </div>
              <span className="text-xs font-medium" style={{ color: "var(--color-text-muted)" }}>{stat.label}</span>
            </div>
            <p
              className="text-2xl font-bold"
              style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
            >
              {stat.value}
            </p>
          </div>
        ))}
      </div>

      {/* Company cards */}
      {portfolio.length === 0 && !esopSummary ? (
        <div
          className="rounded-xl p-12 text-center border"
          style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
        >
          <div
            className="w-14 h-14 mx-auto mb-4 rounded-2xl flex items-center justify-center"
            style={{ background: "rgba(124, 58, 237, 0.08)" }}
          >
            <svg className="w-7 h-7" style={{ color: "var(--color-accent-purple)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z" />
            </svg>
          </div>
          <p className="text-sm font-medium mb-1" style={{ color: "var(--color-text-primary)" }}>No holdings found</p>
          <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
            Your portfolio will appear here once you have shareholdings.
          </p>
        </div>
      ) : (
        <>
          {portfolio.length > 0 && (
            <>
              <h2
                className="text-sm font-semibold uppercase tracking-wider mb-3"
                style={{ color: "var(--color-text-muted)" }}
              >
                Your Companies
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {portfolio.map((holding: any) => (
                  <button
                    key={holding.shareholder_id}
                    onClick={() => router.push(`/investor/${token}/company/${holding.company_id}`)}
                    className="rounded-xl p-5 text-left transition-all border"
                    style={{
                      background: "var(--color-bg-card)",
                      borderColor: "var(--color-border)",
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.borderColor = "var(--color-accent-purple-light)"; e.currentTarget.style.boxShadow = "0 2px 8px rgba(124, 58, 237, 0.08)"; }}
                    onMouseLeave={(e) => { e.currentTarget.style.borderColor = "var(--color-border)"; e.currentTarget.style.boxShadow = "none"; }}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h3
                        className="font-semibold text-base"
                        style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
                      >
                        {holding.company_name}
                      </h3>
                      {holding.is_promoter && (
                        <span
                          className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
                          style={{ background: "rgba(5, 150, 105, 0.08)", color: "var(--color-accent-emerald)" }}
                        >
                          Promoter
                        </span>
                      )}
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-xs mb-0.5" style={{ color: "var(--color-text-muted)" }}>Shares</p>
                        <p className="font-semibold" style={{ color: "var(--color-text-primary)" }}>
                          {(holding.shares)?.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs mb-0.5" style={{ color: "var(--color-text-muted)" }}>Ownership</p>
                        <p className="font-semibold" style={{ color: "var(--color-accent-purple)" }}>
                          {(holding.percentage)?.toFixed(2)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-xs mb-0.5" style={{ color: "var(--color-text-muted)" }}>Type</p>
                        <p className="font-semibold capitalize" style={{ color: "var(--color-text-primary)" }}>
                          {holding.share_type}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </>
          )}
        </>
      )}

      {/* ESOP Summary Section */}
      {esopSummary && (
        <div className="mt-8">
          <h2
            className="text-sm font-semibold uppercase tracking-wider mb-3"
            style={{ color: "var(--color-text-muted)" }}
          >
            Stock Options (ESOP)
          </h2>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
            {[
              { label: "Total Options", value: esopSummary.total_options, color: "var(--color-text-primary)" },
              { label: "Vested", value: esopSummary.total_vested, color: "var(--color-accent-emerald)" },
              { label: "Exercisable", value: esopSummary.total_exercisable, color: "var(--color-accent-purple)" },
              { label: "Exercised", value: esopSummary.total_exercised, color: "var(--color-text-primary)" },
            ].map((stat) => (
              <div
                key={stat.label}
                className="rounded-xl p-4 border"
                style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
              >
                <p className="text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>{stat.label}</p>
                <p className="text-xl font-bold" style={{ fontFamily: "var(--font-display)", color: stat.color }}>
                  {(stat.value)?.toLocaleString()}
                </p>
              </div>
            ))}
          </div>

          {(esopSummary.companies as any[])?.map((comp: any) => (
            <div
              key={comp.company_id}
              className="rounded-xl p-5 mb-4 border"
              style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
            >
              <div className="flex items-center justify-between mb-3">
                <h3
                  className="font-semibold"
                  style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
                >
                  {comp.company_name}
                </h3>
                <button
                  onClick={() => router.push(`/investor/${token}/company/${comp.company_id}`)}
                  className="text-sm font-medium hover:underline"
                  style={{ color: "var(--color-accent-purple)" }}
                >
                  View Details
                </button>
              </div>
              <div className="grid grid-cols-3 gap-4 text-sm mb-3">
                <div>
                  <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>Options</p>
                  <p className="font-medium" style={{ color: "var(--color-text-primary)" }}>{(comp.total_options)?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>Vested</p>
                  <p className="font-medium" style={{ color: "var(--color-accent-emerald)" }}>{(comp.total_vested)?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>Exercised</p>
                  <p className="font-medium" style={{ color: "var(--color-text-primary)" }}>{(comp.total_exercised)?.toLocaleString()}</p>
                </div>
              </div>
              <div className="space-y-2">
                {(comp.grants as any[])?.map((g: any) => (
                  <div
                    key={g.id}
                    className="flex items-center justify-between p-2.5 rounded-lg text-sm"
                    style={{ background: "var(--color-bg-secondary)" }}
                  >
                    <div>
                      <span className="font-medium" style={{ color: "var(--color-text-primary)" }}>{g.plan_name || "Grant"}</span>
                      <span className="ml-2" style={{ color: "var(--color-text-muted)" }}>
                        {g.number_of_options?.toLocaleString()} options @ Rs {g.exercise_price}
                      </span>
                    </div>
                    <span
                      className="text-[10px] px-2 py-0.5 rounded-full font-semibold capitalize"
                      style={{
                        background: (g.status === "active" || g.status === "partially_exercised")
                          ? "rgba(5, 150, 105, 0.08)"
                          : g.status === "fully_exercised"
                          ? "rgba(124, 58, 237, 0.08)"
                          : "rgba(100, 116, 139, 0.08)",
                        color: (g.status === "active" || g.status === "partially_exercised")
                          ? "var(--color-accent-emerald)"
                          : g.status === "fully_exercised"
                          ? "var(--color-accent-purple)"
                          : "var(--color-text-muted)",
                      }}
                    >
                      {g.status?.replace(/_/g, " ")}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
