from .llm_interface import ILLMProvider
class OpenRouterProvider(ILLMProvider):
    async def generate_response(self, prompt: str) -> str:
        return "openrouter_stub"
