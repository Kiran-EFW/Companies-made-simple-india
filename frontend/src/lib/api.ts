const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// ---------------------------------------------------------------------------
// Generic fetch wrapper
// ---------------------------------------------------------------------------

export async function apiCall(path: string, options: RequestInit = {}): Promise<any> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    let message =
      body?.error?.message || body?.detail || `Request failed (${res.status})`;
    // Include specific validation field errors if present
    if (body?.error?.details && Array.isArray(body.error.details)) {
      const fieldErrors = body.error.details
        .map((d: any) => d.message)
        .filter(Boolean);
      if (fieldErrors.length > 0) {
        message = fieldErrors.join(". ");
      }
    }
    throw new Error(message);
  }

  if (res.status === 204) return null;
  return res.json();
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface StateOption {
  value: string;
  label: string;
  stamp_duty_rate?: number;
}

export interface PricingResponse {
  entity_type: string;
  plan_tier: string;
  state: string;
  state_display: string;
  authorized_capital: number;
  num_directors: number;
  platform_fee: number;
  government_fees: {
    name_reservation: number;
    filing_fee: number;
    roc_registration: number;
    section8_license: number;
    stamp_duty: {
      moa_stamp_duty: number;
      aoa_stamp_duty: number;
      deed_stamp_duty: number;
      total_stamp_duty: number;
    };
    pan_tan: number;
    subtotal: number;
  };
  dsc: {
    total_dsc: number;
    num_directors: number;
    dsc_per_unit: number;
    token_per_unit: number;
  };
  grand_total: number;
  optimization_tip?: {
    cheapest_state: string;
    potential_saving: number;
    cheapest_state_display: string;
  };
  partnership_fees?: {
    rof_registration_fee: number;
    deed_stamp_duty: number;
    pan_application_fee: number;
  };
  public_limited_recurring?: {
    secretarial_audit_annual: number;
    cs_compliance_annual: number;
    note: string;
  };
}

export interface WizardResponse {
  recommended: {
    entity_type: string;
    name: string;
    match_score: number;
    best_for: string;
    pros: string[];
    cons: string[];
    [k: string]: any;
  };
  alternatives: {
    entity_type: string;
    name: string;
    match_score: number;
    reason?: string;
    [k: string]: any;
  }[];
  [k: string]: any;
}

// ---------------------------------------------------------------------------
// Auth helpers (used by login / signup pages via apiCall directly)
// ---------------------------------------------------------------------------

// Login / signup hit apiCall("/auth/login", ...) directly.

// ---------------------------------------------------------------------------
// Companies
// ---------------------------------------------------------------------------

export async function getCompanies(): Promise<any> {
  return apiCall("/companies");
}

