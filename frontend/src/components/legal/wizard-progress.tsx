"use client";

interface WizardProgressProps {
  steps: { step_number: number; title: string }[];
  currentStep: number;
  onStepClick?: (step: number) => void;
}

export default function WizardProgress({ steps, currentStep, onStepClick }: WizardProgressProps) {
  return (
    <div className="w-full overflow-x-auto pb-2" style={{ scrollbarWidth: "thin" }}>
      <div className="flex items-center min-w-max">
        {steps.map((step, idx) => {
          const isCompleted = idx < currentStep;
          const isCurrent = idx === currentStep;
          const isFuture = idx > currentStep;
          const isClickable = isCompleted && onStepClick;

          return (
            <div key={step.step_number} className="flex items-center">
              {/* Step circle + label */}
              <button
                onClick={() => isClickable && onStepClick(idx)}
                disabled={!isClickable}
                className={`flex flex-col items-center gap-1.5 ${
                  isClickable ? "cursor-pointer" : "cursor-default"
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-all ${
                    isCurrent ? "ring-4 ring-purple-500/10" : ""
                  }`}
                  style={
                    isCompleted
                      ? { background: "var(--color-success-light)", borderColor: "var(--color-success)", color: "var(--color-success)" }
                      : isCurrent
                      ? { background: "rgba(139,92,246,0.2)", borderColor: "#8b5cf6", color: "var(--color-accent-purple-light)" }
                      : { background: "var(--color-bg-card)", borderColor: "var(--color-border)", color: "var(--color-text-muted)" }
                  }
                >
                  {isCompleted ? (
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    idx + 1
                  )}
                </div>
                <span
                  className="text-[10px] font-medium max-w-[80px] text-center leading-tight"
                  style={{
                    color: isCompleted
                      ? "var(--color-success)"
                      : isCurrent
                      ? "var(--color-accent-purple-light)"
                      : "var(--color-text-muted)",
                  }}
                >
                  {step.title}
                </span>
              </button>

              {/* Connector line */}
              {idx < steps.length - 1 && (
                <div
                  className="w-8 lg:w-12 h-0.5 mx-1 mt-[-16px]"
                  style={{
                    background: isCompleted ? "rgba(16,185,129,0.5)" : "var(--color-border)",
                  }}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
