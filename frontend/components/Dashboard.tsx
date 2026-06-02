"use client";

import { useEffect, useState } from "react";

import { useAuth } from "@/components/AuthProvider";
import AuthGate from "@/components/AuthGate";
import ClusterSelector from "@/components/ClusterSelector";
import DiagnosisCard from "@/components/DiagnosisCard";
import EvidenceCard from "@/components/EvidenceCard";
import ExportMenu from "@/components/ExportMenu";
import InvestigationHistory from "@/components/InvestigationHistory";
import InvestigationProgress from "@/components/InvestigationProgress";
import { useInvestigation } from "@/hooks/useInvestigation";
import { getAccessToken, setAccessToken } from "@/services/api";
import {
  downloadBlob,
  exportInvestigation,
  listClusters,
  listHistory,
} from "@/services/investigationService";
import type { InvestigationHistoryItem } from "@/types/investigation";

function ErrorBanner({
  title,
  message,
  hints,
}: {
  title: string;
  message: string;
  hints?: string[];
}) {
  return (
    <div className="glass-panel border-red-500/20 bg-red-500/[0.06] p-6">
      <div className="mb-3 flex items-center gap-3">
        <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-red-500/15 text-sm text-red-300">
          !
        </span>
        <h3 className="text-sm font-semibold text-red-100">{title}</h3>
      </div>
      <p className="mb-4 text-sm leading-relaxed text-red-100/90">{message}</p>
      {hints && hints.length > 0 && (
        <div className="rounded-xl border border-red-500/15 bg-red-950/20 p-4">
          <p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-red-200/70">
            Please verify
          </p>
          <ul className="space-y-1.5 text-sm text-red-100/85">
            {hints.map((hint) => (
              <li key={hint} className="flex gap-2">
                <span className="text-red-400/80">•</span>
                <span>{hint}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function WarningBanner({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-3 rounded-2xl border border-amber-500/20 bg-amber-500/[0.06] px-5 py-4">
      <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-amber-500/15 text-sm text-amber-300">
        ⚠
      </span>
      <p className="text-sm leading-relaxed text-amber-100/90">{message}</p>
    </div>
  );
}

function DashboardContent() {
  const { signOut, authEnabled, user } = useAuth();
  const {
    loading,
    error,
    result,
    completedSteps,
    activeStep,
    openRouterWarning,
    investigate,
  } = useInvestigation();

  const [clusters, setClusters] = useState<string[]>([]);
  const [clustersLoading, setClustersLoading] = useState(true);
  const [selectedCluster, setSelectedCluster] = useState("");
  const [history, setHistory] = useState<InvestigationHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  useEffect(() => {
    if (authEnabled && !user) {
      console.log("[Dashboard] loadClusters skipped: waiting for authenticated user");
      return;
    }

    let cancelled = false;

    const loadClusters = async () => {
      setClustersLoading(true);

      const storedToken = localStorage.getItem("insforge_access_token");
      if (storedToken && !getAccessToken()) {
        console.log("[Dashboard] syncing access token from localStorage before /clusters");
        setAccessToken(storedToken);
      }

      console.log("[Dashboard] loadClusters start", {
        authEnabled,
        hasUser: Boolean(user),
        hasApiToken: Boolean(getAccessToken()),
      });

      try {
        const contexts = await listClusters();
        if (cancelled) {
          return;
        }

        console.log("[Dashboard] loadClusters success", {
          count: contexts.length,
          contexts,
        });

        setClusters(contexts);
        if (contexts.length > 0) {
          setSelectedCluster((current) => current || contexts[0]);
          console.log("[Dashboard] selectedCluster set to", contexts[0]);
        } else {
          setSelectedCluster("");
          console.warn("[Dashboard] loadClusters returned no contexts");
        }
      } catch (error) {
        console.error("[Dashboard] loadClusters failed", error);
        if (!cancelled) {
          setClusters([]);
          setSelectedCluster("");
        }
      } finally {
        if (!cancelled) {
          setClustersLoading(false);
        }
      }
    };

    loadClusters();

    return () => {
      cancelled = true;
    };
  }, [authEnabled, user]);

  useEffect(() => {
    console.log("[Dashboard] cluster state", {
      clusters,
      selectedCluster,
      clustersLoading,
    });
  }, [clusters, selectedCluster, clustersLoading]);

  useEffect(() => {
    const loadHistory = async () => {
      if (authEnabled && !user) {
        return;
      }

      setHistoryLoading(true);
      try {
        const items = await listHistory();
        setHistory(items);
      } catch {
        setHistory([]);
      } finally {
        setHistoryLoading(false);
      }
    };

    loadHistory();
  }, [authEnabled, result, user]);

  return (
    <div className="min-h-screen bg-[#06080f]">
      {/* Top navigation */}
      <header className="nav-bar">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:px-6 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-violet-500/20 bg-gradient-to-br from-blue-600/30 to-violet-600/20 text-sm shadow-glow-sm">
              ☸
            </div>
            <div>
              <p className="text-sm font-semibold text-white">AI Kubernetes Agent</p>
              <p className="text-[11px] text-slate-500">Incident Intelligence Console</p>
            </div>
          </div>

          <div className="flex flex-1 flex-wrap items-center gap-3 lg:justify-end">
            {authEnabled && user && (
              <>
                <div className="hidden h-8 w-px bg-white/10 sm:block" />
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-violet-600 text-xs font-bold text-white">
                    {(user.email ?? "U").slice(0, 1).toUpperCase()}
                  </div>
                  <div className="hidden min-w-0 sm:block">
                    <p className="truncate text-sm font-medium text-white">{user.email}</p>
                    <p className="text-[11px] text-slate-500">Authenticated</p>
                  </div>
                  <button type="button" onClick={signOut} className="btn-secondary">
                    Logout
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </header>

      <main className="relative mx-auto max-w-7xl px-4 py-8 sm:px-6 sm:py-10">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-64 bg-gradient-to-b from-blue-600/5 to-transparent" />

        {/* Hero */}
        <section className="relative mb-10">
          <p className="section-kicker">Operations Console</p>
          <h1 className="mt-3 max-w-3xl text-4xl font-bold tracking-tight sm:text-5xl">
            <span className="hero-gradient-text">Kubernetes Incident Intelligence</span>
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-slate-400">
            AI-powered investigation and root cause analysis for production clusters.
          </p>

          <div className="mt-8">
            <ClusterSelector
              clusters={clusters}
              selectedCluster={selectedCluster}
              loading={clustersLoading}
              onChange={setSelectedCluster}
            />
          </div>

          <div className="mt-8 flex flex-wrap items-center gap-4">
            <button
              type="button"
              onClick={() => investigate(selectedCluster)}
              disabled={loading || !selectedCluster}
              className="btn-premium w-auto min-w-[220px] px-8"
            >
              {loading ? "Investigating..." : "Investigate Cluster"}
            </button>

            {!loading && !result && !error && selectedCluster && (
              <span className="inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-300">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
                Ready · {selectedCluster}
              </span>
            )}
          </div>
        </section>

        {/* Alerts */}
        <div className="relative mb-8 space-y-4">
          {error && (
            <ErrorBanner title={error.title} message={error.message} hints={error.hints} />
          )}
          {openRouterWarning && <WarningBanner message={openRouterWarning} />}
        </div>

        {/* Progress */}
        {loading && (
          <div className="relative mb-8">
            <InvestigationProgress completedSteps={completedSteps} activeStep={activeStep} />
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="relative mb-10 space-y-8">
            {result.status === "warning" && (
              <WarningBanner message="Critical Kubernetes events were detected during investigation." />
            )}

            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="section-kicker">Latest Analysis</p>
                <h2 className="section-title">AI Diagnosis Report</h2>
              </div>
              <ExportMenu result={result} />
            </div>

            <DiagnosisCard diagnosis={result.diagnosis} />

            <section>
              <div className="mb-4">
                <p className="section-kicker">Raw Evidence</p>
                <h2 className="section-title">Investigation Payload</h2>
              </div>
              <div className="space-y-3">
                <EvidenceCard title="Pods" data={result.investigation.pods} defaultOpen />
                <EvidenceCard title="Events" data={result.investigation.events} />
                <EvidenceCard title="Deployments" data={result.investigation.deployments} />
                <EvidenceCard title="Networking" data={result.investigation.network} />
              </div>
            </section>
          </div>
        )}

        {!result && !loading && (
          <div className="glass-panel relative mb-10 flex min-h-[280px] flex-col items-center justify-center px-6 py-14 text-center">
            <div className="mb-4 h-px w-32 bg-gradient-to-r from-transparent via-violet-500/50 to-transparent" />
            <p className="text-sm font-medium text-slate-300">Awaiting investigation</p>
            <p className="mt-2 max-w-md text-sm text-slate-500">
              Select a cluster and run diagnostics to generate AI root cause analysis.
            </p>
          </div>
        )}

        {/* History table */}
        <InvestigationHistory
          items={history}
          loading={historyLoading}
          onSelect={async (item) => {
            if (!item.id) {
              return;
            }
            try {
              const blob = await exportInvestigation(item.id, "json");
              downloadBlob(blob, `rca-${item.id}.json`);
            } catch {
              window.alert("Unable to export this investigation. Sign in and try again.");
            }
          }}
        />
      </main>
    </div>
  );
}

export default function Dashboard() {
  return (
    <AuthGate>
      <DashboardContent />
    </AuthGate>
  );
}
