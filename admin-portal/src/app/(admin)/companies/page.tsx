"use client";

import { useEffect, useState } from "react";
import { getAdminCompanies } from "@/lib/api";
import Link from "next/link";

function getStatusBadgeStyle(status: string): React.CSSProperties {
  if (["incorporated", "fully_setup", "bank_account_opened"].includes(status))
    return { background: "rgba(16, 185, 129, 0.15)", color: "var(--color-success)", borderColor: "rgba(16, 185, 129, 0.3)" };
  if (["draft", "entity_selected"].includes(status))
    return { background: "rgba(107, 114, 128, 0.15)", color: "var(--color-text-secondary)", borderColor: "rgba(107, 114, 128, 0.3)" };
  if (status.includes("rejected") || status.includes("query"))
    return { background: "rgba(239, 68, 68, 0.15)", color: "var(--color-error)", borderColor: "rgba(239, 68, 68, 0.3)" };
  if (status.includes("pending"))
    return { background: "rgba(245, 158, 11, 0.15)", color: "var(--color-warning)", borderColor: "rgba(245, 158, 11, 0.3)" };
  return { background: "rgba(59, 130, 246, 0.15)", color: "var(--color-info)", borderColor: "rgba(59, 130, 246, 0.3)" };
}

function getPriorityBadge(priority: string) {
  switch (priority) {
    case "urgent":
      return { bg: "rgba(245, 158, 11, 0.15)", borderColor: "rgba(245, 158, 11, 0.3)", color: "var(--color-warning)", label: "URGENT" };
    case "vip":
      return { bg: "rgba(139, 92, 246, 0.15)", borderColor: "rgba(139, 92, 246, 0.3)", color: "var(--color-accent-purple-light)", label: "VIP" };
    default:
      return null;
  }
}

