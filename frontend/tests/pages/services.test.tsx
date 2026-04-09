import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import ServicesPage from "@/app/dashboard/services/page";

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

const mockGetServicesCatalog = jest.fn();
const mockGetSubscriptionPlans = jest.fn();
const mockGetCompanies = jest.fn();
const mockCreateServiceRequest = jest.fn();
const mockCreateSubscription = jest.fn();
const mockGetServiceRequests = jest.fn();
const mockGetSubscriptions = jest.fn();
const mockPayForServiceRequest = jest.fn();
const mockPayForSubscription = jest.fn();

jest.mock("@/lib/api", () => ({
  getServicesCatalog: (...args: any[]) => mockGetServicesCatalog(...args),
  getSubscriptionPlans: (...args: any[]) => mockGetSubscriptionPlans(...args),
  getCompanies: (...args: any[]) => mockGetCompanies(...args),
  createServiceRequest: (...args: any[]) => mockCreateServiceRequest(...args),
  createSubscription: (...args: any[]) => mockCreateSubscription(...args),
  getServiceRequests: (...args: any[]) => mockGetServiceRequests(...args),
  getSubscriptions: (...args: any[]) => mockGetSubscriptions(...args),
  payForServiceRequest: (...args: any[]) => mockPayForServiceRequest(...args),
  payForSubscription: (...args: any[]) => mockPayForSubscription(...args),
}));

// ---------------------------------------------------------------------------
// Test data
// ---------------------------------------------------------------------------

const sampleService = {
  key: "gst_registration",
  name: "GST Registration",
  short_description: "Register for GST with the government",
  category: "registration",
  frequency: "one_time",
  total: 5000,
  government_fee: 0,
  badge: "popular",
  penalty_note: null,
};

