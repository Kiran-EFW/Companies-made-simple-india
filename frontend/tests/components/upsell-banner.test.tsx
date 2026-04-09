/**
 * Tests for src/components/upsell-banner.tsx — UpsellBanner component.
 */

import React from "react";
import { render, screen, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import UpsellBanner from "@/components/upsell-banner";

// ── Mock dependencies ──────────────────────────────────────────────────────────
jest.mock("@/lib/api", () => ({
  getUpsellItems: jest.fn(),
}));

jest.mock("@/lib/subscription-tiers", () => ({
  PAGE_UPSELL_SERVICES: {
    compliance: ["gst_registration", "itr_company", "annual_roc_filing"],
    gst: ["gst_monthly_filing", "gst_registration"],
    empty_page: [],
  },
}));

// Mock next/link since we are not in a Next.js runtime
jest.mock("next/link", () => {
  return ({ children, href, ...props }: any) => (
    <a href={href} {...props}>
      {children}
    </a>
  );
});

import { getUpsellItems } from "@/lib/api";

const mockGetUpsellItems = getUpsellItems as jest.MockedFunction<
  typeof getUpsellItems
>;

// ── sessionStorage mock ────────────────────────────────────────────────────────
const sessionStorageMock = (() => {
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

Object.defineProperty(window, "sessionStorage", { value: sessionStorageMock });

// ── Sample items ───────────────────────────────────────────────────────────────
const sampleItems = [
  {
    service_key: "gst_registration",
    name: "GST Registration",
    short_description: "Register for GST",
    category: "tax",
    total: 2500,
    urgency: "high",
    reason: "Required within 30 days of incorporation",
  },
  {
    service_key: "itr_company",
    name: "Company ITR Filing",
    short_description: "File ITR",
    category: "tax",
    total: 7500,
    urgency: "medium",
    reason: "Due by September 30",
  },
  {
    service_key: "annual_roc_filing",
    name: "Annual ROC Filing",
    short_description: "File annual returns",
    category: "compliance",
    total: 5000,
    urgency: "low",
    reason: "Due by December 31",
  },
];

// ── Tests ──────────────────────────────────────────────────────────────────────

beforeEach(() => {
  jest.clearAllMocks();
  sessionStorageMock._setStore({});
});

describe("UpsellBanner", () => {
  it("renders nothing when pageKey has no associated services", async () => {
    const { container } = render(
      <UpsellBanner pageKey="empty_page" companyId={1} />,
    );

    // The component should render nothing (null)
    await waitFor(() => {
      expect(container.innerHTML).toBe("");
    });
    expect(mockGetUpsellItems).not.toHaveBeenCalled();
  });

  it("renders nothing when pageKey is unknown (no upsell config)", async () => {
    const { container } = render(
      <UpsellBanner pageKey="unknown_page" companyId={1} />,
    );

    await waitFor(() => {
      expect(container.innerHTML).toBe("");
    });
    expect(mockGetUpsellItems).not.toHaveBeenCalled();
  });

  it("renders nothing when API returns no matching items", async () => {
    mockGetUpsellItems.mockResolvedValueOnce([
      {
        service_key: "unrelated_service",
        name: "Unrelated",
        short_description: "Not relevant",
        category: "other",
        total: 1000,
        urgency: "low",
        reason: "No match",
      },
    ]);

    const { container } = render(
      <UpsellBanner pageKey="compliance" companyId={1} />,
    );

    await waitFor(() => {
      expect(container.innerHTML).toBe("");
    });
  });

  it("renders banner with matching upsell items", async () => {
    mockGetUpsellItems.mockResolvedValueOnce(sampleItems);

    render(<UpsellBanner pageKey="compliance" companyId={1} />);

    await waitFor(() => {
      expect(screen.getByText("GST Registration")).toBeInTheDocument();
    });

    // Should show the reason text
    expect(
      screen.getByText("Required within 30 days of incorporation"),
    ).toBeInTheDocument();

    // Should show the "Recommended services" label (plural for multiple items)
    expect(screen.getByText(/Recommended services/i)).toBeInTheDocument();
  });

  it("limits display to 2 items maximum", async () => {
    mockGetUpsellItems.mockResolvedValueOnce(sampleItems);

    render(<UpsellBanner pageKey="compliance" companyId={1} />);

    await waitFor(() => {
      expect(screen.getByText("GST Registration")).toBeInTheDocument();
    });

    // First two items should be present
    expect(screen.getByText("Company ITR Filing")).toBeInTheDocument();
    // Third item should NOT be visible
    expect(screen.queryByText("Annual ROC Filing")).not.toBeInTheDocument();
  });

  it("renders price links with formatted amounts", async () => {
    mockGetUpsellItems.mockResolvedValueOnce(sampleItems);

    render(<UpsellBanner pageKey="compliance" companyId={1} />);

    await waitFor(() => {
      expect(screen.getByText("GST Registration")).toBeInTheDocument();
    });

    // Check that price links exist (using the rupee symbol)
    const links = screen.getAllByRole("link");
    expect(links.length).toBeGreaterThanOrEqual(1);
    // Links should point to services page with highlight param
    expect(links[0]).toHaveAttribute(
      "href",
      "/dashboard/services?highlight=gst_registration",
    );
  });

  it("handles API error gracefully (renders nothing)", async () => {
    mockGetUpsellItems.mockRejectedValueOnce(new Error("API error"));

    const { container } = render(
      <UpsellBanner pageKey="compliance" companyId={1} />,
    );

    await waitFor(() => {
      expect(container.innerHTML).toBe("");
    });
  });

  it("dismisses the banner on button click", async () => {
    mockGetUpsellItems.mockResolvedValueOnce(sampleItems);

    render(<UpsellBanner pageKey="compliance" companyId={1} />);

    await waitFor(() => {
      expect(screen.getByText("GST Registration")).toBeInTheDocument();
    });

    // Click the dismiss button
    const dismissButton = screen.getByRole("button", { name: /dismiss/i });
    await act(async () => {
      await userEvent.click(dismissButton);
    });

    // Banner should disappear
    expect(screen.queryByText("GST Registration")).not.toBeInTheDocument();

    // Should persist dismissal in sessionStorage
    expect(sessionStorageMock.setItem).toHaveBeenCalledWith(
      "upsell_dismissed_compliance_1",
      "1",
    );
  });

  it("does not render if previously dismissed in session", async () => {
    sessionStorageMock._setStore({
      upsell_dismissed_compliance_1: "1",
    });

    const { container } = render(
      <UpsellBanner pageKey="compliance" companyId={1} />,
    );

    await waitFor(() => {
      expect(container.innerHTML).toBe("");
    });
    // Should not even call the API
    expect(mockGetUpsellItems).not.toHaveBeenCalled();
  });

  it("shows singular label when only one item matches", async () => {
    mockGetUpsellItems.mockResolvedValueOnce([sampleItems[0]]);

    render(<UpsellBanner pageKey="compliance" companyId={1} />);

    await waitFor(() => {
      expect(screen.getByText("GST Registration")).toBeInTheDocument();
    });

    expect(screen.getByText(/Recommended service$/i)).toBeInTheDocument();
  });

  it("only filters to page-relevant service keys", async () => {
    // "gst" page only cares about gst_monthly_filing and gst_registration
    mockGetUpsellItems.mockResolvedValueOnce(sampleItems);

    render(<UpsellBanner pageKey="gst" companyId={1} />);

    await waitFor(() => {
      expect(screen.getByText("GST Registration")).toBeInTheDocument();
    });

    // itr_company and annual_roc_filing should not appear even though API returned them
    expect(screen.queryByText("Company ITR Filing")).not.toBeInTheDocument();
    expect(screen.queryByText("Annual ROC Filing")).not.toBeInTheDocument();
  });
});
