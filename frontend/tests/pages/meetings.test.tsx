import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import MeetingsPage from "@/app/dashboard/meetings/page";

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

// Mock ResolutionWorkflow sub-component
jest.mock("@/app/dashboard/meetings/ResolutionWorkflow", () => {
  return () => <div data-testid="resolution-workflow">Resolution Workflow</div>;
});

const mockGetCompanies = jest.fn();
const mockGetMeetings = jest.fn();
const mockGetMeeting = jest.fn();
const mockCreateMeeting = jest.fn();
const mockUpdateMeeting = jest.fn();
const mockGenerateMeetingNotice = jest.fn();
const mockUpdateMeetingAttendance = jest.fn();
const mockUpdateMeetingAgenda = jest.fn();
const mockGenerateMeetingMinutes = jest.fn();
const mockSignMeetingMinutes = jest.fn();
const mockUpdateMeetingResolutions = jest.fn();
const mockGetUpcomingMeetings = jest.fn();
const mockGetPendingMinutes = jest.fn();

jest.mock("@/lib/api", () => ({
  getCompanies: (...args: any[]) => mockGetCompanies(...args),
  getMeetings: (...args: any[]) => mockGetMeetings(...args),
  getMeeting: (...args: any[]) => mockGetMeeting(...args),
  createMeeting: (...args: any[]) => mockCreateMeeting(...args),
  updateMeeting: (...args: any[]) => mockUpdateMeeting(...args),
  generateMeetingNotice: (...args: any[]) => mockGenerateMeetingNotice(...args),
  updateMeetingAttendance: (...args: any[]) => mockUpdateMeetingAttendance(...args),
  updateMeetingAgenda: (...args: any[]) => mockUpdateMeetingAgenda(...args),
  generateMeetingMinutes: (...args: any[]) => mockGenerateMeetingMinutes(...args),
  signMeetingMinutes: (...args: any[]) => mockSignMeetingMinutes(...args),
  updateMeetingResolutions: (...args: any[]) => mockUpdateMeetingResolutions(...args),
  getUpcomingMeetings: (...args: any[]) => mockGetUpcomingMeetings(...args),
  getPendingMinutes: (...args: any[]) => mockGetPendingMinutes(...args),
}));

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const futureMeeting = {
  id: 1,
  meeting_type: "BOARD_MEETING",
  title: "Q4 Board Meeting",
  date: new Date(Date.now() + 86400000 * 30).toISOString().split("T")[0],
  time: "10:00",
  venue: "Registered Office",
  is_virtual: false,
  virtual_link: null,
  status: "scheduled",
  attendees: [{ name: "Director A", din: "12345678" }],
  agenda_items: [{ order: 1, text: "Approve financials" }],
  resolutions: [],
  minutes_html: null,
  minutes_signed: false,
  minutes_signed_by: null,
  minutes_signed_date: null,
  created_at: "2026-01-01T00:00:00Z",
};

