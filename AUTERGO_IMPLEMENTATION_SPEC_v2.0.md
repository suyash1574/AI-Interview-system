# AUTERGO IMPLEMENTATION SPECIFICATION v2.0

## 1. BACKEND MODULE SPECIFICATIONS

| Module | Core Responsibilities |
| :--- | :--- |
| **Auth** | Clerk token verification, JWT issuance for guest candidates. |
| **Tenancy** | RLS enforcement, Company settings, billing tier limits. |
| **Users** | User profiles, role assignments (Super Admin, Company Admin). |
| **Jobs / Drives** | JD parsing, job definitions, recruitment drive batches. |
| **Interviews** | Interview templates, session configuration, state tracking. |
| **Sessions (Realtime)** | LiveKit room management, WebSocket signaling, transient state (Redis). |
| **Evaluations** | Triggering NAT agents, storing evidence, calculating final scores. |
| **Integrity** | Receiving browser telemetry, server-side audio anomaly processing. |
| **Reports** | Aggregating evaluations into structured JSON and PDF formats. |

---

## 2. DATABASE SPECIFICATION (PostgreSQL)

**Schema: `public` (Shared Schema + RLS)**

| Table | Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `tenants` | `id` | UUID | PK, Default `uuid_generate_v4()` | Company identifier |
| | `name` | VARCHAR | Not Null | Company name |
| `users` | `id` | UUID | PK | User identifier |
| | `tenant_id` | UUID | FK -> `tenants(id)` | RLS enforced |
| | `role` | VARCHAR | Not Null | `SUPER_ADMIN`, `COMPANY_ADMIN`, `RECRUITER` |
| `jobs` | `id` | UUID | PK | Job identifier |
| | `tenant_id` | UUID | FK -> `tenants(id)` | RLS enforced |
| | `title` | VARCHAR | Not Null | Job title |
| | `competencies`| JSONB | Not Null | Extracted competencies |
| `interviews` | `id` | UUID | PK | Interview instance |
| | `tenant_id` | UUID | FK -> `tenants(id)` | RLS enforced |
| | `job_id` | UUID | FK -> `jobs(id)` | Link to job |
| | `candidate_id`| UUID | FK -> `candidates(id)` | Link to candidate |
| | `status` | VARCHAR | Not Null | `PENDING`, `IN_PROGRESS`, `COMPLETED` |
| | `transcript` | JSONB | Nullable | Final conversation array |
| `evaluations` | `id` | UUID | PK | Evaluation instance |
| | `interview_id`| UUID | FK -> `interviews(id)` | Link to interview |
| | `score_raw` | INTEGER | Nullable | 1-100 score |
| | `evidence` | JSONB | Nullable | List of transcript refs |

---

## 3. API SPECIFICATION (/api/v1/)

**Global Constraints:**
- **Auth**: Bearer token (Clerk JWT or Guest JWT).
- **Rate Limit**: 100 req/min per IP/User (Redis rate limiter).

### `POST /api/v1/interviews/{id}/session`
* **Auth**: Guest JWT (Candidate).
* **Request**: Empty.
* **Response**: `{"livekit_token": "string", "ws_url": "string", "session_id": "uuid"}`
* **Errors**: `401 Unauthorized`, `404 Not Found`, `409 Conflict (Session already active)`

### `POST /api/v1/jobs`
* **Auth**: Clerk JWT (Company Admin/Recruiter).
* **Request**: `{"title": "string", "description_text": "string"}`
* **Response**: `{"id": "uuid", "competencies": [...]}`
* **Idempotency**: Use `Idempotency-Key` header.

### `POST /api/v1/evaluations/report`
* **Auth**: Clerk JWT (Company Admin/Recruiter).
* **Request**: `{"interview_id": "uuid"}`
* **Response**: `202 Accepted` (Triggers Celery background task).

---

## 4. REALTIME SPECIFICATION

**Transport:** WebSocket (for signaling/text) + WebRTC (for audio via LiveKit).

**WebSocket Message Schemas (JSON):**

*   **Client -> Server (Interrupt)**
    `{"type": "interrupt", "timestamp": 1700000000}`
*   **Server -> Client (Transcript Partial)**
    `{"type": "transcript_partial", "speaker": "CANDIDATE", "text": "I think the best way..."}`
*   **Server -> Client (State Change)**
    `{"type": "state_change", "new_state": "DEEP_DIVE", "competency": "System Design"}`
*   **Server -> Client (Error)**
    `{"type": "error", "code": "RATE_LIMIT", "message": "Provider threshold reached"}`

**Reconnect Protocol:**
If disconnected, Client reconnects with `?session_id=UUID`. Server fetches transient state from Redis. If `state == IN_PROGRESS`, Server re-emits last 5 transcript messages and resumes WebRTC audio track.

