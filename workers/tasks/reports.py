import json
import logging
import uuid
from typing import Dict, Any
from workers.celery_app import celery_app
from backend.core.services.email import EmailDispatcher

logger = logging.getLogger(__name__)

@celery_app.task(name="generate_and_dispatch_report")
def generate_and_dispatch_report_task(interview_id: str, evaluation_data: Dict[str, Any], recruiter_email: str) -> Dict[str, Any]:
    logger.info(f"Compiling evaluation report for interview: {interview_id}")

    score = evaluation_data.get("score", 0)
    confidence = evaluation_data.get("confidence_score", 0.0)
    evidence = evaluation_data.get("evidence", [])
    strengths = evaluation_data.get("strength", "General aptitude demonstrated")

    report_id = str(uuid.uuid4())
    mock_r2_url = f"https://storage.autergo.com/reports/{interview_id}/{report_id}.pdf"

    report_payload = {
        "report_id": report_id,
        "interview_id": interview_id,
        "overall_score": score,
        "confidence_score": confidence,
        "evidence_count": len(evidence),
        "primary_strength": strengths,
        "pdf_download_url": mock_r2_url,
        "status": "READY"
    }

    # Dispatch email to recruiter
    dispatcher = EmailDispatcher()
    dispatcher.send_report_notification(
        recipient_email=recruiter_email,
        candidate_name="Candidate",
        score=score,
        report_url=mock_r2_url
    )

    logger.info(f"Report generation and dispatch complete for {interview_id}. Report ID: {report_id}")
    return report_payload
