import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from backend.api.v1.sessions import router
from backend.config import settings

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_create_livekit_token_success(monkeypatch):
    monkeypatch.setattr(settings, "LIVEKIT_API_KEY", "test_key")
    monkeypatch.setattr(settings, "LIVEKIT_API_SECRET", "test_secret")

    response = client.post(
        "/livekit-token",
        json={
            "room_name": "test_room",
            "participant_name": "test_user",
            "participant_identity": "user_123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert isinstance(data["token"], str)
    assert len(data["token"]) > 0

def test_create_livekit_token_missing_credentials(monkeypatch):
    monkeypatch.setattr(settings, "LIVEKIT_API_KEY", "")
    monkeypatch.setattr(settings, "LIVEKIT_API_SECRET", "")

    response = client.post(
        "/livekit-token",
        json={
            "room_name": "test_room",
            "participant_name": "test_user",
            "participant_identity": "user_123"
        }
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "LiveKit credentials are not configured"
