/**
 * Subscription tier constants, module-to-tier mapping, and helpers.
 *
 * This is the single source of truth for feature gating on the frontend.
 * Tier definitions (prices, features) are kept in sync with
 * backend/src/services/services_catalog.py → SUBSCRIPTION_PLANS.
 */

// ---------------------------------------------------------------------------
// Tier hierarchy
// ---------------------------------------------------------------------------

export const TIER_HIERARCHY = ["starter", "growth", "scale"] as const;
export type SubscriptionTier = (typeof TIER_HIERARCHY)[number];

export function tierLevel(tier: SubscriptionTier): number {
  return TIER_HIERARCHY.indexOf(tier);
}

export function hasAccess(
  currentTier: SubscriptionTier,
  requiredTier: SubscriptionTier,
): boolean {
  return tierLevel(currentTier) >= tierLevel(requiredTier);
}

// ---------------------------------------------------------------------------
// Module → required tier mapping
// ---------------------------------------------------------------------------

/** Pages not listed here are available on all tiers (starter+). */
export const MODULE_REQUIRED_TIER: Record<string, SubscriptionTier> = {
  "cap-table": "growth",
  esop: "growth",
  fundraising: "growth",
  valuations: "growth",
  "data-room": "growth",
  accounting: "growth",
  signatures: "growth",
  meetings: "scale",
  registers: "scale",
};

export function getRequiredTier(moduleKey: string): SubscriptionTier | null {
  return MODULE_REQUIRED_TIER[moduleKey] ?? null;
}

// ---------------------------------------------------------------------------
// Tier display metadata
// ---------------------------------------------------------------------------

export interface TierMeta {
  name: string;
  monthlyPrice: number;
  annualPrice: number;
  tagline: string;
  color: string;
  highlights: string[];
}

export const TIER_META: Record<SubscriptionTier, TierMeta> = {
  starter: {
    name: "Starter",
    monthlyPrice: 499,
    annualPrice: 4999,
    tagline: "Essential company management",
    color: "var(--color-text-secondary)",
    highlights: [
      "Company dashboard with key metrics",
      "Compliance calendar with deadline reminders",
      "Email & SMS alerts before due dates",
      "Document storage (up to 50 documents)",
      "Director/partner KYC tracker",
      "Services marketplace access",
    ],
  },
  growth: {
    name: "Growth",
    monthlyPrice: 2999,
    annualPrice: 29999,
    tagline: "For funded startups & companies planning to raise",
    color: "var(--color-accent-purple)",
    highlights: [
      "Full cap table with dilution modeling",
      "ESOP plan creation & grant management",
      "Fundraising rounds (SAFE, CCD, CCPS, equity)",
      "Investor portal (token-based + authenticated)",
      "Data room with granular access controls",
      "E-signatures (up to 20/month)",
      "Valuations (Rule 11UA FMV calculator)",
      "Team management (up to 10 users)",
    ],
  },
  scale: {
    name: "Scale",
    monthlyPrice: 9999,
    annualPrice: 99999,
    tagline: "For Series A+ companies & pre-IPO",
    color: "var(--color-accent-emerald, #10b981)",
    highlights: [
      "Board meeting management with agenda builder",
      "Resolution workflow and voting",
      "Statutory registers (members, directors, charges)",
      "Investor reporting & portfolio dashboard",
      "Unlimited e-signatures",
      "FEMA/RBI compliance tracker",
      "Unlimited users",
      "Dedicated account manager",
    ],
  },
};

// ---------------------------------------------------------------------------
// Page → marketplace service upsell mapping
// ---------------------------------------------------------------------------

/** Maps the current page key to service keys that should be suggested. */
export const PAGE_UPSELL_SERVICES: Record<string, string[]> = {
  compliance: ["gst_registration", "itr_company", "annual_roc_filing"],
  gst: ["gst_monthly_filing", "gst_registration"],
  tax: ["itr_company", "itr_llp", "tds_quarterly"],
  "company-info": ["inc20a_commencement"],
  "cap-table": ["share_allotment", "increase_capital"],
};
