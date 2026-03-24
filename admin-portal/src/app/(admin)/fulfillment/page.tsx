"use client";

import { useState, useEffect, useCallback } from "react";
import {
  getAdminServiceRequests,
  getMarketplacePartners,
  getAvailablePartners,
  verifyPartner,
  assignToPartner,
  getSettlements,
  markSettlementPaid,
} from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type Tab = "queue" | "partners" | "settlements";

interface AssignModalState {
  open: boolean;
  requestId: number | null;
  requestName: string;
}

interface PayFormState {
  settlementId: number | null;
  paymentReference: string;
  invoiceNumber: string;
}

// ---------------------------------------------------------------------------
// Style helpers
// ---------------------------------------------------------------------------

const SETTLEMENT_STATUS_STYLES: Record<string, React.CSSProperties> = {
  pending: { background: "rgba(245, 158, 11, 0.1)", color: "var(--color-warning)" },
  invoice_received: { background: "rgba(59, 130, 246, 0.1)", color: "var(--color-info)" },
  approved: { background: "rgba(139, 92, 246, 0.1)", color: "rgb(139, 92, 246)" },
  paid: { background: "rgba(16, 185, 129, 0.1)", color: "var(--color-success)" },
};

function formatRupees(amount: number | null | undefined): string {
  return `Rs ${(amount || 0).toLocaleString("en-IN")}`;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function FulfillmentPage() {
  const [activeTab, setActiveTab] = useState<Tab>("queue");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Tab 1 - Fulfillment Queue
  const [queueRequests, setQueueRequests] = useState<any[]>([]);
  const [availablePartners, setAvailablePartners] = useState<any[]>([]);
  const [assignModal, setAssignModal] = useState<AssignModalState>({
    open: false,
    requestId: null,
    requestName: "",
  });
  const [assigning, setAssigning] = useState(false);

  // Tab 2 - Partners
  const [partners, setPartners] = useState<any[]>([]);
  const [verifyingId, setVerifyingId] = useState<number | null>(null);

  // Tab 3 - Settlements
  const [settlements, setSettlements] = useState<any[]>([]);
  const [payForm, setPayForm] = useState<PayFormState>({
    settlementId: null,
    paymentReference: "",
    invoiceNumber: "",
  });
  const [markingPaid, setMarkingPaid] = useState(false);

  // ---------------------------------------------------------------------------
  // Data loading
  // ---------------------------------------------------------------------------

  const loadQueue = useCallback(async () => {
    try {
      // Fetch requests that are accepted or in_progress (paid but unassigned to a partner)
      const [acceptedData, inProgressData] = await Promise.all([
        getAdminServiceRequests({ status: "accepted" }),
        getAdminServiceRequests({ status: "in_progress" }),
      ]);
      const combined = [
        ...(acceptedData.requests || []),
        ...(inProgressData.requests || []),
      ];
      setQueueRequests(combined);
    } catch (err: any) {
      console.error("Failed to load fulfillment queue:", err);
      setError(err.message || "Failed to load fulfillment queue");
    }
  }, []);

  const loadPartners = useCallback(async () => {
    try {
      const data = await getMarketplacePartners();
      setPartners(data || []);
    } catch (err: any) {
      console.error("Failed to load partners:", err);
      setError(err.message || "Failed to load partners");
    }
  }, []);

  const loadSettlements = useCallback(async () => {
    try {
      const data = await getSettlements();
      setSettlements(data || []);
    } catch (err: any) {
      console.error("Failed to load settlements:", err);
      setError(err.message || "Failed to load settlements");
    }
  }, []);

  const loadAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    await Promise.all([loadQueue(), loadPartners(), loadSettlements()]);
    setLoading(false);
  }, [loadQueue, loadPartners, loadSettlements]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  // ---------------------------------------------------------------------------
  // Actions
  // ---------------------------------------------------------------------------

  const openAssignModal = async (requestId: number, serviceName: string) => {
    setAssignModal({ open: true, requestId, requestName: serviceName });
    try {
      const data = await getAvailablePartners();
      setAvailablePartners(data || []);
    } catch (err) {
      console.error("Failed to load available partners:", err);
      setAvailablePartners([]);
    }
  };

  const handleAssign = async (partnerId: number) => {
    if (!assignModal.requestId) return;
    setAssigning(true);
    try {
      await assignToPartner({
        service_request_id: assignModal.requestId,
        partner_id: partnerId,
      });
      setAssignModal({ open: false, requestId: null, requestName: "" });
      await loadQueue();
    } catch (err: any) {
      console.error("Assignment failed:", err);
      setError(err.message || "Assignment failed");
    } finally {
      setAssigning(false);
    }
  };

  const handleVerifyPartner = async (partnerId: number) => {
    setVerifyingId(partnerId);
    try {
      await verifyPartner(partnerId);
      await loadPartners();
    } catch (err: any) {
      console.error("Verify failed:", err);
      setError(err.message || "Verification failed");
    } finally {
      setVerifyingId(null);
    }
  };

  const handleMarkPaid = async () => {
    if (!payForm.settlementId || !payForm.paymentReference.trim()) return;
    setMarkingPaid(true);
    try {
      await markSettlementPaid(payForm.settlementId, {
        payment_reference: payForm.paymentReference.trim(),
        partner_invoice_number: payForm.invoiceNumber.trim() || undefined,
      });
      setPayForm({ settlementId: null, paymentReference: "", invoiceNumber: "" });
      await loadSettlements();
    } catch (err: any) {
      console.error("Mark paid failed:", err);
      setError(err.message || "Failed to mark settlement as paid");
    } finally {
      setMarkingPaid(false);
    }
  };

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  const TABS: { key: Tab; label: string; count: number }[] = [
    { key: "queue", label: "Fulfillment Queue", count: queueRequests.length },
    { key: "partners", label: "Partners", count: partners.length },
    { key: "settlements", label: "Settlements", count: settlements.length },
  ];

  return (
    <div className="p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8">
        <h1
          className="text-2xl font-bold"
          style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
        >
          Marketplace Fulfillment
        </h1>
        <p className="text-sm mt-1" style={{ color: "var(--color-text-secondary)" }}>
          Assign work to partners, review deliverables, and manage settlements
        </p>
      </div>

      {/* Error Banner */}
      {error && (
        <div
          className="rounded-lg px-4 py-3 mb-6 text-sm flex items-center justify-between"
          style={{ background: "rgba(239, 68, 68, 0.08)", border: "1px solid rgba(239, 68, 68, 0.2)", color: "var(--color-error)" }}
        >
          <span>{error}</span>
          <button
            onClick={() => setError(null)}
            className="ml-4 text-xs font-medium underline"
            style={{ color: "var(--color-error)" }}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[
          { label: "Pending Assignment", value: queueRequests.length, color: "var(--color-warning)" },
          { label: "Registered Partners", value: partners.length, color: "var(--color-info)" },
          { label: "Verified Partners", value: partners.filter((p) => p.is_verified).length, color: "var(--color-success)" },
          { label: "Pending Settlements", value: settlements.filter((s) => s.status === "pending").length, color: "var(--color-accent-purple)" },
        ].map((card, i) => (
          <div key={i} className="glass-card rounded-xl p-4">
            <p className="text-[10px] mb-1" style={{ color: "var(--color-text-muted)" }}>
              {card.label}
            </p>
            <p className="text-2xl font-bold" style={{ color: card.color }}>
              {card.value}
            </p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 glass-card rounded-lg p-1 w-fit mb-6">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className="px-4 py-2 rounded-md text-sm font-medium transition"
            style={
              activeTab === tab.key
                ? { background: "var(--color-accent-purple)", color: "#fff" }
                : { color: "var(--color-text-secondary)" }
            }
          >
            {tab.label}
            <span className="ml-2 text-xs opacity-70">({tab.count})</span>
          </button>
        ))}
      </div>

      {/* ---------- Tab 1: Fulfillment Queue ---------- */}
      {activeTab === "queue" && (
        <>
          {loading ? (
            <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>
              Loading...
            </div>
          ) : queueRequests.length === 0 ? (
            <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>
              No service requests pending partner assignment.
            </div>
          ) : (
            <div className="glass-card rounded-xl overflow-x-auto">
              <table className="w-full text-sm min-w-[640px]">
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                    {["ID", "Service", "Company", "Amount", "Status", "Date", "Action"].map((h) => (
                      <th
                        key={h}
                        className="text-left px-4 py-3 text-xs font-medium"
                        style={{ color: "var(--color-text-muted)" }}
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {queueRequests.map((req) => (
                    <tr key={req.id} style={{ borderBottom: "1px solid var(--color-border)" }}>
                      <td className="px-4 py-3 text-xs" style={{ color: "var(--color-text-muted)" }}>
                        #{req.id}
                      </td>
                      <td className="px-4 py-3">
                        <p className="text-xs font-medium" style={{ color: "var(--color-text-primary)" }}>
                          {req.service_name}
                        </p>
                        {req.category && (
                          <p className="text-[10px] capitalize" style={{ color: "var(--color-text-muted)" }}>
                            {req.category}
                          </p>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <p className="text-xs font-medium" style={{ color: "var(--color-text-primary)" }}>
                          {req.company_name || `Company #${req.company_id}`}
                        </p>
                        {req.user_email && (
                          <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                            {req.user_email}
                          </p>
                        )}
                      </td>
                      <td className="px-4 py-3 text-xs font-semibold" style={{ color: "var(--color-text-primary)" }}>
                        {formatRupees(req.total_amount)}
                        {req.is_paid && (
                          <span className="ml-1 text-[10px]" style={{ color: "var(--color-success)" }}>
                            Paid
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
                          style={{
                            background: "var(--color-info-light)",
                            color: "var(--color-info)",
                          }}
                        >
                          {req.status?.replace(/_/g, " ")}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                        {req.created_at ? new Date(req.created_at).toLocaleDateString("en-IN") : "--"}
                      </td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => openAssignModal(req.id, req.service_name || `Request #${req.id}`)}
                          className="text-[11px] font-medium px-3 py-1.5 rounded-lg transition-colors"
                          style={{
                            background: "rgba(20, 184, 166, 0.12)",
                            color: "rgb(20, 184, 166)",
                            border: "1px solid rgba(20, 184, 166, 0.25)",
                          }}
                        >
                          Assign Partner
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {/* ---------- Tab 2: Partners ---------- */}
      {activeTab === "partners" && (
        <>
          {loading ? (
            <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>
              Loading...
            </div>
          ) : partners.length === 0 ? (
            <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>
              No registered partners yet.
            </div>
          ) : (
            <div className="glass-card rounded-xl overflow-x-auto">
              <table className="w-full text-sm min-w-[900px]">
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                    {[
                      "ID",
                      "Membership #",
                      "Type",
                      "Firm",
                      "Verified",
                      "Rating",
                      "Completed",
                      "Earned",
                      "Accepting Work",
                      "Actions",
                    ].map((h) => (
                      <th
                        key={h}
                        className="text-left px-4 py-3 text-xs font-medium"
                        style={{ color: "var(--color-text-muted)" }}
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {partners.map((p) => (
                    <tr key={p.id} style={{ borderBottom: "1px solid var(--color-border)" }}>
                      <td className="px-4 py-3 text-xs" style={{ color: "var(--color-text-muted)" }}>
                        #{p.id}
                      </td>
                      <td className="px-4 py-3 text-xs font-mono" style={{ color: "var(--color-text-primary)" }}>
                        {p.membership_number || "--"}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className="text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase"
                          style={{
                            background: "rgba(139, 92, 246, 0.08)",
                            color: "rgb(139, 92, 246)",
                          }}
                        >
                          {p.membership_type || "--"}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <p className="text-xs font-medium" style={{ color: "var(--color-text-primary)" }}>
                          {p.firm_name || "--"}
                        </p>
                        {p.specializations && p.specializations.length > 0 && (
                          <p className="text-[10px] mt-0.5 truncate max-w-[160px]" style={{ color: "var(--color-text-muted)" }}>
                            {p.specializations.join(", ")}
                          </p>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {p.is_verified ? (
                          <span
                            className="text-[10px] font-semibold px-2 py-0.5 rounded-full inline-flex items-center gap-1"
                            style={{ background: "rgba(16, 185, 129, 0.1)", color: "var(--color-success)" }}
                          >
                            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                            </svg>
                            Verified
                          </span>
                        ) : (
                          <span
                            className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
                            style={{ background: "rgba(245, 158, 11, 0.1)", color: "var(--color-warning)" }}
                          >
                            Unverified
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1">
                          <svg className="w-3.5 h-3.5" viewBox="0 0 20 20" fill="rgb(250, 204, 21)">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                          <span className="text-xs font-medium" style={{ color: "var(--color-text-primary)" }}>
                            {p.avg_rating != null ? Number(p.avg_rating).toFixed(1) : "--"}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-xs font-medium" style={{ color: "var(--color-text-primary)" }}>
                        {p.total_completed ?? 0}
                      </td>
                      <td className="px-4 py-3 text-xs font-semibold" style={{ color: "var(--color-success)" }}>
                        {formatRupees(p.total_earned)}
                      </td>
                      <td className="px-4 py-3">
                        {p.is_accepting_work ? (
                          <span
                            className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
                            style={{ background: "rgba(16, 185, 129, 0.1)", color: "var(--color-success)" }}
                          >
                            Active
                          </span>
                        ) : (
                          <span
                            className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
                            style={{ background: "rgba(148,163,184,0.1)", color: "var(--color-text-muted)" }}
                          >
                            Paused
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {!p.is_verified && (
                          <button
                            onClick={() => handleVerifyPartner(p.id)}
                            disabled={verifyingId === p.id}
                            className="text-[11px] font-medium px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
                            style={{
                              background: "rgba(20, 184, 166, 0.12)",
                              color: "rgb(20, 184, 166)",
                              border: "1px solid rgba(20, 184, 166, 0.25)",
                            }}
                          >
                            {verifyingId === p.id ? "Verifying..." : "Verify"}
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {/* ---------- Tab 3: Settlements ---------- */}
      {activeTab === "settlements" && (
        <>
          {loading ? (
            <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>
              Loading...
            </div>
          ) : settlements.length === 0 ? (
            <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>
              No settlements found.
            </div>
          ) : (
            <div className="glass-card rounded-xl overflow-x-auto">
              <table className="w-full text-sm min-w-[1000px]">
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                    {[
                      "ID",
                      "Fulfillment",
                      "Partner",
                      "Gross",
                      "TDS",
                      "Net",
                      "GST",
                      "Status",
                      "Invoice #",
                      "Payment Ref",
                      "Paid At",
                      "Actions",
                    ].map((h) => (
                      <th
                        key={h}
                        className="text-left px-4 py-3 text-xs font-medium whitespace-nowrap"
                        style={{ color: "var(--color-text-muted)" }}
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {settlements.map((s) => (
                    <tr key={s.id} style={{ borderBottom: "1px solid var(--color-border)" }}>
                      <td className="px-4 py-3 text-xs" style={{ color: "var(--color-text-muted)" }}>
                        #{s.id}
                      </td>
                      <td className="px-4 py-3 text-xs" style={{ color: "var(--color-text-primary)" }}>
                        #{s.fulfillment_id}
                      </td>
                      <td className="px-4 py-3 text-xs" style={{ color: "var(--color-text-primary)" }}>
                        #{s.partner_id}
                      </td>
                      <td className="px-4 py-3 text-xs font-semibold" style={{ color: "var(--color-text-primary)" }}>
                        {formatRupees(s.gross_amount)}
                      </td>
                      <td className="px-4 py-3 text-xs" style={{ color: "var(--color-error)" }}>
                        {formatRupees(s.tds_amount)}
                      </td>
                      <td className="px-4 py-3 text-xs font-semibold" style={{ color: "var(--color-success)" }}>
                        {formatRupees(s.net_amount)}
                      </td>
                      <td className="px-4 py-3 text-xs" style={{ color: "var(--color-text-secondary)" }}>
                        {formatRupees(s.gst_amount)}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className="text-[10px] font-semibold px-2 py-0.5 rounded-full whitespace-nowrap"
                          style={SETTLEMENT_STATUS_STYLES[s.status] || {}}
                        >
                          {s.status?.replace(/_/g, " ")}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-[10px] font-mono" style={{ color: "var(--color-text-secondary)" }}>
                        {s.partner_invoice_number || "--"}
                      </td>
                      <td className="px-4 py-3 text-[10px] font-mono" style={{ color: "var(--color-text-secondary)" }}>
                        {s.payment_reference || "--"}
                      </td>
                      <td className="px-4 py-3 text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                        {s.paid_at ? new Date(s.paid_at).toLocaleDateString("en-IN") : "--"}
                      </td>
                      <td className="px-4 py-3">
                        {s.status !== "paid" && (
                          <>
                            {payForm.settlementId === s.id ? (
                              <div className="flex flex-col gap-2 min-w-[200px]">
                                <input
                                  type="text"
                                  placeholder="Payment Reference *"
                                  value={payForm.paymentReference}
                                  onChange={(e) =>
                                    setPayForm((prev) => ({ ...prev, paymentReference: e.target.value }))
                                  }
                                  className="text-[11px] rounded-md px-2.5 py-1.5 w-full outline-none focus:ring-1"
                                  style={{
                                    background: "var(--color-bg-input, var(--color-bg-secondary))",
                                    color: "var(--color-text-primary)",
                                    border: "1px solid var(--color-border)",
                                  }}
                                />
                                <input
                                  type="text"
                                  placeholder="Invoice # (optional)"
                                  value={payForm.invoiceNumber}
                                  onChange={(e) =>
                                    setPayForm((prev) => ({ ...prev, invoiceNumber: e.target.value }))
                                  }
                                  className="text-[11px] rounded-md px-2.5 py-1.5 w-full outline-none focus:ring-1"
                                  style={{
                                    background: "var(--color-bg-input, var(--color-bg-secondary))",
                                    color: "var(--color-text-primary)",
                                    border: "1px solid var(--color-border)",
                                  }}
                                />
                                <div className="flex gap-2">
                                  <button
                                    onClick={handleMarkPaid}
                                    disabled={markingPaid || !payForm.paymentReference.trim()}
                                    className="text-[10px] font-medium px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
                                    style={{
                                      background: "rgba(16, 185, 129, 0.12)",
                                      color: "var(--color-success)",
                                      border: "1px solid rgba(16, 185, 129, 0.25)",
                                    }}
                                  >
                                    {markingPaid ? "Saving..." : "Submit"}
                                  </button>
                                  <button
                                    onClick={() =>
                                      setPayForm({
                                        settlementId: null,
                                        paymentReference: "",
                                        invoiceNumber: "",
                                      })
                                    }
                                    className="text-[10px] font-medium px-3 py-1.5 rounded-lg transition-colors"
                                    style={{
                                      background: "rgba(239, 68, 68, 0.08)",
                                      color: "var(--color-error)",
                                      border: "1px solid rgba(239, 68, 68, 0.15)",
                                    }}
                                  >
                                    Cancel
                                  </button>
                                </div>
                              </div>
                            ) : (
                              <button
                                onClick={() =>
                                  setPayForm({
                                    settlementId: s.id,
                                    paymentReference: "",
                                    invoiceNumber: "",
                                  })
                                }
                                className="text-[11px] font-medium px-3 py-1.5 rounded-lg transition-colors whitespace-nowrap"
                                style={{
                                  background: "rgba(20, 184, 166, 0.12)",
                                  color: "rgb(20, 184, 166)",
                                  border: "1px solid rgba(20, 184, 166, 0.25)",
                                }}
                              >
                                Mark Paid
                              </button>
                            )}
                          </>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {/* ---------- Assign Partner Modal ---------- */}
      {assignModal.open && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ background: "rgba(0,0,0,0.5)" }}
          onClick={() => setAssignModal({ open: false, requestId: null, requestName: "" })}
        >
          <div
            className="glass-card rounded-2xl w-full max-w-lg max-h-[80vh] overflow-y-auto"
            style={{ border: "1px solid var(--color-border)" }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="p-5" style={{ borderBottom: "1px solid var(--color-border)" }}>
              <div className="flex items-center justify-between">
                <div>
                  <h2
                    className="text-lg font-bold"
                    style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}
                  >
                    Assign Partner
                  </h2>
                  <p className="text-xs mt-0.5" style={{ color: "var(--color-text-muted)" }}>
                    {assignModal.requestName}
                  </p>
                </div>
                <button
                  onClick={() =>
                    setAssignModal({ open: false, requestId: null, requestName: "" })
                  }
                  className="w-8 h-8 flex items-center justify-center rounded-lg transition-colors"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Partner List */}
            <div className="p-5 space-y-3">
              {availablePartners.length === 0 ? (
                <div className="text-center py-8" style={{ color: "var(--color-text-muted)" }}>
                  <p className="text-sm">No partners available</p>
                  <p className="text-xs mt-1">All partners may be at full capacity or none are registered.</p>
                </div>
              ) : (
                availablePartners.map((partner) => (
                  <div
                    key={partner.user_id}
                    className="rounded-xl p-4 transition-colors cursor-pointer"
                    style={{
                      border: "1px solid var(--color-border)",
                      background: "var(--color-bg-secondary, rgba(255,255,255,0.02))",
                    }}
                    onClick={() => !assigning && handleAssign(partner.user_id)}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLElement).style.borderColor = "rgba(20, 184, 166, 0.4)";
                      (e.currentTarget as HTMLElement).style.background = "rgba(20, 184, 166, 0.04)";
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLElement).style.borderColor = "var(--color-border)";
                      (e.currentTarget as HTMLElement).style.background = "var(--color-bg-secondary, rgba(255,255,255,0.02))";
                    }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <p className="text-sm font-medium" style={{ color: "var(--color-text-primary)" }}>
                          {partner.full_name || partner.email}
                        </p>
                        {partner.firm_name && (
                          <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                            {partner.firm_name}
                          </p>
                        )}
                      </div>
                      <span
                        className="text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase"
                        style={{
                          background: "rgba(139, 92, 246, 0.08)",
                          color: "rgb(139, 92, 246)",
                        }}
                      >
                        {partner.membership_type || "--"}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-[11px]">
                      {/* Rating */}
                      <div className="flex items-center gap-1">
                        <svg className="w-3 h-3" viewBox="0 0 20 20" fill="rgb(250, 204, 21)">
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                        <span style={{ color: "var(--color-text-primary)" }}>
                          {partner.avg_rating != null ? Number(partner.avg_rating).toFixed(1) : "--"}
                        </span>
                      </div>
                      {/* Completed */}
                      <span style={{ color: "var(--color-text-secondary)" }}>
                        {partner.total_completed ?? 0} completed
                      </span>
                      {/* Load */}
                      <span
                        style={{
                          color:
                            (partner.current_assignments || 0) >= (partner.max_concurrent_assignments || 5)
                              ? "var(--color-error)"
                              : "var(--color-text-secondary)",
                        }}
                      >
                        {partner.current_assignments || 0} / {partner.max_concurrent_assignments || 5} slots
                      </span>
                    </div>
                    {partner.specializations && partner.specializations.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {partner.specializations.map((spec: string) => (
                          <span
                            key={spec}
                            className="text-[9px] px-1.5 py-0.5 rounded"
                            style={{
                              background: "var(--color-bg-secondary, rgba(255,255,255,0.05))",
                              color: "var(--color-text-muted)",
                              border: "1px solid var(--color-border)",
                            }}
                          >
                            {spec}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>

            {/* Modal Footer */}
            {assigning && (
              <div className="px-5 pb-5">
                <div
                  className="text-center text-xs py-2 rounded-lg"
                  style={{ background: "rgba(20, 184, 166, 0.06)", color: "rgb(20, 184, 166)" }}
                >
                  Assigning partner...
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
