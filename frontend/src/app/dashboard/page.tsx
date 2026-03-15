"use client";

import { useEffect, useState, useRef } from "react";
import { useAuth } from "@/lib/auth-context";
import { getCompanies, uploadDocument, getCompanyLogs, getCompanyMessages, sendMessage, markMessagesRead, getUpsellItems, type UpsellItem } from "@/lib/api";
import Link from "next/link";
import ChatWidget from "@/components/chat-widget";
import NotificationBell from "@/components/notification-bell";
import Footer from "@/components/footer";

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

  // Messages state
  const [openMessageId, setOpenMessageId] = useState<number | null>(null);
  const [companyMessages, setCompanyMessages] = useState<Record<number, any[]>>({});
  const [msgContent, setMsgContent] = useState("");
  const [sendingMsg, setSendingMsg] = useState(false);
  const [msgUnread, setMsgUnread] = useState<Record<number, number>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [upsellItems, setUpsellItems] = useState<Record<number, UpsellItem[]>>({});

  useEffect(() => {
    if (authLoading) return;
    if (!user) return; // Router will redirect due to auth context

    const fetchData = async () => {
      try {
        const comps = await getCompanies();
        setCompanies(comps);
        // Load upsell items for incorporated companies
        for (const c of comps) {
          if (["incorporated", "fully_setup", "bank_account_pending", "bank_account_opened", "inc20a_pending"].includes(c.status)) {
            try {
              const items = await getUpsellItems(c.id);
              setUpsellItems(prev => ({ ...prev, [c.id]: items }));
            } catch {}
          }
        }
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

  // Load messages for a company when toggled open
  const toggleMessages = async (companyId: number) => {
    if (openMessageId === companyId) {
      setOpenMessageId(null);
      return;
    }
    setOpenMessageId(companyId);
    try {
      const data = await getCompanyMessages(companyId);
      setCompanyMessages((prev) => ({ ...prev, [companyId]: data.messages || [] }));
      setMsgUnread((prev) => ({ ...prev, [companyId]: 0 }));
      if (data.unread_count > 0) {
        await markMessagesRead(companyId);
      }
    } catch (err) {
      console.error("Failed to load messages:", err);
    }
  };

  const handleSendMsg = async (companyId: number) => {
    if (!msgContent.trim()) return;
    setSendingMsg(true);
    try {
      const newMsg = await sendMessage(companyId, msgContent);
      setMsgContent("");
      setCompanyMessages((prev) => ({
        ...prev,
        [companyId]: [...(prev[companyId] || []), newMsg],
      }));
    } catch (err) {
      console.error("Failed to send message:", err);
    } finally {
      setSendingMsg(false);
    }
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [companyMessages, openMessageId]);

  // Check for unread messages on load
  useEffect(() => {
    if (companies.length === 0) return;
    const checkUnread = async () => {
      for (const comp of companies) {
        try {
          const data = await getCompanyMessages(comp.id);
          if (data.unread_count > 0) {
            setMsgUnread((prev) => ({ ...prev, [comp.id]: data.unread_count }));
          }
        } catch {}
      }
    };
    checkUnread();
  }, [companies.length]);

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
        <div className="animate-pulse-glow w-16 h-16 rounded-full flex items-center justify-center" style={{ background: "rgba(139, 92, 246, 0.2)" }}>
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
                    href="/learn"
                    className="text-xs font-medium transition-colors hover:text-purple-400"
                    style={{ color: "var(--color-text-secondary)" }}
                  >
                    Learn
                  </Link>
                  <Link
                    href="/services"
                    className="text-xs font-medium transition-colors hover:text-purple-400"
                    style={{ color: "var(--color-text-secondary)" }}
                  >
                    Services
                  </Link>
                  <Link
                    href="/settings/accounting"
                    className="text-xs font-medium transition-colors hover:text-purple-400"
                    style={{ color: "var(--color-text-secondary)" }}
                  >
                    Accounting
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
                    <p className="text-[10px] mt-1" style={{ color: "var(--color-text-secondary)" }}>Founder Account</p>
                  </div>
                  <button onClick={logout} className="text-xs p-2 rounded transition-colors" style={{ color: "var(--color-text-muted)" }}>
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
                     <div className="absolute top-10 left-0 right-0 h-1 rounded-full" style={{ background: "var(--color-border)" }} />
                     
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
                                  : ""}`}
                               style={(!isPast && !isActive) ? { background: "var(--color-bg-card)", borderColor: "var(--color-border)" } : {}}
                             />
                             <span className="text-[10px] md:text-xs text-center font-medium" style={{ color: (isActive || isPast) ? "var(--color-text-primary)" : "var(--color-text-muted)" }}>
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
                            <div key={doc.id} className="p-3 rounded-lg border flex justify-between items-center group" style={isCOI ? { borderColor: "rgba(16, 185, 129, 0.3)", background: "rgba(16, 185, 129, 0.05)" } : { borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" }}>
                               <div>
                                 <p className="text-xs font-medium" style={{ color: isCOI ? "var(--color-success)" : "var(--color-text-primary)" }}>{parsed.display_name || doc.original_filename}</p>
                                 <p className="text-[10px] uppercase" style={{ color: "var(--color-text-muted)" }}>{isCOI ? 'Certificate' : 'PDF Draft'}</p>
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
                              <h3 className="font-bold" style={{ color: "var(--color-text-primary)" }}>Post-Incorporation Setup</h3>
                              <p className="text-xs" style={{ color: "var(--color-text-secondary)" }}>Your company is live! Complete these steps to start transacting.</p>
                           </div>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                           <div className="p-4 rounded-lg border flex justify-between items-center group hover:border-purple-500/30 transition-colors" style={{ background: "var(--color-overlay)", borderColor: "var(--color-border)" }}>
                              <div>
                                 <h4 className="text-sm font-semibold">Business Bank Account</h4>
                                 <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Partnered with Mercury, ICICI & HDFC</p>
                              </div>
                              <Link href="/dashboard/compliance" className="text-xs font-bold text-purple-400 group-hover:underline">Get Started &#8594;</Link>
                           </div>
                           <div className="p-4 rounded-lg border flex justify-between items-center group hover:border-purple-500/30 transition-colors" style={{ background: "var(--color-overlay)", borderColor: "var(--color-border)" }}>
                              <div>
                                 <h4 className="text-sm font-semibold">INC-20A Commencement</h4>
                                 <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Mandatory filing within 180 days</p>
                              </div>
                              <button className="text-xs font-bold cursor-not-allowed" style={{ color: "var(--color-text-muted)" }}>Coming Soon</button>
                           </div>
                           <div className="p-4 rounded-lg border flex justify-between items-center group hover:border-purple-500/30 transition-colors" style={{ background: "var(--color-overlay)", borderColor: "var(--color-border)" }}>
                              <div>
                                 <h4 className="text-sm font-semibold">Statutory Registers</h4>
                                 <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Mandatory registers under Companies Act 2013</p>
                              </div>
                              <Link href="/dashboard/registers" className="text-xs font-bold text-purple-400 group-hover:underline">Manage &#8594;</Link>
                           </div>
                           <div className="p-4 rounded-lg border flex justify-between items-center group hover:border-purple-500/30 transition-colors" style={{ background: "var(--color-overlay)", borderColor: "var(--color-border)" }}>
                              <div>
                                 <h4 className="text-sm font-semibold">Meeting Management</h4>
                                 <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Board &amp; Shareholder meetings, minutes &amp; notices</p>
                              </div>
                              <Link href="/dashboard/meetings" className="text-xs font-bold text-purple-400 group-hover:underline">Manage &#8594;</Link>
                           </div>
                           <div className="p-4 rounded-lg border flex justify-between items-center group hover:border-purple-500/30 transition-colors" style={{ background: "var(--color-overlay)", borderColor: "var(--color-border)" }}>
                              <div>
                                 <h4 className="text-sm font-semibold">Cap Table</h4>
                                 <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Track equity, shareholders &amp; ownership</p>
                              </div>
                              <Link href="/dashboard/cap-table" className="text-xs font-bold text-purple-400 group-hover:underline">Manage &#8594;</Link>
                           </div>
                           <div className="p-4 rounded-lg border flex justify-between items-center group hover:border-purple-500/30 transition-colors" style={{ background: "var(--color-overlay)", borderColor: "var(--color-border)" }}>
                              <div>
                                 <h4 className="text-sm font-semibold">Data Room</h4>
                                 <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Secure document vault with investor sharing</p>
                              </div>
                              <Link href="/dashboard/data-room" className="text-xs font-bold text-purple-400 group-hover:underline">Open &#8594;</Link>
                           </div>
                           <div className="p-4 rounded-lg border flex justify-between items-center group hover:border-purple-500/30 transition-colors" style={{ background: "var(--color-overlay)", borderColor: "var(--color-border)" }}>
                              <div>
                                 <h4 className="text-sm font-semibold">Accounting Integration</h4>
                                 <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Connect Zoho Books or Tally Prime for auto-filing</p>
                              </div>
                              <Link href="/settings/accounting" className="text-xs font-bold text-purple-400 group-hover:underline">Connect &#8594;</Link>
                           </div>
                           <div className="p-4 rounded-lg border flex justify-between items-center group hover:border-purple-500/30 transition-colors" style={{ background: "var(--color-overlay)", borderColor: "var(--color-border)" }}>
                              <div>
                                 <h4 className="text-sm font-semibold">GST Filing</h4>
                                 <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>GSTR-1, GSTR-3B returns &amp; deadlines</p>
                              </div>
                              <Link href="/dashboard/gst" className="text-xs font-bold text-purple-400 group-hover:underline">View &#8594;</Link>
                           </div>
                           <div className="p-4 rounded-lg border flex justify-between items-center group hover:border-purple-500/30 transition-colors" style={{ background: "var(--color-overlay)", borderColor: "var(--color-border)" }}>
                              <div>
                                 <h4 className="text-sm font-semibold">Tax Overview</h4>
                                 <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>ITR, TDS, advance tax &amp; audit pack</p>
                              </div>
                              <Link href="/dashboard/tax" className="text-xs font-bold text-purple-400 group-hover:underline">View &#8594;</Link>
                           </div>
                        </div>
                     </div>
                  )}

                  {/* Recommended Services / Upsell Panel */}
                  {upsellItems[comp.id] && upsellItems[comp.id].length > 0 && (
                    <div className="mt-6">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="text-sm font-semibold flex items-center gap-2" style={{ color: "var(--color-text-primary)" }}>
                          <span className="text-lg">🛡️</span> Recommended Next Steps
                        </h4>
                        <Link href="/services" className="text-xs font-medium text-purple-400 hover:underline">
                          View All Services &#8594;
                        </Link>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {upsellItems[comp.id].slice(0, 6).map(item => (
                          <div
                            key={item.service_key}
                            className="p-4 rounded-xl border flex flex-col justify-between transition-colors hover:border-purple-500/30"
                            style={{ background: "var(--color-overlay)", borderColor: "var(--color-border)" }}
                          >
                            <div>
                              <div className="flex items-start justify-between mb-1.5">
                                <h5 className="text-xs font-semibold leading-tight" style={{ color: "var(--color-text-primary)" }}>{item.name}</h5>
                                {item.badge && (
                                  <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-full uppercase ml-2 shrink-0 ${
                                    item.badge === "mandatory" ? "text-rose-400 bg-rose-500/10" :
                                    item.badge === "popular" ? "text-purple-400 bg-purple-500/10" :
                                    "text-emerald-400 bg-emerald-500/10"
                                  }`}>{item.badge}</span>
                                )}
                              </div>
                              <p className="text-[10px] leading-relaxed mb-2" style={{ color: "var(--color-text-muted)" }}>{item.reason}</p>
                            </div>
                            <div className="flex items-center justify-between pt-2" style={{ borderTop: "1px solid var(--color-border)" }}>
                              <span className="text-sm font-bold" style={{ color: "var(--color-text-primary)" }}>
                                Rs {item.total.toLocaleString("en-IN")}
                              </span>
                              <Link
                                href={`/services?highlight=${item.service_key}`}
                                className="text-[10px] font-bold px-3 py-1.5 rounded-lg transition-colors"
                                style={{ background: item.urgency === "high" ? "var(--color-accent-purple)" : "var(--color-bg-secondary)", color: item.urgency === "high" ? "#fff" : "var(--color-text-primary)" }}
                              >
                                {item.urgency === "high" ? "Get Started" : "Learn More"}
                              </Link>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Live Agent Terminal */}
                  {liveLogs[comp.id] && liveLogs[comp.id].length > 0 && (
                    <div className="mt-6 rounded-xl border overflow-hidden shadow-[0_4px_20px_rgba(0,0,0,0.5)]" style={{ borderColor: "var(--color-border)", background: "var(--color-overlay)" }}>
                      <div className="px-4 py-2 flex items-center justify-between border-b" style={{ borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" }}>
                        <div className="flex items-center gap-2">
                          <div className="flex gap-1.5">
                            <div className="w-2.5 h-2.5 rounded-full bg-red-500/80"></div>
                            <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/80"></div>
                            <div className="w-2.5 h-2.5 rounded-full bg-green-500/80"></div>
                          </div>
                          <span className="text-[10px] font-mono ml-2 uppercase tracking-wider" style={{ color: "var(--color-text-secondary)" }}>
                            Agent Process Terminal
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-[10px] font-mono text-emerald-400 animate-pulse">
                          <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full"></span>
                          CONNECTED
                        </div>
                      </div>
                      
                      <div className="p-4 h-48 overflow-y-auto font-mono text-[11px] leading-relaxed custom-scrollbar" style={{ background: "var(--color-overlay)" }}>
                        <div className="space-y-1.5">
                          {liveLogs[comp.id].map((log, lIdx) => (
                            <div key={lIdx} className="flex gap-3 animate-fade-in">
                              <span className="shrink-0" style={{ color: "var(--color-text-muted)" }}>[{new Date(log.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'})}]</span>
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

                  {/* Messages Section */}
                  {comp.status !== "draft" && (
                    <div className="mt-6">
                      <button
                        onClick={() => toggleMessages(comp.id)}
                        className="w-full flex items-center justify-between p-4 rounded-xl border transition-colors"
                        style={{ background: openMessageId === comp.id ? "rgba(139, 92, 246, 0.05)" : "var(--color-overlay)", borderColor: openMessageId === comp.id ? "rgba(139, 92, 246, 0.2)" : "var(--color-border)" }}
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-lg">💬</span>
                          <div className="text-left">
                            <h4 className="text-sm font-semibold" style={{ color: "var(--color-text-primary)" }}>Messages</h4>
                            <p className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Chat with your incorporation team</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {(msgUnread[comp.id] || 0) > 0 && (
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold" style={{ background: "rgba(239, 68, 68, 0.15)", color: "var(--color-error)" }}>
                              {msgUnread[comp.id]} new
                            </span>
                          )}
                          <span className="text-xs" style={{ color: "var(--color-text-muted)" }}>{openMessageId === comp.id ? "▲" : "▼"}</span>
                        </div>
                      </button>

                      {openMessageId === comp.id && (
                        <div className="mt-2 rounded-xl overflow-hidden flex flex-col" style={{ border: "1px solid var(--color-border)", background: "var(--color-bg-card)", height: "380px" }}>
                          {/* Thread */}
                          <div className="flex-1 overflow-y-auto p-4 space-y-3">
                            {(companyMessages[comp.id] || []).length > 0 ? (
                              (companyMessages[comp.id] || []).map((msg: any) => {
                                const isMe = msg.sender_type === "founder";
                                return (
                                  <div key={msg.id} className={`flex ${isMe ? "justify-end" : "justify-start"}`}>
                                    <div
                                      className="max-w-[75%] rounded-xl px-4 py-3"
                                      style={isMe
                                        ? { background: "rgba(139, 92, 246, 0.1)", border: "1px solid rgba(139, 92, 246, 0.2)" }
                                        : { background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)" }
                                      }
                                    >
                                      <div className="flex items-center gap-2 mb-1">
                                        <span className="text-[10px] font-semibold" style={{ color: isMe ? "var(--color-accent-purple-light)" : "var(--color-info)" }}>
                                          {isMe ? "You" : (msg.sender_name || "CMS Team")}
                                        </span>
                                        <span className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>
                                          {msg.created_at ? new Date(msg.created_at).toLocaleString() : ""}
                                        </span>
                                      </div>
                                      <p className="text-sm leading-relaxed" style={{ color: "var(--color-text-primary)" }}>{msg.content}</p>
                                    </div>
                                  </div>
                                );
                              })
                            ) : (
                              <div className="flex items-center justify-center h-full">
                                <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>No messages yet. Ask your team anything about your incorporation.</p>
                              </div>
                            )}
                            <div ref={messagesEndRef} />
                          </div>

                          {/* Compose */}
                          <div className="p-3 flex gap-2 items-end" style={{ borderTop: "1px solid var(--color-border)", background: "var(--color-bg-secondary)" }}>
                            <textarea
                              value={msgContent}
                              onChange={(e) => setMsgContent(e.target.value)}
                              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSendMsg(comp.id); } }}
                              placeholder="Type a message..."
                              className="flex-1 rounded-lg p-2.5 text-sm resize-none focus:outline-none"
                              style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                              rows={1}
                            />
                            <button
                              onClick={() => handleSendMsg(comp.id)}
                              disabled={!msgContent.trim() || sendingMsg}
                              className="px-4 py-2.5 rounded-lg text-xs font-medium transition-colors disabled:opacity-50 shrink-0"
                              style={{ background: "var(--color-accent-purple)", color: "#fff" }}
                            >
                              {sendingMsg ? "..." : "Send"}
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {comp.status === "payment_pending" && (
                    <div className="mt-6 p-4 rounded-xl border flex justify-between items-center" style={{ background: "rgba(245, 158, 11, 0.05)", borderColor: "rgba(245, 158, 11, 0.2)" }}>
                       <div>
                         <h4 className="text-sm font-semibold mb-1">Complete Payment</h4>
                         <p className="text-xs" style={{ color: "var(--color-text-secondary)" }}>Secure your slot to begin the process.</p>
                       </div>
                       <Link href="/onboarding" className="btn-primary text-sm !py-2 !px-4 bg-amber-600 hover:bg-amber-500" style={{ color: "var(--color-text-primary)" }}>Resume Checkout →</Link>
                    </div>
                  )}

                </div>
              );
            })}
          </div>
        )}
      </div>

      {companies.length > 0 && <ChatWidget companyId={companies[0]?.id} />}
      <Footer />
    </div>
  );
}
