"use client";

import { useState } from "react";

interface EvidenceCardProps {
  title: string;
  data: unknown;
  defaultOpen?: boolean;
}

export default function EvidenceCard({
  title,
  data,
  defaultOpen = false,
}: EvidenceCardProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const formattedJson = JSON.stringify(data, null, 2);

  return (
    <div className="overflow-hidden rounded-xl border border-white/[0.06] bg-white/[0.02] transition hover:border-white/10">
      <button
        type="button"
        onClick={() => setIsOpen((open) => !open)}
        className="flex w-full items-center justify-between px-5 py-4 text-left transition hover:bg-white/[0.02]"
      >
        <div className="flex items-center gap-3">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg border border-violet-500/20 bg-violet-500/10 text-[11px] font-bold uppercase text-violet-200">
            {title.slice(0, 2)}
          </span>
          <span className="text-sm font-medium text-white">{title}</span>
        </div>
        <span
          className={`rounded-md px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider ${
            isOpen
              ? "border border-violet-500/20 bg-violet-500/10 text-violet-200"
              : "border border-white/10 text-slate-500"
          }`}
        >
          {isOpen ? "Collapse" : "Expand"}
        </span>
      </button>

      {isOpen && (
        <div className="border-t border-white/[0.06] px-5 py-4">
          <pre className="max-h-96 overflow-auto rounded-xl border border-black/40 bg-[#030712] p-4 font-mono text-xs leading-relaxed text-slate-400">
            {formattedJson}
          </pre>
        </div>
      )}
    </div>
  );
}
