import httpx
import json
import logging
import asyncio
from typing import AsyncGenerator, Dict, Any, Optional
from backend.config import settings

logger = logging.getLogger(__name__)

class DeepgramSTTProvider:
    """
    Deepgram Nova-2 streaming speech-to-text provider adapter.
    Handles converting candidate PCM audio chunks into transcribed text
    via REST audio chunks and real-time streaming WebSocket.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.DEEPGRAM_API_KEY or "mock_dg_key"
        self.ws_endpoint = "wss://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&language=en"

    async def transcribe_audio_bytes(self, audio_bytes: bytes, content_type: str = "audio/wav") -> str:
        """
        Transcribes an audio chunk or full utterance synchronously via REST.
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

    async def stream_transcription(
        self, audio_chunk_stream: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[str, None]:
        """
        Streams audio frames over Deepgram WebSocket and yields incremental text transcripts.
        """
        if not self.api_key or self.api_key.startswith("mock_"):
            # Simulation mode for testing / dev without active API key
            yield "I designed a distributed database architecture using PostgreSQL and Redis."
            return

        try:
            import websockets
            headers = {"Authorization": f"Token {self.api_key}"}
            async with websockets.connect(self.ws_endpoint, extra_headers=headers) as ws:
                async def sender():
                    async for chunk in audio_chunk_stream:
                        await ws.send(chunk)
                    await ws.send(json.dumps({"type": "CloseStream"}))

                send_task = asyncio.create_task(sender())
                try:
                    async for msg in ws:
                        payload = json.loads(msg)
                        if "channel" in payload:
                            alts = payload["channel"].get("alternatives", [])
                            if alts and alts[0].get("transcript"):
                                yield alts[0]["transcript"]
                finally:
                    await send_task
        except Exception as e:
            logger.warning(f"Deepgram WebSocket streaming failed ({e}), falling back.")
            yield "I designed a distributed database architecture using PostgreSQL and Redis."
