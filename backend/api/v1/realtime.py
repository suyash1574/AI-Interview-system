import json
import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from backend.core.engine.state_machine import InterviewStateMachine, InterviewState
from backend.core.engine.security import LlamaGuardSecurity
from backend.providers.groq_adapter import GroqProvider

logger = logging.getLogger(__name__)
router = APIRouter()

PROMPT_TEMPLATE = """You are Autergo, an expert technical interviewer.
Context: Job: {job_title}. Competency: {competency}.
Current State: {interview_state}.
Candidate's last response: {candidate_response}

Instructions:
1. Acknowledge the response naturally (max 1 sentence).
2. If evidence is missing, ask a specific drill-down question.
3. Keep your total response under 40 words.
4. Do NOT say "As an AI".
"""

# Active session registries in-memory
class RealtimeSessionContext:
    def __init__(self, session_id: str, interview_id: Optional[str] = None):
        self.session_id = session_id
        self.interview_id = interview_id
        self.state_machine = InterviewStateMachine(interview_id=interview_id or session_id)
        self.security = LlamaGuardSecurity()
        self.llm = GroqProvider()
        self.transcript: List[Dict[str, str]] = []
        self.is_interrupted = False
        self.job_title = "Software Engineer"
        self.competency = "System Design & Algorithms"

active_sessions: Dict[str, RealtimeSessionContext] = {}

@router.websocket("/interview/{session_id}")
async def realtime_interview_ws(
    websocket: WebSocket,
    session_id: str,
    interview_id: Optional[str] = Query(None),
):
    await websocket.accept()

    ctx = RealtimeSessionContext(session_id=session_id, interview_id=interview_id)
    active_sessions[session_id] = ctx

    logger.info(f"WebSocket client connected to interview session: {session_id}")

    # Send initial greeting
    welcome_text = "Hello! Welcome to your Autergo technical interview. When you are ready, please introduce yourself and your background."
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
            except Exception:
                await websocket.send_json({"type": "error", "code": "INVALID_JSON", "message": "Payload must be JSON"})
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
                # Sequence: INIT -> DEVICE_CHECK -> CONSENT -> INTRODUCTION -> PROFILE -> CORE -> DEEP_DIVE -> VALIDATION -> CLOSING -> COMPLETE
                current = ctx.state_machine.state
                next_state_map = {
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

                if current in next_state_map:
                    target_state = next_state_map[current]
                    ctx.state_machine.transition_to(
                        target_state,
                        competency=ctx.competency if target_state == InterviewState.DEEP_DIVE else None
                    )
                    await websocket.send_json(ctx.state_machine.build_state_change_event())

                # Generate AI response using strategy prompt
                prompt = PROMPT_TEMPLATE.format(
                    job_title=ctx.job_title,
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

            # 3. Handle Complete / Finish
            elif msg_type == "finish":
                if not ctx.state_machine.is_terminal():
                    while ctx.state_machine.state != InterviewState.COMPLETE:
                        next_state = next_state_map.get(ctx.state_machine.state, InterviewState.COMPLETE)
                        ctx.state_machine.transition_to(next_state)

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
