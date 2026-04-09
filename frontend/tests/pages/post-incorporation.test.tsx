import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import PostIncorporationPage from "@/app/dashboard/post-incorporation/page";

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: jest.fn(), back: jest.fn() }),
  useSearchParams: () => new URLSearchParams(),
  useParams: () => ({}),
}));

jest.mock("@/lib/auth-context", () => ({
  useAuth: () => ({
    user: { id: 1, email: "test@test.com", full_name: "Test User" },
    loading: false,
  }),
}));

const mockSelectedCompany = {
  id: 1,
  approved_name: "Test Co",
  entity_type: "private_limited",
  plan_tier: "launch",
};

let useCompanyReturn: any = {
  selectedCompany: mockSelectedCompany,
  companies: [mockSelectedCompany],
};

jest.mock("@/lib/company-context", () => ({
  useCompany: () => useCompanyReturn,
}));

jest.mock("next/link", () => {
  return ({ children, href, ...rest }: any) => (
    <a href={href} {...rest}>{children}</a>
  );
});

jest.mock("@/components/upsell-banner", () => {
  return () => null;
});

const mockGetPostIncorporationChecklist = jest.fn();
const mockGetPostIncorporationDeadlines = jest.fn();
const mockCompletePostIncorporationTask = jest.fn();
const mockGetComplianceEventTypes = jest.fn();
const mockTriggerComplianceEvent = jest.fn();
const mockCheckComplianceThresholds = jest.fn();

