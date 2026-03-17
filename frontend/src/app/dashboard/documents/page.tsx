"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getLegalTemplates, getLegalDrafts, getSignatureRequests } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { type ReactNode } from "react";

// Category-based icons using Heroicons patterns
const CATEGORY_ICONS: Record<string, ReactNode> = {
  // Startup Essentials
  "Startup Essentials": (
    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
    </svg>
  ),
  // HR & Employment
  "HR & Employment": (
    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 00.75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 00-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0112 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 01-.673-.38m0 0A2.18 2.18 0 013 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 013.413-.387m7.5 0V5.25A2.25 2.25 0 0013.5 3h-3a2.25 2.25 0 00-2.25 2.25v.894m7.5 0a48.667 48.667 0 00-7.5 0M12 12.75h.008v.008H12v-.008z" />
    </svg>
  ),
  // Fundraising
  "Fundraising": (
    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z" />
    </svg>
  ),
  // Team
  "Team": (
    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
    </svg>
  ),
  // Equity
  "Equity": (
    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
    </svg>
  ),
  // Corporate Governance
  "Corporate Governance": (
    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0012 9.75c-2.551 0-5.056.2-7.5.582V21M3 21h18M12 6.75h.008v.008H12V6.75z" />
    </svg>
  ),
  // Compliance
  "Compliance": (
    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
    </svg>
  ),
  // Intellectual Property
  "Intellectual Property": (
    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" />
    </svg>
  ),
  // Business Operations
  "Business Operations": (
    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
    </svg>
  ),
  // Dispute Resolution
  "Dispute Resolution": (
    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v17.25m0 0c-1.472 0-2.882.265-4.185.75M12 20.25c1.472 0 2.882.265 4.185.75M18.75 4.97A48.416 48.416 0 0012 4.5c-2.291 0-4.545.16-6.75.47m13.5 0c1.01.143 2.01.317 3 .52m-3-.52l2.62 10.726c.122.499-.106 1.028-.589 1.202a5.988 5.988 0 01-2.031.352 5.988 5.988 0 01-2.031-.352c-.483-.174-.711-.703-.59-1.202L18.75 4.971zm-16.5.52c.99-.203 1.99-.377 3-.52m0 0l2.62 10.726c.122.499-.106 1.028-.589 1.202a5.989 5.989 0 01-2.031.352 5.989 5.989 0 01-2.031-.352c-.483-.174-.711-.703-.59-1.202L5.25 4.971z" />
    </svg>
  ),
};

// Category display order
const CATEGORY_ORDER = [
  "Startup Essentials",
  "Fundraising",
  "Equity",
  "Team",
  "HR & Employment",
  "Corporate Governance",
  "Compliance",
  "Intellectual Property",
  "Business Operations",
  "Dispute Resolution",
];

// Category accent colors
const CATEGORY_COLORS: Record<string, string> = {
  "Startup Essentials": "border-purple-500/30",
  "Fundraising": "border-emerald-500/30",
  "Equity": "border-blue-500/30",
  "Team": "border-amber-500/30",
  "HR & Employment": "border-cyan-500/30",
  "Corporate Governance": "border-rose-500/30",
  "Compliance": "border-teal-500/30",
  "Intellectual Property": "border-yellow-500/30",
  "Business Operations": "border-indigo-500/30",
  "Dispute Resolution": "border-orange-500/30",
};

const STATUS_BADGES: Record<string, { bg: string; text: string; label: string }> = {
  draft: { bg: "bg-gray-500/15 border-gray-500/30", text: "text-gray-400", label: "Draft" },
  in_progress: { bg: "bg-blue-500/15 border-blue-500/30", text: "text-blue-400", label: "In Progress" },
  preview: { bg: "bg-purple-500/15 border-purple-500/30", text: "text-purple-400", label: "Preview" },
  finalized: { bg: "bg-emerald-500/15 border-emerald-500/30", text: "text-emerald-400", label: "Finalized" },
  downloaded: { bg: "bg-emerald-500/15 border-emerald-500/30", text: "text-emerald-400", label: "Downloaded" },
};

