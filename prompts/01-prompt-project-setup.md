# 01-prompt-project-setup.md

## Context

We are building an **AI Kubernetes Troubleshooting Agent**.

Architecture:

Frontend
↓
FastAPI Backend (Orchestrator)
↓
Kubernetes Investigation Layer
↓
AI Kubernetes Agent
↓
LLM Reasoning (OpenRouter)
↓
Root Cause + Suggested Fix
↓
Frontend Diagnosis

This is an on-demand troubleshooting platform.

Example flow:

User clicks "Investigate Cluster"
↓
Frontend API call
↓
Backend investigation
↓
AI reasoning
↓
Diagnosis returned
↓
Frontend displays results

We are NOT building a Kubernetes Operator or Controller.

---

## Goal

Set up the project foundation only.

Create:

* FastAPI backend
* Next.js frontend
* Docker setup
* Environment configuration
* Logging
* Health endpoint
* Basic folder structure

Do NOT implement:

* Kubernetes investigation
* AI reasoning
* OpenRouter calls
* Authentication
* History
* Realtime updates

Only create the foundation.
