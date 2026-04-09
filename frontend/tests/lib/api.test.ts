/**
 * Tests for src/lib/api.ts — every exported function.
 *
 * Strategy:
 *   - Mock global `fetch` and `localStorage`.
 *   - Thoroughly test apiCall (URL, headers, error paths, 204, subscription gating).
 *   - For the 100+ endpoint helpers, group by pattern and test representative
 *     samples in depth, while also asserting every single function at least once
 *     for URL/method/body correctness.
 */

const API_BASE = "http://localhost:8000/api/v1";

// ── localStorage mock ──────────────────────────────────────────────────────────
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: jest.fn((key: string) => store[key] ?? null),
    setItem: jest.fn((key: string, val: string) => {
      store[key] = val;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
    _setStore(s: Record<string, string>) {
      store = { ...s };
    },
  };
})();

Object.defineProperty(window, "localStorage", { value: localStorageMock });

// ── fetch mock ─────────────────────────────────────────────────────────────────
const mockFetch = jest.fn();
global.fetch = mockFetch as any;

// Utility: build a Response-like object returned by fetch
function jsonResponse(body: any, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: jest.fn().mockResolvedValue(body),
    text: jest.fn().mockResolvedValue(JSON.stringify(body)),
    blob: jest.fn().mockResolvedValue(new Blob()),
    headers: new Headers(),
  } as unknown as Response;
}

function noContentResponse(): Response {
  return {
    ok: true,
    status: 204,
    json: jest.fn(),
    text: jest.fn().mockResolvedValue(""),
    headers: new Headers(),
  } as unknown as Response;
}

// ── Import the module under test AFTER mocks are set up ────────────────────────
import * as api from "@/lib/api";

// ── Setup / teardown ───────────────────────────────────────────────────────────
beforeEach(() => {
  jest.clearAllMocks();
  localStorageMock._setStore({ access_token: "test-jwt-token" });
  // Default: return 200 with empty JSON
  mockFetch.mockResolvedValue(jsonResponse({}));
});

// =============================================================================
// 1. apiCall — generic fetch wrapper
// =============================================================================

describe("apiCall", () => {
  it("constructs the correct URL from path", async () => {
    await api.apiCall("/foo/bar");
    expect(mockFetch).toHaveBeenCalledWith(
      `${API_BASE}/foo/bar`,
      expect.any(Object),
    );
  });

  it("injects Authorization header when token exists", async () => {
    await api.apiCall("/test");
    const opts = mockFetch.mock.calls[0][1] as RequestInit;
    expect((opts.headers as Record<string, string>)["Authorization"]).toBe(
      "Bearer test-jwt-token",
    );
  });

  it("does NOT inject Authorization header when no token", async () => {
    localStorageMock._setStore({});
    await api.apiCall("/test");
    const opts = mockFetch.mock.calls[0][1] as RequestInit;
    expect((opts.headers as Record<string, string>)["Authorization"]).toBeUndefined();
  });

  it("sets Content-Type to application/json by default", async () => {
    await api.apiCall("/test");
    const opts = mockFetch.mock.calls[0][1] as RequestInit;
    expect((opts.headers as Record<string, string>)["Content-Type"]).toBe(
      "application/json",
    );
  });

  it("returns parsed JSON on success", async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({ hello: "world" }));
    const result = await api.apiCall("/test");
    expect(result).toEqual({ hello: "world" });
  });

  it("returns null on 204 No Content", async () => {
    mockFetch.mockResolvedValueOnce(noContentResponse());
    const result = await api.apiCall("/test");
    expect(result).toBeNull();
  });

  it("throws on 4xx with detail message", async () => {
    mockFetch.mockResolvedValueOnce(
      jsonResponse({ detail: "Not found" }, 404),
    );
    await expect(api.apiCall("/missing")).rejects.toThrow("Not found");
  });

  it("throws on 5xx with fallback message", async () => {
    const res = {
      ok: false,
      status: 500,
      json: jest.fn().mockRejectedValue(new Error("parse error")),
      headers: new Headers(),
    } as unknown as Response;
    mockFetch.mockResolvedValueOnce(res);
    await expect(api.apiCall("/boom")).rejects.toThrow("Request failed (500)");
  });

  it("throws with field validation errors joined", async () => {
    mockFetch.mockResolvedValueOnce(
      jsonResponse(
        {
          error: {
            message: "Validation",
            details: [
              { message: "Name required" },
              { message: "Email invalid" },
            ],
          },
        },
        422,
      ),
    );
    await expect(api.apiCall("/validate")).rejects.toThrow(
      "Name required. Email invalid",
    );
  });

  it("throws subscription gating error with extra fields on 403", async () => {
    mockFetch.mockResolvedValueOnce(
      jsonResponse(
        {
          detail: {
            error: "subscription_required",
            message: "Upgrade to Pro",
            required_tier: "pro",
            current_tier: "free",
            upgrade_url: "/upgrade",
          },
        },
        403,
      ),
    );
    try {
      await api.apiCall("/gated");
      fail("Should have thrown");
    } catch (err: any) {
      expect(err.message).toBe("Upgrade to Pro");
      expect(err.upgradeRequired).toBe(true);
      expect(err.requiredTier).toBe("pro");
      expect(err.currentTier).toBe("free");
      expect(err.upgradeUrl).toBe("/upgrade");
    }
  });

  it("passes through custom headers and options", async () => {
    await api.apiCall("/custom", {
      method: "PUT",
      headers: { "X-Custom": "yes" },
      body: '{"a":1}',
    });
    const opts = mockFetch.mock.calls[0][1] as RequestInit;
    expect(opts.method).toBe("PUT");
    expect((opts.headers as Record<string, string>)["X-Custom"]).toBe("yes");
    expect(opts.body).toBe('{"a":1}');
  });
});

// =============================================================================
// Helper: assert the last fetch call matched expected shape
// =============================================================================

function expectFetch(
  url: string,
  method = "GET",
  bodyContains?: Record<string, any>,
) {
  const [calledUrl, calledOpts] = mockFetch.mock.calls[
    mockFetch.mock.calls.length - 1
  ];
  expect(calledUrl).toBe(url);
  if (method !== "GET") {
    expect(calledOpts.method).toBe(method);
  }
  if (bodyContains) {
    const parsed = JSON.parse(calledOpts.body as string);
    expect(parsed).toMatchObject(bodyContains);
  }
}

// Also check that apiCall-based functions inject the auth header
function expectAuthHeader() {
  const opts = mockFetch.mock.calls[mockFetch.mock.calls.length - 1][1];
  expect((opts.headers as Record<string, string>)["Authorization"]).toBe(
    "Bearer test-jwt-token",
  );
}

// =============================================================================
// 2. Companies
// =============================================================================

describe("Companies", () => {
  it("getCompanies", async () => {
    await api.getCompanies();
    expectFetch(`${API_BASE}/companies`);
    expectAuthHeader();
  });

  it("createDraftCompany", async () => {
    await api.createDraftCompany({ entity_type: "pvt_ltd" });
    expectFetch(`${API_BASE}/companies`, "POST", { entity_type: "pvt_ltd" });
  });

  it("updateOnboarding", async () => {
    await api.updateOnboarding(5, { step: 2 });
    expectFetch(`${API_BASE}/companies/5/onboarding`, "PUT", { step: 2 });
  });

  it("getCompanyLogs", async () => {
    await api.getCompanyLogs(3);
    expectFetch(`${API_BASE}/companies/3/logs`);
  });

  it("getPitchProfile", async () => {
    await api.getPitchProfile(1);
    expectFetch(`${API_BASE}/companies/1/pitch-profile`);
  });

  it("updatePitchProfile", async () => {
    await api.updatePitchProfile(1, { tagline: "test" });
    expectFetch(`${API_BASE}/companies/1/pitch-profile`, "PATCH", {
      tagline: "test",
    });
  });

  it("getCompanyTasks", async () => {
    await api.getCompanyTasks(2);
    expectFetch(`${API_BASE}/companies/2/tasks`);
  });

  it("updateCompanyInfo", async () => {
    await api.updateCompanyInfo(7, { cin: "ABC" });
    expectFetch(`${API_BASE}/companies/7/onboarding`, "PUT", { cin: "ABC" });
  });
});

// =============================================================================
// 3. Documents
// =============================================================================

