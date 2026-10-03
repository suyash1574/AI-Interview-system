import logging
from typing import Optional, List, Dict, Any
import httpx
from pydantic import BaseModel, EmailStr
from backend.config import settings

logger = logging.getLogger(__name__)

class EmailMessage(BaseModel):
    to_email: EmailStr
    subject: str
    body_text: str
    report_url: Optional[str] = None

class EmailDispatcher:
    """
    Email notification dispatcher using Resend REST API (https://api.resend.com/emails).
    Gracefully falls back to logged simulation during local and test runs when RESEND_API_KEY is not configured.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.RESEND_API_KEY or "mock_resend_key"
        self.from_email = "Autergo Interviews <no-reply@autergo.com>"

    def _send_resend_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> bool:
        if not self.api_key or self.api_key.startswith("mock_"):
            logger.info(f"[SIMULATED EMAIL] To: {to_email} | Subject: {subject} | Body: {text_body[:80]}...")
            return True

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "from": self.from_email,
            "to": [to_email],
            "subject": subject,
            "html": html_body,
            "text": text_body
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post("https://api.resend.com/emails", headers=headers, json=payload)
                res.raise_for_status()
                logger.info(f"Successfully dispatched email via Resend to {to_email}")
                return True
        except Exception as e:
            logger.error(f"Resend email dispatch failed to {to_email}: {e}")
            return False

    def send_report_notification(self, recipient_email: str, candidate_name: str, score: int, report_url: str) -> bool:
        subject = f"Interview Evaluation Ready: {candidate_name} (Score: {score}/100)"
        text_body = (
            f"Hello,\n\nThe AI technical interview for {candidate_name} has concluded with a score of {score}/100.\n"
            f"Review the full evaluation report and transcript here:\n{report_url}\n\nAutergo Team"
        )
        html_body = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 8px;">
            <h2 style="color: #0f172a; margin-top: 0;">Evaluation Report Available</h2>
            <p style="color: #475569; font-size: 15px;">The AI technical evaluation for <strong>{candidate_name}</strong> is complete.</p>
            <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 16px; margin: 20px 0;">
                <span style="font-size: 14px; color: #64748b; text-transform: uppercase; font-weight: 600;">Composite Score</span>
                <div style="font-size: 32px; font-weight: 700; color: #0284c7; margin-top: 4px;">{score} / 100</div>
            </div>
            <a href="{report_url}" style="display: inline-block; background-color: #0f172a; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: 500; font-size: 14px;">View Evaluation Report</a>
            <p style="color: #94a3b8; font-size: 12px; margin-top: 32px; border-top: 1px solid #e2e8f0; padding-top: 16px;">Autergo Autonomous AI Interview System</p>
        </div>
        """
        return self._send_resend_email(recipient_email, subject, html_body, text_body)

    def send_invitation(self, recipient_email: str, candidate_name: str, job_title: str, interview_link: str, expires_in_days: int = 7) -> bool:
        subject = f"Invitation: AI Technical Interview for {job_title} at Autergo"
        text_body = (
            f"Hi {candidate_name},\n\nYou have been invited to complete an autonomous AI technical interview for the {job_title} position.\n\n"
            f"Start your interview here: {interview_link}\n\nThis link is valid for {expires_in_days} days.\n\nBest regards,\nAutergo Hiring Team"
        )
        html_body = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 8px;">
            <h2 style="color: #0f172a; margin-top: 0;">Technical Interview Invitation</h2>
            <p style="color: #475569; font-size: 15px;">Hello {candidate_name},</p>
            <p style="color: #475569; font-size: 15px;">You have been invited to complete an interactive technical interview for the <strong>{job_title}</strong> role.</p>
            <div style="margin: 24px 0;">
                <a href="{interview_link}" style="display: inline-block; background-color: #0284c7; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: 600; font-size: 14px;">Start Your Interview</a>
            </div>
            <p style="color: #64748b; font-size: 13px;">This invitation link will expire in {expires_in_days} days. Please ensure you are in a quiet room with a working microphone and camera before starting.</p>
            <p style="color: #94a3b8; font-size: 12px; margin-top: 32px; border-top: 1px solid #e2e8f0; padding-top: 16px;">Autergo Autonomous AI Interview System</p>
        </div>
        """
        return self._send_resend_email(recipient_email, subject, html_body, text_body)
