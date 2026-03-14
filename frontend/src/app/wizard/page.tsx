"use client";

import { useState } from "react";
import Link from "next/link";
import type { WizardResponse } from "@/lib/api";

interface WizardStep {
  question: string;
  description: string;
  options: { label: string; emoji: string; value: string | boolean }[];
  field: string;
}

const STEPS: WizardStep[] = [
  {
    question: "Is this a non-profit or social enterprise?",
    description: "Section 8 companies have special tax benefits and licensing requirements.",
    options: [
      { label: "No, it's for-profit", emoji: "💼", value: false },
      { label: "Yes, non-profit", emoji: "💚", value: true },
    ],
    field: "is_nonprofit",
  },
  {
    question: "Are you starting solo or with co-founders?",
    description: "This affects the entity types available to you.",
    options: [
      { label: "Solo founder", emoji: "👤", value: true },
      { label: "With co-founders", emoji: "👥", value: false },
    ],
    field: "is_solo",
  },
  {
    question: "Are you planning to raise investor funding?",
    description: "VC/Angel investors typically require specific company structures.",
    options: [
      { label: "Yes, planning to raise", emoji: "📈", value: true },
      { label: "No, bootstrapping", emoji: "🏗️", value: false },
    ],
    field: "seeking_funding",
  },
  {
    question: "What's your expected annual revenue?",
    description: "This helps determine the most tax-efficient structure.",
    options: [
      { label: "Below ₹50 Lakhs", emoji: "🌱", value: "below_50l" },
      { label: "₹50L – ₹2 Crore", emoji: "🌿", value: "50l_to_2cr" },
      { label: "Above ₹2 Crore", emoji: "🌳", value: "above_2cr" },
    ],
    field: "expected_revenue",
  },
  {
    question: "Is this a professional services firm?",
    description: "Consulting, legal, accounting, or advisory firms have specific options.",
    options: [
      { label: "Yes, professional services", emoji: "👔", value: true },
      { label: "No, product/other", emoji: "🚀", value: false },
    ],
    field: "is_professional_services",
  },
];

const ENTITY_COLORS: Record<string, string> = {
  private_limited: "139, 92, 246",
  opc: "59, 130, 246",
  llp: "16, 185, 129",
  section_8: "245, 158, 11",
  sole_proprietorship: "244, 63, 94",
  partnership: "139, 92, 246",
  public_limited: "59, 130, 246",
};

