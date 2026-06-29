import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  changePasswordRequest,
  fetchCurrentUser,
  loginRequest,
} from "./api";
import type { AuthUser, ChangePasswordRequest } from "./types";
import { clearAuthToken, getAuthToken, setAuthToken } from "../../shared/api/client";

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  changePassword: (body: ChangePasswordRequest) => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    const currentUser = await fetchCurrentUser();
    setUser(currentUser);
  }, []);

  const logout = useCallback(() => {
    clearAuthToken();
    setUser(null);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const tokenResponse = await loginRequest({ email, password });
    setAuthToken(tokenResponse.access_token);
    const currentUser = await fetchCurrentUser();
    setUser(currentUser);
    return currentUser.must_change_password;
  }, []);

  const changePassword = useCallback(async (body: ChangePasswordRequest) => {
    const updated = await changePasswordRequest(body);
    setUser(updated);
  }, []);

  useEffect(() => {
    const token = getAuthToken();
    if (!token) {
      setLoading(false);
      return;
    }

    fetchCurrentUser()
      .then(setUser)
      .catch(() => {
        clearAuthToken();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, logout, refreshUser, changePassword }),
    [user, loading, login, logout, refreshUser, changePassword],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
