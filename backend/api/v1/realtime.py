import json
import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy import select

from backend.core.engine.state_machine import InterviewStateMachine, InterviewState
from backend.core.engine.security import LlamaGuardSecurity
from backend.providers.groq_adapter import GroqProvider
from database.session import AsyncSessionLocal
from database.models import Interview, Job, Candidate, Resume

logger = logging.getLogger(__name__)
router = APIRouter()

PROMPT_TEMPLATE = """You are Autergo, an expert technical interviewer evaluating a candidate for the {job_title} role.
Candidate Name: {candidate_name}
Resume Skills: {resume_skills}
Current Assessment Competency: {competency}
Current Interview Stage: {interview_state}
Candidate's Last Answer: {candidate_response}

Instructions:
1. Briefly acknowledge their response in 1 natural sentence.
2. Formulate a challenging, practical technical follow-up drill-down testing architecture, performance trade-offs, or system design.
3. Keep your total response under 40 words.
4. Do NOT say "As an AI".
"""

NEXT_STATE_MAP = {
    InterviewState.INIT: InterviewState.DEVICE_CHECK,
    InterviewState.DEVICE_CHECK: InterviewState.CONSENT,
    InterviewState.CONSENT: InterviewState.INTRODUCTION,
    InterviewState.INTRODUCTION: InterviewState.PROFILE,
    InterviewState.PROFILE: InterviewState.CORE,
    InterviewState.CORE: InterviewState.DEEP_DIVE,
    InterviewState.DEEP_DIVE: InterviewState.VALIDATION,
    InterviewState.VALIDATION: InterviewState.CLOSING,
    InterviewState.CLOSING: InterviewState.COMPLETE,
}

# Active session registries in-memory + Redis backing
class RealtimeSessionContext:
    def __init__(self, session_id: str, interview_id: Optional[str] = None):
        self.session_id = session_id
        self.interview_id = interview_id
        self.state_machine = InterviewStateMachine(interview_id=interview_id or session_id)
        self.security = LlamaGuardSecurity()
        self.llm = GroqProvider()
        self.transcript: List[Dict[str, str]] = []
        self.is_interrupted = False
        self.candidate_name = "Candidate"
        self.job_title = "Senior Software Engineer"
        self.competency = "System Design & Algorithms"
        self.resume_skills = "Distributed Systems, Python, SQL"

active_sessions: Dict[str, RealtimeSessionContext] = {}

async def save_session_to_redis(session_id: str, ctx: RealtimeSessionContext):
    """Persists session state into Redis hash for horizontal scaling across API pods."""
    try:
        import redis.asyncio as aioredis
        client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        payload = {
            "session_id": session_id,
            "interview_id": ctx.interview_id or "",
            "state": ctx.state_machine.state.value,
            "candidate_name": ctx.candidate_name,
            "job_title": ctx.job_title,
            "transcript": json.dumps(ctx.transcript),
        }
        await client.hset(f"autergo:session:{session_id}", mapping=payload)
        await client.expire(f"autergo:session:{session_id}", 86400)
        await client.aclose()
    except Exception as e:
        logger.debug(f"Redis session sync fallback (in-memory used): {e}")

async def load_session_from_redis(session_id: str, ctx: RealtimeSessionContext):
    """Restores session state from Redis if reconnecting or transferred between workers."""
    try:
        import redis.asyncio as aioredis
        client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        data = await client.hgetall(f"autergo:session:{session_id}")
        await client.aclose()
        if data:
            if "transcript" in data:
                ctx.transcript = json.loads(data["transcript"])
            if "candidate_name" in data:
                ctx.candidate_name = data["candidate_name"]
            if "job_title" in data:
                ctx.job_title = data["job_title"]
            if "state" in data:
                for s in InterviewState:
                    if s.value == data["state"]:
                        ctx.state_machine.state = s
                        break
    except Exception as e:
        logger.debug(f"Redis session restore fallback: {e}")

