"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useCompany } from "@/lib/company-context";
import {
  getSubscriptions,
  getServiceRequests,
  getPaymentReceiptUrl,
  type SubscriptionOut,
  type ServiceRequestOut,
} from "@/lib/api";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDate(iso: string | undefined | null): string {
  if (!iso) return "--";
  return new Date(iso).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function formatCurrency(amount: number): string {
  return `Rs ${amount.toLocaleString("en-IN")}`;
}

function statusColor(status: string): { bg: string; color: string } {
  switch (status) {
    case "active":
    case "completed":
    case "paid":
      return { bg: "rgba(16, 185, 129, 0.1)", color: "#10B981" };
    case "pending":
    case "in_progress":
      return { bg: "rgba(245, 158, 11, 0.1)", color: "#F59E0B" };
    case "cancelled":
    case "failed":
      return { bg: "rgba(239, 68, 68, 0.1)", color: "#EF4444" };
    default:
      return { bg: "rgba(139, 92, 246, 0.08)", color: "var(--color-text-secondary)" };
  }
}

// ---------------------------------------------------------------------------
// StatusBadge
// ---------------------------------------------------------------------------

function StatusBadge({ status }: { status: string }) {
  const { bg, color } = statusColor(status);
  return (
    <span
      style={{
        display: "inline-block",
        fontSize: 10,
        fontWeight: 600,
        padding: "2px 8px",
        borderRadius: 9999,
        background: bg,
        color,
        textTransform: "uppercase",
        letterSpacing: "0.04em",
      }}
    >
      {status.replace(/_/g, " ")}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function BillingPage() {
  const { companies, selectedCompany, selectCompany, loading: companyLoading } = useCompany();

  const [subscriptions, setSubscriptions] = useState<SubscriptionOut[]>([]);
  const [serviceRequests, setServiceRequests] = useState<ServiceRequestOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState<number | null>(null);

  // ---- Fetch data whenever the selected company changes -----------------
  const fetchBillingData = useCallback(async () => {
    if (!selectedCompany) return;
    setLoading(true);
    try {
      const [subs, reqs] = await Promise.all([
        getSubscriptions(selectedCompany.id).catch(() => [] as SubscriptionOut[]),
        getServiceRequests(selectedCompany.id).catch(() => [] as ServiceRequestOut[]),
      ]);
      setSubscriptions(subs);
      setServiceRequests(reqs);
    } catch (err) {
      console.error("Failed to fetch billing data:", err);
    } finally {
      setLoading(false);
    }
  }, [selectedCompany]);

  useEffect(() => {
    fetchBillingData();
  }, [fetchBillingData]);

  // ---- Derive active subscription --------------------------------------
  const activeSub = subscriptions.find((s) => s.status === "active") ?? null;

  // ---- Build payment history rows from service requests -----------------
  const paymentRows = serviceRequests
    .filter((r) => r.is_paid || r.status === "completed")
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  // ---- Receipt download handler ----------------------------------------
  const handleDownloadReceipt = async (requestId: number) => {
    setDownloading(requestId);
    try {
      const url = getPaymentReceiptUrl(requestId);
      const token =
        typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      window.open(`${url}${url.includes("?") ? "&" : "?"}token=${token}`, "_blank");
    } catch (err) {
      console.error("Failed to open receipt:", err);
    } finally {
      setTimeout(() => setDownloading(null), 800);
    }
  };

  // ---- Loading state ----------------------------------------------------
  if (companyLoading || (loading && subscriptions.length === 0 && serviceRequests.length === 0)) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-pulse" style={{ color: "var(--color-text-muted)" }}>Loading billing...</div>
      </div>
    );
  }

  // ---- Render -----------------------------------------------------------
  return (
    <div style={{ maxWidth: 1120, margin: "0 auto", padding: "32px 24px" }}>
        {/* Header */}
        <div style={{ marginBottom: 32 }}>
          <h1
            style={{
              fontSize: 28,
              fontWeight: 700,
              marginBottom: 6,
              fontFamily: "var(--font-display)",
              color: "var(--color-text-primary, #111827)",
            }}
          >
            Billing &amp; Payments
          </h1>
          <p
            style={{
              fontSize: 13,
              color: "var(--color-text-secondary, #6B7280)",
              borderLeft: "2px solid #8B5CF6",
              paddingLeft: 12,
            }}
          >
            Manage your subscription plan and view payment history.
          </p>
        </div>

        {/* No company fallback */}
        {!selectedCompany ? (
          <div
            style={{
              background: "#fff",
              border: "1px solid var(--color-border, #E5E7EB)",
              borderRadius: 12,
              padding: "64px 24px",
              textAlign: "center",
            }}
          >
            <p
              style={{
                fontSize: 18,
                fontWeight: 600,
                marginBottom: 8,
                color: "var(--color-text-primary, #111827)",
              }}
            >
              No company selected
            </p>
            <p style={{ fontSize: 13, color: "var(--color-text-secondary, #6B7280)", marginBottom: 24 }}>
              Register a company first to see your billing information.
            </p>
            <Link
              href="/pricing"
              style={{
                display: "inline-block",
                fontSize: 13,
                fontWeight: 600,
                padding: "10px 24px",
                borderRadius: 8,
                background: "#8B5CF6",
                color: "#fff",
                textDecoration: "none",
              }}
            >
              Get Started
            </Link>
          </div>
        ) : (
          <>
            {/* ====== Current Plan Card ====== */}
            <div
              style={{
                background: "#fff",
                border: "1px solid var(--color-border, #E5E7EB)",
                borderRadius: 12,
                padding: 24,
                marginBottom: 32,
              }}
            >
              <h2
                style={{
                  fontSize: 11,
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                  color: "var(--color-text-secondary, #6B7280)",
                  marginBottom: 16,
                }}
              >
                Current Plan
              </h2>

              {activeSub ? (
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    justifyContent: "space-between",
                    alignItems: "center",
                    gap: 16,
                  }}
                >
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                      <span
                        style={{
                          fontSize: 20,
                          fontWeight: 700,
                          color: "var(--color-text-primary, #111827)",
                        }}
                      >
                        {activeSub.plan_name}
                      </span>
                      <StatusBadge status={activeSub.status} />
                    </div>

                    <div
                      style={{
                        display: "flex",
                        flexWrap: "wrap",
                        gap: 24,
                        fontSize: 13,
                        color: "var(--color-text-secondary, #6B7280)",
                      }}
                    >
                      <span>
                        <strong style={{ color: "var(--color-text-primary, #111827)" }}>
                          {formatCurrency(activeSub.amount)}
                        </strong>{" "}
                        / {activeSub.interval === "annual" ? "year" : "month"}
                      </span>
                      {activeSub.current_period_start && (
                        <span>
                          Period: {formatDate(activeSub.current_period_start)} &ndash;{" "}
                          {formatDate(activeSub.current_period_end)}
                        </span>
                      )}
                    </div>
                  </div>

                  <Link
                    href="/services"
                    style={{
                      fontSize: 12,
                      fontWeight: 600,
                      padding: "8px 20px",
                      borderRadius: 8,
                      border: "1px solid var(--color-border, #E5E7EB)",
                      color: "var(--color-text-primary, #111827)",
                      textDecoration: "none",
                      background: "#fff",
                    }}
                  >
                    Change Plan
                  </Link>
                </div>
              ) : (
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    justifyContent: "space-between",
                    alignItems: "center",
                    gap: 16,
                    padding: "20px 0",
                  }}
                >
                  <div>
                    <p
                      style={{
                        fontSize: 16,
                        fontWeight: 600,
                        color: "var(--color-text-primary, #111827)",
                        marginBottom: 4,
                      }}
                    >
                      No active plan
                    </p>
                    <p style={{ fontSize: 13, color: "var(--color-text-secondary, #6B7280)" }}>
                      Subscribe to a compliance plan and let us handle the filings for you.
                    </p>
                  </div>

                  <Link
                    href="/services"
                    style={{
                      display: "inline-block",
                      fontSize: 13,
                      fontWeight: 600,
                      padding: "10px 24px",
                      borderRadius: 8,
                      background: "#8B5CF6",
                      color: "#fff",
                      textDecoration: "none",
                    }}
                  >
                    Browse Plans
                  </Link>
                </div>
              )}

              {/* Show inactive / cancelled subscriptions if any */}
              {subscriptions.filter((s) => s.status !== "active").length > 0 && (
                <div style={{ marginTop: 20, borderTop: "1px solid var(--color-border, #E5E7EB)", paddingTop: 16 }}>
                  <p
                    style={{
                      fontSize: 11,
                      fontWeight: 600,
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                      color: "var(--color-text-secondary, #6B7280)",
                      marginBottom: 10,
                    }}
                  >
                    Past Subscriptions
                  </p>
                  <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                    {subscriptions
                      .filter((s) => s.status !== "active")
                      .map((sub) => (
                        <div
                          key={sub.id}
                          style={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between",
                            padding: "10px 14px",
                            borderRadius: 8,
                            background: "#F9FAFB",
                            border: "1px solid var(--color-border, #E5E7EB)",
                            fontSize: 13,
                          }}
                        >
                          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                            <span style={{ fontWeight: 600, color: "var(--color-text-primary, #111827)" }}>
                              {sub.plan_name}
                            </span>
                            <StatusBadge status={sub.status} />
                          </div>
                          <span style={{ color: "var(--color-text-secondary, #6B7280)", fontSize: 12 }}>
                            {formatDate(sub.created_at)}
                            {sub.cancelled_at && <> &mdash; Cancelled {formatDate(sub.cancelled_at)}</>}
                          </span>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>

            {/* ====== Payment History Table ====== */}
            <div
              style={{
                background: "#fff",
                border: "1px solid var(--color-border, #E5E7EB)",
                borderRadius: 12,
                overflow: "hidden",
              }}
            >
              <div style={{ padding: "20px 24px", borderBottom: "1px solid var(--color-border, #E5E7EB)" }}>
                <h2
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    textTransform: "uppercase",
                    letterSpacing: "0.06em",
                    color: "var(--color-text-secondary, #6B7280)",
                  }}
                >
                  Payment History
                </h2>
              </div>

              {paymentRows.length === 0 ? (
                <div style={{ padding: "48px 24px", textAlign: "center" }}>
                  <p
                    style={{
                      fontSize: 14,
                      fontWeight: 500,
                      color: "var(--color-text-primary, #111827)",
                      marginBottom: 4,
                    }}
                  >
                    No payments yet
                  </p>
                  <p style={{ fontSize: 13, color: "var(--color-text-secondary, #6B7280)" }}>
                    Payments for services and subscriptions will appear here.
                  </p>
                </div>
              ) : (
                <div style={{ overflowX: "auto" }}>
                  <table
                    style={{
                      width: "100%",
                      borderCollapse: "collapse",
                      fontSize: 13,
                      minWidth: 640,
                    }}
                  >
                    <thead>
                      <tr
                        style={{
                          borderBottom: "1px solid var(--color-border, #E5E7EB)",
                          background: "#F9FAFB",
                        }}
                      >
                        {["Date", "Description", "Amount", "Status", "Receipt"].map((h) => (
                          <th
                            key={h}
                            style={{
                              padding: "10px 16px",
                              textAlign: h === "Amount" ? "right" : "left",
                              fontWeight: 600,
                              fontSize: 11,
                              textTransform: "uppercase",
                              letterSpacing: "0.05em",
                              color: "var(--color-text-secondary, #6B7280)",
                              whiteSpace: "nowrap",
                            }}
                          >
                            {h}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {paymentRows.map((req) => (
                        <tr
                          key={req.id}
                          style={{
                            borderBottom: "1px solid var(--color-border, #E5E7EB)",
                          }}
                        >
                          <td
                            style={{
                              padding: "14px 16px",
                              whiteSpace: "nowrap",
                              color: "var(--color-text-primary, #111827)",
                            }}
                          >
                            {formatDate(req.created_at)}
                          </td>
                          <td
                            style={{
                              padding: "14px 16px",
                              color: "var(--color-text-primary, #111827)",
                            }}
                          >
                            <div>
                              <span style={{ fontWeight: 500 }}>{req.service_name}</span>
                              <br />
                              <span
                                style={{
                                  fontSize: 11,
                                  color: "var(--color-text-secondary, #6B7280)",
                                }}
                              >
                                {req.category?.replace(/_/g, " ")}
                              </span>
                            </div>
                          </td>
                          <td
                            style={{
                              padding: "14px 16px",
                              textAlign: "right",
                              fontWeight: 600,
                              fontVariantNumeric: "tabular-nums",
                              whiteSpace: "nowrap",
                              color: "var(--color-text-primary, #111827)",
                            }}
                          >
                            {formatCurrency(req.total_amount)}
                          </td>
                          <td style={{ padding: "14px 16px" }}>
                            <StatusBadge status={req.is_paid ? "paid" : req.status} />
                          </td>
                          <td style={{ padding: "14px 16px" }}>
                            {req.is_paid ? (
                              <button
                                onClick={() => handleDownloadReceipt(req.id)}
                                disabled={downloading === req.id}
                                style={{
                                  fontSize: 12,
                                  fontWeight: 600,
                                  color: "#8B5CF6",
                                  background: "none",
                                  border: "none",
                                  cursor: downloading === req.id ? "wait" : "pointer",
                                  padding: 0,
                                  textDecoration: "none",
                                  opacity: downloading === req.id ? 0.5 : 1,
                                }}
                              >
                                {downloading === req.id ? "Opening..." : "Download"}
                              </button>
                            ) : (
                              <span
                                style={{
                                  fontSize: 12,
                                  color: "var(--color-text-secondary, #6B7280)",
                                }}
                              >
                                --
                              </span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* ====== All Service Requests (including unpaid) ====== */}
            {serviceRequests.filter((r) => !r.is_paid && r.status !== "completed").length > 0 && (
              <div
                style={{
                  background: "#fff",
                  border: "1px solid var(--color-border, #E5E7EB)",
                  borderRadius: 12,
                  overflow: "hidden",
                  marginTop: 32,
                }}
              >
                <div style={{ padding: "20px 24px", borderBottom: "1px solid var(--color-border, #E5E7EB)" }}>
                  <h2
                    style={{
                      fontSize: 11,
                      fontWeight: 700,
                      textTransform: "uppercase",
                      letterSpacing: "0.06em",
                      color: "var(--color-text-secondary, #6B7280)",
                    }}
                  >
                    Pending Service Requests
                  </h2>
                </div>
                <div style={{ overflowX: "auto" }}>
                  <table
                    style={{
                      width: "100%",
                      borderCollapse: "collapse",
                      fontSize: 13,
                      minWidth: 560,
                    }}
                  >
                    <thead>
                      <tr
                        style={{
                          borderBottom: "1px solid var(--color-border, #E5E7EB)",
                          background: "#F9FAFB",
                        }}
                      >
                        {["Date", "Service", "Amount", "Status"].map((h) => (
                          <th
                            key={h}
                            style={{
                              padding: "10px 16px",
                              textAlign: h === "Amount" ? "right" : "left",
                              fontWeight: 600,
                              fontSize: 11,
                              textTransform: "uppercase",
                              letterSpacing: "0.05em",
                              color: "var(--color-text-secondary, #6B7280)",
                              whiteSpace: "nowrap",
                            }}
                          >
                            {h}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {serviceRequests
                        .filter((r) => !r.is_paid && r.status !== "completed")
                        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                        .map((req) => (
                          <tr key={req.id} style={{ borderBottom: "1px solid var(--color-border, #E5E7EB)" }}>
                            <td
                              style={{
                                padding: "14px 16px",
                                whiteSpace: "nowrap",
                                color: "var(--color-text-primary, #111827)",
                              }}
                            >
                              {formatDate(req.created_at)}
                            </td>
                            <td style={{ padding: "14px 16px", color: "var(--color-text-primary, #111827)" }}>
                              <span style={{ fontWeight: 500 }}>{req.service_name}</span>
                            </td>
                            <td
                              style={{
                                padding: "14px 16px",
                                textAlign: "right",
                                fontWeight: 600,
                                fontVariantNumeric: "tabular-nums",
                                whiteSpace: "nowrap",
                                color: "var(--color-text-primary, #111827)",
                              }}
                            >
                              {formatCurrency(req.total_amount)}
                            </td>
                            <td style={{ padding: "14px 16px" }}>
                              <StatusBadge status={req.status} />
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </div>

  );
}
