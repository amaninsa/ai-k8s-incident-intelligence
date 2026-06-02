"use client";

import LoginForm from "@/components/LoginForm";
import AuthPageShell from "@/components/AuthPageShell";

export default function SignupPage() {
  return (
    <AuthPageShell>
      <LoginForm initialMode="signup" />
    </AuthPageShell>
  );
}
