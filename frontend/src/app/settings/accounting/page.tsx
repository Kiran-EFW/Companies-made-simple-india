"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import Link from "next/link";
import {
  getCompanies,
  getAccountingConnections,
  getZohoAuthUrl,
  connectTally,
  disconnectAccounting,
  syncAccountingData,
  type AccountingConnectionOut,
} from "@/lib/api";

const PLATFORM_LABELS: Record<string, string> = {
  zoho_books: "Zoho Books",
  tally_prime: "Tally Prime",
};

const STATUS_STYLES: Record<string, string> = {
  connected: "bg-[var(--color-success-light)] text-[var(--color-success)]",
  disconnected: "bg-[var(--color-error-light)] text-[var(--color-error)]",
  error: "bg-[var(--color-error-light)] text-[var(--color-error)]",
  pending: "bg-[var(--color-warning-light)] text-[var(--color-warning)]",
};

export default function AccountingSettingsPage() {
  const { user, loading: authLoading } = useAuth();
  const [companies, setCompanies] = useState<any[]>([]);
  const [connections, setConnections] = useState<AccountingConnectionOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCompany, setSelectedCompany] = useState<number>(0);
  const [connectMode, setConnectMode] = useState<"" | "zoho" | "tally">("");
  const [syncing, setSyncing] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  // Tally form
  const [tallyHost, setTallyHost] = useState("localhost");
  const [tallyPort, setTallyPort] = useState("9000");
  const [tallyCompany, setTallyCompany] = useState("");

  useEffect(() => {
    if (authLoading || !user) return;
    const load = async () => {
      try {
        const [comps, conns] = await Promise.all([
          getCompanies(),
          getAccountingConnections(),
        ]);
        setCompanies(comps);
        setConnections(conns);
        if (comps.length > 0) setSelectedCompany(comps[0].id);
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [user, authLoading]);

  // Check for OAuth callback
  useEffect(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    const state = params.get("state");
    if (code && state) {
      // Exchange code
      (async () => {
        try {
          const { connectZohoBooks } = await import("@/lib/api");
          await connectZohoBooks({ company_id: parseInt(state), code });
          setSuccessMsg("Zoho Books connected successfully!");
          const conns = await getAccountingConnections();
          setConnections(conns);
          // Clean URL
          window.history.replaceState({}, "", "/settings/accounting");
        } catch (err: any) {
          setErrorMsg(err.message || "Failed to connect Zoho Books");
        }
      })();
    }
  }, []);

  const currentConnection = connections.find(c => c.company_id === selectedCompany);

  const handleConnectZoho = async () => {
    if (!selectedCompany) return;
    setErrorMsg("");
    try {
      const { auth_url } = await getZohoAuthUrl(selectedCompany);
      window.location.href = auth_url;
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to get auth URL");
    }
  };

  const handleConnectTally = async () => {
    if (!selectedCompany || !tallyCompany.trim()) {
      setErrorMsg("Please enter Tally company name");
      return;
    }
    setErrorMsg("");
    try {
      await connectTally({
        company_id: selectedCompany,
        host: tallyHost,
        port: parseInt(tallyPort),
        company_name: tallyCompany,
      });
      setSuccessMsg("Tally Prime connected!");
      setConnectMode("");
      const conns = await getAccountingConnections();
      setConnections(conns);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to connect Tally");
    }
  };

  const handleDisconnect = async () => {
    if (!selectedCompany) return;
    try {
      await disconnectAccounting(selectedCompany);
      setSuccessMsg("Accounting platform disconnected");
      const conns = await getAccountingConnections();
      setConnections(conns);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to disconnect");
    }
  };

  const handleSync = async () => {
    if (!selectedCompany) return;
    setSyncing(true);
    setErrorMsg("");
    try {
      await syncAccountingData(selectedCompany);
      setSuccessMsg("Data synced successfully!");
      const conns = await getAccountingConnections();
      setConnections(conns);
    } catch (err: any) {
      setErrorMsg(err.message || "Sync failed");
    } finally {
      setSyncing(false);
    }
  };

  if (authLoading || !user) {
    return (
      <div className="min-h-screen bg-[var(--color-bg-primary)] flex items-center justify-center">
        <div className="text-[var(--color-text-secondary)]">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--color-bg-primary)]">
      <header className="border-b border-[var(--color-border)] bg-[var(--color-bg-secondary)]">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <Link href="/dashboard" className="text-[var(--color-text-muted)] text-sm hover:text-[var(--color-text-secondary)] transition">
            &larr; Back to Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)] mt-1">Accounting Integration</h1>
          <p className="text-[var(--color-text-secondary)] text-sm mt-1">
            Connect your accounting software for automated compliance filing
          </p>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Messages */}
        {successMsg && (
          <div className="bg-[var(--color-success-light)] border border-[var(--color-success)]/30 text-[var(--color-success)] px-4 py-3 rounded-lg text-sm mb-6">
            {successMsg}
          </div>
        )}
        {errorMsg && (
          <div className="bg-[var(--color-error-light)] border border-[var(--color-error)]/30 text-[var(--color-error)] px-4 py-3 rounded-lg text-sm mb-6">
            {errorMsg}
          </div>
        )}

        {/* Company selector */}
        {companies.length > 0 && (
          <div className="mb-8">
            <label className="text-sm text-[var(--color-text-secondary)] block mb-2">Select Company</label>
            <select
              value={selectedCompany}
              onChange={e => { setSelectedCompany(Number(e.target.value)); setConnectMode(""); }}
              className="bg-[var(--color-bg-input)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg px-4 py-2.5 w-full max-w-md"
            >
              {companies.map(c => (
                <option key={c.id} value={c.id}>
                  {c.approved_name || c.proposed_names?.[0] || `Company #${c.id}`}
                </option>
              ))}
            </select>
          </div>
        )}

        {loading ? (
          <div className="text-center py-16 text-[var(--color-text-muted)]">Loading...</div>
        ) : currentConnection && currentConnection.status === "connected" ? (
          /* ─── Connected State ─── */
          <div className="space-y-6">
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">
                    {PLATFORM_LABELS[currentConnection.platform] || currentConnection.platform}
                  </h2>
                  {currentConnection.zoho_org_name && (
                    <p className="text-[var(--color-text-secondary)] text-sm">
                      Organization: {currentConnection.zoho_org_name}
                    </p>
                  )}
                  {currentConnection.tally_company_name && (
                    <p className="text-[var(--color-text-secondary)] text-sm">
                      Company: {currentConnection.tally_company_name} ({currentConnection.tally_host}:{currentConnection.tally_port})
                    </p>
                  )}
                </div>
                <span className={`text-xs px-3 py-1 rounded-full font-medium ${STATUS_STYLES[currentConnection.status]}`}>
                  {currentConnection.status}
                </span>
              </div>

              {currentConnection.last_sync_at && (
                <p className="text-[var(--color-text-muted)] text-xs mb-4">
                  Last synced: {new Date(currentConnection.last_sync_at).toLocaleString("en-IN")}
                  {currentConnection.last_sync_status && (
                    <span className={`ml-2 ${currentConnection.last_sync_status === "success" ? "text-[var(--color-success)]" : "text-[var(--color-error)]"}`}>
                      ({currentConnection.last_sync_status})
                    </span>
                  )}
                </p>
              )}

              <div className="flex gap-3">
                <button
                  onClick={handleSync}
                  disabled={syncing}
                  className="bg-[var(--color-accent-purple)] text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-[var(--color-accent-purple-light)] transition disabled:opacity-50"
                >
                  {syncing ? "Syncing..." : "Sync Now"}
                </button>
                <button
                  onClick={handleDisconnect}
                  className="bg-[var(--color-bg-secondary)] text-[var(--color-error)] px-4 py-2 rounded-lg text-sm font-medium border border-[var(--color-border)] hover:bg-[var(--color-error-light)] transition"
                >
                  Disconnect
                </button>
              </div>
            </div>

            {/* What this enables */}
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl p-6">
              <h3 className="text-sm font-semibold text-[var(--color-text-primary)] mb-3">What this enables</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {[
                  "Auto-populated GST returns from your invoices",
                  "TDS calculations from vendor payments",
                  "ITR filing with auto-generated P&L and balance sheet",
                  "Audit-ready financial statements",
                  "Bank reconciliation tracking",
                  "Real-time compliance health monitoring",
                ].map((item, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs text-[var(--color-text-secondary)]">
                    <span className="text-[var(--color-success)] mt-0.5">&#10003;</span>
                    {item}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          /* ─── Not Connected ─── */
          <div className="space-y-6">
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl p-6">
              <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mb-2">
                Connect Your Accounting Software
              </h2>
              <p className="text-[var(--color-text-secondary)] text-sm mb-6">
                Link your books of accounts for automated GST filing, ITR preparation, and compliance monitoring.
                Your data stays secure with OAuth2 read-only access.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Zoho Books */}
                <div
                  className={`border rounded-xl p-5 cursor-pointer transition ${
                    connectMode === "zoho"
                      ? "border-[var(--color-accent-purple)] bg-[var(--color-accent-purple)]/5"
                      : "border-[var(--color-border)] hover:border-[var(--color-accent-purple)]/30"
                  }`}
                  onClick={() => setConnectMode("zoho")}
                >
                  <h3 className="font-semibold text-[var(--color-text-primary)] mb-1">Zoho Books</h3>
                  <p className="text-[var(--color-text-muted)] text-xs mb-3">
                    Most popular for Indian SMEs. Full API access for invoices, bills, bank transactions, and reports.
                  </p>
                  <span className="text-[var(--color-success)] text-[10px] font-semibold uppercase bg-[var(--color-success-light)] px-2 py-0.5 rounded-full">
                    Recommended
                  </span>
                </div>

                {/* Tally Prime */}
                <div
                  className={`border rounded-xl p-5 cursor-pointer transition ${
                    connectMode === "tally"
                      ? "border-[var(--color-accent-purple)] bg-[var(--color-accent-purple)]/5"
                      : "border-[var(--color-border)] hover:border-[var(--color-accent-purple)]/30"
                  }`}
                  onClick={() => setConnectMode("tally")}
                >
                  <h3 className="font-semibold text-[var(--color-text-primary)] mb-1">Tally Prime</h3>
                  <p className="text-[var(--color-text-muted)] text-xs mb-3">
                    India&#39;s most-used accounting software. Connects via local HTTP API on your network.
                  </p>
                  <span className="text-[var(--color-text-muted)] text-[10px] font-semibold uppercase bg-[var(--color-bg-secondary)] px-2 py-0.5 rounded-full">
                    Local Network
                  </span>
                </div>
              </div>
            </div>

            {/* Connect actions */}
            {connectMode === "zoho" && (
              <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl p-6">
                <h3 className="font-semibold text-[var(--color-text-primary)] mb-2">Connect Zoho Books</h3>
                <p className="text-[var(--color-text-secondary)] text-sm mb-4">
                  You&#39;ll be redirected to Zoho to authorize read access to your books.
                  We never modify your accounting data.
                </p>
                <button
                  onClick={handleConnectZoho}
                  className="bg-[var(--color-accent-purple)] text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-[var(--color-accent-purple-light)] transition"
                >
                  Connect with Zoho Books
                </button>
              </div>
            )}

            {connectMode === "tally" && (
              <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl p-6">
                <h3 className="font-semibold text-[var(--color-text-primary)] mb-4">Connect Tally Prime</h3>
                <div className="space-y-4 max-w-md">
                  <div>
                    <label className="text-sm text-[var(--color-text-secondary)] block mb-1">Tally Company Name</label>
                    <input
                      type="text"
                      value={tallyCompany}
                      onChange={e => setTallyCompany(e.target.value)}
                      placeholder="My Company Ltd"
                      className="w-full bg-[var(--color-bg-input)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg px-3 py-2 text-sm"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="text-sm text-[var(--color-text-secondary)] block mb-1">Host</label>
                      <input
                        type="text"
                        value={tallyHost}
                        onChange={e => setTallyHost(e.target.value)}
                        className="w-full bg-[var(--color-bg-input)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg px-3 py-2 text-sm"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-[var(--color-text-secondary)] block mb-1">Port</label>
                      <input
                        type="text"
                        value={tallyPort}
                        onChange={e => setTallyPort(e.target.value)}
                        className="w-full bg-[var(--color-bg-input)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg px-3 py-2 text-sm"
                      />
                    </div>
                  </div>
                  <button
                    onClick={handleConnectTally}
                    className="bg-[var(--color-accent-purple)] text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-[var(--color-accent-purple-light)] transition"
                  >
                    Connect Tally Prime
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
