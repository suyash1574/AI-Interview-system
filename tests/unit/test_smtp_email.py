import pytest
from unittest.mock import MagicMock, patch
from backend.core.services.email import EmailDispatcher

def test_smtp_email_dispatch_starttls():
    with patch("smtplib.SMTP") as mock_smtp_cls:
        mock_server = MagicMock()
        mock_smtp_cls.return_value = mock_server

        dispatcher = EmailDispatcher(
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="test_user",
            smtp_password="test_password",
            smtp_use_tls=True,
            from_email="interviews@autergo.com"
        )

        success = dispatcher.send_invitation(
            recipient_email="candidate@example.com",
            candidate_name="Jane Doe",
            job_title="Senior Engineer",
            interview_link="https://app.autergo.com/interview/123"
        )

        assert success is True
        mock_smtp_cls.assert_called_once_with("smtp.example.com", 587, timeout=10.0)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test_user", "test_password")
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

def test_smtp_email_dispatch_ssl():
    with patch("smtplib.SMTP_SSL") as mock_ssl_cls:
        mock_server = MagicMock()
        mock_ssl_cls.return_value = mock_server

        dispatcher = EmailDispatcher(
            smtp_host="smtp.example.com",
            smtp_port=465,
            smtp_username="test_user",
            smtp_password="test_password",
            smtp_use_tls=True,
            from_email="interviews@autergo.com"
        )

        success = dispatcher.send_report_notification(
            recipient_email="recruiter@example.com",
            candidate_name="Jane Doe",
            score=92,
            report_url="https://app.autergo.com/reports/123"
        )

        assert success is True
        mock_ssl_cls.assert_called_once_with("smtp.example.com", 465, timeout=10.0)
        mock_server.login.assert_called_once_with("test_user", "test_password")
        mock_server.send_message.assert_called_once()

def test_smtp_email_simulation_fallback():
    dispatcher = EmailDispatcher(
        smtp_host="",
        api_key="mock_key"
    )
    success = dispatcher.send_invitation(
        recipient_email="candidate@example.com",
        candidate_name="Jane Doe",
        job_title="Senior Engineer",
        interview_link="https://app.autergo.com/interview/123"
    )
    assert success is True
