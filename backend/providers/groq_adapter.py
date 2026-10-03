import httpx
import logging
from backend.providers.llm_interface import ILLMProvider
from backend.config import settings

logger = logging.getLogger(__name__)

class GroqProvider(ILLMProvider):
    async def generate_response(self, prompt: str) -> str:
        api_key = settings.GROQ_API_KEY or "gsk_fallback_dev_key"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "llama3-8b-8192",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.5,
                        "max_tokens": 150,
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"Groq API call failed or unconfigured ({e}). Using simulated response.")
            return "Thank you for explaining that. Could you describe how you handled database transaction rollbacks in that scenario?"
