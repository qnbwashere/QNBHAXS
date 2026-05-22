"""
Main loop: fetch a soccer match, build an image + caption, post to Instagram.
Waits a random interval between POST_INTERVAL_MIN and POST_INTERVAL_MAX minutes
after each post (default 10–20 min).
"""

import os
import random
import time
import tempfile
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fetcher import pick_post_subject
from content import build_caption, build_image
from poster import login, post_photo

IG_USERNAME = os.environ["IG_USERNAME"]
IG_PASSWORD = os.environ["IG_PASSWORD"]

INTERVAL_MIN = int(os.getenv("POST_INTERVAL_MIN", "10"))
INTERVAL_MAX = int(os.getenv("POST_INTERVAL_MAX", "20"))


def run_once(cl) -> bool:
    """Fetch, generate, and post one piece of content. Returns True on success."""
    print("[scheduler] Fetching match data…")
    subject = pick_post_subject()
    if not subject:
        print("[scheduler] No match data available — skipping post.")
        return False

    m = subject["match"]
    print(f"[scheduler] Subject: [{subject['type']}] {m['home']} vs {m['away']} ({m['competition']})")

    caption = build_caption(subject)
    print(f"[scheduler] Caption preview:\n{caption[:120]}…\n")

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        img_path = f.name

    try:
        build_image(subject, img_path)
        print(f"[scheduler] Image saved to {img_path}")
        media_id = post_photo(cl, img_path, caption)
        return media_id is not None
    finally:
        Path(img_path).unlink(missing_ok=True)


def main():
    print("[scheduler] Starting sports Instagram auto-poster.")
    print(f"[scheduler] Posting every {INTERVAL_MIN}–{INTERVAL_MAX} minutes.")

    cl = login(IG_USERNAME, IG_PASSWORD)

    while True:
        success = run_once(cl)
        wait_min = random.uniform(INTERVAL_MIN, INTERVAL_MAX)
        wait_sec = int(wait_min * 60)
        status = "posted" if success else "skipped"
        print(f"[scheduler] {status.capitalize()}. Next post in {wait_min:.1f} min ({wait_sec}s).")
        time.sleep(wait_sec)


if __name__ == "__main__":
    main()
