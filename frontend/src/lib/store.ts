import { create } from "zustand";

// ====== User Store ======
interface UserState {
  user: any | null;
  token: string | null;
  isAuthenticated: boolean;
  setUser: (user: any, token: string) => void;
  logout: () => void;
  updateUser: (updates: Partial<any>) => void;
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  token: typeof window !== "undefined" ? localStorage.getItem("token") : null,
  isAuthenticated: typeof window !== "undefined" ? !!localStorage.getItem("token") : false,
  setUser: (user, token) => {
    localStorage.setItem("token", token);
    set({ user, token, isAuthenticated: true });
  },
  logout: () => {
    localStorage.removeItem("token");
    set({ user: null, token: null, isAuthenticated: false });
  },
  updateUser: (updates) =>
    set((state) => ({ user: state.user ? { ...state.user, ...updates } : null })),
}));

// ====== Company Store ======
interface CompanyState {
  companies: any[];
  selectedCompany: any | null;
  loading: boolean;
  setCompanies: (companies: any[]) => void;
  selectCompany: (company: any) => void;
  updateCompany: (id: number, updates: Partial<any>) => void;
  setLoading: (loading: boolean) => void;
}

export const useCompanyStore = create<CompanyState>((set) => ({
  companies: [],
  selectedCompany: null,
  loading: false,
  setCompanies: (companies) => {
    set({ companies });
    // Auto-select first company if none selected
    set((state) => ({
      selectedCompany: state.selectedCompany || (companies.length > 0 ? companies[0] : null),
    }));
  },
  selectCompany: (company) => set({ selectedCompany: company }),
  updateCompany: (id, updates) =>
    set((state) => ({
      companies: state.companies.map((c) => (c.id === id ? { ...c, ...updates } : c)),
      selectedCompany:
        state.selectedCompany?.id === id
          ? { ...state.selectedCompany, ...updates }
          : state.selectedCompany,
    })),
  setLoading: (loading) => set({ loading }),
}));

// ====== Notification Store ======
interface NotificationState {
  unreadCount: number;
  notifications: any[];
  setUnreadCount: (count: number) => void;
  setNotifications: (notifications: any[]) => void;
  markRead: (id: number) => void;
  markAllRead: () => void;
}

export const useNotificationStore = create<NotificationState>((set) => ({
  unreadCount: 0,
  notifications: [],
  setUnreadCount: (count) => set({ unreadCount: count }),
  setNotifications: (notifications) => set({ notifications }),
  markRead: (id) =>
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, is_read: true } : n
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    })),
  markAllRead: () =>
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, is_read: true })),
      unreadCount: 0,
    })),
}));

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
