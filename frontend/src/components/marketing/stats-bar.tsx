"use client";

import { useEffect, useRef, useState } from "react";

interface Stat {
  value: string;
  label: string;
}

interface StatsBarProps {
  stats: Stat[];
}

export default function StatsBar({ stats }: StatsBarProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.3 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={`mt-12 flex flex-wrap justify-center gap-8 md:gap-12 transition-all duration-700 ${
        visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
      }`}
    >
      {stats.map((stat, i) => (
        <div key={i} className="flex items-center gap-8 md:gap-12">
          <div className="text-center">
            <div
              className="text-2xl md:text-3xl font-extrabold text-[var(--color-accent-purple)]"
              style={{ fontFamily: "var(--font-display)" }}
            >
              {stat.value}
            </div>
            <div className="text-xs md:text-sm text-[var(--color-text-muted)] mt-1 font-medium">
              {stat.label}
            </div>
          </div>
          {i < stats.length - 1 && (
            <div className="hidden md:block w-px h-10 bg-[var(--color-border)]" />
          )}
        </div>
      ))}
    </div>
  );
}
