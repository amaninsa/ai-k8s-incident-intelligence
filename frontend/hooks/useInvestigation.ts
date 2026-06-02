"use client";

import { useCallback, useEffect, useState } from "react";

import {
  getOpenRouterWarning,
  parseInvestigationError,
  streamInvestigation,
} from "@/services/investigationService";
import type {
  InvestigationError,
  InvestigationResponse,
} from "@/types/investigation";
import { INVESTIGATION_PROGRESS_STEPS } from "@/types/investigation";

export function useInvestigation() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<InvestigationError | null>(null);
  const [result, setResult] = useState<InvestigationResponse | null>(null);
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);
  const [activeStep, setActiveStep] = useState<string | null>(null);
  const [openRouterWarning, setOpenRouterWarning] = useState<string | null>(
    null,
  );

  const investigate = useCallback(async (context: string) => {
    if (!context) {
      setError({
        type: "invalid_context",
        title: "Cluster required",
        message: "Select a cluster context before running an investigation.",
        hints: ["Choose a cluster from the selector above"],
      });
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setOpenRouterWarning(null);
    setCompletedSteps([]);
    setActiveStep(INVESTIGATION_PROGRESS_STEPS[0]);

    const stream = streamInvestigation(context, (event) => {
      if (event.type === "progress" && event.step) {
        if (event.status === "active") {
          setActiveStep(event.step);
        }
        if (event.status === "complete") {
          setCompletedSteps((current) =>
            current.includes(event.step!) ? current : [...current, event.step!],
          );
        }
      }
    });

    try {
      const response = await stream.finished;
      setResult(response);
      setCompletedSteps([...INVESTIGATION_PROGRESS_STEPS]);
      setActiveStep(null);

      const warning = getOpenRouterWarning(response.diagnosis);
      if (warning) {
        setOpenRouterWarning(warning);
      }
    } catch (err) {
      setError(parseInvestigationError(err));
    } finally {
      stream.close();
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    result,
    completedSteps,
    activeStep,
    openRouterWarning,
    investigate,
    setResult,
  };
}
