# 02 - Kubernetes Investigation Engine

## Context

The project foundation is complete.

Current state:

```text
Frontend
    ↓
FastAPI Backend
```

The backend currently supports:

* Configuration Management
* Logging
* Health Endpoint
* Docker Setup

We now want to build the Kubernetes Investigation Layer.

This layer will be responsible for collecting evidence from Kubernetes clusters.

No AI reasoning should happen yet.

At this stage we are only gathering facts.

---

## Goal

Build a Kubernetes investigation engine capable of:

```text
Connect to Cluster
        ↓
Collect Evidence
        ↓
Return Structured Results
```

The investigation engine should be reusable by future AI modules.

---

## Architecture

```text
Frontend
    ↓
FastAPI Backend
    ↓
Kubernetes Investigation Layer
        ├── Cluster Verification
        ├── Pod Analysis
        ├── Event Analysis
        ├── Deployment Analysis
        ├── Log Collection
        └── Network Analysis
```

---

## Requirements

### 1. Cluster Verification

Implement cluster connectivity validation.

Verify:

```text
kubectl exists
kubectl can access cluster
current context exists
```

If cluster access fails:

Return:

```json
{
  "connected": false,
  "error": "cluster access failed"
}
```

---

### 2. Investigation Endpoint

Create:

```http
POST /investigate
```

Flow:

```text
Receive request
        ↓
Verify cluster access
        ↓
Collect evidence
        ↓
Return structured investigation result
```

No AI reasoning yet.

---

### 3. Pod Analysis

Collect:

```text
kubectl get pods -A
```

Detect:

```text
CrashLoopBackOff
ImagePullBackOff
ErrImagePull
OOMKilled
Error
Pending
```

Return:

```json
{
  "healthy": false,
  "problematic_pods": [...]
}
```

---

### 4. Log Collection

For problematic pods:

Collect:

```text
kubectl logs
```

Store:

```json
{
  "pod_name": "example",
  "logs": "..."
}
```

Limit logs:

```text
Last 100 lines
```

Avoid huge payloads.

---

### 5. Event Analysis

Collect:

```text
kubectl get events -A
```

Focus on:

```text
Warning
Failed
BackOff
Unhealthy
FailedScheduling
FailedMount
```

Return:

```json
{
  "critical_events": [...]
}
```

---

### 6. Deployment Analysis

Collect:

```text
kubectl get deployments -A
```

Detect:

```text
Unavailable Replicas
Replica Mismatch
Failed Rollouts
```

Return:

```json
{
  "healthy": false,
  "issues": [...]
}
```

---

### 7. Network Analysis

Collect:

```text
kubectl get svc -A
kubectl get endpoints -A
```

Detect:

```text
Services without endpoints
Selector mismatches
```

Return:

```json
{
  "healthy": false,
  "issues": [...]
}
```

---

## Response Format

Return structured evidence:

```json
{
  "cluster": {
    "connected": true,
    "current_context": "kind-demo"
  },
  "pods": {},
  "logs": {},
  "events": {},
  "deployments": {},
  "network": {}
}
```

---

## Frontend Integration

Connect the existing:

```text
[ Investigate Cluster ]
```

button to:

```http
POST /investigate
```

Display raw JSON results.

No dashboard yet.

No AI diagnosis yet.

Just show collected evidence.

---

## Error Handling

Handle:

### Missing kubectl

```json
{
  "error": "kubectl not found"
}
```

### Missing kubeconfig

```json
{
  "error": "kubeconfig not found"
}
```

### Cluster Unreachable

```json
{
  "error": "cluster unreachable"
}
```

---

## Validation Scenarios

### Healthy Cluster

Expected:

```json
{
  "connected": true,
  "healthy": true
}
```

### CrashLoopBackOff

Create test deployment:

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
      - name: app
        image: busybox
        command: ["false"]
```

Expected:

```text
CrashLoopBackOff detected
Logs collected
```

### ImagePullBackOff

Deploy:

```yaml
image: nginx:does-not-exist
```

Expected:

```text
ImagePullBackOff detected
```

---

## Constraints

Do NOT implement:

* OpenRouter
* AI Reasoning
* Root Cause Analysis
* Authentication
* Investigation History
* Realtime Updates

Only build the Kubernetes Investigation Engine.

---

## Expected Result

The application should now be able to:

```text
Click Investigate
        ↓
Connect to Kubernetes
        ↓
Collect Evidence
        ↓
Return Structured Results
```

The system should now understand the current state of a Kubernetes cluster and prepare evidence for AI analysis in the next step.