function timeAgo(dateStr: string): string {
  const now = new Date();
  const date = new Date(dateStr);
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

const STATUS_OPTIONS = [
  { value: "", label: "All Statuses" },
  { value: "draft", label: "Draft" },
  { value: "entity_selected", label: "Entity Selected" },
  { value: "payment_pending", label: "Payment Pending" },
  { value: "payment_completed", label: "Payment Completed" },
  { value: "documents_pending", label: "Documents Pending" },
  { value: "documents_uploaded", label: "Documents Uploaded" },
  { value: "documents_verified", label: "Documents Verified" },
  { value: "name_pending", label: "Name Pending" },
  { value: "name_reserved", label: "Name Reserved" },
  { value: "name_rejected", label: "Name Rejected" },
  { value: "dsc_in_progress", label: "DSC In Progress" },
  { value: "dsc_obtained", label: "DSC Obtained" },
  { value: "filing_drafted", label: "Filing Drafted" },
  { value: "filing_under_review", label: "Filing Under Review" },
  { value: "filing_submitted", label: "Filing Submitted" },
  { value: "mca_processing", label: "MCA Processing" },
  { value: "mca_query", label: "MCA Query" },
  { value: "incorporated", label: "Incorporated" },
  { value: "bank_account_pending", label: "Bank Account Pending" },
  { value: "bank_account_opened", label: "Bank Account Opened" },
  { value: "inc20a_pending", label: "INC-20A Pending" },
  { value: "fully_setup", label: "Fully Setup" },
];

export default function AdminCompaniesPage() {
  const [companies, setCompanies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => {
    const fetchCompanies = async () => {
      try {
        const data = await getAdminCompanies({
          limit: 500,
          status: statusFilter || undefined,
        });
        setCompanies(data.companies || []);
      } catch (err) {
        console.error("Failed to fetch companies:", err);
      } finally {
        setLoading(false);
      }
    };
    setLoading(true);
    fetchCompanies();
  }, [statusFilter]);

  const filtered = companies.filter((c) => {
    if (!search) return true;
    const q = search.toLowerCase();
    const name = (c.approved_name || c.proposed_names?.[0] || "").toLowerCase();
    const email = (c.user_email || "").toLowerCase();
    const id = String(c.id);
    return name.includes(q) || email.includes(q) || id.includes(q);
  });

  if (loading) {
    return (
      <div className="p-12 flex items-center justify-center">
        <div className="animate-pulse" style={{ color: "var(--color-text-muted)" }}>Loading companies...</div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-full">
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>Companies</h1>
        <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
          All registered companies and their incorporation status.
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} style={{ color: "var(--color-text-muted)" }}>
            <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
          </svg>
          <input
            type="text"
            placeholder="Search by name, email, or ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg pl-10 pr-4 py-2.5 text-sm outline-none transition-colors"
            style={{
              background: "var(--color-bg-secondary)",
              border: "1px solid var(--color-border)",
              color: "var(--color-text-primary)",
            }}
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg px-4 py-2.5 text-sm outline-none cursor-pointer"
          style={{
            background: "var(--color-bg-secondary)",
            border: "1px solid var(--color-border)",
            color: "var(--color-text-primary)",
            minWidth: "180px",
          }}
        >
          {STATUS_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>

      {/* Summary */}
      <div className="text-xs mb-4" style={{ color: "var(--color-text-muted)" }}>
        Showing {filtered.length} of {companies.length} companies
      </div>

      {/* Table */}
      <div className="rounded-xl overflow-hidden" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr style={{ borderBottom: "1px solid var(--color-border)", background: "var(--color-bg-secondary)" }}>
                <th className="text-left text-[10px] uppercase tracking-wider font-semibold px-4 py-3" style={{ color: "var(--color-text-muted)" }}>ID</th>
                <th className="text-left text-[10px] uppercase tracking-wider font-semibold px-4 py-3" style={{ color: "var(--color-text-muted)" }}>Company Name</th>
                <th className="text-left text-[10px] uppercase tracking-wider font-semibold px-4 py-3" style={{ color: "var(--color-text-muted)" }}>Type</th>
                <th className="text-left text-[10px] uppercase tracking-wider font-semibold px-4 py-3" style={{ color: "var(--color-text-muted)" }}>Status</th>
                <th className="text-left text-[10px] uppercase tracking-wider font-semibold px-4 py-3" style={{ color: "var(--color-text-muted)" }}>Priority</th>
                <th className="text-left text-[10px] uppercase tracking-wider font-semibold px-4 py-3" style={{ color: "var(--color-text-muted)" }}>Assigned To</th>
                <th className="text-left text-[10px] uppercase tracking-wider font-semibold px-4 py-3" style={{ color: "var(--color-text-muted)" }}>Updated</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-sm" style={{ color: "var(--color-text-muted)" }}>
                    No companies found.
                  </td>
                </tr>
              ) : (
                filtered.map((comp) => {
                  const displayName = comp.approved_name || (comp.proposed_names && comp.proposed_names[0]) || `Company #${comp.id}`;
                  const statusStyle = getStatusBadgeStyle(comp.status);
                  const priorityBadge = getPriorityBadge(comp.priority);

                  return (
                    <tr
                      key={comp.id}
                      className="transition-colors cursor-pointer"
                      style={{ borderBottom: "1px solid var(--color-border)" }}
                    >
                      <td className="px-4 py-3">
                        <Link href={`/companies/${comp.id}`} className="text-xs font-mono" style={{ color: "var(--color-text-muted)" }}>
                          #{comp.id}
                        </Link>
                      </td>
                      <td className="px-4 py-3">
                        <Link href={`/companies/${comp.id}`} className="block">
                          <p className="text-sm font-medium" style={{ color: "var(--color-text-primary)" }}>{displayName}</p>
                          {comp.user_email && (
                            <p className="text-[10px] mt-0.5" style={{ color: "var(--color-text-muted)" }}>{comp.user_email}</p>
                          )}
                        </Link>
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-xs" style={{ color: "var(--color-text-secondary)" }}>
                          {comp.entity_type?.replace(/_/g, " ").toUpperCase() || "--"}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className="inline-block text-[10px] font-semibold px-2 py-1 rounded-full uppercase tracking-wider"
                          style={{ ...statusStyle, borderWidth: "1px", borderStyle: "solid" }}
                        >
                          {comp.status?.replace(/_/g, " ")}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        {priorityBadge ? (
                          <span
                            className="inline-block text-[10px] font-bold px-2 py-1 rounded"
                            style={{
                              background: priorityBadge.bg,
                              borderWidth: "1px",
                              borderStyle: "solid",
                              borderColor: priorityBadge.borderColor,
                              color: priorityBadge.color,
                            }}
                          >
                            {priorityBadge.label}
                          </span>
                        ) : (
                          <span className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Normal</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {comp.assigned_to_name ? (
                          <span className="text-xs" style={{ color: "var(--color-text-secondary)" }}>{comp.assigned_to_name}</span>
                        ) : (
                          <span className="text-xs italic" style={{ color: "var(--color-text-muted)" }}>Unassigned</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                          {comp.updated_at ? timeAgo(comp.updated_at) : comp.created_at ? timeAgo(comp.created_at) : "--"}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
