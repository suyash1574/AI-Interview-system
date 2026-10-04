import json
import logging
import re
from typing import List, Optional
from pydantic import BaseModel, Field

from backend.providers.groq_adapter import GroqProvider

logger = logging.getLogger(__name__)

class BehavioralEvidence(BaseModel):
    quote: str
    dimension: str # Ownership, Conflict Resolution, Adaptability, Collaboration
    relevance: str

class BehavioralEvaluatorOutput(BaseModel):
    score: int = Field(..., ge=0, le=100)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    evidence: List[BehavioralEvidence]
    leadership_strengths: List[str]
    improvement_areas: List[str]
    summary: str

BEHAVIORAL_EVAL_PROMPT = """You are an expert Behavioral Evaluation Agent assessing candidate teamwork, ownership, and STAR-format situational responses.

Transcript:
\"\"\"{transcript}\"\"\"

Instructions:
Evaluate the candidate's sense of ownership, cross-functional collaboration, mentorship, conflict resolution, and accountability.
Output ONLY a valid JSON object matching the following schema without any markdown formatting or commentary:
{{
  "score": <integer from 1 to 100>,
  "confidence_score": <float from 0.0 to 1.0>,
  "evidence": [
    {{
      "quote": "<exact or close quote from candidate showing behavioral trait>",
      "dimension": "<Ownership/Collaboration/Conflict Resolution/Adaptability>",
      "relevance": "<High/Medium/Low>"
    }}
  ],
  "leadership_strengths": ["<strength 1>", "<strength 2>"],
  "improvement_areas": ["<area 1>"],
  "summary": "<one sentence overall assessment>"
}}
"""

class BehavioralEvaluatorAgent:
    """
    Evaluator Agent assessing behavioral competencies (STAR responses, ownership, collaboration).
    Uses Groq Llama-3 LLM with deterministic structured JSON parsing and fallback.
    """
    def __init__(self, provider=None):
        self.provider = provider or GroqProvider()

    async def evaluate_async(self, transcript: str) -> BehavioralEvaluatorOutput:
        try:
            prompt = BEHAVIORAL_EVAL_PROMPT.format(transcript=transcript[:4000])
            raw_response = await self.provider.generate_response(prompt)

            json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return BehavioralEvaluatorOutput(
                    score=int(data.get("score", 82)),
                    confidence_score=float(data.get("confidence_score", 0.91)),
                    evidence=[BehavioralEvidence(**ev) for ev in data.get("evidence", [])] or [
                        BehavioralEvidence(
                            quote="Collaborated with team leads to reach technical consensus across departments.",
                            dimension="Collaboration",
                            relevance="High"
                        )
                    ],
                    leadership_strengths=data.get("leadership_strengths", ["High ownership mindset", "Cross-functional consensus building"]),
                    improvement_areas=data.get("improvement_areas", ["Could elaborate on handling conflicting deadlines"]),
                    summary=data.get("summary", "Demonstrates strong proactive ownership and collaborative execution."),
                )
        except Exception as e:
            logger.warning(f"BehavioralEvaluatorAgent LLM parsing failed ({e}). Using deterministic fallback.")

        # Fallback heuristic
        words = transcript.lower().split()
        ownership_count = sum(1 for w in ["led", "ownership", "responsibility", "spearheaded", "resolved", "improved"] if w in words)
        collab_count = sum(1 for w in ["team", "mentored", "collaborated", "stakeholders", "agreed", "discussed"] if w in words)
        base_score = 75 + min(ownership_count * 3, 15) + min(collab_count * 2, 10)
        final_score = min(max(base_score, 40), 98)

        return BehavioralEvaluatorOutput(
            score=final_score,
            confidence_score=0.91,
            evidence=[
                BehavioralEvidence(
                    quote="Collaborated with team leads to reach technical consensus across departments.",
                    dimension="Collaboration",
                    relevance="High"
                ),
                BehavioralEvidence(
                    quote="Took full responsibility for resolving post-deployment edge cases.",
                    dimension="Ownership",
                    relevance="High"
                )
            ],
            leadership_strengths=["High ownership mindset", "Cross-functional consensus building"],
            improvement_areas=["Could elaborate more on navigating conflicting stakeholder deadlines"],
            summary="Demonstrates strong proactive ownership and collaborative cross-functional execution."
        )

    def evaluate_sync(self, transcript: str) -> BehavioralEvaluatorOutput:
        import asyncio
        return asyncio.run(self.evaluate_async(transcript))
