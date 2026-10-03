import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.dependencies.auth import get_current_user, CurrentUser
from backend.dependencies.db import get_tenant_db
from database.models import Drive, Job

@pytest.fixture
def mock_recruiter():
    return CurrentUser(user_id="rec-1", tenant_id="tenant-1", role="RECRUITER")

@pytest.fixture
def mock_db():
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.flush = AsyncMock()
    return session

def test_create_drive_endpoint(mock_recruiter, mock_db):
    app.dependency_overrides[get_current_user] = lambda: mock_recruiter
    app.dependency_overrides[get_tenant_db] = lambda: mock_db

    fake_job = Job(id="job-1", tenant_id="tenant-1", title="Platform Engineer", competencies=[])
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = fake_job
    mock_db.execute.return_value = mock_res

    client = TestClient(app)
    response = client.post(
        "/api/v1/drives",
        json={
            "name": "Q4 Platform Hiring Drive",
            "job_id": "job-1",
            "pass_threshold": 75,
            "config": {"duration_minutes": 30}
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Q4 Platform Hiring Drive"
    assert data["job_id"] == "job-1"
    assert data["pass_threshold"] == 75
    assert mock_db.commit.called

    app.dependency_overrides.clear()

def test_list_drives_endpoint(mock_recruiter, mock_db):
    app.dependency_overrides[get_current_user] = lambda: mock_recruiter
    app.dependency_overrides[get_tenant_db] = lambda: mock_db

    fake_drive = Drive(
        id="drive-1",
        tenant_id="tenant-1",
        job_id="job-1",
        name="Backend Hiring",
        status="ACTIVE",
        pass_threshold=70,
        config={},
    )
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = [fake_drive]
    mock_db.execute.return_value = mock_res

    client = TestClient(app)
    response = client.get("/api/v1/drives")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Backend Hiring"

    app.dependency_overrides.clear()

def test_invite_candidates_to_drive(mock_recruiter, mock_db):
    app.dependency_overrides[get_current_user] = lambda: mock_recruiter
    app.dependency_overrides[get_tenant_db] = lambda: mock_db

    fake_drive = Drive(
        id="drive-1",
        tenant_id="tenant-1",
        job_id="job-1",
        name="Backend Hiring",
    )
    mock_drive_res = MagicMock()
    mock_drive_res.scalar_one_or_none.return_value = fake_drive

    mock_cand_res = MagicMock()
    mock_cand_res.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [mock_drive_res, mock_cand_res]

    client = TestClient(app)
    response = client.post(
        "/api/v1/drives/drive-1/invitations",
        json={
            "candidates": [
                {"name": "Alice Candidate", "email": "alice@example.com"}
            ]
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    assert data[0]["candidate_name"] == "Alice Candidate"
    assert "token" in data[0]
    assert "/interview/" in data[0]["session_url"]

    app.dependency_overrides.clear()
