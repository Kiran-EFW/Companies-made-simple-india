import { render, screen, waitFor } from "@testing-library/react";
import DataRoomPage from "@/app/dashboard/data-room/page";

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

const mockGetCompanies = jest.fn();
const mockGetDataRoomFolders = jest.fn();
const mockCreateDataRoomFolder = jest.fn();
const mockGetDataRoomFiles = jest.fn();
const mockUploadDataRoomFile = jest.fn();
const mockDownloadDataRoomFile = jest.fn();
const mockCreateShareLink = jest.fn();
const mockGetShareLinks = jest.fn();
const mockSetupDefaultDataRoom = jest.fn();
const mockGetRetentionAlerts = jest.fn();
const mockGetRetentionSummary = jest.fn();

jest.mock("@/lib/api", () => ({
  getCompanies: (...args: any[]) => mockGetCompanies(...args),
  getDataRoomFolders: (...args: any[]) => mockGetDataRoomFolders(...args),
  createDataRoomFolder: (...args: any[]) => mockCreateDataRoomFolder(...args),
  getDataRoomFiles: (...args: any[]) => mockGetDataRoomFiles(...args),
  uploadDataRoomFile: (...args: any[]) => mockUploadDataRoomFile(...args),
  downloadDataRoomFile: (...args: any[]) => mockDownloadDataRoomFile(...args),
  createShareLink: (...args: any[]) => mockCreateShareLink(...args),
  getShareLinks: (...args: any[]) => mockGetShareLinks(...args),
  setupDefaultDataRoom: (...args: any[]) => mockSetupDefaultDataRoom(...args),
  getRetentionAlerts: (...args: any[]) => mockGetRetentionAlerts(...args),
  getRetentionSummary: (...args: any[]) => mockGetRetentionSummary(...args),
}));

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("DataRoomPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders loading spinner initially", () => {
    mockGetCompanies.mockReturnValue(new Promise(() => {}));
    render(<DataRoomPage />);
    expect(screen.getByAltText("Anvils")).toBeInTheDocument();
  });

  it("renders no company selected when user has no companies", async () => {
    mockGetCompanies.mockResolvedValue([]);
    render(<DataRoomPage />);

    await waitFor(() => {
      expect(screen.getByText("No company selected")).toBeInTheDocument();
    });
    expect(screen.getByText("Incorporate a New Company")).toBeInTheDocument();
    expect(screen.getByText("Connect Existing Company")).toBeInTheDocument();
  });

  it("renders the page header and action buttons", async () => {
    mockGetCompanies.mockResolvedValue([
      { id: 1, approved_name: "Test Co", entity_type: "private_limited" },
    ]);
    mockGetDataRoomFolders.mockResolvedValue([]);
    mockGetDataRoomFiles.mockResolvedValue([]);
    mockGetShareLinks.mockResolvedValue([]);
    mockGetRetentionAlerts.mockResolvedValue([]);
    mockGetRetentionSummary.mockResolvedValue(null);

    render(<DataRoomPage />);

    await waitFor(() => {
      expect(screen.getByText("Data Room")).toBeInTheDocument();
    });
    expect(screen.getByText(/Secure document vault/)).toBeInTheDocument();
    expect(screen.getByText("+ Create Folder")).toBeInTheDocument();
    expect(screen.getByText("+ Share Link")).toBeInTheDocument();
  });

  it("renders setup default folders button when no folders exist", async () => {
    mockGetCompanies.mockResolvedValue([
      { id: 1, approved_name: "Test Co", entity_type: "private_limited" },
    ]);
    mockGetDataRoomFolders.mockResolvedValue([]);
    mockGetDataRoomFiles.mockResolvedValue([]);
    mockGetShareLinks.mockResolvedValue([]);
    mockGetRetentionAlerts.mockResolvedValue([]);
    mockGetRetentionSummary.mockResolvedValue(null);

    render(<DataRoomPage />);

    await waitFor(() => {
      expect(screen.getByText("Setup Default Folders")).toBeInTheDocument();
    });
    expect(screen.getByText("No folders yet. Setup defaults or create one.")).toBeInTheDocument();
  });

  it("renders folder sidebar with folders", async () => {
    mockGetCompanies.mockResolvedValue([
      { id: 1, approved_name: "Test Co", entity_type: "private_limited" },
    ]);
    mockGetDataRoomFolders.mockResolvedValue([
      { id: 1, name: "Legal Documents", description: null, parent_id: null, file_count: 3, created_at: "2026-01-01T00:00:00Z" },
      { id: 2, name: "Financial Records", description: null, parent_id: null, file_count: 5, created_at: "2026-01-01T00:00:00Z" },
    ]);
    mockGetDataRoomFiles.mockResolvedValue([]);
    mockGetShareLinks.mockResolvedValue([]);
    mockGetRetentionAlerts.mockResolvedValue([]);
    mockGetRetentionSummary.mockResolvedValue(null);

    render(<DataRoomPage />);

    await waitFor(() => {
      // "Legal Documents" appears in folder sidebar and as the file area header
      const legalDocs = screen.getAllByText("Legal Documents");
      expect(legalDocs.length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getByText("Financial Records")).toBeInTheDocument();
    expect(screen.getByText("All Files")).toBeInTheDocument();
  });

  it("renders files in folder", async () => {
    mockGetCompanies.mockResolvedValue([
      { id: 1, approved_name: "Test Co", entity_type: "private_limited" },
    ]);
    mockGetDataRoomFolders.mockResolvedValue([
      { id: 1, name: "Legal", description: null, parent_id: null, file_count: 1, created_at: "2026-01-01T00:00:00Z" },
    ]);
    mockGetDataRoomFiles.mockResolvedValue([
      {
        id: 1,
        filename: "moa.pdf",
        original_filename: "MOA.pdf",
        size: 102400,
        mime_type: "application/pdf",
        folder_id: 1,
        description: null,
        tags: ["legal"],
        retention_category: "PERMANENT",
        retention_expiry: null,
        uploaded_at: "2026-01-15T10:00:00Z",
      },
    ]);
    mockGetShareLinks.mockResolvedValue([]);
    mockGetRetentionAlerts.mockResolvedValue([]);
    mockGetRetentionSummary.mockResolvedValue(null);

    render(<DataRoomPage />);

    await waitFor(() => {
      expect(screen.getByText("MOA.pdf")).toBeInTheDocument();
    });
    expect(screen.getByText("Download")).toBeInTheDocument();
    expect(screen.getByText("Permanent")).toBeInTheDocument();
  });

  it("renders share links section when links exist", async () => {
    mockGetCompanies.mockResolvedValue([
      { id: 1, approved_name: "Test Co", entity_type: "private_limited" },
    ]);
    mockGetDataRoomFolders.mockResolvedValue([]);
    mockGetDataRoomFiles.mockResolvedValue([]);
    mockGetShareLinks.mockResolvedValue([
      {
        id: 1,
        name: "Series A DD",
        url: "https://app.anvils.in/share/abc123",
        token: "abc123",
        password_protected: true,
        expires_at: "2026-06-01T00:00:00Z",
        max_downloads: 10,
        download_count: 3,
        is_active: true,
        created_at: "2026-04-01T00:00:00Z",
      },
    ]);
    mockGetRetentionAlerts.mockResolvedValue([]);
    mockGetRetentionSummary.mockResolvedValue(null);

    render(<DataRoomPage />);

    await waitFor(() => {
      expect(screen.getByText("Share Links")).toBeInTheDocument();
    });
    expect(screen.getByText("Series A DD")).toBeInTheDocument();
    expect(screen.getByText("ACTIVE")).toBeInTheDocument();
    expect(screen.getByText("Password Protected")).toBeInTheDocument();
    expect(screen.getByText("Copy Link")).toBeInTheDocument();
  });

  it("renders retention alerts when they exist", async () => {
    mockGetCompanies.mockResolvedValue([
      { id: 1, approved_name: "Test Co", entity_type: "private_limited" },
    ]);
    mockGetDataRoomFolders.mockResolvedValue([]);
    mockGetDataRoomFiles.mockResolvedValue([]);
    mockGetShareLinks.mockResolvedValue([]);
    mockGetRetentionAlerts.mockResolvedValue([
      {
        file_id: 5,
        filename: "tax-return-2023.pdf",
        retention_category: "6_YEARS",
        expiry_date: "2029-03-31",
        days_remaining: 15,
      },
    ]);
    mockGetRetentionSummary.mockResolvedValue(null);

    render(<DataRoomPage />);

    await waitFor(() => {
      expect(screen.getByText("Retention Alerts")).toBeInTheDocument();
    });
    expect(screen.getByText("tax-return-2023.pdf")).toBeInTheDocument();
    expect(screen.getByText("15 days remaining")).toBeInTheDocument();
  });

  it("handles API errors gracefully", async () => {
    mockGetCompanies.mockRejectedValue(new Error("Network error"));
    render(<DataRoomPage />);

    // Should not crash -- page renders with empty state
    await waitFor(() => {
      expect(screen.getByText("Data Room")).toBeInTheDocument();
    });
  });
});
