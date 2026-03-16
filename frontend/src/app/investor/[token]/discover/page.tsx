"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  discoverCompanies,
  expressInterest,
  withdrawInterest,
  getMyInterests,
  getInvestorPitchDeckUrl,
} from "@/lib/api";

const SECTORS = [
  { value: "", label: "All Sectors" },
  { value: "fintech", label: "Fintech" },
  { value: "saas", label: "SaaS" },
  { value: "healthtech", label: "Healthtech" },
  { value: "edtech", label: "Edtech" },
  { value: "ecommerce", label: "E-Commerce" },
  { value: "deeptech", label: "Deep Tech / AI" },
  { value: "cleantech", label: "Clean Tech" },
  { value: "agritech", label: "Agritech" },
  { value: "d2c", label: "D2C / Consumer" },
  { value: "logistics", label: "Logistics" },
  { value: "media", label: "Media / Content" },
  { value: "other", label: "Other" },
];

const STAGES = [
  { value: "", label: "All Stages" },
  { value: "idea", label: "Idea / Pre-revenue" },
  { value: "mvp", label: "MVP / Early Revenue" },
  { value: "seed", label: "Seed" },
  { value: "pre_series_a", label: "Pre-Series A" },
  { value: "series_a", label: "Series A" },
  { value: "series_b", label: "Series B+" },
  { value: "profitable", label: "Profitable" },
];

