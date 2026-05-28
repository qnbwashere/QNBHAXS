"""
Handles Instagram session loading and photo posting.
Uses IG_SESSION secret (pre-built session JSON) to avoid login challenges.
"""

import json
import os
from pathlib import Path

from instagrapi import Client

SESSION_FILE = Path("session.json")


def _build_client() -> Client:
    cl = Client()
    cl.delay_range = [2, 5]
    return cl


def login(username: str, password: str) -> Client:
    """Return an authenticated Client using IG_SESSION secret (no login call)."""
    session_env = os.getenv("IG_SESSION", "").strip()
    if not session_env:
        raise RuntimeError(
            "IG_SESSION secret is not set. "
            "Follow the setup instructions to generate your session JSON."
        )

    cl = _build_client()
    cl.set_settings(json.loads(session_env))

    # Verify the session works without triggering a login
    try:
        cl.get_timeline_feed()
        print("[poster] Session loaded and verified.")
        return cl
    except Exception as e:
        raise RuntimeError(f"[poster] Session invalid or expired: {e}")


def post_photo(cl: Client, image_path: str, caption: str) -> str | None:
    """Upload a photo post. Returns the media ID or None on failure."""
    try:
        media = cl.photo_upload(image_path, caption)
        print(f"[poster] Posted! media_id={media.id}")
        return str(media.id)
    except Exception as e:
        print(f"[poster] Upload failed: {e}")
        return None
