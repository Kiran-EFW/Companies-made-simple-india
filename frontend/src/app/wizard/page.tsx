"use client";

import { useState } from "react";
import Link from "next/link";
import type { WizardResponse } from "@/lib/api";
import Footer from "@/components/footer";

interface WizardStep {
  question: string;
  description: string;
  options: { label: string; iconPath: string; value: string | boolean }[];
  field: string;
}

const STEPS: WizardStep[] = [
  {
    question: "Is this a non-profit or social enterprise?",
    description: "Section 8 companies have special tax benefits and licensing requirements.",
    options: [
      { label: "No, it's for-profit", iconPath: "M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 00.75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 00-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0112 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 01-.673-.38m0 0A2.18 2.18 0 013 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 013.413-.387m7.5 0V5.25A2.25 2.25 0 0013.5 3h-3a2.25 2.25 0 00-2.25 2.25v.894m7.5 0a48.667 48.667 0 00-7.5 0M12 12.75h.008v.008H12v-.008z", value: false },
      { label: "Yes, non-profit", iconPath: "M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z", value: true },
    ],
    field: "is_nonprofit",
  },
  {
    question: "Are you starting solo or with co-founders?",
    description: "This affects the entity types available to you.",
    options: [
      { label: "Solo founder", iconPath: "M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z", value: true },
      { label: "With co-founders", iconPath: "M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z", value: false },
    ],
    field: "is_solo",
  },
  {
    question: "Are you planning to raise investor funding?",
    description: "VC/Angel investors typically require specific company structures.",
    options: [
      { label: "Yes, planning to raise", iconPath: "M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941", value: true },
      { label: "No, bootstrapping", iconPath: "M11.42 15.17l-5.648-3.007A2.972 2.972 0 006 12.157V9.314c0-.592.35-1.128.894-1.367l6.25-2.75a2.99 2.99 0 012.712 0l6.25 2.75c.544.24.894.775.894 1.367v2.843a2.972 2.972 0 01-.228.657l-5.648 3.007m-2.304-6.267l6.25-2.75m-6.25 2.75l-6.25-2.75m6.25 2.75v10.5", value: false },
    ],
    field: "seeking_funding",
  },
  {
    question: "What's your expected annual revenue?",
    description: "This helps determine the most tax-efficient structure.",
    options: [
      { label: "Below ₹50 Lakhs", iconPath: "M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z", value: "below_50l" },
      { label: "₹50L \u2013 ₹2 Crore", iconPath: "M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z", value: "50l_to_2cr" },
      { label: "Above ₹2 Crore", iconPath: "M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5m.75-9l3-3 2.148 2.148A12.061 12.061 0 0116.5 7.605", value: "above_2cr" },
    ],
    field: "expected_revenue",
  },
  {
    question: "Is this a professional services firm?",
    description: "Consulting, legal, accounting, or advisory firms have specific options.",
    options: [
      { label: "Yes, professional services", iconPath: "M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5", value: true },
      { label: "No, product/other", iconPath: "M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z", value: false },
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
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
        const res = await fetch(`${baseUrl}/wizard/recommend`, {
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
        <Link href="/" className="flex items-center gap-2.5">
          <img src="/logo-icon.png" alt="Anvils" className="w-6 h-6 object-contain" />
          <span className="text-xl font-bold gradient-text" style={{ fontFamily: "var(--font-display)" }}>Anvils</span>
        </Link>
        <div className="hidden md:flex items-center gap-6">
          <Link href="/pricing" className="text-sm font-medium" style={{ color: "var(--color-text-secondary)" }}>
            Pricing
          </Link>
          <Link href="/compare" className="text-sm font-medium" style={{ color: "var(--color-text-secondary)" }}>
            Compare
          </Link>
          <Link href="/login" className="text-sm font-medium" style={{ color: "var(--color-text-secondary)" }}>
            Log in
          </Link>
          <Link href="/signup" className="btn-primary text-sm !py-2 !px-5">
            Get Started
          </Link>
        </div>
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
                      <div className="w-10 h-10 rounded-xl flex items-center justify-center mx-auto mb-3" style={{ background: "rgba(139, 92, 246, 0.15)" }}>
                        <svg className="w-5 h-5" style={{ color: "var(--color-accent-purple-light)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d={option.iconPath} />
                        </svg>
                      </div>
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
                AI Recommendation
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
                    Advantages
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
                    Considerations
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
      <Footer />
    </div>
  );
}
