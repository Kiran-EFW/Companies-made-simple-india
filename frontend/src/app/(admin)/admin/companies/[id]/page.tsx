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
  { value: "normal", label: "Normal", color: "text-gray-400" },
  { value: "urgent", label: "Urgent", color: "text-amber-400" },
  { value: "vip", label: "VIP", color: "text-purple-400" },
];

const TABS = [
  { key: "overview", label: "Overview" },
  { key: "documents", label: "Documents" },
  { key: "tasks", label: "Tasks" },
  { key: "notes", label: "Notes" },
  { key: "communication", label: "Communication" },
  { key: "payments", label: "Payments" },
];

function getStatusBadgeClasses(status: string): string {
  if (["incorporated", "fully_setup", "bank_account_opened"].includes(status))
    return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
  if (["draft", "entity_selected"].includes(status))
    return "bg-gray-500/15 text-gray-400 border-gray-500/30";
  if (status.includes("rejected") || status.includes("query"))
    return "bg-red-500/15 text-red-400 border-red-500/30";
  if (status.includes("pending"))
    return "bg-amber-500/15 text-amber-400 border-amber-500/30";
  return "bg-blue-500/15 text-blue-400 border-blue-500/30";
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
        <div className="animate-pulse text-gray-500">Loading company details...</div>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="p-12 text-center">
        <h2 className="text-xl font-bold text-gray-300 mb-2">Company Not Found</h2>
        <p className="text-gray-500 mb-4">The company with ID #{companyId} could not be found.</p>
        <Link href="/admin/dashboard" className="text-purple-400 hover:text-purple-300 text-sm font-medium">
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
        <Link href="/admin/dashboard" className="text-xs text-gray-500 hover:text-purple-400 transition-colors">
          Dashboard
        </Link>
        <span className="text-xs text-gray-600 mx-2">/</span>
        <span className="text-xs text-gray-400">{displayName}</span>
      </div>

      {/* ── Header ── */}
      <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-6 mb-6">
        <div className="flex flex-col lg:flex-row justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold" style={{ fontFamily: "var(--font-display)" }}>{displayName}</h1>
              <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${getStatusBadgeClasses(company.status)}`}>
                {company.status.replace(/_/g, " ").toUpperCase()}
              </span>
            </div>
            <div className="flex items-center gap-4 text-xs text-gray-400">
              <span>{company.entity_type?.replace(/_/g, " ").toUpperCase()}</span>
              <span>State: {company.state?.toUpperCase()}</span>
              <span>Plan: {company.plan_tier?.toUpperCase()}</span>
              {company.priority && company.priority !== "normal" && (
                <span className={`font-bold ${company.priority === "vip" ? "text-purple-400" : "text-amber-400"}`}>
                  {company.priority.toUpperCase()}
                </span>
              )}
              {company.assigned_to_name && (
                <span>Assigned to: <strong className="text-white">{company.assigned_to_name}</strong></span>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => { setSelectedStatus(company.status); setShowStatusModal(true); }}
              className="px-3 py-2 rounded-lg text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20 hover:bg-blue-500/20 transition-colors"
            >
              Change Status
            </button>
            <button
              onClick={() => setShowAssignModal(true)}
              className="px-3 py-2 rounded-lg text-xs font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20 hover:bg-purple-500/20 transition-colors"
            >
              Assign
            </button>
            <button
              onClick={() => { setSelectedPriority(company.priority || "normal"); setShowPriorityModal(true); }}
              className="px-3 py-2 rounded-lg text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20 hover:bg-amber-500/20 transition-colors"
            >
              Set Priority
            </button>
          </div>
        </div>
      </div>

      {/* ── Tabs ── */}
      <div className="flex gap-1 mb-6 overflow-x-auto border-b border-gray-700 pb-px">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2.5 text-sm font-medium whitespace-nowrap transition-colors relative ${
              activeTab === tab.key
                ? "text-purple-400"
                : "text-gray-500 hover:text-gray-300"
            }`}
          >
            {tab.label}
            {activeTab === tab.key && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-purple-500 rounded-full" />
            )}
          </button>
        ))}
      </div>

      {/* ── Tab Content ── */}

      {/* Overview Tab */}
      {activeTab === "overview" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Company Info */}
          <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-5">
            <h3 className="text-sm font-semibold mb-4">Company Information</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">ID</span>
                <span className="text-white font-mono">#{company.id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Entity Type</span>
                <span className="text-white">{company.entity_type?.replace(/_/g, " ")}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">State</span>
                <span className="text-white">{company.state}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Plan</span>
                <span className="text-white">{company.plan_tier}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Authorized Capital</span>
                <span className="text-white">{company.authorized_capital ? `₹${company.authorized_capital.toLocaleString()}` : "--"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Directors</span>
                <span className="text-white">{company.num_directors || "--"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Created</span>
                <span className="text-white">{new Date(company.created_at).toLocaleDateString()}</span>
              </div>
              {company.proposed_names && company.proposed_names.length > 0 && (
                <div>
                  <span className="text-gray-500 block mb-1">Proposed Names</span>
                  <div className="space-y-1">
                    {company.proposed_names.map((name: string, i: number) => (
                      <p key={i} className="text-xs text-gray-300 pl-2 border-l border-gray-700">{name}</p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Directors */}
          <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-5">
            <h3 className="text-sm font-semibold mb-4">Directors</h3>
            {company.directors && company.directors.length > 0 ? (
              <div className="space-y-3">
                {company.directors.map((dir: any, idx: number) => (
                  <div key={idx} className="p-3 rounded-lg border border-gray-700 bg-gray-900/30">
                    <p className="text-sm font-medium text-white">{dir.full_name || dir.name || `Director ${idx + 1}`}</p>
                    <div className="flex gap-4 mt-1 text-[10px] text-gray-500">
                      {dir.email && <span>{dir.email}</span>}
                      {dir.din && <span>DIN: {dir.din}</span>}
                      {dir.pan && <span>PAN: {dir.pan}</span>}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-500">No director information available.</p>
            )}
          </div>

          {/* Timeline */}
          <div className="lg:col-span-2 rounded-xl border border-gray-700 bg-gray-800/50 p-5">
            <h3 className="text-sm font-semibold mb-4">Status Timeline</h3>
            {logs.length > 0 ? (
              <div className="relative pl-6 space-y-4">
                <div className="absolute left-2 top-2 bottom-2 w-px bg-gray-700" />
                {logs.slice(0, 20).map((log, idx) => (
                  <div key={idx} className="relative">
                    <div className={`absolute left-[-18px] top-1.5 w-2.5 h-2.5 rounded-full border-2 ${
                      log.level === "SUCCESS" ? "bg-emerald-500 border-emerald-400" :
                      log.level === "ERROR" ? "bg-red-500 border-red-400" :
                      log.level === "WARN" ? "bg-amber-500 border-amber-400" :
                      "bg-purple-500 border-purple-400"
                    }`} />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-white">{log.agent_name || "System"}</span>
                        <span className="text-[10px] text-gray-600">{new Date(log.timestamp || log.created_at).toLocaleString()}</span>
                      </div>
                      <p className="text-xs text-gray-400 mt-0.5">{log.message}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-500">No timeline entries.</p>
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
                <div key={doc.id} className="rounded-xl border border-gray-700 bg-gray-800/50 overflow-hidden">
                  <div className="flex flex-col lg:flex-row">
                    {/* Document info */}
                    <div className="flex-1 p-5">
                      <div className="flex items-center gap-3 mb-3">
                        <span className="text-xs uppercase tracking-wider text-purple-400 font-bold">
                          {doc.doc_type?.replace(/_/g, " ")}
                        </span>
                        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                          doc.verification_status === "team_verified" ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" :
                          doc.verification_status === "ai_verified" ? "bg-blue-500/15 text-blue-400 border-blue-500/30" :
                          doc.verification_status === "rejected" ? "bg-red-500/15 text-red-400 border-red-500/30" :
                          "bg-amber-500/15 text-amber-400 border-amber-500/30"
                        }`}>
                          {doc.verification_status?.replace(/_/g, " ").toUpperCase()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-300 mb-1">{doc.original_filename}</p>
                      <p className="text-[10px] text-gray-500">Uploaded {new Date(doc.uploaded_at || doc.created_at).toLocaleString()}</p>
                    </div>

                    {/* Extracted data */}
                    {extracted && (
                      <div className="flex-1 p-5 border-t lg:border-t-0 lg:border-l border-gray-700 bg-gray-900/30">
                        <p className="text-xs font-semibold text-gray-400 mb-3">Extracted Data</p>
                        <div className="space-y-1.5 font-mono text-xs">
                          {Object.entries(extracted).filter(([k]) => !k.startsWith("is_")).map(([key, val]) => (
                            <div key={key} className="flex justify-between gap-2">
                              <span className="text-gray-500 truncate">{key.replace(/_/g, " ")}</span>
                              <span className="text-gray-300 truncate text-right">{String(val)}</span>
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
            <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-8 text-center">
              <p className="text-sm text-gray-500">No documents uploaded yet.</p>
            </div>
          )}
        </div>
      )}

      {/* Tasks Tab */}
      {activeTab === "tasks" && (
        <div className="space-y-3">
          {tasks.length > 0 ? (
            tasks.map((task, idx) => (
              <div key={idx} className="rounded-xl border border-gray-700 bg-gray-800/50 p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${
                      task.status === "completed" ? "bg-emerald-500" :
                      task.status === "failed" ? "bg-red-500" :
                      task.status === "running" ? "bg-blue-500 animate-pulse" :
                      "bg-gray-500"
                    }`} />
                    <p className="text-sm font-medium text-white">{task.task_type || task.name || `Task ${idx + 1}`}</p>
                  </div>
                  <span className="text-[10px] text-gray-500">{task.created_at ? timeAgo(task.created_at) : ""}</span>
                </div>
                {task.result && (
                  <p className="text-xs text-gray-400 pl-4">{typeof task.result === "string" ? task.result : JSON.stringify(task.result)}</p>
                )}
                {task.error && (
                  <p className="text-xs text-red-400 pl-4">{task.error}</p>
                )}
              </div>
            ))
          ) : (
            <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-8 text-center">
              <p className="text-sm text-gray-500">No AI agent tasks for this company.</p>
            </div>
          )}
        </div>
      )}

      {/* Notes Tab */}
      {activeTab === "notes" && (
        <div>
          {/* Add Note Form */}
          <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-5 mb-6">
            <h3 className="text-sm font-semibold mb-3">Add Internal Note</h3>
            <textarea
              value={noteContent}
              onChange={(e) => setNoteContent(e.target.value)}
              placeholder="Type your internal note here..."
              className="w-full bg-gray-900/50 border border-gray-700 rounded-lg p-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-purple-500/50 resize-none"
              rows={3}
            />
            <div className="flex justify-end mt-3">
              <button
                onClick={handleAddNote}
                disabled={!noteContent.trim() || addingNote}
                className="px-4 py-2 rounded-lg text-xs font-medium bg-purple-600 hover:bg-purple-500 text-white transition-colors disabled:opacity-50"
              >
                {addingNote ? "Adding..." : "Add Note"}
              </button>
            </div>
          </div>

          {/* Notes List */}
          <div className="space-y-3">
            {company.notes && company.notes.length > 0 ? (
              company.notes.map((note: any, idx: number) => (
                <div key={idx} className="rounded-xl border border-gray-700 bg-gray-800/50 p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-purple-400">{note.author_name || note.author || "Admin"}</span>
                    <span className="text-[10px] text-gray-500">{note.created_at ? new Date(note.created_at).toLocaleString() : ""}</span>
                  </div>
                  <p className="text-sm text-gray-300">{note.content}</p>
                </div>
              ))
            ) : (
              <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-8 text-center">
                <p className="text-sm text-gray-500">No internal notes yet.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Communication Tab */}
      {activeTab === "communication" && (
        <div>
          {/* Send Message Form */}
          <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-5 mb-6">
            <h3 className="text-sm font-semibold mb-3">Send Message to Customer</h3>
            <textarea
              value={messageContent}
              onChange={(e) => setMessageContent(e.target.value)}
              placeholder="Type your message to the customer..."
              className="w-full bg-gray-900/50 border border-gray-700 rounded-lg p-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-purple-500/50 resize-none"
              rows={3}
            />
            <div className="flex justify-end mt-3">
              <button
                onClick={handleSendMessage}
                disabled={!messageContent.trim() || sendingMessage}
                className="px-4 py-2 rounded-lg text-xs font-medium bg-blue-600 hover:bg-blue-500 text-white transition-colors disabled:opacity-50"
              >
                {sendingMessage ? "Sending..." : "Send Message"}
              </button>
            </div>
          </div>

          {/* Messages List */}
          <div className="space-y-3">
            {company.messages && company.messages.length > 0 ? (
              company.messages.map((msg: any, idx: number) => (
                <div key={idx} className={`rounded-xl border p-4 ${
                  msg.direction === "outgoing"
                    ? "border-blue-500/20 bg-blue-500/5"
                    : "border-gray-700 bg-gray-800/50"
                }`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className={`text-xs font-medium ${msg.direction === "outgoing" ? "text-blue-400" : "text-gray-400"}`}>
                      {msg.direction === "outgoing" ? "Sent to customer" : "From customer"}
                    </span>
                    <span className="text-[10px] text-gray-500">{msg.created_at ? new Date(msg.created_at).toLocaleString() : ""}</span>
                  </div>
                  <p className="text-sm text-gray-300">{msg.message || msg.content}</p>
                </div>
              ))
            ) : (
              <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-8 text-center">
                <p className="text-sm text-gray-500">No messages yet.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Payments Tab */}
      {activeTab === "payments" && (
        <div className="space-y-3">
          {company.payments && company.payments.length > 0 ? (
            <div className="rounded-xl border border-gray-700 bg-gray-800/50 overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">Date</th>
                    <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">Amount</th>
                    <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">Status</th>
                    <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">Method</th>
                    <th className="text-left px-5 py-3 text-xs text-gray-500 font-medium uppercase tracking-wider">Ref</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700/50">
                  {company.payments.map((payment: any, idx: number) => (
                    <tr key={idx} className="hover:bg-white/5 transition-colors">
                      <td className="px-5 py-3 text-gray-300">{payment.created_at ? new Date(payment.created_at).toLocaleDateString() : "--"}</td>
                      <td className="px-5 py-3 text-white font-medium">{payment.amount ? `₹${payment.amount.toLocaleString()}` : "--"}</td>
                      <td className="px-5 py-3">
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${
                          payment.status === "completed" || payment.status === "paid" ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" :
                          payment.status === "failed" ? "bg-red-500/15 text-red-400 border-red-500/30" :
                          "bg-amber-500/15 text-amber-400 border-amber-500/30"
                        }`}>
                          {payment.status?.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-5 py-3 text-gray-400">{payment.method || "--"}</td>
                      <td className="px-5 py-3 text-gray-500 font-mono text-xs">{payment.reference_id || payment.razorpay_payment_id || "--"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-8 text-center">
              <p className="text-sm text-gray-500">No payment records.</p>
            </div>
          )}
        </div>
      )}

      {/* ── Modals ── */}

      {/* Status Change Modal */}
      {showStatusModal && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowStatusModal(false)}>
          <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 w-full max-w-md" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold mb-4">Change Status</h3>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-sm text-white mb-3 focus:outline-none focus:border-purple-500/50"
            >
              {STATUS_OPTIONS.map((s) => (
                <option key={s} value={s}>{s.replace(/_/g, " ").toUpperCase()}</option>
              ))}
            </select>
            <textarea
              value={statusNote}
              onChange={(e) => setStatusNote(e.target.value)}
              placeholder="Optional note..."
              className="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-purple-500/50 resize-none mb-4"
              rows={2}
            />
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowStatusModal(false)} className="px-4 py-2 rounded-lg text-sm text-gray-400 hover:bg-white/5 transition-colors">Cancel</button>
              <button onClick={handleStatusChange} disabled={actionLoading} className="px-4 py-2 rounded-lg text-sm font-medium bg-blue-600 hover:bg-blue-500 text-white transition-colors disabled:opacity-50">
                {actionLoading ? "Updating..." : "Update Status"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Assign Modal */}
      {showAssignModal && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowAssignModal(false)}>
          <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 w-full max-w-md" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold mb-4">Assign Company</h3>
            <select
              value={selectedAssignee || ""}
              onChange={(e) => setSelectedAssignee(Number(e.target.value))}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-sm text-white mb-4 focus:outline-none focus:border-purple-500/50"
            >
              <option value="">Select team member...</option>
              {team.map((member) => (
                <option key={member.id} value={member.id}>{member.full_name} ({member.role || member.email})</option>
              ))}
            </select>
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowAssignModal(false)} className="px-4 py-2 rounded-lg text-sm text-gray-400 hover:bg-white/5 transition-colors">Cancel</button>
              <button onClick={handleAssign} disabled={!selectedAssignee || actionLoading} className="px-4 py-2 rounded-lg text-sm font-medium bg-purple-600 hover:bg-purple-500 text-white transition-colors disabled:opacity-50">
                {actionLoading ? "Assigning..." : "Assign"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Priority Modal */}
      {showPriorityModal && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setShowPriorityModal(false)}>
          <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 w-full max-w-md" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold mb-4">Set Priority</h3>
            <div className="space-y-2 mb-4">
              {PRIORITY_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setSelectedPriority(opt.value)}
                  className={`w-full text-left px-4 py-3 rounded-lg border transition-colors ${
                    selectedPriority === opt.value
                      ? "border-purple-500/50 bg-purple-500/10"
                      : "border-gray-700 bg-gray-800/50 hover:bg-gray-800"
                  }`}
                >
                  <span className={`text-sm font-medium ${opt.color}`}>{opt.label}</span>
                </button>
              ))}
            </div>
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowPriorityModal(false)} className="px-4 py-2 rounded-lg text-sm text-gray-400 hover:bg-white/5 transition-colors">Cancel</button>
              <button onClick={handlePriorityChange} disabled={!selectedPriority || actionLoading} className="px-4 py-2 rounded-lg text-sm font-medium bg-amber-600 hover:bg-amber-500 text-white transition-colors disabled:opacity-50">
                {actionLoading ? "Saving..." : "Set Priority"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