export default function WizardPage() {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string | boolean>>({
    is_nonprofit: false,
    is_solo: false,
    seeking_funding: false,
    expected_revenue: "below_50l",
    is_professional_services: false,
    has_foreign_involvement: false,
  });
  const [result, setResult] = useState<WizardResponse | null>(null);
  const [loading, setLoading] = useState(false);

  // Skip irrelevant steps
  function getVisibleSteps(): WizardStep[] {
    if (answers.is_nonprofit === true) {
      return [STEPS[0]]; // Only ask nonprofit question, then recommend directly
    }
    return STEPS;
  }

  async function handleSelect(field: string, value: string | boolean) {
    const newAnswers = { ...answers, [field]: value };
    setAnswers(newAnswers);

    const visibleSteps = getVisibleSteps();
    const isLastStep = currentStep >= visibleSteps.length - 1 || (field === "is_nonprofit" && value === true);

    if (isLastStep) {
      // Fetch recommendation
      setLoading(true);
      try {
        const res = await fetch("http://localhost:8000/api/v1/wizard/recommend", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(newAnswers),
        });
        if (res.ok) {
          setResult(await res.json());
        }
      } catch {
        // Fallback — no backend
      }
      setLoading(false);
    } else {
      setCurrentStep(currentStep + 1);
    }
  }

  function resetWizard() {
    setCurrentStep(0);
    setAnswers({
      is_nonprofit: false,
      is_solo: false,
      seeking_funding: false,
      expected_revenue: "below_50l",
      is_professional_services: false,
      has_foreign_involvement: false,
    });
    setResult(null);
  }

  const visibleSteps = getVisibleSteps();
  const step = visibleSteps[currentStep];

  return (
    <div className="glow-bg min-h-screen">
      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-5 max-w-7xl mx-auto">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-2xl">⚡</span>
          <span className="text-xl font-bold" style={{ fontFamily: "var(--font-display)" }}>
            <span className="gradient-text">CMS</span>{" "}
            <span style={{ color: "var(--color-text-secondary)" }}>India</span>
          </span>
        </Link>
        <Link href="/pricing" className="btn-secondary text-sm !py-2 !px-5">
          View Pricing →
        </Link>
      </nav>

      <div className="relative z-10 max-w-3xl mx-auto px-6 py-12">
        {!result ? (
          <>
            {/* Progress */}
            <div className="flex gap-2 mb-12 justify-center">
              {visibleSteps.map((_, i) => (
                <div
                  key={i}
                  className="h-1.5 rounded-full transition-all duration-300"
                  style={{
                    width: i === currentStep ? "48px" : "24px",
                    background:
                      i < currentStep
                        ? "var(--color-accent-emerald)"
                        : i === currentStep
                          ? "var(--color-accent-purple)"
                          : "var(--color-border)",
                  }}
                />
              ))}
            </div>

            {/* Question */}
            {step && (
              <div className="text-center animate-fade-in-up">
                <div className="badge badge-purple mb-6 mx-auto w-fit">
                  Step {currentStep + 1} of {visibleSteps.length}
                </div>
                <h1
                  className="text-3xl md:text-4xl font-bold mb-3"
                  style={{ fontFamily: "var(--font-display)" }}
                >
                  {step.question}
                </h1>
                <p className="text-lg mb-10" style={{ color: "var(--color-text-secondary)" }}>
                  {step.description}
                </p>

                <div className={`grid gap-4 max-w-xl mx-auto ${step.options.length === 3 ? "grid-cols-1" : "grid-cols-2"}`}>
                  {step.options.map((option) => (
                    <button
                      key={String(option.value)}
                      onClick={() => handleSelect(step.field, option.value)}
                      className="glass-card p-6 text-center transition-all hover:scale-[1.02]"
                    >
                      <div className="text-4xl mb-3">{option.emoji}</div>
                      <div className="font-semibold text-lg">{option.label}</div>
                    </button>
                  ))}
                </div>

                {currentStep > 0 && (
                  <button
                    onClick={() => setCurrentStep(currentStep - 1)}
                    className="mt-8 text-sm"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    ← Go back
                  </button>
                )}
              </div>
            )}
          </>
        ) : (
          /* ── Results ── */
          <div className="animate-fade-in-up">
            <div className="text-center mb-10">
              <div className="badge badge-emerald mb-4 mx-auto w-fit">
                🎯 AI Recommendation
              </div>
              <h1
                className="text-3xl md:text-4xl font-bold mb-3"
                style={{ fontFamily: "var(--font-display)" }}
              >
                We recommend a{" "}
                <span className="gradient-text">{result.recommended.name}</span>
              </h1>
              <p className="text-lg" style={{ color: "var(--color-text-secondary)" }}>
                {result.recommended.match_score}% match for your situation
              </p>
            </div>

            {/* Recommended Card */}
            <div
              className="glass-card p-8 mb-6"
              style={{
                borderColor: `rgba(${ENTITY_COLORS[result.recommended.entity_type] || "139, 92, 246"}, 0.5)`,
                cursor: "default",
              }}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">{result.recommended.name}</h2>
                <div
                  className="text-sm font-bold px-3 py-1 rounded-full"
                  style={{
                    background: `rgba(${ENTITY_COLORS[result.recommended.entity_type] || "139, 92, 246"}, 0.2)`,
                    color: `rgba(${ENTITY_COLORS[result.recommended.entity_type] || "139, 92, 246"}, 1)`,
                  }}
                >
                  {result.recommended.match_score}% Match
                </div>
              </div>

              <p className="mb-4 text-sm" style={{ color: "var(--color-text-secondary)" }}>
                <strong>Best for:</strong> {result.recommended.best_for}
              </p>

              <div className="grid md:grid-cols-2 gap-4 mb-6">
                <div>
                  <div className="text-sm font-semibold mb-2" style={{ color: "var(--color-accent-emerald-light)" }}>
                    ✅ Advantages
                  </div>
                  <ul className="space-y-1.5">
                    {result.recommended.pros.map((pro, i) => (
                      <li key={i} className="text-sm flex gap-2" style={{ color: "var(--color-text-secondary)" }}>
                        <span style={{ color: "var(--color-accent-emerald)" }}>•</span> {pro}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <div className="text-sm font-semibold mb-2" style={{ color: "var(--color-accent-amber)" }}>
                    ⚠️ Considerations
                  </div>
                  <ul className="space-y-1.5">
                    {result.recommended.cons.map((con, i) => (
                      <li key={i} className="text-sm flex gap-2" style={{ color: "var(--color-text-secondary)" }}>
                        <span style={{ color: "var(--color-accent-amber)" }}>•</span> {con}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <Link
                href={`/pricing?entity=${result.recommended.entity_type}`}
                className="btn-primary w-full text-center justify-center"
              >
                See Pricing for {result.recommended.name} →
              </Link>
            </div>

            {/* Alternatives */}
            {result.alternatives.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--color-text-muted)" }}>
                  OTHER OPTIONS TO CONSIDER
                </h3>
                <div className="space-y-3">
                  {result.alternatives.map((alt) => (
                    <Link
                      key={alt.entity_type}
                      href={`/pricing?entity=${alt.entity_type}`}
                      className="glass-card p-5 flex items-center justify-between block"
                    >
                      <div>
                        <div className="font-semibold">{alt.name}</div>
                        <div className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
                          {alt.best_for}
                        </div>
                      </div>
                      <div className="text-sm font-bold" style={{ color: "var(--color-text-muted)" }}>
                        {alt.match_score}% match →
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            )}

            <button
              onClick={resetWizard}
              className="btn-secondary w-full mt-6 text-center justify-center"
            >
              Start Over
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
