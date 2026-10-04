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

def test_verify_token_endpoint():
    from unittest.mock import AsyncMock, MagicMock
    from backend.dependencies.db import get_tenant_db
    from database.models import Invitation, Candidate, Drive, Job

    mock_db = AsyncMock()
    fake_inv = Invitation(id="inv-1", token="valid-tok", candidate_id="cand-1", drive_id="drv-1", email="c@test.com", status="SENT")
    fake_cand = Candidate(id="cand-1", name="Sarah Connor", email="c@test.com")
    fake_drv = Drive(id="drv-1", name="Senior Backend Drive", job_id="job-1")
    fake_job = Job(id="job-1", title="Staff Engineer")

    res_inv = MagicMock()
    res_inv.scalar_one_or_none.return_value = fake_inv

    res_cand = MagicMock()
    res_cand.scalar_one_or_none.return_value = fake_cand

    res_drv = MagicMock()
    res_drv.scalar_one_or_none.return_value = fake_drv

    res_job = MagicMock()
    res_job.scalar_one_or_none.return_value = fake_job

    mock_db.execute.side_effect = [res_inv, res_cand, res_drv, res_job]

    app.dependency_overrides[get_tenant_db] = lambda: mock_db
    test_client = TestClient(app)

    resp = test_client.get("/invitations/verify/valid-tok")
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["candidate_name"] == "Sarah Connor"
    assert data["job_title"] == "Staff Engineer"
    assert data["status"] == "OPENED"

    app.dependency_overrides.clear()
