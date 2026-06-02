# 🚀 AI Kubernetes Agent

****## Why this project?

Kubernetes troubleshooting often requires engineers to manually inspect pods, logs, events, deployments, networking, and cluster health signals.

This project automates the investigation workflow by collecting Kubernetes evidence, correlating operational signals, and generating AI-powered Root Cause Analysis with remediation recommendations.****



AI-powered Kubernetes Incident Intelligence Platform that automatically investigates Kubernetes clusters, correlates operational signals, and generates Root Cause Analysis (RCA) using Large Language Models.

The goal of this project is to reduce Kubernetes troubleshooting time by automating evidence collection, analysis, and remediation recommendations.

---

# 📸 Screenshots

## Login Page

<img width="1512" height="824" alt="image" src="https://github.com/user-attachments/assets/8dfab676-9875-4f40-a094-30f6fd43a94d" />



## Dashboard

<img width="838" height="221" alt="image" src="https://github.com/user-attachments/assets/693ac04a-da3a-4942-9091-4d6958e2e08f" />
<img width="849" height="521" alt="image" src="https://github.com/user-attachments/assets/172d1080-22ec-46d7-99ae-548b5b16e268" />



## Investigation Progress

<img width="944" height="488" alt="image" src="https://github.com/user-attachments/assets/ecb8b74a-b00b-40d7-8070-b4266a65cbd2" />
<img width="1357" height="662" alt="image" src="https://github.com/user-attachments/assets/fb81813f-baea-46ae-8c32-6c934f763c3c" />
<img width="966" height="598" alt="image" src="https://github.com/user-attachments/assets/c3c68699-48f3-4984-9237-2be4a53b2e72" />




## Root Cause Analysis
<img width="1151" height="736" alt="image" src="https://github.com/user-attachments/assets/3466c54c-b16f-4bbf-9560-cf002f0ca46c" />
<img width="1133" height="358" alt="image" src="https://github.com/user-attachments/assets/e5954f8e-5425-4d3c-96a8-385c8df6362b" />




## Investigation History

<img width="1133" height="285" alt="image" src="https://github.com/user-attachments/assets/9fb788bb-9289-43e2-a262-c868e794d720" />



# 🏗 Architecture

```text

```text
┌─────────────────────┐
│       User          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Next.js Frontend   │
│  Dashboard + Auth   │
└──────────┬──────────┘
           │ REST API / SSE
           ▼
┌─────────────────────┐
│  FastAPI Backend    │
│   Orchestrator      │
└──────────┬──────────┘
           │
           ├── Cluster Discovery
           ├── Pod Analysis
           ├── Event Analysis
           ├── Deployment Analysis
           ├── Log Collection
           └── Network Analysis
           │
           ▼
┌─────────────────────┐
│ Evidence Correlation│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ OpenRouter          │
│ Qwen 3.7 Max        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ AI Root Cause       │
│ Analysis Engine     │
└──────────┬──────────┘
           │
           ├── Diagnosis
           ├── Remediation
           ├── Exports
           └── Realtime Updates
           │
           ▼
┌─────────────────────┐
│ InsForge            │
│ Auth + PostgreSQL   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Investigation       │
│ History Dashboard   │
└─────────────────────┘
```




---

# 🔄 Investigation Flow

```text
Select Cluster
      │
      ▼
Collect Kubernetes Evidence
      │
      ├── Pods
      ├── Logs
      ├── Events
      ├── Deployments
      └── Networking
      │
      ▼
Evidence Correlation
      │
      ▼
AI Reasoning Engine
      │
      ▼
Root Cause Analysis
      │
      ▼
Suggested Remediation
      │
      ▼
Save Investigation History
      │
      ▼
