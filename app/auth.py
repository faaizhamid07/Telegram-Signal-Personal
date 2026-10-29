import secrets
from fastapi import Header, HTTPException
from app.config import DASHBOARD_PASSWORD

# MVP: one process, one personal dashboard. Restarting invalidates all issued tokens.
_tokens: set[str] = set()

def login(password: str) -> str:
    if not DASHBOARD_PASSWORD:
        raise HTTPException(503, "DASHBOARD_PASSWORD is not configured")
    if not secrets.compare_digest(password, DASHBOARD_PASSWORD):
        raise HTTPException(401, "Incorrect password")
    token = secrets.token_urlsafe(32)
    _tokens.add(token)
    return token

def require_auth(authorization: str | None = Header(default=None)):
    token = authorization.removeprefix("Bearer ").strip() if authorization else ""
    if not token or token not in _tokens:
        raise HTTPException(401, "Please log in again")
    return True
