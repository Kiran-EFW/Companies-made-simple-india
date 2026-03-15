"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  getAdminCompanyDetail,
  updateCompanyStatus,
  assignCompany,
  setCompanyPriority,
  getAdminTeam,
  getCompanyLogs,
  getCompanyTasks,
  sendAdminMessage,
  addInternalNote,
} from "@/lib/api";

const STATUS_OPTIONS = [
  "draft", "entity_selected", "payment_pending", "payment_completed",
  "documents_pending", "documents_uploaded", "documents_verified",
  "name_pending", "name_reserved", "name_rejected",
  "dsc_in_progress", "dsc_obtained", "filing_drafted", "filing_under_review", "filing_submitted",
  "mca_processing", "mca_query", "incorporated",
  "bank_account_pending", "bank_account_opened", "inc20a_pending", "fully_setup",
];

const PRIORITY_OPTIONS = [
  { value: "normal", label: "Normal", color: "var(--color-text-secondary)" },
  { value: "urgent", label: "Urgent", color: "var(--color-warning)" },
  { value: "vip", label: "VIP", color: "var(--color-accent-purple-light)" },
];

const TABS = [
  { key: "overview", label: "Overview" },
  { key: "documents", label: "Documents" },
  { key: "tasks", label: "Tasks" },
  { key: "notes", label: "Notes" },
  { key: "communication", label: "Communication" },
  { key: "payments", label: "Payments" },
];

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

