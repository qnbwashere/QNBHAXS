"""
Fetches current and upcoming soccer fixtures from football-data.org.
Covers Premier League, MLS, Bundesliga, La Liga, Serie A, Ligue 1, Champions League.
"""

import os
import random
from datetime import datetime, timezone, timedelta

import requests

API_BASE = "https://api.football-data.org/v4"

# Competition IDs on football-data.org
COMPETITIONS = {
    "PL":  "Premier League",
    "MLS": "MLS",
    "BL1": "Bundesliga",
    "PD":  "La Liga",
    "SA":  "Serie A",
    "FL1": "Ligue 1",
    "CL":  "Champions League",
    "EC":  "European Championship",
    "WC":  "World Cup",
}


def _headers() -> dict:
    key = os.getenv("FOOTBALL_DATA_API_KEY", "")
    return {"X-Auth-Token": key}


def _get(path: str, params: dict = None) -> dict | None:
    try:
        r = requests.get(f"{API_BASE}{path}", headers=_headers(), params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
        print(f"[fetcher] API error {r.status_code}: {r.text[:200]}")
    except requests.RequestException as e:
        print(f"[fetcher] Request failed: {e}")
    return None


def get_todays_matches() -> list[dict]:
    """Return all matches scheduled for today across tracked competitions."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data = _get("/matches", {"dateFrom": today, "dateTo": today})
    if not data:
        return []
    matches = []
    for m in data.get("matches", []):
        comp_code = m.get("competition", {}).get("code", "")
        if comp_code in COMPETITIONS:
            matches.append(_normalize(m))
    return matches


def get_upcoming_matches(days: int = 3) -> list[dict]:
    """Return matches in the next `days` days."""
    today = datetime.now(timezone.utc)
    end = (today + timedelta(days=days)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")
    data = _get("/matches", {"dateFrom": today_str, "dateTo": end})
    if not data:
        return []
    matches = []
    for m in data.get("matches", []):
        comp_code = m.get("competition", {}).get("code", "")
        if comp_code in COMPETITIONS:
            matches.append(_normalize(m))
    return matches


def get_live_matches() -> list[dict]:
    """Return matches currently in progress."""
    data = _get("/matches", {"status": "IN_PLAY,PAUSED"})
    if not data:
        return []
    return [_normalize(m) for m in data.get("matches", [])
            if m.get("competition", {}).get("code", "") in COMPETITIONS]


def get_recent_results(hours: int = 24) -> list[dict]:
    """Return finished matches from the last `hours` hours."""
    now = datetime.now(timezone.utc)
    date_from = (now - timedelta(hours=hours)).strftime("%Y-%m-%d")
    date_to = now.strftime("%Y-%m-%d")
    data = _get("/matches", {
        "dateFrom": date_from,
        "dateTo": date_to,
        "status": "FINISHED",
    })
    if not data:
        return []
    return [_normalize(m) for m in data.get("matches", [])
            if m.get("competition", {}).get("code", "") in COMPETITIONS]


def _normalize(m: dict) -> dict:
    """Flatten a match object into a simpler dict."""
    comp = m.get("competition", {})
    home = m.get("homeTeam", {})
    away = m.get("awayTeam", {})
    score = m.get("score", {})
    full = score.get("fullTime", {})
    half = score.get("halfTime", {})
    utc_date = m.get("utcDate", "")

    kick_off = None
    if utc_date:
        try:
            kick_off = datetime.fromisoformat(utc_date.replace("Z", "+00:00"))
        except ValueError:
            pass

    return {
        "id": m.get("id"),
        "status": m.get("status", "SCHEDULED"),
        "competition": comp.get("name", comp.get("code", "Unknown")),
        "competition_code": comp.get("code", ""),
        "home": home.get("shortName") or home.get("name", "Home"),
        "away": away.get("shortName") or away.get("name", "Away"),
        "home_score": full.get("home"),
        "away_score": full.get("away"),
        "half_home": half.get("home"),
        "half_away": half.get("away"),
        "minute": m.get("minute"),
        "kick_off": kick_off,
        "matchday": m.get("matchday"),
        "stage": m.get("stage", ""),
    }


def pick_post_subject() -> dict | None:
    """
    Choose the most interesting match to post about.
    Priority: live > today's upcoming > recent result > future upcoming.
    Returns a dict with keys: type, match (normalized).
    """
    live = get_live_matches()
    if live:
        return {"type": "live", "match": random.choice(live)}

    todays = get_todays_matches()
    upcoming_today = [m for m in todays if m["status"] == "SCHEDULED"]
    if upcoming_today:
        return {"type": "upcoming_today", "match": random.choice(upcoming_today)}

    results = get_recent_results(hours=24)
    if results:
        return {"type": "result", "match": random.choice(results)}

    future = get_upcoming_matches(days=5)
    if future:
        return {"type": "upcoming", "match": random.choice(future)}

    return None
