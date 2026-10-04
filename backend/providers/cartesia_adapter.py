import httpx
import json
import logging
import asyncio
from typing import Optional, AsyncGenerator
from backend.config import settings

logger = logging.getLogger(__name__)

class CartesiaTTSProvider:
    """
    Cartesia Sonic streaming text-to-speech provider adapter.
    Converts interviewer question tokens into sub-100ms PCM audio
    via REST and real-time streaming WebSocket.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.CARTESIA_API_KEY or "mock_cartesia_key"
        self.voice_id = "a0e99841-438c-4a64-b679-ae501e7d6091" # Conversational interviewer voice
        self.ws_endpoint = f"wss://api.cartesia.ai/tts/websocket?api_key={self.api_key}&cartesia_version=2024-06-10"

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

    async def stream_synthesize(
        self, text_stream: AsyncGenerator[str, None]
    ) -> AsyncGenerator[bytes, None]:
        """
        Streams text tokens over Cartesia WebSocket and yields real-time audio byte chunks.
        """
        if not self.api_key or self.api_key.startswith("mock_"):
            # Return simulated audio stream for testing/dev
            yield b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
            return

        try:
            import websockets
            import base64
            async with websockets.connect(self.ws_endpoint) as ws:
                async def sender():
                    async for token in text_stream:
                        msg = {
                            "context_id": "ctx-live",
                            "model_id": "sonic-english",
                            "transcript": token,
                            "voice": {"mode": "id", "id": self.voice_id},
                            "output_format": {
                                "container": "raw",
                                "encoding": "pcm_s16le",
                                "sample_rate": 24000
                            },
                            "continue": True
                        }
                        await ws.send(json.dumps(msg))
                    await ws.send(json.dumps({"context_id": "ctx-live", "continue": False}))

                send_task = asyncio.create_task(sender())
                try:
                    async for raw_msg in ws:
                        data = json.loads(raw_msg)
                        if "data" in data and data["data"]:
                            yield base64.b64decode(data["data"])
                        if data.get("done"):
                            break
                finally:
                    await send_task
        except Exception as e:
            logger.warning(f"Cartesia WebSocket streaming failed ({e}), returning fallback chunk.")
            yield b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
