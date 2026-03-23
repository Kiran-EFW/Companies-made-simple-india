"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import { getSubscriptions, type SubscriptionOut } from "./api";
import { useCompany } from "./company-context";
import {
  type SubscriptionTier,
  getRequiredTier,
  hasAccess,
} from "./subscription-tiers";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface SubscriptionContextValue {
  /** The active subscription for the selected company (null if none). */
  subscription: SubscriptionOut | null;
  /** Effective tier — defaults to "starter" if no active subscription. */
  currentTier: SubscriptionTier;
  /** Whether the subscription data is still loading. */
  loading: boolean;
  /** Check if the current tier meets the requirement for a module. */
  canAccess: (moduleKey: string) => boolean;
  /** Get the tier required for a module (null if available to all). */
  requiredTierFor: (moduleKey: string) => SubscriptionTier | null;
  /** Re-fetch subscription data (e.g. after upgrade). */
  refreshSubscription: () => Promise<void>;
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

const SubscriptionContext = createContext<SubscriptionContextValue>({
  subscription: null,
  currentTier: "starter",
  loading: true,
  canAccess: () => true,
  requiredTierFor: () => null,
  refreshSubscription: async () => {},
});

export function useSubscription(): SubscriptionContextValue {
  return useContext(SubscriptionContext);
}

// ---------------------------------------------------------------------------
// Provider
// ---------------------------------------------------------------------------

export function SubscriptionProvider({ children }: { children: ReactNode }) {
  const { selectedCompany } = useCompany();
  const [subscription, setSubscription] = useState<SubscriptionOut | null>(
    null,
  );
  const [loading, setLoading] = useState(true);

  const fetchSubscription = useCallback(async () => {
    if (!selectedCompany) {
      setSubscription(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const subs = await getSubscriptions(selectedCompany.id);
      // Find the active subscription (most recent active one)
      const active = subs.find((s) => s.status === "active") ?? null;
      setSubscription(active);
    } catch (err) {
      console.error("Failed to fetch subscription:", err);
      setSubscription(null);
    } finally {
      setLoading(false);
    }
  }, [selectedCompany]);

  useEffect(() => {
    fetchSubscription();
  }, [fetchSubscription]);

  // Derive the effective tier
  const currentTier: SubscriptionTier =
    subscription?.plan_key === "scale"
      ? "scale"
      : subscription?.plan_key === "growth"
        ? "growth"
        : "starter";

  const canAccess = useCallback(
    (moduleKey: string): boolean => {
      const required = getRequiredTier(moduleKey);
      if (!required) return true; // No tier restriction
      return hasAccess(currentTier, required);
    },
    [currentTier],
  );

  const requiredTierFor = useCallback(
    (moduleKey: string): SubscriptionTier | null => {
      return getRequiredTier(moduleKey);
    },
    [],
  );

  return (
    <SubscriptionContext.Provider
      value={{
        subscription,
        currentTier,
        loading,
        canAccess,
        requiredTierFor,
        refreshSubscription: fetchSubscription,
      }}
    >
      {children}
    </SubscriptionContext.Provider>
  );
}
