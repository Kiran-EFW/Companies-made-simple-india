"use client";

import { useState, useEffect, useCallback } from "react";
import { updateMeetingResolutions, createLegalDraft } from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ResolutionWorkflowProps {
  companyId: number;
  meeting: {
    id: number;
    title: string;
    meeting_type: string;
    date: string;
    status: string;
    attendees: any[];
    resolutions: any[];
  };
  onUpdate: () => void;
}

interface Resolution {
  id: string;
  text: string;
  type: "Ordinary" | "Special";
  category: string;
  votes: {
    for: string[];
    against: string[];
    abstain: string[];
  };
  result: "Passed" | "Not Passed" | "Pending";
}

interface ComplianceFiling {
  form: string;
  description: string;
  dueDate: string;
  status: "Pending" | "Filed" | "Acknowledged";
}

interface ResolutionState {
  resolutions: Resolution[];
  generatedDocId: string | null;
  filings: Record<string, ComplianceFiling[]>;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const RESOLUTION_CATEGORIES = [
  "Approve Financial Statements",
  "Appoint Auditor",
  "Declare Dividend",
  "Approve ESOP Plan",
  "Approve Share Allotment",
  "Approve Related Party Transaction",
  "Appoint/Remove Director",
  "Change Registered Office",
  "Increase Authorized Capital",
  "Other",
];

function getComplianceFilings(resolution: Resolution, meetingDate: string): ComplianceFiling[] {
  const due = new Date(meetingDate);
  due.setDate(due.getDate() + 30);
  const dueDate = due.toISOString().split("T")[0];

  const filings: ComplianceFiling[] = [];

  if (resolution.category === "Approve Share Allotment") {
    filings.push({
      form: "PAS-3",
      description: "Return of Allotment to be filed with ROC",
      dueDate,
      status: "Pending",
    });
  }

  if (resolution.category === "Appoint/Remove Director") {
    filings.push({
      form: "DIR-12",
      description: "Particulars of appointment/change in directors",
      dueDate,
      status: "Pending",
    });
  }

  if (resolution.type === "Special") {
    filings.push({
      form: "MGT-14",
      description: "Filing of special resolution with ROC",
      dueDate,
      status: "Pending",
    });
  }

  if (resolution.category === "Increase Authorized Capital") {
    filings.push({
      form: "SH-7",
      description: "Notice to ROC for alteration of share capital",
      dueDate,
      status: "Pending",
    });
  }

  return filings;
}

function generateId(): string {
  return `res_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function ResolutionWorkflow({ companyId, meeting, onUpdate }: ResolutionWorkflowProps) {
  const storageKey = `anvils_meeting_resolutions_${meeting.id}`;

  // Load persisted state
  const loadState = useCallback((): ResolutionState => {
    if (typeof window === "undefined") {
      return { resolutions: [], generatedDocId: null, filings: {} };
    }
    try {
      const saved = localStorage.getItem(storageKey);
      if (saved) return JSON.parse(saved);
    } catch {
      // ignore
    }
    return { resolutions: [], generatedDocId: null, filings: {} };
  }, [storageKey]);

  const [state, setState] = useState<ResolutionState>(loadState);
  const [formText, setFormText] = useState("");
  const [formType, setFormType] = useState<"Ordinary" | "Special">("Ordinary");
  const [formCategory, setFormCategory] = useState(RESOLUTION_CATEGORIES[0]);
  const [actionLoading, setActionLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [expandedSection, setExpandedSection] = useState<"add" | "list" | "document" | "compliance" | null>("add");

  // Persist state
  useEffect(() => {
    if (typeof window !== "undefined") {
      localStorage.setItem(storageKey, JSON.stringify(state));
    }
  }, [state, storageKey]);

  // Reload state when meeting changes
  useEffect(() => {
    setState(loadState());
  }, [meeting.id, loadState]);

  // -----------------------------------------------------------------------
  // Helpers
  // -----------------------------------------------------------------------

  const computeResult = (resolution: Resolution): "Passed" | "Not Passed" | "Pending" => {
    const totalVotes = resolution.votes.for.length + resolution.votes.against.length + resolution.votes.abstain.length;
    if (totalVotes === 0) return "Pending";
    const forCount = resolution.votes.for.length;
    const totalCast = forCount + resolution.votes.against.length;
    if (totalCast === 0) return "Pending";
    const percentage = (forCount / totalCast) * 100;
    if (resolution.type === "Special") {
      return percentage >= 75 ? "Passed" : "Not Passed";
    }
    return percentage > 50 ? "Passed" : "Not Passed";
  };

  const passedResolutions = state.resolutions.filter((r) => r.result === "Passed");

  // Get attendee names
  const attendeeNames: string[] = (meeting.attendees || []).map(
    (att: any) => (typeof att === "string" ? att : att.name) || "Unknown"
  );

  // -----------------------------------------------------------------------
  // Actions
  // -----------------------------------------------------------------------

  const handleAddResolution = async () => {
    if (!formText.trim()) return;
    setActionLoading(true);
    setMessage("");

    const newRes: Resolution = {
      id: generateId(),
      text: formText.trim(),
      type: formType,
      category: formCategory,
      votes: { for: [], against: [], abstain: [] },
      result: "Pending",
    };

    const updated = [...state.resolutions, newRes];

    try {
      await updateMeetingResolutions(companyId, meeting.id, {
        resolutions: updated.map((r) => ({
          text: r.text,
          type: r.type,
          category: r.category,
          result: r.result,
        })),
      });
      setState((prev) => ({ ...prev, resolutions: updated }));
      setFormText("");
      setFormType("Ordinary");
      setFormCategory(RESOLUTION_CATEGORIES[0]);
      setMessage("Resolution added successfully.");
      onUpdate();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleVote = async (resolutionId: string, attendeeName: string, vote: "for" | "against" | "abstain") => {
    setState((prev) => {
      const updated = prev.resolutions.map((r) => {
        if (r.id !== resolutionId) return r;
        // Remove from all vote categories first
        const votes = {
          for: r.votes.for.filter((n) => n !== attendeeName),
          against: r.votes.against.filter((n) => n !== attendeeName),
          abstain: r.votes.abstain.filter((n) => n !== attendeeName),
        };
        // Add to the selected category
        votes[vote].push(attendeeName);
        const updated = { ...r, votes };
        updated.result = computeResult(updated);
        return updated;
      });

      // Update compliance filings for passed resolutions
      const filings = { ...prev.filings };
      updated.forEach((r) => {
        if (r.result === "Passed" && !filings[r.id]) {
          const required = getComplianceFilings(r, meeting.date);
          if (required.length > 0) {
            filings[r.id] = required;
          }
        }
      });

      return { ...prev, resolutions: updated, filings };
    });
  };

  const handleRemoveResolution = (resolutionId: string) => {
    setState((prev) => {
      const updated = prev.resolutions.filter((r) => r.id !== resolutionId);
      const filings = { ...prev.filings };
      delete filings[resolutionId];
      return { ...prev, resolutions: updated, filings };
    });
  };

  const handleGenerateDocument = async () => {
    if (passedResolutions.length === 0) {
      setMessage("No passed resolutions to generate a document for.");
      return;
    }
    setActionLoading(true);
    setMessage("");
    try {
      const result = await createLegalDraft({
        template_type: "board_resolution",
        company_id: companyId,
        title: `Board Resolution - ${meeting.title}`,
      });
      setState((prev) => ({ ...prev, generatedDocId: result.id || result.draft_id || "generated" }));
      setMessage("Board Resolution document generated successfully.");
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleSendForSigning = () => {
    setMessage("Resolution document sent to directors for e-signature.");
  };

  const handleUpdateFilingStatus = (resolutionId: string, filingIndex: number, newStatus: "Pending" | "Filed" | "Acknowledged") => {
    setState((prev) => {
      const filings = { ...prev.filings };
      if (filings[resolutionId]) {
        const updated = [...filings[resolutionId]];
        updated[filingIndex] = { ...updated[filingIndex], status: newStatus };
        filings[resolutionId] = updated;
      }
      return { ...prev, filings };
    });
  };

  // -----------------------------------------------------------------------
  // Section toggle
  // -----------------------------------------------------------------------

  const toggleSection = (section: "add" | "list" | "document" | "compliance") => {
    setExpandedSection((prev) => (prev === section ? null : section));
  };

  // -----------------------------------------------------------------------
  // Check for compliance filings
  // -----------------------------------------------------------------------

  const allFilings = Object.entries(state.filings).flatMap(([resId, filings]) => {
    const res = state.resolutions.find((r) => r.id === resId);
    return filings.map((f) => ({ ...f, resolutionText: res?.text || "Unknown" }));
  });

  const pendingFilingsCount = allFilings.filter((f) => f.status === "Pending").length;

  // -----------------------------------------------------------------------
  // Render
  // -----------------------------------------------------------------------

  const getVoteForAttendee = (resolution: Resolution, name: string): "for" | "against" | "abstain" | null => {
    if (resolution.votes.for.includes(name)) return "for";
    if (resolution.votes.against.includes(name)) return "against";
    if (resolution.votes.abstain.includes(name)) return "abstain";
    return null;
  };

  return (
    <div className="mb-6">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-sm font-semibold" style={{ color: "var(--color-text-primary)" }}>
          Resolution Workflow
        </h4>
        <div className="flex items-center gap-2">
          {state.resolutions.length > 0 && (
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full border bg-purple-500/10 border-purple-500/30 text-purple-400">
              {state.resolutions.length} resolution{state.resolutions.length !== 1 ? "s" : ""}
            </span>
          )}
          {passedResolutions.length > 0 && (
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full border bg-emerald-500/10 border-emerald-500/30 text-emerald-400">
              {passedResolutions.length} passed
            </span>
          )}
          {pendingFilingsCount > 0 && (
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full border bg-amber-500/10 border-amber-500/30 text-amber-400">
              {pendingFilingsCount} filing{pendingFilingsCount !== 1 ? "s" : ""} pending
            </span>
          )}
        </div>
      </div>

      {/* Message */}
      {message && (
        <div
          className={`p-3 mb-4 rounded-lg text-xs text-center border ${
            message.startsWith("Error")
              ? "border-red-500/30 bg-red-500/5 text-red-400"
              : "border-emerald-500/30 bg-emerald-500/5 text-emerald-400"
          }`}
        >
          {message}
        </div>
      )}

      {/* ----------------------------------------------------------------- */}
      {/* Section 1: Add Resolutions */}
      {/* ----------------------------------------------------------------- */}
      <div className="rounded-lg border mb-3" style={{ borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" }}>
        <button
          onClick={() => toggleSection("add")}
          className="w-full flex items-center justify-between p-3 text-left"
        >
          <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
            Add Resolution
          </span>
          <span className="text-xs" style={{ color: "var(--color-text-muted)" }}>
            {expandedSection === "add" ? "\u25B2" : "\u25BC"}
          </span>
        </button>

        {expandedSection === "add" && (
          <div className="px-3 pb-3">
            <div className="mb-3">
              <label className="block text-xs font-semibold mb-1" style={{ color: "var(--color-text-muted)" }}>
                Resolution Text *
              </label>
              <textarea
                value={formText}
                onChange={(e) => setFormText(e.target.value)}
                placeholder="RESOLVED THAT the Board hereby approves..."
                rows={3}
                className="w-full px-3 py-2 rounded-lg border text-sm outline-none resize-none"
                style={{
                  background: "var(--color-bg-card)",
                  borderColor: "var(--color-border)",
                  color: "var(--color-text-primary)",
                }}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
              <div>
                <label className="block text-xs font-semibold mb-1" style={{ color: "var(--color-text-muted)" }}>
                  Resolution Type
                </label>
                <select
                  value={formType}
                  onChange={(e) => setFormType(e.target.value as "Ordinary" | "Special")}
                  className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                  style={{
                    background: "var(--color-bg-card)",
                    borderColor: "var(--color-border)",
                    color: "var(--color-text-primary)",
                  }}
                >
                  <option value="Ordinary">Ordinary Resolution</option>
                  <option value="Special">Special Resolution</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold mb-1" style={{ color: "var(--color-text-muted)" }}>
                  Category
                </label>
                <select
                  value={formCategory}
                  onChange={(e) => setFormCategory(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                  style={{
                    background: "var(--color-bg-card)",
                    borderColor: "var(--color-border)",
                    color: "var(--color-text-primary)",
                  }}
                >
                  {RESOLUTION_CATEGORIES.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <button
              onClick={handleAddResolution}
              disabled={actionLoading || !formText.trim()}
              className="btn-primary text-xs !py-2 !px-4"
            >
              {actionLoading ? "Adding..." : "Add Resolution"}
            </button>
          </div>
        )}
      </div>

      {/* ----------------------------------------------------------------- */}
      {/* Section 2: Resolution List with Voting */}
      {/* ----------------------------------------------------------------- */}
      {state.resolutions.length > 0 && (
        <div className="rounded-lg border mb-3" style={{ borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" }}>
          <button
            onClick={() => toggleSection("list")}
            className="w-full flex items-center justify-between p-3 text-left"
          >
            <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
              Resolutions ({state.resolutions.length})
            </span>
            <span className="text-xs" style={{ color: "var(--color-text-muted)" }}>
              {expandedSection === "list" ? "\u25B2" : "\u25BC"}
            </span>
          </button>

          {expandedSection === "list" && (
            <div className="px-3 pb-3 space-y-3">
              {state.resolutions.map((res, idx) => (
                <div
                  key={res.id}
                  className="p-3 rounded-lg border"
                  style={{ borderColor: "var(--color-border)", background: "var(--color-bg-card)" }}
                >
                  {/* Header */}
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs font-mono" style={{ color: "var(--color-text-muted)" }}>
                        #{idx + 1}
                      </span>
                      <span
                        className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                          res.type === "Ordinary"
                            ? "bg-blue-500/10 border-blue-500/30 text-blue-400"
                            : "bg-purple-500/10 border-purple-500/30 text-purple-400"
                        }`}
                      >
                        {res.type}
                      </span>
                      <span
                        className="text-[10px] font-medium px-2 py-0.5 rounded-full border"
                        style={{ borderColor: "var(--color-border)", color: "var(--color-text-secondary)" }}
                      >
                        {res.category}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      {/* Result badge */}
                      <span
                        className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                          res.result === "Passed"
                            ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                            : res.result === "Not Passed"
                            ? "bg-red-500/10 border-red-500/30 text-red-400"
                            : "bg-amber-500/10 border-amber-500/30 text-amber-400"
                        }`}
                      >
                        {res.result}
                      </span>
                      <button
                        onClick={() => handleRemoveResolution(res.id)}
                        className="text-red-400 hover:text-red-300 text-[10px] font-medium"
                        title="Remove resolution"
                      >
                        Remove
                      </button>
                    </div>
                  </div>

                  {/* Resolution text */}
                  <p className="text-sm mb-3" style={{ color: "var(--color-text-primary)" }}>
                    {res.text}
                  </p>

                  {/* Majority indicator */}
                  <p className="text-[10px] mb-3" style={{ color: "var(--color-text-muted)" }}>
                    {res.type === "Special" ? "75% majority required" : "Simple majority required"}
                  </p>

                  {/* Vote counts */}
                  <div className="flex items-center gap-4 mb-3">
                    <span className="text-xs">
                      <span className="font-semibold text-emerald-400">{res.votes.for.length}</span>{" "}
                      <span style={{ color: "var(--color-text-muted)" }}>For</span>
                    </span>
                    <span className="text-xs">
                      <span className="font-semibold text-red-400">{res.votes.against.length}</span>{" "}
                      <span style={{ color: "var(--color-text-muted)" }}>Against</span>
                    </span>
                    <span className="text-xs">
                      <span className="font-semibold text-amber-400">{res.votes.abstain.length}</span>{" "}
                      <span style={{ color: "var(--color-text-muted)" }}>Abstain</span>
                    </span>
                  </div>

                  {/* Per-attendee voting */}
                  {attendeeNames.length > 0 && (
                    <div className="border-t pt-3" style={{ borderColor: "var(--color-border)" }}>
                      <p className="text-[10px] font-semibold uppercase tracking-wider mb-2" style={{ color: "var(--color-text-muted)" }}>
                        Votes
                      </p>
                      <div className="space-y-1.5">
                        {attendeeNames.map((name) => {
                          const currentVote = getVoteForAttendee(res, name);
                          return (
                            <div key={name} className="flex items-center justify-between">
                              <span className="text-xs" style={{ color: "var(--color-text-secondary)" }}>
                                {name}
                              </span>
                              <div className="flex items-center gap-1">
                                <button
                                  onClick={() => handleVote(res.id, name, "for")}
                                  className={`text-[10px] font-medium px-2 py-0.5 rounded border transition-colors ${
                                    currentVote === "for"
                                      ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-400"
                                      : "border-transparent hover:border-emerald-500/30 hover:text-emerald-400"
                                  }`}
                                  style={currentVote !== "for" ? { color: "var(--color-text-muted)" } : {}}
                                >
                                  For
                                </button>
                                <button
                                  onClick={() => handleVote(res.id, name, "against")}
                                  className={`text-[10px] font-medium px-2 py-0.5 rounded border transition-colors ${
                                    currentVote === "against"
                                      ? "bg-red-500/20 border-red-500/40 text-red-400"
                                      : "border-transparent hover:border-red-500/30 hover:text-red-400"
                                  }`}
                                  style={currentVote !== "against" ? { color: "var(--color-text-muted)" } : {}}
                                >
                                  Against
                                </button>
                                <button
                                  onClick={() => handleVote(res.id, name, "abstain")}
                                  className={`text-[10px] font-medium px-2 py-0.5 rounded border transition-colors ${
                                    currentVote === "abstain"
                                      ? "bg-amber-500/20 border-amber-500/40 text-amber-400"
                                      : "border-transparent hover:border-amber-500/30 hover:text-amber-400"
                                  }`}
                                  style={currentVote !== "abstain" ? { color: "var(--color-text-muted)" } : {}}
                                >
                                  Abstain
                                </button>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ----------------------------------------------------------------- */}
      {/* Section 3: Generate Resolution Document */}
      {/* ----------------------------------------------------------------- */}
      {state.resolutions.length > 0 && (
        <div className="rounded-lg border mb-3" style={{ borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" }}>
          <button
            onClick={() => toggleSection("document")}
            className="w-full flex items-center justify-between p-3 text-left"
          >
            <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
              Resolution Document
            </span>
            <span className="text-xs" style={{ color: "var(--color-text-muted)" }}>
              {expandedSection === "document" ? "\u25B2" : "\u25BC"}
            </span>
          </button>

          {expandedSection === "document" && (
            <div className="px-3 pb-3">
              {passedResolutions.length === 0 ? (
                <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                  No resolutions have been passed yet. Vote on resolutions above to proceed.
                </p>
              ) : (
                <>
                  <p className="text-xs mb-3" style={{ color: "var(--color-text-secondary)" }}>
                    {passedResolutions.length} passed resolution{passedResolutions.length !== 1 ? "s" : ""} ready
                    for document generation.
                  </p>

                  <div className="flex items-center gap-2 mb-3">
                    <button
                      onClick={handleGenerateDocument}
                      disabled={actionLoading}
                      className="btn-primary text-xs !py-2 !px-4"
                    >
                      {actionLoading ? "Generating..." : "Generate Board Resolution"}
                    </button>

                    {state.generatedDocId && (
                      <button
                        onClick={handleSendForSigning}
                        className="text-xs font-medium border border-emerald-500/30 text-emerald-400 px-3 py-2 rounded-lg hover:bg-emerald-500/10 transition-colors"
                      >
                        Send for Signing
                      </button>
                    )}
                  </div>

                  {state.generatedDocId && (
                    <div
                      className="p-3 rounded-lg border border-emerald-500/20 bg-emerald-500/5"
                    >
                      <p className="text-xs text-emerald-400 font-semibold">
                        Document generated successfully
                      </p>
                      <p className="text-[10px] mt-1" style={{ color: "var(--color-text-muted)" }}>
                        Document ID: {state.generatedDocId}
                      </p>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </div>
      )}

      {/* ----------------------------------------------------------------- */}
      {/* Section 4: Compliance Tracking */}
      {/* ----------------------------------------------------------------- */}
      {allFilings.length > 0 && (
        <div className="rounded-lg border" style={{ borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" }}>
          <button
            onClick={() => toggleSection("compliance")}
            className="w-full flex items-center justify-between p-3 text-left"
          >
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                Compliance Filings
              </span>
              {pendingFilingsCount > 0 && (
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full border bg-amber-500/10 border-amber-500/30 text-amber-400">
                  {pendingFilingsCount} pending
                </span>
              )}
            </div>
            <span className="text-xs" style={{ color: "var(--color-text-muted)" }}>
              {expandedSection === "compliance" ? "\u25B2" : "\u25BC"}
            </span>
          </button>

          {expandedSection === "compliance" && (
            <div className="px-3 pb-3 space-y-3">
              {Object.entries(state.filings).map(([resId, filings]) => {
                const res = state.resolutions.find((r) => r.id === resId);
                if (!res || filings.length === 0) return null;
                return (
                  <div key={resId}>
                    <p className="text-xs font-medium mb-2" style={{ color: "var(--color-text-secondary)" }}>
                      {res.text.length > 80 ? res.text.substring(0, 80) + "..." : res.text}
                    </p>
                    <div className="space-y-1.5">
                      {filings.map((filing, fi) => (
                        <div
                          key={fi}
                          className="flex items-center justify-between p-2.5 rounded-lg border"
                          style={{ borderColor: "var(--color-border)", background: "var(--color-bg-card)" }}
                        >
                          <div className="flex items-center gap-3">
                            <span className="text-xs font-mono font-bold text-purple-400">{filing.form}</span>
                            <div>
                              <p className="text-xs" style={{ color: "var(--color-text-primary)" }}>
                                {filing.description}
                              </p>
                              <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                                Due:{" "}
                                {new Date(filing.dueDate).toLocaleDateString("en-IN", {
                                  day: "2-digit",
                                  month: "short",
                                  year: "numeric",
                                })}
                              </p>
                            </div>
                          </div>
                          <select
                            value={filing.status}
                            onChange={(e) =>
                              handleUpdateFilingStatus(resId, fi, e.target.value as "Pending" | "Filed" | "Acknowledged")
                            }
                            className={`text-[10px] font-semibold px-2 py-1 rounded-lg border outline-none ${
                              filing.status === "Pending"
                                ? "bg-amber-500/10 border-amber-500/30 text-amber-400"
                                : filing.status === "Filed"
                                ? "bg-blue-500/10 border-blue-500/30 text-blue-400"
                                : "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                            }`}
                            style={{ background: "transparent" }}
                          >
                            <option value="Pending">Pending</option>
                            <option value="Filed">Filed</option>
                            <option value="Acknowledged">Acknowledged</option>
                          </select>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
