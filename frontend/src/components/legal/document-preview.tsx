"use client";

interface DocumentPreviewProps {
  html: string;
  title?: string;
}

export default function DocumentPreview({ html, title }: DocumentPreviewProps) {
  return (
    <div
      className="rounded-xl border overflow-hidden"
      style={{
        borderColor: "var(--color-border)",
        background: "var(--color-bg-card)",
      }}
    >
      {title && (
        <div
          className="px-5 py-3 flex items-center justify-between"
          style={{ borderBottom: "1px solid var(--color-border)" }}
        >
          <h3 className="text-sm font-semibold" style={{ color: "var(--color-text-primary)" }}>{title}</h3>
          <span className="text-[10px] uppercase tracking-wider" style={{ color: "var(--color-text-muted)" }}>Preview</span>
        </div>
      )}
      <div className="p-4">
        <div
          className="bg-white rounded-lg shadow-lg max-h-[600px] overflow-y-auto"
          style={{ scrollbarWidth: "thin" }}
        >
          <div
            className="p-8 text-black prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: html }}
          />
        </div>
      </div>
    </div>
  );
}
