"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import {
  getCaCompanyCompliance,
  getCaCompanyDocuments,
  markFilingComplete,
  getCaAuditPack,
  getCaTaskNotes,
  addCaTaskNote,
} from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ComplianceTask {
  id: number;
  title: string;
  task_type: string;
  due_date: string;
  status: string;
  filing_reference?: string;
  company_name?: string;
}

interface CompanyDocument {
  id: number;
  name: string;
  document_type: string;
  status: string;
  uploaded_at: string;
  file_url?: string;
}

interface AuditChecklistItem {
  label: string;
  filed: boolean;
}

interface AuditPack {
  company_name?: string;
  compliance_score?: number;
  checklist?: AuditChecklistItem[];
  task_summary?: {
    total: number;
    completed: number;
    overdue: number;
    pending: number;
  };
  tasks?: ComplianceTask[];
  generated_at?: string;
}

interface TaskNote {
  id: number;
  note: string;
  author: string;
  created_at: string;
}

// ---------------------------------------------------------------------------
// Theme
// ---------------------------------------------------------------------------
const T = {
  accent: "#0d9488",
  accentLight: "#14b8a6",
  accentBg: "rgba(20, 184, 166, 0.08)",
  textPrimary: "#0f172a",
  textSecondary: "#475569",
  textMuted: "#94a3b8",
  cardBg: "#ffffff",
  cardBorder: "#e2e8f0",
  pageBg: "#f8fafc",
  rose: "#dc2626",
  roseBg: "rgba(220, 38, 38, 0.06)",
  amber: "#d97706",
  amberBg: "rgba(217, 119, 6, 0.06)",
  emerald: "#059669",
  emeraldBg: "rgba(5, 150, 105, 0.06)",
  blue: "#2563eb",
  blueBg: "rgba(37, 99, 235, 0.06)",
};

