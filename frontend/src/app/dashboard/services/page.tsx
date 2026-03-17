"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import {
  getServicesCatalog,
  getSubscriptionPlans,
  getCompanies,
  createServiceRequest,
  createSubscription,
  getServiceRequests,
  getSubscriptions,
  payForServiceRequest,
  payForSubscription,
  type ServiceDefinition,
  type SubscriptionPlanDef,
  type ServiceRequestOut,
  type SubscriptionOut,
} from "@/lib/api";

const CATEGORY_LABELS: Record<string, string> = {
  compliance: "Compliance",
  tax: "Tax Filing",
  registration: "Registrations",
  legal: "Legal",
  accounting: "Accounting",
  amendment: "Amendments",
};

const CATEGORY_ORDER = ["registration", "compliance", "tax", "accounting", "amendment", "legal"];

const FREQUENCY_LABELS: Record<string, string> = {
  one_time: "One-time",
  monthly: "/month",
  quarterly: "/quarter",
  annual: "/year",
};

const BADGE_STYLES: Record<string, string> = {
  popular: "bg-[var(--color-accent-purple)]/20 text-[var(--color-accent-purple-light)]",
  mandatory: "bg-[var(--color-error-light)] text-[var(--color-error)]",
  recommended: "bg-[var(--color-success-light)] text-[var(--color-success)]",
};

