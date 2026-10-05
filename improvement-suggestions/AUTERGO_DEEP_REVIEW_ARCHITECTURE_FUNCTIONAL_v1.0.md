# AUTERGO DEEP REVIEW — Architecture + Functional v1.0

> Date: 2026-10-05 | Scope: full repo (`backend/`, `agents/`, `realtime/`, `workers/`, `database/`, `frontend/`) vs `AUTERGO_ARCHITECTURE_BASELINE_v2.0.md`, `AUTERGO_HLD_LLD_v1.0.md`
> Model policy enforced here: **cloud-first, local-last**; **classification = local HF weights, never HF Inference API**.

---

## 1. Architecture Review

### 1.1 Two-plane separation — COMPLIANT
Baseline v2.0 mandates Interactive (sub-500ms) vs Evaluation (async) planes. Code matches:
- Interactive: `realtime/voice_agent.py`, `realtime/agent_worker.py` → LiveKit + Silero VAD + Deepgram STT → Groq direct → Cartesia TTS. No NAT, no OpenRouter in hot path. Correct per ADR-016/017.
- Evaluation: `workers/tasks/evaluation.py` → `agents/orchestrator.py` (Technical/Behavioral/Communication, `asyncio.gather`) → persist → `workers/tasks/reports.py`. Async-only. Correct.
- State: `backend/core/engine/state_machine.py` is pure deterministic Python (INIT→…→COMPLETE, invalid transition raises `StateTransitionError`). No LLM in transition logic. Correct per ADR-017.

### 1.2 Realtime voice budget — MOSTLY COMPLIANT, 1 GAP
Spec budget: VAD+STT 200ms + Logic 50ms + LLM TTFT 250ms + TTS TTFA 100ms = ~600ms (HLD says 500ms target, LLD admits 600ms).
- `backend/providers/groq_adapter.py`: `httpx` timeout 2.0s, model `llama3-8b-8192`. Good for TTFT.
- `backend/providers/cartesia_adapter.py` / `deepgram_adapter.py`: direct APIs, correct.
- **Gap**: `backend/providers/hf_audio_adapter.py` still POSTs to `https://api-inference.huggingface.co/models/...` for STT/TTS. That endpoint is cold-start heavy (seconds) and breaks the realtime budget. It must stay as **dev/test fallback only**, never in `AUDIO_PROVIDER=auto` production path when Deepgram/Cartesia keys exist. Current factory (`get_stt_provider`/`get_tts_provider`) already prefers Deepgram/Cartesia when keys are real — keep that, document it (see §3).

### 1.3 DB / Redis — COMPLIANT with 1 BUG RISK
- ADR-018 (Redis for transient, Postgres flush once/turn) is reflected in design; `transcript_json` JSONB approach matches Baseline §7.
- Pool tuning exists (`backend/config.py`: `DB_POOL_SIZE=20`, `DB_MAX_OVERFLOW=10`, `DB_POOL_PRE_PING=True`). Good vs POC-10 exhaustion.
- **Risk**: `workers/tasks/evaluation.py:111` references `Candidate` without import (`select(Candidate)` → `NameError` at runtime when `candidate_id` set). Fix: `from database.models import Candidate` or lazy import alongside `Interview, Evaluation, AgentRun, Job, User`.

### 1.4 Security / Integrity — COMPLIANT, DEFENSE-IN-DEPTH PRESENT
- `backend/core/engine/security.py` (`LlamaGuardSecurity`): deterministic regex (11 injection patterns + blocked code keywords) → optional semantic (HF local classifier ≥0.70 → Groq `llama-guard-3-8b`) → PII mask → control-char strip. Correct layering.
- Vision downgrade (0.2 FPS bbox-only, ADR-019) matches Baseline §9. Browser focus/blur/clipboard + async diarization deferred — correct.
- Multi-tenancy: shared-schema + `tenant_id` + RLS (HLD §3). `setup_rls.py` exists; verify RLS enabled on every tenant table in migration.

