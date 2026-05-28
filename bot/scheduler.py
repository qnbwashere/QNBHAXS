"""
Scheduler loop — runs in its own thread.
Fetches a match, builds content, posts to Instagram, notifies Telegram.
Respects app_state.paused and app_state.force_post.
"""

import asyncio
import os
import random
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fetcher import pick_post_subject
from content import build_caption, build_image
from poster import login, post_photo
from state import app_state

INTERVAL_MIN = int(os.getenv("POST_INTERVAL_MIN", "10"))
INTERVAL_MAX = int(os.getenv("POST_INTERVAL_MAX", "20"))


def run_once(cl, tg_app=None, chat_id: str = "") -> bool:
    """Fetch, generate, post. Returns True on success."""
    app_state.add_log("Fetching match data…")
    subject = pick_post_subject()
    if not subject:
        app_state.add_log("No match data available — skipping.")
        return False

    m = subject["match"]
    app_state.add_log(f"[{subject['type']}] {m['home']} vs {m['away']} ({m['competition']})")
    app_state.last_subject = subject

    caption = build_caption(subject)

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        img_path = f.name

    try:
        build_image(subject, img_path)
        media_id = post_photo(cl, img_path, caption)
        success = media_id is not None

        if success:
            app_state.post_count += 1
            app_state.last_post_at = datetime.now(timezone.utc)
            app_state.add_log(f"Posted! media_id={media_id} (total: {app_state.post_count})")

            if tg_app and chat_id:
                # Send Telegram notification with the same image
                loop = asyncio.new_event_loop()
                try:
                    loop.run_until_complete(
                        _notify_telegram(tg_app, img_path, caption, chat_id)
                    )
                finally:
                    loop.close()
        else:
            app_state.add_log("Post failed — will retry next cycle.")

        return success
    finally:
        Path(img_path).unlink(missing_ok=True)


async def _notify_telegram(tg_app, image_path: str, caption: str, chat_id: str):
    from bot import send_post_notification
    await send_post_notification(tg_app, image_path, caption, chat_id)


def run_scheduler(tg_app=None, chat_id: str = ""):
    """Main scheduler loop. Runs forever in its own thread."""
    ig_user = os.environ["IG_USERNAME"]
    ig_pass = os.environ["IG_PASSWORD"]

    app_state.running = True
    app_state.add_log("Scheduler starting, logging into Instagram…")

    cl = login(ig_user, ig_pass)
    app_state.add_log("Instagram login successful.")

    while True:
        if app_state.paused:
            time.sleep(5)
            continue

        run_once(cl, tg_app=tg_app, chat_id=chat_id)

        wait_min = random.uniform(INTERVAL_MIN, INTERVAL_MAX)
        wait_sec = int(wait_min * 60)
        from datetime import timedelta
        app_state.next_post_at = datetime.now(timezone.utc) + timedelta(seconds=wait_sec)
        app_state.add_log(f"Next post in {wait_min:.1f} min.")

        # Sleep in 5-second chunks so force_post and pause are checked promptly
        deadline = time.time() + wait_sec
        while time.time() < deadline:
            if app_state.force_post.is_set():
                app_state.force_post.clear()
                app_state.add_log("Forced post triggered via Telegram.")
                break
            if app_state.paused:
                break
            time.sleep(5)
