from .llm_interface import ILLMProvider
class xAIProvider(ILLMProvider):
    async def generate_response(self, prompt: str) -> str:
        return "xai_stub"
