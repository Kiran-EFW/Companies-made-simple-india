"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { apiCall } from "@/lib/api";

export default function AdminLoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await apiCall("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      await login(res.access_token);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Invalid credentials");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-full max-w-sm mx-4">
        <div className="text-center mb-8">
          <h1
            className="text-3xl font-bold gradient-text"
            style={{ fontFamily: "var(--font-display)" }}
          >
            CMS India
          </h1>
          <p className="text-sm mt-2" style={{ color: "var(--color-text-muted)" }}>Admin Portal</p>
        </div>

        <form onSubmit={handleSubmit} className="glass-card p-6 space-y-4">
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
              <p className="text-sm" style={{ color: "var(--color-error)" }}>{error}</p>
            </div>
          )}

          <div>
            <label className="block text-xs mb-1.5 uppercase tracking-wider font-medium" style={{ color: "var(--color-text-secondary)" }}>
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="input-field w-full"
              placeholder="admin@cmsindia.co"
            />
          </div>

          <div>
            <label className="block text-xs mb-1.5 uppercase tracking-wider font-medium" style={{ color: "var(--color-text-secondary)" }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="input-field w-full"
              placeholder="Enter your password"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
            style={{
              background: "var(--color-accent-purple)",
              color: "var(--color-text-primary)",
            }}
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <p className="text-center text-[10px] mt-6" style={{ color: "var(--color-text-muted)" }}>
          This portal is for authorized CMS India staff only.
        </p>
        <p className="text-center text-[10px] mt-2" style={{ color: "var(--color-text-muted)" }}>
          CMS India &copy; {new Date().getFullYear()}
        </p>
      </div>
    </div>
  );
}
