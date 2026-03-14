import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { getMe, login as apiLogin, type LoginPayload } from '../api';

interface User {
  id: number;
  email: string;
  full_name: string | null;
  company_id: number | null;
}

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem('adminToken');
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const me = await getMe();
      setUser(me);
    } catch {
      localStorage.removeItem('adminToken');
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = useCallback(
    async (payload: LoginPayload) => {
      const { access_token } = await apiLogin(payload);
      localStorage.setItem('adminToken', access_token);
      await loadUser();
    },
    [loadUser]
  );

  const logout = useCallback(() => {
    localStorage.removeItem('adminToken');
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
