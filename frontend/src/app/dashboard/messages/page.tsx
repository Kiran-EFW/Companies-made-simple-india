"use client";

import { useEffect, useState, useRef } from "react";
import { useCompany } from "@/lib/company-context";
import { getCompanyMessages, sendMessage, markMessagesRead } from "@/lib/api";

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
  return date.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

const SENDER_CONFIG: Record<string, { role: string; color: string; bg: string; avatarBg: string }> = {
  founder: { role: "You", color: "var(--color-accent-purple-light)", bg: "var(--color-purple-bg)", avatarBg: "var(--color-accent-purple-light)" },
  admin: { role: "Admin", color: "var(--color-info)", bg: "rgba(59,130,246,0.1)", avatarBg: "#3b82f6" },
  ca_lead: { role: "CA/CS Professional", color: "var(--color-accent-emerald-light)", bg: "rgba(16,185,129,0.1)", avatarBg: "#10b981" },
};

function SenderAvatar({ name, type }: { name: string; type: string }) {
  const cfg = SENDER_CONFIG[type] || SENDER_CONFIG.admin;
  const initial = (name || "?").charAt(0).toUpperCase();
  return (
    <div
      className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0"
      style={{ background: cfg.avatarBg }}
    >
      {initial}
    </div>
  );
}

function SenderRoleBadge({ type }: { type: string }) {
  const cfg = SENDER_CONFIG[type] || SENDER_CONFIG.admin;
  return (
    <span
      className="text-[9px] font-semibold px-1.5 py-0.5 rounded-full uppercase tracking-wider"
      style={{ color: cfg.color, background: cfg.bg }}
    >
      {cfg.role}
    </span>
  );
}

