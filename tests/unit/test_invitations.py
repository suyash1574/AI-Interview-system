import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from backend.api.v1.invitations import router
from backend.core.services.tokens import generate_guest_token
import jwt
from backend.config import settings

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_generate_guest_token():
    token = generate_guest_token("cand_123", "int_456")
    payload = jwt.decode(token, settings.GUEST_SECRET_KEY, algorithms=["HS256"])
    assert payload["sub"] == "cand_123"
    assert payload["interview_id"] == "int_456"

def test_generate_endpoint():
    response = client.post(
        "/invitations/generate",
        json={"candidate_id": "cand_123", "interview_id": "int_456"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    
    token = data["token"]
    payload = jwt.decode(token, settings.GUEST_SECRET_KEY, algorithms=["HS256"])
    assert payload["sub"] == "cand_123"
    assert payload["interview_id"] == "int_456"
