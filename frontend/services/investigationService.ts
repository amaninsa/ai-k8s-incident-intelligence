import { isAxiosError } from "axios";

import { apiClient, getAccessToken, getApiBaseUrl } from "@/services/api";
import type {
  ExportFormat,
  InvestigationError,
  InvestigationHistoryItem,
  InvestigationResponse,
  ProgressEvent,
} from "@/types/investigation";

const INVESTIGATION_TIMEOUT_MS = 180_000;

function normalizeClusterList(data: unknown): string[] {
  if (Array.isArray(data)) {
    return data.filter((item): item is string => typeof item === "string" && item.length > 0);
  }

  if (data && typeof data === "object" && "contexts" in data) {
    const contexts = (data as { contexts?: unknown }).contexts;
    if (Array.isArray(contexts)) {
      return contexts.filter((item): item is string => typeof item === "string" && item.length > 0);
    }
  }

  console.warn("[listClusters] unexpected response shape:", data);
  return [];
}

export async function listClusters(): Promise<string[]> {
  console.log("[listClusters] GET /clusters");
  const response = await apiClient.get<unknown>("/clusters");
  const clusters = normalizeClusterList(response.data);
  console.log("[listClusters] parsed clusters:", clusters);
  return clusters;
}

export async function listHistory(): Promise<InvestigationHistoryItem[]> {
  const response = await apiClient.get<{ history: InvestigationHistoryItem[] }>("/history");
  return response.data.history ?? [];
}

export async function runInvestigation(context: string): Promise<InvestigationResponse> {
  const response = await apiClient.post<InvestigationResponse>(
    "/investigate",
    { context },
    { timeout: INVESTIGATION_TIMEOUT_MS },
  );
  return response.data;
}

export function streamInvestigation(
  context: string,
  onEvent: (event: ProgressEvent) => void,
): { close: () => void; finished: Promise<InvestigationResponse> } {
  const token = getAccessToken();
  const url = new URL("/investigate/stream", getApiBaseUrl());
  url.searchParams.set("context", context);
  if (token) {
    url.searchParams.set("access_token", token);
  }

  const eventSource = new EventSource(url.toString());
  let resolveFinish!: (value: InvestigationResponse) => void;
  let rejectFinish!: (reason?: unknown) => void;

  const finished = new Promise<InvestigationResponse>((resolve, reject) => {
    resolveFinish = resolve;
    rejectFinish = reject;
  });

  eventSource.onmessage = (message) => {
    const event = JSON.parse(message.data) as ProgressEvent;
    onEvent(event);

    if (event.type === "complete" && event.data) {
      resolveFinish(event.data);
      eventSource.close();
    }

    if (event.type === "error") {
      rejectFinish(new Error(event.detail ?? "Investigation failed"));
      eventSource.close();
    }
  };

  eventSource.onerror = () => {
    rejectFinish(new Error("Investigation stream disconnected"));
    eventSource.close();
  };

  return {
    close: () => eventSource.close(),
    finished,
  };
}

export async function exportInvestigation(
  historyId: string,
  format: ExportFormat,
): Promise<Blob> {
  const response = await apiClient.get(`/export/${historyId}`, {
    params: { format },
    responseType: "blob",
  });
  return response.data;
}

