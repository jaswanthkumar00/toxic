import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).with_name(".env"))


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL", "sqlite:///./skillforge.db")
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


DATABASE_URL = get_database_url()
APP_ENV = os.getenv("APP_ENV", "development").lower()
FRONTEND_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "FRONTEND_ORIGINS", "http://localhost:5173"
    ).split(",")
    if origin.strip()
]
if APP_ENV == "production" and not os.getenv("FRONTEND_ORIGINS"):
    raise RuntimeError("Set FRONTEND_ORIGINS to the deployed frontend origin in production.")
COOKIE_SECURE = APP_ENV == "production"
COOKIE_NAME = "skillforge_session"
SESSION_TTL_SECONDS = 60 * 60 * 24 * 7
SECRET_KEY = os.getenv("SECRET_KEY", "")

if APP_ENV == "production" and len(SECRET_KEY) < 32:
    raise RuntimeError("Set SECRET_KEY to a random value of at least 32 characters in production.")
