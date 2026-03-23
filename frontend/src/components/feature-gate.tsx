"use client";

import Link from "next/link";
import { useSubscription } from "@/lib/subscription-context";
import {
  type SubscriptionTier,
  getRequiredTier,
  TIER_META,
} from "@/lib/subscription-tiers";

interface FeatureGateProps {
  moduleKey: string;
  featureName: string;
  featureDescription?: string;
  children: React.ReactNode;
}

/**
 * Wraps a page's content and checks whether the current subscription tier
 * meets the module's requirement.  If not, renders an inline upgrade prompt
 * instead of the children.
 */
export default function FeatureGate({
  moduleKey,
  featureName,
  featureDescription,
  children,
}: FeatureGateProps) {
  const { canAccess, currentTier, loading } = useSubscription();

  // Show loading while subscription data is being fetched
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div
          className="animate-spin rounded-full h-8 w-8 border-b-2"
          style={{ borderColor: "var(--color-accent-purple-light)" }}
        />
      </div>
    );
  }

  // User has access — render the page
  if (canAccess(moduleKey)) {
    return <>{children}</>;
  }

  // User doesn't have access — render upgrade prompt
  const requiredTier = getRequiredTier(moduleKey) as SubscriptionTier;
  const required = TIER_META[requiredTier];

  return (
    <div className="flex items-center justify-center min-h-[500px] px-4">
      <div
        className="max-w-md w-full rounded-2xl p-8 text-center"
        style={{
          background: "var(--color-bg-card)",
          border: "1px solid var(--color-border)",
          boxShadow: "0 4px 24px rgba(0,0,0,0.06)",
        }}
      >
        {/* Lock icon */}
        <div className="flex justify-center mb-5">
          <div
            className="w-16 h-16 rounded-full flex items-center justify-center"
            style={{ background: "rgba(124,58,237,0.1)" }}
          >
            <svg
              className="w-8 h-8"
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
        <h2
          className="text-xl font-bold mb-2"
          style={{
            fontFamily: "var(--font-display)",
            color: "var(--color-text-primary)",
          }}
        >
          {featureName}
        </h2>

        <p
          className="text-sm mb-1"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {featureDescription ||
            `This feature is available on the ${required.name} plan and above.`}
        </p>

        <p
          className="text-xs mb-6"
          style={{ color: "var(--color-text-muted)" }}
        >
          You are currently on the{" "}
          <span className="font-semibold">{TIER_META[currentTier].name}</span>{" "}
          plan.
        </p>

        {/* Feature highlights */}
        <div
          className="rounded-xl p-4 mb-6 text-left"
          style={{
            background: "var(--color-bg-secondary)",
            border: "1px solid var(--color-border)",
          }}
        >
          <p
            className="text-xs font-semibold uppercase tracking-wider mb-3"
            style={{ color: "var(--color-text-muted)" }}
          >
            {required.name} plan includes
          </p>
          <ul className="space-y-2">
            {required.highlights.map((feature, i) => (
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

        {/* Pricing */}
        <div className="mb-5">
          <span
            className="text-2xl font-bold"
            style={{ color: "var(--color-accent-purple-light)" }}
          >
            &#8377;{required.monthlyPrice.toLocaleString("en-IN")}
          </span>
          <span
            className="text-sm ml-1"
            style={{ color: "var(--color-text-muted)" }}
          >
            /month
          </span>
          <span
            className="text-xs ml-2"
            style={{ color: "var(--color-text-muted)" }}
          >
            or &#8377;{required.annualPrice.toLocaleString("en-IN")}/year
          </span>
        </div>

        {/* CTA */}
        <Link
          href={`/dashboard/services?upgrade=${requiredTier}`}
          className="inline-block w-full py-3 rounded-lg text-sm font-semibold text-white transition-colors"
          style={{ background: "var(--color-accent-purple)" }}
        >
          Upgrade to {required.name}
        </Link>

        <Link
          href="/dashboard/billing"
          className="inline-block mt-3 text-xs transition-colors"
          style={{ color: "var(--color-text-muted)" }}
        >
          View billing details
        </Link>
      </div>
    </div>
  );
}