Display Results
```

---

## Supported Clusters

- Kind
- Amazon EKS
- Any cluster available through kubeconfig contexts

# ✨ Features

### ☸️ Multi-Cluster Support

Supports:

* Kind Clusters
* Amazon EKS
* Multiple kubeconfig contexts

Users can investigate any Kubernetes cluster available in their kubeconfig.

---

### 🤖 AI-Powered Root Cause Analysis

Uses OpenRouter + Qwen 3.7 Max to:

* Analyze Kubernetes evidence
* Correlate operational signals
* Generate Root Cause Analysis
* Recommend fixes
* Suggest kubectl troubleshooting commands

---

### ⚡ Realtime Investigation Progress

Live investigation stages:

* Checking Pods
* Collecting Logs
* Reading Events
* Inspecting Deployments
* Checking Networking
* AI Reasoning
* Root Cause Found

Powered by Server-Sent Events (SSE).

---

### 🔐 Authentication & Security

* User Registration
* Login
* Email OTP Verification
* JWT Sessions
* Protected Dashboard

Powered by InsForge Authentication.

---

### 📚 Investigation History

Stores:

* Timestamp
* Cluster
* Root Cause
* Confidence Score
* Investigation Status

Users can revisit previous investigations directly from the dashboard.

---

### 📄 Export Support

Export investigations as:

* JSON
* Markdown
* PDF

---

# ☸️ Supported Kubernetes Problems

## Application Failures

* CrashLoopBackOff
* Restart Loops
* Failed Startup
* Readiness Probe Failures
* Liveness Probe Failures

---

## Image Problems

* ImagePullBackOff
* ErrImagePull
* Invalid Image Tags
* Registry Authentication Failures

---

## Resource Problems

* OOMKilled
* CPU Starvation
* Memory Pressure
* Resource Exhaustion

---

## Networking Problems

* CoreDNS Failures
* DNS Resolution Issues
* Service Connectivity Problems
* Service Selector Mismatch

---

## Deployment Problems

* Failed Rollouts
* Replica Mismatch
* Unavailable Replicas
* Stuck Deployments

---

## Storage Problems

* PVC Provisioning Failures
* StorageClass Issues
* Local Path Provisioner Failures

---

## Cluster Health Problems

* Critical Warning Events
* Node Instability
* Cluster Connectivity Failures
* Kubernetes API Access Issues

---

# 🛠 Tech Stack

| Layer             | Technology                       |
| ----------------- | -------------------------------- |
| Frontend          | Next.js, TypeScript, TailwindCSS |
| Backend           | FastAPI, Python                  |
| AI Gateway        | OpenRouter                       |
| LLM               | Qwen 3.7 Max                     |
| Authentication    | InsForge Auth                    |
| Database          | PostgreSQL (InsForge)            |
| Realtime Updates  | Server-Sent Events (SSE)         |
| Kubernetes Access | kubectl                          |
| Cluster Types     | Kind, Amazon EKS                 |
| Container Runtime | Docker                           |

---

# ⚙️ Installation & Setup

## Clone Repository

```bash
git clone https://github.com/amaninsa/ai-k8s-incident-intelligence.git

cd ai-k8s-incident-intelligence
```

---

## Backend Configuration

```bash
cp backend/.env.example backend/.env
```

Update:

```env
OPENROUTER_API_KEY=<your-openrouter-key>
OPENROUTER_MODEL=qwen/qwen3.7-max

KUBECONFIG_PATH=~/.kube/config

AUTH_ENABLED=true

INSFORGE_URL=<your-insforge-url>
```

---

## Frontend Configuration

```bash
cp frontend/.env.example frontend/.env.local
```

Update:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

NEXT_PUBLIC_INSFORGE_URL=<your-insforge-url>

NEXT_PUBLIC_INSFORGE_ANON_KEY=<your-anon-key>

NEXT_PUBLIC_AUTH_ENABLED=true
```

---

# 🐳 Run with Docker Compose

Start the complete application:

```bash
docker compose up --build
```

Services:

| Service  | Port |
| -------- | ---- |
| Frontend | 3000 |
| Backend  | 8000 |

Application URLs:

```text
Frontend:
http://localhost:3000

Backend:
http://localhost:8000

Swagger:
http://localhost:8000/docs
```

---

# 💻 Run Locally

## Backend

```bash
cd backend

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --reload --port 8000
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

Application URLs:

```text
Frontend:
http://localhost:3000

Backend:
http://localhost:8000
```

---

# ✅ Validation

## Backend Health Check

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

---

## Cluster Discovery

```bash
curl http://localhost:8000/clusters
```

Expected:

```json
[
  "kind-kubernetes-demo-cluster",
  "arn:aws:eks:..."
]
```

---

## Investigation

```bash
curl -X POST http://localhost:8000/investigate
```

Expected:

```json
{
  "status": "success",
  "diagnosis": {
    "root_cause": "...",
    "confidence": 85
  }
}
```

---

# 📊 Example Diagnosis

```text
Root Cause:
CoreDNS readiness probe timeout

Explanation:
CoreDNS pods are failing readiness checks due to DNS service instability.

Suggested Fix:
Restart the CoreDNS deployment and verify DNS connectivity.

Command:
kubectl rollout restart deployment coredns -n kube-system

Confidence:
84%
```

---

# 🚀 Future Improvements

* Prometheus Integration
* Grafana Correlation
* Slack Notifications
* AI Incident Timeline
* Kubernetes Recommendation Engine
* Multi-Tenant Support
* Automated Remediation Workflows
* Alert Correlation Engine

---

# 👨‍💻 Author

**Aman Vats**

Cloud & DevOps Engineer

Passionate about Kubernetes, Cloud Infrastructure, Platform Engineering, SRE, and AI-powered Operations.

### Connect

* LinkedIn: https://www.linkedin.com/in/aman-vatsss/
* GitHub: https://github.com/amaninsa

---

## Highlights

- Multi-cluster Kubernetes investigations
- AI-powered Root Cause Analysis
- Realtime investigation progress (SSE)
- Authentication with Email OTP
- Investigation History & Reports
- JSON / Markdown / PDF exports
- Docker & Local deployment support



## Development Notes

This project was developed using an AI-assisted engineering workflow combining:
- Kubernetes troubleshooting expertise
- Prompt engineering
- FastAPI
- Next.js
- OpenRouter
- InsForge
  
⭐ If you found this project useful, consider giving it a star.

