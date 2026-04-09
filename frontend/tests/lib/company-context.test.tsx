/**
 * Tests for src/lib/company-context.tsx — CompanyProvider and useCompany hook.
 */

import React from "react";
import { render, screen, act, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { CompanyProvider, useCompany } from "@/lib/company-context";
import { useAuth } from "@/lib/auth-context";

// ── Mock dependencies ──────────────────────────────────────────────────────────
jest.mock("@/lib/api", () => ({
  getCompanies: jest.fn(),
}));

jest.mock("@/lib/auth-context", () => ({
  useAuth: jest.fn(),
}));

import { getCompanies } from "@/lib/api";

const mockGetCompanies = getCompanies as jest.MockedFunction<typeof getCompanies>;
const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;

// ── localStorage mock ──────────────────────────────────────────────────────────
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: jest.fn((key: string) => store[key] ?? null),
    setItem: jest.fn((key: string, val: string) => {
      store[key] = val;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
    _setStore(s: Record<string, string>) {
      store = { ...s };
    },
  };
})();

Object.defineProperty(window, "localStorage", { value: localStorageMock });

// ── Test consumer component ────────────────────────────────────────────────────
function TestConsumer() {
  const { companies, selectedCompany, selectCompany, loading } = useCompany();

  return (
    <div>
      <div data-testid="loading">{String(loading)}</div>
      <div data-testid="count">{companies.length}</div>
      <div data-testid="selected">
        {selectedCompany ? selectedCompany.id : "null"}
      </div>
      <div data-testid="company-names">
        {companies.map((c) => c.approved_name || c.proposed_names[0]).join(",")}
      </div>
      <button data-testid="select-2" onClick={() => selectCompany(2)}>
        Select 2
      </button>
      <button data-testid="select-3" onClick={() => selectCompany(3)}>
        Select 3
      </button>
    </div>
  );
}

// ── Sample data ────────────────────────────────────────────────────────────────
const sampleCompanies = [
  {
    id: 1,
    entity_type: "pvt_ltd",
    segment: null,
    plan_tier: "starter",
    proposed_names: ["Company A"],
    approved_name: "Company A Ltd",
    state: "karnataka",
    authorized_capital: 100000,
    num_directors: 2,
    status: "draft",
    priority: "normal",
    cin: null,
    pan: null,
    tan: null,
    data: {},
    created_at: "2024-01-01",
    updated_at: "2024-01-01",
  },
  {
    id: 2,
    entity_type: "llp",
    segment: null,
    plan_tier: "starter",
    proposed_names: ["Company B"],
    approved_name: null,
    state: "maharashtra",
    authorized_capital: 0,
    num_directors: 2,
    status: "draft",
    priority: "normal",
    cin: null,
    pan: null,
    tan: null,
    data: {},
    created_at: "2024-01-02",
    updated_at: "2024-01-02",
  },
];

// ── Tests ──────────────────────────────────────────────────────────────────────

beforeEach(() => {
  jest.clearAllMocks();
  localStorageMock._setStore({});
});

describe("CompanyProvider", () => {
  it("initial state: no companies, no selection when not logged in", async () => {
    mockUseAuth.mockReturnValue({
      user: null,
      loading: false,
      login: jest.fn(),
      logout: jest.fn(),
      refreshUser: jest.fn(),
    });

    const { unmount } = render(
      <CompanyProvider>
        <TestConsumer />
      </CompanyProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });
    expect(screen.getByTestId("count").textContent).toBe("0");
    expect(screen.getByTestId("selected").textContent).toBe("null");
    unmount();
  });

  it("fetches companies when user is logged in", async () => {
    mockUseAuth.mockReturnValue({
      user: { id: 1, email: "a@b.com", full_name: "A", role: "client", is_active: true },
      loading: false,
      login: jest.fn(),
      logout: jest.fn(),
      refreshUser: jest.fn(),
    });
    mockGetCompanies.mockResolvedValueOnce(sampleCompanies);

    const { unmount } = render(
      <CompanyProvider>
        <TestConsumer />
      </CompanyProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });
    expect(screen.getByTestId("count").textContent).toBe("2");
    // First company selected by default
    expect(screen.getByTestId("selected").textContent).toBe("1");
    unmount();
  });

  it("selects a different company", async () => {
    mockUseAuth.mockReturnValue({
      user: { id: 1, email: "a@b.com", full_name: "A", role: "client", is_active: true },
      loading: false,
      login: jest.fn(),
      logout: jest.fn(),
      refreshUser: jest.fn(),
    });
    mockGetCompanies.mockResolvedValueOnce(sampleCompanies);

    const { unmount } = render(
      <CompanyProvider>
        <TestConsumer />
      </CompanyProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });

    await act(async () => {
      await userEvent.click(screen.getByTestId("select-2"));
    });

    expect(screen.getByTestId("selected").textContent).toBe("2");
    // Should persist to localStorage
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      "anvils_selected_company_id",
      "2",
    );
    unmount();
  });

  it("restores previously selected company from localStorage", async () => {
    localStorageMock._setStore({ anvils_selected_company_id: "2" });

    mockUseAuth.mockReturnValue({
      user: { id: 1, email: "a@b.com", full_name: "A", role: "client", is_active: true },
      loading: false,
      login: jest.fn(),
      logout: jest.fn(),
      refreshUser: jest.fn(),
    });
    mockGetCompanies.mockResolvedValueOnce(sampleCompanies);

    const { unmount } = render(
      <CompanyProvider>
        <TestConsumer />
      </CompanyProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("selected").textContent).toBe("2");
    });
    unmount();
  });

  it("falls back to first company when stored id is no longer valid", async () => {
    localStorageMock._setStore({ anvils_selected_company_id: "999" });

    mockUseAuth.mockReturnValue({
      user: { id: 1, email: "a@b.com", full_name: "A", role: "client", is_active: true },
      loading: false,
      login: jest.fn(),
      logout: jest.fn(),
      refreshUser: jest.fn(),
    });
    mockGetCompanies.mockResolvedValueOnce(sampleCompanies);

    const { unmount } = render(
      <CompanyProvider>
        <TestConsumer />
      </CompanyProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("selected").textContent).toBe("1");
    });
    unmount();
  });

  it("handles API error gracefully", async () => {
    mockUseAuth.mockReturnValue({
      user: { id: 1, email: "a@b.com", full_name: "A", role: "client", is_active: true },
      loading: false,
      login: jest.fn(),
      logout: jest.fn(),
      refreshUser: jest.fn(),
    });
    mockGetCompanies.mockRejectedValueOnce(new Error("Network error"));

    const consoleSpy = jest.spyOn(console, "error").mockImplementation();

    const { unmount } = render(
      <CompanyProvider>
        <TestConsumer />
      </CompanyProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });
    expect(screen.getByTestId("count").textContent).toBe("0");
    expect(screen.getByTestId("selected").textContent).toBe("null");

    consoleSpy.mockRestore();
    unmount();
  });

  it("sets selectedCompany to null when no companies exist", async () => {
    mockUseAuth.mockReturnValue({
      user: { id: 1, email: "a@b.com", full_name: "A", role: "client", is_active: true },
      loading: false,
      login: jest.fn(),
      logout: jest.fn(),
      refreshUser: jest.fn(),
    });
    mockGetCompanies.mockResolvedValueOnce([]);

    const { unmount } = render(
      <CompanyProvider>
        <TestConsumer />
      </CompanyProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });
    expect(screen.getByTestId("selected").textContent).toBe("null");
    unmount();
  });
});
