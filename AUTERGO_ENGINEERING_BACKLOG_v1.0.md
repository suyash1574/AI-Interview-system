# AUTERGO ENGINEERING BACKLOG

## 1. MVP SPRINT / PHASE PLAN

Tasks must be executed in dependency order to prevent blocked workflows.

*   **Phase 0 (Foundation)**: Repository, DevOps, Database, Authentication.
*   **Phase 1 (Core Tenancy)**: Multi-tenancy, Admin, Users, Companies.
*   **Phase 2 (Pre-Interview)**: Resume/JD processing, Jobs, Drives, Invitations, Candidate.
*   **Phase 3 (Live Interview)**: AI provider layer, Realtime voice, Interview engine.
*   **Phase 4 (Post-Interview)**: Agents, Evaluation, Reports, Integrity, Email.
*   **Phase 5 (Hardening)**: Security, Observability, Testing.
*   **Future (Post-MVP)**: Coding interview, advanced integrations.

---

## 2. WORKSTREAMS (EPIC → FEATURE → USER STORY → TASK)

### EPIC 1: Infrastructure & Foundation (Workstreams 1, 4, 25)

**FEATURE: Project Scaffolding**
*   **USER STORY**: As an engineer, I want the base repository set up so I can start writing code.
    *   **TASK-FND-001**: Initialize FastAPI + Celery + Tailwind repository.
        *   **Description**: Create standard directory structure (`api`, `core`, `workers`, `frontend`).
        *   **Dependencies**: None
        *   **Files**: `pyproject.toml`, `docker-compose.yml`, `api/main.py`
        *   **AC**: `docker-compose up` starts API, Redis, and frontend.
        *   **Test**: Dummy pytest passes.

**FEATURE: Database Schema**
*   **USER STORY**: As a backend service, I need the database schema instantiated to store data.
    *   **TASK-DB-001**: Implement Alembic migrations for Core Schema.
        *   **Description**: Create tables for tenants, users, jobs, interviews (Implementation Spec v2.0).
        *   **Dependencies**: TASK-FND-001
        *   **Files**: `infrastructure/models.py`, `alembic/versions/`
        *   **AC**: Migrations run from empty DB to full schema successfully.
        *   **Test**: Migration upgrade/downgrade test.

### EPIC 2: Auth & Tenancy (Workstreams 2, 5, 6, 21)

**FEATURE: Identity Management**
*   **USER STORY**: As a company admin, I need to log in securely.
    *   **TASK-AUTH-001**: Integrate Clerk JWT verification.
        *   **Description**: Build FastAPI dependency to parse and validate Clerk JWTs.
        *   **Dependencies**: TASK-FND-001
        *   **Files**: `api/dependencies/auth.py`
        *   **AC**: Unauthorized requests return 401; valid JWTs attach user to `request.state`.
        *   **Test**: Unit test with mocked Clerk JWKS.

**FEATURE: Tenant Isolation**
*   **USER STORY**: As a client, I want my data completely isolated from other companies.
    *   **TASK-TEN-001**: Implement PostgreSQL Row-Level Security (RLS).
        *   **Description**: Add RLS policies for `tenant_id` on all customer tables.
        *   **Dependencies**: TASK-DB-001, TASK-AUTH-001
        *   **Files**: `alembic/versions/rls_migration.sql`, `core/db.py`
        *   **AC**: User from Tenant A cannot SELECT records from Tenant B.
        *   **Test**: DB integration tests using two tenant IDs.

### EPIC 3: Pre-Interview Workflows (Workstreams 7, 8, 9, 10, 11)

**FEATURE: Job & Resume Parsing**
*   **USER STORY**: As a recruiter, I want the system to extract competencies from a JD.
    *   **TASK-AI-001**: Implement GLiNER JD/Resume extraction.
        *   **Description**: Service to extract `skills` and `competencies` from uploaded text.
        *   **Dependencies**: TASK-FND-001
        *   **Files**: `core/services/extraction.py`
        *   **AC**: Returns structured JSON of competencies.
        *   **Test**: Assert extraction matches expected JSON schema.

**FEATURE: Drives & Invitations**
*   **USER STORY**: As a recruiter, I want to invite a candidate to a job drive.
    *   **TASK-INV-001**: Generate Candidate Guest JWT.
        *   **Description**: Create single-use token tied to `interview_id`.
        *   **Dependencies**: TASK-DB-001
        *   **Files**: `core/services/tokens.py`, `api/routers/invitations.py`
        *   **AC**: Token encodes `candidate_id` and `interview_id`.
        *   **Test**: Token signing and verification unit tests.

### EPIC 4: Realtime Interactive Plane (Workstreams 12, 13, 14)

**FEATURE: AI Provider Adapters**
*   **USER STORY**: As the engine, I need uniform interfaces to interact with Groq and Deepgram.
    *   **TASK-PROV-001**: Implement `ILLMProvider` for Groq.
        *   **Description**: Async streaming wrapper for Llama 3 8B.
        *   **Dependencies**: None
        *   **Files**: `realtime/providers/groq_adapter.py`
        *   **AC**: Yields string tokens asynchronously.
        *   **Test**: Mocked HTTP streaming test.

