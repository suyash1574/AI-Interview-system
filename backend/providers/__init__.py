from typing import Optional
from backend.config import settings
from backend.providers.llm_interface import ILLMProvider
from backend.providers.groq_adapter import GroqProvider
from backend.providers.nvidia_adapter import NVIDIAProvider
from backend.providers.local_llm_adapter import LocalLLMProvider
from backend.providers.classification_adapter import ClassificationProvider

def get_llm_provider(preferred_provider: Optional[str] = None) -> ILLMProvider:
    """
    Factory function to resolve the active LLM provider.
    Order: Groq -> NVIDIA -> Local (last resort).
    - 'local': Local GGUF via llama-cpp-python (e.g. Qwen 2.5 Coder 1.5B)
    - 'groq': Ultra-low latency cloud Llama 3 via Groq
    - 'nvidia': Enterprise cloud NIM Llama 3.3 70B
    - 'auto': Groq (if key), else NVIDIA (if key), else Local (if GGUF on disk), else Groq stub
    ponytail: local is intentionally LAST — cloud models have better quality/latency;
    local GGUF exists only for offline/cost-zero fallback, not primary.
    """
    provider_name = (preferred_provider or getattr(settings, "LLM_PROVIDER", "auto")).lower()

    if provider_name == "local":
        return LocalLLMProvider()

    if provider_name == "nvidia":
        return NVIDIAProvider()

    if provider_name == "groq":
        return GroqProvider()

    # Automatic selection strategy: cloud first, local last.
    if getattr(settings, "GROQ_API_KEY", ""):
        return GroqProvider()

    if getattr(settings, "NVIDIA_API_KEY", ""):
        return NVIDIAProvider()

    if LocalLLMProvider.is_available():
        return LocalLLMProvider()

    # Default fallback (stub response inside GroqProvider, no crash)
    return GroqProvider()

__all__ = [
    "ILLMProvider",
    "GroqProvider",
    "NVIDIAProvider",
    "LocalLLMProvider",
    "ClassificationProvider",
    "get_llm_provider",
]