export default function AdminCompanyDetailPage() {
  const params = useParams();
  const companyId = Number(params.id);

  const [company, setCompany] = useState<any>(null);
  const [team, setTeam] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  // Action states
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [showPriorityModal, setShowPriorityModal] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState("");
  const [statusNote, setStatusNote] = useState("");
  const [selectedAssignee, setSelectedAssignee] = useState<number | null>(null);
  const [selectedPriority, setSelectedPriority] = useState("");
  const [actionLoading, setActionLoading] = useState(false);

  // Notes
  const [noteContent, setNoteContent] = useState("");
  const [addingNote, setAddingNote] = useState(false);

  // Messages
  const [messageContent, setMessageContent] = useState("");
  const [sendingMessage, setSendingMessage] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [companyData, teamData, logsData, tasksData] = await Promise.allSettled([
          getAdminCompanyDetail(companyId),
          getAdminTeam(),
          getCompanyLogs(companyId),
          getCompanyTasks(companyId),
        ]);

        if (companyData.status === "fulfilled") setCompany(companyData.value);
        if (teamData.status === "fulfilled") setTeam(teamData.value || []);
        if (logsData.status === "fulfilled") setLogs(logsData.value || []);
        if (tasksData.status === "fulfilled") setTasks(tasksData.value || []);
      } catch (err) {
        console.error("Failed to load company detail:", err);
      } finally {
        setLoading(false);
      }
    };

    if (companyId) fetchData();
  }, [companyId]);

  const handleStatusChange = async () => {
    if (!selectedStatus) return;
    setActionLoading(true);
    try {
      await updateCompanyStatus(companyId, selectedStatus, statusNote || undefined);
      setCompany((prev: any) => ({ ...prev, status: selectedStatus }));
      setShowStatusModal(false);
      setSelectedStatus("");
      setStatusNote("");
    } catch (err) {
      console.error("Failed to update status:", err);
      alert("Failed to update status.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleAssign = async () => {
    if (!selectedAssignee) return;
    setActionLoading(true);
    try {
      await assignCompany(companyId, selectedAssignee);
      const assignee = team.find((t) => t.id === selectedAssignee);
      setCompany((prev: any) => ({ ...prev, assigned_to: selectedAssignee, assigned_to_name: assignee?.full_name }));
      setShowAssignModal(false);
      setSelectedAssignee(null);
    } catch (err) {
      console.error("Failed to assign:", err);
      alert("Failed to assign company.");
    } finally {
      setActionLoading(false);
    }
  };

  const handlePriorityChange = async () => {
    if (!selectedPriority) return;
    setActionLoading(true);
    try {
      await setCompanyPriority(companyId, selectedPriority);
      setCompany((prev: any) => ({ ...prev, priority: selectedPriority }));
      setShowPriorityModal(false);
      setSelectedPriority("");
    } catch (err) {
      console.error("Failed to set priority:", err);
      alert("Failed to set priority.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleAddNote = async () => {
    if (!noteContent.trim()) return;
    setAddingNote(true);
    try {
      await addInternalNote(companyId, noteContent);
      setNoteContent("");
      // Refresh company to get updated notes
      const updated = await getAdminCompanyDetail(companyId);
      setCompany(updated);
    } catch (err) {
      console.error("Failed to add note:", err);
      alert("Failed to add note.");
    } finally {
      setAddingNote(false);
    }
  };

  const handleSendMessage = async () => {
    if (!messageContent.trim()) return;
    setSendingMessage(true);
    try {
      await sendAdminMessage(companyId, messageContent);
      setMessageContent("");
      // Refresh company to get updated messages
      const updated = await getAdminCompanyDetail(companyId);
      setCompany(updated);
    } catch (err) {
      console.error("Failed to send message:", err);
      alert("Failed to send message.");
    } finally {
      setSendingMessage(false);
    }
  };

  if (loading) {
    return (
      <div className="p-12 flex items-center justify-center">
        <div className="animate-pulse" style={{ color: "var(--color-text-muted)" }}>Loading company details...</div>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="p-12 text-center">
        <h2 className="text-xl font-bold mb-2" style={{ color: "var(--color-text-primary)" }}>Company Not Found</h2>
        <p className="mb-4" style={{ color: "var(--color-text-muted)" }}>The company with ID #{companyId} could not be found.</p>
        <Link href="/dashboard" className="text-sm font-medium" style={{ color: "var(--color-accent-purple-light)" }}>
          Back to Dashboard
        </Link>
      </div>
    );
  }

  const displayName = company.approved_name || (company.proposed_names && company.proposed_names[0]) || `Company #${company.id}`;

  return (
    <div className="p-6 lg:p-8 max-w-6xl">
      {/* Breadcrumb */}
      <div className="mb-6">
        <Link href="/dashboard" className="text-xs transition-colors" style={{ color: "var(--color-text-muted)" }}>
          Dashboard
        </Link>
        <span className="text-xs mx-2" style={{ color: "var(--color-text-muted)" }}>/</span>
        <span className="text-xs" style={{ color: "var(--color-text-secondary)" }}>{displayName}</span>
      </div>

      {/* Header */}
      <div className="rounded-xl p-6 mb-6" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
        <div className="flex flex-col lg:flex-row justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold" style={{ fontFamily: "var(--font-display)" }}>{displayName}</h1>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full border" style={getStatusBadgeStyle(company.status)}>
                {company.status.replace(/_/g, " ").toUpperCase()}
              </span>
            </div>
            <div className="flex items-center gap-4 text-xs" style={{ color: "var(--color-text-secondary)" }}>
              <span>{company.entity_type?.replace(/_/g, " ").toUpperCase()}</span>
              <span>State: {company.state?.toUpperCase()}</span>
              <span>Plan: {company.plan_tier?.toUpperCase()}</span>
              {company.priority && company.priority !== "normal" && (
                <span className="font-bold" style={{ color: company.priority === "vip" ? "var(--color-accent-purple-light)" : "var(--color-warning)" }}>
                  {company.priority.toUpperCase()}
                </span>
              )}
              {company.assigned_to_name && (
                <span>Assigned to: <strong style={{ color: "var(--color-text-primary)" }}>{company.assigned_to_name}</strong></span>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => { setSelectedStatus(company.status); setShowStatusModal(true); }}
              className="px-3 py-2 rounded-lg text-xs font-medium transition-colors"
              style={{ background: "var(--color-info-light)", color: "var(--color-info)", border: "1px solid rgba(59, 130, 246, 0.2)" }}
            >
              Change Status
            </button>
            <button
              onClick={() => setShowAssignModal(true)}
              className="px-3 py-2 rounded-lg text-xs font-medium transition-colors"
              style={{ background: "rgba(139, 92, 246, 0.1)", color: "var(--color-accent-purple-light)", border: "1px solid rgba(139, 92, 246, 0.2)" }}
            >
              Assign
            </button>
            <button
              onClick={() => { setSelectedPriority(company.priority || "normal"); setShowPriorityModal(true); }}
              className="px-3 py-2 rounded-lg text-xs font-medium transition-colors"
              style={{ background: "var(--color-warning-light)", color: "var(--color-warning)", border: "1px solid rgba(245, 158, 11, 0.2)" }}
            >
              Set Priority
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 overflow-x-auto pb-px" style={{ borderBottom: "1px solid var(--color-border)" }}>
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className="px-4 py-2.5 text-sm font-medium whitespace-nowrap transition-colors relative"
            style={{ color: activeTab === tab.key ? "var(--color-accent-purple-light)" : "var(--color-text-muted)" }}
          >
            {tab.label}
            {activeTab === tab.key && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 rounded-full" style={{ background: "var(--color-accent-purple)" }} />
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}

      {/* Overview Tab */}
      {activeTab === "overview" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Company Info */}
          <div className="rounded-xl p-5" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
            <h3 className="text-sm font-semibold mb-4">Company Information</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span style={{ color: "var(--color-text-muted)" }}>ID</span>
                <span className="font-mono" style={{ color: "var(--color-text-primary)" }}>#{company.id}</span>
              </div>
              <div className="flex justify-between">
                <span style={{ color: "var(--color-text-muted)" }}>Entity Type</span>
                <span style={{ color: "var(--color-text-primary)" }}>{company.entity_type?.replace(/_/g, " ")}</span>
              </div>
              <div className="flex justify-between">
                <span style={{ color: "var(--color-text-muted)" }}>State</span>
                <span style={{ color: "var(--color-text-primary)" }}>{company.state}</span>
              </div>
              <div className="flex justify-between">
                <span style={{ color: "var(--color-text-muted)" }}>Plan</span>
                <span style={{ color: "var(--color-text-primary)" }}>{company.plan_tier}</span>
              </div>
              <div className="flex justify-between">
                <span style={{ color: "var(--color-text-muted)" }}>Authorized Capital</span>
                <span style={{ color: "var(--color-text-primary)" }}>{company.authorized_capital ? `₹${company.authorized_capital.toLocaleString()}` : "--"}</span>
              </div>
              <div className="flex justify-between">
                <span style={{ color: "var(--color-text-muted)" }}>Directors</span>
                <span style={{ color: "var(--color-text-primary)" }}>{company.num_directors || "--"}</span>
              </div>
              <div className="flex justify-between">
                <span style={{ color: "var(--color-text-muted)" }}>Created</span>
                <span style={{ color: "var(--color-text-primary)" }}>{new Date(company.created_at).toLocaleDateString()}</span>
              </div>
              {company.proposed_names && company.proposed_names.length > 0 && (
                <div>
                  <span className="block mb-1" style={{ color: "var(--color-text-muted)" }}>Proposed Names</span>
                  <div className="space-y-1">
                    {company.proposed_names.map((name: string, i: number) => (
                      <p key={i} className="text-xs pl-2" style={{ color: "var(--color-text-primary)", borderLeft: "1px solid var(--color-border)" }}>{name}</p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Directors */}
          <div className="rounded-xl p-5" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
            <h3 className="text-sm font-semibold mb-4">Directors</h3>
            {company.directors && company.directors.length > 0 ? (
              <div className="space-y-3">
                {company.directors.map((dir: any, idx: number) => (
                  <div key={idx} className="p-3 rounded-lg" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-secondary)" }}>
                    <p className="text-sm font-medium" style={{ color: "var(--color-text-primary)" }}>{dir.full_name || dir.name || `Director ${idx + 1}`}</p>
                    <div className="flex gap-4 mt-1 text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                      {dir.email && <span>{dir.email}</span>}
                      {dir.din && <span>DIN: {dir.din}</span>}
                      {dir.pan && <span>PAN: {dir.pan}</span>}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>No director information available.</p>
            )}
          </div>

          {/* Timeline */}
          <div className="lg:col-span-2 rounded-xl p-5" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
            <h3 className="text-sm font-semibold mb-4">Status Timeline</h3>
            {logs.length > 0 ? (
              <div className="relative pl-6 space-y-4">
                <div className="absolute left-2 top-2 bottom-2 w-px" style={{ background: "var(--color-border)" }} />
                {logs.slice(0, 20).map((log, idx) => (
                  <div key={idx} className="relative">
                    <div className="absolute left-[-18px] top-1.5 w-2.5 h-2.5 rounded-full" style={
                      log.level === "SUCCESS" ? { background: "var(--color-success)", border: "2px solid var(--color-success)" } :
                      log.level === "ERROR" ? { background: "var(--color-error)", border: "2px solid var(--color-error)" } :
                      log.level === "WARN" ? { background: "var(--color-warning)", border: "2px solid var(--color-warning)" } :
                      { background: "var(--color-accent-purple)", border: "2px solid var(--color-accent-purple-light)" }
                    } />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium" style={{ color: "var(--color-text-primary)" }}>{log.agent_name || "System"}</span>
                        <span className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>{new Date(log.timestamp || log.created_at).toLocaleString()}</span>
                      </div>
                      <p className="text-xs mt-0.5" style={{ color: "var(--color-text-secondary)" }}>{log.message}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>No timeline entries.</p>
            )}
          </div>
        </div>
      )}

      {/* Documents Tab */}
      {activeTab === "documents" && (
        <div className="space-y-4">
          {company.documents && company.documents.length > 0 ? (
            company.documents.map((doc: any) => {
              const extracted = doc.extracted_data ? (() => { try { return JSON.parse(doc.extracted_data); } catch { return null; } })() : null;
              return (
                <div key={doc.id} className="rounded-xl overflow-hidden" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
                  <div className="flex flex-col lg:flex-row">
                    <div className="flex-1 p-5">
                      <div className="flex items-center gap-3 mb-3">
                        <span className="text-xs uppercase tracking-wider font-bold" style={{ color: "var(--color-accent-purple-light)" }}>
                          {doc.doc_type?.replace(/_/g, " ")}
                        </span>
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full" style={
                          doc.verification_status === "team_verified" ? { background: "rgba(16, 185, 129, 0.15)", color: "var(--color-success)", border: "1px solid rgba(16, 185, 129, 0.3)" } :
                          doc.verification_status === "ai_verified" ? { background: "rgba(59, 130, 246, 0.15)", color: "var(--color-info)", border: "1px solid rgba(59, 130, 246, 0.3)" } :
                          doc.verification_status === "rejected" ? { background: "rgba(239, 68, 68, 0.15)", color: "var(--color-error)", border: "1px solid rgba(239, 68, 68, 0.3)" } :
                          { background: "rgba(245, 158, 11, 0.15)", color: "var(--color-warning)", border: "1px solid rgba(245, 158, 11, 0.3)" }
                        }>
                          {doc.verification_status?.replace(/_/g, " ").toUpperCase()}
                        </span>
                      </div>
                      <p className="text-sm mb-1" style={{ color: "var(--color-text-primary)" }}>{doc.original_filename}</p>
                      <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Uploaded {new Date(doc.uploaded_at || doc.created_at).toLocaleString()}</p>
                    </div>
                    {extracted && (
                      <div className="flex-1 p-5" style={{ borderTop: "1px solid var(--color-border)", background: "var(--color-bg-secondary)" }}>
                        <p className="text-xs font-semibold mb-3" style={{ color: "var(--color-text-secondary)" }}>Extracted Data</p>
                        <div className="space-y-1.5 font-mono text-xs">
                          {Object.entries(extracted).filter(([k]) => !k.startsWith("is_")).map(([key, val]) => (
                            <div key={key} className="flex justify-between gap-2">
                              <span className="truncate" style={{ color: "var(--color-text-muted)" }}>{key.replace(/_/g, " ")}</span>
                              <span className="truncate text-right" style={{ color: "var(--color-text-primary)" }}>{String(val)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          ) : (
            <div className="rounded-xl p-8 text-center" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
              <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>No documents uploaded yet.</p>
            </div>
          )}
        </div>
      )}

      {/* Tasks Tab */}
      {activeTab === "tasks" && (
        <div className="space-y-3">
          {tasks.length > 0 ? (
            tasks.map((task, idx) => (
              <div key={idx} className="rounded-xl p-4" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${task.status === "running" ? "animate-pulse" : ""}`} style={{
                      background: task.status === "completed" ? "var(--color-success)" :
                        task.status === "failed" ? "var(--color-error)" :
                        task.status === "running" ? "var(--color-info)" :
                        "var(--color-text-muted)"
                    }} />
                    <p className="text-sm font-medium" style={{ color: "var(--color-text-primary)" }}>{task.task_type || task.name || `Task ${idx + 1}`}</p>
                  </div>
                  <span className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>{task.created_at ? timeAgo(task.created_at) : ""}</span>
                </div>
                {task.result && (
                  <p className="text-xs pl-4" style={{ color: "var(--color-text-secondary)" }}>{typeof task.result === "string" ? task.result : JSON.stringify(task.result)}</p>
                )}
                {task.error && (
                  <p className="text-xs pl-4" style={{ color: "var(--color-error)" }}>{task.error}</p>
                )}
              </div>
            ))
          ) : (
            <div className="rounded-xl p-8 text-center" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
              <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>No AI agent tasks for this company.</p>
            </div>
          )}
        </div>
      )}

      {/* Notes Tab */}
      {activeTab === "notes" && (
        <div>
          <div className="rounded-xl p-5 mb-6" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
            <h3 className="text-sm font-semibold mb-3">Add Internal Note</h3>
            <textarea
              value={noteContent}
              onChange={(e) => setNoteContent(e.target.value)}
              placeholder="Type your internal note here..."
              className="w-full rounded-lg p-3 text-sm resize-none focus:outline-none"
              style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
              rows={3}
            />
            <div className="flex justify-end mt-3">
              <button
                onClick={handleAddNote}
                disabled={!noteContent.trim() || addingNote}
                className="px-4 py-2 rounded-lg text-xs font-medium transition-colors disabled:opacity-50"
                style={{ background: "var(--color-accent-purple)", color: "var(--color-text-primary)" }}
              >
                {addingNote ? "Adding..." : "Add Note"}
              </button>
            </div>
          </div>
          <div className="space-y-3">
            {company.notes && company.notes.length > 0 ? (
              company.notes.map((note: any, idx: number) => (
                <div key={idx} className="rounded-xl p-4" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium" style={{ color: "var(--color-accent-purple-light)" }}>{note.author_name || note.author || "Admin"}</span>
                    <span className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>{note.created_at ? new Date(note.created_at).toLocaleString() : ""}</span>
                  </div>
                  <p className="text-sm" style={{ color: "var(--color-text-primary)" }}>{note.content}</p>
                </div>
              ))
            ) : (
              <div className="rounded-xl p-8 text-center" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
                <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>No internal notes yet.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Communication Tab */}
      {activeTab === "communication" && (
        <div>
          <div className="rounded-xl p-5 mb-6" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
            <h3 className="text-sm font-semibold mb-3">Send Message to Customer</h3>
            <textarea
              value={messageContent}
              onChange={(e) => setMessageContent(e.target.value)}
              placeholder="Type your message to the customer..."
              className="w-full rounded-lg p-3 text-sm resize-none focus:outline-none"
              style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
              rows={3}
            />
            <div className="flex justify-end mt-3">
              <button
                onClick={handleSendMessage}
                disabled={!messageContent.trim() || sendingMessage}
                className="px-4 py-2 rounded-lg text-xs font-medium transition-colors disabled:opacity-50"
                style={{ background: "var(--color-info)", color: "var(--color-text-primary)" }}
              >
                {sendingMessage ? "Sending..." : "Send Message"}
              </button>
            </div>
          </div>
          <div className="space-y-3">
            {company.messages && company.messages.length > 0 ? (
              company.messages.map((msg: any, idx: number) => (
                <div key={idx} className="rounded-xl p-4" style={
                  msg.direction === "outgoing"
                    ? { border: "1px solid rgba(59, 130, 246, 0.2)", background: "rgba(59, 130, 246, 0.05)" }
                    : { border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }
                }>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium" style={{ color: msg.direction === "outgoing" ? "var(--color-info)" : "var(--color-text-secondary)" }}>
                      {msg.direction === "outgoing" ? "Sent to customer" : "From customer"}
                    </span>
                    <span className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>{msg.created_at ? new Date(msg.created_at).toLocaleString() : ""}</span>
                  </div>
                  <p className="text-sm" style={{ color: "var(--color-text-primary)" }}>{msg.message || msg.content}</p>
                </div>
              ))
            ) : (
              <div className="rounded-xl p-8 text-center" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
                <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>No messages yet.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Payments Tab */}
      {activeTab === "payments" && (
        <div className="space-y-3">
          {company.payments && company.payments.length > 0 ? (
            <div className="rounded-xl overflow-hidden" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
              <table className="w-full text-sm">
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                    <th className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Date</th>
                    <th className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Amount</th>
                    <th className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Status</th>
                    <th className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Method</th>
                    <th className="text-left px-5 py-3 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Ref</th>
                  </tr>
                </thead>
                <tbody>
                  {company.payments.map((payment: any, idx: number) => (
                    <tr key={idx} className="transition-colors">
                      <td className="px-5 py-3" style={{ color: "var(--color-text-primary)" }}>{payment.created_at ? new Date(payment.created_at).toLocaleDateString() : "--"}</td>
                      <td className="px-5 py-3 font-medium" style={{ color: "var(--color-text-primary)" }}>{payment.amount ? `₹${payment.amount.toLocaleString()}` : "--"}</td>
                      <td className="px-5 py-3">
                        <span className="text-xs font-semibold px-2 py-0.5 rounded-full" style={
                          payment.status === "completed" || payment.status === "paid" ? { background: "rgba(16, 185, 129, 0.15)", color: "var(--color-success)", border: "1px solid rgba(16, 185, 129, 0.3)" } :
                          payment.status === "failed" ? { background: "rgba(239, 68, 68, 0.15)", color: "var(--color-error)", border: "1px solid rgba(239, 68, 68, 0.3)" } :
                          { background: "rgba(245, 158, 11, 0.15)", color: "var(--color-warning)", border: "1px solid rgba(245, 158, 11, 0.3)" }
                        }>
                          {payment.status?.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-5 py-3" style={{ color: "var(--color-text-secondary)" }}>{payment.method || "--"}</td>
                      <td className="px-5 py-3 font-mono text-xs" style={{ color: "var(--color-text-muted)" }}>{payment.reference_id || payment.razorpay_payment_id || "--"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="rounded-xl p-8 text-center" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }}>
              <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>No payment records.</p>
            </div>
          )}
        </div>
      )}

      {/* Modals */}

      {/* Status Change Modal */}
      {showStatusModal && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowStatusModal(false)}>
          <div className="rounded-xl p-6 w-full max-w-md" style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)" }} onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold mb-4">Change Status</h3>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="w-full rounded-lg p-3 text-sm mb-3 focus:outline-none"
              style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
            >
              {STATUS_OPTIONS.map((s) => (
                <option key={s} value={s}>{s.replace(/_/g, " ").toUpperCase()}</option>
              ))}
            </select>
            <textarea
              value={statusNote}
              onChange={(e) => setStatusNote(e.target.value)}
              placeholder="Optional note..."
              className="w-full rounded-lg p-3 text-sm resize-none mb-4 focus:outline-none"
              style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
              rows={2}
            />
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowStatusModal(false)} className="px-4 py-2 rounded-lg text-sm transition-colors" style={{ color: "var(--color-text-secondary)" }}>Cancel</button>
              <button onClick={handleStatusChange} disabled={actionLoading} className="px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50" style={{ background: "var(--color-info)", color: "var(--color-text-primary)" }}>
                {actionLoading ? "Updating..." : "Update Status"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Assign Modal */}
      {showAssignModal && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowAssignModal(false)}>
          <div className="rounded-xl p-6 w-full max-w-md" style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)" }} onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold mb-4">Assign Company</h3>
            <select
              value={selectedAssignee || ""}
              onChange={(e) => setSelectedAssignee(Number(e.target.value))}
              className="w-full rounded-lg p-3 text-sm mb-4 focus:outline-none"
              style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
            >
              <option value="">Select team member...</option>
              {team.map((member) => (
                <option key={member.id} value={member.id}>{member.full_name} ({member.role || member.email})</option>
              ))}
            </select>
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowAssignModal(false)} className="px-4 py-2 rounded-lg text-sm transition-colors" style={{ color: "var(--color-text-secondary)" }}>Cancel</button>
              <button onClick={handleAssign} disabled={!selectedAssignee || actionLoading} className="px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50" style={{ background: "var(--color-accent-purple)", color: "var(--color-text-primary)" }}>
                {actionLoading ? "Assigning..." : "Assign"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Priority Modal */}
      {showPriorityModal && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowPriorityModal(false)}>
          <div className="rounded-xl p-6 w-full max-w-md" style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)" }} onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold mb-4">Set Priority</h3>
            <div className="space-y-2 mb-4">
              {PRIORITY_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setSelectedPriority(opt.value)}
                  className="w-full text-left px-4 py-3 rounded-lg transition-colors"
                  style={selectedPriority === opt.value
                    ? { border: "1px solid rgba(139, 92, 246, 0.5)", background: "rgba(139, 92, 246, 0.1)" }
                    : { border: "1px solid var(--color-border)", background: "var(--color-bg-card)" }
                  }
                >
                  <span className="text-sm font-medium" style={{ color: opt.color }}>{opt.label}</span>
                </button>
              ))}
            </div>
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowPriorityModal(false)} className="px-4 py-2 rounded-lg text-sm transition-colors" style={{ color: "var(--color-text-secondary)" }}>Cancel</button>
              <button onClick={handlePriorityChange} disabled={!selectedPriority || actionLoading} className="px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50" style={{ background: "var(--color-warning)", color: "var(--color-text-primary)" }}>
                {actionLoading ? "Saving..." : "Set Priority"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
