# Local LLM & Classification Model Gap Analysis

**Date:** 2026-10-05  
**Local Model Available:** `D:\Projects\Large Language Models\qwen2.5-coder-1.5b-instruct-q4_k_m.gguf` (1.1 GB, Q4_K_M quantization)

---

## 1. Current Architecture: Cloud-Only LLM Providers

### Real-time Interview Pipeline (`realtime/agent_worker.py`, `realtime/voice_agent.py`)

| Component | Current Provider | Type | Latency Target |
|-----------|------------------|------|----------------|
| **LLM (Question Generation)** | Groq `llama3-8b-8192` | Cloud API | TTFT < 200ms |
| **LLM (Fallback)** | NVIDIA NIM `meta/llama-3.3-70b-instruct` | Cloud API | TTFT < 500ms |
| **STT** | Deepgram Nova-2 / HF Whisper-tiny | Cloud API | < 250ms |
| **TTS** | Cartesia Sonic / HF MMS-TTS | Cloud API | TTFA < 100ms |

### Async Evaluation Pipeline (`workers/tasks/evaluation.py`, `agents/orchestrator.py`)

| Agent | Current Provider | Type |
|-------|------------------|------|
| Technical Evaluator | Groq / NVIDIA NIM | Cloud API |
| Behavioral Evaluator | Groq / NVIDIA NIM | Cloud API |
| Communication Evaluator | Groq / NVIDIA NIM | Cloud API |

---

## 2. Local LLM Integration: MISSING

### What's Not Implemented

| Missing Piece | Status | Required Effort |
|---------------|--------|-----------------|
| `llama-cpp-python` dependency | ❌ Not in `requirements.txt` | Add to requirements |
| Local model config in `Settings` | ❌ No `LOCAL_MODEL_PATH`, `LOCAL_MODEL_N_GPU_LAYERS`, `LOCAL_MODEL_CTX_SIZE` | Add to `backend/config.py` |
| `LocalLLMProvider` class | ❌ No implementation | Create `backend/providers/local_llm_adapter.py` |
| Provider factory selection | ❌ Only `groq`/`nvidia`/`auto` | Extend `LLM_PROVIDER` enum in `agent_worker.py` |
| Model warmup/loading strategy | ❌ Not implemented | Add startup loading with progress |
| Quantization config | ❌ Hardcoded to Q4_K_M | Make configurable |
| GPU offload config | ❌ Not implemented | Add `n_gpu_layers` setting |

### Your Model: `qwen2.5-coder-1.5b-instruct-q4_k_m.gguf`

| Property | Value | Suitability |
|----------|-------|-------------|
| **Parameters** | 1.5B | ✅ Good for real-time (fast inference) |
| **Quantization** | Q4_K_M (4-bit) | ✅ Good quality/size tradeoff |
| **Context Window** | 32K (default) | ✅ Sufficient for interview context |
| **Specialization** | Code/Technical | ✅ Ideal for technical interviews |
| **Size** | 1.1 GB | ✅ Fits in CPU RAM, can offload to GPU |
| **License** | Apache 2.0 (Qwen) | ✅ Commercial use allowed |

### Estimated Performance (Local)

| Hardware | Expected TTFT | Throughput | Notes |
|----------|---------------|------------|-------|
| CPU only (modern 8-core) | ~150-300ms | ~15-25 tok/s | Good for async eval |
| CPU + GPU offload (8GB VRAM) | ~50-100ms | ~40-60 tok/s | Viable for real-time |
| Apple Silicon (M1/M2/M3) | ~80-150ms | ~30-50 tok/s | Metal acceleration |

---

## 3. Classification Model from HF: MISSING

### Required Classification Tasks

| Task | Purpose | Current Approach | HF Model Candidate |
|------|---------|------------------|---------------------|
| **Prompt Injection Detection** | Security filter for candidate answers | Regex only (`security.py`) | `microsoft/deberta-v3-base-prompt-injection` |
| **PII Detection** | Mask personal info in transcripts | None | `microsoft/presidio-analyzer` or `obi/deid_roberta_i2b2` |
| **Topic Classification** | Route to correct competency evaluator | Hardcoded first competency | `facebook/bart-large-mnli` (zero-shot) |
| **Sentiment/Confidence** | Assess candidate confidence level | None | `cardiffnlp/twitter-roberta-base-sentiment-latest` |
| **Language Detection** | Ensure English responses | None | `papluca/xlm-roberta-base-language-detection` |
| **Audio Quality Classification** | Flag poor audio before STT | None | `MIT/ast-finetuned-audioset-10-10-0.4593` |

