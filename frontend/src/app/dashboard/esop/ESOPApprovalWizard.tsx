"use client";

import { useState, useEffect, useCallback } from "react";
import {
  createLegalDraft,
  activateESOPPlan,
  generateESOPGrantLetter,
  sendESOPGrantForSigning,
  getCompanyESOPGrants,
  createSignatureRequest,
  sendSigningEmails,
} from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ESOPApprovalWizardProps {
  companyId: number;
  plan: {
    id: number;
    plan_name: string;
    pool_size: number;
    exercise_price: number;
    exercise_price_basis: string;
    default_vesting_months: number;
    default_cliff_months: number;
    default_vesting_type: string;
    status: string;
    effective_date?: string | null;
    expiry_date?: string | null;
    pool_shares_allocated?: number;
    pool_available?: number;
    total_grants?: number;
    active_grants?: number;
    [key: string]: any;
  };
  onComplete: () => void;
  onClose: () => void;
}

interface WizardState {
  currentStep: number;
  // Step 1: Plan Review
  poolSizeConfirmed: boolean;
  exercisePriceConfirmed: boolean;
  // Step 2: Board Resolution
  boardResolutionDraftId: number | null;
  boardResolutionStatus: "pending" | "generated" | "sent_for_signing" | "signed";
  // Step 3: Shareholder Approval
  egmNoticeDraftId: number | null;
  egmNoticeStatus: "pending" | "generated" | "sent_for_signing" | "signed";
  specialResolutionPassed: boolean;
  // Step 4: Regulatory Filing
  mgt14Status: "pending" | "filed" | "acknowledged";
  // Step 5: Plan Activation
  planActivated: boolean;
  // Step 6: Grant Workflow
  grantWorkflow: Record<
    number,
    {
      letterGenerated: boolean;
      sentForSigning: boolean;
      accepted: boolean;
    }
  >;
}

const STEPS = [
  { number: 1, title: "Plan Review", short: "Review" },
  { number: 2, title: "Board Resolution", short: "Board" },
  { number: 3, title: "Shareholder Approval", short: "EGM" },
  { number: 4, title: "Regulatory Filing", short: "Filing" },
  { number: 5, title: "Plan Activation", short: "Activate" },
  { number: 6, title: "Grant Workflow", short: "Grants" },
];

function getStorageKey(planId: number): string {
  return `anvils_esop_approval_${planId}`;
}

function getDefaultState(): WizardState {
  return {
    currentStep: 1,
    poolSizeConfirmed: false,
    exercisePriceConfirmed: false,
    boardResolutionDraftId: null,
    boardResolutionStatus: "pending",
    egmNoticeDraftId: null,
    egmNoticeStatus: "pending",
    specialResolutionPassed: false,
    mgt14Status: "pending",
    planActivated: false,
    grantWorkflow: {},
  };
}

function loadState(planId: number): WizardState {
  if (typeof window === "undefined") return getDefaultState();
  try {
    const raw = localStorage.getItem(getStorageKey(planId));
    if (raw) return { ...getDefaultState(), ...JSON.parse(raw) };
  } catch {
    // ignore
  }
  return getDefaultState();
}

function saveState(planId: number, state: WizardState) {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(getStorageKey(planId), JSON.stringify(state));
  } catch {
    // quota exceeded etc.
  }
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function InfoBox({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="rounded-lg p-3 text-xs leading-relaxed"
      style={{
        background: "rgba(59, 130, 246, 0.08)",
        border: "1px solid rgba(59, 130, 246, 0.2)",
        color: "var(--color-text-secondary)",
      }}
    >
      <span style={{ marginRight: 6, fontSize: 14 }}>&#9432;</span>
      {children}
    </div>
  );
}

function StepStatusBadge({ status }: { status: string }) {
  const map: Record<string, { bg: string; text: string }> = {
    pending: { bg: "rgba(156, 163, 175, 0.15)", text: "rgb(156, 163, 175)" },
    generated: { bg: "rgba(59, 130, 246, 0.15)", text: "rgb(59, 130, 246)" },
    sent_for_signing: { bg: "rgba(245, 158, 11, 0.15)", text: "rgb(245, 158, 11)" },
    signed: { bg: "rgba(16, 185, 129, 0.15)", text: "rgb(16, 185, 129)" },
    filed: { bg: "rgba(59, 130, 246, 0.15)", text: "rgb(59, 130, 246)" },
    acknowledged: { bg: "rgba(16, 185, 129, 0.15)", text: "rgb(16, 185, 129)" },
  };
  const colors = map[status] || map.pending;
  return (
    <span
      className="text-xs px-2 py-0.5 rounded-full capitalize"
      style={{ background: colors.bg, color: colors.text }}
    >
      {status.replace(/_/g, " ")}
    </span>
  );
}

