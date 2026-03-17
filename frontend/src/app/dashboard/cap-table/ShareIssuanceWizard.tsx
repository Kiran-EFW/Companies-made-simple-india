"use client";

import { useState, useCallback } from "react";
import { createLegalDraft, allotShares, getShareCertificate, apiCall } from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type IssueType = "rights_issue" | "private_placement";
type AllotteeType = "existing" | "new";

interface Allottee {
  name: string;
  email: string;
  type: AllotteeType;
  shares: number;
  accepted: boolean;
  fundsReceived: boolean;
  fundReceivedDate: string | null;
  certificateGenerated: boolean;
}

interface PreCheckData {
  authorizedCapital: string;
  issuedCapital: string;
  sharesToIssue: string;
  faceValue: string;
  premium: string;
  issueType: IssueType;
  allottees: Allottee[];
}

type StepStatus = "upcoming" | "current" | "completed";

interface FilingStatus {
  filed: boolean;
  filedDate: string | null;
}

interface WorkflowState {
  currentStep: number;
  preCheck: PreCheckData;
  boardResolution: {
    status: "draft" | "approved";
    draftId: number | null;
    resolutionText: string;
    sentForSigning: boolean;
    boardMeetingHeld: boolean;
    generating: boolean;
  };
  shareholderApproval: {
    status: "pending" | "sr_passed";
    egmNoticeGenerated: boolean;
    egmHeld: boolean;
    srPassed: boolean;
    generating: boolean;
  };
  regulatoryFiling: {
    mgt14: FilingStatus;
    sh7: FilingStatus;
  };
  offerLetters: {
    generated: boolean;
    sentForAcceptance: boolean;
    generating: boolean;
  };
  receiveFunds: {
    allFundsReceived: boolean;
    moneyReceivedDate: string | null;
  };
  allotment: {
    boardMeetingHeld: boolean;
    allotmentComplete: boolean;
    allotting: boolean;
  };
  postAllotment: {
    pas3Filed: boolean;
    pas3FiledDate: string | null;
    certificatesGenerated: boolean;
    registerUpdated: boolean;
    generatingCerts: boolean;
  };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function createInitialState(): WorkflowState {
  return {
    currentStep: 0,
    preCheck: {
      authorizedCapital: "1000000",
      issuedCapital: "100000",
      sharesToIssue: "",
      faceValue: "10",
      premium: "0",
      issueType: "private_placement",
      allottees: [{ name: "", email: "", type: "new", shares: 0, accepted: false, fundsReceived: false, fundReceivedDate: null, certificateGenerated: false }],
    },
    boardResolution: {
      status: "draft",
      draftId: null,
      resolutionText: "",
      sentForSigning: false,
      boardMeetingHeld: false,
      generating: false,
    },
    shareholderApproval: {
      status: "pending",
      egmNoticeGenerated: false,
      egmHeld: false,
      srPassed: false,
      generating: false,
    },
    regulatoryFiling: {
      mgt14: { filed: false, filedDate: null },
      sh7: { filed: false, filedDate: null },
    },
    offerLetters: {
      generated: false,
      sentForAcceptance: false,
      generating: false,
    },
    receiveFunds: {
      allFundsReceived: false,
      moneyReceivedDate: null,
    },
    allotment: {
      boardMeetingHeld: false,
      allotmentComplete: false,
      allotting: false,
    },
    postAllotment: {
      pas3Filed: false,
      pas3FiledDate: null,
      certificatesGenerated: false,
      registerUpdated: false,
      generatingCerts: false,
    },
  };
}

function formatCurrency(val: number): string {
  if (val >= 10000000) return `Rs ${(val / 10000000).toFixed(2)} Cr`;
  if (val >= 100000) return `Rs ${(val / 100000).toFixed(2)} L`;
  return `Rs ${val.toLocaleString("en-IN")}`;
}

const STEP_LABELS = [
  "Pre-Check",
  "Board Resolution",
  "Shareholder Approval",
  "Regulatory Filing",
  "Offer Letters",
  "Receive Funds",
  "Allotment",
  "Post-Allotment",
];

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function StepIndicator({
  steps,
  currentStep,
  onStepClick,
}: {
  steps: string[];
  currentStep: number;
  onStepClick: (step: number) => void;
}) {
  return (
    <div className="flex items-center justify-center mb-8 flex-wrap gap-y-3">
      {steps.map((label, idx) => {
        let status: StepStatus = "upcoming";
        if (idx < currentStep) status = "completed";
        else if (idx === currentStep) status = "current";

        return (
          <div key={label} className="flex items-center">
            <button
              onClick={() => onStepClick(idx)}
              className="flex items-center gap-2 px-2 py-1 rounded-lg transition-all"
              style={{
                cursor: idx <= currentStep ? "pointer" : "default",
                opacity: status === "upcoming" ? 0.4 : 1,
              }}
            >
              <div
                className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
                style={{
                  background:
                    status === "completed"
                      ? "var(--color-success-light)"
                      : status === "current"
                        ? "var(--color-purple-bg)"
                        : "var(--color-hover-overlay)",
                  border: `2px solid ${
                    status === "completed"
                      ? "var(--color-accent-emerald-light)"
                      : status === "current"
                        ? "var(--color-accent-purple-light)"
                        : "var(--color-hover-overlay)"
                  }`,
                  color:
                    status === "completed"
                      ? "var(--color-accent-emerald-light)"
                      : status === "current"
                        ? "var(--color-accent-purple-light)"
                        : "var(--color-text-muted)",
                }}
              >
                {status === "completed" ? (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                ) : (
                  idx + 1
                )}
              </div>
              <span
                className="text-xs font-medium hidden sm:inline"
                style={{
                  color:
                    status === "completed"
                      ? "var(--color-accent-emerald-light)"
                      : status === "current"
                        ? "var(--color-accent-purple-light)"
                        : "var(--color-text-muted)",
                }}
              >
                {label}
              </span>
            </button>
            {idx < steps.length - 1 && (
              <div
                className="w-6 h-0.5 mx-1 hidden sm:block"
                style={{
                  background:
                    idx < currentStep
                      ? "var(--color-accent-emerald-light)"
                      : "var(--color-hover-overlay)",
                }}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

function StatusBadge({ status, label }: { status: "completed" | "current" | "pending" | "warning"; label: string }) {
  const colorMap = {
    completed: { bg: "var(--color-success-light)", color: "var(--color-accent-emerald-light)" },
    current: { bg: "var(--color-purple-bg)", color: "var(--color-accent-purple-light)" },
    pending: { bg: "var(--color-hover-overlay)", color: "var(--color-text-muted)" },
    warning: { bg: "var(--color-warning-light)", color: "var(--color-accent-amber)" },
  };
  const c = colorMap[status];
  return (
    <span
      className="text-xs px-2.5 py-1 rounded-full font-medium"
      style={{ background: c.bg, color: c.color }}
    >
      {label}
    </span>
  );
}

function ChecklistItem({
  checked,
  label,
  onChange,
}: {
  checked: boolean;
  label: string;
  onChange?: (val: boolean) => void;
}) {
  return (
    <label className="flex items-center gap-2.5 text-sm py-1.5 cursor-pointer" style={{ color: "var(--color-text-secondary)" }}>
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange?.(e.target.checked)}
        className="rounded"
        style={{ accentColor: "var(--color-accent-purple-light)" }}
      />
      <span style={{ textDecoration: checked ? "line-through" : "none", opacity: checked ? 0.6 : 1 }}>
        {label}
      </span>
    </label>
  );
}

function ActionButton({
  onClick,
  loading,
  disabled,
  variant = "primary",
  children,
}: {
  onClick: () => void;
  loading?: boolean;
  disabled?: boolean;
  variant?: "primary" | "secondary" | "success";
  children: React.ReactNode;
}) {
  const styles = {
    primary: {
      background: loading || disabled ? "var(--color-purple-bg)" : "var(--color-accent-purple-light)",
      color: "#fff",
      border: "1px solid var(--color-accent-purple-light)",
    },
    secondary: {
      background: loading || disabled ? "var(--color-hover-overlay)" : "var(--color-hover-overlay)",
      color: "var(--color-text-secondary)",
      border: "1px solid var(--color-border)",
    },
    success: {
      background: loading || disabled ? "var(--color-success-light)" : "var(--color-accent-emerald-light)",
      color: "#fff",
      border: "1px solid var(--color-accent-emerald-light)",
    },
  };
  const s = styles[variant];
  return (
    <button
      onClick={onClick}
      disabled={loading || disabled}
      className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
      style={{ ...s, cursor: loading || disabled ? "not-allowed" : "pointer" }}
    >
      {loading ? "Processing..." : children}
    </button>
  );
}

// ---------------------------------------------------------------------------
// Step Components
// ---------------------------------------------------------------------------

interface StepCardProps {
  stepNumber: number;
  title: string;
  status: StepStatus;
  expanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

function StepCard({ stepNumber, title, status, expanded, onToggle, children }: StepCardProps) {
  return (
    <div
      className="glass-card mb-4 overflow-hidden transition-all"
      style={{
        cursor: "default",
        borderColor:
          status === "current"
            ? "var(--color-accent-purple-light)"
            : status === "completed"
              ? "var(--color-accent-emerald-light)"
              : "var(--color-border)",
      }}
    >
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-5 text-left transition-all"
        style={{ cursor: "pointer" }}
      >
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shrink-0"
            style={{
              background:
                status === "completed"
                  ? "var(--color-success-light)"
                  : status === "current"
                    ? "var(--color-purple-bg)"
                    : "var(--color-hover-overlay)",
              color:
                status === "completed"
                  ? "var(--color-accent-emerald-light)"
                  : status === "current"
                    ? "var(--color-accent-purple-light)"
                    : "var(--color-text-muted)",
            }}
          >
            {status === "completed" ? (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            ) : (
              stepNumber
            )}
          </div>
          <div>
            <h3 className="font-semibold text-sm" style={{ color: "var(--color-text-primary)" }}>
              {title}
            </h3>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge
            status={status === "completed" ? "completed" : status === "current" ? "current" : "pending"}
            label={status === "completed" ? "Completed" : status === "current" ? "In Progress" : "Upcoming"}
          />
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{
              color: "var(--color-text-muted)",
              transform: expanded ? "rotate(180deg)" : "rotate(0deg)",
              transition: "transform 0.2s",
            }}
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </div>
      </button>
      {expanded && (
        <div className="px-5 pb-5" style={{ borderTop: "1px solid var(--color-border)" }}>
          <div className="pt-4">{children}</div>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

interface ShareIssuanceWizardProps {
  companyId: number;
  capTableData: {
    total_shares: number;
    shareholders: {
      id: number;
      name: string;
      email: string | null;
      shares: number;
      share_type: string;
      face_value: number;
      percentage: number;
    }[];
  } | null;
  onComplete: () => void;
  setMessage: (msg: string) => void;
}

export default function ShareIssuanceWizard({
  companyId,
  capTableData,
  onComplete,
  setMessage,
}: ShareIssuanceWizardProps) {
  const [state, setState] = useState<WorkflowState>(createInitialState);
  const [expandedStep, setExpandedStep] = useState<number>(0);

  // Pre-populate issued capital from cap table data
  const issuedShares = capTableData?.total_shares ?? 0;
  const defaultFaceValue = capTableData?.shareholders?.[0]?.face_value ?? 10;

  // Derived values
  const authorizedCapital = parseFloat(state.preCheck.authorizedCapital) || 0;
  const currentIssuedCapital = issuedShares * defaultFaceValue;
  const newSharesCount = parseInt(state.preCheck.sharesToIssue) || 0;
  const faceValue = parseFloat(state.preCheck.faceValue) || 10;
  const premium = parseFloat(state.preCheck.premium) || 0;
  const newIssuanceCapital = newSharesCount * faceValue;
  const totalAfterIssuance = currentIssuedCapital + newIssuanceCapital;
  const capitalSufficient = totalAfterIssuance <= authorizedCapital;
  const isPrivatePlacement = state.preCheck.issueType === "private_placement";

  // Update helpers
  const updatePreCheck = useCallback((updates: Partial<PreCheckData>) => {
    setState((prev) => ({ ...prev, preCheck: { ...prev.preCheck, ...updates } }));
  }, []);

  const updateAllottee = useCallback((index: number, updates: Partial<Allottee>) => {
    setState((prev) => {
      const allottees = [...prev.preCheck.allottees];
      allottees[index] = { ...allottees[index], ...updates };
      return { ...prev, preCheck: { ...prev.preCheck, allottees } };
    });
  }, []);

  const addAllottee = useCallback(() => {
    setState((prev) => ({
      ...prev,
      preCheck: {
        ...prev.preCheck,
        allottees: [
          ...prev.preCheck.allottees,
          { name: "", email: "", type: "new" as AllotteeType, shares: 0, accepted: false, fundsReceived: false, fundReceivedDate: null, certificateGenerated: false },
        ],
      },
    }));
  }, []);

  const removeAllottee = useCallback((index: number) => {
    setState((prev) => ({
      ...prev,
      preCheck: {
        ...prev.preCheck,
        allottees: prev.preCheck.allottees.filter((_, i) => i !== index),
      },
    }));
  }, []);

  const goToStep = useCallback((step: number) => {
    setState((prev) => {
      const newCurrent = Math.max(prev.currentStep, step);
      return { ...prev, currentStep: newCurrent };
    });
    setExpandedStep(step);
  }, []);

  const completeStep = useCallback((step: number) => {
    setState((prev) => ({
      ...prev,
      currentStep: Math.max(prev.currentStep, step + 1),
    }));
    setExpandedStep(step + 1);
  }, []);

  // API handlers
  const handleGenerateBoardResolution = useCallback(async () => {
    setState((prev) => ({
      ...prev,
      boardResolution: { ...prev.boardResolution, generating: true },
    }));
    try {
      const result = await createLegalDraft({
        template_type: "board_resolution",
        company_id: companyId,
        title: `Board Resolution - Share Allotment of ${newSharesCount} shares`,
      });
      const resolutionText = `RESOLVED THAT pursuant to the provisions of Section 62 of the Companies Act, 2013 read with Rule 13 of the Companies (Share Capital and Debentures) Rules, 2014, and subject to the applicable provisions of the Companies Act, 2013, and the Articles of Association of the Company, the consent of the Board of Directors be and is hereby accorded to issue and allot ${newSharesCount.toLocaleString("en-IN")} equity shares of Rs. ${faceValue}/- each at a premium of Rs. ${premium}/- per share (total issue price of Rs. ${(faceValue + premium).toLocaleString("en-IN")}/- per share) aggregating to Rs. ${(newSharesCount * (faceValue + premium)).toLocaleString("en-IN")}/- on a ${isPrivatePlacement ? "Private Placement" : "Rights Issue"} basis to the proposed allottees as per the list annexed hereto.`;
      setState((prev) => ({
        ...prev,
        boardResolution: {
          ...prev.boardResolution,
          draftId: result.id ?? null,
          resolutionText,
          generating: false,
        },
      }));
      setMessage("Board Resolution draft generated successfully.");
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
      setState((prev) => ({
        ...prev,
        boardResolution: { ...prev.boardResolution, generating: false },
      }));
    }
  }, [companyId, newSharesCount, faceValue, premium, isPrivatePlacement, setMessage]);

  const handleSendForSigning = useCallback(async () => {
    setState((prev) => ({
      ...prev,
      boardResolution: { ...prev.boardResolution, sentForSigning: true },
    }));
    setMessage("Board Resolution sent to directors for e-signature.");
  }, [setMessage]);

  const handleGenerateEGMNotice = useCallback(async () => {
    setState((prev) => ({
      ...prev,
      shareholderApproval: { ...prev.shareholderApproval, generating: true },
    }));
    try {
      await createLegalDraft({
        template_type: "egm_notice",
        company_id: companyId,
        title: `EGM Notice - Private Placement of ${newSharesCount} shares`,
      });
      setState((prev) => ({
        ...prev,
        shareholderApproval: {
          ...prev.shareholderApproval,
          egmNoticeGenerated: true,
          generating: false,
        },
      }));
      setMessage("EGM Notice generated. 14 clear days advance notice required before the meeting.");
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
      setState((prev) => ({
        ...prev,
        shareholderApproval: { ...prev.shareholderApproval, generating: false },
      }));
    }
  }, [companyId, newSharesCount, setMessage]);

  const handleGenerateOfferLetters = useCallback(async () => {
    setState((prev) => ({
      ...prev,
      offerLetters: { ...prev.offerLetters, generating: true },
    }));
    try {
      await createLegalDraft({
        template_type: "pas4_offer_letter",
        company_id: companyId,
        title: `PAS-4 Offer Letters - Private Placement`,
      });
      setState((prev) => ({
        ...prev,
        offerLetters: { ...prev.offerLetters, generated: true, generating: false },
      }));
      setMessage("PAS-4 Offer Letters generated for all allottees.");
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
      setState((prev) => ({
        ...prev,
        offerLetters: { ...prev.offerLetters, generating: false },
      }));
    }
  }, [companyId, setMessage]);

  const handleSendOfferLetters = useCallback(() => {
    setState((prev) => ({
      ...prev,
      offerLetters: { ...prev.offerLetters, sentForAcceptance: true },
    }));
    setMessage("Offer letters sent to allottees for acceptance.");
  }, [setMessage]);

  const handleCompleteAllotment = useCallback(async () => {
    setState((prev) => ({
      ...prev,
      allotment: { ...prev.allotment, allotting: true },
    }));
    try {
      const allotmentData = {
        allottees: state.preCheck.allottees.map((a) => ({
          name: a.name,
          email: a.email,
          shares: a.shares,
          share_type: "equity",
          face_value: faceValue,
          premium,
          is_new: a.type === "new",
        })),
        issue_type: state.preCheck.issueType,
        total_shares: newSharesCount,
        face_value: faceValue,
        premium,
      };
      await allotShares(companyId, allotmentData);
      setState((prev) => ({
        ...prev,
        allotment: {
          ...prev.allotment,
          allotmentComplete: true,
          allotting: false,
        },
      }));
      setMessage("Share allotment completed successfully. Cap table has been updated.");
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
      setState((prev) => ({
        ...prev,
        allotment: { ...prev.allotment, allotting: false },
      }));
    }
  }, [companyId, state.preCheck, faceValue, premium, newSharesCount, setMessage]);

  const handleGenerateCertificates = useCallback(async () => {
    setState((prev) => ({
      ...prev,
      postAllotment: { ...prev.postAllotment, generatingCerts: true },
    }));
    try {
      // Generate certificates for each allottee using the cap table's shareholder data
      for (const allottee of state.preCheck.allottees) {
        if (allottee.name) {
          // Find the shareholder by name in the cap table (after allotment, they should be there)
          const shareholder = capTableData?.shareholders.find(
            (s) => s.name.toLowerCase() === allottee.name.toLowerCase()
          );
          if (shareholder) {
            await getShareCertificate(companyId, shareholder.id);
          }
        }
      }
      setState((prev) => ({
        ...prev,
        postAllotment: {
          ...prev.postAllotment,
          certificatesGenerated: true,
          generatingCerts: false,
        },
      }));
      setMessage("Share certificates generated for all new allottees.");
    } catch (err: any) {
      setMessage(`Error generating certificates: ${err.message}`);
      setState((prev) => ({
        ...prev,
        postAllotment: { ...prev.postAllotment, generatingCerts: false },
      }));
    }
  }, [companyId, state.preCheck.allottees, capTableData, setMessage]);

  // Step status helpers
  function getStepStatus(stepIdx: number): StepStatus {
    if (stepIdx < state.currentStep) return "completed";
    if (stepIdx === state.currentStep) return "current";
    return "upcoming";
  }

  // Compute whether pre-check can proceed
  const preCheckValid =
    newSharesCount > 0 &&
    faceValue > 0 &&
    state.preCheck.allottees.length > 0 &&
    state.preCheck.allottees.every((a) => a.name.trim() !== "" && a.shares > 0);

  // Input field styles
  const inputStyle = {
    background: "var(--color-bg-card)",
    border: "1px solid var(--color-border)",
    color: "var(--color-text-primary)",
  };

  return (
    <div>
      {/* Step Indicator */}
      <StepIndicator
        steps={STEP_LABELS}
        currentStep={state.currentStep}
        onStepClick={(step) => {
          if (step <= state.currentStep) {
            setExpandedStep(step);
          }
        }}
      />

      {/* Step 1: Pre-Check */}
      <StepCard
        stepNumber={1}
        title="Pre-Check: Capital & Allottee Details"
        status={getStepStatus(0)}
        expanded={expandedStep === 0}
        onToggle={() => setExpandedStep(expandedStep === 0 ? -1 : 0)}
      >
        <div className="space-y-5">
          {/* Capital Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="glass-card p-4 text-center" style={{ cursor: "default" }}>
              <div className="text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>
                Authorized Capital
              </div>
              <input
                type="number"
                value={state.preCheck.authorizedCapital}
                onChange={(e) => updatePreCheck({ authorizedCapital: e.target.value })}
                className="w-full text-center text-lg font-bold px-2 py-1 rounded-lg"
                style={inputStyle}
              />
              <div className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
                {formatCurrency(authorizedCapital)}
              </div>
            </div>
            <div className="glass-card p-4 text-center" style={{ cursor: "default" }}>
              <div className="text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>
                Current Issued Capital
              </div>
              <div className="text-lg font-bold" style={{ color: "var(--color-accent-blue)" }}>
                {formatCurrency(currentIssuedCapital)}
              </div>
              <div className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
                {issuedShares.toLocaleString("en-IN")} shares
              </div>
            </div>
            <div className="glass-card p-4 text-center" style={{ cursor: "default" }}>
              <div className="text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>
                After Issuance
              </div>
              <div
                className="text-lg font-bold"
                style={{ color: capitalSufficient ? "var(--color-accent-emerald-light)" : "var(--color-accent-rose)" }}
              >
                {formatCurrency(totalAfterIssuance)}
              </div>
              <div className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
                {(issuedShares + newSharesCount).toLocaleString("en-IN")} shares
              </div>
            </div>
          </div>

          {/* Capital Warning */}
          {newSharesCount > 0 && !capitalSufficient && (
            <div
              className="glass-card p-4"
              style={{
                cursor: "default",
                borderColor: "var(--color-accent-amber)",
                background: "var(--color-warning-light)",
              }}
            >
              <div className="flex items-start gap-3">
                <div className="text-lg shrink-0" style={{ color: "var(--color-accent-amber)" }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                    <line x1="12" y1="9" x2="12" y2="13" />
                    <line x1="12" y1="17" x2="12.01" y2="17" />
                  </svg>
                </div>
                <div>
                  <div className="font-semibold text-sm" style={{ color: "var(--color-accent-amber)" }}>
                    Authorized Capital Increase Needed (SH-7)
                  </div>
                  <p className="text-xs mt-1" style={{ color: "var(--color-text-secondary)" }}>
                    The proposed issuance of {formatCurrency(newIssuanceCapital)} exceeds the available authorized capital.
                    You will need to file Form SH-7 with the ROC to increase authorized capital before proceeding.
                    This requires a Special Resolution at an EGM and payment of additional stamp duty and ROC fees.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Issue Details */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                Number of Shares to Issue *
              </label>
              <input
                type="number"
                value={state.preCheck.sharesToIssue}
                onChange={(e) => updatePreCheck({ sharesToIssue: e.target.value })}
                min={1}
                className="w-full px-3 py-2 rounded-lg text-sm"
                style={inputStyle}
                placeholder="e.g., 10000"
              />
            </div>
            <div>
              <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                Face Value (Rs) *
              </label>
              <input
                type="number"
                value={state.preCheck.faceValue}
                onChange={(e) => updatePreCheck({ faceValue: e.target.value })}
                min={1}
                className="w-full px-3 py-2 rounded-lg text-sm"
                style={inputStyle}
                placeholder="10"
              />
            </div>
            <div>
              <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>
                Premium (Rs)
              </label>
              <input
                type="number"
                value={state.preCheck.premium}
                onChange={(e) => updatePreCheck({ premium: e.target.value })}
                min={0}
                className="w-full px-3 py-2 rounded-lg text-sm"
                style={inputStyle}
                placeholder="0"
              />
            </div>
          </div>

          {/* Total Issue Price */}
          {newSharesCount > 0 && (
            <div className="glass-card p-3 text-center" style={{ cursor: "default" }}>
              <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                Total Issue Price
              </div>
              <div className="text-lg font-bold" style={{ color: "var(--color-accent-purple-light)" }}>
                {formatCurrency(newSharesCount * (faceValue + premium))}
              </div>
              <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                {newSharesCount.toLocaleString("en-IN")} shares x Rs {(faceValue + premium).toLocaleString("en-IN")} per share
              </div>
            </div>
          )}

          {/* Issue Type */}
          <div>
            <label className="block text-sm mb-2 font-medium" style={{ color: "var(--color-text-secondary)" }}>
              Issue Type
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <label
                className="glass-card p-4 flex items-start gap-3 cursor-pointer transition-all"
                style={{
                  borderColor:
                    state.preCheck.issueType === "rights_issue"
                      ? "var(--color-accent-purple-light)"
                      : "var(--color-border)",
                  background:
                    state.preCheck.issueType === "rights_issue"
                      ? "var(--color-purple-bg)"
                      : "transparent",
                }}
              >
                <input
                  type="radio"
                  name="issueType"
                  value="rights_issue"
                  checked={state.preCheck.issueType === "rights_issue"}
                  onChange={() => updatePreCheck({ issueType: "rights_issue" })}
                  style={{ accentColor: "var(--color-accent-purple-light)", marginTop: "2px" }}
                />
                <div>
                  <div className="font-medium text-sm">Rights Issue</div>
                  <div className="text-xs mt-0.5" style={{ color: "var(--color-text-muted)" }}>
                    Offer to existing shareholders in proportion to their current holdings (Section 62(1)(a))
                  </div>
                </div>
              </label>
              <label
                className="glass-card p-4 flex items-start gap-3 cursor-pointer transition-all"
                style={{
                  borderColor:
                    state.preCheck.issueType === "private_placement"
                      ? "var(--color-accent-purple-light)"
                      : "var(--color-border)",
                  background:
                    state.preCheck.issueType === "private_placement"
                      ? "var(--color-purple-bg)"
                      : "transparent",
                }}
              >
                <input
                  type="radio"
                  name="issueType"
                  value="private_placement"
                  checked={state.preCheck.issueType === "private_placement"}
                  onChange={() => updatePreCheck({ issueType: "private_placement" })}
                  style={{ accentColor: "var(--color-accent-purple-light)", marginTop: "2px" }}
                />
                <div>
                  <div className="font-medium text-sm">Private Placement</div>
                  <div className="text-xs mt-0.5" style={{ color: "var(--color-text-muted)" }}>
                    Issue to select investors via PAS-4 offer letter (Section 42, max 200 persons per FY)
                  </div>
                </div>
              </label>
            </div>
          </div>

          {/* Allottees */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm font-medium" style={{ color: "var(--color-text-secondary)" }}>
                Allottee Details
              </label>
              <button
                onClick={addAllottee}
                className="text-xs px-3 py-1.5 rounded-lg transition-all"
                style={{ background: "var(--color-purple-bg)", color: "var(--color-accent-purple-light)" }}
              >
                + Add Allottee
              </button>
            </div>
            <div className="space-y-3">
              {state.preCheck.allottees.map((allottee, idx) => (
                <div
                  key={idx}
                  className="glass-card p-4"
                  style={{ cursor: "default" }}
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-medium" style={{ color: "var(--color-text-muted)" }}>
                      Allottee #{idx + 1}
                    </span>
                    {state.preCheck.allottees.length > 1 && (
                      <button
                        onClick={() => removeAllottee(idx)}
                        className="text-xs px-2 py-1 rounded"
                        style={{ color: "var(--color-accent-rose)" }}
                      >
                        Remove
                      </button>
                    )}
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                    <div>
                      <label className="block text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>
                        Name *
                      </label>
                      <input
                        type="text"
                        value={allottee.name}
                        onChange={(e) => updateAllottee(idx, { name: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg text-sm"
                        style={inputStyle}
                        placeholder="Investor name"
                      />
                    </div>
                    <div>
                      <label className="block text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>
                        Email
                      </label>
                      <input
                        type="email"
                        value={allottee.email}
                        onChange={(e) => updateAllottee(idx, { email: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg text-sm"
                        style={inputStyle}
                        placeholder="investor@example.com"
                      />
                    </div>
                    <div>
                      <label className="block text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>
                        Shares *
                      </label>
                      <input
                        type="number"
                        value={allottee.shares || ""}
                        onChange={(e) => updateAllottee(idx, { shares: parseInt(e.target.value) || 0 })}
                        min={1}
                        className="w-full px-3 py-2 rounded-lg text-sm"
                        style={inputStyle}
                        placeholder="Number of shares"
                      />
                    </div>
                    <div>
                      <label className="block text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>
                        Type
                      </label>
                      <select
                        value={allottee.type}
                        onChange={(e) => updateAllottee(idx, { type: e.target.value as AllotteeType })}
                        className="w-full px-3 py-2 rounded-lg text-sm"
                        style={inputStyle}
                      >
                        <option value="new">New Investor</option>
                        <option value="existing">Existing Shareholder</option>
                      </select>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            {state.preCheck.allottees.length > 0 && (
              <div className="text-xs mt-2 text-right" style={{ color: "var(--color-text-muted)" }}>
                Total shares to allottees:{" "}
                <span className="font-mono font-bold">
                  {state.preCheck.allottees.reduce((s, a) => s + a.shares, 0).toLocaleString("en-IN")}
                </span>
                {newSharesCount > 0 &&
                  state.preCheck.allottees.reduce((s, a) => s + a.shares, 0) !== newSharesCount && (
                    <span style={{ color: "var(--color-accent-rose)" }}>
                      {" "}(does not match total shares to issue: {newSharesCount.toLocaleString("en-IN")})
                    </span>
                  )}
              </div>
            )}
          </div>

          {/* Action */}
          <div className="flex justify-end">
            <ActionButton
              onClick={() => completeStep(0)}
              disabled={!preCheckValid}
            >
              Proceed to Board Resolution
            </ActionButton>
          </div>
        </div>
      </StepCard>

      {/* Step 2: Board Resolution */}
      <StepCard
        stepNumber={2}
        title="Board Resolution"
        status={getStepStatus(1)}
        expanded={expandedStep === 1}
        onToggle={() => setExpandedStep(expandedStep === 1 ? -1 : 1)}
      >
        <div className="space-y-4">
          <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
            A Board Resolution is required to authorize the issue of new shares. The Board must pass a resolution
            approving the allotment at a duly convened Board Meeting with quorum.
          </p>

          <div className="flex items-center gap-3 mb-4">
            <span className="text-sm" style={{ color: "var(--color-text-muted)" }}>Status:</span>
            <StatusBadge
              status={state.boardResolution.status === "approved" ? "completed" : "current"}
              label={state.boardResolution.status === "approved" ? "Approved" : "Draft"}
            />
          </div>

          {/* Generate Button */}
          <div className="flex flex-wrap gap-3">
            <ActionButton
              onClick={handleGenerateBoardResolution}
              loading={state.boardResolution.generating}
              disabled={!!state.boardResolution.resolutionText}
            >
              Generate Board Resolution
            </ActionButton>
            {state.boardResolution.resolutionText && !state.boardResolution.sentForSigning && (
              <ActionButton
                onClick={handleSendForSigning}
                variant="secondary"
              >
                Send for Signing
              </ActionButton>
            )}
          </div>

          {/* Resolution Preview */}
          {state.boardResolution.resolutionText && (
            <div
              className="glass-card p-4 mt-4"
              style={{ cursor: "default" }}
            >
              <div className="text-xs font-medium mb-2" style={{ color: "var(--color-text-muted)" }}>
                Resolution Text Preview
              </div>
              <p className="text-sm leading-relaxed" style={{ color: "var(--color-text-secondary)" }}>
                {state.boardResolution.resolutionText}
              </p>
            </div>
          )}

          {state.boardResolution.sentForSigning && (
            <div
              className="glass-card p-3 text-sm"
              style={{
                cursor: "default",
                borderColor: "var(--color-accent-emerald-light)",
                background: "var(--color-success-light)",
                color: "var(--color-accent-emerald-light)",
              }}
            >
              Resolution sent to directors for e-signature.
            </div>
          )}

          {/* Checklist */}
          <div className="mt-4">
            <ChecklistItem
              checked={state.boardResolution.boardMeetingHeld}
              label="Board meeting held with quorum"
              onChange={(val) =>
                setState((prev) => ({
                  ...prev,
                  boardResolution: { ...prev.boardResolution, boardMeetingHeld: val },
                }))
              }
            />
            <ChecklistItem
              checked={state.boardResolution.status === "approved"}
              label="Resolution approved by Board"
              onChange={(val) =>
                setState((prev) => ({
                  ...prev,
                  boardResolution: {
                    ...prev.boardResolution,
                    status: val ? "approved" : "draft",
                  },
                }))
              }
            />
          </div>

          {/* Actions */}
          <div className="flex justify-between mt-4">
            <ActionButton onClick={() => goToStep(0)} variant="secondary">
              Back
            </ActionButton>
            <ActionButton
              onClick={() => completeStep(1)}
              disabled={
                !state.boardResolution.boardMeetingHeld ||
                state.boardResolution.status !== "approved"
              }
            >
              {isPrivatePlacement ? "Proceed to Shareholder Approval" : "Proceed to Regulatory Filing"}
            </ActionButton>
          </div>
        </div>
      </StepCard>

      {/* Step 3: Shareholder Approval (Private Placement only) */}
      <StepCard
        stepNumber={3}
        title="Shareholder Approval (Special Resolution)"
        status={
          !isPrivatePlacement && state.currentStep >= 2
            ? "completed"
            : getStepStatus(2)
        }
        expanded={expandedStep === 2}
        onToggle={() => setExpandedStep(expandedStep === 2 ? -1 : 2)}
      >
        {!isPrivatePlacement ? (
          <div className="text-sm" style={{ color: "var(--color-text-muted)" }}>
            Shareholder approval via Special Resolution is not required for Rights Issues.
            This step is automatically marked as complete.
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
              For Private Placement under Section 42, a Special Resolution must be passed at an EGM.
              Notice of 14 clear days must be given to all shareholders. The resolution requires approval
              by at least 75% of members present and voting.
            </p>

            <div className="flex items-center gap-3 mb-4">
              <span className="text-sm" style={{ color: "var(--color-text-muted)" }}>Status:</span>
              <StatusBadge
                status={state.shareholderApproval.status === "sr_passed" ? "completed" : "current"}
                label={state.shareholderApproval.status === "sr_passed" ? "SR Passed" : "Pending"}
              />
            </div>

            <div className="flex flex-wrap gap-3">
              <ActionButton
                onClick={handleGenerateEGMNotice}
                loading={state.shareholderApproval.generating}
                disabled={state.shareholderApproval.egmNoticeGenerated}
              >
                Generate EGM Notice
              </ActionButton>
            </div>

            {state.shareholderApproval.egmNoticeGenerated && (
              <div
                className="glass-card p-4"
                style={{ cursor: "default" }}
              >
                <div className="text-sm font-medium mb-2" style={{ color: "var(--color-text-secondary)" }}>
                  Special Resolution Text
                </div>
                <p className="text-sm leading-relaxed" style={{ color: "var(--color-text-secondary)" }}>
                  &quot;RESOLVED THAT pursuant to Section 42 and Section 62(1)(c) of the Companies Act, 2013 read with Rule 14 of the
                  Companies (Prospectus and Allotment of Securities) Rules, 2014, and subject to such approvals as may be required,
                  consent of the members be and is hereby accorded to the Board of Directors to make an offer or invitation to
                  subscribe to {newSharesCount.toLocaleString("en-IN")} equity shares of Rs. {faceValue}/- each at a premium of
                  Rs. {premium}/- per share on a private placement basis, to such persons and on such terms as the Board may
                  determine from time to time.&quot;
                </p>
              </div>
            )}

            <div className="mt-4">
              <ChecklistItem
                checked={state.shareholderApproval.egmNoticeGenerated}
                label="EGM notice generated (14 clear days advance)"
                onChange={() => {}}
              />
              <ChecklistItem
                checked={state.shareholderApproval.egmHeld}
                label="EGM held with requisite quorum"
                onChange={(val) =>
                  setState((prev) => ({
                    ...prev,
                    shareholderApproval: { ...prev.shareholderApproval, egmHeld: val },
                  }))
                }
              />
              <ChecklistItem
                checked={state.shareholderApproval.srPassed}
                label="Special Resolution passed with 75% majority"
                onChange={(val) =>
                  setState((prev) => ({
                    ...prev,
                    shareholderApproval: {
                      ...prev.shareholderApproval,
                      srPassed: val,
                      status: val ? "sr_passed" : "pending",
                    },
                  }))
                }
              />
            </div>

            <div className="flex justify-between mt-4">
              <ActionButton onClick={() => goToStep(1)} variant="secondary">
                Back
              </ActionButton>
              <ActionButton
                onClick={() => completeStep(2)}
                disabled={!state.shareholderApproval.srPassed || !state.shareholderApproval.egmHeld}
              >
                Proceed to Regulatory Filing
              </ActionButton>
            </div>
          </div>
        )}
      </StepCard>

      {/* Step 4: Regulatory Filing */}
      <StepCard
        stepNumber={4}
        title="Regulatory Filing"
        status={getStepStatus(3)}
        expanded={expandedStep === 3}
        onToggle={() => setExpandedStep(expandedStep === 3 ? -1 : 3)}
      >
        <div className="space-y-4">
          <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
            Track required MCA filings. These must be completed within the statutory timelines to avoid penalties.
          </p>

          {/* MGT-14 */}
          {isPrivatePlacement && (
            <div className="glass-card p-4" style={{ cursor: "default" }}>
              <div className="flex items-center justify-between mb-2">
                <div>
                  <div className="font-medium text-sm">MGT-14: Filing of Special Resolution</div>
                  <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                    Must be filed within 30 days of passing the Special Resolution
                  </div>
                </div>
                <StatusBadge
                  status={state.regulatoryFiling.mgt14.filed ? "completed" : "warning"}
                  label={state.regulatoryFiling.mgt14.filed ? "Filed" : "Pending"}
                />
              </div>
              <ChecklistItem
                checked={state.regulatoryFiling.mgt14.filed}
                label="MGT-14 filed with ROC"
                onChange={(val) =>
                  setState((prev) => ({
                    ...prev,
                    regulatoryFiling: {
                      ...prev.regulatoryFiling,
                      mgt14: {
                        filed: val,
                        filedDate: val ? new Date().toISOString() : null,
                      },
                    },
                  }))
                }
              />
            </div>
          )}

          {/* SH-7 */}
          {!capitalSufficient && newSharesCount > 0 && (
            <div className="glass-card p-4" style={{ cursor: "default" }}>
              <div className="flex items-center justify-between mb-2">
                <div>
                  <div className="font-medium text-sm">SH-7: Notice of Alteration of Capital</div>
                  <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                    Required since authorized capital needs to be increased. File within 30 days of passing SR.
                  </div>
                </div>
                <StatusBadge
                  status={state.regulatoryFiling.sh7.filed ? "completed" : "warning"}
                  label={state.regulatoryFiling.sh7.filed ? "Filed" : "Required"}
                />
              </div>
              <ChecklistItem
                checked={state.regulatoryFiling.sh7.filed}
                label="SH-7 filed with ROC for capital increase"
                onChange={(val) =>
                  setState((prev) => ({
                    ...prev,
                    regulatoryFiling: {
                      ...prev.regulatoryFiling,
                      sh7: {
                        filed: val,
                        filedDate: val ? new Date().toISOString() : null,
                      },
                    },
                  }))
                }
              />
            </div>
          )}

          {/* No filings needed message */}
          {!isPrivatePlacement && (capitalSufficient || newSharesCount === 0) && (
            <div className="text-sm" style={{ color: "var(--color-text-muted)" }}>
              No regulatory filings are required at this stage for a Rights Issue with sufficient authorized capital.
            </div>
          )}

          <div className="flex justify-between mt-4">
            <ActionButton onClick={() => goToStep(2)} variant="secondary">
              Back
            </ActionButton>
            <ActionButton
              onClick={() => completeStep(3)}
              disabled={
                (isPrivatePlacement && !state.regulatoryFiling.mgt14.filed) ||
                (!capitalSufficient && newSharesCount > 0 && !state.regulatoryFiling.sh7.filed)
              }
            >
              Proceed to Offer Letters
            </ActionButton>
          </div>
        </div>
      </StepCard>

      {/* Step 5: Offer Letters */}
      <StepCard
        stepNumber={5}
        title={isPrivatePlacement ? "PAS-4 Private Placement Offer Letters" : "Offer Letters"}
        status={getStepStatus(4)}
        expanded={expandedStep === 4}
        onToggle={() => setExpandedStep(expandedStep === 4 ? -1 : 4)}
      >
        <div className="space-y-4">
          <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
            {isPrivatePlacement
              ? "PAS-4 Offer Letters must be sent to each proposed allottee as per Section 42 of the Companies Act. Offers can be made to a maximum of 200 persons in a financial year."
              : "Rights Issue offer letters are sent to existing shareholders in proportion to their current holdings. Shareholders have the right to renounce their entitlement."}
          </p>

          {/* Allottee List */}
          <div className="glass-card overflow-hidden" style={{ cursor: "default" }}>
            <div className="p-4" style={{ borderBottom: "1px solid var(--color-border)" }}>
              <h4 className="font-semibold text-sm">
                Allottee List ({state.preCheck.allottees.filter((a) => a.name).length} persons)
              </h4>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                    <th className="text-left p-3 text-xs" style={{ color: "var(--color-text-muted)" }}>
                      S.No.
                    </th>
                    <th className="text-left p-3 text-xs" style={{ color: "var(--color-text-muted)" }}>
                      Name
                    </th>
                    <th className="text-left p-3 text-xs" style={{ color: "var(--color-text-muted)" }}>
                      Email
                    </th>
                    <th className="text-right p-3 text-xs" style={{ color: "var(--color-text-muted)" }}>
                      Shares
                    </th>
                    <th className="text-right p-3 text-xs" style={{ color: "var(--color-text-muted)" }}>
                      Amount (Rs)
                    </th>
                    <th className="text-center p-3 text-xs" style={{ color: "var(--color-text-muted)" }}>
                      Type
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {state.preCheck.allottees
                    .filter((a) => a.name)
                    .map((allottee, idx) => (
                      <tr key={idx} style={{ borderBottom: "1px solid var(--color-border)" }}>
                        <td className="p-3 font-mono text-xs">{idx + 1}</td>
                        <td className="p-3 font-medium">{allottee.name}</td>
                        <td className="p-3 text-xs" style={{ color: "var(--color-text-muted)" }}>
                          {allottee.email || "-"}
                        </td>
                        <td className="p-3 text-right font-mono">
                          {allottee.shares.toLocaleString("en-IN")}
                        </td>
                        <td className="p-3 text-right font-mono">
                          {(allottee.shares * (faceValue + premium)).toLocaleString("en-IN")}
                        </td>
                        <td className="p-3 text-center">
                          <span
                            className="text-xs px-2 py-0.5 rounded-full"
                            style={{
                              background:
                                allottee.type === "new"
                                  ? "var(--color-info-light)"
                                  : "var(--color-purple-bg)",
                              color:
                                allottee.type === "new"
                                  ? "var(--color-accent-blue)"
                                  : "var(--color-accent-purple-light)",
                            }}
                          >
                            {allottee.type === "new" ? "New" : "Existing"}
                          </span>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            <ActionButton
              onClick={handleGenerateOfferLetters}
              loading={state.offerLetters.generating}
              disabled={state.offerLetters.generated}
            >
              Generate Offer Letters
            </ActionButton>
            {state.offerLetters.generated && !state.offerLetters.sentForAcceptance && (
              <ActionButton
                onClick={handleSendOfferLetters}
                variant="secondary"
              >
                Send for Acceptance
              </ActionButton>
            )}
          </div>

          {state.offerLetters.sentForAcceptance && (
            <div
              className="glass-card p-3 text-sm"
              style={{
                cursor: "default",
                borderColor: "var(--color-accent-emerald-light)",
                background: "var(--color-success-light)",
                color: "var(--color-accent-emerald-light)",
              }}
            >
              Offer letters sent to all allottees for acceptance.
            </div>
          )}

          <div className="flex justify-between mt-4">
            <ActionButton onClick={() => goToStep(3)} variant="secondary">
              Back
            </ActionButton>
            <ActionButton
              onClick={() => completeStep(4)}
              disabled={!state.offerLetters.generated}
            >
              Proceed to Receive Funds
            </ActionButton>
          </div>
        </div>
      </StepCard>

      {/* Step 6: Receive Funds */}
      <StepCard
        stepNumber={6}
        title="Receive Application Money"
        status={getStepStatus(5)}
        expanded={expandedStep === 5}
        onToggle={() => setExpandedStep(expandedStep === 5 ? -1 : 5)}
      >
        <div className="space-y-4">
          <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
            Track application money received from each allottee. All monies must be received
            through the company&apos;s bank account. Cheques/DD should be in the name of the company.
          </p>

          {/* Warning */}
          <div
            className="glass-card p-4"
            style={{
              cursor: "default",
              borderColor: "var(--color-accent-amber)",
              background: "var(--color-warning-light)",
            }}
          >
            <div className="flex items-start gap-3">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent-amber)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0 mt-0.5">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              <div className="text-sm" style={{ color: "var(--color-accent-amber)" }}>
                <span className="font-semibold">Important:</span> Allotment must happen within 60 days
                of receiving the application money. If allotment is not made within 60 days, the money
                must be refunded within 15 days thereafter.
              </div>
            </div>
          </div>

          {/* Per-investor fund tracking */}
          <div className="glass-card overflow-hidden" style={{ cursor: "default" }}>
            <div className="p-4" style={{ borderBottom: "1px solid var(--color-border)" }}>
              <h4 className="font-semibold text-sm">Fund Receipt Status</h4>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                    <th className="text-left p-3 text-xs" style={{ color: "var(--color-text-muted)" }}>
                      Investor
                    </th>
                    <th className="text-right p-3 text-xs" style={{ color: "var(--color-text-muted)" }}>
                      Amount Due (Rs)
                    </th>
                    <th className="text-center p-3 text-xs" style={{ color: "var(--color-text-muted)" }}>
                      Received
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {state.preCheck.allottees
                    .filter((a) => a.name)
                    .map((allottee, idx) => (
                      <tr key={idx} style={{ borderBottom: "1px solid var(--color-border)" }}>
                        <td className="p-3 font-medium">{allottee.name}</td>
                        <td className="p-3 text-right font-mono">
                          {(allottee.shares * (faceValue + premium)).toLocaleString("en-IN")}
                        </td>
                        <td className="p-3 text-center">
                          <input
                            type="checkbox"
                            checked={allottee.fundsReceived}
                            onChange={(e) => {
                              updateAllottee(idx, {
                                fundsReceived: e.target.checked,
                                fundReceivedDate: e.target.checked ? new Date().toISOString() : null,
                              });
                            }}
                            style={{ accentColor: "var(--color-accent-emerald-light)" }}
                          />
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Total received summary */}
          <div className="glass-card p-4 text-center" style={{ cursor: "default" }}>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                  Total Expected
                </div>
                <div className="text-lg font-bold">
                  {formatCurrency(
                    state.preCheck.allottees.reduce((s, a) => s + a.shares * (faceValue + premium), 0)
                  )}
                </div>
              </div>
              <div>
                <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                  Total Received
                </div>
                <div
                  className="text-lg font-bold"
                  style={{ color: "var(--color-accent-emerald-light)" }}
                >
                  {formatCurrency(
                    state.preCheck.allottees
                      .filter((a) => a.fundsReceived)
                      .reduce((s, a) => s + a.shares * (faceValue + premium), 0)
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-between mt-4">
            <ActionButton onClick={() => goToStep(4)} variant="secondary">
              Back
            </ActionButton>
            <ActionButton
              onClick={() => {
                setState((prev) => ({
                  ...prev,
                  receiveFunds: {
                    allFundsReceived: true,
                    moneyReceivedDate: new Date().toISOString(),
                  },
                }));
                completeStep(5);
              }}
              disabled={!state.preCheck.allottees.filter((a) => a.name).every((a) => a.fundsReceived)}
            >
              Proceed to Allotment
            </ActionButton>
          </div>
        </div>
      </StepCard>

      {/* Step 7: Allotment */}
      <StepCard
        stepNumber={7}
        title="Board Meeting for Allotment"
        status={getStepStatus(6)}
        expanded={expandedStep === 6}
        onToggle={() => setExpandedStep(expandedStep === 6 ? -1 : 6)}
      >
        <div className="space-y-4">
          <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
            A Board Meeting must be convened to approve the allotment of shares. Upon approval,
            shares will be allotted and the cap table will be updated automatically.
          </p>

          <ChecklistItem
            checked={state.allotment.boardMeetingHeld}
            label="Board meeting convened for allotment"
            onChange={(val) =>
              setState((prev) => ({
                ...prev,
                allotment: { ...prev.allotment, boardMeetingHeld: val },
              }))
            }
          />

          {/* Allotment Summary */}
          <div className="glass-card p-4" style={{ cursor: "default" }}>
            <h4 className="font-semibold text-sm mb-3">Allotment Summary</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
              <div>
                <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                  Total Shares
                </div>
                <div className="text-lg font-bold font-mono">
                  {newSharesCount.toLocaleString("en-IN")}
                </div>
              </div>
              <div>
                <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                  Face Value
                </div>
                <div className="text-lg font-bold font-mono">
                  Rs {faceValue}
                </div>
              </div>
              <div>
                <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                  Premium
                </div>
                <div className="text-lg font-bold font-mono">
                  Rs {premium}
                </div>
              </div>
              <div>
                <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                  Total Amount
                </div>
                <div className="text-lg font-bold font-mono" style={{ color: "var(--color-accent-emerald-light)" }}>
                  {formatCurrency(newSharesCount * (faceValue + premium))}
                </div>
              </div>
            </div>
          </div>

          {state.allotment.allotmentComplete && (
            <div
              className="glass-card p-4"
              style={{
                cursor: "default",
                borderColor: "var(--color-accent-emerald-light)",
                background: "var(--color-success-light)",
              }}
            >
              <div className="flex items-center gap-2 text-sm font-medium" style={{ color: "var(--color-accent-emerald-light)" }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
                Allotment completed. Cap table has been updated.
              </div>
              <p className="text-xs mt-2" style={{ color: "var(--color-text-muted)" }}>
                Reminder: PAS-3 (Return of Allotment) must be filed within 30 days of allotment.
              </p>
            </div>
          )}

          <div className="flex flex-wrap gap-3">
            {!state.allotment.allotmentComplete && (
              <ActionButton
                onClick={handleCompleteAllotment}
                loading={state.allotment.allotting}
                disabled={!state.allotment.boardMeetingHeld}
                variant="success"
              >
                Complete Allotment
              </ActionButton>
            )}
          </div>

          <div className="flex justify-between mt-4">
            <ActionButton onClick={() => goToStep(5)} variant="secondary">
              Back
            </ActionButton>
            <ActionButton
              onClick={() => completeStep(6)}
              disabled={!state.allotment.allotmentComplete}
            >
              Proceed to Post-Allotment
            </ActionButton>
          </div>
        </div>
      </StepCard>

      {/* Step 8: Post-Allotment */}
      <StepCard
        stepNumber={8}
        title="Post-Allotment Compliance"
        status={getStepStatus(7)}
        expanded={expandedStep === 7}
        onToggle={() => setExpandedStep(expandedStep === 7 ? -1 : 7)}
      >
        <div className="space-y-4">
          <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
            Complete the post-allotment compliance requirements within the statutory timelines.
          </p>

          {/* PAS-3 Filing */}
          <div className="glass-card p-4" style={{ cursor: "default" }}>
            <div className="flex items-center justify-between mb-2">
              <div>
                <div className="font-medium text-sm">PAS-3: Return of Allotment</div>
                <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                  Must be filed within 30 days of allotment
                </div>
              </div>
              <StatusBadge
                status={state.postAllotment.pas3Filed ? "completed" : "warning"}
                label={state.postAllotment.pas3Filed ? "Filed" : "Pending"}
              />
            </div>
            <ChecklistItem
              checked={state.postAllotment.pas3Filed}
              label="PAS-3 filed with ROC"
              onChange={(val) =>
                setState((prev) => ({
                  ...prev,
                  postAllotment: {
                    ...prev.postAllotment,
                    pas3Filed: val,
                    pas3FiledDate: val ? new Date().toISOString() : null,
                  },
                }))
              }
            />
          </div>

          {/* Share Certificates */}
          <div className="glass-card p-4" style={{ cursor: "default" }}>
            <div className="flex items-center justify-between mb-2">
              <div>
                <div className="font-medium text-sm">Share Certificates</div>
                <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                  Must be issued within 2 months of allotment
                </div>
              </div>
              <StatusBadge
                status={state.postAllotment.certificatesGenerated ? "completed" : "pending"}
                label={state.postAllotment.certificatesGenerated ? "Generated" : "Pending"}
              />
            </div>
            <div className="mt-3">
              <ActionButton
                onClick={handleGenerateCertificates}
                loading={state.postAllotment.generatingCerts}
                disabled={state.postAllotment.certificatesGenerated}
              >
                Generate Share Certificates
              </ActionButton>
            </div>
          </div>

          {/* Register of Members */}
          <div className="glass-card p-4" style={{ cursor: "default" }}>
            <div className="flex items-center justify-between mb-2">
              <div>
                <div className="font-medium text-sm">Register of Members (MGT-1)</div>
                <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                  Update within 7 days of allotment
                </div>
              </div>
              <StatusBadge
                status={state.postAllotment.registerUpdated ? "completed" : "pending"}
                label={state.postAllotment.registerUpdated ? "Updated" : "Pending"}
              />
            </div>
            <ChecklistItem
              checked={state.postAllotment.registerUpdated}
              label="Register of Members updated with new allottees"
              onChange={(val) =>
                setState((prev) => ({
                  ...prev,
                  postAllotment: { ...prev.postAllotment, registerUpdated: val },
                }))
              }
            />
          </div>

          {/* Completion */}
          {state.postAllotment.pas3Filed &&
            state.postAllotment.certificatesGenerated &&
            state.postAllotment.registerUpdated && (
              <div
                className="glass-card p-6 text-center"
                style={{
                  cursor: "default",
                  borderColor: "var(--color-accent-emerald-light)",
                  background: "var(--color-success-light)",
                }}
              >
                <div className="flex flex-col items-center gap-3">
                  <div
                    className="w-14 h-14 rounded-full flex items-center justify-center"
                    style={{ background: "var(--color-success-light)" }}
                  >
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent-emerald-light)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                      <polyline points="22 4 12 14.01 9 11.01" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-bold text-lg" style={{ color: "var(--color-accent-emerald-light)" }}>
                      Share Issuance Complete
                    </h3>
                    <p className="text-sm mt-1" style={{ color: "var(--color-text-secondary)" }}>
                      All {newSharesCount.toLocaleString("en-IN")} shares have been successfully issued and all
                      post-allotment compliance has been completed.
                    </p>
                  </div>
                  <ActionButton
                    onClick={onComplete}
                    variant="success"
                  >
                    View Updated Cap Table
                  </ActionButton>
                </div>
              </div>
            )}

          <div className="flex justify-start mt-4">
            <ActionButton onClick={() => goToStep(6)} variant="secondary">
              Back
            </ActionButton>
          </div>
        </div>
      </StepCard>
    </div>
  );
}
