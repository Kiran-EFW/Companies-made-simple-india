"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useCompany } from "@/lib/company-context";
import { sendCopilotMessage, getCopilotSuggestions } from "@/lib/api";
import { formatContent } from "@/lib/format-content";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface CopilotMessage {
  role: "user" | "assistant";
  content: string;
}

interface Suggestion {
  id: string;
  title: string;
  description: string;
  action_url: string;
  priority: "high" | "medium" | "low";
  category: string;
}

// ---------------------------------------------------------------------------
// Category icons (inline SVGs matching project convention)
// ---------------------------------------------------------------------------

function CategoryIcon({ category }: { category: string }) {
  const color = "var(--color-accent-purple, #7c3aed)";
  const size = 16;
  const common = { width: size, height: size, viewBox: "0 0 24 24", fill: "none", stroke: color, strokeWidth: 2, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };

  switch (category) {
    case "compliance":
      return (
        <svg {...common}>
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        </svg>
      );
    case "fundraising":
      return (
        <svg {...common}>
          <line x1="12" y1="1" x2="12" y2="23" />
          <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
        </svg>
      );
    case "esop":
      return (
        <svg {...common}>
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
          <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
      );
    case "cap_table":
      return (
        <svg {...common}>
          <rect x="3" y="12" width="4" height="9" />
          <rect x="10" y="7" width="4" height="14" />
          <rect x="17" y="3" width="4" height="18" />
        </svg>
      );
    default:
      return (
        <svg {...common}>
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="16" x2="12" y2="12" />
          <line x1="12" y1="8" x2="12.01" y2="8" />
        </svg>
      );
  }
}

// ---------------------------------------------------------------------------
// CopilotWidget — renders trigger button + slide-out panel
// ---------------------------------------------------------------------------

