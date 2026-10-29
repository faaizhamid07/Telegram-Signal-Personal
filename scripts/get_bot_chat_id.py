import os, requests
from dotenv import load_dotenv
load_dotenv()
token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
if not token:
    raise SystemExit("Set TELEGRAM_BOT_TOKEN in .env first.")
data = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=15).json()
if not data.get("ok"):
    raise SystemExit(f"Telegram returned an error: {data}")
ids = {}
for update in data.get("result", []):
    msg = update.get("message") or update.get("my_chat_member") or {}
    chat = msg.get("chat") or {}
    if chat.get("id") is not None:
        ids[chat["id"]] = (chat.get("type"), chat.get("first_name") or chat.get("title") or "")
if not ids:
    print("No chat IDs found. Open your bot and send /start, then rerun this script.")
else:
    for chat_id, (kind, name) in ids.items():
        print(f"chat_id={chat_id} type={kind} name={name}")
