"use client";

import {
  downloadBlob,
  exportClientSide,
  exportInvestigation,
} from "@/services/investigationService";
import type { ExportFormat, InvestigationResponse } from "@/types/investigation";

interface ExportMenuProps {
  result: InvestigationResponse;
}

export default function ExportMenu({ result }: ExportMenuProps) {
  const handleExport = async (format: ExportFormat) => {
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    const baseName = result.history_id ?? timestamp;

    if (result.history_id && format !== "json") {
      const blob = await exportInvestigation(result.history_id, format);
      const extension = format === "markdown" ? "md" : format;
      downloadBlob(blob, `rca-${baseName}.${extension}`);
      return;
    }

    const blob = exportClientSide(result, format === "pdf" ? "markdown" : format);
    const extension = format === "markdown" ? "md" : "json";
    downloadBlob(blob, `rca-${baseName}.${extension}`);
  };

  return (
    <div className="flex flex-wrap gap-2">
      <button type="button" onClick={() => handleExport("json")} className="btn-secondary">
        JSON
      </button>
      <button type="button" onClick={() => handleExport("markdown")} className="btn-secondary">
        Markdown
      </button>
      <button
        type="button"
        onClick={() => handleExport("pdf")}
        disabled={!result.history_id}
        className="btn-premium w-auto px-5 disabled:shadow-none"
      >
        PDF Report
      </button>
    </div>
  );
}
