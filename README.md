# Autergo AI Interview System

An AI-powered technical interview platform that conducts structured, voice-driven interviews, evaluates candidates automatically, and delivers detailed reports to recruiters — all with zero human interviewer involvement.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Running Tests](#running-tests)
- [Implementation Status](#implementation-status)
- [Engineering Backlog](#engineering-backlog)

---

## Overview

Autergo automates the live technical interview. A recruiter creates a job drive, uploads a JD, and invites candidates. Each candidate joins a voice session where an AI interviewer conducts a structured conversation — from device check through deep-dive competency probing — then async agents score the transcript and generate a PDF report.

Key properties:

- **Deterministic interview flow** — a validated state machine controls every stage transition; no undefined behaviour.
- **Multi-tenant isolation** — PostgreSQL Row-Level Security ensures tenant data is fully isolated.
- **Voice-first UX** — candidates interact by speaking; LiveKit handles the WebRTC media plane.
- **Async post-processing** — Celery workers run evaluation and reporting off the critical path.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Frontend                         │
│           React 18 + Vite + Tailwind CSS                │
└────────────────────────┬────────────────────────────────┘
                         │ REST / WebSocket
┌────────────────────────▼────────────────────────────────┐
│                    FastAPI Backend                       │
│  /api/v1  ·  Clerk JWT Auth  ·  X-Request-ID Tracing    │
│                                                         │
│  ┌────────────────────┐   ┌────────────────────────┐    │
│  │  Interview Engine  │   │   AI Provider Layer    │    │
│  │  State Machine     │   │   Groq (Llama 3 8B)    │    │
│  │  Session Manager   │   │   Deepgram STT/TTS     │    │
│  └────────────────────┘   └────────────────────────┘    │
└────────────┬───────────────────────┬────────────────────┘
             │                       │
┌────────────▼──────────┐  ┌─────────▼──────────────────┐
│   PostgreSQL 15        │  │   Redis + Celery Workers   │
│   Alembic migrations   │  │   Evaluation · Reports     │
│   Row-Level Security   │  │   Email dispatch           │
└───────────────────────┘  └────────────────────────────┘
             │
┌────────────▼──────────┐
│   LiveKit SFU          │
│   WebRTC media plane   │
└───────────────────────┘
```

For the full design see [`AUTERGO_ARCHITECTURE_BASELINE_v2.0.md`](./AUTERGO_ARCHITECTURE_BASELINE_v2.0.md) and [`AUTERGO_HLD_LLD_v1.0.md`](./AUTERGO_HLD_LLD_v1.0.md).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI 0.104, Uvicorn, Pydantic v2 |
| Database | PostgreSQL 15, SQLAlchemy 2.0 (async), Alembic |
| Auth | Clerk (JWT verification via PyJWT) |
| Realtime | LiveKit (WebRTC SFU), `livekit-api` SDK |
| LLM | Groq — Llama 3 8B (async streaming) |
| Speech | Deepgram STT / Cartesia TTS |
| Task Queue | Celery 5.3, Redis 7 |
| Frontend | React 18, Vite 5, Tailwind CSS 3, Framer Motion |
| Testing | pytest, pytest-asyncio |
| Infra | Docker Compose, GitHub Actions CI |

---

## Project Structure

```
├── backend/
│   ├── api/
│   │   └── v1/             # Route handlers: drives, interviews, invitations,
│   │                       #   jobs, evaluations, realtime, resumes, sessions
│   ├── core/
│   │   ├── engine/
│   │   │   └── state_machine.py   # Interview state machine (TASK-ENG-001 ✅)
│   │   ├── services/       # Business logic services
│   │   ├── errors.py       # Domain error hierarchy (StateTransitionError, …)
│   │   └── config.py       # Settings via pydantic-settings
│   ├── dependencies/       # FastAPI dependency injection (auth, db session)
│   ├── middleware/         # Tracing, CORS
│   └── main.py             # Application entry point
├── workers/                # Celery task definitions
├── agents/                 # AI agent implementations
├── realtime/               # LiveKit / provider adapters
├── models/                 # SQLAlchemy ORM models
├── alembic/                # Database migrations
├── frontend/
│   ├── src/                # React components and pages
│   └── index.html
├── tests/
│   ├── unit/               # Unit tests (state machine, auth, tokens)
│   ├── integration/        # DB and API integration tests
│   └── ai/                 # Agent evaluation tests
├── infra/                  # Infrastructure-as-code
├── docs/                   # Extended documentation
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 20+

### 1. Clone and configure

```bash
git clone <repo-url>
cd "AI Interview System"
cp .env.example .env
# Fill in secrets — see Environment Variables section below
```

### 2. Start services

```bash
docker-compose up
```

This starts the FastAPI API on `http://localhost:8000`, PostgreSQL on `5432`, and Redis on `6379`.

### 3. Run database migrations

```bash
alembic upgrade head
```

### 4. Start the frontend (development)

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server starts on `http://localhost:5173`.

---

## Environment Variables

Copy `.env.example` to `.env` and populate:

| Variable | Description |
|---|---|
| `ENV` | `development` or `production` |
| `DATABASE_URL` | PostgreSQL connection string (asyncpg) |
| `REDIS_URL` | Redis connection string |
| `CLERK_SECRET_KEY` | Clerk backend secret key for JWT verification |

Additional variables (LiveKit, Groq, Deepgram, Resend) are documented in [`AUTERGO_IMPLEMENTATION_SPEC_v2.0.md`](./AUTERGO_IMPLEMENTATION_SPEC_v2.0.md).

---

## Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Unit tests only
python -m pytest tests/unit/ -v

# With coverage
python -m pytest tests/ --cov=backend --cov-report=term-missing
```

Current status: **101 tests passing**.

---

## Implementation Status

| Task | Description | Status |
|---|---|---|
| TASK-FND-001 | Repository scaffolding | ✅ Done |
| TASK-DB-001 | Alembic migrations (core schema) | ✅ Done |
| TASK-AUTH-001 | Clerk JWT verification | ✅ Done |
| TASK-ENG-001 | Interview state machine | ✅ Done |
| TASK-TEN-001 | PostgreSQL Row-Level Security | 🔲 Pending |
| TASK-AI-001 | GLiNER JD/Resume extraction | 🔲 Pending |
| TASK-INV-001 | Candidate guest JWT | 🔲 Pending |
| TASK-PROV-001 | Groq async streaming adapter | 🔲 Pending |
| TASK-RTC-001 | LiveKit token management | 🔲 Pending |
| TASK-EVAL-001 | TechnicalEvaluator NAT agent | 🔲 Pending |
| TASK-REP-001 | PDF report generation + email | 🔲 Pending |
| TASK-OBS-001 | X-Request-ID tracing middleware | 🔲 Pending |
| TASK-SEC-001 | Llama Guard 3 prompt injection filter | 🔲 Pending |

### Next dependency-ready tasks

- **TASK-EVAL-001** — unblocked by TASK-ENG-001 (just completed)
- **TASK-INV-001** — no blockers
- **TASK-RTC-001** — unblocked by TASK-AUTH-001

---

## Engineering Backlog

Full backlog with acceptance criteria and dependency graph: [`AUTERGO_ENGINEERING_BACKLOG_v1.0.md`](./AUTERGO_ENGINEERING_BACKLOG_v1.0.md)

Phase plan summary:

| Phase | Scope |
|---|---|
| 0 — Foundation | Repo, DevOps, DB, Auth |
| 1 — Core Tenancy | Multi-tenancy, Admin, Users, Companies |
| 2 — Pre-Interview | Resume/JD processing, Jobs, Drives, Invitations |
| 3 — Live Interview | AI provider layer, Realtime voice, Interview engine |
| 4 — Post-Interview | Agents, Evaluation, Reports, Integrity, Email |
| 5 — Hardening | Security, Observability, Testing |
| Future | Coding interview sandbox, Enterprise SSO, ATS integrations |
