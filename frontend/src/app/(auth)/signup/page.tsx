"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { apiCall, acceptInvite } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

function SignupForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const inviteToken = searchParams.get("invite");
  const preselectedRole = searchParams.get("role");
  const isCa = preselectedRole === "ca";
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    phone: "",
    password: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    if (formData.password.length < 8 || !/[A-Z]/.test(formData.password) || !/[a-z]/.test(formData.password) || !/\d/.test(formData.password)) {
      setError("Password must be at least 8 characters with uppercase, lowercase, and a digit");
      setLoading(false);
      return;
    }

    try {
      const res = await apiCall("/auth/signup", {
        method: "POST",
        body: JSON.stringify({
          ...formData,
          role: isCa ? "ca_lead" : "user",
        }),
      });
      const loggedInUser = await login(res.access_token);

      // If they signed up via an invite link, accept the invite first
      if (inviteToken) {
        try {
          await acceptInvite(inviteToken);
        } catch {
          // Invite may have already been accepted or expired — continue
        }
        router.push("/dashboard");
      } else if (isCa || loggedInUser?.role === "ca_lead") {
        router.push("/ca");
      } else if (typeof window !== "undefined" && localStorage.getItem("pending_company_draft")) {
        router.push("/onboarding");
      } else {
        router.push("/dashboard");
      }
    } catch (err: any) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card p-8 min-w-[360px]">
      <div className="text-center mb-6">
        <Link href="/" className="inline-flex items-center gap-2 mb-2">
          <img src="/logo-icon.png" alt="Anvils" className="h-7 w-auto" />
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
            <h1 className="text-2xl font-bold mb-1">Create your partner account</h1>
            <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
              Manage clients, fulfill services, and earn from the marketplace.
            </p>
          </>
        ) : (
          <>
            <h1 className="text-2xl font-bold mb-1">Create your account</h1>
            <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
              Sign up to incorporate and manage your company.
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
            Full Name
          </label>
          <input
            required
            type="text"
            className="input-field"
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            placeholder={isCa ? "CA Rajesh Kumar" : "John Doe"}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1" style={{ color: "var(--color-text-secondary)" }}>
            Email Address
          </label>
          <input
            required
            type="email"
            className="input-field"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            placeholder={isCa ? "ca@firm.com" : "john@example.com"}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1" style={{ color: "var(--color-text-secondary)" }}>
            Phone Number (Optional)
          </label>
          <input
            type="tel"
            className="input-field"
            value={formData.phone}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            placeholder="+91 98765 43210"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1" style={{ color: "var(--color-text-secondary)" }}>
            Password
          </label>
          <input
            required
            type="password"
            className="input-field"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            placeholder="••••••••"
            minLength={8}
          />
          <div className="mt-1.5 space-y-0.5">
            {[
              { test: formData.password.length >= 8, label: "At least 8 characters" },
              { test: /[A-Z]/.test(formData.password), label: "One uppercase letter" },
              { test: /[a-z]/.test(formData.password), label: "One lowercase letter" },
              { test: /\d/.test(formData.password), label: "One digit" },
            ].map((rule) => (
              <div key={rule.label} className="flex items-center gap-1.5 text-xs" style={{ color: formData.password ? (rule.test ? "var(--color-accent-emerald)" : "var(--color-text-muted)") : "var(--color-text-muted)" }}>
                {formData.password ? (
                  rule.test ? (
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}><path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
                  ) : (
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
                  )
                ) : (
                  <span className="w-3 h-3 flex items-center justify-center">-</span>
                )}
                {rule.label}
              </div>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className={
            isCa
              ? "w-full justify-center mt-2 inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold text-white transition-colors hover:opacity-90"
              : "btn-primary w-full justify-center mt-2"
          }
          style={isCa ? { backgroundColor: "#0d9488" } : undefined}
        >
          {loading
            ? "Creating account..."
            : isCa
            ? "Create Partner Account"
            : "Sign Up"
          }
        </button>
      </form>

      {isCa && (
        <p className="mt-4 text-xs text-center leading-relaxed" style={{ color: "var(--color-text-muted)" }}>
          After signup, you can register as a marketplace partner and start accepting service assignments.
        </p>
      )}

      <div className="mt-6 text-center text-sm" style={{ color: "var(--color-text-secondary)" }}>
        Already have an account?{" "}
        <Link
          href={isCa ? "/login?portal=ca" : "/login"}
          className="font-semibold transition-colors"
          style={{ color: isCa ? "#0d9488" : "var(--color-accent-purple-light)" }}
        >
          {isCa ? "Log in to Partner Portal" : "Log in"}
        </Link>
      </div>

      {isCa && (
        <div className="mt-3 text-center">
          <Link
            href="/signup"
            className="text-xs transition-colors"
            style={{ color: "var(--color-text-muted)" }}
          >
            Not a partner? Sign up as founder
          </Link>
        </div>
      )}

      {!isCa && (
        <div className="mt-3 text-center">
          <Link
            href="/signup?role=ca"
            className="text-xs transition-colors"
            style={{ color: "var(--color-text-muted)" }}
          >
            Are you a CA? Sign up for Partner Portal
          </Link>
        </div>
      )}
    </div>
  );
}

export default function SignupPage() {
  return (
    <Suspense>
      <SignupForm />
    </Suspense>
  );
}
