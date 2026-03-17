"use client";

import { useState, useEffect } from "react";
import { useCompany } from "@/lib/company-context";
import Link from "next/link";

import {
  getESOPPlans,
  createESOPPlan,
  activateESOPPlan,
  getCompanyESOPGrants,
  createESOPGrant,
  exerciseESOPOptions,
  generateESOPGrantLetter,
  sendESOPGrantForSigning,
  getESOPSummary,
} from "@/lib/api";
import ESOPApprovalWizard from "./ESOPApprovalWizard";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";


interface ESOPPlan {
  id: number;
  company_id: number;
  plan_name: string;
  pool_size: number;
  pool_shares_allocated: number;
  pool_available: number;
  default_vesting_months: number;
  default_cliff_months: number;
  default_vesting_type: string;
  exercise_price: number;
  exercise_price_basis: string;
  effective_date: string | null;
  expiry_date: string | null;
  status: string;
  total_grants: number;
  active_grants: number;
  created_at: string;
  updated_at: string;
}

interface ESOPGrant {
  id: number;
  plan_id: number;
  company_id: number;
  grantee_name: string;
  grantee_email: string;
  grantee_employee_id: string | null;
  grantee_designation: string | null;
  grant_date: string;
  number_of_options: number;
  exercise_price: number;
  vesting_months: number;
  cliff_months: number;
  vesting_type: string;
  vesting_start_date: string;
  options_vested: number;
  options_exercised: number;
  options_unvested: number;
  options_exercisable: number;
  options_lapsed: number;
  status: string;
  grant_letter_document_id: number | null;
  vesting_schedule: {
    date: string;
    options_vesting: number;
    cumulative_vested: number;
    percentage_vested: number;
  }[];
  created_at: string;
  updated_at: string;
}

interface PoolSummary {
  total_pool: number;
  allocated: number;
  available: number;
  vested: number;
  unvested: number;
  exercised: number;
  lapsed: number;
  active_plans: number;
  active_grants: number;
}

const STATUS_COLORS: Record<string, { bg: string; text: string }> = {
  draft: { bg: "var(--color-text-muted)", text: "var(--color-text-muted)" },
  board_approved: { bg: "var(--color-info-light)", text: "var(--color-accent-blue)" },
  shareholder_approved: { bg: "rgba(99, 102, 241, 0.15)", text: "rgb(99, 102, 241)" },
  active: { bg: "var(--color-success-light)", text: "var(--color-accent-emerald-light)" },
  frozen: { bg: "var(--color-warning-light)", text: "var(--color-accent-amber)" },
  terminated: { bg: "var(--color-error-light)", text: "var(--color-accent-rose)" },
  offered: { bg: "var(--color-purple-bg)", text: "var(--color-accent-purple-light)" },
  accepted: { bg: "var(--color-info-light)", text: "var(--color-accent-blue)" },
  partially_exercised: { bg: "var(--color-warning-light)", text: "var(--color-accent-amber)" },
  fully_exercised: { bg: "var(--color-success-light)", text: "var(--color-accent-emerald-light)" },
  lapsed: { bg: "var(--color-error-light)", text: "var(--color-accent-rose)" },
  cancelled: { bg: "var(--color-error-light)", text: "var(--color-accent-rose)" },
};

function StatusBadge({ status }: { status: string }) {
  const colors = STATUS_COLORS[status] || STATUS_COLORS.draft;
  return (
    <span
      className="text-xs px-2 py-0.5 rounded-full capitalize"
      style={{ background: colors.bg, color: colors.text }}
    >
      {status.replace(/_/g, " ")}
    </span>
  );
}

