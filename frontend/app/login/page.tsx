"use client";

import LoginForm from "@/components/LoginForm";
import AuthPageShell from "@/components/AuthPageShell";

export default function LoginPage() {
  return (
    <AuthPageShell>
      <LoginForm initialMode="signin" />
    </AuthPageShell>
  );
}