describe("Documents", () => {
  it("getCompanyDocuments", async () => {
    await api.getCompanyDocuments(4);
    expectFetch(`${API_BASE}/documents/company/4`);
  });

  it("uploadDocument sends FormData without Content-Type", async () => {
    const file = new File(["data"], "test.pdf", { type: "application/pdf" });
    await api.uploadDocument(10, "pan_card", file);

    const [url, opts] = mockFetch.mock.calls[mockFetch.mock.calls.length - 1];
    expect(url).toBe(`${API_BASE}/documents/upload`);
    expect(opts.method).toBe("POST");
    // Should NOT have Content-Type (browser sets multipart boundary)
    expect(opts.headers["Content-Type"]).toBeUndefined();
    expect(opts.body).toBeInstanceOf(FormData);
    expect((opts.body as FormData).get("doc_type")).toBe("pan_card");
    expect((opts.body as FormData).get("company_id")).toBe("10");
  });

  it("uploadDocument includes auth header", async () => {
    const file = new File(["data"], "f.pdf");
    await api.uploadDocument(1, "aoa", file);
    const opts = mockFetch.mock.calls[mockFetch.mock.calls.length - 1][1];
    expect(opts.headers["Authorization"]).toBe("Bearer test-jwt-token");
  });

  it("uploadDocument throws on failure", async () => {
    mockFetch.mockResolvedValueOnce(
      jsonResponse({ error: { message: "Too large" } }, 413),
    );
    const file = new File(["x".repeat(1000)], "big.pdf");
    await expect(api.uploadDocument(1, "moa", file)).rejects.toThrow("Too large");
  });

  it("uploadPitchDeck", async () => {
    const file = new File(["d"], "deck.pdf");
    await api.uploadPitchDeck(2, file);
    const [url, opts] = mockFetch.mock.calls[mockFetch.mock.calls.length - 1];
    expect(url).toBe(`${API_BASE}/documents/pitch-deck/upload`);
    expect(opts.method).toBe("POST");
    expect(opts.body).toBeInstanceOf(FormData);
  });

  it("getInvestorPitchDeckUrl returns URL string", () => {
    const url = api.getInvestorPitchDeckUrl("tok123", 5);
    expect(url).toBe(`${API_BASE}/investor-portal/tok123/companies/5/pitch-deck`);
  });
});

// =============================================================================
// 4. Payments
// =============================================================================

describe("Payments", () => {
  it("createPaymentOrder", async () => {
    await api.createPaymentOrder(8);
    expectFetch(`${API_BASE}/payments/create-order`, "POST", { company_id: 8 });
  });

  it("verifyPayment", async () => {
    const data = {
      razorpay_order_id: "order_1",
      razorpay_payment_id: "pay_1",
      razorpay_signature: "sig_1",
    };
    await api.verifyPayment(data);
    expectFetch(`${API_BASE}/payments/verify`, "POST", data);
  });
});

// =============================================================================
// 5. Messages
// =============================================================================

describe("Messages", () => {
  it("getCompanyMessages", async () => {
    await api.getCompanyMessages(3);
    expectFetch(`${API_BASE}/companies/3/messages`);
  });

  it("sendMessage", async () => {
    await api.sendMessage(3, "hello");
    expectFetch(`${API_BASE}/companies/3/messages`, "POST", {
      content: "hello",
    });
  });

  it("markMessagesRead", async () => {
    await api.markMessagesRead(3);
    expectFetch(`${API_BASE}/companies/3/messages/read`, "PUT");
  });
});

// =============================================================================
// 6. Notifications
// =============================================================================

describe("Notifications", () => {
  it("getNotifications without pagination", async () => {
    await api.getNotifications();
    expectFetch(`${API_BASE}/notifications`);
  });

  it("getNotifications with skip and limit", async () => {
    await api.getNotifications(10, 25);
    expectFetch(`${API_BASE}/notifications?skip=10&limit=25`);
  });

  it("getUnreadCount", async () => {
    await api.getUnreadCount();
    expectFetch(`${API_BASE}/notifications/unread-count`);
  });

  it("markNotificationRead", async () => {
    await api.markNotificationRead(42);
    expectFetch(`${API_BASE}/notifications/42/read`, "PUT");
  });

  it("markAllNotificationsRead", async () => {
    await api.markAllNotificationsRead();
    expectFetch(`${API_BASE}/notifications/read-all`, "PUT");
  });

  it("deleteNotification", async () => {
    await api.deleteNotification(99);
    expectFetch(`${API_BASE}/notifications/99`, "DELETE");
  });

  it("getNotificationPreferences", async () => {
    await api.getNotificationPreferences();
    expectFetch(`${API_BASE}/notifications/preferences`);
  });

  it("updateNotificationPreferences", async () => {
    await api.updateNotificationPreferences({ email: true });
    expectFetch(`${API_BASE}/notifications/preferences`, "PUT", {
      email: true,
    });
  });
});

// =============================================================================
// 7. Compliance
// =============================================================================

describe("Compliance", () => {
  it("getComplianceScore", async () => {
    await api.getComplianceScore(1);
    expectFetch(`${API_BASE}/companies/1/compliance/score`);
  });

  it("getComplianceCalendar", async () => {
    await api.getComplianceCalendar(1);
    expectFetch(`${API_BASE}/companies/1/compliance/calendar`);
  });

  it("getUpcomingDeadlines", async () => {
    await api.getUpcomingDeadlines(1);
    expectFetch(`${API_BASE}/companies/1/compliance/upcoming`);
  });

  it("getOverdueTasks", async () => {
    await api.getOverdueTasks(1);
    expectFetch(`${API_BASE}/companies/1/compliance/overdue`);
  });

  it("generateComplianceTasks", async () => {
    await api.generateComplianceTasks(1);
    expectFetch(`${API_BASE}/companies/1/compliance/generate`, "POST");
  });

  it("updateComplianceTask", async () => {
    await api.updateComplianceTask(1, 5, { status: "done" });
    expectFetch(`${API_BASE}/companies/1/compliance/tasks/5`, "PUT", {
      status: "done",
    });
  });

  it("getPenaltyEstimate", async () => {
    await api.getPenaltyEstimate(1);
    expectFetch(`${API_BASE}/companies/1/compliance/penalty-estimate`);
  });

  it("calculateTds", async () => {
    await api.calculateTds(1, { section: "194C", amount: 50000 });
    expectFetch(`${API_BASE}/companies/1/compliance/tds/calculate`, "POST", {
      section: "194C",
      amount: 50000,
    });
  });

  it("getTdsSections", async () => {
    await api.getTdsSections(1);
    expectFetch(`${API_BASE}/companies/1/compliance/tds/sections`);
  });

  it("getGstDashboard", async () => {
    await api.getGstDashboard(1);
    expectFetch(`${API_BASE}/companies/1/compliance/gst/dashboard`);
  });

  it("getTaxOverview", async () => {
    await api.getTaxOverview(1);
    expectFetch(`${API_BASE}/companies/1/compliance/tax/overview`);
  });

  it("getAuditPack", async () => {
    await api.getAuditPack(1);
    expectFetch(`${API_BASE}/companies/1/compliance/audit-pack`);
  });

  it("getAOC4Data", async () => {
    await api.getAOC4Data(2);
    expectFetch(`${API_BASE}/companies/2/compliance/filings/aoc4`);
  });

  it("generateAOC4", async () => {
    await api.generateAOC4(2, { year: 2024 });
    expectFetch(`${API_BASE}/companies/2/compliance/filings/aoc4`, "POST", {
      year: 2024,
    });
  });

  it("getMGT7Data", async () => {
    await api.getMGT7Data(2);
    expectFetch(`${API_BASE}/companies/2/compliance/filings/mgt7`);
  });

  it("getMGT7AData", async () => {
    await api.getMGT7AData(2);
    expectFetch(`${API_BASE}/companies/2/compliance/filings/mgt7a`);
  });

  it("getForm11Data", async () => {
    await api.getForm11Data(2);
    expectFetch(`${API_BASE}/companies/2/compliance/filings/form11`);
  });

  it("getForm8Data", async () => {
    await api.getForm8Data(2);
    expectFetch(`${API_BASE}/companies/2/compliance/filings/form8`);
  });

  it("getTdsDueDates", async () => {
    await api.getTdsDueDates(1, "Q1");
    expectFetch(
      `${API_BASE}/companies/1/compliance/tds/due-dates?quarter=Q1`,
    );
  });

  it("sendComplianceReminders", async () => {
    await api.sendComplianceReminders(1);
    expectFetch(`${API_BASE}/companies/1/compliance/reminders`, "POST");
  });
});

// =============================================================================
// 8. Compliance Documents
// =============================================================================

describe("Compliance Documents", () => {
  it("generatePAS3", async () => {
    await api.generatePAS3(1, { amount: 100000 });
    expectFetch(`${API_BASE}/companies/1/compliance-documents/pas-3`, "POST", {
      amount: 100000,
    });
  });

  it("generateMGT14", async () => {
    await api.generateMGT14(1, { resolution: "test" });
    expectFetch(
      `${API_BASE}/companies/1/compliance-documents/mgt-14`,
      "POST",
      { resolution: "test" },
    );
  });

  it("generateSH7", async () => {
    await api.generateSH7(1, { data: true });
    expectFetch(`${API_BASE}/companies/1/compliance-documents/sh-7`, "POST", {
      data: true,
    });
  });

  it("getComplianceDocuments", async () => {
    await api.getComplianceDocuments(1);
    expectFetch(`${API_BASE}/companies/1/compliance-documents`);
  });
});

// =============================================================================
// 9. Legal Document Templates
// =============================================================================

