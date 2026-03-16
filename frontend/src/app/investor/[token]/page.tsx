"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getInvestorProfile, getInvestorPortfolio, getInvestorESOPSummary } from "@/lib/api";

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
        // Fetch ESOP summary (may return empty if no grants)
        try {
          const esopData = await getInvestorESOPSummary(token);
          if (esopData.total_options > 0) setEsopSummary(esopData);
        } catch {
          // No ESOP grants — that's fine
        }
      } catch (err: any) {
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
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-20">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Access Denied</h2>
        <p className="text-gray-600">{error}</p>
      </div>
    );
  }

  return (
    <div>
      {/* Investor header */}
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome, {profile?.name}
          </h1>
          <p className="text-gray-600 mt-1">
            {profile?.stakeholder_type === "investor" ? "Investor" : profile?.stakeholder_type}
            {profile?.entity_name && ` at ${profile.entity_name}`}
          </p>
        </div>
        <button
          onClick={() => router.push(`/investor/${token}/discover`)}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          Discover Companies
        </button>
      </div>

      {/* Portfolio summary */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <p className="text-sm text-gray-500">Companies</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{portfolio.length}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <p className="text-sm text-gray-500">Total Shares</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {portfolio.reduce((sum: number, p: any) => sum + (p.shares || 0), 0).toLocaleString()}
          </p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <p className="text-sm text-gray-500">Promoter Holdings</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {portfolio.filter((p: any) => p.is_promoter).length}
          </p>
        </div>
      </div>

      {/* Company cards */}
      {portfolio.length === 0 && !esopSummary ? (
        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
          <p className="text-gray-500">No holdings found.</p>
        </div>
      ) : (
        <>
          {portfolio.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {portfolio.map((holding: any) => (
                <button
                  key={holding.shareholder_id}
                  onClick={() => router.push(`/investor/${token}/company/${holding.company_id}`)}
                  className="bg-white rounded-lg border border-gray-200 p-6 text-left hover:border-blue-400 hover:shadow-sm transition-all"
                >
                  <h3 className="font-semibold text-gray-900 text-lg">
                    {holding.company_name}
                  </h3>
                  <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Shares</p>
                      <p className="font-medium text-gray-900">
                        {holding.shares?.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Ownership</p>
                      <p className="font-medium text-gray-900">
                        {holding.percentage?.toFixed(2)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Type</p>
                      <p className="font-medium text-gray-900 capitalize">
                        {holding.share_type}
                      </p>
                    </div>
                  </div>
                  {holding.is_promoter && (
                    <span className="inline-block mt-3 px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded">
                      Promoter
                    </span>
                  )}
                </button>
              ))}
            </div>
          )}
        </>
      )}

      {/* ESOP Summary Section */}
      {esopSummary && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Stock Options (ESOP)</h2>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <p className="text-sm text-gray-500">Total Options</p>
              <p className="text-xl font-bold text-gray-900">{esopSummary.total_options?.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <p className="text-sm text-gray-500">Vested</p>
              <p className="text-xl font-bold text-green-700">{esopSummary.total_vested?.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <p className="text-sm text-gray-500">Exercisable</p>
              <p className="text-xl font-bold text-blue-700">{esopSummary.total_exercisable?.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <p className="text-sm text-gray-500">Exercised</p>
              <p className="text-xl font-bold text-gray-900">{esopSummary.total_exercised?.toLocaleString()}</p>
            </div>
          </div>

          {esopSummary.companies?.map((comp: any) => (
            <div key={comp.company_id} className="bg-white rounded-lg border border-gray-200 p-5 mb-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-900">{comp.company_name}</h3>
                <button
                  onClick={() => router.push(`/investor/${token}/company/${comp.company_id}`)}
                  className="text-sm text-blue-600 hover:underline"
                >
                  View Details
                </button>
              </div>
              <div className="grid grid-cols-3 gap-4 text-sm mb-3">
                <div>
                  <p className="text-gray-500">Options</p>
                  <p className="font-medium">{comp.total_options?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-gray-500">Vested</p>
                  <p className="font-medium text-green-700">{comp.total_vested?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-gray-500">Exercised</p>
                  <p className="font-medium">{comp.total_exercised?.toLocaleString()}</p>
                </div>
              </div>
              <div className="space-y-2">
                {comp.grants?.map((g: any) => (
                  <div key={g.id} className="flex items-center justify-between p-2 rounded bg-gray-50 text-sm">
                    <div>
                      <span className="font-medium">{g.plan_name || "Grant"}</span>
                      <span className="ml-2 text-gray-500">{g.number_of_options?.toLocaleString()} options @ Rs {g.exercise_price}</span>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded font-medium capitalize ${
                      g.status === "active" || g.status === "partially_exercised"
                        ? "bg-green-100 text-green-700"
                        : g.status === "fully_exercised"
                        ? "bg-blue-100 text-blue-700"
                        : "bg-gray-100 text-gray-600"
                    }`}>
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
