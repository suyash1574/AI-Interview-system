import json
from pydantic import BaseModel, Field
from typing import List

class Evidence(BaseModel):
    quote: str = Field(..., description="Candidate's exact quote")
    relevance: str = Field(..., description="High/Medium/Low relevance to competency")

class TechnicalEvaluatorOutput(BaseModel):
    score: int = Field(..., description="Score from 1-100")
    confidence_score: float = Field(..., description="Confidence of the agent (0.0-1.0)")
    evidence: List[Evidence] = Field(..., description="Evidence supporting the score")
    missing_knowledge: List[str] = Field(..., description="Key areas the candidate failed to cover")
    strength: str = Field(..., description="Candidate's biggest technical strength shown")

class TechnicalEvaluatorAgent:
    '''
    Agent that encapsulates NVIDIA NAT / LLM evaluation logic.
    For MVP, uses mocked/structured inference logic.
    '''
    def __init__(self, provider=None):
        self.provider = provider
        
    async def evaluate_async(self, transcript: str) -> TechnicalEvaluatorOutput:
        # Placeholder for actual LLM call using provider with structured outputs
        # MVP: Return static parsed output or invoke mock LLM logic.
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
