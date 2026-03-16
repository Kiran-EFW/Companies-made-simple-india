"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { getCADashboardSummary, getCACompanies } from "@/lib/api";

export default function CADashboardPage() {
  const router = useRouter();
  const { user, loading: authLoading, logout } = useAuth();
  const [summary, setSummary] = useState<any>(null);
  const [companies, setCompanies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.push("/login");
      return;
    }
    if (user.role !== "ca_lead" && user.role !== "cs_lead") {
      router.push("/dashboard");
      return;
    }

    async function load() {
      try {
        const [summaryData, companiesData] = await Promise.all([
          getCADashboardSummary(),
          getCACompanies(),
        ]);
        setSummary(summaryData);
        setCompanies(Array.isArray(companiesData) ? companiesData : []);
      } catch (err: any) {
        setError(err.message || "Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [user, authLoading, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">A</span>
            </div>
            <span className="text-xl font-semibold text-gray-900">Anvils</span>
            <span className="text-sm text-gray-500 ml-2">CA Portal</span>
          </div>
          <div className="flex items-center gap-4">
            {user && (
              <span className="text-sm text-gray-600">{user.full_name}</span>
            )}
            <button
              onClick={() => { logout(); router.push("/login"); }}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Log Out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">CA Dashboard</h1>

        {/* Summary cards */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <p className="text-sm text-gray-500">Companies</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{summary?.total_companies || 0}</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <p className="text-sm text-gray-500">Pending Tasks</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{summary?.pending_tasks || 0}</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <p className="text-sm text-gray-500">Overdue</p>
            <p className="text-2xl font-bold text-red-600 mt-1">{summary?.overdue_tasks || 0}</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <p className="text-sm text-gray-500">Upcoming</p>
            <p className="text-2xl font-bold text-blue-600 mt-1">{summary?.upcoming_tasks || 0}</p>
          </div>
        </div>

        {/* Company list */}
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Assigned Companies</h2>
        {companies.length === 0 ? (
          <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-500">
            No companies assigned yet. Ask your clients to invite you from their dashboard.
          </div>
        ) : (
          <div className="space-y-3">
            {companies.map((c: any) => (
              <button
                key={c.id}
                onClick={() => router.push(`/ca-dashboard/company/${c.id}`)}
                className="w-full bg-white rounded-lg border border-gray-200 p-5 text-left hover:border-blue-400 hover:shadow-sm transition-all flex items-center justify-between"
              >
                <div>
                  <h3 className="font-semibold text-gray-900">{c.name}</h3>
                  <div className="flex gap-3 mt-1 text-sm text-gray-500">
                    {c.entity_type && <span className="capitalize">{c.entity_type.replace("_", " ")}</span>}
                    {c.cin && <span>CIN: {c.cin}</span>}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {c.pending_tasks > 0 && (
                    <span className="bg-orange-100 text-orange-700 px-2.5 py-1 rounded-full text-xs font-medium">
                      {c.pending_tasks} pending
                    </span>
                  )}
                  <span className="text-gray-400">&rarr;</span>
                </div>
              </button>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
