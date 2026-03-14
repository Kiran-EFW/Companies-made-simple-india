"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  getSignatureRequests,
  sendSigningEmails,
  sendSigningReminder,
  cancelSignatureRequest,
  getSignatureAuditTrail,
  getSignedDocument,
  getSignatureCertificate,
} from "@/lib/api";

const STATUS_BADGES: Record<string, { bg: string; text: string; label: string }> = {
  draft: { bg: "bg-gray-500/15 border-gray-500/30", text: "text-gray-400", label: "Draft" },
  sent: { bg: "bg-blue-500/15 border-blue-500/30", text: "text-blue-400", label: "Sent" },
  partially_signed: { bg: "bg-amber-500/15 border-amber-500/30", text: "text-amber-400", label: "Partially Signed" },
  completed: { bg: "bg-emerald-500/15 border-emerald-500/30", text: "text-emerald-400", label: "Completed" },
  cancelled: { bg: "bg-red-500/15 border-red-500/30", text: "text-red-400", label: "Cancelled" },
  expired: { bg: "bg-gray-500/15 border-gray-500/30", text: "text-gray-400", label: "Expired" },
};

const SIGNER_STATUS_ICON: Record<string, { icon: string; color: string }> = {
  signed: { icon: "check", color: "text-emerald-400" },
  pending: { icon: "clock", color: "text-amber-400" },
  email_sent: { icon: "clock", color: "text-blue-400" },
  viewed: { icon: "clock", color: "text-blue-400" },
  declined: { icon: "x", color: "text-red-400" },
};

type TabFilter = "all" | "pending" | "completed" | "expired";

