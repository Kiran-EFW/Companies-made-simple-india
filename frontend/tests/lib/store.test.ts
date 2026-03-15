import { useUserStore, useUIStore } from "@/lib/store";

describe("UserStore", () => {
  beforeEach(() => {
    useUserStore.setState({ user: null, token: null, isAuthenticated: false });
  });

  it("sets user and token", () => {
    useUserStore.getState().setUser({ id: 1, email: "test@test.com" }, "fake-token");
    const state = useUserStore.getState();
    expect(state.user?.email).toBe("test@test.com");
    expect(state.token).toBe("fake-token");
    expect(state.isAuthenticated).toBe(true);
  });

  it("logs out", () => {
    useUserStore.getState().setUser({ id: 1 }, "token");
    useUserStore.getState().logout();
    const state = useUserStore.getState();
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });
});

describe("UIStore", () => {
  it("adds and removes toasts", () => {
    useUIStore.getState().addToast("success", "Test message");
    expect(useUIStore.getState().toasts).toHaveLength(1);

    const toastId = useUIStore.getState().toasts[0].id;
    useUIStore.getState().removeToast(toastId);
    expect(useUIStore.getState().toasts).toHaveLength(0);
  });
});
