"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import {
  getLegalTemplateDefinition,
  createLegalDraft,
  getLegalDraft,
  updateLegalDraftClauses,
  generateLegalPreview,
  finalizeLegalDocument,
  getLegalDownloadUrl,
} from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import ClauseCard from "@/components/legal/clause-card";
import WizardProgress from "@/components/legal/wizard-progress";
import DocumentPreview from "@/components/legal/document-preview";

export default function DocumentWizardPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const templateType = params.type as string;
  const existingDraftId = searchParams.get("draft");

  const [templateDef, setTemplateDef] = useState<any>(null);
  const [draftId, setDraftId] = useState<number | null>(existingDraftId ? Number(existingDraftId) : null);
  const [currentStep, setCurrentStep] = useState(0);
  const [clauseValues, setClauseValues] = useState<Record<string, any>>({});
  const [previewHtml, setPreviewHtml] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auth guard
  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  // Load template definition and create/load draft
  useEffect(() => {
    if (authLoading || !user) return;

    const init = async () => {
      try {
        const def = await getLegalTemplateDefinition(templateType);
        if (!def) {
          setError("Template not found");
          setLoading(false);
          return;
        }
        setTemplateDef(def);

        // Initialize clause values with defaults
        const defaults: Record<string, any> = {};
        if (def.clauses) {
          for (const clause of def.clauses) {
            if (clause.default !== undefined && clause.default !== null) {
              defaults[clause.id] = clause.default;
            }
          }
        }

        if (existingDraftId) {
          // Load existing draft
          try {
            const draft = await getLegalDraft(Number(existingDraftId));
            setDraftId(draft.id);
            setClauseValues({ ...defaults, ...(draft.clauses_config || {}) });
          } catch {
            // If draft load fails, create new
            const draft = await createLegalDraft({ template_type: templateType });
            setDraftId(draft.id);
            setClauseValues(defaults);
          }
        } else {
          // Create new draft
          const draft = await createLegalDraft({ template_type: templateType });
          setDraftId(draft.id);
          setClauseValues(defaults);
        }
      } catch (err: any) {
        setError(err.message || "Failed to load template");
      } finally {
        setLoading(false);
      }
    };
    init();
  }, [templateType, existingDraftId, user, authLoading]);

  // Save current clause values
  const saveProgress = useCallback(async () => {
    if (!draftId) return;
    setSaving(true);
    try {
      await updateLegalDraftClauses(draftId, clauseValues);
    } catch (err) {
      console.error("Failed to save progress:", err);
    } finally {
      setSaving(false);
    }
  }, [draftId, clauseValues]);

  const handleClauseChange = (clauseId: string, value: any) => {
    setClauseValues((prev) => ({ ...prev, [clauseId]: value }));
  };

  const handleNext = async () => {
    await saveProgress();
    if (currentStep < (templateDef?.steps?.length ?? 0) - 1) {
      setCurrentStep((prev) => prev + 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const handleStepClick = async (step: number) => {
    if (step < currentStep) {
      await saveProgress();
      setCurrentStep(step);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const handleGeneratePreview = async () => {
    if (!draftId) return;
    setGenerating(true);
    try {
      await saveProgress();
      const result = await generateLegalPreview(draftId);
      setPreviewHtml(result.generated_html);
    } catch (err: any) {
      setError(err.message || "Failed to generate preview");
    } finally {
      setGenerating(false);
    }
  };

  const handleFinalize = async () => {
    if (!draftId) return;
    try {
      await finalizeLegalDocument(draftId);
      // Open download in new tab
      const url = getLegalDownloadUrl(draftId);
      window.open(url, "_blank");
      router.push("/documents");
    } catch (err: any) {
      setError(err.message || "Failed to finalize document");
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-800 rounded w-64" />
          <div className="h-2 bg-gray-800 rounded w-full" />
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 bg-gray-800 rounded-xl" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !templateDef) {
    return (
      <div className="p-8 text-center">
        <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-8 max-w-md mx-auto">
          <svg className="w-10 h-10 text-red-400 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          <p className="text-sm text-red-400 mb-4">{error}</p>
          <button
            onClick={() => router.push("/documents")}
            className="text-sm text-purple-400 hover:text-purple-300 font-medium"
          >
            Back to Documents
          </button>
        </div>
      </div>
    );
  }

  if (!templateDef) return null;

  const steps = templateDef.steps || [];
  const allClauses = templateDef.clauses || [];
  const currentStepDef = steps[currentStep];
  const isLastStep = currentStep === steps.length - 1;
  const showPreview = previewHtml !== null;

  // Get clauses for current step
  const stepClauses = currentStepDef
    ? allClauses.filter((c: any) => currentStepDef.clause_ids?.includes(c.id))
    : [];

  return (
    <div className="p-6 lg:p-8 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => router.push("/documents")}
          className="text-gray-400 hover:text-white transition-colors"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
        </button>
        <div>
          <h1 className="text-xl font-bold" style={{ fontFamily: "var(--font-display)" }}>
            {templateDef.name}
          </h1>
          <p className="text-xs text-gray-400">{templateDef.description}</p>
        </div>
      </div>

      {/* Progress Bar */}
      <WizardProgress
        steps={steps}
        currentStep={currentStep}
        onStepClick={handleStepClick}
      />

      {/* Error Banner */}
      {error && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-3 flex items-center gap-2">
          <svg className="w-4 h-4 text-red-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          <p className="text-xs text-red-300 flex-1">{error}</p>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-red-300">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* Preview View */}
      {showPreview ? (
        <div className="space-y-4">
          <DocumentPreview html={previewHtml!} title="Document Preview" />
          <div className="flex items-center justify-between">
            <button
              onClick={() => setPreviewHtml(null)}
              className="px-4 py-2 rounded-lg text-sm font-medium text-gray-400 hover:text-white border border-gray-700 hover:border-gray-600 transition-colors"
            >
              Back to Editing
            </button>
            <button
              onClick={handleFinalize}
              className="px-6 py-2.5 rounded-lg text-sm font-medium bg-emerald-600 hover:bg-emerald-500 text-white transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
              </svg>
              Finalize & Download
            </button>
          </div>
        </div>
      ) : (
        <>
          {/* Step Header */}
          {currentStepDef && (
            <div className="border-b border-gray-700 pb-4">
              <h2 className="text-lg font-bold text-white" style={{ fontFamily: "var(--font-display)" }}>
                Step {currentStep + 1}: {currentStepDef.title}
              </h2>
              {currentStepDef.description && (
                <p className="text-xs text-gray-400 mt-1">{currentStepDef.description}</p>
              )}
            </div>
          )}

          {/* Clause Cards */}
          <div className="space-y-4">
            {stepClauses.map((clause: any) => (
              <ClauseCard
                key={clause.id}
                clause={clause}
                value={clauseValues[clause.id]}
                onChange={handleClauseChange}
                allValues={clauseValues}
              />
            ))}
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-700">
            <button
              onClick={handleBack}
              disabled={currentStep === 0}
              className="px-4 py-2 rounded-lg text-sm font-medium text-gray-400 hover:text-white border border-gray-700 hover:border-gray-600 transition-colors disabled:opacity-30 disabled:cursor-not-allowed flex items-center gap-1.5"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
              </svg>
              Back
            </button>

            <div className="flex items-center gap-3">
              {saving && (
                <span className="text-[10px] text-gray-500 flex items-center gap-1">
                  <div className="w-2 h-2 rounded-full bg-purple-500 animate-pulse" />
                  Saving...
                </span>
              )}

              {isLastStep ? (
                <button
                  onClick={handleGeneratePreview}
                  disabled={generating}
                  className="px-6 py-2.5 rounded-lg text-sm font-medium bg-purple-600 hover:bg-purple-500 text-white transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  {generating ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      Generate Preview
                    </>
                  )}
                </button>
              ) : (
                <button
                  onClick={handleNext}
                  className="px-6 py-2.5 rounded-lg text-sm font-medium bg-purple-600 hover:bg-purple-500 text-white transition-colors flex items-center gap-1.5"
                >
                  Next
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                  </svg>
                </button>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
