import pytest
from agents.technical import TechnicalEvaluatorAgent, TechnicalEvaluatorOutput
from agents.behavioral import BehavioralEvaluatorAgent, BehavioralEvaluatorOutput
from agents.communication import CommunicationEvaluatorAgent, CommunicationEvaluatorOutput
from agents.orchestrator import MultiAgentOrchestrator, MultiAgentEvaluationResult
from workers.tasks.evaluation import evaluate_interview_task

@pytest.mark.asyncio
async def test_technical_evaluator_agent_async():
    agent = TechnicalEvaluatorAgent()
    result = await agent.evaluate_async("Candidate explained database partitioning and indexing.")
    assert isinstance(result, TechnicalEvaluatorOutput)
    assert result.score > 0
    assert len(result.evidence) > 0

@pytest.mark.asyncio
async def test_behavioral_evaluator_agent_async():
    agent = BehavioralEvaluatorAgent()
    transcript = "I led the migration, took ownership of the incident response, and collaborated with cross-functional stakeholders."
    result = await agent.evaluate_async(transcript)
    assert isinstance(result, BehavioralEvaluatorOutput)
    assert result.score >= 70
    assert len(result.leadership_strengths) > 0

@pytest.mark.asyncio
async def test_communication_evaluator_agent_async():
    agent = CommunicationEvaluatorAgent()
    transcript = "Our team adopted an event-driven architecture using Kafka streams to achieve low latency."
    result = await agent.evaluate_async(transcript)
    assert isinstance(result, CommunicationEvaluatorOutput)
    assert result.clarity_score > 0
    assert result.conciseness_score > 0

@pytest.mark.asyncio
async def test_multi_agent_orchestrator():
    orchestrator = MultiAgentOrchestrator()
    transcript = "I led the engineering team to deploy our multi-tenant PostgreSQL RLS database with Redis caching."
    result = await orchestrator.evaluate_interview_async("int-123", transcript)
    assert isinstance(result, MultiAgentEvaluationResult)
    assert result.overall_score >= 75
    assert result.recommendation == "PASS"
    assert len(result.aggregated_evidence) >= 3

def test_evaluate_interview_task_celery():
    result = evaluate_interview_task("int-999", "Candidate answer about system reliability.")
    assert isinstance(result, dict)
    assert "overall_score" in result
    assert "recommendation" in result
    assert "technical" in result
    assert "behavioral" in result
    assert "communication" in result
