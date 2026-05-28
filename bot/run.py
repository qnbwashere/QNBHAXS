"""
Unified entry point — starts the scheduler and Telegram bot together.

Usage:
    python run.py

Requires .env with:
    IG_USERNAME, IG_PASSWORD, FOOTBALL_DATA_API_KEY,
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
"""

import asyncio
import os
import threading

from dotenv import load_dotenv

load_dotenv()

from bot import build_app
from scheduler import run_scheduler
from state import app_state


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

    if not token:
        print("[run] No TELEGRAM_BOT_TOKEN — running scheduler only (no Telegram).")
        run_scheduler()
        return

    tg_app = build_app(token)

    # Scheduler runs in a background thread
    t = threading.Thread(
        target=run_scheduler,
        kwargs={"tg_app": tg_app, "chat_id": chat_id},
        daemon=True,
        name="scheduler",
    )
    t.start()

    print("[run] Scheduler started. Starting Telegram bot (polling)…")
    print(f"[run] Open Telegram and message your bot to control the poster.")

    # Telegram bot runs in the main thread via asyncio
    tg_app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
