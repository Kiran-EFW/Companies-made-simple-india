"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { useParams } from "next/navigation";
import { getSigningPageData, submitSignature, declineSignature } from "@/lib/api";

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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-3 border-purple-200 border-t-purple-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm text-gray-500">Loading document...</p>
        </div>
      </div>
    );
  }

  // Error state (no data)
  if (error && !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
          <svg className="w-12 h-12 text-red-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          <h2 className="text-lg font-semibold text-gray-900 mb-2">Unable to Load Document</h2>
          <p className="text-sm text-gray-500">{error}</p>
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
      <div className="min-h-screen bg-gray-50">
        <link
          href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Great+Vibes&family=Sacramento&display=swap"
          rel="stylesheet"
        />
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="max-w-4xl mx-auto flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
              </svg>
            </div>
            <div>
              <h1 className="text-sm font-bold text-gray-900">Companies Made Simple India</h1>
              <p className="text-xs text-gray-500">Document Signing</p>
            </div>
          </div>
        </header>

        <div className="max-w-lg mx-auto px-6 py-16 text-center">
          <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-6">
            <svg className="w-8 h-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Document Signed Successfully</h2>
          <p className="text-sm text-gray-500 mb-6">
            Your signature has been recorded. You will receive a confirmation email with a copy of the signed document once all parties have signed.
          </p>
          <div className="bg-gray-100 rounded-lg p-4 text-xs text-gray-500">
            You can safely close this window.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Google Fonts for typed signatures */}
      <link
        href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Great+Vibes&family=Sacramento&display=swap"
        rel="stylesheet"
      />

      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
          </div>
          <div>
            <h1 className="text-sm font-bold text-gray-900">Companies Made Simple India</h1>
            <p className="text-xs text-gray-500">Document Signing</p>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
        {/* Error Banner */}
        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-3 flex items-center gap-2">
            <svg className="w-4 h-4 text-red-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
            <p className="text-xs text-red-700 flex-1">{error}</p>
            <button onClick={() => setError(null)} className="text-red-400 hover:text-red-600">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {/* Expired / Cancelled state */}
        {isExpiredOrCancelled && (
          <div className="max-w-lg mx-auto text-center py-12">
            <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-xl font-bold text-gray-900 mb-2">
              This signing request has {data.request_status === "cancelled" ? "been cancelled" : "expired"}
            </h2>
            <p className="text-sm text-gray-500">
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
            <h2 className="text-xl font-bold text-gray-900 mb-2">You have already signed this document</h2>
            {data.signed_at && (
              <p className="text-sm text-gray-500 mb-4">
                Signed on {new Date(data.signed_at).toLocaleString()}
              </p>
            )}
            <p className="text-xs text-gray-400">
              {data.all_signed
                ? "All parties have signed. You will receive a copy of the completed document."
                : "Waiting for other parties to complete signing."}
            </p>
          </div>
        )}

        {/* Declined state */}
        {isDeclined && !isExpiredOrCancelled && (
          <div className="max-w-lg mx-auto text-center py-12">
            <svg className="w-12 h-12 text-red-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <h2 className="text-xl font-bold text-gray-900 mb-2">You have declined to sign this document</h2>
            <p className="text-sm text-gray-500">
              The document sender has been notified of your decision.
            </p>
          </div>
        )}

        {/* Pending: Main signing flow */}
        {isPending && !isExpiredOrCancelled && (
          <>
            {/* Document Title */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <h2 className="text-lg font-bold text-gray-900">
                {data.document_title || "Document"}
              </h2>
              <p className="text-xs text-gray-500 mt-1">
                Please review the document below, then provide your signature at the bottom.
              </p>
            </div>

            {/* Document Viewer */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="px-5 py-3 border-b border-gray-100 flex items-center gap-2">
                <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                </svg>
                <span className="text-xs font-medium text-gray-600">Document Preview</span>
              </div>
              <div
                className="p-8 max-h-[500px] overflow-y-auto bg-white prose prose-sm max-w-none text-gray-800"
                dangerouslySetInnerHTML={{ __html: data.document_html || "<p>Document content will appear here.</p>" }}
              />
            </div>

            {/* Signatory Info */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Your Details</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-xs text-gray-500 block">Name</span>
                  <span className="text-gray-900 font-medium">{data.signer_name || "--"}</span>
                </div>
                <div>
                  <span className="text-xs text-gray-500 block">Email</span>
                  <span className="text-gray-900">{data.signer_email || "--"}</span>
                </div>
                <div>
                  <span className="text-xs text-gray-500 block">Designation</span>
                  <span className="text-gray-900">{data.signer_designation || "--"}</span>
                </div>
              </div>
            </div>

            {/* All Parties */}
            {data.all_signatories && data.all_signatories.length > 1 && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
                <h3 className="text-sm font-semibold text-gray-900 mb-3">All Signing Parties</h3>
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
                        <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      )}
                      <span className="text-gray-900">{s.name}</span>
                      {s.designation && (
                        <span className="text-gray-400 text-xs">({s.designation})</span>
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
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 space-y-5">
              <h3 className="text-sm font-semibold text-gray-900">Your Signature</h3>

              {/* Signature Method Tabs */}
              <div className="flex gap-1 bg-gray-100 rounded-lg p-1 w-fit">
                {(["draw", "type", "upload"] as SignatureMethod[]).map((method) => (
                  <button
                    key={method}
                    onClick={() => setSignatureMethod(method)}
                    className={`px-4 py-1.5 rounded-md text-xs font-medium transition-colors capitalize ${
                      signatureMethod === method
                        ? "bg-white text-gray-900 shadow-sm"
                        : "text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    {method === "draw" ? "Draw" : method === "type" ? "Type" : "Upload"}
                  </button>
                ))}
              </div>

              {/* Draw Tab */}
              {signatureMethod === "draw" && (
                <div className="space-y-3">
                  <p className="text-xs text-gray-500">Draw your signature using your mouse or finger</p>
                  <canvas
                    ref={canvasRef}
                    width={400}
                    height={150}
                    className="border-2 border-dashed border-gray-300 rounded-lg cursor-crosshair bg-white touch-none w-full max-w-[400px]"
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
                    className="px-3 py-1.5 rounded-lg text-xs font-medium border border-gray-300 text-gray-600 hover:bg-gray-50 transition-colors"
                  >
                    Clear
                  </button>
                </div>
              )}

              {/* Type Tab */}
              {signatureMethod === "type" && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Type your name</label>
                    <input
                      type="text"
                      value={typedName}
                      onChange={(e) => setTypedName(e.target.value)}
                      placeholder="Your full name"
                      className="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 transition-colors"
                    />
                  </div>

                  {typedName && (
                    <div>
                      <label className="block text-xs text-gray-500 mb-2">Select a font style</label>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        {fonts.map((font) => (
                          <button
                            key={font}
                            onClick={() => setSelectedFont(font)}
                            className={`rounded-lg border-2 p-4 text-center transition-all ${
                              selectedFont === font
                                ? "border-purple-500 bg-purple-50"
                                : "border-gray-200 hover:border-gray-300"
                            }`}
                          >
                            <span
                              className="text-2xl text-gray-900 block mb-1"
                              style={{ fontFamily: `'${font}', cursive` }}
                            >
                              {typedName}
                            </span>
                            <span className="text-[10px] text-gray-400">{font}</span>
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
                  <p className="text-xs text-gray-500">Upload an image of your signature (PNG, JPG)</p>

                  {!uploadedSignature ? (
                    <label className="flex flex-col items-center justify-center w-full max-w-[400px] h-[150px] border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                      <svg className="w-8 h-8 text-gray-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                      </svg>
                      <span className="text-xs text-gray-500">Click to upload signature image</span>
                      <input
                        type="file"
                        accept="image/png,image/jpeg,image/jpg"
                        onChange={handleFileUpload}
                        className="hidden"
                      />
                    </label>
                  ) : (
                    <div className="space-y-2">
                      <div className="border-2 border-gray-200 rounded-lg p-4 bg-white max-w-[400px]">
                        <img
                          src={uploadedSignature}
                          alt="Uploaded signature"
                          className="max-h-[120px] mx-auto"
                        />
                      </div>
                      <button
                        onClick={() => setUploadedSignature(null)}
                        className="px-3 py-1.5 rounded-lg text-xs font-medium border border-gray-300 text-gray-600 hover:bg-gray-50 transition-colors"
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
                <span className="text-xs text-gray-600 leading-relaxed">
                  I agree that this electronic signature is legally binding under the Information Technology Act, 2000 and constitutes my consent to sign this document.
                </span>
              </label>

              {/* Sign Button */}
              <button
                onClick={handleSign}
                disabled={submitting || !agreedToTerms}
                className="w-full sm:w-auto px-8 py-3 rounded-lg text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
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
                className="text-xs text-red-500 hover:text-red-600 font-medium transition-colors"
              >
                Decline to Sign
              </button>
            </div>

            {/* Decline Modal */}
            {showDeclineModal && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-6">
                <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900">Decline to Sign</h3>
                  <p className="text-sm text-gray-500">
                    Please provide a reason for declining. The document sender will be notified.
                  </p>
                  <textarea
                    value={declineReason}
                    onChange={(e) => setDeclineReason(e.target.value)}
                    rows={3}
                    placeholder="Reason for declining..."
                    className="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 resize-none"
                  />
                  <div className="flex items-center justify-end gap-3">
                    <button
                      onClick={() => {
                        setShowDeclineModal(false);
                        setDeclineReason("");
                      }}
                      className="px-4 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleDecline}
                      disabled={declining || !declineReason.trim()}
                      className="px-4 py-2 rounded-lg text-sm font-medium bg-red-600 hover:bg-red-500 text-white transition-colors disabled:opacity-50 flex items-center gap-2"
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
      <footer className="border-t border-gray-200 mt-12 py-6 px-6">
        <div className="max-w-4xl mx-auto text-center text-xs text-gray-400">
          <p>Powered by Companies Made Simple India</p>
          <p className="mt-1">E-signatures are legally valid under the Information Technology Act, 2000</p>
        </div>
      </footer>
    </div>
  );
}
