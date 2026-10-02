# 07 Technology Decision Matrix

## Document Header
| Field | Value |
| --- | --- |
| **Product** | Autergo |
| **Version** | 1.0 |
| **Date** | October 2026 |
| **Status** | Draft |
| **Document Owner** | System Architect |
| **Purpose** | Comprehensive technology selection with research-backed decisions |

### Revision History
| Version | Date | Author | Changes |
| --- | --- | --- | --- |
| 1.0 | Oct 2026 | System Architect | Initial draft and technology decisions |

### References
- [00-Master-Requirements-Baseline](00-Master-Requirements-Baseline.md)

### Assumptions
- [ASSUMPTION] Cost projections are based on current pricing models as of Q4 2026 and are subject to change.

### Open Decisions
- [OPEN DECISION] Benchmark Speech-to-Speech vs Cascaded (STT+LLM+TTS) approaches. Default to cascaded for MVP for control, evaluate S2S for V2.

---

## 1. Client Voice Transport

| Option | Functionality | Latency | Scalability | Reliability | Open-Source | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| WebRTC (LiveKit) | Native audio streaming, AEC, Opus codec | Ultra-low (<50ms) | High (SFU architecture) | High (Adaptive jitter, no HOL blocking) | Yes (Apache 2.0) | **SELECTED** |
| WebSocket | Raw binary streaming | Low to Medium | Medium | Medium (TCP HOL blocking) | N/A | Rejected |
| aiortc | Python WebRTC implementation | Low | Low (Hard to scale across workers) | Medium | Yes | Rejected |

**Rationale:** WebRTC via LiveKit provides hardware Acoustic Echo Cancellation (AEC), eliminates TCP Head-of-Line (HOL) blocking, uses the highly efficient Opus codec, and features an adaptive jitter buffer.

---

## 2. STT Provider

| Option | Functionality | Latency | Cost | Privacy | Developer Experience | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| Deepgram Nova-3 | High accuracy, native WebSocket | 200-300ms | $0.0077/min ($200 free credit) | SOC2 | Excellent | **SELECTED (Primary)** |
| AssemblyAI | High accuracy | 300-400ms | Comparable | SOC2 | Good | **SELECTED (Fallback)** |
| Google Cloud STT | Standard accuracy | >500ms | High | Varies | Medium | Rejected |
| Azure STT | Standard accuracy | >400ms | High | Enterprise | Medium | Rejected |
| OpenAI Whisper (API) | High accuracy | High (not streaming optimized) | Medium | Standard | Simple | Rejected |

**Rationale:** Deepgram Nova-3 offers the best latency-to-accuracy ratio (200-300ms) with native WebSocket support and cost-effective per-audio billing.

---

## 3. TTS Provider

| Option | Functionality | Latency (TTFA) | Cost | License/Lock-in | Decision |
| --- | --- | --- | --- | --- | --- |
| Cartesia Sonic | High emotion, fast | 40-90ms | ~$0.0001/char | Commercial | **SELECTED (Primary)** |
| ElevenLabs Flash | Excellent quality | ~150ms | Premium | Commercial | **SELECTED (Fallback)** |
| OpenAI TTS | Good quality | >300ms | Medium | Commercial | Rejected |
| Azure/Google TTS | Standard | 200ms+ | Low/Medium | Commercial | Rejected |
| XTTS-v2 | Open weights | Varies | Infrastructure cost | CPML non-commercial | Rejected |

**Rationale:** Cartesia Sonic provides the absolute lowest Time-To-First-Audio (TTFA) at 40-90ms with bidirectional WebSocket support. XTTS-v2 was rejected due to its CPML non-commercial license.

---

## 4. Voice Activity Detection (VAD)

| Option | Functionality | Latency | Size | License | Decision |
| --- | --- | --- | --- | --- | --- |
| Silero VAD v5 | Excellent noise rejection | <1ms | <2MB | MIT | **SELECTED** |
| WebRTC VAD | Standard VAD | <1ms | Very Small | BSD | Rejected |
| Picovoice Cobra | Good accuracy | Low | Small | Commercial restrictions | Rejected |

**Rationale:** Silero VAD v5 is exceptionally fast, lightweight, and offers superior noise rejection under a permissive MIT license.

---

## 5. Turn Detection

| Option | Description | Performance | Decision |
| --- | --- | --- | --- |
| Semantic Turn Detection | Uses context and VAD to determine turn | High accuracy, low false positives | **SELECTED** |
| Static Silence | Fixed silence threshold | High false positives on pauses | Rejected |
| STT Endpointing | Relies on STT provider to signal end | High latency | Rejected |
| S2S Native | Native multi-modal turn detection | High cost, less control | Rejected |

