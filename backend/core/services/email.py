import logging
from typing import Optional, List
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

class EmailMessage(BaseModel):
    to_email: EmailStr
    subject: str
    body_text: str
    report_url: Optional[str] = None

class EmailDispatcher:
    """
    Email notification dispatcher (e.g. Resend / SES / SendGrid).
    Logs and simulates dispatch during local and test runs.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def send_report_notification(self, recipient_email: str, candidate_name: str, score: int, report_url: str) -> bool:
        logger.info(
            f"Dispatching interview evaluation report email to {recipient_email} "
            f"for candidate {candidate_name} (Score: {score}). Report URL: {report_url}"
        )
        return True