const samplePlan = {
  key: "starter",
  name: "Starter",
  target: "Early-stage startups",
  features: ["Annual Return Filing", "GST Returns"],
  annual_price: 24000,
  monthly_price: 2500,
  highlighted: false,
  is_peace_of_mind: false,
};

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("ServicesPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders loading state initially", async () => {
    mockGetServicesCatalog.mockReturnValue(new Promise(() => {}));
    mockGetSubscriptionPlans.mockReturnValue(new Promise(() => {}));
    mockGetCompanies.mockReturnValue(new Promise(() => {}));
    mockGetServiceRequests.mockReturnValue(new Promise(() => {}));
    mockGetSubscriptions.mockReturnValue(new Promise(() => {}));

    render(<ServicesPage />);

    await waitFor(() => {
      expect(screen.getByText("Loading services...")).toBeInTheDocument();
    });
  });

  it("renders the page header after loading", async () => {
    mockGetServicesCatalog.mockResolvedValue([]);
    mockGetSubscriptionPlans.mockResolvedValue([]);
    mockGetCompanies.mockResolvedValue([{ id: 1, approved_name: "Test Co" }]);
    mockGetServiceRequests.mockResolvedValue([]);
    mockGetSubscriptions.mockResolvedValue([]);

    render(<ServicesPage />);

    await waitFor(() => {
      expect(screen.getByText("Services Marketplace")).toBeInTheDocument();
    });
    expect(screen.getByText(/Post-incorporation services/)).toBeInTheDocument();
  });

  it("renders tab navigation", async () => {
    mockGetServicesCatalog.mockResolvedValue([]);
    mockGetSubscriptionPlans.mockResolvedValue([]);
    mockGetCompanies.mockResolvedValue([{ id: 1, approved_name: "Test Co" }]);
    mockGetServiceRequests.mockResolvedValue([]);
    mockGetSubscriptions.mockResolvedValue([]);

    render(<ServicesPage />);

    await waitFor(() => {
      expect(screen.getByText("Add-On Services")).toBeInTheDocument();
    });
    expect(screen.getByText("Compliance Plans")).toBeInTheDocument();
    expect(screen.getByText("My Requests")).toBeInTheDocument();
  });

  it("renders service cards with category grouping", async () => {
    mockGetServicesCatalog.mockResolvedValue([sampleService]);
    mockGetSubscriptionPlans.mockResolvedValue([]);
    mockGetCompanies.mockResolvedValue([{ id: 1, approved_name: "Test Co" }]);
    mockGetServiceRequests.mockResolvedValue([]);
    mockGetSubscriptions.mockResolvedValue([]);

    render(<ServicesPage />);

    await waitFor(() => {
      expect(screen.getByText("GST Registration")).toBeInTheDocument();
    });
    // "Registrations" appears both as category filter button and as group heading
    const registrationsElements = screen.getAllByText("Registrations");
    expect(registrationsElements.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("popular")).toBeInTheDocument();
    expect(screen.getByText("Request")).toBeInTheDocument();
  });

  it("renders category filter buttons", async () => {
    mockGetServicesCatalog.mockResolvedValue([sampleService]);
    mockGetSubscriptionPlans.mockResolvedValue([]);
    mockGetCompanies.mockResolvedValue([{ id: 1, approved_name: "Test Co" }]);
    mockGetServiceRequests.mockResolvedValue([]);
    mockGetSubscriptions.mockResolvedValue([]);

    render(<ServicesPage />);

    await waitFor(() => {
      expect(screen.getByText("All Services")).toBeInTheDocument();
    });
    expect(screen.getByText("Compliance")).toBeInTheDocument();
    expect(screen.getByText("Tax Filing")).toBeInTheDocument();
  });

  it("renders subscription plans tab", async () => {
    mockGetServicesCatalog.mockResolvedValue([]);
    mockGetSubscriptionPlans.mockResolvedValue([samplePlan]);
    mockGetCompanies.mockResolvedValue([{ id: 1, approved_name: "Test Co" }]);
    mockGetServiceRequests.mockResolvedValue([]);
    mockGetSubscriptions.mockResolvedValue([]);

    render(<ServicesPage />);

    await waitFor(() => {
      expect(screen.getByText("Compliance Plans")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Compliance Plans"));

    await waitFor(() => {
      expect(screen.getByText("Annual Compliance Packages")).toBeInTheDocument();
    });
    expect(screen.getByText("Starter")).toBeInTheDocument();
    expect(screen.getByText("Subscribe")).toBeInTheDocument();
  });

  it("renders empty state for my requests tab", async () => {
    mockGetServicesCatalog.mockResolvedValue([]);
    mockGetSubscriptionPlans.mockResolvedValue([]);
    mockGetCompanies.mockResolvedValue([{ id: 1, approved_name: "Test Co" }]);
    mockGetServiceRequests.mockResolvedValue([]);
    mockGetSubscriptions.mockResolvedValue([]);

    render(<ServicesPage />);

    await waitFor(() => {
      expect(screen.getByText("My Requests")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("My Requests"));

    await waitFor(() => {
      expect(screen.getByText("No service requests yet")).toBeInTheDocument();
    });
  });

  it("renders my requests with existing requests", async () => {
    mockGetServicesCatalog.mockResolvedValue([]);
    mockGetSubscriptionPlans.mockResolvedValue([]);
    mockGetCompanies.mockResolvedValue([{ id: 1, approved_name: "Test Co" }]);
    mockGetServiceRequests.mockResolvedValue([
      {
        id: 1,
        service_key: "gst_registration",
        service_name: "GST Registration",
        category: "registration",
        company_id: 1,
        status: "pending",
        total_amount: 5000,
        created_at: "2026-04-01T00:00:00Z",
      },
    ]);
    mockGetSubscriptions.mockResolvedValue([]);

    render(<ServicesPage />);

    await waitFor(() => {
      expect(screen.getByText("My Requests")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("My Requests"));

    await waitFor(() => {
      expect(screen.getByText("GST Registration")).toBeInTheDocument();
    });
    expect(screen.getByText("pending")).toBeInTheDocument();
  });

  it("handles API errors gracefully", async () => {
    mockGetServicesCatalog.mockRejectedValue(new Error("API error"));
    mockGetSubscriptionPlans.mockRejectedValue(new Error("API error"));
    mockGetCompanies.mockRejectedValue(new Error("API error"));
    mockGetServiceRequests.mockRejectedValue(new Error("API error"));
    mockGetSubscriptions.mockRejectedValue(new Error("API error"));

    render(<ServicesPage />);

    // Should not crash
    await waitFor(() => {
      expect(screen.getByText("Services Marketplace")).toBeInTheDocument();
    });
  });
});
