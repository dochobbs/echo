import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { supabase, isSupabaseConfigured, SupabaseUser } from '../api/supabase';
import { api } from '../api/client';
import type { User, LearnerLevel } from '../types';

interface AuthContextType {
  user: User | null;
  supabaseUser: SupabaseUser | null;
  loading: boolean;
  signUp: (email: string, password: string, name?: string, level?: LearnerLevel) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  updateProfile: (updates: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [supabaseUser, setSupabaseUser] = useState<SupabaseUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Skip auth if Supabase not configured
    if (!isSupabaseConfigured || !supabase) {
      setLoading(false);
      return;
    }

    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) {
        setSupabaseUser(session.user);
        api.setToken(session.access_token);
        fetchProfile(session.user.id);
      } else {
        setLoading(false);
      }
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (_event, session) => {
        if (session?.user) {
          setSupabaseUser(session.user);
          api.setToken(session.access_token);
          await fetchProfile(session.user.id);
        } else {
          setSupabaseUser(null);
          setUser(null);
          api.setToken(null);
        }
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  async function fetchProfile(userId: string) {
    if (!supabase) {
      setLoading(false);
      return;
    }
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .single();

      if (error) throw error;
      setUser(data as User);
    } catch (err) {
      console.error('Error fetching profile:', err);
    } finally {
      setLoading(false);
    }
  }

  async function signUp(
    email: string,
    password: string,
    name?: string,
    level: LearnerLevel = 'student'
  ) {
    if (!supabase) throw new Error('Auth not configured');
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { name, level },
      },
    });
    if (error) throw error;
  }

  async function signIn(email: string, password: string) {
    if (!supabase) throw new Error('Auth not configured');
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    if (error) throw error;
  }

  async function signOut() {
    if (!supabase) return;
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
    setUser(null);
    setSupabaseUser(null);
    api.setToken(null);
  }

  async function updateProfile(updates: Partial<User>) {
    if (!supabase) throw new Error('Auth not configured');
    if (!supabaseUser) throw new Error('Not authenticated');

    const { data, error } = await supabase
      .from('profiles')
      .update(updates)
      .eq('id', supabaseUser.id)
      .select()
      .single();

    if (error) throw error;
    setUser(data as User);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        supabaseUser,
        loading,
        signUp,
        signIn,
        signOut,
        updateProfile,
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