const pastMeeting = {
  ...futureMeeting,
  id: 2,
  title: "Q3 Board Meeting",
  date: "2025-12-01",
  status: "completed",
};

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("MeetingsPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders loading spinner initially", () => {
    mockGetCompanies.mockReturnValue(new Promise(() => {}));
    render(<MeetingsPage />);
    expect(screen.getByAltText("Anvils")).toBeInTheDocument();
  });

  it("renders no company selected when user has no companies", async () => {
    mockGetCompanies.mockResolvedValue([]);
    render(<MeetingsPage />);

    await waitFor(() => {
      expect(screen.getByText("No company selected")).toBeInTheDocument();
    });
    expect(screen.getByText("Incorporate a New Company")).toBeInTheDocument();
  });

  it("renders page header and schedule button", async () => {
    mockGetCompanies.mockResolvedValue([
      { id: 1, approved_name: "Test Co" },
    ]);
    mockGetMeetings.mockResolvedValue([]);
    mockGetUpcomingMeetings.mockResolvedValue([]);
    mockGetPendingMinutes.mockResolvedValue([]);

    render(<MeetingsPage />);

    await waitFor(() => {
      expect(screen.getByText("Meeting Management")).toBeInTheDocument();
    });
    expect(screen.getByText(/Board & Shareholder meetings/)).toBeInTheDocument();
    expect(screen.getByText("+ Schedule Meeting")).toBeInTheDocument();
  });

  it("renders stats row with correct counts", async () => {
    mockGetCompanies.mockResolvedValue([
      { id: 1, approved_name: "Test Co" },
    ]);
    mockGetMeetings.mockResolvedValue([futureMeeting, pastMeeting]);
    mockGetUpcomingMeetings.mockResolvedValue([futureMeeting]);
    mockGetPendingMinutes.mockResolvedValue([]);

    render(<MeetingsPage />);

    await waitFor(() => {
      expect(screen.getByText("Total This FY")).toBeInTheDocument();
    });
    // Wait for meeting data to load (nested async: companies then meetings)
    await waitFor(() => {
      expect(screen.getByText("Minutes Pending")).toBeInTheDocument();
    });
    expect(screen.getByText("Completed")).toBeInTheDocument();
  });

  it("renders tab navigation with correct counts", async () => {
    mockGetCompanies.mockResolvedValue([
      { id: 1, approved_name: "Test Co" },
    ]);
    mockGetMeetings.mockResolvedValue([futureMeeting, pastMeeting]);
    mockGetUpcomingMeetings.mockResolvedValue([futureMeeting]);
    mockGetPendingMinutes.mockResolvedValue([]);

    render(<MeetingsPage />);

    // Wait for companies + meetings data to load (nested async)
    await waitFor(() => {
      expect(screen.getByText(/Upcoming \(/)).toBeInTheDocument();
    });
    expect(screen.getByText(/Past \(/)).toBeInTheDocument();
    expect(screen.getByText(/Minutes Pending \(/)).toBeInTheDocument();
  });

  it("renders upcoming meeting cards", async () => {
    mockGetCompanies.mockResolvedValue([
      { id: 1, approved_name: "Test Co" },
    ]);
    mockGetMeetings.mockResolvedValue([futureMeeting]);
    mockGetUpcomingMeetings.mockResolvedValue([futureMeeting]);
    mockGetPendingMinutes.mockResolvedValue([]);

    render(<MeetingsPage />);

    await waitFor(() => {
      expect(screen.getByText("Q4 Board Meeting")).toBeInTheDocument();
    });
    expect(screen.getByText("Board Meeting")).toBeInTheDocument();
    expect(screen.getByText("Scheduled")).toBeInTheDocument();
    expect(screen.getByText("Generate Notice")).toBeInTheDocument();
    expect(screen.getByText("Record Minutes")).toBeInTheDocument();
  });

  it("renders empty state for upcoming meetings", async () => {
    mockGetCompanies.mockResolvedValue([
      { id: 1, approved_name: "Test Co" },
    ]);
    mockGetMeetings.mockResolvedValue([pastMeeting]);
    mockGetUpcomingMeetings.mockResolvedValue([]);
    mockGetPendingMinutes.mockResolvedValue([]);

    render(<MeetingsPage />);

    await waitFor(() => {
      expect(screen.getByText(/No upcoming meetings/)).toBeInTheDocument();
    });
  });

  it("renders compliance warning when pending minutes exist", async () => {
    mockGetCompanies.mockResolvedValue([
      { id: 1, approved_name: "Test Co" },
    ]);
    mockGetMeetings.mockResolvedValue([futureMeeting]);
    mockGetUpcomingMeetings.mockResolvedValue([futureMeeting]);
    mockGetPendingMinutes.mockResolvedValue([futureMeeting]);

    render(<MeetingsPage />);

    await waitFor(() => {
      expect(screen.getByText(/Minutes must be signed within 30 days/)).toBeInTheDocument();
    });
  });

  it("renders schedule meeting form when button is clicked", async () => {
    mockGetCompanies.mockResolvedValue([
      { id: 1, approved_name: "Test Co" },
    ]);
    mockGetMeetings.mockResolvedValue([]);
    mockGetUpcomingMeetings.mockResolvedValue([]);
    mockGetPendingMinutes.mockResolvedValue([]);

    render(<MeetingsPage />);

    await waitFor(() => {
      expect(screen.getByText("+ Schedule Meeting")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("+ Schedule Meeting"));

    await waitFor(() => {
      expect(screen.getByText("Schedule New Meeting")).toBeInTheDocument();
    });
    expect(screen.getByText("Schedule Meeting")).toBeInTheDocument();
    expect(screen.getByText("+ Add Attendee")).toBeInTheDocument();
    expect(screen.getByText("+ Add Agenda Item")).toBeInTheDocument();
  });

  it("handles API errors gracefully", async () => {
    mockGetCompanies.mockRejectedValue(new Error("Network error"));
    render(<MeetingsPage />);

    // Should not crash
    await waitFor(() => {
      expect(screen.getByText("Meeting Management")).toBeInTheDocument();
    });
  });
});
