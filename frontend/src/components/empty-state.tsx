export default function EmptyState({
  icon,
  title,
  description,
  action,
}: {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {icon && <div className="mb-4" style={{ color: "var(--color-text-muted)" }}>{icon}</div>}
      <h3 className="text-lg font-semibold" style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }}>
        {title}
      </h3>
      {description && <p className="mt-1 text-sm max-w-md" style={{ color: "var(--color-text-muted)" }}>{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