function statusStyle(status: string) {
  switch (status) {
    case "overdue":
      return { bg: T.roseBg, color: T.rose };
    case "due_soon":
      return { bg: T.amberBg, color: T.amber };
    case "upcoming":
      return { bg: T.blueBg, color: T.blue };
    case "completed":
      return { bg: T.emeraldBg, color: T.emerald };
    default:
      return { bg: T.accentBg, color: T.accent };
  }
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CaCompanyDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();

  const [tab, setTab] = useState<"compliance" | "documents" | "audit">("compliance");
  const [tasks, setTasks] = useState<ComplianceTask[]>([]);
  const [docs, setDocs] = useState<CompanyDocument[]>([]);
  const [auditPack, setAuditPack] = useState<AuditPack | null>(null);
  const [auditLoading, setAuditLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Filing modal state
  const [filingModal, setFilingModal] = useState<ComplianceTask | null>(null);
  const [filingRef, setFilingRef] = useState("");
  const [filingLoading, setFilingLoading] = useState(false);
  const [filingError, setFilingError] = useState("");
  const [noteError, setNoteError] = useState<Record<number, string>>({});

  // Task notes state
  const [expandedNotes, setExpandedNotes] = useState<Record<number, boolean>>({});
  const [taskNotes, setTaskNotes] = useState<Record<number, TaskNote[]>>({});
  const [notesLoading, setNotesLoading] = useState<Record<number, boolean>>({});
  const [newNote, setNewNote] = useState<Record<number, string>>({});
  const [addingNote, setAddingNote] = useState<Record<number, boolean>>({});

  const companyId = Number(id);
  const companyName = tasks[0]?.company_name || `Company #${id}`;

  useEffect(() => {
    if (authLoading || !user) return;

    (async () => {
      try {
        const [complianceData, docsData] = await Promise.all([
          getCaCompanyCompliance(companyId),
          getCaCompanyDocuments(companyId),
        ]);
        setTasks(Array.isArray(complianceData) ? complianceData : complianceData.tasks || []);
        setDocs(Array.isArray(docsData) ? docsData : docsData.documents || []);
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Failed to load company data";
        setError(message);
      } finally {
        setLoading(false);
      }
    })();
  }, [user, authLoading, companyId]);

  // Load audit pack when tab switches to audit
  useEffect(() => {
    if (tab !== "audit" || auditPack || auditLoading) return;
    let cancelled = false;
    setAuditLoading(true);
    getCaAuditPack(companyId)
      .then((data) => { if (!cancelled) setAuditPack(data); })
      .catch((err) => { if (!cancelled) console.error("Failed to load audit pack:", err); })
      .finally(() => { if (!cancelled) setAuditLoading(false); });
    return () => { cancelled = true; };
  }, [tab, companyId, auditPack, auditLoading]);

  const handleMarkComplete = async () => {
    if (!filingModal || !filingRef.trim()) return;
    setFilingLoading(true);
    setFilingError("");
    try {
      await markFilingComplete(companyId, filingModal.id, filingRef.trim());
      const updated = await getCaCompanyCompliance(companyId);
      setTasks(Array.isArray(updated) ? updated : updated.tasks || []);
      setFilingModal(null);
      setFilingRef("");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to mark filing complete";
      setFilingError(message);
    } finally {
      setFilingLoading(false);
    }
  };

  const toggleNotes = async (taskId: number) => {
    const isOpen = expandedNotes[taskId];
    setExpandedNotes((prev) => ({ ...prev, [taskId]: !isOpen }));

    if (!isOpen && !taskNotes[taskId]) {
      setNotesLoading((prev) => ({ ...prev, [taskId]: true }));
      try {
        const notes = await getCaTaskNotes(companyId, taskId);
        setTaskNotes((prev) => ({
          ...prev,
          [taskId]: Array.isArray(notes) ? notes : notes.notes || [],
        }));
      } catch {
        setTaskNotes((prev) => ({ ...prev, [taskId]: [] }));
      } finally {
        setNotesLoading((prev) => ({ ...prev, [taskId]: false }));
      }
    }
  };

  const handleAddNote = async (taskId: number) => {
    const noteText = newNote[taskId]?.trim();
    if (!noteText) return;
    setAddingNote((prev) => ({ ...prev, [taskId]: true }));
    try {
      await addCaTaskNote(companyId, taskId, noteText);
      const notes = await getCaTaskNotes(companyId, taskId);
      setTaskNotes((prev) => ({
        ...prev,
        [taskId]: Array.isArray(notes) ? notes : notes.notes || [],
      }));
      setNewNote((prev) => ({ ...prev, [taskId]: "" }));
      setNoteError((prev) => ({ ...prev, [taskId]: "" }));
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to add note";
      setNoteError((prev) => ({ ...prev, [taskId]: message }));
    } finally {
      setAddingNote((prev) => ({ ...prev, [taskId]: false }));
    }
  };

  const handleCopyAuditPack = () => {
    if (!auditPack) return;
    navigator.clipboard.writeText(JSON.stringify(auditPack, null, 2));
  };

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: T.accent }} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-10">
        <div className="rounded-xl p-6 text-center text-sm" style={{ background: T.roseBg, color: T.rose, border: `1px solid rgba(220,38,38,0.15)` }}>
          {error}
        </div>
      </div>
    );
  }

  const pendingCount = tasks.filter((t) => t.status !== "completed").length;
  const overdueCount = tasks.filter((t) => t.status === "overdue").length;

  const tabItems: { key: "compliance" | "documents" | "audit"; label: string }[] = [
    { key: "compliance", label: "Compliance Tasks" },
    { key: "documents", label: "Documents" },
    { key: "audit", label: "Audit Pack" },
  ];

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 lg:py-10">
      {/* ── Breadcrumb + Header ─────────────────────────────── */}
      <div className="mb-6">
        <Link
          href="/ca/companies"
          className="inline-flex items-center gap-1.5 text-sm font-medium mb-3 transition-colors"
          style={{ color: T.accent }}
          onMouseEnter={(e) => { e.currentTarget.style.color = "#0f766e"; }}
          onMouseLeave={(e) => { e.currentTarget.style.color = T.accent; }}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
          Back to Companies
        </Link>

        <h1
          className="text-2xl font-bold mb-2"
          style={{ fontFamily: "var(--font-display)", color: T.textPrimary }}
        >
          {companyName}
        </h1>

        {/* Summary badges */}
        <div className="flex flex-wrap gap-2">
          <span
            className="inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full"
            style={{ background: T.accentBg, color: T.accent }}
          >
            {tasks.length} total tasks
          </span>
          {pendingCount > 0 && (
            <span
              className="inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full"
              style={{ background: T.amberBg, color: T.amber }}
            >
              {pendingCount} pending
            </span>
          )}
          {overdueCount > 0 && (
            <span
              className="inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full"
              style={{ background: T.roseBg, color: T.rose }}
            >
              {overdueCount} overdue
            </span>
          )}
        </div>
      </div>

      {/* ── Tab Switcher ────────────────────────────────────── */}
      <div className="flex gap-1 mb-6 p-1 rounded-lg w-fit" style={{ background: "#f1f5f9" }}>
        {tabItems.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className="px-4 py-2 rounded-md text-sm font-medium transition-colors"
            style={{
              background: tab === t.key ? T.cardBg : "transparent",
              color: tab === t.key ? T.textPrimary : T.textMuted,
              boxShadow: tab === t.key ? "0 1px 3px rgba(0,0,0,0.08)" : "none",
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* ── Compliance Tasks Tab ────────────────────────────── */}
      {tab === "compliance" && (
        <div
          className="rounded-xl overflow-hidden"
          style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}` }}
        >
          {tasks.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-sm" style={{ color: T.textMuted }}>
                No compliance tasks found for this company.
              </p>
            </div>
          ) : (
            <>
              {/* Header — hidden on mobile, shown on lg */}
              <div
                className="hidden lg:grid grid-cols-[1fr_100px_100px_90px_100px] gap-3 px-5 py-3 text-xs font-semibold uppercase tracking-wider"
                style={{ color: T.textMuted, borderBottom: `1px solid ${T.cardBorder}`, background: T.pageBg }}
              >
                <div>Task</div>
                <div>Type</div>
                <div>Due Date</div>
                <div>Status</div>
                <div className="text-right">Action</div>
              </div>

              {/* Rows */}
              {tasks.map((task, idx) => {
                const s = statusStyle(task.status);
                const notesOpen = expandedNotes[task.id];
                const notes = taskNotes[task.id] || [];
                const loadingNotes = notesLoading[task.id];
                return (
                  <div key={task.id}>
                    <div
                      className="flex flex-col gap-2 px-5 py-3.5 lg:grid lg:grid-cols-[1fr_100px_100px_90px_100px] lg:gap-3 lg:items-center text-sm"
                      style={{
                        borderBottom: (idx < tasks.length - 1 && !notesOpen) ? `1px solid ${T.cardBorder}` : undefined,
                      }}
                    >
                      {/* Title + filing ref */}
                      <div className="min-w-0">
                        <div className="font-medium truncate" style={{ color: T.textPrimary }}>
                          {task.title}
                        </div>
                        {task.filing_reference && (
                          <div className="text-[11px] font-mono mt-0.5 truncate" style={{ color: T.textMuted }}>
                            Ref: {task.filing_reference}
                          </div>
                        )}
                        <button
                          onClick={() => toggleNotes(task.id)}
                          className="text-[11px] font-medium mt-1 transition-colors"
                          style={{ color: T.accent }}
                          aria-expanded={notesOpen}
                          aria-label={`${notesOpen ? "Hide" : "Show"} notes for ${task.title}`}
                        >
                          {notesOpen ? "Hide Notes" : "Notes"}
                          {notes.length > 0 && ` (${notes.length})`}
                        </button>
                      </div>

                      {/* Mobile: inline meta row */}
                      <div className="flex flex-wrap items-center gap-2 lg:contents">
                        {/* Type */}
                        <span className="text-xs capitalize" style={{ color: T.textSecondary }}>
                          {task.task_type.replace(/_/g, " ")}
                        </span>

                        {/* Due date */}
                        <span className="text-xs" style={{ color: T.textSecondary }}>
                          {formatDate(task.due_date)}
                        </span>

                        {/* Status badge */}
                        <span
                          className="inline-flex text-[11px] font-semibold px-2 py-0.5 rounded-full capitalize"
                          style={{ background: s.bg, color: s.color }}
                        >
                          {task.status.replace(/_/g, " ")}
                        </span>

                        {/* Action */}
                        <span className="lg:text-right lg:ml-auto">
                          {task.status !== "completed" ? (
                            <button
                              onClick={() => { setFilingModal(task); setFilingRef(""); setFilingError(""); }}
                              className="text-xs font-medium px-3 py-1.5 rounded-lg transition-colors"
                              style={{ background: T.accentBg, color: T.accent }}
                              onMouseEnter={(e) => { e.currentTarget.style.background = T.accent; e.currentTarget.style.color = "#fff"; }}
                              onMouseLeave={(e) => { e.currentTarget.style.background = T.accentBg; e.currentTarget.style.color = T.accent; }}
                            >
                              Mark Complete
                            </button>
                          ) : (
                            <span className="text-xs" style={{ color: T.emerald }}>
                              Done
                            </span>
                          )}
                        </span>
                      </div>
                    </div>

                    {/* Notes expand section */}
                    {notesOpen && (
                      <div
                        className="px-5 pb-4 pt-1"
                        style={{
                          background: T.pageBg,
                          borderBottom: idx < tasks.length - 1 ? `1px solid ${T.cardBorder}` : undefined,
                        }}
                      >
                        {loadingNotes ? (
                          <div className="flex items-center gap-2 py-3">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2" style={{ borderColor: T.accent }} />
                            <span className="text-xs" style={{ color: T.textMuted }}>Loading notes...</span>
                          </div>
                        ) : (
                          <>
                            {notes.length > 0 ? (
                              <div className="space-y-2 mb-3">
                                {notes.map((note) => (
                                  <div
                                    key={note.id}
                                    className="rounded-lg p-3 text-sm"
                                    style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}` }}
                                  >
                                    <p style={{ color: T.textPrimary }}>{note.note}</p>
                                    <div className="flex items-center gap-2 mt-1.5 text-[11px]" style={{ color: T.textMuted }}>
                                      <span className="font-medium">{note.author}</span>
                                      <span>&middot;</span>
                                      <span>{formatDate(note.created_at)}</span>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <p className="text-xs mb-3" style={{ color: T.textMuted }}>
                                No notes yet.
                              </p>
                            )}

                            {/* Note error */}
                            {noteError[task.id] && (
                              <div className="p-2 rounded-lg mb-2 text-xs" style={{ background: T.roseBg, color: T.rose }}>
                                {noteError[task.id]}
                              </div>
                            )}

                            {/* Add note form */}
                            <div className="flex gap-2">
                              <input
                                type="text"
                                value={newNote[task.id] || ""}
                                onChange={(e) =>
                                  setNewNote((prev) => ({ ...prev, [task.id]: e.target.value }))
                                }
                                placeholder="Add a note..."
                                className="flex-1 px-3 py-2 rounded-lg text-sm"
                                style={{
                                  background: T.cardBg,
                                  border: `1px solid ${T.cardBorder}`,
                                  color: T.textPrimary,
                                  outline: "none",
                                }}
                                onKeyDown={(e) => {
                                  if (e.key === "Enter" && !addingNote[task.id]) {
                                    handleAddNote(task.id);
                                  }
                                }}
                              />
                              <button
                                onClick={() => handleAddNote(task.id)}
                                disabled={!newNote[task.id]?.trim() || addingNote[task.id]}
                                className="px-3 py-2 rounded-lg text-xs font-medium text-white transition-colors disabled:opacity-50"
                                style={{ background: T.accent }}
                              >
                                {addingNote[task.id] ? "..." : "Add"}
                              </button>
                            </div>
                          </>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </>
          )}
        </div>
      )}

      {/* ── Documents Tab ───────────────────────────────────── */}
      {tab === "documents" && (
        <div
          className="rounded-xl overflow-hidden"
          style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}` }}
        >
          {docs.length === 0 ? (
            <div className="p-12 text-center">
              <svg className="w-10 h-10 mx-auto mb-3" style={{ color: T.textMuted }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
              </svg>
              <p className="text-sm font-medium mb-1" style={{ color: T.textPrimary }}>
                No documents yet
              </p>
              <p className="text-xs" style={{ color: T.textMuted }}>
                Documents uploaded by the company will appear here for review.
              </p>
            </div>
          ) : (
            <>
              {/* Header */}
              <div
                className="grid grid-cols-[1fr_120px_100px_110px] gap-3 px-5 py-3 text-xs font-semibold uppercase tracking-wider"
                style={{ color: T.textMuted, borderBottom: `1px solid ${T.cardBorder}`, background: T.pageBg }}
              >
                <div>Document</div>
                <div>Type</div>
                <div>Status</div>
                <div>Uploaded</div>
              </div>

              {/* Rows */}
              {docs.map((doc, idx) => (
                <div
                  key={doc.id}
                  className="grid grid-cols-[1fr_120px_100px_110px] gap-3 px-5 py-3.5 items-center text-sm"
                  style={{
                    borderBottom: idx < docs.length - 1 ? `1px solid ${T.cardBorder}` : undefined,
                  }}
                >
                  {/* Name */}
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <svg className="w-4 h-4 flex-shrink-0" style={{ color: T.textMuted }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                      </svg>
                      <span className="font-medium truncate" style={{ color: T.textPrimary }}>
                        {doc.name}
                      </span>
                    </div>
                  </div>

                  {/* Type */}
                  <div className="text-xs capitalize" style={{ color: T.textSecondary }}>
                    {doc.document_type.replace(/_/g, " ")}
                  </div>

                  {/* Status */}
                  <div>
                    <span
                      className="inline-flex text-[11px] font-medium px-2 py-0.5 rounded-full capitalize"
                      style={
                        doc.status === "verified"
                          ? { background: T.emeraldBg, color: T.emerald }
                          : doc.status === "rejected"
                          ? { background: T.roseBg, color: T.rose }
                          : { background: T.amberBg, color: T.amber }
                      }
                    >
                      {doc.status}
                    </span>
                  </div>

                  {/* Uploaded date */}
                  <div className="text-xs" style={{ color: T.textMuted }}>
                    {formatDate(doc.uploaded_at)}
                  </div>
                </div>
              ))}
            </>
          )}
        </div>
      )}

      {/* ── Audit Pack Tab ──────────────────────────────────── */}
      {tab === "audit" && (
        <div>
          {auditLoading ? (
            <div className="flex items-center justify-center py-20">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2" style={{ borderColor: T.accent }} />
            </div>
          ) : !auditPack ? (
            <div
              className="rounded-xl p-8 text-center"
              style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}` }}
            >
              <svg className="w-10 h-10 mx-auto mb-3" style={{ color: T.textMuted }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25z" />
              </svg>
              <p className="text-sm font-medium mb-1" style={{ color: T.textPrimary }}>
                No audit pack available
              </p>
              <p className="text-xs" style={{ color: T.textMuted }}>
                The audit pack will be generated once compliance tasks are created for this company.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Compliance Score + Actions */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  {auditPack.compliance_score != null && (
                    <div
                      className="flex items-center gap-2 px-4 py-2 rounded-lg"
                      style={{
                        background: auditPack.compliance_score >= 80 ? T.emeraldBg : auditPack.compliance_score >= 50 ? T.amberBg : T.roseBg,
                        border: `1px solid ${auditPack.compliance_score >= 80 ? "rgba(5,150,105,0.15)" : auditPack.compliance_score >= 50 ? "rgba(217,119,6,0.15)" : "rgba(220,38,38,0.15)"}`,
                      }}
                    >
                      <span className="text-xs font-medium" style={{ color: T.textSecondary }}>
                        Compliance Score
                      </span>
                      <span
                        className="text-lg font-bold"
                        style={{
                          color: auditPack.compliance_score >= 80 ? T.emerald : auditPack.compliance_score >= 50 ? T.amber : T.rose,
                        }}
                      >
                        {auditPack.compliance_score}%
                      </span>
                    </div>
                  )}
                </div>
                <button
                  onClick={handleCopyAuditPack}
                  className="inline-flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-colors"
                  style={{ background: T.accentBg, color: T.accent, border: `1px solid rgba(20,184,166,0.15)` }}
                >
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9.75a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184" />
                  </svg>
                  Copy JSON
                </button>
              </div>

              {/* Checklist */}
              {auditPack.checklist && auditPack.checklist.length > 0 && (
                <div
                  className="rounded-xl p-5"
                  style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}` }}
                >
                  <h2 className="text-sm font-semibold mb-4" style={{ color: T.textPrimary }}>
                    Audit Checklist
                  </h2>
                  <div className="space-y-2">
                    {auditPack.checklist.map((item, idx) => (
                      <div
                        key={idx}
                        className="flex items-center gap-3 py-1.5"
                      >
                        <div
                          className="w-5 h-5 rounded flex items-center justify-center flex-shrink-0"
                          style={{
                            background: item.filed ? T.emeraldBg : T.roseBg,
                            color: item.filed ? T.emerald : T.rose,
                          }}
                        >
                          {item.filed ? (
                            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                            </svg>
                          ) : (
                            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          )}
                        </div>
                        <span
                          className="text-sm"
                          style={{ color: item.filed ? T.textPrimary : T.textSecondary }}
                        >
                          {item.label}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Task Summary */}
              {auditPack.task_summary && (
                <div
                  className="rounded-xl p-5"
                  style={{ background: T.cardBg, border: `1px solid ${T.cardBorder}` }}
                >
                  <h2 className="text-sm font-semibold mb-4" style={{ color: T.textPrimary }}>
                    Task Summary
                  </h2>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="rounded-lg p-3" style={{ background: T.pageBg }}>
                      <div className="text-xs mb-1" style={{ color: T.textMuted }}>Total</div>
                      <div className="text-xl font-bold" style={{ color: T.textPrimary }}>
                        {auditPack.task_summary.total}
                      </div>
                    </div>
                    <div className="rounded-lg p-3" style={{ background: T.emeraldBg }}>
                      <div className="text-xs mb-1" style={{ color: T.emerald }}>Completed</div>
                      <div className="text-xl font-bold" style={{ color: T.emerald }}>
                        {auditPack.task_summary.completed}
                      </div>
                    </div>
                    <div className="rounded-lg p-3" style={{ background: T.roseBg }}>
                      <div className="text-xs mb-1" style={{ color: T.rose }}>Overdue</div>
                      <div className="text-xl font-bold" style={{ color: T.rose }}>
                        {auditPack.task_summary.overdue}
                      </div>
                    </div>
                    <div className="rounded-lg p-3" style={{ background: T.amberBg }}>
                      <div className="text-xs mb-1" style={{ color: T.amber }}>Pending</div>
                      <div className="text-xl font-bold" style={{ color: T.amber }}>
                        {auditPack.task_summary.pending}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Generated timestamp */}
              {auditPack.generated_at && (
                <p className="text-xs text-center" style={{ color: T.textMuted }}>
                  Generated: {formatDate(auditPack.generated_at)}
                </p>
              )}
            </div>
          )}
        </div>
      )}

      {/* ── Filing Modal ────────────────────────────────────── */}
      {filingModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center px-4"
          style={{ background: "rgba(0,0,0,0.4)" }}
          role="dialog"
          aria-modal="true"
          aria-label="Mark filing complete"
          onClick={() => setFilingModal(null)}
          onKeyDown={(e) => { if (e.key === "Escape") setFilingModal(null); }}
        >
          <div
            className="rounded-xl p-6 w-full max-w-md"
            style={{ background: T.cardBg }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-lg font-semibold mb-1" style={{ color: T.textPrimary }}>
              Mark Filing Complete
            </h3>
            <p className="text-sm mb-5" style={{ color: T.textSecondary }}>
              {filingModal.title}
            </p>

            {filingError && (
              <div className="p-3 rounded-lg mb-4 text-xs font-medium" style={{ background: T.roseBg, color: T.rose, border: `1px solid rgba(220,38,38,0.15)` }}>
                {filingError}
              </div>
            )}

            <label className="block text-sm font-medium mb-1.5" style={{ color: T.textSecondary }}>
              Filing Reference Number
            </label>
            <input
              type="text"
              value={filingRef}
              onChange={(e) => { setFilingRef(e.target.value); setFilingError(""); }}
              placeholder="e.g. ARN-12345678"
              className="w-full px-3 py-2.5 rounded-lg text-sm mb-5"
              style={{
                background: T.pageBg,
                border: `1px solid ${T.cardBorder}`,
                color: T.textPrimary,
                outline: "none",
              }}
              onFocus={(e) => { e.currentTarget.style.borderColor = T.accent; }}
              onBlur={(e) => { e.currentTarget.style.borderColor = T.cardBorder; }}
              autoFocus
            />

            <div className="flex justify-end gap-3">
              <button
                onClick={() => setFilingModal(null)}
                className="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                style={{ color: T.textSecondary, border: `1px solid ${T.cardBorder}` }}
              >
                Cancel
              </button>
              <button
                onClick={handleMarkComplete}
                disabled={!filingRef.trim() || filingLoading}
                className="px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors disabled:opacity-50"
                style={{ background: T.accent }}
              >
                {filingLoading ? "Submitting..." : "Confirm"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
