import logging
from workers.celery_app import celery_app
from agents.technical import TechnicalEvaluatorAgent
import asyncio

logger = logging.getLogger(__name__)

@celery_app.task(name="evaluate_interview")
def evaluate_interview_task(interview_id: str, transcript: str):
    logger.info(f"Starting evaluation for interview: {interview_id}")
    
    agent = TechnicalEvaluatorAgent()
    # NAT agent evaluation runs synchronously inside Celery worker
    result = agent.evaluate_sync(transcript)
    
    logger.info(f"Completed evaluation for {interview_id}. Score: {result.score}")
    return result.model_dump()
