"use client";

import { useState, useEffect } from "react";

import {
  getFundingRounds,
  getFundingRound,
  createFundingRound,
  addRoundInvestor,
  updateRoundInvestor,
  removeRoundInvestor,
  getClosingRoom,
  initiateClosing,
  completeAllotment,
  previewConversion,
  convertRound,
} from "@/lib/api";


interface Investor {
  id: number;
  investor_name: string;
  investor_email: string | null;
  investor_type: string;
  investor_entity: string | null;
  investment_amount: number;
  shares_allotted: number;
  share_type: string;
  committed: boolean;
  funds_received: boolean;
  documents_signed: boolean;
  shares_issued: boolean;
  notes: string | null;
}

interface FundingRound {
  id: number;
  company_id: number;
  round_name: string;
  instrument_type: string;
  pre_money_valuation: number | null;
  post_money_valuation: number | null;
  price_per_share: number | null;
  target_amount: number | null;
  amount_raised: number;
  status: string;
  allotment_completed: boolean;
  valuation_cap: number | null;
  discount_rate: number | null;
  interest_rate: number | null;
  maturity_months: number | null;
  notes: string | null;
  investor_count?: number;
  investors?: Investor[];
  created_at: string;
}

const STATUS_COLORS: Record<string, { bg: string; text: string }> = {
  draft: { bg: "rgba(156, 163, 175, 0.15)", text: "rgb(156, 163, 175)" },
  term_sheet: { bg: "rgba(139, 92, 246, 0.15)", text: "rgb(139, 92, 246)" },
  due_diligence: { bg: "rgba(59, 130, 246, 0.15)", text: "rgb(59, 130, 246)" },
  documentation: { bg: "rgba(99, 102, 241, 0.15)", text: "rgb(99, 102, 241)" },
  closing: { bg: "rgba(245, 158, 11, 0.15)", text: "rgb(245, 158, 11)" },
  closed: { bg: "rgba(16, 185, 129, 0.15)", text: "rgb(16, 185, 129)" },
  cancelled: { bg: "rgba(244, 63, 94, 0.15)", text: "rgb(244, 63, 94)" },
};

const INSTRUMENT_LABELS: Record<string, string> = {
  equity: "Equity",
  ccps: "CCPS",
  ccd: "CCD",
  safe: "SAFE",
  convertible_note: "Convertible Note",
};

function StatusBadge({ status }: { status: string }) {
  const colors = STATUS_COLORS[status] || STATUS_COLORS.draft;
  return (
    <span
      className="text-xs px-2 py-0.5 rounded-full capitalize"
      style={{ background: colors.bg, color: colors.text }}
    >
      {status.replace(/_/g, " ")}
    </span>
  );
}

function formatCurrency(val: number): string {
  if (val >= 10000000) return `Rs ${(val / 10000000).toFixed(2)} Cr`;
  if (val >= 100000) return `Rs ${(val / 100000).toFixed(2)} L`;
  return `Rs ${val.toLocaleString()}`;
}

