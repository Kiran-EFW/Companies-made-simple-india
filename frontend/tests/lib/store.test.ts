import { useUIStore } from "@/lib/store";

describe("UIStore", () => {
  beforeEach(() => {
    useUIStore.setState({ toasts: [] });
  });

  it("adds and removes toasts", () => {
    useUIStore.getState().addToast("success", "Test message");
    expect(useUIStore.getState().toasts).toHaveLength(1);

    const toastId = useUIStore.getState().toasts[0].id;
    useUIStore.getState().removeToast(toastId);
    expect(useUIStore.getState().toasts).toHaveLength(0);
  });

  it("toggles sidebar", () => {
    expect(useUIStore.getState().sidebarOpen).toBe(false);
    useUIStore.getState().toggleSidebar();
    expect(useUIStore.getState().sidebarOpen).toBe(true);
    useUIStore.getState().toggleSidebar();
    expect(useUIStore.getState().sidebarOpen).toBe(false);
  });
});
