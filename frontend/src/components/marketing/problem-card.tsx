import { ReactNode } from "react";

interface ProblemCardProps {
  icon: ReactNode;
  problem: string;
  stat: string;
}

export default function ProblemCard({ icon, problem, stat }: ProblemCardProps) {
  return (
    <div className="card-static p-6 border-l-4 border-l-amber-400 h-full">
      <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4 bg-amber-50 text-amber-600">
        {icon}
      </div>
      <h3 className="text-base font-bold text-[var(--color-text-primary)] mb-2">
        {problem}
      </h3>
      <p className="text-sm text-[var(--color-text-muted)] leading-relaxed">
        {stat}
      </p>
    </div>
  );
}