describe("Legal docs", () => {
  it("getLegalTemplates", async () => {
    await api.getLegalTemplates();
    expectFetch(`${API_BASE}/legal-docs/templates`);
  });

  it("getLegalTemplateDefinition", async () => {
    await api.getLegalTemplateDefinition("nda");
    expectFetch(`${API_BASE}/legal-docs/templates/nda`);
  });

  it("createLegalDraft", async () => {
    await api.createLegalDraft({
      template_type: "nda",
      company_id: 1,
      title: "NDA",
    });
    expectFetch(`${API_BASE}/legal-docs/drafts`, "POST", {
      template_type: "nda",
    });
  });

  it("getLegalDrafts", async () => {
    await api.getLegalDrafts();
    expectFetch(`${API_BASE}/legal-docs/drafts`);
  });

  it("getLegalDraft", async () => {
    await api.getLegalDraft(7);
    expectFetch(`${API_BASE}/legal-docs/drafts/7`);
  });

  it("updateLegalDraftClauses", async () => {
    await api.updateLegalDraftClauses(7, { non_compete: "yes" });
    expectFetch(`${API_BASE}/legal-docs/drafts/7/clauses`, "PUT", {
      clauses_config: { non_compete: "yes" },
    });
  });

  it("generateLegalPreview", async () => {
    await api.generateLegalPreview(7);
    expectFetch(`${API_BASE}/legal-docs/drafts/7/preview`, "POST");
  });

  it("finalizeLegalDocument", async () => {
    await api.finalizeLegalDocument(7);
    expectFetch(`${API_BASE}/legal-docs/drafts/7/finalize`, "POST");
  });

  it("getClausePreview", async () => {
    await api.getClausePreview("nda", "non_compete", "2 years");
    expectFetch(
      `${API_BASE}/legal-docs/templates/nda/clauses/non_compete/preview?value=2%20years`,
    );
  });
});

// =============================================================================
// 10. Statutory Registers
// =============================================================================

describe("Registers", () => {
  it("getRegisters", async () => {
    await api.getRegisters(1);
    expectFetch(`${API_BASE}/companies/1/registers`);
  });

  it("getRegister", async () => {
    await api.getRegister(1, "members");
    expectFetch(`${API_BASE}/companies/1/registers/members`);
  });

  it("addRegisterEntry", async () => {
    await api.addRegisterEntry(1, "members", { name: "Alice" });
    expectFetch(`${API_BASE}/companies/1/registers/members/entries`, "POST", {
      name: "Alice",
    });
  });

  it("updateRegisterEntry", async () => {
    await api.updateRegisterEntry(1, "members", 3, { name: "Bob" });
    expectFetch(
      `${API_BASE}/companies/1/registers/members/entries/3`,
      "PUT",
      { name: "Bob" },
    );
  });

  it("getRegistersSummary", async () => {
    await api.getRegistersSummary(1);
    expectFetch(`${API_BASE}/companies/1/registers/summary`);
  });

  it("exportRegister", async () => {
    await api.exportRegister(1, "directors");
    expectFetch(`${API_BASE}/companies/1/registers/directors/export`);
  });
});

// =============================================================================
// 11. Meetings
// =============================================================================

describe("Meetings", () => {
  it("createMeeting", async () => {
    await api.createMeeting(1, { type: "board" });
    expectFetch(`${API_BASE}/companies/1/meetings`, "POST", { type: "board" });
  });

  it("getMeetings without params", async () => {
    await api.getMeetings(1);
    expectFetch(`${API_BASE}/companies/1/meetings`);
  });

  it("getMeetings with params", async () => {
    await api.getMeetings(1, { type: "agm" });
    expectFetch(`${API_BASE}/companies/1/meetings?type=agm`);
  });

  it("getMeeting", async () => {
    await api.getMeeting(1, 5);
    expectFetch(`${API_BASE}/companies/1/meetings/5`);
  });

  it("updateMeeting", async () => {
    await api.updateMeeting(1, 5, { status: "completed" });
    expectFetch(`${API_BASE}/companies/1/meetings/5`, "PUT", {
      status: "completed",
    });
  });

  it("generateMeetingNotice", async () => {
    await api.generateMeetingNotice(1, 5);
    expectFetch(`${API_BASE}/companies/1/meetings/5/notice`, "POST");
  });

  it("generateMeetingMinutes", async () => {
    await api.generateMeetingMinutes(1, 5);
    expectFetch(`${API_BASE}/companies/1/meetings/5/minutes`, "POST");
  });

  it("sendMinutesForSigning", async () => {
    await api.sendMinutesForSigning(1, 5, {
      chairman_name: "Alice",
      chairman_email: "alice@test.com",
    });
    expectFetch(
      `${API_BASE}/companies/1/meetings/5/minutes/send-for-signing`,
      "POST",
      { chairman_name: "Alice", chairman_email: "alice@test.com" },
    );
  });

  it("updateMeetingAttendance", async () => {
    await api.updateMeetingAttendance(1, 5, { present: [1, 2] });
    expectFetch(`${API_BASE}/companies/1/meetings/5/attendance`, "PUT");
  });

  it("updateMeetingAgenda", async () => {
    await api.updateMeetingAgenda(1, 5, { items: [] });
    expectFetch(`${API_BASE}/companies/1/meetings/5/agenda`, "PUT");
  });

  it("signMeetingMinutes", async () => {
    await api.signMeetingMinutes(1, 5, { signer: "A" });
    expectFetch(`${API_BASE}/companies/1/meetings/5/minutes/sign`, "PUT");
  });

  it("updateMeetingResolutions", async () => {
    await api.updateMeetingResolutions(1, 5, { res: [] });
    expectFetch(`${API_BASE}/companies/1/meetings/5/resolutions`, "PUT");
  });

  it("getUpcomingMeetings", async () => {
    await api.getUpcomingMeetings(1);
    expectFetch(`${API_BASE}/companies/1/meetings/upcoming`);
  });

  it("getPendingMinutes", async () => {
    await api.getPendingMinutes(1);
    expectFetch(`${API_BASE}/companies/1/meetings/minutes-pending`);
  });

  it("exportMeeting", async () => {
    await api.exportMeeting(1, 5);
    expectFetch(`${API_BASE}/companies/1/meetings/5/export`);
  });

  it("updateResolutionVotes", async () => {
    await api.updateResolutionVotes(1, 5, { votes: {} });
    expectFetch(`${API_BASE}/companies/1/meetings/5/resolution-votes`, "PUT");
  });

  it("updateMeetingFilingStatus", async () => {
    await api.updateMeetingFilingStatus(1, 5, { filed: true });
    expectFetch(`${API_BASE}/companies/1/meetings/5/filing-status`, "PUT");
  });

  it("getMinutesSigningStatus", async () => {
    await api.getMinutesSigningStatus(1, 5);
    expectFetch(
      `${API_BASE}/companies/1/meetings/5/minutes/signing-status`,
    );
  });
});

// =============================================================================
// 12. Data Room
// =============================================================================

describe("Data Room", () => {
  it("getDataRoomFolders", async () => {
    await api.getDataRoomFolders(1);
    expectFetch(`${API_BASE}/companies/1/data-room/folders`);
  });

  it("createDataRoomFolder", async () => {
    await api.createDataRoomFolder(1, { name: "Legal" });
    expectFetch(`${API_BASE}/companies/1/data-room/folders`, "POST", {
      name: "Legal",
    });
  });

  it("getDataRoomFiles without params", async () => {
    await api.getDataRoomFiles(1);
    expectFetch(`${API_BASE}/companies/1/data-room/files`);
  });

  it("getDataRoomFiles with params", async () => {
    await api.getDataRoomFiles(1, { folder_id: "2" });
    expectFetch(`${API_BASE}/companies/1/data-room/files?folder_id=2`);
  });

  it("createShareLink", async () => {
    await api.createShareLink(1, { file_ids: [1, 2] });
    expectFetch(`${API_BASE}/companies/1/data-room/share-links`, "POST", {
      file_ids: [1, 2],
    });
  });

  it("setupDefaultDataRoom", async () => {
    await api.setupDefaultDataRoom(1);
    expectFetch(`${API_BASE}/companies/1/data-room/setup-defaults`, "POST");
  });

  it("getShareLinks", async () => {
    await api.getShareLinks(1);
    expectFetch(`${API_BASE}/companies/1/data-room/share-links`);
  });

  it("getRetentionAlerts", async () => {
    await api.getRetentionAlerts(1);
    expectFetch(`${API_BASE}/companies/1/data-room/retention/alerts`);
  });

  it("getRetentionSummary", async () => {
    await api.getRetentionSummary(1);
    expectFetch(`${API_BASE}/companies/1/data-room/retention/summary`);
  });
});

// =============================================================================
// 13. E-Signature
// =============================================================================

