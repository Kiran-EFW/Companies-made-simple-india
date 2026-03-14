import { render, screen } from "@testing-library/react";
import StatusBadge from "@/components/status-badge";

describe("StatusBadge", () => {
  it("renders status text", () => {
    render(<StatusBadge status="completed" />);
    expect(screen.getByText("Completed")).toBeInTheDocument();
  });

  it("renders custom label", () => {
    render(<StatusBadge status="draft" label="New Draft" />);
    expect(screen.getByText("New Draft")).toBeInTheDocument();
  });

  it("handles underscored status names", () => {
    render(<StatusBadge status="in_progress" />);
    expect(screen.getByText("In Progress")).toBeInTheDocument();
  });
});
