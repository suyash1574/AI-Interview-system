import pytest
from unittest.mock import patch, MagicMock
from backend.core.services.email import EmailDispatcher

def test_email_dispatcher_mock_mode():
    dispatcher = EmailDispatcher(api_key="mock_key")
    res1 = dispatcher.send_invitation(
        recipient_email="candidate@example.com",
        candidate_name="Alex Smith",
        job_title="Software Architect",
        interview_link="https://autergo.com/interview/123"
    )
    assert res1 is True

    res2 = dispatcher.send_report_notification(
        recipient_email="recruiter@example.com",
        candidate_name="Alex Smith",
        score=88,
        report_url="https://autergo.com/report/123"
    )
    assert res2 is True

def test_email_dispatcher_resend_api_success():
    dispatcher = EmailDispatcher(api_key="re_valid_api_key")
    with patch("httpx.Client.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        result = dispatcher.send_invitation(
            recipient_email="candidate@example.com",
            candidate_name="Alex Smith",
            job_title="Software Architect",
            interview_link="https://autergo.com/interview/123"
        )
        assert result is True
        assert mock_post.called
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.resend.com/emails"
        assert kwargs["json"]["to"] == ["candidate@example.com"]
        assert "Software Architect" in kwargs["json"]["subject"]
