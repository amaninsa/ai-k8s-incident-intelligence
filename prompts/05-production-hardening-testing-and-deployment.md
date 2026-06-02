# 05 - Production Hardening, Testing & Deployment Readiness

## Context

The AI Kubernetes Agent is now feature complete.

Users can:

```text
Register
        ↓
Verify Email OTP
        ↓
Login
        ↓
Select Kubernetes Cluster
        ↓
Investigate Cluster
        ↓
Realtime Progress Updates
        ↓
AI Root Cause Analysis
        ↓
View Investigation History
        ↓
Export Reports
```

Current Architecture:

```text
Next.js Frontend
        ↓
FastAPI Backend
        ↓
Kubernetes Investigation Engine
        ↓
AI Root Cause Analysis
(OpenRouter)
        ↓
Investigation History
(InsForge PostgreSQL)
        ↓
Dashboard
```

The application now works as a product.

The next objective is to make it reliable, production-ready, and easier to operate.

---

# Goal

Implement:

```text
End-to-End Validation
Reliability Improvements
Production Hardening
Failure Simulation
Observability
Deployment Readiness
```

The application should now feel like a real-world platform engineering tool.

---

# Architecture

```text
User
 │
 ▼
Next.js Dashboard
 │
 ▼
FastAPI Backend
 │
 ├── Cluster Discovery
 ├── Investigation Engine
 ├── AI RCA Engine
 ├── Export Service
 ├── History Service
 └── Authentication
 │
 ▼
OpenRouter
 │
 ▼
InsForge
 │
 ▼
Kubernetes Clusters
```

---

# Requirements

## 1. End-to-End Validation

Validate the complete workflow.

Expected flow:

```text
User Login
        ↓
Cluster Discovery
        ↓
Cluster Selection
        ↓
Investigation
        ↓
Evidence Collection
        ↓
AI Analysis
        ↓
History Persistence
        ↓
Dashboard Update
        ↓
Export
```

Validate:

* Authentication
* Cluster Selection
* Investigation
* AI Analysis
* History Storage
* Export Functionality
* Realtime Updates

---

## 2. Reliability Improvements

Improve error handling.

Handle:

### Kubernetes Errors

```text
kubectl missing
kubeconfig missing
cluster unreachable
invalid context
permission denied
```

Display user-friendly messages.

Example:

```text
Unable to connect to Kubernetes cluster.

Please verify:
- kubeconfig path
- cluster access
- kubectl permissions
```

---

### AI Errors

Handle:

```text
OpenRouter timeout
invalid model
rate limiting
missing API key
```

Fallback:

```text
Investigation completed.

AI diagnosis unavailable.

Raw investigation evidence is still available.
```

---

### Authentication Errors

Handle:

```text
expired JWT
invalid session
OTP verification failure
unauthorized access
```

Redirect users appropriately.

---

### History Errors

Handle:

```text
database unavailable
RLS rejection
invalid token
```

The investigation should still complete even if history persistence fails.

---

## 3. Empty State Improvements

### Healthy Cluster

Display:

```text
No critical Kubernetes issues detected.

Cluster appears healthy.
```

---

### No Investigation Yet

Display:

```text
Select a Kubernetes cluster and start an investigation.
```

---

### No History

Display:

```text
No previous investigations found.
```

---

## 4. Kubernetes Failure Testing

Create reproducible Kubernetes test scenarios.

---

### Scenario 1 — CrashLoopBackOff

Example:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crash-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: crash-demo
  template:
    metadata:
      labels:
        app: crash-demo
    spec:
      containers:
      - name: crash-demo
        image: busybox
        command: ["false"]
```

Expected diagnosis:

```text
Root Cause:
Container repeatedly exits immediately.

Suggested Fix:
Correct startup command.
```

---

### Scenario 2 — ImagePullBackOff

Example:

```yaml
image: nginx:this-tag-does-not-exist
```

Expected diagnosis:

```text
Root Cause:
Invalid image tag.

Suggested Fix:
Update deployment image.
```

---

### Scenario 3 — OOMKilled

Example:

```yaml
resources:
  limits:
    memory: "32Mi"
```

Expected diagnosis:

```text
Root Cause:
Container exceeded memory limit.

Suggested Fix:
Increase memory requests and limits.
```

---

### Scenario 4 — Service Selector Mismatch

Example:

```yaml
selector:
  app: wrong-label
```

Expected diagnosis:

```text
Root Cause:
Service selector does not match pod labels.

Suggested Fix:
Update selector labels.
```

---

### Scenario 5 — PVC Failure

Example:

```text
Missing StorageClass
```

Expected diagnosis:

```text
Root Cause:
Persistent Volume Claim cannot be provisioned.

Suggested Fix:
Create StorageClass or update PVC configuration.
```

---

## 5. Observability

Improve application visibility.

### Backend Logging

Track:

```text
Authentication Events
Investigation Start
Investigation Completion
AI Requests
History Persistence
Export Generation
```

Use structured logging.

---

### Metrics

Expose:

```http
GET /health
```

Include:

```json
{
  "status": "healthy",
  "service": "ai-kubernetes-agent"
}
```

Future-compatible for Prometheus integration.

---

## 6. Multi-Cluster Validation

Validate:

```text
Kind
Amazon EKS
Multiple kubeconfig contexts
```

Requirements:

* Cluster switching works correctly
* Investigations target selected cluster only
* Invalid contexts return friendly errors

---

## 7. Deployment Readiness

Prepare for production deployment.

Create:

### Backend Dockerfile

Production-ready image.

---

### Frontend Dockerfile

Production Next.js image.

---

### Docker Compose

Support:

```text
Frontend
Backend
```

Single-command startup:

```bash
docker compose up --build
```

---

## 8. Security Review

Validate:

### Secrets

Ensure:

```text
No API keys in repository
No hardcoded tokens
No credentials committed
```

---

### Environment Variables

Use:

```env
OPENROUTER_API_KEY=
INSFORGE_URL=
NEXT_PUBLIC_INSFORGE_URL=
NEXT_PUBLIC_API_BASE_URL=
```

---

### Protected Routes

Verify:

```text
Dashboard
History
Exports
Investigation APIs
```

Require authentication.

---

## Validation Checklist

### Authentication

```text
Signup
OTP Verification
Login
Logout
Session Restore
```

---

### Cluster Selection

```text
Load Clusters
Select Cluster
Switch Cluster
```

---

### Investigation

```text
Run Investigation
Receive Diagnosis
Receive Confidence Score
```

---

### History

```text
Save Investigation
Load Investigation History
Open Previous Investigation
```

---

### Export

```text
Export JSON
Export Markdown
Export PDF
```

---

### Failure Simulation

```text
CrashLoopBackOff
ImagePullBackOff
OOMKilled
PVC Failure
Service Selector Mismatch
```

All should generate meaningful AI diagnoses.

---

## Constraints

Do NOT rewrite:

```text
Authentication
Investigation Engine
AI Reasoning Engine
History System
Export System
```

Only improve reliability, validation, testing, and deployment readiness.

Extend existing functionality.

---

## Expected Result

The platform should now support:

```text
Authentication
        ↓
Cluster Selection
        ↓
Realtime Investigation
        ↓
AI Root Cause Analysis
        ↓
History Persistence
        ↓
Report Export
        ↓
Production-Ready Reliability
```

The application should now resemble a real-world AI-powered Kubernetes Incident Intelligence Platform suitable for Platform Engineering, SRE, and DevOps environments.
i
