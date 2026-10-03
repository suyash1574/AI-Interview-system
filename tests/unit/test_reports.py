import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.dependencies.auth import get_current_user, CurrentUser
from backend.dependencies.db import get_tenant_db
from database.models import Interview, Evaluation
from workers.tasks.reports import generate_and_dispatch_report_task

@pytest.fixture
def mock_recruiter():
    return CurrentUser(user_id="rec-1", tenant_id="tenant-1", role="RECRUITER")

@pytest.fixture
def mock_db():
    session = AsyncMock()
    return session

def test_generate_and_dispatch_report_task():
    eval_data = {
        "score": 88,
        "confidence_score": 0.94,
        "evidence": [{"quote": "Strong SQL knowledge", "relevance": "High"}],
        "strength": "Relational Data Modeling",
    }
    result = generate_and_dispatch_report_task("int-999", eval_data, "recruiter@autergo.com")
    assert result["interview_id"] == "int-999"
    assert result["overall_score"] == 88
    assert result["status"] == "READY"
    assert "https://storage.autergo.com/reports/" in result["pdf_download_url"]

def test_request_evaluation_report_api(mock_recruiter, mock_db):
    app.dependency_overrides[get_current_user] = lambda: mock_recruiter
    app.dependency_overrides[get_tenant_db] = lambda: mock_db

    fake_interview = Interview(id="int-1", tenant_id="tenant-1", status="COMPLETED")
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = fake_interview
    mock_db.execute.return_value = mock_res

    client = TestClient(app)
    response = client.post("/api/v1/evaluations/report", json={"interview_id": "int-1"})

    assert response.status_code == 202
    data = response.json()
    assert data["interview_id"] == "int-1"
    assert data["status"] == "PROCESSING"

    app.dependency_overrides.clear()

def test_get_evaluation_detail_api(mock_recruiter, mock_db):
    app.dependency_overrides[get_current_user] = lambda: mock_recruiter
    app.dependency_overrides[get_tenant_db] = lambda: mock_db

    fake_interview = Interview(id="int-1", tenant_id="tenant-1")
    fake_eval = Evaluation(
        id="eval-1",
        interview_id="int-1",
        score_raw=90,
        evidence=[{"quote": "Clean architecture explained"}]
    )

    mock_int_res = MagicMock()
    mock_int_res.scalar_one_or_none.return_value = fake_interview

    mock_eval_res = MagicMock()
    mock_eval_res.scalar_one_or_none.return_value = fake_eval

    mock_db.execute.side_effect = [mock_int_res, mock_eval_res]

    client = TestClient(app)
    response = client.get("/api/v1/evaluations/int-1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "eval-1"
    assert data["score_raw"] == 90

    app.dependency_overrides.clear()
