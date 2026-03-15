"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { useParams } from "next/navigation";
import { getSigningPageData, submitSignature, declineSignature } from "@/lib/api";
import Footer from "@/components/footer";

type SignatureMethod = "draw" | "type" | "upload";
type FontChoice = "Dancing Script" | "Great Vibes" | "Sacramento";

export default function PublicSigningPage() {
  const params = useParams();
  const accessToken = params.token as string;

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  // Signature state
  const [signatureMethod, setSignatureMethod] = useState<SignatureMethod>("draw");
  const [typedName, setTypedName] = useState("");
  const [selectedFont, setSelectedFont] = useState<FontChoice>("Dancing Script");
  const [uploadedSignature, setUploadedSignature] = useState<string | null>(null);
  const [agreedToTerms, setAgreedToTerms] = useState(false);

  // Decline state
  const [showDeclineModal, setShowDeclineModal] = useState(false);
  const [declineReason, setDeclineReason] = useState("");
  const [declining, setDeclining] = useState(false);

  // Canvas refs
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [hasDrawn, setHasDrawn] = useState(false);

  // Load signing page data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await getSigningPageData(accessToken);
        setData(result);
      } catch (err: any) {
        setError(err.message || "Failed to load signing page");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [accessToken]);

  // Canvas drawing functions
  const getCoordinates = useCallback((e: React.MouseEvent | React.TouchEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    if ("touches" in e) {
      return {
        x: (e.touches[0].clientX - rect.left) * scaleX,
        y: (e.touches[0].clientY - rect.top) * scaleY,
      };
    }
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY,
    };
  }, []);

  const startDrawing = useCallback((e: React.MouseEvent | React.TouchEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    setIsDrawing(true);
    setHasDrawn(true);
    const { x, y } = getCoordinates(e);
    ctx.beginPath();
    ctx.moveTo(x, y);
  }, [getCoordinates]);

  const draw = useCallback((e: React.MouseEvent | React.TouchEvent) => {
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const { x, y } = getCoordinates(e);
    ctx.lineWidth = 2;
    ctx.lineCap = "round";
    ctx.strokeStyle = "#000";
    ctx.lineTo(x, y);
    ctx.stroke();
  }, [isDrawing, getCoordinates]);

  const stopDrawing = useCallback(() => {
    setIsDrawing(false);
  }, []);

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    setHasDrawn(false);
  };

  const getSignatureData = (): string | null => {
    if (signatureMethod === "draw") {
      if (!hasDrawn) return null;
      return canvasRef.current?.toDataURL("image/png") || null;
    }
    if (signatureMethod === "type") {
      if (!typedName.trim()) return null;
      // Create a canvas with the typed signature
      const canvas = document.createElement("canvas");
      canvas.width = 400;
      canvas.height = 150;
      const ctx = canvas.getContext("2d");
      if (!ctx) return null;
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(0, 0, 400, 150);
      ctx.fillStyle = "#000000";
      ctx.font = `48px '${selectedFont}', cursive`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(typedName, 200, 75);
      return canvas.toDataURL("image/png");
    }
    if (signatureMethod === "upload") {
      return uploadedSignature;
    }
    return null;
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      setError("Please upload an image file (PNG, JPG)");
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      setUploadedSignature(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleSign = async () => {
    setError(null);
    const signatureData = getSignatureData();
    if (!signatureData) {
      setError("Please provide your signature");
      return;
    }
    if (!agreedToTerms) {
      setError("Please agree to the terms to proceed");
      return;
    }

    setSubmitting(true);
    try {
      await submitSignature(accessToken, {
        signature_data: signatureData,
        signature_method: signatureMethod,
        font_family: signatureMethod === "type" ? selectedFont : undefined,
      });
      setSuccess(true);
    } catch (err: any) {
      setError(err.message || "Failed to submit signature");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDecline = async () => {
    if (!declineReason.trim()) {
      setError("Please provide a reason for declining");
      return;
    }
    setDeclining(true);
    try {
      await declineSignature(accessToken, declineReason.trim());
      setData((prev: any) => ({ ...prev, signer_status: "declined" }));
      setShowDeclineModal(false);
    } catch (err: any) {
      setError(err.message || "Failed to decline");
    } finally {
      setDeclining(false);
    }
  };

  const fonts: FontChoice[] = ["Dancing Script", "Great Vibes", "Sacramento"];

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: "var(--color-bg-primary, #f9fafb)" }}>
        <div className="text-center">
          <div className="w-8 h-8 border-3 rounded-full animate-spin mx-auto mb-4" style={{ borderColor: "var(--color-border, #e5e7eb)", borderTopColor: "var(--color-accent-purple, #9333ea)" }} />
          <p className="text-sm" style={{ color: "var(--color-text-muted, #6b7280)" }}>Loading document...</p>
        </div>
      </div>
    );
  }

  // Error state (no data)
  if (error && !data) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6" style={{ background: "var(--color-bg-primary, #f9fafb)" }}>
        <div className="max-w-md w-full rounded-xl shadow-lg p-8 text-center" style={{ background: "var(--color-bg-card, #ffffff)" }}>
          <svg className="w-12 h-12 mx-auto mb-4" style={{ color: "var(--color-error, #f87171)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          <h2 className="text-lg font-semibold mb-2" style={{ color: "var(--color-text-primary, #111827)" }}>Unable to Load Document</h2>
          <p className="text-sm" style={{ color: "var(--color-text-muted, #6b7280)" }}>{error}</p>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const signerStatus = data.signer_status || data.status;
  const isPending = ["pending", "email_sent", "viewed"].includes(signerStatus);
  const isSigned = signerStatus === "signed";
  const isDeclined = signerStatus === "declined";
  const isExpiredOrCancelled = ["expired", "cancelled"].includes(data.request_status || data.status);

  // Success state after signing
  if (success) {
    return (
      <div className="min-h-screen" style={{ background: "var(--color-bg-primary, #f9fafb)" }}>
        <link
          href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Great+Vibes&family=Sacramento&display=swap"
          rel="stylesheet"
        />
        {/* Header */}
        <header className="px-6 py-4" style={{ background: "var(--color-bg-card, #ffffff)", borderBottom: "1px solid var(--color-border, #e5e7eb)" }}>
          <div className="max-w-4xl mx-auto flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: "var(--color-accent-purple, #9333ea)" }}>
              <svg className="w-5 h-5" style={{ color: "#ffffff" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
              </svg>
            </div>
            <div>
              <h1 className="text-sm font-bold" style={{ color: "var(--color-text-primary, #111827)" }}>Companies Made Simple India</h1>
              <p className="text-xs" style={{ color: "var(--color-text-muted, #6b7280)" }}>Document Signing</p>
            </div>
          </div>
        </header>

        <div className="max-w-lg mx-auto px-6 py-16 text-center">
          <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-6">
            <svg className="w-8 h-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold mb-2" style={{ color: "var(--color-text-primary, #111827)" }}>Document Signed Successfully</h2>
          <p className="text-sm mb-6" style={{ color: "var(--color-text-muted, #6b7280)" }}>
            Your signature has been recorded. You will receive a confirmation email with a copy of the signed document once all parties have signed.
          </p>
          <div className="rounded-lg p-4 text-xs" style={{ background: "var(--color-bg-secondary, #f3f4f6)", color: "var(--color-text-muted, #6b7280)" }}>
            You can safely close this window.
          </div>
        </div>

        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ background: "var(--color-bg-primary, #f9fafb)" }}>
      {/* Google Fonts for typed signatures */}
      <link
        href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Great+Vibes&family=Sacramento&display=swap"
        rel="stylesheet"
      />

      {/* Header */}
      <header className="px-6 py-4 sticky top-0 z-10" style={{ background: "var(--color-bg-card, #ffffff)", borderBottom: "1px solid var(--color-border, #e5e7eb)" }}>
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: "var(--color-accent-purple, #9333ea)" }}>
            <svg className="w-5 h-5" style={{ color: "#ffffff" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
          </div>
          <div>
            <h1 className="text-sm font-bold" style={{ color: "var(--color-text-primary, #111827)" }}>Companies Made Simple India</h1>
            <p className="text-xs" style={{ color: "var(--color-text-muted, #6b7280)" }}>Document Signing</p>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
        {/* Error Banner */}
        {error && (
          <div className="rounded-lg border p-3 flex items-center gap-2" style={{ borderColor: "rgba(239,68,68,0.3)", background: "rgba(239,68,68,0.05)" }}>
            <svg className="w-4 h-4 shrink-0" style={{ color: "var(--color-error, #ef4444)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
            <p className="text-xs flex-1" style={{ color: "#b91c1c" }}>{error}</p>
            <button onClick={() => setError(null)} style={{ color: "var(--color-error, #f87171)" }}>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {/* Expired / Cancelled state */}
        {isExpiredOrCancelled && (
          <div className="max-w-lg mx-auto text-center py-12">
            <svg className="w-12 h-12 mx-auto mb-4" style={{ color: "var(--color-text-secondary, #9ca3af)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-xl font-bold mb-2" style={{ color: "var(--color-text-primary, #111827)" }}>
              This signing request has {data.request_status === "cancelled" ? "been cancelled" : "expired"}
            </h2>
            <p className="text-sm" style={{ color: "var(--color-text-muted, #6b7280)" }}>
              Please contact the document sender for more information.
            </p>
          </div>
        )}

        {/* Already signed state */}
        {isSigned && !isExpiredOrCancelled && (
          <div className="max-w-lg mx-auto text-center py-12">
            <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
              </svg>
            </div>
            <h2 className="text-xl font-bold mb-2" style={{ color: "var(--color-text-primary, #111827)" }}>You have already signed this document</h2>
            {data.signed_at && (
              <p className="text-sm mb-4" style={{ color: "var(--color-text-muted, #6b7280)" }}>
                Signed on {new Date(data.signed_at).toLocaleString()}
              </p>
            )}
            <p className="text-xs" style={{ color: "var(--color-text-secondary, #9ca3af)" }}>
              {data.all_signed
                ? "All parties have signed. You will receive a copy of the completed document."
                : "Waiting for other parties to complete signing."}
            </p>
          </div>
        )}

        {/* Declined state */}
        {isDeclined && !isExpiredOrCancelled && (
          <div className="max-w-lg mx-auto text-center py-12">
            <svg className="w-12 h-12 mx-auto mb-4" style={{ color: "var(--color-error, #f87171)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <h2 className="text-xl font-bold mb-2" style={{ color: "var(--color-text-primary, #111827)" }}>You have declined to sign this document</h2>
            <p className="text-sm" style={{ color: "var(--color-text-muted, #6b7280)" }}>
              The document sender has been notified of your decision.
            </p>
          </div>
        )}

        {/* Pending: Main signing flow */}
        {isPending && !isExpiredOrCancelled && (
          <>
            {/* Document Title */}
            <div className="rounded-xl shadow-sm border p-5" style={{ background: "var(--color-bg-card, #ffffff)", borderColor: "var(--color-border, #e5e7eb)" }}>
              <h2 className="text-lg font-bold" style={{ color: "var(--color-text-primary, #111827)" }}>
                {data.document_title || "Document"}
              </h2>
              <p className="text-xs mt-1" style={{ color: "var(--color-text-muted, #6b7280)" }}>
                Please review the document below, then provide your signature at the bottom.
              </p>
            </div>

            {/* Document Viewer */}
            <div className="rounded-xl shadow-sm border overflow-hidden" style={{ background: "var(--color-bg-card, #ffffff)", borderColor: "var(--color-border, #e5e7eb)" }}>
              <div className="px-5 py-3 flex items-center gap-2" style={{ borderBottom: "1px solid var(--color-border, #f3f4f6)" }}>
                <svg className="w-4 h-4" style={{ color: "var(--color-text-secondary, #9ca3af)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                </svg>
                <span className="text-xs font-medium" style={{ color: "var(--color-text-muted, #6b7280)" }}>Document Preview</span>
              </div>
              <div
                className="p-8 max-h-[500px] overflow-y-auto prose prose-sm max-w-none"
                style={{ background: "var(--color-bg-card, #ffffff)", color: "var(--color-text-primary, #1f2937)" }}
                dangerouslySetInnerHTML={{ __html: data.document_html || "<p>Document content will appear here.</p>" }}
              />
            </div>

            {/* Signatory Info */}
            <div className="rounded-xl shadow-sm border p-5" style={{ background: "var(--color-bg-card, #ffffff)", borderColor: "var(--color-border, #e5e7eb)" }}>
              <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--color-text-primary, #111827)" }}>Your Details</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-xs block" style={{ color: "var(--color-text-muted, #6b7280)" }}>Name</span>
                  <span className="font-medium" style={{ color: "var(--color-text-primary, #111827)" }}>{data.signer_name || "--"}</span>
                </div>
                <div>
                  <span className="text-xs block" style={{ color: "var(--color-text-muted, #6b7280)" }}>Email</span>
                  <span style={{ color: "var(--color-text-primary, #111827)" }}>{data.signer_email || "--"}</span>
                </div>
                <div>
                  <span className="text-xs block" style={{ color: "var(--color-text-muted, #6b7280)" }}>Designation</span>
                  <span style={{ color: "var(--color-text-primary, #111827)" }}>{data.signer_designation || "--"}</span>
                </div>
              </div>
            </div>

            {/* All Parties */}
            {data.all_signatories && data.all_signatories.length > 1 && (
              <div className="rounded-xl shadow-sm border p-5" style={{ background: "var(--color-bg-card, #ffffff)", borderColor: "var(--color-border, #e5e7eb)" }}>
                <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--color-text-primary, #111827)" }}>All Signing Parties</h3>
                <div className="space-y-2">
                  {data.all_signatories.map((s: any, idx: number) => (
                    <div key={idx} className="flex items-center gap-3 text-sm">
                      {s.status === "signed" ? (
                        <svg className="w-4 h-4 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                        </svg>
                      ) : s.status === "declined" ? (
                        <svg className="w-4 h-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      ) : (
                        <svg className="w-4 h-4" style={{ color: "var(--color-text-secondary, #9ca3af)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      )}
                      <span style={{ color: "var(--color-text-primary, #111827)" }}>{s.name}</span>
                      {s.designation && (
                        <span className="text-xs" style={{ color: "var(--color-text-secondary, #9ca3af)" }}>({s.designation})</span>
                      )}
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full ${
                          s.status === "signed"
                            ? "bg-emerald-50 text-emerald-700"
                            : s.status === "declined"
                            ? "bg-red-50 text-red-700"
                            : "bg-gray-100 text-gray-500"
                        }`}
                      >
                        {s.status === "signed" ? "Signed" : s.status === "declined" ? "Declined" : "Pending"}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Signature Capture */}
            <div className="rounded-xl shadow-sm border p-5 space-y-5" style={{ background: "var(--color-bg-card, #ffffff)", borderColor: "var(--color-border, #e5e7eb)" }}>
              <h3 className="text-sm font-semibold" style={{ color: "var(--color-text-primary, #111827)" }}>Your Signature</h3>

              {/* Signature Method Tabs */}
              <div className="flex gap-1 rounded-lg p-1 w-fit" style={{ background: "var(--color-bg-secondary, #f3f4f6)" }}>
                {(["draw", "type", "upload"] as SignatureMethod[]).map((method) => (
                  <button
                    key={method}
                    onClick={() => setSignatureMethod(method)}
                    className="px-4 py-1.5 rounded-md text-xs font-medium transition-colors capitalize"
                    style={
                      signatureMethod === method
                        ? { background: "var(--color-bg-card, #ffffff)", color: "var(--color-text-primary, #111827)", boxShadow: "0 1px 2px rgba(0,0,0,0.05)" }
                        : { color: "var(--color-text-muted, #6b7280)" }
                    }
                  >
                    {method === "draw" ? "Draw" : method === "type" ? "Type" : "Upload"}
                  </button>
                ))}
              </div>

              {/* Draw Tab */}
              {signatureMethod === "draw" && (
                <div className="space-y-3">
                  <p className="text-xs" style={{ color: "var(--color-text-muted, #6b7280)" }}>Draw your signature using your mouse or finger</p>
                  <canvas
                    ref={canvasRef}
                    width={400}
                    height={150}
                    className="border-2 border-dashed rounded-lg cursor-crosshair touch-none w-full max-w-[400px]"
                    style={{ borderColor: "var(--color-border, #d1d5db)", background: "var(--color-bg-card, #ffffff)" }}
                    onMouseDown={startDrawing}
                    onMouseMove={draw}
                    onMouseUp={stopDrawing}
                    onMouseLeave={stopDrawing}
                    onTouchStart={startDrawing}
                    onTouchMove={draw}
                    onTouchEnd={stopDrawing}
                  />
                  <button
                    onClick={clearCanvas}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors"
                    style={{ borderColor: "var(--color-border, #d1d5db)", color: "var(--color-text-muted, #6b7280)" }}
                  >
                    Clear
                  </button>
                </div>
              )}

              {/* Type Tab */}
              {signatureMethod === "type" && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs mb-1" style={{ color: "var(--color-text-muted, #6b7280)" }}>Type your name</label>
                    <input
                      type="text"
                      value={typedName}
                      onChange={(e) => setTypedName(e.target.value)}
                      placeholder="Your full name"
                      className="w-full px-3 py-2 rounded-lg border text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 transition-colors"
                      style={{ borderColor: "var(--color-border, #d1d5db)", color: "var(--color-text-primary, #111827)" }}
                    />
                  </div>

                  {typedName && (
                    <div>
                      <label className="block text-xs mb-2" style={{ color: "var(--color-text-muted, #6b7280)" }}>Select a font style</label>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        {fonts.map((font) => (
                          <button
                            key={font}
                            onClick={() => setSelectedFont(font)}
                            className="rounded-lg border-2 p-4 text-center transition-all"
                            style={{
                              borderColor: selectedFont === font ? "var(--color-accent-purple, #9333ea)" : "var(--color-border, #e5e7eb)",
                              background: selectedFont === font ? "rgba(147,51,234,0.05)" : "transparent",
                            }}
                          >
                            <span
                              className="text-2xl block mb-1"
                              style={{ fontFamily: `'${font}', cursive`, color: "var(--color-text-primary, #111827)" }}
                            >
                              {typedName}
                            </span>
                            <span className="text-[10px]" style={{ color: "var(--color-text-secondary, #9ca3af)" }}>{font}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Upload Tab */}
              {signatureMethod === "upload" && (
                <div className="space-y-3">
                  <p className="text-xs" style={{ color: "var(--color-text-muted, #6b7280)" }}>Upload an image of your signature (PNG, JPG)</p>

                  {!uploadedSignature ? (
                    <label className="flex flex-col items-center justify-center w-full max-w-[400px] h-[150px] border-2 border-dashed rounded-lg cursor-pointer transition-colors" style={{ borderColor: "var(--color-border, #d1d5db)" }}>
                      <svg className="w-8 h-8 mb-2" style={{ color: "var(--color-text-secondary, #9ca3af)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                      </svg>
                      <span className="text-xs" style={{ color: "var(--color-text-muted, #6b7280)" }}>Click to upload signature image</span>
                      <input
                        type="file"
                        accept="image/png,image/jpeg,image/jpg"
                        onChange={handleFileUpload}
                        className="hidden"
                      />
                    </label>
                  ) : (
                    <div className="space-y-2">
                      <div className="border-2 rounded-lg p-4 max-w-[400px]" style={{ borderColor: "var(--color-border, #e5e7eb)", background: "var(--color-bg-card, #ffffff)" }}>
                        <img
                          src={uploadedSignature}
                          alt="Uploaded signature"
                          className="max-h-[120px] mx-auto"
                        />
                      </div>
                      <button
                        onClick={() => setUploadedSignature(null)}
                        className="px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors"
                        style={{ borderColor: "var(--color-border, #d1d5db)", color: "var(--color-text-muted, #6b7280)" }}
                      >
                        Remove & Upload New
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Terms Checkbox */}
              <label className="flex items-start gap-3 cursor-pointer pt-2">
                <input
                  type="checkbox"
                  checked={agreedToTerms}
                  onChange={(e) => setAgreedToTerms(e.target.checked)}
                  className="mt-0.5 w-4 h-4 rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                />
                <span className="text-xs leading-relaxed" style={{ color: "var(--color-text-muted, #4b5563)" }}>
                  I agree that this electronic signature is legally binding under the Information Technology Act, 2000 and constitutes my consent to sign this document.
                </span>
              </label>

              {/* Sign Button */}
              <button
                onClick={handleSign}
                disabled={submitting || !agreedToTerms}
                className="w-full sm:w-auto px-8 py-3 rounded-lg text-sm font-semibold text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                style={{ background: submitting ? "rgba(16,185,129,0.5)" : "var(--color-success, #059669)" }}
              >
                {submitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Signing...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                    Sign Document
                  </>
                )}
              </button>
            </div>

            {/* Decline Button */}
            <div className="text-center pt-2">
              <button
                onClick={() => setShowDeclineModal(true)}
                className="text-xs font-medium transition-colors"
                style={{ color: "var(--color-error, #ef4444)" }}
              >
                Decline to Sign
              </button>
            </div>

            {/* Decline Modal */}
            {showDeclineModal && (
              <div className="fixed inset-0 flex items-center justify-center z-50 p-6" style={{ background: "var(--color-overlay, rgba(0,0,0,0.5))" }}>
                <div className="rounded-xl shadow-xl max-w-md w-full p-6 space-y-4" style={{ background: "var(--color-bg-card, #ffffff)" }}>
                  <h3 className="text-lg font-semibold" style={{ color: "var(--color-text-primary, #111827)" }}>Decline to Sign</h3>
                  <p className="text-sm" style={{ color: "var(--color-text-muted, #6b7280)" }}>
                    Please provide a reason for declining. The document sender will be notified.
                  </p>
                  <textarea
                    value={declineReason}
                    onChange={(e) => setDeclineReason(e.target.value)}
                    rows={3}
                    placeholder="Reason for declining..."
                    className="w-full px-3 py-2 rounded-lg border text-sm focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 resize-none"
                    style={{ borderColor: "var(--color-border, #d1d5db)", color: "var(--color-text-primary, #111827)" }}
                  />
                  <div className="flex items-center justify-end gap-3">
                    <button
                      onClick={() => {
                        setShowDeclineModal(false);
                        setDeclineReason("");
                      }}
                      className="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                      style={{ color: "var(--color-text-muted, #6b7280)" }}
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleDecline}
                      disabled={declining || !declineReason.trim()}
                      className="px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors disabled:opacity-50 flex items-center gap-2"
                      style={{ background: "var(--color-error, #dc2626)" }}
                    >
                      {declining ? (
                        <>
                          <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          Declining...
                        </>
                      ) : (
                        "Decline"
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Footer */}
      <footer className="mt-12 py-6 px-6" style={{ borderTop: "1px solid var(--color-border, #e5e7eb)" }}>
        <div className="max-w-4xl mx-auto text-center text-xs" style={{ color: "var(--color-text-secondary, #9ca3af)" }}>
          <p>Powered by Companies Made Simple India</p>
          <p className="mt-1">E-signatures are legally valid under the Information Technology Act, 2000</p>
        </div>
      </footer>
    </div>
  );
}
