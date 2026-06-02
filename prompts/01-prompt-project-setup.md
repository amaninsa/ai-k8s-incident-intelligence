# 01 - Foundation & Project Setup

## Context

We want to build an AI-powered Kubernetes troubleshooting platform.

The long-term vision is:

```text
User
   ↓
Select Kubernetes Cluster
   ↓
Investigate Cluster
   ↓
Collect Kubernetes Evidence
   ↓
AI Root Cause Analysis
   ↓
Suggested Remediation
   ↓
Investigation History
```

The system should eventually support:

* Kubernetes cluster investigations
* AI-powered Root Cause Analysis
* Multi-cluster support
* Authentication
* Investigation history
* Realtime updates

However, in this first step we only want to establish the project foundation.

---

## Goal

Create the initial project structure for:

```text
Frontend
Backend
Configuration
Logging
Docker Setup
```

The objective is to create a clean and scalable foundation.

Do not implement Kubernetes investigation logic yet.

Do not implement AI reasoning yet.

---

## Architecture

```text
Frontend (Next.js)
        ↓
FastAPI Backend
        ↓
Future Kubernetes Investigation Layer
        ↓
Future AI Layer
```

---

## Requirements

### Backend

Use:

* FastAPI
* Pydantic Settings
* Loguru
* HTTPX

Create a clean structure:

```text
backend/
├── api/
├── core/
├── services/
├── kubernetes/
├── ai/
├── models/
├── main.py
```

Implement:

* Health endpoint
* Configuration management
* Centralized logging
* Environment variable loading

Health endpoint:

```http
GET /health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "ai-kubernetes-agent"
}
```

---

### Frontend

Use:

* Next.js
* TypeScript
* TailwindCSS

Create a minimal landing page.

Display:

```text
AI Kubernetes Agent

[ Investigate Cluster ]
```

No functionality required yet.

Only UI scaffolding.

---

### Configuration

Support environment variables using:

Backend:

```env
OPENROUTER_API_KEY=
OPENROUTER_MODEL=
KUBECONFIG_PATH=
```

Frontend:

```env
NEXT_PUBLIC_API_BASE_URL=
```

---

### Logging

Implement centralized structured logging.

Requirements:

* Startup logs
* Request logs
* Error logs

Use Loguru.

---

### Docker

Create:

```text
Dockerfile
docker-compose.yml
```

Services:

```text
frontend
backend
```

Expose:

```text
Frontend → 3000
Backend → 8000
```

---

## Validation

The following should work:

### Backend

```bash
curl http://localhost:8000/health
```

Expected:

```json
{
  "status": "healthy",
  "service": "ai-kubernetes-agent"
}
```

### Frontend

Open:

```text
http://localhost:3000
```

Expected:

```text
AI Kubernetes Agent

[ Investigate Cluster ]
```

---

## Constraints

Do NOT implement:

* Kubernetes investigation
* OpenRouter integration
* AI reasoning
* Authentication
* History
* Realtime updates

Only create the project foundation.

Keep the implementation beginner-friendly and production-ready.

---

## Expected Result

A developer should be able to:

```text
Clone Repository
      ↓
Run Docker Compose
      ↓
Open Frontend
      ↓
Call Health Endpoint
```

The project should now be ready for Kubernetes investigation features in the next prompt.
