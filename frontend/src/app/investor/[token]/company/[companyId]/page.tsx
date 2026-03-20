"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  getInvestorCompanyDetail,
  getInvestorCapTable,
  getInvestorFundingRounds,
  getInvestorESOPGrants,
  getInvestorDocuments,
  getInvestorPitchDeckUrl,
} from "@/lib/api";

type Tab = "holdings" | "cap-table" | "rounds" | "esop" | "documents";

/* eslint-disable @typescript-eslint/no-explicit-any */

export default function InvestorCompanyDetailPage() {
  const params = useParams();
  const router = useRouter();
  const token = params.token as string;
  const companyId = Number(params.companyId);

  const [activeTab, setActiveTab] = useState<Tab>("holdings");
  const [detail, setDetail] = useState<any>(null);
  const [capTable, setCapTable] = useState<any[]>([]);
  const [rounds, setRounds] = useState<any[]>([]);
  const [esopGrants, setEsopGrants] = useState<any[]>([]);
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [detailData, capData, roundsData, esopData, docsData] = await Promise.all([
          getInvestorCompanyDetail(token, companyId),
          getInvestorCapTable(token, companyId),
          getInvestorFundingRounds(token, companyId),
          getInvestorESOPGrants(token, companyId),
          getInvestorDocuments(token, companyId),
        ]);
        setDetail(detailData);
        setCapTable(capData.cap_table || []);
        setRounds(roundsData.funding_rounds || []);
        setEsopGrants(esopData.esop_grants || []);
        setDocuments(docsData.documents || []);
      } catch {
        setError("Unable to load company details.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [token, companyId]);

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
        <p style={{ color: "var(--color-text-secondary)" }}>{error}</p>
        <button
          onClick={() => router.push(`/investor/${token}`)}
          className="mt-4 text-sm font-medium hover:underline"
          style={{ color: "var(--color-accent-purple)" }}
        >
          Back to Portfolio
        </button>
      </div>
    );
  }

  const company = detail?.company;
  const holdings = detail?.holdings;
  const tabs: { key: Tab; label: string; count?: number }[] = [
    { key: "holdings", label: "Holdings" },
    { key: "cap-table", label: "Cap Table", count: capTable.length },
    { key: "rounds", label: "Funding Rounds", count: rounds.length },
    { key: "esop", label: "ESOP", count: esopGrants.length },
    { key: "documents", label: "Documents", count: documents.length },
  ];

  return (
    <div>
      {/* Back link */}
      <button
        onClick={() => router.push(`/investor/${token}`)}
        className="text-sm font-medium hover:underline mb-5 inline-flex items-center gap-1"
        style={{ color: "var(--color-accent-purple)" }}
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
        </svg>
        Back to Portfolio
      </button>

      {/* Company header */}
      <div className="mb-6">
        <h1
          className="text-2xl font-bold"
          style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
        >
          {company?.name}
        </h1>
        {company?.tagline && (
          <p className="mt-1 text-sm" style={{ color: "var(--color-text-secondary)" }}>{company.tagline}</p>
        )}
        <div className="flex flex-wrap gap-2 mt-3">
          {company?.entity_type && (
            <span
              className="text-[10px] font-semibold px-2.5 py-1 rounded-full capitalize"
              style={{ background: "rgba(124, 58, 237, 0.08)", color: "var(--color-accent-purple)" }}
            >
              {company.entity_type.replace("_", " ")}
            </span>
          )}
          {company?.sector && (
            <span
              className="text-[10px] font-semibold px-2.5 py-1 rounded-full"
              style={{ background: "rgba(124, 58, 237, 0.08)", color: "var(--color-accent-purple)" }}
            >
              {company.sector}
            </span>
          )}
          {company?.cin && (
            <span className="text-xs" style={{ color: "var(--color-text-muted)" }}>CIN: {company.cin}</span>
          )}
          {company?.status && (
            <span
              className="text-[10px] font-semibold px-2.5 py-1 rounded-full capitalize"
              style={{ background: "rgba(37, 99, 235, 0.08)", color: "var(--color-accent-blue)" }}
            >
              {company.status.replace("_", " ")}
            </span>
          )}
          {company?.website && (
            <a
              href={company.website}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-medium hover:underline"
              style={{ color: "var(--color-accent-purple)" }}
            >
              Website
            </a>
          )}
        </div>
      </div>

      {/* Pitch deck viewer + description */}
      {(company?.has_pitch_deck || company?.description) && (
        <div className="mb-6 grid grid-cols-1 lg:grid-cols-2 gap-4">
          {company?.has_pitch_deck && (
            <div
              className="rounded-xl overflow-hidden border"
              style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
            >
              <div className="relative w-full" style={{ paddingBottom: "75%" }}>
                <iframe
                  className="absolute inset-0 w-full h-full"
                  src={getInvestorPitchDeckUrl(token, companyId)}
                  title="Pitch Deck"
                />
              </div>
              <div
                className="p-3 border-t flex items-center justify-between"
                style={{ borderColor: "var(--color-border)" }}
              >
                <span className="text-xs" style={{ color: "var(--color-text-muted)" }}>Pitch Deck</span>
                <a
                  href={getInvestorPitchDeckUrl(token, companyId)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs font-medium hover:underline"
                  style={{ color: "var(--color-accent-purple)" }}
                >
                  Download
                </a>
              </div>
            </div>
          )}
          {company?.description && (
            <div
              className="rounded-xl p-5 border"
              style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
            >
              <h3 className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: "var(--color-text-muted)" }}>
                About
              </h3>
              <p className="text-sm whitespace-pre-line" style={{ color: "var(--color-text-secondary)" }}>
                {company.description}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        {[
          { label: "Your Shares", value: holdings?.total_shares?.toLocaleString() || "0" },
          { label: "Ownership", value: `${holdings?.total_percentage?.toFixed(2) || "0.00"}%`, accent: true },
          { label: "Funding Rounds", value: rounds.length },
        ].map((stat) => (
          <div
            key={stat.label}
            className="rounded-xl p-5 border"
            style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
          >
            <p className="text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>{stat.label}</p>
            <p
              className="text-2xl font-bold"
              style={{
                fontFamily: "var(--font-display)",
                color: stat.accent ? "var(--color-accent-purple)" : "var(--color-text-primary)",
              }}
            >
              {stat.value}
            </p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="border-b mb-6" style={{ borderColor: "var(--color-border)" }}>
        <nav className="flex gap-6">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className="pb-3 text-sm font-medium border-b-2 transition-colors"
              style={{
                borderColor: activeTab === tab.key ? "var(--color-accent-purple)" : "transparent",
                color: activeTab === tab.key ? "var(--color-accent-purple)" : "var(--color-text-muted)",
              }}
            >
              {tab.label}
              {tab.count !== undefined && (
                <span className="ml-1.5 text-[10px] opacity-60">({tab.count})</span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab content */}
      {activeTab === "holdings" && (
        <div
          className="rounded-xl overflow-hidden border"
          style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
        >
          <table className="w-full text-sm">
            <thead>
              <tr style={{ background: "var(--color-bg-secondary)" }}>
                <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Share Type</th>
                <th className="text-right px-4 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Shares</th>
                <th className="text-right px-4 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Ownership %</th>
                <th className="text-right px-4 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Face Value</th>
                <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Allotment Date</th>
              </tr>
            </thead>
            <tbody>
              {holdings?.details?.map((h: any, i: number) => (
                <tr key={i} style={{ borderBottom: `1px solid var(--color-border)` }}>
                  <td className="px-4 py-3 capitalize" style={{ color: "var(--color-text-primary)" }}>{h.share_type}</td>
                  <td className="px-4 py-3 text-right font-medium" style={{ color: "var(--color-text-primary)" }}>{h.shares?.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right font-medium" style={{ color: "var(--color-accent-purple)" }}>{h.percentage?.toFixed(2)}%</td>
                  <td className="px-4 py-3 text-right" style={{ color: "var(--color-text-secondary)" }}>{h.face_value || "-"}</td>
                  <td className="px-4 py-3" style={{ color: "var(--color-text-secondary)" }}>{h.date_of_allotment || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === "cap-table" && (
        <div
          className="rounded-xl overflow-hidden border"
          style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
        >
          <table className="w-full text-sm">
            <thead>
              <tr style={{ background: "var(--color-bg-secondary)" }}>
                <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Shareholder</th>
                <th className="text-right px-4 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Shares</th>
                <th className="text-right px-4 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Ownership %</th>
                <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Type</th>
              </tr>
            </thead>
            <tbody>
              {capTable.map((sh: any, i: number) => (
                <tr
                  key={i}
                  style={{
                    borderBottom: `1px solid var(--color-border)`,
                    background: sh.is_self ? "rgba(124, 58, 237, 0.04)" : undefined,
                  }}
                >
                  <td className="px-4 py-3" style={{ color: "var(--color-text-primary)" }}>
                    {sh.name}
                    {sh.is_self && (
                      <span
                        className="ml-2 text-[10px] font-semibold px-1.5 py-0.5 rounded-full"
                        style={{ background: "rgba(124, 58, 237, 0.08)", color: "var(--color-accent-purple)" }}
                      >
                        You
                      </span>
                    )}
                    {sh.is_promoter && (
                      <span
                        className="ml-1 text-[10px] font-semibold px-1.5 py-0.5 rounded-full"
                        style={{ background: "rgba(5, 150, 105, 0.08)", color: "var(--color-accent-emerald)" }}
                      >
                        Promoter
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right font-medium" style={{ color: "var(--color-text-primary)" }}>{sh.shares?.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right font-medium" style={{ color: "var(--color-accent-purple)" }}>{sh.percentage?.toFixed(2)}%</td>
                  <td className="px-4 py-3 capitalize" style={{ color: "var(--color-text-secondary)" }}>{sh.share_type}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === "rounds" && (
        <div className="space-y-4">
          {rounds.length === 0 ? (
            <div
              className="rounded-xl p-12 text-center border"
              style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
            >
              <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>No funding rounds recorded.</p>
            </div>
          ) : (
            rounds.map((r: any) => (
              <div
                key={r.id}
                className="rounded-xl p-5 border"
                style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
              >
                <div className="flex items-center justify-between mb-3">
                  <h3
                    className="font-semibold"
                    style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
                  >
                    {r.round_name}
                  </h3>
                  <div className="flex items-center gap-2">
                    {r.participated && (
                      <span
                        className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
                        style={{ background: "rgba(5, 150, 105, 0.08)", color: "var(--color-accent-emerald)" }}
                      >
                        Participated
                      </span>
                    )}
                    <span
                      className="text-[10px] font-semibold px-2 py-0.5 rounded-full capitalize"
                      style={{ background: "rgba(100, 116, 139, 0.08)", color: "var(--color-text-muted)" }}
                    >
                      {r.status?.replace("_", " ")}
                    </span>
                  </div>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                  {[
                    { label: "Instrument", value: r.instrument_type || "-", capitalize: true },
                    { label: "Pre-Money", value: r.pre_money_valuation ? `Rs ${(r.pre_money_valuation / 100000).toFixed(1)}L` : "-" },
                    { label: "Amount Raised", value: r.amount_raised ? `Rs ${(r.amount_raised / 100000).toFixed(1)}L` : "-" },
                    { label: "Price/Share", value: r.price_per_share ? `Rs ${r.price_per_share}` : "-" },
                  ].map((item) => (
                    <div key={item.label}>
                      <p className="text-xs mb-0.5" style={{ color: "var(--color-text-muted)" }}>{item.label}</p>
                      <p className={`font-medium ${item.capitalize ? "capitalize" : ""}`} style={{ color: "var(--color-text-primary)" }}>
                        {item.value}
                      </p>
                    </div>
                  ))}
                </div>
                {r.participated && (
                  <div
                    className="mt-3 pt-3 grid grid-cols-2 gap-4 text-sm border-t"
                    style={{ borderColor: "var(--color-border)" }}
                  >
                    <div>
                      <p className="text-xs mb-0.5" style={{ color: "var(--color-text-muted)" }}>Your Investment</p>
                      <p className="font-semibold" style={{ color: "var(--color-accent-purple)" }}>
                        {r.my_investment ? `Rs ${r.my_investment.toLocaleString()}` : "-"}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs mb-0.5" style={{ color: "var(--color-text-muted)" }}>Shares Allotted</p>
                      <p className="font-semibold" style={{ color: "var(--color-accent-purple)" }}>
                        {r.my_shares?.toLocaleString() || "-"}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === "esop" && (
        <div className="space-y-4">
          {esopGrants.length === 0 ? (
            <div
              className="rounded-xl p-12 text-center border"
              style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
            >
              <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>No ESOP grants found.</p>
            </div>
          ) : (
            esopGrants.map((g: any) => {
              const vestedPct = g.number_of_options > 0
                ? Math.round(((g.options_vested || 0) / g.number_of_options) * 100)
                : 0;
              return (
                <div
                  key={g.id}
                  className="rounded-xl p-5 border"
                  style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
                >
                  <div className="flex items-center justify-between mb-3">
                    <h3
                      className="font-semibold"
                      style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
                    >
                      {g.plan_name || "Grant"}
                    </h3>
                    <span
                      className="text-[10px] font-semibold px-2 py-0.5 rounded-full capitalize"
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

                  {/* Vesting progress bar */}
                  <div className="mb-4">
                    <div className="flex justify-between text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>
                      <span>{vestedPct}% vested</span>
                      <span>{(g.options_vested || 0).toLocaleString()} / {g.number_of_options?.toLocaleString()}</span>
                    </div>
                    <div className="w-full h-2 rounded-full overflow-hidden" style={{ background: "var(--color-bg-secondary)" }}>
                      <div
                        className="h-full rounded-full transition-all"
                        style={{ width: `${vestedPct}%`, background: "var(--color-accent-emerald)" }}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-sm">
                    {[
                      { label: "Granted", value: g.number_of_options?.toLocaleString() },
                      { label: "Vested", value: (g.options_vested || 0).toLocaleString(), color: "var(--color-accent-emerald)" },
                      { label: "Exercisable", value: (g.options_exercisable || 0).toLocaleString(), color: "var(--color-accent-purple)" },
                      { label: "Exercised", value: g.options_exercised?.toLocaleString() },
                      { label: "Exercise Price", value: `Rs ${g.exercise_price}` },
                    ].map((item) => (
                      <div key={item.label}>
                        <p className="text-xs mb-0.5" style={{ color: "var(--color-text-muted)" }}>{item.label}</p>
                        <p className="font-medium" style={{ color: item.color || "var(--color-text-primary)" }}>{item.value}</p>
                      </div>
                    ))}
                  </div>

                  <div
                    className="mt-3 pt-3 grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm border-t"
                    style={{ borderColor: "var(--color-border)" }}
                  >
                    {[
                      { label: "Grant Date", value: g.grant_date?.split("T")[0] || "-" },
                      { label: "Vesting Period", value: `${g.vesting_months} months (${g.cliff_months}m cliff)` },
                      { label: "Vesting Type", value: g.vesting_type || "monthly" },
                      { label: "Vesting Start", value: g.vesting_start_date?.split("T")[0] || "-" },
                    ].map((item) => (
                      <div key={item.label}>
                        <p className="text-xs mb-0.5" style={{ color: "var(--color-text-muted)" }}>{item.label}</p>
                        <p className="font-medium capitalize" style={{ color: "var(--color-text-primary)" }}>{item.value}</p>
                      </div>
                    ))}
                  </div>

                  {/* Vesting schedule */}
                  {g.vesting_schedule && g.vesting_schedule.length > 0 && (
                    <details className="mt-3 pt-3 border-t" style={{ borderColor: "var(--color-border)" }}>
                      <summary
                        className="text-sm cursor-pointer hover:underline font-medium"
                        style={{ color: "var(--color-accent-purple)" }}
                      >
                        View vesting schedule ({g.vesting_schedule.length} milestones)
                      </summary>
                      <div className="mt-2 max-h-48 overflow-y-auto">
                        <table className="w-full text-xs">
                          <thead>
                            <tr style={{ borderBottom: `1px solid var(--color-border)` }}>
                              <th className="text-left py-1.5 pr-3" style={{ color: "var(--color-text-muted)" }}>Date</th>
                              <th className="text-right py-1.5 pr-3" style={{ color: "var(--color-text-muted)" }}>Vesting</th>
                              <th className="text-right py-1.5 pr-3" style={{ color: "var(--color-text-muted)" }}>Cumulative</th>
                              <th className="text-right py-1.5" style={{ color: "var(--color-text-muted)" }}>%</th>
                            </tr>
                          </thead>
                          <tbody>
                            {g.vesting_schedule.map((vs: any, idx: number) => {
                              const isPast = new Date(vs.date) <= new Date();
                              return (
                                <tr
                                  key={idx}
                                  style={{
                                    borderBottom: `1px solid var(--color-border)`,
                                    color: isPast ? "var(--color-text-primary)" : "var(--color-text-muted)",
                                  }}
                                >
                                  <td className="py-1.5 pr-3">{vs.date?.split("T")[0]}</td>
                                  <td className="py-1.5 pr-3 text-right">{vs.options_vesting?.toLocaleString()}</td>
                                  <td className="py-1.5 pr-3 text-right font-medium">{vs.cumulative_vested?.toLocaleString()}</td>
                                  <td className="py-1.5 text-right">{vs.percentage_vested?.toFixed(1)}%</td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </details>
                  )}
                </div>
              );
            })
          )}
        </div>
      )}

      {activeTab === "documents" && (
        <div
          className="rounded-xl overflow-hidden border"
          style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
        >
          {documents.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>No documents available.</p>
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr style={{ background: "var(--color-bg-secondary)" }}>
                  <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Document</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Type</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Status</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Date</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((d: any) => (
                  <tr key={d.id} style={{ borderBottom: `1px solid var(--color-border)` }}>
                    <td className="px-4 py-3 font-medium" style={{ color: "var(--color-text-primary)" }}>{d.name}</td>
                    <td className="px-4 py-3 capitalize" style={{ color: "var(--color-text-secondary)" }}>{d.doc_type?.replace("_", " ") || "-"}</td>
                    <td className="px-4 py-3">
                      <span
                        className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
                        style={{
                          background: (d.status === "team_verified" || d.status === "ai_verified")
                            ? "rgba(5, 150, 105, 0.08)"
                            : d.status === "rejected"
                            ? "rgba(225, 29, 72, 0.08)"
                            : "rgba(100, 116, 139, 0.08)",
                          color: (d.status === "team_verified" || d.status === "ai_verified")
                            ? "var(--color-accent-emerald)"
                            : d.status === "rejected"
                            ? "var(--color-accent-rose)"
                            : "var(--color-text-muted)",
                        }}
                      >
                        {d.status?.replace("_", " ") || "pending"}
                      </span>
                    </td>
                    <td className="px-4 py-3" style={{ color: "var(--color-text-secondary)" }}>{d.uploaded_at?.split("T")[0] || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
