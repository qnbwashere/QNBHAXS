"""
One-shot posting script — fetches a match, posts to Instagram, notifies Telegram.
Designed to be run by GitHub Actions (or manually).
"""

import os
import sys
import tempfile
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

from fetcher import pick_post_subject
from content import build_caption, build_image
from poster import login, post_photo


def notify_telegram(image_path: str, caption: str):
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return
    try:
        with open(image_path, "rb") as f:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendPhoto",
                data={"chat_id": chat_id, "caption": f"✅ Posted to Instagram!\n\n{caption[:900]}"},
                files={"photo": f},
                timeout=15,
            )
        print("[post_once] Telegram notification sent.")
    except Exception as e:
        print(f"[post_once] Telegram notification failed: {e}")


def main():
    print("[post_once] Fetching match data…")
    subject = pick_post_subject()
    if not subject:
        print("[post_once] No match data — nothing to post.")
        sys.exit(0)

    m = subject["match"]
    print(f"[post_once] {subject['type'].upper()}: {m['home']} vs {m['away']} ({m['competition']})")

    caption = build_caption(subject)

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        img_path = f.name

    try:
        build_image(subject, img_path)
        print("[post_once] Image generated. Logging into Instagram…")

        cl = login(os.environ["IG_USERNAME"], os.environ["IG_PASSWORD"])
        media_id = post_photo(cl, img_path, caption)

        if media_id:
            print(f"[post_once] Posted! media_id={media_id}")
            notify_telegram(img_path, caption)
        else:
            print("[post_once] Post failed.")
            sys.exit(1)
    finally:
        Path(img_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
