import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import ProfilePage from "@/app/dashboard/profile/page";

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

const mockRefreshUser = jest.fn();

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: jest.fn(), back: jest.fn() }),
  useSearchParams: () => new URLSearchParams(),
  useParams: () => ({}),
}));

let mockAuthReturn: any = {
  user: { id: 1, email: "test@test.com", full_name: "Test User", phone: "+919876543210" },
  loading: false,
  refreshUser: mockRefreshUser,
};

jest.mock("@/lib/auth-context", () => ({
  useAuth: () => mockAuthReturn,
}));

const mockUpdateProfile = jest.fn();
const mockChangePassword = jest.fn();

jest.mock("@/lib/api", () => ({
  updateProfile: (...args: any[]) => mockUpdateProfile(...args),
  changePassword: (...args: any[]) => mockChangePassword(...args),
}));

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("ProfilePage (Settings)", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockAuthReturn = {
      user: { id: 1, email: "test@test.com", full_name: "Test User", phone: "+919876543210" },
      loading: false,
      refreshUser: mockRefreshUser,
    };
  });

  it("returns null when user is not available", () => {
    mockAuthReturn = { user: null, loading: false, refreshUser: mockRefreshUser };
    const { container } = render(<ProfilePage />);
    expect(container.innerHTML).toBe("");
  });

  it("renders page header", () => {
    render(<ProfilePage />);
    expect(screen.getByText("Profile Settings")).toBeInTheDocument();
    expect(screen.getByText(/Manage your account details/)).toBeInTheDocument();
  });

  it("renders profile information form with user data", () => {
    render(<ProfilePage />);
    expect(screen.getByText("Profile Information")).toBeInTheDocument();
    expect(screen.getByDisplayValue("test@test.com")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Test User")).toBeInTheDocument();
    expect(screen.getByDisplayValue("+919876543210")).toBeInTheDocument();
    expect(screen.getByText("Save Changes")).toBeInTheDocument();
  });

  it("renders email field as disabled", () => {
    render(<ProfilePage />);
    const emailInput = screen.getByDisplayValue("test@test.com");
    expect(emailInput).toBeDisabled();
    expect(screen.getByText("Email cannot be changed.")).toBeInTheDocument();
  });

  it("renders change password form", () => {
    render(<ProfilePage />);
    const changePasswordElements = screen.getAllByText("Change Password");
    expect(changePasswordElements.length).toBe(2); // heading + button
    expect(screen.getByPlaceholderText("Enter current password")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Minimum 8 characters")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Re-enter new password")).toBeInTheDocument();
  });

  it("shows success message on profile update", async () => {
    mockUpdateProfile.mockResolvedValue({});
    mockRefreshUser.mockResolvedValue(undefined);

    render(<ProfilePage />);

    fireEvent.click(screen.getByText("Save Changes"));

    await waitFor(() => {
      expect(screen.getByText("Profile updated successfully.")).toBeInTheDocument();
    });
    expect(mockUpdateProfile).toHaveBeenCalled();
    expect(mockRefreshUser).toHaveBeenCalled();
  });

  it("shows error message on profile update failure", async () => {
    mockUpdateProfile.mockRejectedValue(new Error("Server error"));

    render(<ProfilePage />);

    fireEvent.click(screen.getByText("Save Changes"));

    await waitFor(() => {
      expect(screen.getByText("Server error")).toBeInTheDocument();
    });
  });

  it("validates password mismatch", async () => {
    render(<ProfilePage />);

    const currentPwInput = screen.getByPlaceholderText("Enter current password");
    const newPwInput = screen.getByPlaceholderText("Minimum 8 characters");
    const confirmPwInput = screen.getByPlaceholderText("Re-enter new password");

    fireEvent.change(currentPwInput, { target: { value: "oldpassword" } });
    fireEvent.change(newPwInput, { target: { value: "newpassword123" } });
    fireEvent.change(confirmPwInput, { target: { value: "differentpassword" } });

    const changePasswordBtn = screen.getAllByText("Change Password").find(
      (el) => el.tagName === "BUTTON"
    )!;
    fireEvent.click(changePasswordBtn);

    await waitFor(() => {
      expect(screen.getByText("New passwords do not match.")).toBeInTheDocument();
    });
    expect(mockChangePassword).not.toHaveBeenCalled();
  });

  it("validates password minimum length", async () => {
    render(<ProfilePage />);

    const currentPwInput = screen.getByPlaceholderText("Enter current password");
    const newPwInput = screen.getByPlaceholderText("Minimum 8 characters");
    const confirmPwInput = screen.getByPlaceholderText("Re-enter new password");

    fireEvent.change(currentPwInput, { target: { value: "oldpassword" } });
    fireEvent.change(newPwInput, { target: { value: "short" } });
    fireEvent.change(confirmPwInput, { target: { value: "short" } });

    const changePasswordBtn = screen.getAllByText("Change Password").find(
      (el) => el.tagName === "BUTTON"
    )!;
    fireEvent.click(changePasswordBtn);

    await waitFor(() => {
      expect(screen.getByText("New password must be at least 8 characters.")).toBeInTheDocument();
    });
    expect(mockChangePassword).not.toHaveBeenCalled();
  });

  it("shows success message on password change", async () => {
    mockChangePassword.mockResolvedValue({});

    render(<ProfilePage />);

    const currentPwInput = screen.getByPlaceholderText("Enter current password");
    const newPwInput = screen.getByPlaceholderText("Minimum 8 characters");
    const confirmPwInput = screen.getByPlaceholderText("Re-enter new password");

    fireEvent.change(currentPwInput, { target: { value: "oldpassword" } });
    fireEvent.change(newPwInput, { target: { value: "newpassword123" } });
    fireEvent.change(confirmPwInput, { target: { value: "newpassword123" } });

    const changePasswordBtn = screen.getAllByText("Change Password").find(
      (el) => el.tagName === "BUTTON"
    )!;
    fireEvent.click(changePasswordBtn);

    await waitFor(() => {
      expect(screen.getByText("Password changed successfully.")).toBeInTheDocument();
    });
    expect(mockChangePassword).toHaveBeenCalledWith({
      current_password: "oldpassword",
      new_password: "newpassword123",
    });
  });

  it("shows error message on password change failure", async () => {
    mockChangePassword.mockRejectedValue(new Error("Incorrect current password"));

    render(<ProfilePage />);

    const currentPwInput = screen.getByPlaceholderText("Enter current password");
    const newPwInput = screen.getByPlaceholderText("Minimum 8 characters");
    const confirmPwInput = screen.getByPlaceholderText("Re-enter new password");

    fireEvent.change(currentPwInput, { target: { value: "wrongpassword" } });
    fireEvent.change(newPwInput, { target: { value: "newpassword123" } });
    fireEvent.change(confirmPwInput, { target: { value: "newpassword123" } });

    const changePasswordBtn = screen.getAllByText("Change Password").find(
      (el) => el.tagName === "BUTTON"
    )!;
    fireEvent.click(changePasswordBtn);

    await waitFor(() => {
      expect(screen.getByText("Incorrect current password")).toBeInTheDocument();
    });
  });
});
