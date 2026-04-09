/**
 * Tests for src/lib/auth-context.tsx — AuthProvider and useAuth hook.
 */

import React from "react";
import { render, screen, act, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

// ── Set act environment before imports ──────────────────────────────────────────
(globalThis as any).IS_REACT_ACT_ENVIRONMENT = true;

// ── localStorage mock ──────────────────────────────────────────────────────────
let storageStore: Record<string, string> = {};
const localStorageMock = {
  getItem: jest.fn((key: string) => storageStore[key] ?? null),
  setItem: jest.fn((key: string, val: string) => {
    storageStore[key] = val;
  }),
  removeItem: jest.fn((key: string) => {
    delete storageStore[key];
  }),
  clear: jest.fn(() => {
    storageStore = {};
  }),
};
Object.defineProperty(window, "localStorage", { value: localStorageMock });

// ── Mock apiCall ────────────────────────────────────────────────────────────────
jest.mock("@/lib/api", () => ({
  apiCall: jest.fn(),
}));

import { apiCall } from "@/lib/api";
import { AuthProvider, useAuth } from "@/lib/auth-context";

const mockApiCall = apiCall as jest.MockedFunction<typeof apiCall>;

// ── Test consumer component ────────────────────────────────────────────────────
function TestConsumer() {
  const { user, loading, login, logout } = useAuth();

  return (
    <div>
      <div data-testid="loading">{String(loading)}</div>
      <div data-testid="user">{user ? user.email : "null"}</div>
      <button data-testid="login" onClick={() => login("new-token")}>
        Login
      </button>
      <button data-testid="logout" onClick={logout}>
        Logout
      </button>
    </div>
  );
}

// ── Setup / teardown ───────────────────────────────────────────────────────────

beforeEach(() => {
  jest.clearAllMocks();
  storageStore = {};
});

// ── Tests ──────────────────────────────────────────────────────────────────────

describe("AuthProvider", () => {
  it("starts in loading state with no user when no token exists", async () => {
    // No token in storage, so fetchUser finds no token, sets user to null
    // apiCall should never be called because there is no token
    const { unmount } = render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });
    expect(screen.getByTestId("user").textContent).toBe("null");
    // apiCall should NOT have been called since there was no token
    expect(mockApiCall).not.toHaveBeenCalled();
    unmount();
  });

  it("auto-loads user from token on mount", async () => {
    storageStore = { access_token: "existing-token" };

    const mockUser = {
      id: 1,
      email: "alice@test.com",
      full_name: "Alice",
      role: "client",
      is_active: true,
    };
    mockApiCall.mockResolvedValueOnce(mockUser);

    const { unmount } = render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("user").textContent).toBe("alice@test.com");
    });
    expect(screen.getByTestId("loading").textContent).toBe("false");
    expect(mockApiCall).toHaveBeenCalledWith("/auth/me");
    unmount();
  });

  it("sets user and stores token on login", async () => {
    // Initial mount: no token => no user
    const { unmount } = render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });
    expect(screen.getByTestId("user").textContent).toBe("null");

    // Now set up mock for the login call.
    // login("new-token") stores the token, then calls fetchUser -> apiCall("/auth/me")
    const mockUser = {
      id: 2,
      email: "bob@test.com",
      full_name: "Bob",
      role: "client",
      is_active: true,
    };
    mockApiCall.mockResolvedValueOnce(mockUser);

    await act(async () => {
      await userEvent.click(screen.getByTestId("login"));
    });

    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      "access_token",
      "new-token",
    );

    await waitFor(() => {
      expect(screen.getByTestId("user").textContent).toBe("bob@test.com");
    });
    unmount();
  });

  it("clears user and token on logout", async () => {
    storageStore = { access_token: "tok" };

    const mockUser = {
      id: 1,
      email: "alice@test.com",
      full_name: "Alice",
      role: "client",
      is_active: true,
    };
    mockApiCall.mockResolvedValueOnce(mockUser);

    const { unmount } = render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("user").textContent).toBe("alice@test.com");
    });

    await act(async () => {
      await userEvent.click(screen.getByTestId("logout"));
    });

    expect(screen.getByTestId("user").textContent).toBe("null");
    expect(localStorageMock.removeItem).toHaveBeenCalledWith("access_token");
    unmount();
  });

  it("clears token on invalid/expired token", async () => {
    storageStore = { access_token: "expired-token" };
    mockApiCall.mockRejectedValueOnce(new Error("401 Unauthorized"));

    const { unmount } = render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });

    expect(screen.getByTestId("user").textContent).toBe("null");
    expect(localStorageMock.removeItem).toHaveBeenCalledWith("access_token");
    unmount();
  });
});
