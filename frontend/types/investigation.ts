export interface HealthResponse {
  status: string;
  service: string;
}

export interface Diagnosis {
  root_cause: string;
  explanation: string;
  fix: string;
  kubectl_command: string;
  prevention_recommendation: string;
  confidence: number;
  affected_resources: string[];
  evidence_count: number;
}

export interface InvestigationEvidence {
  cluster: Record<string, unknown>;
  pods: Record<string, unknown>;
  logs: Record<string, unknown>;
  events: Record<string, unknown>;
  deployments: Record<string, unknown>;
  network: Record<string, unknown>;
}

export interface InvestigationResponse {
  status: "success" | "warning";
  investigation: InvestigationEvidence;
  diagnosis: Diagnosis;
  history_id?: string;
}

export interface InvestigationHistoryItem {
  id: string;
  timestamp: string;
  cluster: string;
  namespace?: string | null;
  root_cause: string;
  confidence: number;
  status: string;
}

export interface ProgressEvent {
  type: "progress" | "complete" | "error";
  step?: string;
  status?: "active" | "complete";
  data?: InvestigationResponse;
  detail?: string;
}

export type InvestigationErrorType =
  | "backend_unavailable"
  | "timeout"
  | "cluster_access"
  | "kubectl_not_found"
  | "kubeconfig_not_found"
  | "invalid_context"
  | "unauthorized"
  | "unknown";

export interface InvestigationError {
  type: InvestigationErrorType;
  title: string;
  message: string;
  hints?: string[];
}

export const INVESTIGATION_PROGRESS_STEPS = [
  "Checking Pods",
  "Collecting Logs",
  "Reading Events",
  "Inspecting Deployments",
  "Checking Networking",
  "AI Reasoning",
  "Root Cause Found",
] as const;

export type ExportFormat = "json" | "markdown" | "pdf";
