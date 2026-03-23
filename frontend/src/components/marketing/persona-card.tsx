import { ReactNode } from "react";
import Link from "next/link";

interface PersonaCardProps {
  icon: ReactNode;
  persona: string;
  headline: string;
  bullets: string[];
  href: string;
  accentColor: "purple" | "emerald" | "blue";
}

const COLOR_MAP = {
  purple: { bg: "bg-purple-50", text: "text-purple-600", border: "border-purple-100", bullet: "text-purple-400" },
  emerald: { bg: "bg-emerald-50", text: "text-emerald-600", border: "border-emerald-100", bullet: "text-emerald-400" },
  blue: { bg: "bg-blue-50", text: "text-blue-600", border: "border-blue-100", bullet: "text-blue-400" },
};

export default function PersonaCard({
  icon,
  persona,
  headline,
  bullets,
  href,
  accentColor,
}: PersonaCardProps) {
  const colors = COLOR_MAP[accentColor];

  return (
    <div className="card-static p-6 flex flex-col h-full">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${colors.bg}`}>
        <div className={colors.text}>{icon}</div>
      </div>
      <div className={`text-xs font-semibold uppercase tracking-wider mb-1 ${colors.text}`}>
        {persona}
      </div>
      <h3 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">{headline}</h3>
      <ul className="space-y-2 mb-6 flex-1">
        {bullets.map((b) => (
          <li key={b} className="flex items-start gap-2 text-sm text-[var(--color-text-secondary)]">
            <svg className={`w-4 h-4 mt-0.5 shrink-0 ${colors.bullet}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
            {b}
          </li>
        ))}
      </ul>
      <Link
        href={href}
        className={`text-sm font-semibold ${colors.text} hover:underline inline-flex items-center gap-1`}
      >
        Learn more &rarr;
      </Link>
    </div>
  );
}
