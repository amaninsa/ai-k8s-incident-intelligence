"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { useAuth } from "@/components/AuthProvider";

type AuthMode = "signin" | "signup" | "verify";

interface LoginFormProps {
  initialMode?: AuthMode;
  initialEmail?: string;
}

function OtpInput({
  value,
  onChange,
  disabled,
}: {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}) {
  const inputsRef = useRef<(HTMLInputElement | null)[]>([]);
  const digits = value.padEnd(6, " ").slice(0, 6).split("");

  const updateAtIndex = (index: number, digit: string) => {
    const next = value.split("");
    next[index] = digit;
    onChange(next.join("").replace(/\s/g, "").slice(0, 6));
  };

  const handleChange = (index: number, inputValue: string) => {
    const digit = inputValue.replace(/\D/g, "").slice(-1);
    updateAtIndex(index, digit);
    if (digit && index < 5) {
      inputsRef.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, key: string) => {
    if (key === "Backspace" && !digits[index]?.trim() && index > 0) {
      inputsRef.current[index - 1]?.focus();
    }
  };

  const handlePaste = (event: React.ClipboardEvent) => {
    event.preventDefault();
    const pasted = event.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    onChange(pasted);
    const focusIndex = Math.min(pasted.length, 5);
    inputsRef.current[focusIndex]?.focus();
  };

  return (
    <div className="flex justify-between gap-2 sm:gap-3" onPaste={handlePaste}>
      {digits.map((digit, index) => (
        <input
          key={index}
          ref={(el) => {
            inputsRef.current[index] = el;
          }}
          type="text"
          inputMode="numeric"
          maxLength={1}
          disabled={disabled}
          value={digit.trim()}
          onChange={(event) => handleChange(index, event.target.value)}
          onKeyDown={(event) => handleKeyDown(index, event.key)}
          className={`otp-box ${digit.trim() ? "otp-box-filled" : ""}`}
          aria-label={`Verification digit ${index + 1}`}
        />
      ))}
    </div>
  );
}

export default function LoginForm({
  initialMode = "signin",
  initialEmail = "",
}: LoginFormProps) {
  const router = useRouter();
  const {
    signIn,
    signUp,
    verifyEmail,
    resendVerificationEmail,
    pendingVerificationEmail,
    clearPendingVerification,
    user,
    authEnabled,
  } = useAuth();

  const [email, setEmail] = useState(initialEmail);
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [otp, setOtp] = useState("");
  const [mode, setMode] = useState<AuthMode>(initialMode);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (authEnabled && user) {
      router.replace("/");
    }
  }, [authEnabled, router, user]);

  useEffect(() => {
    if (pendingVerificationEmail) {
      setMode("verify");
      setEmail(pendingVerificationEmail);
    }
  }, [pendingVerificationEmail]);

  useEffect(() => {
    setMode(initialMode);
  }, [initialMode]);

  useEffect(() => {
    if (initialEmail) {
      setEmail(initialEmail);
    }
  }, [initialEmail]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    setSuccess(null);

    let result: string | null = null;
    if (mode === "signin") {
      result = await signIn(email, password);
      if (!result) {
        router.push("/");
      }
    } else if (mode === "signup") {
      const signupResult = await signUp(email, password, name);
      if (signupResult === "verification_required") {
        setMode("verify");
        setSuccess("Verification code sent. Check your email.");
      } else if (signupResult) {
        result = signupResult;
      } else {
        router.push("/");
      }
    } else {
      result = await verifyEmail(email, otp);
      if (!result) {
        setSuccess("Email verified. Redirecting to dashboard...");
      }
    }

    if (result) {
      setError(result);
    }
    setSubmitting(false);
  };

  const handleResend = async () => {
    setSubmitting(true);
    setError(null);
    setSuccess(null);
    const result = await resendVerificationEmail(email);
    if (result) {
      setError(result);
    } else {
      setSuccess("A new verification code was sent to your email.");
    }
    setSubmitting(false);
  };

  const title =
    mode === "verify"
      ? "Verify your email"
      : mode === "signin"
        ? "Welcome back"
        : "Create your account";

  const subtitle =
    mode === "verify"
      ? "Enter the 6-digit code we sent to your inbox."
      : mode === "signin"
        ? "Sign in to access your incident intelligence console."
        : "Start investigating clusters with AI-powered diagnostics.";

  return (
    <div className="glass-panel-strong p-8 sm:p-10">
      <div className="mb-8 text-center">
        <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl border border-violet-500/20 bg-gradient-to-br from-blue-600/20 to-violet-600/20 shadow-glow-sm">
          <span className="text-xl font-semibold text-violet-200">
            {mode === "verify" ? "✉" : mode === "signup" ? "+" : "→"}
          </span>
        </div>
        <h2 className="text-2xl font-semibold tracking-tight text-white">{title}</h2>
        <p className="mt-2 text-sm leading-relaxed text-slate-400">{subtitle}</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {mode === "signup" && (
          <div>
            <label htmlFor="name" className="auth-label">
              Full name
            </label>
            <input
              id="name"
              type="text"
              placeholder="Jane Doe"
              value={name}
              onChange={(event) => setName(event.target.value)}
              className="auth-input"
            />
          </div>
        )}

        {mode !== "verify" && (
          <>
            <div>
              <label htmlFor="email" className="auth-label">
                Email address
              </label>
              <input
                id="email"
                type="email"
                placeholder="you@company.com"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="auth-input"
              />
            </div>
            <div>
              <label htmlFor="password" className="auth-label">
                Password
              </label>
              <input
                id="password"
                type="password"
                placeholder="••••••••"
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="auth-input"
              />
            </div>
          </>
        )}

        {mode === "verify" && (
          <>
            <div>
              <label htmlFor="verify-email" className="auth-label">
                Email
              </label>
              <input
                id="verify-email"
                type="email"
                required
                readOnly
                value={email}
                className="auth-input cursor-not-allowed opacity-70"
              />
            </div>
            <div>
              <label className="auth-label">Verification code</label>
              <OtpInput value={otp} onChange={setOtp} disabled={submitting} />
              <input type="hidden" value={otp} required minLength={6} maxLength={6} readOnly />
            </div>
          </>
        )}

        {error && (
          <p className="rounded-xl border border-red-500/25 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {error}
          </p>
        )}

        {success && (
          <p className="rounded-xl border border-emerald-500/25 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200">
            {success}
          </p>
        )}

        <button type="submit" disabled={submitting} className="btn-premium">
          {submitting
            ? "Please wait..."
            : mode === "verify"
              ? "Verify email"
              : mode === "signin"
                ? "Sign in"
                : "Create account"}
        </button>
      </form>

      {mode === "verify" && (
        <div className="mt-6 flex flex-col gap-2 border-t border-white/[0.06] pt-6 text-sm">
          <button
            type="button"
            onClick={handleResend}
            disabled={submitting}
            className="text-left text-violet-300 transition hover:text-violet-200 disabled:opacity-60"
          >
            Resend verification code
          </button>
          <button
            type="button"
            onClick={() => {
              clearPendingVerification();
              setMode("signin");
              setOtp("");
              setError(null);
              setSuccess(null);
            }}
            className="text-left text-slate-400 transition hover:text-slate-200"
          >
            Back to sign in
          </button>
        </div>
      )}

      {mode === "signin" && (
        <div className="mt-6 flex flex-col gap-2 border-t border-white/[0.06] pt-6 text-sm">
          <Link href="/signup" className="text-violet-300 transition hover:text-violet-200">
            Need an account? Sign up
          </Link>
          <Link href="/verify-otp" className="text-slate-400 transition hover:text-slate-200">
            Already have a verification code?
          </Link>
        </div>
      )}

      {mode === "signup" && (
        <Link
          href="/login"
          className="mt-6 inline-block border-t border-white/[0.06] pt-6 text-sm text-violet-300 transition hover:text-violet-200"
        >
          Already have an account? Sign in
        </Link>
      )}

      <p className="mt-8 flex items-center justify-center gap-2 text-center text-xs text-slate-500">
        <span className="text-slate-600">🔒</span>
        Your data is encrypted and secure
      </p>
    </div>
  );
}
