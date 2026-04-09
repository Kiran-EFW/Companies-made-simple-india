import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import CapTablePage from "@/app/dashboard/cap-table/page";

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

jest.mock("@/components/upsell-banner", () => {
  return () => null;
});

// Mock the ShareIssuanceWizard sub-component
jest.mock("@/app/dashboard/cap-table/ShareIssuanceWizard", () => {
  return () => <div data-testid="share-issuance-wizard">Share Issuance Wizard</div>;
});

const mockApiCall = jest.fn();
const mockSimulateRound = jest.fn();
const mockSimulateExit = jest.fn();
const mockSimulateExitWaterfall = jest.fn();
const mockGetShareCertificate = jest.fn();

jest.mock("@/lib/api", () => ({
  apiCall: (...args: any[]) => mockApiCall(...args),
  simulateRound: (...args: any[]) => mockSimulateRound(...args),
  simulateExit: (...args: any[]) => mockSimulateExit(...args),
  simulateExitWaterfall: (...args: any[]) => mockSimulateExitWaterfall(...args),
  getShareCertificate: (...args: any[]) => mockGetShareCertificate(...args),
}));

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("CapTablePage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useCompanyReturn = {
      selectedCompany: mockSelectedCompany,
      companies: [mockSelectedCompany],
      selectCompany: jest.fn(),
      loading: false,
    };
    // Default: return cap table with shareholders
    mockApiCall.mockImplementation((url: string) => {
      if (url.includes("/cap-table/transactions")) {
        return Promise.resolve([]);
      }
      if (url.includes("/cap-table")) {
        return Promise.resolve({
          company_id: 1,
          total_shares: 10000,
          total_shareholders: 2,
          shareholders: [
            {
              id: 1,
              name: "Founder A",
              email: "a@test.com",
              pan_number: null,
              shares: 6000,
              share_type: "equity",
              face_value: 10,
              paid_up_value: 10,
              percentage: 60,
              date_of_allotment: "2025-01-01",
              is_promoter: true,
            },
            {
              id: 2,
              name: "Founder B",
              email: "b@test.com",
              pan_number: null,
              shares: 4000,
              share_type: "equity",
              face_value: 10,
              paid_up_value: 10,
              percentage: 40,
              date_of_allotment: "2025-01-01",
              is_promoter: true,
            },
          ],
          esop_pool: null,
          summary: {
            equity_shares: 10000,
            preference_shares: 0,
            promoter_shares: 10000,
            promoter_percentage: 100,
          },
        });
      }
      return Promise.resolve({});
    });
  });

  it("renders loading state when company is loading", () => {
    useCompanyReturn = { ...useCompanyReturn, loading: true, selectedCompany: null };
    render(<CapTablePage />);
    expect(screen.getByAltText("Anvils")).toBeInTheDocument();
  });

  it("renders no company selected when selectedCompany is null", () => {
    useCompanyReturn = { ...useCompanyReturn, selectedCompany: null, loading: false };
    render(<CapTablePage />);
    expect(screen.getByText("No company selected")).toBeInTheDocument();
  });

  it("renders cap table header", async () => {
    render(<CapTablePage />);

    await waitFor(() => {
      expect(screen.getByText("Cap Table")).toBeInTheDocument();
    });
    expect(screen.getByText(/Track shareholding/)).toBeInTheDocument();
  });

  it("renders shareholder summary cards", async () => {
    render(<CapTablePage />);

    await waitFor(() => {
      // "Shareholders" appears in both summary card and table heading
      const shareholdersElements = screen.getAllByText("Shareholders");
      expect(shareholdersElements.length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getByText("2")).toBeInTheDocument(); // total shareholders
    // "10,000" may appear in multiple summary cards (total shares, equity shares, promoter shares)
    const totalSharesElements = screen.getAllByText("10,000");
    expect(totalSharesElements.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("100%")).toBeInTheDocument(); // promoter holding
  });

  it("renders shareholders table with correct data", async () => {
    render(<CapTablePage />);

    await waitFor(() => {
      expect(screen.getByText("Founder A")).toBeInTheDocument();
    });
    expect(screen.getByText("Founder B")).toBeInTheDocument();
    expect(screen.getByText("60%")).toBeInTheDocument();
    expect(screen.getByText("40%")).toBeInTheDocument();
  });

  it("renders tab navigation", async () => {
    render(<CapTablePage />);

    await waitFor(() => {
      expect(screen.getByText("Overview")).toBeInTheDocument();
    });
    expect(screen.getByText("Issue Shares")).toBeInTheDocument();
    expect(screen.getByText("Add Shareholder")).toBeInTheDocument();
    expect(screen.getByText("Record Transfer")).toBeInTheDocument();
    expect(screen.getByText("Transaction History")).toBeInTheDocument();
    expect(screen.getByText("Round Simulator")).toBeInTheDocument();
    expect(screen.getByText("Exit Scenarios")).toBeInTheDocument();
    expect(screen.getByText("Waterfall Analysis")).toBeInTheDocument();
  });

  it("renders the round simulator tab content", async () => {
    render(<CapTablePage />);

    await waitFor(() => {
      expect(screen.getByText("Overview")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Round Simulator"));

    await waitFor(() => {
      expect(screen.getByText("Round Parameters")).toBeInTheDocument();
    });
    expect(screen.getByText("Run Simulation")).toBeInTheDocument();
  });

  it("renders add shareholder form", async () => {
    render(<CapTablePage />);

    await waitFor(() => {
      expect(screen.getByText("Overview")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Add Shareholder"));

    await waitFor(() => {
      expect(screen.getByText("Add New Shareholder")).toBeInTheDocument();
    });
    expect(screen.getByPlaceholderText("Shareholder name")).toBeInTheDocument();
  });

  it("renders empty cap table state", async () => {
    mockApiCall.mockImplementation((url: string) => {
      if (url.includes("/cap-table/transactions")) return Promise.resolve([]);
      if (url.includes("/cap-table")) return Promise.reject(new Error("No data"));
      return Promise.resolve({});
    });

    render(<CapTablePage />);

    await waitFor(() => {
      expect(screen.getByText("No Cap Table Data")).toBeInTheDocument();
    });
    expect(screen.getByText("Add First Shareholder")).toBeInTheDocument();
  });

  it("renders certificate buttons for each shareholder", async () => {
    render(<CapTablePage />);

    await waitFor(() => {
      expect(screen.getByText("Founder A")).toBeInTheDocument();
    });

    const certButtons = screen.getAllByText("Certificate");
    expect(certButtons.length).toBe(2);
  });

  it("handles API errors gracefully", async () => {
    mockApiCall.mockRejectedValue(new Error("Network error"));
    render(<CapTablePage />);

    // Should not crash
    await waitFor(() => {
      expect(screen.getByText("Cap Table")).toBeInTheDocument();
    });
  });
});
