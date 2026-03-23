"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { getLearningPath, getTemplateContext } from "@/lib/api";
import Header from "@/components/header";
import Footer from "@/components/footer";

// Priority badge color mapping
const PRIORITY_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  critical: {
    bg: "rgba(244, 63, 94, 0.15)",
    border: "rgba(244, 63, 94, 0.4)",
    text: "rgb(244, 63, 94)",
  },
  mandatory: {
    bg: "rgba(244, 63, 94, 0.15)",
    border: "rgba(244, 63, 94, 0.4)",
    text: "rgb(244, 63, 94)",
  },
  recommended: {
    bg: "rgba(139, 92, 246, 0.15)",
    border: "rgba(139, 92, 246, 0.4)",
    text: "rgb(139, 92, 246)",
  },
  "as-needed": {
    bg: "rgba(245, 158, 11, 0.15)",
    border: "rgba(245, 158, 11, 0.4)",
    text: "rgb(245, 158, 11)",
  },
  optional: {
    bg: "rgba(245, 158, 11, 0.15)",
    border: "rgba(245, 158, 11, 0.4)",
    text: "rgb(245, 158, 11)",
  },
};

function getPriorityStyle(priority: string) {
  const key = priority?.toLowerCase() || "optional";
  return PRIORITY_COLORS[key] || PRIORITY_COLORS.optional;
}

// Category badge colors for tips
const CATEGORY_BADGE_COLORS: Record<string, { bg: string; text: string }> = {
  legal: { bg: "rgba(139, 92, 246, 0.15)", text: "rgb(139, 92, 246)" },
  compliance: { bg: "rgba(16, 185, 129, 0.15)", text: "rgb(16, 185, 129)" },
  finance: { bg: "rgba(59, 130, 246, 0.15)", text: "rgb(59, 130, 246)" },
  fundraising: { bg: "rgba(244, 63, 94, 0.15)", text: "rgb(244, 63, 94)" },
  operations: { bg: "rgba(245, 158, 11, 0.15)", text: "rgb(245, 158, 11)" },
  tax: { bg: "rgba(236, 72, 153, 0.15)", text: "rgb(236, 72, 153)" },
  governance: { bg: "rgba(14, 165, 233, 0.15)", text: "rgb(14, 165, 233)" },
};

function getCategoryStyle(category: string) {
  const key = category?.toLowerCase() || "legal";
  return CATEGORY_BADGE_COLORS[key] || CATEGORY_BADGE_COLORS.legal;
}

