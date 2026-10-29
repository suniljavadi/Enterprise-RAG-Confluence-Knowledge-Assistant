import hmac
from fastapi import Header, HTTPException
from app.config import get_settings


def token_matches(authorization: str | None, configured: str) -> bool:
    if not authorization:
        return False
    supplied = authorization[7:] if authorization.lower().startswith("bearer ") else authorization
    return hmac.compare_digest(supplied.encode(), configured.encode())


def require_bearer_token(authorization: str | None = Header(default=None)) -> str | None:
    configured = get_settings().api_auth_token
    if configured and not token_matches(authorization, configured):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return authorization
