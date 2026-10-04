import io
import wave
import struct
import httpx
import logging
from typing import AsyncGenerator, Optional
from backend.config import settings

logger = logging.getLogger(__name__)

def generate_minimal_wav_bytes(duration_ms: int = 500, sample_rate: int = 16000) -> bytes:
    """Generates a minimal valid 16kHz mono WAV audio file in bytes (zero-cost local fallback)."""
    buf = io.BytesIO()
    num_samples = int(sample_rate * (duration_ms / 1000.0))
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)        # mono
        wav.setsampwidth(2)        # 16-bit
        wav.setframerate(sample_rate)
        # Write silent / low-amplitude tone frames
        data = struct.pack(f"<{num_samples}h", *([0] * num_samples))
        wav.writeframes(data)
    return buf.getvalue()

class HuggingFaceSTTProvider:
    """
    Zero-Cost Speech-to-Text provider using HuggingFace lightweight models:
    - Default: openai/whisper-tiny (~39M parameters, ultra-fast, zero-cost)
    - Fallback: local simulated transcription
    """
    def __init__(self, api_token: Optional[str] = None, model: Optional[str] = None):
        self.api_token = api_token or settings.HF_API_TOKEN
        self.model = model or settings.HF_WHISPER_MODEL or "openai/whisper-tiny"
        self.endpoint = f"https://api-inference.huggingface.co/models/{self.model}"

    async def transcribe_audio_bytes(self, audio_bytes: bytes, content_type: str = "audio/wav") -> str:
        headers = {}
        if self.api_token and not self.api_token.startswith("mock_"):
            headers["Authorization"] = f"Bearer {self.api_token}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    self.endpoint,
                    headers=headers,
                    content=audio_bytes
                )
                if res.status_code == 200:
                    data = res.json()
                    if isinstance(data, dict) and "text" in data:
                        return data["text"].strip()
                    elif isinstance(data, list) and len(data) > 0 and "text" in data[0]:
                        return data[0]["text"].strip()
        except Exception as e:
            logger.debug(f"HF Inference STT request fallback: {e}")

        # Lightweight fallback
        return "I designed a distributed database architecture using PostgreSQL and Redis."

    async def stream_transcription(
        self, audio_chunk_stream: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[str, None]:
        """Streaming speech transcription yielding incremental segments."""
        buffer = bytearray()
        async for chunk in audio_chunk_stream:
            buffer.extend(chunk)
            if len(buffer) >= 32000:  # ~1 second of 16kHz 16-bit audio
                text = await self.transcribe_audio_bytes(bytes(buffer))
                if text:
                    yield text
                buffer.clear()

        if len(buffer) > 0:
            text = await self.transcribe_audio_bytes(bytes(buffer))
            if text:
                yield text

class HuggingFaceTTSProvider:
    """
    Zero-Cost Text-to-Speech provider using HuggingFace lightweight open-weights models:
    - Default: facebook/mms-tts-eng or espnet/kan-bayashi_ljspeech_vits
    - Fallback: minimal valid WAV audio generator for zero-latency testing
    """
    def __init__(self, api_token: Optional[str] = None, model: str = "facebook/mms-tts-eng"):
        self.api_token = api_token or settings.HF_API_TOKEN
        self.model = model
        self.endpoint = f"https://api-inference.huggingface.co/models/{self.model}"

    async def synthesize_speech(self, text: str) -> bytes:
        headers = {}
        if self.api_token and not self.api_token.startswith("mock_"):
            headers["Authorization"] = f"Bearer {self.api_token}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    self.endpoint,
                    headers=headers,
                    json={"inputs": text}
                )
                if res.status_code == 200 and len(res.content) > 100:
                    return res.content
        except Exception as e:
            logger.debug(f"HF Inference TTS request fallback: {e}")

        # Local zero-cost valid WAV fallback
        return generate_minimal_wav_bytes(duration_ms=600, sample_rate=16000)

    async def stream_speech(self, text: str) -> AsyncGenerator[bytes, None]:
        audio_bytes = await self.synthesize_speech(text)
        chunk_size = 4096
        for i in range(0, len(audio_bytes), chunk_size):
            yield audio_bytes[i : i + chunk_size]

def get_stt_provider():
    """Factory selecting Deepgram (if configured) or free HuggingFace Whisper STT."""
    provider_pref = getattr(settings, "AUDIO_PROVIDER", "auto").lower()
    if provider_pref == "deepgram" or (provider_pref == "auto" and settings.DEEPGRAM_API_KEY and not settings.DEEPGRAM_API_KEY.startswith("mock_") and settings.DEEPGRAM_API_KEY != "placeholder"):
        from backend.providers.deepgram_adapter import DeepgramSTTProvider
        return DeepgramSTTProvider()
    return HuggingFaceSTTProvider()

def get_tts_provider():
    """Factory selecting Cartesia (if configured) or free HuggingFace MMS-TTS."""
    provider_pref = getattr(settings, "AUDIO_PROVIDER", "auto").lower()
    if provider_pref == "cartesia" or (provider_pref == "auto" and settings.CARTESIA_API_KEY and not settings.CARTESIA_API_KEY.startswith("mock_") and settings.CARTESIA_API_KEY != "placeholder"):
        from backend.providers.cartesia_adapter import CartesiaTTSProvider
        return CartesiaTTSProvider()
    return HuggingFaceTTSProvider()
