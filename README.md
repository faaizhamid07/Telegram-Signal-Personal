# Telegram Signal

A personal dashboard that watches selected Telegram groups for keywords and brings matching messages into one place.

## Features

- Monitor Telegram groups your account can already access.
- Add, pause, and remove groups and keywords from the dashboard.
- Match words and phrases without case sensitivity.
- View the latest 100 matches in a local dashboard.
- Send matching alerts to your own Telegram chat through a bot.

## How it works

React + Vite provides the dashboard. FastAPI serves the API, Telethon listens to Telegram as your user account, the Telegram Bot API sends optional alerts, and SQLite stores settings and matches on your computer.

## Requirements

- Windows 10/11
- Python 3.12
- Node.js LTS and npm
- A Telegram account
- Telegram API ID and API hash from [my.telegram.org](https://my.telegram.org)
- A Telegram bot created with [@BotFather](https://t.me/BotFather)

## Install on Windows

Open PowerShell in the project folder.

### 1. Install the backend

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks activation, run this in the same terminal, then activate the environment again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 2. Configure Telegram

Open `.env` in a text editor and fill in:

- `TELEGRAM_API_ID` and `TELEGRAM_API_HASH`: get these from [my.telegram.org](https://my.telegram.org).
- `TELEGRAM_BOT_TOKEN`: create a bot with @BotFather.
- `TELEGRAM_CHAT_ID`: your own Telegram chat ID.
- `DASHBOARD_PASSWORD`: choose a long, unique password.
- `TELEGRAM_SESSION`: add this after generating your session in the next step.

Never share your `.env` file or Telegram session string. A session string can grant access to your Telegram account.

### 3. Generate your user session

With `.env` filled in with your API ID and API hash, run:

```powershell
python scripts/generate_session.py
```

Follow the Telegram login prompts. Copy the generated session string into `TELEGRAM_SESSION` in `.env`. Do not paste it into GitHub, screenshots, or chats.

### 4. Get your bot chat ID

Start a chat with your bot in Telegram and send `/start`. Then run:

```powershell
python scripts/get_bot_chat_id.py
```

Copy your numeric chat ID into `TELEGRAM_CHAT_ID` in `.env`. If no ID appears, send another message to the bot and rerun the script.

### 5. Build the dashboard and start the app

From the project root:

```powershell
npm run build
uvicorn app.main:app
```

Open http://127.0.0.1:8000 in your browser and sign in with `DASHBOARD_PASSWORD`.

Keep the terminal running while you use the app. To stop it, press `Ctrl+C`.

### 6. Add groups and keywords

In the dashboard, add a group using its username or numeric peer ID, then add the keywords or phrases you want to watch. To list groups your account can already access, run:

```powershell
python scripts/list_groups.py
```

The listener only monitors enabled groups that your account can access. It watches new messages after it starts; it does not backfill old messages.

## Data and privacy

- Settings and matched messages are stored in a local SQLite database named `telegram_signal.db` by default.
- The database, environment file, and Telethon session are excluded from Git by `.gitignore`.
- Matched messages can contain private information. Keep your computer and database secure.
- The app is intended for local use. The dashboard has basic password protection, but it is not designed or security-audited for internet exposure or multiple users. Do not port-forward it or deploy it as a public service.
- Use Telegram's APIs responsibly and follow applicable group rules and Telegram terms.

## Known limitations

- Single-user MVP, not a hosted multi-user service.
- Case-insensitive literal keyword/phrase matching only.
- Text-only matching; media-only posts are ignored.
- No historical backfill.
- SQLite is intended for a single local instance.

## License

This project uses a custom personal-use source-available license. You may download, run, and modify your own copy for personal, non-commercial use. Redistribution, commercial use, and publishing modified versions require prior written permission. See [LICENSE](LICENSE) for the full terms.

This is not an OSI-approved open-source license. Third-party dependencies and assets remain subject to their own licenses.
