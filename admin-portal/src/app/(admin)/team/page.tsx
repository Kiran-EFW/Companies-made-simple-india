"use client";

import { useEffect, useState } from "react";
import { getAdminTeam, apiCall } from "@/lib/api";

const ROLE_OPTIONS = [
  { value: "admin", label: "Admin", description: "Full access to all features" },
  { value: "super_admin", label: "Super Admin", description: "Full platform control" },
  { value: "cs_lead", label: "CS Lead", description: "Company Secretary lead" },
  { value: "ca_lead", label: "CA Lead", description: "Chartered Accountant lead" },
  { value: "filing_coordinator", label: "Filing Coordinator", description: "Handle MCA filings" },
  { value: "customer_success", label: "Customer Success", description: "Customer support" },
];

function getRoleBadgeStyle(role: string): React.CSSProperties {
  switch (role) {
    case "super_admin": return { background: "rgba(239, 68, 68, 0.15)", color: "var(--color-error)", borderColor: "rgba(239, 68, 68, 0.3)" };
    case "admin": return { background: "rgba(139, 92, 246, 0.15)", color: "var(--color-accent-purple-light)", borderColor: "rgba(139, 92, 246, 0.3)" };
    case "cs_lead":
    case "ca_lead": return { background: "rgba(59, 130, 246, 0.15)", color: "var(--color-info)", borderColor: "rgba(59, 130, 246, 0.3)" };
    case "filing_coordinator": return { background: "rgba(16, 185, 129, 0.15)", color: "var(--color-success)", borderColor: "rgba(16, 185, 129, 0.3)" };
    case "customer_success": return { background: "rgba(6, 182, 212, 0.15)", color: "rgb(34, 211, 238)", borderColor: "rgba(6, 182, 212, 0.3)" };
    default: return { background: "rgba(107, 114, 128, 0.15)", color: "var(--color-text-secondary)", borderColor: "rgba(107, 114, 128, 0.3)" };
  }
}

