# 04 - Dashboard, Authentication & API Integration

## Context

The application can now:

```text
Investigate Kubernetes
        ↓
Collect Evidence
        ↓
AI Reasoning
        ↓
Root Cause Analysis
        ↓
Suggested Fix
```

Current architecture:

```text
Frontend
    ↓
FastAPI Backend (Orchestrator)
    ↓
Kubernetes Investigation Layer
    ↓
AI Kubernetes Agent
    ↓
OpenRouter (Qwen 3.7 Max)
    ↓
Root Cause Analysis
```

The system works, but it still feels like a developer tool.

We now want to transform it into a real product experience.

---

## Goal

Build a professional user-facing dashboard.

Implement:

```text
Authentication
Cluster Selection
Realtime Investigation Progress
Diagnosis Dashboard
Investigation History
Frontend ↔ Backend Integration
```

Keep the implementation clean and beginner friendly.

Do not overengineer.

---

# Architecture

```text
User
 │
 ▼
Next.js Dashboard
 │
 ├── Authentication
 ├── Cluster Selection
 ├── Investigation History
 └── Investigation Results
 │
 ▼
FastAPI Backend
 │
 ├── Cluster Discovery
 ├── Kubernetes Investigation
 ├── AI Root Cause Analysis
 └── History Storage
 │
 ▼
InsForge
(Auth + Database)
```

---

# Requirements

## 1. Authentication

Implement authentication using InsForge.

Support:

```text
User Registration
Email OTP Verification
Login
Logout
Session Persistence
```

Requirements:

* Protected Dashboard
* JWT-based Sessions
* Route Protection
* Automatic Session Restore

Only authenticated users should be able to:

```text
Run Investigations
View History
Export Reports
```

---

## 2. Cluster Selection

The application must support multiple Kubernetes clusters.

Backend:

Create:

```http
GET /clusters
```

Return:

```json
[
  "kind-kubernetes-demo-cluster",
  "arn:aws:eks:eu-central-1:cluster/prod",
  "arn:aws:eks:eu-central-1:cluster/staging"
]
```

Frontend:

Display clusters as selectable cards.

Do NOT use a simple dropdown.

Each cluster card should display:

```text
Cluster Name
Environment Type
Selected State
```

Examples:

```text
┌────────────────────┐
│ KIND DEV CLUSTER   │
│ Local Development  │
└────────────────────┘

┌────────────────────┐
│ PROD EKS           │
│ Production         │
└────────────────────┘
```

Selected cluster should:

* Highlight
* Show check icon
* Enable investigation button

---

## 3. Dashboard

Create a professional dashboard.

Sections:

### Header

```text
AI Kubernetes Agent
```

---

### Cluster Selection

Display available clusters.

---

### Main CTA

Button:

```text
[ Investigate Cluster ]
```

Button remains disabled until a cluster is selected.

---

### Investigation Progress

Display realtime investigation stages:

```text
✓ Checking Pods
✓ Collecting Logs
✓ Reading Events
✓ Inspecting Deployments
✓ Checking Networking
✓ AI Reasoning
✓ Root Cause Found
```

---

### Diagnosis Card

Display:

```text
Root Cause
Explanation
Suggested Fix
kubectl Command
Confidence Score
Affected Resources
```

---

### Evidence Section

Collapsible panels:

```text
Pods
Events
Deployments
Networking
Logs
```

Display structured JSON.

---

## 4. Realtime Progress

Implement Server-Sent Events (SSE).

Backend:

```http
GET /investigate/stream
```

Frontend should receive:

```json
{
  "step": "Checking Pods",
  "status": "active"
}
```

Examples:

```text
Checking Pods
Collecting Logs
Reading Events
Inspecting Deployments
Checking Networking
AI Reasoning
Root Cause Found
```

Progress should reflect actual backend stages.

Do not simulate progress with timers.

---

## 5. Investigation History

Persist investigations in InsForge PostgreSQL.

Create table:

```text
investigation_history
```

Store:

```text
Timestamp
Cluster
Root Cause
Confidence
Status
Diagnosis
Investigation Data
```

Create endpoint:

```http
GET /history
```

Return:

```json
{
  "history": [...]
}
```

Frontend:

Display:

```text
Recent Investigations
```

Columns:

```text
Time
Cluster
Root Cause
Confidence
Status
```

Allow selecting historical investigations.

---

## 6. Export Support

Create:

```http
GET /export/{id}
```

Supported formats:

```text
JSON
Markdown
PDF
```

Frontend:

Buttons:

```text
Export JSON
Export Markdown
Export PDF
```

---

## 7. Frontend API Integration

Connect dashboard to backend.

Flow:

```text
Select Cluster
        ↓
Click Investigate
        ↓
SSE Progress
        ↓
Backend Investigation
        ↓
AI Analysis
        ↓
History Saved
        ↓
Diagnosis Displayed
```

Handle:

```text
Loading State
Timeouts
Network Failures
Authentication Errors
Empty Responses
```

---

## 8. UX Improvements

Show:

### Loading

```text
Investigating Kubernetes Cluster...
```

### Healthy Cluster

```text
No critical Kubernetes issues detected.

Cluster appears healthy.
```

### Authentication Required

```text
Please login to investigate clusters.
```

### Cluster Unreachable

```text
Unable to connect to cluster.

Verify:
- kubeconfig
- cluster access
- kubectl permissions
```

No stack traces should be exposed to users.

---

## Validation

### Authentication

```text
Signup
        ↓
Verify OTP
        ↓
Login
        ↓
Dashboard Access
```

---

### Cluster Discovery

```text
Load Clusters
        ↓
Select Cluster
        ↓
Investigate Enabled
```

---

### Investigation

```text
Click Investigate
        ↓
Realtime Progress
        ↓
Diagnosis
        ↓
History Entry Created
```

---

### Export

```text
Investigation
        ↓
Export JSON
Export Markdown
Export PDF
```

All formats should download successfully.

---

## Constraints

Do NOT break:

```text
Kubernetes Investigation Engine
AI Root Cause Analysis
OpenRouter Integration
```

Extend the existing system.

Do not rewrite working code.

---

## Expected Result

Users should now be able to:

```text
Register
        ↓
Verify Email
        ↓
Login
        ↓
Select Kubernetes Cluster
        ↓
Investigate Cluster
        ↓
Watch Realtime Progress
        ↓
Receive Root Cause Analysis
        ↓
View Investigation History
        ↓
Export Reports
```

The system should now feel like a real AI-powered Kubernetes Incident Intelligence Platform.
i
