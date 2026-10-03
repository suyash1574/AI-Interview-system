import pytest
from agents.technical import TechnicalEvaluatorAgent, TechnicalEvaluatorOutput
from workers.tasks.evaluation import evaluate_interview_task

@pytest.mark.asyncio
async def test_technical_evaluator_agent_async():
    agent = TechnicalEvaluatorAgent()
    result = await agent.evaluate_async("Candidate said something technical.")
    assert isinstance(result, TechnicalEvaluatorOutput)
    assert result.score == 85
    assert "Database Optimization" in result.strength

def test_evaluate_interview_task_sync():
    # Test Celery task wrapper directly
    result = evaluate_interview_task("test-int-123", "Dummy transcript.")
    assert isinstance(result, dict)
    assert result["score"] == 85
    assert len(result["evidence"]) == 1
