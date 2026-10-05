import asyncio
import logging
from typing import Optional, List, Dict, Any
from backend.config import settings
from backend.core.engine.state_machine import InterviewStateMachine, InterviewState
from backend.core.engine.security import LlamaGuardSecurity
from backend.providers.groq_adapter import GroqProvider
from backend.providers.deepgram_adapter import DeepgramSTTProvider
from backend.providers.cartesia_adapter import CartesiaTTSProvider

logger = logging.getLogger(__name__)

class LiveKitVoiceAgent:
    """
    LiveKit Real-time Voice Agent.
    Orchestrates the entire sub-second Voice-to-Voice interview loop:
    WebRTC Audio -> Deepgram Nova-2 STT -> Llama Guard 3 -> InterviewStateMachine -> Groq Llama-3 -> Cartesia Sonic TTS -> WebRTC Audio.
    """

    def __init__(
        self, 
        room_name: str, 
        interview_id: str, 
        job_title: str = "Senior Backend Engineer",
        competency: str = "System Design & Algorithms"
    ):
        self.room_name = room_name
        self.interview_id = interview_id
        self.job_title = job_title
        self.competency = competency

        # Core pipeline components
        self.state_machine = InterviewStateMachine(interview_id=interview_id)
        self.security = LlamaGuardSecurity()
        self.stt = DeepgramSTTProvider()
        self.llm = GroqProvider()
        self.tts = CartesiaTTSProvider()

        self.transcript: List[Dict[str, Any]] = []
        self.is_interrupted = False
        self.is_running = False

    async def start_session(self) -> bytes:
        """
        Initializes the interview session and generates opening greeting audio.
        """
        self.is_running = True
        logger.info(f"LiveKit Voice Agent starting session for room {self.room_name}")

        welcome_text = (
            f"Hello and welcome to your Autergo technical interview for the {self.job_title} role. "
            "When you are ready, please tell me about your background and core technical strengths."
        )
        self.transcript.append({"speaker": "AI", "text": welcome_text})

        # Synthesize opening question to audio bytes
        audio_bytes = await self.tts.synthesize_speech_bytes(welcome_text)
        return audio_bytes

    async def process_candidate_audio_turn(self, candidate_audio: bytes) -> Dict[str, Any]:
        """
        Executes one full voice-to-voice conversational turn:
        1. Transcribe candidate speech via Deepgram
        2. Audit against prompt injection via Llama Guard 3
        3. Step state machine
        4. Synthesize follow-up question via Groq LLM
        5. Convert to PCM audio via Cartesia TTS
        """
        if self.is_interrupted:
            self.is_interrupted = False

        # 1. STT: Transcribe audio
        candidate_text = await self.stt.transcribe_audio_bytes(candidate_audio)

        # 2. Guardrails: Validate safety
        sec_result = await self.security.validate_input(candidate_text)
        if not sec_result.is_safe:
            warning_text = "I noticed unusual directives in your answer. Let's refocus on the technical problem at hand."
            audio = await self.tts.synthesize_speech_bytes(warning_text)
            return {
                "transcription": candidate_text,
                "sanitized": False,
                "ai_response_text": warning_text,
                "ai_audio_bytes": audio,
                "state": self.state_machine.state.value,
            }

        # 3. Add to transcript
        self.transcript.append({"speaker": "CANDIDATE", "text": sec_result.sanitized_text})

        # 4. Advance State Machine via canonical progression
        self.state_machine.advance(
            competency=self.competency if self.state_machine.state == InterviewState.CORE else None
        )

        # 5. LLM: Adaptive Strategy Prompt
        prompt = (
            f"You are Autergo, an expert technical interviewer.\n"
            f"Context: Job: {self.job_title}. Competency: {self.competency}.\n"
            f"Current State: {self.state_machine.state.value}.\n"
            f"Candidate's last response: {sec_result.sanitized_text}\n"
            f"Instructions:\n"
            f"1. Acknowledge naturally in 1 sentence.\n"
            f"2. Ask a specific technical follow-up drill-down.\n"
            f"3. Keep under 40 words. Do NOT say 'As an AI'."
        )

        try:
            ai_reply = await asyncio.wait_for(
                self.llm.generate_response(prompt),
                timeout=2.5
            )
        except asyncio.TimeoutError:
            logger.warning("LLM response timed out in voice hot path, using fallback prompt.")
            ai_reply = f"Thank you for sharing that. Focusing now on {self.competency}, what key trade-offs did you consider in that approach?"

        self.transcript.append({"speaker": "AI", "text": ai_reply})

        # 6. TTS: Synthesize sub-100ms voice audio
        ai_audio = await self.tts.synthesize_speech_bytes(ai_reply)

        return {
            "transcription": sec_result.sanitized_text,
            "sanitized": True,
            "ai_response_text": ai_reply,
            "ai_audio_bytes": ai_audio,
            "state": self.state_machine.state.value,
            "is_complete": self.state_machine.is_terminal(),
        }

    def interrupt_ai(self):
        """Signals candidate barge-in to halt active TTS output."""
        self.is_interrupted = True
        logger.info(f"Barge-in interrupt signaled on session {self.room_name}")
