import pytest
import json
from unittest.mock import patch, MagicMock
from backend.providers.nvidia_adapter import NVIDIAProvider

@pytest.mark.asyncio
async def test_nvidia_generate_response_live_mock():
    provider = NVIDIAProvider(api_key="nvapi-test-key", model="meta/llama-3.3-70b-instruct")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "Can you explain how you handled distributed transactions?"
                }
            }
        ]
    }

    with patch("httpx.AsyncClient.post", return_value=mock_resp) as mock_post:
        res = await provider.generate_response("Test prompt")
        assert "distributed transactions" in res
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer nvapi-test-key"
        assert kwargs["json"]["model"] == "meta/llama-3.3-70b-instruct"

@pytest.mark.asyncio
async def test_nvidia_generate_response_evaluation_fallback():
    provider = NVIDIAProvider(api_key="mock_key")
    prompt = "You are the Technical Evaluation Agent for this interview."
    res = await provider.generate_response(prompt)
    data = json.loads(res)
    assert data["score"] >= 80
    assert "confidence_score" in data
    assert "evidence" in data
