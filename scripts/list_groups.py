import asyncio, os
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

load_dotenv()
api_id = int(os.getenv("TELEGRAM_API_ID", "0") or 0)
api_hash = os.getenv("TELEGRAM_API_HASH", "").strip()
session = os.getenv("TELEGRAM_SESSION", "").strip()
if not (api_id and api_hash and session):
    raise SystemExit("Set TELEGRAM_API_ID, TELEGRAM_API_HASH and TELEGRAM_SESSION in .env.")
async def main():
    async with TelegramClient(StringSession(session), api_id, api_hash) as client:
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                print(f"title={dialog.name!r} | id={dialog.id} | username={getattr(dialog.entity, 'username', None)}")
asyncio.run(main())