### 1.5 Deployment — COMPLIANT
Cloud Run (API/workers) + LiveKit Cloud SFU + Neon (pooled) + Upstash Redis + R2. Matches Baseline §10. No action.

---

## 2. Functional Review (module-by-module)

| Module | Location | Verdict | Notes |
|---|---|---|---|
| Auth (Clerk + Guest JWT) | `backend/api/v1/`, `backend/core/services/tokens.py`, `backend/dependencies/` | ✅ Pass | Clerk JWKS + HMAC guest path both present. Ensure all `/api/v1/` routers enforce one of the two. |
| Tenant / RLS | `database/models.py`, `setup_rls.py` | ⚠️ Verify | Model-level `tenant_id` present; confirm RLS policy per table, plus `DB_ECHO=False` in prod. |
| Job / JD parsing (GLiNER) | `backend/core/services/extraction.py`, `resume_parser.py` | ✅ Pass | `gliner>=0.2.12` in requirements. Confirm lazy-load so API cold start unaffected. |
| Interview template/sequence | `backend/api/v1/`, `database/models.py` | ✅ Pass | CRUD present. |
| Session / LiveKit tokens | `backend/api/v1/` (`POST /sessions/{id}/join`) | ✅ Pass | Returns LiveKit token; webhook `POST /webhooks/livekit` handles join/leave. |
| Realtime Engine (STT→LLM→TTS, barge-in) | `realtime/`, `backend/providers/*_adapter.py` | ✅ Pass | Cascade correct; interruption (>300ms VAD → `cancel()` Cartesia → `[INTERRUPTED]` → flush Redis→LLM) per Baseline §6. |
| State machine | `backend/core/engine/state_machine.py` | ✅ Pass | Strict, tested transitions; `advance()` / `complete_all()` / `build_state_change_event()` match Spec §4 WS contract. |
| Evaluators (Tech/Behav/Comm) | `agents/technical.py`, `behavioral.py`, `communication.py` | ✅ Pass | Structured JSON prompts + regex-extract + deterministic heuristic fallback. Weights 50/25/25 in `agents/orchestrator.py:39-44`, thresholds PASS≥75 / HOLD≥60 correct. |
| Integrity scoring | `workers/tasks/evaluation.py:92-98` | ✅ Pass | `base − high*pen − med*pen`, calibrated via `INTEGRITY_*` settings. Zero hardcoded magic. |
| Reports + Email | `workers/tasks/reports.py`, `backend/core/services/pdf_generator.py`, `email.py` | ✅ Pass | PDF via reportlab; SMTP primary + Resend fallback correct. |
| Storage (R2) | `backend/core/services/storage.py` | ✅ Pass | S3-compat via boto3. Confirm presigned-URL expiry for resumes/reports. |
| Frontend | `frontend/` | ➖ Out of scope | Redesign plan exists (`docs/06-Frontend-Redesign-Plan.md`); not audited here. |

**Functional gaps (ranked):**
1. `Candidate` NameError (§1.3) — P0, one-line import fix.
2. `OpenRouterProvider` (`backend/providers/openrouter.py`) and `xAIProvider` (`backend/providers/xai.py`) are stubs (`"openrouter_stub"` / `"xai_stub"`). Either implement or remove from routing docs so Evaluation Plane doesn't silently score on stubs. ponytail: delete if unused; don't build abstraction around stubs.
3. `HuggingFaceProvider.generate_response` (`backend/providers/huggingface.py:10`) returns hardcoded string — must never be in LLM routing chain. It isn't (factory only uses Groq/NVIDIA/Local) — keep it that way.

---

## 3. Model Routing Policy — LOCAL IS LAST (enforced)

### 3.1 LLM fallback chain (each falls back to the next, local terminal)

```
Groq (llama3-8b-8192, timeout 2s, realtime + default eval)
  → NVIDIA NIM (meta/llama-3.3-70b-instruct, timeout 10s, deep eval)
    → Local GGUF (llama-cpp-python, Qwen2.5-Coder-1.5B Q4_K_M, ctx 4096)
      → deterministic stub (no further hop, never loops back to cloud)
```