---

## 5. AI INTERFACE CONTRACTS

```python
from abc import ABC, abstractmethod
from typing import AsyncGenerator

class ILLMProvider(ABC):
    @abstractmethod
    async def generate_stream(self, prompt: list[dict], max_tokens: int) -> AsyncGenerator[str, None]:
        pass
    
    @abstractmethod
    async def generate_structured(self, prompt: list[dict], schema: dict) -> dict:
        pass

class ISTTProvider(ABC):
    @abstractmethod
    async def stream_audio_in(self, audio_chunk: bytes):
        pass
    
    # Emits partial/final transcripts
    @abstractmethod
    async def transcript_events(self) -> AsyncGenerator[dict, None]:
        pass

class ITTSProvider(ABC):
    @abstractmethod
    async def stream_text_in(self, text_chunk: str):
        pass
    
    # Emits PCM audio bytes
    @abstractmethod
    async def audio_events(self) -> AsyncGenerator[bytes, None]:
        pass
```

---

## 6. AGENT I/O SCHEMAS

### TechnicalEvaluatorAgent
**Input:**
```json
{
  "interview_id": "uuid",
  "competency": "string",
  "transcript_snippets": [{"role": "candidate", "text": "..."}]
}
```
**Output:**
```json
{
  "score": 85,
  "confidence_score": 0.92,
  "evidence": [
    {"quote": "Candidate mentioned connection pooling", "relevance": "High"}
  ],
  "missing_knowledge": ["Did not mention transaction isolation"],
  "strength": "Strong practical database knowledge"
}
```

---

## 7. PROMPT SPECIFICATIONS

**Format**: Managed in code as versioned constants (e.g., `PROMPTS_V1_0`).

**Interviewer Prompt (`v1.0.0-interviewer`)**:
```text
You are Autergo, an expert technical interviewer.
Context: Job: {job_title}. Competency: {competency}.
Current State: {interview_state}.
Candidate's last response: {candidate_response}

Instructions:
1. Acknowledge the response naturally (max 1 sentence).
2. If evidence is missing, ask a specific drill-down question.
3. Keep your total response under 40 words.
4. Do NOT say "As an AI".
```

---

## 8. EVENT CONTRACTS

**Pub/Sub (Redis) & Celery:**

*   `interview.completed`
    *   Payload: `{"interview_id": "uuid", "tenant_id": "uuid", "timestamp": "ISO8601"}`
*   `integrity.event.detected`
    *   Payload: `{"session_id": "uuid", "event_type": "MULTIPLE_FACES", "confidence": 0.95}`

---

## 9. ERRORS

**Standardized Error Payload (RFC 7807 Problem Details format):**
```json
{
  "type": "https://api.autergo.com/errors/resource-not-found",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "The interview session '1234' does not exist or has expired.",
  "instance": "/api/v1/interviews/1234/session",
  "trace_id": "req-xyz-789"
}
```

---

## 10. CONFIGURATION

**Environment Variables (`.env`)**
```env
# Application
ENV=production # development | testing | staging | production
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:pass@ep-rest-of-url.neon.tech/neondb?options=project%3D...

# Redis
REDIS_URL=rediss://default:pass@upstash-url...

# AI Providers
GROQ_API_KEY=gsk_...
DEEPGRAM_API_KEY=dg_...
CARTESIA_API_KEY=car_...
OPENROUTER_API_KEY=sk-or-v1-...

# LiveKit
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
LIVEKIT_URL=wss://...
```

---

## 11. OBSERVABILITY

*   **Correlation IDs**: Every incoming API request receives an `X-Request-ID`. This ID is passed to Celery workers, LiveKit Webhooks, and LLM Gateway requests.
*   **AI Telemetry**: Logged to `usage_records` table: `{"interview_id": "...", "provider": "groq", "model": "llama-3-8b", "prompt_tokens": 120, "completion_tokens": 45, "cost_usd": 0.0001}`
*   **Latency Metrics**: Emitted to Grafana via OpenTelemetry middleware:
    *   `autergo_stt_latency_ms`
    *   `autergo_llm_ttft_ms`
    *   `autergo_tts_ttfa_ms`

---

## 12. SECURITY IMPLEMENTATION

*   **API Security**:
    *   `FastAPI` Depends on `verify_clerk_token` or `verify_guest_token`.
    *   CORS restricted to `['https://app.autergo.com', 'https://interview.autergo.com']`.
*   **Tenant Isolation**:
    *   PostgreSQL RLS Policy: `CREATE POLICY tenant_isolation ON users USING (tenant_id = current_setting('app.current_tenant')::uuid);`
*   **Prompt Injection**:
    *   System prompts enclosed in specialized delimiters.
    *   Candidate inputs scrubbed of standard delimiter sequences before appending to the context window.
