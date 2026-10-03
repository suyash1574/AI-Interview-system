import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.dependencies.auth import get_current_user, CurrentUser
from backend.dependencies.db import get_tenant_db
from database.models import Job

@pytest.fixture
def mock_user():
    return CurrentUser(user_id="usr-123", tenant_id="tenant-abc", role="COMPANY_ADMIN")

@pytest.fixture
def mock_db():
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session

def test_create_job_endpoint(mock_user, mock_db):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_tenant_db] = lambda: mock_db

    client = TestClient(app)
    response = client.post(
        "/api/v1/jobs",
        json={
            "title": "Senior Backend Engineer",
            "description_text": "We are seeking a Python and FastAPI specialist with PostgreSQL and Celery expertise."
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Senior Backend Engineer"
    assert data["tenant_id"] == "tenant-abc"
    assert len(data["competencies"]) > 0
    assert mock_db.commit.called

    app.dependency_overrides.clear()

def test_list_jobs_endpoint(mock_user, mock_db):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_tenant_db] = lambda: mock_db

    fake_job = Job(
        id="job-1",
        tenant_id="tenant-abc",
        title="AI Engineer",
        competencies=[{"name": "PyTorch", "type": "tool", "score": 0.95}],
    )
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [fake_job]
    mock_db.execute.return_value = mock_result

    client = TestClient(app)
    response = client.get("/api/v1/jobs")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "job-1"
    assert data[0]["title"] == "AI Engineer"

    app.dependency_overrides.clear()

def test_get_job_not_found(mock_user, mock_db):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_tenant_db] = lambda: mock_db

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    client = TestClient(app)
    response = client.get("/api/v1/jobs/nonexistent-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"

    app.dependency_overrides.clear()
