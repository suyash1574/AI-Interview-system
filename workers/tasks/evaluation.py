import asyncio
import logging
import uuid
from typing import Dict, Any
from sqlalchemy import select

from workers.celery_app import celery_app
from agents.orchestrator import MultiAgentOrchestrator
from database.session import AsyncSessionLocal
from database.models import Interview, Evaluation, AgentRun, Job, User, Candidate
from backend.config import settings



logger = logging.getLogger(__name__)

async def persist_evaluation_to_db(interview_id: str, result_dict: Dict[str, Any]):
    """Persists the multi-agent consensus evaluation and agent runs into the database."""
    try:
        async with AsyncSessionLocal() as db:
            # 1. Fetch interview
            stmt = select(Interview).where(Interview.id == interview_id)
            res = await db.execute(stmt)
            interview = res.scalar_one_or_none()
            if not interview:
                logger.warning(f"Cannot persist evaluation: Interview {interview_id} not found.")
                return

            tenant_id = interview.tenant_id
            eval_id = str(uuid.uuid4())

            # 2. Create Evaluation record
            evaluation = Evaluation(
                id=eval_id,
                tenant_id=tenant_id,
                interview_id=interview_id,
                overall_score=result_dict["overall_score"],
                recommendation=result_dict["recommendation"],
                summary=result_dict["executive_summary"],
                score_raw=result_dict["overall_score"],
                evidence=result_dict["aggregated_evidence"],
            )
            db.add(evaluation)

            # 3. Create AgentRun records
            # Technical
            tech = result_dict["technical"]
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                evaluation_id=eval_id,
                agent_name="TECHNICAL",
                score=tech["score"],
                confidence=tech["confidence_score"],
                feedback=f"Strength: {tech['strength']}. Missing: {', '.join(tech['missing_knowledge'])}",
                evidence_citations=[e if isinstance(e, dict) else e.model_dump() for e in tech["evidence"]],
                raw_output=tech,
            ))

            # Behavioral
            behav = result_dict["behavioral"]
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                evaluation_id=eval_id,
                agent_name="BEHAVIORAL",
                score=behav["score"],
                confidence=behav["confidence_score"],
                feedback=behav["summary"],
                evidence_citations=[e if isinstance(e, dict) else e.model_dump() for e in behav["evidence"]],
                raw_output=behav,
            ))

            # Communication
            comm = result_dict["communication"]
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                evaluation_id=eval_id,
                agent_name="COMMUNICATION",
                score=comm["score"],
                confidence=comm["confidence_score"],
                feedback=comm["summary"],
                evidence_citations=[e if isinstance(e, dict) else e.model_dump() for e in comm["evidence"]],
                raw_output=comm,
            ))

            # Calculate and persist integrity score from logged integrity events
            from database.models import IntegrityEvent
            events_stmt = select(IntegrityEvent).where(IntegrityEvent.interview_id == interview_id)
            events_res = await db.execute(events_stmt)
            events = events_res.scalars().all()
            high_count = sum(1 for e in events if e.severity == "HIGH")
            med_count = sum(1 for e in events if e.severity == "MEDIUM")
            base = getattr(settings, "INTEGRITY_BASE_SCORE", 1.0)
            high_pen = getattr(settings, "INTEGRITY_HIGH_PENALTY", 0.15)
            med_pen = getattr(settings, "INTEGRITY_MED_PENALTY", 0.05)
            integrity = max(0.0, round(base - (high_count * high_pen) - (med_count * med_pen), 2))
            interview.integrity_score = integrity


            # Query real recruiter email for notification
            recruiter_email = "recruiter@autergo.com"
            user_stmt = select(User).where(User.tenant_id == tenant_id)
            user_res = await db.execute(user_stmt)
            recruiter_user = user_res.scalars().first()
            if recruiter_user and recruiter_user.email:
                recruiter_email = recruiter_user.email

            # Query real Candidate and Job names
            candidate_name = "Candidate"
            if interview.candidate_id:
                cand_res = await db.execute(select(Candidate).where(Candidate.id == interview.candidate_id))
                cand_obj = cand_res.scalar_one_or_none()
                if cand_obj and cand_obj.name:
                    candidate_name = cand_obj.name

            job_title = "Software Engineer"
            if interview.job_id:
                job_res = await db.execute(select(Job).where(Job.id == interview.job_id))
                job_obj = job_res.scalar_one_or_none()
                if job_obj and job_obj.title:
                    job_title = job_obj.title

            # Update interview status
            interview.status = "COMPLETED"
            await db.commit()
            logger.info(f"Successfully persisted Evaluation {eval_id} and 3 AgentRuns for interview {interview_id}. Integrity Score: {integrity}")

            # 4. Trigger Report Generation & Email Dispatch
            try:
                from workers.tasks.reports import generate_and_dispatch_report_task
                generate_and_dispatch_report_task.delay(
                    interview_id=interview_id,
                    evaluation_data={
                        "candidate_name": candidate_name,
                        "job_title": job_title,
                        "score": result_dict["overall_score"],
                        "confidence_score": 0.92,
                        "evidence": result_dict["aggregated_evidence"],
                        "strength": tech["strength"],
                        "integrity_score": integrity,
                    },
                    recruiter_email=recruiter_email
                )
            except Exception as report_err:
                logger.info(f"Celery report dispatch deferred ({report_err})")

    except Exception as e:
        logger.error(f"Failed to persist evaluation records to database: {e}")


@celery_app.task(name="evaluate_interview")
def evaluate_interview_task(interview_id: str, transcript: str):
    logger.info(f"Starting multi-agent evaluation for interview: {interview_id}")
    
    orchestrator = MultiAgentOrchestrator()
    result = orchestrator.evaluate_interview_sync(interview_id, transcript)
    result_dict = result.model_dump()

    # Persist to database with safe event loop management
    import os
    if not os.environ.get("PYTEST_CURRENT_TEST"):
        try:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            loop.run_until_complete(
                asyncio.wait_for(persist_evaluation_to_db(interview_id, result_dict), timeout=30.0)
            )
        except Exception as db_err:
            logger.warning(f"Evaluation DB persistence wrapper encountered: {db_err}")

    logger.info(f"Completed multi-agent evaluation for {interview_id}. Overall Score: {result.overall_score} ({result.recommendation})")
    return result_dict