export default function AdminTeamPage() {
  const [team, setTeam] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteName, setInviteName] = useState("");
  const [inviteRole, setInviteRole] = useState("customer_success");
  const [inviting, setInviting] = useState(false);
  const [changingRole, setChangingRole] = useState<number | null>(null);

  useEffect(() => {
    fetchTeam();
  }, []);

  const fetchTeam = async () => {
    try {
      const data = await getAdminTeam();
      setTeam(data || []);
    } catch (err) {
      console.error("Failed to fetch team:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = async () => {
    if (!inviteEmail.trim() || !inviteName.trim()) return;
    setInviting(true);
    try {
      await apiCall("/admin/users/invite", {
        method: "POST",
        body: JSON.stringify({ email: inviteEmail, full_name: inviteName, role: inviteRole }),
      });
      setInviteEmail("");
      setInviteName("");
      setInviteRole("customer_success");
      setShowInviteForm(false);
      await fetchTeam();
    } catch (err) {
      console.error("Failed to invite:", err);
      alert("Failed to send invitation. Please check the email and try again.");
    } finally {
      setInviting(false);
    }
  };

  const handleRoleChange = async (userId: number, newRole: string) => {
    setChangingRole(userId);
    try {
      await apiCall(`/admin/users/${userId}/role`, {
        method: "PUT",
        body: JSON.stringify({ role: newRole }),
      });
      setTeam((prev) =>
        prev.map((m) => (m.id === userId ? { ...m, role: newRole } : m))
      );
    } catch (err) {
      console.error("Failed to change role:", err);
      alert("Failed to update role.");
    } finally {
      setChangingRole(null);
    }
  };

  const handleDeactivate = async (userId: number) => {
    if (!confirm("Are you sure you want to deactivate this team member?")) return;
    try {
      await apiCall(`/admin/users/${userId}/deactivate`, {
        method: "PUT",
      });
      setTeam((prev) =>
        prev.map((m) => (m.id === userId ? { ...m, is_active: false } : m))
      );
    } catch (err) {
      console.error("Failed to deactivate:", err);
      alert("Failed to deactivate team member.");
    }
  };

  if (loading) {
    return (
      <div className="p-12 flex items-center justify-center">
        <div className="animate-pulse" style={{ color: "var(--color-text-muted)" }}>Loading team members...</div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-5xl">
      {/* Header */}
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>Team Management</h1>
          <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>Manage your operations team members and their roles.</p>
        </div>
        <button
          onClick={() => setShowInviteForm(!showInviteForm)}
          className="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          style={{ background: "var(--color-accent-purple)", color: "var(--color-text-primary)" }}
        >
          + Invite Member
        </button>
      </div>

      {/* Invite Form */}
      {showInviteForm && (
        <div className="rounded-xl p-6 mb-6" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
          <h3 className="text-sm font-semibold mb-4">Invite New Team Member</h3>
          <div className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              value={inviteName}
              onChange={(e) => setInviteName(e.target.value)}
              placeholder="Full name..."
              className="sm:w-48 rounded-lg p-3 text-sm focus:outline-none"
              style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
            />
            <input
              type="email"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              placeholder="Email address..."
              className="flex-1 rounded-lg p-3 text-sm focus:outline-none"
              style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
            />
            <select
              value={inviteRole}
              onChange={(e) => setInviteRole(e.target.value)}
              className="rounded-lg p-3 text-sm focus:outline-none"
              style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
            >
              {ROLE_OPTIONS.map((r) => (
                <option key={r.value} value={r.value}>{r.label}</option>
              ))}
            </select>
            <button
              onClick={handleInvite}
              disabled={!inviteEmail.trim() || !inviteName.trim() || inviting}
              className="px-6 py-3 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 whitespace-nowrap"
              style={{ background: "var(--color-accent-purple)", color: "var(--color-text-primary)" }}
            >
              {inviting ? "Sending..." : "Send Invite"}
            </button>
          </div>
          <p className="text-[10px] mt-2" style={{ color: "var(--color-text-muted)" }}>An invitation email will be sent with a link to create their account.</p>
        </div>
      )}

      {/* Team List */}
      <div className="rounded-xl overflow-hidden" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
        <table className="w-full text-sm">
          <thead>
            <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
              <th className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Member</th>
              <th className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Role</th>
              <th className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Status</th>
              <th className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Joined</th>
              <th className="text-right px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {team.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-5 py-8 text-center" style={{ color: "var(--color-text-muted)" }}>No team members found.</td>
              </tr>
            ) : (
              team.map((member) => (
                <tr key={member.id} className="transition-colors">
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold" style={{ background: "rgba(139, 92, 246, 0.2)", color: "var(--color-accent-purple-light)" }}>
                        {(member.full_name || member.email || "?").charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <p className="text-sm font-medium" style={{ color: "var(--color-text-primary)" }}>{member.full_name || "Unnamed"}</p>
                        <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>{member.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-4">
                    <select
                      value={member.role || "agent"}
                      onChange={(e) => handleRoleChange(member.id, e.target.value)}
                      disabled={changingRole === member.id}
                      className="text-xs font-semibold px-2.5 py-1 rounded-full border cursor-pointer focus:outline-none"
                      style={getRoleBadgeStyle(member.role || "agent")}
                    >
                      {ROLE_OPTIONS.map((r) => (
                        <option key={r.value} value={r.value} style={{ background: "var(--color-bg-secondary)", color: "var(--color-text-primary)" }}>{r.label}</option>
                      ))}
                    </select>
                  </td>
                  <td className="px-5 py-4">
                    <span className="text-xs font-medium" style={{ color: member.is_active !== false ? "var(--color-success)" : "var(--color-text-muted)" }}>
                      {member.is_active !== false ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-xs" style={{ color: "var(--color-text-secondary)" }}>
                    {member.created_at ? new Date(member.created_at).toLocaleDateString() : "--"}
                  </td>
                  <td className="px-5 py-4 text-right">
                    {member.is_active !== false && (
                      <button
                        onClick={() => handleDeactivate(member.id)}
                        className="text-xs font-medium transition-colors"
                        style={{ color: "var(--color-error)" }}
                      >
                        Deactivate
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
