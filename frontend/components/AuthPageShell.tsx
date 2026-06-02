"use client";

const FEATURES = [
  "AI Incident Investigation",
  "Root Cause Detection",
  "Kubernetes Cluster Analysis",
  "Historical Investigations",
  "Realtime Diagnostic Pipeline",
];

interface AuthPageShellProps {
  children: React.ReactNode;
}

export default function AuthPageShell({ children }: AuthPageShellProps) {
  return (
    <div className="relative min-h-screen bg-[#06080f] lg:grid lg:grid-cols-2">
      {/* Left branding panel */}
      <div className="relative hidden overflow-hidden border-r border-white/[0.06] lg:flex lg:flex-col lg:justify-between">
        <div className="absolute inset-0 mesh-bg opacity-60" />
        <div className="absolute inset-0 bg-auth-mesh" />
        <div className="pointer-events-none absolute -left-20 top-20 h-72 w-72 rounded-full bg-blue-500/20 blur-[100px]" />
        <div className="pointer-events-none absolute bottom-20 right-0 h-80 w-80 rounded-full bg-violet-600/15 blur-[120px]" />

        <div className="relative flex flex-1 flex-col justify-center px-12 xl:px-16">
          <div className="mb-8 inline-flex w-fit items-center gap-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-3 py-1">
            <span className="h-1.5 w-1.5 animate-pulse-soft rounded-full bg-cyan-400" />
            <span className="text-[11px] font-semibold uppercase tracking-[0.22em] text-blue-200/90">
              AI Kubernetes Agent
            </span>
          </div>

          <h1 className="max-w-lg text-4xl font-bold leading-[1.1] tracking-tight text-white xl:text-5xl">
            Diagnose Kubernetes failures{" "}
            <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-violet-300 bg-clip-text text-transparent">
              in seconds
            </span>
          </h1>

          <p className="mt-5 max-w-md text-base leading-relaxed text-slate-400">
            AI-powered root cause analysis for production Kubernetes environments.
          </p>

          <ul className="mt-10 space-y-3">
            {FEATURES.map((feature) => (
              <li key={feature} className="flex items-center gap-3 text-sm text-slate-300">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-500/15 text-[10px] text-emerald-400">
                  ✓
                </span>
                {feature}
              </li>
            ))}
          </ul>

          {/* Decorative intelligence nodes */}
          <div className="relative mt-16 h-48">
            <div className="animate-float absolute left-8 top-4 glass-panel px-4 py-3">
              <p className="text-[10px] uppercase tracking-wider text-slate-500">Cluster Health</p>
              <p className="mt-1 text-sm font-semibold text-emerald-300">Healthy · 98%</p>
            </div>
            <div className="animate-float-delayed absolute right-12 top-0 glass-panel px-4 py-3">
              <p className="text-[10px] uppercase tracking-wider text-slate-500">AI Confidence</p>
              <p className="mt-1 text-sm font-semibold text-cyan-300">92%</p>
            </div>
            <div className="absolute bottom-0 left-1/2 h-24 w-24 -translate-x-1/2 rounded-2xl border border-blue-500/20 bg-gradient-to-br from-blue-600/20 to-violet-600/20 shadow-glow-sm backdrop-blur-xl">
              <div className="flex h-full items-center justify-center text-3xl opacity-90">☸</div>
            </div>
          </div>
        </div>

        <div className="relative border-t border-white/[0.06] px-12 py-6 xl:px-16">
          <p className="text-xs text-slate-500">
            Enterprise-grade incident intelligence · Encrypted sessions · InsForge auth
          </p>
        </div>
      </div>

      {/* Right form panel */}
      <div className="relative flex min-h-screen items-center justify-center px-6 py-10 sm:px-10">
        <div className="pointer-events-none absolute inset-0 mesh-bg opacity-30 lg:hidden" />
        <div className="pointer-events-none absolute right-0 top-0 h-64 w-64 rounded-full bg-violet-600/10 blur-[100px]" />

        <div className="relative w-full max-w-[440px] animate-fade-up">
          {/* Mobile branding compact */}
          <div className="mb-8 text-center lg:hidden">
            <p className="section-kicker">AI Kubernetes Agent</p>
            <h2 className="mt-2 text-2xl font-bold tracking-tight text-white">
              Incident intelligence platform
            </h2>
          </div>

          {children}
        </div>
      </div>
    </div>
  );
}