**Rationale:** Semantic turn detection using LiveKit Turn Detector combined with Silero VAD offers the best balance of speed and conversational naturalness.

---

## 6. LLM Gateway

| Option | Functionality | Cost | Reliability | Decision |
| --- | --- | --- | --- | --- |
| OpenRouter | Multi-model routing, fallback | Provider cost | High | **SELECTED** |
| Direct APIs | Direct vendor connection | Vendor cost | Vendor dependent | **SELECTED (Latency-critical)** |
| LiteLLM | Self-hosted gateway | Infrastructure cost | High | Rejected |

**Rationale:** OpenRouter provides excellent flexibility for multi-model routing and fallbacks, while direct APIs will be used for latency-critical paths.

---

## 7. Agent Orchestration

| Option | Developer Experience | Scalability | License | Decision |
| --- | --- | --- | --- | --- |
| NVIDIA NAT | YAML-driven, FastAPI serving | High | Apache 2.0 | **SELECTED** |
| LangGraph | Graph-based, steep learning curve | Medium | MIT | Rejected |
| CrewAI | Multi-agent, heavyweight | Medium | MIT | Rejected |
| Custom | Total control, high dev time | Varies | N/A | Rejected |

**Rationale:** NVIDIA NeMo Agent Toolkit (NAT) provides a scalable, YAML-driven approach with native FastAPI serving under an Apache 2.0 license.

---

## 8. Resume/JD Parsing

| Option | Accuracy | Speed | License | Decision |
| --- | --- | --- | --- | --- |
| GLiNER + NuExtract | High (Structured extraction) | Fast (Local inference) | Apache 2.0/MIT | **SELECTED** |
| LLM-only | Very High | Slow (Network bound) | Varies | Rejected |
| spaCy | Medium (Requires training) | Very Fast | MIT | Rejected |

**Rationale:** GLiNER v2.1 for Named Entity Recognition and NuExtract-1.5 for structured extraction offer fast, local processing with permissive licenses.

---

## 9. Embeddings

| Option | Context Length | Features | License | Decision |
| --- | --- | --- | --- | --- |
| nomic-embed-text-v1.5 | 8K | Matryoshka representation | Apache 2.0 | **SELECTED** |
| bge-small | Small | Fast | MIT | Rejected |
| OpenAI Embeddings | High | Proprietary | Commercial | Rejected |

**Rationale:** nomic-embed-text-v1.5 supports an 8K context window, Matryoshka embeddings for flexibility, and is Apache 2.0 licensed.

---

## 10. Code Sandbox

| Option | Language Support | Security | License | Decision |
| --- | --- | --- | --- | --- |
| Piston (with gVisor) | Multi-language | High (gVisor) | MIT | **SELECTED** |
| Judge0 | Multi-language | Medium | MIT | Rejected |
| Firecracker | Varies | Very High | Apache 2.0 | Rejected |
| Pyodide | Python only | High (Browser) | MPL | Rejected |

**Rationale:** Piston provides a simple REST API and broad language support, secured via gVisor.

---

## 11. Database

| Option | Scalability | Features | Pricing | Decision |
| --- | --- | --- | --- | --- |
| Neon PostgreSQL | Scale-to-zero | Auto-wake, branching | Generous free tier | **SELECTED** |
| Supabase | High | Full BaaS | Standard | Rejected |
| Railway / Render | Medium | Standard SQL | Fixed instance | Rejected |

**Rationale:** Neon offers scale-to-zero serverless PostgreSQL, branching capabilities, and data retention guarantees.

---

## 12. Authentication

| Option | B2B Features | Pricing | Developer Experience | Decision |
| --- | --- | --- | --- | --- |
| Clerk | Native B2B RBAC, org switching | 50K MRUs free | Excellent | **SELECTED** |
| Supabase Auth | Standard | Usage based | Good | Rejected |
| Auth0 | Comprehensive | Expensive at scale | Good | Rejected |
| Keycloak | Comprehensive | Requires hosting | Steep | Rejected |

**Rationale:** Clerk provides superior out-of-the-box B2B RBAC and organization switching with a generous free tier.

---

## 13. Email

| Option | API Cleanliness | Pricing | Delivery Rate | Decision |
| --- | --- | --- | --- | --- |
| Resend | Excellent | 3K/mo free | High | **SELECTED (MVP)** |
| Amazon SES | Standard | Highly cost-effective | High | **SELECTED (Prod)** |
| SendGrid / Postmark / Mailgun | Good | Standard | High | Rejected |

**Rationale:** Resend offers the best developer experience for the MVP, while Amazon SES will provide cost efficiency at production scale.

---

## 14. Object Storage