- `backend/providers/__init__.py:get_llm_provider` — `auto` now resolves **Groq (if `GROQ_API_KEY`) → NVIDIA (if `NVIDIA_API_KEY`) → Local (if `LocalLLMProvider.is_available()`) → Groq stub**. Explicit `preferred_provider="local"|"groq"|"nvidia"` still honored for tests/jobs.
- `backend/providers/local_llm_adapter.py:LocalLLMProvider` — on inference exception returns a generic follow-up stub. ponytail: terminal fallback returns stub instead of chaining back to Groq (avoids cloud↔local loop, keeps offline usable).
- `LocalLLMProvider.is_available()` = GGUF path exists on disk AND `llama_cpp` importable. Config: `LOCAL_MODEL_PATH`, `N_GPU_LAYERS=0` (CPU default), `N_CTX=4096`, `N_THREADS=8` in `backend/config.py:67-73`.
- Rationale: cloud models win on quality + TTFT for realtime; local 1.5B GGUF is for zero-cost/offline continuity only. Previous order (local-first) is reversed as of this review.

| Task | Primary | Fallback 1 | Last resort |
|---|---|---|---|
| Realtime Q&A | Groq direct | NVIDIA NIM | Local GGUF → stub |
| Deep evaluation | Groq / NVIDIA (per job config) | NVIDIA / Groq | Local GGUF → heuristic JSON in agent (`agents/technical.py:73-80` etc.) |
| Guardrail LLM (`llama-guard-3-8b`) | Groq | skip (fail-open to regex+HF local) | — |

### 3.2 Classification — LOCAL HF WEIGHTS, NEVER HF INFERENCE API

`backend/providers/classification_adapter.py:ClassificationProvider` loads **local open-weights via `transformers.pipeline` from the HF Hub snapshot cache** — zero network inference calls:

- Prompt injection: `microsoft/deberta-v3-base-prompt-injection` → `pipeline("text-classification")`, truncation to 512 chars, `run_in_executor` (non-blocking), threshold ≥0.70 in `security.py:61`. Gated by `ENABLE_HF_CLASSIFIERS`; when off/tests → fast regex pre-check.
- Competency/topic: `facebook/bart-large-mnli` → `pipeline("zero-shot-classification")`; when off/tests → keyword-overlap fallback.
- PII: regex fast-path (email/phone/credential) in `mask_pii()` / `detect_pii()` — no model download, no API. ponytail: `PII_DETECTION_MODEL` (`obi/deid_roberta_i2b2`) is config-listed but intentionally NOT loaded — regex covers the compliance need at zero cost; load NER only if a future audit demands span-level entities.
- **Explicit non-goal**: no `POST api-inference.huggingface.co` anywhere in this path. `HF_API_TOKEN` / `HF_WHISPER_MODEL` are for **audio adapters only** (`hf_audio_adapter.py`), never classification. No `HF_TOKEN` required for classification once weights are cached (`HF_HUB_OFFLINE=1` works).

To pre-warm offline cache: `python -c "from transformers import pipeline; pipeline('text-classification', model='microsoft/deberta-v3-base-prompt-injection'); pipeline('zero-shot-classification', model='facebook/bart-large-mnli')"` then ship the HF cache with the image.

---

## 4. Decisions / Action Items

- [ ] P0: fix `Candidate` import in `workers/tasks/evaluation.py`.
- [ ] P1: decide OpenRouter/xAI stubs — implement or delete; update Provider Strategy table (Baseline §8) accordingly.
- [ ] P1: keep `AUDIO_PROVIDER=auto` preferring Deepgram/Cartesia when keys are real; HF Whisper/MMS-TTS stays dev-fallback only (latency).
- [ ] P2: pre-warm HF classifier weights into Docker image; set `ENABLE_HF_CLASSIFIERS=true` in staging, measure CPU delta before prod rollout.

<!-- GOAL_COMPLETE -->
