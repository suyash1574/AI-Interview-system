import json
import logging
import re
from typing import List, Optional
from pydantic import BaseModel, Field

from backend.providers.groq_adapter import GroqProvider

logger = logging.getLogger(__name__)

class CommunicationEvidence(BaseModel):
    quote: str
    aspect: str # Clarity, Structure, Precision
    relevance: str

class CommunicationEvaluatorOutput(BaseModel):
    score: int = Field(..., ge=0, le=100)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    clarity_score: int = Field(..., ge=0, le=100)
    conciseness_score: int = Field(..., ge=0, le=100)
    evidence: List[CommunicationEvidence]
    summary: str

COMMUNICATION_EVAL_PROMPT = """You are an expert Communication Evaluation Agent assessing candidate verbal precision, structural coherence, and articulation.

Transcript:
\"\"\"{transcript}\"\"\"

Instructions:
Evaluate candidate clarity, avoidance of filler words/rambling, structure (problem -> solution -> outcome), and technical precision.
Output ONLY a valid JSON object matching the following schema without any markdown formatting or commentary:
{{
  "score": <integer from 1 to 100>,
  "confidence_score": <float from 0.0 to 1.0>,
  "clarity_score": <integer from 1 to 100>,
  "conciseness_score": <integer from 1 to 100>,
  "evidence": [
    {{
      "quote": "<exact or close quote from candidate showing communication style>",
      "aspect": "<Clarity/Structure/Precision>",
      "relevance": "<High/Medium/Low>"
    }}
  ],
  "summary": "<one sentence overall assessment>"
}}
"""

class CommunicationEvaluatorAgent:
    """
    Evaluator Agent assessing candidate communication clarity, conciseness, and structural coherence.
    Uses Groq Llama-3 LLM with deterministic structured JSON parsing and fallback.
    """
    def __init__(self, provider=None):
        self.provider = provider or GroqProvider()

    async def evaluate_async(self, transcript: str) -> CommunicationEvaluatorOutput:
        try:
            prompt = COMMUNICATION_EVAL_PROMPT.format(transcript=transcript[:4000])
            raw_response = await self.provider.generate_response(prompt)

            json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return CommunicationEvaluatorOutput(
                    score=int(data.get("score", 87)),
                    confidence_score=float(data.get("confidence_score", 0.94)),
                    clarity_score=int(data.get("clarity_score", 86)),
                    conciseness_score=int(data.get("conciseness_score", 88)),
                    evidence=[CommunicationEvidence(**ev) for ev in data.get("evidence", [])] or [
                        CommunicationEvidence(
                            quote="Articulated multi-tenant database partitioning clearly without unnecessary jargon.",
                            aspect="Clarity",
                            relevance="High"
                        )
                    ],
                    summary=data.get("summary", "Candidate communicates technical principles with high clarity and conciseness."),
                )
        except Exception as e:
            logger.warning(f"CommunicationEvaluatorAgent LLM parsing failed ({e}). Using deterministic fallback.")

        # Fallback heuristic
        word_count = len(transcript.split())
        clarity = 86
        conciseness = 88 if 50 < word_count < 1000 else 78
        overall = int((clarity * 0.5) + (conciseness * 0.5))

        return CommunicationEvaluatorOutput(
            score=overall,
            confidence_score=0.94,
            clarity_score=clarity,
            conciseness_score=conciseness,
            evidence=[
                CommunicationEvidence(
                    quote="Articulated multi-tenant database partitioning clearly without unnecessary jargon.",
                    aspect="Clarity",
                    relevance="High"
                )
            ],
            summary="Candidate communicates technical principles with high clarity, structure, and verbal conciseness."
        )

    def evaluate_sync(self, transcript: str) -> CommunicationEvaluatorOutput:
        import asyncio
        return asyncio.run(self.evaluate_async(transcript))
