"""
Generates Instagram post text and image card for a soccer match.
"""

import os
import random
import textwrap
from datetime import timezone
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ── Text templates ────────────────────────────────────────────────────────────

LIVE_TEMPLATES = [
    "⚽ LIVE: {home} {hs}-{as_} {away}\n{comp} | Minute {min}\n\n{cta}",
    "🔴 IN PLAY → {home} vs {away}\nScore: {hs}-{as_} ({comp})\n\n{cta}",
    "MATCH UPDATE 🟢\n{comp}\n{home} {hs} – {as_} {away}\n⏱ {min}'\n\n{cta}",
]

UPCOMING_TODAY_TEMPLATES = [
    "⚽ TODAY: {home} vs {away}\n{comp} | Kick-off {ko}\n\n{cta}",
    "🗓 Coming up TODAY!\n{home} take on {away}\n{comp} — {ko} UTC\n\n{cta}",
    "Get ready! 🔥\n{home} vs {away}\n{comp} | {ko} UTC\n\n{cta}",
]

RESULT_TEMPLATES = [
    "FT: {home} {hs}-{as_} {away} ✅\n{comp}\n\n{cta}",
    "Full-time result ⚽\n{comp}\n{home} {hs} – {as_} {away}\n\n{cta}",
    "📊 FINAL SCORE\n{home} vs {away} | {comp}\n{hs} – {as_}\n\n{cta}",
]

UPCOMING_TEMPLATES = [
    "📅 Coming up: {home} vs {away}\n{comp} | {ko} UTC\n\n{cta}",
    "Don't miss it! 👀\n{home} vs {away}\n{comp} — {ko}\n\n{cta}",
    "⚽ Next match alert!\n{home} v {away}\n{comp} | {ko} UTC\n\n{cta}",
]

CTAS = [
    "Follow for more soccer updates! ⚽🔥",
    "Drop a 🔥 if you're watching!",
    "Who you got? Comment below! 👇",
    "Stay locked in for live updates! 📲",
    "Like & follow for daily soccer content! ⚽",
    "Tag a friend who needs to see this! 👀",
    "Which team wins? Let us know! 👇⚽",
]

HASHTAG_BASE = [
    "#soccer", "#football", "#soccernews", "#footballnews",
    "#premierleague", "#mls", "#bundesliga", "#laliga",
    "#seriea", "#ligue1", "#championsleague", "#matchday",
    "#soccerlife", "#footballlovers", "#sportsnews",
]

LEAGUE_TAGS = {
    "PL":  ["#premierleague", "#eplsoccer", "#bpl"],
    "MLS": ["#mls", "#majorleaguesoccer", "#soccerusa"],
    "BL1": ["#bundesliga", "#germansoccer"],
    "PD":  ["#laliga", "#spanishfootball"],
    "SA":  ["#seriea", "#italianfootball"],
    "FL1": ["#ligue1", "#frenchfootball"],
    "CL":  ["#championsleague", "#ucl"],
}


def _ko_str(match: dict) -> str:
    if match["kick_off"]:
        return match["kick_off"].astimezone(timezone.utc).strftime("%b %d %H:%M")
    return "TBD"


def build_caption(subject: dict) -> str:
    t = subject["type"]
    m = subject["match"]
    cta = random.choice(CTAS)

    ctx = {
        "home": m["home"],
        "away": m["away"],
        "comp": m["competition"],
        "hs": m["home_score"] if m["home_score"] is not None else "-",
        "as_": m["away_score"] if m["away_score"] is not None else "-",
        "min": m["minute"] or "?",
        "ko": _ko_str(m),
        "cta": cta,
    }

    if t == "live":
        template = random.choice(LIVE_TEMPLATES)
    elif t == "upcoming_today":
        template = random.choice(UPCOMING_TODAY_TEMPLATES)
    elif t == "result":
        template = random.choice(RESULT_TEMPLATES)
    else:
        template = random.choice(UPCOMING_TEMPLATES)

    caption = template.format(**ctx)

    # Build hashtag block
    tags = list(HASHTAG_BASE)
    tags += LEAGUE_TAGS.get(m["competition_code"], [])
    random.shuffle(tags)
    caption += "\n\n" + " ".join(tags[:20])

    return caption


# ── Image generation ──────────────────────────────────────────────────────────

CARD_W, CARD_H = 1080, 1080

LEAGUE_COLORS = {
    "PL":  ("#3d195b", "#00ff85"),   # purple / green
    "MLS": ("#002f6c", "#d4121b"),   # navy / red
    "BL1": ("#d20515", "#ffffff"),   # red / white
    "PD":  ("#ee8707", "#ffffff"),   # orange / white
    "SA":  ("#024494", "#ffffff"),   # blue / white
    "FL1": ("#ffffff", "#002395"),   # white / blue
    "CL":  ("#000000", "#ffffff"),   # black / white
    "_":   ("#1a1a2e", "#e94560"),   # default dark
}

