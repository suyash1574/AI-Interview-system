from .llm_interface import ILLMProvider
class HuggingFaceProvider(ILLMProvider):
    async def generate_response(self, prompt: str) -> str:
        return "hf_stub"
