"use client";

import { useEffect, useState, useRef } from "react";
import { useAuth } from "@/lib/auth-context";
import { getCompanies, uploadDocument, getCompanyLogs } from "@/lib/api";
import Link from "next/link";
import ChatWidget from "@/components/chat-widget";
import NotificationBell from "@/components/notification-bell";

const PIPELINE_STEPS = [
  { key: "draft_to_payment", label: "Draft & Payment", statuses: ["draft", "entity_selected", "payment_pending", "payment_completed"] },
  { key: "documents", label: "Document Verification", statuses: ["documents_pending", "documents_uploaded", "documents_verified"] },
  { key: "name_reservation", label: "Name Approval", statuses: ["name_pending", "name_reserved", "name_rejected"] },
  { key: "mca_filing", label: "MCA Processing", statuses: ["dsc_in_progress", "dsc_obtained", "filing_drafted", "filing_under_review", "filing_submitted", "mca_processing", "mca_query"] },
  { key: "setup", label: "Post Setup", statuses: ["incorporated", "bank_account_pending", "bank_account_opened", "inc20a_pending", "fully_setup"] }
];

export default function DashboardPage() {
  const { user, loading: authLoading, logout } = useAuth();
  const [companies, setCompanies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploadingId, setUploadingId] = useState<number | null>(null);
  const [liveLogs, setLiveLogs] = useState<Record<number, any[]>>({});
  const [isRefreshing, setIsRefreshing] = useState(false);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (authLoading) return;
    if (!user) return; // Router will redirect due to auth context

    const fetchData = async () => {
      try {
        const comps = await getCompanies();
        setCompanies(comps);
      } catch (err) {
        console.error("Failed to fetch companies:", err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [user, authLoading]);

  // Optimized Polling for Live Agent Logs
  useEffect(() => {
    if (companies.length === 0) return;
    
    const needsPolling = companies.some(c => 
      !["incorporated", "draft"].includes(c.status)
    );

    if (!needsPolling) return;

    const runPolling = async () => {
      if (document.visibilityState !== "visible") return;
      
      setIsRefreshing(true);
      const activeComps = companies.filter(c => !["incorporated", "draft"].includes(c.status));
      
      try {
        const logsPromises = activeComps.map(async (c) => {
          try {
            const logs = await getCompanyLogs(c.id);
            return { id: c.id, logs };
          } catch (e) {
            return { id: c.id, logs: [] };
          }
        });
        
        const results = await Promise.all(logsPromises);
        setLiveLogs(prev => {
          const next = { ...prev };
          results.forEach(r => { next[r.id] = r.logs; });
          return next;
        });
        
        const updatedComps = await getCompanies();
        setCompanies(updatedComps);
      } catch (e) {
        console.error("Polling error", e);
      } finally {
        setTimeout(() => setIsRefreshing(false), 500);
      }
    };

    pollingRef.current = setInterval(runPolling, 5000); // More conservative 5s interval

    const handleVisibility = () => {
      if (document.visibilityState === "hidden") {
        if (pollingRef.current) clearInterval(pollingRef.current);
      } else {
        pollingRef.current = setInterval(runPolling, 5000);
      }
    };

    document.addEventListener("visibilitychange", handleVisibility);
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, [companies.length]); // Only reset if number of companies changes

  // Determine which step group a status falls into to visually light up the pipeline
  const getStepIndex = (status: string) => {
    for (let i = 0; i < PIPELINE_STEPS.length; i++) {
        if (PIPELINE_STEPS[i].statuses.includes(status)) return i;
    }
    return 0;
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center glow-bg">
        <div className="animate-pulse-glow w-16 h-16 rounded-full bg-purple-500/20 flex items-center justify-center">
           <span className="text-2xl">⚡</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen glow-bg">
      <nav className="glass-card sticky top-0 z-50 rounded-none border-t-0 border-x-0 border-b">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <Link href="/dashboard" className="flex items-center gap-2">
              <span className="text-xl">⚡</span>
              <span className="font-bold hidden md:block" style={{ fontFamily: "var(--font-display)" }}>CMS Prime</span>
            </Link>
            
            <div className="flex items-center gap-6">
              {isRefreshing && (
                <div className="flex items-center gap-2 text-[10px] font-mono text-purple-400 animate-pulse">
                  <span className="w-1.5 h-1.5 bg-purple-500 rounded-full"></span>
                  LIVE SYNCING
                </div>
              )}
              {user && (
                <div className="flex items-center gap-4">
                  <NotificationBell />
                  <Link
                    href="/documents"
                    className="text-xs font-medium transition-colors hover:text-purple-400"
                    style={{ color: "var(--color-text-secondary)" }}
                  >
                    Legal Docs
                  </Link>
                  <Link
                    href="/compare"
                    className="text-xs font-medium transition-colors hover:text-purple-400"
                    style={{ color: "var(--color-text-secondary)" }}
                  >
                    Compare
                  </Link>
                  <Link
                    href="/profile"
                    className="text-xs font-medium transition-colors hover:text-purple-400"
                    style={{ color: "var(--color-text-secondary)" }}
                  >
                    Profile
                  </Link>
                  <div className="text-right hidden sm:block">
                    <p className="text-sm font-medium leading-none">{user.full_name}</p>
                    <p className="text-[10px] text-gray-400 mt-1">Founder Account</p>
                  </div>
                  <button onClick={logout} className="text-xs p-2 rounded hover:bg-white/5 transition-colors" style={{ color: "var(--color-text-muted)" }}>
                    Log Out
                  </button>
                </div>
              )}
            </div>
          </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex justify-between items-end mb-8 animate-fade-in-up">
           <div>
              <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>Your Companies</h1>
              <p className="text-sm border-l-2 pl-3 border-purple-500" style={{ color: "var(--color-text-secondary)" }}>
                Track the live status of your incorporations.
              </p>
           </div>
           {companies.length > 0 && (
             <Link href="/pricing" className="btn-secondary text-sm !py-2 !px-4 hidden md:block">
               + Start New
             </Link>
           )}
        </div>

        {companies.length === 0 ? (
          <div className="glass-card p-12 text-center animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
             <div className="text-5xl mb-4">🚀</div>
             <h2 className="text-2xl font-bold mb-2">No active incorporations</h2>
             <p className="mb-8 max-w-sm mx-auto" style={{ color: "var(--color-text-secondary)" }}>
               You are one step away from forming your dream company. Pricing is transparent, and AI helps us move 10x faster.
             </p>
             <Link href="/pricing" className="btn-primary">Calculate Pricing and Start →</Link>
          </div>
        ) : (
          <div className="space-y-6">
            {companies.map((comp, idx) => {
              const currentStepIndex = getStepIndex(comp.status);
              const displayName = comp.approved_name || (comp.proposed_names && comp.proposed_names[0]) || "Draft Company";
              const isPending = comp.status.includes('pending') || comp.status === 'draft';
              
              return (
                <div key={comp.id} className="glass-card p-6 animate-fade-in-up" style={{ animationDelay: `${idx * 0.1}s` }}>
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
                     <div>
                       <div className="flex items-center gap-3 mb-1">
                         <h2 className="text-xl font-bold">{displayName}</h2>
                         <span className="text-xs font-semibold px-2 py-0.5 rounded-full" style={{ background: "rgba(16, 185, 129, 0.1)", color: "var(--color-accent-emerald-light)" }}>
                           {comp.entity_type.replace(/_/g, " ").toUpperCase()}
                         </span>
                       </div>
                       <p className="text-xs font-mono" style={{ color: "var(--color-text-muted)" }}>
                         ID: #{comp.id} • STATE: {comp.state.toUpperCase()} • PKG: {comp.plan_tier.toUpperCase()}
                       </p>
                     </div>
                     
                     <div className="mt-4 md:mt-0 text-right">
                       <span className={`text-xs font-semibold px-3 py-1 rounded-full border ${isPending ? 'border-amber-500/30 text-amber-500 bg-amber-500/10' : 'border-purple-500/30 text-purple-400 bg-purple-500/10'}`}>
                         {comp.status.replace(/_/g, " ").toUpperCase()}
                       </span>
                     </div>
                  </div>

                  {/* Status Pipeline Visualizer */}
                  <div className="relative pt-8 pb-4">
                     <div className="absolute top-10 left-0 right-0 h-1 bg-gray-800 rounded-full" style={{ background: "var(--color-border)" }} />
                     
                     <div className="relative flex justify-between z-10 w-full">
                       {PIPELINE_STEPS.map((step, sIdx) => {
                         const isActive = sIdx === currentStepIndex;
                         const isPast = sIdx < currentStepIndex;
                         
                         return (
                           <div key={step.key} className="flex flex-col items-center flex-1 max-w-[20%] relative group">
                             <div 
                               className={`w-6 h-6 rounded-full border-4 mb-2 transition-colors
                                ${isPast ? "bg-emerald-500 border-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]" 
                                  : isActive ? "bg-purple-500 border-purple-200 animate-pulse shadow-[0_0_15px_rgba(168,85,247,0.6)]" 
                                  : "bg-gray-800 border-gray-700"}`}
                               style={(!isPast && !isActive) ? { background: "var(--color-bg-card)", borderColor: "var(--color-border)" } : {}}
                             />
                             <span className={`text-[10px] md:text-xs text-center font-medium ${isActive || isPast ? "text-white" : "text-gray-500"}`} style={(!isActive && !isPast) ? { color: "var(--color-text-muted)" } : {}}>
                               {step.label}
                             </span>
                           </div>
                         );
                       })}
                     </div>
                  </div>
                  
                  {/* Next Step CTA */}
                  {comp.status === "payment_completed" && (
                    <div className="mt-6 p-4 rounded-xl border flex justify-between items-center" style={{ background: "rgba(139, 92, 246, 0.05)", borderColor: "rgba(139, 92, 246, 0.2)" }}>
                       <div>
                         <h4 className="text-sm font-semibold mb-1">Upload Documents</h4>
                         <p className="text-xs" style={{ color: "var(--color-text-secondary)" }}>Your payment was successful. Please upload PAN/Aadhaar for the {comp.num_directors} directors.</p>
                       </div>
                       <label className={`btn-primary text-sm !py-2 !px-4 cursor-pointer ${uploadingId === comp.id ? 'opacity-50 cursor-not-allowed' : ''}`}>
                         {uploadingId === comp.id ? 'Uploading...' : 'Upload PAN →'}
                         <input 
                           type="file" 
                           className="hidden" 
                           accept="image/*,.pdf"
                           disabled={uploadingId === comp.id}
                           onChange={async (e) => {
                             const file = e.target.files?.[0];
                             if (!file) return;
                             
                             setUploadingId(comp.id);
                             try {
                               await uploadDocument(comp.id, "pan_card", file);
                               const updatedComps = await getCompanies();
                               setCompanies(updatedComps);
                             } catch (err) {
                               console.error("Upload failed", err);
                               alert("Document upload failed.");
                             } finally {
                               setUploadingId(null);
                             }
                           }}
                         />
                       </label>
                    </div>
                  )}

                  {/* Generated Documents Section */}
                  {comp.documents && comp.documents.some((d: any) => {
                    if (!d.extracted_data) return false;
                    try {
                      const parsed = JSON.parse(d.extracted_data);
                      return parsed.is_generated;
                    } catch (e) { return false; }
                  }) && (
                    <div className="mt-6">
                      <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
                        <span className="text-emerald-400 text-lg">📄</span> 
                        {comp.status === 'incorporated' ? 'Official Company Documents' : 'Generated Legal Drafts (Pending Submission)'}
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {comp.documents.filter((d: any) => {
                          if (!d.extracted_data) return false;
                          try {
                            const parsed = JSON.parse(d.extracted_data);
                            return parsed.is_generated;
                          } catch (e) { return false; }
                        }).map((doc: any) => {
                          const parsed = JSON.parse(doc.extracted_data);
                          const isCOI = parsed.display_name?.includes("COI") || parsed.display_name?.includes("Incorporation");
                          return (
                            <div key={doc.id} className={`p-3 rounded-lg border ${isCOI ? 'border-emerald-500/30 bg-emerald-500/5' : 'border-gray-800 bg-gray-900/30'} flex justify-between items-center group`}>
                               <div>
                                 <p className={`text-xs font-medium ${isCOI ? 'text-emerald-400' : 'text-white'}`}>{parsed.display_name || doc.original_filename}</p>
                                 <p className="text-[10px] text-gray-500 uppercase">{isCOI ? 'Certificate' : 'PDF Draft'}</p>
                               </div>
                               <a 
                                 href="#" 
                                 onClick={(e) => {
                                   e.preventDefault();
                                   const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
                                   const token = localStorage.getItem("access_token");
                                   window.open(`${baseUrl}/documents/${doc.id}/download?token=${token}`, "_blank");
                                 }}
                                 className="text-purple-400 hover:text-purple-300 text-xs font-bold opacity-0 group-hover:opacity-100 transition-opacity"
                               >
                                 Download
                               </a>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* Post-Incorporation Setup Section */}
                  {comp.status === "incorporated" && (
                     <div className="mt-6 p-6 rounded-xl border border-purple-500/20 bg-purple-500/5">
                        <div className="flex items-center gap-3 mb-4">
                           <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center text-xl">🎉</div>
                           <div>
                              <h3 className="font-bold text-white">Post-Incorporation Setup</h3>
                              <p className="text-xs text-gray-400">Your company is live! Complete these steps to start transacting.</p>
                           </div>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                           <div className="p-4 rounded-lg bg-black/40 border border-gray-800 flex justify-between items-center group hover:border-purple-500/30 transition-colors">
                              <div>
                                 <h4 className="text-sm font-semibold">Business Bank Account</h4>
                                 <p className="text-[10px] text-gray-500">Partnered with Mercury, ICICI & HDFC</p>
                              </div>
                              <Link href="/dashboard/compliance" className="text-xs font-bold text-purple-400 group-hover:underline">Get Started &#8594;</Link>
                           </div>
                           <div className="p-4 rounded-lg bg-black/40 border border-gray-800 flex justify-between items-center group hover:border-purple-500/30 transition-colors">
                              <div>
                                 <h4 className="text-sm font-semibold">INC-20A Commencement</h4>
                                 <p className="text-[10px] text-gray-500">Mandatory filing within 180 days</p>
                              </div>
                              <button className="text-xs font-bold text-gray-500 cursor-not-allowed">Coming Soon</button>
                           </div>
                           <div className="p-4 rounded-lg bg-black/40 border border-gray-800 flex justify-between items-center group hover:border-purple-500/30 transition-colors">
                              <div>
                                 <h4 className="text-sm font-semibold">Statutory Registers</h4>
                                 <p className="text-[10px] text-gray-500">Mandatory registers under Companies Act 2013</p>
                              </div>
                              <Link href="/dashboard/registers" className="text-xs font-bold text-purple-400 group-hover:underline">Manage &#8594;</Link>
                           </div>
                           <div className="p-4 rounded-lg bg-black/40 border border-gray-800 flex justify-between items-center group hover:border-purple-500/30 transition-colors">
                              <div>
                                 <h4 className="text-sm font-semibold">Meeting Management</h4>
                                 <p className="text-[10px] text-gray-500">Board &amp; Shareholder meetings, minutes &amp; notices</p>
                              </div>
                              <Link href="/dashboard/meetings" className="text-xs font-bold text-purple-400 group-hover:underline">Manage &#8594;</Link>
                           </div>
                           <div className="p-4 rounded-lg bg-black/40 border border-gray-800 flex justify-between items-center group hover:border-purple-500/30 transition-colors">
                              <div>
                                 <h4 className="text-sm font-semibold">Cap Table</h4>
                                 <p className="text-[10px] text-gray-500">Track equity, shareholders &amp; ownership</p>
                              </div>
                              <Link href="/dashboard/cap-table" className="text-xs font-bold text-purple-400 group-hover:underline">Manage &#8594;</Link>
                           </div>
                           <div className="p-4 rounded-lg bg-black/40 border border-gray-800 flex justify-between items-center group hover:border-purple-500/30 transition-colors">
                              <div>
                                 <h4 className="text-sm font-semibold">Data Room</h4>
                                 <p className="text-[10px] text-gray-500">Secure document vault with investor sharing</p>
                              </div>
                              <Link href="/dashboard/data-room" className="text-xs font-bold text-purple-400 group-hover:underline">Open &#8594;</Link>
                           </div>
                        </div>
                     </div>
                  )}

                  {/* Live Agent Terminal */}
                  {liveLogs[comp.id] && liveLogs[comp.id].length > 0 && (
                    <div className="mt-6 rounded-xl border border-gray-800 overflow-hidden bg-black/60 shadow-[0_4px_20px_rgba(0,0,0,0.5)]">
                      <div className="px-4 py-2 flex items-center justify-between border-b border-gray-800 bg-gray-900/50">
                        <div className="flex items-center gap-2">
                          <div className="flex gap-1.5">
                            <div className="w-2.5 h-2.5 rounded-full bg-red-500/80"></div>
                            <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/80"></div>
                            <div className="w-2.5 h-2.5 rounded-full bg-green-500/80"></div>
                          </div>
                          <span className="text-[10px] font-mono ml-2 text-gray-400 uppercase tracking-wider">
                            Agent Process Terminal
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-[10px] font-mono text-emerald-400 animate-pulse">
                          <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full"></span>
                          CONNECTED
                        </div>
                      </div>
                      
                      <div className="p-4 h-48 overflow-y-auto font-mono text-[11px] leading-relaxed custom-scrollbar bg-black/40">
                        <div className="space-y-1.5">
                          {liveLogs[comp.id].map((log, lIdx) => (
                            <div key={lIdx} className="flex gap-3 animate-fade-in">
                              <span className="text-gray-600 shrink-0">[{new Date(log.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'})}]</span>
                              <span className={
                                log.level === "SUCCESS" ? "text-emerald-400" : 
                                log.level === "ERROR" ? "text-rose-400" : 
                                log.level === "WARN" ? "text-amber-400" : 
                                "text-purple-300"
                              }>
                                <span className="opacity-60">{log.agent_name}:</span> {log.message}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {comp.status === "payment_pending" && (
                    <div className="mt-6 p-4 rounded-xl border flex justify-between items-center" style={{ background: "rgba(245, 158, 11, 0.05)", borderColor: "rgba(245, 158, 11, 0.2)" }}>
                       <div>
                         <h4 className="text-sm font-semibold mb-1">Complete Payment</h4>
                         <p className="text-xs" style={{ color: "var(--color-text-secondary)" }}>Secure your slot to begin the process.</p>
                       </div>
                       <Link href="/onboarding" className="btn-primary text-sm !py-2 !px-4 bg-amber-600 hover:bg-amber-500 text-white">Resume Checkout →</Link>
                    </div>
                  )}

                </div>
              );
            })}
          </div>
        )}
      </div>

      {companies.length > 0 && <ChatWidget companyId={companies[0]?.id} />}
    </div>
  );
}