function PoolDonut({ summary }: { summary: PoolSummary }) {
  const segments = [
    { label: "Available", value: summary.available, color: "rgb(16, 185, 129)" },
    { label: "Unvested", value: summary.unvested, color: "rgb(139, 92, 246)" },
    { label: "Vested (Unexercised)", value: Math.max(0, summary.vested - summary.exercised), color: "rgb(59, 130, 246)" },
    { label: "Exercised", value: summary.exercised, color: "rgb(245, 158, 11)" },
    { label: "Lapsed", value: summary.lapsed, color: "rgb(244, 63, 94)" },
  ].filter(s => s.value > 0);

  const total = summary.total_pool || 1;
  let cumulative = 0;
  const gradientParts = segments.map(s => {
    const start = cumulative;
    const pct = (s.value / total) * 100;
    cumulative += pct;
    return `${s.color} ${start}% ${cumulative}%`;
  });

  if (cumulative < 100) {
    gradientParts.push(`var(--color-hover-overlay) ${cumulative}% 100%`);
  }

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative">
        <div
          style={{
            width: "180px",
            height: "180px",
            borderRadius: "50%",
            background: `conic-gradient(${gradientParts.join(", ")})`,
            boxShadow: "0 0 30px var(--color-purple-bg)",
          }}
        />
        <div
          className="absolute inset-0 flex items-center justify-center"
          style={{ top: "30px", bottom: "30px", left: "30px", right: "30px" }}
        >
          <div
            className="w-full h-full rounded-full flex items-center justify-center"
            style={{ background: "var(--color-bg-card, rgba(17, 17, 27, 0.95))" }}
          >
            <div className="text-center">
              <div className="text-lg font-bold">{summary.total_pool.toLocaleString()}</div>
              <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Total Pool</div>
            </div>
          </div>
        </div>
      </div>
      <div className="flex flex-wrap gap-3 justify-center max-w-xs">
        {segments.map(s => (
          <div key={s.label} className="flex items-center gap-1.5 text-xs">
            <span className="inline-block w-2.5 h-2.5 rounded-sm" style={{ background: s.color }} />
            <span style={{ color: "var(--color-text-secondary)" }}>
              {s.label} ({s.value.toLocaleString()})
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ESOPPage() {
  const { companies, selectedCompany, selectCompany, loading: companyLoading } = useCompany();
  const [activeTab, setActiveTab] = useState<"plans" | "grants" | "pool" | "approval">("plans");
  const [approvalPlan, setApprovalPlan] = useState<ESOPPlan | null>(null);
  const [plans, setPlans] = useState<ESOPPlan[]>([]);
  const [grants, setGrants] = useState<ESOPGrant[]>([]);
  const [poolSummary, setPoolSummary] = useState<PoolSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  // Create plan modal
  const [showCreatePlan, setShowCreatePlan] = useState(false);
  const [planForm, setPlanForm] = useState({
    plan_name: "",
    pool_size: "",
    default_vesting_months: "48",
    default_cliff_months: "12",
    default_vesting_type: "monthly",
    exercise_price: "10",
    exercise_price_basis: "face_value",
    effective_date: "",
    expiry_date: "",
  });

  // Create grant modal
  const [showCreateGrant, setShowCreateGrant] = useState(false);
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null);
  const [grantForm, setGrantForm] = useState({
    grantee_name: "",
    grantee_email: "",
    grantee_employee_id: "",
    grantee_designation: "",
    grant_date: new Date().toISOString().split("T")[0],
    number_of_options: "",
    exercise_price: "",
    vesting_months: "",
    cliff_months: "",
    vesting_type: "",
    vesting_start_date: "",
  });

  // Exercise modal
  const [showExercise, setShowExercise] = useState(false);
  const [exerciseGrantId, setExerciseGrantId] = useState<number | null>(null);
  const [exerciseCount, setExerciseCount] = useState("");

  // Expanded grant (vesting timeline)
  const [expandedGrantId, setExpandedGrantId] = useState<number | null>(null);

  useEffect(() => {
    if (selectedCompany?.id) {
      fetchData();
    }
  }, [selectedCompany?.id]);

  async function fetchData() {
    setLoading(true);
    try {
      const [plansData, grantsData, summaryData] = await Promise.all([
        getESOPPlans(selectedCompany!.id).catch(() => []),
        getCompanyESOPGrants(selectedCompany!.id).catch(() => []),
        getESOPSummary(selectedCompany!.id).catch(() => null),
      ]);
      setPlans(plansData);
      setGrants(grantsData);
      setPoolSummary(summaryData);
    } catch {
      // Backend may not be running
    }
    setLoading(false);
  }

  async function handleCreatePlan(e: React.FormEvent) {
    e.preventDefault();
    setMessage("");
    try {
      await createESOPPlan(selectedCompany!.id, {
        ...planForm,
        pool_size: parseInt(planForm.pool_size),
        default_vesting_months: parseInt(planForm.default_vesting_months),
        default_cliff_months: parseInt(planForm.default_cliff_months),
        exercise_price: parseFloat(planForm.exercise_price),
        effective_date: planForm.effective_date || undefined,
        expiry_date: planForm.expiry_date || undefined,
      });
      setMessage("ESOP plan created successfully!");
      setShowCreatePlan(false);
      setPlanForm({
        plan_name: "",
        pool_size: "",
        default_vesting_months: "48",
        default_cliff_months: "12",
        default_vesting_type: "monthly",
        exercise_price: "10",
        exercise_price_basis: "face_value",
        effective_date: "",
        expiry_date: "",
      });
      fetchData();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleActivatePlan(planId: number) {
    setMessage("");
    try {
      await activateESOPPlan(selectedCompany!.id, planId);
      setMessage("Plan activated successfully!");
      fetchData();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleCreateGrant(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedPlanId) return;
    setMessage("");
    try {
      await createESOPGrant(selectedCompany!.id, selectedPlanId, {
        grantee_name: grantForm.grantee_name,
        grantee_email: grantForm.grantee_email,
        grantee_employee_id: grantForm.grantee_employee_id || undefined,
        grantee_designation: grantForm.grantee_designation || undefined,
        grant_date: grantForm.grant_date,
        number_of_options: parseInt(grantForm.number_of_options),
        exercise_price: grantForm.exercise_price ? parseFloat(grantForm.exercise_price) : undefined,
        vesting_months: grantForm.vesting_months ? parseInt(grantForm.vesting_months) : undefined,
        cliff_months: grantForm.cliff_months ? parseInt(grantForm.cliff_months) : undefined,
        vesting_type: grantForm.vesting_type || undefined,
        vesting_start_date: grantForm.vesting_start_date || undefined,
      });
      setMessage("Grant issued successfully!");
      setShowCreateGrant(false);
      setGrantForm({
        grantee_name: "",
        grantee_email: "",
        grantee_employee_id: "",
        grantee_designation: "",
        grant_date: new Date().toISOString().split("T")[0],
        number_of_options: "",
        exercise_price: "",
        vesting_months: "",
        cliff_months: "",
        vesting_type: "",
        vesting_start_date: "",
      });
      fetchData();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleExercise(e: React.FormEvent) {
    e.preventDefault();
    if (!exerciseGrantId) return;
    setMessage("");
    try {
      await exerciseESOPOptions(selectedCompany!.id, exerciseGrantId, {
        number_of_options: parseInt(exerciseCount),
      });
      setMessage("Options exercised successfully! Shares allotted to cap table.");
      setShowExercise(false);
      setExerciseCount("");
      fetchData();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleGenerateLetter(grantId: number) {
    setMessage("");
    try {
      await generateESOPGrantLetter(selectedCompany!.id, grantId);
      setMessage("Grant letter generated successfully!");
      fetchData();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleSendForSigning(grantId: number) {
    setMessage("");
    try {
      await sendESOPGrantForSigning(selectedCompany!.id, grantId);
      setMessage("Grant letter sent for signing!");
      fetchData();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  return (
    <div>
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="badge badge-purple mb-4 mx-auto w-fit">Employee Stock Options</div>
          <h1
            className="text-3xl md:text-4xl font-bold mb-3"
            style={{ fontFamily: "var(--font-display)" }}
          >
            <span className="gradient-text">ESOP Management</span>
          </h1>
          <p className="text-base" style={{ color: "var(--color-text-secondary)" }}>
            Create plans, issue grants, track vesting schedules, and exercise options.
          </p>
        </div>

        {/* Company selector */}
        {companies.length > 1 && (
          <div className="flex justify-center mb-6">
            <select
              className="glass-card text-sm px-3 py-2 rounded-lg border-none outline-none"
              style={{ background: "var(--color-bg-card)", color: "var(--color-text-primary)" }}
              value={selectedCompany?.id || ""}
              onChange={(e) => selectCompany(Number(e.target.value))}
            >
              {companies.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.approved_name || c.proposed_names?.[0] || `Company #${c.id}`}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* No company guard */}
        {!selectedCompany && !companyLoading && (
          <div className="glass-card p-12 text-center" style={{ cursor: "default" }}>
            <h2 className="text-xl font-bold mb-2" style={{ color: "var(--color-text-primary)" }}>No company selected</h2>
            <p className="text-sm mb-6" style={{ color: "var(--color-text-secondary)" }}>
              Select a company from the sidebar to view ESOP management.
            </p>
            <div className="flex items-center justify-center gap-3">
              <Link href="/pricing" className="px-5 py-2.5 rounded-lg text-sm font-semibold text-white" style={{ background: "var(--color-accent-purple-light)" }}>
                Incorporate a New Company
              </Link>
              <Link href="/dashboard/connect" className="px-5 py-2.5 rounded-lg text-sm font-semibold border" style={{ borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}>
                Connect Existing Company
              </Link>
            </div>
          </div>
        )}

        {companyLoading && (
          <div className="flex items-center justify-center py-24">
            <div className="animate-pulse-glow w-16 h-16 rounded-full flex items-center justify-center" style={{ background: "var(--color-purple-bg)" }}>
              <img src="/logo-icon.png" alt="Anvils" className="w-7 h-7 object-contain" />
            </div>
          </div>
        )}

        {selectedCompany && (
          <>
        {/* Message */}
        {message && (
          <div
            className="glass-card p-3 mb-6 text-center text-sm"
            style={{
              borderColor: message.startsWith("Error")
                ? "var(--color-accent-rose)"
                : "var(--color-accent-emerald-light)",
              cursor: "default",
            }}
          >
            {message}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-8 justify-center flex-wrap">
          {(["plans", "grants", "pool", "approval"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className="glass-card px-4 py-2 text-sm font-medium transition-all"
              style={{
                borderColor: activeTab === tab ? "var(--color-accent-purple-light)" : "var(--color-border)",
                background: activeTab === tab ? "var(--color-purple-bg)" : "transparent",
              }}
            >
              {tab === "plans" && "ESOP Plans"}
              {tab === "grants" && "Grants"}
              {tab === "pool" && "Pool Summary"}
              {tab === "approval" && "Approval Flow"}
            </button>
          ))}
        </div>

        {loading && (
          <div className="text-center py-12" style={{ color: "var(--color-text-muted)" }}>
            Loading ESOP data...
          </div>
        )}

        {/* ====== PLANS TAB ====== */}
        {activeTab === "plans" && !loading && (
          <div>
            <div className="flex justify-end mb-4">
              <button
                onClick={() => setShowCreatePlan(true)}
                className="btn-primary text-sm"
              >
                + Create Plan
              </button>
            </div>

            {plans.length === 0 ? (
              <div className="text-center py-16">
                <div className="text-4xl mb-4">&#128203;</div>
                <h3 className="text-lg font-semibold mb-2">No ESOP Plans Yet</h3>
                <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                  Create your first ESOP plan to start issuing stock options to employees.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {plans.map((plan) => {
                  const usagePct = plan.pool_size > 0
                    ? Math.round((plan.pool_shares_allocated / plan.pool_size) * 100)
                    : 0;
                  return (
                    <div key={plan.id} className="glass-card p-5" style={{ cursor: "default" }}>
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="font-semibold text-base">{plan.plan_name}</h3>
                          <p className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
                            Exercise Price: Rs {plan.exercise_price} ({plan.exercise_price_basis.replace(/_/g, " ")})
                          </p>
                        </div>
                        <StatusBadge status={plan.status} />
                      </div>

                      {/* Pool utilization bar */}
                      <div className="mb-3">
                        <div className="flex justify-between text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>
                          <span>Pool Utilization</span>
                          <span>{plan.pool_shares_allocated.toLocaleString()} / {plan.pool_size.toLocaleString()} ({usagePct}%)</span>
                        </div>
                        <div
                          className="w-full h-2 rounded-full overflow-hidden"
                          style={{ background: "var(--color-hover-overlay)" }}
                        >
                          <div
                            className="h-full rounded-full transition-all"
                            style={{
                              width: `${usagePct}%`,
                              background: usagePct > 90
                                ? "var(--color-accent-rose)"
                                : usagePct > 70
                                  ? "var(--color-accent-amber)"
                                  : "var(--color-accent-purple-light)",
                            }}
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-3 gap-3 text-center mb-4">
                        <div>
                          <div className="text-sm font-bold">{plan.pool_available.toLocaleString()}</div>
                          <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Available</div>
                        </div>
                        <div>
                          <div className="text-sm font-bold">{plan.total_grants}</div>
                          <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Total Grants</div>
                        </div>
                        <div>
                          <div className="text-sm font-bold">{plan.active_grants}</div>
                          <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Active Grants</div>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        {plan.status === "draft" && (
                          <>
                            <button
                              onClick={() => {
                                setApprovalPlan(plan);
                                setActiveTab("approval");
                              }}
                              className="text-xs px-3 py-1.5 rounded-lg transition-all"
                              style={{
                                background: "var(--color-purple-bg)",
                                border: "1px solid var(--color-purple-bg)",
                                color: "var(--color-accent-purple-light)",
                              }}
                            >
                              Start Approval Flow
                            </button>
                            <button
                              onClick={() => handleActivatePlan(plan.id)}
                              className="text-xs px-3 py-1.5 rounded-lg transition-all"
                              style={{
                                background: "var(--color-success-light)",
                                border: "1px solid var(--color-success-light)",
                                color: "var(--color-accent-emerald-light)",
                              }}
                            >
                              Activate Plan
                            </button>
                          </>
                        )}
                        {plan.status === "active" && (
                          <>
                            <button
                              onClick={() => {
                                setApprovalPlan(plan);
                                setActiveTab("approval");
                              }}
                              className="text-xs px-3 py-1.5 rounded-lg transition-all"
                              style={{
                                background: "var(--color-purple-bg)",
                                border: "1px solid var(--color-purple-bg)",
                                color: "var(--color-accent-purple-light)",
                              }}
                            >
                              View Approval Flow
                            </button>
                            <button
                              onClick={() => {
                                setSelectedPlanId(plan.id);
                                setShowCreateGrant(true);
                              }}
                              className="text-xs px-3 py-1.5 rounded-lg transition-all"
                              style={{
                                background: "var(--color-success-light)",
                                border: "1px solid var(--color-success-light)",
                                color: "var(--color-accent-emerald-light)",
                              }}
                            >
                              Issue Grant
                            </button>
                          </>
                        )}
                      </div>

                      <div className="mt-3 text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                        Vesting: {plan.default_vesting_months}mo, {plan.default_cliff_months}mo cliff, {plan.default_vesting_type}
                        {plan.effective_date && ` | Effective: ${new Date(plan.effective_date).toLocaleDateString()}`}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* ====== GRANTS TAB ====== */}
        {activeTab === "grants" && !loading && (
          <div>
            {grants.length === 0 ? (
              <div className="text-center py-16">
                <div className="text-4xl mb-4">&#128196;</div>
                <h3 className="text-lg font-semibold mb-2">No Grants Issued</h3>
                <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                  Create an active ESOP plan first, then issue grants to employees.
                </p>
              </div>
            ) : (
              <div className="glass-card overflow-hidden" style={{ cursor: "default" }}>
                <div className="p-4" style={{ borderBottom: "1px solid var(--color-border)" }}>
                  <h3 className="font-semibold">All Grants ({grants.length})</h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                        <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Grantee</th>
                        <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Options</th>
                        <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Vested</th>
                        <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Exercised</th>
                        <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Exercisable</th>
                        <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Status</th>
                        <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {grants.map((grant) => (
                        <>
                          <tr
                            key={grant.id}
                            style={{ borderBottom: "1px solid var(--color-border)", cursor: "pointer" }}
                            onClick={() => setExpandedGrantId(expandedGrantId === grant.id ? null : grant.id)}
                          >
                            <td className="p-3">
                              <div className="font-medium">{grant.grantee_name}</div>
                              <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                                {grant.grantee_designation || grant.grantee_email}
                              </div>
                            </td>
                            <td className="p-3 text-center font-mono">{grant.number_of_options.toLocaleString()}</td>
                            <td className="p-3 text-center font-mono">{grant.options_vested.toLocaleString()}</td>
                            <td className="p-3 text-center font-mono">{grant.options_exercised.toLocaleString()}</td>
                            <td className="p-3 text-center font-mono font-bold" style={{
                              color: grant.options_exercisable > 0 ? "var(--color-accent-emerald-light)" : "var(--color-text-muted)",
                            }}>
                              {grant.options_exercisable.toLocaleString()}
                            </td>
                            <td className="p-3 text-center">
                              <StatusBadge status={grant.status} />
                            </td>
                            <td className="p-3 text-right">
                              <div className="flex gap-1 justify-end" onClick={(e) => e.stopPropagation()}>
                                {grant.options_exercisable > 0 && (
                                  <button
                                    onClick={() => {
                                      setExerciseGrantId(grant.id);
                                      setShowExercise(true);
                                    }}
                                    className="text-[11px] px-2 py-1 rounded"
                                    style={{ background: "var(--color-success-light)", color: "var(--color-accent-emerald-light)" }}
                                  >
                                    Exercise
                                  </button>
                                )}
                                {!grant.grant_letter_document_id && (
                                  <button
                                    onClick={() => handleGenerateLetter(grant.id)}
                                    className="text-[11px] px-2 py-1 rounded"
                                    style={{ background: "var(--color-purple-bg)", color: "var(--color-accent-purple-light)" }}
                                  >
                                    Gen Letter
                                  </button>
                                )}
                                {grant.grant_letter_document_id && grant.status === "draft" && (
                                  <button
                                    onClick={() => handleSendForSigning(grant.id)}
                                    className="text-[11px] px-2 py-1 rounded"
                                    style={{ background: "var(--color-info-light)", color: "var(--color-accent-blue)" }}
                                  >
                                    Send for Sign
                                  </button>
                                )}
                              </div>
                            </td>
                          </tr>

                          {/* Expanded vesting timeline */}
                          {expandedGrantId === grant.id && (
                            <tr key={`${grant.id}-vest`}>
                              <td colSpan={7} className="p-0">
                                <div
                                  className="px-6 py-4"
                                  style={{ background: "var(--color-hover-overlay)" }}
                                >
                                  <div className="flex items-center gap-3 mb-3">
                                    <h4 className="text-sm font-semibold">Vesting Schedule</h4>
                                    <span className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                                      {grant.vesting_months}mo vesting, {grant.cliff_months}mo cliff, {grant.vesting_type}
                                    </span>
                                  </div>

                                  {/* Vesting progress bar */}
                                  <div className="mb-4">
                                    <div className="flex justify-between text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>
                                      <span>Vesting Progress</span>
                                      <span>{grant.options_vested} / {grant.number_of_options} ({Math.round((grant.options_vested / grant.number_of_options) * 100)}%)</span>
                                    </div>
                                    <div className="w-full h-3 rounded-full overflow-hidden flex" style={{ background: "var(--color-hover-overlay)" }}>
                                      {/* Exercised portion */}
                                      {grant.options_exercised > 0 && (
                                        <div
                                          className="h-full"
                                          style={{
                                            width: `${(grant.options_exercised / grant.number_of_options) * 100}%`,
                                            background: "var(--color-accent-amber)",
                                          }}
                                        />
                                      )}
                                      {/* Vested but not exercised */}
                                      {grant.options_exercisable > 0 && (
                                        <div
                                          className="h-full"
                                          style={{
                                            width: `${(grant.options_exercisable / grant.number_of_options) * 100}%`,
                                            background: "var(--color-accent-emerald-light)",
                                          }}
                                        />
                                      )}
                                      {/* Unvested */}
                                      {grant.options_unvested > 0 && (
                                        <div
                                          className="h-full"
                                          style={{
                                            width: `${(grant.options_unvested / grant.number_of_options) * 100}%`,
                                            background: "var(--color-purple-bg)",
                                          }}
                                        />
                                      )}
                                    </div>
                                    <div className="flex gap-4 mt-1">
                                      {grant.options_exercised > 0 && (
                                        <span className="flex items-center gap-1 text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                                          <span className="w-2 h-2 rounded-sm" style={{ background: "var(--color-accent-amber)" }} /> Exercised
                                        </span>
                                      )}
                                      <span className="flex items-center gap-1 text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                                        <span className="w-2 h-2 rounded-sm" style={{ background: "var(--color-accent-emerald-light)" }} /> Exercisable
                                      </span>
                                      <span className="flex items-center gap-1 text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                                        <span className="w-2 h-2 rounded-sm" style={{ background: "var(--color-purple-bg)" }} /> Unvested
                                      </span>
                                    </div>
                                  </div>

                                  {/* Vesting Schedule Area Chart */}
                                  {grant.vesting_schedule.length >= 2 && (() => {
                                    const chartData = grant.vesting_schedule.map((entry) => {
                                      const d = new Date(entry.date);
                                      const label = d.toLocaleDateString("en-US", { month: "short", year: "2-digit" });
                                      return {
                                        date: label,
                                        fullDate: d.toLocaleDateString(),
                                        options_vesting: entry.options_vesting,
                                        cumulative_vested: entry.cumulative_vested,
                                      };
                                    });
                                    // Cliff date = first entry where options_vesting > 0
                                    const cliffEntry = chartData.find((d) => d.options_vesting > 0);
                                    const cliffDate = cliffEntry?.date;
                                    return (
                                      <div
                                        className="glass-card p-4 mb-4"
                                        style={{ cursor: "default" }}
                                      >
                                        <h5
                                          className="text-xs font-semibold mb-3"
                                          style={{ color: "#9CA3AF" }}
                                        >
                                          Vesting Timeline
                                        </h5>
                                        <ResponsiveContainer width="100%" height={220}>
                                          <AreaChart
                                            data={chartData}
                                            margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
                                          >
                                            <defs>
                                              <linearGradient id={`purpleGradient-${grant.id}`} x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="0%" stopColor="#8B5CF6" stopOpacity={0.4} />
                                                <stop offset="100%" stopColor="#8B5CF6" stopOpacity={0.05} />
                                              </linearGradient>
                                            </defs>
                                            <CartesianGrid
                                              strokeDasharray="3 3"
                                              stroke="#374151"
                                              vertical={false}
                                            />
                                            <XAxis
                                              dataKey="date"
                                              tick={{ fill: "#9CA3AF", fontSize: 11 }}
                                              axisLine={{ stroke: "#374151" }}
                                              tickLine={{ stroke: "#374151" }}
                                            />
                                            <YAxis
                                              tick={{ fill: "#9CA3AF", fontSize: 11 }}
                                              axisLine={{ stroke: "#374151" }}
                                              tickLine={{ stroke: "#374151" }}
                                              tickFormatter={(v: number) =>
                                                v >= 1000 ? `${(v / 1000).toFixed(0)}k` : String(v)
                                              }
                                            />
                                            <Tooltip
                                              contentStyle={{
                                                background: "#1a1a2e",
                                                border: "1px solid rgba(255,255,255,0.1)",
                                                borderRadius: 8,
                                              }}
                                              labelStyle={{ color: "#9CA3AF" }}
                                              // eslint-disable-next-line @typescript-eslint/no-explicit-any
                                              formatter={(value: any, name: any) => {
                                                const displayLabel =
                                                  name === "cumulative_vested"
                                                    ? "Cumulative Vested"
                                                    : name;
                                                return [Number(value).toLocaleString(), displayLabel];
                                              }}
                                              labelFormatter={(label) => `Date: ${label}`}
                                              itemStyle={{ color: "#8B5CF6" }}
                                            />
                                            {cliffDate && (
                                              <ReferenceLine
                                                x={cliffDate}
                                                stroke="#10B981"
                                                strokeDasharray="4 4"
                                                label={{
                                                  value: "Cliff",
                                                  position: "top",
                                                  fill: "#10B981",
                                                  fontSize: 11,
                                                }}
                                              />
                                            )}
                                            <Area
                                              type="monotone"
                                              dataKey="cumulative_vested"
                                              stroke="#8B5CF6"
                                              strokeWidth={2}
                                              fill={`url(#purpleGradient-${grant.id})`}
                                              dot={false}
                                              activeDot={{
                                                r: 4,
                                                stroke: "#8B5CF6",
                                                strokeWidth: 2,
                                                fill: "#1a1a2e",
                                              }}
                                            />
                                          </AreaChart>
                                        </ResponsiveContainer>
                                      </div>
                                    );
                                  })()}

                                  {/* Schedule table */}
                                  {grant.vesting_schedule.length > 0 && (
                                    <div className="overflow-x-auto">
                                      <table className="w-full text-xs">
                                        <thead>
                                          <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                                            <th className="text-left p-2" style={{ color: "var(--color-text-muted)" }}>Date</th>
                                            <th className="text-right p-2" style={{ color: "var(--color-text-muted)" }}>Vesting</th>
                                            <th className="text-right p-2" style={{ color: "var(--color-text-muted)" }}>Cumulative</th>
                                            <th className="text-right p-2" style={{ color: "var(--color-text-muted)" }}>%</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {grant.vesting_schedule.map((entry, idx) => {
                                            const isPast = new Date(entry.date) <= new Date();
                                            return (
                                              <tr
                                                key={idx}
                                                style={{
                                                  borderBottom: "1px solid var(--color-border)",
                                                  opacity: isPast ? 1 : 0.5,
                                                }}
                                              >
                                                <td className="p-2">
                                                  {new Date(entry.date).toLocaleDateString()}
                                                  {isPast && (
                                                    <span className="ml-1" style={{ color: "var(--color-accent-emerald-light)" }}>&#10003;</span>
                                                  )}
                                                </td>
                                                <td className="p-2 text-right font-mono">{entry.options_vesting.toLocaleString()}</td>
                                                <td className="p-2 text-right font-mono">{entry.cumulative_vested.toLocaleString()}</td>
                                                <td className="p-2 text-right font-mono">{entry.percentage_vested}%</td>
                                              </tr>
                                            );
                                          })}
                                        </tbody>
                                      </table>
                                    </div>
                                  )}
                                </div>
                              </td>
                            </tr>
                          )}
                        </>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ====== POOL SUMMARY TAB ====== */}
        {activeTab === "pool" && !loading && (
          <div>
            {!poolSummary || poolSummary.total_pool === 0 ? (
              <div className="text-center py-16">
                <div className="text-4xl mb-4">&#128200;</div>
                <h3 className="text-lg font-semibold mb-2">No ESOP Pool Data</h3>
                <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                  Create and activate an ESOP plan to see pool statistics.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Donut chart */}
                <div className="glass-card p-8" style={{ cursor: "default" }}>
                  <h3 className="text-center font-semibold mb-6">Pool Distribution</h3>
                  <PoolDonut summary={poolSummary} />
                </div>

                {/* Stats */}
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="glass-card p-4 text-center" style={{ cursor: "default" }}>
                      <div className="text-2xl font-bold">{poolSummary.total_pool.toLocaleString()}</div>
                      <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Total Pool</div>
                    </div>
                    <div className="glass-card p-4 text-center" style={{ cursor: "default" }}>
                      <div className="text-2xl font-bold" style={{ color: "var(--color-accent-emerald-light)" }}>
                        {poolSummary.available.toLocaleString()}
                      </div>
                      <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Available</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3">
                    <div className="glass-card p-3 text-center" style={{ cursor: "default" }}>
                      <div className="text-lg font-bold">{poolSummary.allocated.toLocaleString()}</div>
                      <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Allocated</div>
                    </div>
                    <div className="glass-card p-3 text-center" style={{ cursor: "default" }}>
                      <div className="text-lg font-bold">{poolSummary.vested.toLocaleString()}</div>
                      <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Vested</div>
                    </div>
                    <div className="glass-card p-3 text-center" style={{ cursor: "default" }}>
                      <div className="text-lg font-bold">{poolSummary.unvested.toLocaleString()}</div>
                      <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Unvested</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="glass-card p-3 text-center" style={{ cursor: "default" }}>
                      <div className="text-lg font-bold" style={{ color: "var(--color-accent-amber)" }}>
                        {poolSummary.exercised.toLocaleString()}
                      </div>
                      <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Exercised</div>
                    </div>
                    <div className="glass-card p-3 text-center" style={{ cursor: "default" }}>
                      <div className="text-lg font-bold" style={{ color: "var(--color-accent-rose)" }}>
                        {poolSummary.lapsed.toLocaleString()}
                      </div>
                      <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Lapsed</div>
                    </div>
                  </div>

                  <div className="glass-card p-4" style={{ cursor: "default" }}>
                    <div className="flex justify-between text-sm">
                      <span style={{ color: "var(--color-text-muted)" }}>Active Plans</span>
                      <span className="font-bold">{poolSummary.active_plans}</span>
                    </div>
                    <div className="flex justify-between text-sm mt-1">
                      <span style={{ color: "var(--color-text-muted)" }}>Active Grants</span>
                      <span className="font-bold">{poolSummary.active_grants}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ====== APPROVAL FLOW TAB ====== */}
        {activeTab === "approval" && !loading && (
          <div>
            {approvalPlan ? (
              <ESOPApprovalWizard
                companyId={selectedCompany!.id}
                plan={approvalPlan}
                onComplete={() => {
                  fetchData();
                }}
                onClose={() => {
                  setApprovalPlan(null);
                  setActiveTab("plans");
                }}
              />
            ) : (
              <div className="text-center py-16">
                <div className="text-4xl mb-4">&#128203;</div>
                <h3 className="text-lg font-semibold mb-2" style={{ color: "var(--color-text-primary)" }}>
                  Select a Plan
                </h3>
                <p className="text-sm mb-6" style={{ color: "var(--color-text-muted)" }}>
                  Go to the ESOP Plans tab and click &quot;Start Approval Flow&quot; on a draft plan
                  to begin the compliance workflow.
                </p>

                {/* Show draft plans as quick-select cards */}
                {plans.filter(p => p.status === "draft" || p.status === "active").length > 0 && (
                  <div className="max-w-md mx-auto space-y-2">
                    <p className="text-xs font-medium mb-3" style={{ color: "var(--color-text-muted)" }}>
                      Or select a plan below:
                    </p>
                    {plans
                      .filter(p => p.status === "draft" || p.status === "active")
                      .map((p) => (
                        <button
                          key={p.id}
                          onClick={() => setApprovalPlan(p)}
                          className="glass-card p-3 w-full text-left transition-all hover:border-purple-500"
                          style={{ borderColor: "var(--color-border)" }}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <span className="text-sm font-semibold">{p.plan_name}</span>
                              <span className="text-xs ml-2" style={{ color: "var(--color-text-muted)" }}>
                                {p.pool_size.toLocaleString()} options
                              </span>
                            </div>
                            <span
                              className="text-xs px-2 py-0.5 rounded-full capitalize"
                              style={{
                                background: p.status === "active" ? "var(--color-success-light)" : "var(--color-text-muted)",
                                color: p.status === "active" ? "var(--color-accent-emerald-light)" : "var(--color-text-muted)",
                              }}
                            >
                              {p.status}
                            </span>
                          </div>
                        </button>
                      ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
          </>
        )}
      </div>

      {/* ====== MODALS ====== */}

      {/* Create Plan Modal */}
      {showCreatePlan && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "var(--color-overlay)" }}>
          <div
            className="glass-card p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto"
            style={{ cursor: "default", background: "var(--color-bg-card)" }}
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Create ESOP Plan</h3>
              <button onClick={() => setShowCreatePlan(false)} className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                Close
              </button>
            </div>
            <form onSubmit={handleCreatePlan} className="space-y-4">
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Plan Name *</label>
                <input
                  type="text"
                  required
                  value={planForm.plan_name}
                  onChange={(e) => setPlanForm({ ...planForm, plan_name: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  placeholder="e.g., ESOP Plan 2024"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Pool Size (options) *</label>
                  <input
                    type="number"
                    required
                    min={1}
                    value={planForm.pool_size}
                    onChange={(e) => setPlanForm({ ...planForm, pool_size: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="100000"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Exercise Price (Rs)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={planForm.exercise_price}
                    onChange={(e) => setPlanForm({ ...planForm, exercise_price: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Vesting (months)</label>
                  <input
                    type="number"
                    value={planForm.default_vesting_months}
                    onChange={(e) => setPlanForm({ ...planForm, default_vesting_months: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Cliff (months)</label>
                  <input
                    type="number"
                    value={planForm.default_cliff_months}
                    onChange={(e) => setPlanForm({ ...planForm, default_cliff_months: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Vesting Type</label>
                  <select
                    value={planForm.default_vesting_type}
                    onChange={(e) => setPlanForm({ ...planForm, default_vesting_type: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  >
                    <option value="monthly">Monthly</option>
                    <option value="quarterly">Quarterly</option>
                    <option value="annually">Annually</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Effective Date</label>
                  <input
                    type="date"
                    value={planForm.effective_date}
                    onChange={(e) => setPlanForm({ ...planForm, effective_date: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Expiry Date</label>
                  <input
                    type="date"
                    value={planForm.expiry_date}
                    onChange={(e) => setPlanForm({ ...planForm, expiry_date: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Price Basis</label>
                <select
                  value={planForm.exercise_price_basis}
                  onChange={(e) => setPlanForm({ ...planForm, exercise_price_basis: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                >
                  <option value="face_value">Face Value</option>
                  <option value="fmv">Fair Market Value</option>
                  <option value="custom">Custom</option>
                </select>
              </div>
              <button type="submit" className="btn-primary w-full text-center justify-center">
                Create Plan
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Create Grant Modal */}
      {showCreateGrant && selectedPlanId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "var(--color-overlay)" }}>
          <div
            className="glass-card p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto"
            style={{ cursor: "default", background: "var(--color-bg-card)" }}
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Issue Grant</h3>
              <button onClick={() => setShowCreateGrant(false)} className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                Close
              </button>
            </div>
            <form onSubmit={handleCreateGrant} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Grantee Name *</label>
                  <input
                    type="text"
                    required
                    value={grantForm.grantee_name}
                    onChange={(e) => setGrantForm({ ...grantForm, grantee_name: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="Employee Name"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Email *</label>
                  <input
                    type="email"
                    required
                    value={grantForm.grantee_email}
                    onChange={(e) => setGrantForm({ ...grantForm, grantee_email: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="employee@company.com"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Employee ID</label>
                  <input
                    type="text"
                    value={grantForm.grantee_employee_id}
                    onChange={(e) => setGrantForm({ ...grantForm, grantee_employee_id: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="EMP001"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Designation</label>
                  <input
                    type="text"
                    value={grantForm.grantee_designation}
                    onChange={(e) => setGrantForm({ ...grantForm, grantee_designation: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="Software Engineer"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Grant Date *</label>
                  <input
                    type="date"
                    required
                    value={grantForm.grant_date}
                    onChange={(e) => setGrantForm({ ...grantForm, grant_date: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Number of Options *</label>
                  <input
                    type="number"
                    required
                    min={1}
                    value={grantForm.number_of_options}
                    onChange={(e) => setGrantForm({ ...grantForm, number_of_options: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="10000"
                  />
                </div>
              </div>
              <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                Leave fields below blank to use plan defaults.
              </p>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Exercise Price</label>
                  <input
                    type="number"
                    step="0.01"
                    value={grantForm.exercise_price}
                    onChange={(e) => setGrantForm({ ...grantForm, exercise_price: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="Plan default"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Vesting (mo)</label>
                  <input
                    type="number"
                    value={grantForm.vesting_months}
                    onChange={(e) => setGrantForm({ ...grantForm, vesting_months: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="Plan default"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Cliff (mo)</label>
                  <input
                    type="number"
                    value={grantForm.cliff_months}
                    onChange={(e) => setGrantForm({ ...grantForm, cliff_months: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="Plan default"
                  />
                </div>
              </div>
              <button type="submit" className="btn-primary w-full text-center justify-center">
                Issue Grant
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Exercise Modal */}
      {showExercise && exerciseGrantId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "var(--color-overlay)" }}>
          <div
            className="glass-card p-6 w-full max-w-sm"
            style={{ cursor: "default", background: "var(--color-bg-card)" }}
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Exercise Options</h3>
              <button onClick={() => setShowExercise(false)} className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                Close
              </button>
            </div>
            {(() => {
              const grant = grants.find(g => g.id === exerciseGrantId);
              if (!grant) return null;
              return (
                <div className="mb-4 text-sm space-y-1" style={{ color: "var(--color-text-secondary)" }}>
                  <div>Grantee: <strong>{grant.grantee_name}</strong></div>
                  <div>Exercisable: <strong>{grant.options_exercisable.toLocaleString()}</strong> options</div>
                  <div>Exercise Price: <strong>Rs {grant.exercise_price}</strong> / option</div>
                </div>
              );
            })()}
            <form onSubmit={handleExercise} className="space-y-4">
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Options to Exercise *</label>
                <input
                  type="number"
                  required
                  min={1}
                  value={exerciseCount}
                  onChange={(e) => setExerciseCount(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  placeholder="Number of options"
                />
              </div>
              {exerciseCount && (() => {
                const grant = grants.find(g => g.id === exerciseGrantId);
                if (!grant) return null;
                const totalCost = parseInt(exerciseCount) * grant.exercise_price;
                return (
                  <div className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                    Total cost: <strong>Rs {totalCost.toLocaleString()}</strong>
                  </div>
                );
              })()}
              <button type="submit" className="btn-primary w-full text-center justify-center">
                Exercise Options
              </button>
              <p className="text-[10px] text-center" style={{ color: "var(--color-text-muted)" }}>
                Exercising will allot shares via the cap table and generate PAS-3 data.
              </p>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
