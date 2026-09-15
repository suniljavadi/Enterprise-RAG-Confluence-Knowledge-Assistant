import re
from app.models import Chunk

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous instructions",
    r"reveal\s+(the\s+)?system prompt",
    r"disclose\s+(the\s+)?secret",
    r"you are now",
]
SENSITIVE_PATTERNS = [r"sk-[A-Za-z0-9_-]+", r"bearer\s+[A-Za-z0-9._-]+", r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"]


def is_prompt_injection(text: str) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in INJECTION_PATTERNS)


def sanitize_document(text: str) -> str:
    for pattern in INJECTION_PATTERNS:
        text = re.sub(pattern, "[untrusted instruction removed]", text, flags=re.IGNORECASE)
    return text


def redact_pii(text: str) -> str:
    for pattern in SENSITIVE_PATTERNS:
        text = re.sub(pattern, "[REDACTED]", text, flags=re.IGNORECASE)
    return text


def authorized(chunk: Chunk, roles: list[str]) -> bool:
    return bool(set(chunk.allowed_roles).intersection(roles))
