"use client";

import type { Diagnosis } from "@/types/investigation";

interface DiagnosisCardProps {
  diagnosis: Diagnosis;
}

function DiagnosisField({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-5 transition hover:border-white/10">
      <h3 className="mb-2.5 text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-500">
        {label}
      </h3>
      <p
        className={`leading-relaxed text-slate-100 ${
          mono
            ? "overflow-x-auto rounded-lg bg-black/30 p-3 font-mono text-xs text-cyan-200"
            : "text-sm"
        }`}
      >
        {value || "Not available"}
      </p>
    </div>
  );
}

export default function DiagnosisCard({ diagnosis }: DiagnosisCardProps) {
  const confidenceColor =
    diagnosis.confidence >= 90
      ? "from-emerald-500 to-green-400"
      : diagnosis.confidence >= 75
        ? "from-blue-500 to-indigo-400"
        : diagnosis.confidence >= 50
          ? "from-amber-500 to-orange-400"
          : "from-red-500 to-rose-400";

  const confidenceText =
    diagnosis.confidence >= 90
      ? "text-emerald-300"
      : diagnosis.confidence >= 75
        ? "text-blue-300"
        : diagnosis.confidence >= 50
          ? "text-amber-300"
          : "text-red-300";

  const ringColor =
    diagnosis.confidence >= 90
      ? "stroke-emerald-400"
      : diagnosis.confidence >= 75
        ? "stroke-blue-400"
        : diagnosis.confidence >= 50
          ? "stroke-amber-400"
          : "stroke-red-400";

  const circumference = 2 * Math.PI * 42;
  const strokeDashoffset = circumference - (diagnosis.confidence / 100) * circumference;

  return (
    <section className="glass-panel overflow-hidden">
      <div className="border-b border-white/[0.06] bg-gradient-to-r from-violet-600/[0.08] to-transparent px-6 py-6">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="section-kicker">AI Analysis</p>
            <h2 className="section-title">Root Cause Diagnosis</h2>
          </div>

          <div className="flex items-center gap-4">
            <div className="relative h-24 w-24 shrink-0">
              <svg className="h-24 w-24 -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="42"
                  fill="none"
                  stroke="rgba(255,255,255,0.06)"
                  strokeWidth="8"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="42"
                  fill="none"
                  className={ringColor}
                  strokeWidth="8"
                  strokeLinecap="round"
                  strokeDasharray={circumference}
                  strokeDashoffset={strokeDashoffset}
                  style={{ transition: "stroke-dashoffset 1s ease-out" }}
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`text-2xl font-bold tabular-nums ${confidenceText}`}>
                  {diagnosis.confidence}
                </span>
                <span className="text-[10px] uppercase tracking-wider text-slate-500">%</span>
              </div>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wider text-slate-500">Confidence</p>
              <p className={`text-lg font-semibold ${confidenceText}`}>
                {diagnosis.confidence >= 75 ? "High" : diagnosis.confidence >= 50 ? "Medium" : "Low"}
              </p>
            </div>
          </div>
        </div>

        <div className="mt-5 h-1 overflow-hidden rounded-full bg-white/[0.06]">
          <div
            className={`h-full rounded-full bg-gradient-to-r ${confidenceColor} transition-all duration-700`}
            style={{ width: `${diagnosis.confidence}%` }}
          />
        </div>
      </div>

      <div className="grid gap-4 p-6 md:grid-cols-2">
        <div className="md:col-span-2">
          <DiagnosisField label="Root Cause" value={diagnosis.root_cause} />
        </div>
        <DiagnosisField label="Explanation" value={diagnosis.explanation} />
        <DiagnosisField label="Suggested Fix" value={diagnosis.fix} />
        <DiagnosisField label="Kubectl Command" value={diagnosis.kubectl_command} mono />
        <DiagnosisField label="Prevention" value={diagnosis.prevention_recommendation} />
      </div>

      {diagnosis.affected_resources.length > 0 && (
        <div className="border-t border-white/[0.06] px-6 py-5">
          <p className="mb-3 text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-500">
            Affected Resources
          </p>
          <div className="flex flex-wrap gap-2">
            {diagnosis.affected_resources.map((resource) => (
              <span
                key={resource}
                className="rounded-lg border border-white/10 bg-white/[0.03] px-3 py-1.5 font-mono text-xs text-slate-300"
              >
                {resource}
              </span>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
