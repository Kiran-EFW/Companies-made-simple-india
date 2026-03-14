"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  getLegalDrafts,
  getLegalDraft,
  createSignatureRequest,
  sendSigningEmails,
} from "@/lib/api";

interface Signatory {
  name: string;
  email: string;
  designation: string;
  signing_order: number;
}

function SendForSigningContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
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

  // Fetch finalized documents
  useEffect(() => {
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
  }, [documentIdParam]);

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
      router.push("/documents/signatures");
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
          <div className="h-8 bg-gray-800 rounded w-64" />
          <div className="h-4 bg-gray-800 rounded w-96" />
          <div className="h-48 bg-gray-800 rounded-xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-3xl mx-auto space-y-6">
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
            Send for Signing
          </h1>
          <p className="text-xs text-gray-400">Configure and send your document for e-signatures</p>
        </div>
      </div>

      {/* Step Progress */}
      <div className="flex items-center gap-2">
        {steps.map((step, idx) => (
          <div key={idx} className="flex items-center gap-2 flex-1">
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                idx < currentStep
                  ? "bg-emerald-600 text-white"
                  : idx === currentStep
                  ? "bg-purple-600 text-white"
                  : "bg-gray-700 text-gray-500"
              }`}
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
              className={`text-xs font-medium hidden sm:inline ${
                idx === currentStep ? "text-white" : "text-gray-500"
              }`}
            >
              {step.short}
            </span>
            {idx < steps.length - 1 && (
              <div
                className={`flex-1 h-px ${
                  idx < currentStep ? "bg-emerald-600" : "bg-gray-700"
                }`}
              />
            )}
          </div>
        ))}
      </div>

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

      {/* Step Content */}
      <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-6">
        {/* Step 1: Document Selection */}
        {currentStep === 0 && (
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-white" style={{ fontFamily: "var(--font-display)" }}>
              Select Document
            </h2>
            <p className="text-xs text-gray-400">
              Choose a finalized document to send for signing
            </p>

            {documents.length === 0 ? (
              <div className="text-center py-8">
                <svg className="w-10 h-10 text-gray-600 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12l-3-3m0 0l-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                </svg>
                <p className="text-sm text-gray-400">No finalized documents available</p>
                <p className="text-xs text-gray-500 mt-1">Create and finalize a document first</p>
                <button
                  onClick={() => router.push("/documents")}
                  className="mt-4 px-4 py-2 rounded-lg text-xs font-medium bg-purple-600 hover:bg-purple-500 text-white transition-colors"
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
                    className={`w-full text-left rounded-lg border p-4 transition-all ${
                      selectedDocId === doc.id
                        ? "border-purple-500/50 bg-purple-500/10"
                        : "border-gray-700 hover:border-gray-600 hover:bg-gray-700/30"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-sm font-medium text-white">
                          {doc.title || `Untitled ${doc.template_type?.replace(/_/g, " ") || "Document"}`}
                        </h4>
                        <p className="text-xs text-gray-500 mt-0.5 capitalize">
                          {doc.template_type?.replace(/_/g, " ")} &middot; {doc.created_at ? new Date(doc.created_at).toLocaleDateString() : ""}
                        </p>
                      </div>
                      {selectedDocId === doc.id && (
                        <svg className="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
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
                <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                  Document Preview
                </h4>
                <div
                  className="rounded-lg border border-gray-700 bg-white p-6 max-h-64 overflow-y-auto text-black text-sm prose prose-sm"
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
                <h2 className="text-lg font-bold text-white" style={{ fontFamily: "var(--font-display)" }}>
                  Add Signatories
                </h2>
                <p className="text-xs text-gray-400 mt-0.5">
                  Add the people who need to sign this document
                </p>
              </div>
              <button
                onClick={addSignatory}
                className="px-3 py-1.5 rounded-lg text-xs font-medium bg-purple-600 hover:bg-purple-500 text-white transition-colors flex items-center gap-1.5"
              >
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                </svg>
                Add Signatory
              </button>
            </div>

            {/* Signing Mode Toggle */}
            <div className="flex items-center gap-3 p-3 rounded-lg bg-gray-700/30 border border-gray-700">
              <span className="text-xs text-gray-400">Signing mode:</span>
              <button
                onClick={() => setSigningMode("parallel")}
                className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                  signingMode === "parallel"
                    ? "bg-purple-600 text-white"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                All sign in parallel
              </button>
              <button
                onClick={() => setSigningMode("sequential")}
                className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                  signingMode === "sequential"
                    ? "bg-purple-600 text-white"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                Sequential signing
              </button>
            </div>

            {/* Signatory Forms */}
            <div className="space-y-3">
              {signatories.map((s, idx) => (
                <div
                  key={idx}
                  className="rounded-lg border border-gray-700 p-4 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-gray-400">
                      Signatory {idx + 1}
                    </span>
                    {signatories.length > 2 && (
                      <button
                        onClick={() => removeSignatory(idx)}
                        className="text-red-400 hover:text-red-300 transition-colors"
                      >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[10px] text-gray-500 uppercase tracking-wider mb-1">
                        Name *
                      </label>
                      <input
                        type="text"
                        value={s.name}
                        onChange={(e) => updateSignatory(idx, "name", e.target.value)}
                        placeholder="Full name"
                        className="w-full px-3 py-2 rounded-lg bg-gray-900/50 border border-gray-700 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-purple-500/50 transition-colors"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] text-gray-500 uppercase tracking-wider mb-1">
                        Email *
                      </label>
                      <input
                        type="email"
                        value={s.email}
                        onChange={(e) => updateSignatory(idx, "email", e.target.value)}
                        placeholder="email@example.com"
                        className="w-full px-3 py-2 rounded-lg bg-gray-900/50 border border-gray-700 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-purple-500/50 transition-colors"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] text-gray-500 uppercase tracking-wider mb-1">
                        Designation
                      </label>
                      <input
                        type="text"
                        value={s.designation}
                        onChange={(e) => updateSignatory(idx, "designation", e.target.value)}
                        placeholder="e.g. Director, Partner"
                        className="w-full px-3 py-2 rounded-lg bg-gray-900/50 border border-gray-700 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-purple-500/50 transition-colors"
                      />
                    </div>
                    {signingMode === "sequential" && (
                      <div>
                        <label className="block text-[10px] text-gray-500 uppercase tracking-wider mb-1">
                          Signing Order
                        </label>
                        <input
                          type="number"
                          value={s.signing_order}
                          onChange={(e) => updateSignatory(idx, "signing_order", parseInt(e.target.value) || 1)}
                          min={1}
                          className="w-full px-3 py-2 rounded-lg bg-gray-900/50 border border-gray-700 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-purple-500/50 transition-colors"
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
            <h2 className="text-lg font-bold text-white" style={{ fontFamily: "var(--font-display)" }}>
              Settings
            </h2>

            <div>
              <label className="block text-[10px] text-gray-500 uppercase tracking-wider mb-1">
                Custom Message to Signatories (optional)
              </label>
              <textarea
                value={customMessage}
                onChange={(e) => setCustomMessage(e.target.value)}
                rows={4}
                placeholder="Add a personal message that will be included in the signing email..."
                className="w-full px-3 py-2 rounded-lg bg-gray-900/50 border border-gray-700 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-purple-500/50 transition-colors resize-none"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] text-gray-500 uppercase tracking-wider mb-1">
                  Expiry (days)
                </label>
                <input
                  type="number"
                  value={expiryDays}
                  onChange={(e) => setExpiryDays(parseInt(e.target.value) || 30)}
                  min={1}
                  max={365}
                  className="w-full px-3 py-2 rounded-lg bg-gray-900/50 border border-gray-700 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-purple-500/50 transition-colors"
                />
                <p className="text-[10px] text-gray-600 mt-1">
                  Signing request will expire after this many days
                </p>
              </div>
              <div>
                <label className="block text-[10px] text-gray-500 uppercase tracking-wider mb-1">
                  Reminder Interval (days)
                </label>
                <input
                  type="number"
                  value={reminderDays}
                  onChange={(e) => setReminderDays(parseInt(e.target.value) || 3)}
                  min={1}
                  max={30}
                  className="w-full px-3 py-2 rounded-lg bg-gray-900/50 border border-gray-700 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-purple-500/50 transition-colors"
                />
                <p className="text-[10px] text-gray-600 mt-1">
                  Automatic reminders sent at this interval
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Review & Send */}
        {currentStep === 3 && (
          <div className="space-y-5">
            <h2 className="text-lg font-bold text-white" style={{ fontFamily: "var(--font-display)" }}>
              Review & Send
            </h2>

            {/* Document Summary */}
            <div className="rounded-lg border border-gray-700 p-4 space-y-1">
              <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Document
              </h4>
              <p className="text-sm font-medium text-white">
                {selectedDoc?.title || `Untitled ${selectedDoc?.template_type?.replace(/_/g, " ") || "Document"}`}
              </p>
              <p className="text-xs text-gray-500 capitalize">
                {selectedDoc?.template_type?.replace(/_/g, " ")}
              </p>
            </div>

            {/* Signatories Summary */}
            <div className="rounded-lg border border-gray-700 p-4 space-y-3">
              <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Signatories ({signatories.length})
              </h4>
              <p className="text-[10px] text-gray-500">
                Signing mode: {signingMode === "parallel" ? "All sign in parallel" : "Sequential signing"}
              </p>
              <div className="space-y-2">
                {signatories.map((s, idx) => (
                  <div key={idx} className="flex items-center gap-3 text-xs">
                    <div className="w-6 h-6 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center text-[10px] font-bold shrink-0">
                      {signingMode === "sequential" ? s.signing_order : idx + 1}
                    </div>
                    <div>
                      <span className="text-white">{s.name}</span>
                      <span className="text-gray-500 ml-2">{s.email}</span>
                      {s.designation && (
                        <span className="text-gray-600 ml-2">({s.designation})</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Settings Summary */}
            <div className="rounded-lg border border-gray-700 p-4 space-y-2">
              <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Settings
              </h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-gray-500">Expiry:</span>{" "}
                  <span className="text-white">{expiryDays} days</span>
                </div>
                <div>
                  <span className="text-gray-500">Reminders:</span>{" "}
                  <span className="text-white">Every {reminderDays} days</span>
                </div>
              </div>
              {customMessage && (
                <div className="text-xs mt-2">
                  <span className="text-gray-500">Custom message:</span>
                  <p className="text-gray-300 mt-1 italic">&ldquo;{customMessage}&rdquo;</p>
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
          className="px-4 py-2 rounded-lg text-sm font-medium text-gray-400 hover:text-white border border-gray-700 hover:border-gray-600 transition-colors disabled:opacity-30 disabled:cursor-not-allowed flex items-center gap-1.5"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
          Back
        </button>

        {currentStep < 3 ? (
          <button
            onClick={handleNext}
            className="px-6 py-2.5 rounded-lg text-sm font-medium bg-purple-600 hover:bg-purple-500 text-white transition-colors flex items-center gap-1.5"
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
            className="px-6 py-2.5 rounded-lg text-sm font-medium bg-purple-600 hover:bg-purple-500 text-white transition-colors disabled:opacity-50 flex items-center gap-2"
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
    </div>
  );
}

export default function SendForSigningPage() {
  return (
    <Suspense
      fallback={
        <div className="p-8">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-800 rounded w-64" />
            <div className="h-4 bg-gray-800 rounded w-96" />
            <div className="h-48 bg-gray-800 rounded-xl" />
          </div>
        </div>
      }
    >
      <SendForSigningContent />
    </Suspense>
  );
}