export default function ServicesPage() {
  const { user, loading: authLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<"services" | "subscriptions" | "my-requests">("services");
  const [services, setServices] = useState<ServiceDefinition[]>([]);
  const [plans, setPlans] = useState<SubscriptionPlanDef[]>([]);
  const [companies, setCompanies] = useState<any[]>([]);
  const [requests, setRequests] = useState<ServiceRequestOut[]>([]);
  const [subscriptions, setSubscriptions] = useState<SubscriptionOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedCompany, setSelectedCompany] = useState<number>(0);
  const [requesting, setRequesting] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [subInterval, setSubInterval] = useState<"annual" | "monthly">("annual");

  useEffect(() => {
    if (authLoading || !user) return;
    const load = async () => {
      try {
        const [svcs, pls, comps, reqs, subs] = await Promise.all([
          getServicesCatalog(),
          getSubscriptionPlans(),
          getCompanies(),
          getServiceRequests(),
          getSubscriptions(),
        ]);
        setServices(svcs);
        setPlans(pls);
        setCompanies(comps);
        setRequests(reqs);
        setSubscriptions(subs);
        if (comps.length > 0) setSelectedCompany(comps[0].id);
      } catch (err) {
        console.error("Failed to load services:", err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [user, authLoading]);

  const handleRequest = async (svc: ServiceDefinition) => {
    if (!selectedCompany) {
      setErrorMsg("Please select a company first.");
      return;
    }
    setRequesting(svc.key);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      await createServiceRequest({ company_id: selectedCompany, service_key: svc.key });
      setSuccessMsg(`Request submitted for "${svc.name}". Our team will reach out shortly.`);
      const reqs = await getServiceRequests();
      setRequests(reqs);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to submit request");
    } finally {
      setRequesting(null);
    }
  };

  const handleSubscribe = async (plan: SubscriptionPlanDef) => {
    if (!selectedCompany) {
      setErrorMsg("Please select a company first.");
      return;
    }
    setRequesting(plan.key);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      await createSubscription({
        company_id: selectedCompany,
        plan_key: plan.key,
        interval: subInterval,
      });
      setSuccessMsg(`Subscribed to "${plan.name}" plan! Our team will set up your compliance services.`);
      const subs = await getSubscriptions();
      setSubscriptions(subs);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to subscribe");
    } finally {
      setRequesting(null);
    }
  };

  const filteredServices = selectedCategory === "all"
    ? services
    : services.filter(s => s.category === selectedCategory);

  const groupedServices: Record<string, ServiceDefinition[]> = {};
  for (const svc of filteredServices) {
    if (!groupedServices[svc.category]) groupedServices[svc.category] = [];
    groupedServices[svc.category].push(svc);
  }

  const existingRequestKeys = new Set(
    requests.filter(r => r.company_id === selectedCompany && r.status !== "cancelled").map(r => r.service_key)
  );

  const activeSubscription = subscriptions.find(
    s => s.company_id === selectedCompany && s.status === "active"
  );

  return (
    <div>
      {/* Page header with company selector */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">Services Marketplace</h1>
          <p className="text-[var(--color-text-secondary)] text-sm mt-1">
            Post-incorporation services, compliance packages, and add-ons
          </p>
        </div>
        {companies.length > 0 && (
          <div className="flex items-center gap-3">
            <label className="text-sm text-[var(--color-text-secondary)]">Company:</label>
            <select
              value={selectedCompany}
              onChange={e => setSelectedCompany(Number(e.target.value))}
              className="bg-[var(--color-bg-input)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg px-3 py-2 text-sm"
            >
              {companies.map(c => (
                <option key={c.id} value={c.id}>
                  {c.approved_name || c.proposed_names?.[0] || `Company #${c.id}`}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="flex gap-1 bg-[var(--color-bg-secondary)] rounded-lg p-1 w-fit">
          {[
            { key: "services" as const, label: "Add-On Services" },
            { key: "subscriptions" as const, label: "Compliance Plans" },
            { key: "my-requests" as const, label: "My Requests" },
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition ${
                activeTab === tab.key
                  ? "bg-[var(--color-accent-purple)] text-white"
                  : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
              }`}
            >
              {tab.label}
              {tab.key === "my-requests" && requests.length > 0 && (
                <span className="ml-2 bg-[var(--color-accent-purple)]/30 text-[var(--color-accent-purple-light)] px-1.5 py-0.5 rounded-full text-xs">
                  {requests.filter(r => r.status !== "cancelled" && r.status !== "completed").length}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      {(successMsg || errorMsg) && (
        <div className="mb-4">
          {successMsg && (
            <div className="bg-[var(--color-success-light)] border border-[var(--color-success)]/30 text-[var(--color-success)] px-4 py-3 rounded-lg text-sm">
              {successMsg}
            </div>
          )}
          {errorMsg && (
            <div className="bg-[var(--color-error-light)] border border-[var(--color-error)]/30 text-[var(--color-error)] px-4 py-3 rounded-lg text-sm">
              {errorMsg}
            </div>
          )}
        </div>
      )}

      {loading ? (
        <div className="text-center py-20 text-[var(--color-text-secondary)]">Loading services...</div>
      ) : activeTab === "services" ? (
        /* ─── Add-On Services ─── */
        <div>
          {/* Category filter */}
          <div className="flex flex-wrap gap-2 mb-6">
            <button
              onClick={() => setSelectedCategory("all")}
              className={`px-3 py-1.5 rounded-full text-sm transition ${
                selectedCategory === "all"
                  ? "bg-[var(--color-accent-purple)] text-white"
                  : "bg-[var(--color-bg-card)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] border border-[var(--color-border)]"
              }`}
            >
              All Services
            </button>
            {CATEGORY_ORDER.map(cat => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1.5 rounded-full text-sm transition ${
                  selectedCategory === cat
                    ? "bg-[var(--color-accent-purple)] text-white"
                    : "bg-[var(--color-bg-card)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] border border-[var(--color-border)]"
                }`}
              >
                {CATEGORY_LABELS[cat]}
              </button>
            ))}
          </div>

          {/* Services grid by category */}
          {CATEGORY_ORDER.filter(cat => groupedServices[cat]).map(cat => (
            <div key={cat} className="mb-8">
              <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mb-4">
                {CATEGORY_LABELS[cat]}
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {groupedServices[cat].map(svc => {
                  const alreadyRequested = existingRequestKeys.has(svc.key);
                  return (
                    <div
                      key={svc.key}
                      className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl p-5 flex flex-col justify-between hover:border-[var(--color-accent-purple)]/30 transition"
                    >
                      <div>
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="font-semibold text-[var(--color-text-primary)] text-sm leading-tight">
                            {svc.name}
                          </h3>
                          {svc.badge && (
                            <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase ${BADGE_STYLES[svc.badge] || ""}`}>
                              {svc.badge}
                            </span>
                          )}
                        </div>
                        <p className="text-[var(--color-text-secondary)] text-xs mb-3 leading-relaxed">
                          {svc.short_description}
                        </p>
                        {svc.penalty_note && (
                          <p className="text-[var(--color-warning)] text-[10px] bg-[var(--color-warning-light)] px-2 py-1 rounded mb-3">
                            {svc.penalty_note}
                          </p>
                        )}
                      </div>
                      <div className="flex items-end justify-between mt-3 pt-3 border-t border-[var(--color-border)]">
                        <div>
                          <span className="text-lg font-bold text-[var(--color-text-primary)]">
                            Rs {svc.total.toLocaleString("en-IN")}
                          </span>
                          <span className="text-[var(--color-text-muted)] text-xs ml-1">
                            {FREQUENCY_LABELS[svc.frequency] || ""}
                          </span>
                          {svc.government_fee > 0 && (
                            <span className="block text-[var(--color-text-muted)] text-[10px]">
                              incl. Rs {svc.government_fee.toLocaleString("en-IN")} govt fee
                            </span>
                          )}
                        </div>
                        <button
                          onClick={() => handleRequest(svc)}
                          disabled={requesting === svc.key || alreadyRequested}
                          className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                            alreadyRequested
                              ? "bg-[var(--color-bg-secondary)] text-[var(--color-text-muted)] cursor-not-allowed"
                              : "bg-[var(--color-accent-purple)] text-white hover:bg-[var(--color-accent-purple-light)]"
                          }`}
                        >
                          {requesting === svc.key ? "..." : alreadyRequested ? "Requested" : "Request"}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      ) : activeTab === "subscriptions" ? (
        /* ─── Compliance Subscription Plans ─── */
        <div>
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-[var(--color-text-primary)] mb-2">
              Annual Compliance Packages
            </h2>
            <p className="text-[var(--color-text-secondary)] mb-4">
              Stay compliant year-round. Every package includes filing, reminders, and a dedicated manager.
            </p>
            {/* Interval toggle */}
            <div className="flex items-center justify-center gap-3">
              <span className={`text-sm ${subInterval === "monthly" ? "text-[var(--color-text-primary)]" : "text-[var(--color-text-muted)]"}`}>Monthly</span>
              <button
                onClick={() => setSubInterval(prev => prev === "annual" ? "monthly" : "annual")}
                className="relative w-14 h-7 rounded-full bg-[var(--color-bg-secondary)] border border-[var(--color-border)] transition"
              >
                <span
                  className={`absolute top-0.5 w-6 h-6 rounded-full bg-[var(--color-accent-purple)] transition-all ${
                    subInterval === "annual" ? "left-7" : "left-0.5"
                  }`}
                />
              </button>
              <span className={`text-sm ${subInterval === "annual" ? "text-[var(--color-text-primary)]" : "text-[var(--color-text-muted)]"}`}>
                Annual <span className="text-[var(--color-success)] text-xs">(Save ~17%)</span>
              </span>
            </div>
          </div>

          {/* Peace of Mind — featured banner */}
          {plans.filter(p => p.is_peace_of_mind).map(plan => {
            const price = subInterval === "annual" ? plan.annual_price : plan.monthly_price;
            const isCurrentPlan = activeSubscription?.plan_key === plan.key;
            const individualCost = 145000; // approximate cost if services bought individually
            const savings = individualCost - (subInterval === "annual" ? plan.annual_price : plan.monthly_price * 12);

            return (
              <div
                key={plan.key}
                className="mb-8 bg-gradient-to-r from-[var(--color-accent-purple)]/10 via-[var(--color-bg-card)] to-[var(--color-accent-purple)]/10 border-2 border-[var(--color-accent-purple)]/40 rounded-2xl p-8 relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 bg-[var(--color-accent-purple)] text-white text-[10px] font-bold uppercase tracking-wider px-4 py-1.5 rounded-bl-xl">
                  All-Inclusive
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-[1fr_auto] gap-8 items-center">
                  <div>
                    <h3 className="text-2xl font-bold text-[var(--color-text-primary)] mb-1">
                      {plan.name}
                    </h3>
                    <p className="text-[var(--color-accent-purple-light)] text-sm font-medium mb-4">
                      {plan.target}
                    </p>
                    <p className="text-[var(--color-text-secondary)] text-sm mb-5 max-w-2xl">
                      Never worry about compliance again. We handle every filing, every deadline, every audit — so you can focus on building your business. Connects with your Zoho Books or Tally for financial sync.
                    </p>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-x-6 gap-y-2">
                      {plan.features.map((f, i) => (
                        <div key={i} className="flex items-start gap-2 text-xs text-[var(--color-text-secondary)]">
                          <span className="text-[var(--color-accent-purple-light)] mt-0.5 flex-shrink-0">&#10003;</span>
                          {f}
                        </div>
                      ))}
                    </div>
                    {plan.not_included_note && (
                      <p className="text-[var(--color-text-muted)] text-[11px] mt-3 italic">
                        {plan.not_included_note}
                      </p>
                    )}
                  </div>
                  <div className="text-center lg:text-right lg:min-w-[220px]">
                    <div className="mb-1">
                      <span className="text-4xl font-bold text-[var(--color-text-primary)]">
                        Rs {price.toLocaleString("en-IN")}
                      </span>
                      <span className="text-[var(--color-text-muted)] text-sm">
                        {subInterval === "annual" ? "/year" : "/month"}
                      </span>
                    </div>
                    {subInterval === "annual" && (
                      <p className="text-[var(--color-text-muted)] text-xs mb-1">
                        Rs {Math.round(price / 12).toLocaleString("en-IN")}/month effective
                      </p>
                    )}
                    <p className="text-[var(--color-success)] text-xs font-medium mb-4">
                      Save Rs {savings.toLocaleString("en-IN")}+ vs individual pricing
                    </p>
                    <button
                      onClick={() => handleSubscribe(plan)}
                      disabled={requesting === plan.key || isCurrentPlan || !!activeSubscription}
                      className={`w-full py-3 rounded-lg text-sm font-semibold transition ${
                        isCurrentPlan
                          ? "bg-[var(--color-success-light)] text-[var(--color-success)] cursor-not-allowed"
                          : activeSubscription
                            ? "bg-[var(--color-bg-secondary)] text-[var(--color-text-muted)] cursor-not-allowed"
                            : "bg-[var(--color-accent-purple)] text-white hover:bg-[var(--color-accent-purple-light)] shadow-lg shadow-[var(--color-accent-purple)]/20"
                      }`}
                    >
                      {requesting === plan.key
                        ? "..."
                        : isCurrentPlan
                          ? "Current Plan"
                          : activeSubscription
                            ? "Switch Plan"
                            : "Get Peace of Mind"}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}

          {/* Standard plans grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            {plans.filter(p => !p.is_peace_of_mind).map(plan => {
              const price = subInterval === "annual" ? plan.annual_price : plan.monthly_price;
              const isCurrentPlan = activeSubscription?.plan_key === plan.key;

              return (
                <div
                  key={plan.key}
                  className={`bg-[var(--color-bg-card)] border rounded-xl p-6 flex flex-col ${
                    plan.highlighted
                      ? "border-[var(--color-accent-purple)] ring-1 ring-[var(--color-accent-purple)]/20"
                      : "border-[var(--color-border)]"
                  }`}
                >
                  {plan.highlighted && (
                    <span className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-accent-purple)] mb-2">
                      Most Popular
                    </span>
                  )}
                  <h3 className="text-xl font-bold text-[var(--color-text-primary)]">{plan.name}</h3>
                  <p className="text-[var(--color-text-muted)] text-xs mt-1 mb-4">{plan.target}</p>
                  <div className="mb-4">
                    <span className="text-3xl font-bold text-[var(--color-text-primary)]">
                      Rs {price.toLocaleString("en-IN")}
                    </span>
                    <span className="text-[var(--color-text-muted)] text-sm">
                      {subInterval === "annual" ? "/year" : "/month"}
                    </span>
                    {subInterval === "annual" && (
                      <span className="block text-[var(--color-text-muted)] text-xs mt-1">
                        Rs {Math.round(price / 12).toLocaleString("en-IN")}/month effective
                      </span>
                    )}
                  </div>
                  <ul className="flex-1 space-y-2 mb-6">
                    {plan.features.map((f, i) => (
                      <li key={i} className="flex items-start gap-2 text-xs text-[var(--color-text-secondary)]">
                        <span className="text-[var(--color-success)] mt-0.5 flex-shrink-0">&#10003;</span>
                        {f}
                      </li>
                    ))}
                  </ul>
                  <button
                    onClick={() => handleSubscribe(plan)}
                    disabled={requesting === plan.key || isCurrentPlan || !!activeSubscription}
                    className={`w-full py-2.5 rounded-lg text-sm font-medium transition ${
                      isCurrentPlan
                        ? "bg-[var(--color-success-light)] text-[var(--color-success)] cursor-not-allowed"
                        : activeSubscription
                          ? "bg-[var(--color-bg-secondary)] text-[var(--color-text-muted)] cursor-not-allowed"
                          : plan.highlighted
                            ? "bg-[var(--color-accent-purple)] text-white hover:bg-[var(--color-accent-purple-light)]"
                            : "bg-[var(--color-bg-secondary)] text-[var(--color-text-primary)] hover:bg-[var(--color-bg-card-hover)] border border-[var(--color-border)]"
                    }`}
                  >
                    {requesting === plan.key
                      ? "..."
                      : isCurrentPlan
                        ? "Current Plan"
                        : activeSubscription
                          ? "Switch Plan"
                          : "Subscribe"}
                  </button>
                </div>
              );
            })}
          </div>

          {activeSubscription && (
            <div className="mt-6 bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl p-5">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-[var(--color-text-primary)]">
                    Active: {activeSubscription.plan_name} ({activeSubscription.interval})
                  </h3>
                  <p className="text-[var(--color-text-secondary)] text-sm">
                    Rs {activeSubscription.amount.toLocaleString("en-IN")}{activeSubscription.interval === "annual" ? "/year" : "/month"}
                    {activeSubscription.current_period_end && (
                      <> &middot; Renews {new Date(activeSubscription.current_period_end).toLocaleDateString("en-IN")}</>
                    )}
                  </p>
                </div>
                <span className="text-xs bg-[var(--color-success-light)] text-[var(--color-success)] px-3 py-1 rounded-full font-medium">
                  Active
                </span>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* ─── My Requests ─── */
        <div>
          <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mb-4">Your Service Requests</h2>
          {requests.length === 0 ? (
            <div className="text-center py-16 text-[var(--color-text-muted)]">
              <p className="text-lg mb-2">No service requests yet</p>
              <p className="text-sm">Browse the catalog to request your first service.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {requests.map(req => (
                <div
                  key={req.id}
                  className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl p-4 flex items-center justify-between"
                >
                  <div>
                    <h3 className="font-medium text-[var(--color-text-primary)] text-sm">{req.service_name}</h3>
                    <p className="text-[var(--color-text-muted)] text-xs mt-0.5">
                      {CATEGORY_LABELS[req.category] || req.category} &middot; Requested {new Date(req.created_at).toLocaleDateString("en-IN")}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-sm font-semibold text-[var(--color-text-primary)]">
                      Rs {req.total_amount.toLocaleString("en-IN")}
                    </span>
                    <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                      req.status === "completed" ? "bg-[var(--color-success-light)] text-[var(--color-success)]"
                      : req.status === "cancelled" ? "bg-[var(--color-error-light)] text-[var(--color-error)]"
                      : req.status === "in_progress" ? "bg-[var(--color-info-light)] text-[var(--color-info)]"
                      : "bg-[var(--color-warning-light)] text-[var(--color-warning)]"
                    }`}>
                      {req.status.replace(/_/g, " ")}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Subscriptions section */}
          {subscriptions.length > 0 && (
            <div className="mt-8">
              <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mb-4">Your Subscriptions</h2>
              <div className="space-y-3">
                {subscriptions.map(sub => (
                  <div
                    key={sub.id}
                    className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl p-4 flex items-center justify-between"
                  >
                    <div>
                      <h3 className="font-medium text-[var(--color-text-primary)] text-sm">
                        {sub.plan_name} Plan ({sub.interval})
                      </h3>
                      <p className="text-[var(--color-text-muted)] text-xs mt-0.5">
                        Started {new Date(sub.created_at).toLocaleDateString("en-IN")}
                        {sub.current_period_end && <> &middot; Renews {new Date(sub.current_period_end).toLocaleDateString("en-IN")}</>}
                      </p>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-sm font-semibold text-[var(--color-text-primary)]">
                        Rs {sub.amount.toLocaleString("en-IN")}/{sub.interval === "annual" ? "yr" : "mo"}
                      </span>
                      <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                        sub.status === "active" ? "bg-[var(--color-success-light)] text-[var(--color-success)]"
                        : sub.status === "cancelled" ? "bg-[var(--color-error-light)] text-[var(--color-error)]"
                        : "bg-[var(--color-warning-light)] text-[var(--color-warning)]"
                      }`}>
                        {sub.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
