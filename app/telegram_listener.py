import asyncio
import logging
from urllib.parse import quote
import httpx
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from app import db
from app.config import API_ID, API_HASH, TELEGRAM_SESSION, BOT_TOKEN, BOT_CHAT_ID, PUBLIC_BASE_URL

log = logging.getLogger(__name__)
client = None

def message_link(chat, message_id: int):
    username = getattr(chat, "username", None)
    if username:
        return f"https://t.me/{username}/{message_id}"
    # For private supergroups/channels Telegram's internal ID is commonly -100<id>.
    chat_id = getattr(chat, "id", None)
    if chat_id and getattr(chat, "megagroup", False):
        return f"https://t.me/c/{chat_id}/{message_id}"
    return None

async def send_alert(group_title, text, terms, link):
    if not BOT_TOKEN or not BOT_CHAT_ID:
        log.warning("Bot notification skipped: BOT_TOKEN or BOT_CHAT_ID is missing")
        return
    body = f"🔎 <b>Telegram Signal match</b>\n<b>Group:</b> {group_title}\n<b>Keywords:</b> {', '.join(terms)}\n\n{ text[:2500] }"
    # HTML-escape user-provided message content to avoid Telegram markup injection.
    import html
    body = f"🔎 <b>Telegram Signal match</b>\n<b>Group:</b> {html.escape(group_title)}\n<b>Keywords:</b> {html.escape(', '.join(terms))}\n\n{html.escape(text[:2500])}"
    if link:
        body += f'\n\n<a href="{html.escape(link, quote=True)}">Open original message</a>'
    async with httpx.AsyncClient(timeout=15) as session:
        response = await session.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": BOT_CHAT_ID, "text": body, "parse_mode": "HTML", "disable_web_page_preview": True},
        )
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError("Telegram Bot API returned an unsuccessful response")

async def start_listener():
    global client
    if not (API_ID and API_HASH and TELEGRAM_SESSION):
        log.warning("Telegram listener disabled: set TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION")
        return
    client = TelegramClient(StringSession(TELEGRAM_SESSION), API_ID, API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        raise RuntimeError("TELEGRAM_SESSION is not authorized; regenerate it locally")
    log.info("Telegram user session connected")

    @client.on(events.NewMessage)
    async def on_new_message(event):
        try:
            if not event.is_group:
                return
            # Do not log message contents; Telegram messages may contain private data.
            row_groups = db.all_rows("SELECT * FROM groups WHERE enabled=1")
            peer = str(event.chat_id)
            selected = next((g for g in row_groups if g["peer"].strip() in {peer, str(getattr(event.chat, "username", "") or "")}), None)
            if not selected:
                return
            text = (event.raw_text or "").strip()
            if not text:
                return
            keywords = db.all_rows("SELECT term FROM keywords WHERE enabled=1")
            matched = [k["term"] for k in keywords if k["term"].casefold() in text.casefold()]
            if not matched:
                return
            title = getattr(event.chat, "title", None) or selected["title"]
            link = message_link(event.chat, event.message.id)
            with db.connect() as conn:
                cur = conn.execute(
                    "INSERT OR IGNORE INTO matches(chat_id, group_title, message_id, text, matched_terms, link) VALUES(?,?,?,?,?,?)",
                    (event.chat_id, title, event.message.id, text, ", ".join(matched), link),
                )
                inserted = cur.rowcount == 1
            if inserted:
                await send_alert(title, text, matched, link)
        except Exception:
            log.exception("Failed to process Telegram message")

    await client.run_until_disconnected()
