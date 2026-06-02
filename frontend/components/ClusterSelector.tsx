"use client";

type EnvironmentBadge = "Production" | "Local";

interface ClusterSelectorProps {
  clusters: string[];
  selectedCluster: string;
  loading: boolean;
  onChange: (cluster: string) => void;
  compact?: boolean;
}

function getFriendlyClusterName(context: string): string {
  const trimmed = context.trim();
  if (!trimmed) {
    return "Unknown cluster";
  }

  const slashParts = trimmed.split("/");
  if (slashParts.length > 1) {
    const last = slashParts[slashParts.length - 1];
    if (last) {
      return last;
    }
  }

  if (/^kind-/i.test(trimmed)) {
    const name = trimmed.replace(/^kind-/i, "");
    return name || trimmed;
  }

  return trimmed;
}

function getEnvironmentBadge(context: string): EnvironmentBadge | null {
  const lower = context.toLowerCase();
  if (lower.includes("eks") || lower.includes("arn:aws:eks")) {
    return "Production";
  }
  if (lower.includes("kind") || /^kind-/i.test(context)) {
    return "Local";
  }
  return null;
}

function EnvironmentBadgePill({ badge }: { badge: EnvironmentBadge }) {
  if (badge === "Production") {
    return (
      <span className="inline-flex items-center rounded-md border border-amber-500/25 bg-amber-500/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-amber-300">
        Production
      </span>
    );
  }

  return (
    <span className="inline-flex items-center rounded-md border border-emerald-500/25 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-emerald-300">
      Local
    </span>
  );
}

function CheckIcon() {
  return (
    <svg
      className="h-4 w-4 text-violet-300"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2.5}
      aria-hidden="true"
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  );
}

function ClusterCardSkeleton() {
  return (
    <div className="animate-pulse rounded-2xl border border-white/[0.06] bg-white/[0.03] p-5">
      <div className="mb-3 h-4 w-24 rounded-md bg-white/10" />
      <div className="mb-2 h-3 w-full rounded-md bg-white/[0.06]" />
      <div className="h-5 w-16 rounded-md bg-white/[0.06]" />
    </div>
  );
}

export default function ClusterSelector({
  clusters,
  selectedCluster,
  loading,
  onChange,
}: ClusterSelectorProps) {
  return (
    <div className="w-full">
      <div className="mb-4">
        <p className="section-kicker">Target Cluster</p>
        <h2 className="section-title">Select a cluster context</h2>
        <p className="mt-1 text-sm text-slate-500">
          Loaded from kubeconfig on the backend host. The full context name is sent to investigations.
        </p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <ClusterCardSkeleton />
          <ClusterCardSkeleton />
          <ClusterCardSkeleton />
        </div>
      ) : clusters.length === 0 ? (
        <div className="glass-panel flex min-h-[140px] flex-col items-center justify-center px-6 py-10 text-center">
          <p className="text-sm font-medium text-slate-300">No clusters available</p>
          <p className="mt-2 max-w-md text-sm text-slate-500">
            Verify kubeconfig on the backend host and ensure kubectl contexts are configured.
          </p>
        </div>
      ) : (
        <div
          role="radiogroup"
          aria-label="Select cluster context"
          className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
        >
          {clusters.map((context) => {
            const isSelected = selectedCluster === context;
            const friendlyName = getFriendlyClusterName(context);
            const badge = getEnvironmentBadge(context);

            return (
              <button
                key={context}
                type="button"
                role="radio"
                aria-checked={isSelected}
                onClick={() => onChange(context)}
                className={[
                  "group relative w-full rounded-2xl border p-5 text-left transition duration-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-400/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#06080f]",
                  isSelected
                    ? "border-violet-400/60 bg-gradient-to-br from-blue-600/15 via-violet-600/10 to-indigo-600/10 shadow-glow ring-1 ring-violet-400/40"
                    : "border-white/[0.08] bg-white/[0.03] hover:border-white/20 hover:bg-white/[0.05] hover:shadow-glow-sm",
                ].join(" ")}
              >
                {isSelected && (
                  <span className="absolute inset-0 rounded-2xl bg-gradient-to-br from-blue-500/10 via-violet-500/10 to-transparent opacity-80" />
                )}

                <div className="relative flex items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="truncate text-base font-semibold text-white">{friendlyName}</h3>
                      {badge && <EnvironmentBadgePill badge={badge} />}
                    </div>
                    <p className="mt-2 break-all font-mono text-[11px] leading-relaxed text-slate-500">
                      {context}
                    </p>
                  </div>

                  {isSelected && (
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-violet-400/40 bg-violet-500/20 shadow-glow-sm">
                      <CheckIcon />
                    </span>
                  )}
                </div>

                {isSelected && (
                  <div className="relative mt-4 flex items-center gap-2 border-t border-violet-400/20 pt-3">
                    <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-violet-300">
                      <CheckIcon />
                      Selected
                    </span>
                  </div>
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
