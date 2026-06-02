"use client";

import type { InvestigationHistoryItem } from "@/types/investigation";

interface InvestigationHistoryProps {
  items: InvestigationHistoryItem[];
  loading: boolean;
  onSelect: (item: InvestigationHistoryItem) => void;
}

function formatTimestamp(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function InvestigationHistory({
  items,
  loading,
  onSelect,
}: InvestigationHistoryProps) {
  return (
    <section className="glass-panel overflow-hidden">
      <div className="flex items-center justify-between border-b border-white/[0.06] px-6 py-5">
        <div>
          <p className="section-kicker">Audit Trail</p>
          <h2 className="section-title">Investigation History</h2>
        </div>
        {!loading && items.length > 0 && (
          <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs text-slate-400">
            {items.length} records
          </span>
        )}
      </div>

      {loading && (
        <div className="flex items-center gap-3 px-6 py-12 text-sm text-slate-400">
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-600 border-t-violet-400" />
          Loading investigation history...
        </div>
      )}

      {!loading && items.length === 0 && (
        <div className="px-6 py-16 text-center">
          <p className="text-sm font-medium text-slate-300">No investigations recorded</p>
          <p className="mt-1 text-xs text-slate-500">
            Completed investigations will appear here with cluster, status, and confidence.
          </p>
        </div>
      )}

      {!loading && items.length > 0 && (
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Cluster</th>
                <th>Root Cause</th>
                <th>Confidence</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr
                  key={item.id}
                  className="cursor-pointer"
                  onClick={() => onSelect(item)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      onSelect(item);
                    }
                  }}
                  tabIndex={0}
                  role="button"
                >
                  <td className="whitespace-nowrap text-slate-400">
                    {formatTimestamp(item.timestamp)}
                  </td>
                  <td>
                    <span className="badge-cluster">{item.cluster}</span>
                  </td>
                  <td className="max-w-xs">
                    <p className="line-clamp-2 font-medium text-white">{item.root_cause}</p>
                    {item.namespace && (
                      <p className="mt-0.5 text-xs text-slate-500">ns/{item.namespace}</p>
                    )}
                  </td>
                  <td>
                    <span className="badge-confidence">{item.confidence}%</span>
                  </td>
                  <td>
                    <span
                      className={
                        item.status === "warning" ? "badge-warning" : "badge-success"
                      }
                    >
                      {item.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && items.length > 0 && (
        <p className="border-t border-white/[0.04] px-6 py-3 text-xs text-slate-600">
          Click a row to export investigation JSON
        </p>
      )}
    </section>
  );
}
