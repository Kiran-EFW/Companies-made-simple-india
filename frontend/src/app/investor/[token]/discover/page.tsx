"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  discoverCompanies,
  expressInterest,
  withdrawInterest,
  getMyInterests,
  getInvestorPitchDeckUrl,
} from "@/lib/api";

/* eslint-disable @typescript-eslint/no-explicit-any */

export default function InvestorDealsPage() {
  const params = useParams();
  const token = params.token as string;

  const [deals, setDeals] = useState<any[]>([]);
  const [interests, setInterests] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<"deals" | "interests">("deals");
  const [actioningId, setActioningId] = useState<number | null>(null);
  const [messageModal, setMessageModal] = useState<any | null>(null);
  const [interestMessage, setInterestMessage] = useState("");

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [dealsData, interestsData] = await Promise.all([
        discoverCompanies(token, {}),
        getMyInterests(token),
      ]);
      setDeals(dealsData.companies || []);
      setInterests(interestsData.interests || []);
    } catch {
      setError("Unable to load deals. Check your portal link.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [token]);

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
        <p style={{ color: "var(--color-text-secondary)" }}>{error}</p>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1
          className="text-2xl font-bold"
          style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
        >
          Deals
        </h1>
        <p className="text-sm mt-1" style={{ color: "var(--color-text-secondary)" }}>
          Opportunities shared with you by founders
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b" style={{ borderColor: "var(--color-border)" }}>
        {[
          { key: "deals" as const, label: `Shared with You (${deals.length})` },
          { key: "interests" as const, label: `My Interests (${interests.length})` },
        ].map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className="px-4 py-2.5 text-sm font-medium border-b-2 transition-colors"
            style={{
              borderColor: tab === t.key ? "var(--color-accent-purple)" : "transparent",
              color: tab === t.key ? "var(--color-accent-purple)" : "var(--color-text-muted)",
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "deals" && (
        <>
          {loading ? (
            <div className="flex items-center justify-center py-16">
              <div
                className="animate-spin rounded-full h-8 w-8 border-b-2"
                style={{ borderColor: "var(--color-accent-purple)" }}
              />
            </div>
          ) : deals.length === 0 ? (
            <div
              className="rounded-xl p-12 text-center border"
              style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
            >
              <div className="flex justify-center mb-4">
                <svg className="w-12 h-12" style={{ color: "var(--color-text-muted)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 13.5h3.86a2.25 2.25 0 012.012 1.244l.256.512a2.25 2.25 0 002.013 1.244h3.218a2.25 2.25 0 002.013-1.244l.256-.512a2.25 2.25 0 012.013-1.244h3.859m-19.5.338V18a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18v-4.162c0-.224-.034-.447-.1-.661L19.24 5.338a2.25 2.25 0 00-2.15-1.588H6.911a2.25 2.25 0 00-2.15 1.588L2.35 13.177a2.25 2.25 0 00-.1.661z" />
                </svg>
              </div>
              <p className="text-sm font-medium mb-1" style={{ color: "var(--color-text-primary)" }}>
                No deals yet
              </p>
              <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                When a founder shares their fundraising deal with you, it will appear here.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {deals.map((c: any) => (
                <div
                  key={c.company_id}
                  className="rounded-xl p-5 border transition-colors"
                  style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
                  onMouseEnter={(e) => { e.currentTarget.style.borderColor = "rgba(124, 58, 237, 0.3)"; }}
                  onMouseLeave={(e) => { e.currentTarget.style.borderColor = "var(--color-border)"; }}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3
                        className="font-semibold text-base"
                        style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
                      >
                        {c.name}
                      </h3>
                      {c.tagline && (
                        <p className="text-xs mt-0.5" style={{ color: "var(--color-text-muted)" }}>{c.tagline}</p>
                      )}
                    </div>
                    {c.already_invested && (
                      <span
                        className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
                        style={{ background: "rgba(5, 150, 105, 0.08)", color: "var(--color-accent-emerald)" }}
                      >
                        Portfolio
                      </span>
                    )}
                  </div>

                  {/* Founder's shared message */}
                  {c.shared_message && (
                    <div
                      className="rounded-lg px-3 py-2 mb-3 text-xs italic"
                      style={{
                        background: "rgba(124, 58, 237, 0.04)",
                        border: "1px solid rgba(124, 58, 237, 0.1)",
                        color: "var(--color-text-secondary)",
                      }}
                    >
                      &ldquo;{c.shared_message}&rdquo;
                    </div>
                  )}

                  <div className="flex flex-wrap gap-1.5 mb-3">
                    {c.sector && (
                      <span
                        className="text-[10px] font-semibold px-2 py-0.5 rounded-full capitalize"
                        style={{ background: "rgba(124, 58, 237, 0.08)", color: "var(--color-accent-purple)" }}
                      >
                        {c.sector.replace(/_/g, " ")}
                      </span>
                    )}
                    {c.stage && (
                      <span
                        className="text-[10px] font-semibold px-2 py-0.5 rounded-full capitalize"
                        style={{ background: "rgba(37, 99, 235, 0.08)", color: "var(--color-accent-blue)" }}
                      >
                        {c.stage.replace(/_/g, " ")}
                      </span>
                    )}
                    {c.fundraise_ask && (
                      <span
                        className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
                        style={{ background: "rgba(217, 119, 6, 0.08)", color: "var(--color-accent-amber)" }}
                      >
                        Raising: {c.fundraise_ask}
                      </span>
                    )}
                  </div>

                  {c.description && (
                    <p className="text-sm mb-3 line-clamp-2" style={{ color: "var(--color-text-secondary)" }}>
                      {c.description}
                    </p>
                  )}

                  {c.shared_at && (
                    <p className="text-[10px] mb-3" style={{ color: "var(--color-text-muted)" }}>
                      Shared {new Date(c.shared_at).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}
                    </p>
                  )}

                  <div
                    className="flex items-center justify-between pt-3 border-t"
                    style={{ borderColor: "var(--color-border)" }}
                  >
                    <div className="flex gap-3">
                      {c.has_pitch_deck && (
                        <a
                          href={getInvestorPitchDeckUrl(token, c.company_id)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs font-medium hover:underline"
                          style={{ color: "var(--color-accent-purple)" }}
                        >
                          View Pitch Deck
                        </a>
                      )}
                      {c.website && (
                        <a
                          href={c.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs hover:underline"
                          style={{ color: "var(--color-text-muted)" }}
                        >
                          Website
                        </a>
                      )}
                    </div>

                    {c.interest_expressed ? (
                      <button
                        onClick={() => handleWithdraw(c.company_id)}
                        disabled={actioningId === c.company_id}
                        className="text-xs px-3 py-1.5 rounded-lg font-medium disabled:opacity-50 transition-colors"
                        style={{
                          border: `1px solid var(--color-border)`,
                          color: "var(--color-text-secondary)",
                        }}
                      >
                        {actioningId === c.company_id ? "..." : "Withdraw Interest"}
                      </button>
                    ) : (
                      <button
                        onClick={() => setMessageModal(c)}
                        disabled={actioningId === c.company_id}
                        className="text-xs px-3 py-1.5 rounded-lg text-white font-medium disabled:opacity-50 transition-colors"
                        style={{ background: "var(--color-accent-purple)" }}
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
            <div
              className="rounded-xl p-12 text-center border"
              style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
            >
              <p className="text-sm mb-2" style={{ color: "var(--color-text-muted)" }}>
                You haven&apos;t expressed interest in any deals yet.
              </p>
              <button
                onClick={() => setTab("deals")}
                className="text-sm font-medium hover:underline"
                style={{ color: "var(--color-accent-purple)" }}
              >
                View shared deals
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {interests.map((i: any) => (
                <div
                  key={i.interest_id}
                  className="rounded-xl p-4 border flex items-center justify-between"
                  style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
                >
                  <div>
                    <h3
                      className="font-medium"
                      style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
                    >
                      {i.company_name}
                    </h3>
                    <div className="flex gap-2 mt-1">
                      {i.sector && (
                        <span className="text-xs capitalize" style={{ color: "var(--color-accent-purple)" }}>
                          {i.sector.replace(/_/g, " ")}
                        </span>
                      )}
                      {i.stage && (
                        <span className="text-xs capitalize" style={{ color: "var(--color-accent-blue)" }}>
                          {i.stage.replace(/_/g, " ")}
                        </span>
                      )}
                    </div>
                    {i.message && (
                      <p className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
                        &ldquo;{i.message}&rdquo;
                      </p>
                    )}
                    <p className="text-[10px] mt-1" style={{ color: "var(--color-text-muted)" }}>
                      {i.created_at ? new Date(i.created_at).toLocaleDateString() : ""}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span
                      className="text-[10px] font-semibold px-2 py-0.5 rounded-full capitalize"
                      style={{
                        background: i.status === "intro_made"
                          ? "rgba(5, 150, 105, 0.08)"
                          : "rgba(124, 58, 237, 0.08)",
                        color: i.status === "intro_made"
                          ? "var(--color-accent-emerald)"
                          : "var(--color-accent-purple)",
                      }}
                    >
                      {i.status.replace(/_/g, " ")}
                    </span>
                    {i.status === "interested" && (
                      <button
                        onClick={() => handleWithdraw(i.company_id)}
                        disabled={actioningId === i.company_id}
                        className="text-xs hover:underline disabled:opacity-50"
                        style={{ color: "var(--color-text-muted)" }}
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
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ background: "rgba(0,0,0,0.4)" }}
          role="dialog"
          aria-modal="true"
          aria-label="Express interest"
          onClick={() => setMessageModal(null)}
          onKeyDown={(e) => { if (e.key === "Escape") setMessageModal(null); }}
        >
          <div
            className="rounded-xl p-6 w-full max-w-md shadow-xl"
            style={{ background: "var(--color-bg-card)" }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3
              className="text-lg font-semibold mb-1"
              style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
            >
              Express Interest in {messageModal.name}
            </h3>
            <p className="text-sm mb-4" style={{ color: "var(--color-text-muted)" }}>
              The founder will see your name, email, and message.
            </p>
            <textarea
              value={interestMessage}
              onChange={(e) => setInterestMessage(e.target.value)}
              placeholder="Optional: Add a note (e.g. your fund, check size, thesis)..."
              className="w-full px-3 py-2.5 rounded-lg text-sm resize-none mb-4"
              style={{
                background: "var(--color-bg-secondary)",
                border: `1px solid var(--color-border)`,
                color: "var(--color-text-primary)",
                outline: "none",
              }}
              onFocus={(e) => { e.currentTarget.style.borderColor = "var(--color-accent-purple)"; }}
              onBlur={(e) => { e.currentTarget.style.borderColor = "var(--color-border)"; }}
              rows={3}
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => { setMessageModal(null); setInterestMessage(""); }}
                className="px-4 py-2 text-sm font-medium rounded-lg transition-colors"
                style={{ color: "var(--color-text-secondary)", border: `1px solid var(--color-border)` }}
              >
                Cancel
              </button>
              <button
                onClick={() => handleExpress(messageModal.company_id, interestMessage || undefined)}
                disabled={actioningId === messageModal.company_id}
                className="px-4 py-2 text-sm text-white rounded-lg font-medium disabled:opacity-50 transition-colors"
                style={{ background: "var(--color-accent-purple)" }}
              >
                {actioningId === messageModal.company_id ? "Sending..." : "Send Interest"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
