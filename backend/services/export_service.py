"""Export investigation diagnoses in multiple formats."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


def build_export_payload(record: dict[str, Any]) -> dict[str, Any]:
    diagnosis = record.get("diagnosis") or {}
    return {
        "cluster": record.get("cluster"),
        "timestamp": record.get("timestamp") or datetime.now(timezone.utc).isoformat(),
        "root_cause": diagnosis.get("root_cause", record.get("root_cause", "")),
        "explanation": diagnosis.get("explanation", ""),
        "fix": diagnosis.get("fix", ""),
        "kubectl_command": diagnosis.get("kubectl_command", ""),
        "confidence": diagnosis.get("confidence", record.get("confidence", 0)),
        "prevention_recommendation": diagnosis.get("prevention_recommendation", ""),
        "affected_resources": diagnosis.get("affected_resources", []),
        "evidence_count": diagnosis.get("evidence_count", 0),
        "status": record.get("status"),
    }


def export_as_json(record: dict[str, Any]) -> str:
    return json.dumps(build_export_payload(record), indent=2)


def export_as_markdown(record: dict[str, Any]) -> str:
    payload = build_export_payload(record)
    resources = ", ".join(payload.get("affected_resources") or []) or "None"

    return f"""# Kubernetes RCA Report

**Cluster:** {payload.get("cluster")}
**Timestamp:** {payload.get("timestamp")}
**Status:** {payload.get("status")}
**Confidence:** {payload.get("confidence")}%

## Root Cause
{payload.get("root_cause")}

## Explanation
{payload.get("explanation")}

## Suggested Fix
{payload.get("fix")}

## Kubectl Command
```
{payload.get("kubectl_command")}
```

## Prevention
{payload.get("prevention_recommendation")}

## Affected Resources
{resources}

## Evidence Count
{payload.get("evidence_count")}
"""


def export_as_pdf_bytes(record: dict[str, Any]) -> bytes:
    """Generate a simple text-based PDF report."""
    markdown = export_as_markdown(record)
    lines = markdown.splitlines()

    content_lines = []
    y = 800
    for line in lines[:60]:
        safe_line = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content_lines.append(f"BT /F1 10 Tf 50 {y} Td ({safe_line}) Tj ET")
        y -= 14
        if y < 50:
            break

    stream = "\n".join(content_lines)
    pdf = f"""%PDF-1.4
1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj
2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj
3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj
4 0 obj<< /Length {len(stream)} >>stream
{stream}
endstream endobj
5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj
xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000060 00000 n 
0000000114 00000 n 
0000000280 00000 n 
trailer<< /Size 6 /Root 1 0 R >>
startxref
400
%%EOF"""
    return pdf.encode("latin-1", errors="replace")
