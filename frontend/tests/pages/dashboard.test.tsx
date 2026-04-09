import { render, screen, waitFor } from "@testing-library/react";
import DashboardPage from "@/app/dashboard/page";

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

const mockPush = jest.fn();
const mockBack = jest.fn();

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush, back: mockBack }),
  useSearchParams: () => new URLSearchParams(),
  useParams: () => ({}),
}));

jest.mock("@/lib/auth-context", () => ({
  useAuth: () => ({
    user: { id: 1, email: "test@test.com", full_name: "Test User" },
    loading: false,
  }),
}));

// We mock next/link to render a plain anchor so link text is testable
jest.mock("next/link", () => {
  return ({ children, href, ...rest }: any) => (
    <a href={href} {...rest}>
      {children}
    </a>
  );
});

const mockGetCompanies = jest.fn();
const mockGetCompanyMessages = jest.fn();
const mockGetUpsellItems = jest.fn();
const mockGetInvestorInterests = jest.fn();

jest.mock("@/lib/api", () => ({
  getCompanies: (...args: any[]) => mockGetCompanies(...args),
  uploadDocument: jest.fn(),
  getCompanyLogs: jest.fn().mockResolvedValue([]),
  getCompanyMessages: (...args: any[]) => mockGetCompanyMessages(...args),
  sendMessage: jest.fn(),
  markMessagesRead: jest.fn(),
  getUpsellItems: (...args: any[]) => mockGetUpsellItems(...args),
  uploadPitchDeck: jest.fn(),
  getInvestorInterests: (...args: any[]) => mockGetInvestorInterests(...args),
}));

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderPage() {
  return render(<DashboardPage />);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("DashboardPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockGetCompanyMessages.mockResolvedValue({ messages: [], unread_count: 0 });
    mockGetUpsellItems.mockResolvedValue([]);
    mockGetInvestorInterests.mockResolvedValue({ interests: [] });
  });

  it("renders the loading spinner while data is being fetched", () => {
    // getCompanies never resolves, so loading stays true
    mockGetCompanies.mockReturnValue(new Promise(() => {}));
    renderPage();
    // The loading spinner uses an img with alt "Anvils"
    expect(screen.getByAltText("Anvils")).toBeInTheDocument();
  });

  it("renders the empty state when user has no companies", async () => {
    mockGetCompanies.mockResolvedValue([]);
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Welcome to Anvils")).toBeInTheDocument();
    });
    expect(screen.getByText("Incorporate a New Company")).toBeInTheDocument();
    expect(screen.getByText("Connect an Existing Company")).toBeInTheDocument();
  });

  it("renders company cards when companies exist", async () => {
    mockGetCompanies.mockResolvedValue([
      {
        id: 1,
        approved_name: "Acme Pvt Ltd",
        entity_type: "private_limited",
        state: "karnataka",
        plan_tier: "launch",
        status: "incorporated",
        num_directors: 2,
        proposed_names: [],
        documents: [],
      },
    ]);

    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Acme Pvt Ltd")).toBeInTheDocument();
    });
    expect(screen.getByText("PRIVATE LIMITED")).toBeInTheDocument();
  });

  it("renders the pipeline steps for an in-progress company", async () => {
    mockGetCompanies.mockResolvedValue([
      {
        id: 2,
        approved_name: null,
        proposed_names: ["MyStartup"],
        entity_type: "llp",
        state: "delhi",
        plan_tier: "accelerate",
        status: "payment_completed",
        num_directors: 3,
        documents: [],
      },
    ]);

    renderPage();

    await waitFor(() => {
      expect(screen.getByText("MyStartup")).toBeInTheDocument();
    });

    // Pipeline step labels should be visible
    expect(screen.getByText("Draft & Payment")).toBeInTheDocument();
    expect(screen.getByText("Document Verification")).toBeInTheDocument();
    expect(screen.getByText("Name Approval")).toBeInTheDocument();
    expect(screen.getByText("MCA Processing")).toBeInTheDocument();
    expect(screen.getByText("Post Setup")).toBeInTheDocument();
  });

  it("shows upload documents CTA for payment_completed status", async () => {
    mockGetCompanies.mockResolvedValue([
      {
        id: 3,
        approved_name: "TestCo",
        entity_type: "private_limited",
        state: "maharashtra",
        plan_tier: "launch",
        status: "payment_completed",
        num_directors: 2,
        proposed_names: [],
        documents: [],
      },
    ]);

    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Upload Documents")).toBeInTheDocument();
    });
  });

  it("shows post-incorporation setup for incorporated status", async () => {
    mockGetCompanies.mockResolvedValue([
      {
        id: 4,
        approved_name: "IncorpCo",
        entity_type: "private_limited",
        state: "karnataka",
        plan_tier: "launch",
        status: "incorporated",
        num_directors: 2,
        proposed_names: [],
        documents: [],
      },
    ]);

    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Post-Incorporation Setup")).toBeInTheDocument();
    });
    expect(screen.getByText("Business Bank Account")).toBeInTheDocument();
    expect(screen.getByText("Cap Table")).toBeInTheDocument();
  });

  it("handles API errors gracefully", async () => {
    mockGetCompanies.mockRejectedValue(new Error("Network error"));
    renderPage();

    // Should not crash, and the loading should eventually complete
    // The page will show loading then stop when the fetch fails
    await waitFor(() => {
      // After error, loading is set to false, page renders with empty companies
      expect(screen.getByText("Welcome to Anvils")).toBeInTheDocument();
    });
  });

  it("shows the start new button when companies exist", async () => {
    mockGetCompanies.mockResolvedValue([
      {
        id: 1,
        approved_name: "ExistingCo",
        entity_type: "private_limited",
        state: "karnataka",
        plan_tier: "launch",
        status: "draft",
        num_directors: 2,
        proposed_names: [],
        documents: [],
      },
    ]);

    renderPage();

    await waitFor(() => {
      expect(screen.getByText("+ Start New")).toBeInTheDocument();
    });
  });
});