export default function DocumentsPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [templates, setTemplates] = useState<any[]>([]);
  const [drafts, setDrafts] = useState<any[]>([]);
  const [signatureReqs, setSignatureReqs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    if (!user) return; // Dashboard layout handles auth redirect

    const fetchData = async () => {
      try {
        const [templatesRes, draftsRes, sigReqsRes] = await Promise.allSettled([
          getLegalTemplates(),
          getLegalDrafts(),
          getSignatureRequests(),
        ]);
        if (templatesRes.status === "fulfilled") {
          setTemplates(Array.isArray(templatesRes.value) ? templatesRes.value : []);
        }
        if (draftsRes.status === "fulfilled") {
          setDrafts(Array.isArray(draftsRes.value) ? draftsRes.value : []);
        }
        if (sigReqsRes.status === "fulfilled") {
          setSignatureReqs(Array.isArray(sigReqsRes.value) ? sigReqsRes.value : []);
        }
      } catch (err) {
        console.error("Failed to load documents:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user, authLoading]);

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 rounded w-56" style={{ background: "var(--color-bg-card)" }} />
          <div className="h-4 rounded w-80" style={{ background: "var(--color-bg-card)" }} />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-48 rounded-xl" style={{ background: "var(--color-bg-card)" }} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-5xl space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold" style={{ fontFamily: "var(--font-display)" }}>
          Legal Documents
        </h1>
        <p className="text-sm mt-1" style={{ color: "var(--color-text-secondary)" }}>
          Create customized legal documents with clause-by-clause guidance. Every clause comes with
          plain-language explanations and India-specific legal notes.
        </p>
      </div>

      {/* Founder's Guide Banner */}
      <Link
        href="/learn"
        className="block rounded-xl border p-4 transition-all hover:border-purple-500/40 group"
        style={{
          background: "var(--color-purple-bg)",
          borderColor: "var(--color-accent-purple-light)",
        }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span
              className="w-9 h-9 rounded-full flex items-center justify-center shrink-0"
              style={{
                background: "var(--color-purple-bg)",
                border: "1px solid var(--color-accent-purple-light)",
              }}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="var(--color-accent-purple-light)" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.438 60.438 0 00-.491 6.347A48.62 48.62 0 0112 20.904a48.62 48.62 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.636 50.636 0 00-2.658-.813A59.906 59.906 0 0112 3.493a59.903 59.903 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5" />
              </svg>
            </span>
            <div>
              <h3 className="text-sm font-semibold" style={{ color: "var(--color-text-primary)" }}>New to legal documents? Check our Founder&apos;s Guide</h3>
              <p className="text-[10px] mt-0.5" style={{ color: "var(--color-text-secondary)" }}>Learn what documents you need, when to create them, and common mistakes to avoid.</p>
            </div>
          </div>
          <svg
            className="w-5 h-5 group-hover:translate-x-1 transition-transform shrink-0"
            style={{ color: "var(--color-accent-purple-light)" }}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
          </svg>
        </div>
      </Link>

      {/* Template Cards grouped by category */}
      {(() => {
        // Group templates by category
        const grouped: Record<string, any[]> = {};
        templates.forEach((t) => {
          const cat = t.category || "Other";
          if (!grouped[cat]) grouped[cat] = [];
          grouped[cat].push(t);
        });
        // Sort categories by defined order
        const sortedCategories = Object.keys(grouped).sort((a, b) => {
          const ai = CATEGORY_ORDER.indexOf(a);
          const bi = CATEGORY_ORDER.indexOf(b);
          return (ai === -1 ? 999 : ai) - (bi === -1 ? 999 : bi);
        });

        return sortedCategories.map((category) => (
          <div key={category}>
            <h2 className="text-sm font-semibold uppercase tracking-wider mb-4 flex items-center gap-2" style={{ color: "var(--color-text-secondary)" }}>
              <span className="w-5 h-5" style={{ color: "var(--color-accent-purple-light)" }}>
                {CATEGORY_ICONS[category] ? (
                  <span className="[&>svg]:w-5 [&>svg]:h-5">{CATEGORY_ICONS[category]}</span>
                ) : null}
              </span>
              {category}
              <span className="text-[10px] font-normal normal-case" style={{ color: "var(--color-text-muted)" }}>
                ({grouped[category].length} {grouped[category].length === 1 ? "template" : "templates"})
              </span>
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
              {grouped[category].map((template: any) => (
                <div
                  key={template.template_type}
                  className="rounded-xl border p-6 transition-all group"
                  style={{ borderColor: "var(--color-border)", background: "var(--color-bg-card)" }}
                >
                  <div className="mb-3" style={{ color: "var(--color-accent-purple-light)" }}>
                    {CATEGORY_ICONS[category] || CATEGORY_ICONS["Business Operations"]}
                  </div>
                  <h3 className="text-base font-bold mb-1" style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}>
                    {template.name}
                  </h3>
                  <p className="text-xs mb-4 leading-relaxed line-clamp-2" style={{ color: "var(--color-text-secondary)" }}>
                    {template.description}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                      {template.step_count ?? template.total_steps ?? "?"} steps &middot; {template.clause_count ?? template.total_clauses ?? "?"} clauses
                    </span>
                    <button
                      onClick={() => router.push(`/documents/create/${template.template_type}`)}
                      className="px-4 py-2 rounded-lg text-xs font-medium transition-colors flex items-center gap-1.5 group-hover:shadow-lg"
                      style={{ background: "var(--color-accent-purple)", color: "var(--color-text-primary)" }}
                    >
                      Create
                      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ));
      })()}

      {/* E-Signature Requests */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider flex items-center gap-2" style={{ color: "var(--color-text-secondary)" }}>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5} style={{ color: "var(--color-accent-purple-light)" }}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
            </svg>
            Signature Requests
            {signatureReqs.filter((r) => ["draft", "sent", "partially_signed"].includes(r.status)).length > 0 && (
              <span className="inline-flex text-[10px] font-semibold px-2 py-0.5 rounded-full border bg-amber-500/15 border-amber-500/30 text-amber-400">
                {signatureReqs.filter((r) => ["draft", "sent", "partially_signed"].includes(r.status)).length} pending
              </span>
            )}
          </h2>
          <button
            onClick={() => router.push("/dashboard/signatures")}
            className="text-xs font-medium transition-colors flex items-center gap-1"
            style={{ color: "var(--color-accent-purple-light)" }}
          >
            View All
            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
          </button>
        </div>

        {signatureReqs.length === 0 ? (
          <div className="rounded-xl border p-8 text-center" style={{ borderColor: "var(--color-border)", background: "var(--color-bg-card)" }}>
            <svg className="w-10 h-10 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1} style={{ color: "var(--color-text-muted)" }}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
            </svg>
            <p className="text-xs" style={{ color: "var(--color-text-secondary)" }}>No signature requests yet</p>
            <p className="text-[10px] mt-0.5" style={{ color: "var(--color-text-muted)" }}>Finalize a document, then send it for signing</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {signatureReqs.slice(0, 4).map((req) => {
              const statusMap: Record<string, { bg: string; text: string; label: string }> = {
                draft: { bg: "bg-gray-500/15 border-gray-500/30", text: "text-gray-400", label: "Draft" },
                sent: { bg: "bg-blue-500/15 border-blue-500/30", text: "text-blue-400", label: "Sent" },
                partially_signed: { bg: "bg-amber-500/15 border-amber-500/30", text: "text-amber-400", label: "Partially Signed" },
                completed: { bg: "bg-emerald-500/15 border-emerald-500/30", text: "text-emerald-400", label: "Completed" },
                cancelled: { bg: "bg-red-500/15 border-red-500/30", text: "text-red-400", label: "Cancelled" },
                expired: { bg: "bg-gray-500/15 border-gray-500/30", text: "text-gray-400", label: "Expired" },
              };
              const badge = statusMap[req.status] || statusMap.draft;
              const signatories = Array.isArray(req.signatories) ? req.signatories : [];
              const signedCount = signatories.filter((s: any) => s.status === "signed").length;

              return (
                <button
                  key={req.id}
                  onClick={() => router.push("/dashboard/signatures")}
                  className="rounded-xl border p-4 text-left transition-all"
                  style={{ borderColor: "var(--color-border)", background: "var(--color-bg-card)" }}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="text-sm font-medium truncate flex-1 mr-2" style={{ color: "var(--color-text-primary)" }}>
                      {req.document_title || req.title || "Untitled"}
                    </h4>
                    <span className={`inline-flex text-[10px] font-semibold px-2 py-0.5 rounded-full border ${badge.bg} ${badge.text} shrink-0`}>
                      {badge.label}
                    </span>
                  </div>
                  {signatories.length > 0 && (
                    <div className="flex items-center gap-1.5 text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
                      </svg>
                      {signedCount} of {signatories.length} signed
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* User's Documents */}
      <div>
        <h2 className="text-sm font-semibold uppercase tracking-wider mb-4" style={{ color: "var(--color-text-secondary)" }}>
          Your Documents
        </h2>
        {drafts.length === 0 ? (
          <div className="rounded-xl border p-8 text-center" style={{ borderColor: "var(--color-border)", background: "var(--color-bg-card)" }}>
            <svg className="w-10 h-10 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1} style={{ color: "var(--color-text-muted)" }}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
            <p className="text-xs" style={{ color: "var(--color-text-secondary)" }}>No documents created yet</p>
            <p className="text-[10px] mt-0.5" style={{ color: "var(--color-text-muted)" }}>Choose a template above to create your first legal document</p>
          </div>
        ) : (
          <div className="rounded-xl border overflow-hidden" style={{ borderColor: "var(--color-border)", background: "var(--color-bg-card)" }}>
            <table className="w-full text-sm">
              <thead>
                <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                  <th className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Document</th>
                  <th className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Type</th>
                  <th className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Status</th>
                  <th className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Created</th>
                  <th className="text-right px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {drafts.map((draft) => {
                  const badge = STATUS_BADGES[draft.status] || STATUS_BADGES.draft;
                  return (
                    <tr key={draft.id} className="transition-colors" style={{ borderBottom: "1px solid var(--color-border)" }}>
                      <td className="px-5 py-3 font-medium" style={{ color: "var(--color-text-primary)" }}>
                        {draft.title || `Untitled ${draft.template_type.replace(/_/g, " ")}`}
                      </td>
                      <td className="px-5 py-3 capitalize" style={{ color: "var(--color-text-secondary)" }}>
                        {draft.template_type.replace(/_/g, " ")}
                      </td>
                      <td className="px-5 py-3">
                        <span className={`inline-flex text-[10px] font-semibold px-2 py-0.5 rounded-full border ${badge.bg} ${badge.text}`}>
                          {badge.label}
                        </span>
                      </td>
                      <td className="px-5 py-3 text-xs" style={{ color: "var(--color-text-secondary)" }}>
                        {draft.created_at ? new Date(draft.created_at).toLocaleDateString() : "--"}
                      </td>
                      <td className="px-5 py-3 text-right flex items-center justify-end gap-3">
                        {(draft.status === "finalized" || draft.status === "downloaded") && (
                          <button
                            onClick={() => router.push(`/documents/send-for-signing?documentId=${draft.id}`)}
                            className="text-xs font-medium transition-colors flex items-center gap-1"
                            style={{ color: "var(--color-success)" }}
                          >
                            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                            </svg>
                            Send for Signing
                          </button>
                        )}
                        <button
                          onClick={() => router.push(`/documents/create/${draft.template_type}?draft=${draft.id}`)}
                          className="text-xs font-medium transition-colors"
                          style={{ color: "var(--color-accent-purple-light)" }}
                        >
                          {draft.status === "finalized" || draft.status === "downloaded" ? "View" : "Continue"}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