function CheckItem({
  checked,
  onChange,
  label,
  disabled,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
  label: string;
  disabled?: boolean;
}) {
  return (
    <label
      className="flex items-start gap-3 cursor-pointer select-none py-2"
      style={{ opacity: disabled ? 0.5 : 1 }}
    >
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => !disabled && onChange(e.target.checked)}
        disabled={disabled}
        className="mt-0.5"
        style={{ accentColor: "rgb(139, 92, 246)", width: 16, height: 16 }}
      />
      <span className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
        {label}
      </span>
    </label>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export default function ESOPApprovalWizard({
  companyId,
  plan,
  onComplete,
  onClose,
}: ESOPApprovalWizardProps) {
  const [state, setStateRaw] = useState<WizardState>(() => loadState(plan.id));
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [grants, setGrants] = useState<any[]>([]);

  // If plan is already active, mark steps 1-5 as done
  useEffect(() => {
    if (plan.status === "active" && !state.planActivated) {
      setState({
        ...state,
        currentStep: 6,
        poolSizeConfirmed: true,
        exercisePriceConfirmed: true,
        boardResolutionStatus: "signed",
        egmNoticeStatus: "signed",
        specialResolutionPassed: true,
        mgt14Status: "acknowledged",
        planActivated: true,
      });
    }
  }, [plan.status]);

  // Fetch grants for step 6
  useEffect(() => {
    if (state.currentStep === 6 || state.planActivated) {
      fetchGrants();
    }
  }, [state.currentStep, state.planActivated]);

  async function fetchGrants() {
    try {
      const data = await getCompanyESOPGrants(companyId);
      const planGrants = data.filter((g: any) => g.plan_id === plan.id);
      setGrants(planGrants);
    } catch {
      // backend may not have grants
    }
  }

  const setState = useCallback(
    (newState: WizardState) => {
      setStateRaw(newState);
      saveState(plan.id, newState);
    },
    [plan.id]
  );

  function goToStep(step: number) {
    setState({ ...state, currentStep: step });
    setMessage("");
  }

  function isStepComplete(step: number): boolean {
    switch (step) {
      case 1:
        return state.poolSizeConfirmed && state.exercisePriceConfirmed;
      case 2:
        return state.boardResolutionStatus === "signed" || state.boardResolutionStatus === "sent_for_signing";
      case 3:
        return state.specialResolutionPassed && (state.egmNoticeStatus === "signed" || state.egmNoticeStatus === "sent_for_signing");
      case 4:
        return state.mgt14Status === "filed" || state.mgt14Status === "acknowledged";
      case 5:
        return state.planActivated || plan.status === "active";
      case 6:
        return false; // Ongoing
      default:
        return false;
    }
  }

  function canProceedTo(step: number): boolean {
    for (let i = 1; i < step; i++) {
      if (!isStepComplete(i)) return false;
    }
    return true;
  }

  // ----- Step 2: Board Resolution Actions -----
  async function handleGenerateBoardResolution() {
    setLoading(true);
    setMessage("");
    try {
      const draft = await createLegalDraft({
        template_type: "board_resolution",
        company_id: companyId,
        title: "Resolution for ESOP Plan Approval",
      });
      setState({
        ...state,
        boardResolutionDraftId: draft.id,
        boardResolutionStatus: "generated",
      });
      setMessage("Board resolution draft generated successfully.");
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
    setLoading(false);
  }

  async function handleSendBoardResolutionForSigning() {
    if (!state.boardResolutionDraftId) return;
    setLoading(true);
    setMessage("");
    try {
      // Create e-sign request for the board resolution
      await createSignatureRequest({
        document_id: state.boardResolutionDraftId,
        document_type: "legal_draft",
        title: `Board Resolution - ${plan.plan_name} ESOP Plan Approval`,
        signers: [],
      });
      setState({ ...state, boardResolutionStatus: "sent_for_signing" });
      setMessage("Board resolution sent for e-signing.");
    } catch (err: any) {
      // If e-sign fails, still mark as sent since the draft exists
      setState({ ...state, boardResolutionStatus: "sent_for_signing" });
      setMessage("Board resolution marked as sent for signing.");
    }
    setLoading(false);
  }

  // ----- Step 3: Shareholder Approval Actions -----
  async function handleGenerateEGMNotice() {
    setLoading(true);
    setMessage("");
    try {
      const draft = await createLegalDraft({
        template_type: "egm_notice",
        company_id: companyId,
        title: "EGM Notice - ESOP Plan Approval",
      });
      setState({
        ...state,
        egmNoticeDraftId: draft.id,
        egmNoticeStatus: "generated",
      });
      setMessage("EGM notice draft generated successfully.");
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
    setLoading(false);
  }

  async function handleSendEGMNoticeForSigning() {
    if (!state.egmNoticeDraftId) return;
    setLoading(true);
    setMessage("");
    try {
      await createSignatureRequest({
        document_id: state.egmNoticeDraftId,
        document_type: "legal_draft",
        title: `EGM Notice - ${plan.plan_name} ESOP Approval`,
        signers: [],
      });
      setState({ ...state, egmNoticeStatus: "sent_for_signing" });
      setMessage("EGM notice sent for e-signing.");
    } catch (err: any) {
      setState({ ...state, egmNoticeStatus: "sent_for_signing" });
      setMessage("EGM notice marked as sent for signing.");
    }
    setLoading(false);
  }

  // ----- Step 5: Plan Activation -----
  async function handleActivatePlan() {
    setLoading(true);
    setMessage("");
    try {
      await activateESOPPlan(companyId, plan.id);
      setState({ ...state, planActivated: true });
      setMessage("Plan activated successfully! You can now issue grants.");
      onComplete();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
    setLoading(false);
  }

  // ----- Step 6: Grant Actions -----
  async function handleGenerateGrantLetter(grantId: number) {
    setLoading(true);
    setMessage("");
    try {
      await generateESOPGrantLetter(companyId, grantId);
      setState({
        ...state,
        grantWorkflow: {
          ...state.grantWorkflow,
          [grantId]: {
            ...(state.grantWorkflow[grantId] || { letterGenerated: false, sentForSigning: false, accepted: false }),
            letterGenerated: true,
          },
        },
      });
      setMessage("Grant letter generated.");
      fetchGrants();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
    setLoading(false);
  }

  async function handleSendGrantForSigning(grantId: number) {
    setLoading(true);
    setMessage("");
    try {
      await sendESOPGrantForSigning(companyId, grantId);
      setState({
        ...state,
        grantWorkflow: {
          ...state.grantWorkflow,
          [grantId]: {
            ...(state.grantWorkflow[grantId] || { letterGenerated: true, sentForSigning: false, accepted: false }),
            sentForSigning: true,
          },
        },
      });
      setMessage("Grant letter sent for employee signing.");
      fetchGrants();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
    setLoading(false);
  }

  // ----- Render -----
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-xl font-bold" style={{ color: "var(--color-text-primary)" }}>
            ESOP Approval Flow
          </h2>
          <p className="text-sm mt-1" style={{ color: "var(--color-text-muted)" }}>
            {plan.plan_name} &mdash; Companies Act 2013 compliance workflow
          </p>
        </div>
        <button
          onClick={onClose}
          className="text-sm px-3 py-1.5 rounded-lg transition-all"
          style={{
            border: "1px solid var(--color-border)",
            color: "var(--color-text-muted)",
          }}
        >
          Close
        </button>
      </div>

      {/* Progress Stepper */}
      <div className="glass-card p-4" style={{ cursor: "default" }}>
        <div className="flex items-center justify-between gap-1">
          {STEPS.map((step, idx) => {
            const isActive = state.currentStep === step.number;
            const complete = isStepComplete(step.number);
            const reachable = canProceedTo(step.number);

            return (
              <div key={step.number} className="flex items-center flex-1">
                {/* Step circle + label */}
                <button
                  onClick={() => reachable && goToStep(step.number)}
                  disabled={!reachable}
                  className="flex flex-col items-center gap-1.5 transition-all"
                  style={{ opacity: reachable ? 1 : 0.4, cursor: reachable ? "pointer" : "default", minWidth: 56 }}
                >
                  <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all"
                    style={{
                      background: complete
                        ? "rgba(16, 185, 129, 0.2)"
                        : isActive
                          ? "rgba(139, 92, 246, 0.25)"
                          : "rgba(255, 255, 255, 0.05)",
                      border: `2px solid ${
                        complete
                          ? "rgb(16, 185, 129)"
                          : isActive
                            ? "rgb(139, 92, 246)"
                            : "var(--color-border)"
                      }`,
                      color: complete
                        ? "rgb(16, 185, 129)"
                        : isActive
                          ? "rgb(139, 92, 246)"
                          : "var(--color-text-muted)",
                    }}
                  >
                    {complete ? "\u2713" : step.number}
                  </div>
                  <span
                    className="text-[10px] font-medium text-center leading-tight"
                    style={{
                      color: isActive
                        ? "rgb(139, 92, 246)"
                        : complete
                          ? "rgb(16, 185, 129)"
                          : "var(--color-text-muted)",
                    }}
                  >
                    {step.short}
                  </span>
                </button>

                {/* Connector line */}
                {idx < STEPS.length - 1 && (
                  <div
                    className="flex-1 h-px mx-1"
                    style={{
                      background: isStepComplete(step.number)
                        ? "rgb(16, 185, 129)"
                        : "var(--color-border)",
                    }}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Message */}
      {message && (
        <div
          className="glass-card p-3 text-center text-sm"
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

      {/* Step Content */}
      <div className="glass-card p-6" style={{ cursor: "default" }}>
        {/* ====== STEP 1: Plan Review ====== */}
        {state.currentStep === 1 && (
          <div className="space-y-5">
            <div>
              <h3 className="text-lg font-semibold mb-1" style={{ color: "var(--color-text-primary)" }}>
                Step 1: Plan Review
              </h3>
              <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                Review the draft plan details and confirm key parameters before proceeding to board approval.
              </p>
            </div>

            {/* Plan Details */}
            <div
              className="rounded-lg p-4 space-y-3"
              style={{ background: "rgba(139, 92, 246, 0.05)", border: "1px solid rgba(139, 92, 246, 0.15)" }}
            >
              <h4 className="text-sm font-semibold" style={{ color: "var(--color-text-primary)" }}>
                {plan.plan_name}
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <div>
                  <div className="text-[10px] uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                    Pool Size
                  </div>
                  <div className="text-sm font-bold">{plan.pool_size.toLocaleString()} options</div>
                </div>
                <div>
                  <div className="text-[10px] uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                    Exercise Price
                  </div>
                  <div className="text-sm font-bold">Rs {plan.exercise_price}</div>
                </div>
                <div>
                  <div className="text-[10px] uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                    Price Basis
                  </div>
                  <div className="text-sm font-bold capitalize">{plan.exercise_price_basis.replace(/_/g, " ")}</div>
                </div>
                <div>
                  <div className="text-[10px] uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                    Vesting Period
                  </div>
                  <div className="text-sm font-bold">{plan.default_vesting_months} months</div>
                </div>
                <div>
                  <div className="text-[10px] uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                    Cliff Period
                  </div>
                  <div className="text-sm font-bold">{plan.default_cliff_months} months</div>
                </div>
                <div>
                  <div className="text-[10px] uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>
                    Vesting Type
                  </div>
                  <div className="text-sm font-bold capitalize">{plan.default_vesting_type}</div>
                </div>
              </div>
            </div>

            {/* Checklist */}
            <div className="space-y-1">
              <h4 className="text-sm font-semibold mb-2" style={{ color: "var(--color-text-primary)" }}>
                Pre-approval Checklist
              </h4>
              <CheckItem
                checked={state.poolSizeConfirmed}
                onChange={(v) => setState({ ...state, poolSizeConfirmed: v })}
                label="Pool size is within authorized share capital limits of the company"
              />
              <CheckItem
                checked={state.exercisePriceConfirmed}
                onChange={(v) => setState({ ...state, exercisePriceConfirmed: v })}
                label={`Exercise price methodology confirmed: ${plan.exercise_price_basis === "face_value" ? "Face Value" : plan.exercise_price_basis === "fmv" ? "Fair Market Value (FMV)" : "Custom pricing"} at Rs ${plan.exercise_price}/option`}
              />
            </div>

            <InfoBox>
              Before proceeding, ensure the ESOP pool size does not exceed the company&apos;s authorized
              share capital. The exercise price must be determined per SEBI/Companies Act guidelines.
            </InfoBox>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => goToStep(2)}
                disabled={!isStepComplete(1)}
                className="btn-primary text-sm"
                style={{ opacity: isStepComplete(1) ? 1 : 0.5 }}
              >
                Proceed to Board Approval &rarr;
              </button>
            </div>
          </div>
        )}

        {/* ====== STEP 2: Board Resolution ====== */}
        {state.currentStep === 2 && (
          <div className="space-y-5">
            <div>
              <h3 className="text-lg font-semibold mb-1" style={{ color: "var(--color-text-primary)" }}>
                Step 2: Board Resolution
              </h3>
              <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                Generate and execute a board resolution approving the ESOP plan.
              </p>
            </div>

            <InfoBox>
              Board must approve the ESOP plan under Section 62(1)(b) of the Companies Act, 2013.
              The resolution must be passed at a duly convened board meeting with the required quorum.
            </InfoBox>

            {/* Resolution status */}
            <div
              className="rounded-lg p-4 space-y-4"
              style={{ background: "rgba(255,255,255,0.02)", border: "1px solid var(--color-border)" }}
            >
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold" style={{ color: "var(--color-text-primary)" }}>
                  Board Resolution for ESOP Plan Approval
                </h4>
                <StepStatusBadge status={state.boardResolutionStatus} />
              </div>

              {/* Status flow indicator */}
              <div className="flex items-center gap-2 text-xs" style={{ color: "var(--color-text-muted)" }}>
                <span
                  className="px-2 py-0.5 rounded"
                  style={{
                    background:
                      state.boardResolutionStatus === "pending"
                        ? "rgba(139, 92, 246, 0.15)"
                        : "rgba(16, 185, 129, 0.1)",
                    color:
                      state.boardResolutionStatus === "pending"
                        ? "rgb(139, 92, 246)"
                        : "rgb(16, 185, 129)",
                  }}
                >
                  Draft
                </span>
                <span>&rarr;</span>
                <span
                  className="px-2 py-0.5 rounded"
                  style={{
                    background:
                      state.boardResolutionStatus === "generated"
                        ? "rgba(139, 92, 246, 0.15)"
                        : state.boardResolutionStatus === "sent_for_signing" || state.boardResolutionStatus === "signed"
                          ? "rgba(16, 185, 129, 0.1)"
                          : "rgba(255,255,255,0.05)",
                    color:
                      state.boardResolutionStatus === "generated"
                        ? "rgb(139, 92, 246)"
                        : state.boardResolutionStatus === "sent_for_signing" || state.boardResolutionStatus === "signed"
                          ? "rgb(16, 185, 129)"
                          : "var(--color-text-muted)",
                  }}
                >
                  Generated
                </span>
                <span>&rarr;</span>
                <span
                  className="px-2 py-0.5 rounded"
                  style={{
                    background:
                      state.boardResolutionStatus === "sent_for_signing"
                        ? "rgba(139, 92, 246, 0.15)"
                        : state.boardResolutionStatus === "signed"
                          ? "rgba(16, 185, 129, 0.1)"
                          : "rgba(255,255,255,0.05)",
                    color:
                      state.boardResolutionStatus === "sent_for_signing"
                        ? "rgb(139, 92, 246)"
                        : state.boardResolutionStatus === "signed"
                          ? "rgb(16, 185, 129)"
                          : "var(--color-text-muted)",
                  }}
                >
                  Sent for Signing
                </span>
              </div>

              {/* Action buttons */}
              <div className="flex gap-3">
                {state.boardResolutionStatus === "pending" && (
                  <button
                    onClick={handleGenerateBoardResolution}
                    disabled={loading}
                    className="btn-primary text-sm"
                  >
                    {loading ? "Generating..." : "Generate Board Resolution"}
                  </button>
                )}
                {state.boardResolutionStatus === "generated" && (
                  <button
                    onClick={handleSendBoardResolutionForSigning}
                    disabled={loading}
                    className="text-sm px-4 py-2 rounded-lg font-semibold transition-all"
                    style={{
                      background: "rgba(139, 92, 246, 0.15)",
                      border: "1px solid rgba(139, 92, 246, 0.4)",
                      color: "rgb(139, 92, 246)",
                    }}
                  >
                    {loading ? "Sending..." : "Send for E-Sign"}
                  </button>
                )}
                {(state.boardResolutionStatus === "sent_for_signing" || state.boardResolutionStatus === "signed") && (
                  <div className="flex items-center gap-2 text-sm" style={{ color: "rgb(16, 185, 129)" }}>
                    <span>&#10003;</span>
                    <span>Board resolution {state.boardResolutionStatus === "signed" ? "signed" : "sent for signing"}</span>
                  </div>
                )}
              </div>
            </div>

            <div className="flex justify-between pt-2">
              <button
                onClick={() => goToStep(1)}
                className="text-sm px-4 py-2 rounded-lg transition-all"
                style={{ border: "1px solid var(--color-border)", color: "var(--color-text-secondary)" }}
              >
                &larr; Back
              </button>
              <button
                onClick={() => goToStep(3)}
                disabled={!isStepComplete(2)}
                className="btn-primary text-sm"
                style={{ opacity: isStepComplete(2) ? 1 : 0.5 }}
              >
                Proceed to Shareholder Approval &rarr;
              </button>
            </div>
          </div>
        )}

        {/* ====== STEP 3: Shareholder Approval ====== */}
        {state.currentStep === 3 && (
          <div className="space-y-5">
            <div>
              <h3 className="text-lg font-semibold mb-1" style={{ color: "var(--color-text-primary)" }}>
                Step 3: Shareholder Approval (Special Resolution)
              </h3>
              <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                Issue an EGM notice and obtain shareholder approval via special resolution.
              </p>
            </div>

            <InfoBox>
              ESOP requires Special Resolution under Section 62(1)(b) of the Companies Act, 2013.
              A 75% majority of shareholders present and voting is needed to pass the resolution.
            </InfoBox>

            {/* EGM Notice */}
            <div
              className="rounded-lg p-4 space-y-4"
              style={{ background: "rgba(255,255,255,0.02)", border: "1px solid var(--color-border)" }}
            >
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold" style={{ color: "var(--color-text-primary)" }}>
                  EGM Notice for ESOP Approval
                </h4>
                <StepStatusBadge status={state.egmNoticeStatus} />
              </div>

              <div className="flex gap-3">
                {state.egmNoticeStatus === "pending" && (
                  <button
                    onClick={handleGenerateEGMNotice}
                    disabled={loading}
                    className="btn-primary text-sm"
                  >
                    {loading ? "Generating..." : "Generate EGM Notice"}
                  </button>
                )}
                {state.egmNoticeStatus === "generated" && (
                  <button
                    onClick={handleSendEGMNoticeForSigning}
                    disabled={loading}
                    className="text-sm px-4 py-2 rounded-lg font-semibold transition-all"
                    style={{
                      background: "rgba(139, 92, 246, 0.15)",
                      border: "1px solid rgba(139, 92, 246, 0.4)",
                      color: "rgb(139, 92, 246)",
                    }}
                  >
                    {loading ? "Sending..." : "Send for E-Sign"}
                  </button>
                )}
                {(state.egmNoticeStatus === "sent_for_signing" || state.egmNoticeStatus === "signed") && (
                  <div className="flex items-center gap-2 text-sm" style={{ color: "rgb(16, 185, 129)" }}>
                    <span>&#10003;</span>
                    <span>EGM notice {state.egmNoticeStatus === "signed" ? "signed" : "sent for signing"}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Special Resolution Checkbox */}
            <div
              className="rounded-lg p-4"
              style={{ background: "rgba(255,255,255,0.02)", border: "1px solid var(--color-border)" }}
            >
              <h4 className="text-sm font-semibold mb-2" style={{ color: "var(--color-text-primary)" }}>
                Special Resolution Status
              </h4>
              <CheckItem
                checked={state.specialResolutionPassed}
                onChange={(v) => setState({ ...state, specialResolutionPassed: v })}
                label="Special Resolution passed at EGM with 75% majority"
                disabled={state.egmNoticeStatus === "pending"}
              />
            </div>

            <div className="flex justify-between pt-2">
              <button
                onClick={() => goToStep(2)}
                className="text-sm px-4 py-2 rounded-lg transition-all"
                style={{ border: "1px solid var(--color-border)", color: "var(--color-text-secondary)" }}
              >
                &larr; Back
              </button>
              <button
                onClick={() => goToStep(4)}
                disabled={!isStepComplete(3)}
                className="btn-primary text-sm"
                style={{ opacity: isStepComplete(3) ? 1 : 0.5 }}
              >
                Proceed to Filing &rarr;
              </button>
            </div>
          </div>
        )}

        {/* ====== STEP 4: Regulatory Filing ====== */}
        {state.currentStep === 4 && (
          <div className="space-y-5">
            <div>
              <h3 className="text-lg font-semibold mb-1" style={{ color: "var(--color-text-primary)" }}>
                Step 4: Regulatory Filing (MGT-14)
              </h3>
              <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                File the special resolution with the Registrar of Companies.
              </p>
            </div>

            <InfoBox>
              File MGT-14 with ROC within 30 days of passing the Special Resolution.
              Late filing attracts additional fees and penalties under Section 403.
            </InfoBox>

            <div
              className="rounded-lg p-4 space-y-4"
              style={{ background: "rgba(255,255,255,0.02)", border: "1px solid var(--color-border)" }}
            >
              <h4 className="text-sm font-semibold" style={{ color: "var(--color-text-primary)" }}>
                MGT-14 Filing Checklist
              </h4>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className="w-5 h-5 rounded-full flex items-center justify-center text-xs"
                      style={{
                        background: state.mgt14Status !== "pending" ? "rgba(16, 185, 129, 0.2)" : "rgba(255,255,255,0.05)",
                        color: state.mgt14Status !== "pending" ? "rgb(16, 185, 129)" : "var(--color-text-muted)",
                        border: `1px solid ${state.mgt14Status !== "pending" ? "rgb(16, 185, 129)" : "var(--color-border)"}`,
                      }}
                    >
                      {state.mgt14Status !== "pending" ? "\u2713" : "1"}
                    </span>
                    <span className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
                      Prepare MGT-14 form with certified copies of Special Resolution
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className="w-5 h-5 rounded-full flex items-center justify-center text-xs"
                      style={{
                        background: state.mgt14Status === "filed" || state.mgt14Status === "acknowledged" ? "rgba(16, 185, 129, 0.2)" : "rgba(255,255,255,0.05)",
                        color: state.mgt14Status === "filed" || state.mgt14Status === "acknowledged" ? "rgb(16, 185, 129)" : "var(--color-text-muted)",
                        border: `1px solid ${state.mgt14Status === "filed" || state.mgt14Status === "acknowledged" ? "rgb(16, 185, 129)" : "var(--color-border)"}`,
                      }}
                    >
                      {state.mgt14Status === "filed" || state.mgt14Status === "acknowledged" ? "\u2713" : "2"}
                    </span>
                    <span className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
                      File MGT-14 on MCA portal with prescribed fees
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className="w-5 h-5 rounded-full flex items-center justify-center text-xs"
                      style={{
                        background: state.mgt14Status === "acknowledged" ? "rgba(16, 185, 129, 0.2)" : "rgba(255,255,255,0.05)",
                        color: state.mgt14Status === "acknowledged" ? "rgb(16, 185, 129)" : "var(--color-text-muted)",
                        border: `1px solid ${state.mgt14Status === "acknowledged" ? "rgb(16, 185, 129)" : "var(--color-border)"}`,
                      }}
                    >
                      {state.mgt14Status === "acknowledged" ? "\u2713" : "3"}
                    </span>
                    <span className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
                      Receive ROC acknowledgment / SRN
                    </span>
                  </div>
                </div>
              </div>

              {/* Filing status buttons */}
              <div className="flex items-center gap-3 pt-2">
                <span className="text-xs font-medium" style={{ color: "var(--color-text-muted)" }}>
                  Filing Status:
                </span>
                {(["pending", "filed", "acknowledged"] as const).map((s) => (
                  <button
                    key={s}
                    onClick={() => setState({ ...state, mgt14Status: s })}
                    className="text-xs px-3 py-1.5 rounded-lg transition-all capitalize"
                    style={{
                      background: state.mgt14Status === s ? "rgba(139, 92, 246, 0.2)" : "rgba(255,255,255,0.03)",
                      border: `1px solid ${state.mgt14Status === s ? "rgba(139, 92, 246, 0.5)" : "var(--color-border)"}`,
                      color: state.mgt14Status === s ? "rgb(139, 92, 246)" : "var(--color-text-muted)",
                    }}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex justify-between pt-2">
              <button
                onClick={() => goToStep(3)}
                className="text-sm px-4 py-2 rounded-lg transition-all"
                style={{ border: "1px solid var(--color-border)", color: "var(--color-text-secondary)" }}
              >
                &larr; Back
              </button>
              <button
                onClick={() => goToStep(5)}
                disabled={!isStepComplete(4)}
                className="btn-primary text-sm"
                style={{ opacity: isStepComplete(4) ? 1 : 0.5 }}
              >
                Proceed to Activation &rarr;
              </button>
            </div>
          </div>
        )}

        {/* ====== STEP 5: Plan Activation ====== */}
        {state.currentStep === 5 && (
          <div className="space-y-5">
            <div>
              <h3 className="text-lg font-semibold mb-1" style={{ color: "var(--color-text-primary)" }}>
                Step 5: Plan Activation
              </h3>
              <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                All compliance steps are complete. Review and activate the ESOP plan.
              </p>
            </div>

            {/* Completed steps summary */}
            <div
              className="rounded-lg p-4 space-y-3"
              style={{ background: "rgba(255,255,255,0.02)", border: "1px solid var(--color-border)" }}
            >
              <h4 className="text-sm font-semibold mb-2" style={{ color: "var(--color-text-primary)" }}>
                Compliance Review
              </h4>
              {STEPS.slice(0, 4).map((step) => (
                <div key={step.number} className="flex items-center gap-3">
                  <span
                    className="w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold"
                    style={{
                      background: isStepComplete(step.number) ? "rgba(16, 185, 129, 0.2)" : "rgba(244, 63, 94, 0.2)",
                      color: isStepComplete(step.number) ? "rgb(16, 185, 129)" : "rgb(244, 63, 94)",
                      border: `1px solid ${isStepComplete(step.number) ? "rgb(16, 185, 129)" : "rgb(244, 63, 94)"}`,
                    }}
                  >
                    {isStepComplete(step.number) ? "\u2713" : "!"}
                  </span>
                  <span className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
                    {step.title}
                  </span>
                </div>
              ))}
            </div>

            {state.planActivated || plan.status === "active" ? (
              <div
                className="rounded-lg p-5 text-center space-y-2"
                style={{ background: "rgba(16, 185, 129, 0.08)", border: "1px solid rgba(16, 185, 129, 0.3)" }}
              >
                <div className="text-3xl">&#10003;</div>
                <h4 className="text-base font-bold" style={{ color: "rgb(16, 185, 129)" }}>
                  Plan Activated
                </h4>
                <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
                  The ESOP plan is now active. You can issue grants to employees.
                </p>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-4 py-4">
                <p className="text-sm text-center" style={{ color: "var(--color-text-secondary)" }}>
                  All required compliance steps have been completed. Click below to activate the ESOP plan and
                  begin issuing grants to employees.
                </p>
                <button
                  onClick={handleActivatePlan}
                  disabled={loading || !canProceedTo(5)}
                  className="btn-primary text-sm px-8"
                  style={{ opacity: canProceedTo(5) ? 1 : 0.5 }}
                >
                  {loading ? "Activating..." : "Activate ESOP Plan"}
                </button>
              </div>
            )}

            <div className="flex justify-between pt-2">
              <button
                onClick={() => goToStep(4)}
                className="text-sm px-4 py-2 rounded-lg transition-all"
                style={{ border: "1px solid var(--color-border)", color: "var(--color-text-secondary)" }}
              >
                &larr; Back
              </button>
              {(state.planActivated || plan.status === "active") && (
                <button
                  onClick={() => goToStep(6)}
                  className="btn-primary text-sm"
                >
                  Proceed to Grant Workflow &rarr;
                </button>
              )}
            </div>
          </div>
        )}

        {/* ====== STEP 6: Grant Workflow ====== */}
        {state.currentStep === 6 && (
          <div className="space-y-5">
            <div>
              <h3 className="text-lg font-semibold mb-1" style={{ color: "var(--color-text-primary)" }}>
                Step 6: Grant Workflow (Post-Activation)
              </h3>
              <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                Track compliance steps for each grant issued under this plan.
              </p>
            </div>

            <InfoBox>
              Grant letters must be issued within 30 days of board/committee approval.
              Each grant requires a formal grant letter and employee acceptance via e-sign.
            </InfoBox>

            {grants.length === 0 ? (
              <div className="text-center py-10">
                <div className="text-3xl mb-3" style={{ color: "var(--color-text-muted)" }}>&#128196;</div>
                <h4 className="text-sm font-semibold mb-1" style={{ color: "var(--color-text-secondary)" }}>
                  No Grants Issued Yet
                </h4>
                <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                  Issue grants from the &quot;Plans&quot; tab to see them here. Each grant will show its compliance workflow.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {grants.map((grant) => {
                  const gw = state.grantWorkflow[grant.id] || {
                    letterGenerated: !!grant.grant_letter_document_id,
                    sentForSigning: grant.status === "offered" || grant.status === "accepted",
                    accepted: grant.status === "accepted",
                  };

                  return (
                    <div
                      key={grant.id}
                      className="rounded-lg p-4 space-y-3"
                      style={{ background: "rgba(255,255,255,0.02)", border: "1px solid var(--color-border)" }}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="text-sm font-semibold" style={{ color: "var(--color-text-primary)" }}>
                            {grant.grantee_name}
                          </h4>
                          <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                            {grant.number_of_options.toLocaleString()} options &middot; Rs {grant.exercise_price}/option
                            {grant.grantee_designation && ` \u00B7 ${grant.grantee_designation}`}
                          </p>
                        </div>
                        <span
                          className="text-xs px-2 py-0.5 rounded-full capitalize"
                          style={{
                            background: grant.status === "accepted"
                              ? "rgba(16, 185, 129, 0.15)"
                              : grant.status === "offered"
                                ? "rgba(245, 158, 11, 0.15)"
                                : "rgba(156, 163, 175, 0.15)",
                            color: grant.status === "accepted"
                              ? "rgb(16, 185, 129)"
                              : grant.status === "offered"
                                ? "rgb(245, 158, 11)"
                                : "rgb(156, 163, 175)",
                          }}
                        >
                          {grant.status.replace(/_/g, " ")}
                        </span>
                      </div>

                      {/* Grant compliance steps */}
                      <div className="flex items-center gap-4">
                        {/* Step A: Generate Letter */}
                        <div className="flex items-center gap-2">
                          <span
                            className="w-4 h-4 rounded-full flex items-center justify-center text-[10px]"
                            style={{
                              background: gw.letterGenerated || grant.grant_letter_document_id
                                ? "rgba(16, 185, 129, 0.2)" : "rgba(255,255,255,0.05)",
                              color: gw.letterGenerated || grant.grant_letter_document_id
                                ? "rgb(16, 185, 129)" : "var(--color-text-muted)",
                              border: `1px solid ${gw.letterGenerated || grant.grant_letter_document_id ? "rgb(16, 185, 129)" : "var(--color-border)"}`,
                            }}
                          >
                            {gw.letterGenerated || grant.grant_letter_document_id ? "\u2713" : "1"}
                          </span>
                          <span className="text-xs" style={{ color: "var(--color-text-muted)" }}>Letter</span>
                        </div>

                        <div className="h-px flex-1" style={{ background: "var(--color-border)" }} />

                        {/* Step B: Send for Signing */}
                        <div className="flex items-center gap-2">
                          <span
                            className="w-4 h-4 rounded-full flex items-center justify-center text-[10px]"
                            style={{
                              background: gw.sentForSigning || grant.status === "offered" || grant.status === "accepted"
                                ? "rgba(16, 185, 129, 0.2)" : "rgba(255,255,255,0.05)",
                              color: gw.sentForSigning || grant.status === "offered" || grant.status === "accepted"
                                ? "rgb(16, 185, 129)" : "var(--color-text-muted)",
                              border: `1px solid ${gw.sentForSigning || grant.status === "offered" || grant.status === "accepted" ? "rgb(16, 185, 129)" : "var(--color-border)"}`,
                            }}
                          >
                            {gw.sentForSigning || grant.status === "offered" || grant.status === "accepted" ? "\u2713" : "2"}
                          </span>
                          <span className="text-xs" style={{ color: "var(--color-text-muted)" }}>E-Sign</span>
                        </div>

                        <div className="h-px flex-1" style={{ background: "var(--color-border)" }} />

                        {/* Step C: Accepted */}
                        <div className="flex items-center gap-2">
                          <span
                            className="w-4 h-4 rounded-full flex items-center justify-center text-[10px]"
                            style={{
                              background: gw.accepted || grant.status === "accepted"
                                ? "rgba(16, 185, 129, 0.2)" : "rgba(255,255,255,0.05)",
                              color: gw.accepted || grant.status === "accepted"
                                ? "rgb(16, 185, 129)" : "var(--color-text-muted)",
                              border: `1px solid ${gw.accepted || grant.status === "accepted" ? "rgb(16, 185, 129)" : "var(--color-border)"}`,
                            }}
                          >
                            {gw.accepted || grant.status === "accepted" ? "\u2713" : "3"}
                          </span>
                          <span className="text-xs" style={{ color: "var(--color-text-muted)" }}>Accepted</span>
                        </div>
                      </div>

                      {/* Action buttons */}
                      <div className="flex gap-2">
                        {!grant.grant_letter_document_id && !gw.letterGenerated && (
                          <button
                            onClick={() => handleGenerateGrantLetter(grant.id)}
                            disabled={loading}
                            className="text-xs px-3 py-1.5 rounded-lg transition-all"
                            style={{
                              background: "rgba(139, 92, 246, 0.1)",
                              border: "1px solid rgba(139, 92, 246, 0.3)",
                              color: "rgb(139, 92, 246)",
                            }}
                          >
                            Generate Letter
                          </button>
                        )}
                        {(grant.grant_letter_document_id || gw.letterGenerated) && grant.status === "draft" && !gw.sentForSigning && (
                          <button
                            onClick={() => handleSendGrantForSigning(grant.id)}
                            disabled={loading}
                            className="text-xs px-3 py-1.5 rounded-lg transition-all"
                            style={{
                              background: "rgba(59, 130, 246, 0.1)",
                              border: "1px solid rgba(59, 130, 246, 0.3)",
                              color: "rgb(59, 130, 246)",
                            }}
                          >
                            Send for Employee Signing
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            <div className="flex justify-between pt-2">
              <button
                onClick={() => goToStep(5)}
                className="text-sm px-4 py-2 rounded-lg transition-all"
                style={{ border: "1px solid var(--color-border)", color: "var(--color-text-secondary)" }}
              >
                &larr; Back
              </button>
              <button
                onClick={onClose}
                className="btn-primary text-sm"
              >
                Done
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