STATUS_LABELS = {
    "live": "LIVE",
    "upcoming_today": "TODAY",
    "result": "FULL TIME",
    "upcoming": "UPCOMING",
}

STATUS_COLORS = {
    "live": "#ff2222",
    "upcoming_today": "#00cc66",
    "result": "#4488ff",
    "upcoming": "#ff9900",
}


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    ]
    for p in font_paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _load_font_regular(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
    ]
    for p in font_paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _draw_centered(draw: ImageDraw.Draw, text: str, y: int, font, color: str, width: int = CARD_W):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (width - tw) // 2
    draw.text((x, y), text, font=font, fill=color)
    return bbox[3] - bbox[1]  # height


def build_image(subject: dict, out_path: str) -> str:
    """Generate a 1080x1080 image card and save to out_path. Returns out_path."""
    t = subject["type"]
    m = subject["match"]
    code = m["competition_code"]
    bg_color, accent = LEAGUE_COLORS.get(code, LEAGUE_COLORS["_"])

    img = Image.new("RGB", (CARD_W, CARD_H), bg_color)
    draw = ImageDraw.Draw(img)

    # Background gradient bars
    bar_h = 140
    bar_img = Image.new("RGB", (CARD_W, bar_h), accent)
    img.paste(bar_img, (0, 0))
    img.paste(bar_img, (0, CARD_H - bar_h))

    # Status pill
    status_text = STATUS_LABELS.get(t, "MATCH")
    status_color = STATUS_COLORS.get(t, "#ffffff")
    font_status = _load_font(42)
    pill_w, pill_h = 260, 60
    pill_x = (CARD_W - pill_w) // 2
    draw.rounded_rectangle([pill_x, 155, pill_x + pill_w, 155 + pill_h],
                            radius=30, fill=status_color)
    bbox = draw.textbbox((0, 0), status_text, font=font_status)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((CARD_W - tw) // 2, 155 + (pill_h - th) // 2),
              status_text, font=font_status, fill=bg_color)

    # Competition name
    font_comp = _load_font_regular(36)
    comp_name = m["competition"]
    _draw_centered(draw, comp_name, 240, font_comp, accent)

    # VS line
    font_team = _load_font(88)
    font_vs = _load_font_regular(52)

    home = m["home"]
    away = m["away"]
    vs_y = 380

    # Wrap long team names
    max_chars = 14
    home_display = home if len(home) <= max_chars else home[:max_chars - 1] + "…"
    away_display = away if len(away) <= max_chars else away[:max_chars - 1] + "…"

    # Layout: HOME   vs   AWAY
    col_w = CARD_W // 3

    # home team
    bbox_h = draw.textbbox((0, 0), home_display, font=font_team)
    hw = bbox_h[2] - bbox_h[0]
    draw.text(((col_w - hw) // 2, vs_y), home_display, font=font_team, fill="#ffffff")

    # vs
    bbox_v = draw.textbbox((0, 0), "vs", font=font_vs)
    vw = bbox_v[2] - bbox_v[0]
    draw.text((col_w + (col_w - vw) // 2, vs_y + 20), "vs", font=font_vs, fill=accent)

    # away team
    bbox_a = draw.textbbox((0, 0), away_display, font=font_team)
    aw = bbox_a[2] - bbox_a[0]
    draw.text((2 * col_w + (col_w - aw) // 2, vs_y), away_display, font=font_team, fill="#ffffff")

    # Score or kick-off time
    font_score = _load_font(120)
    font_time = _load_font(72)
    score_y = 560

    if t in ("live", "result") and m["home_score"] is not None:
        score_str = f"{m['home_score']}  –  {m['away_score']}"
        _draw_centered(draw, score_str, score_y, font_score, "#ffffff")
        if t == "live" and m["minute"]:
            _draw_centered(draw, f"⏱ {m['minute']}'", score_y + 130, font_vs, status_color)
    else:
        ko = _ko_str(m)
        _draw_centered(draw, ko, score_y + 30, font_time, "#ffffff")
        _draw_centered(draw, "UTC", score_y + 110, font_comp, accent)

    # Bottom bar text
    font_bottom = _load_font(38)
    bb_text = "⚽  SOCCER UPDATES  ⚽"
    _draw_centered(draw, bb_text, CARD_H - bar_h + 40, font_bottom, bg_color)

    img.save(out_path, "JPEG", quality=95)
    return out_path
