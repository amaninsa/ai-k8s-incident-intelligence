# 03 - AI Root Cause Analysis Engine

## Context

The Kubernetes Investigation Engine is now complete.

Current architecture:

```text
Frontend
    ↓
FastAPI Backend
    ↓
Kubernetes Investigation Layer
        ↓
Structured Evidence
```

The system can already collect:

* Cluster Status
* Pod Health
* Logs
* Events
* Deployments
* Networking Information

However, users still need to manually interpret the results.

We now want to introduce AI-powered reasoning.

---

## Goal

Build an AI Root Cause Analysis Engine.

The system should:

```text
Collect Kubernetes Evidence
        ↓
Send Evidence to LLM
        ↓
Generate Root Cause Analysis
        ↓
Generate Suggested Fix
        ↓
Return Diagnosis
```

The user should no longer need to manually analyze Kubernetes evidence.

---

## Architecture

```text
Frontend
    ↓
FastAPI Backend (Orchestrator)
    ↓
Kubernetes Investigation Layer
    ↓
Evidence Package
    ↓
AI Kubernetes Agent
    ↓
OpenRouter
(Qwen 3.7 Max)
    ↓
Root Cause Analysis
    ↓
Suggested Fix
```

---

## Requirements

### 1. OpenRouter Integration

Use:

```text
OpenRouter API
```

Default model:

```text
qwen/qwen3.7-max
```

Configuration:

```env
OPENROUTER_API_KEY=
OPENROUTER_MODEL=qwen/qwen3.7-max
```

Create a dedicated AI service.

Responsibilities:

```text
Prompt Construction
LLM Invocation
Response Parsing
Fallback Handling
```

---

### 2. Evidence Packaging

Convert Kubernetes investigation results into a structured evidence package.

Input:

```json
{
  "cluster": {},
  "pods": {},
  "logs": {},
  "events": {},
  "deployments": {},
  "network": {}
}
```

Provide only relevant information to the LLM.

Avoid sending:

```text
Large logs
Unnecessary metadata
Noise
```

Keep prompts concise.

---

### 3. AI Kubernetes Agent

The AI agent should behave like:

```text
Senior Kubernetes SRE
Platform Engineer
Production Incident Responder
```

Responsibilities:

* Identify root cause
* Explain failure
* Recommend remediation
* Suggest kubectl commands
* Estimate confidence level

---

### 4. Diagnosis Format

Return:

```json
{
  "root_cause": "...",
  "explanation": "...",
  "fix": "...",
  "kubectl_command": "...",
  "prevention_recommendation": "...",
  "confidence": 90
}
```

Confidence range:

```text
0 - 100
```

---

### 5. Root Cause Categories

The AI should identify:

### Application Problems

```text
CrashLoopBackOff
Startup Failures
Readiness Failures
Liveness Failures
```

---

### Image Problems

```text
ImagePullBackOff
ErrImagePull
Registry Authentication Failures
```

---

### Resource Problems

```text
OOMKilled
Memory Pressure
CPU Starvation
```

---

### Networking Problems

```text
CoreDNS Failures
DNS Resolution Issues
Service Connectivity Problems
Selector Mismatch
```

---

### Deployment Problems

```text
Failed Rollouts
Replica Mismatch
Unavailable Replicas
```

---

### Storage Problems

```text
PVC Failures
StorageClass Issues
Provisioner Failures
```

---

## AI Prompting Strategy

The AI should:

### Step 1

Analyze:

```text
Pods
Logs
Events
Deployments
Networking
```

### Step 2

Correlate signals.

Example:

```text
CrashLoopBackOff
+
ConfigMap Error
+
Startup Log Failure
```

↓

```text
Root Cause:
Missing configuration
```

### Step 3

Generate remediation.

---

## Update Investigation Endpoint

Current:

```http
POST /investigate
```

New flow:

```text
Collect Evidence
        ↓
AI Analysis
        ↓
Return Diagnosis
```

Return:

```json
{
  "status": "success",
  "investigation": {},
  "diagnosis": {}
}
```

---

## OpenRouter Failure Handling

Handle:

### Missing API Key

Return:

```json
{
  "status": "warning",
  "message": "AI analysis unavailable"
}
```

---

### OpenRouter Timeout

Return:

```json
{
  "status": "warning",
  "message": "AI request timed out"
}
```

---

### Invalid Model

Return:

```json
{
  "status": "warning",
  "message": "AI model unavailable"
}
```

Investigation evidence should still be returned.

The system must never fail completely because of AI.

---

## Example Scenarios

### Scenario 1

Evidence:

```text
CrashLoopBackOff
```

Logs:

```text
DATABASE_URL missing
```

Expected:

```text
Root Cause:
Missing DATABASE_URL

Fix:
Add environment variable

Confidence:
95%
```

---

### Scenario 2

Evidence:

```text
ImagePullBackOff
```

Expected:

```text
Root Cause:
Invalid container image

Fix:
Update image tag

Confidence:
98%
```

---

### Scenario 3

Evidence:

```text
OOMKilled
```

Expected:

```text
Root Cause:
Container exceeded memory limit

Fix:
Increase memory limits

Confidence:
92%
```

---

### Scenario 4

Evidence:

```text
Service without endpoints
```

Expected:

```text
Root Cause:
Service selector mismatch

Fix:
Update service selector labels

Confidence:
90%
```

---

## Frontend

Display:

```text
Root Cause
Explanation
Suggested Fix
kubectl Command
Confidence
```

Raw JSON evidence can remain visible below diagnosis.

No dashboard redesign required yet.

---

## Constraints

Do NOT implement:

* Authentication
* Investigation History
* Realtime Updates
* Multi-user Support

Focus only on:

```text
AI Analysis
OpenRouter Integration
Root Cause Analysis
Diagnosis Generation
```

---

## Expected Result

Users should now be able to:

```text
Click Investigate
        ↓
Collect Kubernetes Evidence
        ↓
AI Analysis
        ↓
Root Cause Analysis
        ↓
Suggested Fix
```

The application should now behave like an AI-powered Kubernetes troubleshooting assistant rather than a simple evidence collector.
