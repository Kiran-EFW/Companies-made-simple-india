import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import ESOPPage from "@/app/dashboard/esop/page";

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
  selectCompany: jest.fn(),
  loading: false,
};

jest.mock("@/lib/company-context", () => ({
  useCompany: () => useCompanyReturn,
}));

jest.mock("next/link", () => {
  return ({ children, href, ...rest }: any) => (
    <a href={href} {...rest}>{children}</a>
  );
});

// Mock FeatureGate to just render children
jest.mock("@/components/feature-gate", () => {
  return ({ children }: any) => <>{children}</>;
});

// Mock ESOPApprovalWizard sub-component
jest.mock("@/app/dashboard/esop/ESOPApprovalWizard", () => {
  return () => <div data-testid="esop-approval-wizard">ESOP Approval Wizard</div>;
});

// Mock recharts
jest.mock("recharts", () => ({
  AreaChart: ({ children }: any) => <div data-testid="area-chart">{children}</div>,
  Area: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
  ReferenceLine: () => <div />,
}));

const mockGetESOPPlans = jest.fn();
const mockCreateESOPPlan = jest.fn();
const mockActivateESOPPlan = jest.fn();
const mockGetCompanyESOPGrants = jest.fn();
const mockCreateESOPGrant = jest.fn();
const mockExerciseESOPOptions = jest.fn();
const mockGenerateESOPGrantLetter = jest.fn();
const mockSendESOPGrantForSigning = jest.fn();
const mockGetESOPSummary = jest.fn();

jest.mock("@/lib/api", () => ({
  getESOPPlans: (...args: any[]) => mockGetESOPPlans(...args),
  createESOPPlan: (...args: any[]) => mockCreateESOPPlan(...args),
  activateESOPPlan: (...args: any[]) => mockActivateESOPPlan(...args),
  getCompanyESOPGrants: (...args: any[]) => mockGetCompanyESOPGrants(...args),
  createESOPGrant: (...args: any[]) => mockCreateESOPGrant(...args),
  exerciseESOPOptions: (...args: any[]) => mockExerciseESOPOptions(...args),
  generateESOPGrantLetter: (...args: any[]) => mockGenerateESOPGrantLetter(...args),
  sendESOPGrantForSigning: (...args: any[]) => mockSendESOPGrantForSigning(...args),
  getESOPSummary: (...args: any[]) => mockGetESOPSummary(...args),
}));

// ---------------------------------------------------------------------------
// Test data
// ---------------------------------------------------------------------------

const samplePlan = {
  id: 1,
  company_id: 1,
  plan_name: "ESOP Plan 2025",
  pool_size: 100000,
  pool_shares_allocated: 30000,
  pool_available: 70000,
  default_vesting_months: 48,
  default_cliff_months: 12,
  default_vesting_type: "monthly",
  exercise_price: 10,
  exercise_price_basis: "face_value",
  effective_date: "2025-01-01",
  expiry_date: "2035-01-01",
  status: "active",
  total_grants: 5,
  active_grants: 3,
  created_at: "2025-01-01T00:00:00Z",
  updated_at: "2025-01-01T00:00:00Z",
};

const sampleGrant = {
  id: 1,
  plan_id: 1,
  company_id: 1,
  grantee_name: "Alice Developer",
  grantee_email: "alice@test.com",
  grantee_employee_id: "EMP001",
  grantee_designation: "Senior Engineer",
  grant_date: "2025-06-01",
  number_of_options: 10000,
  exercise_price: 10,
  vesting_months: 48,
  cliff_months: 12,
  vesting_type: "monthly",
  vesting_start_date: "2025-06-01",
  options_vested: 5000,
  options_exercised: 2000,
  options_unvested: 5000,
  options_exercisable: 3000,
  options_lapsed: 0,
  status: "accepted",
  grant_letter_document_id: null,
  vesting_schedule: [],
  created_at: "2025-06-01T00:00:00Z",
  updated_at: "2025-06-01T00:00:00Z",
};

