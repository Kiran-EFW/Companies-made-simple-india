"use client";

interface DocumentPreviewProps {
  html: string;
  title?: string;
}

export default function DocumentPreview({ html, title }: DocumentPreviewProps) {
  return (
    <div className="rounded-xl border border-gray-700 bg-gray-800/50 overflow-hidden">
      {title && (
        <div className="px-5 py-3 border-b border-gray-700 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white">{title}</h3>
          <span className="text-[10px] text-gray-500 uppercase tracking-wider">Preview</span>
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