export default function InvestorDiscoverPage() {
  const params = useParams();
  const router = useRouter();
  const token = params.token as string;

  const [companies, setCompanies] = useState<any[]>([]);
  const [interests, setInterests] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sector, setSector] = useState("");
  const [stage, setStage] = useState("");
  const [tab, setTab] = useState<"discover" | "interests">("discover");
  const [actioningId, setActioningId] = useState<number | null>(null);
  const [messageModal, setMessageModal] = useState<number | null>(null);
  const [interestMessage, setInterestMessage] = useState("");

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const filters: { sector?: string; stage?: string } = {};
      if (sector) filters.sector = sector;
      if (stage) filters.stage = stage;
      const [discoverData, interestsData] = await Promise.all([
        discoverCompanies(token, filters),
        getMyInterests(token),
      ]);
      setCompanies(discoverData.companies || []);
      setInterests(interestsData.interests || []);
    } catch {
      setError("Unable to load. Check your portal link.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [token, sector, stage]);

  const handleExpress = async (companyId: number, message?: string) => {
    setActioningId(companyId);
    try {
      await expressInterest(token, companyId, message);
      setMessageModal(null);
      setInterestMessage("");
      await loadData();
    } catch {
      // Ignore
    } finally {
      setActioningId(null);
    }
  };

  const handleWithdraw = async (companyId: number) => {
    setActioningId(companyId);
    try {
      await withdrawInterest(token, companyId);
      await loadData();
    } catch {
      // Ignore
    } finally {
      setActioningId(null);
    }
  };

  if (error) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-600">{error}</p>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <button
            onClick={() => router.push(`/investor/${token}`)}
            className="text-sm text-blue-600 hover:underline mb-2 inline-block"
          >
            &larr; Back to Portfolio
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Discover Companies</h1>
          <p className="text-sm text-gray-500 mt-1">
            Browse startups that are actively fundraising
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b border-gray-200">
        <button
          onClick={() => setTab("discover")}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
            tab === "discover"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-700"
          }`}
        >
          Browse ({companies.length})
        </button>
        <button
          onClick={() => setTab("interests")}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
            tab === "interests"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-700"
          }`}
        >
          My Interests ({interests.length})
        </button>
      </div>

      {tab === "discover" && (
        <>
          {/* Filters */}
          <div className="flex flex-wrap gap-3 mb-6">
            <select
              value={sector}
              onChange={(e) => setSector(e.target.value)}
              className="px-3 py-2 rounded-lg border border-gray-200 bg-white text-sm text-gray-700"
            >
              {SECTORS.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
            <select
              value={stage}
              onChange={(e) => setStage(e.target.value)}
              className="px-3 py-2 rounded-lg border border-gray-200 bg-white text-sm text-gray-700"
            >
              {STAGES.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-16">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
            </div>
          ) : companies.length === 0 ? (
            <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
              <p className="text-gray-500">No companies are currently fundraising{sector || stage ? " matching your filters" : ""}.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {companies.map((c: any) => (
                <div
                  key={c.company_id}
                  className="bg-white rounded-lg border border-gray-200 p-5 hover:border-blue-300 transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-semibold text-gray-900 text-lg">{c.name}</h3>
                      {c.tagline && (
                        <p className="text-sm text-gray-500 mt-0.5">{c.tagline}</p>
                      )}
                    </div>
                    {c.already_invested && (
                      <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs font-medium rounded">
                        Portfolio
                      </span>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-2 mb-3">
                    {c.sector && (
                      <span className="px-2 py-0.5 bg-purple-100 text-purple-700 text-xs font-medium rounded capitalize">
                        {c.sector.replace(/_/g, " ")}
                      </span>
                    )}
                    {c.stage && (
                      <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs font-medium rounded capitalize">
                        {c.stage.replace(/_/g, " ")}
                      </span>
                    )}
                    {c.fundraise_ask && (
                      <span className="px-2 py-0.5 bg-amber-100 text-amber-700 text-xs font-medium rounded">
                        Raising: {c.fundraise_ask}
                      </span>
                    )}
                  </div>

                  {c.description && (
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">{c.description}</p>
                  )}

                  <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                    <div className="flex gap-2">
                      {c.has_pitch_deck && (
                        <a
                          href={getInvestorPitchDeckUrl(token, c.company_id)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:underline font-medium"
                        >
                          View Pitch Deck
                        </a>
                      )}
                      {c.website && (
                        <a
                          href={c.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-gray-500 hover:underline"
                        >
                          Website
                        </a>
                      )}
                    </div>

                    {c.interest_expressed ? (
                      <button
                        onClick={() => handleWithdraw(c.company_id)}
                        disabled={actioningId === c.company_id}
                        className="text-xs px-3 py-1.5 rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-50 disabled:opacity-50"
                      >
                        {actioningId === c.company_id ? "..." : "Withdraw Interest"}
                      </button>
                    ) : (
                      <button
                        onClick={() => setMessageModal(c.company_id)}
                        disabled={actioningId === c.company_id}
                        className="text-xs px-3 py-1.5 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 font-medium"
                      >
                        {actioningId === c.company_id ? "..." : "Express Interest"}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {tab === "interests" && (
        <div>
          {interests.length === 0 ? (
            <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
              <p className="text-gray-500">You haven&apos;t expressed interest in any companies yet.</p>
              <button
                onClick={() => setTab("discover")}
                className="mt-3 text-sm text-blue-600 hover:underline"
              >
                Browse companies
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {interests.map((i: any) => (
                <div
                  key={i.interest_id}
                  className="bg-white rounded-lg border border-gray-200 p-4 flex items-center justify-between"
                >
                  <div>
                    <h3 className="font-medium text-gray-900">{i.company_name}</h3>
                    <div className="flex gap-2 mt-1">
                      {i.sector && (
                        <span className="text-xs text-purple-600 capitalize">{i.sector.replace(/_/g, " ")}</span>
                      )}
                      {i.stage && (
                        <span className="text-xs text-blue-600 capitalize">{i.stage.replace(/_/g, " ")}</span>
                      )}
                    </div>
                    {i.message && (
                      <p className="text-xs text-gray-500 mt-1">&ldquo;{i.message}&rdquo;</p>
                    )}
                    <p className="text-[10px] text-gray-400 mt-1">
                      {i.created_at ? new Date(i.created_at).toLocaleDateString() : ""}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs px-2 py-0.5 rounded font-medium capitalize ${
                      i.status === "intro_made"
                        ? "bg-green-100 text-green-700"
                        : "bg-blue-100 text-blue-700"
                    }`}>
                      {i.status.replace(/_/g, " ")}
                    </span>
                    {i.status === "interested" && (
                      <button
                        onClick={() => handleWithdraw(i.company_id)}
                        disabled={actioningId === i.company_id}
                        className="text-xs text-gray-500 hover:underline disabled:opacity-50"
                      >
                        Withdraw
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Express Interest Modal */}
      {messageModal !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Express Interest</h3>
            <p className="text-sm text-gray-500 mb-4">
              The company founder will see your name, email, and message.
            </p>
            <textarea
              value={interestMessage}
              onChange={(e) => setInterestMessage(e.target.value)}
              placeholder="Optional: Add a note (e.g. your fund, check size, thesis)..."
              className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm resize-none mb-4"
              rows={3}
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => { setMessageModal(null); setInterestMessage(""); }}
                className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={() => handleExpress(messageModal, interestMessage || undefined)}
                disabled={actioningId === messageModal}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
              >
                {actioningId === messageModal ? "Sending..." : "Send Interest"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
