"use client";

import { useState, useEffect } from "react";
import { getWorkflowStatus, triggerNextStep } from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface WorkflowStep {
  index: number;
  key: string;
  name: string;
  description: string;
  status: "completed" | "current" | "upcoming";
}

interface WorkflowData {
  entity_type: string;
  company_status: string;
  steps: WorkflowStep[];
  current_step_index: number;
  total_steps: number;
  completed_steps: number;
  progress_pct: number;
}

// ---------------------------------------------------------------------------
// Step Icons
// ---------------------------------------------------------------------------

function CompletedIcon() {
  return (
    <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
    </svg>
  );
}

function CurrentIcon() {
  return (
    <div className="relative flex items-center justify-center">
      <span className="absolute w-5 h-5 rounded-full bg-blue-500/30 animate-ping" />
      <span className="relative w-3 h-3 rounded-full bg-blue-500" />
    </div>
  );
}

function UpcomingIcon() {
  return (
    <span className="w-3 h-3 rounded-full bg-gray-600 border-2 border-gray-500" />
  );
}

// ---------------------------------------------------------------------------
// Entity type display helpers
// ---------------------------------------------------------------------------

const ENTITY_LABELS: Record<string, string> = {
  private_limited: "Private Limited Company",
  opc: "One Person Company (OPC)",
  llp: "Limited Liability Partnership (LLP)",
  section_8: "Section 8 Company (Non-Profit)",
  sole_proprietorship: "Sole Proprietorship",
  public_limited: "Public Limited Company",
  partnership: "Partnership Firm",
};

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export default function WorkflowProgress({ companyId }: { companyId: number }) {
  const [workflow, setWorkflow] = useState<WorkflowData | null>(null);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [expandedStep, setExpandedStep] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Fetch workflow status
  const fetchWorkflow = async () => {
    try {
      setError(null);
      const data = await getWorkflowStatus(companyId);
      setWorkflow(data);
    } catch (err: any) {
      setError(err.message || "Failed to load workflow");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkflow();
  }, [companyId]);

  // Handle "Next Step" action
  const handleNextStep = async () => {
    setTriggering(true);
    try {
      await triggerNextStep(companyId);
      // Refresh workflow after triggering
      await fetchWorkflow();
    } catch (err: any) {
      setError(err.message || "Failed to trigger next step");
    } finally {
      setTriggering(false);
    }
  };

  // Toggle step expansion
  const toggleStep = (index: number) => {
    setExpandedStep(expandedStep === index ? null : index);
  };

  // ---------------------------------------------------------------------------
  // Loading state
  // ---------------------------------------------------------------------------
  if (loading) {
    return (
      <div
        className="rounded-xl border p-6"
        style={{
          background: "var(--color-bg-card, #1a1f35)",
          borderColor: "var(--color-border, #2a3050)",
        }}
      >
        <div className="animate-pulse space-y-4">
          <div className="h-5 bg-gray-700/50 rounded w-48" />
          <div className="h-2 bg-gray-700/50 rounded w-full" />
          <div className="space-y-3 mt-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gray-700/50" />
                <div className="h-4 bg-gray-700/50 rounded w-40" />
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // Error state
  // ---------------------------------------------------------------------------
  if (error && !workflow) {
    return (
      <div
        className="rounded-xl border p-6"
        style={{
          background: "var(--color-bg-card, #1a1f35)",
          borderColor: "var(--color-border, #2a3050)",
        }}
      >
        <p className="text-red-400 text-sm">{error}</p>
        <button
          onClick={fetchWorkflow}
          className="mt-3 text-xs text-purple-400 hover:text-purple-300 transition-colors"
        >
          Try again
        </button>
      </div>
    );
  }

  if (!workflow || !workflow.steps || workflow.steps.length === 0) {
    return (
      <div
        className="rounded-xl border p-6"
        style={{
          background: "var(--color-bg-card, #1a1f35)",
          borderColor: "var(--color-border, #2a3050)",
        }}
      >
        <p className="text-gray-400 text-sm">No workflow steps available for this entity type.</p>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------
  const entityLabel = ENTITY_LABELS[workflow.entity_type] || workflow.entity_type;
  const isComplete = workflow.completed_steps >= workflow.total_steps;

  return (
    <div
      className="rounded-xl border overflow-hidden"
      style={{
        background: "var(--color-bg-card, #1a1f35)",
        borderColor: "var(--color-border, #2a3050)",
      }}
    >
      {/* Header */}
      <div className="px-6 py-4 border-b" style={{ borderColor: "var(--color-border, #2a3050)" }}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">Incorporation Workflow</h3>
            <p className="text-xs text-gray-400 mt-0.5">{entityLabel}</p>
          </div>
          <div className="text-right">
            <span className="text-lg font-bold text-white">{workflow.progress_pct}%</span>
            <p className="text-[10px] text-gray-500">
              {workflow.completed_steps}/{workflow.total_steps} steps
            </p>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-3 h-1.5 bg-gray-700/50 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-700 ease-out"
            style={{
              width: `${workflow.progress_pct}%`,
              background: isComplete
                ? "linear-gradient(90deg, #10b981, #34d399)"
                : "linear-gradient(90deg, #8b5cf6, #6366f1)",
            }}
          />
        </div>
      </div>

      {/* Steps */}
      <div className="px-6 py-4">
        <div className="space-y-0">
          {workflow.steps.map((step, idx) => {
            const isLast = idx === workflow.steps.length - 1;
            const isExpanded = expandedStep === idx;

            return (
              <div key={step.key}>
                {/* Step row */}
                <button
                  onClick={() => toggleStep(idx)}
                  className="w-full flex items-start gap-3 py-2.5 text-left hover:bg-white/[0.02] rounded-lg transition-colors px-1 -mx-1"
                >
                  {/* Connector line + icon */}
                  <div className="flex flex-col items-center shrink-0 pt-0.5">
                    <div className="w-8 h-8 rounded-full flex items-center justify-center"
                      style={{
                        background:
                          step.status === "completed"
                            ? "rgba(16, 185, 129, 0.15)"
                            : step.status === "current"
                            ? "rgba(59, 130, 246, 0.15)"
                            : "rgba(75, 85, 99, 0.15)",
                      }}
                    >
                      {step.status === "completed" && <CompletedIcon />}
                      {step.status === "current" && <CurrentIcon />}
                      {step.status === "upcoming" && <UpcomingIcon />}
                    </div>
                    {!isLast && (
                      <div
                        className="w-0.5 flex-1 min-h-[16px] mt-1"
                        style={{
                          background:
                            step.status === "completed"
                              ? "rgba(16, 185, 129, 0.3)"
                              : "rgba(75, 85, 99, 0.3)",
                        }}
                      />
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0 pb-1">
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-sm font-medium ${
                          step.status === "completed"
                            ? "text-emerald-400"
                            : step.status === "current"
                            ? "text-blue-400"
                            : "text-gray-500"
                        }`}
                      >
                        {step.name}
                      </span>
                      {step.status === "completed" && (
                        <span className="text-[10px] text-emerald-500/70 font-medium uppercase tracking-wider">
                          Done
                        </span>
                      )}
                      {step.status === "current" && (
                        <span className="text-[10px] text-blue-400/70 font-medium uppercase tracking-wider">
                          In Progress
                        </span>
                      )}
                    </div>

                    {/* Expand indicator */}
                    <div className="flex items-center gap-1 mt-0.5">
                      <svg
                        className={`w-3 h-3 text-gray-600 transition-transform ${isExpanded ? "rotate-90" : ""}`}
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        strokeWidth={2}
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                      </svg>
                      <span className="text-[11px] text-gray-600">Details</span>
                    </div>

                    {/* Expanded content */}
                    {isExpanded && (
                      <div
                        className="mt-2 p-3 rounded-lg text-xs text-gray-400 leading-relaxed"
                        style={{ background: "rgba(255, 255, 255, 0.03)" }}
                      >
                        {step.description}
                      </div>
                    )}
                  </div>
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Footer action */}
      {!isComplete && (
        <div
          className="px-6 py-4 border-t"
          style={{ borderColor: "var(--color-border, #2a3050)" }}
        >
          {error && (
            <p className="text-xs text-red-400 mb-2">{error}</p>
          )}
          <button
            onClick={handleNextStep}
            disabled={triggering}
            className="w-full py-2.5 rounded-lg text-sm font-medium text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              background: triggering
                ? "rgba(139, 92, 246, 0.3)"
                : "linear-gradient(135deg, #8b5cf6, #6366f1)",
            }}
          >
            {triggering ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Processing...
              </span>
            ) : (
              "Trigger Next Step"
            )}
          </button>
        </div>
      )}

      {/* Completion banner */}
      {isComplete && (
        <div
          className="px-6 py-4 border-t text-center"
          style={{
            borderColor: "rgba(16, 185, 129, 0.2)",
            background: "rgba(16, 185, 129, 0.05)",
          }}
        >
          <div className="flex items-center justify-center gap-2">
            <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12c0 4.97-4.03 9-9 9s-9-4.03-9-9 4.03-9 9-9 9 4.03 9 9z" />
            </svg>
            <span className="text-sm font-medium text-emerald-400">
              All workflow steps completed
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
