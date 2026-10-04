from .llm_interface import ILLMProvider
from .hf_audio_adapter import (
    HuggingFaceSTTProvider,
    HuggingFaceTTSProvider,
    get_stt_provider,
    get_tts_provider,
)

class HuggingFaceProvider(ILLMProvider):
    async def generate_response(self, prompt: str) -> str:
        return "I designed a scalable microservices architecture with Redis pub/sub and PostgreSQL."

__all__ = [
    "HuggingFaceProvider",
    "HuggingFaceSTTProvider",
    "HuggingFaceTTSProvider",
    "get_stt_provider",
    "get_tts_provider",
]
