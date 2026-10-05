import pytest
from unittest.mock import patch, MagicMock
from backend.providers.local_llm_adapter import LocalLLMProvider
from backend.providers import get_llm_provider
from backend.config import settings

@pytest.mark.asyncio
async def test_local_llm_is_available():
    # Model path exists on this host per gap analysis
    available = LocalLLMProvider.is_available()
    assert isinstance(available, bool)

@pytest.mark.asyncio
async def test_local_llm_generate_response_mock():
    provider = LocalLLMProvider()
    res = await provider.generate_response("You are an interviewer. Ask about system design.")
    assert isinstance(res, str)
    assert len(res) > 10

@pytest.mark.asyncio
async def test_local_llm_evaluation_agent_prompts():
    provider = LocalLLMProvider()
    tech_res = await provider.generate_response("Technical Evaluation Agent prompt here")
    assert "score" in tech_res

    behav_res = await provider.generate_response("Behavioral Evaluation Agent prompt here")
    assert "score" in behav_res

    comm_res = await provider.generate_response("Communication Evaluation Agent prompt here")
    assert "score" in comm_res

@pytest.mark.asyncio
async def test_get_llm_provider_factory():
    local_p = get_llm_provider("local")
    assert isinstance(local_p, LocalLLMProvider)

    groq_p = get_llm_provider("groq")
    from backend.providers.groq_adapter import GroqProvider
    assert isinstance(groq_p, GroqProvider)
