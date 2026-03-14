export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="glow-bg min-h-screen flex flex-col items-center justify-center p-6">
      {/* We'll use the specific auth pages to show the forms */}
      <div className="w-full max-w-md animate-fade-in-up">
        {children}
      </div>
    </div>
  );
}
