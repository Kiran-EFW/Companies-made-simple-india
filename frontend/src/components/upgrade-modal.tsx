"use client";

import { useEffect } from "react";
import Link from "next/link";
import { type SubscriptionTier, TIER_META } from "@/lib/subscription-tiers";

interface UpgradeModalProps {
  open: boolean;
  onClose: () => void;
  requiredTier: SubscriptionTier;
  currentTier: SubscriptionTier;
  featureName: string;
  featureDescription?: string;
}

export default function UpgradeModal({
  open,
  onClose,
  requiredTier,
  currentTier,
  featureName,
  featureDescription,
}: UpgradeModalProps) {
  useEffect(() => {
    if (!open) return;
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleEsc);
    return () => document.removeEventListener("keydown", handleEsc);
  }, [open, onClose]);

  if (!open) return null;

  const required = TIER_META[requiredTier];
  const current = TIER_META[currentTier];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 backdrop-blur-sm"
        style={{ background: "var(--color-overlay)" }}
        onClick={onClose}
      />
      <div
        className="relative rounded-2xl p-8 max-w-lg w-full mx-4 shadow-2xl animate-fade-in-up"
        style={{
          background: "var(--color-bg-secondary)",
          border: "1px solid var(--color-border)",
        }}
      >
        {/* Lock icon */}
        <div className="flex justify-center mb-4">
          <div
            className="w-14 h-14 rounded-full flex items-center justify-center"
            style={{ background: "rgba(124,58,237,0.1)" }}
          >
            <svg
              className="w-7 h-7"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
              style={{ color: "var(--color-accent-purple-light)" }}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              />
            </svg>
          </div>
        </div>

        {/* Title */}
        <h3
          className="text-xl font-bold text-center mb-1"
          style={{
            fontFamily: "var(--font-display)",
            color: "var(--color-text-primary)",
          }}
        >
          Unlock {featureName}
        </h3>

        {featureDescription && (
          <p
            className="text-sm text-center mb-6"
            style={{ color: "var(--color-text-secondary)" }}
          >
            {featureDescription}
          </p>
        )}

        {/* Tier comparison */}
        <div
          className="rounded-xl p-4 mb-6"
          style={{
            background: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
          }}
        >
          <div className="flex items-center justify-between mb-3">
            <div>
              <span
                className="text-xs font-medium uppercase tracking-wider"
                style={{ color: "var(--color-text-muted)" }}
              >
                Current plan
              </span>
              <p
                className="text-sm font-semibold"
                style={{ color: "var(--color-text-primary)" }}
              >
                {current.name}
              </p>
            </div>
            <svg
              className="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
              style={{ color: "var(--color-text-muted)" }}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M13 7l5 5m0 0l-5 5m5-5H6"
              />
            </svg>
            <div className="text-right">
              <span
                className="text-xs font-medium uppercase tracking-wider"
                style={{ color: required.color }}
              >
                Required
              </span>
              <p className="text-sm font-semibold" style={{ color: required.color }}>
                {required.name}
              </p>
            </div>
          </div>

          <div
            className="text-center py-2 rounded-lg"
            style={{ background: "rgba(124,58,237,0.06)" }}
          >
            <span
              className="text-lg font-bold"
              style={{ color: "var(--color-accent-purple-light)" }}
            >
              &#8377;{required.monthlyPrice.toLocaleString("en-IN")}
            </span>
            <span
              className="text-xs ml-1"
              style={{ color: "var(--color-text-muted)" }}
            >
              /month
            </span>
            <span
              className="text-xs ml-2"
              style={{ color: "var(--color-text-muted)" }}
            >
              (&#8377;{required.annualPrice.toLocaleString("en-IN")}/year)
            </span>
          </div>
        </div>

        {/* Feature highlights */}
        <div className="mb-6">
          <p
            className="text-xs font-semibold uppercase tracking-wider mb-2"
            style={{ color: "var(--color-text-muted)" }}
          >
            What you get with {required.name}
          </p>
          <ul className="space-y-1.5">
            {required.highlights.slice(0, 6).map((feature, i) => (
              <li
                key={i}
                className="flex items-start gap-2 text-sm"
                style={{ color: "var(--color-text-secondary)" }}
              >
                <svg
                  className="w-4 h-4 flex-shrink-0 mt-0.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                  style={{ color: "#10b981" }}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                {feature}
              </li>
            ))}
          </ul>
        </div>

        {/* Actions */}
        <div className="flex flex-col gap-2">
          <Link
            href={`/dashboard/services?upgrade=${requiredTier}`}
            className="w-full py-2.5 rounded-lg text-sm font-semibold text-white text-center transition-colors"
            style={{ background: "var(--color-accent-purple)" }}
            onClick={onClose}
          >
            Upgrade to {required.name}
          </Link>
          <button
            onClick={onClose}
            className="w-full py-2 text-sm transition-colors"
            style={{ color: "var(--color-text-muted)" }}
          >
            Maybe later
          </button>
        </div>
      </div>
    </div>
  );
}
