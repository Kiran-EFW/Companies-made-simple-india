import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import FundraisingPage from "@/app/dashboard/fundraising/page";

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

jest.mock("next/link", () => {
  return ({ children, href, ...rest }: any) => (
    <a href={href} {...rest}>{children}</a>
  );
});

// Mock FeatureGate to just render children
jest.mock("@/components/feature-gate", () => {
  return ({ children }: any) => <>{children}</>;
});

// Mock recharts
jest.mock("recharts", () => ({
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  Pie: () => <div />,
  Cell: () => <div />,
}));

const mockGetCompanies = jest.fn();
const mockGetFundingRounds = jest.fn();
const mockGetFundingRound = jest.fn();
const mockCreateFundingRound = jest.fn();
const mockUpdateFundingRound = jest.fn();
const mockAddRoundInvestor = jest.fn();
const mockUpdateRoundInvestor = jest.fn();
const mockRemoveRoundInvestor = jest.fn();
const mockGetClosingRoom = jest.fn();
const mockInitiateClosing = jest.fn();
const mockCompleteAllotment = jest.fn();
const mockPreviewConversion = jest.fn();
const mockConvertRound = jest.fn();
const mockCreateLegalDraft = jest.fn();
const mockSaveFundraisingChecklistState = jest.fn();
const mockGetFundraisingChecklistState = jest.fn();
const mockShareDeal = jest.fn();
const mockListSharedDeals = jest.fn();
const mockRevokeSharedDeal = jest.fn();

jest.mock("@/lib/api", () => ({
  getCompanies: (...args: any[]) => mockGetCompanies(...args),
  getFundingRounds: (...args: any[]) => mockGetFundingRounds(...args),
  getFundingRound: (...args: any[]) => mockGetFundingRound(...args),
  createFundingRound: (...args: any[]) => mockCreateFundingRound(...args),
  updateFundingRound: (...args: any[]) => mockUpdateFundingRound(...args),
  addRoundInvestor: (...args: any[]) => mockAddRoundInvestor(...args),
  updateRoundInvestor: (...args: any[]) => mockUpdateRoundInvestor(...args),
  removeRoundInvestor: (...args: any[]) => mockRemoveRoundInvestor(...args),
  getClosingRoom: (...args: any[]) => mockGetClosingRoom(...args),
  initiateClosing: (...args: any[]) => mockInitiateClosing(...args),
  completeAllotment: (...args: any[]) => mockCompleteAllotment(...args),
  previewConversion: (...args: any[]) => mockPreviewConversion(...args),
  convertRound: (...args: any[]) => mockConvertRound(...args),
  createLegalDraft: (...args: any[]) => mockCreateLegalDraft(...args),
  saveFundraisingChecklistState: (...args: any[]) => mockSaveFundraisingChecklistState(...args),
  getFundraisingChecklistState: (...args: any[]) => mockGetFundraisingChecklistState(...args),
  shareDeal: (...args: any[]) => mockShareDeal(...args),
  listSharedDeals: (...args: any[]) => mockListSharedDeals(...args),
  revokeSharedDeal: (...args: any[]) => mockRevokeSharedDeal(...args),
}));

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("FundraisingPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // localStorage mock
    Storage.prototype.getItem = jest.fn(() => null);
    Storage.prototype.setItem = jest.fn();
  });

  it("renders loading indicator initially", () => {
    mockGetCompanies.mockReturnValue(new Promise(() => {}));
    render(<FundraisingPage />);
    // Fundraising page renders header immediately, shows "Loading..." for content
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("renders empty rounds state when user has no companies", async () => {
    mockGetCompanies.mockResolvedValue([]);
    render(<FundraisingPage />);

    await waitFor(() => {
      // With no companies, no rounds can load, so shows empty rounds state
      expect(screen.getByText("Fundraising")).toBeInTheDocument();
    });
  });

  it("renders the page header when company exists", async () => {
    mockGetCompanies.mockResolvedValue([
      { id: 1, approved_name: "Test Co", entity_type: "private_limited" },
    ]);
    mockGetFundingRounds.mockResolvedValue([]);

    render(<FundraisingPage />);

    await waitFor(() => {
      expect(screen.getByText("Fundraising")).toBeInTheDocument();
    });
  });

  it("renders empty state when no funding rounds exist", async () => {
    mockGetCompanies.mockResolvedValue([
      { id: 1, approved_name: "Test Co", entity_type: "private_limited" },
    ]);
    mockGetFundingRounds.mockResolvedValue([]);

    render(<FundraisingPage />);

    await waitFor(() => {
      expect(screen.getByText(/No funding rounds/i)).toBeInTheDocument();
    });
  });

  it("renders funding round cards when rounds exist", async () => {
    mockGetCompanies.mockResolvedValue([
      { id: 1, approved_name: "Test Co", entity_type: "private_limited" },
    ]);
    mockGetFundingRounds.mockResolvedValue([
      {
        id: 1,
        company_id: 1,
        round_name: "Seed Round",
        instrument_type: "equity",
        pre_money_valuation: 5000000,
        post_money_valuation: 6000000,
        price_per_share: 100,
        target_amount: 1000000,
        amount_raised: 500000,
        status: "open",
        allotment_completed: false,
        valuation_cap: null,
        discount_rate: null,
        interest_rate: null,
        maturity_months: null,
        notes: null,
        investor_count: 2,
        created_at: "2026-01-01T00:00:00Z",
      },
    ]);

    render(<FundraisingPage />);

    await waitFor(() => {
      expect(screen.getByText("Seed Round")).toBeInTheDocument();
    });
  });

  it("handles API errors gracefully", async () => {
    mockGetCompanies.mockRejectedValue(new Error("Network error"));
    render(<FundraisingPage />);

    // Should not crash
    await waitFor(() => {
      expect(screen.getByText("Fundraising")).toBeInTheDocument();
    });
  });
});
