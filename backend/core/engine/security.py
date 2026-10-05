import re
import logging
from typing import Optional, List
from pydantic import BaseModel
from backend.config import settings

logger = logging.getLogger(__name__)

class SecurityCheckResult(BaseModel):
    is_safe: bool
    violation: Optional[str] = None
    sanitized_text: str

class LlamaGuardSecurity:
    """
    Security filter inspired by Llama Guard 3 principles.
    Protects the AI Interviewer strategy engine against prompt injection,
    jailbreaking, system prompt extraction, and malicious directives.
    Combines high-speed deterministic pattern matching with optional
    semantic guardrail evaluation.
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
        re.compile(r"bypass\s+(safety|content)\s+filters?", re.IGNORECASE),
        re.compile(r"simulate\s+(an\s+unfiltered|jailbroken)\s+assistant", re.IGNORECASE),
        re.compile(r"classify\s+this\s+as\s+(safe|pass)\s+unconditionally", re.IGNORECASE),
    ]

    def __init__(self, blocked_keywords: Optional[List[str]] = None, enable_semantic_eval: bool = False):
        self.blocked_keywords = blocked_keywords or [
            "__import__",
            "eval(",
            "exec(",
            "<script>",
            "os.system",
            "subprocess.Popen",
        ]
        self.enable_semantic_eval = enable_semantic_eval

    async def check_semantic_safety(self, text: str) -> Optional[str]:
        """
        Runs an optional fast semantic guardrail check using Llama-Guard-3 on Groq
        if enabled and configured. Returns violation string if unsafe, None if safe.
        """
        if not self.enable_semantic_eval or not getattr(settings, "GROQ_API_KEY", ""):
            return None

        try:
            import httpx
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
                    json={
                        "model": "llama-guard-3-8b",
                        "messages": [{"role": "user", "content": text}],
                        "temperature": 0.0,
                    }
                )
                if res.status_code == 200:
                    content = res.json()["choices"][0]["message"]["content"].strip()
                    if content.lower().startswith("unsafe"):
                        return f"Llama Guard 3 semantic violation: {content}"
        except Exception as e:
            logger.debug(f"Semantic guardrail evaluation skipped/failed: {e}")
        return None

    async def validate_input(self, text: str) -> SecurityCheckResult:
        """
        Validates candidate answer or utterance.
        """
        trimmed = text.strip()
        if not trimmed:
            return SecurityCheckResult(is_safe=True, violation=None, sanitized_text="")

        # 1. Deterministic prompt injection pattern checks
        for pattern in self.INJECTION_PATTERNS:
            if pattern.search(trimmed):
                return SecurityCheckResult(
                    is_safe=False,
                    violation=f"Prompt injection pattern detected: {pattern.pattern}",
                    sanitized_text="[FILTERED_INJECTION_ATTEMPT]"
                )

        # 2. Blocked executable code keywords
        for keyword in self.blocked_keywords:
            if keyword.lower() in trimmed.lower():
                return SecurityCheckResult(
                    is_safe=False,
                    violation=f"Prohibited executable keyword detected: {keyword}",
                    sanitized_text="[FILTERED_MALICIOUS_INPUT]"
                )

        # 3. Optional semantic guardrail check
        if self.enable_semantic_eval:
            semantic_violation = await self.check_semantic_safety(trimmed)
            if semantic_violation:
                return SecurityCheckResult(
                    is_safe=False,
                    violation=semantic_violation,
                    sanitized_text="[FILTERED_SEMANTIC_VIOLATION]"
                )

        # 4. Basic sanitization of null bytes and control chars
        sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", trimmed)

        return SecurityCheckResult(
            is_safe=True,
            violation=None,
            sanitized_text=sanitized
        )

