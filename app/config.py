import os
from dotenv import load_dotenv

load_dotenv()

def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()

API_ID = int(env("TELEGRAM_API_ID", "0") or 0)
API_HASH = env("TELEGRAM_API_HASH")
TELEGRAM_SESSION = env("TELEGRAM_SESSION")
BOT_TOKEN = env("TELEGRAM_BOT_TOKEN")
BOT_CHAT_ID = env("TELEGRAM_CHAT_ID")
DASHBOARD_PASSWORD = env("DASHBOARD_PASSWORD")
DATABASE_PATH = env("DATABASE_PATH", "./telegram_signal.db")
PUBLIC_BASE_URL = env("PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
