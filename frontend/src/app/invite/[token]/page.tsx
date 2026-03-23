"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { getInviteInfo, acceptInvite, declineInvite } from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface InviteDetails {
  company_name: string;
  role: string;
  inviter_name: string;
  inviter_email?: string;
  invite_message?: string;
  invite_status: string; // pending, accepted, declined, revoked, expired
  invite_email: string;
  invite_name: string;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const ROLE_COLORS: Record<string, { bg: string; text: string }> = {
  owner: { bg: "var(--color-purple-bg)", text: "var(--color-accent-purple-light)" },
  director: { bg: "var(--color-info-light)", text: "var(--color-info)" },
  shareholder: { bg: "var(--color-success-light)", text: "var(--color-accent-emerald-light)" },
  company_secretary: { bg: "rgba(6, 182, 212, 0.15)", text: "var(--color-accent-cyan)" },
  auditor: { bg: "var(--color-warning-light)", text: "var(--color-warning)" },
  advisor: { bg: "rgba(99, 102, 241, 0.15)", text: "rgb(99, 102, 241)" },
  viewer: { bg: "var(--color-hover-overlay)", text: "var(--color-text-muted)" },
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function InviteAcceptPage() {
  const params = useParams();
  const router = useRouter();
  const token = params.token as string;

  const [invite, setInvite] = useState<InviteDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionLoading, setActionLoading] = useState(false);
  const [declined, setDeclined] = useState(false);

  const isLoggedIn =
    typeof window !== "undefined" && !!localStorage.getItem("access_token");

  // ─── Fetch invite details ─────────────────────────────────
  useEffect(() => {
    if (!token) return;
    (async () => {
      setLoading(true);
      try {
        const data = await getInviteInfo(token);
        setInvite(data);
      } catch (err: any) {
        setError(err.message || "This invite link is invalid or has expired.");
      } finally {
        setLoading(false);
      }
    })();
  }, [token]);

  // ─── Accept invite ────────────────────────────────────────
  async function handleAccept() {
    setActionLoading(true);
    setError("");
    try {
      await acceptInvite(token);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to accept invite.");
    } finally {
      setActionLoading(false);
    }
  }

  // ─── Decline invite ───────────────────────────────────────
  async function handleDecline() {
    setActionLoading(true);
    setError("");
    try {
      await declineInvite(token);
      setDeclined(true);
    } catch (err: any) {
      setError(err.message || "Failed to decline invite.");
    } finally {
      setActionLoading(false);
    }
  }

  // ─── Role badge helper ────────────────────────────────────
  function RoleBadge({ role }: { role: string }) {
    const colors = ROLE_COLORS[role] || ROLE_COLORS.viewer;
    return (
      <span
        className="text-sm px-3 py-1 rounded-full capitalize font-semibold"
        style={{ background: colors.bg, color: colors.text }}
      >
        {role.replace(/_/g, " ")}
      </span>
    );
  }

  // ─── Loading state ────────────────────────────────────────
  if (loading) {
    return (
      <div className="glow-bg min-h-screen flex items-center justify-center p-6">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: "var(--color-accent-purple-light)" }} />
      </div>
    );
  }

  // ─── Error state ──────────────────────────────────────────
  if (error && !invite) {
    return (
      <div className="glow-bg min-h-screen flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <div
            className="glass-card p-8 text-center"
            style={{ cursor: "default" }}
          >
            <Link href="/" className="inline-flex items-center gap-2 mb-6">
              <img src="/logo-icon.png" alt="Anvils" className="w-8 h-8 object-contain" />
              <span className="text-xl font-bold gradient-text" style={{ fontFamily: "var(--font-display)" }}>
                Anvils
              </span>
            </Link>

            <svg
              className="w-14 h-14 mx-auto mb-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="var(--color-accent-rose)"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
              />
            </svg>

            <h1 className="text-xl font-bold mb-2" style={{ color: "var(--color-text-primary)" }}>
              Invalid Invite
            </h1>
            <p className="text-sm mb-6" style={{ color: "var(--color-text-secondary)" }}>
              {error}
            </p>
            <Link
              href="/"
              className="btn-primary px-5 py-2.5 rounded-lg text-sm font-semibold inline-block"
            >
              Go to Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // ─── Already accepted/declined/revoked/expired ────────────
  if (invite && invite.invite_status !== "pending") {
    const statusMessages: Record<string, { title: string; desc: string }> = {
      accepted: {
        title: "Invite Already Accepted",
        desc: "This invite has already been accepted. You can access the company from your dashboard.",
      },
      declined: {
        title: "Invite Declined",
        desc: "This invite has been declined. Contact the inviter if you would like a new invitation.",
      },
      revoked: {
        title: "Invite Revoked",
        desc: "This invite has been revoked by the company administrator.",
      },
      expired: {
        title: "Invite Expired",
        desc: "This invite has expired. Contact the inviter to request a new invitation.",
      },
    };

    const msg = statusMessages[invite.invite_status] || {
      title: "Invite Unavailable",
      desc: "This invite is no longer available.",
    };

    return (
      <div className="glow-bg min-h-screen flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <div
            className="glass-card p-8 text-center"
            style={{ cursor: "default" }}
          >
            <Link href="/" className="inline-flex items-center gap-2 mb-6">
              <img src="/logo-icon.png" alt="Anvils" className="w-8 h-8 object-contain" />
              <span className="text-xl font-bold gradient-text" style={{ fontFamily: "var(--font-display)" }}>
                Anvils
              </span>
            </Link>

            <h1 className="text-xl font-bold mb-2" style={{ color: "var(--color-text-primary)" }}>
              {msg.title}
            </h1>
            <p className="text-sm mb-6" style={{ color: "var(--color-text-secondary)" }}>
              {msg.desc}
            </p>

            {invite.invite_status === "accepted" && isLoggedIn ? (
              <Link
                href="/dashboard"
                className="btn-primary px-5 py-2.5 rounded-lg text-sm font-semibold inline-block"
              >
                Go to Dashboard
              </Link>
            ) : (
              <Link
                href="/"
                className="btn-primary px-5 py-2.5 rounded-lg text-sm font-semibold inline-block"
              >
                Go to Home
              </Link>
            )}
          </div>
        </div>
      </div>
    );
  }

  // ─── Declined success ─────────────────────────────────────
  if (declined) {
    return (
      <div className="glow-bg min-h-screen flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <div
            className="glass-card p-8 text-center"
            style={{ cursor: "default" }}
          >
            <Link href="/" className="inline-flex items-center gap-2 mb-6">
              <img src="/logo-icon.png" alt="Anvils" className="w-8 h-8 object-contain" />
              <span className="text-xl font-bold gradient-text" style={{ fontFamily: "var(--font-display)" }}>
                Anvils
              </span>
            </Link>

            <svg
              className="w-14 h-14 mx-auto mb-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="var(--color-text-muted)"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>

            <h1 className="text-xl font-bold mb-2" style={{ color: "var(--color-text-primary)" }}>
              Invite Declined
            </h1>
            <p className="text-sm mb-6" style={{ color: "var(--color-text-secondary)" }}>
              You have declined the invitation to join {invite?.company_name}. The inviter will be notified.
            </p>
            <Link
              href="/"
              className="px-5 py-2.5 rounded-lg text-sm font-semibold border inline-block transition-colors hover:bg-gray-50"
              style={{ borderColor: "var(--color-border)", color: "var(--color-text-primary)" }}
            >
              Go to Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // ─── Main invite card ─────────────────────────────────────
  return (
    <div className="glow-bg min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-md animate-fade-in-up">
        <div
          className="glass-card p-8"
          style={{ cursor: "default" }}
        >
          {/* Logo */}
          <div className="text-center mb-6">
            <Link href="/" className="inline-flex items-center gap-2 mb-2">
              <img src="/logo-icon.png" alt="Anvils" className="w-8 h-8 object-contain" />
              <span className="text-xl font-bold gradient-text" style={{ fontFamily: "var(--font-display)" }}>
                Anvils
              </span>
            </Link>
          </div>

          {/* Invite details */}
          <div className="text-center mb-6">
            <h1 className="text-2xl font-bold mb-3" style={{ color: "var(--color-text-primary)" }}>
              You&apos;re invited to join
            </h1>
            <div
              className="text-xl font-bold mb-3"
              style={{ color: "var(--color-accent-purple-light)", fontFamily: "var(--font-display)" }}
            >
              {invite?.company_name}
            </div>
            <div className="flex justify-center mb-4">
              <RoleBadge role={invite?.role || "viewer"} />
            </div>
            <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
              Invited by <strong style={{ color: "var(--color-text-primary)" }}>{invite?.inviter_name}</strong>
            </p>
          </div>

          {/* Personal message */}
          {invite?.invite_message && (
            <div
              className="rounded-lg p-4 mb-6"
              style={{
                background: "var(--color-purple-bg)",
                borderLeft: "3px solid var(--color-accent-purple-light)",
              }}
            >
              <p className="text-sm italic" style={{ color: "var(--color-text-secondary)" }}>
                &ldquo;{invite.invite_message}&rdquo;
              </p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div
              className="p-3 rounded-lg mb-4 text-sm"
              style={{ background: "var(--color-error-light)", color: "var(--color-accent-rose)" }}
            >
              {error}
            </div>
          )}

          {/* Actions */}
          {isLoggedIn ? (
            <div className="space-y-3">
              <button
                className="btn-primary w-full py-3 rounded-lg text-sm font-semibold flex items-center justify-center gap-2"
                onClick={handleAccept}
                disabled={actionLoading}
              >
                {actionLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                    Processing...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Accept Invite
                  </>
                )}
              </button>
              <button
                className="w-full py-3 rounded-lg text-sm font-medium border transition-colors hover:bg-gray-50"
                style={{ borderColor: "var(--color-border)", color: "var(--color-text-secondary)" }}
                onClick={handleDecline}
                disabled={actionLoading}
              >
                Decline
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              <Link
                href={`/signup?invite=${token}`}
                className="btn-primary w-full py-3 rounded-lg text-sm font-semibold flex items-center justify-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M18 7.5v3m0 0v3m0-3h3m-3 0h-3m-2.25-4.125a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zM3 19.235v-.11a6.375 6.375 0 0112.75 0v.109A12.318 12.318 0 019.374 21c-2.331 0-4.512-.645-6.374-1.766z" />
                </svg>
                Sign Up to Accept
              </Link>
              <div className="text-center">
                <Link
                  href={`/login?redirect=/invite/${token}`}
                  className="text-sm font-medium transition-colors hover:opacity-80"
                  style={{ color: "var(--color-accent-purple-light)" }}
                >
                  Already have an account? Log in
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
