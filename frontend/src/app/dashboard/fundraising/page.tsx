"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import FeatureGate from "@/components/feature-gate";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from "recharts";

import {
  getCompanies,
  getFundingRounds,
  getFundingRound,
  createFundingRound,
  updateFundingRound,
  addRoundInvestor,
  updateRoundInvestor,
  removeRoundInvestor,
  getClosingRoom,
  initiateClosing,
  completeAllotment,
  previewConversion,
  convertRound,
  createLegalDraft,
  saveFundraisingChecklistState,
  getFundraisingChecklistState,
  shareDeal,
  listSharedDeals,
  revokeSharedDeal,
} from "@/lib/api";


interface Investor {
  id: number;
  investor_name: string;
  investor_email: string | null;
  investor_type: string;
  investor_entity: string | null;
  investment_amount: number;
  shares_allotted: number;
  share_type: string;
  committed: boolean;
  funds_received: boolean;
  documents_signed: boolean;
  shares_issued: boolean;
  notes: string | null;
}

interface FundingRound {
  id: number;
  company_id: number;
  round_name: string;
  instrument_type: string;
  pre_money_valuation: number | null;
  post_money_valuation: number | null;
  price_per_share: number | null;
  target_amount: number | null;
  amount_raised: number;
  status: string;
  allotment_completed: boolean;
  valuation_cap: number | null;
  discount_rate: number | null;
  interest_rate: number | null;
  maturity_months: number | null;
  notes: string | null;
  investor_count?: number;
  investors?: Investor[];
  created_at: string;
}

// ── Document Checklist Types ──

type DocStatus = "not_started" | "in_progress" | "complete";
type TransactionDocStatus = "draft" | "in_review" | "signed";
type FilingStatus = "not_filed" | "filed" | "acknowledged";
type ShareholderApprovalStatus = "pending" | "sr_passed";

interface ChecklistState {
  // Step 1: Valuation
  valuation_status: DocStatus;

  // Step 2: Transaction Documents
  sha_status: TransactionDocStatus;
  sha_draft_id: number | null;
  ssa_status: TransactionDocStatus;
  ssa_draft_id: number | null;
  aoa_amended: boolean;

  // Step 3: Board Approval
  board_resolution_status: TransactionDocStatus;
  board_resolution_draft_id: number | null;
  board_meeting_held: boolean;
  board_resolution_passed: boolean;

  // Step 4: Shareholder Approval
  shareholder_approval_status: ShareholderApprovalStatus;
  egm_notice_sent: boolean;
  sr_private_placement: boolean;
  sr_aoa_amendment: boolean;
  sr_capital_increase: boolean;

  // Step 5: Regulatory Filings
  mgt14_filed: FilingStatus;
  sh7_filed: FilingStatus;
  sh7_amount: string;

  // Step 6: Offer & Allotment
  pas4_issued: boolean;
  funds_received_investors: Record<number, boolean>;
  allotment_board_resolution: boolean;

  // Step 7: Post-Closing Filings
  pas3_filed: boolean;
  share_certificates_issued: boolean;
  fc_gpr_filed: boolean;
}

const DEFAULT_CHECKLIST_STATE: ChecklistState = {
  valuation_status: "not_started",
  sha_status: "draft",
  sha_draft_id: null,
  ssa_status: "draft",
  ssa_draft_id: null,
  aoa_amended: false,
  board_resolution_status: "draft",
  board_resolution_draft_id: null,
  board_meeting_held: false,
  board_resolution_passed: false,
  shareholder_approval_status: "pending",
  egm_notice_sent: false,
  sr_private_placement: false,
  sr_aoa_amendment: false,
  sr_capital_increase: false,
  mgt14_filed: "not_filed",
  sh7_filed: "not_filed",
  sh7_amount: "",
  pas4_issued: false,
  funds_received_investors: {},
  allotment_board_resolution: false,
  pas3_filed: false,
  share_certificates_issued: false,
  fc_gpr_filed: false,
};

function useChecklistState(roundId: number | null, companyId: number | null): [ChecklistState, (patch: Partial<ChecklistState>) => void] {
  const storageKey = roundId != null ? `anvils_round_checklist_${roundId}` : null;

  const [state, setState] = useState<ChecklistState>(DEFAULT_CHECKLIST_STATE);

  useEffect(() => {
    if (!roundId || !companyId) {
      setState(DEFAULT_CHECKLIST_STATE);
      return;
    }
    const loadState = async () => {
      try {
        const serverState = await getFundraisingChecklistState(companyId, roundId);
        if (serverState) {
          setState({ ...DEFAULT_CHECKLIST_STATE, ...serverState });
          return;
        }
      } catch {
        // Server unavailable, fall back to localStorage
      }
      // Fall back to localStorage
      try {
        const stored = localStorage.getItem(`anvils_round_checklist_${roundId}`);
        if (stored) {
          setState({ ...DEFAULT_CHECKLIST_STATE, ...JSON.parse(stored) });
        } else {
          setState(DEFAULT_CHECKLIST_STATE);
        }
      } catch {
        setState(DEFAULT_CHECKLIST_STATE);
      }
    };
    loadState();
  }, [roundId, companyId]);

  const updateState = useCallback(
    (patch: Partial<ChecklistState>) => {
      setState((prev) => {
        const next = { ...prev, ...patch };
        if (storageKey) {
          try {
            localStorage.setItem(storageKey, JSON.stringify(next));
          } catch {
            // localStorage quota exceeded - silently fail
          }
        }
        if (companyId && roundId) {
          saveFundraisingChecklistState(companyId, roundId, next).catch(() => {});
        }
        return next;
      });
    },
    [storageKey, companyId, roundId]
  );

  return [state, updateState];
}

// ── Checklist UI Helpers ──

function StepStatusIcon({ status }: { status: "complete" | "in_progress" | "not_started" }) {
  if (status === "complete") {
    return (
      <div
        className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0"
        style={{ background: "var(--color-success-light)", color: "var(--color-accent-emerald-light)" }}
      >
        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
        </svg>
      </div>
    );
  }
  if (status === "in_progress") {
    return (
      <div
        className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0"
        style={{ background: "var(--color-warning-light)", color: "var(--color-accent-amber)" }}
      >
        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5" />
        </svg>
      </div>
    );
  }
  return (
    <div
      className="w-5 h-5 rounded-full flex-shrink-0"
      style={{ border: "2px solid var(--color-border)" }}
    />
  );
}

function MiniCheckbox({
  checked,
  onChange,
  disabled = false,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
  disabled?: boolean;
}) {
  return (
    <button
      onClick={() => !disabled && onChange(!checked)}
      disabled={disabled}
      className="w-4 h-4 rounded border inline-flex items-center justify-center transition-all flex-shrink-0"
      style={{
        borderColor: checked ? "var(--color-accent-emerald-light)" : "var(--color-border)",
        background: checked ? "var(--color-success-light)" : "transparent",
        color: checked ? "var(--color-accent-emerald-light)" : "transparent",
        opacity: disabled ? 0.4 : 1,
        cursor: disabled ? "not-allowed" : "pointer",
      }}
    >
      {checked && (
        <svg className="w-2.5 h-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
        </svg>
      )}
    </button>
  );
}

function SmallActionButton({
  onClick,
  children,
  variant = "purple",
  disabled = false,
}: {
  onClick: () => void;
  children: React.ReactNode;
  variant?: "purple" | "green" | "amber";
  disabled?: boolean;
}) {
  const colors = {
    purple: { bg: "var(--color-purple-bg)", border: "var(--color-purple-bg)", text: "var(--color-accent-purple-light)" },
    green: { bg: "var(--color-success-light)", border: "var(--color-success-light)", text: "var(--color-accent-emerald-light)" },
    amber: { bg: "var(--color-warning-light)", border: "var(--color-warning-light)", text: "var(--color-accent-amber)" },
  };
  const c = colors[variant];
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="text-[10px] px-2 py-1 rounded-md whitespace-nowrap"
      style={{
        background: c.bg,
        border: `1px solid ${c.border}`,
        color: c.text,
        opacity: disabled ? 0.4 : 1,
        cursor: disabled ? "not-allowed" : "pointer",
      }}
    >
      {children}
    </button>
  );
}

function TransactionDocStatusBadge({ status }: { status: TransactionDocStatus }) {
  const map: Record<TransactionDocStatus, { bg: string; text: string; label: string }> = {
    draft: { bg: "var(--color-hover-overlay)", text: "var(--color-text-muted)", label: "Draft" },
    in_review: { bg: "var(--color-warning-light)", text: "var(--color-accent-amber)", label: "In Review" },
    signed: { bg: "var(--color-success-light)", text: "var(--color-accent-emerald-light)", label: "Signed" },
  };
  const s = map[status];
  return (
    <span className="text-[9px] px-1.5 py-0.5 rounded-full" style={{ background: s.bg, color: s.text }}>
      {s.label}
    </span>
  );
}

function FilingStatusBadge({ status }: { status: FilingStatus }) {
  const map: Record<FilingStatus, { bg: string; text: string; label: string }> = {
    not_filed: { bg: "var(--color-hover-overlay)", text: "var(--color-text-muted)", label: "Not Filed" },
    filed: { bg: "var(--color-warning-light)", text: "var(--color-accent-amber)", label: "Filed" },
    acknowledged: { bg: "var(--color-success-light)", text: "var(--color-accent-emerald-light)", label: "Acknowledged" },
  };
  const s = map[status];
  return (
    <span className="text-[9px] px-1.5 py-0.5 rounded-full" style={{ background: s.bg, color: s.text }}>
      {s.label}
    </span>
  );
}