export default function MessagesPage() {
  const { selectedCompany, companies } = useCompany();
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [content, setContent] = useState("");
  const [unreadCount, setUnreadCount] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  const companyId = selectedCompany?.id;
  const companyName =
    selectedCompany?.approved_name ||
    selectedCompany?.proposed_names?.[0] ||
    "Your Company";

  // Fetch messages
  const fetchMessages = async () => {
    if (!companyId) return;
    try {
      const data = await getCompanyMessages(companyId);
      setMessages(data.messages || []);
      if (data.unread_count > 0) {
        setUnreadCount(data.unread_count);
        await markMessagesRead(companyId);
        setUnreadCount(0);
      }
    } catch {
      // Silently fail
    }
  };

  useEffect(() => {
    if (!companyId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    fetchMessages().finally(() => setLoading(false));

    // Poll every 10 seconds for new messages
    pollingRef.current = setInterval(fetchMessages, 10000);
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [companyId]);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!content.trim() || !companyId) return;
    setSending(true);
    try {
      const newMsg = await sendMessage(companyId, content.trim());
      setMessages((prev) => [...prev, newMsg]);
      setContent("");
    } catch {
      // Handle error silently
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Group messages by date
  const groupedMessages: { date: string; msgs: any[] }[] = [];
  let lastDate = "";
  for (const msg of messages) {
    const d = new Date(msg.created_at).toLocaleDateString("en-IN", {
      weekday: "long",
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
    if (d !== lastDate) {
      groupedMessages.push({ date: d, msgs: [] });
      lastDate = d;
    }
    groupedMessages[groupedMessages.length - 1].msgs.push(msg);
  }

  if (!selectedCompany) {
    return (
      <div className="p-8">
        <div className="max-w-2xl mx-auto text-center py-20">
          <svg
            className="w-12 h-12 mx-auto mb-4 opacity-30"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z"
            />
          </svg>
          <h2
            className="text-lg font-semibold mb-2"
            style={{ color: "var(--color-text-primary)" }}
          >
            No Company Selected
          </h2>
          <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
            Select a company from the header to view messages.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 h-[calc(100vh-3.5rem)] flex flex-col">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1
            className="text-2xl font-bold"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Messages
          </h1>
          <p className="text-sm mt-1" style={{ color: "var(--color-text-secondary)" }}>
            Conversation with your Anvils team and assigned CA/CS for{" "}
            <span className="font-medium" style={{ color: "var(--color-text-primary)" }}>
              {companyName}
            </span>
          </p>
        </div>
        {messages.length > 0 && (
          <div
            className="text-xs px-3 py-1.5 rounded-full"
            style={{ background: "var(--color-purple-bg)", color: "var(--color-accent-purple-light)" }}
          >
            {messages.length} message{messages.length !== 1 ? "s" : ""}
          </div>
        )}
      </div>

      {/* Chat Thread */}
      <div
        className="flex-1 rounded-xl border overflow-hidden flex flex-col"
        style={{ background: "var(--color-bg-card)", borderColor: "var(--color-border)" }}
      >
        {/* Messages Area */}
        <div
          className="flex-1 overflow-y-auto p-6 space-y-1"
          style={{ scrollbarWidth: "thin", scrollbarColor: "rgba(139,92,246,0.3) transparent" }}
        >
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div
                className="animate-spin rounded-full h-6 w-6 border-b-2"
                style={{ borderColor: "var(--color-accent-purple-light)" }}
              />
            </div>
          ) : messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div
                className="w-16 h-16 rounded-full flex items-center justify-center mb-4"
                style={{ background: "var(--color-purple-bg)" }}
              >
                <svg
                  className="w-8 h-8"
                  style={{ color: "var(--color-accent-purple-light)" }}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z"
                  />
                </svg>
              </div>
              <h3
                className="font-semibold mb-1"
                style={{ color: "var(--color-text-primary)" }}
              >
                No messages yet
              </h3>
              <p
                className="text-sm max-w-sm"
                style={{ color: "var(--color-text-muted)" }}
              >
                Send a message to your Anvils team or assigned CA/CS. They will
                respond here with updates on filings, compliance, and more.
              </p>
            </div>
          ) : (
            <>
              {groupedMessages.map((group) => (
                <div key={group.date}>
                  {/* Date separator */}
                  <div className="flex items-center gap-3 my-4">
                    <div className="flex-1 h-px" style={{ background: "var(--color-border)" }} />
                    <span
                      className="text-[10px] font-medium px-3 py-1 rounded-full"
                      style={{ background: "var(--color-bg-secondary)", color: "var(--color-text-muted)" }}
                    >
                      {group.date}
                    </span>
                    <div className="flex-1 h-px" style={{ background: "var(--color-border)" }} />
                  </div>

                  {group.msgs.map((msg: any) => {
                    const isMe = msg.sender_type === "founder";
                    const senderName = msg.sender_name || (isMe ? "You" : "Anvils Team");
                    return (
                      <div
                        key={msg.id}
                        className={`flex ${isMe ? "justify-end" : "justify-start"} mb-4`}
                      >
                        <div className={`flex gap-2.5 max-w-[75%] ${isMe ? "flex-row-reverse" : "flex-row"}`}>
                          <SenderAvatar name={senderName} type={msg.sender_type} />
                          <div>
                            {/* Sender name + role + time */}
                            <div className={`flex items-center gap-2 mb-1 ${isMe ? "justify-end" : "justify-start"}`}>
                              <span
                                className="text-xs font-semibold"
                                style={{ color: "var(--color-text-primary)" }}
                              >
                                {senderName}
                              </span>
                              <SenderRoleBadge type={msg.sender_type} />
                              <span
                                className="text-[10px]"
                                style={{ color: "var(--color-text-muted)" }}
                              >
                                {timeAgo(msg.created_at)}
                              </span>
                            </div>
                            {/* Message bubble */}
                            <div
                              className="rounded-2xl px-4 py-3"
                              style={
                                isMe
                                  ? {
                                      background: "var(--color-purple-bg)",
                                      border: "1px solid rgba(139,92,246,0.2)",
                                    }
                                  : {
                                      background: "var(--color-bg-secondary)",
                                      border: "1px solid var(--color-border)",
                                    }
                              }
                            >
                              <p
                                className="text-sm leading-relaxed whitespace-pre-wrap"
                                style={{ color: "var(--color-text-primary)" }}
                              >
                                {msg.content}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Compose Bar */}
        <div
          className="px-4 py-3 flex items-end gap-3"
          style={{
            borderTop: "1px solid var(--color-border)",
            background: "var(--color-bg-secondary)",
          }}
        >
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            className="flex-1 rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-purple-500/30"
            style={{
              background: "var(--color-bg-card)",
              border: "1px solid var(--color-border)",
              color: "var(--color-text-primary)",
              minHeight: "44px",
              maxHeight: "120px",
            }}
            rows={1}
          />
          <button
            onClick={handleSend}
            disabled={!content.trim() || sending}
            className="px-5 py-3 rounded-xl text-sm font-medium transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
            style={{ background: "var(--color-accent-purple)", color: "#fff" }}
          >
            {sending ? (
              <div
                className="animate-spin rounded-full h-4 w-4 border-b-2"
                style={{ borderColor: "#fff" }}
              />
            ) : (
              <svg
                className="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5"
                />
              </svg>
            )}
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
