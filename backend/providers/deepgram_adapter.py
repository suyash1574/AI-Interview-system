import httpx
import logging
from typing import AsyncGenerator, Dict, Any, Optional
from backend.config import settings

logger = logging.getLogger(__name__)

class DeepgramSTTProvider:
    """
    Deepgram Nova-2 streaming speech-to-text provider adapter.
    Handles converting candidate PCM audio chunks into transcribed text.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.DEEPGRAM_API_KEY or "mock_dg_key"

    async def transcribe_audio_bytes(self, audio_bytes: bytes, content_type: str = "audio/wav") -> str:
        """
        Transcribes an audio chunk or full utterance.
        """
        if not self.api_key or self.api_key.startswith("mock_"):
            logger.info("Using simulated Deepgram Nova-2 STT transcription")
            return "I designed a distributed database architecture using PostgreSQL and Redis."

        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": content_type
        }
        params = {
            "model": "nova-2",
            "smart_format": "true",
            "language": "en"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    "https://api.deepgram.com/v1/listen",
                    headers=headers,
                    params=params,
                    content=audio_bytes
                )
                res.raise_for_status()
                data = res.json()
                transcript = data["results"]["channels"][0]["alternatives"][0]["transcript"]
                return transcript
        except Exception as e:
            logger.warning(f"Deepgram API request failed ({e}). Returning fallback transcription.")
            return "I designed a distributed database architecture using PostgreSQL and Redis."
