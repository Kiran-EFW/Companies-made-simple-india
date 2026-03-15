"use client";

import { useState } from "react";

interface ClauseOption {
  value: string;
  label: string;
  description?: string;
}

interface ClauseDefinition {
  id: string;
  title: string;
  explanation: string;
  learn_more?: string;
  india_note?: string;
  pros?: string[];
  cons?: string[];
  input_type: string;
  options?: ClauseOption[];
  default?: any;
  common_choice_label?: string;
  warning_conditions?: Record<string, any>;
  preview_template?: string;
  depends_on?: string;
}

interface ClauseCardProps {
  clause: ClauseDefinition;
  value: any;
  onChange: (clauseId: string, value: any) => void;
  allValues?: Record<string, any>;
}

export default function ClauseCard({ clause, value, onChange, allValues }: ClauseCardProps) {
  const [expanded, setExpanded] = useState(false);

  // Check depends_on
  if (clause.depends_on && allValues) {
    const depVal = allValues[clause.depends_on];
    if (depVal === false || depVal === "no" || depVal === "" || depVal == null) {
      return null;
    }
  }

  // Check warning conditions
  let warningMessage = "";
  if (clause.warning_conditions && allValues) {
    for (const [condition, message] of Object.entries(clause.warning_conditions)) {
      if (condition === "value_is" && value === clause.warning_conditions.trigger_value) {
        warningMessage = message as string;
      } else if (condition === "when_false" && value === false) {
        warningMessage = message as string;
      } else if (condition === "when_not" && value !== clause.warning_conditions.expected) {
        warningMessage = message as string;
      }
    }
    // Simple string warning
    if (typeof clause.warning_conditions === "object" && clause.warning_conditions.message) {
      const cond = clause.warning_conditions;
      if (cond.when === "false" && value === false) warningMessage = cond.message;
      if (cond.when === "not" && value !== cond.expected) warningMessage = cond.message;
    }
  }

  const hasLearnMore = clause.learn_more || (clause.pros && clause.pros.length > 0) || clause.india_note;

  const inputStyle = {
    background: "var(--color-bg-secondary)",
    borderColor: "var(--color-border)",
    color: "var(--color-text-primary)",
  };

  const renderInput = () => {
    switch (clause.input_type) {
      case "dropdown":
        return (
          <select
            value={value ?? clause.default ?? ""}
            onChange={(e) => onChange(clause.id, e.target.value)}
            className="w-full border rounded-lg p-3 text-sm focus:outline-none focus:border-purple-500/50"
            style={inputStyle}
          >
            <option value="" style={{ background: "var(--color-bg-secondary)" }}>Select...</option>
            {clause.options?.map((opt) => (
              <option key={opt.value} value={opt.value} style={{ background: "var(--color-bg-secondary)" }}>
                {opt.label}
              </option>
            ))}
          </select>
        );

      case "toggle":
        return (
          <button
            onClick={() => onChange(clause.id, !value)}
            className="flex items-center gap-3"
          >
            <div
              className="relative w-12 h-6 rounded-full transition-colors"
              style={{ background: value ? "var(--color-accent-purple)" : "var(--color-border-light)" }}
            >
              <div
                className={`absolute top-0.5 w-5 h-5 rounded-full bg-white transition-transform ${
                  value ? "translate-x-6" : "translate-x-0.5"
                }`}
              />
            </div>
            <span className="text-sm" style={{ color: "var(--color-text-primary)" }}>{value ? "Yes" : "No"}</span>
          </button>
        );

      case "text":
        return (
          <input
            type="text"
            value={value ?? ""}
            onChange={(e) => onChange(clause.id, e.target.value)}
            placeholder={`Enter ${clause.title.toLowerCase()}...`}
            className="w-full border rounded-lg p-3 text-sm focus:outline-none focus:border-purple-500/50"
            style={inputStyle}
          />
        );

      case "textarea":
        return (
          <textarea
            value={value ?? ""}
            onChange={(e) => onChange(clause.id, e.target.value)}
            placeholder={`Enter ${clause.title.toLowerCase()}...`}
            rows={3}
            className="w-full border rounded-lg p-3 text-sm focus:outline-none focus:border-purple-500/50 resize-y"
            style={inputStyle}
          />
        );

      case "number":
        return (
          <input
            type="number"
            value={value ?? ""}
            onChange={(e) => onChange(clause.id, e.target.value ? Number(e.target.value) : "")}
            placeholder="Enter amount..."
            className="w-full border rounded-lg p-3 text-sm focus:outline-none focus:border-purple-500/50"
            style={inputStyle}
          />
        );

      case "date":
        return (
          <input
            type="date"
            value={value ?? ""}
            onChange={(e) => onChange(clause.id, e.target.value)}
            className="w-full border rounded-lg p-3 text-sm focus:outline-none focus:border-purple-500/50"
            style={inputStyle}
          />
        );

      case "multi_select":
        const selected: string[] = Array.isArray(value) ? value : [];
        return (
          <div className="space-y-2">
            {clause.options?.map((opt) => (
              <label key={opt.value} className="flex items-start gap-3 cursor-pointer group">
                <input
                  type="checkbox"
                  checked={selected.includes(opt.value)}
                  onChange={(e) => {
                    const next = e.target.checked
                      ? [...selected, opt.value]
                      : selected.filter((v) => v !== opt.value);
                    onChange(clause.id, next);
                  }}
                  className="mt-0.5 w-4 h-4 rounded text-purple-600 focus:ring-purple-500/30"
                  style={{ borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" }}
                />
                <div>
                  <span className="text-sm transition-colors" style={{ color: "var(--color-text-primary)" }}>
                    {opt.label}
                  </span>
                  {opt.description && (
                    <p className="text-xs mt-0.5" style={{ color: "var(--color-text-muted)" }}>{opt.description}</p>
                  )}
                </div>
              </label>
            ))}
          </div>
        );

      case "slider":
        return (
          <div>
            <input
              type="range"
              min={0}
              max={100}
              value={value ?? 50}
              onChange={(e) => onChange(clause.id, Number(e.target.value))}
              className="w-full accent-purple-600"
            />
            <div className="flex justify-between text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>
              <span>0</span>
              <span className="font-semibold" style={{ color: "var(--color-accent-purple-light)" }}>{value ?? 50}%</span>
              <span>100</span>
            </div>
          </div>
        );

      case "custom":
        return (
          <textarea
            value={typeof value === "string" ? value : JSON.stringify(value ?? "", null, 2)}
            onChange={(e) => onChange(clause.id, e.target.value)}
            placeholder="Enter details..."
            rows={3}
            className="w-full border rounded-lg p-3 text-sm focus:outline-none focus:border-purple-500/50 resize-y"
            style={inputStyle}
          />
        );

      default:
        return (
          <input
            type="text"
            value={value ?? ""}
            onChange={(e) => onChange(clause.id, e.target.value)}
            className="w-full border rounded-lg p-3 text-sm focus:outline-none focus:border-purple-500/50"
            style={inputStyle}
          />
        );
    }
  };

  return (
    <div
      className="rounded-xl border p-5 transition-all"
      style={{
        borderColor: "var(--color-border)",
        background: "var(--color-bg-card)",
      }}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-1">
        <h3 className="text-sm font-semibold" style={{ color: "var(--color-text-primary)" }}>{clause.title}</h3>
        {clause.common_choice_label && (
          <span className="shrink-0 text-[10px] font-medium px-2 py-0.5 rounded-full border" style={{ background: "var(--color-success-light)", color: "var(--color-success)", borderColor: "rgba(16,185,129,0.3)" }}>
            {clause.common_choice_label}
          </span>
        )}
      </div>
      <p className="text-xs mb-4" style={{ color: "var(--color-text-secondary)" }}>{clause.explanation}</p>

      {/* Learn More Toggle */}
      {hasLearnMore && (
        <div className="mb-4">
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1.5 text-xs font-medium transition-colors"
            style={{ color: "var(--color-accent-purple-light)" }}
          >
            <svg
              className={`w-3 h-3 transition-transform ${expanded ? "rotate-90" : ""}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
            {expanded ? "Hide Details" : "Learn More"}
          </button>

          {expanded && (
            <div className="mt-3 rounded-lg border p-4 space-y-3" style={{ borderColor: "rgba(139,92,246,0.2)", background: "rgba(139,92,246,0.05)" }}>
              {clause.learn_more && (
                <p className="text-xs leading-relaxed" style={{ color: "var(--color-text-primary)" }}>{clause.learn_more}</p>
              )}

              {/* Pros and Cons */}
              {((clause.pros && clause.pros.length > 0) || (clause.cons && clause.cons.length > 0)) && (
                <div className="grid grid-cols-2 gap-4">
                  {clause.pros && clause.pros.length > 0 && (
                    <div>
                      <p className="text-[10px] font-semibold uppercase tracking-wider mb-1.5" style={{ color: "var(--color-success)" }}>Pros</p>
                      <ul className="space-y-1">
                        {clause.pros.map((pro, i) => (
                          <li key={i} className="flex items-start gap-1.5 text-xs" style={{ color: "var(--color-text-primary)" }}>
                            <svg className="w-3 h-3 mt-0.5 shrink-0" style={{ color: "var(--color-success)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                            </svg>
                            {pro}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {clause.cons && clause.cons.length > 0 && (
                    <div>
                      <p className="text-[10px] font-semibold uppercase tracking-wider mb-1.5" style={{ color: "var(--color-warning)" }}>Cons</p>
                      <ul className="space-y-1">
                        {clause.cons.map((con, i) => (
                          <li key={i} className="flex items-start gap-1.5 text-xs" style={{ color: "var(--color-text-primary)" }}>
                            <svg className="w-3 h-3 mt-0.5 shrink-0" style={{ color: "var(--color-warning)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126z" />
                            </svg>
                            {con}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* India Note */}
              {clause.india_note && (
                <div className="rounded-lg border p-3" style={{ borderColor: "rgba(245,158,11,0.2)", background: "rgba(245,158,11,0.05)" }}>
                  <p className="text-[10px] font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--color-warning)" }}>India Legal Note</p>
                  <p className="text-xs leading-relaxed" style={{ color: "var(--color-text-primary)" }}>{clause.india_note}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Input Widget */}
      <div className="mb-3">{renderInput()}</div>

      {/* Warning */}
      {warningMessage && (
        <div className="rounded-lg border p-3 mb-3" style={{ borderColor: "rgba(244,63,94,0.2)", background: "rgba(244,63,94,0.1)" }}>
          <div className="flex items-start gap-2">
            <svg className="w-4 h-4 shrink-0 mt-0.5" style={{ color: "var(--color-error)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126z" />
            </svg>
            <p className="text-xs" style={{ color: "var(--color-error)" }}>{warningMessage}</p>
          </div>
        </div>
      )}

      {/* Preview Text */}
      {clause.preview_template && value && (
        <div className="rounded-lg border p-3" style={{ background: "var(--color-bg-secondary)", borderColor: "var(--color-border)" }}>
          <p className="text-[10px] font-medium uppercase tracking-wider mb-1" style={{ color: "var(--color-text-muted)" }}>Clause Preview</p>
          <p className="text-xs italic leading-relaxed" style={{ color: "var(--color-text-secondary)" }}>
            {clause.preview_template.replace("{value}", String(value))}
          </p>
        </div>
      )}
    </div>
  );
}