export default function CopilotWidget() {
  const pathname = usePathname();
  const router = useRouter();
  const { selectedCompany } = useCompany();

  const [isOpen, setIsOpen] = useState(false);
  const [isFullScreen, setIsFullScreen] = useState(false);
  const [activeTab, setActiveTab] = useState<"suggestions" | "chat">("suggestions");
  const [messages, setMessages] = useState<CopilotMessage[]>(() => {
    if (typeof window === "undefined") return [];
    try {
      const saved = sessionStorage.getItem("copilot_messages");
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [suggestionCount, setSuggestionCount] = useState(0);
  const [suggestionsLoading, setSuggestionsLoading] = useState(false);
  const [suggestionsError, setSuggestionsError] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);
  const suggestionCacheRef = useRef<{ key: string; data: { suggestions: Suggestion[]; suggestion_count: number }; ts: number } | null>(null);

  // Fetch suggestions when company or page changes (with 30s cache)
  const fetchSuggestions = useCallback(async () => {
    if (!selectedCompany?.id) return;

    const cacheKey = `${selectedCompany.id}:${pathname}`;
    const cached = suggestionCacheRef.current;
    if (cached && cached.key === cacheKey && Date.now() - cached.ts < 30_000) {
      setSuggestions(cached.data.suggestions);
      setSuggestionCount(cached.data.suggestion_count);
      setSuggestionsError(false);
      return;
    }

    setSuggestionsLoading(true);
    setSuggestionsError(false);
    try {
      const data = await getCopilotSuggestions(selectedCompany.id, pathname);
      const result = {
        suggestions: data.suggestions || [],
        suggestion_count: data.suggestion_count || 0,
      };
      suggestionCacheRef.current = { key: cacheKey, data: result, ts: Date.now() };
      setSuggestions(result.suggestions);
      setSuggestionCount(result.suggestion_count);
    } catch {
      setSuggestions([]);
      setSuggestionCount(0);
      setSuggestionsError(true);
    } finally {
      setSuggestionsLoading(false);
    }
  }, [selectedCompany?.id, pathname]);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(fetchSuggestions, 300);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [fetchSuggestions]);

  // Auto-scroll chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Persist chat messages to sessionStorage
  useEffect(() => {
    try {
      if (messages.length > 0) {
        sessionStorage.setItem("copilot_messages", JSON.stringify(messages.slice(-40)));
      } else {
        sessionStorage.removeItem("copilot_messages");
      }
    } catch { /* quota exceeded — ignore */ }
  }, [messages]);

  // Escape key to close panel / exit full-screen
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        if (isFullScreen) {
          setIsFullScreen(false);
        } else if (isOpen) {
          setIsOpen(false);
        }
      }
    };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isOpen, isFullScreen]);

  // Focus input when panel opens on chat tab
  useEffect(() => {
    if (isOpen && activeTab === "chat") {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen, activeTab]);

  const handleSend = async (messageText?: string) => {
    const text = messageText || inputValue.trim();
    if (!text || loading || !selectedCompany?.id) return;

    const userMessage: CopilotMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setLoading(true);

    // Auto-switch to chat tab
    setActiveTab("chat");

    try {
      const history = [...messages, userMessage]
        .slice(-20)
        .map((m) => ({ role: m.role, content: m.content }));

      const data = await sendCopilotMessage({
        message: text,
        company_id: selectedCompany.id,
        current_page: pathname,
        conversation_history: history,
      });

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestionClick = (suggestion: Suggestion) => {
    router.push(suggestion.action_url);
    setIsOpen(false);
    setIsFullScreen(false);
  };

  const fullScreenContentCls = isFullScreen ? "px-6 sm:px-12 mx-auto w-full max-w-3xl" : "";

  // Don't render if no company selected
  if (!selectedCompany) return null;

  return (
    <>
      {/* ── Trigger Button (inline in header) ── */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-lg transition-colors"
        style={{ color: isOpen ? "var(--color-accent-purple, #7c3aed)" : "var(--color-text-secondary)" }}
        aria-label="Open Copilot"
      >
        {/* Sparkle icon */}
        <svg
          className="w-5 h-5"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={1.5}
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M12 2l2.4 7.2L22 12l-7.6 2.8L12 22l-2.4-7.2L2 12l7.6-2.8L12 2z" />
        </svg>

        {/* Badge */}
        {suggestionCount > 0 && !isOpen && (
          <span
            className="absolute -top-0.5 -right-0.5 min-w-[16px] h-4 flex items-center justify-center rounded-full text-[10px] font-bold text-white px-1"
            style={{ background: "var(--color-accent-purple, #7c3aed)" }}
          >
            {suggestionCount > 9 ? "9+" : suggestionCount}
          </span>
        )}
      </button>

      {/* ── Backdrop ── */}
      {isOpen && (
        <div
          className={`fixed inset-0 ${isFullScreen ? "z-40" : "z-30 sm:hidden"}`}
          style={isFullScreen ? { background: "rgba(0, 0, 0, 0.5)", backdropFilter: "blur(2px)" } : undefined}
          onClick={() => { if (isFullScreen) { setIsFullScreen(false); } else { setIsOpen(false); } }}
        />
      )}

      {/* ── Panel (side panel or full-screen) ── */}
      {isOpen && (
        <div
          className={
            isFullScreen
              ? "fixed inset-4 sm:inset-8 z-50 flex flex-col animate-fade-in-up rounded-2xl overflow-hidden"
              : "fixed top-14 right-0 bottom-0 w-full sm:w-96 z-40 flex flex-col animate-fade-in-up"
          }
          style={{
            background: "var(--color-bg-card, #ffffff)",
            borderLeft: isFullScreen ? undefined : "1px solid var(--color-border, #e5e7eb)",
            border: isFullScreen ? "1px solid var(--color-border, #e5e7eb)" : undefined,
            boxShadow: isFullScreen
              ? "0 16px 64px rgba(0, 0, 0, 0.2)"
              : "-4px 0 24px rgba(0, 0, 0, 0.08)",
          }}
        >
          {/* ── Header ── */}
          <div
            className="flex items-center justify-between px-4 py-3 shrink-0"
            style={{
              borderBottom: "1px solid var(--color-border, #e5e7eb)",
              background: "var(--color-accent-purple, #7c3aed)",
            }}
          >
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-white/20 flex items-center justify-center">
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="white"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M12 2l2.4 7.2L22 12l-7.6 2.8L12 22l-2.4-7.2L2 12l7.6-2.8L12 2z" />
                </svg>
              </div>
              <div>
                <span className="text-sm font-semibold text-white">Anvils Copilot</span>
                <div className="flex items-center gap-1.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-300" />
                  <span className="text-[10px] text-white/70">AI-powered</span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-1">
              {/* Expand / Collapse */}
              <button
                onClick={() => setIsFullScreen(!isFullScreen)}
                className="w-7 h-7 rounded-lg flex items-center justify-center transition-colors hover:bg-white/20 text-white/80 hover:text-white"
                aria-label={isFullScreen ? "Exit full screen" : "Full screen"}
              >
                {isFullScreen ? (
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="4 14 10 14 10 20" />
                    <polyline points="20 10 14 10 14 4" />
                    <line x1="14" y1="10" x2="21" y2="3" />
                    <line x1="3" y1="21" x2="10" y2="14" />
                  </svg>
                ) : (
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="15 3 21 3 21 9" />
                    <polyline points="9 21 3 21 3 15" />
                    <line x1="21" y1="3" x2="14" y2="10" />
                    <line x1="3" y1="21" x2="10" y2="14" />
                  </svg>
                )}
              </button>
              {/* Close */}
              <button
                onClick={() => { setIsOpen(false); setIsFullScreen(false); }}
                className="w-7 h-7 rounded-lg flex items-center justify-center transition-colors hover:bg-white/20 text-white/80 hover:text-white"
                aria-label="Close copilot"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
          </div>

          {/* ── Tab Bar ── */}
          <div
            className="flex shrink-0"
            style={{ borderBottom: "1px solid var(--color-border, #e5e7eb)" }}
          >
            {(["suggestions", "chat"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className="flex-1 py-2.5 text-xs font-medium transition-colors relative"
                style={{
                  color:
                    activeTab === tab
                      ? "var(--color-accent-purple, #7c3aed)"
                      : "var(--color-text-muted, #9ca3af)",
                }}
              >
                {tab === "suggestions" ? (
                  <span className="flex items-center justify-center gap-1.5">
                    Suggestions
                    {suggestionCount > 0 && (
                      <span
                        className="min-w-[16px] h-4 flex items-center justify-center rounded-full text-[10px] font-bold text-white px-1"
                        style={{ background: "var(--color-accent-purple, #7c3aed)" }}
                      >
                        {suggestionCount}
                      </span>
                    )}
                  </span>
                ) : (
                  "Chat"
                )}
                {activeTab === tab && (
                  <div
                    className="absolute bottom-0 left-2 right-2 h-0.5 rounded-full"
                    style={{ background: "var(--color-accent-purple, #7c3aed)" }}
                  />
                )}
              </button>
            ))}
          </div>

          {/* ── Content Area ── */}
          <div
            className={`flex-1 overflow-y-auto py-4 space-y-3 ${fullScreenContentCls || "px-4"}`}
            style={{
              scrollbarWidth: "thin",
              scrollbarColor: "rgba(124, 58, 237, 0.2) transparent",
            }}
          >
            {/* Suggestions Tab */}
            {activeTab === "suggestions" && (
              <>
                {suggestionsLoading && (
                  <div className="flex items-center justify-center py-8">
                    <div
                      className="w-6 h-6 rounded-full border-2 animate-spin"
                      style={{
                        borderColor: "var(--color-border, #e5e7eb)",
                        borderTopColor: "var(--color-accent-purple, #7c3aed)",
                      }}
                    />
                  </div>
                )}

                {!suggestionsLoading && suggestionsError && (
                  <div className="text-center py-8 space-y-2">
                    <div
                      className="w-10 h-10 rounded-full mx-auto flex items-center justify-center"
                      style={{ background: "rgba(239, 68, 68, 0.08)" }}
                    >
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="12" cy="12" r="10" />
                        <line x1="12" y1="8" x2="12" y2="12" />
                        <line x1="12" y1="16" x2="12.01" y2="16" />
                      </svg>
                    </div>
                    <p className="text-sm font-medium" style={{ color: "var(--color-text-primary)" }}>
                      Failed to load suggestions
                    </p>
                    <button
                      onClick={fetchSuggestions}
                      className="text-xs px-3 py-1.5 rounded-lg transition-colors"
                      style={{
                        color: "var(--color-accent-purple, #7c3aed)",
                        background: "rgba(124, 58, 237, 0.08)",
                      }}
                    >
                      Retry
                    </button>
                  </div>
                )}

                {!suggestionsLoading && !suggestionsError && suggestions.length === 0 && (
                  <div className="text-center py-8 space-y-2">
                    <div
                      className="w-10 h-10 rounded-full mx-auto flex items-center justify-center"
                      style={{ background: "rgba(124, 58, 237, 0.08)" }}
                    >
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent-purple, #7c3aed)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                        <polyline points="22 4 12 14.01 9 11.01" />
                      </svg>
                    </div>
                    <p className="text-sm font-medium" style={{ color: "var(--color-text-primary)" }}>
                      All caught up
                    </p>
                    <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                      No suggestions right now. Ask me anything in the Chat tab.
                    </p>
                  </div>
                )}

                {!suggestionsLoading && !suggestionsError &&
                  suggestions.map((s) => (
                    <button
                      key={s.id}
                      onClick={() => handleSuggestionClick(s)}
                      className="w-full text-left p-3 rounded-xl transition-all duration-200 hover:shadow-sm"
                      style={{
                        background: "var(--color-bg-secondary, #f9fafb)",
                        border: "1px solid var(--color-border, #e5e7eb)",
                      }}
                    >
                      <div className="flex items-start gap-2.5">
                        <div className="mt-0.5 shrink-0">
                          <CategoryIcon category={s.category} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <p
                              className="text-sm font-medium truncate"
                              style={{ color: "var(--color-text-primary)" }}
                            >
                              {s.title}
                            </p>
                            {s.priority === "high" && (
                              <span
                                className="text-[10px] px-1.5 py-0.5 rounded-full shrink-0 font-medium"
                                style={{
                                  background: "rgba(239, 68, 68, 0.1)",
                                  color: "#ef4444",
                                }}
                              >
                                Urgent
                              </span>
                            )}
                          </div>
                          <p
                            className="text-xs mt-0.5 line-clamp-2"
                            style={{ color: "var(--color-text-muted)" }}
                          >
                            {s.description}
                          </p>
                        </div>
                        <svg
                          className="w-4 h-4 mt-0.5 shrink-0"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="var(--color-text-muted, #9ca3af)"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <polyline points="9 18 15 12 9 6" />
                        </svg>
                      </div>
                    </button>
                  ))}
              </>
            )}

            {/* Chat Tab */}
            {activeTab === "chat" && (
              <>
                {/* Clear chat button */}
                {messages.length > 0 && (
                  <div className="flex justify-end -mt-1 mb-1">
                    <button
                      onClick={() => setMessages([])}
                      className="text-[11px] px-2 py-1 rounded-md transition-colors"
                      style={{
                        color: "var(--color-text-muted, #9ca3af)",
                      }}
                    >
                      Clear chat
                    </button>
                  </div>
                )}

                {/* Welcome message */}
                {messages.length === 0 && !loading && (
                  <div className="space-y-4">
                    <div
                      className="p-3 rounded-xl text-sm leading-relaxed"
                      style={{
                        background: "var(--color-bg-secondary, #f9fafb)",
                        border: "1px solid var(--color-border, #e5e7eb)",
                        color: "var(--color-text-secondary, #6b7280)",
                      }}
                    >
                      I have full context about your company — compliance
                      deadlines, cap table, fundraising rounds, ESOP plans, and
                      more. Ask me anything.
                    </div>

                    <div className="space-y-2">
                      <p
                        className="text-[11px] font-medium uppercase tracking-wider"
                        style={{ color: "var(--color-text-muted, #9ca3af)" }}
                      >
                        Try asking
                      </p>
                      <div className="flex flex-col gap-2">
                        {[
                          "What should I do next?",
                          "Summarize my compliance status",
                          "Explain my cap table",
                        ].map((q, idx) => (
                          <button
                            key={idx}
                            onClick={() => handleSend(q)}
                            className="text-left text-xs px-3 py-2.5 rounded-lg transition-all duration-200 hover:shadow-sm"
                            style={{
                              background: "var(--color-bg-secondary, #f9fafb)",
                              border: "1px solid var(--color-border, #e5e7eb)",
                              color: "var(--color-text-primary, #374151)",
                            }}
                          >
                            <span style={{ color: "var(--color-accent-purple, #7c3aed)" }}>
                              {"\u2192"}{" "}
                            </span>
                            {q}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* Chat messages */}
                {messages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className="max-w-[85%] px-3 py-2 rounded-xl text-sm leading-relaxed"
                      style={
                        msg.role === "user"
                          ? {
                              background: "var(--color-accent-purple, #7c3aed)",
                              color: "white",
                              borderBottomRightRadius: "4px",
                            }
                          : {
                              background: "var(--color-bg-secondary, #f9fafb)",
                              border: "1px solid var(--color-border, #e5e7eb)",
                              color: "var(--color-text-primary, #374151)",
                              borderBottomLeftRadius: "4px",
                            }
                      }
                    >
                      {msg.role === "assistant"
                        ? formatContent(msg.content)
                        : msg.content}
                    </div>
                  </div>
                ))}

                {/* Typing indicator */}
                {loading && (
                  <div className="flex justify-start">
                    <div
                      className="px-4 py-3 rounded-xl flex items-center gap-1.5"
                      style={{
                        background: "var(--color-bg-secondary, #f9fafb)",
                        border: "1px solid var(--color-border, #e5e7eb)",
                        borderBottomLeftRadius: "4px",
                      }}
                    >
                      <span
                        className="w-2 h-2 rounded-full animate-bounce"
                        style={{
                          background: "var(--color-accent-purple, #7c3aed)",
                          animationDelay: "0ms",
                        }}
                      />
                      <span
                        className="w-2 h-2 rounded-full animate-bounce"
                        style={{
                          background: "var(--color-accent-purple, #7c3aed)",
                          animationDelay: "150ms",
                        }}
                      />
                      <span
                        className="w-2 h-2 rounded-full animate-bounce"
                        style={{
                          background: "var(--color-accent-purple, #7c3aed)",
                          animationDelay: "300ms",
                        }}
                      />
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* ── Input Area (always visible) ── */}
          <div
            className={`px-3 py-3 shrink-0 ${fullScreenContentCls}`}
            style={{ borderTop: "1px solid var(--color-border, #e5e7eb)" }}
          >
            <div
              className="flex items-end gap-2 rounded-xl px-3 py-2"
              style={{
                background: "var(--color-bg-secondary, #f9fafb)",
                border: "1px solid var(--color-border, #e5e7eb)",
              }}
            >
              {isFullScreen ? (
                <textarea
                  ref={inputRef as React.RefObject<HTMLTextAreaElement>}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                  placeholder="Ask about your company... (Shift+Enter for new line)"
                  disabled={loading}
                  rows={2}
                  className="flex-1 bg-transparent text-sm outline-none placeholder:text-gray-400 resize-none"
                  style={{ color: "var(--color-text-primary, #111827)" }}
                />
              ) : (
                <input
                  ref={inputRef as React.RefObject<HTMLInputElement>}
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask about your company..."
                  disabled={loading}
                  className="flex-1 bg-transparent text-sm outline-none placeholder:text-gray-400"
                  style={{ color: "var(--color-text-primary, #111827)" }}
                />
              )}
              <button
                onClick={() => handleSend()}
                disabled={loading || !inputValue.trim()}
                className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 transition-all duration-200 disabled:opacity-30"
                style={{
                  background:
                    inputValue.trim() && !loading
                      ? "var(--color-accent-purple, #7c3aed)"
                      : "transparent",
                }}
                aria-label="Send message"
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke={
                    inputValue.trim() && !loading ? "white" : "currentColor"
                  }
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  style={{
                    color:
                      inputValue.trim() && !loading
                        ? undefined
                        : "var(--color-text-muted, #9ca3af)",
                  }}
                >
                  <line x1="22" y1="2" x2="11" y2="13" />
                  <polygon points="22 2 15 22 11 13 2 9 22 2" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