export function exportClientSide(
  result: InvestigationResponse,
  format: ExportFormat,
): Blob {
  const payload = {
    cluster: result.investigation.cluster,
    timestamp: new Date().toISOString(),
    status: result.status,
    ...result.diagnosis,
  };

  if (format === "json") {
    return new Blob([JSON.stringify(payload, null, 2)], {
      type: "application/json",
    });
  }

  const markdown = `# Kubernetes RCA Report

**Cluster:** ${JSON.stringify(result.investigation.cluster)}
**Status:** ${result.status}
**Confidence:** ${result.diagnosis.confidence}%

## Root Cause
${result.diagnosis.root_cause}

## Explanation
${result.diagnosis.explanation}

## Suggested Fix
${result.diagnosis.fix}

## Kubectl Command
\`\`\`
${result.diagnosis.kubectl_command}
\`\`\`
`;

  return new Blob([markdown], { type: "text/markdown" });
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function parseInvestigationError(error: unknown): InvestigationError {
  if (error instanceof Error && error.message.includes("Investigation stream")) {
    return {
      type: "backend_unavailable",
      title: "Investigation stream failed",
      message: error.message,
      hints: ["Retry the investigation", "Ensure the backend supports SSE on /investigate/stream"],
    };
  }

  if (isAxiosError(error)) {
    if (error.response?.status === 401) {
      return {
        type: "unauthorized",
        title: "Session expired",
        message: "Your session has expired or you are not signed in.",
        hints: [
          "Sign in again to continue",
          "Verify NEXT_PUBLIC_AUTH_ENABLED and NEXT_PUBLIC_INSFORGE_ANON_KEY are set",
        ],
      };
    }

    if (error.code === "ECONNABORTED") {
      return {
        type: "timeout",
        title: "Investigation timed out",
        message:
          "The investigation took too long to complete. This can happen on large clusters.",
        hints: [
          "Try again in a moment",
          "Ensure the backend is running and reachable",
          "Check backend logs for slow kubectl commands",
        ],
      };
    }

    if (!error.response) {
      return {
        type: "backend_unavailable",
        title: "Backend unavailable",
        message:
          "Unable to reach the investigation API. The backend may be stopped or unreachable.",
        hints: [
          "Start the backend with: uvicorn main:app --reload",
          "Verify NEXT_PUBLIC_API_BASE_URL in frontend/.env.local",
          "Confirm http://localhost:8000/health responds",
        ],
      };
    }

    const detail =
      typeof error.response.data?.detail === "string"
        ? error.response.data.detail
        : undefined;

    if (detail === "cluster access failed") {
      return {
        type: "cluster_access",
        title: "Unable to access Kubernetes cluster",
        message: "The backend could not verify cluster connectivity.",
        hints: [
          "Verify kubectl access on the machine running the backend",
          "Check kubeconfig path in backend/.env",
          "Confirm the selected cluster context is valid",
          "Run: kubectl get ns --context=<your-context>",
        ],
      };
    }

    if (detail === "invalid context selected") {
      return {
        type: "invalid_context",
        title: "Invalid cluster context",
        message: "The selected kubectl context could not be used.",
        hints: [
          "Choose a different cluster from the selector",
          "Run: kubectl config get-contexts",
        ],
      };
    }

    if (detail === "kubectl not found") {
      return {
        type: "kubectl_not_found",
        title: "kubectl not found",
        message: "The backend cannot find the kubectl binary.",
        hints: [
          "Install kubectl and ensure it is on PATH",
          "Restart the backend after installing kubectl",
        ],
      };
    }

    if (detail === "kubeconfig not found") {
      return {
        type: "kubeconfig_not_found",
        title: "kubeconfig not found",
        message: "The backend could not locate a valid kubeconfig file.",
        hints: [
          "Set KUBECONFIG_PATH in backend/.env",
          "Ensure ~/.kube/config exists",
          "Verify the kubeconfig file path is correct",
        ],
      };
    }

    return {
      type: "unknown",
      title: "Investigation failed",
      message: detail ?? `Request failed with status ${error.response.status}.`,
      hints: ["Check backend logs for more details"],
    };
  }

  return {
    type: "unknown",
    title: "Investigation failed",
    message: "An unexpected error occurred while running the investigation.",
    hints: ["Try again", "Check browser console and backend logs"],
  };
}

export function getOpenRouterWarning(
  diagnosis: InvestigationResponse["diagnosis"],
): string | null {
  if (
    diagnosis.root_cause === "Unable to determine root cause automatically" ||
    diagnosis.confidence < 50
  ) {
    if (diagnosis.explanation.toLowerCase().includes("openrouter")) {
      return diagnosis.explanation;
    }
    return "AI diagnosis used a fallback result. Verify OpenRouter configuration in backend/.env.";
  }
  return null;
}
