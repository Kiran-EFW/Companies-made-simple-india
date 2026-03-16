import { ReactNode } from "react";
import Link from "next/link";

interface FeatureCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  href?: string;
  accentColor?: "purple" | "emerald" | "blue";
}

const COLOR_MAP = {
  purple: { bg: "bg-purple-50", text: "text-purple-600" },
  emerald: { bg: "bg-emerald-50", text: "text-emerald-600" },
  blue: { bg: "bg-blue-50", text: "text-blue-600" },
};

export default function FeatureCard({
  icon,
  title,
  description,
  href,
  accentColor = "purple",
}: FeatureCardProps) {
  const colors = COLOR_MAP[accentColor];

  const content = (
    <div className="card p-6 h-full">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-4 ${colors.bg}`}>
        <div className={colors.text}>{icon}</div>
      </div>
      <h3 className="text-lg font-bold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-500 leading-relaxed">{description}</p>
      {href && (
        <div className="mt-4 text-sm font-medium text-purple-600">
          Learn more &rarr;
        </div>
      )}
    </div>
  );

  if (href) {
    return (
      <Link href={href} className="block hover:no-underline">
        {content}
      </Link>
    );
  }

  return content;
}
