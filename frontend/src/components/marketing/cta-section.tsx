import Link from "next/link";

interface CTASectionProps {
  title: string;
  subtitle: string;
  primaryCTA: { label: string; href: string };
  secondaryCTA?: { label: string; href: string };
  variant?: "purple" | "white";
}

export default function CTASection({
  title,
  subtitle,
  primaryCTA,
  secondaryCTA,
  variant = "purple",
}: CTASectionProps) {
  if (variant === "purple") {
    return (
      <section className="relative z-10 py-20">
        <div className="max-w-4xl mx-auto px-6">
          <div className="bg-purple-700 rounded-2xl p-10 md:p-14 text-center">
            <h2
              className="text-3xl md:text-4xl font-bold text-white mb-4"
              style={{ fontFamily: "var(--font-display)" }}
            >
              {title}
            </h2>
            <p className="text-purple-200 text-lg mb-8 max-w-xl mx-auto">{subtitle}</p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href={primaryCTA.href}
                className="inline-flex items-center justify-center gap-2 px-8 py-3.5 bg-white text-purple-700 font-semibold rounded-xl hover:bg-purple-50 transition-colors text-lg"
              >
                {primaryCTA.label}
              </Link>
              {secondaryCTA && (
                <Link
                  href={secondaryCTA.href}
                  className="inline-flex items-center justify-center gap-2 px-8 py-3.5 border border-purple-400 text-white font-semibold rounded-xl hover:bg-purple-600 transition-colors text-lg"
                >
                  {secondaryCTA.label}
                </Link>
              )}
            </div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="relative z-10 py-20 bg-gray-50">
      <div className="max-w-3xl mx-auto px-6 text-center">
        <h2
          className="text-3xl md:text-4xl font-bold text-gray-900 mb-4"
          style={{ fontFamily: "var(--font-display)" }}
        >
          {title}
        </h2>
        <p className="text-gray-500 text-lg mb-8">{subtitle}</p>
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
      </div>
    </section>
  );
}
