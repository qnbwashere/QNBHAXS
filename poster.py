"""
Handles Instagram login (with session caching) and photo posting.
"""

import json
import os
from pathlib import Path

from instagrapi import Client
from instagrapi.exceptions import LoginRequired, TwoFactorRequired

SESSION_FILE = Path("session.json")


def _build_client() -> Client:
    cl = Client()
    cl.delay_range = [2, 5]
    return cl


def login(username: str, password: str) -> Client:
    """Return an authenticated instagrapi Client.
    Prefers IG_SESSION env var (JSON string), then session.json file, then fresh login.
    """
    cl = _build_client()

    # Try session from environment variable first (GitHub Actions secret)
    session_env = os.getenv("IG_SESSION", "").strip()
    if session_env:
        try:
            cl.set_settings(json.loads(session_env))
            cl.login(username, password)
            cl.get_timeline_feed()
            print("[poster] Logged in via IG_SESSION secret.")
            return cl
        except Exception as e:
            print(f"[poster] IG_SESSION failed ({e}), trying other methods.")
            cl = _build_client()

    # Try cached session file
    if SESSION_FILE.exists():
        try:
            cl.set_settings(json.loads(SESSION_FILE.read_text()))
            cl.login(username, password)
            cl.get_timeline_feed()
            print("[poster] Re-used cached session file.")
            return cl
        except Exception as e:
            print(f"[poster] Session file failed ({e}), logging in fresh.")
            cl = _build_client()

    # Fresh login
    try:
        cl.login(username, password)
    except TwoFactorRequired:
        code = input("[poster] 2FA code: ").strip()
        cl.login(username, password, verification_code=code)

    SESSION_FILE.write_text(json.dumps(cl.get_settings()))
    print("[poster] Logged in fresh, session saved.")
    return cl


def post_photo(cl: Client, image_path: str, caption: str) -> str | None:
    """Upload a photo post. Returns the media ID or None on failure."""
    try:
        media = cl.photo_upload(image_path, caption)
        print(f"[poster] Posted! media_id={media.id}")
        return str(media.id)
    except Exception as e:
        print(f"[poster] Upload failed: {e}")
        return None