jest.mock("@/lib/api", () => ({
  getPostIncorporationChecklist: (...args: any[]) => mockGetPostIncorporationChecklist(...args),
  getPostIncorporationDeadlines: (...args: any[]) => mockGetPostIncorporationDeadlines(...args),
  completePostIncorporationTask: (...args: any[]) => mockCompletePostIncorporationTask(...args),
  triggerComplianceEvent: (...args: any[]) => mockTriggerComplianceEvent(...args),
  getComplianceEventTypes: (...args: any[]) => mockGetComplianceEventTypes(...args),
  checkComplianceThresholds: (...args: any[]) => mockCheckComplianceThresholds(...args),
}));

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("PostIncorporationPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useCompanyReturn = {
      selectedCompany: mockSelectedCompany,
      companies: [mockSelectedCompany],
    };
    mockGetPostIncorporationChecklist.mockResolvedValue({
      checklist: [
        {
          task_type: "open_bank_account",
          title: "Open Bank Account",
          description: "Open a current account for the company",
          deadline: "2026-06-01",
          deadline_days: 30,
          days_remaining: 53,
          is_overdue: false,
          category: "banking",
          priority: 1,
        },
        {
          task_type: "file_inc20a",
          title: "File INC-20A",
          description: "Declaration of commencement of business",
          deadline: "2026-10-01",
          deadline_days: 180,
          days_remaining: 175,
          is_overdue: false,
          category: "compliance",
          priority: 2,
        },
      ],
    });
    mockGetPostIncorporationDeadlines.mockResolvedValue({
      deadlines: [
        {
          task_type: "open_bank_account",
          title: "Open Bank Account",
          deadline: "2026-06-01",
          days_remaining: 53,
          is_overdue: false,
        },
      ],
    });
    mockGetComplianceEventTypes.mockResolvedValue({
      events: [
        {
          event_name: "director_appointment",
          tasks: [
            {
              type: "dir_12",
              title: "File DIR-12",
              form: "DIR-12",
              section: "Section 170",
              deadline_days: 30,
            },
          ],
        },
      ],
    });
  });

  it("renders loading spinner initially", () => {
    // Override auth to loading
    jest.spyOn(require("@/lib/auth-context"), "useAuth").mockReturnValue({
      user: null,
      loading: true,
    });
    render(<PostIncorporationPage />);
    expect(screen.getByAltText("Anvils")).toBeInTheDocument();
    jest.restoreAllMocks();
  });

  it("renders no company selected when selectedCompany is null", async () => {
    useCompanyReturn = { selectedCompany: null, companies: [] };
    render(<PostIncorporationPage />);

    await waitFor(() => {
      expect(screen.getByText("No company selected")).toBeInTheDocument();
    });
  });

  it("renders the checklist tab with tasks", async () => {
    render(<PostIncorporationPage />);

    await waitFor(() => {
      const checklistElements = screen.getAllByText("Post-Incorporation Checklist");
      expect(checklistElements.length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getByText("Open Bank Account")).toBeInTheDocument();
    expect(screen.getByText("File INC-20A")).toBeInTheDocument();
  });

  it("renders summary cards with correct counts", async () => {
    render(<PostIncorporationPage />);

    await waitFor(() => {
      expect(screen.getByText("Total Tasks")).toBeInTheDocument();
    });
    // 2 total tasks, 0 completed, 2 pending, 0 overdue
    // "2" appears in both total and pending cards
    const twoElements = screen.getAllByText("2");
    expect(twoElements.length).toBeGreaterThanOrEqual(1);
  });

  it("renders completion progress bar", async () => {
    render(<PostIncorporationPage />);

    await waitFor(() => {
      expect(screen.getByText("Completion Progress")).toBeInTheDocument();
    });
    expect(screen.getByText("0%")).toBeInTheDocument();
  });

  it("shows mark complete button for pending tasks", async () => {
    render(<PostIncorporationPage />);

    await waitFor(() => {
      expect(screen.getByText("Open Bank Account")).toBeInTheDocument();
    });

    const markCompleteButtons = screen.getAllByText("Mark Complete");
    expect(markCompleteButtons.length).toBeGreaterThanOrEqual(1);
  });

  it("renders the events tab with event types", async () => {
    render(<PostIncorporationPage />);

    await waitFor(() => {
      const checklistElements = screen.getAllByText("Post-Incorporation Checklist");
      expect(checklistElements.length).toBeGreaterThanOrEqual(1);
    });

    // Click events tab
    const eventsTab = screen.getByText("Event Triggers");
    fireEvent.click(eventsTab);

    await waitFor(() => {
      expect(screen.getByText("Compliance Event Triggers")).toBeInTheDocument();
    });
    expect(screen.getByText("Director Appointment")).toBeInTheDocument();
  });

  it("renders the thresholds tab with initial state", async () => {
    render(<PostIncorporationPage />);

    await waitFor(() => {
      const checklistElements = screen.getAllByText("Post-Incorporation Checklist");
      expect(checklistElements.length).toBeGreaterThanOrEqual(1);
    });

    // Click thresholds tab
    const thresholdsTab = screen.getByText("Threshold Monitor");
    fireEvent.click(thresholdsTab);

    await waitFor(() => {
      expect(screen.getByText("No threshold data yet")).toBeInTheDocument();
    });
    expect(screen.getByText("Check Thresholds")).toBeInTheDocument();
  });

  it("handles threshold check with no triggers", async () => {
    mockCheckComplianceThresholds.mockResolvedValue({
      thresholds_triggered: 0,
      tasks: [],
    });

    render(<PostIncorporationPage />);

    await waitFor(() => {
      const checklistElements = screen.getAllByText("Post-Incorporation Checklist");
      expect(checklistElements.length).toBeGreaterThanOrEqual(1);
    });

    const thresholdsTab = screen.getByText("Threshold Monitor");
    fireEvent.click(thresholdsTab);

    await waitFor(() => {
      expect(screen.getByText("Check Thresholds")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Check Thresholds"));

    await waitFor(() => {
      expect(screen.getByText("All metrics within limits")).toBeInTheDocument();
    });
  });

  it("renders key milestones reference section", async () => {
    render(<PostIncorporationPage />);

    await waitFor(() => {
      expect(screen.getByText("Key Post-Incorporation Milestones")).toBeInTheDocument();
    });
    expect(screen.getByText("INC-20A Declaration")).toBeInTheDocument();
    expect(screen.getByText("Bank Account Opening")).toBeInTheDocument();
  });

  it("handles API errors gracefully without crashing", async () => {
    mockGetPostIncorporationChecklist.mockRejectedValue(new Error("Fail"));
    mockGetPostIncorporationDeadlines.mockRejectedValue(new Error("Fail"));
    mockGetComplianceEventTypes.mockRejectedValue(new Error("Fail"));

    render(<PostIncorporationPage />);

    await waitFor(() => {
      expect(screen.getByText("Post-Incorporation")).toBeInTheDocument();
    });
  });
});
