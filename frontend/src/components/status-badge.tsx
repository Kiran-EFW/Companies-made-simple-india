const STATUS_COLORS: Record<string, string> = {
  // Company statuses
  draft: "bg-gray-500/15 text-gray-400 border-gray-500/20",
  pending: "bg-amber-500/15 text-amber-400 border-amber-500/20",
  in_progress: "bg-blue-500/15 text-blue-400 border-blue-500/20",
  completed: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
  finalized: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
  cancelled: "bg-red-500/15 text-red-400 border-red-500/20",
  expired: "bg-gray-500/15 text-gray-500 border-gray-500/20",

  // Compliance
  upcoming: "bg-blue-500/15 text-blue-400 border-blue-500/20",
  due_soon: "bg-amber-500/15 text-amber-400 border-amber-500/20",
  overdue: "bg-red-500/15 text-red-400 border-red-500/20",

  // E-sign
  sent: "bg-blue-500/15 text-blue-400 border-blue-500/20",
  partially_signed: "bg-amber-500/15 text-amber-400 border-amber-500/20",
  signed: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
  declined: "bg-red-500/15 text-red-400 border-red-500/20",

  // Meetings
  scheduled: "bg-blue-500/15 text-blue-400 border-blue-500/20",
  notice_sent: "bg-purple-500/15 text-purple-400 border-purple-500/20",
  minutes_draft: "bg-amber-500/15 text-amber-400 border-amber-500/20",
  minutes_signed: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",

  // Documents
  preview: "bg-purple-500/15 text-purple-400 border-purple-500/20",
  downloaded: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",

  // Default
  default: "bg-gray-500/15 text-gray-400 border-gray-500/20",
};

export default function StatusBadge({
  status,
  label,
  size = "sm",
}: {
  status: string;
  label?: string;
  size?: "xs" | "sm" | "md";
}) {
  const colors = STATUS_COLORS[status.toLowerCase()] || STATUS_COLORS.default;
  const sizeClasses = {
    xs: "text-[10px] px-1.5 py-0.5",
    sm: "text-xs px-2 py-0.5",
    md: "text-sm px-3 py-1",
  };

  return (
    <span className={`inline-flex items-center rounded-full border font-medium ${colors} ${sizeClasses[size]}`}>
      {label || status.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
    </span>
  );
}
