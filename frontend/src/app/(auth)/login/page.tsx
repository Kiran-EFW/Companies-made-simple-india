"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiCall } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [resetMsg, setResetMsg] = useState("");
  
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
      await login(res.access_token);
      
      if (typeof window !== "undefined" && localStorage.getItem("pending_company_draft")) {
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

  const handleDevSkip = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await apiCall("/auth/dev-login", {
        method: "POST"
      });
      await login(res.access_token);
      router.push("/dashboard");
    } catch (err: any) {
      setError("Dev login failed. Ensure database is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card p-8 min-w-[360px]">
      <div className="text-center mb-6">
        <Link href="/" className="inline-block text-2xl mb-2">⚡</Link>
        <h1 className="text-2xl font-bold mb-1">Welcome back</h1>
        <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
          Log in to track your company incorporation.
        </p>
      </div>

      {process.env.NODE_ENV === "development" && (
        <button
          onClick={handleDevSkip}
          className="w-full mb-6 py-2 px-4 rounded-lg border text-xs font-mono transition-colors flex items-center justify-center gap-2"
          style={{ background: "var(--color-bg-card)", borderColor: "rgba(139, 92, 246, 0.3)", color: "var(--color-accent-purple-light)" }}
        >
          <span>🛠️</span> DEV SKIP (AUTO LOGIN)
        </button>
      )}

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
            <span className="text-xs cursor-pointer transition-colors" style={{ color: "var(--color-text-muted)" }} onClick={() => setResetMsg("Password reset coming soon. Contact support@companiesmade.in for help.")}>
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
          {resetMsg && (
            <p className="text-xs mt-2" style={{ color: "var(--color-text-muted)" }}>
              {resetMsg}
            </p>
          )}
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

    </div>
  );
}
