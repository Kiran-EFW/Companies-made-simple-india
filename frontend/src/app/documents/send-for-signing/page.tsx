"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  getLegalDrafts,
  getLegalDraft,
  createSignatureRequest,
  sendSigningEmails,
} from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import Footer from "@/components/footer";

interface Signatory {
  name: string;
  email: string;
  designation: string;
  signing_order: number;
}

function SendForSigningContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, loading: authLoading } = useAuth();
  const documentIdParam = searchParams.get("documentId");

  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Step 1: Document
  const [documents, setDocuments] = useState<any[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<number | null>(
    documentIdParam ? Number(documentIdParam) : null
  );
  const [selectedDoc, setSelectedDoc] = useState<any>(null);

  // Step 2: Signatories
  const [signatories, setSignatories] = useState<Signatory[]>([
    { name: "", email: "", designation: "", signing_order: 1 },
    { name: "", email: "", designation: "", signing_order: 2 },
  ]);
  const [signingMode, setSigningMode] = useState<"parallel" | "sequential">("parallel");

  // Step 3: Settings
  const [customMessage, setCustomMessage] = useState("");
  const [expiryDays, setExpiryDays] = useState(30);
  const [reminderDays, setReminderDays] = useState(3);

  // Auth guard
  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  // Fetch finalized documents
  useEffect(() => {
    if (authLoading || !user) return;

    const fetchDocs = async () => {
      try {
        const drafts = await getLegalDrafts();
        const finalized = (Array.isArray(drafts) ? drafts : []).filter(
          (d: any) => d.status === "finalized" || d.status === "downloaded"
        );
        setDocuments(finalized);

        // If documentId param provided, load that document
        if (documentIdParam) {
          const docId = Number(documentIdParam);
          try {
            const doc = await getLegalDraft(docId);
            setSelectedDoc(doc);
            setSelectedDocId(docId);
          } catch {
            // Doc might be in the list already
            const found = finalized.find((d: any) => d.id === docId);
            if (found) {
              setSelectedDoc(found);
            }
          }
        }
      } catch (err: any) {
        console.error("Failed to load documents:", err);
        setError(err.message || "Failed to load documents");
      } finally {
        setLoading(false);
      }
    };
    fetchDocs();
  }, [documentIdParam, user, authLoading]);

  const handleDocSelect = async (docId: number) => {
    setSelectedDocId(docId);
    try {
      const doc = await getLegalDraft(docId);
      setSelectedDoc(doc);
    } catch {
      const found = documents.find((d) => d.id === docId);
      if (found) setSelectedDoc(found);
    }
  };

  const addSignatory = () => {
    setSignatories((prev) => [
      ...prev,
      { name: "", email: "", designation: "", signing_order: prev.length + 1 },
    ]);
  };

  const removeSignatory = (idx: number) => {
    if (signatories.length <= 2) return;
    setSignatories((prev) => {
      const updated = prev.filter((_, i) => i !== idx);
      return updated.map((s, i) => ({ ...s, signing_order: i + 1 }));
    });
  };

  const updateSignatory = (idx: number, field: keyof Signatory, value: string | number) => {
    setSignatories((prev) =>
      prev.map((s, i) => (i === idx ? { ...s, [field]: value } : s))
    );
  };

  const validateStep = (step: number): boolean => {
    if (step === 0) {
      if (!selectedDocId) {
        setError("Please select a document");
        return false;
      }
      return true;
    }
    if (step === 1) {
      for (const s of signatories) {
        if (!s.name.trim() || !s.email.trim()) {
          setError("All signatories must have a name and email");
          return false;
        }
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s.email)) {
          setError(`Invalid email: ${s.email}`);
          return false;
        }
      }
      return true;
    }
    return true;
  };

  const handleNext = () => {
    setError(null);
    if (!validateStep(currentStep)) return;
    setCurrentStep((prev) => Math.min(prev + 1, 3));
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleBack = () => {
    setError(null);
    setCurrentStep((prev) => Math.max(prev - 1, 0));
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleSubmit = async () => {
    setError(null);
    setSubmitting(true);
    try {
      const payload = {
        document_id: selectedDocId,
        signatories: signatories.map((s) => ({
          name: s.name.trim(),
          email: s.email.trim(),
          designation: s.designation.trim(),
          signing_order: signingMode === "parallel" ? 1 : s.signing_order,
        })),
        signing_mode: signingMode,
        custom_message: customMessage.trim() || undefined,
        expiry_days: expiryDays,
        reminder_interval_days: reminderDays,
      };

      const result = await createSignatureRequest(payload);
      // Auto-send emails
      if (result?.id) {
        await sendSigningEmails(result.id);
      }
      router.push("/dashboard/signatures");
    } catch (err: any) {
      setError(err.message || "Failed to create signature request");
    } finally {
      setSubmitting(false);
    }
  };

  const steps = [
    { title: "Select Document", short: "Document" },
    { title: "Add Signatories", short: "Signatories" },
    { title: "Settings", short: "Settings" },
    { title: "Review & Send", short: "Review" },
  ];

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 rounded w-64" style={{ background: "var(--color-bg-card)" }} />
          <div className="h-4 rounded w-96" style={{ background: "var(--color-bg-card)" }} />
          <div className="h-48 rounded-xl" style={{ background: "var(--color-bg-card)" }} />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => router.push("/dashboard/documents")}
          className="transition-colors"
          style={{ color: "var(--color-text-secondary)" }}
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
        </button>
        <div>
          <h1 className="text-xl font-bold" style={{ fontFamily: "var(--font-display)" }}>
            Send for Signing
          </h1>
          <p className="text-xs" style={{ color: "var(--color-text-secondary)" }}>Configure and send your document for e-signatures</p>
        </div>
      </div>

      {/* Step Progress */}
      <div className="flex items-center gap-2">
        {steps.map((step, idx) => (
          <div key={idx} className="flex items-center gap-2 flex-1">
            <div
              className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
              style={
                idx < currentStep
                  ? { background: "var(--color-success)", color: "var(--color-text-primary)" }
                  : idx === currentStep
                  ? { background: "var(--color-accent-purple)", color: "var(--color-text-primary)" }
                  : { background: "var(--color-border)", color: "var(--color-text-muted)" }
              }
            >
              {idx < currentStep ? (
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
              ) : (
                idx + 1
              )}
            </div>
            <span
              className="text-xs font-medium hidden sm:inline"
              style={{ color: idx === currentStep ? "var(--color-text-primary)" : "var(--color-text-muted)" }}
            >
              {step.short}
            </span>
            {idx < steps.length - 1 && (
              <div
                className="flex-1 h-px"
              style={{ background: idx < currentStep ? "var(--color-success)" : "var(--color-border)" }}
              />
            )}
          </div>
        ))}
      </div>

      {/* Error Banner */}
      {error && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-3 flex items-center gap-2">
          <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} style={{ color: "var(--color-error)" }}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          <p className="text-xs flex-1" style={{ color: "var(--color-error)" }}>{error}</p>
          <button onClick={() => setError(null)} style={{ color: "var(--color-error)" }}>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* Step Content */}
      <div className="rounded-xl border p-6" style={{ borderColor: "var(--color-border)", background: "var(--color-bg-card)" }}>
        {/* Step 1: Document Selection */}
        {currentStep === 0 && (
          <div className="space-y-4">
            <h2 className="text-lg font-bold" style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}>
              Select Document
            </h2>
            <p className="text-xs" style={{ color: "var(--color-text-secondary)" }}>
              Choose a finalized document to send for signing
            </p>

            {documents.length === 0 ? (
              <div className="text-center py-8">
                <svg className="w-10 h-10 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1} style={{ color: "var(--color-text-muted)" }}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12l-3-3m0 0l-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                </svg>
                <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>No finalized documents available</p>
                <p className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>Create and finalize a document first</p>
                <button
                  onClick={() => router.push("/dashboard/documents")}
                  className="mt-4 px-4 py-2 rounded-lg text-xs font-medium transition-colors"
                  style={{ background: "var(--color-accent-purple)", color: "var(--color-text-primary)" }}
                >
                  Go to Documents
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                {documents.map((doc) => (
                  <button
                    key={doc.id}
                    onClick={() => handleDocSelect(doc.id)}
                    className="w-full text-left rounded-lg border p-4 transition-all"
                    style={
                      selectedDocId === doc.id
                        ? { borderColor: "rgba(139, 92, 246, 0.5)", background: "rgba(139, 92, 246, 0.1)" }
                        : { borderColor: "var(--color-border)" }
                    }
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-sm font-medium" style={{ color: "var(--color-text-primary)" }}>
                          {doc.title || `Untitled ${doc.template_type?.replace(/_/g, " ") || "Document"}`}
                        </h4>
                        <p className="text-xs mt-0.5 capitalize" style={{ color: "var(--color-text-muted)" }}>
                          {doc.template_type?.replace(/_/g, " ")} &middot; {doc.created_at ? new Date(doc.created_at).toLocaleDateString() : ""}
                        </p>
                      </div>
                      {selectedDocId === doc.id && (
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} style={{ color: "var(--color-accent-purple-light)" }}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}

            {/* Document Preview */}
            {selectedDoc?.generated_html && (
              <div className="mt-4">
                <h4 className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: "var(--color-text-secondary)" }}>
                  Document Preview
                </h4>
                <div
                  className="rounded-lg border bg-white p-6 max-h-64 overflow-y-auto text-black text-sm prose prose-sm"
                  style={{ borderColor: "var(--color-border)" }}
                  dangerouslySetInnerHTML={{ __html: selectedDoc.generated_html }}
                />
              </div>
            )}
          </div>
        )}

        {/* Step 2: Add Signatories */}
        {currentStep === 1 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold" style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}>
                  Add Signatories
                </h2>
                <p className="text-xs mt-0.5" style={{ color: "var(--color-text-secondary)" }}>
                  Add the people who need to sign this document
                </p>
              </div>
              <button
                onClick={addSignatory}
                className="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors flex items-center gap-1.5"
                style={{ background: "var(--color-accent-purple)", color: "var(--color-text-primary)" }}
              >
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                </svg>
                Add Signatory
              </button>
            </div>

            {/* Signing Mode Toggle */}
            <div className="flex items-center gap-3 p-3 rounded-lg border" style={{ background: "var(--color-border-light)", borderColor: "var(--color-border)" }}>
              <span className="text-xs" style={{ color: "var(--color-text-secondary)" }}>Signing mode:</span>
              <button
                onClick={() => setSigningMode("parallel")}
                className="px-3 py-1 rounded-md text-xs font-medium transition-colors"
                style={
                  signingMode === "parallel"
                    ? { background: "var(--color-accent-purple)", color: "var(--color-text-primary)" }
                    : { color: "var(--color-text-secondary)" }
                }
              >
                All sign in parallel
              </button>
              <button
                onClick={() => setSigningMode("sequential")}
                className="px-3 py-1 rounded-md text-xs font-medium transition-colors"
                style={
                  signingMode === "sequential"
                    ? { background: "var(--color-accent-purple)", color: "var(--color-text-primary)" }
                    : { color: "var(--color-text-secondary)" }
                }
              >
                Sequential signing
              </button>
            </div>

            {/* Signatory Forms */}
            <div className="space-y-3">
              {signatories.map((s, idx) => (
                <div
                  key={idx}
                  className="rounded-lg border p-4 space-y-3"
                  style={{ borderColor: "var(--color-border)" }}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold" style={{ color: "var(--color-text-secondary)" }}>
                      Signatory {idx + 1}
                    </span>
                    {signatories.length > 2 && (
                      <button
                        onClick={() => removeSignatory(idx)}
                        className="transition-colors"
                        style={{ color: "var(--color-error)" }}
                      >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[10px] uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>
                        Name *
                      </label>
                      <input
                        type="text"
                        value={s.name}
                        onChange={(e) => updateSignatory(idx, "name", e.target.value)}
                        placeholder="Full name"
                        className="w-full px-3 py-2 rounded-lg text-sm transition-colors input-field"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>
                        Email *
                      </label>
                      <input
                        type="email"
                        value={s.email}
                        onChange={(e) => updateSignatory(idx, "email", e.target.value)}
                        placeholder="email@example.com"
                        className="w-full px-3 py-2 rounded-lg text-sm transition-colors input-field"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>
                        Designation
                      </label>
                      <input
                        type="text"
                        value={s.designation}
                        onChange={(e) => updateSignatory(idx, "designation", e.target.value)}
                        placeholder="e.g. Director, Partner"
                        className="w-full px-3 py-2 rounded-lg text-sm transition-colors input-field"
                      />
                    </div>
                    {signingMode === "sequential" && (
                      <div>
                        <label className="block text-[10px] uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>
                          Signing Order
                        </label>
                        <input
                          type="number"
                          value={s.signing_order}
                          onChange={(e) => updateSignatory(idx, "signing_order", parseInt(e.target.value) || 1)}
                          min={1}
                          className="w-full px-3 py-2 rounded-lg text-sm transition-colors input-field"
                        />
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Step 3: Settings */}
        {currentStep === 2 && (
          <div className="space-y-5">
            <h2 className="text-lg font-bold" style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}>
              Settings
            </h2>

            <div>
              <label className="block text-[10px] uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>
                Custom Message to Signatories (optional)
              </label>
              <textarea
                value={customMessage}
                onChange={(e) => setCustomMessage(e.target.value)}
                rows={4}
                placeholder="Add a personal message that will be included in the signing email..."
                className="w-full px-3 py-2 rounded-lg text-sm transition-colors resize-none input-field"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>
                  Expiry (days)
                </label>
                <input
                  type="number"
                  value={expiryDays}
                  onChange={(e) => setExpiryDays(parseInt(e.target.value) || 30)}
                  min={1}
                  max={365}
                  className="w-full px-3 py-2 rounded-lg text-sm transition-colors input-field"
                />
                <p className="text-[10px] mt-1" style={{ color: "var(--color-text-muted)" }}>
                  Signing request will expire after this many days
                </p>
              </div>
              <div>
                <label className="block text-[10px] uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>
                  Reminder Interval (days)
                </label>
                <input
                  type="number"
                  value={reminderDays}
                  onChange={(e) => setReminderDays(parseInt(e.target.value) || 3)}
                  min={1}
                  max={30}
                  className="w-full px-3 py-2 rounded-lg text-sm transition-colors input-field"
                />
                <p className="text-[10px] mt-1" style={{ color: "var(--color-text-muted)" }}>
                  Automatic reminders sent at this interval
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Review & Send */}
        {currentStep === 3 && (
          <div className="space-y-5">
            <h2 className="text-lg font-bold" style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}>
              Review & Send
            </h2>

            {/* Document Summary */}
            <div className="rounded-lg border p-4 space-y" style={{ borderColor: "var(--color-border)" }}>
              <h4 className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-secondary)" }}>
                Document
              </h4>
              <p className="text-sm font-medium" style={{ color: "var(--color-text-primary)" }}>
                {selectedDoc?.title || `Untitled ${selectedDoc?.template_type?.replace(/_/g, " ") || "Document"}`}
              </p>
              <p className="text-xs capitalize" style={{ color: "var(--color-text-muted)" }}>
                {selectedDoc?.template_type?.replace(/_/g, " ")}
              </p>
            </div>

            {/* Signatories Summary */}
            <div className="rounded-lg border p-4 space-y" style={{ borderColor: "var(--color-border)" }}>
              <h4 className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-secondary)" }}>
                Signatories ({signatories.length})
              </h4>
              <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                Signing mode: {signingMode === "parallel" ? "All sign in parallel" : "Sequential signing"}
              </p>
              <div className="space-y-2">
                {signatories.map((s, idx) => (
                  <div key={idx} className="flex items-center gap-3 text-xs">
                    <div className="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0" style={{ background: "rgba(139, 92, 246, 0.2)", color: "var(--color-accent-purple-light)" }}>
                      {signingMode === "sequential" ? s.signing_order : idx + 1}
                    </div>
                    <div>
                      <span style={{ color: "var(--color-text-primary)" }}>{s.name}</span>
                      <span className="ml-2" style={{ color: "var(--color-text-muted)" }}>{s.email}</span>
                      {s.designation && (
                        <span className="ml-2" style={{ color: "var(--color-text-muted)" }}>({s.designation})</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Settings Summary */}
            <div className="rounded-lg border p-4 space-y" style={{ borderColor: "var(--color-border)" }}>
              <h4 className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-secondary)" }}>
                Settings
              </h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span style={{ color: "var(--color-text-muted)" }}>Expiry:</span>{" "}
                  <span style={{ color: "var(--color-text-primary)" }}>{expiryDays} days</span>
                </div>
                <div>
                  <span style={{ color: "var(--color-text-muted)" }}>Reminders:</span>{" "}
                  <span style={{ color: "var(--color-text-primary)" }}>Every {reminderDays} days</span>
                </div>
              </div>
              {customMessage && (
                <div className="text-xs mt-2">
                  <span style={{ color: "var(--color-text-muted)" }}>Custom message:</span>
                  <p className="mt-1 italic" style={{ color: "var(--color-text-primary)" }}>&ldquo;{customMessage}&rdquo;</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between pt-2">
        <button
          onClick={handleBack}
          disabled={currentStep === 0}
          className="px-4 py-2 rounded-lg text-sm font-medium border transition-colors disabled:opacity-30 disabled:cursor-not-allowed flex items-center gap-1.5"
          style={{ color: "var(--color-text-secondary)", borderColor: "var(--color-border)" }}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
          Back
        </button>

        {currentStep < 3 ? (
          <button
            onClick={handleNext}
            className="px-6 py-2.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5"
            style={{ background: "var(--color-accent-purple)", color: "var(--color-text-primary)" }}
          >
            Next
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="px-6 py-2.5 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 flex items-center gap-2"
            style={{ background: "var(--color-accent-purple)", color: "var(--color-text-primary)" }}
          >
            {submitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Sending...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                </svg>
                Send for Signing
              </>
            )}
          </button>
        )}
      </div>
      <Footer />
    </div>
  );
}

export default function SendForSigningPage() {
  return (
    <Suspense
      fallback={
        <div className="p-8">
          <div className="animate-pulse space-y-6">
            <div className="h-8 rounded w-64" style={{ background: "var(--color-bg-card)" }} />
            <div className="h-4 rounded w-96" style={{ background: "var(--color-bg-card)" }} />
            <div className="h-48 rounded-xl" style={{ background: "var(--color-bg-card)" }} />
          </div>
        </div>
      }
    >
      <SendForSigningContent />
    </Suspense>
  );
}