describe("E-sign", () => {
  it("createSignatureRequest", async () => {
    await api.createSignatureRequest({ document_id: 1, signers: [] });
    expectFetch(`${API_BASE}/esign/requests`, "POST", { document_id: 1 });
  });

  it("getSignatureRequests", async () => {
    await api.getSignatureRequests();
    expectFetch(`${API_BASE}/esign/requests`);
  });

  it("getSignatureRequest", async () => {
    await api.getSignatureRequest(3);
    expectFetch(`${API_BASE}/esign/requests/3`);
  });

  it("sendSigningEmails", async () => {
    await api.sendSigningEmails(3);
    expectFetch(`${API_BASE}/esign/requests/3/send`, "POST");
  });

  it("sendSigningReminder", async () => {
    await api.sendSigningReminder(3);
    expectFetch(`${API_BASE}/esign/requests/3/remind`, "POST");
  });

  it("cancelSignatureRequest", async () => {
    await api.cancelSignatureRequest(3);
    expectFetch(`${API_BASE}/esign/requests/3/cancel`, "POST");
  });

  it("getSignatureAuditTrail", async () => {
    await api.getSignatureAuditTrail(3);
    expectFetch(`${API_BASE}/esign/requests/3/audit-trail`);
  });

  it("getSignedDocument", async () => {
    await api.getSignedDocument(3);
    expectFetch(`${API_BASE}/esign/requests/3/signed-document`);
  });

  it("getSignatureCertificate", async () => {
    await api.getSignatureCertificate(3);
    expectFetch(`${API_BASE}/esign/requests/3/certificate`);
  });

  it("getSigningPageData — public, no auth", async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({ doc: "hello" }));
    const result = await api.getSigningPageData("abc123");
    const [url, opts] = mockFetch.mock.calls[mockFetch.mock.calls.length - 1];
    expect(url).toBe(`${API_BASE}/esign/sign/abc123`);
    // No Authorization header (uses direct fetch)
    expect(opts?.headers?.Authorization).toBeUndefined();
    expect(result).toEqual({ doc: "hello" });
  });

  it("getSigningPageData throws on error", async () => {
    const res = {
      ok: false,
      status: 404,
      text: jest.fn().mockResolvedValue("Not found"),
    } as unknown as Response;
    mockFetch.mockResolvedValueOnce(res);
    await expect(api.getSigningPageData("bad")).rejects.toThrow("Not found");
  });

  it("submitSignature — public, no auth", async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({ signed: true }));
    const result = await api.submitSignature("abc123", { sig: "data:image" });
    const [url, opts] = mockFetch.mock.calls[mockFetch.mock.calls.length - 1];
    expect(url).toBe(`${API_BASE}/esign/sign/abc123`);
    expect(opts.method).toBe("POST");
    expect(JSON.parse(opts.body)).toEqual({ sig: "data:image" });
    expect(result).toEqual({ signed: true });
  });

  it("declineSignature", async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({ declined: true }));
    await api.declineSignature("abc123", "Not interested");
    const [url, opts] = mockFetch.mock.calls[mockFetch.mock.calls.length - 1];
    expect(url).toBe(`${API_BASE}/esign/sign/abc123/decline`);
    expect(opts.method).toBe("POST");
    expect(JSON.parse(opts.body)).toEqual({ reason: "Not interested" });
  });
});

// =============================================================================
// 14. PDF URL helpers (synchronous, no fetch)
// =============================================================================

describe("PDF URL helpers", () => {
  it("getLegalDocPdfUrl", () => {
    expect(api.getLegalDocPdfUrl(5)).toBe(
      `${API_BASE}/legal-docs/drafts/5/download-pdf`,
    );
  });

  it("getSignedDocPdfUrl", () => {
    expect(api.getSignedDocPdfUrl(3)).toBe(
      `${API_BASE}/esign/requests/3/signed-document-pdf`,
    );
  });

  it("getPaymentReceiptUrl", () => {
    expect(api.getPaymentReceiptUrl(7)).toBe(
      `${API_BASE}/invoices/payments/7/receipt`,
    );
  });

  it("getPaymentReceiptPdfUrl", () => {
    expect(api.getPaymentReceiptPdfUrl(7)).toBe(
      `${API_BASE}/invoices/payments/7/receipt-pdf`,
    );
  });

  it("getPaymentInvoiceUrl", () => {
    expect(api.getPaymentInvoiceUrl(7)).toBe(
      `${API_BASE}/invoices/payments/7/invoice`,
    );
  });
});

// =============================================================================
// 15. Cap Table
// =============================================================================

describe("Cap Table", () => {
  it("getCapTable", async () => {
    await api.getCapTable(1);
    expectFetch(`${API_BASE}/companies/1/cap-table`);
  });

  it("addShareholder", async () => {
    await api.addShareholder(1, { name: "Alice", shares: 100 });
    expectFetch(`${API_BASE}/companies/1/cap-table/shareholders`, "POST", {
      name: "Alice",
    });
  });

  it("transferShares", async () => {
    await api.transferShares(1, { from: 1, to: 2, shares: 50 });
    expectFetch(`${API_BASE}/companies/1/cap-table/transfer`, "POST", {
      from: 1,
      to: 2,
    });
  });

  it("allotShares", async () => {
    await api.allotShares(1, { shareholder_id: 1, shares: 200 });
    expectFetch(`${API_BASE}/companies/1/cap-table/allotment`, "POST", {
      shareholder_id: 1,
    });
  });

  it("getDilutionPreview without optional params", async () => {
    await api.getDilutionPreview(1, 1000);
    const url = mockFetch.mock.calls[mockFetch.mock.calls.length - 1][0];
    expect(url).toContain("/cap-table/dilution-preview?");
    expect(url).toContain("new_shares=1000");
  });

  it("getDilutionPreview with optional params", async () => {
    await api.getDilutionPreview(1, 1000, "Alice", 50);
    const url = mockFetch.mock.calls[mockFetch.mock.calls.length - 1][0];
    expect(url).toContain("investor_name=Alice");
    expect(url).toContain("price_per_share=50");
  });

  it("exportCapTable", async () => {
    await api.exportCapTable(1);
    expectFetch(`${API_BASE}/companies/1/cap-table/export`);
  });

  it("getCapTableTransactions", async () => {
    await api.getCapTableTransactions(1);
    expectFetch(`${API_BASE}/companies/1/cap-table/transactions`);
  });

  it("simulateRound", async () => {
    const data = {
      pre_money_valuation: 10000000,
      investment_amount: 2000000,
    };
    await api.simulateRound(1, data);
    expectFetch(`${API_BASE}/companies/1/cap-table/simulate-round`, "POST", data);
  });

  it("simulateExit", async () => {
    const data = { exit_valuation: 50000000 };
    await api.simulateExit(1, data);
    expectFetch(`${API_BASE}/companies/1/cap-table/simulate-exit`, "POST", data);
  });

  it("saveCapTableScenario", async () => {
    await api.saveCapTableScenario(1, {
      scenario_name: "Test",
      scenario_type: "round",
      scenario_data: {},
    });
    expectFetch(`${API_BASE}/companies/1/cap-table/scenarios`, "POST", {
      scenario_name: "Test",
    });
  });

  it("simulateExitWaterfall", async () => {
    await api.simulateExitWaterfall(1, { exit_valuation: 50000000 });
    expectFetch(
      `${API_BASE}/companies/1/cap-table/simulate-exit-waterfall`,
      "POST",
    );
  });

  it("getShareCertificate", async () => {
    await api.getShareCertificate(1, 2);
    expectFetch(
      `${API_BASE}/companies/1/cap-table/shareholders/2/certificate`,
    );
  });

  it("sendShareCertificateForSigning", async () => {
    await api.sendShareCertificateForSigning(1, 2, {
      director_name: "John",
      director_email: "john@test.com",
    });
    expectFetch(
      `${API_BASE}/companies/1/cap-table/shareholders/2/certificate/send-for-signing`,
      "POST",
    );
  });
});

// =============================================================================
// 16. Share Issuance
// =============================================================================

