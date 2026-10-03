import re
from typing import Optional, List
from pydantic import BaseModel

class SecurityCheckResult(BaseModel):
    is_safe: bool
    violation: Optional[str] = None
    sanitized_text: str

class LlamaGuardSecurity:
    """
    Security filter inspired by Llama Guard 3 principles.
    Protects the AI Interviewer strategy engine against prompt injection,
    jailbreaking, system prompt extraction, and malicious directives.
    """

    INJECTION_PATTERNS: List[re.Pattern] = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions?", re.IGNORECASE),
        re.compile(r"you\s+are\s+now\s+(in|a)\s+developer\s+mode", re.IGNORECASE),
        re.compile(r"disregard\s+(system\s+)?rules", re.IGNORECASE),
        re.compile(r"(reveal|print|show)\s+(your\s+)?(system\s+prompt|hidden\s+instructions)", re.IGNORECASE),
        re.compile(r"act\s+as\s+DAN", re.IGNORECASE),
        re.compile(r"<\s*script\s*>", re.IGNORECASE),
        re.compile(r"sudo\s+mode", re.IGNORECASE),
        re.compile(r"repeat\s+everything\s+above", re.IGNORECASE),
    ]

    def __init__(self, blocked_keywords: Optional[List[str]] = None):
        self.blocked_keywords = blocked_keywords or [
            "__import__",
            "eval(",
            "exec(",
            "<script>",
        ]

    async def validate_input(self, text: str) -> SecurityCheckResult:
        """
        Validates candidate answer or utterance.
        """
        trimmed = text.strip()
        if not trimmed:
            return SecurityCheckResult(is_safe=True, violation=None, sanitized_text="")

        # Check prompt injection regular expressions
        for pattern in self.INJECTION_PATTERNS:
            if pattern.search(trimmed):
                return SecurityCheckResult(
                    is_safe=False,
                    violation=f"Prompt injection pattern detected: {pattern.pattern}",
                    sanitized_text="[FILTERED_INJECTION_ATTEMPT]"
                )

        # Check blocked executable keywords
        for keyword in self.blocked_keywords:
            if keyword.lower() in trimmed.lower():
                return SecurityCheckResult(
                    is_safe=False,
                    violation=f"Prohibited executable keyword detected: {keyword}",
                    sanitized_text="[FILTERED_MALICIOUS_INPUT]"
                )

        # Basic sanitization of null bytes and control chars
        sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", trimmed)

        return SecurityCheckResult(
            is_safe=True,
            violation=None,
            sanitized_text=sanitized
        )
