"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import { getCompanies, getCACompanies } from "./api";
import { useAuth } from "./auth-context";
import { isCARole } from "./roles";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface Company {
  id: number;
  entity_type: string;
  plan_tier: string;
  proposed_names: string[];
  approved_name: string | null;
  state: string;
  authorized_capital: number;
  num_directors: number;
  status: string;
  priority: string;
  cin: string | null;
  pan: string | null;
  tan: string | null;
  data: Record<string, any>;
  created_at: string;
  updated_at: string;
  directors?: any[];
  documents?: any[];
  payments?: any[];
  shareholders?: any[];
}

interface CompanyContextValue {
  companies: Company[];
  selectedCompany: Company | null;
  selectCompany: (id: number) => void;
  loading: boolean;
  refreshCompanies: () => Promise<void>;
  isCA: boolean;
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

const CompanyContext = createContext<CompanyContextValue>({
  companies: [],
  selectedCompany: null,
  selectCompany: () => {},
  loading: true,
  refreshCompanies: async () => {},
  isCA: false,
});

export function useCompany(): CompanyContextValue {
  return useContext(CompanyContext);
}

// ---------------------------------------------------------------------------
// Provider
// ---------------------------------------------------------------------------

const STORAGE_KEY = "anvils_selected_company_id";

export function CompanyProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [isCA, setIsCA] = useState(false);

  const fetchCompanies = useCallback(async () => {
    if (!user) {
      setCompanies([]);
      setSelectedId(null);
      setLoading(false);
      return;
    }

    const caUser = isCARole(user.role);
    setIsCA(caUser);

    try {
      let data: Company[];

      if (caUser) {
        // CA/CS users: fetch assigned client companies and normalize shape
        const caCompanies = await getCACompanies();
        data = (Array.isArray(caCompanies) ? caCompanies : []).map(
          (c: any) =>
            ({
              id: c.id,
              entity_type: c.entity_type || "",
              plan_tier: "",
              proposed_names: [],
              approved_name: c.name || null,
              state: "",
              authorized_capital: 0,
              num_directors: 0,
              status: c.status || "",
              priority: "",
              cin: c.cin || null,
              pan: null,
              tan: null,
              data: { pending_tasks: c.pending_tasks || 0 },
              created_at: "",
              updated_at: "",
            }) as Company
        );
      } else {
        data = await getCompanies();
      }

      setCompanies(data);

      // Restore previously selected company or pick the first one
      const stored =
        typeof window !== "undefined"
          ? localStorage.getItem(STORAGE_KEY)
          : null;
      const storedId = stored ? parseInt(stored, 10) : null;

      if (storedId && data.some((c: Company) => c.id === storedId)) {
        setSelectedId(storedId);
      } else if (data.length > 0) {
        setSelectedId(data[0].id);
      } else {
        setSelectedId(null);
      }
    } catch (err) {
      console.error("Failed to fetch companies:", err);
      setCompanies([]);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchCompanies();
  }, [fetchCompanies]);

  const selectCompany = useCallback((id: number) => {
    setSelectedId(id);
    if (typeof window !== "undefined") {
      localStorage.setItem(STORAGE_KEY, String(id));
    }
  }, []);

  const selectedCompany =
    companies.find((c) => c.id === selectedId) ?? null;

  return (
    <CompanyContext.Provider
      value={{
        companies,
        selectedCompany,
        selectCompany,
        loading,
        refreshCompanies: fetchCompanies,
        isCA,
      }}
    >
      {children}
    </CompanyContext.Provider>
  );
}
