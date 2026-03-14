export function Spinner({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const sizeMap = { sm: "w-4 h-4", md: "w-8 h-8", lg: "w-12 h-12" };
  return (
    <div className={`${sizeMap[size]} border-2 border-gray-700 border-t-purple-500 rounded-full animate-spin`} />
  );
}

export function PageLoader({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
      <Spinner size="lg" />
      <p className="text-sm text-gray-400">{message}</p>
    </div>
  );
}

export function ButtonLoader({ className = "" }: { className?: string }) {
  return <Spinner size="sm" />;
}
