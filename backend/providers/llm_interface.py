from abc import ABC, abstractmethod

class ILLMProvider(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str) -> str:
        pass
