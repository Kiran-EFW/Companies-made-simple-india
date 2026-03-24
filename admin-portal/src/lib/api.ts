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
    const message =
      body?.error?.message || body?.detail || `Request failed (${res.status})`;
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
  platform_fee: number;
  government_fees: {
    name_reservation: number;
    filing_fee: number;
    roc_registration: number;
    section8_license: number;
    stamp_duty: { total_stamp_duty: number; [k: string]: any };
    pan_tan: number;
    subtotal: number;
    [k: string]: any;
  };
  dsc: {
    total_dsc: number;
    num_directors: number;
    dsc_per_unit: number;
    token_per_unit: number;
    [k: string]: any;
  };
  grand_total: number;
  optimization_tip?: {
    potential_saving: number;
    cheapest_state_display: string;
    [k: string]: any;
  };
  [k: string]: any;
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
  return apiCall(`/companies/${companyId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function getCompanyLogs(companyId: number): Promise<any> {
  return apiCall(`/companies/${companyId}/logs`);
}

export async function getCompanyTasks(companyId: number): Promise<any> {
  return apiCall(`/companies/${companyId}/tasks`);
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
  formData.append("company_id", String(companyId));

  const headers: Record<string, string> = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

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
// Admin — Companies
// ---------------------------------------------------------------------------

export async function getAdminCompanies(params?: {
  skip?: number;
  limit?: number;
  status?: string;
}): Promise<any> {
  const qs = new URLSearchParams();
  if (params?.skip != null) qs.set("skip", String(params.skip));
  if (params?.limit != null) qs.set("limit", String(params.limit));
  if (params?.status) qs.set("status", params.status);
  const query = qs.toString();
  return apiCall(`/admin/companies${query ? `?${query}` : ""}`);
}

export async function getAdminCompanyDetail(companyId: number): Promise<any> {
  return apiCall(`/admin/companies/${companyId}`);
}

export async function updateCompanyStatus(
  companyId: number,
  status: string,
  note?: string,
): Promise<any> {
  return apiCall(`/admin/companies/${companyId}/status`, {
    method: "PUT",
    body: JSON.stringify({ status, note }),
  });
}

export async function assignCompany(
  companyId: number,
  assigneeId: number,
): Promise<any> {
  return apiCall(`/admin/companies/${companyId}/assign`, {
    method: "PUT",
    body: JSON.stringify({ assigned_to: assigneeId }),
  });
}

export async function setCompanyPriority(
  companyId: number,
  priority: string,
): Promise<any> {
  return apiCall(`/admin/companies/${companyId}/priority`, {
    method: "PUT",
    body: JSON.stringify({ priority }),
  });
}

export async function sendAdminMessage(
  companyId: number,
  content: string,
): Promise<any> {
  return apiCall(`/admin/companies/${companyId}/messages`, {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

export async function getAdminCompanyMessages(companyId: number): Promise<any> {
  return apiCall(`/admin/companies/${companyId}/messages`);
}

export async function markAdminMessagesRead(companyId: number): Promise<any> {
  return apiCall(`/admin/companies/${companyId}/messages/read`, { method: "PUT" });
}

export async function addInternalNote(
  companyId: number,
  content: string,
): Promise<any> {
  return apiCall(`/admin/companies/${companyId}/notes`, {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

// ---------------------------------------------------------------------------
// Admin — Team
// ---------------------------------------------------------------------------

export async function getAdminTeam(): Promise<any> {
  return apiCall("/admin/users");
}

// ---------------------------------------------------------------------------
// Admin — Analytics
// ---------------------------------------------------------------------------

export async function getAdminAnalytics(): Promise<any> {
  return apiCall("/admin/analytics/summary");
}

export async function getAdminFunnel(): Promise<any> {
  return apiCall("/admin/analytics/funnel");
}

export async function getAdminRevenue(): Promise<any> {
  return apiCall("/admin/analytics/revenue");
}

export async function getSLAOverview(): Promise<any> {
  return apiCall("/admin/sla/overview");
}

export async function getSLABreaches(): Promise<any> {
  return apiCall("/admin/sla/breaches");
}

// ---------------------------------------------------------------------------
// Ops — Filing Tasks
// ---------------------------------------------------------------------------

export async function getFilingTasks(params?: {
  company_id?: number;
  status?: string;
  task_type?: string;
  assigned_to?: number;
  priority?: string;
  overdue_only?: boolean;
  skip?: number;
  limit?: number;
}): Promise<any> {
  const qs = new URLSearchParams();
  if (params?.company_id != null) qs.set("company_id", String(params.company_id));
  if (params?.status) qs.set("status", params.status);
  if (params?.task_type) qs.set("task_type", params.task_type);
  if (params?.assigned_to != null) qs.set("assigned_to", String(params.assigned_to));
  if (params?.priority) qs.set("priority", params.priority);
  if (params?.overdue_only) qs.set("overdue_only", "true");
  if (params?.skip != null) qs.set("skip", String(params.skip));
  if (params?.limit != null) qs.set("limit", String(params.limit));
  const query = qs.toString();
  return apiCall(`/ops/filing-tasks${query ? `?${query}` : ""}`);
}

export async function getFilingTask(taskId: number): Promise<any> {
  return apiCall(`/ops/filing-tasks/${taskId}`);
}

export async function createFilingTask(data: any): Promise<any> {
  return apiCall("/ops/filing-tasks", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateFilingTaskStatus(taskId: number, data: { status: string; notes?: string; completion_notes?: string }): Promise<any> {
  return apiCall(`/ops/filing-tasks/${taskId}/status`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function assignFilingTask(taskId: number, assignedTo: number): Promise<any> {
  return apiCall(`/ops/filing-tasks/${taskId}/assign`, {
    method: "PUT",
    body: JSON.stringify({ assigned_to: assignedTo }),
  });
}

export async function claimFilingTask(taskId: number): Promise<any> {
  return apiCall(`/ops/filing-tasks/${taskId}/claim`, { method: "POST" });
}

export async function generateFilingTasks(companyId: number, autoAssign: boolean = true): Promise<any> {
  return apiCall(`/ops/filing-tasks/generate/${companyId}?auto_assign=${autoAssign}`, { method: "POST" });
}

export async function handoffFilingTask(taskId: number, data: { reassign_to?: number; reason?: string }): Promise<any> {
  return apiCall(`/ops/filing-tasks/${taskId}/handoff`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ---------------------------------------------------------------------------
// Ops — My Queue
// ---------------------------------------------------------------------------

export async function getMyQueue(): Promise<any> {
  return apiCall("/ops/my-queue");
}

// ---------------------------------------------------------------------------
// Ops — Document Verification
// ---------------------------------------------------------------------------

export async function getReviewQueue(params?: {
  decision?: string;
  company_id?: number;
  reviewer_id?: number;
  skip?: number;
  limit?: number;
}): Promise<any> {
  const qs = new URLSearchParams();
  if (params?.decision) qs.set("decision", params.decision);
  if (params?.company_id != null) qs.set("company_id", String(params.company_id));
  if (params?.reviewer_id != null) qs.set("reviewer_id", String(params.reviewer_id));
  if (params?.skip != null) qs.set("skip", String(params.skip));
  if (params?.limit != null) qs.set("limit", String(params.limit));
  const query = qs.toString();
  return apiCall(`/ops/documents/review-queue${query ? `?${query}` : ""}`);
}

export async function claimDocReview(documentId: number): Promise<any> {
  return apiCall(`/ops/documents/${documentId}/claim-review`, { method: "POST" });
}

export async function verifyDocument(documentId: number, data: {
  decision: string;
  review_notes?: string;
  rejection_reason?: string;
  checklist?: { item: string; checked: boolean }[];
}): Promise<any> {
  return apiCall(`/ops/documents/${documentId}/verify`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

// ---------------------------------------------------------------------------
// Ops — Escalations
// ---------------------------------------------------------------------------

export async function getEscalations(params?: { is_resolved?: boolean; company_id?: number }): Promise<any> {
  const qs = new URLSearchParams();
  if (params?.is_resolved != null) qs.set("is_resolved", String(params.is_resolved));
  if (params?.company_id != null) qs.set("company_id", String(params.company_id));
  const query = qs.toString();
  return apiCall(`/ops/escalations${query ? `?${query}` : ""}`);
}

export async function resolveEscalation(escalationId: number, notes?: string): Promise<any> {
  return apiCall(`/ops/escalations/${escalationId}/resolve`, {
    method: "POST",
    body: JSON.stringify({ resolution_notes: notes }),
  });
}

export async function getEscalationRules(): Promise<any> {
  return apiCall("/ops/escalation-rules");
}

export async function createEscalationRule(data: any): Promise<any> {
  return apiCall("/ops/escalation-rules", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ---------------------------------------------------------------------------
// Ops — Workload & Performance
// ---------------------------------------------------------------------------

export async function getOpsWorkload(): Promise<any> {
  return apiCall("/ops/workload");
}

export async function getUserPerformance(userId: number, days?: number): Promise<any> {
  const qs = days ? `?days=${days}` : "";
  return apiCall(`/ops/performance/${userId}${qs}`);
}

export async function getAllPerformance(days?: number): Promise<any> {
  const qs = days ? `?days=${days}` : "";
  return apiCall(`/ops/performance${qs}`);
}

// ---------------------------------------------------------------------------
// Ops — Bulk Operations
// ---------------------------------------------------------------------------

export async function bulkAssignTasks(taskIds: number[], assignedTo: number): Promise<any> {
  return apiCall("/ops/bulk/assign", {
    method: "PUT",
    body: JSON.stringify({ task_ids: taskIds, assigned_to: assignedTo }),
  });
}

export async function bulkUpdateTaskStatus(taskIds: number[], status: string, notes?: string): Promise<any> {
  return apiCall("/ops/bulk/status", {
    method: "PUT",
    body: JSON.stringify({ task_ids: taskIds, status, notes }),
  });
}

// ---------------------------------------------------------------------------
// Ops — Staff
// ---------------------------------------------------------------------------

export async function getOpsStaff(params?: { department?: string; seniority?: string }): Promise<any> {
  const qs = new URLSearchParams();
  if (params?.department) qs.set("department", params.department);
  if (params?.seniority) qs.set("seniority", params.seniority);
  const query = qs.toString();
  return apiCall(`/ops/staff${query ? `?${query}` : ""}`);
}

export async function updateStaffHierarchy(userId: number, data: {
  department?: string;
  seniority?: string;
  reports_to?: number;
}): Promise<any> {
  return apiCall(`/ops/staff/${userId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteFilingTask(taskId: number): Promise<any> {
  return apiCall(`/ops/filing-tasks/${taskId}`, { method: "DELETE" });
}

export async function deleteEscalationRule(ruleId: number): Promise<any> {
  return apiCall(`/ops/escalation-rules/${ruleId}`, { method: "DELETE" });
}

export async function updateEscalationRule(ruleId: number, data: any): Promise<any> {
  return apiCall(`/ops/escalation-rules/${ruleId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function seedDefaultEscalationRules(): Promise<any> {
  return apiCall("/ops/escalation-rules/seed-defaults", { method: "POST" });
}

// ---------------------------------------------------------------------------
// Services & Compliance Management
// ---------------------------------------------------------------------------

export async function getAdminServiceRequests(params?: {
  status?: string;
  company_id?: number;
  skip?: number;
  limit?: number;
}): Promise<{ requests: any[]; total: number }> {
  const qs = new URLSearchParams();
  if (params?.status) qs.set("status", params.status);
  if (params?.company_id) qs.set("company_id", String(params.company_id));
  if (params?.skip) qs.set("skip", String(params.skip));
  if (params?.limit) qs.set("limit", String(params.limit));
  const q = qs.toString();
  return apiCall(`/admin/services/requests${q ? `?${q}` : ""}`);
}

export async function updateServiceRequestStatus(
  requestId: number,
  status: string,
  adminNotes?: string,
): Promise<any> {
  const qs = new URLSearchParams({ status });
  if (adminNotes) qs.set("admin_notes", adminNotes);
  return apiCall(`/admin/services/requests/${requestId}/status?${qs}`, { method: "PUT" });
}

export async function getAdminSubscriptions(params?: {
  status?: string;
  company_id?: number;
}): Promise<{ subscriptions: any[]; total: number }> {
  const qs = new URLSearchParams();
  if (params?.status) qs.set("status", params.status);
  if (params?.company_id) qs.set("company_id", String(params.company_id));
  const q = qs.toString();
  return apiCall(`/admin/services/subscriptions${q ? `?${q}` : ""}`);
}

export async function getServicesStats(): Promise<any> {
  return apiCall("/admin/services/stats");
}

// ---------------------------------------------------------------------------
// Marketplace Fulfillment (Admin)
// ---------------------------------------------------------------------------

export async function getMarketplacePartners(): Promise<any[]> {
  return apiCall("/marketplace/partners");
}

export async function verifyPartner(partnerId: number): Promise<any> {
  return apiCall(`/marketplace/partners/${partnerId}/verify`, { method: "PUT" });
}

export async function getAvailablePartners(category?: string): Promise<any[]> {
  const qs = category ? `?category=${category}` : "";
  return apiCall(`/marketplace/available-partners${qs}`);
}

export async function assignToPartner(data: {
  service_request_id: number;
  partner_id: number;
}): Promise<any> {
  return apiCall("/marketplace/assign", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function approveDelivery(fulfillmentId: number): Promise<any> {
  return apiCall(`/marketplace/fulfillments/${fulfillmentId}/approve`, {
    method: "POST",
  });
}

export async function requestRevision(
  fulfillmentId: number,
  note: string,
): Promise<any> {
  return apiCall(`/marketplace/fulfillments/${fulfillmentId}/revision`, {
    method: "POST",
    body: JSON.stringify({ note }),
  });
}

export async function getSettlements(): Promise<any[]> {
  return apiCall("/marketplace/settlements");
}

export async function markSettlementPaid(
  settlementId: number,
  data: { payment_reference: string; partner_invoice_number?: string },
): Promise<any> {
  return apiCall(`/marketplace/settlements/${settlementId}/mark-paid`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ---------------------------------------------------------------------------
// Admin Compliance Workflow
// ---------------------------------------------------------------------------

export async function getComplianceOverview(): Promise<any> {
  return apiCall("/admin/compliance/overview");
}

export async function getComplianceTasks(params?: {
  status?: string;
  company_id?: number;
  task_type?: string;
  skip?: number;
  limit?: number;
}): Promise<any> {
  const qs = new URLSearchParams();
  if (params?.status) qs.set("status", params.status);
  if (params?.company_id) qs.set("company_id", String(params.company_id));
  if (params?.task_type) qs.set("task_type", params.task_type);
  if (params?.skip) qs.set("skip", String(params.skip));
  if (params?.limit) qs.set("limit", String(params.limit));
  const q = qs.toString();
  return apiCall(`/admin/compliance/tasks${q ? `?${q}` : ""}`);
}

export async function adminUpdateComplianceTask(
  taskId: number,
  params: { status?: string; filing_reference?: string },
): Promise<any> {
  const qs = new URLSearchParams();
  if (params.status) qs.set("status", params.status);
  if (params.filing_reference) qs.set("filing_reference", params.filing_reference);
  return apiCall(`/admin/compliance/tasks/${taskId}?${qs.toString()}`, {
    method: "PUT",
  });
}
