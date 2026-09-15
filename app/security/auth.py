from fastapi import Header, HTTPException
from app.config import get_settings


def require_bearer_token(authorization: str | None = Header(default=None)) -> str | None:
    configured = get_settings().api_auth_token
    if configured and authorization not in {configured, f"Bearer {configured}"}:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return authorization
