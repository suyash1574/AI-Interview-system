import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.providers.deepgram_adapter import DeepgramSTTProvider
from backend.providers.cartesia_adapter import CartesiaTTSProvider
from realtime.voice_agent import LiveKitVoiceAgent
from backend.core.engine.state_machine import InterviewState

@pytest.mark.asyncio
async def test_deepgram_mock_transcription():
    provider = DeepgramSTTProvider(api_key="mock_dg_key")
    result = await provider.transcribe_audio_bytes(b"dummy_bytes")
    assert "PostgreSQL" in result

@pytest.mark.asyncio
async def test_deepgram_api_call_mocked():
    provider = DeepgramSTTProvider(api_key="valid_test_key")
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": {
                "channels": [
                    {
                        "alternatives": [
                            {"transcript": "Hello, I specialize in distributed systems."}
                        ]
                    }
                ]
            }
        }
        mock_post.return_value = mock_response
        result = await provider.transcribe_audio_bytes(b"audio")
        assert result == "Hello, I specialize in distributed systems."

@pytest.mark.asyncio
async def test_cartesia_mock_synthesis():
    provider = CartesiaTTSProvider(api_key="mock_cartesia_key")
    audio = await provider.synthesize_speech_bytes("Hello world")
    assert audio.startswith(b"RIFF")

@pytest.mark.asyncio
async def test_cartesia_api_call_mocked():
    provider = CartesiaTTSProvider(api_key="valid_cartesia_key")
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"RIFF_MOCK_SYNTHESIZED_AUDIO"
        mock_post.return_value = mock_response
        audio = await provider.synthesize_speech_bytes("Tell me about indexing.")
        assert audio == b"RIFF_MOCK_SYNTHESIZED_AUDIO"

@pytest.mark.asyncio
async def test_livekit_voice_agent_start_session():
    agent = LiveKitVoiceAgent(room_name="room-123", interview_id="int-123", job_title="Staff Engineer")
    audio = await agent.start_session()
    assert agent.is_running is True
    assert len(agent.transcript) == 1
    assert agent.transcript[0]["speaker"] == "AI"
    assert "Staff Engineer" in agent.transcript[0]["text"]
    assert audio.startswith(b"RIFF")

@pytest.mark.asyncio
async def test_livekit_voice_agent_turn_processing():
    agent = LiveKitVoiceAgent(room_name="room-123", interview_id="int-123")
    
    # Mock LLM to avoid external Groq calls
    agent.llm.generate_response = AsyncMock(return_value="Could you explain your sharding strategy?")
    
    turn_result = await agent.process_candidate_audio_turn(b"dummy_candidate_audio")
    
    assert turn_result["sanitized"] is True
    assert "sharding" in turn_result["ai_response_text"]
    assert turn_result["ai_audio_bytes"].startswith(b"RIFF")
    assert agent.state_machine.state == InterviewState.DEVICE_CHECK

def test_livekit_voice_agent_interrupt():
    agent = LiveKitVoiceAgent(room_name="room-123", interview_id="int-123")
    assert agent.is_interrupted is False
    agent.interrupt_ai()
    assert agent.is_interrupted is True