### Current Security Filter Gap (`backend/core/engine/security.py`)

```python
# ONLY 9 regex patterns - easily bypassed
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions?",
    r"you\s+are\s+now\s+(in|a)\s+developer\s+mode",
    # ... 7 more basic patterns
]
```

**No semantic understanding** - cannot detect:
- Encoded/obfuscated injections
- Multi-turn social engineering
- Context-aware manipulation
- Adversarial suffixes

---

## 4. Implementation Roadmap

### Phase 1: Local LLM Provider (Week 1)

```python
# backend/providers/local_llm_adapter.py (NEW)
from llama_cpp import Llama
from backend.providers.llm_interface import ILLMProvider
from backend.config import settings

class LocalLLMProvider(ILLMProvider):
    def __init__(self):
        self.llm = Llama(
            model_path=settings.LOCAL_MODEL_PATH,
            n_gpu_layers=settings.LOCAL_MODEL_N_GPU_LAYERS,
            n_ctx=settings.LOCAL_MODEL_CTX_SIZE,
            n_threads=settings.LOCAL_MODEL_N_THREADS,
            verbose=False,
        )
    
    async def generate_response(self, prompt: str) -> str:
        # Run in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            lambda: self.llm(prompt, max_tokens=250, temperature=0.5)["choices"][0]["text"]
        )
```

### Phase 2: Classification Pipeline (Week 1-2)

```python
# backend/providers/classification_adapter.py (NEW)
from transformers import pipeline
from backend.config import settings

class ClassificationProvider:
    def __init__(self):
        self.prompt_injection_clf = pipeline(
            "text-classification",
            model="microsoft/deberta-v3-base-prompt-injection",
            device=settings.CLASSIFICATION_DEVICE  # "cuda" or "cpu"
        )
        self.pii_clf = pipeline(
            "token-classification",
            model="obi/deid_roberta_i2b2",
            aggregation_strategy="simple",
            device=settings.CLASSIFICATION_DEVICE
        )
        self.topic_clf = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=settings.CLASSIFICATION_DEVICE
        )
    
    async def check_prompt_injection(self, text: str) -> dict:
        result = await asyncio.get_event_loop().run_in_executor(
            None, self.prompt_injection_clf, text
        )
        return {"is_injection": result[0]["label"] == "INJECTION", "score": result[0]["score"]}
    
    async def detect_pii(self, text: str) -> list:
        return await asyncio.get_event_loop().run_in_executor(None, self.pii_clf, text)
    
    async def classify_competency(self, text: str, competencies: list) -> dict:
        return await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.topic_clf(text, candidate_labels=competencies)
        )
```

### Phase 3: Config Updates (Week 1)

```python
# backend/config.py - ADDITIONS
class Settings(BaseSettings):
    # ... existing ...
    
    # Local LLM Configuration
    LOCAL_MODEL_PATH: str = "D:/Projects/Large Language Models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"
    LOCAL_MODEL_N_GPU_LAYERS: int = 0  # -1 for all, 0 for CPU only
    LOCAL_MODEL_CTX_SIZE: int = 4096
    LOCAL_MODEL_N_THREADS: int = 8
    LOCAL_MODEL_N_BATCH: int = 512
    LOCAL_MODEL_USE_MLOCK: bool = True
    LOCAL_MODEL_USE_MMAP: bool = True
    
    # Classification Models
    CLASSIFICATION_DEVICE: str = "cpu"  # "cuda" for GPU
    PROMPT_INJECTION_MODEL: str = "microsoft/deberta-v3-base-prompt-injection"
    PII_DETECTION_MODEL: str = "obi/deid_roberta_i2b2"
    TOPIC_CLASSIFICATION_MODEL: str = "facebook/bart-large-mnli"
    
    # Provider Selection
    LLM_PROVIDER: str = "local"  # "groq", "nvidia", "local", "auto"
    AUDIO_PROVIDER: str = "hf"   # "deepgram", "cartesia", "hf", "auto"
```