describe("Share Issuance", () => {
  it("createShareIssuance", async () => {
    await api.createShareIssuance(1, { type: "rights" });
    expectFetch(`${API_BASE}/companies/1/share-issuance`, "POST", {
      type: "rights",
    });
  });

  it("getShareIssuances", async () => {
    await api.getShareIssuances(1);
    expectFetch(`${API_BASE}/companies/1/share-issuance`);
  });

  it("getShareIssuance", async () => {
    await api.getShareIssuance(1, 7);
    expectFetch(`${API_BASE}/companies/1/share-issuance/7`);
  });

  it("updateShareIssuance", async () => {
    await api.updateShareIssuance(1, 7, { step: 3 });
    expectFetch(`${API_BASE}/companies/1/share-issuance/7`, "PUT", {
      step: 3,
    });
  });

  it("linkShareIssuanceDocument", async () => {
    await api.linkShareIssuanceDocument(1, 7, {
      doc_type: "board_res",
      document_id: 10,
    });
    expectFetch(
      `${API_BASE}/companies/1/share-issuance/7/link-document`,
      "POST",
    );
  });

  it("updateShareIssuanceFilingStatus", async () => {
    await api.updateShareIssuanceFilingStatus(1, 7, { filed: true });
    expectFetch(
      `${API_BASE}/companies/1/share-issuance/7/filing-status`,
      "PUT",
    );
  });

  it("addShareIssuanceAllottee", async () => {
    await api.addShareIssuanceAllottee(1, 7, { name: "X" });
    expectFetch(
      `${API_BASE}/companies/1/share-issuance/7/allottees`,
      "POST",
    );
  });

  it("removeShareIssuanceAllottee", async () => {
    await api.removeShareIssuanceAllottee(1, 7, 0);
    expectFetch(
      `${API_BASE}/companies/1/share-issuance/7/allottees/0`,
      "DELETE",
    );
  });

  it("recordShareIssuanceFundReceipt", async () => {
    await api.recordShareIssuanceFundReceipt(1, 7, { amount: 1000 });
    expectFetch(
      `${API_BASE}/companies/1/share-issuance/7/fund-receipt`,
      "POST",
    );
  });

  it("saveShareIssuanceWizardState", async () => {
    await api.saveShareIssuanceWizardState(1, 7, { step: 2 });
    expectFetch(
      `${API_BASE}/companies/1/share-issuance/7/wizard-state`,
      "PUT",
    );
  });

  it("completeShareIssuanceAllotment", async () => {
    await api.completeShareIssuanceAllotment(1, 7);
    expectFetch(
      `${API_BASE}/companies/1/share-issuance/7/complete-allotment`,
      "POST",
    );
  });

  it("sendShareIssuanceForSigning", async () => {
    await api.sendShareIssuanceForSigning(1, 7);
    expectFetch(
      `${API_BASE}/companies/1/share-issuance/7/send-for-signing`,
      "POST",
    );
  });
});

// =============================================================================
// 17. ESOP
// =============================================================================

describe("ESOP", () => {
  it("getESOPPlans", async () => {
    await api.getESOPPlans(1);
    expectFetch(`${API_BASE}/companies/1/esop/plans`);
  });

  it("createESOPPlan", async () => {
    await api.createESOPPlan(1, { name: "Plan A" });
    expectFetch(`${API_BASE}/companies/1/esop/plans`, "POST", {
      name: "Plan A",
    });
  });

  it("getESOPPlan", async () => {
    await api.getESOPPlan(1, 3);
    expectFetch(`${API_BASE}/companies/1/esop/plans/3`);
  });

  it("updateESOPPlan", async () => {
    await api.updateESOPPlan(1, 3, { name: "Updated" });
    expectFetch(`${API_BASE}/companies/1/esop/plans/3`, "PUT");
  });

  it("activateESOPPlan", async () => {
    await api.activateESOPPlan(1, 3);
    expectFetch(`${API_BASE}/companies/1/esop/plans/3/activate`, "POST");
  });

  it("getESOPGrants", async () => {
    await api.getESOPGrants(1, 3);
    expectFetch(`${API_BASE}/companies/1/esop/plans/3/grants`);
  });

  it("createESOPGrant", async () => {
    await api.createESOPGrant(1, 3, { employee: "Alice" });
    expectFetch(`${API_BASE}/companies/1/esop/plans/3/grants`, "POST");
  });

  it("getCompanyESOPGrants", async () => {
    await api.getCompanyESOPGrants(1);
    expectFetch(`${API_BASE}/companies/1/esop/grants`);
  });

  it("getESOPGrant", async () => {
    await api.getESOPGrant(1, 5);
    expectFetch(`${API_BASE}/companies/1/esop/grants/5`);
  });

  it("exerciseESOPOptions", async () => {
    await api.exerciseESOPOptions(1, 5, { number_of_options: 100 });
    expectFetch(`${API_BASE}/companies/1/esop/grants/5/exercise`, "POST", {
      number_of_options: 100,
    });
  });

  it("generateESOPGrantLetter", async () => {
    await api.generateESOPGrantLetter(1, 5);
    expectFetch(
      `${API_BASE}/companies/1/esop/grants/5/generate-letter`,
      "POST",
    );
  });

  it("sendESOPGrantForSigning", async () => {
    await api.sendESOPGrantForSigning(1, 5);
    expectFetch(
      `${API_BASE}/companies/1/esop/grants/5/send-for-signing`,
      "POST",
    );
  });

  it("getESOPSummary", async () => {
    await api.getESOPSummary(1);
    expectFetch(`${API_BASE}/companies/1/esop/summary`);
  });

  it("getESOPValuationReference", async () => {
    await api.getESOPValuationReference(1);
    expectFetch(`${API_BASE}/companies/1/esop/valuation-reference`);
  });
});

// =============================================================================
// 18. Fundraising
// =============================================================================

describe("Fundraising", () => {
  it("createFundingRound", async () => {
    await api.createFundingRound(1, { round_name: "Seed" });
    expectFetch(`${API_BASE}/companies/1/fundraising/rounds`, "POST", {
      round_name: "Seed",
    });
  });

  it("getFundingRounds", async () => {
    await api.getFundingRounds(1);
    expectFetch(`${API_BASE}/companies/1/fundraising/rounds`);
  });

  it("getFundingRound", async () => {
    await api.getFundingRound(1, 4);
    expectFetch(`${API_BASE}/companies/1/fundraising/rounds/4`);
  });

  it("updateFundingRound", async () => {
    await api.updateFundingRound(1, 4, { status: "closed" });
    expectFetch(`${API_BASE}/companies/1/fundraising/rounds/4`, "PUT");
  });

  it("addRoundInvestor", async () => {
    await api.addRoundInvestor(1, 4, { name: "VC Fund" });
    expectFetch(
      `${API_BASE}/companies/1/fundraising/rounds/4/investors`,
      "POST",
    );
  });

  it("updateRoundInvestor", async () => {
    await api.updateRoundInvestor(1, 4, 2, { amount: 500000 });
    expectFetch(
      `${API_BASE}/companies/1/fundraising/rounds/4/investors/2`,
      "PUT",
    );
  });

  it("removeRoundInvestor", async () => {
    await api.removeRoundInvestor(1, 4, 2);
    expectFetch(
      `${API_BASE}/companies/1/fundraising/rounds/4/investors/2`,
      "DELETE",
    );
  });

  it("linkRoundDocument", async () => {
    await api.linkRoundDocument(1, 4, {
      doc_type: "sha",
      document_id: 10,
    });
    expectFetch(
      `${API_BASE}/companies/1/fundraising/rounds/4/link-document`,
      "POST",
    );
  });

  it("initiateClosing", async () => {
    await api.initiateClosing(1, 4, { documents_to_sign: ["sha", "ssa"] });
    expectFetch(
      `${API_BASE}/companies/1/fundraising/rounds/4/initiate-closing`,
      "POST",
      { documents_to_sign: ["sha", "ssa"] },
    );
  });

  it("getClosingRoom", async () => {
    await api.getClosingRoom(1, 4);
    expectFetch(
      `${API_BASE}/companies/1/fundraising/rounds/4/closing-room`,
    );
  });

  it("completeAllotment", async () => {
    await api.completeAllotment(1, 4);
    expectFetch(
      `${API_BASE}/companies/1/fundraising/rounds/4/complete-allotment`,
      "POST",
    );
  });

  it("saveFundraisingChecklistState", async () => {
    await api.saveFundraisingChecklistState(1, 4, { items: [] });
    expectFetch(
      `${API_BASE}/companies/1/fundraising/rounds/4/checklist-state`,
      "PUT",
    );
  });

  it("getFundraisingChecklistState", async () => {
    await api.getFundraisingChecklistState(1, 4);
    expectFetch(
      `${API_BASE}/companies/1/fundraising/rounds/4/checklist-state`,
    );
  });

  it("getFundraisingValuationReference", async () => {
    await api.getFundraisingValuationReference(1);
    expectFetch(
      `${API_BASE}/companies/1/fundraising/valuation-reference`,
    );
  });
});

// =============================================================================
// 19. Stakeholders
// =============================================================================

describe("Stakeholders", () => {
  it("getStakeholderPortfolio", async () => {
    await api.getStakeholderPortfolio();
    expectFetch(`${API_BASE}/stakeholders/me/portfolio`);
  });

  it("getStakeholderCompanyDetail", async () => {
    await api.getStakeholderCompanyDetail(3);
    expectFetch(`${API_BASE}/stakeholders/me/companies/3`);
  });

  it("createStakeholderProfile", async () => {
    await api.createStakeholderProfile({
      name: "Bob",
      email: "bob@test.com",
      stakeholder_type: "individual",
    });
    expectFetch(`${API_BASE}/stakeholders/profiles`, "POST", { name: "Bob" });
  });

  it("updateStakeholderProfile", async () => {
    await api.updateStakeholderProfile(5, { phone: "123" });
    expectFetch(`${API_BASE}/stakeholders/profiles/5`, "PUT");
  });

  it("getStakeholderProfiles without companyId", async () => {
    await api.getStakeholderProfiles();
    expectFetch(`${API_BASE}/stakeholders/profiles`);
  });

  it("getStakeholderProfiles with companyId", async () => {
    await api.getStakeholderProfiles(2);
    expectFetch(`${API_BASE}/stakeholders/profiles?company_id=2`);
  });

  it("getStakeholderProfile", async () => {
    await api.getStakeholderProfile(5);
    expectFetch(`${API_BASE}/stakeholders/profiles/5`);
  });

  it("linkStakeholderToShareholder", async () => {
    await api.linkStakeholderToShareholder(5, 10);
    expectFetch(`${API_BASE}/stakeholders/profiles/5/link/10`, "POST");
  });
});

