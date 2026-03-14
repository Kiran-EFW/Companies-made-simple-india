"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  useRef,
  type ReactNode,
} from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type ToastType = "success" | "error" | "info";

interface ToastItem {
  id: number;
  message: string;
  type: ToastType;
  /** Whether the toast is currently visible (drives CSS transition) */
  visible: boolean;
}

interface ToastContextValue {
  toast: (message: string, type?: ToastType) => void;
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

const ToastContext = createContext<ToastContextValue | null>(null);

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error("useToast must be used within a <ToastProvider>");
  }
  return ctx;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const MAX_TOASTS = 5;
const AUTO_DISMISS_MS = 4_000;
const ANIMATION_MS = 300;

const BORDER_COLOR: Record<ToastType, string> = {
  success: "border-l-emerald-500",
  error: "border-l-red-500",
  info: "border-l-blue-500",
};

const ICON_COLOR: Record<ToastType, string> = {
  success: "text-emerald-400",
  error: "text-red-400",
  info: "text-blue-400",
};

// ---------------------------------------------------------------------------
// Provider
// ---------------------------------------------------------------------------

let nextId = 0;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const timersRef = useRef<Map<number, ReturnType<typeof setTimeout>>>(
    new Map(),
  );

  // Remove a toast from state (called after exit animation completes)
  const remove = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
    const timer = timersRef.current.get(id);
    if (timer) {
      clearTimeout(timer);
      timersRef.current.delete(id);
    }
  }, []);

  // Begin the exit animation, then remove
  const dismiss = useCallback(
    (id: number) => {
      setToasts((prev) =>
        prev.map((t) => (t.id === id ? { ...t, visible: false } : t)),
      );
      setTimeout(() => remove(id), ANIMATION_MS);
    },
    [remove],
  );

  // Public toast function exposed via context
  const toast = useCallback(
    (message: string, type: ToastType = "info") => {
      const id = ++nextId;
      const item: ToastItem = { id, message, type, visible: false };

      setToasts((prev) => {
        // Drop oldest if we already have MAX_TOASTS
        const trimmed =
          prev.length >= MAX_TOASTS ? prev.slice(prev.length - MAX_TOASTS + 1) : prev;
        return [...trimmed, item];
      });

      // Trigger enter animation on next frame
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          setToasts((prev) =>
            prev.map((t) => (t.id === id ? { ...t, visible: true } : t)),
          );
        });
      });

      // Auto-dismiss
      const timer = setTimeout(() => dismiss(id), AUTO_DISMISS_MS);
      timersRef.current.set(id, timer);
    },
    [dismiss],
  );

  // Cleanup timers on unmount
  useEffect(() => {
    const timers = timersRef.current;
    return () => {
      timers.forEach((t) => clearTimeout(t));
      timers.clear();
    };
  }, []);

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}

      {/* Toast container -- fixed bottom-right */}
      <div className="fixed bottom-6 right-6 z-[9999] flex flex-col-reverse items-end gap-2 pointer-events-none">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`
              pointer-events-auto
              flex items-start gap-3
              w-80 max-w-[calc(100vw-3rem)]
              px-4 py-3
              rounded-lg
              border border-gray-700 border-l-4
              ${BORDER_COLOR[t.type]}
              bg-gray-900 text-white shadow-lg shadow-black/40
              transition-all duration-300 ease-out
              ${
                t.visible
                  ? "opacity-100 translate-x-0"
                  : "opacity-0 translate-x-4"
              }
            `}
            role="alert"
          >
            {/* Icon */}
            <span className={`mt-0.5 shrink-0 ${ICON_COLOR[t.type]}`}>
              {t.type === "success" && (
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
                    d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              )}
              {t.type === "error" && (
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
                    d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
                  />
                </svg>
              )}
              {t.type === "info" && (
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
                    d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z"
                  />
                </svg>
              )}
            </span>

            {/* Message */}
            <span className="flex-1 text-sm leading-snug">{t.message}</span>

            {/* Close button */}
            <button
              onClick={() => dismiss(t.id)}
              className="shrink-0 mt-0.5 text-gray-500 hover:text-gray-300 transition-colors"
              aria-label="Dismiss"
            >
              <svg
                className="w-3.5 h-3.5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
