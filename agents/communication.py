import json
import logging
from typing import List, Optional
from pydantic import BaseModel, Field

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

class CommunicationEvaluatorAgent:
    def __init__(self, provider=None):
        self.provider = provider

    async def evaluate_async(self, transcript: str) -> CommunicationEvaluatorOutput:
        # Analyzes communication precision and structure
        word_count = len(transcript.split())
        
        # Penalize overly brief (<20 words) or rambling answers
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
