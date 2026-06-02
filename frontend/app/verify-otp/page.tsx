"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";

import LoginForm from "@/components/LoginForm";
import AuthPageShell from "@/components/AuthPageShell";

function VerifyOtpContent() {
  const searchParams = useSearchParams();
  const email = searchParams.get("email") ?? "";

  return <LoginForm initialMode="verify" initialEmail={email} />;
}

export default function VerifyOtpPage() {
  return (
    <AuthPageShell>
      <Suspense
        fallback={
          <div className="glass-card p-8 text-center text-sm text-slate-400">
            Loading verification form...
          </div>
        }
      >
        <VerifyOtpContent />
      </Suspense>
    </AuthPageShell>
  );
}
