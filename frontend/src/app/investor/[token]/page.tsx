"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getInvestorProfile, getInvestorPortfolio } from "@/lib/api";

export default function InvestorPortfolioPage() {
  const params = useParams();
  const router = useRouter();
  const token = params.token as string;

  const [profile, setProfile] = useState<any>(null);
  const [portfolio, setPortfolio] = useState<any[]>([]);
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
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome, {profile?.name}
        </h1>
        <p className="text-gray-600 mt-1">
          {profile?.stakeholder_type === "investor" ? "Investor" : profile?.stakeholder_type}
          {profile?.entity_name && ` at ${profile.entity_name}`}
        </p>
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
      {portfolio.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
          <p className="text-gray-500">No holdings found.</p>
        </div>
      ) : (
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
    </div>
  );
}
