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
        llm_provider: Optional[Any] = None,
    ):
        self.room_name = room_name
        self.interview_id = interview_id or room_name.replace("interview-", "")
        self.job_title = job_title
        self.competencies = competencies or ["System Design", "Distributed Systems", "Algorithms"]
        self.candidate_name = candidate_name
        self.resume_summary = resume_summary

        self.state_machine = InterviewStateMachine(interview_id=self.interview_id)
        self.security = LlamaGuardSecurity()
        
        # Select LLM Provider: Local GGUF, NVIDIA NIM, Groq, or explicit injection
        if llm_provider is not None:
            self.llm = llm_provider
        else:
            from backend.providers import get_llm_provider
            self.llm = get_llm_provider()


        # Select STT & TTS Providers (Deepgram/Cartesia or Free Hugging Face Voice)
        from backend.providers.hf_audio_adapter import get_stt_provider, get_tts_provider
        self.stt = get_stt_provider()
        self.tts = get_tts_provider()

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

        # Advance state machine via canonical progression
        self.state_machine.advance(
            competency=self.competencies[0] if self.state_machine.state == InterviewState.CORE else None
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

        try:
            ai_response = await asyncio.wait_for(
                self.llm.generate_response(prompt),
                timeout=2.5
            )
        except asyncio.TimeoutError:
            logger.warning("LLM response timed out in hot path, providing dynamic fallback prompt.")
            ai_response = f"Understood. Moving forward to our assessment on {self.competencies[0] if self.competencies else 'architecture'}, can you walk me through your system design trade-offs?"

        self.transcript.append({"speaker": "AI", "text": ai_response})

        return {
            "ai_text": ai_response,
            "sanitized": True,
            "state": self.state_machine.state.value,
            "is_complete": self.state_machine.is_terminal(),
        }

    async def complete_session(self) -> Dict[str, Any]:
        """Finalizes interview, updates status, and initiates post-interview evaluation task."""
        self.state_machine.complete_all()

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


async def load_interview_context(interview_id: str) -> Dict[str, Any]:
    """Loads interview candidate, target job competencies, and resume summary from DB."""
    context = {
        "candidate_name": "Candidate",
        "job_title": "Senior Backend Engineer",
        "competencies": ["System Design", "Distributed Systems", "Algorithms"],
        "resume_summary": "Experienced engineer with backend background."
    }
    try:
        from database.session import AsyncSessionLocal
        from database.models import Interview, Job, Candidate, Resume
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            stmt = select(Interview).where(Interview.id == interview_id)
            res = await db.execute(stmt)
            interview = res.scalar_one_or_none()
            if interview:
                if interview.candidate_id:
                    cand_res = await db.execute(select(Candidate).where(Candidate.id == interview.candidate_id))
                    cand = cand_res.scalar_one_or_none()
                    if cand and cand.name:
                        context["candidate_name"] = cand.name

                if interview.job_id:
                    job_res = await db.execute(select(Job).where(Job.id == interview.job_id))
                    job = job_res.scalar_one_or_none()
                    if job and job.title:
                        context["job_title"] = job.title
                        if job.competencies and isinstance(job.competencies, list):
                            comp_names = [c.get("name") for c in job.competencies if isinstance(c, dict) and "name" in c]
                            if comp_names:
                                context["competencies"] = comp_names

                if interview.resume_id:
                    resume_res = await db.execute(select(Resume).where(Resume.id == interview.resume_id))
                    resume = resume_res.scalar_one_or_none()
                    if resume and resume.parsed_text:
                        preview = " ".join(resume.parsed_text.split()[:40])
                        context["resume_summary"] = f"Candidate Background: {preview}"
    except Exception as e:
        logger.warning(f"Could not load DB context for interview {interview_id} ({e}), using default context.")

    return context


# LiveKit Agent SDK Entrypoint for worker process
async def entrypoint(ctx: Any):
    """
    LiveKit Agent Process Entrypoint.
    Subscribes to candidate audio track, runs Silero VAD, streaming Deepgram STT,
    Llama Guard security check + Groq LLM reasoning, and streaming Cartesia TTS.
    """
    from livekit.agents import AutoSubscribe
    from livekit.agents.voice import Agent, AgentSession
    from livekit.plugins import silero, deepgram, cartesia

    logger.info(f"Connecting to LiveKit room: {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Extract interview ID and load DB context
    interview_id = ctx.room.name.replace("interview-", "")
    ctx_data = await load_interview_context(interview_id)

    worker = LiveKitAgentWorker(
        room_name=ctx.room.name,
        interview_id=interview_id,
        job_title=ctx_data["job_title"],
        competencies=ctx_data["competencies"],
        candidate_name=ctx_data["candidate_name"],
        resume_summary=ctx_data["resume_summary"],
    )
    logger.info(f"LiveKitAgentWorker initialized for {worker.candidate_name} ({worker.job_title})")

    # Initialize Voice Pipeline components
    try:
        vad = silero.VAD.load()
    except Exception:
        vad = None

    try:
        stt = deepgram.STT(model="nova-2", language="en")
    except Exception:
        stt = None

    try:
        tts = cartesia.TTS(model="sonic-english", voice="a0e99841-438c-4a64-b679-ae501e7d6091")
    except Exception:
        tts = None

    instructions = (
        f"You are Autergo, an elite technical interviewer conducting an adaptive engineering interview.\n"
        f"Target Role: {worker.job_title}\n"
        f"Candidate: {worker.candidate_name}\n"
        f"Competencies: {', '.join(worker.competencies)}\n"
        f"Acknowledge the candidate's responses naturally and probe deeper into architecture, code quality, and trade-offs."
    )

    agent = Agent(instructions=instructions)
    session = AgentSession(stt=stt, vad=vad, tts=tts)

    # Attach session to room
    try:
        await session.start(agent, room=ctx.room)
    except Exception as e:
        logger.warning(f"LiveKit AgentSession start ({e}), continuing in pipeline mode.")

    # Speak opening greeting
    greeting = await worker.get_opening_greeting()
    logger.info(f"AI Opening Greeting: {greeting}")
    try:
        await session.say(greeting)
    except Exception as e:
        logger.info(f"Voice output simulated ({e}): {greeting}")

    # Wire candidate speech turn handling into adaptive interview FSM
    async def on_candidate_speech_turn(transcribed_text: str):
        if not transcribed_text or not transcribed_text.strip():
            return
        logger.info(f"Candidate voice turn received: '{transcribed_text}'")
        result = await worker.handle_user_speech(transcribed_text)
        reply = result.get("ai_text")
        if reply:
            try:
                await session.say(reply)
            except Exception as e:
                logger.info(f"Voice reply output ({e}): {reply}")

        if result.get("is_complete"):
            logger.info("Interview finished all phases, completing session.")
            await worker.complete_session()

    try:
        @session.on("user_speech_committed")
        def on_user_speech(msg):
            text = getattr(msg, "content", None) or getattr(msg, "text", None) or str(msg)
            asyncio.create_task(on_candidate_speech_turn(text))
    except Exception as e:
        logger.warning(f"Could not bind user_speech_committed event listener: {e}")

    # Listen for participant disconnection to finalize interview and dispatch Celery evaluation
    @ctx.room.on("participant_disconnected")
    def on_participant_disconnected(participant):
        logger.info(f"Participant disconnected: {participant.identity}")
        asyncio.create_task(worker.complete_session())


def main():
    """Runs the LiveKit agent worker application via CLI."""
    from livekit.agents import WorkerOptions, cli
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

if __name__ == "__main__":
    main()
