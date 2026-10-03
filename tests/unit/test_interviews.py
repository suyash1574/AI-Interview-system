import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.dependencies.auth import get_current_user, CurrentUser, get_actor, AuthActor
from backend.dependencies.db import get_tenant_db
from database.models import Job, Candidate, Interview

@pytest.fixture
def mock_recruiter():
    return CurrentUser(user_id="rec-1", tenant_id="tenant-1", role="RECRUITER")

@pytest.fixture
def mock_actor_candidate():
    return AuthActor(id="cand-1", role="CANDIDATE", interview_id="int-1", is_candidate=True)

@pytest.fixture
def mock_db():
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.flush = AsyncMock()
    return session

def test_create_interview_success(mock_recruiter, mock_db):
    app.dependency_overrides[get_current_user] = lambda: mock_recruiter
    app.dependency_overrides[get_tenant_db] = lambda: mock_db

    fake_job = Job(id="job-1", tenant_id="tenant-1", title="Backend Dev", competencies=[])
    
    # Mock job query result
    mock_job_res = MagicMock()
    mock_job_res.scalar_one_or_none.return_value = fake_job

    # Mock candidate query result (None -> creates new candidate)
    mock_cand_res = MagicMock()
    mock_cand_res.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [mock_job_res, mock_cand_res]

    client = TestClient(app)
    response = client.post(
        "/api/v1/interviews",
        json={
            "job_id": "job-1",
            "candidate_name": "Jane Doe",
            "candidate_email": "jane@example.com"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["job_id"] == "job-1"
    assert data["candidate_email"] == "jane@example.com"
    assert data["status"] == "PENDING"
    assert "guest_token" in data
    assert mock_db.commit.called

    app.dependency_overrides.clear()

def test_initiate_session_success(mock_actor_candidate, mock_db):
    app.dependency_overrides[get_actor] = lambda: mock_actor_candidate
    app.dependency_overrides[get_tenant_db] = lambda: mock_db

    fake_interview = Interview(
        id="int-1",
        tenant_id="tenant-1",
        job_id="job-1",
        candidate_id="cand-1",
        status="PENDING",
    )
    mock_int_res = MagicMock()
    mock_int_res.scalar_one_or_none.return_value = fake_interview
    mock_db.execute.return_value = mock_int_res

    client = TestClient(app)
    response = client.post("/api/v1/interviews/int-1/session")

    assert response.status_code == 200
    data = response.json()
    assert data["interview_id"] == "int-1"
    assert "livekit_token" in data
    assert "/api/v1/realtime/interview/" in data["ws_url"]

    app.dependency_overrides.clear()

def test_initiate_session_unauthorized_candidate(mock_db):
    # Candidate trying to access a different interview
    wrong_candidate = AuthActor(id="cand-2", role="CANDIDATE", interview_id="int-999", is_candidate=True)
    app.dependency_overrides[get_actor] = lambda: wrong_candidate
    app.dependency_overrides[get_tenant_db] = lambda: mock_db

    fake_interview = Interview(
        id="int-1",
        tenant_id="tenant-1",
        job_id="job-1",
        candidate_id="cand-1",
        status="PENDING",
    )
    mock_int_res = MagicMock()
    mock_int_res.scalar_one_or_none.return_value = fake_interview
    mock_db.execute.return_value = mock_int_res

    client = TestClient(app)
    response = client.post("/api/v1/interviews/int-1/session")

    assert response.status_code == 403
    assert "Candidate not authorized" in response.json()["detail"]

    app.dependency_overrides.clear()