export default function LearnPage() {
  const [learningPath, setLearningPath] = useState<any>(null);
  const [expandedStage, setExpandedStage] = useState<string | null>(null);
  const [templateContext, setTemplateContext] = useState<any>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [contextLoading, setContextLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getLearningPath();
        setLearningPath(data);
      } catch (err: any) {
        console.error("Failed to load learning path:", err);
        setError(err.message || "Failed to load learning path");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleLearnMore = async (templateType: string) => {
    if (selectedTemplate === templateType) {
      // Toggle off
      setSelectedTemplate(null);
      setTemplateContext(null);
      return;
    }
    setSelectedTemplate(templateType);
    setContextLoading(true);
    try {
      const ctx = await getTemplateContext(templateType);
      setTemplateContext(ctx);
    } catch (err) {
      console.error("Failed to load template context:", err);
      setTemplateContext(null);
    } finally {
      setContextLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center glow-bg">
        <div className="animate-pulse-glow w-16 h-16 rounded-full bg-purple-500/20 flex items-center justify-center">
          <img src="/logo-icon.png" alt="Anvils" className="w-7 h-7 object-contain" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen glow-bg">
        <Header />
        <div className="max-w-4xl mx-auto px-6 py-16 text-center">
          <div className="glass-card p-12">
            <div className="text-5xl mb-4">&#128218;</div>
            <h2 className="text-2xl font-bold mb-2">Unable to Load Learning Path</h2>
            <p className="mb-6" style={{ color: "var(--color-text-secondary)" }}>{error}</p>
            <button onClick={() => window.location.reload()} className="btn-primary">
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  const stages = learningPath?.stages || [];
  const tips = learningPath?.tips || [];

  return (
    <div className="min-h-screen glow-bg">
      <Header />

      <div className="max-w-5xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-16 animate-fade-in-up">
          <h1
            className="text-4xl md:text-5xl font-bold mb-4 gradient-text"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Founder&apos;s Legal Journey
          </h1>
          <p className="text-lg max-w-2xl mx-auto" style={{ color: "var(--color-text-secondary)" }}>
            Everything you need to know &mdash; from incorporation to fundraising
          </p>
        </div>

        {/* Section 1: Learning Path (Stage Timeline) */}
        <div className="mb-20">
          <h2
            className="text-xl font-bold mb-8 flex items-center gap-3"
            style={{ fontFamily: "var(--font-display)" }}
          >
            <span
              className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold"
              style={{
                background: "rgba(139, 92, 246, 0.15)",
                border: "1px solid rgba(139, 92, 246, 0.5)",
                color: "rgb(139, 92, 246)",
              }}
            >
              &#9654;
            </span>
            <span style={{ color: "var(--color-text-primary)" }}>Learning Path</span>
          </h2>

          {/* Timeline */}
          <div className="relative">
            {/* Vertical timeline line */}
            <div
              className="absolute left-6 top-0 bottom-0 w-px"
              style={{ background: "linear-gradient(to bottom, rgba(139, 92, 246, 0.5), rgba(139, 92, 246, 0.1))" }}
            />

            <div className="space-y-4">
              {stages.map((stage: any, idx: number) => {
                const isExpanded = expandedStage === stage.id;
                return (
                  <div key={stage.id || idx} className="relative pl-16 animate-fade-in-up" style={{ animationDelay: `${idx * 0.05}s` }}>
                    {/* Stage number circle */}
                    <div
                      className="absolute left-2 top-5 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold z-10"
                      style={{
                        background: isExpanded
                          ? "rgba(139, 92, 246, 0.3)"
                          : "rgba(139, 92, 246, 0.15)",
                        border: "1px solid rgba(139, 92, 246, 0.5)",
                        color: "rgb(139, 92, 246)",
                      }}
                    >
                      {idx + 1}
                    </div>

                    {/* Stage card */}
                    <div
                      className="glass-card p-5 transition-all duration-200"
                      style={{
                        cursor: "pointer",
                        borderColor: isExpanded ? "rgba(139, 92, 246, 0.3)" : undefined,
                        background: isExpanded ? "rgba(139, 92, 246, 0.05)" : undefined,
                      }}
                      onClick={() => setExpandedStage(isExpanded ? null : stage.id)}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="text-base font-bold" style={{ color: "var(--color-text-primary)" }}>
                            {stage.title}
                          </h3>
                          <p className="text-sm mt-1" style={{ color: "var(--color-text-secondary)" }}>
                            {stage.description}
                          </p>
                        </div>
                        <svg
                          className={`w-5 h-5 shrink-0 ml-4 transition-transform duration-200 ${isExpanded ? "rotate-180" : ""}`}
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                          strokeWidth={2}
                          style={{ color: "var(--color-text-muted)" }}
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                        </svg>
                      </div>

                      {/* Expanded content */}
                      {isExpanded && (
                        <div className="mt-6 space-y-6">
                          {/* Why It Matters */}
                          {stage.why_it_matters && (
                            <div>
                              <h4
                                className="text-xs font-semibold uppercase tracking-wider mb-3"
                                style={{ color: "rgb(139, 92, 246)" }}
                              >
                                Why It Matters
                              </h4>
                              <div className="space-y-3">
                                {stage.why_it_matters.split("\n\n").map((para: string, pIdx: number) => (
                                  <p
                                    key={pIdx}
                                    className="text-sm leading-relaxed"
                                    style={{ color: "var(--color-text-secondary)" }}
                                  >
                                    {para}
                                  </p>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Key Deadlines */}
                          {stage.key_deadlines && stage.key_deadlines.length > 0 && (
                            <div>
                              <h4
                                className="text-xs font-semibold uppercase tracking-wider mb-3"
                                style={{ color: "rgb(245, 158, 11)" }}
                              >
                                Key Deadlines
                              </h4>
                              <div className="space-y-2">
                                {stage.key_deadlines.map((deadline: any, dIdx: number) => (
                                  <div
                                    key={dIdx}
                                    className="flex items-start gap-3 text-sm p-3 rounded-lg"
                                    style={{
                                      borderLeft: "3px solid rgba(245, 158, 11, 0.6)",
                                      background: "rgba(245, 158, 11, 0.05)",
                                    }}
                                  >
                                    <span
                                      className="text-[10px] font-semibold px-2 py-0.5 rounded-full shrink-0 mt-0.5"
                                      style={{
                                        background: "rgba(245, 158, 11, 0.15)",
                                        color: "rgb(245, 158, 11)",
                                      }}
                                    >
                                      {typeof deadline === "string" ? "DEADLINE" : deadline.label || "DEADLINE"}
                                    </span>
                                    <span style={{ color: "var(--color-text-secondary)" }}>
                                      {typeof deadline === "string" ? deadline : deadline.text || deadline.description}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Documents */}
                          {stage.documents && stage.documents.length > 0 && (
                            <div>
                              <h4
                                className="text-xs font-semibold uppercase tracking-wider mb-3"
                                style={{ color: "var(--color-text-primary)" }}
                              >
                                Documents
                              </h4>
                              <div className="space-y-3">
                                {stage.documents.map((doc: any, docIdx: number) => {
                                  const priorityStyle = getPriorityStyle(doc.priority);
                                  const isTemplateSelected = selectedTemplate === doc.template_type;

                                  return (
                                    <div
                                      key={docIdx}
                                      className="rounded-xl border p-4"
                                      style={{
                                        cursor: "default",
                                        borderColor: "var(--color-border)",
                                        background: "var(--color-bg-card)",
                                      }}
                                      onClick={(e) => e.stopPropagation()}
                                    >
                                      <div className="flex items-start justify-between gap-3 mb-2">
                                        <h5 className="text-sm font-semibold" style={{ color: "var(--color-text-primary)" }}>
                                          {doc.name}
                                        </h5>
                                        <span
                                          className="text-[10px] font-semibold px-2 py-0.5 rounded-full shrink-0"
                                          style={{
                                            background: priorityStyle.bg,
                                            border: `1px solid ${priorityStyle.border}`,
                                            color: priorityStyle.text,
                                          }}
                                        >
                                          {(doc.priority || "optional").toUpperCase()}
                                        </span>
                                      </div>

                                      {doc.why_needed && (
                                        <p className="text-xs mb-2 leading-relaxed" style={{ color: "var(--color-text-secondary)" }}>
                                          {doc.why_needed}
                                        </p>
                                      )}

                                      {doc.when_to_create && (
                                        <p className="text-[10px] mb-3" style={{ color: "var(--color-text-muted)" }}>
                                          <span className="font-semibold">When:</span> {doc.when_to_create}
                                        </p>
                                      )}

                                      <div className="flex items-center gap-2 flex-wrap">
                                        {doc.template_type && (
                                          <Link
                                            href={`/documents/create/${doc.template_type}`}
                                            className="btn-primary text-xs !py-1.5 !px-3 inline-flex items-center gap-1"
                                          >
                                            Create This Document
                                            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                                            </svg>
                                          </Link>
                                        )}
                                        {doc.template_type && (
                                          <button
                                            className="text-xs font-medium px-3 py-1.5 rounded-lg transition-colors"
                                            style={{
                                              color: "rgb(139, 92, 246)",
                                              background: isTemplateSelected ? "rgba(139, 92, 246, 0.15)" : "transparent",
                                            }}
                                            onClick={() => handleLearnMore(doc.template_type)}
                                          >
                                            {isTemplateSelected ? "Hide Context" : "Learn More"}
                                          </button>
                                        )}
                                      </div>

                                      {/* Template Context Panel */}
                                      {isTemplateSelected && (
                                        <div
                                          className="mt-4 pt-4"
                                          style={{ borderTop: "1px solid var(--color-border)" }}
                                        >
                                          {contextLoading ? (
                                            <div className="flex items-center gap-2 text-xs py-4" style={{ color: "var(--color-text-muted)" }}>
                                              <div className="w-4 h-4 border-2 border-purple-500/30 border-t-purple-500 rounded-full animate-spin" />
                                              Loading context...
                                            </div>
                                          ) : templateContext ? (
                                            <div className="space-y-4">
                                              {/* Tip */}
                                              {templateContext.tip && (
                                                <div
                                                  className="p-3 rounded-lg text-sm leading-relaxed"
                                                  style={{
                                                    background: "rgba(139, 92, 246, 0.08)",
                                                    border: "1px solid rgba(139, 92, 246, 0.2)",
                                                    color: "var(--color-text-secondary)",
                                                  }}
                                                >
                                                  <span className="text-[10px] font-semibold uppercase tracking-wider block mb-1" style={{ color: "rgb(139, 92, 246)" }}>
                                                    Pro Tip
                                                  </span>
                                                  {templateContext.tip}
                                                </div>
                                              )}

                                              {/* Common Mistakes */}
                                              {templateContext.common_mistakes && templateContext.common_mistakes.length > 0 && (
                                                <div>
                                                  <h6
                                                    className="text-[10px] font-semibold uppercase tracking-wider mb-2"
                                                    style={{ color: "rgb(244, 63, 94)" }}
                                                  >
                                                    Common Mistakes to Avoid
                                                  </h6>
                                                  <ul className="space-y-1.5">
                                                    {templateContext.common_mistakes.map((mistake: string, mIdx: number) => (
                                                      <li
                                                        key={mIdx}
                                                        className="flex items-start gap-2 text-xs"
                                                        style={{ color: "var(--color-text-secondary)" }}
                                                      >
                                                        <span
                                                          className="mt-0.5 shrink-0 w-4 h-4 rounded-full flex items-center justify-center text-[10px]"
                                                          style={{
                                                            background: "rgba(244, 63, 94, 0.15)",
                                                            color: "rgb(244, 63, 94)",
                                                          }}
                                                        >
                                                          !
                                                        </span>
                                                        {mistake}
                                                      </li>
                                                    ))}
                                                  </ul>
                                                </div>
                                              )}

                                              {/* Connected Templates */}
                                              {(templateContext.before_this || templateContext.after_this) && (
                                                <div>
                                                  <h6
                                                    className="text-[10px] font-semibold uppercase tracking-wider mb-2"
                                                    style={{ color: "var(--color-text-muted)" }}
                                                  >
                                                    Related Documents
                                                  </h6>
                                                  <div className="flex flex-wrap gap-2">
                                                    {templateContext.before_this && (
                                                      <Link
                                                        href={`/documents/create/${templateContext.before_this}`}
                                                        className="inline-flex items-center gap-1.5 text-[10px] font-medium px-2.5 py-1 rounded-full transition-colors"
                                                        style={{
                                                          background: "rgba(59, 130, 246, 0.15)",
                                                          border: "1px solid rgba(59, 130, 246, 0.3)",
                                                          color: "rgb(59, 130, 246)",
                                                        }}
                                                      >
                                                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                                          <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
                                                        </svg>
                                                        Do First: {templateContext.before_this.replace(/_/g, " ")}
                                                      </Link>
                                                    )}
                                                    {templateContext.after_this && (
                                                      <Link
                                                        href={`/documents/create/${templateContext.after_this}`}
                                                        className="inline-flex items-center gap-1.5 text-[10px] font-medium px-2.5 py-1 rounded-full transition-colors"
                                                        style={{
                                                          background: "rgba(16, 185, 129, 0.15)",
                                                          border: "1px solid rgba(16, 185, 129, 0.3)",
                                                          color: "rgb(16, 185, 129)",
                                                        }}
                                                      >
                                                        Do Next: {templateContext.after_this.replace(/_/g, " ")}
                                                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                                          <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                                                        </svg>
                                                      </Link>
                                                    )}
                                                  </div>
                                                </div>
                                              )}
                                            </div>
                                          ) : (
                                            <p className="text-xs py-2" style={{ color: "var(--color-text-muted)" }}>
                                              No additional context available for this template.
                                            </p>
                                          )}
                                        </div>
                                      )}
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Section 2: Quick Tips */}
        {tips.length > 0 && (
          <div className="mb-12">
            <h2
              className="text-xl font-bold mb-8 flex items-center gap-3"
              style={{ fontFamily: "var(--font-display)" }}
            >
              <span
                className="w-8 h-8 rounded-full flex items-center justify-center text-sm"
                style={{
                  background: "rgba(16, 185, 129, 0.15)",
                  border: "1px solid rgba(16, 185, 129, 0.5)",
                  color: "rgb(16, 185, 129)",
                }}
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" />
                </svg>
              </span>
              <span style={{ color: "var(--color-text-primary)" }}>Quick Tips</span>
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {tips.map((tip: any, tIdx: number) => {
                const catStyle = getCategoryStyle(tip.category);
                return (
                  <div
                    key={tIdx}
                    className="glass-card p-5 animate-fade-in-up"
                    style={{ cursor: "default", animationDelay: `${tIdx * 0.05}s` }}
                  >
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <h3 className="text-sm font-bold" style={{ color: "var(--color-text-primary)" }}>
                        {tip.title}
                      </h3>
                      {tip.category && (
                        <span
                          className="text-[10px] font-semibold px-2 py-0.5 rounded-full shrink-0"
                          style={{
                            background: catStyle.bg,
                            color: catStyle.text,
                          }}
                        >
                          {tip.category}
                        </span>
                      )}
                    </div>
                    <p className="text-xs leading-relaxed" style={{ color: "var(--color-text-secondary)" }}>
                      {tip.content}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* CTA */}
        <div className="text-center mt-16 mb-8 animate-fade-in-up">
          <div className="glass-card p-8 max-w-2xl mx-auto" style={{ cursor: "default" }}>
            <h3 className="text-lg font-bold mb-2" style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}>
              Ready to create your documents?
            </h3>
            <p className="text-sm mb-6" style={{ color: "var(--color-text-secondary)" }}>
              Use our guided document builder to create legally sound documents with clause-by-clause explanations.
            </p>
            <Link href="/documents" className="btn-primary inline-flex items-center gap-2">
              Go to Legal Documents
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
              </svg>
            </Link>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}
