"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { getNotifications, markNotificationRead, markAllNotificationsRead, deleteNotification } from "@/lib/api";
import Link from "next/link";

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
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString();
}

const FILTER_TABS = [
  { key: "all", label: "All" },
  { key: "unread", label: "Unread" },
  { key: "status_update", label: "Status Updates" },
  { key: "payment", label: "Payments" },
  { key: "compliance", label: "Compliance" },
];

function NotificationTypeIcon({ type }: { type: string }) {
  const styleMap: Record<string, { color: string; background: string }> = {
    status_update: { color: "var(--color-info)", background: "var(--color-info-light)" },
    payment: { color: "var(--color-success)", background: "var(--color-success-light)" },
    document: { color: "var(--color-accent-purple-light)", background: "var(--color-purple-bg)" },
    compliance: { color: "var(--color-warning)", background: "var(--color-warning-light)" },
    message: { color: "var(--color-accent-cyan)", background: "rgba(34,211,238,0.1)" },
  };

  const defaultStyle = { color: "var(--color-text-secondary)", background: "var(--color-hover-overlay)" };
  const s = styleMap[type] || defaultStyle;

  const icons: Record<string, React.ReactNode> = {
    status_update: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
      </svg>
    ),
    payment: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5z" />
      </svg>
    ),
    document: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
      </svg>
    ),
    compliance: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
      </svg>
    ),
    message: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
      </svg>
    ),
  };

  return (
    <div className="w-10 h-10 rounded-full flex items-center justify-center shrink-0" style={{ color: s.color, background: s.background }}>
      {icons[type] || (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
        </svg>
      )}
    </div>
  );
}

export default function NotificationsPage() {
  const { user, loading: authLoading } = useAuth();
  const [notifications, setNotifications] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState("all");
  const [page, setPage] = useState(0);
  const limit = 20;

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const data = await getNotifications(page * limit, limit);
      setNotifications(data.notifications || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error("Failed to fetch notifications:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (authLoading) return;
    if (!user) return;
    fetchNotifications();
  }, [user, authLoading, page]);

  const filteredNotifications = notifications.filter((n) => {
    if (activeFilter === "all") return true;
    if (activeFilter === "unread") return !n.is_read;
    return (n.notification_type || n.type) === activeFilter;
  });

  const handleMarkRead = async (id: number) => {
    try {
      await markNotificationRead(id);
      setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
    } catch (err) {
      console.error("Failed to mark as read:", err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllNotificationsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch (err) {
      console.error("Failed to mark all as read:", err);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteNotification(id);
      setNotifications((prev) => prev.filter((n) => n.id !== id));
      setTotal((prev) => prev - 1);
    } catch (err) {
      console.error("Failed to delete notification:", err);
    }
  };

  const handleNotificationClick = async (notif: any) => {
    if (!notif.is_read) {
      await handleMarkRead(notif.id);
    }
    if (notif.action_url) {
      window.location.href = notif.action_url;
    }
  };

  const totalPages = Math.ceil(total / limit);

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-pulse" style={{ color: "var(--color-text-muted)" }}>Loading notifications...</div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>Notifications</h1>
          <p className="text-sm border-l-2 pl-3 border-purple-500" style={{ color: "var(--color-text-secondary)" }}>
            Stay updated on your company incorporation progress.
          </p>
        </div>
        {notifications.some((n) => !n.is_read) && (
          <button onClick={handleMarkAllRead} className="btn-secondary text-sm !py-2 !px-4">
            Mark all as read
          </button>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto">
        {FILTER_TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveFilter(tab.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
              activeFilter === tab.key
                ? "bg-purple-500/20 border border-purple-500/30"
                : "border border-transparent"
            }`}
            style={
              activeFilter === tab.key
                ? { color: "var(--color-accent-purple-light)" }
                : { color: "var(--color-text-secondary)" }
            }
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Notification List */}
      {filteredNotifications.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <svg className="w-12 h-12 mx-auto mb-4" style={{ color: "var(--color-text-muted)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
          </svg>
          <h2 className="text-xl font-bold mb-2" style={{ color: "var(--color-text-primary)" }}>No notifications</h2>
          <p style={{ color: "var(--color-text-muted)" }}>
            {activeFilter === "unread"
              ? "You're all caught up! No unread notifications."
              : "Nothing to show here yet. Notifications will appear as your incorporation progresses."}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredNotifications.map((notif, idx) => (
            <div
              key={notif.id}
              className={`glass-card p-4 flex items-start gap-4 cursor-pointer group ${
                !notif.is_read ? "border-l-2 border-l-purple-500" : ""
              }`}
              onClick={() => handleNotificationClick(notif)}
            >
              <NotificationTypeIcon type={notif.notification_type || notif.type} />

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3
                    className="text-sm font-semibold"
                    style={{ color: "var(--color-text-primary)" }}
                  >
                    {notif.title}
                  </h3>
                  {!notif.is_read && (
                    <span className="w-2 h-2 bg-purple-500 rounded-full shrink-0" />
                  )}
                </div>
                <p className="text-xs leading-relaxed" style={{ color: "var(--color-text-secondary)" }}>{notif.message}</p>
                <p className="text-[10px] mt-1.5" style={{ color: "var(--color-text-muted)" }}>{timeAgo(notif.created_at)}</p>
              </div>

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(notif.id);
                }}
                className="p-1.5 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-red-500/10 transition-all"
                style={{ color: "var(--color-text-muted)" }}
                title="Delete notification"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-4 mt-8">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="px-4 py-2 rounded-lg text-sm font-medium border transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            style={{ borderColor: "var(--color-border)" }}
          >
            Previous
          </button>
          <span className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
            Page {page + 1} of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
            className="px-4 py-2 rounded-lg text-sm font-medium border transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            style={{ borderColor: "var(--color-border)" }}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
