interface Logo {
  name: string;
  src?: string;
  alt: string;
}

interface LogoCloudProps {
  logos: Logo[];
  title?: string;
}

export default function LogoCloud({ logos, title }: LogoCloudProps) {
  return (
    <div className="text-center">
      {title && (
        <p className="text-xs uppercase tracking-wider font-semibold text-[var(--color-text-muted)] mb-6">
          {title}
        </p>
      )}
      <div className="flex flex-wrap items-center justify-center gap-8 md:gap-12">
        {logos.map((logo, i) =>
          logo.src ? (
            <img
              key={i}
              src={logo.src}
              alt={logo.alt}
              className="h-8 md:h-10 object-contain grayscale opacity-60 hover:grayscale-0 hover:opacity-100 transition-all duration-300"
            />
          ) : (
            <span
              key={i}
              className="text-sm font-semibold text-[var(--color-text-muted)] opacity-60 hover:opacity-100 transition-opacity"
            >
              {logo.name}
            </span>
          )
        )}
      </div>
    </div>
  );
}
