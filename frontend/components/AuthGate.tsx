"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/components/AuthProvider";

function LoadingScreen({ message }: { message: string }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#06080f]">
      <div className="glass-panel-strong flex items-center gap-4 px-8 py-6">
        <span className="relative flex h-5 w-5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-violet-400 opacity-30" />
          <span className="relative inline-flex h-5 w-5 animate-spin rounded-full border-2 border-violet-400 border-t-transparent" />
        </span>
        <p className="text-sm font-medium text-slate-300">{message}</p>
      </div>
    </div>
  );
}

export default function AuthGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, loading, authEnabled, pendingVerificationEmail } = useAuth();

  useEffect(() => {
    if (!authEnabled || loading || user) {
      return;
    }

    if (pendingVerificationEmail) {
      router.replace("/verify-otp");
      return;
    }

    router.replace("/login");
  }, [authEnabled, loading, pendingVerificationEmail, router, user]);

  if (!authEnabled) {
    return <>{children}</>;
  }

  if (loading) {
    return <LoadingScreen message="Checking session..." />;
  }

  if (!user) {
    return <LoadingScreen message="Redirecting..." />;
  }

  return <>{children}</>;
}
