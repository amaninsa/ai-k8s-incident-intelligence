"use client";

import { INVESTIGATION_PROGRESS_STEPS } from "@/types/investigation";

interface InvestigationProgressProps {
  completedSteps: string[];
  activeStep: string | null;
}

export default function InvestigationProgress({
  completedSteps,
  activeStep,
}: InvestigationProgressProps) {
  const totalSteps = INVESTIGATION_PROGRESS_STEPS.length;
  const progressPercent = Math.round((completedSteps.length / totalSteps) * 100);

  return (
    <div className="glass-panel overflow-hidden">
      <div className="border-b border-white/[0.06] px-6 py-5">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="relative flex h-3 w-3">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-violet-400 opacity-40" />
              <span className="relative inline-flex h-3 w-3 rounded-full bg-violet-500" />
            </span>
            <div>
              <p className="text-sm font-semibold text-white">Diagnostic pipeline running</p>
              <p className="text-xs text-slate-500">Realtime evidence collection & AI reasoning</p>
            </div>
          </div>
          <span className="rounded-lg border border-violet-500/20 bg-violet-500/10 px-3 py-1.5 text-xs font-semibold tabular-nums text-violet-200">
            {progressPercent}%
          </span>
        </div>

        <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-white/[0.06]">
          <div
            className="h-full rounded-full bg-gradient-to-r from-blue-600 via-indigo-500 to-violet-500 transition-all duration-700 ease-out"
            style={{ width: `${Math.max(progressPercent, 4)}%` }}
          />
        </div>
      </div>

      <div className="px-6 py-5">
        <ol className="relative space-y-0">
          {INVESTIGATION_PROGRESS_STEPS.map((step, index) => {
            const isComplete = completedSteps.includes(step);
            const isActive = activeStep === step && !isComplete;
            const isLast = index === INVESTIGATION_PROGRESS_STEPS.length - 1;

            return (
              <li key={step} className="relative flex gap-4 pb-6 last:pb-0">
                {!isLast && (
                  <span
                    className={`absolute left-[15px] top-8 h-[calc(100%-12px)] w-px ${
                      isComplete ? "bg-emerald-500/40" : "bg-white/10"
                    }`}
                  />
                )}

                <span
                  className={`relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border text-xs font-semibold transition duration-300 ${
                    isComplete
                      ? "border-emerald-500/30 bg-emerald-500/15 text-emerald-300"
                      : isActive
                        ? "border-violet-500/40 bg-violet-500/15 text-violet-200 shadow-glow-sm"
                        : "border-white/10 bg-white/[0.03] text-slate-500"
                  }`}
                >
                  {isComplete ? "✓" : isActive ? "●" : index + 1}
                </span>

                <div className="min-w-0 pt-1">
                  <p
                    className={`text-sm font-medium ${
                      isComplete
                        ? "text-emerald-200"
                        : isActive
                          ? "text-white"
                          : "text-slate-500"
                    }`}
                  >
                    {step}
                  </p>
                  {isActive && (
                    <p className="mt-0.5 text-xs text-slate-500 animate-pulse-soft">
                      Processing...
                    </p>
                  )}
                </div>
              </li>
            );
          })}
        </ol>
      </div>
    </div>
  );
}
