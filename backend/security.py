import base64
import hashlib
import hmac
import json
import secrets
import time

from fastapi import HTTPException, Request, Response, status

from backend.config import (
    COOKIE_NAME,
    COOKIE_SECURE,
    SECRET_KEY,
    SESSION_TTL_SECONDS,
)


def _secret() -> bytes:
    if SECRET_KEY:
        return SECRET_KEY.encode("utf-8")
    return b"development-only-change-this-secret-before-deployment"


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"{base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_text, digest_text = stored.split("$", 1)
        salt = base64.urlsafe_b64decode(salt_text.encode())
        expected = base64.urlsafe_b64decode(digest_text.encode())
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def issue_session(user_id: int) -> str:
    payload = _b64(json.dumps({
        "sub": user_id,
        "exp": int(time.time()) + SESSION_TTL_SECONDS,
    }, separators=(",", ":")).encode())
    signature = _b64(hmac.new(_secret(), payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{signature}"


def read_session(token: str) -> int | None:
    try:
        payload, signature = token.split(".", 1)
        expected = _b64(hmac.new(_secret(), payload.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            return None
        decoded = base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
        data = json.loads(decoded)
        if int(data["exp"]) < int(time.time()):
            return None
        return int(data["sub"])
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return None


def set_session_cookie(response: Response, user_id: int) -> None:
    response.set_cookie(
        COOKIE_NAME,
        issue_session(user_id),
        max_age=SESSION_TTL_SECONDS,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/", httponly=True, secure=COOKIE_SECURE, samesite="lax")


def require_user_id(request: Request) -> int:
    user_id = read_session(request.cookies.get(COOKIE_NAME, ""))
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please sign in.")
    return user_id

