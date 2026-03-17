"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/lib/auth-context";
import Link from "next/link";
import {
  getCompanies,
  getMeetings,
  getMeeting,
  createMeeting,
  updateMeeting,
  generateMeetingNotice,
  updateMeetingAttendance,
  updateMeetingAgenda,
  generateMeetingMinutes,
  signMeetingMinutes,
  updateMeetingResolutions,
  getUpcomingMeetings,
  getPendingMinutes,
} from "@/lib/api";


// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface MeetingItem {
  id: number;
  meeting_type: string;
  title: string;
  date: string;
  time: string;
  venue: string | null;
  is_virtual: boolean;
  virtual_link: string | null;
  status: string;
  attendees: any[];
  agenda_items: any[];
  resolutions: any[];
  minutes_html: string | null;
  minutes_signed: boolean;
  minutes_signed_by: string | null;
  minutes_signed_date: string | null;
  created_at: string;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const MEETING_TYPE_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  BOARD_MEETING: { bg: "bg-purple-500/10 border-purple-500/30", text: "text-purple-400", label: "Board Meeting" },
  AGM: { bg: "bg-emerald-500/10 border-emerald-500/30", text: "text-emerald-400", label: "AGM" },
  EGM: { bg: "bg-amber-500/10 border-amber-500/30", text: "text-amber-400", label: "EGM" },
  COMMITTEE: { bg: "bg-blue-500/10 border-blue-500/30", text: "text-blue-400", label: "Committee" },
};

