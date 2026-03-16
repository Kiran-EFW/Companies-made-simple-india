"use client";

import { useState, useEffect } from "react";
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
import Footer from "@/components/footer";

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
  draft: { bg: "rgba(156, 163, 175, 0.15)", text: "rgb(156, 163, 175)" },
  board_approved: { bg: "rgba(59, 130, 246, 0.15)", text: "rgb(59, 130, 246)" },
  shareholder_approved: { bg: "rgba(99, 102, 241, 0.15)", text: "rgb(99, 102, 241)" },
  active: { bg: "rgba(16, 185, 129, 0.15)", text: "rgb(16, 185, 129)" },
  frozen: { bg: "rgba(245, 158, 11, 0.15)", text: "rgb(245, 158, 11)" },
  terminated: { bg: "rgba(244, 63, 94, 0.15)", text: "rgb(244, 63, 94)" },
  offered: { bg: "rgba(139, 92, 246, 0.15)", text: "rgb(139, 92, 246)" },
  accepted: { bg: "rgba(59, 130, 246, 0.15)", text: "rgb(59, 130, 246)" },
  partially_exercised: { bg: "rgba(245, 158, 11, 0.15)", text: "rgb(245, 158, 11)" },
  fully_exercised: { bg: "rgba(16, 185, 129, 0.15)", text: "rgb(16, 185, 129)" },
  lapsed: { bg: "rgba(244, 63, 94, 0.15)", text: "rgb(244, 63, 94)" },
  cancelled: { bg: "rgba(244, 63, 94, 0.15)", text: "rgb(244, 63, 94)" },
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
    gradientParts.push(`rgba(255,255,255,0.05) ${cumulative}% 100%`);
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
            boxShadow: "0 0 30px rgba(139, 92, 246, 0.2)",
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
  const [companyId, setCompanyId] = useState<number>(1);
  const [activeTab, setActiveTab] = useState<"plans" | "grants" | "pool">("plans");
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
    fetchData();
  }, [companyId]);

  async function fetchData() {
    setLoading(true);
    try {
      const [plansData, grantsData, summaryData] = await Promise.all([
        getESOPPlans(companyId).catch(() => []),
        getCompanyESOPGrants(companyId).catch(() => []),
        getESOPSummary(companyId).catch(() => null),
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
      await createESOPPlan(companyId, {
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
      await activateESOPPlan(companyId, planId);
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
      await createESOPGrant(companyId, selectedPlanId, {
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
      await exerciseESOPOptions(companyId, exerciseGrantId, {
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
      await generateESOPGrantLetter(companyId, grantId);
      setMessage("Grant letter generated successfully!");
      fetchData();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleSendForSigning(grantId: number) {
    setMessage("");
    try {
      await sendESOPGrantForSigning(companyId, grantId);
      setMessage("Grant letter sent for signing!");
      fetchData();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  return (
    <div className="glow-bg min-h-screen">
      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-5 max-w-7xl mx-auto">
        <Link href="/" className="flex items-center gap-2.5">
          <img src="/logo-icon.png" alt="Anvils" className="w-6 h-6 object-contain" />
          <span className="text-xl font-bold gradient-text" style={{ fontFamily: "var(--font-display)" }}>Anvils</span>
        </Link>
        <div className="flex gap-3">
          <Link href="/dashboard" className="btn-secondary text-sm !py-2 !px-5">Dashboard</Link>
          <Link href="/dashboard/cap-table" className="btn-secondary text-sm !py-2 !px-5">Cap Table</Link>
        </div>
      </nav>

      <div className="relative z-10 max-w-6xl mx-auto px-6 py-8">
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
        <div className="flex justify-center mb-6">
          <div className="flex items-center gap-3">
            <label className="text-sm" style={{ color: "var(--color-text-muted)" }}>Company ID:</label>
            <input
              type="number"
              value={companyId}
              onChange={(e) => setCompanyId(parseInt(e.target.value) || 1)}
              className="glass-card px-3 py-1.5 text-sm w-20 text-center"
              style={{
                background: "var(--color-bg-card)",
                border: "1px solid var(--color-border)",
                color: "var(--color-text-primary)",
                cursor: "text",
              }}
              min={1}
            />
          </div>
        </div>

        {/* Message */}
        {message && (
          <div
            className="glass-card p-3 mb-6 text-center text-sm"
            style={{
              borderColor: message.startsWith("Error")
                ? "rgba(244, 63, 94, 0.5)"
                : "rgba(16, 185, 129, 0.5)",
              cursor: "default",
            }}
          >
            {message}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-8 justify-center flex-wrap">
          {(["plans", "grants", "pool"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className="glass-card px-4 py-2 text-sm font-medium transition-all"
              style={{
                borderColor: activeTab === tab ? "rgba(139, 92, 246, 0.6)" : "var(--color-border)",
                background: activeTab === tab ? "rgba(139, 92, 246, 0.15)" : "transparent",
              }}
            >
              {tab === "plans" && "ESOP Plans"}
              {tab === "grants" && "Grants"}
              {tab === "pool" && "Pool Summary"}
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
                          style={{ background: "rgba(255,255,255,0.05)" }}
                        >
                          <div
                            className="h-full rounded-full transition-all"
                            style={{
                              width: `${usagePct}%`,
                              background: usagePct > 90
                                ? "rgb(244, 63, 94)"
                                : usagePct > 70
                                  ? "rgb(245, 158, 11)"
                                  : "rgb(139, 92, 246)",
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
                          <button
                            onClick={() => handleActivatePlan(plan.id)}
                            className="text-xs px-3 py-1.5 rounded-lg transition-all"
                            style={{
                              background: "rgba(16, 185, 129, 0.1)",
                              border: "1px solid rgba(16, 185, 129, 0.3)",
                              color: "rgb(16, 185, 129)",
                            }}
                          >
                            Activate Plan
                          </button>
                        )}
                        {plan.status === "active" && (
                          <button
                            onClick={() => {
                              setSelectedPlanId(plan.id);
                              setShowCreateGrant(true);
                            }}
                            className="text-xs px-3 py-1.5 rounded-lg transition-all"
                            style={{
                              background: "rgba(139, 92, 246, 0.1)",
                              border: "1px solid rgba(139, 92, 246, 0.3)",
                              color: "rgb(139, 92, 246)",
                            }}
                          >
                            Issue Grant
                          </button>
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
                              color: grant.options_exercisable > 0 ? "rgb(16, 185, 129)" : "var(--color-text-muted)",
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
                                    style={{ background: "rgba(16, 185, 129, 0.1)", color: "rgb(16, 185, 129)" }}
                                  >
                                    Exercise
                                  </button>
                                )}
                                {!grant.grant_letter_document_id && (
                                  <button
                                    onClick={() => handleGenerateLetter(grant.id)}
                                    className="text-[11px] px-2 py-1 rounded"
                                    style={{ background: "rgba(139, 92, 246, 0.1)", color: "rgb(139, 92, 246)" }}
                                  >
                                    Gen Letter
                                  </button>
                                )}
                                {grant.grant_letter_document_id && grant.status === "draft" && (
                                  <button
                                    onClick={() => handleSendForSigning(grant.id)}
                                    className="text-[11px] px-2 py-1 rounded"
                                    style={{ background: "rgba(59, 130, 246, 0.1)", color: "rgb(59, 130, 246)" }}
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
                                  style={{ background: "rgba(139, 92, 246, 0.03)" }}
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
                                    <div className="w-full h-3 rounded-full overflow-hidden flex" style={{ background: "rgba(255,255,255,0.05)" }}>
                                      {/* Exercised portion */}
                                      {grant.options_exercised > 0 && (
                                        <div
                                          className="h-full"
                                          style={{
                                            width: `${(grant.options_exercised / grant.number_of_options) * 100}%`,
                                            background: "rgb(245, 158, 11)",
                                          }}
                                        />
                                      )}
                                      {/* Vested but not exercised */}
                                      {grant.options_exercisable > 0 && (
                                        <div
                                          className="h-full"
                                          style={{
                                            width: `${(grant.options_exercisable / grant.number_of_options) * 100}%`,
                                            background: "rgb(16, 185, 129)",
                                          }}
                                        />
                                      )}
                                      {/* Unvested */}
                                      {grant.options_unvested > 0 && (
                                        <div
                                          className="h-full"
                                          style={{
                                            width: `${(grant.options_unvested / grant.number_of_options) * 100}%`,
                                            background: "rgba(139, 92, 246, 0.3)",
                                          }}
                                        />
                                      )}
                                    </div>
                                    <div className="flex gap-4 mt-1">
                                      {grant.options_exercised > 0 && (
                                        <span className="flex items-center gap-1 text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                                          <span className="w-2 h-2 rounded-sm" style={{ background: "rgb(245, 158, 11)" }} /> Exercised
                                        </span>
                                      )}
                                      <span className="flex items-center gap-1 text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                                        <span className="w-2 h-2 rounded-sm" style={{ background: "rgb(16, 185, 129)" }} /> Exercisable
                                      </span>
                                      <span className="flex items-center gap-1 text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                                        <span className="w-2 h-2 rounded-sm" style={{ background: "rgba(139, 92, 246, 0.3)" }} /> Unvested
                                      </span>
                                    </div>
                                  </div>

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
                                                    <span className="ml-1" style={{ color: "rgb(16, 185, 129)" }}>&#10003;</span>
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
                      <div className="text-2xl font-bold" style={{ color: "rgb(16, 185, 129)" }}>
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
                      <div className="text-lg font-bold" style={{ color: "rgb(245, 158, 11)" }}>
                        {poolSummary.exercised.toLocaleString()}
                      </div>
                      <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Exercised</div>
                    </div>
                    <div className="glass-card p-3 text-center" style={{ cursor: "default" }}>
                      <div className="text-lg font-bold" style={{ color: "rgb(244, 63, 94)" }}>
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
      </div>

      {/* ====== MODALS ====== */}

      {/* Create Plan Modal */}
      {showCreatePlan && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "rgba(0,0,0,0.6)" }}>
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
                  style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
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
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
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
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
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
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Cliff (months)</label>
                  <input
                    type="number"
                    value={planForm.default_cliff_months}
                    onChange={(e) => setPlanForm({ ...planForm, default_cliff_months: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Vesting Type</label>
                  <select
                    value={planForm.default_vesting_type}
                    onChange={(e) => setPlanForm({ ...planForm, default_vesting_type: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
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
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Expiry Date</label>
                  <input
                    type="date"
                    value={planForm.expiry_date}
                    onChange={(e) => setPlanForm({ ...planForm, expiry_date: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Price Basis</label>
                <select
                  value={planForm.exercise_price_basis}
                  onChange={(e) => setPlanForm({ ...planForm, exercise_price_basis: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
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
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "rgba(0,0,0,0.6)" }}>
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
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
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
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
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
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
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
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
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
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
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
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
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
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
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
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
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
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
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
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "rgba(0,0,0,0.6)" }}>
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
                  style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
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

      <Footer />
    </div>
  );
}
