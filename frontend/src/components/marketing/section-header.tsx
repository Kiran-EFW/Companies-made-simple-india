import { ReactNode } from "react";

interface SectionHeaderProps {
  title: ReactNode;
  subtitle?: string;
}

export default function SectionHeader({ title, subtitle }: SectionHeaderProps) {
  return (
    <div className="text-center mb-12">
      <h2
        className="text-3xl md:text-4xl font-bold text-gray-900 mb-4"
        style={{ fontFamily: "var(--font-display)" }}
      >
        {title}
      </h2>
      {subtitle && (
        <p className="text-gray-500 max-w-xl mx-auto text-lg">{subtitle}</p>
      )}
    </div>
  );
}
