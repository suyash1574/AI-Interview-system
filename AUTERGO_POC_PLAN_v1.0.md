# AUTERGO POC IMPLEMENTATION & VALIDATION PLAN

This document outlines the design, implementation code, and validation matrix for the 10 critical Proof-of-Concepts (POCs) required before full platform development.

---

## POC 1 — REALTIME VOICE

**Objective**: Validate the end-to-end latency and stability of the WebRTC (microphone) → VAD → STT (Deepgram) → LLM → TTS (Cartesia) → Speaker pipeline.

**Implementation (Python Async Stub)**:
```python
import asyncio
import time

async def simulate_voice_loop():
    start_time = time.time()
    
    # 1. VAD / Microphone (Simulated WebRTC chunk)
    await asyncio.sleep(0.05) # 50ms VAD delay
    
    # 2. STT (Deepgram WebSocket)
    stt_start = time.time()
    await asyncio.sleep(0.25) # 250ms STT delay
    stt_latency = time.time() - stt_start
    
    # 3. LLM (OpenRouter Llama 3)
    llm_start = time.time()
    await asyncio.sleep(0.30) # 300ms Time-To-First-Token
    llm_latency = time.time() - llm_start
    
    # 4. TTS (Cartesia WebSocket)
    tts_start = time.time()
    await asyncio.sleep(0.10) # 100ms Time-To-First-Audio
    tts_latency = time.time() - tts_start
    
    total_latency = time.time() - start_time
    print(f"STT: {stt_latency:.2f}s | LLM TTFT: {llm_latency:.2f}s | TTS TTFA: {tts_latency:.2f}s | Total TAT: {total_latency:.2f}s")

# Execute: asyncio.run(simulate_voice_loop())
```

**Metric**: STT latency, LLM TTFT, TTS TTFA, Total Turn-Around Time (TAT), Interruption response time.
**Target**: Total TAT < 800ms. Interruption halt < 200ms.
**Observed result**: [Pending Execution with API Keys]
**Pass/Fail**: [Pending]
**Limitation**: Network jitter and real-world audio quality can degrade STT and TTS speeds.
**Decision**: [Pending]

---

## POC 2 — ADAPTIVE INTERVIEW

**Objective**: Verify the engine dynamically shifts questions based on candidate answer quality.

**Implementation**:
```python
def generate_next_question(jd, resume, current_competency, previous_q, candidate_a):
    prompt = f"""
    Context: JD: {jd}, Resume: {resume}
    Competency: {current_competency}
    Previous Q: {previous_q}
    Candidate Answer: {candidate_a}
    Task: Classify answer (Weak, Strong, Ambiguous, Incorrect). If Weak/Incorrect, drill down. If Strong, move on. Generate next question.
    """
    # mock_llm_call(prompt)
    return {"classification": "Weak", "next_action": "Drill_Down", "question": "Can you explain the specific error you encountered?"}
```

**Metric**: Appropriateness of the next question type (drill-down vs. progression).
**Target**: 100% adherence to deterministic routing based on LLM classification.
**Observed result**: [Pending Execution]
**Pass/Fail**: [Pending]
**Limitation**: Subjective evaluation of what constitutes a "Strong" vs "Ambiguous" answer by the LLM.
**Decision**: [Pending]

---

## POC 3 — RESUME + JD

**Objective**: Measure structured data extraction quality from unstructured PDFs.

**Implementation**:
```python
# Utilizing GLiNER for zero-shot NER
from gliner import GLiNER
model = GLiNER.from_pretrained("urchade/gliner_multi-v2.1")
text = "Senior Backend Engineer with 5 years of Python and FastAPI experience."
labels = ["job_title", "years_experience", "skills"]
entities = model.predict_entities(text, labels)
print(entities)
```

**Metric**: Precision and Recall of extracted skills, roles, and required competencies.
**Target**: >90% precision on skill extraction.
**Observed result**: [Pending Execution]
**Pass/Fail**: [Pending]
**Limitation**: Highly stylized resumes may break standard text extraction pipelines.
**Decision**: [Pending]

---

## POC 4 — MULTI-AGENT

**Objective**: Evaluate if NVIDIA NAT orchestration provides value over standard deterministic function calling for the evaluation pipeline.

**Implementation**:
```yaml
# NVIDIA NAT Minimal config
name: InterviewOrchestrator
agents:
  - name: TechnicalEvaluator
    model: gpt-4o-mini
    tools: [extract_evidence]
  - name: EvidenceAggregator
    model: claude-3-5-sonnet
    tools: [calculate_final_score]
```

**Metric**: Time-to-implement, runtime overhead (latency), and reasoning quality.
**Target**: Orchestration overhead < 2s; superior reasoning compared to single zero-shot prompt.
**Observed result**: [Pending Execution]
**Pass/Fail**: [Pending]
**Limitation**: Adds architectural complexity and potential failure points.
**Decision**: [Pending]

---

## POC 5 — EVALUATION

**Objective**: Generate an evidence-based score strictly tied to a rubric.

