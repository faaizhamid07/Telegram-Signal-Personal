import asyncio
from getpass import getpass
from dotenv import load_dotenv
import os
from telethon import TelegramClient
from telethon.sessions import StringSession

load_dotenv()
api_id = int(os.getenv("TELEGRAM_API_ID", "0") or 0)
api_hash = os.getenv("TELEGRAM_API_HASH", "").strip()
if not api_id or not api_hash:
    raise SystemExit("Set TELEGRAM_API_ID and TELEGRAM_API_HASH in .env first.")

async def main():
    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.start(phone=lambda: input("Telegram phone number (international format): ").strip(),
                       password=lambda: getpass("Telegram 2-step verification password (if enabled): "))
    print("\nSESSION STRING — SECRET, DO NOT SHARE OR COMMIT:\n")
    print(client.session.save())
    await client.disconnect()

asyncio.run(main())
