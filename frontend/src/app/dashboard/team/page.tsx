"use client";

import { useState, useEffect, useCallback } from "react";
import { useCompany } from "@/lib/company-context";
import Link from "next/link";
import {
  inviteCompanyMember,
  getCompanyMembers,
  updateCompanyMember,
  removeCompanyMember,
  resendMemberInvite,
} from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Member {
  id: number;
  user_id: number | null;
  invite_email: string;
  invite_name: string;
  role: string;
  din: string | null;
  designation: string | null;
  invite_status: string; // pending, accepted, declined, revoked
  invite_token: string | null;
  accepted_at: string | null;
  created_at: string;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const ROLES = [
  { value: "director", label: "Director" },
  { value: "shareholder", label: "Shareholder" },
  { value: "company_secretary", label: "Company Secretary" },
  { value: "auditor", label: "Auditor" },
  { value: "advisor", label: "Advisor" },
  { value: "viewer", label: "Viewer" },
];

const ROLE_COLORS: Record<string, { bg: string; text: string }> = {
  owner: { bg: "var(--color-purple-bg)", text: "var(--color-accent-purple-light)" },
  director: { bg: "var(--color-info-light)", text: "var(--color-accent-blue)" },
  shareholder: { bg: "var(--color-success-light)", text: "var(--color-accent-emerald-light)" },
  company_secretary: { bg: "rgba(6, 182, 212, 0.15)", text: "var(--color-accent-cyan)" },
  auditor: { bg: "var(--color-warning-light)", text: "var(--color-accent-amber)" },
  advisor: { bg: "rgba(99, 102, 241, 0.15)", text: "rgb(99, 102, 241)" },
  viewer: { bg: "rgba(156, 163, 175, 0.15)", text: "var(--color-text-muted)" },
};

const STATUS_COLORS: Record<string, { bg: string; text: string }> = {
  pending: { bg: "var(--color-warning-light)", text: "var(--color-accent-amber)" },
  accepted: { bg: "var(--color-success-light)", text: "var(--color-accent-emerald-light)" },
  declined: { bg: "var(--color-error-light)", text: "var(--color-accent-rose)" },
  revoked: { bg: "rgba(156, 163, 175, 0.15)", text: "var(--color-text-muted)" },
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function TeamManagementPage() {
  const { companies, selectedCompany, selectCompany, loading: companyLoading } = useCompany();

  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState<"success" | "error">("success");

  // Invite modal
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteForm, setInviteForm] = useState({
    name: "",
    email: "",
    role: "director",
    din: "",
    designation: "",
    message: "",
  });
  const [inviting, setInviting] = useState(false);
  const [inviteLink, setInviteLink] = useState<string | null>(null);
  const [copiedLink, setCopiedLink] = useState(false);

  // Edit role modal
  const [editingMember, setEditingMember] = useState<Member | null>(null);
  const [editForm, setEditForm] = useState({ role: "", designation: "" });

  // Confirm remove
  const [removingMember, setRemovingMember] = useState<Member | null>(null);

  // ─── Fetch members ─────────────────────────────────────────
  const fetchMembers = useCallback(async () => {
    if (!selectedCompany) return;
    setLoading(true);
    try {
      const data = await getCompanyMembers(selectedCompany.id);
      setMembers(Array.isArray(data) ? data : []);
    } catch {
      // backend may not be running
    }
    setLoading(false);
  }, [selectedCompany]);

  useEffect(() => {
    if (selectedCompany?.id) {
      fetchMembers();
    }
  }, [selectedCompany?.id, fetchMembers]);

  // ─── Show message helper ───────────────────────────────────
  function showMsg(text: string, type: "success" | "error" = "success") {
    setMessage(text);
    setMessageType(type);
    setTimeout(() => setMessage(""), 5000);
  }

  // ─── Invite handler ────────────────────────────────────────
  async function handleInvite(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedCompany) return;
    setInviting(true);
    setInviteLink(null);
    try {
      const res = await inviteCompanyMember(selectedCompany.id, {
        email: inviteForm.email,
        name: inviteForm.name,
        role: inviteForm.role,
        din: inviteForm.din || undefined,
        designation: inviteForm.designation || undefined,
        message: inviteForm.message || undefined,
      });
      // Response should contain the invite token
      const token = res?.invite_token || res?.token;
      if (token) {
        setInviteLink(`${window.location.origin}/invite/${token}`);
      }
      showMsg("Invitation sent successfully!");
      setInviteForm({ name: "", email: "", role: "director", din: "", designation: "", message: "" });
      fetchMembers();
    } catch (err: any) {
      showMsg(`Error: ${err.message}`, "error");
    } finally {
      setInviting(false);
    }
  }

  // ─── Copy invite link ──────────────────────────────────────
  function handleCopyLink(link: string) {
    navigator.clipboard.writeText(link);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2000);
  }

  // ─── Update role ───────────────────────────────────────────
  async function handleUpdateRole(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedCompany || !editingMember) return;
    try {
      await updateCompanyMember(selectedCompany.id, editingMember.id, {
        role: editForm.role || undefined,
        designation: editForm.designation || undefined,
      });
      showMsg("Member role updated successfully!");
      setEditingMember(null);
      fetchMembers();
    } catch (err: any) {
      showMsg(`Error: ${err.message}`, "error");
    }
  }

  // ─── Remove member ─────────────────────────────────────────
  async function handleRemove() {
    if (!selectedCompany || !removingMember) return;
    try {
      await removeCompanyMember(selectedCompany.id, removingMember.id);
      showMsg("Member removed successfully!");
      setRemovingMember(null);
      fetchMembers();
    } catch (err: any) {
      showMsg(`Error: ${err.message}`, "error");
    }
  }

  // ─── Resend invite ─────────────────────────────────────────
  async function handleResend(member: Member) {
    if (!selectedCompany) return;
    try {
      await resendMemberInvite(selectedCompany.id, member.id);
      showMsg(`Invite resent to ${member.invite_email}`);
    } catch (err: any) {
      showMsg(`Error: ${err.message}`, "error");
    }
  }

  // ─── Stats ─────────────────────────────────────────────────
  const totalMembers = members.length;
  const directors = members.filter((m) => m.role === "director").length;
  const pending = members.filter((m) => m.invite_status === "pending").length;

  // ─── Render helpers ────────────────────────────────────────
  function RoleBadge({ role }: { role: string }) {
    const colors = ROLE_COLORS[role] || ROLE_COLORS.viewer;
    return (
      <span
        className="text-xs px-2 py-0.5 rounded-full capitalize font-medium"
        style={{ background: colors.bg, color: colors.text }}
      >
        {role.replace(/_/g, " ")}
      </span>
    );
  }

  function StatusBadge({ status }: { status: string }) {
    const colors = STATUS_COLORS[status] || STATUS_COLORS.revoked;
    return (
      <span
        className="text-xs px-2 py-0.5 rounded-full capitalize font-medium"
        style={{ background: colors.bg, color: colors.text }}
      >
        {status}
      </span>
    );
  }

  const companyName =
    selectedCompany?.approved_name ||
    selectedCompany?.proposed_names?.[0] ||
    "Your Company";

  // ─── Render ────────────────────────────────────────────────
  return (
    <div>
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="badge badge-purple mb-4 mx-auto w-fit">Team Management</div>
          <h1
            className="text-3xl md:text-4xl font-bold mb-3"
            style={{ fontFamily: "var(--font-display)" }}
          >
            <span className="gradient-text">Team &amp; Collaboration</span>
          </h1>
          <p className="text-base" style={{ color: "var(--color-text-secondary)" }}>
            Invite directors, shareholders, and advisors to collaborate on {companyName}.
          </p>
        </div>

        {/* Company selector */}
        {companies.length > 1 && (
          <div className="flex justify-center mb-6">
            <select
              className="glass-card text-sm px-3 py-2 rounded-lg border-none outline-none"
              style={{ background: "var(--color-bg-card)", color: "var(--color-text-primary)" }}
              value={selectedCompany?.id || ""}
              onChange={(e) => selectCompany(Number(e.target.value))}
            >
              {companies.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.approved_name || c.proposed_names?.[0] || `Company #${c.id}`}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* No company guard */}
        {!selectedCompany && !companyLoading && (
          <div className="glass-card p-12 text-center" style={{ cursor: "default" }}>
            <h2 className="text-xl font-bold mb-2" style={{ color: "var(--color-text-primary)" }}>
              No company selected
            </h2>
            <p className="text-sm mb-6" style={{ color: "var(--color-text-secondary)" }}>
              Select a company from the sidebar to manage team members.
            </p>
            <div className="flex items-center justify-center gap-3">
              <Link
                href="/pricing"
                className="px-5 py-2.5 rounded-lg text-sm font-semibold text-white"
                style={{ background: "var(--color-accent-purple-light)" }}
              >
                Incorporate a New Company
              </Link>
              <Link
                href="/dashboard/connect"
                className="px-5 py-2.5 rounded-lg text-sm font-semibold border"
                style={{ borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
              >
                Connect Existing Company
              </Link>
            </div>
          </div>
        )}

        {selectedCompany && (
          <>
            {/* Message banner */}
            {message && (
              <div
                className="p-3 rounded-lg mb-6 text-sm"
                style={{
                  background: messageType === "success" ? "var(--color-success-light)" : "var(--color-error-light)",
                  color: messageType === "success" ? "var(--color-accent-emerald-light)" : "var(--color-accent-rose)",
                }}
              >
                {message}
              </div>
            )}

            {/* Stats row + Invite button */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
              <div className="flex flex-wrap gap-3">
                <div className="glass-card px-4 py-3 text-center min-w-[120px]" style={{ cursor: "default" }}>
                  <div className="text-2xl font-bold" style={{ color: "var(--color-text-primary)" }}>
                    {totalMembers}
                  </div>
                  <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                    Total Members
                  </div>
                </div>
                <div className="glass-card px-4 py-3 text-center min-w-[120px]" style={{ cursor: "default" }}>
                  <div className="text-2xl font-bold" style={{ color: "var(--color-accent-blue)" }}>
                    {directors}
                  </div>
                  <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                    Directors
                  </div>
                </div>
                <div className="glass-card px-4 py-3 text-center min-w-[120px]" style={{ cursor: "default" }}>
                  <div className="text-2xl font-bold" style={{ color: "var(--color-accent-amber)" }}>
                    {pending}
                  </div>
                  <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                    Pending Invites
                  </div>
                </div>
              </div>

              <button
                className="btn-primary px-5 py-2.5 rounded-lg text-sm font-semibold flex items-center gap-2"
                onClick={() => { setShowInviteModal(true); setInviteLink(null); }}
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                </svg>
                Invite Member
              </button>
            </div>

            {/* Members list */}
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: "var(--color-accent-purple-light)" }} />
              </div>
            ) : members.length === 0 ? (
              <div className="glass-card p-12 text-center" style={{ cursor: "default" }}>
                <svg
                  className="w-12 h-12 mx-auto mb-4 opacity-30"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1}
                  style={{ color: "var(--color-text-muted)" }}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z"
                  />
                </svg>
                <h3 className="text-lg font-semibold mb-2" style={{ color: "var(--color-text-primary)" }}>
                  No team members yet
                </h3>
                <p className="text-sm mb-6" style={{ color: "var(--color-text-secondary)" }}>
                  Invite directors and stakeholders to collaborate on your company.
                </p>
                <button
                  className="btn-primary px-5 py-2.5 rounded-lg text-sm font-semibold"
                  onClick={() => { setShowInviteModal(true); setInviteLink(null); }}
                >
                  Send Your First Invite
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {members.map((member) => (
                  <div
                    key={member.id}
                    className="glass-card p-5"
                    style={{ cursor: "default" }}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                      {/* Member info */}
                      <div className="flex items-start gap-3">
                        <div
                          className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold text-white flex-shrink-0"
                          style={{
                            background: ROLE_COLORS[member.role]?.text || "var(--color-text-muted)",
                          }}
                        >
                          {member.invite_name?.charAt(0).toUpperCase() || "?"}
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-semibold text-sm" style={{ color: "var(--color-text-primary)" }}>
                              {member.invite_name}
                            </span>
                            <RoleBadge role={member.role} />
                            <StatusBadge status={member.invite_status} />
                          </div>
                          <div className="text-xs mt-0.5" style={{ color: "var(--color-text-secondary)" }}>
                            {member.invite_email}
                          </div>
                          <div className="flex flex-wrap items-center gap-3 mt-1.5">
                            {member.din && (
                              <span className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                                DIN: {member.din}
                              </span>
                            )}
                            {member.designation && (
                              <span className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                                {member.designation}
                              </span>
                            )}
                            <span className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                              {member.invite_status === "accepted" && member.accepted_at
                                ? `Joined on ${new Date(member.accepted_at).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })}`
                                : `Invite sent on ${new Date(member.created_at).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })}`}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <button
                          className="text-xs px-3 py-1.5 rounded-lg border transition-colors hover:bg-gray-50"
                          style={{ borderColor: "var(--color-border)", color: "var(--color-text-secondary)" }}
                          onClick={() => {
                            setEditingMember(member);
                            setEditForm({ role: member.role, designation: member.designation || "" });
                          }}
                        >
                          Change Role
                        </button>
                        {member.invite_status === "pending" && (
                          <button
                            className="text-xs px-3 py-1.5 rounded-lg border transition-colors hover:bg-gray-50"
                            style={{ borderColor: "var(--color-border)", color: "var(--color-accent-amber)" }}
                            onClick={() => handleResend(member)}
                          >
                            Resend Invite
                          </button>
                        )}
                        {member.role !== "owner" && (
                          <button
                            className="text-xs px-3 py-1.5 rounded-lg border transition-colors hover:bg-gray-50"
                            style={{ borderColor: "var(--color-border)", color: "var(--color-accent-rose)" }}
                            onClick={() => setRemovingMember(member)}
                          >
                            Remove
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* ── Invite Modal ─────────────────────────────────────────── */}
      {showInviteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "var(--color-overlay)" }}>
          <div
            className="w-full max-w-lg rounded-2xl shadow-xl p-6 max-h-[90vh] overflow-y-auto"
            style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)" }}
          >
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-bold" style={{ color: "var(--color-text-primary)" }}>
                Invite Team Member
              </h2>
              <button
                onClick={() => { setShowInviteModal(false); setInviteLink(null); }}
                className="p-1 rounded-lg hover:bg-gray-100 transition-colors"
                style={{ color: "var(--color-text-muted)" }}
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Invite link success */}
            {inviteLink && (
              <div
                className="p-4 rounded-lg mb-5"
                style={{ background: "var(--color-success-light)", border: "1px solid var(--color-success-light)" }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="var(--color-accent-emerald-light)" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm font-semibold" style={{ color: "var(--color-accent-emerald-light)" }}>
                    Invite sent!
                  </span>
                </div>
                <p className="text-xs mb-2" style={{ color: "var(--color-text-secondary)" }}>
                  Share this link with the invitee:
                </p>
                <div className="flex items-center gap-2">
                  <input
                    readOnly
                    value={inviteLink}
                    className="flex-1 text-xs px-3 py-2 rounded-lg border bg-white"
                    style={{ borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                  />
                  <button
                    className="text-xs px-3 py-2 rounded-lg font-medium text-white flex-shrink-0"
                    style={{ background: copiedLink ? "var(--color-accent-emerald-light)" : "var(--color-accent-purple-light)" }}
                    onClick={() => handleCopyLink(inviteLink)}
                  >
                    {copiedLink ? "Copied!" : "Copy"}
                  </button>
                </div>
              </div>
            )}

            <form onSubmit={handleInvite} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1" style={{ color: "var(--color-text-secondary)" }}>
                    Full Name *
                  </label>
                  <input
                    required
                    type="text"
                    className="input-field"
                    value={inviteForm.name}
                    onChange={(e) => setInviteForm({ ...inviteForm, name: e.target.value })}
                    placeholder="Jane Smith"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1" style={{ color: "var(--color-text-secondary)" }}>
                    Email Address *
                  </label>
                  <input
                    required
                    type="email"
                    className="input-field"
                    value={inviteForm.email}
                    onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
                    placeholder="jane@example.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: "var(--color-text-secondary)" }}>
                  Role *
                </label>
                <select
                  className="input-field"
                  value={inviteForm.role}
                  onChange={(e) => setInviteForm({ ...inviteForm, role: e.target.value })}
                >
                  {ROLES.map((r) => (
                    <option key={r.value} value={r.value}>
                      {r.label}
                    </option>
                  ))}
                </select>
              </div>

              {inviteForm.role === "director" && (
                <div>
                  <label className="block text-sm font-medium mb-1" style={{ color: "var(--color-text-secondary)" }}>
                    DIN (Director Identification Number)
                  </label>
                  <input
                    type="text"
                    className="input-field"
                    value={inviteForm.din}
                    onChange={(e) => setInviteForm({ ...inviteForm, din: e.target.value })}
                    placeholder="e.g. 07654321"
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: "var(--color-text-secondary)" }}>
                  Designation
                </label>
                <input
                  type="text"
                  className="input-field"
                  value={inviteForm.designation}
                  onChange={(e) => setInviteForm({ ...inviteForm, designation: e.target.value })}
                  placeholder="e.g. Managing Director, CFO"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: "var(--color-text-secondary)" }}>
                  Personal Message (optional)
                </label>
                <textarea
                  className="input-field"
                  rows={3}
                  value={inviteForm.message}
                  onChange={(e) => setInviteForm({ ...inviteForm, message: e.target.value })}
                  placeholder="Hi Jane, I'd like to invite you to join our company on Anvils..."
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  className="px-4 py-2 rounded-lg text-sm font-medium border transition-colors hover:bg-gray-50"
                  style={{ borderColor: "var(--color-border)", color: "var(--color-text-secondary)" }}
                  onClick={() => { setShowInviteModal(false); setInviteLink(null); }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary px-5 py-2 rounded-lg text-sm font-semibold flex items-center gap-2"
                  disabled={inviting}
                >
                  {inviting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                      Sending...
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                      </svg>
                      Send Invite
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Edit Role Modal ──────────────────────────────────────── */}
      {editingMember && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "var(--color-overlay)" }}>
          <div
            className="w-full max-w-md rounded-2xl shadow-xl p-6"
            style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)" }}
          >
            <h2 className="text-lg font-bold mb-4" style={{ color: "var(--color-text-primary)" }}>
              Update Role for {editingMember.invite_name}
            </h2>
            <form onSubmit={handleUpdateRole} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: "var(--color-text-secondary)" }}>
                  Role
                </label>
                <select
                  className="input-field"
                  value={editForm.role}
                  onChange={(e) => setEditForm({ ...editForm, role: e.target.value })}
                >
                  {ROLES.map((r) => (
                    <option key={r.value} value={r.value}>
                      {r.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: "var(--color-text-secondary)" }}>
                  Designation
                </label>
                <input
                  type="text"
                  className="input-field"
                  value={editForm.designation}
                  onChange={(e) => setEditForm({ ...editForm, designation: e.target.value })}
                  placeholder="e.g. Managing Director"
                />
              </div>
              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  className="px-4 py-2 rounded-lg text-sm font-medium border transition-colors hover:bg-gray-50"
                  style={{ borderColor: "var(--color-border)", color: "var(--color-text-secondary)" }}
                  onClick={() => setEditingMember(null)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary px-5 py-2 rounded-lg text-sm font-semibold"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Remove Confirmation Modal ────────────────────────────── */}
      {removingMember && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "var(--color-overlay)" }}>
          <div
            className="w-full max-w-sm rounded-2xl shadow-xl p-6"
            style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)" }}
          >
            <h2 className="text-lg font-bold mb-2" style={{ color: "var(--color-text-primary)" }}>
              Remove Member
            </h2>
            <p className="text-sm mb-5" style={{ color: "var(--color-text-secondary)" }}>
              Are you sure you want to remove <strong>{removingMember.invite_name}</strong> ({removingMember.invite_email}) from {companyName}? This action cannot be undone.
            </p>
            <div className="flex items-center justify-end gap-3">
              <button
                className="px-4 py-2 rounded-lg text-sm font-medium border transition-colors hover:bg-gray-50"
                style={{ borderColor: "var(--color-border)", color: "var(--color-text-secondary)" }}
                onClick={() => setRemovingMember(null)}
              >
                Cancel
              </button>
              <button
                className="px-5 py-2 rounded-lg text-sm font-semibold text-white transition-colors"
                style={{ background: "var(--color-accent-rose)" }}
                onClick={handleRemove}
              >
                Remove Member
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
