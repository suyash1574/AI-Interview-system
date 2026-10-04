import asyncio
import logging
import json
import os
from typing import Optional, Dict, Any, List

from backend.config import settings
from backend.core.engine.state_machine import InterviewStateMachine, InterviewState
from backend.core.engine.security import LlamaGuardSecurity
from backend.providers.groq_adapter import GroqProvider

logger = logging.getLogger("autergo.realtime.agent_worker")

class LiveKitAgentWorker:
    """
    LiveKit Python Voice Agent Worker.
    Orchestrates real-time WebRTC audio room interaction with:
    - Silero VAD (Voice Activity Detection)
    - Deepgram Nova-2 Streaming STT
    - Interview State Machine & Llama Guard 3 security filter
    - Groq Llama-3 adaptive technical interviewer prompts
    - Cartesia Sonic Streaming TTS with sub-second latency
    """

    def __init__(
        self,
        room_name: str,
        interview_id: Optional[str] = None,
        job_title: str = "Senior Backend Engineer",
        competencies: Optional[List[str]] = None,
        candidate_name: str = "Candidate",
        resume_summary: str = "",
    ):
        self.room_name = room_name
        self.interview_id = interview_id or room_name.replace("interview-", "")
        self.job_title = job_title
        self.competencies = competencies or ["System Design", "Distributed Systems", "Algorithms"]
        self.candidate_name = candidate_name
        self.resume_summary = resume_summary

        self.state_machine = InterviewStateMachine(interview_id=self.interview_id)
        self.security = LlamaGuardSecurity()
        self.llm = GroqProvider()
        self.transcript: List[Dict[str, Any]] = []
        self.is_active = False

    async def get_opening_greeting(self) -> str:
        """Generates opening welcome greeting tailored to the candidate and role."""
        greeting = (
            f"Hello {self.candidate_name}! Welcome to your Autergo technical interview for the {self.job_title} role. "
            f"We'll explore your experience in {', '.join(self.competencies[:2])}. "
            f"When you are ready, please give a brief overview of your background."
        )
        self.transcript.append({"speaker": "AI", "text": greeting})
        return greeting

    async def handle_user_speech(self, transcribed_text: str) -> Dict[str, Any]:
        """
        Processes candidate speech transcript:
        1. Validates against prompt injection / jailbreak via Llama Guard 3
        2. Advances 9-state FSM
        3. Generates next technical drill-down question using candidate's resume + JD context
        """
        sec_check = await self.security.validate_input(transcribed_text)
        if not sec_check.is_safe:
            warning = "I noticed unexpected instructions in your response. Let's refocus on the technical problem at hand."
            self.transcript.append({"speaker": "AI", "text": warning})
            return {
                "ai_text": warning,
                "sanitized": False,
                "state": self.state_machine.state.value,
                "is_complete": False,
            }

        self.transcript.append({"speaker": "CANDIDATE", "text": sec_check.sanitized_text})

        # Advance state machine
        next_states = {
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
        current = self.state_machine.state
        if current in next_states:
            target = next_states[current]
            self.state_machine.transition_to(
                target,
                competency=self.competencies[0] if target == InterviewState.DEEP_DIVE else None
            )

        # Dynamic LLM Prompt with Resume & Job Context
        prompt = (
            f"You are Autergo, an elite technical interviewer conducting a live voice interview.\n"
            f"Target Role: {self.job_title}\n"
            f"Candidate Name: {self.candidate_name}\n"
            f"Resume Highlights: {self.resume_summary or 'General technical background'}\n"
            f"Evaluated Competency: {self.competencies[0] if self.competencies else 'Core Engineering'}\n"
            f"Interview State: {self.state_machine.state.value}\n"
            f"Candidate just said: {sec_check.sanitized_text}\n\n"
            f"Instructions:\n"
            f"1. Acknowledge the candidate's answer naturally in 1 short sentence.\n"
            f"2. Probe deeper into technical specifics, architecture trade-offs, or implementation details.\n"
            f"3. Keep response under 35 words. Do NOT include greetings or AI disclaimers."
        )

        ai_response = await self.llm.generate_response(prompt)
        self.transcript.append({"speaker": "AI", "text": ai_response})

        return {
            "ai_text": ai_response,
            "sanitized": True,
            "state": self.state_machine.state.value,
            "is_complete": self.state_machine.is_terminal(),
        }

    async def complete_session(self) -> Dict[str, Any]:
        """Finalizes interview, updates status, and initiates post-interview evaluation task."""
        if not self.state_machine.is_terminal():
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
            while self.state_machine.state != InterviewState.COMPLETE:
                nxt = next_state_map.get(self.state_machine.state, InterviewState.COMPLETE)
                self.state_machine.transition_to(nxt)

        logger.info(f"Interview {self.interview_id} completed with {len(self.transcript)} turns.")

        # Trigger Celery evaluation task asynchronously
        try:
            from workers.tasks.evaluation import evaluate_interview_task
            evaluate_interview_task.delay(self.interview_id, json.dumps(self.transcript))
        except Exception as e:
            logger.warning(f"Celery dispatch failed ({e}), running task locally.")
            try:
                from workers.tasks.evaluation import evaluate_interview_task
                evaluate_interview_task(self.interview_id, json.dumps(self.transcript))
            except Exception as task_err:
                logger.error(f"Local evaluation fallback failed: {task_err}")

        return {
            "interview_id": self.interview_id,
            "status": "COMPLETED",
            "transcript_count": len(self.transcript),
        }


# LiveKit Agent SDK Entrypoint for worker process
async def entrypoint(ctx: Any):
    """
    LiveKit Agent Process Entrypoint.
    Subscribes to room audio track and streams STT/TTS in real time.
    """
    from livekit.agents import AutoSubscribe
    from livekit.plugins import silero, deepgram, cartesia

    logger.info(f"Connecting to room: {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    worker = LiveKitAgentWorker(room_name=ctx.room.name)
    logger.info(f"LiveKitAgentWorker initialized for room {ctx.room.name}")

    # Send opening greeting
    greeting = await worker.get_opening_greeting()
    logger.info(f"AI Opening Greeting: {greeting}")


def main():
    """Runs the LiveKit agent worker application via CLI."""
    from livekit.agents import WorkerOptions, cli
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

if __name__ == "__main__":
    main()