**Implementation**:
```python
def evaluate_response(question, answer, rubric):
    # LLM outputs structured JSON
    return {
        "score": 85,
        "confidence": 0.9,
        "evidence": "Candidate explicitly mentioned connection pooling.",
        "strength": "Strong database fundamentals.",
        "weakness": "Did not mention transaction isolation levels."
    }
```

**Metric**: Score consistency across 3 repeated runs of the same answer.
**Target**: Score variance <= 5 points.
**Observed result**: [Pending Execution]
**Pass/Fail**: [Pending]
**Limitation**: LLM may hallucinate evidence not explicitly present in the transcript.
**Decision**: [Pending]

---

## POC 6 — INTEGRITY

**Objective**: Assess client-side (MediaPipe) and server-side cheating detection signals.

**Implementation**:
```javascript
// Browser-side MediaPipe (JS) stub
import { FaceLandmarker } from '@mediapipe/tasks-vision';
function analyzeFrame(videoElement) {
    const faces = faceLandmarker.detect(videoElement);
    if (faces.length > 1) {
        sendTelemetry({ event: "MULTIPLE_FACES_DETECTED", timestamp: Date.now() });
    }
}

// Browser API checks
window.addEventListener('blur', () => sendTelemetry({ event: "TAB_SWITCHED" }));
document.addEventListener('paste', () => sendTelemetry({ event: "COPY_PASTE" }));
```

**Metric**: Precision of detections, False Positive Rate, CPU usage.
**Target**: CPU usage < 15%, False Positives < 2%.
**Observed result**: [Pending Execution]
**Pass/Fail**: [Pending]
**Limitation**: Poor lighting causes false positives in vision models.
**Decision**: [Pending]

---

## POC 7 — PROVIDER FALLBACK

**Objective**: Ensure the system recovers gracefully if the primary LLM/STT provider fails.

**Implementation**:
```python
import httpx
async def call_llm_with_fallback(prompt):
    try:
        # Primary: OpenRouter
        return await httpx.post("https://openrouter.ai/api/v1/...", timeout=2.0)
    except httpx.TimeoutException:
        # Fallback: Groq
        return await httpx.post("https://api.groq.com/...", timeout=2.0)
```

**Metric**: Time to detect failure and receive response from fallback.
**Target**: Total recovery time < 3 seconds.
**Observed result**: [Pending Execution]
**Pass/Fail**: [Pending]
**Limitation**: Doubles cost if requests are run in parallel for extreme low-latency redundancy.
**Decision**: [Pending]

---

## POC 8 — CODING SANDBOX

**Objective**: Safely execute untrusted candidate code.

**Implementation**:
```python
import requests
def run_code_in_piston(code, language="python"):
    # Using public Piston API for POC
    res = requests.post("https://emojicoder.piston.run/api/v2/execute", json={
        "language": language,
        "version": "3.10.0",
        "files": [{"content": code}],
        "compile_timeout": 5000,
        "run_timeout": 3000
    })
    return res.json()

# Test malicious
result = run_code_in_piston("import os; os.system('cat /etc/passwd')")
print(result) # Should show isolated gVisor filesystem
```

**Metric**: Process isolation, timeout enforcement.
**Target**: 100% block of network/filesystem access. Hard timeout at 3000ms.
**Observed result**: [Pending Execution]
**Pass/Fail**: [Pending]
**Limitation**: Heavy reliance on third-party gVisor security posture.
**Decision**: [Pending]

---

## POC 9 — SESSION RECOVERY

**Objective**: Survive a candidate network drop without losing interview progress.

**Implementation**:
```python
# Server-side state store (Redis)
import redis
r = redis.Redis()

def save_state(session_id, state):
    r.setex(f"session:{session_id}", 600, state) # 10 minute expiry

def restore_session(session_id):
    state = r.get(f"session:{session_id}")
    if not state:
        raise Exception("Session expired or invalid")
    return state
```

**Metric**: Success rate of reconnecting a dropped WebSocket within 60 seconds.
**Target**: 100% recovery with exact state restoration.
**Observed result**: [Pending Execution]
**Pass/Fail**: [Pending]
**Limitation**: State > 10 mins is permanently closed to prevent abuse.
**Decision**: [Pending]

---

## POC 10 — LOAD TEST

**Objective**: Assess system bottlenecks at 1, 10, 50, and 100 concurrent voice sessions.

**Implementation**:
```python
# Utilizing Locust for load testing WebSockets
from locust import HttpUser, task, between

class InterviewUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def simulate_interview(self):
        # 1. Hit API to get token
        # 2. Open WebSocket
        # 3. Stream dummy audio binary
        pass
```

**Metric**: CPU/RAM per container, DB connections, API Provider Rate Limits (HTTP 429).
**Target**: Successfully sustain 100 concurrent sessions without >5% packet loss or TTFT > 1000ms.
**Observed result**: [Pending Execution]
**Pass/Fail**: [Pending]
**Limitation**: Load testing requires paid credits on provider platforms (Deepgram/Cartesia/LLM).
**Decision**: [Pending]
