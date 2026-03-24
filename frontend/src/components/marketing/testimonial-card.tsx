import { Quote } from "lucide-react";

interface TestimonialCardProps {
  quote: string;
  author: string;
  role: string;
  company: string;
}

export default function TestimonialCard({
  quote,
  author,
  role,
  company,
}: TestimonialCardProps) {
  return (
    <div className="card-static p-6 md:p-8 border-l-4 border-l-purple-500 flex flex-col h-full">
      <Quote className="w-6 h-6 text-purple-300 mb-4 shrink-0" />
      <p className="text-[var(--color-text-secondary)] leading-relaxed flex-1 text-sm md:text-base italic">
        &ldquo;{quote}&rdquo;
      </p>
      <div className="mt-6 pt-4 border-t border-[var(--color-border)]">
        <div className="font-semibold text-[var(--color-text-primary)] text-sm">
          {author}
        </div>
        <div className="text-xs text-[var(--color-text-muted)] mt-0.5">
          {role}, {company}
        </div>
      </div>
    </div>
  );
}
