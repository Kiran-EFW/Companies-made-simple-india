import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { ErrorBoundary } from "@/components/error-boundary";
import ToastContainer from "@/components/toast";

export const metadata: Metadata = {
  title: "Anvils — Equity & Governance for Indian Startups",
  description:
    "Cap table management, ESOP administration, fundraising tools, compliance automation, and investor portals. Purpose-built for Indian startups and the professionals who advise them.",
  keywords: [
    "cap table management India",
    "ESOP management",
    "startup compliance India",
    "fundraising platform",
    "company incorporation India",
    "investor portal",
    "equity management",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen antialiased">
        <AuthProvider>
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
          <ToastContainer />
        </AuthProvider>
      </body>
    </html>
  );
}
