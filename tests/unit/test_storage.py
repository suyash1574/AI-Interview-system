import pytest
from backend.core.services.storage import StorageService

def test_storage_service_upload_and_presigned_url():
    storage = StorageService(
        account_id="test-acc",
        access_key_id="test-key",
        secret_access_key="test-secret",
        bucket_name="test-bucket",
        public_url="https://cdn.autergo.com"
    )
    test_bytes = b"%PDF-1.4 simulated pdf document"
    url = storage.upload_bytes(test_bytes, "reports/int-101/summary.pdf", "application/pdf")
    assert "https://cdn.autergo.com/reports/int-101/summary.pdf" in url

    presigned = storage.generate_presigned_url("reports/int-101/summary.pdf", expires_in=1800)
    assert "reports/int-101/summary.pdf" in presigned

def test_storage_service_fallback_url():
    storage = StorageService()
    url = storage.upload_bytes(b"sample data", "resumes/cand-5/resume.pdf")
    assert "/resumes/cand-5/resume.pdf" in url
