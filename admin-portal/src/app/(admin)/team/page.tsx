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

function getRoleBadgeClasses(role: string): string {
  switch (role) {
    case "super_admin": return "bg-red-500/15 text-red-400 border-red-500/30";
    case "admin": return "bg-purple-500/15 text-purple-400 border-purple-500/30";
    case "cs_lead":
    case "ca_lead": return "bg-blue-500/15 text-blue-400 border-blue-500/30";
    case "filing_coordinator": return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
    case "customer_success": return "bg-cyan-500/15 text-cyan-400 border-cyan-500/30";
    default: return "bg-gray-500/15 text-gray-400 border-gray-500/30";
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
        <div className="animate-pulse text-gray-500">Loading team members...</div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-5xl">
      {/* Header */}
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>Team Management</h1>
          <p className="text-sm text-gray-400">Manage your operations team members and their roles.</p>
        </div>
        <button
          onClick={() => setShowInviteForm(!showInviteForm)}
          className="px-4 py-2 rounded-lg text-sm font-medium bg-purple-600 hover:bg-purple-500 text-white transition-colors"
        >
          + Invite Member
        </button>
      </div>

      {/* Invite Form */}
      {showInviteForm && (
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-6 mb-6">
          <h3 className="text-sm font-semibold mb-4">Invite New Team Member</h3>
          <div className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              value={inviteName}
              onChange={(e) => setInviteName(e.target.value)}
              placeholder="Full name..."
              className="sm:w-48 bg-gray-900/50 border border-gray-700 rounded-lg p-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-purple-500/50"
            />
            <input
              type="email"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              placeholder="Email address..."
              className="flex-1 bg-gray-900/50 border border-gray-700 rounded-lg p-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-purple-500/50"
            />
            <select
              value={inviteRole}
              onChange={(e) => setInviteRole(e.target.value)}
              className="bg-gray-900/50 border border-gray-700 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-purple-500/50"
            >
              {ROLE_OPTIONS.map((r) => (
                <option key={r.value} value={r.value}>{r.label}</option>
              ))}
            </select>
            <button
              onClick={handleInvite}
              disabled={!inviteEmail.trim() || !inviteName.trim() || inviting}
              className="px-6 py-3 rounded-lg text-sm font-medium bg-purple-600 hover:bg-purple-500 text-white transition-colors disabled:opacity-50 whitespace-nowrap"
            >
              {inviting ? "Sending..." : "Send Invite"}
            </button>
          </div>
          <p className="text-[10px] text-gray-500 mt-2">An invitation email will be sent with a link to create their account.</p>
        </div>
      )}

      {/* Team List */}
      <div className="rounded-xl border border-gray-700 bg-gray-800/50 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">Member</th>
              <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">Role</th>
              <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">Status</th>
              <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">Joined</th>
              <th className="text-right px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700/50">
            {team.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-5 py-8 text-center text-gray-500">No team members found.</td>
              </tr>
            ) : (
              team.map((member) => (
                <tr key={member.id} className="hover:bg-white/5 transition-colors">
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center text-xs font-bold text-purple-400">
                        {(member.full_name || member.email || "?").charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-white">{member.full_name || "Unnamed"}</p>
                        <p className="text-[10px] text-gray-500">{member.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-4">
                    <select
                      value={member.role || "agent"}
                      onChange={(e) => handleRoleChange(member.id, e.target.value)}
                      disabled={changingRole === member.id}
                      className={`text-xs font-semibold px-2.5 py-1 rounded-full border bg-transparent cursor-pointer focus:outline-none ${getRoleBadgeClasses(member.role || "agent")}`}
                    >
                      {ROLE_OPTIONS.map((r) => (
                        <option key={r.value} value={r.value} className="bg-gray-900 text-white">{r.label}</option>
                      ))}
                    </select>
                  </td>
                  <td className="px-5 py-4">
                    <span className={`text-xs font-medium ${member.is_active !== false ? "text-emerald-400" : "text-gray-500"}`}>
                      {member.is_active !== false ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-xs text-gray-400">
                    {member.created_at ? new Date(member.created_at).toLocaleDateString() : "--"}
                  </td>
                  <td className="px-5 py-4 text-right">
                    {member.is_active !== false && (
                      <button
                        onClick={() => handleDeactivate(member.id)}
                        className="text-xs text-red-400 hover:text-red-300 font-medium transition-colors"
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
