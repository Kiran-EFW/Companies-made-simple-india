interface StatusStyle {
  background: string;
  color: string;
  borderColor: string;
}

const STATUS_STYLES: Record<string, StatusStyle> = {
  // Company statuses
  draft: { background: "rgba(107,114,128,0.15)", color: "var(--color-text-secondary)", borderColor: "rgba(107,114,128,0.2)" },
  pending: { background: "rgba(245,158,11,0.15)", color: "var(--color-warning)", borderColor: "rgba(245,158,11,0.2)" },
  in_progress: { background: "rgba(59,130,246,0.15)", color: "var(--color-info)", borderColor: "rgba(59,130,246,0.2)" },
  completed: { background: "rgba(16,185,129,0.15)", color: "var(--color-success)", borderColor: "rgba(16,185,129,0.2)" },
  finalized: { background: "rgba(16,185,129,0.15)", color: "var(--color-success)", borderColor: "rgba(16,185,129,0.2)" },
  cancelled: { background: "rgba(239,68,68,0.15)", color: "var(--color-error)", borderColor: "rgba(239,68,68,0.2)" },
  expired: { background: "rgba(107,114,128,0.15)", color: "var(--color-text-muted)", borderColor: "rgba(107,114,128,0.2)" },

  // Compliance
  upcoming: { background: "rgba(59,130,246,0.15)", color: "var(--color-info)", borderColor: "rgba(59,130,246,0.2)" },
  due_soon: { background: "rgba(245,158,11,0.15)", color: "var(--color-warning)", borderColor: "rgba(245,158,11,0.2)" },
  overdue: { background: "rgba(239,68,68,0.15)", color: "var(--color-error)", borderColor: "rgba(239,68,68,0.2)" },

  // E-sign
  sent: { background: "rgba(59,130,246,0.15)", color: "var(--color-info)", borderColor: "rgba(59,130,246,0.2)" },
  partially_signed: { background: "rgba(245,158,11,0.15)", color: "var(--color-warning)", borderColor: "rgba(245,158,11,0.2)" },
  signed: { background: "rgba(16,185,129,0.15)", color: "var(--color-success)", borderColor: "rgba(16,185,129,0.2)" },
  declined: { background: "rgba(239,68,68,0.15)", color: "var(--color-error)", borderColor: "rgba(239,68,68,0.2)" },

  // Meetings
  scheduled: { background: "rgba(59,130,246,0.15)", color: "var(--color-info)", borderColor: "rgba(59,130,246,0.2)" },
  notice_sent: { background: "rgba(139,92,246,0.15)", color: "var(--color-accent-purple-light)", borderColor: "rgba(139,92,246,0.2)" },
  minutes_draft: { background: "rgba(245,158,11,0.15)", color: "var(--color-warning)", borderColor: "rgba(245,158,11,0.2)" },
  minutes_signed: { background: "rgba(16,185,129,0.15)", color: "var(--color-success)", borderColor: "rgba(16,185,129,0.2)" },

  // Documents
  preview: { background: "rgba(139,92,246,0.15)", color: "var(--color-accent-purple-light)", borderColor: "rgba(139,92,246,0.2)" },
  downloaded: { background: "rgba(16,185,129,0.15)", color: "var(--color-success)", borderColor: "rgba(16,185,129,0.2)" },

  // Default
  default: { background: "rgba(107,114,128,0.15)", color: "var(--color-text-secondary)", borderColor: "rgba(107,114,128,0.2)" },
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
  const styles = STATUS_STYLES[status.toLowerCase()] || STATUS_STYLES.default;
  const sizeClasses = {
    xs: "text-[10px] px-1.5 py-0.5",
    sm: "text-xs px-2 py-0.5",
    md: "text-sm px-3 py-1",
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border font-medium ${sizeClasses[size]}`}
      style={styles}
    >
      {label || status.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
    </span>
  );
}
