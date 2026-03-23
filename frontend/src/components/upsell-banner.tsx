"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getUpsellItems } from "@/lib/api";
import { PAGE_UPSELL_SERVICES } from "@/lib/subscription-tiers";

interface UpsellBannerProps {
  pageKey: string;
  companyId: number;
}

interface UpsellItem {
  service_key: string;
  name: string;
  short_description: string;
  category: string;
  total: number;
  urgency: string;
  reason: string;
}

/**
 * Contextual banner that suggests relevant marketplace services based on
 * the current page.  Dismissible per page per company.
 */
export default function UpsellBanner({ pageKey, companyId }: UpsellBannerProps) {
  const [items, setItems] = useState<UpsellItem[]>([]);
  const [dismissed, setDismissed] = useState(true);
  const [loading, setLoading] = useState(true);

  const storageKey = `upsell_dismissed_${pageKey}_${companyId}`;

  useEffect(() => {
    // Check if dismissed in this session
    const wasDismissed =
      typeof window !== "undefined" &&
      sessionStorage.getItem(storageKey) === "1";
    setDismissed(wasDismissed);

    if (wasDismissed) {
      setLoading(false);
      return;
    }

    const relevantKeys = PAGE_UPSELL_SERVICES[pageKey] || [];
    if (relevantKeys.length === 0) {
      setLoading(false);
      return;
    }

    getUpsellItems(companyId)
      .then((allItems: UpsellItem[]) => {
        const matching = allItems.filter((item) =>
          relevantKeys.includes(item.service_key),
        );
        setItems(matching);
      })
      .catch(() => {
        setItems([]);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [companyId, pageKey, storageKey]);

  const handleDismiss = () => {
    setDismissed(true);
    if (typeof window !== "undefined") {
      sessionStorage.setItem(storageKey, "1");
    }
  };

  if (loading || dismissed || items.length === 0) return null;

  return (
    <div
      className="rounded-xl p-4 mb-4 flex items-start gap-4"
      style={{
        background:
          "linear-gradient(135deg, rgba(124,58,237,0.06), rgba(16,185,129,0.06))",
        border: "1px solid var(--color-border)",
      }}
    >
      {/* Icon */}
      <div
        className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
        style={{ background: "rgba(124,58,237,0.12)" }}
      >
        <svg
          className="w-5 h-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.5}
          style={{ color: "var(--color-accent-purple-light)" }}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M13 10V3L4 14h7v7l9-11h-7z"
          />
        </svg>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <p
          className="text-xs font-semibold uppercase tracking-wider mb-1"
          style={{ color: "var(--color-accent-purple-light)" }}
        >
          Recommended service{items.length > 1 ? "s" : ""}
        </p>
        <div className="space-y-2">
          {items.slice(0, 2).map((item) => (
            <div key={item.service_key} className="flex items-center gap-3">
              <div className="flex-1 min-w-0">
                <p
                  className="text-sm font-medium truncate"
                  style={{ color: "var(--color-text-primary)" }}
                >
                  {item.name}
                </p>
                <p
                  className="text-xs truncate"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  {item.reason}
                </p>
              </div>
              <Link
                href={`/dashboard/services?highlight=${item.service_key}`}
                className="flex-shrink-0 px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition-colors"
                style={{ background: "var(--color-accent-purple)" }}
              >
                &#8377;{item.total.toLocaleString("en-IN")}
              </Link>
            </div>
          ))}
        </div>
      </div>

      {/* Dismiss */}
      <button
        onClick={handleDismiss}
        className="flex-shrink-0 p-1 rounded-lg transition-colors hover:bg-gray-100"
        style={{ color: "var(--color-text-muted)" }}
        aria-label="Dismiss"
      >
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
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>
  );
}
