from .llm_interface import ILLMProvider
class NVIDIAProvider(ILLMProvider):
    async def generate_response(self, prompt: str) -> str:
        return "nvidia_stub"
