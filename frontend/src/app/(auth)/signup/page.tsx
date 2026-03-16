"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiCall } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
export default function SignupPage() {
  const router = useRouter();
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

    try {
      const res = await apiCall("/auth/signup", {
        method: "POST",
        body: JSON.stringify(formData),
      });
      await login(res.access_token);
      
      // If they came from pricing with saved configuration, redirect to onboarding
      if (typeof window !== "undefined" && localStorage.getItem("pending_company_draft")) {
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
    <div className="glass-card p-8">
      <div className="text-center mb-8">
        <Link href="/" className="inline-flex items-center gap-2 mb-4">
          <img src="/logo-icon.png" alt="Anvils" className="w-7 h-7 object-contain" />
          <span className="text-xl font-bold gradient-text" style={{ fontFamily: "var(--font-display)" }}>Anvils</span>
        </Link>
        <h1 className="text-2xl font-bold mb-2">Create your account</h1>
        <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
          Start incorporating your company today.
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
            Full Name
          </label>
          <input
            required
            type="text"
            className="input-field"
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            placeholder="John Doe"
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
            placeholder="john@example.com"
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
          className="btn-primary w-full justify-center mt-2"
        >
          {loading ? "Creating account..." : "Sign Up →"}
        </button>
      </form>

      <div className="mt-6 text-center text-sm" style={{ color: "var(--color-text-secondary)" }}>
        Already have an account?{" "}
        <Link href="/login" className="font-semibold transition-colors" style={{ color: "var(--color-accent-purple-light)" }}>
          Log in
        </Link>
      </div>

    </div>
  );
}
