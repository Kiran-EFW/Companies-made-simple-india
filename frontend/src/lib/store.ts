import { create } from "zustand";

// ====== UI Store ======
interface UIState {
  sidebarOpen: boolean;
  toasts: Array<{ id: string; type: "success" | "error" | "info" | "warning"; message: string }>;
  toggleSidebar: () => void;
  addToast: (type: "success" | "error" | "info" | "warning", message: string) => void;
  removeToast: (id: string) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: false,
  toasts: [],
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  addToast: (type, message) => {
    const id = Date.now().toString();
    set((state) => ({ toasts: [...state.toasts, { id, type, message }] }));
    // Auto-remove after 5 seconds
    setTimeout(() => {
      set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }));
    }, 5000);
  },
  removeToast: (id) =>
    set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) })),
}));
