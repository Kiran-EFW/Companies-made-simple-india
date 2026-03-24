"use client";

import { useState } from "react";
import { Plus, Minus } from "lucide-react";

interface FAQItem {
  question: string;
  answer: string;
}

interface FAQAccordionProps {
  items: FAQItem[];
}

export default function FAQAccordion({ items }: FAQAccordionProps) {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <div className="space-y-3">
      {items.map((item, i) => {
        const isOpen = openIndex === i;
        return (
          <div
            key={i}
            className="card-static border border-[var(--color-border)] rounded-xl overflow-hidden"
          >
            <button
              onClick={() => setOpenIndex(isOpen ? null : i)}
              className="w-full flex items-center justify-between gap-4 px-5 py-4 text-left hover:bg-[var(--color-bg-secondary)] transition-colors"
            >
              <span className="text-sm md:text-base font-semibold text-[var(--color-text-primary)]">
                {item.question}
              </span>
              {isOpen ? (
                <Minus className="w-4 h-4 shrink-0 text-purple-500" />
              ) : (
                <Plus className="w-4 h-4 shrink-0 text-[var(--color-text-muted)]" />
              )}
            </button>
            <div
              className={`overflow-hidden transition-all duration-300 ${
                isOpen ? "max-h-96 opacity-100" : "max-h-0 opacity-0"
              }`}
            >
              <div className="px-5 pb-4 text-sm text-[var(--color-text-secondary)] leading-relaxed">
                {item.answer}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
