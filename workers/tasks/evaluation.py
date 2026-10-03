import logging
from workers.celery_app import celery_app
from agents.orchestrator import MultiAgentOrchestrator

logger = logging.getLogger(__name__)

@celery_app.task(name="evaluate_interview")
def evaluate_interview_task(interview_id: str, transcript: str):
    logger.info(f"Starting multi-agent evaluation for interview: {interview_id}")
    
    orchestrator = MultiAgentOrchestrator()
    result = orchestrator.evaluate_interview_sync(interview_id, transcript)
    
    logger.info(f"Completed multi-agent evaluation for {interview_id}. Overall Score: {result.overall_score} ({result.recommendation})")
    return result.model_dump()
