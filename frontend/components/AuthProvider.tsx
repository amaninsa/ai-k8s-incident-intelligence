"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useRouter } from "next/navigation";

import { authEnabled, insforge } from "@/lib/insforge";
import { registerUnauthorizedHandler, setAccessToken } from "@/services/api";

interface AuthUser {
  id: string;
  email?: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  authEnabled: boolean;
  pendingVerificationEmail: string | null;
  signIn: (email: string, password: string) => Promise<string | null>;
  signUp: (email: string, password: string, name?: string) => Promise<string | null | "verification_required">;
  verifyEmail: (email: string, otp: string) => Promise<string | null>;
  resendVerificationEmail: (email: string) => Promise<string | null>;
  clearPendingVerification: () => void;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(authEnabled);
  const [pendingVerificationEmail, setPendingVerificationEmail] = useState<string | null>(
    null,
  );

  const persistSession = useCallback((accessToken: string | null, nextUser: AuthUser | null) => {
    if (accessToken) {
      localStorage.setItem("insforge_access_token", accessToken);
      setAccessToken(accessToken);
    } else {
      localStorage.removeItem("insforge_access_token");
      setAccessToken(null);
    }
    setUser(nextUser);
  }, []);

  const clearPendingVerification = useCallback(() => {
    setPendingVerificationEmail(null);
  }, []);

  const signOut = useCallback(async () => {
    await insforge.auth.signOut();
    persistSession(null, null);
    clearPendingVerification();
    if (authEnabled) {
      router.push("/login");
    }
  }, [clearPendingVerification, persistSession, router]);

  useEffect(() => {
    registerUnauthorizedHandler(() => {
      persistSession(null, null);
      clearPendingVerification();
      if (authEnabled) {
        router.push("/login");
      }
    });
  }, [clearPendingVerification, persistSession, router]);

  useEffect(() => {
    if (!authEnabled) {
      setLoading(false);
      return;
    }

    const bootstrap = async () => {
      let { data } = await insforge.auth.getCurrentUser();
      if (!data?.user) {
        const refreshResult = await insforge.auth.refreshSession();
        if (refreshResult.data?.accessToken && refreshResult.data.user) {
          persistSession(refreshResult.data.accessToken, {
            id: refreshResult.data.user.id,
            email: refreshResult.data.user.email,
          });
          setLoading(false);
          return;
        }
        persistSession(null, null);
        setLoading(false);
        return;
      }

      const refreshResult = await insforge.auth.refreshSession();
      if (refreshResult.data?.accessToken && refreshResult.data.user) {
        persistSession(refreshResult.data.accessToken, {
          id: refreshResult.data.user.id,
          email: refreshResult.data.user.email,
        });
      } else {
        const storedToken = localStorage.getItem("insforge_access_token");
        if (storedToken) {
          setAccessToken(storedToken);
        }
        setUser({ id: data.user.id, email: data.user.email });
      }
      setLoading(false);
    };

    bootstrap();
  }, [persistSession]);

  const signIn = useCallback(
    async (email: string, password: string) => {
      const { data, error } = await insforge.auth.signInWithPassword({ email, password });
      if (error) {
        const message = error.message ?? "Sign in failed";
        if (message.toLowerCase().includes("verify")) {
          setPendingVerificationEmail(email);
        }
        return message;
      }
      if (data?.accessToken && data.user) {
        clearPendingVerification();
        persistSession(data.accessToken, { id: data.user.id, email: data.user.email });
      }
      return null;
    },
    [clearPendingVerification, persistSession],
  );

  const signUp = useCallback(
    async (email: string, password: string, name?: string) => {
      const { data, error } = await insforge.auth.signUp({
        email,
        password,
        name,
        redirectTo: typeof window !== "undefined" ? `${window.location.origin}/verify-otp` : undefined,
      });
      if (error) {
        return error.message ?? "Sign up failed";
      }
      if (data?.requireEmailVerification) {
        setPendingVerificationEmail(email);
        return "verification_required";
      }
      if (data?.accessToken && data.user) {
        clearPendingVerification();
        persistSession(data.accessToken, { id: data.user.id, email: data.user.email });
      }
      return null;
    },
    [clearPendingVerification, persistSession],
  );

  const verifyEmail = useCallback(
    async (email: string, otp: string) => {
      const { data, error } = await insforge.auth.verifyEmail({ email, otp });
      if (error) {
        const message = error.message ?? "Verification failed";
        if (message.toLowerCase().includes("expired")) {
          return "Verification code expired. Request a new code and try again.";
        }
        if (message.toLowerCase().includes("invalid")) {
          return "Invalid verification code. Check the code and try again.";
        }
        return message;
      }
      if (data?.accessToken && data.user) {
        clearPendingVerification();
        persistSession(data.accessToken, { id: data.user.id, email: data.user.email });
        router.push("/");
        return null;
      }
      clearPendingVerification();
      return "Account verified. Sign in with your email and password.";
    },
    [clearPendingVerification, persistSession, router],
  );

  const resendVerificationEmail = useCallback(async (email: string) => {
    const { error } = await insforge.auth.resendVerificationEmail({
      email,
      redirectTo:
        typeof window !== "undefined" ? `${window.location.origin}/verify-otp` : undefined,
    });
    if (error) {
      return error.message ?? "Unable to resend verification code";
    }
    return null;
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      authEnabled,
      pendingVerificationEmail,
      signIn,
      signUp,
      verifyEmail,
      resendVerificationEmail,
      clearPendingVerification,
      signOut,
    }),
    [
      user,
      loading,
      pendingVerificationEmail,
      signIn,
      signUp,
      verifyEmail,
      resendVerificationEmail,
      clearPendingVerification,
      signOut,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