**FEATURE: WebRTC Gateway**
*   **USER STORY**: As a candidate, I need to connect my mic to the interview.
    *   **TASK-RTC-001**: LiveKit Room & Token Management.
        *   **Description**: API endpoint to mint LiveKit access tokens for authenticated sessions.
        *   **Dependencies**: TASK-AUTH-001
        *   **Files**: `api/routers/sessions.py`
        *   **AC**: Client successfully connects to LiveKit SFU.
        *   **Test**: LiveKit API mock test.

**FEATURE: Interview State Machine**
*   **USER STORY**: As the system, I must control the flow of the interview deterministically.
    *   **TASK-ENG-001**: Implement Core Python State Machine.
        *   **Description**: Code the transitions (INIT -> INTRO -> CORE -> DEEP_DIVE).
        *   **Dependencies**: TASK-DB-001
        *   **Files**: `core/engine/state_machine.py`
        *   **AC**: Invalid transitions throw `StateTransitionError`.
        *   **Test**: Exhaustive state transition unit tests.

### EPIC 5: Post-Interview Evaluation Plane (Workstreams 15, 16, 17, 18, 19)

**FEATURE: Async Evaluation Agents**
*   **USER STORY**: As a recruiter, I want the AI to score the candidate's transcript.
    *   **TASK-EVAL-001**: Implement TechnicalEvaluator NAT Agent.
        *   **Description**: Celery task triggering NVIDIA NAT logic against transcript.
        *   **Dependencies**: TASK-ENG-001, TASK-DB-001
        *   **Files**: `workers/tasks/evaluation.py`, `agents/technical.py`
        *   **AC**: Agent outputs valid `TechnicalEvaluatorOutput` JSON schema.
        *   **Test**: E2E test with dummy transcript.

**FEATURE: Reports & Emails**
*   **USER STORY**: As a recruiter, I want an email when the report is ready.
    *   **TASK-REP-001**: Generate PDF & Dispatch Email.
        *   **Description**: Compile agent outputs into a PDF report (R2) and trigger Resend email.
        *   **Dependencies**: TASK-EVAL-001
        *   **Files**: `workers/tasks/reports.py`, `core/services/email.py`
        *   **AC**: PDF saved to R2, signed URL generated, email queued.
        *   **Test**: Assert PDF generation logic and mock email API.

### EPIC 6: Cross-Cutting Concerns (Workstreams 22, 23, 24)

**FEATURE: Observability**
*   **USER STORY**: As a devops engineer, I need to trace errors across boundaries.
    *   **TASK-OBS-001**: Implement `X-Request-ID` middleware.
        *   **Description**: Pass correlation ID to logs, Celery, and LLM requests.
        *   **Dependencies**: TASK-FND-001
        *   **Files**: `api/middleware/tracing.py`
        *   **AC**: All logs contain trace ID.
        *   **Test**: API request test asserting log output.

**FEATURE: Security & Integrity**
*   **USER STORY**: As a company admin, I want to prevent prompt injection.
    *   **TASK-SEC-001**: Implement Llama Guard 3.
        *   **Description**: Filter candidate answers prior to LLM submission.
        *   **Dependencies**: TASK-PROV-001
        *   **Files**: `core/engine/security.py`
        *   **AC**: Prompt injections return standard block response without executing.
        *   **Test**: Benchmark dataset of known injections.

---

## 3. PARALLELIZABLE TASKS

Once **TASK-FND-001** and **TASK-DB-001** are complete, the following streams can be executed simultaneously by different engineers:
1.  **Frontend**: Build React/Tailwind components based on API specs.
2.  **Auth/Tenancy**: Implement RLS, Clerk, and Admin APIs.
3.  **Realtime/AI**: Build the Groq/Cartesia adapters and LiveKit connections.
4.  **Agents**: Write NVIDIA NAT prompts and async Celery workers.

---

## 4. BLOCKED TASKS

*   **TASK-ENG-001 (State Machine)** is blocked by **TASK-PROV-001 (LLM Adapters)** (needs classification functions).
*   **TASK-EVAL-001 (Evaluation)** is blocked by **TASK-ENG-001** (needs complete transcripts to parse).
*   **TASK-REP-001 (Reports)** is blocked by **TASK-EVAL-001** (needs scored outputs).

---

## 5. FUTURE BACKLOG (Post-MVP)

### EPIC: Coding Interview (Workstream 20)
*   **TASK-CODE-001**: Deploy Piston sandbox on isolated VPC.
*   **TASK-CODE-002**: Implement Monaco Editor WebSocket sync.
*   **TASK-CODE-003**: Build `execute_code` tool for the Realtime Interview Engine.

### EPIC: Enterprise Scaling
*   **TASK-ENT-001**: Database-per-tenant migration script.
*   **TASK-ENT-002**: SAML/SSO Integration via Clerk.
*   **TASK-ENT-003**: Native ATS Integrations (Greenhouse, Workday).
