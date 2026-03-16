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
      } catch (err: any) {
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
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-600">{error}</p>
        <button
          onClick={() => router.push(`/investor/${token}`)}
          className="mt-4 text-blue-600 hover:underline text-sm"
        >
          Back to Portfolio
        </button>
      </div>
    );
  }

  const company = detail?.company;
  const holdings = detail?.holdings;
  const tabs: { key: Tab; label: string }[] = [
    { key: "holdings", label: "Holdings" },
    { key: "cap-table", label: "Cap Table" },
    { key: "rounds", label: "Funding Rounds" },
    { key: "esop", label: "ESOP" },
    { key: "documents", label: "Documents" },
  ];

  return (
    <div>
      {/* Back link */}
      <button
        onClick={() => router.push(`/investor/${token}`)}
        className="text-sm text-blue-600 hover:underline mb-4 inline-block"
      >
        &larr; Back to Portfolio
      </button>

      {/* Company header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{company?.name}</h1>
        {company?.tagline && (
          <p className="text-gray-600 mt-1">{company.tagline}</p>
        )}
        <div className="flex flex-wrap gap-3 mt-2 text-sm text-gray-500">
          {company?.entity_type && <span className="capitalize">{company.entity_type.replace("_", " ")}</span>}
          {company?.sector && <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs font-medium">{company.sector}</span>}
          {company?.cin && <span>CIN: {company.cin}</span>}
          {company?.status && (
            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs font-medium capitalize">
              {company.status.replace("_", " ")}
            </span>
          )}
          {company?.website && (
            <a href={company.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
              Website
            </a>
          )}
        </div>
      </div>

      {/* Pitch deck viewer + description */}
      {(company?.has_pitch_deck || company?.description) && (
        <div className="mb-6 grid grid-cols-1 lg:grid-cols-2 gap-4">
          {company?.has_pitch_deck && (
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <div className="relative w-full" style={{ paddingBottom: "75%" }}>
                <iframe
                  className="absolute inset-0 w-full h-full"
                  src={getInvestorPitchDeckUrl(token, companyId)}
                  title="Pitch Deck"
                />
              </div>
              <div className="p-3 border-t border-gray-200 flex items-center justify-between">
                <span className="text-xs text-gray-500">Pitch Deck</span>
                <a
                  href={getInvestorPitchDeckUrl(token, companyId)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-600 hover:underline font-medium"
                >
                  Download
                </a>
              </div>
            </div>
          )}
          {company?.description && (
            <div className="bg-white rounded-lg border border-gray-200 p-5">
              <h3 className="text-sm font-medium text-gray-500 mb-2">About</h3>
              <p className="text-sm text-gray-700 whitespace-pre-line">{company.description}</p>
            </div>
          )}
        </div>
      )}

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <p className="text-sm text-gray-500">Your Shares</p>
          <p className="text-2xl font-bold text-gray-900">
            {holdings?.total_shares?.toLocaleString()}
          </p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <p className="text-sm text-gray-500">Ownership</p>
          <p className="text-2xl font-bold text-gray-900">
            {holdings?.total_percentage?.toFixed(2)}%
          </p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <p className="text-sm text-gray-500">Funding Rounds</p>
          <p className="text-2xl font-bold text-gray-900">{rounds.length}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-6">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.key
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab content */}
      {activeTab === "holdings" && (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Share Type</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">Shares</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">Ownership %</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">Face Value</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Allotment Date</th>
              </tr>
            </thead>
            <tbody>
              {holdings?.details?.map((h: any, i: number) => (
                <tr key={i} className="border-b border-gray-100">
                  <td className="px-4 py-3 capitalize">{h.share_type}</td>
                  <td className="px-4 py-3 text-right">{h.shares?.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right">{h.percentage?.toFixed(2)}%</td>
                  <td className="px-4 py-3 text-right">{h.face_value || "-"}</td>
                  <td className="px-4 py-3">{h.date_of_allotment || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === "cap-table" && (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Shareholder</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">Shares</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">Ownership %</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Type</th>
              </tr>
            </thead>
            <tbody>
              {capTable.map((sh: any, i: number) => (
                <tr
                  key={i}
                  className={`border-b border-gray-100 ${sh.is_self ? "bg-blue-50" : ""}`}
                >
                  <td className="px-4 py-3">
                    {sh.name}
                    {sh.is_self && (
                      <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">
                        You
                      </span>
                    )}
                    {sh.is_promoter && (
                      <span className="ml-1 text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">
                        Promoter
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right">{sh.shares?.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right">{sh.percentage?.toFixed(2)}%</td>
                  <td className="px-4 py-3 capitalize">{sh.share_type}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === "rounds" && (
        <div className="space-y-4">
          {rounds.length === 0 ? (
            <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-500">
              No funding rounds recorded.
            </div>
          ) : (
            rounds.map((r: any) => (
              <div key={r.id} className="bg-white rounded-lg border border-gray-200 p-5">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-gray-900">{r.round_name}</h3>
                  <div className="flex items-center gap-2">
                    {r.participated && (
                      <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded font-medium">
                        Participated
                      </span>
                    )}
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded capitalize">
                      {r.status?.replace("_", " ")}
                    </span>
                  </div>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Instrument</p>
                    <p className="font-medium capitalize">{r.instrument_type || "-"}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Pre-Money</p>
                    <p className="font-medium">
                      {r.pre_money_valuation ? `Rs ${(r.pre_money_valuation / 100000).toFixed(1)}L` : "-"}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500">Amount Raised</p>
                    <p className="font-medium">
                      {r.amount_raised ? `Rs ${(r.amount_raised / 100000).toFixed(1)}L` : "-"}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500">Price/Share</p>
                    <p className="font-medium">
                      {r.price_per_share ? `Rs ${r.price_per_share}` : "-"}
                    </p>
                  </div>
                </div>
                {r.participated && (
                  <div className="mt-3 pt-3 border-t border-gray-100 grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Your Investment</p>
                      <p className="font-medium text-blue-700">
                        {r.my_investment ? `Rs ${r.my_investment.toLocaleString()}` : "-"}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Shares Allotted</p>
                      <p className="font-medium text-blue-700">
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
            <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-500">
              No ESOP grants found.
            </div>
          ) : (
            esopGrants.map((g: any) => {
              const vestedPct = g.number_of_options > 0
                ? Math.round(((g.options_vested || 0) / g.number_of_options) * 100)
                : 0;
              return (
                <div key={g.id} className="bg-white rounded-lg border border-gray-200 p-5">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-gray-900">{g.plan_name || "Grant"}</h3>
                    <span className={`text-xs px-2 py-1 rounded font-medium capitalize ${
                      g.status === "active" || g.status === "partially_exercised"
                        ? "bg-green-100 text-green-700"
                        : g.status === "fully_exercised"
                        ? "bg-blue-100 text-blue-700"
                        : "bg-gray-100 text-gray-600"
                    }`}>
                      {g.status?.replace(/_/g, " ")}
                    </span>
                  </div>

                  {/* Vesting progress bar */}
                  <div className="mb-4">
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>{vestedPct}% vested</span>
                      <span>{(g.options_vested || 0).toLocaleString()} / {g.number_of_options?.toLocaleString()}</span>
                    </div>
                    <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full bg-green-500 transition-all"
                        style={{ width: `${vestedPct}%` }}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-sm">
                    <div>
                      <p className="text-gray-500">Granted</p>
                      <p className="font-medium">{g.number_of_options?.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Vested</p>
                      <p className="font-medium text-green-700">{(g.options_vested || 0).toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Exercisable</p>
                      <p className="font-medium text-blue-700">{(g.options_exercisable || 0).toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Exercised</p>
                      <p className="font-medium">{g.options_exercised?.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Exercise Price</p>
                      <p className="font-medium">Rs {g.exercise_price}</p>
                    </div>
                  </div>

                  <div className="mt-3 pt-3 border-t border-gray-100 grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
                    <div>
                      <p className="text-gray-500">Grant Date</p>
                      <p className="font-medium">{g.grant_date?.split("T")[0] || "-"}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Vesting Period</p>
                      <p className="font-medium">{g.vesting_months} months ({g.cliff_months}m cliff)</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Vesting Type</p>
                      <p className="font-medium capitalize">{g.vesting_type || "monthly"}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Vesting Start</p>
                      <p className="font-medium">{g.vesting_start_date?.split("T")[0] || "-"}</p>
                    </div>
                  </div>

                  {/* Vesting schedule table */}
                  {g.vesting_schedule && g.vesting_schedule.length > 0 && (
                    <details className="mt-3 pt-3 border-t border-gray-100">
                      <summary className="text-sm text-blue-600 cursor-pointer hover:underline">
                        View vesting schedule ({g.vesting_schedule.length} milestones)
                      </summary>
                      <div className="mt-2 max-h-48 overflow-y-auto">
                        <table className="w-full text-xs">
                          <thead>
                            <tr className="text-gray-500 border-b border-gray-100">
                              <th className="text-left py-1.5 pr-3">Date</th>
                              <th className="text-right py-1.5 pr-3">Vesting</th>
                              <th className="text-right py-1.5 pr-3">Cumulative</th>
                              <th className="text-right py-1.5">%</th>
                            </tr>
                          </thead>
                          <tbody>
                            {g.vesting_schedule.map((vs: any, idx: number) => {
                              const isPast = new Date(vs.date) <= new Date();
                              return (
                                <tr key={idx} className={`border-b border-gray-50 ${isPast ? "text-gray-900" : "text-gray-400"}`}>
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
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          {documents.length === 0 ? (
            <div className="p-8 text-center text-gray-500">No documents available.</div>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Document</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Type</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Date</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((d: any) => (
                  <tr key={d.id} className="border-b border-gray-100">
                    <td className="px-4 py-3 font-medium">{d.name}</td>
                    <td className="px-4 py-3 capitalize">{d.doc_type?.replace("_", " ") || "-"}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                        d.status === "team_verified" || d.status === "ai_verified"
                          ? "bg-green-100 text-green-700"
                          : d.status === "rejected"
                          ? "bg-red-100 text-red-700"
                          : "bg-gray-100 text-gray-600"
                      }`}>
                        {d.status?.replace("_", " ") || "pending"}
                      </span>
                    </td>
                    <td className="px-4 py-3">{d.uploaded_at?.split("T")[0] || "-"}</td>
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
