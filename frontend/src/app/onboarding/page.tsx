"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { createDraftCompany, updateOnboarding, createPaymentOrder, verifyPayment } from "@/lib/api";
import Footer from "@/components/footer";

export default function OnboardingPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(true);
  const [companyId, setCompanyId] = useState<number | null>(null);
  const [draftConfig, setDraftConfig] = useState<any>(null);

  // Form states
  const [names, setNames] = useState(["", ""]);
  const [directors, setDirectors] = useState<any[]>([]);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.push("/login");
      return;
    }

    const initDraft = async () => {
      try {
        const stored = localStorage.getItem("pending_company_draft");
        if (!stored) {
          router.push("/dashboard");
          return;
        }

        const payload = JSON.parse(stored);
        setDraftConfig(payload);

        // Initialize enough director slots
        const slots = Array(payload.num_directors).fill({ full_name: "", email: "", phone: "" });
        
        // Auto-fill user into slot 1
        if (slots.length > 0) {
          slots[0] = { full_name: user.full_name, email: user.email, phone: user.phone || "" };
        }
        setDirectors(slots);

        // Call backend API to create the draft Company instance in DB
        const company = await createDraftCompany({
          entity_type: payload.entity_type,
          plan_tier: payload.plan_tier,
          state: payload.state,
          authorized_capital: payload.authorized_capital,
          num_directors: payload.num_directors,
          pricing_snapshot: payload.pricing_snapshot, 
        });

        setCompanyId(company.id);
        setLoading(false);
      } catch (err) {
        console.error("Failed to initialize draft:", err);
        router.push("/pricing"); // Fail safe
      }
    };

    initDraft();
  }, [user, authLoading, router]);

  // Load Razorpay checkout.js script
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.async = true;
    document.body.appendChild(script);
    return () => {
      document.body.removeChild(script);
    };
  }, []);

  const handleUpdateDetails = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyId) return;
    setLoading(true);
    
    try {
      // Filter out empty names
      const proposedNames = names.filter(n => n.trim() !== "");
      
      await updateOnboarding(companyId, {
        proposed_names: proposedNames,
        directors: directors
      });
      setStep(3); // Move to checkout
    } catch (err) {
      console.error(err);
      alert("Failed to save details. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleRazorpayCheckout = async () => {
    if (!companyId) return;
    setLoading(true);
    try {
      const orderData = await createPaymentOrder(companyId);

      if (!orderData.key_id) {
        throw new Error("Payment service is not configured. Please contact support.");
      }

      // Mock payment mode — skip Razorpay modal and auto-complete
      if (orderData.mock) {
        try {
          await verifyPayment({
            razorpay_order_id: orderData.order_id,
            razorpay_payment_id: `mock_pay_${Date.now()}`,
            razorpay_signature: `mock_sig_${Date.now()}`,
          });
          localStorage.removeItem("pending_company_draft");
          router.push("/dashboard");
        } catch (verifyErr) {
          console.error("Mock payment verification failed:", verifyErr);
          alert("Payment verification failed. Please contact support.");
          setLoading(false);
        }
        return;
      }

      const options = {
        key: orderData.key_id,
        amount: orderData.amount,
        currency: orderData.currency,
        name: "Anvils",
        description: `Incorporation - ${draftConfig.entity_type.replace("_", " ")}`,
        order_id: orderData.order_id,
        handler: async function (response: any) {
          try {
            await verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            });
            localStorage.removeItem("pending_company_draft");
            router.push("/dashboard");
          } catch (verifyErr) {
            console.error("Payment verification failed:", verifyErr);
            alert("Payment verification failed. Please contact support.");
            setLoading(false);
          }
        },
        prefill: {
          name: user?.full_name,
          email: user?.email,
          contact: user?.phone,
        },
        theme: {
          color: "#8b5cf6",
        },
        modal: {
          ondismiss: function () {
            setLoading(false);
          },
        },
      };

      const rzp = new (window as any).Razorpay(options);
      rzp.on("payment.failed", function (response: any) {
        console.error("Payment failed:", response.error);
        alert(`Payment failed: ${response.error.description}`);
        setLoading(false);
      });
      rzp.open();
    } catch (err) {
      console.error("Checkout error:", err);
      alert("Failed to initiate payment. Please try again.");
      setLoading(false);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center glow-bg">
        <div className="animate-pulse-glow w-16 h-16 rounded-full bg-purple-500/20 flex items-center justify-center">
           <img src="/logo-icon.png" alt="Anvils" className="w-7 h-7 object-contain" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 pb-12 glow-bg px-6">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8 p-4 rounded-2xl glass-card flex items-center justify-between animate-fade-in-up">
           <div>
              <h1 className="text-xl font-bold">Incorporation Setup</h1>
              <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
                {draftConfig.pricing_snapshot.state_display} • {draftConfig.entity_type.replace("_", " ").toUpperCase()}
              </p>
           </div>
           <div className="text-right">
             <div className="text-sm" style={{ color: "var(--color-text-secondary)" }}>Total Due</div>
             <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-emerald-400">
               ₹{draftConfig.pricing_snapshot.grand_total.toLocaleString()}
             </div>
           </div>
        </div>

        <div className="glass-card p-8 animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
          
          {/* Progress Bar */}
          <div className="flex items-center mb-8">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center flex-1 last:flex-none">
                <div 
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors ${
                    step >= i ? "" : ""
                  }`}
                  style={step >= i ? { background: "var(--color-primary-purple)", color: "var(--color-text-primary)" } : { background: "var(--color-bg-card)", color: "var(--color-text-muted)" }}
                >
                  {i}
                </div>
                {i < 3 && (
                  <div className="flex-1 h-1 mx-2 rounded-full transition-colors" 
                       style={{ background: step > i ? "var(--color-primary-purple)" : "var(--color-border)" }} />
                )}
              </div>
            ))}
          </div>

          <form onSubmit={step === 2 ? handleUpdateDetails : (e) => { e.preventDefault(); setStep(2); }}>
            
            {step === 1 && (
              <div className="space-y-6 animate-fade-in-up">
                <h2 className="text-2xl font-semibold mb-2 font-heading">Company Names</h2>
                <p className="text-sm mb-6" style={{ color: "var(--color-text-secondary)" }}>
                  Provide up to 2 creative names for your new company. We will run an AI clash-check against the MCA database before filing.
                </p>
                
                {[0, 1].map((idx) => (
                  <div key={idx}>
                    <label className="block text-sm font-medium mb-1">
                      Preference {idx + 1} {idx === 1 && "(Optional)"}
                    </label>
                    <input
                      required={idx === 0}
                      type="text"
                      className="w-full p-3 rounded-xl bg-transparent border text-sm transition-colors"
                      style={{ borderColor: "var(--color-border)" }}
                      value={names[idx]}
                      onChange={(e) => {
                        const newNames = [...names];
                        newNames[idx] = e.target.value.toUpperCase();
                        setNames(newNames);
                      }}
                      placeholder={`e.g. ACME INNOVATION ${draftConfig.entity_type === 'private_limited' ? 'PRIVATE LIMITED' : ''}`}
                    />
                  </div>
                ))}
                
                <div className="pt-4 flex justify-end">
                  <button type="submit" className="btn-primary">
                    Next: Directors →
                  </button>
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-6 animate-fade-in-up">
                <h2 className="text-2xl font-semibold mb-2 font-heading">Director Details</h2>
                <p className="text-sm mb-6" style={{ color: "var(--color-text-secondary)" }}>
                  We need basic contact info for your {draftConfig.num_directors} directors to generate the DSC authorization forms.
                </p>

                {directors.map((dir, idx) => (
                  <div key={idx} className="p-4 rounded-xl border mb-4" style={{ borderColor: "var(--color-border)", background: "rgba(255,255,255,0.02)" }}>
                    <h3 className="font-semibold mb-3">
                      Director {idx + 1} 
                      {idx === 0 && <span className="ml-2 text-xs py-1 px-2 rounded-full" style={{ background: "rgba(139, 92, 246, 0.2)", color: "var(--color-accent-purple-light)" }}>You</span>}
                    </h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="md:col-span-2">
                        <label className="block text-xs font-medium mb-1" style={{ color: "var(--color-text-secondary)" }}>Full Name as per PAN</label>
                        <input required type="text" className="w-full p-2 rounded-lg bg-transparent border text-sm" style={{ borderColor: "var(--color-border)" }}
                          value={dir.full_name}
                          onChange={(e) => {
                            const newDirs = [...directors];
                            newDirs[idx].full_name = e.target.value;
                            setDirectors(newDirs);
                          }}
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium mb-1" style={{ color: "var(--color-text-secondary)" }}>Email</label>
                        <input required type="email" className="w-full p-2 rounded-lg bg-transparent border text-sm" style={{ borderColor: "var(--color-border)" }}
                           value={dir.email}
                           onChange={(e) => {
                             const newDirs = [...directors];
                             newDirs[idx].email = e.target.value;
                             setDirectors(newDirs);
                           }}
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium mb-1" style={{ color: "var(--color-text-secondary)" }}>Phone Number</label>
                        <input required type="tel" className="w-full p-2 rounded-lg bg-transparent border text-sm" style={{ borderColor: "var(--color-border)" }}
                           value={dir.phone}
                           onChange={(e) => {
                             const newDirs = [...directors];
                             newDirs[idx].phone = e.target.value;
                             setDirectors(newDirs);
                           }}
                        />
                      </div>
                    </div>
                  </div>
                ))}

                <div className="pt-4 flex justify-between">
                  <button type="button" onClick={() => setStep(1)} className="btn-secondary">
                    ← Back
                  </button>
                  <button type="submit" className="btn-primary">
                    Proceed to Payment →
                  </button>
                </div>
              </div>
            )}
            
            {step === 3 && (
              <div className="space-y-6 text-center animate-fade-in-up">
                 <div className="w-20 h-20 mx-auto rounded-full flex items-center justify-center mb-6" style={{ background: "rgba(16, 185, 129, 0.1)" }}>
                   <span className="text-4xl">🔐</span>
                 </div>
                 <h2 className="text-2xl font-semibold mb-2 font-heading">Secure Your Slot</h2>
                 <p className="text-sm max-w-md mx-auto mb-8" style={{ color: "var(--color-text-secondary)" }}>
                   Your details are saved! Complete the payment to begin the formal incorporation process. A dedicated agent will be assigned to your case immediately.
                 </p>
                 
                 <div className="inline-block p-6 rounded-2xl mb-8" style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--color-border)" }}>
                    <div className="text-sm mb-1" style={{ color: "var(--color-text-secondary)" }}>Total Amount</div>
                    <div className="text-4xl font-bold">₹{draftConfig.pricing_snapshot.grand_total.toLocaleString()}</div>
                 </div>

                 <div>
                   <button type="button" onClick={handleRazorpayCheckout} disabled={loading} className="btn-primary py-4 px-12 text-lg">
                     {loading ? "Processing..." : "Pay Securely via Razorpay"}
                   </button>
                 </div>
              </div>
            )}
          </form>
        </div>
      </div>
      <Footer />
    </div>
  );
}
