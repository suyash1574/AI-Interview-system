import asyncio
import logging
from typing import Dict, Any, List
from pydantic import BaseModel

from agents.technical import TechnicalEvaluatorAgent, TechnicalEvaluatorOutput
from agents.behavioral import BehavioralEvaluatorAgent, BehavioralEvaluatorOutput
from agents.communication import CommunicationEvaluatorAgent, CommunicationEvaluatorOutput

logger = logging.getLogger(__name__)

class MultiAgentEvaluationResult(BaseModel):
    overall_score: int
    recommendation: str # PASS, HOLD, REJECT
    executive_summary: str
    technical: TechnicalEvaluatorOutput
    behavioral: BehavioralEvaluatorOutput
    communication: CommunicationEvaluatorOutput
    aggregated_evidence: List[Dict[str, Any]]

class MultiAgentOrchestrator:
    def __init__(self, provider=None):
        self.technical_agent = TechnicalEvaluatorAgent(provider=provider)
        self.behavioral_agent = BehavioralEvaluatorAgent(provider=provider)
        self.communication_agent = CommunicationEvaluatorAgent(provider=provider)

    async def evaluate_interview_async(self, interview_id: str, transcript: str) -> MultiAgentEvaluationResult:
        logger.info(f"Running multi-agent evaluation for interview {interview_id}...")

        # Concurrently execute all domain agents
        tech_out, behav_out, comm_out = await asyncio.gather(
            self.technical_agent.evaluate_async(transcript),
            self.behavioral_agent.evaluate_async(transcript),
            self.communication_agent.evaluate_async(transcript),
        )

        # Weighted composite score per AUTERGO_ARCHITECTURE_BASELINE_v2.0.md
        # 50% Technical, 25% Behavioral, 25% Communication
        overall = int(round(
            (tech_out.score * 0.50) +
            (behav_out.score * 0.25) +
            (comm_out.score * 0.25)
        ))

        # Determine hiring recommendation
        if overall >= 75:
            recommendation = "PASS"
        elif overall >= 60:
            recommendation = "HOLD"
        else:
            recommendation = "REJECT"

        summary = (
            f"Overall Score: {overall}/100 ({recommendation}). "
            f"Technical Strengths: {tech_out.strength}. "
            f"Leadership: {', '.join(behav_out.leadership_strengths[:2])}. "
            f"Communication: {comm_out.summary}"
        )

        # Aggregate evidence citations
        evidence_list = []
        for ev in tech_out.evidence:
            evidence_list.append({"agent": "TECHNICAL", "quote": ev.quote, "relevance": ev.relevance})
        for ev in behav_out.evidence:
            evidence_list.append({"agent": "BEHAVIORAL", "quote": ev.quote, "dimension": ev.dimension, "relevance": ev.relevance})
        for ev in comm_out.evidence:
            evidence_list.append({"agent": "COMMUNICATION", "quote": ev.quote, "aspect": ev.aspect, "relevance": ev.relevance})

        logger.info(f"Multi-agent evaluation completed for {interview_id}. Result: {overall} ({recommendation})")

        return MultiAgentEvaluationResult(
            overall_score=overall,
            recommendation=recommendation,
            executive_summary=summary,
            technical=tech_out,
            behavioral=behav_out,
            communication=comm_out,
            aggregated_evidence=evidence_list,
        )

    def evaluate_interview_sync(self, interview_id: str, transcript: str) -> MultiAgentEvaluationResult:
        return asyncio.run(self.evaluate_interview_async(interview_id, transcript))