| Option | Egress Costs | Compatibility | Free Tier | Decision |
| --- | --- | --- | --- | --- |
| Cloudflare R2 | $0 egress | S3 compatible | 10GB free | **SELECTED** |
| Backblaze B2 | Low | S3 compatible | 10GB free | Rejected |
| Supabase / MinIO | Standard / Hosting cost | Standard | Varies | Rejected |

**Rationale:** Cloudflare R2 provides an S3-compatible API with zero egress fees, ideal for serving audio and reports.

---

## 15. Compute/Hosting

| Option | Scalability | Deployment | Free Tier | Decision |
| --- | --- | --- | --- | --- |
| Google Cloud Run | Auto-scale to zero | Docker | 2M req/mo free | **SELECTED** |
| AWS Lambda | High | Serverless function | High | Rejected |
| Render / Railway / Fly.io | Standard | Docker/Native | Varies | Rejected |

**Rationale:** Google Cloud Run offers straightforward container deployment with auto-scaling to zero and a generous free tier.

---

## 16. CDN/DNS

| Option | Features | Cost | Decision |
| --- | --- | --- | --- |
| Cloudflare | CDN, DNS, DDoS, SSL, WAF | Unlimited free bandwidth | **SELECTED** |

**Rationale:** Cloudflare is the industry standard for comprehensive web security and CDN services with an unbeatable free tier.

---

## 17. Monitoring

| Option | Scope | Decision |
| --- | --- | --- |
| Grafana Cloud | Metrics, Logs, Traces | **SELECTED (Metrics/Logs)** |
| Sentry | Error tracking | **SELECTED (Errors)** |
| New Relic / Axiom | Comprehensive | Rejected |

**Rationale:** A dual approach using Grafana Cloud for system observability and Sentry for application error tracking provides the best coverage.

---

## 18. CI/CD

| Option | Integration | Pricing | Decision |
| --- | --- | --- | --- |
| GitHub Actions | Native to GitHub | 2K min/mo free | **SELECTED** |
| GitLab CI | Requires GitLab | Standard | Rejected |

**Rationale:** GitHub Actions provides seamless integration with the code repository and sufficient free tier for early development.

---

## 19. Secrets Management

| Option | Features | License | Decision |
| --- | --- | --- | --- |
| Infisical | CLI injection, sync | MIT (5 identities free) | **SELECTED** |
| Doppler | Comprehensive | Commercial | Rejected |
| HashiCorp Vault | Enterprise | BSL | Rejected |

**Rationale:** Infisical offers a great developer experience with CLI injection and an open-source MIT license.

---

## 20. Frontend

| Option | Complexity | Build Step | Decision |
| --- | --- | --- | --- |
| HTML/CSS/JS + Tailwind | Low | No | **SELECTED** |
| React / Next.js / Vue | High | Yes | Rejected (for MVP) |

**Rationale:** A simple stack without a build step accelerates MVP development while Tailwind ensures consistent styling.

---

## 21. Browser Integrity Vision

| Option | Architecture | Performance | Decision |
| --- | --- | --- | --- |
| MediaPipe + YOLO11n | Client-side (INT8 via ONNX Web) | 1 FPS | **SELECTED** |
| Server-side only | Requires video streaming | High bandwidth/cost | Rejected |

**Rationale:** Client-side processing preserves privacy, reduces server bandwidth, and provides sufficient integrity checks at 1 FPS.

---

## 22. Prompt Injection Defense

| Option | Architecture | Cost | Decision |
| --- | --- | --- | --- |
| Llama Guard 3 + Rules | Local + dual-LLM isolation | Compute cost | **SELECTED** |
| Lakera | API based | Per-call cost | Rejected |
| Custom rules only | Basic | N/A | Rejected |

**Rationale:** A layered defense using Llama Guard 3 locally, combined with structural delimiters and dual-LLM isolation, provides robust security.

---

## 23. Speech-to-Speech vs Cascaded

| Option | Control | Latency | Decision |
| --- | --- | --- | --- |
| Cascaded (STT+LLM+TTS) | High | Medium | **SELECTED (MVP Default)** |
| OpenAI Realtime / Gemini Live | Low | Low | **[OPEN DECISION] Benchmark for V2** |

**Rationale:** Cascaded approaches offer necessary control over the interview state machine and logic for the MVP. S2S models will be evaluated for V2 to reduce latency.

---

## Cost Projection Table

Estimated cost per interview (30-minute average):

| Service | Usage | Unit Cost | Per-Interview Cost |
| --- | --- | --- | --- |
| STT (Deepgram) | 30 min | $0.0077/min | $0.23 |
| TTS (Cartesia) | ~5K chars | ~$0.0001/char | $0.50 |
| LLM (conversation) | ~4K tokens | ~$0.001/1K | $0.004 |
| LLM (evaluation) | ~10K tokens | ~$0.003/1K | $0.03 |
| **Total** | | | **~$0.76 - $1.50** |
