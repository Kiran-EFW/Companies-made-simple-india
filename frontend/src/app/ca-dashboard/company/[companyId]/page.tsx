"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { getCACompanyCompliance, getCACompanyDocuments, markFilingDone } from "@/lib/api";

type Tab = "compliance" | "documents";

export default function CACompanyDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user, loading: authLoading, logout } = useAuth();
  const companyId = Number(params.companyId);

  const [activeTab, setActiveTab] = useState<Tab>("compliance");
  const [tasks, setTasks] = useState<any[]>([]);
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Mark-as-done modal state
  const [selectedTask, setSelectedTask] = useState<any>(null);
  const [filingRef, setFilingRef] = useState("");
  const [filingNotes, setFilingNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);

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
        const [tasksData, docsData] = await Promise.all([
          getCACompanyCompliance(companyId),
          getCACompanyDocuments(companyId),
        ]);
        setTasks(Array.isArray(tasksData) ? tasksData : []);
        setDocuments(Array.isArray(docsData) ? docsData : []);
      } catch {
        // error handled by empty arrays
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [companyId, user, authLoading, router]);

  const handleMarkDone = async () => {
    if (!selectedTask) return;
    setSubmitting(true);
    try {
      await markFilingDone(companyId, selectedTask.id, {
        filing_reference: filingRef,
        notes: filingNotes,
      });
      // Update local state
      setTasks(tasks.map((t) =>
        t.id === selectedTask.id
          ? { ...t, status: "completed", filing_reference: filingRef }
          : t
      ));
      setSelectedTask(null);
      setFilingRef("");
      setFilingNotes("");
    } catch {
      // ignore
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  const statusColor = (status: string) => {
    switch (status) {
      case "completed": return "bg-green-100 text-green-700";
      case "overdue": return "bg-red-100 text-red-700";
      case "upcoming": return "bg-blue-100 text-blue-700";
      default: return "bg-gray-100 text-gray-600";
    }
  };

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
        <button
          onClick={() => router.push("/ca-dashboard")}
          className="text-sm text-blue-600 hover:underline mb-4 inline-block"
        >
          &larr; Back to Dashboard
        </button>

        <h1 className="text-2xl font-bold text-gray-900 mb-6">Company Compliance</h1>

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="flex gap-6">
            {(["compliance", "documents"] as Tab[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`pb-3 text-sm font-medium border-b-2 transition-colors capitalize ${
                  activeTab === tab
                    ? "border-blue-600 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                {tab}
              </button>
            ))}
          </nav>
        </div>

        {activeTab === "compliance" && (
          <div className="space-y-3">
            {tasks.length === 0 ? (
              <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-500">
                No compliance tasks found.
              </div>
            ) : (
              tasks.map((t: any) => (
                <div key={t.id} className="bg-white rounded-lg border border-gray-200 p-5">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900">{t.title}</h3>
                      <div className="flex gap-3 mt-1 text-sm text-gray-500">
                        {t.filing_form && <span>Form: {t.filing_form}</span>}
                        {t.due_date && <span>Due: {t.due_date.split("T")[0]}</span>}
                      </div>
                      {t.filing_reference && (
                        <p className="text-sm text-green-600 mt-1">Ref: {t.filing_reference}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${statusColor(t.status)}`}>
                        {t.status}
                      </span>
                      {t.status !== "completed" && (
                        <button
                          onClick={() => setSelectedTask(t)}
                          className="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
                        >
                          Mark Done
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "documents" && (
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            {documents.length === 0 ? (
              <div className="p-8 text-center text-gray-500">No documents found.</div>
            ) : (
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Document</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Type</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((d: any) => (
                    <tr key={d.id} className="border-b border-gray-100">
                      <td className="px-4 py-3">{d.name}</td>
                      <td className="px-4 py-3">{d.doc_type}</td>
                      <td className="px-4 py-3">{d.status}</td>
                      <td className="px-4 py-3">{d.uploaded_at?.split("T")[0]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {/* Mark Done Modal */}
        {selectedTask && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md mx-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Mark Filing Complete
              </h3>
              <p className="text-sm text-gray-600 mb-4">{selectedTask.title}</p>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Filing Reference / SRN
                </label>
                <input
                  type="text"
                  value={filingRef}
                  onChange={(e) => setFilingRef(e.target.value)}
                  placeholder="e.g. SRN: A12345678"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notes (optional)
                </label>
                <textarea
                  value={filingNotes}
                  onChange={(e) => setFilingNotes(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => { setSelectedTask(null); setFilingRef(""); setFilingNotes(""); }}
                  className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleMarkDone}
                  disabled={submitting}
                  className="flex-1 bg-green-600 text-white py-2.5 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 transition-colors"
                >
                  {submitting ? "Saving..." : "Complete Filing"}
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
