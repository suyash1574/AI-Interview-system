import httpx
import logging
from typing import Optional, AsyncGenerator
from backend.config import settings

logger = logging.getLogger(__name__)

class CartesiaTTSProvider:
    """
    Cartesia Sonic streaming text-to-speech provider adapter.
    Converts interviewer question tokens into sub-100ms PCM audio.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.CARTESIA_API_KEY or "mock_cartesia_key"
        self.voice_id = "a0e99841-438c-4a64-b679-ae501e7d6091" # Conversational interviewer voice

    async def synthesize_speech_bytes(self, text: str) -> bytes:
        if not self.api_key or self.api_key.startswith("mock_"):
            logger.info("Using simulated Cartesia Sonic TTS audio generation")
            # Return dummy valid WAV header / PCM bytes
            return b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"

        headers = {
            "X-API-Key": self.api_key,
            "Cartesia-Version": "2024-06-10",
            "Content-Type": "application/json"
        }
        payload = {
            "model_id": "sonic-english",
            "transcript": text,
            "voice": {
                "mode": "id",
                "id": self.voice_id
            },
            "output_format": {
                "container": "wav",
                "encoding": "pcm_s16le",
                "sample_rate": 24000
            }
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    "https://api.cartesia.ai/tts/bytes",
                    headers=headers,
                    json=payload
                )
                res.raise_for_status()
                return res.content
        except Exception as e:
            logger.warning(f"Cartesia API request failed ({e}). Returning fallback audio.")
            return b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