export default function FundraisingPage() {
  const [companyId, setCompanyId] = useState<number>(1);
  const [rounds, setRounds] = useState<FundingRound[]>([]);
  const [selectedRound, setSelectedRound] = useState<FundingRound | null>(null);
  const [closingRoom, setClosingRoom] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  // Create round modal
  const [showCreateRound, setShowCreateRound] = useState(false);
  const [roundForm, setRoundForm] = useState({
    round_name: "",
    instrument_type: "equity",
    pre_money_valuation: "",
    target_amount: "",
    price_per_share: "",
    notes: "",
  });

  // Conversion state
  const [conversionPreview, setConversionPreview] = useState<any>(null);
  const [triggerRoundId, setTriggerRoundId] = useState<string>("");
  const [converting, setConverting] = useState(false);
  const [showConversionConfirm, setShowConversionConfirm] = useState(false);

  // Add investor modal
  const [showAddInvestor, setShowAddInvestor] = useState(false);
  const [investorForm, setInvestorForm] = useState({
    investor_name: "",
    investor_email: "",
    investor_type: "angel",
    investor_entity: "",
    investment_amount: "",
    share_type: "equity",
  });

  useEffect(() => {
    fetchRounds();
  }, [companyId]);

  async function fetchRounds() {
    setLoading(true);
    try {
      const data = await getFundingRounds(companyId);
      setRounds(data);
    } catch {
      // Backend may not be running
    }
    setLoading(false);
  }

  async function fetchRoundDetail(roundId: number) {
    try {
      const data = await getFundingRound(companyId, roundId);
      setSelectedRound(data);
      // Also fetch closing room status if in closing/closed state
      if (data.status === "closing" || data.status === "closed") {
        try {
          const cr = await getClosingRoom(companyId, roundId);
          setClosingRoom(cr);
        } catch {
          setClosingRoom(null);
        }
      } else {
        setClosingRoom(null);
      }
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleCreateRound(e: React.FormEvent) {
    e.preventDefault();
    setMessage("");
    try {
      await createFundingRound(companyId, {
        round_name: roundForm.round_name,
        instrument_type: roundForm.instrument_type,
        pre_money_valuation: roundForm.pre_money_valuation ? parseFloat(roundForm.pre_money_valuation) : undefined,
        target_amount: roundForm.target_amount ? parseFloat(roundForm.target_amount) : undefined,
        price_per_share: roundForm.price_per_share ? parseFloat(roundForm.price_per_share) : undefined,
        notes: roundForm.notes || undefined,
      });
      setMessage("Round created successfully!");
      setShowCreateRound(false);
      setRoundForm({
        round_name: "",
        instrument_type: "equity",
        pre_money_valuation: "",
        target_amount: "",
        price_per_share: "",
        notes: "",
      });
      fetchRounds();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleAddInvestor(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedRound) return;
    setMessage("");
    try {
      await addRoundInvestor(companyId, selectedRound.id, {
        investor_name: investorForm.investor_name,
        investor_email: investorForm.investor_email || undefined,
        investor_type: investorForm.investor_type,
        investor_entity: investorForm.investor_entity || undefined,
        investment_amount: parseFloat(investorForm.investment_amount),
        share_type: investorForm.share_type,
      });
      setMessage("Investor added!");
      setShowAddInvestor(false);
      setInvestorForm({
        investor_name: "",
        investor_email: "",
        investor_type: "angel",
        investor_entity: "",
        investment_amount: "",
        share_type: "equity",
      });
      fetchRoundDetail(selectedRound.id);
      fetchRounds();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleToggleFlag(investorId: number, field: string, value: boolean) {
    if (!selectedRound) return;
    try {
      await updateRoundInvestor(companyId, selectedRound.id, investorId, {
        [field]: value,
      });
      fetchRoundDetail(selectedRound.id);
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleRemoveInvestor(investorId: number) {
    if (!selectedRound) return;
    try {
      await removeRoundInvestor(companyId, selectedRound.id, investorId);
      setMessage("Investor removed");
      fetchRoundDetail(selectedRound.id);
      fetchRounds();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleInitiateClosing() {
    if (!selectedRound) return;
    setMessage("");
    try {
      await initiateClosing(companyId, selectedRound.id, {
        documents_to_sign: ["sha", "ssa"],
      });
      setMessage("Closing room initiated! Documents sent for signing.");
      fetchRoundDetail(selectedRound.id);
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleCompleteAllotment() {
    if (!selectedRound) return;
    setMessage("");
    try {
      await completeAllotment(companyId, selectedRound.id);
      setMessage("Shares allotted! Cap table updated.");
      fetchRoundDetail(selectedRound.id);
      fetchRounds();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  const isConvertible = (type: string) =>
    ["safe", "ccd", "convertible_note", "ccps"].includes(type);

  const equityRounds = rounds.filter(
    (r) => r.instrument_type === "equity" && r.id !== selectedRound?.id
  );

  async function handlePreviewConversion() {
    if (!selectedRound) return;
    setMessage("");
    try {
      const data = await previewConversion(
        companyId,
        selectedRound.id,
        triggerRoundId ? parseInt(triggerRoundId) : undefined
      );
      setConversionPreview(data);
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  }

  async function handleExecuteConversion() {
    if (!selectedRound) return;
    setConverting(true);
    setMessage("");
    try {
      await convertRound(companyId, selectedRound.id, {
        trigger_round_id: triggerRoundId ? parseInt(triggerRoundId) : undefined,
      });
      setMessage("Conversion complete! Shares have been allotted to the cap table.");
      setConversionPreview(null);
      setShowConversionConfirm(false);
      fetchRoundDetail(selectedRound.id);
      fetchRounds();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
    setConverting(false);
  }

  return (
    <div>
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="badge badge-purple mb-4 mx-auto w-fit">Fundraising Engine</div>
          <h1 className="text-3xl md:text-4xl font-bold mb-3" style={{ fontFamily: "var(--font-display)" }}>
            <span className="gradient-text">Fundraising</span>
          </h1>
          <p className="text-base" style={{ color: "var(--color-text-secondary)" }}>
            Manage funding rounds, track investors, and close deals.
          </p>
        </div>

        {/* Company selector */}
        <div className="flex justify-center mb-6">
          <div className="flex items-center gap-3">
            <label className="text-sm" style={{ color: "var(--color-text-muted)" }}>Company ID:</label>
            <input
              type="number"
              value={companyId}
              onChange={(e) => { setCompanyId(parseInt(e.target.value) || 1); setSelectedRound(null); }}
              className="glass-card px-3 py-1.5 text-sm w-20 text-center"
              style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)", cursor: "text" }}
              min={1}
            />
          </div>
        </div>

        {message && (
          <div
            className="glass-card p-3 mb-6 text-center text-sm"
            style={{
              borderColor: message.startsWith("Error") ? "rgba(244, 63, 94, 0.5)" : "rgba(16, 185, 129, 0.5)",
              cursor: "default",
            }}
          >
            {message}
          </div>
        )}

        {loading && (
          <div className="text-center py-12" style={{ color: "var(--color-text-muted)" }}>Loading...</div>
        )}

        {/* Two-panel layout: rounds list + detail */}
        {!loading && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left: Rounds List */}
            <div className="lg:col-span-1">
              <div className="flex justify-between items-center mb-4">
                <h2 className="font-semibold">Rounds</h2>
                <button onClick={() => setShowCreateRound(true)} className="text-xs px-3 py-1.5 rounded-lg" style={{ background: "rgba(139, 92, 246, 0.1)", border: "1px solid rgba(139, 92, 246, 0.3)", color: "rgb(139, 92, 246)" }}>
                  + New Round
                </button>
              </div>

              {rounds.length === 0 ? (
                <div className="glass-card p-8 text-center" style={{ cursor: "default" }}>
                  <div className="text-3xl mb-3">&#128176;</div>
                  <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>No funding rounds yet.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {rounds.map((round) => {
                    const progressPct = round.target_amount && round.target_amount > 0
                      ? Math.min(100, Math.round((round.amount_raised / round.target_amount) * 100))
                      : 0;
                    return (
                      <button
                        key={round.id}
                        onClick={() => fetchRoundDetail(round.id)}
                        className="glass-card p-4 w-full text-left transition-all"
                        style={{
                          borderColor: selectedRound?.id === round.id ? "rgba(139, 92, 246, 0.6)" : "var(--color-border)",
                          background: selectedRound?.id === round.id ? "rgba(139, 92, 246, 0.08)" : undefined,
                        }}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <div className="font-semibold text-sm">{round.round_name}</div>
                            <div className="text-[10px] mt-0.5" style={{ color: "var(--color-text-muted)" }}>
                              {INSTRUMENT_LABELS[round.instrument_type] || round.instrument_type}
                              {round.investor_count !== undefined && ` | ${round.investor_count} investor(s)`}
                            </div>
                          </div>
                          <StatusBadge status={round.status} />
                        </div>
                        {round.target_amount && round.target_amount > 0 && (
                          <div>
                            <div className="flex justify-between text-[10px] mb-1" style={{ color: "var(--color-text-muted)" }}>
                              <span>{formatCurrency(round.amount_raised)}</span>
                              <span>{formatCurrency(round.target_amount)}</span>
                            </div>
                            <div className="w-full h-1.5 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.05)" }}>
                              <div className="h-full rounded-full" style={{ width: `${progressPct}%`, background: "rgb(139, 92, 246)" }} />
                            </div>
                          </div>
                        )}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Right: Round Detail */}
            <div className="lg:col-span-2">
              {!selectedRound ? (
                <div className="glass-card p-12 text-center" style={{ cursor: "default" }}>
                  <div className="text-4xl mb-4">&#128200;</div>
                  <h3 className="text-lg font-semibold mb-2">Select a Round</h3>
                  <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                    Click on a round from the list to view details, manage investors, and track closing.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Round Header */}
                  <div className="glass-card p-5" style={{ cursor: "default" }}>
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h2 className="text-xl font-bold">{selectedRound.round_name}</h2>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: "rgba(139, 92, 246, 0.15)", color: "rgb(139, 92, 246)" }}>
                            {INSTRUMENT_LABELS[selectedRound.instrument_type] || selectedRound.instrument_type}
                          </span>
                          <StatusBadge status={selectedRound.status} />
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {selectedRound.pre_money_valuation != null && (
                        <div className="text-center">
                          <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Pre-Money</div>
                          <div className="text-sm font-bold">{formatCurrency(selectedRound.pre_money_valuation)}</div>
                        </div>
                      )}
                      <div className="text-center">
                        <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Raised</div>
                        <div className="text-sm font-bold" style={{ color: "rgb(16, 185, 129)" }}>
                          {formatCurrency(selectedRound.amount_raised)}
                        </div>
                      </div>
                      {selectedRound.post_money_valuation != null && (
                        <div className="text-center">
                          <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Post-Money</div>
                          <div className="text-sm font-bold">{formatCurrency(selectedRound.post_money_valuation)}</div>
                        </div>
                      )}
                      {selectedRound.price_per_share != null && (
                        <div className="text-center">
                          <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>Price/Share</div>
                          <div className="text-sm font-bold">Rs {selectedRound.price_per_share.toFixed(2)}</div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Convertible Conversion Section */}
                  {isConvertible(selectedRound.instrument_type) && !selectedRound.allotment_completed && (
                    <div className="glass-card p-5" style={{ cursor: "default" }}>
                      <div className="flex items-center gap-2 mb-4">
                        <h3 className="font-semibold">Convert to Equity</h3>
                        <span className="text-[10px] px-2 py-0.5 rounded-full" style={{ background: "rgba(245, 158, 11, 0.15)", color: "rgb(245, 158, 11)" }}>
                          {INSTRUMENT_LABELS[selectedRound.instrument_type]}
                        </span>
                      </div>

                      {/* Convertible terms summary */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4 p-3 rounded-lg" style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--color-border)" }}>
                        {selectedRound.valuation_cap != null && (
                          <div className="text-center">
                            <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Valuation Cap</div>
                            <div className="text-sm font-bold">{formatCurrency(selectedRound.valuation_cap)}</div>
                          </div>
                        )}
                        {selectedRound.discount_rate != null && (
                          <div className="text-center">
                            <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Discount Rate</div>
                            <div className="text-sm font-bold">{selectedRound.discount_rate}%</div>
                          </div>
                        )}
                        {selectedRound.interest_rate != null && (
                          <div className="text-center">
                            <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Interest Rate</div>
                            <div className="text-sm font-bold">{selectedRound.interest_rate}%</div>
                          </div>
                        )}
                        {selectedRound.maturity_months != null && (
                          <div className="text-center">
                            <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Maturity</div>
                            <div className="text-sm font-bold">{selectedRound.maturity_months} months</div>
                          </div>
                        )}
                        {!selectedRound.valuation_cap && !selectedRound.discount_rate && !selectedRound.interest_rate && !selectedRound.maturity_months && (
                          <div className="col-span-4 text-center text-xs" style={{ color: "var(--color-text-muted)" }}>
                            No convertible terms set. Edit the round to add valuation cap, discount rate, etc.
                          </div>
                        )}
                      </div>

                      {/* Trigger round selector */}
                      <div className="flex flex-wrap items-end gap-3 mb-4">
                        <div className="flex-1 min-w-[200px]">
                          <label className="block text-xs mb-1" style={{ color: "var(--color-text-muted)" }}>
                            Trigger Round (equity round that sets price)
                          </label>
                          <select
                            value={triggerRoundId}
                            onChange={(e) => { setTriggerRoundId(e.target.value); setConversionPreview(null); }}
                            className="w-full px-3 py-2 rounded-lg text-sm"
                            style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                          >
                            <option value="">None (use valuation cap only)</option>
                            {equityRounds.map((r) => (
                              <option key={r.id} value={r.id.toString()}>
                                {r.round_name} {r.price_per_share ? `(Rs ${r.price_per_share}/share)` : ""}
                              </option>
                            ))}
                          </select>
                        </div>
                        <button
                          onClick={handlePreviewConversion}
                          className="text-sm px-4 py-2 rounded-lg"
                          style={{ background: "rgba(139, 92, 246, 0.1)", border: "1px solid rgba(139, 92, 246, 0.3)", color: "rgb(139, 92, 246)" }}
                        >
                          Preview Conversion
                        </button>
                      </div>

                      {/* Conversion preview results */}
                      {conversionPreview && (
                        <div>
                          <div className="grid grid-cols-3 gap-3 mb-4">
                            <div className="p-3 rounded-lg text-center" style={{ background: "rgba(139, 92, 246, 0.08)", border: "1px solid rgba(139, 92, 246, 0.2)" }}>
                              <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Trigger Price</div>
                              <div className="text-sm font-bold">
                                {conversionPreview.trigger_price_per_share ? `Rs ${conversionPreview.trigger_price_per_share}` : "N/A"}
                              </div>
                            </div>
                            <div className="p-3 rounded-lg text-center" style={{ background: "rgba(139, 92, 246, 0.08)", border: "1px solid rgba(139, 92, 246, 0.2)" }}>
                              <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Existing Shares</div>
                              <div className="text-sm font-bold">{conversionPreview.total_existing_shares?.toLocaleString()}</div>
                            </div>
                            <div className="p-3 rounded-lg text-center" style={{ background: "rgba(139, 92, 246, 0.08)", border: "1px solid rgba(139, 92, 246, 0.2)" }}>
                              <div className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>Total New Shares</div>
                              <div className="text-sm font-bold">
                                {conversionPreview.conversions?.reduce((s: number, c: any) => s + c.shares_issued, 0)?.toLocaleString()}
                              </div>
                            </div>
                          </div>

                          <div className="overflow-x-auto rounded-lg" style={{ border: "1px solid var(--color-border)" }}>
                            <table className="w-full text-sm">
                              <thead>
                                <tr style={{ borderBottom: "1px solid var(--color-border)", background: "rgba(255,255,255,0.02)" }}>
                                  <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Investor</th>
                                  <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Principal</th>
                                  <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Interest</th>
                                  <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Total</th>
                                  <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Price/Share</th>
                                  <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Method</th>
                                  <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Shares</th>
                                </tr>
                              </thead>
                              <tbody>
                                {conversionPreview.conversions?.map((c: any) => (
                                  <tr key={c.investor_id} style={{ borderBottom: "1px solid var(--color-border)" }}>
                                    <td className="p-3 font-medium">{c.investor_name}</td>
                                    <td className="p-3 text-right font-mono">{formatCurrency(c.principal)}</td>
                                    <td className="p-3 text-right font-mono">{c.interest_accrued > 0 ? formatCurrency(c.interest_accrued) : "-"}</td>
                                    <td className="p-3 text-right font-mono">{formatCurrency(c.total_amount)}</td>
                                    <td className="p-3 text-right font-mono">Rs {c.conversion_price}</td>
                                    <td className="p-3">
                                      <span className="text-xs px-2 py-0.5 rounded-full capitalize" style={{ background: "rgba(139, 92, 246, 0.15)", color: "rgb(139, 92, 246)" }}>
                                        {c.conversion_method?.replace(/_/g, " ")}
                                      </span>
                                    </td>
                                    <td className="p-3 text-right font-bold" style={{ color: "rgb(16, 185, 129)" }}>{c.shares_issued?.toLocaleString()}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>

                          {/* All available conversion prices per investor */}
                          {conversionPreview.conversions?.length > 0 && conversionPreview.conversions[0].all_prices && (
                            <div className="mt-3 p-3 rounded-lg text-xs" style={{ background: "rgba(255,255,255,0.02)", border: "1px solid var(--color-border)" }}>
                              <span style={{ color: "var(--color-text-muted)" }}>Available prices: </span>
                              {Object.entries(conversionPreview.conversions[0].all_prices as Record<string, number>).map(([method, price]) => (
                                <span key={method} className="mr-3">
                                  <span className="capitalize">{method.replace(/_/g, " ")}</span>: <span className="font-mono">Rs {price}</span>
                                </span>
                              ))}
                            </div>
                          )}

                          {/* Execute conversion button */}
                          <div className="mt-4 flex items-center gap-3">
                            {!showConversionConfirm ? (
                              <button
                                onClick={() => setShowConversionConfirm(true)}
                                className="btn-primary text-sm"
                              >
                                Execute Conversion
                              </button>
                            ) : (
                              <>
                                <span className="text-sm" style={{ color: "rgb(245, 158, 11)" }}>
                                  This will create new shareholders on the cap table. Continue?
                                </span>
                                <button
                                  onClick={handleExecuteConversion}
                                  disabled={converting}
                                  className="text-sm px-4 py-2 rounded-lg"
                                  style={{ background: "rgba(16, 185, 129, 0.15)", border: "1px solid rgba(16, 185, 129, 0.4)", color: "rgb(16, 185, 129)" }}
                                >
                                  {converting ? "Converting..." : "Confirm Conversion"}
                                </button>
                                <button
                                  onClick={() => setShowConversionConfirm(false)}
                                  className="text-sm px-3 py-2 rounded-lg"
                                  style={{ color: "var(--color-text-muted)" }}
                                >
                                  Cancel
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Investors Table */}
                  <div className="glass-card overflow-hidden" style={{ cursor: "default" }}>
                    <div className="p-4 flex justify-between items-center" style={{ borderBottom: "1px solid var(--color-border)" }}>
                      <h3 className="font-semibold">Investors ({selectedRound.investors?.length || 0})</h3>
                      {selectedRound.status !== "closed" && selectedRound.status !== "cancelled" && (
                        <button
                          onClick={() => setShowAddInvestor(true)}
                          className="text-xs px-3 py-1.5 rounded-lg"
                          style={{ background: "rgba(139, 92, 246, 0.1)", border: "1px solid rgba(139, 92, 246, 0.3)", color: "rgb(139, 92, 246)" }}
                        >
                          + Add Investor
                        </button>
                      )}
                    </div>

                    {!selectedRound.investors || selectedRound.investors.length === 0 ? (
                      <div className="p-8 text-center" style={{ color: "var(--color-text-muted)" }}>
                        No investors added yet.
                      </div>
                    ) : (
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                              <th className="text-left p-3" style={{ color: "var(--color-text-muted)" }}>Investor</th>
                              <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Amount</th>
                              <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Committed</th>
                              <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Funds</th>
                              <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Docs</th>
                              <th className="text-center p-3" style={{ color: "var(--color-text-muted)" }}>Shares</th>
                              <th className="text-right p-3" style={{ color: "var(--color-text-muted)" }}>Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            {selectedRound.investors.map((inv) => (
                              <tr key={inv.id} style={{ borderBottom: "1px solid var(--color-border)" }}>
                                <td className="p-3">
                                  <div className="font-medium">{inv.investor_name}</div>
                                  <div className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                                    {inv.investor_type}{inv.investor_entity && ` | ${inv.investor_entity}`}
                                  </div>
                                </td>
                                <td className="p-3 text-right font-mono">{formatCurrency(inv.investment_amount)}</td>
                                {(["committed", "funds_received", "documents_signed", "shares_issued"] as const).map((field) => (
                                  <td key={field} className="p-3 text-center">
                                    <button
                                      onClick={() => handleToggleFlag(inv.id, field, !inv[field])}
                                      className="w-5 h-5 rounded border inline-flex items-center justify-center transition-all"
                                      style={{
                                        borderColor: inv[field] ? "rgb(16, 185, 129)" : "var(--color-border)",
                                        background: inv[field] ? "rgba(16, 185, 129, 0.15)" : "transparent",
                                        color: inv[field] ? "rgb(16, 185, 129)" : "transparent",
                                      }}
                                    >
                                      {inv[field] && (
                                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                                          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                                        </svg>
                                      )}
                                    </button>
                                  </td>
                                ))}
                                <td className="p-3 text-right">
                                  {!inv.shares_issued && (
                                    <button
                                      onClick={() => handleRemoveInvestor(inv.id)}
                                      className="text-[11px] px-2 py-1 rounded"
                                      style={{ color: "rgb(244, 63, 94)" }}
                                    >
                                      Remove
                                    </button>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>

                  {/* Closing Room */}
                  {closingRoom && (
                    <div className="glass-card p-5" style={{ cursor: "default" }}>
                      <h3 className="font-semibold mb-3">Closing Room</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {Object.entries(closingRoom.documents || {}).map(([docType, doc]: [string, any]) => (
                          <div
                            key={docType}
                            className="p-3 rounded-lg"
                            style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--color-border)" }}
                          >
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-sm font-semibold uppercase">{docType}</span>
                              <StatusBadge status={doc.status} />
                            </div>
                            {doc.signatories && doc.signatories.length > 0 && (
                              <div className="space-y-1">
                                {doc.signatories.map((s: any, idx: number) => (
                                  <div key={idx} className="flex justify-between text-xs">
                                    <span style={{ color: "var(--color-text-secondary)" }}>{s.name}</span>
                                    <span style={{
                                      color: s.status === "signed" ? "rgb(16, 185, 129)"
                                        : s.status === "declined" ? "rgb(244, 63, 94)"
                                        : "var(--color-text-muted)",
                                    }}>
                                      {s.status}{s.signed_at && ` (${new Date(s.signed_at).toLocaleDateString()})`}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex gap-3 flex-wrap">
                    {selectedRound.status === "documentation" && (
                      <button onClick={handleInitiateClosing} className="btn-primary text-sm">
                        Initiate Closing
                      </button>
                    )}
                    {(selectedRound.status === "closing" || selectedRound.status === "documentation") && !selectedRound.allotment_completed && (
                      <button onClick={handleCompleteAllotment} className="text-sm px-4 py-2 rounded-lg" style={{ background: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.3)", color: "rgb(16, 185, 129)" }}>
                        Complete Allotment
                      </button>
                    )}
                    {selectedRound.allotment_completed && (
                      <div className="text-xs px-3 py-2 rounded-lg" style={{ background: "rgba(16, 185, 129, 0.1)", color: "rgb(16, 185, 129)" }}>
                        Allotment Complete - PAS-3 filing required within 15 days
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Create Round Modal */}
      {showCreateRound && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "rgba(0,0,0,0.6)" }}>
          <div className="glass-card p-6 w-full max-w-lg" style={{ cursor: "default", background: "var(--color-bg-card)" }}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">New Funding Round</h3>
              <button onClick={() => setShowCreateRound(false)} className="text-sm" style={{ color: "var(--color-text-muted)" }}>Close</button>
            </div>
            <form onSubmit={handleCreateRound} className="space-y-4">
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Round Name *</label>
                <input
                  type="text"
                  required
                  value={roundForm.round_name}
                  onChange={(e) => setRoundForm({ ...roundForm, round_name: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  placeholder="e.g., Seed Round, Series A"
                />
              </div>
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Instrument Type</label>
                <select
                  value={roundForm.instrument_type}
                  onChange={(e) => setRoundForm({ ...roundForm, instrument_type: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                >
                  <option value="equity">Equity</option>
                  <option value="ccps">CCPS (Compulsorily Convertible Preference Shares)</option>
                  <option value="ccd">CCD (Compulsorily Convertible Debentures)</option>
                  <option value="safe">SAFE</option>
                  <option value="convertible_note">Convertible Note</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Pre-Money Valuation (Rs)</label>
                  <input
                    type="number"
                    value={roundForm.pre_money_valuation}
                    onChange={(e) => setRoundForm({ ...roundForm, pre_money_valuation: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="10000000"
                  />
                  {roundForm.pre_money_valuation && (
                    <div className="text-[10px] mt-0.5" style={{ color: "var(--color-text-muted)" }}>
                      {formatCurrency(parseFloat(roundForm.pre_money_valuation) || 0)}
                    </div>
                  )}
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Target Amount (Rs)</label>
                  <input
                    type="number"
                    value={roundForm.target_amount}
                    onChange={(e) => setRoundForm({ ...roundForm, target_amount: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="2500000"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Price Per Share (Rs)</label>
                <input
                  type="number"
                  step="0.01"
                  value={roundForm.price_per_share}
                  onChange={(e) => setRoundForm({ ...roundForm, price_per_share: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  placeholder="100"
                />
              </div>
              <button type="submit" className="btn-primary w-full text-center justify-center">
                Create Round
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Add Investor Modal */}
      {showAddInvestor && selectedRound && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "rgba(0,0,0,0.6)" }}>
          <div className="glass-card p-6 w-full max-w-lg" style={{ cursor: "default", background: "var(--color-bg-card)" }}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Add Investor to {selectedRound.round_name}</h3>
              <button onClick={() => setShowAddInvestor(false)} className="text-sm" style={{ color: "var(--color-text-muted)" }}>Close</button>
            </div>
            <form onSubmit={handleAddInvestor} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Investor Name *</label>
                  <input
                    type="text"
                    required
                    value={investorForm.investor_name}
                    onChange={(e) => setInvestorForm({ ...investorForm, investor_name: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="Investor name"
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Email</label>
                  <input
                    type="email"
                    value={investorForm.investor_email}
                    onChange={(e) => setInvestorForm({ ...investorForm, investor_email: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="investor@fund.com"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Type</label>
                  <select
                    value={investorForm.investor_type}
                    onChange={(e) => setInvestorForm({ ...investorForm, investor_type: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  >
                    <option value="angel">Angel</option>
                    <option value="vc">VC</option>
                    <option value="institutional">Institutional</option>
                    <option value="strategic">Strategic</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Entity / Fund</label>
                  <input
                    type="text"
                    value={investorForm.investor_entity}
                    onChange={(e) => setInvestorForm({ ...investorForm, investor_entity: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                    placeholder="Fund name"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm mb-1" style={{ color: "var(--color-text-muted)" }}>Investment Amount (Rs) *</label>
                <input
                  type="number"
                  required
                  min={1}
                  value={investorForm.investment_amount}
                  onChange={(e) => setInvestorForm({ ...investorForm, investment_amount: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg text-sm"
                  style={{ background: "rgba(255,255,255,0.04)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
                  placeholder="2500000"
                />
                {investorForm.investment_amount && (
                  <div className="text-[10px] mt-0.5" style={{ color: "var(--color-text-muted)" }}>
                    {formatCurrency(parseFloat(investorForm.investment_amount) || 0)}
                  </div>
                )}
              </div>
              <button type="submit" className="btn-primary w-full text-center justify-center">
                Add Investor
              </button>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
