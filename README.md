# Sports Instagram Auto-Poster

Posts soccer match updates (live scores, upcoming fixtures, results) to Instagram automatically every 10–20 minutes. Controlled from your phone via Telegram.

## Leagues covered
- Premier League, MLS, Bundesliga, La Liga, Serie A, Ligue 1, Champions League

---

## Setup (5 minutes)

### 1. Get your API keys

**football-data.org** (soccer data, free):
- Sign up at https://www.football-data.org/client/register
- Copy your API key from the dashboard

**Telegram bot** (phone control, free):
- Open Telegram → search `@BotFather` → send `/newbot`
- Follow prompts, copy the bot token it gives you
- Search `@userinfobot` → send `/start` → copy your numeric Chat ID

### 2. Configure credentials

```bash
cp .env.example .env
# Fill in all 5 values in .env
```

### 3. Install & run

```bash
pip install -r requirements.txt
python run.py
```

---

## Controlling from your phone

Open Telegram, find your bot, and send:

| Command | What it does |
|---------|-------------|
| `/start` | Welcome message + current status |
| `/post` | Post to Instagram right now |
| `/preview` | See what the next post would look like (no posting) |
| `/status` | Scheduler state, post count, next/last post time |
| `/pause` | Stop auto-posting |
| `/resume` | Resume auto-posting |
| `/logs` | Recent activity log |

Every automatic post also sends you a copy of the image in Telegram.

---

## Files

| File | Purpose |
|------|---------|
| `run.py` | Unified entry point — starts scheduler + Telegram bot |
| `scheduler.py` | Posts every 10–20 min (randomized), respects pause/force |
| `bot.py` | Telegram command handlers |
| `state.py` | Shared state between scheduler and bot threads |
| `fetcher.py` | Pulls match data from football-data.org |
| `content.py` | Generates caption text and 1080x1080 image card |
| `poster.py` | Instagram login (session-cached) and photo upload |

## Notes

- Instagram session cached in `session.json` (gitignored) — only logs in once.
- 2FA: prompted in terminal on first login.
- Interval controlled by `POST_INTERVAL_MIN` / `POST_INTERVAL_MAX` in `.env`.
