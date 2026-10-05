# Architecture Flaws - Autergo AI Interview System

**Date:** 2026-10-05  
**Review Type:** Full Application Architecture Review  
**Total Issues:** 15 (4 Critical, 5 High, 4 Medium, 2 Low)

---

## Critical Severity (Fix Immediately)

### 1. In-Memory Session State Not Scalable
**Location:** `backend/api/v1/realtime.py:43-57, 59-98`  
**Issue:** Session context stored in global `Dict[str, RealtimeSessionContext]` with optional Redis sync (fire-and-forget, no consistency).  
**Impact:** Cannot scale horizontally; session loss on pod restart; race conditions.  
**Fix:** Use Redis as primary session store with atomic operations and TTL; remove in-memory dict entirely.

### 2. Duplicate State Machine Logic in 4 Places
**Locations:**  
- `backend/core/engine/state_machine.py` (canonical)
- `backend/api/v1/realtime.py:30-40` (`NEXT_STATE_MAP`)
- `realtime/voice_agent.py:92-102` (`next_states`)
- `realtime/agent_worker.py:93-103` (`next_states`)

**Impact:** Violates DRY; any state change requires 4 edits; high divergence risk.  
**Fix:** Single source of truth in `state_machine.py`; expose transitions as importable constant.

### 3. Row-Level Security Not Enforced Despite Architecture Claims
**Location:** `backend/dependencies/db.py:12` sets `SET LOCAL app.current_tenant` but no RLS policies exist in migrations.  
**Impact:** Multi-tenant isolation claimed but not implemented; data leakage risk.  
**Fix:** Add migration with `CREATE POLICY` statements for all tenant-scoped tables; add integration tests verifying isolation.

### 4. Silent Mock Fallbacks Mask Configuration Issues
**Location:** `backend/providers/groq_adapter.py:12-21` and similar in other adapters.  
**Issue:** Returns hardcoded mock responses if API keys missing or in test env - no startup validation.  
**Impact:** Production deploys with missing keys silently return fake data.  
**Fix:** Fail-fast at startup for required keys; separate test mocks from production code paths.

---

## High Severity (Fix This Sprint)

### 5. Synchronous LLM Calls in Hot Path Without Timeout
**Locations:** `realtime/agent_worker.py:127`, `realtime/voice_agent.py:120`  
```python
ai_reply = await self.llm.generate_response(prompt)  # No timeout, no streaming
```
**Impact:** Single slow LLM call stalls entire interview; no circuit breaker; blocks event loop.  
**Fix:** Wrap with `asyncio.wait_for(..., timeout=2.0)`; implement streaming TTS overlap.

### 6. Celery Async-in-Sync Anti-Pattern
**Location:** `workers/tasks/evaluation.py:139-154`  
Manual event loop management breaks Python 3.12+; no proper async task support.  
**Fix:** Use Celery 5.3+ native async tasks (`@celery_app.task(..., async=True)`) or move to FastAPI background tasks.

### 7. Security Filter is Regex-Only (Insufficient)
**Location:** `backend/core/engine/security.py:17-26` - Only 9 regex patterns.  
**Impact:** Easily bypassed; no semantic analysis; "Llama Guard 3" in name only.  
**Fix:** Integrate actual Llama Guard 3 model or dedicated guardrail service (e.g., NVIDIA NeMo Guardrails).

### 8. No Observability on Real-time Pipeline
**Location:** Prometheus `/metrics` exists but no custom metrics for:  
- STT/LLM/TTS latency percentiles (p50, p95, p99)  
- WebSocket connection health (active, errors, reconnects)  
- Interview completion/failure rates  
- Queue depths  

**Fix:** Add `prometheus_client.Histogram` and `Counter` metrics at each pipeline stage.

### 9. No Dead Letter Queue for Failed Evaluations
**Location:** `workers/tasks/evaluation.py` - Celery tasks retry but no DLQ.  
**Impact:** Lost interviews if evaluation crashes after `delay()`.  
**Fix:** Configure Celery DLQ with `task_acks_late=True`, `task_reject_on_worker_lost=True`, and dead letter exchange.

---

## Medium Severity (Fix Next Sprint)

### 10. Database Engine Created Per Import
**Location:** `database/session.py:5`  
```python
engine = create_async_engine(settings.DATABASE_URL, echo=True)
```
**Issues:** Module-level creation; `echo=True` logs all SQL (production perf hit); no pool tuning.  
**Fix:** Lazy initialization; configurable pool size (`pool_size`, `max_overflow`); `echo` from settings.

### 11. No Database Migration Strategy for Production
**Evidence:** Alembic configured but no migration testing in CI; no rollback procedures documented.  
**Risk:** Schema drift in production; no zero-downtime migration plan.  
**Fix:** Add migration test to CI; document rollback procedure; use expand/contract pattern for schema changes.

### 12. Arbitrary Integrity Scoring Formula
**Location:** `workers/tasks/evaluation.py:90-92`  
```python
integrity = max(0.0, round(1.0 - (high_count * 0.15) - (med_count * 0.05), 2))
```
**Issues:** Magic numbers; no calibration; severity definitions unclear.  
**Fix:** Configurable weights via settings; evidence-based calibration; audit trail for score changes.

### 13. Race Condition in Session Cleanup
**Location:** `backend/api/v1/realtime.py:294-297`  
```python
finally:
    active_sessions.pop(session_id, None)
```
No cleanup of Redis session data on disconnect; orphaned keys accumulate.  
**Fix:** Use Redis TTL as primary expiry; add explicit cleanup on WebSocket disconnect.

---

## Low Severity (Technical Debt)

### 14. Frontend Has No Auth State Management
**Location:** `frontend/src/App.jsx` - Routes have no auth guards; no token refresh; no Clerk React SDK integration.  
**Fix:** Add Clerk provider; protected routes; token auto-refresh.

### 15. Type Safety Gaps
**Evidence:** `Any` used extensively in `agent_worker.py` entrypoint; no strict mypy config; JSONB columns lack Pydantic models.  
**Fix:** Enable strict mypy; add Pydantic models for all JSONB columns; replace `Any` with proper types.

---

## Summary by Component

| Component | Critical | High | Medium | Low |
|-----------|----------|------|--------|-----|
| Real-time Pipeline | 2 | 3 | 1 | - |
| Session Management | 1 | - | 1 | - |
| Database/RLS | 1 | - | 1 | - |
| AI Providers | 1 | 1 | - | - |
| Celery/Workers | - | 2 | - | - |
| Security | - | 1 | - | - |
| Observability | - | 1 | - | - |
| Frontend | - | - | - | 1 |
| Type Safety | - | - | - | 1 |

---

## Recommended Fix Order

1. **Session Store** → Redis-only with atomic ops
2. **State Machine** → Single source of truth, remove duplicates
3. **LLM Timeout** → Add `asyncio.wait_for(..., timeout=2.0)` everywhere
4. **Security** → Replace regex filter with actual Llama Guard 3
5. **RLS** → Add migration with `CREATE POLICY` + test coverage
6. **Celery** → Migrate to native async tasks
7. **Startup Validation** → Fail fast on missing API keys
8. **Observability** → Custom Prometheus metrics for pipeline
9. **DLQ** → Configure Celery dead letter exchange
10. **DB Engine** → Lazy init, pool tuning, configurable echo
11. **Migration Strategy** → CI integration + rollback docs
12. **Integrity Scoring** → Configurable weights + calibration
13. **Session Cleanup** → Redis TTL + explicit disconnect cleanup
14. **Frontend Auth** → Clerk provider + protected routes
15. **Type Safety** → Strict mypy + Pydantic for JSONB