export async function createDraftCompany(data: any): Promise<any> {
  return apiCall("/companies", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateOnboarding(companyId: number, data: any): Promise<any> {
  return apiCall(`/companies/${companyId}/onboarding`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function getCompanyLogs(companyId: number): Promise<any> {
  return apiCall(`/companies/${companyId}/logs`);
}

export async function getPitchProfile(companyId: number) {
  return apiCall(`/companies/${companyId}/pitch-profile`);
}

export async function updatePitchProfile(companyId: number, data: Record<string, any>) {
  return apiCall(`/companies/${companyId}/pitch-profile`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function getCompanyTasks(companyId: number): Promise<any> {
  return apiCall(`/companies/${companyId}/tasks`);
}

// ---------------------------------------------------------------------------
// Company Info
// ---------------------------------------------------------------------------

export async function updateCompanyInfo(companyId: number, data: Record<string, any>): Promise<any> {
  return apiCall(`/companies/${companyId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function getCompanyDocuments(companyId: number): Promise<any> {
  return apiCall(`/companies/${companyId}/documents`);
}

// ---------------------------------------------------------------------------
// Documents
// ---------------------------------------------------------------------------

export async function uploadDocument(companyId: number, docType: string, file: File): Promise<any> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("doc_type", docType);

  const headers: Record<string, string> = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  formData.append("company_id", String(companyId));

  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message || "Upload failed");
  }

  return res.json();
}

export async function uploadPitchDeck(companyId: number, file: File): Promise<any> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("company_id", String(companyId));

  const headers: Record<string, string> = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}/documents/pitch-deck/upload`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail || "Pitch deck upload failed");
  }

  return res.json();
}

export function getInvestorPitchDeckUrl(token: string, companyId: number): string {
  return `${API_BASE}/investor-portal/${token}/companies/${companyId}/pitch-deck`;
}

// ---------------------------------------------------------------------------
// Payments
// ---------------------------------------------------------------------------

export async function createPaymentOrder(companyId: number): Promise<any> {
  return apiCall("/payments/create-order", {
    method: "POST",
    body: JSON.stringify({ company_id: companyId }),
  });
}

export async function verifyPayment(data: {
  razorpay_order_id: string;
  razorpay_payment_id: string;
  razorpay_signature: string;
}): Promise<any> {
  return apiCall("/payments/verify", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ---------------------------------------------------------------------------
// Messages (two-way conversation with admin)
// ---------------------------------------------------------------------------

export async function getCompanyMessages(companyId: number): Promise<any> {
  return apiCall(`/companies/${companyId}/messages`);
}

export async function sendMessage(companyId: number, content: string): Promise<any> {
  return apiCall(`/companies/${companyId}/messages`, {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

export async function markMessagesRead(companyId: number): Promise<any> {
  return apiCall(`/companies/${companyId}/messages/read`, { method: "PUT" });
}

// ---------------------------------------------------------------------------
// Notifications
// ---------------------------------------------------------------------------

export async function getNotifications(skip?: number, limit?: number): Promise<any> {
  const qs = new URLSearchParams();
  if (skip != null) qs.set("skip", String(skip));
  if (limit != null) qs.set("limit", String(limit));
  const query = qs.toString();
  return apiCall(`/notifications${query ? `?${query}` : ""}`);
}

export async function getUnreadCount(): Promise<any> {
  return apiCall("/notifications/unread-count");
}

export async function markNotificationRead(id: number): Promise<any> {
  return apiCall(`/notifications/${id}/read`, { method: "PUT" });
}

export async function markAllNotificationsRead(): Promise<any> {
  return apiCall("/notifications/read-all", { method: "PUT" });
}

export async function deleteNotification(id: number): Promise<any> {
  return apiCall(`/notifications/${id}`, { method: "DELETE" });
}

export async function getNotificationPreferences(): Promise<any> {
  return apiCall("/notifications/preferences");
}

export async function updateNotificationPreferences(data: any): Promise<any> {
  return apiCall("/notifications/preferences", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

// ---------------------------------------------------------------------------
// Chatbot
// ---------------------------------------------------------------------------

export async function sendChatMessage(
  data: { message: string; company_id?: number; conversation_history?: any[] },
): Promise<any> {
  return apiCall("/chatbot/message", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getSuggestedQuestions(companyId?: number): Promise<any> {
  const qs = companyId ? `?company_id=${companyId}` : "";
  return apiCall(`/chatbot/suggested-questions${qs}`);
}

// ---------------------------------------------------------------------------
// Workflow / Post-Incorporation
// ---------------------------------------------------------------------------

export async function getWorkflowStatus(companyId: number): Promise<any> {
  return apiCall(`/companies/${companyId}/workflow`);
}

export async function triggerNextStep(companyId: number): Promise<any> {
  return apiCall(`/companies/${companyId}/workflow/next`, {
    method: "POST",
  });
}

// ---------------------------------------------------------------------------
// Compliance
// ---------------------------------------------------------------------------

export async function getComplianceScore(companyId: number): Promise<any> {
  return apiCall(`/companies/${companyId}/compliance/score`);
}

export async function getComplianceCalendar(companyId: number): Promise<any> {
  return apiCall(`/companies/${companyId}/compliance/calendar`);
}

export async function getUpcomingDeadlines(companyId: number): Promise<any> {
  return apiCall(`/companies/${companyId}/compliance/upcoming`);
}

export async function getOverdueTasks(companyId: number): Promise<any> {
  return apiCall(`/companies/${companyId}/compliance/overdue`);
}

export async function generateComplianceTasks(companyId: number): Promise<any> {
  return apiCall(`/companies/${companyId}/compliance/generate`, { method: "POST" });
}

export async function updateComplianceTask(
  companyId: number,
  taskId: number,
  data: any,
): Promise<any> {
  return apiCall(`/companies/${companyId}/compliance/tasks/${taskId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function getPenaltyEstimate(companyId: number): Promise<any> {
  return apiCall(`/companies/${companyId}/compliance/penalty-estimate`);
}

export async function calculateTds(companyId: number, data: any): Promise<any> {
  return apiCall(`/companies/${companyId}/compliance/tds/calculate`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getTdsSections(companyId: number): Promise<any> {
  return apiCall(`/companies/${companyId}/compliance/tds/sections`);
}

export async function getGstDashboard(companyId: number): Promise<any> {
  return apiCall(`/companies/${companyId}/compliance/gst/dashboard`);
}

export async function getTaxOverview(companyId: number): Promise<any> {
  return apiCall(`/companies/${companyId}/compliance/tax/overview`);
}

export async function getAuditPack(companyId: number): Promise<any> {
  return apiCall(`/companies/${companyId}/compliance/audit-pack`);
}

// ---------------------------------------------------------------------------
// Profile
// ---------------------------------------------------------------------------

export async function updateProfile(data: {
  full_name?: string;
  phone?: string;
}): Promise<any> {
  return apiCall("/auth/profile", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function changePassword(data: {
  current_password: string;
  new_password: string;
}): Promise<any> {
  return apiCall("/auth/password", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

// ---------------------------------------------------------------------------
// Legal Document Templates
// ---------------------------------------------------------------------------

export async function getLegalTemplates(): Promise<any> {
  return apiCall("/legal-docs/templates");
}

export async function getLegalTemplateDefinition(type: string): Promise<any> {
  return apiCall(`/legal-docs/templates/${type}`);
}

export async function getClausePreview(type: string, clauseId: string, value: string): Promise<any> {
  return apiCall(`/legal-docs/templates/${type}/clauses/${clauseId}/preview?value=${encodeURIComponent(value)}`);
}

export async function createLegalDraft(data: { template_type: string; company_id?: number; title?: string }): Promise<any> {
  return apiCall("/legal-docs/drafts", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getLegalDrafts(): Promise<any> {
  return apiCall("/legal-docs/drafts");
}

export async function getLegalDraft(id: number): Promise<any> {
  return apiCall(`/legal-docs/drafts/${id}`);
}

export async function updateLegalDraftClauses(id: number, clauses_config: Record<string, any>): Promise<any> {
  return apiCall(`/legal-docs/drafts/${id}/clauses`, {
    method: "PUT",
    body: JSON.stringify({ clauses_config }),
  });
}

export async function generateLegalPreview(id: number): Promise<any> {
  return apiCall(`/legal-docs/drafts/${id}/preview`, { method: "POST" });
}

export async function finalizeLegalDocument(id: number): Promise<any> {
  return apiCall(`/legal-docs/drafts/${id}/finalize`, { method: "POST" });
}

export async function downloadLegalDocument(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/legal-docs/drafts/${id}/download-pdf`, {
    headers: {
      Authorization: `Bearer ${typeof window !== "undefined" ? localStorage.getItem("access_token") : ""}`,
    },
  });
  if (!res.ok) {
    // Fall back to HTML download if PDF generation is unavailable
    const fallback = await fetch(`${API_BASE}/legal-docs/drafts/${id}/download`, {
      headers: {
        Authorization: `Bearer ${typeof window !== "undefined" ? localStorage.getItem("access_token") : ""}`,
      },
    });
    if (!fallback.ok) throw new Error("Download failed");
    const blob = await fallback.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `legal-document-${id}.html`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    return;
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `legal-document-${id}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

// ---------------------------------------------------------------------------
// Statutory Registers
// ---------------------------------------------------------------------------

export async function getRegisters(companyId: number) {
  return apiCall(`/companies/${companyId}/registers`);
}

export async function getRegister(companyId: number, registerType: string) {
  return apiCall(`/companies/${companyId}/registers/${registerType}`);
}

export async function addRegisterEntry(companyId: number, registerType: string, data: any) {
  return apiCall(`/companies/${companyId}/registers/${registerType}/entries`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateRegisterEntry(companyId: number, registerType: string, entryId: number, data: any) {
  return apiCall(`/companies/${companyId}/registers/${registerType}/entries/${entryId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function getRegistersSummary(companyId: number) {
  return apiCall(`/companies/${companyId}/registers/summary`);
}

export async function exportRegister(companyId: number, registerType: string) {
  return apiCall(`/companies/${companyId}/registers/${registerType}/export`);
}

// ---------------------------------------------------------------------------
// Meeting Management
// ---------------------------------------------------------------------------

export async function createMeeting(companyId: number, data: any) {
  return apiCall(`/companies/${companyId}/meetings`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getMeetings(companyId: number, params?: Record<string, string>) {
  const query = params ? "?" + new URLSearchParams(params).toString() : "";
  return apiCall(`/companies/${companyId}/meetings${query}`);
}

export async function getMeeting(companyId: number, meetingId: number) {
  return apiCall(`/companies/${companyId}/meetings/${meetingId}`);
}

export async function updateMeeting(companyId: number, meetingId: number, data: any) {
  return apiCall(`/companies/${companyId}/meetings/${meetingId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function generateMeetingNotice(companyId: number, meetingId: number) {
  return apiCall(`/companies/${companyId}/meetings/${meetingId}/notice`, { method: "POST" });
}

export async function updateMeetingAttendance(companyId: number, meetingId: number, data: any) {
  return apiCall(`/companies/${companyId}/meetings/${meetingId}/attendance`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function updateMeetingAgenda(companyId: number, meetingId: number, data: any) {
  return apiCall(`/companies/${companyId}/meetings/${meetingId}/agenda`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function generateMeetingMinutes(companyId: number, meetingId: number) {
  return apiCall(`/companies/${companyId}/meetings/${meetingId}/minutes`, { method: "POST" });
}

export async function signMeetingMinutes(companyId: number, meetingId: number, data: any) {
  return apiCall(`/companies/${companyId}/meetings/${meetingId}/minutes/sign`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function updateMeetingResolutions(companyId: number, meetingId: number, data: any) {
  return apiCall(`/companies/${companyId}/meetings/${meetingId}/resolutions`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function getUpcomingMeetings(companyId: number) {
  return apiCall(`/companies/${companyId}/meetings/upcoming`);
}

export async function getPendingMinutes(companyId: number) {
  return apiCall(`/companies/${companyId}/meetings/minutes-pending`);
}

// ---------------------------------------------------------------------------
// Data Room
// ---------------------------------------------------------------------------

export async function getDataRoomFolders(companyId: number) {
  return apiCall(`/companies/${companyId}/data-room/folders`);
}

export async function createDataRoomFolder(companyId: number, data: any) {
  return apiCall(`/companies/${companyId}/data-room/folders`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getDataRoomFiles(companyId: number, params?: Record<string, string>) {
  const query = params ? "?" + new URLSearchParams(params).toString() : "";
  return apiCall(`/companies/${companyId}/data-room/files${query}`);
}

export async function uploadDataRoomFile(companyId: number, folderId: number, file: File, metadata?: any) {
  const formData = new FormData();
  formData.append("file", file);
  if (metadata?.description) formData.append("description", metadata.description);
  if (metadata?.tags) formData.append("tags", JSON.stringify(metadata.tags));
  if (metadata?.retention_category) formData.append("retention_category", metadata.retention_category);

  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  const res = await fetch(`${API_BASE}/companies/${companyId}/data-room/folders/${folderId}/files`, {
    method: "POST",
    headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    body: formData,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function downloadDataRoomFile(companyId: number, fileId: number) {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  const res = await fetch(`${API_BASE}/companies/${companyId}/data-room/files/${fileId}/download`, {
    headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
  });
  if (!res.ok) throw new Error("Download failed");
  const blob = await res.blob();
  return blob;
}

export async function createShareLink(companyId: number, data: any) {
  return apiCall(`/companies/${companyId}/data-room/share-links`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getShareLinks(companyId: number) {
  return apiCall(`/companies/${companyId}/data-room/share-links`);
}

export async function setupDefaultDataRoom(companyId: number) {
  return apiCall(`/companies/${companyId}/data-room/setup-defaults`, { method: "POST" });
}

export async function getRetentionAlerts(companyId: number) {
  return apiCall(`/companies/${companyId}/data-room/retention/alerts`);
}

export async function getRetentionSummary(companyId: number) {
  return apiCall(`/companies/${companyId}/data-room/retention/summary`);
}

// ---------------------------------------------------------------------------
// E-Signature
// ---------------------------------------------------------------------------

export async function createSignatureRequest(data: any) {
  return apiCall("/esign/requests", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getSignatureRequests() {
  return apiCall("/esign/requests");
}

export async function getSignatureRequest(requestId: number) {
  return apiCall(`/esign/requests/${requestId}`);
}

export async function sendSigningEmails(requestId: number) {
  return apiCall(`/esign/requests/${requestId}/send`, { method: "POST" });
}

export async function sendSigningReminder(requestId: number) {
  return apiCall(`/esign/requests/${requestId}/remind`, { method: "POST" });
}

export async function cancelSignatureRequest(requestId: number) {
  return apiCall(`/esign/requests/${requestId}/cancel`, { method: "POST" });
}

export async function getSignatureAuditTrail(requestId: number) {
  return apiCall(`/esign/requests/${requestId}/audit-trail`);
}

export async function getSignedDocument(requestId: number) {
  return apiCall(`/esign/requests/${requestId}/signed-document`);
}

export async function getSignatureCertificate(requestId: number) {
  return apiCall(`/esign/requests/${requestId}/certificate`);
}

// Public signing endpoints (no auth)
export async function getSigningPageData(accessToken: string) {
  const res = await fetch(`${API_BASE}/esign/sign/${accessToken}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function submitSignature(accessToken: string, data: any) {
  const res = await fetch(`${API_BASE}/esign/sign/${accessToken}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function declineSignature(accessToken: string, reason: string) {
  const res = await fetch(`${API_BASE}/esign/sign/${accessToken}/decline`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ---------------------------------------------------------------------------
// PDF Downloads
// ---------------------------------------------------------------------------

export function getLegalDocPdfUrl(draftId: number) {
  return `${API_BASE}/legal-docs/drafts/${draftId}/download-pdf`;
}

export function getSignedDocPdfUrl(requestId: number) {
  return `${API_BASE}/esign/requests/${requestId}/signed-document-pdf`;
}

export function getPaymentReceiptUrl(paymentId: number) {
  return `${API_BASE}/invoices/payments/${paymentId}/receipt`;
}

export function getPaymentReceiptPdfUrl(paymentId: number) {
  return `${API_BASE}/invoices/payments/${paymentId}/receipt-pdf`;
}

export function getPaymentInvoiceUrl(paymentId: number) {
  return `${API_BASE}/invoices/payments/${paymentId}/invoice`;
}

// ---------------------------------------------------------------------------
// Cap Table
// ---------------------------------------------------------------------------

export async function getCapTable(companyId: number) {
  return apiCall(`/companies/${companyId}/cap-table`);
}

export async function addShareholder(companyId: number, data: any) {
  return apiCall(`/companies/${companyId}/cap-table/shareholders`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function transferShares(companyId: number, data: any) {
  return apiCall(`/companies/${companyId}/cap-table/transfer`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function allotShares(companyId: number, data: any) {
  return apiCall(`/companies/${companyId}/cap-table/allotment`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getDilutionPreview(companyId: number) {
  return apiCall(`/companies/${companyId}/cap-table/dilution-preview`);
}

export async function exportCapTable(companyId: number) {
  return apiCall(`/companies/${companyId}/cap-table/export`);
}

export async function getCapTableTransactions(companyId: number) {
  return apiCall(`/companies/${companyId}/cap-table/transactions`);
}

export async function simulateRound(companyId: number, data: {
  pre_money_valuation: number;
  investment_amount: number;
  esop_pool_pct?: number;
  investors?: { name: string; amount: number }[];
  round_name?: string;
}) {
  return apiCall(`/companies/${companyId}/cap-table/simulate-round`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function simulateExit(companyId: number, data: {
  exit_valuation: number;
  liquidation_preference?: number;
  participating_preferred?: boolean;
}) {
  return apiCall(`/companies/${companyId}/cap-table/simulate-exit`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function saveCapTableScenario(companyId: number, data: {
  scenario_name: string;
  scenario_type: string;
  scenario_data: any;
}) {
  return apiCall(`/companies/${companyId}/cap-table/scenarios`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function simulateExitWaterfall(companyId: number, data: {
  exit_valuation: number;
  liquidation_preferences?: { shareholder_id: number; multiple: number; invested_amount: number }[];
  participating_preferred?: boolean;
}) {
  return apiCall(`/companies/${companyId}/cap-table/simulate-exit-waterfall`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getShareCertificate(companyId: number, shareholderId: number) {
  return apiCall(`/companies/${companyId}/cap-table/shareholders/${shareholderId}/certificate`);
}

// ---------------------------------------------------------------------------
// Stakeholders
// ---------------------------------------------------------------------------

export async function getStakeholderPortfolio() {
  return apiCall("/stakeholders/me/portfolio");
}

export async function getStakeholderCompanyDetail(companyId: number) {
  return apiCall(`/stakeholders/me/companies/${companyId}`);
}

export async function createStakeholderProfile(data: {
  name: string;
  email: string;
  phone?: string;
  stakeholder_type: string;
  entity_name?: string;
  entity_type?: string;
  pan_number?: string;
  is_foreign?: boolean;
}) {
  return apiCall("/stakeholders/profiles", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateStakeholderProfile(profileId: number, data: any) {
  return apiCall(`/stakeholders/profiles/${profileId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function getStakeholderProfiles(companyId?: number) {
  const qs = companyId ? `?company_id=${companyId}` : "";
  return apiCall(`/stakeholders/profiles${qs}`);
}

export async function getStakeholderProfile(profileId: number) {
  return apiCall(`/stakeholders/profiles/${profileId}`);
}

export async function linkStakeholderToShareholder(profileId: number, shareholderId: number) {
  return apiCall(`/stakeholders/profiles/${profileId}/link/${shareholderId}`, {
    method: "POST",
  });
}

// ---------------------------------------------------------------------------
// Founder Education / Learning Journey
// ---------------------------------------------------------------------------

export async function getLearningPath() {
  return apiCall("/founder-education/learning-path");
}

export async function getEducationStage(stageId: string) {
  return apiCall(`/founder-education/stages/${stageId}`);
}

export async function getTemplateContext(templateType: string) {
  return apiCall(`/founder-education/templates/${templateType}/context`);
}

export async function getTemplateStage(templateType: string) {
  return apiCall(`/founder-education/templates/${templateType}/stage`);
}

// ---------------------------------------------------------------------------
// Services Marketplace
// ---------------------------------------------------------------------------

export interface ServiceDefinition {
  key: string;
  name: string;
  short_description: string;
  category: string;
  platform_fee: number;
  government_fee: number;
  total: number;
  frequency: string;
  entity_types: string[];
  is_mandatory: boolean;
  penalty_note?: string;
  badge?: string;
}

export interface SubscriptionPlanDef {
  key: string;
  name: string;
  target: string;
  monthly_price: number;
  annual_price: number;
  features: string[];
  highlighted: boolean;
  entity_types: string[];
  is_peace_of_mind?: boolean;
  not_included_note?: string;
}

export interface ServiceRequestOut {
  id: number;
  company_id: number;
  service_key: string;
  service_name: string;
  category: string;
  platform_fee: number;
  government_fee: number;
  total_amount: number;
  status: string;
  notes?: string;
  is_paid: boolean;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface SubscriptionOut {
  id: number;
  company_id: number;
  plan_key: string;
  plan_name: string;
  interval: string;
  amount: number;
  status: string;
  current_period_start?: string;
  current_period_end?: string;
  created_at: string;
  cancelled_at?: string;
}

export interface UpsellItem {
  service_key: string;
  name: string;
  short_description: string;
  category: string;
  total: number;
  urgency: string;
  reason: string;
  badge?: string;
}

export async function getServicesCatalog(entityType?: string): Promise<ServiceDefinition[]> {
  const qs = entityType ? `?entity_type=${entityType}` : "";
  return apiCall(`/services/catalog${qs}`);
}

export async function getSubscriptionPlans(entityType?: string): Promise<SubscriptionPlanDef[]> {
  const qs = entityType ? `?entity_type=${entityType}` : "";
  return apiCall(`/services/plans${qs}`);
}

export async function createServiceRequest(data: {
  company_id: number;
  service_key: string;
  notes?: string;
}): Promise<ServiceRequestOut> {
  return apiCall("/services/requests", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getServiceRequests(companyId?: number): Promise<ServiceRequestOut[]> {
  const qs = companyId ? `?company_id=${companyId}` : "";
  return apiCall(`/services/requests${qs}`);
}

export async function cancelServiceRequest(requestId: number): Promise<ServiceRequestOut> {
  return apiCall(`/services/requests/${requestId}/cancel`, { method: "POST" });
}

export async function payForServiceRequest(requestId: number): Promise<any> {
  return apiCall(`/services/requests/${requestId}/pay`, { method: "POST" });
}

export async function createSubscription(data: {
  company_id: number;
  plan_key: string;
  interval?: string;
}): Promise<SubscriptionOut> {
  return apiCall("/services/subscriptions", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getSubscriptions(companyId?: number): Promise<SubscriptionOut[]> {
  const qs = companyId ? `?company_id=${companyId}` : "";
  return apiCall(`/services/subscriptions${qs}`);
}

export async function payForSubscription(subId: number): Promise<any> {
  return apiCall(`/services/subscriptions/${subId}/pay`, { method: "POST" });
}

export async function cancelSubscription(subId: number): Promise<SubscriptionOut> {
  return apiCall(`/services/subscriptions/${subId}/cancel`, { method: "POST" });
}

export async function getUpsellItems(companyId: number): Promise<UpsellItem[]> {
  return apiCall(`/services/upsell/${companyId}`);
}

// ---------------------------------------------------------------------------
// Accounting Integration
// ---------------------------------------------------------------------------

export interface AccountingConnectionOut {
  id: number;
  company_id: number;
  platform: string;
  status: string;
  zoho_org_name?: string;
  tally_host?: string;
  tally_port?: number;
  tally_company_name?: string;
  last_sync_at?: string;
  last_sync_status?: string;
  created_at: string;
}

export async function getZohoAuthUrl(companyId: number): Promise<{ auth_url: string }> {
  return apiCall(`/accounting/zoho/auth-url?company_id=${companyId}`);
}

export async function connectZohoBooks(data: { company_id: number; code: string }): Promise<AccountingConnectionOut> {
  return apiCall("/accounting/zoho/connect", { method: "POST", body: JSON.stringify(data) });
}

export async function connectTally(data: {
  company_id: number;
  host?: string;
  port?: number;
  company_name: string;
}): Promise<AccountingConnectionOut> {
  return apiCall("/accounting/tally/connect", { method: "POST", body: JSON.stringify(data) });
}

export async function getAccountingConnection(companyId: number): Promise<AccountingConnectionOut> {
  return apiCall(`/accounting/connection/${companyId}`);
}

export async function getAccountingConnections(): Promise<AccountingConnectionOut[]> {
  return apiCall("/accounting/connections");
}

export async function disconnectAccounting(companyId: number): Promise<void> {
  return apiCall(`/accounting/disconnect/${companyId}`, { method: "POST" });
}

export async function syncAccountingData(companyId: number): Promise<any> {
  return apiCall(`/accounting/sync/${companyId}`, { method: "POST" });
}

// ---------------------------------------------------------------------------
// ESOP Management
// ---------------------------------------------------------------------------

export async function getESOPPlans(companyId: number) {
  return apiCall(`/companies/${companyId}/esop/plans`);
}

export async function createESOPPlan(companyId: number, data: any) {
  return apiCall(`/companies/${companyId}/esop/plans`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getESOPPlan(companyId: number, planId: number) {
  return apiCall(`/companies/${companyId}/esop/plans/${planId}`);
}

export async function updateESOPPlan(companyId: number, planId: number, data: any) {
  return apiCall(`/companies/${companyId}/esop/plans/${planId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function activateESOPPlan(companyId: number, planId: number) {
  return apiCall(`/companies/${companyId}/esop/plans/${planId}/activate`, {
    method: "POST",
  });
}

export async function getESOPGrants(companyId: number, planId: number) {
  return apiCall(`/companies/${companyId}/esop/plans/${planId}/grants`);
}

export async function createESOPGrant(companyId: number, planId: number, data: any) {
  return apiCall(`/companies/${companyId}/esop/plans/${planId}/grants`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getCompanyESOPGrants(companyId: number) {
  return apiCall(`/companies/${companyId}/esop/grants`);
}

export async function getESOPGrant(companyId: number, grantId: number) {
  return apiCall(`/companies/${companyId}/esop/grants/${grantId}`);
}

export async function exerciseESOPOptions(companyId: number, grantId: number, data: { number_of_options: number }) {
  return apiCall(`/companies/${companyId}/esop/grants/${grantId}/exercise`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function generateESOPGrantLetter(companyId: number, grantId: number) {
  return apiCall(`/companies/${companyId}/esop/grants/${grantId}/generate-letter`, {
    method: "POST",
  });
}

export async function sendESOPGrantForSigning(companyId: number, grantId: number) {
  return apiCall(`/companies/${companyId}/esop/grants/${grantId}/send-for-signing`, {
    method: "POST",
  });
}

export async function getESOPSummary(companyId: number) {
  return apiCall(`/companies/${companyId}/esop/summary`);
}

// ---------------------------------------------------------------------------
// Fundraising
// ---------------------------------------------------------------------------

export async function createFundingRound(companyId: number, data: any) {
  return apiCall(`/companies/${companyId}/fundraising/rounds`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getFundingRounds(companyId: number) {
  return apiCall(`/companies/${companyId}/fundraising/rounds`);
}

export async function getFundingRound(companyId: number, roundId: number) {
  return apiCall(`/companies/${companyId}/fundraising/rounds/${roundId}`);
}

export async function updateFundingRound(companyId: number, roundId: number, data: any) {
  return apiCall(`/companies/${companyId}/fundraising/rounds/${roundId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function addRoundInvestor(companyId: number, roundId: number, data: any) {
  return apiCall(`/companies/${companyId}/fundraising/rounds/${roundId}/investors`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateRoundInvestor(companyId: number, roundId: number, investorId: number, data: any) {
  return apiCall(`/companies/${companyId}/fundraising/rounds/${roundId}/investors/${investorId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function removeRoundInvestor(companyId: number, roundId: number, investorId: number) {
  return apiCall(`/companies/${companyId}/fundraising/rounds/${roundId}/investors/${investorId}`, {
    method: "DELETE",
  });
}

export async function linkRoundDocument(companyId: number, roundId: number, data: { doc_type: string; document_id: number }) {
  return apiCall(`/companies/${companyId}/fundraising/rounds/${roundId}/link-document`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function initiateClosing(companyId: number, roundId: number, data: { documents_to_sign: string[] }) {
  return apiCall(`/companies/${companyId}/fundraising/rounds/${roundId}/initiate-closing`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getClosingRoom(companyId: number, roundId: number) {
  return apiCall(`/companies/${companyId}/fundraising/rounds/${roundId}/closing-room`);
}

export async function completeAllotment(companyId: number, roundId: number, data?: { investor_ids?: number[] }) {
  return apiCall(`/companies/${companyId}/fundraising/rounds/${roundId}/complete-allotment`, {
    method: "POST",
    body: JSON.stringify(data || {}),
  });
}

// ---------------------------------------------------------------------------
// Investor Portal (public, no auth)
// ---------------------------------------------------------------------------

export async function getInvestorProfile(token: string) {
  const res = await fetch(`${API_BASE}/investor-portal/${token}/profile`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getInvestorPortfolio(token: string) {
  const res = await fetch(`${API_BASE}/investor-portal/${token}/portfolio`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getInvestorCompanyDetail(token: string, companyId: number) {
  const res = await fetch(`${API_BASE}/investor-portal/${token}/companies/${companyId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getInvestorCapTable(token: string, companyId: number) {
  const res = await fetch(`${API_BASE}/investor-portal/${token}/companies/${companyId}/cap-table`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getInvestorFundingRounds(token: string, companyId: number) {
  const res = await fetch(`${API_BASE}/investor-portal/${token}/companies/${companyId}/funding-rounds`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getInvestorESOPGrants(token: string, companyId: number) {
  const res = await fetch(`${API_BASE}/investor-portal/${token}/companies/${companyId}/esop-grants`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getInvestorDocuments(token: string, companyId: number) {
  const res = await fetch(`${API_BASE}/investor-portal/${token}/companies/${companyId}/documents`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getInvestorESOPSummary(token: string) {
  const res = await fetch(`${API_BASE}/investor-portal/${token}/esop-summary`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ---------------------------------------------------------------------------
// Investor Discovery / Matchmaking
// ---------------------------------------------------------------------------

export async function discoverCompanies(token: string, filters?: { sector?: string; stage?: string }) {
  const params = new URLSearchParams();
  if (filters?.sector) params.set("sector", filters.sector);
  if (filters?.stage) params.set("stage", filters.stage);
  const qs = params.toString() ? `?${params.toString()}` : "";
  const res = await fetch(`${API_BASE}/investor-portal/${token}/discover${qs}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function expressInterest(token: string, companyId: number, message?: string) {
  const res = await fetch(`${API_BASE}/investor-portal/${token}/interest/${companyId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(message ? { message } : {}),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function withdrawInterest(token: string, companyId: number) {
  const res = await fetch(`${API_BASE}/investor-portal/${token}/interest/${companyId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getMyInterests(token: string) {
  const res = await fetch(`${API_BASE}/investor-portal/${token}/my-interests`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getInvestorInterests(companyId: number) {
  return apiCall(`/companies/${companyId}/investor-interests`);
}

// ---------------------------------------------------------------------------
// Cap Table Onboarding
// ---------------------------------------------------------------------------

export async function quickCapTableSetup(data: {
  company_name: string;
  entity_type?: string;
  shareholders: { name: string; shares: number; email?: string; is_promoter?: boolean }[];
}) {
  return apiCall("/cap-table-onboarding/quick-setup", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ---------------------------------------------------------------------------
// Convertible Conversion
// ---------------------------------------------------------------------------

export async function previewConversion(companyId: number, roundId: number, triggerRoundId?: number) {
  const params = triggerRoundId ? `?trigger_round_id=${triggerRoundId}` : "";
  return apiCall(`/companies/${companyId}/fundraising/rounds/${roundId}/conversion-preview${params}`);
}

export async function convertRound(companyId: number, roundId: number, data?: { trigger_round_id?: number }) {
  return apiCall(`/companies/${companyId}/fundraising/rounds/${roundId}/convert`, {
    method: "POST",
    body: JSON.stringify(data || {}),
  });
}

// ---------------------------------------------------------------------------
// Valuations
// ---------------------------------------------------------------------------

export async function calculateNAV(companyId: number, data: { total_assets: number; total_liabilities: number; total_shares?: number }) {
  return apiCall(`/companies/${companyId}/valuations/calculate-nav`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function calculateDCF(companyId: number, data: { current_revenue: number; growth_rate: number; profit_margin: number; discount_rate: number; total_shares?: number }) {
  return apiCall(`/companies/${companyId}/valuations/calculate-dcf`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function createValuation(companyId: number, data: any) {
  return apiCall(`/companies/${companyId}/valuations`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function listValuations(companyId: number) {
  return apiCall(`/companies/${companyId}/valuations`);
}

export async function getLatestValuation(companyId: number) {
  return apiCall(`/companies/${companyId}/valuations/latest`);
}

// ---------------------------------------------------------------------------
// Company Members / Team Collaboration
// ---------------------------------------------------------------------------

export async function inviteCompanyMember(companyId: number, data: {
  email: string;
  name: string;
  role: string;
  din?: string;
  designation?: string;
  message?: string;
}) {
  return apiCall(`/companies/${companyId}/members/invite`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getCompanyMembers(companyId: number) {
  return apiCall(`/companies/${companyId}/members`);
}

export async function updateCompanyMember(companyId: number, memberId: number, data: {
  role?: string;
  designation?: string;
}) {
  return apiCall(`/companies/${companyId}/members/${memberId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function removeCompanyMember(companyId: number, memberId: number) {
  return apiCall(`/companies/${companyId}/members/${memberId}`, {
    method: "DELETE",
  });
}

export async function resendMemberInvite(companyId: number, memberId: number) {
  return apiCall(`/companies/${companyId}/members/${memberId}/resend`, {
    method: "POST",
  });
}

export async function getInviteInfo(token: string) {
  return apiCall(`/invites/${token}`);
}

export async function acceptInvite(token: string) {
  return apiCall(`/invites/${token}/accept`, { method: "POST" });
}

export async function declineInvite(token: string) {
  return apiCall(`/invites/${token}/decline`, { method: "POST" });
}

// ---------------------------------------------------------------------------
// CA Portal
// ---------------------------------------------------------------------------

export async function getCaDashboardSummary(): Promise<any> {
  return apiCall("/ca/dashboard-summary");
}

export async function getCaCompanies(): Promise<any> {
  return apiCall("/ca/companies");
}

export async function getCaCompanyCompliance(companyId: number): Promise<any> {
  return apiCall(`/ca/companies/${companyId}/compliance`);
}

export async function getCaCompanyDocuments(companyId: number): Promise<any> {
  return apiCall(`/ca/companies/${companyId}/documents`);
}

export async function markFilingComplete(companyId: number, taskId: number, filingReference: string): Promise<any> {
  return apiCall(`/ca/companies/${companyId}/filings/${taskId}`, {
    method: "PUT",
    body: JSON.stringify({ filing_reference: filingReference }),
  });
}

export async function getCaAllTasks(status?: string): Promise<any> {
  const query = status ? `?status=${status}` : "";
  return apiCall(`/ca/tasks${query}`);
}

export async function getCaCompanyScore(companyId: number): Promise<any> {
  return apiCall(`/ca/companies/${companyId}/score`);
}

export async function getCaCompanyPenalties(companyId: number): Promise<any> {
  return apiCall(`/ca/companies/${companyId}/penalties`);
}

export async function getCaAllScores(): Promise<any> {
  return apiCall("/ca/scores");
}

export async function getCaTaxOverview(companyId: number): Promise<any> {
  return apiCall(`/ca/companies/${companyId}/tax-overview`);
}

export async function getCaGstDashboard(companyId: number): Promise<any> {
  return apiCall(`/ca/companies/${companyId}/gst-dashboard`);
}

export async function caTdsCalculate(data: {
  section: string;
  amount: number;
  payee_type?: string;
  has_pan?: boolean;
}): Promise<any> {
  return apiCall("/ca/tds/calculate", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getCaTdsSections(): Promise<any> {
  return apiCall("/ca/tds/sections");
}

export async function getCaTdsDueDates(quarter: string): Promise<any> {
  return apiCall(`/ca/tds/due-dates?quarter=${quarter}`);
}

export async function getCaAuditPack(companyId: number): Promise<any> {
  return apiCall(`/ca/companies/${companyId}/audit-pack`);
}

export async function addCaTaskNote(companyId: number, taskId: number, note: string): Promise<any> {
  return apiCall(`/ca/companies/${companyId}/tasks/${taskId}/notes`, {
    method: "POST",
    body: JSON.stringify({ note }),
  });
}

export async function getCaTaskNotes(companyId: number, taskId: number): Promise<any> {
  return apiCall(`/ca/companies/${companyId}/tasks/${taskId}/notes`);
}

// ---------------------------------------------------------------------------
// Admin/Ops functions have been moved to the separate admin-portal app.
// ---------------------------------------------------------------------------