const STATUS_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  scheduled: { bg: "bg-blue-500/10 border-blue-500/30", text: "text-blue-400", label: "Scheduled" },
  notice_sent: { bg: "bg-purple-500/10 border-purple-500/30", text: "text-purple-400", label: "Notice Sent" },
  in_progress: { bg: "bg-amber-500/10 border-amber-500/30", text: "text-amber-400", label: "In Progress" },
  minutes_draft: { bg: "bg-cyan-500/10 border-cyan-500/30", text: "text-cyan-400", label: "Minutes Draft" },
  minutes_signed: { bg: "bg-emerald-500/10 border-emerald-500/30", text: "text-emerald-400", label: "Minutes Signed" },
  completed: { bg: "bg-emerald-500/10 border-emerald-500/30", text: "text-emerald-400", label: "Completed" },
};

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function MeetingsPage() {
  const { user, loading: authLoading } = useAuth();

  const [companies, setCompanies] = useState<any[]>([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  // Meetings data
  const [meetings, setMeetings] = useState<MeetingItem[]>([]);
  const [upcomingMeetings, setUpcomingMeetings] = useState<MeetingItem[]>([]);
  const [pendingMinutes, setPendingMinutes] = useState<MeetingItem[]>([]);

  // UI state
  const [activeTab, setActiveTab] = useState<"upcoming" | "past" | "pending">("upcoming");
  const [selectedMeeting, setSelectedMeeting] = useState<MeetingItem | null>(null);
  const [showScheduleForm, setShowScheduleForm] = useState(false);
  const [message, setMessage] = useState("");
  const [actionLoading, setActionLoading] = useState(false);

  // Schedule form
  const [formType, setFormType] = useState("BOARD_MEETING");
  const [formTitle, setFormTitle] = useState("");
  const [formDate, setFormDate] = useState("");
  const [formTime, setFormTime] = useState("10:00");
  const [formVenue, setFormVenue] = useState("");
  const [formIsVirtual, setFormIsVirtual] = useState(false);
  const [formVirtualLink, setFormVirtualLink] = useState("");
  const [formAttendees, setFormAttendees] = useState<{ name: string; din: string }[]>([{ name: "", din: "" }]);
  const [formAgenda, setFormAgenda] = useState<string[]>([""]);

  // Fetch companies
  useEffect(() => {
    if (authLoading || !user) return;
    getCompanies()
      .then((comps) => {
        setCompanies(comps);
        if (comps.length > 0) setSelectedCompanyId(comps[0].id);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [user, authLoading]);

  // Fetch meetings data
  const fetchMeetingsData = useCallback(async () => {
    if (!selectedCompanyId) return;
    try {
      const [allRes, upRes, pendRes] = await Promise.allSettled([
        getMeetings(selectedCompanyId),
        getUpcomingMeetings(selectedCompanyId),
        getPendingMinutes(selectedCompanyId),
      ]);
      if (allRes.status === "fulfilled") {
        setMeetings(Array.isArray(allRes.value) ? allRes.value : allRes.value?.meetings || []);
      }
      if (upRes.status === "fulfilled") {
        setUpcomingMeetings(Array.isArray(upRes.value) ? upRes.value : upRes.value?.meetings || []);
      }
      if (pendRes.status === "fulfilled") {
        setPendingMinutes(Array.isArray(pendRes.value) ? pendRes.value : pendRes.value?.meetings || []);
      }
    } catch (err) {
      console.error("Failed to fetch meetings:", err);
    }
  }, [selectedCompanyId]);

  useEffect(() => {
    if (!selectedCompanyId) return;
    setLoading(true);
    fetchMeetingsData().finally(() => setLoading(false));
  }, [selectedCompanyId, fetchMeetingsData]);

  // Stats
  const totalThisFY = meetings.length;
  const nextUpcoming = upcomingMeetings.length > 0 ? upcomingMeetings[0] : null;
  const pendingCount = pendingMinutes.length;
  const completedCount = meetings.filter((m) => m.status === "completed" || m.status === "minutes_signed").length;

  // Split meetings
  const now = new Date();
  const pastMeetings = meetings.filter((m) => new Date(m.date) < now || m.status === "completed" || m.status === "minutes_signed");
  const futureMeetings = meetings.filter((m) => new Date(m.date) >= now && m.status !== "completed" && m.status !== "minutes_signed");

  // Schedule meeting
  const handleSchedule = async () => {
    if (!selectedCompanyId || !formTitle || !formDate) return;
    setActionLoading(true);
    setMessage("");
    try {
      await createMeeting(selectedCompanyId, {
        meeting_type: formType,
        title: formTitle,
        date: formDate,
        time: formTime,
        venue: formIsVirtual ? null : formVenue,
        is_virtual: formIsVirtual,
        virtual_link: formIsVirtual ? formVirtualLink : null,
        attendees: formAttendees.filter((a) => a.name.trim()),
        agenda_items: formAgenda.filter((a) => a.trim()).map((text, i) => ({ order: i + 1, text })),
      });
      setMessage("Meeting scheduled successfully.");
      setShowScheduleForm(false);
      resetScheduleForm();
      await fetchMeetingsData();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const resetScheduleForm = () => {
    setFormType("BOARD_MEETING");
    setFormTitle("");
    setFormDate("");
    setFormTime("10:00");
    setFormVenue("");
    setFormIsVirtual(false);
    setFormVirtualLink("");
    setFormAttendees([{ name: "", din: "" }]);
    setFormAgenda([""]);
  };

  // Meeting actions
  const handleGenerateNotice = async (meetingId: number) => {
    if (!selectedCompanyId) return;
    setActionLoading(true);
    try {
      await generateMeetingNotice(selectedCompanyId, meetingId);
      setMessage("Notice generated successfully.");
      await fetchMeetingsData();
      if (selectedMeeting?.id === meetingId) {
        const detail = await getMeeting(selectedCompanyId, meetingId);
        setSelectedMeeting(detail);
      }
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleGenerateMinutes = async (meetingId: number) => {
    if (!selectedCompanyId) return;
    setActionLoading(true);
    try {
      await generateMeetingMinutes(selectedCompanyId, meetingId);
      setMessage("Minutes generated successfully.");
      await fetchMeetingsData();
      if (selectedMeeting?.id === meetingId) {
        const detail = await getMeeting(selectedCompanyId, meetingId);
        setSelectedMeeting(detail);
      }
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleSignMinutes = async (meetingId: number) => {
    if (!selectedCompanyId) return;
    setActionLoading(true);
    try {
      await signMeetingMinutes(selectedCompanyId, meetingId, {
        signed_by: user?.full_name || "Director",
      });
      setMessage("Minutes signed successfully.");
      await fetchMeetingsData();
      if (selectedMeeting?.id === meetingId) {
        const detail = await getMeeting(selectedCompanyId, meetingId);
        setSelectedMeeting(detail);
      }
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleViewDetail = async (meeting: MeetingItem) => {
    if (!selectedCompanyId) return;
    try {
      const detail = await getMeeting(selectedCompanyId, meeting.id);
      setSelectedMeeting(detail);
    } catch {
      setSelectedMeeting(meeting);
    }
  };

  // Loading / Auth
  if (authLoading || (loading && meetings.length === 0)) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="animate-pulse-glow w-16 h-16 rounded-full flex items-center justify-center" style={{ background: "rgba(139, 92, 246, 0.2)" }}>
          <img src="/logo-icon.png" alt="Anvils" className="w-7 h-7 object-contain" />
        </div>
      </div>
    );
  }

  const renderMeetingCard = (meeting: MeetingItem) => {
    const typeStyle = MEETING_TYPE_STYLES[meeting.meeting_type] || MEETING_TYPE_STYLES.BOARD_MEETING;
    const statusStyle = STATUS_STYLES[meeting.status] || STATUS_STYLES.scheduled;

    return (
      <div
        key={meeting.id}
        className="p-4 rounded-lg border hover:border-purple-500/30 transition-colors cursor-pointer"
        style={{ borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" }}
        onClick={() => handleViewDetail(meeting)}
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${typeStyle.bg} ${typeStyle.text}`}>
              {typeStyle.label}
            </span>
            <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${statusStyle.bg} ${statusStyle.text}`}>
              {statusStyle.label}
            </span>
          </div>
          {meeting.attendees && (
            <span className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>
              {meeting.attendees.length} attendees
            </span>
          )}
        </div>
        <h4 className="text-sm font-semibold mb-1" style={{ color: "var(--color-text-primary)" }}>{meeting.title}</h4>
        <div className="flex items-center gap-3 text-xs" style={{ color: "var(--color-text-muted)" }}>
          <span>
            {new Date(meeting.date).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })}
          </span>
          {meeting.time && <span>{meeting.time}</span>}
          <span>{meeting.is_virtual ? "Virtual" : meeting.venue || "TBD"}</span>
        </div>
        <div className="flex items-center gap-2 mt-3">
          {(meeting.status === "scheduled") && (
            <button
              onClick={(e) => { e.stopPropagation(); handleGenerateNotice(meeting.id); }}
              disabled={actionLoading}
              className="text-[10px] font-bold text-purple-400 hover:text-purple-300 border border-purple-500/30 px-2 py-1 rounded-lg hover:bg-purple-500/10 transition-colors"
            >
              Generate Notice
            </button>
          )}
          {(meeting.status === "notice_sent" || meeting.status === "in_progress" || meeting.status === "scheduled") && (
            <button
              onClick={(e) => { e.stopPropagation(); handleGenerateMinutes(meeting.id); }}
              disabled={actionLoading}
              className="text-[10px] font-bold text-cyan-400 hover:text-cyan-300 border border-cyan-500/30 px-2 py-1 rounded-lg hover:bg-cyan-500/10 transition-colors"
            >
              Record Minutes
            </button>
          )}
          {meeting.status === "minutes_draft" && !meeting.minutes_signed && (
            <button
              onClick={(e) => { e.stopPropagation(); handleSignMinutes(meeting.id); }}
              disabled={actionLoading}
              className="text-[10px] font-bold text-emerald-400 hover:text-emerald-300 border border-emerald-500/30 px-2 py-1 rounded-lg hover:bg-emerald-500/10 transition-colors"
            >
              Sign Minutes
            </button>
          )}
        </div>
      </div>
    );
  };

  return (
    <div>
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 gap-4 animate-fade-in-up">
          <div>
            <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>
              Meeting Management
            </h1>
            <p className="text-sm border-l-2 pl-3 border-purple-500" style={{ color: "var(--color-text-secondary)" }}>
              Board &amp; Shareholder meetings
            </p>
          </div>
          <div className="flex items-center gap-3">
            {companies.length > 1 && (
              <select
                className="glass-card text-sm px-3 py-2 rounded-lg border-none outline-none"
                style={{ background: "var(--color-bg-card)", color: "var(--color-text-primary)" }}
                value={selectedCompanyId || ""}
                onChange={(e) => setSelectedCompanyId(Number(e.target.value))}
              >
                {companies.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.approved_name || c.proposed_names?.[0] || `Company #${c.id}`}
                  </option>
                ))}
              </select>
            )}
            <button
              onClick={() => { setShowScheduleForm(true); setMessage(""); }}
              className="btn-primary text-sm !py-2 !px-4"
            >
              + Schedule Meeting
            </button>
          </div>
        </div>

        {/* Message */}
        {message && (
          <div className={`p-3 mb-6 rounded-lg text-sm text-center border animate-fade-in-up ${
            message.startsWith("Error")
              ? "border-red-500/30 bg-red-500/5 text-red-400"
              : "border-emerald-500/30 bg-emerald-500/5 text-emerald-400"
          }`}>
            {message}
          </div>
        )}

        {companies.length === 0 ? (
          <div className="p-12 text-center" style={{ background: "var(--color-bg-card)" }}>
            <h2 className="text-xl font-bold mb-2" style={{ color: "var(--color-text-primary)" }}>No company selected</h2>
            <p className="text-sm mb-6" style={{ color: "var(--color-text-secondary)" }}>
              Select a company from the sidebar to view board meetings and resolutions.
            </p>
            <div className="flex items-center justify-center gap-3">
              <Link href="/pricing" className="px-5 py-2.5 rounded-lg text-sm font-semibold text-white" style={{ background: "#8B5CF6" }}>
                Incorporate a New Company
              </Link>
              <Link href="/dashboard/connect" className="px-5 py-2.5 rounded-lg text-sm font-semibold border" style={{ borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}>
                Connect Existing Company
              </Link>
            </div>
          </div>
        ) : (
          <>
            {/* Stats Row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
              <div className="glass-card p-5" style={{ cursor: "default" }}>
                <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Total This FY</p>
                <p className="text-3xl font-bold mt-2">{totalThisFY}</p>
              </div>
              <div className="glass-card p-5" style={{ cursor: "default" }}>
                <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Next Upcoming</p>
                <p className="text-sm font-bold mt-2 text-purple-400">
                  {nextUpcoming
                    ? new Date(nextUpcoming.date).toLocaleDateString("en-IN", { day: "2-digit", month: "short" })
                    : "None"}
                </p>
              </div>
              <div className="glass-card p-5" style={{ cursor: "default" }}>
                <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Minutes Pending</p>
                <p className="text-3xl font-bold mt-2" style={{ color: "var(--color-warning)" }}>{pendingCount}</p>
              </div>
              <div className="glass-card p-5" style={{ cursor: "default" }}>
                <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Completed</p>
                <p className="text-3xl font-bold mt-2" style={{ color: "var(--color-success)" }}>{completedCount}</p>
              </div>
            </div>

            {/* Compliance warnings */}
            {pendingCount > 0 && (
              <div className="p-4 rounded-lg border border-amber-500/30 bg-amber-500/5 mb-6 animate-fade-in-up" style={{ animationDelay: "0.15s" }}>
                <p className="text-xs" style={{ color: "var(--color-warning)" }}>
                  <span className="font-semibold">Warning:</span> Minutes must be signed within 30 days of the meeting. You have {pendingCount} meeting(s) with unsigned minutes.
                </p>
              </div>
            )}

            {/* Schedule Meeting Form */}
            {showScheduleForm && (
              <div className="glass-card p-6 mb-8 animate-fade-in-up" style={{ cursor: "default" }}>
                <h3 className="text-lg font-bold mb-4">Schedule New Meeting</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>Meeting Type *</label>
                    <select
                      value={formType}
                      onChange={(e) => setFormType(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                      style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                    >
                      <option value="BOARD_MEETING">Board Meeting</option>
                      <option value="AGM">Annual General Meeting (AGM)</option>
                      <option value="EGM">Extraordinary General Meeting (EGM)</option>
                      <option value="COMMITTEE">Committee Meeting</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>Title *</label>
                    <input
                      type="text"
                      value={formTitle}
                      onChange={(e) => setFormTitle(e.target.value)}
                      placeholder="e.g., Q4 Board Meeting"
                      className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                      style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>Date *</label>
                    <input
                      type="date"
                      value={formDate}
                      onChange={(e) => setFormDate(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                      style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>Time</label>
                    <input
                      type="time"
                      value={formTime}
                      onChange={(e) => setFormTime(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                      style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                    />
                  </div>
                </div>

                {/* Virtual toggle */}
                <div className="mb-4">
                  <label className="flex items-center gap-2 text-sm" style={{ color: "var(--color-text-secondary)" }}>
                    <input
                      type="checkbox"
                      checked={formIsVirtual}
                      onChange={(e) => setFormIsVirtual(e.target.checked)}
                    />
                    Virtual meeting
                  </label>
                </div>

                {formIsVirtual ? (
                  <div className="mb-4">
                    <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>Virtual Link</label>
                    <input
                      type="url"
                      value={formVirtualLink}
                      onChange={(e) => setFormVirtualLink(e.target.value)}
                      placeholder="https://meet.google.com/..."
                      className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                      style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                    />
                  </div>
                ) : (
                  <div className="mb-4">
                    <label className="block text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>Venue</label>
                    <input
                      type="text"
                      value={formVenue}
                      onChange={(e) => setFormVenue(e.target.value)}
                      placeholder="Registered office address"
                      className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                      style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                    />
                  </div>
                )}

                {/* Attendees */}
                <div className="mb-4">
                  <label className="block text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: "var(--color-text-muted)" }}>Attendees</label>
                  {formAttendees.map((att, i) => (
                    <div key={i} className="flex gap-2 mb-2">
                      <input
                        type="text"
                        value={att.name}
                        onChange={(e) => {
                          const updated = [...formAttendees];
                          updated[i] = { ...updated[i], name: e.target.value };
                          setFormAttendees(updated);
                        }}
                        placeholder="Name"
                        className="flex-1 px-3 py-2 rounded-lg border text-sm outline-none"
                        style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                      />
                      <input
                        type="text"
                        value={att.din}
                        onChange={(e) => {
                          const updated = [...formAttendees];
                          updated[i] = { ...updated[i], din: e.target.value };
                          setFormAttendees(updated);
                        }}
                        placeholder="DIN (optional)"
                        className="w-40 px-3 py-2 rounded-lg border text-sm outline-none"
                        style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                      />
                      {formAttendees.length > 1 && (
                        <button
                          onClick={() => setFormAttendees(formAttendees.filter((_, j) => j !== i))}
                          className="text-red-400 hover:text-red-300 text-xs px-2"
                        >
                          Remove
                        </button>
                      )}
                    </div>
                  ))}
                  <button
                    onClick={() => setFormAttendees([...formAttendees, { name: "", din: "" }])}
                    className="text-xs text-purple-400 hover:text-purple-300 font-medium"
                  >
                    + Add Attendee
                  </button>
                </div>

                {/* Agenda */}
                <div className="mb-6">
                  <label className="block text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: "var(--color-text-muted)" }}>Agenda Items</label>
                  {formAgenda.map((item, i) => (
                    <div key={i} className="flex gap-2 mb-2">
                      <span className="text-xs font-mono pt-2.5 w-6 text-right" style={{ color: "var(--color-text-muted)" }}>{i + 1}.</span>
                      <input
                        type="text"
                        value={item}
                        onChange={(e) => {
                          const updated = [...formAgenda];
                          updated[i] = e.target.value;
                          setFormAgenda(updated);
                        }}
                        placeholder="Agenda item description"
                        className="flex-1 px-3 py-2 rounded-lg border text-sm outline-none"
                        style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
                      />
                      {formAgenda.length > 1 && (
                        <button
                          onClick={() => setFormAgenda(formAgenda.filter((_, j) => j !== i))}
                          className="text-red-400 hover:text-red-300 text-xs px-2"
                        >
                          Remove
                        </button>
                      )}
                    </div>
                  ))}
                  <button
                    onClick={() => setFormAgenda([...formAgenda, ""])}
                    className="text-xs text-purple-400 hover:text-purple-300 font-medium"
                  >
                    + Add Agenda Item
                  </button>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={handleSchedule}
                    disabled={actionLoading || !formTitle || !formDate}
                    className="btn-primary text-sm !py-2 !px-6"
                  >
                    {actionLoading ? "Scheduling..." : "Schedule Meeting"}
                  </button>
                  <button
                    onClick={() => { setShowScheduleForm(false); resetScheduleForm(); }}
                    className="text-sm px-4 py-2 rounded-lg border transition-colors"
                    style={{ color: "var(--color-text-secondary)", borderColor: "var(--color-border)" }}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {/* Tabs */}
            <div className="flex gap-1 mb-6 animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
              {(["upcoming", "past", "pending"] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => { setActiveTab(tab); setSelectedMeeting(null); }}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === tab
                      ? "bg-purple-500/20 text-purple-400 border border-purple-500/30"
                      : ""
                  }`}
                  style={activeTab !== tab ? { color: "var(--color-text-secondary)" } : {}}
                >
                  {tab === "upcoming" && `Upcoming (${futureMeetings.length})`}
                  {tab === "past" && `Past (${pastMeetings.length})`}
                  {tab === "pending" && `Minutes Pending (${pendingCount})`}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="animate-fade-in-up" style={{ animationDelay: "0.3s" }}>
              {activeTab === "upcoming" && (
                <div className="space-y-3">
                  {futureMeetings.length === 0 ? (
                    <div className="glass-card p-12 text-center" style={{ cursor: "default" }}>
                      <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                        No upcoming meetings. Click &quot;Schedule Meeting&quot; to create one.
                      </p>
                    </div>
                  ) : (
                    futureMeetings.map(renderMeetingCard)
                  )}
                </div>
              )}

              {activeTab === "past" && (
                <div className="space-y-3">
                  {pastMeetings.length === 0 ? (
                    <div className="glass-card p-12 text-center" style={{ cursor: "default" }}>
                      <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                        No past meetings recorded yet.
                      </p>
                    </div>
                  ) : (
                    pastMeetings.map(renderMeetingCard)
                  )}
                </div>
              )}

              {activeTab === "pending" && (
                <div className="space-y-3">
                  {pendingMinutes.length === 0 ? (
                    <div className="glass-card p-12 text-center" style={{ cursor: "default" }}>
                      <div className="text-4xl mb-3">&#10003;</div>
                      <p className="text-sm font-semibold" style={{ color: "var(--color-success)" }}>All minutes are signed. No pending items.</p>
                    </div>
                  ) : (
                    pendingMinutes.map(renderMeetingCard)
                  )}
                </div>
              )}
            </div>

            {/* Meeting Detail View */}
            {selectedMeeting && (
              <div className="glass-card p-6 mt-6 animate-fade-in-up" style={{ cursor: "default" }}>
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      {(() => {
                        const ts = MEETING_TYPE_STYLES[selectedMeeting.meeting_type] || MEETING_TYPE_STYLES.BOARD_MEETING;
                        return <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${ts.bg} ${ts.text}`}>{ts.label}</span>;
                      })()}
                      {(() => {
                        const ss = STATUS_STYLES[selectedMeeting.status] || STATUS_STYLES.scheduled;
                        return <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${ss.bg} ${ss.text}`}>{ss.label}</span>;
                      })()}
                    </div>
                    <h3 className="text-lg font-bold">{selectedMeeting.title}</h3>
                    <p className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
                      {new Date(selectedMeeting.date).toLocaleDateString("en-IN", { weekday: "long", day: "2-digit", month: "long", year: "numeric" })}
                      {selectedMeeting.time && ` at ${selectedMeeting.time}`}
                      {" | "}
                      {selectedMeeting.is_virtual ? `Virtual - ${selectedMeeting.virtual_link || "Link pending"}` : selectedMeeting.venue || "Venue TBD"}
                    </p>
                  </div>
                  <button
                    onClick={() => setSelectedMeeting(null)}
                    className="text-xs transition-colors" style={{ color: "var(--color-text-secondary)" }}
                  >
                    Close
                  </button>
                </div>

                {/* Agenda */}
                {selectedMeeting.agenda_items && selectedMeeting.agenda_items.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold mb-3">Agenda</h4>
                    <div className="space-y-2">
                      {selectedMeeting.agenda_items.map((item: any, i: number) => (
                        <div key={i} className="flex gap-3 p-3 rounded-lg border" style={{ borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" }}>
                          <span className="text-xs font-mono text-purple-400 shrink-0">{item.order || i + 1}.</span>
                          <p className="text-sm">{item.text || item.description || item}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Attendees */}
                {selectedMeeting.attendees && selectedMeeting.attendees.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold mb-3">Attendees</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedMeeting.attendees.map((att: any, i: number) => (
                        <span key={i} className="text-xs px-3 py-1.5 rounded-full border" style={{ borderColor: "var(--color-border)", background: "var(--color-border-light)" }}>
                          {att.name || att}
                          {att.din && <span className="ml-1" style={{ color: "var(--color-text-muted)" }}>(DIN: {att.din})</span>}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Resolutions */}
                {selectedMeeting.resolutions && selectedMeeting.resolutions.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold mb-3">Resolutions</h4>
                    <div className="space-y-2">
                      {selectedMeeting.resolutions.map((res: any, i: number) => (
                        <div key={i} className="p-3 rounded-lg border border-emerald-500/20 bg-emerald-500/5">
                          <p className="text-sm">{res.text || res.description || res}</p>
                          {res.result && <p className="text-[10px] text-emerald-400 mt-1 font-semibold uppercase">{res.result}</p>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Minutes Preview */}
                {selectedMeeting.minutes_html && (
                  <div className="mb-6">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm font-semibold">Minutes</h4>
                      {selectedMeeting.minutes_signed && (
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full border bg-emerald-500/10 border-emerald-500/30 text-emerald-400">
                          SIGNED {selectedMeeting.minutes_signed_date && `on ${new Date(selectedMeeting.minutes_signed_date).toLocaleDateString("en-IN")}`}
                        </span>
                      )}
                    </div>
                    <div
                      className="p-4 rounded-lg border prose prose-invert prose-sm max-w-none"
                      style={{ borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" }}
                      dangerouslySetInnerHTML={{ __html: selectedMeeting.minutes_html }}
                    />
                  </div>
                )}

                {/* Action buttons */}
                <div className="flex gap-3 pt-4 border-t" style={{ borderColor: "var(--color-border)" }}>
                  {selectedMeeting.status === "scheduled" && (
                    <button
                      onClick={() => handleGenerateNotice(selectedMeeting.id)}
                      disabled={actionLoading}
                      className="btn-primary text-sm !py-2 !px-4"
                    >
                      Generate Notice
                    </button>
                  )}
                  {(selectedMeeting.status === "notice_sent" || selectedMeeting.status === "in_progress" || selectedMeeting.status === "scheduled") && (
                    <button
                      onClick={() => handleGenerateMinutes(selectedMeeting.id)}
                      disabled={actionLoading}
                      className="text-sm font-medium border border-cyan-500/30 text-cyan-400 px-4 py-2 rounded-lg hover:bg-cyan-500/10 transition-colors"
                    >
                      Generate Minutes
                    </button>
                  )}
                  {selectedMeeting.status === "minutes_draft" && !selectedMeeting.minutes_signed && (
                    <button
                      onClick={() => handleSignMinutes(selectedMeeting.id)}
                      disabled={actionLoading}
                      className="text-sm font-medium border border-emerald-500/30 text-emerald-400 px-4 py-2 rounded-lg hover:bg-emerald-500/10 transition-colors"
                    >
                      Sign Minutes
                    </button>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