### Phase 4: Requirements Update

```text
# requirements.txt - ADDITIONS
llama-cpp-python==0.2.90  # with GPU: llama-cpp-python[cuBLAS]
transformers==4.36.0
torch==2.1.0
accelerate==0.25.0
safetensors==0.4.1
# For GPU support on Windows:
# pip install llama-cpp-python --extra-index-url=https://abetlen.github.io/llama-cpp-python/whl/cu121
```

---

## 5. Architecture Decision: Where to Use Local vs Cloud

| Use Case | Recommended Provider | Rationale |
|----------|---------------------|-----------|
| **Real-time Question Generation** | Local (Qwen 1.5B) | Sub-200ms TTFT achievable; no API costs; privacy |
| **Async Technical Evaluation** | Local (Qwen 1.5B) or Cloud (70B) | Local for cost; Cloud for complex reasoning |
| **Async Behavioral/Communication Eval** | Cloud (70B) | Better nuance understanding |
| **Prompt Injection Detection** | Local (DeBERTa) | Must be sub-50ms; run inline |
| **PII Detection** | Local (RoBERTa) | Privacy - never send PII to cloud |
| **Topic Classification** | Local (BART) | Fast zero-shot; no API dependency |
| **STT** | Deepgram (Cloud) or HF Whisper (Local) | Deepgram better accuracy; Whisper local for privacy |
| **TTS** | Cartesia (Cloud) or HF MMS-TTS (Local) | Cartesia better quality; MMS-TTS for offline |

---

## 6. Cost Comparison (Monthly Estimate)

| Scenario | Cloud API Costs | Local Inference Cost |
|----------|-----------------|---------------------|
| 100 interviews/mo × 30 min | ~$150-300 (Groq + Deepgram + Cartesia) | $0 (hardware only) |
| 1,000 interviews/mo | ~$1,500-3,000 | $0 (hardware only) |
| **Break-even** | — | **~50 interviews** (GPU electricity) |

---

## 7. Risk Assessment

| Risk | Local LLM | Cloud API |
|------|-----------|-----------|
| **Latency variance** | Low (deterministic) | High (queueing, cold starts) |
| **Data privacy** | Full control | Vendor dependent |
| **Model quality** | Good for structured tasks | Better for open-ended reasoning |
| **Availability** | Hardware dependent | SLA backed |
| **Scaling** | Vertical (more GPUs) | Horizontal (auto-scale) |
| **Maintenance** | Model updates, driver mgmt | Zero ops |

---

## 8. Recommended Next Steps

1. **Add `llama-cpp-python` to requirements** with GPU variant for your hardware
2. **Create `LocalLLMProvider`** implementing `ILLMProvider`
3. **Add classification models** for security (prompt injection, PII)
4. **Update provider factory** in `agent_worker.py` to support `LLM_PROVIDER=local`
5. **Add config validation** at startup for local model path existence
6. **Benchmark** your Qwen 1.5B model on target hardware
7. **Implement hybrid routing**: Local for real-time, Cloud for complex eval

---

## 9. File Inventory for Implementation

### New Files Needed
```
backend/providers/
├── local_llm_adapter.py      # Local GGUF inference
├── classification_adapter.py # HF classification pipelines
└── __init__.py               # Export new providers
```

### Files to Modify
```
backend/config.py                    # Add local model + classification settings
backend/providers/__init__.py        # Export new providers
realtime/agent_worker.py             # Add local provider selection logic
realtime/voice_agent.py              # Add local provider selection logic
requirements.txt                     # Add llama-cpp-python, transformers, torch
backend/core/engine/security.py      # Replace regex with classification provider
```

---

## 10. Testing Checklist

- [ ] Local model loads successfully on target hardware
- [ ] TTFT < 200ms for real-time prompts
- [ ] Prompt injection detection catches known attack patterns
- [ ] PII detection masks emails, phones, names in transcripts
- [ ] Topic classification correctly routes to competencies
- [ ] Fallback to cloud provider when local fails
- [ ] Memory usage stable under concurrent interviews
- [ ] GPU memory doesn't OOM with multiple sessions