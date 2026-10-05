import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from backend.main import app
from backend.dependencies.auth import get_actor, AuthActor
from backend.dependencies.db import get_tenant_db
from database.models import Interview, Evaluation, AgentRun, Candidate, Job

def test_get_report_detail_recruiter():
    mock_actor = AuthActor(id="user-recruiter-1", role="RECRUITER", tenant_id="tenant-1", is_candidate=False)
    mock_db = AsyncMock()

    mock_interview = Interview(
        id="int-123",
        tenant_id="tenant-1",
        candidate_id="cand-1",
        job_id="job-1",
        status="COMPLETED",
        integrity_score=0.98,
        transcript=[{"speaker": "AI", "text": "Hello"}, {"speaker": "CANDIDATE", "text": "Hi"}],
        created_at=datetime.now(timezone.utc)
    )
    mock_candidate = Candidate(id="cand-1", tenant_id="tenant-1", name="Sarah Connor", email="sarah@example.com")
    mock_job = Job(id="job-1", tenant_id="tenant-1", title="Staff Systems Architect")
    mock_eval = Evaluation(
        id="eval-123",
        tenant_id="tenant-1",
        interview_id="int-123",
        overall_score=91,
        recommendation="PASS",
        summary="Outstanding architectural execution"
    )
    mock_agent_run = AgentRun(
        id="ar-1",
        tenant_id="tenant-1",
        evaluation_id="eval-123",
        agent_name="TECHNICAL",
        score=94,
        confidence=0.96,
        feedback="Mastery in distributed systems",
        evidence_citations=[{"quote": "I implemented raft consensus", "relevance": "High"}]
    )

    def mock_execute_side_effect(stmt):
        res = MagicMock()
        stmt_str = str(stmt)
        if "FROM interviews" in stmt_str:
            res.scalar_one_or_none.return_value = mock_interview
        elif "FROM candidates" in stmt_str:
            res.scalar_one_or_none.return_value = mock_candidate
        elif "FROM jobs" in stmt_str:
            res.scalar_one_or_none.return_value = mock_job
        elif "FROM evaluations" in stmt_str:
            res.scalar_one_or_none.return_value = mock_eval
        elif "FROM agent_runs" in stmt_str:
            res.scalars.return_value.all.return_value = [mock_agent_run]
        elif "FROM integrity_events" in stmt_str:
            res.scalars.return_value.all.return_value = []
        else:
            res.scalar_one_or_none.return_value = None
            res.scalars.return_value.all.return_value = []
        return res

    mock_db.execute.side_effect = mock_execute_side_effect
    app.dependency_overrides[get_actor] = lambda: mock_actor
    app.dependency_overrides[get_tenant_db] = lambda: mock_db

    client = TestClient(app)
    response = client.get("/api/v1/reports/int-123")

    assert response.status_code == 200
    data = response.json()
    assert data["interview_id"] == "int-123"
    assert data["candidate_name"] == "Sarah Connor"
    assert data["job_title"] == "Staff Systems Architect"
    assert data["composite_score"] == 91
    assert data["recommendation"] == "PASS"
    assert data["technical"]["score"] == 94
    assert len(data["transcript"]) == 2

    # Test PDF download endpoint
    pdf_resp = client.get("/api/v1/reports/int-123/pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert len(pdf_resp.content) > 100

    app.dependency_overrides.clear()