// =============================================================================
// 20. Members
// =============================================================================

describe("Members", () => {
  it("inviteCompanyMember", async () => {
    await api.inviteCompanyMember(1, {
      email: "a@b.com",
      name: "A",
      role: "director",
    });
    expectFetch(`${API_BASE}/companies/1/members/invite`, "POST", {
      email: "a@b.com",
    });
  });

  it("getCompanyMembers", async () => {
    await api.getCompanyMembers(1);
    expectFetch(`${API_BASE}/companies/1/members`);
  });

  it("updateCompanyMember", async () => {
    await api.updateCompanyMember(1, 3, { role: "admin" });
    expectFetch(`${API_BASE}/companies/1/members/3`, "PUT", { role: "admin" });
  });

  it("removeCompanyMember", async () => {
    await api.removeCompanyMember(1, 3);
    expectFetch(`${API_BASE}/companies/1/members/3`, "DELETE");
  });

  it("resendMemberInvite", async () => {
    await api.resendMemberInvite(1, 3);
    expectFetch(`${API_BASE}/companies/1/members/3/resend`, "POST");
  });

  it("getInviteInfo", async () => {
    await api.getInviteInfo("tok");
    expectFetch(`${API_BASE}/invites/tok`);
  });

  it("acceptInvite", async () => {
    await api.acceptInvite("tok");
    expectFetch(`${API_BASE}/invites/tok/accept`, "POST");
  });

  it("declineInvite", async () => {
    await api.declineInvite("tok");
    expectFetch(`${API_BASE}/invites/tok/decline`, "POST");
  });

  it("getMyCompanies", async () => {
    await api.getMyCompanies();
    expectFetch(`${API_BASE}/my-companies`);
  });
});

// =============================================================================
// 21. Valuations
// =============================================================================

describe("Valuations", () => {
  it("calculateNAV", async () => {
    await api.calculateNAV(1, {
      total_assets: 500000,
      total_liabilities: 100000,
    });
    expectFetch(
      `${API_BASE}/companies/1/valuations/calculate-nav`,
      "POST",
      { total_assets: 500000 },
    );
  });

  it("calculateDCF", async () => {
    await api.calculateDCF(1, {
      current_revenue: 1000000,
      growth_rate: 0.2,
      profit_margin: 0.15,
      discount_rate: 0.1,
    });
    expectFetch(
      `${API_BASE}/companies/1/valuations/calculate-dcf`,
      "POST",
      { current_revenue: 1000000 },
    );
  });

  it("createValuation", async () => {
    await api.createValuation(1, { method: "nav", value: 5000000 });
    expectFetch(`${API_BASE}/companies/1/valuations`, "POST", {
      method: "nav",
    });
  });

  it("listValuations", async () => {
    await api.listValuations(1);
    expectFetch(`${API_BASE}/companies/1/valuations`);
  });

  it("getLatestValuation", async () => {
    await api.getLatestValuation(1);
    expectFetch(`${API_BASE}/companies/1/valuations/latest`);
  });

  it("getValuation", async () => {
    await api.getValuation(1, 5);
    expectFetch(`${API_BASE}/companies/1/valuations/5`);
  });
});

// =============================================================================
// 22. Post-Incorporation
// =============================================================================

describe("Post-Incorporation", () => {
  it("getPostIncorporationChecklist", async () => {
    await api.getPostIncorporationChecklist(1);
    expectFetch(`${API_BASE}/companies/1/post-incorp/checklist`);
  });

  it("getPostIncorporationDeadlines", async () => {
    await api.getPostIncorporationDeadlines(1);
    expectFetch(`${API_BASE}/companies/1/post-incorp/deadlines`);
  });

  it("completePostIncorporationTask", async () => {
    await api.completePostIncorporationTask(1, "open_bank_account");
    expectFetch(
      `${API_BASE}/companies/1/post-incorp/tasks/open_bank_account/complete`,
      "PUT",
    );
  });
});

// =============================================================================
// 23. Audit Trail
// =============================================================================

describe("Audit Trail", () => {
  it("getCompanyAuditTrail without filters", async () => {
    await api.getCompanyAuditTrail(1);
    expectFetch(`${API_BASE}/companies/1/audit-trail`);
  });

  it("getCompanyAuditTrail with entity_type and limit", async () => {
    await api.getCompanyAuditTrail(1, "legal_draft", 50);
    const url = mockFetch.mock.calls[mockFetch.mock.calls.length - 1][0];
    expect(url).toContain("entity_type=legal_draft");
    expect(url).toContain("limit=50");
  });

  it("getDocumentAuditTrail", async () => {
    await api.getDocumentAuditTrail(10);
    expectFetch(`${API_BASE}/legal-docs/drafts/10/audit-trail`);
  });

  it("reviseDocument", async () => {
    await api.reviseDocument(10, "typo fix");
    expectFetch(`${API_BASE}/legal-docs/drafts/10/revise`, "POST", {
      reason: "typo fix",
    });
  });

  it("getDocumentVersions", async () => {
    await api.getDocumentVersions(10);
    expectFetch(`${API_BASE}/legal-docs/drafts/10/versions`);
  });
});

// =============================================================================
// 24. GST
// =============================================================================

describe("GST", () => {
  it("validateGSTIN", async () => {
    await api.validateGSTIN(1, "22AAAAA0000A1Z5");
    expectFetch(
      `${API_BASE}/companies/1/compliance/gst/validate-gstin`,
      "POST",
      { gstin: "22AAAAA0000A1Z5" },
    );
  });

  it("getGSTStateCodes", async () => {
    await api.getGSTStateCodes(1);
    expectFetch(`${API_BASE}/companies/1/compliance/gst/state-codes`);
  });

  it("generateGSTR1", async () => {
    const data = {
      gstin: "22AAAAA0000A1Z5",
      filing_period: "042026",
      invoices: [],
    };
    await api.generateGSTR1(1, data);
    expectFetch(
      `${API_BASE}/companies/1/compliance/gst/gstr1/generate`,
      "POST",
      data,
    );
  });

  it("generateGSTR3B", async () => {
    const data = {
      gstin: "22AAAAA0000A1Z5",
      filing_period: "042026",
    };
    await api.generateGSTR3B(1, data);
    expectFetch(
      `${API_BASE}/companies/1/compliance/gst/gstr3b/generate`,
      "POST",
      data,
    );
  });
});

// =============================================================================
// 25. Letterhead
// =============================================================================

describe("Letterhead", () => {
  it("getLetterheadDesigns", async () => {
    await api.getLetterheadDesigns();
    expectFetch(`${API_BASE}/companies/letterhead/designs`);
  });

  it("getLetterheadSettings", async () => {
    await api.getLetterheadSettings(1);
    expectFetch(`${API_BASE}/companies/1/letterhead`);
  });

  it("updateLetterheadSettings", async () => {
    await api.updateLetterheadSettings(1, {
      design: "classic",
      accent_color: "#000",
    });
    expectFetch(`${API_BASE}/companies/1/letterhead`, "PUT", {
      design: "classic",
    });
  });

  it("generateLetterhead without design", async () => {
    await api.generateLetterhead(1);
    expectFetch(`${API_BASE}/companies/1/letterhead/generate`);
  });

  it("generateLetterhead with design", async () => {
    await api.generateLetterhead(1, "modern");
    expectFetch(`${API_BASE}/companies/1/letterhead/generate?design=modern`);
  });
});

// =============================================================================
// 26. Services Marketplace
// =============================================================================

