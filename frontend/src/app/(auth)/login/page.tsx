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
        <h1 className="text-2xl font-bold mb-1">Welcome back</h1>
        <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
          Log in to manage your company.
        </p>
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
            placeholder="john@example.com"
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
          className="btn-primary w-full justify-center mt-4"
        >
          {loading ? "Logging in..." : "Log In →"}
        </button>
      </form>

      <div className="mt-6 text-center text-sm" style={{ color: "var(--color-text-secondary)" }}>
        Don&#39;t have an account?{" "}
        <Link href="/signup" className="font-semibold transition-colors" style={{ color: "var(--color-accent-purple-light)" }}>
          Sign up
        </Link>
      </div>

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