const samplePoolSummary = {
  total_pool: 100000,
  allocated: 30000,
  available: 70000,
  vested: 15000,
  unvested: 15000,
  exercised: 5000,
  lapsed: 0,
  active_plans: 1,
  active_grants: 3,
};

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("ESOPPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useCompanyReturn = {
      selectedCompany: mockSelectedCompany,
      companies: [mockSelectedCompany],
      selectCompany: jest.fn(),
      loading: false,
    };
    mockGetESOPPlans.mockResolvedValue([]);
    mockGetCompanyESOPGrants.mockResolvedValue([]);
    mockGetESOPSummary.mockResolvedValue(null);
  });

  it("renders loading state when company is loading", () => {
    useCompanyReturn = { ...useCompanyReturn, loading: true, selectedCompany: null };
    render(<ESOPPage />);
    expect(screen.getByAltText("Anvils")).toBeInTheDocument();
  });

  it("renders no company selected when selectedCompany is null", () => {
    useCompanyReturn = { ...useCompanyReturn, selectedCompany: null, loading: false };
    render(<ESOPPage />);
    expect(screen.getByText("No company selected")).toBeInTheDocument();
    expect(screen.getByText("Incorporate a New Company")).toBeInTheDocument();
  });

  it("renders the page header", async () => {
    render(<ESOPPage />);

    await waitFor(() => {
      expect(screen.getByText("ESOP Management")).toBeInTheDocument();
    });
    expect(screen.getByText(/Create plans, issue grants/)).toBeInTheDocument();
  });

  it("renders tab navigation", async () => {
    render(<ESOPPage />);

    await waitFor(() => {
      expect(screen.getByText("ESOP Plans")).toBeInTheDocument();
    });
    expect(screen.getByText("Grants")).toBeInTheDocument();
    expect(screen.getByText("Pool Summary")).toBeInTheDocument();
    expect(screen.getByText("Approval Flow")).toBeInTheDocument();
  });

  it("renders empty state when no plans exist", async () => {
    render(<ESOPPage />);

    await waitFor(() => {
      expect(screen.getByText("No ESOP Plans Yet")).toBeInTheDocument();
    });
    expect(screen.getByText("+ Create Plan")).toBeInTheDocument();
  });

  it("renders plan cards with details", async () => {
    mockGetESOPPlans.mockResolvedValue([samplePlan]);

    render(<ESOPPage />);

    await waitFor(() => {
      expect(screen.getByText("ESOP Plan 2025")).toBeInTheDocument();
    });
    expect(screen.getByText("active")).toBeInTheDocument();
    expect(screen.getByText("Pool Utilization")).toBeInTheDocument();
    expect(screen.getByText("Issue Grant")).toBeInTheDocument();
  });

  it("renders grants tab with empty state", async () => {
    render(<ESOPPage />);

    await waitFor(() => {
      expect(screen.getByText("ESOP Plans")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Grants"));

    await waitFor(() => {
      expect(screen.getByText("No Grants Issued")).toBeInTheDocument();
    });
  });

  it("renders grants table when grants exist", async () => {
    mockGetCompanyESOPGrants.mockResolvedValue([sampleGrant]);

    render(<ESOPPage />);

    await waitFor(() => {
      expect(screen.getByText("ESOP Plans")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Grants"));

    await waitFor(() => {
      expect(screen.getByText("Alice Developer")).toBeInTheDocument();
    });
    expect(screen.getByText("accepted")).toBeInTheDocument();
    expect(screen.getByText("Exercise")).toBeInTheDocument();
  });

  it("renders pool summary tab with empty state", async () => {
    render(<ESOPPage />);

    await waitFor(() => {
      expect(screen.getByText("ESOP Plans")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Pool Summary"));

    await waitFor(() => {
      expect(screen.getByText("No ESOP Pool Data")).toBeInTheDocument();
    });
  });

  it("renders pool summary with data", async () => {
    mockGetESOPSummary.mockResolvedValue(samplePoolSummary);

    render(<ESOPPage />);

    await waitFor(() => {
      expect(screen.getByText("ESOP Plans")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Pool Summary"));

    await waitFor(() => {
      expect(screen.getByText("Pool Distribution")).toBeInTheDocument();
    });
    // "100,000" appears in both the donut center and the stats card
    const totalPoolElements = screen.getAllByText("100,000");
    expect(totalPoolElements.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Active Plans")).toBeInTheDocument();
    expect(screen.getByText("Active Grants")).toBeInTheDocument();
  });

  it("renders approval flow tab with select plan message", async () => {
    render(<ESOPPage />);

    await waitFor(() => {
      expect(screen.getByText("ESOP Plans")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Approval Flow"));

    await waitFor(() => {
      expect(screen.getByText("Select a Plan")).toBeInTheDocument();
    });
  });

  it("handles API errors gracefully without crashing", async () => {
    mockGetESOPPlans.mockRejectedValue(new Error("API fail"));
    mockGetCompanyESOPGrants.mockRejectedValue(new Error("API fail"));
    mockGetESOPSummary.mockRejectedValue(new Error("API fail"));

    render(<ESOPPage />);

    // Page should still render
    await waitFor(() => {
      expect(screen.getByText("ESOP Management")).toBeInTheDocument();
    });
  });
});
