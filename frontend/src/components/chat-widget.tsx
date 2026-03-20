"use client";

import { useState, useEffect, useRef } from "react";
import { sendChatMessage, getSuggestedQuestions } from "@/lib/api";
import { formatContent } from "@/lib/format-content";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

interface ChatWidgetProps {
  companyId?: number;
}

export default function ChatWidget({ companyId }: ChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Fetch suggested questions on mount (only if authenticated)
  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    if (!token) {
      setSuggestedQuestions([
        "What type of company should I form?",
        "How does cap table management work?",
        "What compliance filings are required?",
      ]);
      return;
    }
    const fetchSuggestions = async () => {
      try {
        const data = await getSuggestedQuestions();
        setSuggestedQuestions(data.questions || []);
      } catch (err) {
        setSuggestedQuestions([
          "How do I set up my cap table?",
          "What ESOP plans can I create?",
          "What compliance deadlines are coming up?",
        ]);
      }
    };
    fetchSuggestions();
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  const handleSend = async (messageText?: string) => {
    const text = messageText || inputValue.trim();
    if (!text || loading) return;

    const userMessage: ChatMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setLoading(true);

    try {
      // Build conversation history from last 10 messages
      const history = [...messages, userMessage]
        .slice(-10)
        .map((m) => ({ role: m.role, content: m.content }));

      const data = await sendChatMessage({
        message: text,
        company_id: companyId,
        conversation_history: history,
      });

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: data.response,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Chat error:", err);
      const errorMessage: ChatMessage = {
        role: "assistant",
        content:
          "Sorry, I encountered an error. Please try again in a moment.",
      };
      setMessages((prev) => [...prev, errorMessage]);
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

  return (
    <>
      {/* Chat Toggle Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-all duration-300 hover:scale-110 hover:shadow-xl"
          style={{
            background: "var(--color-accent-purple, #7c3aed)",
            boxShadow: "0 4px 20px rgba(124, 58, 237, 0.35)",
          }}
          aria-label="Open chat"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="white"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </button>
      )}

      {/* Chat Panel */}
      {isOpen && (
        <div
          className="fixed bottom-6 right-6 z-50 flex flex-col overflow-hidden animate-fade-in-up"
          style={{
            width: "380px",
            height: "520px",
            maxHeight: "calc(100vh - 48px)",
            maxWidth: "calc(100vw - 48px)",
            background: "var(--color-bg-card, #ffffff)",
            border: "1px solid var(--color-border, #e5e7eb)",
            borderRadius: "16px",
            boxShadow:
              "0 8px 40px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(124, 58, 237, 0.08)",
          }}
        >
          {/* Header */}
          <div
            className="flex items-center justify-between px-4 py-3 shrink-0"
            style={{
              borderBottom: "1px solid var(--color-border, #e5e7eb)",
              background: "var(--color-accent-purple, #7c3aed)",
            }}
          >
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="white"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
              </div>
              <div>
                <span className="text-sm font-semibold text-white">Anvils Assistant</span>
                <div className="flex items-center gap-1.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-300" />
                  <span className="text-[10px] text-white/70">Online</span>
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="w-7 h-7 rounded-lg flex items-center justify-center transition-colors hover:bg-white/20 text-white/80 hover:text-white"
              aria-label="Close chat"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>

          {/* Messages Area */}
          <div
            className="flex-1 overflow-y-auto px-4 py-4 space-y-3"
            style={{
              scrollbarWidth: "thin",
              scrollbarColor: "rgba(124, 58, 237, 0.2) transparent",
            }}
          >
            {/* Welcome Message & Suggested Questions */}
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
                  Hi! I can help you with cap table management, ESOP plans,
                  fundraising, compliance, incorporation, and more.
                  Ask me anything about managing your company on Anvils.
                </div>

                {suggestedQuestions.length > 0 && (
                  <div className="space-y-2">
                    <p
                      className="text-[11px] font-medium uppercase tracking-wider"
                      style={{
                        color: "var(--color-text-muted, #9ca3af)",
                      }}
                    >
                      Try asking
                    </p>
                    <div className="flex flex-col gap-2">
                      {suggestedQuestions.map((q, idx) => (
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
                          <span style={{ color: "var(--color-accent-purple, #7c3aed)" }}>→ </span>
                          {q}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Chat Messages */}
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
                  {msg.role === "assistant" ? formatContent(msg.content) : msg.content}
                </div>
              </div>
            ))}

            {/* Typing Indicator */}
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
          </div>

          {/* Input Area */}
          <div
            className="px-3 py-3 shrink-0"
            style={{
              borderTop: "1px solid var(--color-border, #e5e7eb)",
            }}
          >
            <div
              className="flex items-center gap-2 rounded-xl px-3 py-2"
              style={{
                background: "var(--color-bg-secondary, #f9fafb)",
                border: "1px solid var(--color-border, #e5e7eb)",
              }}
            >
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask anything about Anvils..."
                disabled={loading}
                className="flex-1 bg-transparent text-sm outline-none placeholder:text-gray-400"
                style={{ color: "var(--color-text-primary, #111827)" }}
              />
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
                  stroke={inputValue.trim() && !loading ? "white" : "currentColor"}
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  style={{
                    color: inputValue.trim() && !loading ? undefined : "var(--color-text-muted, #9ca3af)",
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
