import pytest
from unittest.mock import patch, MagicMock
from backend.providers.hf_audio_adapter import (
    HuggingFaceSTTProvider,
    HuggingFaceTTSProvider,
    generate_minimal_wav_bytes,
    get_stt_provider,
    get_tts_provider
)

def test_generate_minimal_wav_bytes():
    wav = generate_minimal_wav_bytes(duration_ms=200, sample_rate=16000)
    assert len(wav) > 44  # Has WAV header + data
    assert wav[:4] == b"RIFF"
    assert wav[8:12] == b"WAVE"

@pytest.mark.asyncio
async def test_hf_stt_transcription_mock():
    stt = HuggingFaceSTTProvider(api_token="hf_mock_token")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"text": "I implemented caching using Redis."}

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        res = await stt.transcribe_audio_bytes(b"dummy_audio_bytes")
        assert "implemented caching" in res

@pytest.mark.asyncio
async def test_hf_stt_transcription_fallback():
    stt = HuggingFaceSTTProvider()
    with patch("httpx.AsyncClient.post", side_effect=Exception("Network error")):
        res = await stt.transcribe_audio_bytes(b"dummy_audio_bytes")
        assert len(res) > 0

@pytest.mark.asyncio
async def test_hf_tts_synthesis_mock():
    tts = HuggingFaceTTSProvider(api_token="hf_mock_token")
    fake_wav = generate_minimal_wav_bytes(100)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = fake_wav

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        audio = await tts.synthesize_speech("Hello candidate")
        assert len(audio) > 44

@pytest.mark.asyncio
async def test_hf_tts_stream_speech():
    tts = HuggingFaceTTSProvider()
    chunks = []
    async for chunk in tts.stream_speech("Tell me about yourself."):
        chunks.append(chunk)
    assert len(chunks) > 0
    full_audio = b"".join(chunks)
    assert full_audio[:4] == b"RIFF"

def test_provider_factories():
    stt = get_stt_provider()
    tts = get_tts_provider()
    assert stt is not None
    assert tts is not None
