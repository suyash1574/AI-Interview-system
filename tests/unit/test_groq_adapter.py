import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
from backend.providers.groq_adapter import GroqProvider

@pytest.mark.asyncio
async def test_groq_provider_generate_response():
    provider = GroqProvider()
    prompt = "Hello!"
    expected_response = "Hi there!"

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": expected_response
                }
            }
        ]
    }

    mock_post = AsyncMock(return_value=mock_response)
    
    with patch("httpx.AsyncClient.post", mock_post):
        response = await provider.generate_response(prompt)
        
        assert response == expected_response
        mock_post.assert_called_once()
