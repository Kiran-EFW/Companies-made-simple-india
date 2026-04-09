import { render, screen, waitFor } from "@testing-library/react";
import DocumentsPage from "@/app/dashboard/documents/page";

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

const mockPush = jest.fn();

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush, back: jest.fn() }),
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

const mockGetLegalTemplates = jest.fn();
const mockGetLegalDrafts = jest.fn();
const mockGetSignatureRequests = jest.fn();

jest.mock("@/lib/api", () => ({
  getLegalTemplates: (...args: any[]) => mockGetLegalTemplates(...args),
  getLegalDrafts: (...args: any[]) => mockGetLegalDrafts(...args),
  getSignatureRequests: (...args: any[]) => mockGetSignatureRequests(...args),
}));

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("DocumentsPage (Legal Documents)", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockGetSignatureRequests.mockResolvedValue([]);
  });

  it("renders loading skeleton initially", () => {
    mockGetLegalTemplates.mockReturnValue(new Promise(() => {}));
    mockGetLegalDrafts.mockReturnValue(new Promise(() => {}));
    mockGetSignatureRequests.mockReturnValue(new Promise(() => {}));

    render(<DocumentsPage />);
    // Loading skeleton uses animated divs -- the page header will not yet be visible
    expect(screen.queryByText("Legal Documents")).not.toBeInTheDocument();
  });

  it("renders main content with header after loading", async () => {
    mockGetLegalTemplates.mockResolvedValue([]);
    mockGetLegalDrafts.mockResolvedValue([]);
    mockGetSignatureRequests.mockResolvedValue([]);

    render(<DocumentsPage />);

    await waitFor(() => {
      expect(screen.getByText("Legal Documents")).toBeInTheDocument();
    });
    expect(
      screen.getByText(/Create customized legal documents/)
    ).toBeInTheDocument();
  });

  it("renders template cards grouped by category", async () => {
    mockGetLegalTemplates.mockResolvedValue([
      {
        template_type: "sha",
        name: "Shareholders Agreement",
        description: "Standard SHA for Indian startups",
        category: "Startup Essentials",
        step_count: 5,
        clause_count: 12,
      },
      {
        template_type: "employment",
        name: "Employment Agreement",
        description: "Standard employment contract",
        category: "HR & Employment",
        step_count: 4,
        clause_count: 8,
      },
    ]);
    mockGetLegalDrafts.mockResolvedValue([]);
    mockGetSignatureRequests.mockResolvedValue([]);

    render(<DocumentsPage />);

    await waitFor(() => {
      expect(screen.getByText("Shareholders Agreement")).toBeInTheDocument();
    });
    expect(screen.getByText("Employment Agreement")).toBeInTheDocument();
    expect(screen.getByText(/Startup Essentials/)).toBeInTheDocument();
    expect(screen.getByText(/HR & Employment/)).toBeInTheDocument();
  });

  it("renders create buttons on template cards", async () => {
    mockGetLegalTemplates.mockResolvedValue([
      {
        template_type: "nda",
        name: "Non-Disclosure Agreement",
        description: "Standard NDA",
        category: "Startup Essentials",
        step_count: 3,
        clause_count: 6,
      },
    ]);
    mockGetLegalDrafts.mockResolvedValue([]);
    mockGetSignatureRequests.mockResolvedValue([]);

    render(<DocumentsPage />);

    await waitFor(() => {
      expect(screen.getByText("Non-Disclosure Agreement")).toBeInTheDocument();
    });
    expect(screen.getByText("Create")).toBeInTheDocument();
  });

  it("renders empty state for user documents when no drafts exist", async () => {
    mockGetLegalTemplates.mockResolvedValue([]);
    mockGetLegalDrafts.mockResolvedValue([]);
    mockGetSignatureRequests.mockResolvedValue([]);

    render(<DocumentsPage />);

    await waitFor(() => {
      expect(screen.getByText("No documents created yet")).toBeInTheDocument();
    });
  });

  it("renders user drafts in a table", async () => {
    mockGetLegalTemplates.mockResolvedValue([]);
    mockGetLegalDrafts.mockResolvedValue([
      {
        id: 1,
        title: "My NDA Draft",
        template_type: "nda",
        status: "draft",
        created_at: "2026-01-15T10:00:00Z",
      },
      {
        id: 2,
        title: "SHA Final",
        template_type: "sha",
        status: "finalized",
        created_at: "2026-02-01T10:00:00Z",
      },
    ]);
    mockGetSignatureRequests.mockResolvedValue([]);

    render(<DocumentsPage />);

    await waitFor(() => {
      expect(screen.getByText("My NDA Draft")).toBeInTheDocument();
    });
    expect(screen.getByText("SHA Final")).toBeInTheDocument();
    expect(screen.getByText("Draft")).toBeInTheDocument();
    expect(screen.getByText("Finalized")).toBeInTheDocument();
  });

  it("shows send for signing button on finalized drafts", async () => {
    mockGetLegalTemplates.mockResolvedValue([]);
    mockGetLegalDrafts.mockResolvedValue([
      {
        id: 3,
        title: "Finalized Doc",
        template_type: "sha",
        status: "finalized",
        created_at: "2026-02-01T10:00:00Z",
      },
    ]);
    mockGetSignatureRequests.mockResolvedValue([]);

    render(<DocumentsPage />);

    await waitFor(() => {
      expect(screen.getByText("Finalized Doc")).toBeInTheDocument();
    });
    expect(screen.getByText("Send for Signing")).toBeInTheDocument();
  });

  it("renders signature requests section", async () => {
    mockGetLegalTemplates.mockResolvedValue([]);
    mockGetLegalDrafts.mockResolvedValue([]);
    mockGetSignatureRequests.mockResolvedValue([
      {
        id: 1,
        document_title: "SHA v2",
        status: "sent",
        signatories: [
          { name: "Alice", status: "signed" },
          { name: "Bob", status: "pending" },
        ],
      },
    ]);

    render(<DocumentsPage />);

    await waitFor(() => {
      expect(screen.getByText("SHA v2")).toBeInTheDocument();
    });
    expect(screen.getByText("Sent")).toBeInTheDocument();
    expect(screen.getByText("1 of 2 signed")).toBeInTheDocument();
  });

  it("renders empty signature requests state", async () => {
    mockGetLegalTemplates.mockResolvedValue([]);
    mockGetLegalDrafts.mockResolvedValue([]);
    mockGetSignatureRequests.mockResolvedValue([]);

    render(<DocumentsPage />);

    await waitFor(() => {
      expect(screen.getByText("No signature requests yet")).toBeInTheDocument();
    });
  });

  it("handles API errors gracefully", async () => {
    mockGetLegalTemplates.mockRejectedValue(new Error("API error"));
    mockGetLegalDrafts.mockRejectedValue(new Error("API error"));
    mockGetSignatureRequests.mockRejectedValue(new Error("API error"));

    render(<DocumentsPage />);

    await waitFor(() => {
      expect(screen.getByText("Legal Documents")).toBeInTheDocument();
    });
  });
});
