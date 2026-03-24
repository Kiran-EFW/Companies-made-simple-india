"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { apiCall } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get("redirect");
  const portal = searchParams.get("portal"); // "ca" for partner-themed login
  const isCa = portal === "ca";
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const handleForgotPassword = async () => {
    const email = (document.getElementById("email") as HTMLInputElement)?.value;
    if (!email) {
      setError("Please enter your email address first");
      return;
    }
    try {
      await apiCall("/auth/forgot-password", {
        method: "POST",
        body: JSON.stringify({ email }),
      });
      setError("");
      alert("If an account exists with that email, a password reset link has been sent.");
    } catch {
      alert("If an account exists with that email, a password reset link has been sent.");
    }
  };

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const res = await apiCall("/auth/login", {
        method: "POST",
        body: JSON.stringify(formData),
      });
      const loggedInUser = await login(res.access_token);

      if (redirectTo) {
        router.push(redirectTo);
      } else if (loggedInUser?.role === "ca_lead") {
        router.push("/ca");
      } else if (typeof window !== "undefined" && localStorage.getItem("pending_company_draft")) {
        router.push("/onboarding");
      } else {
        router.push("/dashboard");
      }
    } catch (err: any) {
      setError(err.message || "Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card p-8 min-w-[360px]">
      <div className="text-center mb-6">
        <Link href="/" className="inline-flex items-center gap-2 mb-2">
          <img src="/logo-icon.png" alt="Anvils" className="w-7 h-7 object-contain" />
          <span className="text-xl font-bold gradient-text" style={{ fontFamily: "var(--font-display)" }}>Anvils</span>
        </Link>

        {isCa ? (
          <>
            <div
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider mb-3"
              style={{ background: "rgba(13, 148, 136, 0.1)", color: "#0d9488" }}
            >
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 00.75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 00-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0112 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 01-.673-.38m0 0A2.18 2.18 0 013 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 013.413-.387m7.5 0V5.25A2.25 2.25 0 0013.5 3h-3a2.25 2.25 0 00-2.25 2.25v.894m7.5 0a48.667 48.667 0 00-7.5 0M12 12.75h.008v.008H12v-.008z" />
              </svg>
              Partner Portal
            </div>
            <h1 className="text-2xl font-bold mb-1">Log in to Partner Portal</h1>
            <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
              Manage your clients, compliance, and marketplace.
            </p>
          </>
        ) : (
          <>
            <h1 className="text-2xl font-bold mb-1">Welcome back</h1>
            <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
              Log in to manage your company.
            </p>
          </>
        )}
      </div>

      {error && (
        <div className="p-3 rounded-lg mb-6 text-sm" style={{ background: "rgba(244, 63, 94, 0.1)", color: "var(--color-accent-rose)" }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1" style={{ color: "var(--color-text-secondary)" }}>
            Email Address
          </label>
          <input
            id="email"
            required
            type="email"
            className="input-field"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            placeholder={isCa ? "ca@firm.com" : "john@example.com"}
          />
        </div>

        <div>
           <div className="flex justify-between items-center mb-1">
            <label className="block text-sm font-medium" style={{ color: "var(--color-text-secondary)" }}>
              Password
            </label>
            <span className="text-xs cursor-pointer transition-colors" style={{ color: "var(--color-text-muted)" }} onClick={handleForgotPassword}>
              Forgot password?
            </span>
          </div>
          <input
            required
            type="password"
            className="input-field"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            placeholder="••••••••"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className={
            isCa
              ? "w-full justify-center mt-4 inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold text-white transition-colors hover:opacity-90"
              : "btn-primary w-full justify-center mt-4"
          }
          style={isCa ? { backgroundColor: "#0d9488" } : undefined}
        >
          {loading ? "Logging in..." : isCa ? "Log In to Partner Portal" : "Log In"}
        </button>
      </form>

      <div className="mt-6 text-center text-sm" style={{ color: "var(--color-text-secondary)" }}>
        Don&#39;t have an account?{" "}
        <Link
          href={isCa ? "/signup?role=ca" : "/signup"}
          className="font-semibold transition-colors"
          style={{ color: isCa ? "#0d9488" : "var(--color-accent-purple-light)" }}
        >
          {isCa ? "Sign up as partner" : "Sign up"}
        </Link>
      </div>

      {isCa && (
        <div className="mt-3 text-center">
          <Link
            href="/login"
            className="text-xs transition-colors"
            style={{ color: "var(--color-text-muted)" }}
          >
            Not a partner? Log in as founder
          </Link>
        </div>
      )}

      {!isCa && (
        <div className="mt-3 text-center">
          <Link
            href="/login?portal=ca"
            className="text-xs transition-colors"
            style={{ color: "var(--color-text-muted)" }}
          >
            Are you a CA? Log in to Partner Portal
          </Link>
        </div>
      )}

      {/* Dev quick-login */}
      {process.env.NODE_ENV === "development" && (
        <div className="mt-6 pt-5 border-t" style={{ borderColor: "var(--color-border)" }}>
          <p className="text-xs text-center mb-3" style={{ color: "var(--color-text-muted)" }}>
            Demo accounts
          </p>
          <div className="grid grid-cols-2 gap-2">
            {[
              { label: "Paul", email: "paul@anvils.in", password: "Anvils123" },
              { label: "Janeevan", email: "janeevan@anvils.in", password: "Anvils123" },
              { label: "Abey", email: "abey@anvils.in", password: "Anvils123" },
              { label: "CA Demo", email: "ca@anvils.in", password: "Anvils123" },
            ].map((acct) => (
              <button
                key={acct.email}
                type="button"
                className="px-3 py-2 rounded-lg text-xs font-medium transition-colors"
                style={{ background: "var(--color-overlay)", color: "var(--color-text-secondary)", border: "1px solid var(--color-border)" }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = "var(--color-accent-purple-light)"; e.currentTarget.style.color = "var(--color-text-primary)"; }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = "var(--color-border)"; e.currentTarget.style.color = "var(--color-text-secondary)"; }}
                onClick={() => {
                  localStorage.removeItem("pending_company_draft");
                  setFormData({ email: acct.email, password: acct.password });
                  setTimeout(() => {
                    const form = document.querySelector("form");
                    if (form) form.requestSubmit();
                  }, 100);
                }}
              >
                {acct.label}
              </button>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense>
      <LoginForm />
    </Suspense>
  );
}