export default function SignaturesPage() {
  const router = useRouter();
  const [requests, setRequests] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabFilter>("all");
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [auditTrail, setAuditTrail] = useState<any[] | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const fetchRequests = async () => {
    try {
      const data = await getSignatureRequests();
      setRequests(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error("Failed to load signature requests:", err);
      setError(err.message || "Failed to load signature requests");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  // Clear success message after 4 seconds
  useEffect(() => {
    if (successMsg) {
      const t = setTimeout(() => setSuccessMsg(null), 4000);
      return () => clearTimeout(t);
    }
  }, [successMsg]);

  const filteredRequests = requests.filter((r) => {
    if (activeTab === "all") return true;
    if (activeTab === "pending") return ["draft", "sent", "partially_signed"].includes(r.status);
    if (activeTab === "completed") return r.status === "completed";
    if (activeTab === "expired") return ["expired", "cancelled"].includes(r.status);
    return true;
  });

  const handleSendEmails = async (requestId: number) => {
    setActionLoading(`send-${requestId}`);
    try {
      await sendSigningEmails(requestId);
      setSuccessMsg("Signing emails sent successfully");
      await fetchRequests();
    } catch (err: any) {
      setError(err.message || "Failed to send emails");
    } finally {
      setActionLoading(null);
    }
  };

  const handleRemind = async (requestId: number) => {
    setActionLoading(`remind-${requestId}`);
    try {
      await sendSigningReminder(requestId);
      setSuccessMsg("Reminder sent successfully");
    } catch (err: any) {
      setError(err.message || "Failed to send reminder");
    } finally {
      setActionLoading(null);
    }
  };

  const handleCancel = async (requestId: number) => {
    if (!confirm("Are you sure you want to cancel this signing request?")) return;
    setActionLoading(`cancel-${requestId}`);
    try {
      await cancelSignatureRequest(requestId);
      setSuccessMsg("Signing request cancelled");
      await fetchRequests();
    } catch (err: any) {
      setError(err.message || "Failed to cancel request");
    } finally {
      setActionLoading(null);
    }
  };

  const handleViewAudit = async (requestId: number) => {
    if (expandedId === requestId && auditTrail) {
      setExpandedId(null);
      setAuditTrail(null);
      return;
    }
    setExpandedId(requestId);
    try {
      const trail = await getSignatureAuditTrail(requestId);
      setAuditTrail(Array.isArray(trail) ? trail : trail?.events || []);
    } catch (err: any) {
      setError(err.message || "Failed to load audit trail");
      setAuditTrail([]);
    }
  };

  const handleDownloadSigned = async (requestId: number) => {
    setActionLoading(`download-${requestId}`);
    try {
      const data = await getSignedDocument(requestId);
      if (data?.download_url) {
        window.open(data.download_url, "_blank");
      } else if (data?.url) {
        window.open(data.url, "_blank");
      } else {
        setSuccessMsg("Document download initiated");
      }
    } catch (err: any) {
      setError(err.message || "Failed to download signed document");
    } finally {
      setActionLoading(null);
    }
  };

  const handleDownloadCertificate = async (requestId: number) => {
    setActionLoading(`cert-${requestId}`);
    try {
      const data = await getSignatureCertificate(requestId);
      if (data?.download_url) {
        window.open(data.download_url, "_blank");
      } else if (data?.url) {
        window.open(data.url, "_blank");
      } else {
        setSuccessMsg("Certificate download initiated");
      }
    } catch (err: any) {
      setError(err.message || "Failed to download certificate");
    } finally {
      setActionLoading(null);
    }
  };

  const getSignedCount = (signatories: any[]) => {
    if (!Array.isArray(signatories)) return 0;
    return signatories.filter((s) => s.status === "signed").length;
  };

  const tabs: { key: TabFilter; label: string }[] = [
    { key: "all", label: "All" },
    { key: "pending", label: "Pending" },
    { key: "completed", label: "Completed" },
    { key: "expired", label: "Expired" },
  ];

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-800 rounded w-56" />
          <div className="h-4 bg-gray-800 rounded w-80" />
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-36 bg-gray-800 rounded-xl" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-5xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ fontFamily: "var(--font-display)" }}>
            E-Signatures
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Track document signing status
          </p>
        </div>
        <button
          onClick={() => router.push("/documents")}
          className="px-4 py-2 rounded-lg text-sm font-medium bg-purple-600 hover:bg-purple-500 text-white transition-colors flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          New Signature Request
        </button>
      </div>

      {/* Success Banner */}
      {successMsg && (
        <div className="rounded-lg border border-emerald-500/20 bg-emerald-500/10 p-3 flex items-center gap-2">
          <svg className="w-4 h-4 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-xs text-emerald-300 flex-1">{successMsg}</p>
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-3 flex items-center gap-2">
          <svg className="w-4 h-4 text-red-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          <p className="text-xs text-red-300 flex-1">{error}</p>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-red-300">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* Tab Filters */}
      <div className="flex gap-1 bg-gray-800/50 rounded-lg p-1 w-fit">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-1.5 rounded-md text-xs font-medium transition-colors ${
              activeTab === tab.key
                ? "bg-purple-600 text-white"
                : "text-gray-400 hover:text-white hover:bg-gray-700/50"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Request Cards */}
      {filteredRequests.length === 0 ? (
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-12 text-center">
          <svg className="w-12 h-12 text-gray-600 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12l-3-3m0 0l-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
          </svg>
          <p className="text-sm text-gray-400">No signature requests found</p>
          <p className="text-xs text-gray-500 mt-1">Create a legal document first, then send it for signing</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredRequests.map((req) => {
            const badge = STATUS_BADGES[req.status] || STATUS_BADGES.draft;
            const signatories = Array.isArray(req.signatories) ? req.signatories : [];
            const signedCount = getSignedCount(signatories);
            const totalCount = signatories.length;
            const progressPercent = totalCount > 0 ? (signedCount / totalCount) * 100 : 0;
            const isExpanded = expandedId === req.id;

            return (
              <div
                key={req.id}
                className="rounded-xl border border-gray-700 bg-gray-800/50 overflow-hidden"
              >
                {/* Card Header */}
                <div className="p-5">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1 min-w-0">
                      <h3
                        className="text-base font-bold text-white truncate"
                        style={{ fontFamily: "var(--font-display)" }}
                      >
                        {req.document_title || req.title || "Untitled Document"}
                      </h3>
                      <p className="text-xs text-gray-500 mt-0.5">
                        Created {req.created_at ? new Date(req.created_at).toLocaleDateString() : "--"}
                      </p>
                    </div>
                    <span
                      className={`inline-flex text-[10px] font-semibold px-2.5 py-0.5 rounded-full border ${badge.bg} ${badge.text} shrink-0 ml-3`}
                    >
                      {badge.label}
                    </span>
                  </div>

                  {/* Progress Bar */}
                  {totalCount > 0 && (
                    <div className="mb-3">
                      <div className="flex items-center justify-between text-[10px] text-gray-500 mb-1">
                        <span>{signedCount} of {totalCount} signed</span>
                        <span>{Math.round(progressPercent)}%</span>
                      </div>
                      <div className="w-full h-1.5 bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-purple-500 rounded-full transition-all duration-500"
                          style={{ width: `${progressPercent}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Signatories List */}
                  {signatories.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {signatories.map((s: any, idx: number) => {
                        const signerInfo = SIGNER_STATUS_ICON[s.status] || SIGNER_STATUS_ICON.pending;
                        return (
                          <div
                            key={idx}
                            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-gray-700/50 text-xs"
                          >
                            {s.status === "signed" ? (
                              <svg className={`w-3 h-3 ${signerInfo.color}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                              </svg>
                            ) : s.status === "declined" ? (
                              <svg className={`w-3 h-3 ${signerInfo.color}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                              </svg>
                            ) : (
                              <svg className={`w-3 h-3 ${signerInfo.color}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                            )}
                            <span className="text-gray-300">{s.name || s.email}</span>
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex flex-wrap gap-2">
                    {(req.status === "draft") && (
                      <button
                        onClick={() => handleSendEmails(req.id)}
                        disabled={actionLoading === `send-${req.id}`}
                        className="px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-600 hover:bg-blue-500 text-white transition-colors disabled:opacity-50 flex items-center gap-1.5"
                      >
                        {actionLoading === `send-${req.id}` ? (
                          <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        ) : (
                          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                          </svg>
                        )}
                        Send Emails
                      </button>
                    )}

                    {["sent", "partially_signed"].includes(req.status) && (
                      <button
                        onClick={() => handleRemind(req.id)}
                        disabled={actionLoading === `remind-${req.id}`}
                        className="px-3 py-1.5 rounded-lg text-xs font-medium bg-amber-600 hover:bg-amber-500 text-white transition-colors disabled:opacity-50 flex items-center gap-1.5"
                      >
                        {actionLoading === `remind-${req.id}` ? (
                          <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        ) : (
                          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
                          </svg>
                        )}
                        Remind
                      </button>
                    )}

                    {["draft", "sent", "partially_signed"].includes(req.status) && (
                      <button
                        onClick={() => handleCancel(req.id)}
                        disabled={actionLoading === `cancel-${req.id}`}
                        className="px-3 py-1.5 rounded-lg text-xs font-medium border border-red-500/30 text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-50 flex items-center gap-1.5"
                      >
                        {actionLoading === `cancel-${req.id}` ? (
                          <div className="w-3 h-3 border-2 border-red-400/30 border-t-red-400 rounded-full animate-spin" />
                        ) : (
                          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        )}
                        Cancel
                      </button>
                    )}

                    {req.status === "completed" && (
                      <>
                        <button
                          onClick={() => handleDownloadSigned(req.id)}
                          disabled={actionLoading === `download-${req.id}`}
                          className="px-3 py-1.5 rounded-lg text-xs font-medium bg-emerald-600 hover:bg-emerald-500 text-white transition-colors disabled:opacity-50 flex items-center gap-1.5"
                        >
                          {actionLoading === `download-${req.id}` ? (
                            <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          ) : (
                            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                            </svg>
                          )}
                          Signed Document
                        </button>
                        <button
                          onClick={() => handleDownloadCertificate(req.id)}
                          disabled={actionLoading === `cert-${req.id}`}
                          className="px-3 py-1.5 rounded-lg text-xs font-medium border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10 transition-colors disabled:opacity-50 flex items-center gap-1.5"
                        >
                          {actionLoading === `cert-${req.id}` ? (
                            <div className="w-3 h-3 border-2 border-emerald-400/30 border-t-emerald-400 rounded-full animate-spin" />
                          ) : (
                            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                            </svg>
                          )}
                          Audit Certificate
                        </button>
                      </>
                    )}

                    <button
                      onClick={() => handleViewAudit(req.id)}
                      className="px-3 py-1.5 rounded-lg text-xs font-medium border border-gray-600 text-gray-400 hover:text-white hover:border-gray-500 transition-colors flex items-center gap-1.5"
                    >
                      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m5.231 13.481L15 17.25m-4.5-15H5.625c-.621 0-1.125.504-1.125 1.125v16.5c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9zm3.75 11.625a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
                      </svg>
                      {isExpanded ? "Hide" : "View"} Audit Trail
                    </button>
                  </div>
                </div>

                {/* Expanded Detail: Signatories Table */}
                {isExpanded && (
                  <div className="border-t border-gray-700">
                    {/* Signatories Table */}
                    <div className="px-5 py-4">
                      <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                        Signatories
                      </h4>
                      <div className="rounded-lg border border-gray-700 overflow-hidden">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b border-gray-700 bg-gray-800/50">
                              <th className="text-left px-4 py-2 text-[10px] text-gray-500 font-medium uppercase tracking-wider">Name</th>
                              <th className="text-left px-4 py-2 text-[10px] text-gray-500 font-medium uppercase tracking-wider">Email</th>
                              <th className="text-left px-4 py-2 text-[10px] text-gray-500 font-medium uppercase tracking-wider">Designation</th>
                              <th className="text-left px-4 py-2 text-[10px] text-gray-500 font-medium uppercase tracking-wider">Status</th>
                              <th className="text-left px-4 py-2 text-[10px] text-gray-500 font-medium uppercase tracking-wider">Signed At</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-700/50">
                            {signatories.map((s: any, idx: number) => {
                              const sBadge = STATUS_BADGES[s.status] || STATUS_BADGES.draft;
                              return (
                                <tr key={idx} className="hover:bg-white/5 transition-colors">
                                  <td className="px-4 py-2 text-white text-xs">{s.name || "--"}</td>
                                  <td className="px-4 py-2 text-gray-400 text-xs">{s.email || "--"}</td>
                                  <td className="px-4 py-2 text-gray-400 text-xs">{s.designation || "--"}</td>
                                  <td className="px-4 py-2">
                                    <span className={`inline-flex text-[10px] font-semibold px-2 py-0.5 rounded-full border ${sBadge.bg} ${sBadge.text}`}>
                                      {s.status ? s.status.replace(/_/g, " ") : "pending"}
                                    </span>
                                  </td>
                                  <td className="px-4 py-2 text-gray-400 text-xs">
                                    {s.signed_at ? new Date(s.signed_at).toLocaleString() : "--"}
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Audit Trail */}
                    {auditTrail && (
                      <div className="px-5 py-4 border-t border-gray-700/50">
                        <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                          Audit Trail
                        </h4>
                        {auditTrail.length === 0 ? (
                          <p className="text-xs text-gray-500">No audit events recorded yet.</p>
                        ) : (
                          <div className="space-y-2">
                            {auditTrail.map((event: any, idx: number) => (
                              <div key={idx} className="flex items-start gap-3 text-xs">
                                <div className="w-1.5 h-1.5 rounded-full bg-purple-500 mt-1.5 shrink-0" />
                                <div className="flex-1">
                                  <span className="text-gray-300">{event.action || event.event_type || event.description}</span>
                                  {event.actor && (
                                    <span className="text-gray-500 ml-2">by {event.actor}</span>
                                  )}
                                </div>
                                <span className="text-gray-600 shrink-0">
                                  {event.timestamp || event.created_at
                                    ? new Date(event.timestamp || event.created_at).toLocaleString()
                                    : ""}
                                </span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
