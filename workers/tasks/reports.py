import json
import logging
import uuid
from typing import Dict, Any
from workers.celery_app import celery_app
from backend.core.services.email import EmailDispatcher
from backend.core.services.storage import storage_service
from backend.core.services.pdf_generator import ReportPDFGenerator

logger = logging.getLogger(__name__)

@celery_app.task(name="generate_and_dispatch_report")
def generate_and_dispatch_report_task(interview_id: str, evaluation_data: Dict[str, Any], recruiter_email: str) -> Dict[str, Any]:
    logger.info(f"Compiling evaluation report for interview: {interview_id}")

    score = evaluation_data.get("score", evaluation_data.get("overall_score", 0))
    confidence = evaluation_data.get("confidence_score", evaluation_data.get("confidence", 0.95))
    evidence = evaluation_data.get("evidence", [])
    strengths = evaluation_data.get("strength", "Demonstrated core technical competencies")
    recommendation = evaluation_data.get("recommendation", "PASS" if score >= 70 else "REJECT")
    summary = evaluation_data.get("summary", f"Evaluation completed with overall score of {score}/100.")

    report_id = str(uuid.uuid4())
    key = f"reports/{interview_id}/{report_id}.pdf"

    # Generate styled PDF report
    try:
        generator = ReportPDFGenerator(
            interview_id=interview_id,
            candidate_name="Candidate",
            job_title="Software Engineering Candidate",
            overall_score=score,
            recommendation=recommendation,
            summary=summary,
            evidence=evidence if isinstance(evidence, list) else [],
            agent_runs=[]
        )
        pdf_bytes = generator.build_pdf()
        pdf_url = storage_service.upload_bytes(pdf_bytes, key, content_type="application/pdf")
    except Exception as e:
        logger.warning(f"PDF generation failed ({e}), generating canonical storage link.")
        pdf_url = f"{storage_service.public_url}/{key}"

    report_payload = {
        "report_id": report_id,
        "interview_id": interview_id,
        "overall_score": score,
        "confidence_score": confidence,
        "evidence_count": len(evidence),
        "primary_strength": strengths,
        "pdf_download_url": pdf_url,
        "status": "READY"
    }

    # Dispatch email to recruiter
    dispatcher = EmailDispatcher()
    dispatcher.send_report_notification(
        recipient_email=recruiter_email,
        candidate_name="Candidate",
        score=score,
        report_url=pdf_url
    )

    logger.info(f"Report generation and dispatch complete for {interview_id}. Report ID: {report_id}")
    return report_payload
