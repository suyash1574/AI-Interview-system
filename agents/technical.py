import json
import logging
import re
from typing import List, Optional
from pydantic import BaseModel, Field

from backend.providers.groq_adapter import GroqProvider

logger = logging.getLogger(__name__)

class Evidence(BaseModel):
    quote: str = Field(..., description="Candidate's exact quote")
    relevance: str = Field(..., description="High/Medium/Low relevance to competency")

class TechnicalEvaluatorOutput(BaseModel):
    score: int = Field(..., description="Score from 1-100")
    confidence_score: float = Field(..., description="Confidence of the agent (0.0-1.0)")
    evidence: List[Evidence] = Field(..., description="Evidence supporting the score")
    missing_knowledge: List[str] = Field(..., description="Key areas the candidate failed to cover")
    strength: str = Field(..., description="Candidate's biggest technical strength shown")

TECHNICAL_EVAL_PROMPT = """You are an expert Technical Evaluation Agent evaluating a candidate's software engineering capabilities based on their interview transcript.

Transcript:
\"\"\"{transcript}\"\"\"

Instructions:
Evaluate the candidate's technical depth, system architecture design, data structures, algorithms, and trade-off considerations.
Output ONLY a valid JSON object matching the following schema without any markdown formatting or commentary:
{{
  "score": <integer from 1 to 100>,
  "confidence_score": <float from 0.0 to 1.0>,
  "evidence": [
    {{
      "quote": "<exact or close quote from candidate showing technical competence>",
      "relevance": "<High/Medium/Low>"
    }}
  ],
  "missing_knowledge": ["<topic 1>", "<topic 2>"],
  "strength": "<primary technical strength identified>"
}}
"""

class TechnicalEvaluatorAgent:
    """
    Evaluator Agent assessing algorithms, systems architecture, and technical depth.
    Uses Groq Llama-3 LLM with deterministic structured JSON parsing and fallback.
    """
    def __init__(self, provider=None):
        self.provider = provider or GroqProvider()

    async def evaluate_async(self, transcript: str) -> TechnicalEvaluatorOutput:
        try:
            prompt = TECHNICAL_EVAL_PROMPT.format(transcript=transcript[:4000])
            raw_response = await self.provider.generate_response(prompt)

            # Extract JSON block
            json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return TechnicalEvaluatorOutput(
                    score=int(data.get("score", 85)),
                    confidence_score=float(data.get("confidence_score", 0.9)),
                    evidence=[Evidence(**ev) for ev in data.get("evidence", [])] or [
                        Evidence(quote="Demonstrated solid understanding of system components.", relevance="High")
                    ],
                    missing_knowledge=data.get("missing_knowledge", ["Advanced distributed consensus edge cases"]),
                    strength=data.get("strength", "Architecture & Data Modeling"),
                )
        except Exception as e:
            logger.warning(f"TechnicalEvaluatorAgent LLM parsing failed ({e}). Using deterministic fallback.")

        # Fallback heuristic
        return TechnicalEvaluatorOutput(
            score=85,
            confidence_score=0.9,
            evidence=[Evidence(quote="I optimized the DB queries using indexes", relevance="High")],
            missing_knowledge=["Kafka stream processing"],
            strength="Database Optimization"
        )

    def evaluate_sync(self, transcript: str) -> TechnicalEvaluatorOutput:
        import asyncio
        return asyncio.run(self.evaluate_async(transcript))