function cycleTransactionDocStatus(s: TransactionDocStatus): TransactionDocStatus {
  if (s === "draft") return "in_review";
  if (s === "in_review") return "signed";
  return "draft";
}

function cycleFilingStatus(s: FilingStatus): FilingStatus {
  if (s === "not_filed") return "filed";
  if (s === "filed") return "acknowledged";
  return "not_filed";
}

// ── Document Checklist Component ──

function DocumentChecklist({
  round,
  companyId,
  onAllotment,
  onMessage,
}: {
  round: FundingRound;
  companyId: number;
  onAllotment: () => void;
  onMessage: (msg: string) => void;
}) {
  const [checklist, updateChecklist] = useChecklistState(round.id, companyId);
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set([1]));
  const [draftingDoc, setDraftingDoc] = useState<string | null>(null);

  const toggleStep = (step: number) => {
    setExpandedSteps((prev) => {
      const next = new Set(prev);
      if (next.has(step)) next.delete(step);
      else next.add(step);
      return next;
    });
  };

  const hasForeignInvestor = useMemo(
    () => round.investors?.some((inv) => inv.investor_type === "foreign" || inv.investor_type === "fdi") ?? false,
    [round.investors]
  );

  // Step completion logic
  const stepStatuses = useMemo(() => {
    const s1 = checklist.valuation_status === "complete";
    const s2 = checklist.sha_status === "signed" && checklist.ssa_status === "signed";
    const s3 = checklist.board_meeting_held && checklist.board_resolution_passed && checklist.board_resolution_status === "signed";
    const s4 = checklist.shareholder_approval_status === "sr_passed";
    const s5 =
      checklist.mgt14_filed !== "not_filed" &&
      (checklist.sh7_filed !== "not_filed" || !checklist.sr_capital_increase);
    const s6 =
      checklist.pas4_issued &&
      checklist.allotment_board_resolution &&
      round.allotment_completed === true;
    const s7 =
      checklist.pas3_filed &&
      checklist.share_certificates_issued &&
      (!hasForeignInvestor || checklist.fc_gpr_filed);

    return [s1, s2, s3, s4, s5, s6, s7];
  }, [checklist, round.allotment_completed, hasForeignInvestor]);

  const completedCount = stepStatuses.filter(Boolean).length;

  function getStepIconStatus(stepIndex: number): "complete" | "in_progress" | "not_started" {
    if (stepStatuses[stepIndex]) return "complete";
    // Check if any field in the step has been touched
    if (stepIndex === 0 && checklist.valuation_status !== "not_started") return "in_progress";
    if (stepIndex === 1 && (checklist.sha_status !== "draft" || checklist.ssa_status !== "draft")) return "in_progress";
    if (stepIndex === 2 && (checklist.board_meeting_held || checklist.board_resolution_passed || checklist.board_resolution_status !== "draft")) return "in_progress";
    if (stepIndex === 3 && (checklist.egm_notice_sent || checklist.sr_private_placement)) return "in_progress";
    if (stepIndex === 4 && (checklist.mgt14_filed !== "not_filed" || checklist.sh7_filed !== "not_filed")) return "in_progress";
    if (stepIndex === 5 && (checklist.pas4_issued || checklist.allotment_board_resolution)) return "in_progress";
    if (stepIndex === 6 && (checklist.pas3_filed || checklist.share_certificates_issued || checklist.fc_gpr_filed)) return "in_progress";
    return "not_started";
  }

  function isStepBlocked(stepIndex: number): string | null {
    // Steps 0,1 are never blocked
    if (stepIndex <= 1) return null;
    // Step 2 blocked if step 1 not at least in progress
    if (stepIndex === 2 && checklist.sha_status === "draft" && checklist.ssa_status === "draft") {
      return "Complete transaction documents first";
    }
    // Step 3 blocked if board not approved
    if (stepIndex === 3 && !stepStatuses[2]) return "Board approval required first";
    // Step 4 blocked if shareholder approval not done
    if (stepIndex === 4 && !stepStatuses[3]) return "Shareholder approval required first";
    // Step 5 blocked if regulatory filings not done
    if (stepIndex === 5 && !stepStatuses[4]) return "Complete regulatory filings first";
    // Step 6 blocked if allotment not done
    if (stepIndex === 6 && !stepStatuses[5]) return "Complete offer & allotment first";
    return null;
  }

  async function handleDraftDocument(templateType: string, fieldPrefix: string) {
    setDraftingDoc(templateType);
    try {
      const result = await createLegalDraft({ template_type: templateType, company_id: companyId });
      if (result?.id) {
        updateChecklist({ [`${fieldPrefix}_draft_id`]: result.id } as Partial<ChecklistState>);
      }
      onMessage(`${templateType.toUpperCase().replace(/_/g, " ")} draft created successfully.`);
    } catch (err: any) {
      onMessage(`Error creating draft: ${err.message}`);
    }
    setDraftingDoc(null);
  }

  const stepLabels = [
    "Valuation Report",
    "Transaction Documents",
    "Board Approval",
    "Shareholder Approval",
    "Regulatory Filings",
    "Offer & Allotment",
    "Post-Closing Filings",
  ];

  return (
    <div className="glass-card overflow-hidden" style={{ cursor: "default" }}>
      {/* Header with progress */}
      <div className="p-4" style={{ borderBottom: "1px solid var(--color-border)" }}>
        <div className="flex justify-between items-center mb-2">
          <h3 className="font-semibold text-sm">Document & Compliance Checklist</h3>
          <span className="text-[10px] px-2 py-0.5 rounded-full" style={{ background: "var(--color-purple-bg)", color: "var(--color-accent-purple-light)" }}>
            {completedCount} of 7 complete
          </span>
        </div>
        {/* Progress bar */}
        <div className="w-full h-1.5 rounded-full overflow-hidden" style={{ background: "var(--color-hover-overlay)" }}>
          <div
            className="h-full rounded-full transition-all duration-300"
            style={{
              width: `${Math.round((completedCount / 7) * 100)}%`,
              background: completedCount === 7 ? "var(--color-accent-emerald-light)" : "var(--color-accent-purple-light)",
            }}
          />
        </div>
      </div>

      {/* Steps */}
      <div>
        {stepLabels.map((label, idx) => {
          const stepNum = idx + 1;
          const isExpanded = expandedSteps.has(stepNum);
          const blocked = isStepBlocked(idx);
          const iconStatus = getStepIconStatus(idx);

          return (
            <div key={stepNum} style={{ borderBottom: idx < 6 ? "1px solid var(--color-border)" : undefined }}>
              {/* Step header */}
              <button
                onClick={() => toggleStep(stepNum)}
                className="w-full flex items-center gap-2.5 px-4 py-2.5 text-left transition-colors"
                style={{
                  opacity: blocked ? 0.5 : 1,
                  background: isExpanded ? "var(--color-stripe-alt)" : "transparent",
                }}
              >
                <StepStatusIcon status={iconStatus} />
                <div className="flex-1 min-w-0">
                  <span className="text-xs font-medium">{stepNum}. {label}</span>
                  {blocked && (
                    <div className="text-[9px] mt-0.5" style={{ color: "var(--color-text-muted)" }}>
                      {blocked}
                    </div>
                  )}
                </div>
                <svg
                  className="w-3 h-3 flex-shrink-0 transition-transform"
                  style={{
                    color: "var(--color-text-muted)",
                    transform: isExpanded ? "rotate(180deg)" : "rotate(0deg)",
                  }}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                </svg>
              </button>

              {/* Step content */}
              {isExpanded && !blocked && (
                <div className="px-4 pb-3 pt-0.5" style={{ paddingLeft: "2.75rem" }}>
                  {/* Step 1: Valuation Report */}
                  {stepNum === 1 && (
                    <div className="space-y-2">
                      <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                        Registered valuer&apos;s report (required for private placement pricing)
                      </p>
                      <div className="flex items-center gap-2 flex-wrap">
                        <select
                          value={checklist.valuation_status}
                          onChange={(e) => updateChecklist({ valuation_status: e.target.value as DocStatus })}
                          className="text-[10px] px-2 py-1 rounded-md"
                          style={{
                            background: "var(--color-hover-overlay)",
                            border: "1px solid var(--color-border)",
                            color: "var(--color-text-primary)",
                          }}
                        >
                          <option value="not_started">Not Started</option>
                          <option value="in_progress">In Progress</option>
                          <option value="complete">Complete</option>
                        </select>
                        <Link
                          href="/dashboard/valuations"
                          className="text-[10px] px-2 py-1 rounded-md"
                          style={{
                            background: "var(--color-purple-bg)",
                            border: "1px solid var(--color-purple-bg)",
                            color: "var(--color-accent-purple-light)",
                          }}
                        >
                          Go to Valuations
                        </Link>
                      </div>
                    </div>
                  )}

                  {/* Step 2: Transaction Documents */}
                  {stepNum === 2 && (
                    <div className="space-y-2.5">
                      {/* SHA */}
                      <div className="flex items-center gap-2 flex-wrap">
                        <TransactionDocStatusBadge status={checklist.sha_status} />
                        <span className="text-[10px] flex-1">SHA (Shareholders&apos; Agreement)</span>
                        <SmallActionButton
                          onClick={() => handleDraftDocument("sha", "sha")}
                          disabled={draftingDoc === "sha"}
                        >
                          {draftingDoc === "sha" ? "Drafting..." : "Draft SHA"}
                        </SmallActionButton>
                        <SmallActionButton
                          onClick={() => updateChecklist({ sha_status: cycleTransactionDocStatus(checklist.sha_status) })}
                          variant="amber"
                        >
                          {checklist.sha_status === "draft" ? "Send for Review" : checklist.sha_status === "in_review" ? "Mark Signed" : "Reset"}
                        </SmallActionButton>
                      </div>

                      {/* SSA */}
                      <div className="flex items-center gap-2 flex-wrap">
                        <TransactionDocStatusBadge status={checklist.ssa_status} />
                        <span className="text-[10px] flex-1">SSA (Share Subscription Agreement)</span>
                        <SmallActionButton
                          onClick={() => handleDraftDocument("ssa", "ssa")}
                          disabled={draftingDoc === "ssa"}
                        >
                          {draftingDoc === "ssa" ? "Drafting..." : "Draft SSA"}
                        </SmallActionButton>
                        <SmallActionButton
                          onClick={() => updateChecklist({ ssa_status: cycleTransactionDocStatus(checklist.ssa_status) })}
                          variant="amber"
                        >
                          {checklist.ssa_status === "draft" ? "Send for Review" : checklist.ssa_status === "in_review" ? "Mark Signed" : "Reset"}
                        </SmallActionButton>
                      </div>

                      {/* Amended AOA */}
                      <div className="flex items-center gap-2">
                        <MiniCheckbox
                          checked={checklist.aoa_amended}
                          onChange={(v) => updateChecklist({ aoa_amended: v })}
                        />
                        <span className="text-[10px]" style={{ color: "var(--color-text-secondary)" }}>
                          Amended AOA (if needed)
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Step 3: Board Approval */}
                  {stepNum === 3 && (
                    <div className="space-y-2.5">
                      <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                        Board resolution approving the fundraise
                      </p>
                      <div className="flex items-center gap-2 flex-wrap">
                        <TransactionDocStatusBadge status={checklist.board_resolution_status} />
                        <span className="text-[10px] flex-1">Board Resolution</span>
                        <SmallActionButton
                          onClick={() => handleDraftDocument("board_resolution", "board_resolution")}
                          disabled={draftingDoc === "board_resolution"}
                        >
                          {draftingDoc === "board_resolution" ? "Generating..." : "Generate Board Resolution"}
                        </SmallActionButton>
                        <SmallActionButton
                          onClick={() => updateChecklist({ board_resolution_status: cycleTransactionDocStatus(checklist.board_resolution_status) })}
                          variant="amber"
                        >
                          {checklist.board_resolution_status === "draft" ? "Send for Signing" : checklist.board_resolution_status === "in_review" ? "Mark Signed" : "Reset"}
                        </SmallActionButton>
                      </div>
                      <div className="space-y-1.5 mt-1">
                        <div className="flex items-center gap-2">
                          <MiniCheckbox
                            checked={checklist.board_meeting_held}
                            onChange={(v) => updateChecklist({ board_meeting_held: v })}
                          />
                          <span className="text-[10px]">Board meeting held</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <MiniCheckbox
                            checked={checklist.board_resolution_passed}
                            onChange={(v) => updateChecklist({ board_resolution_passed: v })}
                          />
                          <span className="text-[10px]">Resolution passed</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Step 4: Shareholder Approval */}
                  {stepNum === 4 && (
                    <div className="space-y-2.5">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] font-medium">Status:</span>
                        <span
                          className="text-[9px] px-1.5 py-0.5 rounded-full"
                          style={{
                            background:
                              checklist.shareholder_approval_status === "sr_passed"
                                ? "var(--color-success-light)"
                                : "var(--color-warning-light)",
                            color:
                              checklist.shareholder_approval_status === "sr_passed"
                                ? "var(--color-accent-emerald-light)"
                                : "var(--color-accent-amber)",
                          }}
                        >
                          {checklist.shareholder_approval_status === "sr_passed" ? "SR Passed" : "Pending"}
                        </span>
                      </div>
                      <div className="space-y-1.5">
                        <div className="flex items-center gap-2">
                          <MiniCheckbox
                            checked={checklist.egm_notice_sent}
                            onChange={(v) => updateChecklist({ egm_notice_sent: v })}
                          />
                          <span className="text-[10px]">EGM notice sent (14 clear days)</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <MiniCheckbox
                            checked={checklist.sr_private_placement}
                            onChange={(v) => updateChecklist({ sr_private_placement: v })}
                          />
                          <span className="text-[10px]">Special Resolution for private placement</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <MiniCheckbox
                            checked={checklist.sr_aoa_amendment}
                            onChange={(v) => updateChecklist({ sr_aoa_amendment: v })}
                          />
                          <span className="text-[10px]" style={{ color: "var(--color-text-secondary)" }}>
                            Special Resolution for AOA amendment (if applicable)
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <MiniCheckbox
                            checked={checklist.sr_capital_increase}
                            onChange={(v) => updateChecklist({ sr_capital_increase: v })}
                          />
                          <span className="text-[10px]" style={{ color: "var(--color-text-secondary)" }}>
                            Special Resolution for capital increase (if applicable)
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 mt-1 flex-wrap">
                        <SmallActionButton
                          onClick={() => {
                            handleDraftDocument("egm_notice", "egm_notice");
                            updateChecklist({ egm_notice_sent: true });
                          }}
                        >
                          Generate EGM Notice
                        </SmallActionButton>
                        {checklist.sr_private_placement && (
                          <SmallActionButton
                            onClick={() => updateChecklist({ shareholder_approval_status: checklist.shareholder_approval_status === "pending" ? "sr_passed" : "pending" })}
                            variant="green"
                          >
                            {checklist.shareholder_approval_status === "pending" ? "Mark SR Passed" : "Revert to Pending"}
                          </SmallActionButton>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Step 5: Regulatory Filings */}
                  {stepNum === 5 && (
                    <div className="space-y-2.5">
                      {/* MGT-14 */}
                      <div className="flex items-center gap-2 flex-wrap">
                        <FilingStatusBadge status={checklist.mgt14_filed} />
                        <span className="text-[10px] flex-1">MGT-14 (within 30 days of SR)</span>
                        <SmallActionButton
                          onClick={() => updateChecklist({ mgt14_filed: cycleFilingStatus(checklist.mgt14_filed) })}
                          variant="amber"
                        >
                          {checklist.mgt14_filed === "not_filed" ? "Mark Filed" : checklist.mgt14_filed === "filed" ? "Acknowledged" : "Reset"}
                        </SmallActionButton>
                      </div>

                      {/* SH-7 */}
                      {checklist.sr_capital_increase && (
                        <div className="space-y-1.5">
                          <div className="flex items-center gap-2 flex-wrap">
                            <FilingStatusBadge status={checklist.sh7_filed} />
                            <span className="text-[10px] flex-1">SH-7 (capital increase)</span>
                            <SmallActionButton
                              onClick={() => updateChecklist({ sh7_filed: cycleFilingStatus(checklist.sh7_filed) })}
                              variant="amber"
                            >
                              {checklist.sh7_filed === "not_filed" ? "Mark Filed" : checklist.sh7_filed === "filed" ? "Acknowledged" : "Reset"}
                            </SmallActionButton>
                          </div>
                          <div className="flex items-center gap-2 pl-1">
                            <label className="text-[9px]" style={{ color: "var(--color-text-muted)" }}>Amount:</label>
                            <input
                              type="text"
                              value={checklist.sh7_amount}
                              onChange={(e) => updateChecklist({ sh7_amount: e.target.value })}
                              placeholder="Capital increase amount"
                              className="text-[10px] px-2 py-0.5 rounded-md flex-1"
                              style={{
                                background: "var(--color-hover-overlay)",
                                border: "1px solid var(--color-border)",
                                color: "var(--color-text-primary)",
                                maxWidth: "160px",
                              }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Step 6: Offer & Allotment */}
                  {stepNum === 6 && (
                    <div className="space-y-2.5">
                      <div className="flex items-center gap-2">
                        <MiniCheckbox
                          checked={checklist.pas4_issued}
                          onChange={(v) => updateChecklist({ pas4_issued: v })}
                        />
                        <span className="text-[10px]">PAS-4 offer letters issued</span>
                      </div>

                      {/* Per-investor funds received */}
                      {round.investors && round.investors.length > 0 && (
                        <div className="space-y-1 pl-1">
                          <span className="text-[9px] font-medium" style={{ color: "var(--color-text-muted)" }}>
                            Funds received per investor:
                          </span>
                          {round.investors.map((inv) => (
                            <div key={inv.id} className="flex items-center gap-2">
                              <MiniCheckbox
                                checked={checklist.funds_received_investors[inv.id] ?? inv.funds_received}
                                onChange={(v) =>
                                  updateChecklist({
                                    funds_received_investors: {
                                      ...checklist.funds_received_investors,
                                      [inv.id]: v,
                                    },
                                  })
                                }
                              />
                              <span className="text-[10px]">{inv.investor_name}</span>
                              <span className="text-[9px] font-mono" style={{ color: "var(--color-text-muted)" }}>
                                {formatCurrency(inv.investment_amount)}
                              </span>
                            </div>
                          ))}
                        </div>
                      )}

                      <div className="flex items-center gap-2">
                        <MiniCheckbox
                          checked={checklist.allotment_board_resolution}
                          onChange={(v) => updateChecklist({ allotment_board_resolution: v })}
                        />
                        <span className="text-[10px]">Board resolution for allotment</span>
                      </div>

                      <div className="flex items-center gap-2 mt-1">
                        {!round.allotment_completed ? (
                          <SmallActionButton
                            onClick={onAllotment}
                            variant="green"
                            disabled={!checklist.pas4_issued || !checklist.allotment_board_resolution}
                          >
                            Complete Allotment
                          </SmallActionButton>
                        ) : (
                          <span
                            className="text-[10px] px-2 py-1 rounded-md"
                            style={{ background: "var(--color-success-light)", color: "var(--color-accent-emerald-light)" }}
                          >
                            Allotment Complete
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Step 7: Post-Closing Filings */}
                  {stepNum === 7 && (
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-2">
                        <MiniCheckbox
                          checked={checklist.pas3_filed}
                          onChange={(v) => updateChecklist({ pas3_filed: v })}
                        />
                        <span className="text-[10px]">PAS-3 filed (within 30 days of allotment)</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <MiniCheckbox
                          checked={checklist.share_certificates_issued}
                          onChange={(v) => updateChecklist({ share_certificates_issued: v })}
                        />
                        <span className="text-[10px]">Share certificates issued</span>
                      </div>
                      {hasForeignInvestor && (
                        <div className="flex items-center gap-2">
                          <MiniCheckbox
                            checked={checklist.fc_gpr_filed}
                            onChange={(v) => updateChecklist({ fc_gpr_filed: v })}
                          />
                          <span className="text-[10px]">FC-GPR filed (foreign investor)</span>
                        </div>
                      )}
                      <div className="flex items-center gap-2">
                        <MiniCheckbox checked={round.allotment_completed} onChange={() => {}} disabled />
                        <span className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                          Cap table updated {round.allotment_completed ? "(auto-checked)" : "(pending allotment)"}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

const STATUS_COLORS: Record<string, { bg: string; text: string }> = {
  draft: { bg: "var(--color-hover-overlay)", text: "var(--color-text-muted)" },
  term_sheet: { bg: "var(--color-purple-bg)", text: "var(--color-accent-purple-light)" },
  due_diligence: { bg: "var(--color-info-light)", text: "var(--color-accent-blue)" },
  documentation: { bg: "rgba(99, 102, 241, 0.15)", text: "rgb(99, 102, 241)" },
  closing: { bg: "var(--color-warning-light)", text: "var(--color-accent-amber)" },
  closed: { bg: "var(--color-success-light)", text: "var(--color-accent-emerald-light)" },
  cancelled: { bg: "var(--color-error-light)", text: "var(--color-accent-rose)" },
};

const INSTRUMENT_LABELS: Record<string, string> = {
  equity: "Equity",
  ccps: "CCPS",
  ccd: "CCD",
  safe: "SAFE",
  convertible_note: "Convertible Note",
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

function formatCurrency(val: number): string {
  if (val >= 10000000) return `Rs ${(val / 10000000).toFixed(2)} Cr`;
  if (val >= 100000) return `Rs ${(val / 100000).toFixed(2)} L`;
  return `Rs ${val.toLocaleString()}`;
}

export default function FundraisingPage() {
  const { user, loading: authLoading } = useAuth();
  const [companies, setCompanies] = useState<any[]>([]);
  const [companyId, setCompanyId] = useState<number | null>(null);
  const [rounds, setRounds] = useState<FundingRound[]>([]);
  const [selectedRound, setSelectedRound] = useState<FundingRound | null>(null);
  const [closingRoom, setClosingRoom] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  // Create round modal
  const [showCreateRound, setShowCreateRound] = useState(false);
  const [roundForm, setRoundForm] = useState({
    round_name: "",
    instrument_type: "equity",
    pre_money_valuation: "",
    target_amount: "",
    price_per_share: "",
    notes: "",
  });

  // Conversion state
  const [conversionPreview, setConversionPreview] = useState<any>(null);
  const [triggerRoundId, setTriggerRoundId] = useState<string>("");
  const [converting, setConverting] = useState(false);
  const [showConversionConfirm, setShowConversionConfirm] = useState(false);

  // Edit round state
  const [showEditRound, setShowEditRound] = useState(false);
  const [editRoundForm, setEditRoundForm] = useState({
    round_name: "",
    pre_money_valuation: "",
    target_amount: "",
    price_per_share: "",
    valuation_cap: "",
    discount_rate: "",
    interest_rate: "",
    maturity_months: "",
    notes: "",
  });

  // Deal sharing state
  const [showShareDeal, setShowShareDeal] = useState(false);
  const [shareDealEmail, setShareDealEmail] = useState("");
  const [shareDealMessage, setShareDealMessage] = useState("");
  const [sharedDeals, setSharedDeals] = useState<any[]>([]);
  const [sharingDeal, setSharingDeal] = useState(false);

  // Add investor modal
  const [showAddInvestor, setShowAddInvestor] = useState(false);
  const [investorForm, setInvestorForm] = useState({
    investor_name: "",
    investor_email: "",
    investor_type: "angel",
    investor_entity: "",
    investment_amount: "",
    share_type: "equity",
  });

  // Fetch companies
  useEffect(() => {
    if (authLoading || !user) return;
    getCompanies()
      .then((comps) => {
        setCompanies(comps);
        if (comps.length > 0) setCompanyId(comps[0].id);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [user, authLoading]);

  useEffect(() => {
    fetchRounds();
  }, [companyId]);

  async function fetchRounds() {
    if (!companyId) return;
    setLoading(true);
    try {
      const data = await getFundingRounds(companyId);
      setRounds(data);
    } catch {
      // Backend may not be running
    }
    setLoading(false);
  }

  async function fetchRoundDetail(roundId: number) {
    if (!companyId) return;
    try {
      const data = await getFundingRound(companyId, roundId);
      setSelectedRound(data);
      // Also fetch closing room status if in closing/closed state
      if (data.status === "closing" || data.status === "closed") {
        try {
          const cr = await getClosingRoom(companyId, roundId);
          setClosingRoom(cr);
        } catch {
          setClosingRoom(null);
        }
      } else {
        setClosingRoom(null);
      }
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleCreateRound(e: React.FormEvent) {
    e.preventDefault();
    if (!companyId) return;
    setMessage("");
    try {
      await createFundingRound(companyId, {
        round_name: roundForm.round_name,
        instrument_type: roundForm.instrument_type,
        pre_money_valuation: roundForm.pre_money_valuation ? parseFloat(roundForm.pre_money_valuation) : undefined,
        target_amount: roundForm.target_amount ? parseFloat(roundForm.target_amount) : undefined,
        price_per_share: roundForm.price_per_share ? parseFloat(roundForm.price_per_share) : undefined,
        notes: roundForm.notes || undefined,
      });
      setMessage("Round created successfully!");
      setShowCreateRound(false);
      setRoundForm({
        round_name: "",
        instrument_type: "equity",
        pre_money_valuation: "",
        target_amount: "",
        price_per_share: "",
        notes: "",
      });
      fetchRounds();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleAddInvestor(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedRound || !companyId) return;
    setMessage("");
    try {
      await addRoundInvestor(companyId, selectedRound.id, {
        investor_name: investorForm.investor_name,
        investor_email: investorForm.investor_email || undefined,
        investor_type: investorForm.investor_type,
        investor_entity: investorForm.investor_entity || undefined,
        investment_amount: parseFloat(investorForm.investment_amount),
        share_type: investorForm.share_type,
      });
      setMessage("Investor added!");
      setShowAddInvestor(false);
      setInvestorForm({
        investor_name: "",
        investor_email: "",
        investor_type: "angel",
        investor_entity: "",
        investment_amount: "",
        share_type: "equity",
      });
      fetchRoundDetail(selectedRound.id);
      fetchRounds();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleToggleFlag(investorId: number, field: string, value: boolean) {
    if (!selectedRound || !companyId) return;
    try {
      await updateRoundInvestor(companyId, selectedRound.id, investorId, {
        [field]: value,
      });
      fetchRoundDetail(selectedRound.id);
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleRemoveInvestor(investorId: number) {
    if (!selectedRound || !companyId) return;
    try {
      await removeRoundInvestor(companyId, selectedRound.id, investorId);
      setMessage("Investor removed");
      fetchRoundDetail(selectedRound.id);
      fetchRounds();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleInitiateClosing() {
    if (!selectedRound || !companyId) return;
    setMessage("");
    try {
      await initiateClosing(companyId, selectedRound.id, {
        documents_to_sign: ["sha", "ssa"],
      });
      setMessage("Closing room initiated! Documents sent for signing.");
      fetchRoundDetail(selectedRound.id);
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleCompleteAllotment() {
    if (!selectedRound || !companyId) return;
    setMessage("");
    try {
      await completeAllotment(companyId, selectedRound.id);
      setMessage("Shares allotted! Cap table updated.");
      fetchRoundDetail(selectedRound.id);
      fetchRounds();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  // ── Edit round ──
  function openEditRound() {
    if (!selectedRound) return;
    setEditRoundForm({
      round_name: selectedRound.round_name || "",
      pre_money_valuation: selectedRound.pre_money_valuation?.toString() || "",
      target_amount: selectedRound.target_amount?.toString() || "",
      price_per_share: selectedRound.price_per_share?.toString() || "",
      valuation_cap: selectedRound.valuation_cap?.toString() || "",
      discount_rate: selectedRound.discount_rate?.toString() || "",
      interest_rate: selectedRound.interest_rate?.toString() || "",
      maturity_months: selectedRound.maturity_months?.toString() || "",
      notes: selectedRound.notes || "",
    });
    setShowEditRound(true);
  }

  async function handleUpdateRound(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedRound || !companyId) return;
    setMessage("");
    try {
      const payload: any = { round_name: editRoundForm.round_name };
      if (editRoundForm.pre_money_valuation) payload.pre_money_valuation = parseFloat(editRoundForm.pre_money_valuation);
      if (editRoundForm.target_amount) payload.target_amount = parseFloat(editRoundForm.target_amount);
      if (editRoundForm.price_per_share) payload.price_per_share = parseFloat(editRoundForm.price_per_share);
      if (editRoundForm.valuation_cap) payload.valuation_cap = parseFloat(editRoundForm.valuation_cap);
      if (editRoundForm.discount_rate) payload.discount_rate = parseFloat(editRoundForm.discount_rate);
      if (editRoundForm.interest_rate) payload.interest_rate = parseFloat(editRoundForm.interest_rate);
      if (editRoundForm.maturity_months) payload.maturity_months = parseInt(editRoundForm.maturity_months);
      if (editRoundForm.notes) payload.notes = editRoundForm.notes;
      await updateFundingRound(companyId, selectedRound.id, payload);
      setMessage("Round updated successfully.");
      setShowEditRound(false);
      fetchRoundDetail(selectedRound.id);
      fetchRounds();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  // ── Deal sharing ──
  async function fetchSharedDeals() {
    if (!companyId) return;
    try {
      const data = await listSharedDeals(companyId);
      setSharedDeals(data.shared_deals || data || []);
    } catch {
      // silently fail
    }
  }

  async function handleShareDeal(e: React.FormEvent) {
    e.preventDefault();
    if (!companyId || !shareDealEmail.trim()) return;
    setSharingDeal(true);
    setMessage("");
    try {
      await shareDeal(companyId, {
        investor_email: shareDealEmail.trim(),
        message: shareDealMessage.trim() || undefined,
      });
      setMessage("Deal shared successfully.");
      setShareDealEmail("");
      setShareDealMessage("");
      fetchSharedDeals();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
    setSharingDeal(false);
  }

  async function handleRevokeDeal(shareId: number) {
    if (!companyId) return;
    try {
      await revokeSharedDeal(companyId, shareId);
      setMessage("Deal access revoked.");
      fetchSharedDeals();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  const isConvertible = (type: string) =>
    ["safe", "ccd", "convertible_note", "ccps"].includes(type);

  const equityRounds = rounds.filter(
    (r) => r.instrument_type === "equity" && r.id !== selectedRound?.id
  );

  async function handlePreviewConversion() {
    if (!selectedRound || !companyId) return;
    setMessage("");
    try {
      const data = await previewConversion(
        companyId,
        selectedRound.id,
        triggerRoundId ? parseInt(triggerRoundId) : undefined
      );
      setConversionPreview(data);
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleExecuteConversion() {
    if (!selectedRound || !companyId) return;
    setConverting(true);
    setMessage("");
    try {
      await convertRound(companyId, selectedRound.id, {
        trigger_round_id: triggerRoundId ? parseInt(triggerRoundId) : undefined,
      });
      setMessage("Conversion complete! Shares have been allotted to the cap table.");
      setConversionPreview(null);
      setShowConversionConfirm(false);
      fetchRoundDetail(selectedRound.id);
      fetchRounds();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
    setConverting(false);
  }

  return (
    <FeatureGate
      moduleKey="fundraising"
      featureName="Fundraising Rounds"
      featureDescription="Create and manage funding rounds, track investors, and execute closings."
    >
    <div>
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="badge badge-purple mb-4 mx-auto w-fit">Fundraising Engine</div>
          <h1 className="text-3xl md:text-4xl font-bold mb-3" style={{ fontFamily: "var(--font-display)" }}>
            <span className="gradient-text">Fundraising</span>
          </h1>
          <p className="text-base" style={{ color: "var(--color-text-secondary)" }}>
            Manage funding rounds, track investors, and close deals.
          </p>
        </div>

        {/* Company selector */}
        {companies.length > 1 && (
          <div className="flex justify-center mb-6">
            <select
              className="glass-card text-sm px-3 py-2 rounded-lg border-none outline-none"
              style={{ background: "var(--color-bg-card)", color: "var(--color-text-primary)" }}
              value={companyId || ""}
              onChange={(e) => { setCompanyId(Number(e.target.value)); setSelectedRound(null); }}
            >
              {companies.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.approved_name || c.proposed_names?.[0] || `Company #${c.id}`}
                </option>
              ))}
            </select>
          </div>
        )}

        {message && (
          <div
            className="glass-card p-3 mb-6 text-center text-sm"
            style={{
              borderColor: message.startsWith("Error") ? "var(--color-accent-rose)" : "var(--color-accent-emerald-light)",
              cursor: "default",
            }}
          >
            {message}
          </div>
        )}

        {loading && (
          <div className="text-center py-12" style={{ color: "var(--color-text-muted)" }}>Loading...</div>
        )}

        {/* Two-panel layout: rounds list + detail */}
        {!loading && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left: Rounds List */}
            <div className="lg:col-span-1">
              <div className="flex justify-between items-center mb-4">
                <h2 className="font-semibold">Rounds</h2>
                <button onClick={() => setShowCreateRound(true)} className="text-xs px-3 py-1.5 rounded-lg" style={{ background: "var(--color-purple-bg)", border: "1px solid var(--color-purple-bg)", color: "var(--color-accent-purple-light)" }}>
                  + New Round
                </button>
              </div>

              {rounds.length === 0 ? (
                <div className="glass-card p-8 text-center" style={{ cursor: "default" }}>
                  <div className="text-3xl mb-3">&#128176;</div>
                  <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>No funding rounds yet.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {rounds.map((round) => {
                    const progressPct = round.target_amount && round.target_amount > 0
                      ? Math.min(100, Math.round((round.amount_raised / round.target_amount) * 100))
                      : 0;
                    return (
                      <button
                        key={round.id}
                        onClick={() => fetchRoundDetail(round.id)}
                        className="glass-card p-4 w-full text-left transition-all"
                        style={{
                          borderColor: selectedRound?.id === round.id ? "var(--color-accent-purple-light)" : "var(--color-border)",
                          background: selectedRound?.id === round.id ? "var(--color-purple-bg)" : undefined,
                        }}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <div className="font-semibold text-sm">{round.round_name}</div>
                            <div className="text-[10px] mt-0.5" style={{ color: "var(--color-text-muted)" }}>
                              {INSTRUMENT_LABELS[round.instrument_type] || round.instrument_type}
                              {round.investor_count !== undefined && ` | ${round.investor_count} investor(s)`}
                            </div>
                          </div>
                          <StatusBadge status={round.status} />
                        </div>
                        {round.target_amount && round.target_amount > 0 && (
                          <div>
                            <div className="flex justify-between text-[10px] mb-1" style={{ color: "var(--color-text-muted)" }}>
                              <span>{formatCurrency(round.amount_raised)}</span>
                              <span>{formatCurrency(round.target_amount)}</span>
                            </div>
                            <div className="w-full h-1.5 rounded-full overflow-hidden" style={{ background: "var(--color-hover-overlay)" }}>
                              <div className="h-full rounded-full" style={{ width: `${progressPct}%`, background: "var(--color-accent-purple-light)" }} />
                            </div>
                          </div>
                        )}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Right: Round Detail */}
            <div className="lg:col-span-2">
              {!selectedRound ? (
                <div className="glass-card p-12 text-center" style={{ cursor: "default" }}>
                  <div className="text-4xl mb-4">&#128200;</div>
                  <h3 className="text-lg font-semibold mb-2">Select a Round</h3>
                  <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                    Click on a round from the list to view details, manage investors, and track closing.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Round Header */}
                  <div className="glass-card p-5" style={{ cursor: "default" }}>
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h2 className="text-xl font-bold">{selectedRound.round_name}</h2>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: "var(--color-purple-bg)", color: "var(--color-accent-purple-light)" }}>
                            {INSTRUMENT_LABELS[selectedRound.instrument_type] || selectedRound.instrument_type}
                          </span>
                          <StatusBadge status={selectedRound.status} />
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={openEditRound}
                          className="text-xs px-3 py-1.5 rounded-lg transition-colors"
                          style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-secondary)" }}
                        >
                          Edit Round
                        </button>
                        <button
                          onClick={() => { setShowShareDeal(true); fetchSharedDeals(); }}
                          className="text-xs px-3 py-1.5 rounded-lg transition-colors"
                          style={{ background: "var(--color-purple-bg)", border: "1px solid var(--color-purple-bg)", color: "var(--color-accent-purple-light)" }}
                        >
                          Share Deal
                        </button>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {selectedRound.pre_money_valuation != null && (
                        <div className="text-center">
                          <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Pre-Money</div>
                          <div className="text-sm font-bold">{formatCurrency(selectedRound.pre_money_valuation)}</div>
                        </div>
                      )}
                      <div className="text-center">
                        <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Raised</div>
                        <div className="text-sm font-bold" style={{ color: "var(--color-accent-emerald-light)" }}>
                          {formatCurrency(selectedRound.amount_raised)}
                        </div>
                      </div>
                      {selectedRound.post_money_valuation != null && (
                        <div className="text-center">
                          <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Post-Money</div>
                          <div className="text-sm font-bold">{formatCurrency(selectedRound.post_money_valuation)}</div>
                        </div>
                      )}
                      {selectedRound.price_per_share != null && (
                        <div className="text-center">
                          <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Price/Share</div>
                          <div className="text-sm font-bold">Rs {selectedRound.price_per_share.toFixed(2)}</div>
                        </div>
                      )}
                    </div>

                    {/* Funding Progress Ring */}
                    {selectedRound.target_amount != null && selectedRound.target_amount > 0 && (() => {
                      const fundedPct = Math.min(100, Math.round((selectedRound.amount_raised / selectedRound.target_amount!) * 100));
                      const progressData = [
                        { name: "Funded", value: fundedPct },
                        { name: "Remaining", value: 100 - fundedPct },
                      ];
                      return (
                        <div className="mt-4 pt-4" style={{ borderTop: "1px solid var(--color-border)" }}>
                          <div className="flex items-center gap-4">
                            <div className="relative" style={{ width: 80, height: 80 }}>
                              <PieChart width={80} height={80}>
                                <Pie
                                  data={progressData}
                                  cx={35}
                                  cy={35}
                                  innerRadius={24}
                                  outerRadius={35}
                                  startAngle={90}
                                  endAngle={-270}
                                  dataKey="value"
                                  stroke="none"
                                >
                                  <Cell fill="#8B5CF6" />
                                  <Cell fill="#374151" />
                                </Pie>
                              </PieChart>
                              <div
                                className="absolute inset-0 flex items-center justify-center text-xs font-bold"
                                style={{ color: "#8B5CF6" }}
                              >
                                {fundedPct}%
                              </div>
                            </div>
                            <div className="flex-1">
                              <div className="flex justify-between text-xs mb-1" style={{ color: "#9CA3AF" }}>
                                <span>Raised: {formatCurrency(selectedRound.amount_raised)}</span>
                                <span>Target: {formatCurrency(selectedRound.target_amount!)}</span>
                              </div>
                              <div className="w-full h-1.5 rounded-full overflow-hidden" style={{ background: "#374151" }}>
                                <div className="h-full rounded-full transition-all" style={{ width: `${fundedPct}%`, background: "#8B5CF6" }} />
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })()}
                  </div>

                  {/* Convertible Conversion Section */}
                  {isConvertible(selectedRound.instrument_type) && !selectedRound.allotment_completed && (
                    <div className="glass-card p-5" style={{ cursor: "default" }}>
                      <div className="flex items-center gap-2 mb-4">
                        <h3 className="font-semibold">Convert to Equity</h3>
                        <span className="text-[10px] px-2 py-0.5 rounded-full" style={{ background: "var(--color-warning-light)", color: "var(--color-accent-amber)" }}>
                          {INSTRUMENT_LABELS[selectedRound.instrument_type]}
                        </span>
                      </div>

                      {/* Convertible terms summary */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4 p-3 rounded-lg" style={{ background: "var(--color-stripe-alt)", border: "1px solid var(--color-border)" }}>
                        {selectedRound.valuation_cap != null && (
                          <div className="text-center">
                            <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Valuation Cap</div>
                            <div className="text-sm font-bold">{formatCurrency(selectedRound.valuation_cap)}</div>
                          </div>
                        )}
                        {selectedRound.discount_rate != null && (
                          <div className="text-center">
                            <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Discount Rate</div>
                            <div className="text-sm font-bold">{selectedRound.discount_rate}%</div>
                          </div>
                        )}
                        {selectedRound.interest_rate != null && (
                          <div className="text-center">
                            <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Interest Rate</div>
                            <div className="text-sm font-bold">{selectedRound.interest_rate}%</div>
                          </div>
                        )}
                        {selectedRound.maturity_months != null && (
                          <div className="text-center">
                            <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Maturity</div>
                            <div className="text-sm font-bold">{selectedRound.maturity_months} months</div>
                          </div>
                        )}
                        {!selectedRound.valuation_cap && !selectedRound.discount_rate && !selectedRound.interest_rate && !selectedRound.maturity_months && (
                          <div className="col-span-4 text-center text-xs" style={{ color: "var(--color-text-muted)" }}>
                            No convertible terms set.{" "}
                            <button
                              onClick={openEditRound}
                              className="underline font-semibold"
                              style={{ color: "var(--color-accent-purple-light)" }}
                            >
                              Edit the round
                            </button>{" "}
                            to add valuation cap, discount rate, etc.
                          </div>
                        )}
                      </div>

                      {/* Trigger round selector */}
                      <div className="flex flex-wrap items-end gap-3 mb-4">
                        <div className="flex-1 min-w-[200px]">
                          <label className="block text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>
                            Trigger Round (equity round that sets price)
                          </label>
                          <select
                            value={triggerRoundId}
                            onChange={(e) => { setTriggerRoundId(e.target.value); setConversionPreview(null); }}
                            className="w-full px-3 py-2 rounded-lg text-sm"
                            style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                          >
                            <option value="">None (use valuation cap only)</option>
                            {equityRounds.map((r) => (
                              <option key={r.id} value={r.id.toString()}>
                                {r.round_name} {r.price_per_share ? `(Rs ${r.price_per_share}/share)` : ""}
                              </option>
                            ))}
                          </select>
                        </div>
                        <button
                          onClick={handlePreviewConversion}
                          className="text-sm px-4 py-2 rounded-lg"
                          style={{ background: "var(--color-purple-bg)", border: "1px solid var(--color-purple-bg)", color: "var(--color-accent-purple-light)" }}
                        >
                          Preview Conversion
                        </button>
                      </div>

                      {/* Conversion preview results */}
                      {conversionPreview && (
                        <div>
                          <div className="grid grid-cols-3 gap-3 mb-4">
                            <div className="p-3 rounded-lg text-center" style={{ background: "var(--color-purple-bg)", border: "1px solid var(--color-purple-bg)" }}>
                              <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Trigger Price</div>
                              <div className="text-sm font-bold">
                                {conversionPreview.trigger_price_per_share ? `Rs ${conversionPreview.trigger_price_per_share}` : "N/A"}
                              </div>
                            </div>
                            <div className="p-3 rounded-lg text-center" style={{ background: "var(--color-purple-bg)", border: "1px solid var(--color-purple-bg)" }}>
                              <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Existing Shares</div>
                              <div className="text-sm font-bold">{conversionPreview.total_existing_shares?.toLocaleString()}</div>
                            </div>
                            <div className="p-3 rounded-lg text-center" style={{ background: "var(--color-purple-bg)", border: "1px solid var(--color-purple-bg)" }}>
                              <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Total New Shares</div>
                              <div className="text-sm font-bold">
                                {conversionPreview.conversions?.reduce((s: number, c: any) => s + c.shares_issued, 0)?.toLocaleString()}
                              </div>
                            </div>
                          </div>

                          <div className="overflow-x-auto rounded-lg" style={{ border: "1px solid var(--color-border)" }}>
                            <table className="w-full text-sm">
                              <thead>
                                <tr style={{ borderBottom: "1px solid var(--color-border)", background: "var(--color-stripe-alt)" }}>
                                  <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Investor</th>
                                  <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Principal</th>
                                  <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Interest</th>
                                  <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Total</th>
                                  <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Price/Share</th>
                                  <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Method</th>
                                  <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Shares</th>
                                </tr>
                              </thead>
                              <tbody>
                                {conversionPreview.conversions?.map((c: any) => (
                                  <tr key={c.investor_id} style={{ borderBottom: "1px solid var(--color-border)" }}>
                                    <td className="p-3 font-medium">{c.investor_name}</td>
                                    <td className="p-3 text-right font-mono">{formatCurrency(c.principal)}</td>
                                    <td className="p-3 text-right font-mono">{c.interest_accrued > 0 ? formatCurrency(c.interest_accrued) : "-"}</td>
                                    <td className="p-3 text-right font-mono">{formatCurrency(c.total_amount)}</td>
                                    <td className="p-3 text-right font-mono">Rs {c.conversion_price}</td>
                                    <td className="p-3">
                                      <span className="text-xs px-2 py-0.5 rounded-full capitalize" style={{ background: "var(--color-purple-bg)", color: "var(--color-accent-purple-light)" }}>
                                        {c.conversion_method?.replace(/_/g, " ")}
                                      </span>
                                    </td>
                                    <td className="p-3 text-right font-bold" style={{ color: "var(--color-accent-emerald-light)" }}>{c.shares_issued?.toLocaleString()}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>

                          {/* All available conversion prices per investor */}
                          {conversionPreview.conversions?.length > 0 && conversionPreview.conversions[0].all_prices && (
                            <div className="mt-3 p-3 rounded-lg text-xs" style={{ background: "var(--color-stripe-alt)", border: "1px solid var(--color-border)" }}>
                              <span style={{ color: "var(--color-text-muted)" }}>Available prices: </span>
                              {Object.entries(conversionPreview.conversions[0].all_prices as Record<string, number>).map(([method, price]) => (
                                <span key={method} className="mr-3">
                                  <span className="capitalize">{method.replace(/_/g, " ")}</span>: <span className="font-mono">Rs {price}</span>
                                </span>
                              ))}
                            </div>
                          )}

                          {/* Execute conversion button */}
                          <div className="mt-4 flex items-center gap-3">
                            {!showConversionConfirm ? (
                              <button
                                onClick={() => setShowConversionConfirm(true)}
                                className="btn-primary text-sm"
                              >
                                Execute Conversion
                              </button>
                            ) : (
                              <>
                                <span className="text-sm" style={{ color: "var(--color-accent-amber)" }}>
                                  This will create new shareholders on the cap table. Continue?
                                </span>
                                <button
                                  onClick={handleExecuteConversion}
                                  disabled={converting}
                                  className="text-sm px-4 py-2 rounded-lg"
                                  style={{ background: "var(--color-success-light)", border: "1px solid var(--color-accent-emerald-light)", color: "var(--color-accent-emerald-light)" }}
                                >
                                  {converting ? "Converting..." : "Confirm Conversion"}
                                </button>
                                <button
                                  onClick={() => setShowConversionConfirm(false)}
                                  className="text-sm px-3 py-2 rounded-lg"
                                  style={{ color: "var(--color-text-muted)" }}
                                >
                                  Cancel
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Investor Contribution Bar Chart */}
                  {selectedRound.investors && selectedRound.investors.length >= 2 && (() => {
                    const chartData = selectedRound.investors!
                      .map((inv) => ({
                        name: inv.investor_name,
                        amount: inv.investment_amount,
                      }))
                      .sort((a, b) => b.amount - a.amount);
                    return (
                      <div className="glass-card p-5" style={{ cursor: "default" }}>
                        <h3 className="font-semibold mb-4">Investor Contributions</h3>
                        <ResponsiveContainer width="100%" height={Math.max(200, chartData.length * 44)}>
                          <BarChart data={chartData} layout="vertical" margin={{ top: 0, right: 20, bottom: 0, left: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={false} />
                            <XAxis
                              type="number"
                              tick={{ fill: "#9CA3AF", fontSize: 11 }}
                              axisLine={{ stroke: "#374151" }}
                              tickLine={{ stroke: "#374151" }}
                              tickFormatter={(v: number) => {
                                if (v >= 10000000) return `${(v / 10000000).toFixed(1)}Cr`;
                                if (v >= 100000) return `${(v / 100000).toFixed(1)}L`;
                                if (v >= 1000) return `${(v / 1000).toFixed(0)}K`;
                                return String(v);
                              }}
                            />
                            <YAxis
                              type="category"
                              dataKey="name"
                              width={120}
                              tick={{ fill: "#9CA3AF", fontSize: 12 }}
                              axisLine={{ stroke: "#374151" }}
                              tickLine={false}
                            />
                            <Tooltip
                              contentStyle={{ background: "#1a1a2e", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8 }}
                              labelStyle={{ color: "#9CA3AF" }}
                              formatter={(value) => [formatCurrency(Number(value)), "Investment"]}
                              cursor={{ fill: "rgba(139,92,246,0.1)" }}
                            />
                            <Bar dataKey="amount" fill="#8B5CF6" radius={[0, 4, 4, 0]} barSize={24} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    );
                  })()}

                  {/* Investors Table */}
                  <div className="glass-card overflow-hidden" style={{ cursor: "default" }}>
                    <div className="p-4 flex justify-between items-center" style={{ borderBottom: "1px solid var(--color-border)" }}>
                      <h3 className="font-semibold">Investors ({selectedRound.investors?.length || 0})</h3>
                      {selectedRound.status !== "closed" && selectedRound.status !== "cancelled" && (
                        <button
                          onClick={() => setShowAddInvestor(true)}
                          className="text-xs px-3 py-1.5 rounded-lg"
                          style={{ background: "var(--color-purple-bg)", border: "1px solid var(--color-purple-bg)", color: "var(--color-accent-purple-light)" }}
                        >
                          + Add Investor
                        </button>
                      )}
                    </div>

                    {!selectedRound.investors || selectedRound.investors.length === 0 ? (
                      <div className="p-8 text-center" style={{ color: "var(--color-text-muted)" }}>
                        No investors added yet.
                      </div>
                    ) : (
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                              <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Investor</th>
                              <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Amount</th>
                              <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Committed</th>
                              <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Funds</th>
                              <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Docs</th>
                              <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Shares</th>
                              <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            {selectedRound.investors.map((inv) => (
                              <tr key={inv.id} style={{ borderBottom: "1px solid var(--color-border)" }}>
                                <td className="p-3">
                                  <div className="font-medium">{inv.investor_name}</div>
                                  <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                                    {inv.investor_type}{inv.investor_entity && ` | ${inv.investor_entity}`}
                                  </div>
                                </td>
                                <td className="p-3 text-right font-mono">{formatCurrency(inv.investment_amount)}</td>
                                {(["committed", "funds_received", "documents_signed", "shares_issued"] as const).map((field) => (
                                  <td key={field} className="p-3 text-center">
                                    <button
                                      onClick={() => handleToggleFlag(inv.id, field, !inv[field])}
                                      className="w-5 h-5 rounded border inline-flex items-center justify-center transition-all"
                                      style={{
                                        borderColor: inv[field] ? "var(--color-accent-emerald-light)" : "var(--color-border)",
                                        background: inv[field] ? "var(--color-success-light)" : "transparent",
                                        color: inv[field] ? "var(--color-accent-emerald-light)" : "transparent",
                                      }}
                                    >
                                      {inv[field] && (
                                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                                          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                                        </svg>
                                      )}
                                    </button>
                                  </td>
                                ))}
                                <td className="p-3 text-right">
                                  {!inv.shares_issued && (
                                    <button
                                      onClick={() => handleRemoveInvestor(inv.id)}
                                      className="text-[11px] px-2 py-1 rounded"
                                      style={{ color: "var(--color-accent-rose)" }}
                                    >
                                      Remove
                                    </button>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>

                  {/* Closing Room */}
                  {closingRoom && (
                    <div className="glass-card p-5" style={{ cursor: "default" }}>
                      <h3 className="font-semibold mb-3">Closing Room</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {Object.entries(closingRoom.documents || {}).map(([docType, doc]: [string, any]) => (
                          <div
                            key={docType}
                            className="p-3 rounded-lg"
                            style={{ background: "var(--color-stripe-alt)", border: "1px solid var(--color-border)" }}
                          >
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-sm font-semibold uppercase">{docType}</span>
                              <StatusBadge status={doc.status} />
                            </div>
                            {doc.signatories && doc.signatories.length > 0 && (
                              <div className="space-y-1">
                                {doc.signatories.map((s: any, idx: number) => (
                                  <div key={idx} className="flex justify-between text-xs">
                                    <span style={{ color: "var(--color-text-secondary)" }}>{s.name}</span>
                                    <span style={{
                                      color: s.status === "signed" ? "var(--color-accent-emerald-light)"
                                        : s.status === "declined" ? "var(--color-accent-rose)"
                                        : "var(--color-text-muted)",
                                    }}>
                                      {s.status}{s.signed_at && ` (${new Date(s.signed_at).toLocaleDateString()})`}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Document & Compliance Checklist */}
                  <DocumentChecklist
                    round={selectedRound}
                    companyId={companyId!}
                    onAllotment={handleCompleteAllotment}
                    onMessage={setMessage}
                  />

                  {/* Action Buttons */}
                  <div className="flex gap-3 flex-wrap">
                    {selectedRound.status === "documentation" && (
                      <button onClick={handleInitiateClosing} className="btn-primary text-sm">
                        Initiate Closing
                      </button>
                    )}
                    {(selectedRound.status === "closing" || selectedRound.status === "documentation") && !selectedRound.allotment_completed && (
                      <button onClick={handleCompleteAllotment} className="text-sm px-4 py-2 rounded-lg" style={{ background: "var(--color-success-light)", border: "1px solid var(--color-accent-emerald-light)", color: "var(--color-accent-emerald-light)" }}>
                        Complete Allotment
                      </button>
                    )}
                    {selectedRound.allotment_completed && (
                      <div className="text-xs px-3 py-2 rounded-lg" style={{ background: "var(--color-success-light)", color: "var(--color-accent-emerald-light)" }}>
                        Allotment Complete - PAS-3 filing required within 15 days
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Create Round Modal */}
      {showCreateRound && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "var(--color-overlay)" }}>
          <div className="glass-card p-6 w-full max-w-lg" style={{ cursor: "default", background: "var(--color-bg-card)" }}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">New Funding Round</h3>
              <button onClick={() => setShowCreateRound(false)} className="text-sm" style={{ color: "var(--color-text-muted)" }}>Close</button>
            </div>
            <form onSubmit={handleCreateRound} className="space-y-4">
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Round Name *</label>
                <input
                  type="text"
                  required
                  value={roundForm.round_name}
                  onChange={(e) => setRoundForm({ ...roundForm, round_name: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  placeholder="e.g., Seed Round, Series A"
                />
              </div>
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Instrument Type</label>
                <select
                  value={roundForm.instrument_type}
                  onChange={(e) => setRoundForm({ ...roundForm, instrument_type: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                >
                  <option value="equity">Equity</option>
                  <option value="ccps">CCPS (Compulsorily Convertible Preference Shares)</option>
                  <option value="ccd">CCD (Compulsorily Convertible Debentures)</option>
                  <option value="safe">SAFE</option>
                  <option value="convertible_note">Convertible Note</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Pre-Money Valuation (Rs)</label>
                  <input
                    type="number"
                    value={roundForm.pre_money_valuation}
                    onChange={(e) => setRoundForm({ ...roundForm, pre_money_valuation: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="10000000"
                  />
                  {roundForm.pre_money_valuation && (
                    <div className="text-[10px] mt-0.5" style={{ color: "var(--color-text-muted)" }}>
                      {formatCurrency(parseFloat(roundForm.pre_money_valuation) || 0)}
                    </div>
                  )}
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Target Amount (Rs)</label>
                  <input
                    type="number"
                    value={roundForm.target_amount}
                    onChange={(e) => setRoundForm({ ...roundForm, target_amount: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="2500000"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Price Per Share (Rs)</label>
                <input
                  type="number"
                  step="0.01"
                  value={roundForm.price_per_share}
                  onChange={(e) => setRoundForm({ ...roundForm, price_per_share: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  placeholder="100"
                />
              </div>
              <button type="submit" className="btn-primary w-full text-center justify-center">
                Create Round
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Add Investor Modal */}
      {showAddInvestor && selectedRound && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "var(--color-overlay)" }}>
          <div className="glass-card p-6 w-full max-w-lg" style={{ cursor: "default", background: "var(--color-bg-card)" }}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Add Investor to {selectedRound.round_name}</h3>
              <button onClick={() => setShowAddInvestor(false)} className="text-sm" style={{ color: "var(--color-text-muted)" }}>Close</button>
            </div>
            <form onSubmit={handleAddInvestor} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Investor Name *</label>
                  <input
                    type="text"
                    required
                    value={investorForm.investor_name}
                    onChange={(e) => setInvestorForm({ ...investorForm, investor_name: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="Investor name"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Email</label>
                  <input
                    type="email"
                    value={investorForm.investor_email}
                    onChange={(e) => setInvestorForm({ ...investorForm, investor_email: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="investor@fund.com"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Type</label>
                  <select
                    value={investorForm.investor_type}
                    onChange={(e) => setInvestorForm({ ...investorForm, investor_type: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  >
                    <option value="angel">Angel</option>
                    <option value="vc">VC</option>
                    <option value="institutional">Institutional</option>
                    <option value="strategic">Strategic</option>
                    <option value="foreign">Foreign Investor</option>
                    <option value="fdi">FDI Entity</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Entity / Fund</label>
                  <input
                    type="text"
                    value={investorForm.investor_entity}
                    onChange={(e) => setInvestorForm({ ...investorForm, investor_entity: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="Fund name"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Investment Amount (Rs) *</label>
                <input
                  type="number"
                  required
                  min={1}
                  value={investorForm.investment_amount}
                  onChange={(e) => setInvestorForm({ ...investorForm, investment_amount: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  placeholder="2500000"
                />
                {investorForm.investment_amount && (
                  <div className="text-[10px] mt-0.5" style={{ color: "var(--color-text-muted)" }}>
                    {formatCurrency(parseFloat(investorForm.investment_amount) || 0)}
                  </div>
                )}
              </div>
              <button type="submit" className="btn-primary w-full text-center justify-center">
                Add Investor
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Edit Round Modal */}
      {showEditRound && selectedRound && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "var(--color-overlay)" }}>
          <div className="glass-card p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto" style={{ cursor: "default", background: "var(--color-bg-card)" }}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Edit {selectedRound.round_name}</h3>
              <button onClick={() => setShowEditRound(false)} className="text-sm" style={{ color: "var(--color-text-muted)" }}>Close</button>
            </div>
            <form onSubmit={handleUpdateRound} className="space-y-4">
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Round Name *</label>
                <input
                  type="text"
                  required
                  value={editRoundForm.round_name}
                  onChange={(e) => setEditRoundForm({ ...editRoundForm, round_name: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Pre-Money Valuation (Rs)</label>
                  <input
                    type="number"
                    value={editRoundForm.pre_money_valuation}
                    onChange={(e) => setEditRoundForm({ ...editRoundForm, pre_money_valuation: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="10000000"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Target Amount (Rs)</label>
                  <input
                    type="number"
                    value={editRoundForm.target_amount}
                    onChange={(e) => setEditRoundForm({ ...editRoundForm, target_amount: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="2500000"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Price Per Share (Rs)</label>
                <input
                  type="number"
                  step="0.01"
                  value={editRoundForm.price_per_share}
                  onChange={(e) => setEditRoundForm({ ...editRoundForm, price_per_share: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  placeholder="100"
                />
              </div>
              {isConvertible(selectedRound.instrument_type) && (
                <>
                  <div className="pt-2 border-t" style={{ borderColor: "var(--color-border)" }}>
                    <p className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: "var(--color-text-muted)" }}>
                      Convertible Terms
                    </p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Valuation Cap (Rs)</label>
                      <input
                        type="number"
                        value={editRoundForm.valuation_cap}
                        onChange={(e) => setEditRoundForm({ ...editRoundForm, valuation_cap: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg text-sm"
                        style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                        placeholder="50000000"
                      />
                    </div>
                    <div>
                      <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Discount Rate (%)</label>
                      <input
                        type="number"
                        step="0.1"
                        value={editRoundForm.discount_rate}
                        onChange={(e) => setEditRoundForm({ ...editRoundForm, discount_rate: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg text-sm"
                        style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                        placeholder="20"
                      />
                    </div>
                    <div>
                      <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Interest Rate (%)</label>
                      <input
                        type="number"
                        step="0.1"
                        value={editRoundForm.interest_rate}
                        onChange={(e) => setEditRoundForm({ ...editRoundForm, interest_rate: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg text-sm"
                        style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                        placeholder="8"
                      />
                    </div>
                    <div>
                      <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Maturity (Months)</label>
                      <input
                        type="number"
                        value={editRoundForm.maturity_months}
                        onChange={(e) => setEditRoundForm({ ...editRoundForm, maturity_months: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg text-sm"
                        style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                        placeholder="24"
                      />
                    </div>
                  </div>
                </>
              )}
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Notes</label>
                <textarea
                  value={editRoundForm.notes}
                  onChange={(e) => setEditRoundForm({ ...editRoundForm, notes: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  rows={3}
                  placeholder="Round notes..."
                />
              </div>
              <button type="submit" className="btn-primary w-full text-center justify-center">
                Update Round
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Share Deal Modal */}
      {showShareDeal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "var(--color-overlay)" }}>
          <div className="glass-card p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto" style={{ cursor: "default", background: "var(--color-bg-card)" }}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Share Deal</h3>
              <button onClick={() => setShowShareDeal(false)} className="text-sm" style={{ color: "var(--color-text-muted)" }}>Close</button>
            </div>
            <form onSubmit={handleShareDeal} className="space-y-4 mb-6">
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Investor Email *</label>
                <input
                  type="email"
                  required
                  value={shareDealEmail}
                  onChange={(e) => setShareDealEmail(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  placeholder="investor@fund.com"
                />
              </div>
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Message (optional)</label>
                <textarea
                  value={shareDealMessage}
                  onChange={(e) => setShareDealMessage(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{ background: "var(--color-hover-overlay)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  rows={3}
                  placeholder="Invitation message for the investor..."
                />
              </div>
              <button type="submit" disabled={sharingDeal} className="btn-primary w-full text-center justify-center">
                {sharingDeal ? "Sharing..." : "Share Deal"}
              </button>
            </form>

            {/* Shared Deals List */}
            {sharedDeals.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold mb-3" style={{ color: "var(--color-text-secondary)" }}>Shared With</h4>
                <div className="space-y-2">
                  {sharedDeals.map((sd: any) => (
                    <div
                      key={sd.id}
                      className="flex items-center justify-between p-3 rounded-lg text-sm"
                      style={{ background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)" }}
                    >
                      <div>
                        <div className="font-medium" style={{ color: "var(--color-text-primary)" }}>{sd.investor_email}</div>
                        {sd.created_at && (
                          <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                            Shared {new Date(sd.created_at).toLocaleDateString("en-IN")}
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => handleRevokeDeal(sd.id)}
                        className="text-xs px-2 py-1 rounded hover:bg-red-500/10 transition-colors"
                        style={{ color: "var(--color-error)" }}
                      >
                        Revoke
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

    </div>
    </FeatureGate>
  );
}
