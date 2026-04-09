import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import ComplianceDashboard from "@/app/dashboard/compliance/page";

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

// Mock recharts to avoid rendering issues in jsdom
jest.mock("recharts", () => ({
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
  Cell: () => <div />,
}));

jest.mock("@/components/upsell-banner", () => {
  return () => null;
});

const mockGetComplianceScore = jest.fn();
const mockGetComplianceCalendar = jest.fn();
const mockGetUpcomingDeadlines = jest.fn();
const mockGetOverdueTasks = jest.fn();
const mockGenerateComplianceTasks = jest.fn();
const mockUpdateComplianceTask = jest.fn();
const mockGetPenaltyEstimate = jest.fn();
const mockCalculateTds = jest.fn();

jest.mock("@/lib/api", () => ({
  getComplianceScore: (...args: any[]) => mockGetComplianceScore(...args),
  getComplianceCalendar: (...args: any[]) => mockGetComplianceCalendar(...args),
  getUpcomingDeadlines: (...args: any[]) => mockGetUpcomingDeadlines(...args),
  getOverdueTasks: (...args: any[]) => mockGetOverdueTasks(...args),
  generateComplianceTasks: (...args: any[]) => mockGenerateComplianceTasks(...args),
  updateComplianceTask: (...args: any[]) => mockUpdateComplianceTask(...args),
  getPenaltyEstimate: (...args: any[]) => mockGetPenaltyEstimate(...args),
  calculateTds: (...args: any[]) => mockCalculateTds(...args),
}));

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("ComplianceDashboard", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useCompanyReturn = {
      selectedCompany: mockSelectedCompany,
      companies: [mockSelectedCompany],
    };
    mockGetComplianceScore.mockResolvedValue({
      score: 85,
      grade: "A",
      total_tasks: 10,
      completed: 7,
      overdue: 1,
      due_soon: 1,
      in_progress: 1,
      upcoming: 0,
      estimated_penalty_exposure: 5000,
      message: "Good compliance health",
    });
    mockGetComplianceCalendar.mockResolvedValue({
      calendar: [
        {
          type: "annual_return",
          title: "Annual Return (MGT-7)",
          description: "File annual return with MCA",
          frequency: "annual",
          due_date: "2026-05-30",
          days_remaining: 51,
          status: "upcoming",
          financial_year: "2025-26",
        },
      ],
    });
    mockGetUpcomingDeadlines.mockResolvedValue({
      tasks: [
        {
          id: 1,
          task_type: "annual_return",
          title: "Annual Return",
          description: "File MGT-7",
          due_date: "2026-05-01",
          status: "due_soon",
          completed_date: null,
          filing_reference: null,
        },
      ],
    });
    mockGetOverdueTasks.mockResolvedValue({ tasks: [] });
    mockGetPenaltyEstimate.mockResolvedValue({
      total_estimated_penalty: 0,
      penalty_details: [],
    });
  });

  it("renders the loading spinner when auth is loading", () => {
    // Override the auth mock for this single test
    jest.spyOn(require("@/lib/auth-context"), "useAuth").mockReturnValue({
      user: null,
      loading: true,
    });

    render(<ComplianceDashboard />);
    expect(screen.getByAltText("Anvils")).toBeInTheDocument();

    // Restore
    jest.restoreAllMocks();
  });

  it("renders no company selected state when selectedCompany is null", async () => {
    useCompanyReturn = { selectedCompany: null, companies: [] };
    render(<ComplianceDashboard />);

    await waitFor(() => {
      expect(screen.getByText("No company selected")).toBeInTheDocument();
    });
    expect(screen.getByText("Incorporate a New Company")).toBeInTheDocument();
  });

  it("renders compliance score and stats when data loads", async () => {
    render(<ComplianceDashboard />);

    await waitFor(() => {
      expect(screen.getByText("85")).toBeInTheDocument();
    });
    expect(screen.getByText("A")).toBeInTheDocument();
    expect(screen.getByText("Good compliance health")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument(); // total tasks
    expect(screen.getByText("7")).toBeInTheDocument();  // completed
  });

  it("renders the compliance calendar tab with entries", async () => {
    render(<ComplianceDashboard />);

    await waitFor(() => {
      // "Compliance Calendar" appears in both tab button and section heading
      const calendarElements = screen.getAllByText("Compliance Calendar");
      expect(calendarElements.length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getByText("Annual Return (MGT-7)")).toBeInTheDocument();
  });

  it("renders the overdue tab showing no overdue tasks", async () => {
    render(<ComplianceDashboard />);

    await waitFor(() => {
      expect(screen.getByText("85")).toBeInTheDocument();
    });

    // Click overdue tab (find the tab button specifically)
    const overdueTab = screen.getAllByText(/Overdue/).find(
      (el) => el.tagName === "BUTTON"
    )!;
    fireEvent.click(overdueTab);

    await waitFor(() => {
      expect(screen.getByText("All clear! No overdue tasks.")).toBeInTheDocument();
    });
  });

  it("renders overdue tasks when they exist", async () => {
    mockGetOverdueTasks.mockResolvedValue({
      tasks: [
        {
          id: 10,
          task_type: "gst_return",
          title: "GSTR-3B Filing",
          description: "File monthly GST return",
          due_date: "2026-03-15",
          status: "overdue",
          completed_date: null,
          filing_reference: null,
        },
      ],
    });

    render(<ComplianceDashboard />);

    await waitFor(() => {
      expect(screen.getByText("85")).toBeInTheDocument();
    });

    const overdueTab = screen.getAllByText(/Overdue/).find(
      (el) => el.tagName === "BUTTON"
    )!;
    fireEvent.click(overdueTab);

    await waitFor(() => {
      expect(screen.getByText("GSTR-3B Filing")).toBeInTheDocument();
    });
    expect(screen.getByText("Mark Complete")).toBeInTheDocument();
  });

  it("renders the TDS calculator tab", async () => {
    render(<ComplianceDashboard />);

    await waitFor(() => {
      expect(screen.getByText("85")).toBeInTheDocument();
    });

    const tdsTab = screen.getByText("TDS Calculator");
    fireEvent.click(tdsTab);

    await waitFor(() => {
      expect(screen.getByText("Section")).toBeInTheDocument();
    });
    expect(screen.getByPlaceholderText("Enter amount")).toBeInTheDocument();
  });

  it("renders upcoming deadlines section", async () => {
    render(<ComplianceDashboard />);

    await waitFor(() => {
      expect(screen.getByText("Upcoming Deadlines (Next 30 Days)")).toBeInTheDocument();
    });
    expect(screen.getByText("Annual Return")).toBeInTheDocument();
  });

  it("renders Generate Tasks button", async () => {
    render(<ComplianceDashboard />);

    await waitFor(() => {
      expect(screen.getByText("Generate Tasks")).toBeInTheDocument();
    });
  });

  it("handles API errors gracefully", async () => {
    mockGetComplianceScore.mockRejectedValue(new Error("API error"));
    mockGetComplianceCalendar.mockRejectedValue(new Error("API error"));
    mockGetUpcomingDeadlines.mockRejectedValue(new Error("API error"));
    mockGetOverdueTasks.mockRejectedValue(new Error("API error"));
    mockGetPenaltyEstimate.mockRejectedValue(new Error("API error"));

    render(<ComplianceDashboard />);

    // Should render page header at minimum without crashing
    await waitFor(() => {
      expect(screen.getByText("Compliance Dashboard")).toBeInTheDocument();
    });
  });
});