describe("Services", () => {
  it("getServicesCatalog without entityType", async () => {
    await api.getServicesCatalog();
    expectFetch(`${API_BASE}/services/catalog`);
  });

  it("getServicesCatalog with entityType", async () => {
    await api.getServicesCatalog("pvt_ltd");
    expectFetch(`${API_BASE}/services/catalog?entity_type=pvt_ltd`);
  });

  it("getSubscriptionPlans", async () => {
    await api.getSubscriptionPlans();
    expectFetch(`${API_BASE}/services/plans`);
  });

  it("createServiceRequest", async () => {
    await api.createServiceRequest({
      company_id: 1,
      service_key: "gst_registration",
    });
    expectFetch(`${API_BASE}/services/requests`, "POST", {
      service_key: "gst_registration",
    });
  });

  it("getServiceRequests without companyId", async () => {
    await api.getServiceRequests();
    expectFetch(`${API_BASE}/services/requests`);
  });

  it("getServiceRequests with companyId", async () => {
    await api.getServiceRequests(1);
    expectFetch(`${API_BASE}/services/requests?company_id=1`);
  });

  it("cancelServiceRequest", async () => {
    await api.cancelServiceRequest(5);
    expectFetch(`${API_BASE}/services/requests/5/cancel`, "POST");
  });

  it("payForServiceRequest", async () => {
    await api.payForServiceRequest(5);
    expectFetch(`${API_BASE}/services/requests/5/pay`, "POST");
  });

  it("verifyServicePayment", async () => {
    await api.verifyServicePayment(5, {
      razorpay_order_id: "o1",
      razorpay_payment_id: "p1",
      razorpay_signature: "s1",
    });
    expectFetch(`${API_BASE}/services/requests/5/verify-payment`, "POST", {
      razorpay_order_id: "o1",
    });
  });

  it("createSubscription", async () => {
    await api.createSubscription({ company_id: 1, plan_key: "starter" });
    expectFetch(`${API_BASE}/services/subscriptions`, "POST", {
      plan_key: "starter",
    });
  });

  it("getSubscriptions", async () => {
    await api.getSubscriptions(1);
    expectFetch(`${API_BASE}/services/subscriptions?company_id=1`);
  });

  it("payForSubscription", async () => {
    await api.payForSubscription(3);
    expectFetch(`${API_BASE}/services/subscriptions/3/pay`, "POST");
  });

  it("cancelSubscription", async () => {
    await api.cancelSubscription(3);
    expectFetch(`${API_BASE}/services/subscriptions/3/cancel`, "POST");
  });

  it("upgradeSubscription", async () => {
    await api.upgradeSubscription(3, { new_plan_key: "pro" });
    expectFetch(`${API_BASE}/services/subscriptions/3/upgrade`, "POST", {
      new_plan_key: "pro",
    });
  });

  it("downgradeSubscription", async () => {
    await api.downgradeSubscription(3, { new_plan_key: "free" });
    expectFetch(`${API_BASE}/services/subscriptions/3/downgrade`, "POST", {
      new_plan_key: "free",
    });
  });

  it("getUpsellItems", async () => {
    await api.getUpsellItems(1);
    expectFetch(`${API_BASE}/services/upsell/1`);
  });
});

// =============================================================================
// 27. Accounting
// =============================================================================

describe("Accounting", () => {
  it("getZohoAuthUrl", async () => {
    await api.getZohoAuthUrl(1);
    expectFetch(`${API_BASE}/accounting/zoho/auth-url?company_id=1`);
  });

  it("connectZohoBooks", async () => {
    await api.connectZohoBooks({ company_id: 1, code: "abc" });
    expectFetch(`${API_BASE}/accounting/zoho/connect`, "POST", { code: "abc" });
  });

  it("connectTally", async () => {
    await api.connectTally({ company_id: 1, company_name: "Foo" });
    expectFetch(`${API_BASE}/accounting/tally/connect`, "POST");
  });

  it("getAccountingConnection", async () => {
    await api.getAccountingConnection(1);
    expectFetch(`${API_BASE}/accounting/connection/1`);
  });

  it("getAccountingConnections", async () => {
    await api.getAccountingConnections();
    expectFetch(`${API_BASE}/accounting/connections`);
  });

  it("disconnectAccounting", async () => {
    await api.disconnectAccounting(1);
    expectFetch(`${API_BASE}/accounting/disconnect/1`, "POST");
  });

  it("syncAccountingData", async () => {
    await api.syncAccountingData(1);
    expectFetch(`${API_BASE}/accounting/sync/1`, "POST");
  });
});

// =============================================================================
// 28. CA Portal
// =============================================================================

describe("CA Portal", () => {
  it("getCaDashboardSummary", async () => {
    await api.getCaDashboardSummary();
    expectFetch(`${API_BASE}/ca/dashboard-summary`);
  });

  it("getCaCompanies", async () => {
    await api.getCaCompanies();
    expectFetch(`${API_BASE}/ca/companies`);
  });

  it("getCaCompanyCompliance", async () => {
    await api.getCaCompanyCompliance(1);
    expectFetch(`${API_BASE}/ca/companies/1/compliance`);
  });

  it("getCaCompanyDocuments", async () => {
    await api.getCaCompanyDocuments(1);
    expectFetch(`${API_BASE}/ca/companies/1/documents`);
  });

  it("markFilingComplete", async () => {
    await api.markFilingComplete(1, 5, "REF123");
    expectFetch(`${API_BASE}/ca/companies/1/filings/5`, "PUT", {
      filing_reference: "REF123",
    });
  });

  it("getCaAllTasks", async () => {
    await api.getCaAllTasks("pending");
    expectFetch(`${API_BASE}/ca/tasks?status=pending`);
  });

  it("getCaAllTasks without status", async () => {
    await api.getCaAllTasks();
    expectFetch(`${API_BASE}/ca/tasks`);
  });

  it("getCaCompanyScore", async () => {
    await api.getCaCompanyScore(1);
    expectFetch(`${API_BASE}/ca/companies/1/score`);
  });

  it("getCaCompanyPenalties", async () => {
    await api.getCaCompanyPenalties(1);
    expectFetch(`${API_BASE}/ca/companies/1/penalties`);
  });

  it("getCaAllScores", async () => {
    await api.getCaAllScores();
    expectFetch(`${API_BASE}/ca/scores`);
  });

  it("getCaTaxOverview", async () => {
    await api.getCaTaxOverview(1);
    expectFetch(`${API_BASE}/ca/companies/1/tax-overview`);
  });

  it("getCaGstDashboard", async () => {
    await api.getCaGstDashboard(1);
    expectFetch(`${API_BASE}/ca/companies/1/gst-dashboard`);
  });

  it("caTdsCalculate", async () => {
    await api.caTdsCalculate({ section: "194C", amount: 50000 });
    expectFetch(`${API_BASE}/ca/tds/calculate`, "POST");
  });

  it("getCaTdsSections", async () => {
    await api.getCaTdsSections();
    expectFetch(`${API_BASE}/ca/tds/sections`);
  });

  it("getCaTdsDueDates", async () => {
    await api.getCaTdsDueDates("Q1");
    expectFetch(`${API_BASE}/ca/tds/due-dates?quarter=Q1`);
  });

  it("getCaAuditPack", async () => {
    await api.getCaAuditPack(1);
    expectFetch(`${API_BASE}/ca/companies/1/audit-pack`);
  });

  it("addCaTaskNote", async () => {
    await api.addCaTaskNote(1, 5, "Some note");
    expectFetch(`${API_BASE}/ca/companies/1/tasks/5/notes`, "POST", {
      note: "Some note",
    });
  });

  it("getCaTaskNotes", async () => {
    await api.getCaTaskNotes(1, 5);
    expectFetch(`${API_BASE}/ca/companies/1/tasks/5/notes`);
  });

  it("getCaCompanyMessages", async () => {
    await api.getCaCompanyMessages(1);
    expectFetch(`${API_BASE}/ca/companies/1/messages`);
  });

  it("sendCaCompanyMessage", async () => {
    await api.sendCaCompanyMessage(1, "Hello");
    expectFetch(`${API_BASE}/ca/companies/1/messages`, "POST", {
      content: "Hello",
    });
  });
});

// =============================================================================
// 29. Marketplace
// =============================================================================

describe("Marketplace", () => {
  it("registerAsPartner", async () => {
    await api.registerAsPartner({
      membership_number: "M123",
      membership_type: "CA",
    });
    expectFetch(`${API_BASE}/marketplace/partners/register`, "POST", {
      membership_number: "M123",
    });
  });

  it("getPartnerDashboard", async () => {
    await api.getPartnerDashboard();
    expectFetch(`${API_BASE}/marketplace/partner/dashboard`);
  });

  it("getPartnerAssignments", async () => {
    await api.getPartnerAssignments("active");
    expectFetch(
      `${API_BASE}/marketplace/partner/assignments?status=active`,
    );
  });

  it("getPartnerEarnings", async () => {
    await api.getPartnerEarnings();
    expectFetch(`${API_BASE}/marketplace/partner/earnings`);
  });

  it("acceptAssignment", async () => {
    await api.acceptAssignment(5);
    expectFetch(`${API_BASE}/marketplace/fulfillments/5/accept`, "POST");
  });

  it("startAssignment", async () => {
    await api.startAssignment(5);
    expectFetch(`${API_BASE}/marketplace/fulfillments/5/start`, "POST");
  });

  it("deliverAssignment", async () => {
    await api.deliverAssignment(5, "Done");
    expectFetch(`${API_BASE}/marketplace/fulfillments/5/deliver`, "POST", {
      note: "Done",
    });
  });
});

// =============================================================================
// 30. Investor Portal (public, no auth — direct fetch)
// =============================================================================

