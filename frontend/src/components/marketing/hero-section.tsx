import { ReactNode } from "react";
import Link from "next/link";

interface HeroSectionProps {
  badge?: string;
  title: ReactNode;
  subtitle: string;
  primaryCTA: { label: string; href: string };
  secondaryCTA?: { label: string; href: string };
  children?: ReactNode;
}

export default function HeroSection({
  badge,
  title,
  subtitle,
  primaryCTA,
  secondaryCTA,
  children,
}: HeroSectionProps) {
  return (
    <section className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-24 text-center">
      <div className="animate-fade-in-up max-w-3xl mx-auto">
        {badge && (
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-purple-50 border border-purple-100 text-purple-700 text-xs font-semibold uppercase tracking-wider mb-6">
            {badge}
          </div>
        )}
        <h1
          className="text-4xl md:text-5xl lg:text-6xl font-extrabold leading-tight mb-6 text-[var(--color-text-primary)]"
          style={{ fontFamily: "var(--font-display)" }}
        >
          {title}
        </h1>
        <p className="text-lg md:text-xl text-[var(--color-text-secondary)] leading-relaxed mb-10">
          {subtitle}
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href={primaryCTA.href} className="btn-primary text-lg !py-3.5 !px-8">
            {primaryCTA.label}
          </Link>
          {secondaryCTA && (
            <Link href={secondaryCTA.href} className="btn-secondary text-lg !py-3.5 !px-8">
              {secondaryCTA.label}
            </Link>
          )}
        </div>
        {children}
      </div>
    </section>
  );
}
