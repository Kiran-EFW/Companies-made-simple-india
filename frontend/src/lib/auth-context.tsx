"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import { apiCall } from "./api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface User {
  id: number;
  email: string;
  full_name: string;
  phone?: string;
  role: string;
  is_active: boolean;
}

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (token: string) => Promise<User | null>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

const AuthContext = createContext<AuthContextValue>({
  user: null,
  loading: true,
  login: async () => null,
  logout: () => {},
  refreshUser: async () => {},
});

export function useAuth(): AuthContextValue {
  return useContext(AuthContext);
}

// ---------------------------------------------------------------------------
// Provider
// ---------------------------------------------------------------------------

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = useCallback(async (): Promise<User | null> => {
    try {
      const token =
        typeof window !== "undefined"
          ? localStorage.getItem("access_token")
          : null;

      if (!token) {
        setUser(null);
        return null;
      }

      const data = await apiCall("/auth/me");
      setUser(data);
      return data;
    } catch {
      // Token invalid / expired — clear it
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
      }
      setUser(null);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const login = useCallback(
    async (token: string): Promise<User | null> => {
      if (typeof window !== "undefined") {
        localStorage.setItem("access_token", token);
      }
      return await fetchUser();
    },
    [fetchUser],
  );

  const logout = useCallback(() => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
    }
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    await fetchUser();
  }, [fetchUser]);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}
