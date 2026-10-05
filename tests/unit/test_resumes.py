import io
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.dependencies.auth import get_actor, AuthActor
from backend.dependencies.db import get_tenant_db
from backend.core.services.resume_parser import ResumeParserService
from database.models import Candidate

def test_resume_parser_service_text():
    parser = ResumeParserService()
    text_content = b"Jane Doe. Senior Engineer with 5 years experience in Python, FastAPI, and Kubernetes."
    result = parser.parse("resume.txt", text_content)
    assert result.filename == "resume.txt"
    assert "Jane Doe" in result.raw_text
    assert len(result.skills) > 0
    assert "Skills:" in result.summary

def test_resume_parser_service_docx():
    import zipfile
    parser = ResumeParserService()
    
    # Construct in-memory DOCX zip
    docx_buf = io.BytesIO()
    with zipfile.ZipFile(docx_buf, "w") as docx_zip:
        xml_content = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:body><w:p><w:r><w:t>Jane Doe Senior Backend Engineer with Python, FastAPI, and PostgreSQL.</w:t></w:r></w:p></w:body>'
            '</w:document>'
        )
        docx_zip.writestr("word/document.xml", xml_content)
    
    result = parser.parse("jane_resume.docx", docx_buf.getvalue())
    assert result.filename == "jane_resume.docx"
    assert "Jane Doe" in result.raw_text
    assert "Python" in result.raw_text
    assert len(result.skills) > 0


def test_resume_upload_endpoint():
    mock_actor = AuthActor(id="cand-1", role="CANDIDATE", is_candidate=True)
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()

    mock_cand = Candidate(id="cand-1", tenant_id="tenant-1", name="Alex", email="alex@example.com")
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = mock_cand
    mock_db.execute.return_value = mock_res

    app.dependency_overrides[get_actor] = lambda: mock_actor
    app.dependency_overrides[get_tenant_db] = lambda: mock_db

    client = TestClient(app)
    file_bytes = b"Alex Developer. Skills: React, Node.js, PostgreSQL, Docker."
    response = client.post(
        "/api/v1/resumes/upload",
        data={"candidate_id": "cand-1"},
        files={"file": ("resume.txt", io.BytesIO(file_bytes), "text/plain")}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["candidate_id"] == "cand-1"
    assert data["filename"] == "resume.txt"
    assert len(data["extracted_skills"]) > 0

    app.dependency_overrides.clear()
