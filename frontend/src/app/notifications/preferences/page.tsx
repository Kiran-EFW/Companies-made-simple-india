"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { getNotificationPreferences, updateNotificationPreferences } from "@/lib/api";
import Link from "next/link";

interface Preferences {
  email_enabled: boolean;
  sms_enabled: boolean;
  whatsapp_enabled: boolean;
  in_app_enabled: boolean;
  status_updates: boolean;
  payment_alerts: boolean;
  compliance_reminders: boolean;
  marketing: boolean;
}

const DEFAULT_PREFS: Preferences = {
  email_enabled: true,
  sms_enabled: false,
  whatsapp_enabled: true,
  in_app_enabled: true,
  status_updates: true,
  payment_alerts: true,
  compliance_reminders: true,
  marketing: false,
};

function Toggle({ checked, onChange, label, description }: { checked: boolean; onChange: (val: boolean) => void; label: string; description?: string }) {
  return (
    <div className="flex items-center justify-between py-4 border-b" style={{ borderColor: "var(--color-border)" }}>
      <div>
        <p className="text-sm font-medium text-white">{label}</p>
        {description && <p className="text-xs text-gray-500 mt-0.5">{description}</p>}
      </div>
      <button
        onClick={() => onChange(!checked)}
        className={`relative w-11 h-6 rounded-full transition-colors ${
          checked ? "bg-purple-600" : "bg-gray-700"
        }`}
      >
        <span
          className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white transition-transform ${
            checked ? "translate-x-5" : "translate-x-0"
          }`}
        />
      </button>
    </div>
  );
}

export default function NotificationPreferencesPage() {
  const { user, loading: authLoading } = useAuth();
  const [preferences, setPreferences] = useState<Preferences>(DEFAULT_PREFS);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (authLoading) return;
    if (!user) return;

    const fetchPrefs = async () => {
      try {
        const data = await getNotificationPreferences();
        setPreferences({ ...DEFAULT_PREFS, ...data });
      } catch {
        // Use defaults
      } finally {
        setLoading(false);
      }
    };
    fetchPrefs();
  }, [user, authLoading]);

  const updatePref = (key: keyof Preferences, value: boolean) => {
    setPreferences((prev) => ({ ...prev, [key]: value }));
    setSaved(false);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateNotificationPreferences(preferences);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error("Failed to save preferences:", err);
      alert("Failed to save preferences. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center glow-bg">
        <div className="animate-pulse text-gray-500">Loading preferences...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen glow-bg">
      {/* Nav */}
      <nav className="glass-card sticky top-0 z-50 rounded-none border-t-0 border-x-0 border-b">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/dashboard" className="flex items-center gap-2">
            <span className="text-xl">&#9889;</span>
            <span className="font-bold hidden md:block" style={{ fontFamily: "var(--font-display)" }}>CMS Prime</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/notifications" className="text-xs font-medium text-gray-400 hover:text-purple-400 transition-colors">
              Notifications
            </Link>
            <Link href="/profile" className="text-xs font-medium text-gray-400 hover:text-purple-400 transition-colors">
              Profile
            </Link>
          </div>
        </div>
      </nav>

      <div className="max-w-3xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8 animate-fade-in-up">
          <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>Notification Preferences</h1>
          <p className="text-sm border-l-2 pl-3 border-purple-500" style={{ color: "var(--color-text-secondary)" }}>
            Control how and when you receive notifications.
          </p>
        </div>

        {/* Delivery Channels */}
        <div className="glass-card p-6 mb-6 animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
          <h2 className="text-lg font-bold mb-1">Delivery Channels</h2>
          <p className="text-xs text-gray-500 mb-4">Choose how you want to receive notifications.</p>

          <Toggle
            checked={preferences.email_enabled}
            onChange={(v) => updatePref("email_enabled", v)}
            label="Email"
            description="Receive notifications via email"
          />
          <Toggle
            checked={preferences.sms_enabled}
            onChange={(v) => updatePref("sms_enabled", v)}
            label="SMS"
            description="Receive notifications via text message"
          />
          <Toggle
            checked={preferences.whatsapp_enabled}
            onChange={(v) => updatePref("whatsapp_enabled", v)}
            label="WhatsApp"
            description="Receive notifications via WhatsApp"
          />
          <Toggle
            checked={preferences.in_app_enabled}
            onChange={(v) => updatePref("in_app_enabled", v)}
            label="In-App"
            description="Show notifications in the app bell icon"
          />
        </div>

        {/* Notification Types */}
        <div className="glass-card p-6 mb-6 animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
          <h2 className="text-lg font-bold mb-1">Notification Types</h2>
          <p className="text-xs text-gray-500 mb-4">Choose which types of notifications you want to receive.</p>

          <Toggle
            checked={preferences.status_updates}
            onChange={(v) => updatePref("status_updates", v)}
            label="Status Updates"
            description="Incorporation progress, document verifications, name approvals"
          />
          <Toggle
            checked={preferences.payment_alerts}
            onChange={(v) => updatePref("payment_alerts", v)}
            label="Payment Alerts"
            description="Payment confirmations, invoices, reminders"
          />
          <Toggle
            checked={preferences.compliance_reminders}
            onChange={(v) => updatePref("compliance_reminders", v)}
            label="Compliance Reminders"
            description="Filing deadlines, annual compliance, INC-20A reminders"
          />
          <Toggle
            checked={preferences.marketing}
            onChange={(v) => updatePref("marketing", v)}
            label="Marketing & Updates"
            description="New features, offers, and company updates"
          />
        </div>

        {/* Save Button */}
        <div className="flex items-center gap-4 animate-fade-in-up" style={{ animationDelay: "0.3s" }}>
          <button
            onClick={handleSave}
            disabled={saving}
            className="btn-primary text-sm !py-3 !px-8 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save Preferences"}
          </button>
          {saved && (
            <span className="text-sm text-emerald-400 font-medium animate-fade-in-up">
              Preferences saved successfully!
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