describe("Investor Portal", () => {
  it("getInvestorProfile — no auth", async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({ name: "Investor" }));
    const result = await api.getInvestorProfile("inv_tok");
    const url = mockFetch.mock.calls[mockFetch.mock.calls.length - 1][0];
    expect(url).toBe(`${API_BASE}/investor-portal/inv_tok/profile`);
    expect(result).toEqual({ name: "Investor" });
  });

  it("getInvestorPortfolio", async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({ portfolio: [] }));
    await api.getInvestorPortfolio("tok");
    expectFetch(`${API_BASE}/investor-portal/tok/portfolio`);
  });

  it("getInvestorCompanyDetail", async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({}));
    await api.getInvestorCompanyDetail("tok", 5);
    expectFetch(`${API_BASE}/investor-portal/tok/companies/5`);
  });

  it("getInvestorCapTable", async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({}));
    await api.getInvestorCapTable("tok", 5);
    expectFetch(`${API_BASE}/investor-portal/tok/companies/5/cap-table`);
  });

  it("getInvestorFundingRounds", async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({}));
    await api.getInvestorFundingRounds("tok", 5);
    expectFetch(
      `${API_BASE}/investor-portal/tok/companies/5/funding-rounds`,
    );
  });

  it("getInvestorESOPGrants", async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({}));
    await api.getInvestorESOPGrants("tok", 5);
    expectFetch(
      `${API_BASE}/investor-portal/tok/companies/5/esop-grants`,
    );
  });

  it("getInvestorDocuments", async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({}));
    await api.getInvestorDocuments("tok", 5);
    expectFetch(`${API_BASE}/investor-portal/tok/companies/5/documents`);
  });

  it("getInvestorESOPSummary", async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({}));
    await api.getInvestorESOPSummary("tok");
    expectFetch(`${API_BASE}/investor-portal/tok/esop-summary`);
  });

  it("discoverCompanies without filters", async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse([]));
    await api.discoverCompanies("tok");
    expectFetch(`${API_BASE}/investor-portal/tok/discover`);
  });

  it("discoverCompanies with filters", async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse([]));
    await api.discoverCompanies("tok", { sector: "fintech", stage: "seed" });
    const url = mockFetch.mock.calls[mockFetch.mock.calls.length - 1][0];
    expect(url).toContain("sector=fintech");
    expect(url).toContain("stage=seed");
  });

  it("expressInterest", async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({ ok: true }));
    await api.expressInterest("tok", 5, "Interested!");
    const [url, opts] =
      mockFetch.mock.calls[mockFetch.mock.calls.length - 1];
    expect(url).toBe(`${API_BASE}/investor-portal/tok/interest/5`);
    expect(opts.method).toBe("POST");
    expect(JSON.parse(opts.body)).toEqual({ message: "Interested!" });
  });

  it("withdrawInterest", async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({ ok: true }));
    await api.withdrawInterest("tok", 5);
    const [url, opts] =
      mockFetch.mock.calls[mockFetch.mock.calls.length - 1];
    expect(url).toBe(`${API_BASE}/investor-portal/tok/interest/5`);
    expect(opts.method).toBe("DELETE");
  });

  it("getMyInterests", async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse([]));
    await api.getMyInterests("tok");
    expectFetch(`${API_BASE}/investor-portal/tok/my-interests`);
  });

  it("getInvestorInterests (authenticated)", async () => {
    await api.getInvestorInterests(5);
    expectFetch(`${API_BASE}/companies/5/investor-interests`);
  });
});

// =============================================================================
// 31. Copilot
// =============================================================================

describe("Copilot", () => {
  it("sendCopilotMessage", async () => {
    await api.sendCopilotMessage({
      message: "What should I do?",
      company_id: 1,
      current_page: "dashboard",
    });
    expectFetch(`${API_BASE}/copilot/message`, "POST", {
      message: "What should I do?",
      company_id: 1,
      current_page: "dashboard",
    });
  });

  it("getCopilotSuggestions", async () => {
    await api.getCopilotSuggestions(1, "cap-table");
    const url = mockFetch.mock.calls[mockFetch.mock.calls.length - 1][0];
    expect(url).toBe(
      `${API_BASE}/copilot/suggestions/1?page=cap-table`,
    );
  });
});

// =============================================================================
// 32. Chatbot
// =============================================================================

describe("Chatbot", () => {
  it("sendChatMessage", async () => {
    await api.sendChatMessage({ message: "hello" });
    expectFetch(`${API_BASE}/chatbot/message`, "POST", { message: "hello" });
  });

  it("getSuggestedQuestions without companyId", async () => {
    await api.getSuggestedQuestions();
    expectFetch(`${API_BASE}/chatbot/suggested-questions`);
  });

  it("getSuggestedQuestions with companyId", async () => {
    await api.getSuggestedQuestions(3);
    expectFetch(`${API_BASE}/chatbot/suggested-questions?company_id=3`);
  });
});

// =============================================================================
// 33. Workflow
// =============================================================================

describe("Workflow", () => {
  it("getWorkflowStatus", async () => {
    await api.getWorkflowStatus(1);
    expectFetch(`${API_BASE}/companies/1/workflow`);
  });

  it("triggerNextStep", async () => {
    await api.triggerNextStep(1);
    expectFetch(`${API_BASE}/companies/1/workflow/next`, "POST");
  });
});

// =============================================================================
// 34. Profile
// =============================================================================

describe("Profile", () => {
  it("updateProfile", async () => {
    await api.updateProfile({ full_name: "Alice" });
    expectFetch(`${API_BASE}/auth/profile`, "PUT", { full_name: "Alice" });
  });

  it("changePassword", async () => {
    await api.changePassword({
      current_password: "old",
      new_password: "new",
    });
    expectFetch(`${API_BASE}/auth/password`, "PUT", {
      current_password: "old",
      new_password: "new",
    });
  });
});

// =============================================================================
// 35. Cap Table Onboarding
// =============================================================================

describe("Cap Table Onboarding", () => {
  it("quickCapTableSetup", async () => {
    await api.quickCapTableSetup({
      company_name: "Test Co",
      shareholders: [{ name: "A", shares: 100 }],
    });
    expectFetch(`${API_BASE}/cap-table-onboarding/quick-setup`, "POST", {
      company_name: "Test Co",
    });
  });
});

// =============================================================================
// 36. Convertible Conversion
// =============================================================================

describe("Convertible Conversion", () => {
  it("previewConversion without trigger round", async () => {
    await api.previewConversion(1, 4);
    expectFetch(
      `${API_BASE}/companies/1/fundraising/rounds/4/conversion-preview`,
    );
  });

  it("previewConversion with trigger round", async () => {
    await api.previewConversion(1, 4, 5);
    expectFetch(
      `${API_BASE}/companies/1/fundraising/rounds/4/conversion-preview?trigger_round_id=5`,
    );
  });

  it("convertRound", async () => {
    await api.convertRound(1, 4);
    expectFetch(
      `${API_BASE}/companies/1/fundraising/rounds/4/convert`,
      "POST",
    );
  });
});

// =============================================================================
// 37. Deal Sharing
// =============================================================================

describe("Deal Sharing", () => {
  it("shareDeal", async () => {
    await api.shareDeal(1, { investor_email: "a@b.com" });
    expectFetch(
      `${API_BASE}/companies/1/fundraising/share-deal`,
      "POST",
      { investor_email: "a@b.com" },
    );
  });

  it("listSharedDeals", async () => {
    await api.listSharedDeals(1);
    expectFetch(`${API_BASE}/companies/1/fundraising/shared-deals`);
  });

  it("revokeSharedDeal", async () => {
    await api.revokeSharedDeal(1, 3);
    expectFetch(
      `${API_BASE}/companies/1/fundraising/shared-deals/3`,
      "DELETE",
    );
  });
});

// =============================================================================
// 38. Founder Education
// =============================================================================

describe("Founder Education", () => {
  it("getLearningPath", async () => {
    await api.getLearningPath();
    expectFetch(`${API_BASE}/founder-education/learning-path`);
  });

  it("getEducationStage", async () => {
    await api.getEducationStage("pre-incorp");
    expectFetch(`${API_BASE}/founder-education/stages/pre-incorp`);
  });

  it("getTemplateContext", async () => {
    await api.getTemplateContext("nda");
    expectFetch(`${API_BASE}/founder-education/templates/nda/context`);
  });

  it("getTemplateStage", async () => {
    await api.getTemplateStage("nda");
    expectFetch(`${API_BASE}/founder-education/templates/nda/stage`);
  });
});

// =============================================================================
// 39. Event-Triggered Compliance
// =============================================================================

describe("Event-Triggered Compliance", () => {
  it("triggerComplianceEvent", async () => {
    await api.triggerComplianceEvent(1, { event_name: "director_change" });
    expectFetch(
      `${API_BASE}/companies/1/compliance/events/trigger`,
      "POST",
      { event_name: "director_change" },
    );
  });

  it("getComplianceEventTypes", async () => {
    await api.getComplianceEventTypes(1);
    expectFetch(`${API_BASE}/companies/1/compliance/events/types`);
  });

  it("checkComplianceThresholds", async () => {
    await api.checkComplianceThresholds(1);
    expectFetch(
      `${API_BASE}/companies/1/compliance/thresholds/check`,
      "POST",
    );
  });
});

// =============================================================================
// 40. Data Room Versions
// =============================================================================

describe("Data Room Versions", () => {
  it("getDataRoomFileVersions", async () => {
    await api.getDataRoomFileVersions(1, 7);
    expectFetch(`${API_BASE}/companies/1/data-room/files/7/versions`);
  });
});
