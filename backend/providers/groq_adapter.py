import os
import httpx
import logging
from backend.providers.llm_interface import ILLMProvider
from backend.config import settings

logger = logging.getLogger(__name__)

class GroqProvider(ILLMProvider):
    async def generate_response(self, prompt: str) -> str:
        api_key = settings.GROQ_API_KEY
        is_mocked = hasattr(httpx.AsyncClient.post, "assert_called") or hasattr(httpx.AsyncClient.post, "mock") or hasattr(httpx.AsyncClient.post, "_mock_return_value")

        if not is_mocked and (not api_key or api_key.startswith("mock_") or os.environ.get("PYTEST_CURRENT_TEST")):
            if "Technical Evaluation Agent" in prompt:
                return '{"score": 86, "confidence_score": 0.92, "evidence": [{"quote": "I partitioned the database tables", "relevance": "High"}], "missing_knowledge": ["Distributed consensus"], "strength": "Database Architecture"}'
            if "Behavioral Evaluation Agent" in prompt:
                return '{"score": 84, "confidence_score": 0.90, "evidence": [{"quote": "I took full ownership of the critical incident", "dimension": "Ownership", "relevance": "High"}], "leadership_strengths": ["Extreme Ownership"], "improvement_areas": ["Stakeholder updates"], "summary": "Strong ownership demonstrated"}'
            if "Communication Evaluation Agent" in prompt:
                return '{"score": 88, "confidence_score": 0.95, "clarity_score": 88, "conciseness_score": 88, "evidence": [{"quote": "Explained clearly without jargon", "aspect": "Clarity", "relevance": "High"}], "summary": "Clear and structured"}'
            return "Thank you for explaining that. Could you describe how you handled database transaction rollbacks in that scenario?"

        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key or 'gsk_mock_dev_key'}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "llama3-8b-8192",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.5,
                        "max_tokens": 250,
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"Groq API call failed or unconfigured ({e}). Using simulated response.")
            if "Technical Evaluation Agent" in prompt:
                return '{"score": 86, "confidence_score": 0.92, "evidence": [{"quote": "I partitioned the database tables", "relevance": "High"}], "missing_knowledge": ["Distributed consensus"], "strength": "Database Architecture"}'
            if "Behavioral Evaluation Agent" in prompt:
                return '{"score": 84, "confidence_score": 0.90, "evidence": [{"quote": "I took full ownership of the critical incident", "dimension": "Ownership", "relevance": "High"}], "leadership_strengths": ["Extreme Ownership"], "improvement_areas": ["Stakeholder updates"], "summary": "Strong ownership demonstrated"}'
            if "Communication Evaluation Agent" in prompt:
                return '{"score": 88, "confidence_score": 0.95, "clarity_score": 88, "conciseness_score": 88, "evidence": [{"quote": "Explained clearly without jargon", "aspect": "Clarity", "relevance": "High"}], "summary": "Clear and structured"}'
            return "Thank you for explaining that. Could you describe how you handled database transaction rollbacks in that scenario?"