@router.websocket("/interview/{session_id}")
async def realtime_interview_ws(
    websocket: WebSocket,
    session_id: str,
    interview_id: Optional[str] = Query(None),
):
    await websocket.accept()

    ctx = RealtimeSessionContext(session_id=session_id, interview_id=interview_id)
    active_sessions[session_id] = ctx
    await load_session_from_redis(session_id, ctx)

    logger.info(f"WebSocket client connected to interview session: {session_id}")

    # Inject real Candidate, Job & Resume Context from Database
    if interview_id:
        try:
            async with AsyncSessionLocal() as db:
                stmt = select(Interview).where(Interview.id == interview_id)
                res = await db.execute(stmt)
                interview = res.scalar_one_or_none()
                if interview:
                    # Fetch Job details
                    job_stmt = select(Job).where(Job.id == interview.job_id)
                    job_res = await db.execute(job_stmt)
                    job = job_res.scalar_one_or_none()
                    if job:
                        ctx.job_title = job.title
                        if job.competencies and len(job.competencies) > 0:
                            comp_list = []
                            for c in job.competencies:
                                if isinstance(c, dict):
                                    comp_list.append(c.get("name", ""))
                                else:
                                    comp_list.append(str(c))
                            ctx.competency = ", ".join(filter(None, comp_list)) or ctx.competency

                    # Fetch Candidate details
                    cand_stmt = select(Candidate).where(Candidate.id == interview.candidate_id)
                    cand_res = await db.execute(cand_stmt)
                    candidate = cand_res.scalar_one_or_none()
                    if candidate:
                        ctx.candidate_name = candidate.name

                    # Fetch Resume skills
                    if interview.resume_id:
                        res_stmt = select(Resume).where(Resume.id == interview.resume_id)
                        res_res = await db.execute(res_stmt)
                        resume = res_res.scalar_one_or_none()
                        if resume and resume.extracted_skills:
                            skills = [
                                s.get("name", "") if isinstance(s, dict) else str(s)
                                for s in resume.extracted_skills
                            ]
                            ctx.resume_skills = ", ".join(filter(None, skills)) or ctx.resume_skills
        except Exception as e:
            logger.warning(f"Could not load database context for interview {interview_id}: {e}")

    # Send dynamic opening greeting
    welcome_text = (
        f"Hello {ctx.candidate_name}! Welcome to your Autergo technical interview for the {ctx.job_title} role. "
        f"When you are ready, please give a brief overview of your background and experience."
    )
    ctx.transcript.append({"speaker": "AI", "text": welcome_text})
    await websocket.send_json({
        "type": "ai_response",
        "text": welcome_text,
        "state": ctx.state_machine.state.value,
    })

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                message = json.loads(raw_data)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON format"})
                continue

            msg_type = message.get("type")

            # 1. Handle Barge-in / Interrupt
            if msg_type == "interrupt":
                ctx.is_interrupted = True
                await websocket.send_json({
                    "type": "interrupted",
                    "timestamp": message.get("timestamp"),
                })
                continue

            # 2. Handle Candidate Answer
            elif msg_type == "candidate_answer":
                ctx.is_interrupted = False
                candidate_text = message.get("text", "").strip()

                # Safety check via LlamaGuardSecurity
                sec_check = await ctx.security.validate_input(candidate_text)
                if not sec_check.is_safe:
                    await websocket.send_json({
                        "type": "error",
                        "code": "POLICY_VIOLATION",
                        "message": "Answer flagged by security filter. Please rephrase without system directives.",
                    })
                    continue

                # Add to transcript
                ctx.transcript.append({"speaker": "CANDIDATE", "text": sec_check.sanitized_text})
                await websocket.send_json({
                    "type": "transcript_partial",
                    "speaker": "CANDIDATE",
                    "text": sec_check.sanitized_text,
                })

                # Deterministically step state machine if not complete
                current = ctx.state_machine.state
                if current in NEXT_STATE_MAP:
                    target_state = NEXT_STATE_MAP[current]
                    ctx.state_machine.transition_to(
                        target_state,
                        competency=ctx.competency if target_state == InterviewState.DEEP_DIVE else None
                    )
                    await websocket.send_json(ctx.state_machine.build_state_change_event())

                # Generate AI response using dynamically injected strategy prompt
                prompt = PROMPT_TEMPLATE.format(
                    job_title=ctx.job_title,
                    candidate_name=ctx.candidate_name,
                    resume_skills=ctx.resume_skills,
                    competency=ctx.competency,
                    interview_state=ctx.state_machine.state.value,
                    candidate_response=sec_check.sanitized_text,
                )

                ai_reply = await ctx.llm.generate_response(prompt)

                if not ctx.is_interrupted:
                    ctx.transcript.append({"speaker": "AI", "text": ai_reply})
                    await websocket.send_json({
                        "type": "ai_response",
                        "text": ai_reply,
                        "state": ctx.state_machine.state.value,
                    })
                
                # Persist turn to Redis
                await save_session_to_redis(session_id, ctx)

            # 3. Handle Complete / Finish
            elif msg_type == "finish":
                if not ctx.state_machine.is_terminal():
                    while ctx.state_machine.state != InterviewState.COMPLETE:
                        next_state = NEXT_STATE_MAP.get(ctx.state_machine.state, InterviewState.COMPLETE)
                        ctx.state_machine.transition_to(next_state)

                await save_session_to_redis(session_id, ctx)

                # Persist final transcript to DB & trigger evaluation
                if ctx.interview_id:
                    try:
                        async with AsyncSessionLocal() as db:
                            stmt = select(Interview).where(Interview.id == ctx.interview_id)
                            res = await db.execute(stmt)
                            interview_rec = res.scalar_one_or_none()
                            if interview_rec:
                                interview_rec.transcript = ctx.transcript
                                interview_rec.status = "COMPLETED"
                                await db.commit()
                    except Exception as db_err:
                        logger.warning(f"Could not persist interview {ctx.interview_id} transcript: {db_err}")

                    # Trigger Celery / background evaluation
                    try:
                        from workers.tasks.evaluation import evaluate_interview_task
                        evaluate_interview_task.delay(ctx.interview_id, json.dumps(ctx.transcript))
                    except Exception as celery_err:
                        logger.warning(f"Celery dispatch failed ({celery_err}), evaluating directly.")
                        try:
                            from workers.tasks.evaluation import evaluate_interview_task
                            evaluate_interview_task(ctx.interview_id, json.dumps(ctx.transcript))
                        except Exception as eval_err:
                            logger.error(f"Fallback evaluation failed: {eval_err}")

                await websocket.send_json({
                    "type": "complete",
                    "message": "Interview finished successfully. Evaluation pipeline triggered.",
                    "transcript_length": len(ctx.transcript),
                })
                break

            else:
                await websocket.send_json({
                    "type": "error",
                    "code": "UNKNOWN_MESSAGE_TYPE",
                    "message": f"Unrecognized message type: {msg_type}"
                })

    except WebSocketDisconnect:
        logger.info(f"Client disconnected from session {session_id}")
    finally:
        active_sessions.pop(session_id, None)
