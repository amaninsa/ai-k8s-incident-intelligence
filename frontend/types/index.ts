export interface HealthResponse {
  status: string;
  service: string;
}

export interface InvestigationResult {
  rootCause: string;
  suggestedFix: string;
}
