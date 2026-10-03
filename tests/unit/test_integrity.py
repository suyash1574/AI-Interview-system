import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.dependencies.auth import get_actor, AuthActor
from backend.dependencies.db import get_tenant_db
from database.models import Interview, IntegrityEvent
from datetime import datetime, timezone

@pytest.fixture
def mock_candidate_actor():
    return AuthActor(id="cand-1", role="CANDIDATE", is_candidate=True, interview_id="int-123")

@pytest.fixture
def mock_recruiter_actor():
    return AuthActor(id="rec-1", role="RECRUITER", is_candidate=False, tenant_id="tenant-1")

@pytest.fixture
def mock_db():
    session = AsyncMock()
    return session

def test_log_telemetry_event_success(mock_candidate_actor, mock_db):
    app.dependency_overrides[get_actor] = lambda: mock_candidate_actor
    app.dependency_overrides[get_tenant_db] = lambda: mock_db

    fake_interview = Interview(id="int-123", tenant_id="tenant-1")
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = fake_interview
    mock_db.execute.return_value = mock_res

    client = TestClient(app)
    response = client.post(
        "/api/v1/interviews/int-123/telemetry",
        json={
            "event_type": "TAB_SWITCH",
            "severity": "MEDIUM",
            "metadata": {"duration_ms": 4200, "url": "https://google.com"}
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["interview_id"] == "int-123"
    assert data["event_type"] == "TAB_SWITCH"
    assert data["severity"] == "MEDIUM"
    assert data["metadata"]["duration_ms"] == 4200
    assert mock_db.add.called
    assert mock_db.commit.called

    app.dependency_overrides.clear()

def test_get_integrity_events_success(mock_recruiter_actor, mock_db):
    app.dependency_overrides[get_actor] = lambda: mock_recruiter_actor
    app.dependency_overrides[get_tenant_db] = lambda: mock_db

    fake_interview = Interview(id="int-123", tenant_id="tenant-1")
    fake_event = IntegrityEvent(
        id="evt-1",
        tenant_id="tenant-1",
        interview_id="int-123",
        event_type="WINDOW_BLUR",
        severity="LOW",
        timestamp=datetime.now(timezone.utc),
        details={"blur_count": 1}
    )

    mock_res1 = MagicMock()
    mock_res1.scalar_one_or_none.return_value = fake_interview

    mock_res2 = MagicMock()
    mock_res2.scalars.return_value.all.return_value = [fake_event]

    mock_db.execute.side_effect = [mock_res1, mock_res2]

    client = TestClient(app)
    response = client.get("/api/v1/interviews/int-123/integrity-events")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["event_type"] == "WINDOW_BLUR"
    assert data[0]["severity"] == "LOW"

    app.dependency_overrides.clear()
