import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { api } from '../api/client';
import type { User, LearnerLevel } from '../types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signUp: (email: string, password: string, name?: string, level?: LearnerLevel) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  updateProfile: (updates: Partial<User>) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  async function checkAuth() {
    if (!api.hasToken()) {
      setLoading(false);
      return;
    }

    try {
      const userData = await api.getMe();
      setUser(userData);
    } catch (err) {
      console.error('Auth check failed:', err);
      api.logout();
    } finally {
      setLoading(false);
    }
  }

  async function refreshUser() {
    if (!api.hasToken()) return;
    try {
      const userData = await api.getMe();
      setUser(userData);
    } catch (err) {
      console.error('Refresh user failed:', err);
    }
  }

  async function signUp(
    email: string,
    password: string,
    name?: string,
    level: LearnerLevel = 'student'
  ) {
    await api.register({ email, password, name, level });
    const userData = await api.getMe();
    setUser(userData);
  }

  async function signIn(email: string, password: string) {
    await api.login({ email, password });
    const userData = await api.getMe();
    setUser(userData);
  }

  async function signOut() {
    api.logout();
    setUser(null);
  }

  async function updateProfile(updates: Partial<User>) {
    const updatedUser = await api.updateMe(updates);
    setUser(updatedUser);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        signUp,
        signIn,
        signOut,
        updateProfile,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
