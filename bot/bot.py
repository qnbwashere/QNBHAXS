"""
Telegram bot interface — control the poster from your phone.

Commands:
  /start   — welcome + current status
  /status  — show scheduler state, next post time, post count
  /post    — trigger an immediate post right now
  /preview — generate image + caption without posting to Instagram
  /pause   — pause the auto-scheduler
  /resume  — resume the auto-scheduler
  /logs    — show recent activity log
"""

import asyncio
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

from state import app_state
from fetcher import pick_post_subject
from content import build_caption, build_image


def _status_text() -> str:
    s = app_state
    paused = "PAUSED ⏸" if s.paused else "RUNNING ▶"
    nxt = s.next_post_at.strftime("%H:%M:%S UTC") if s.next_post_at else "—"
    last = s.last_post_at.strftime("%H:%M:%S UTC") if s.last_post_at else "never"
    return (
        f"*Scheduler:* {paused}\n"
        f"*Posts sent:* {s.post_count}\n"
        f"*Last post:* {last}\n"
        f"*Next post:* {nxt}"
    )


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ *Sports Instagram Auto-Poster*\n\n"
        + _status_text()
        + "\n\n"
        "*Commands:*\n"
        "/post — post right now\n"
        "/preview — preview without posting\n"
        "/status — show status\n"
        "/pause — pause auto-posting\n"
        "/resume — resume auto-posting\n"
        "/logs — recent activity",
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(_status_text(), parse_mode=ParseMode.MARKDOWN)


async def cmd_pause(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    app_state.paused = True
    app_state.add_log("Paused via Telegram.")
    await update.message.reply_text("⏸ Scheduler paused. Send /resume to start again.")


async def cmd_resume(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    app_state.paused = False
    app_state.add_log("Resumed via Telegram.")
    await update.message.reply_text("▶ Scheduler resumed!")


async def cmd_logs(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lines = app_state.recent_logs(15)
    text = "\n".join(lines) if lines else "No logs yet."
    await update.message.reply_text(f"```\n{text}\n```", parse_mode=ParseMode.MARKDOWN)


async def cmd_post(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📤 Triggering a post now…")
    app_state.force_post.set()


async def cmd_preview(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Fetching match data for preview…")
    subject = pick_post_subject()
    if not subject:
        await update.message.reply_text("No match data available right now.")
        return

    caption = build_caption(subject)
    m = subject["match"]

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        img_path = f.name
    try:
        build_image(subject, img_path)
        with open(img_path, "rb") as img_file:
            await update.message.reply_photo(
                photo=img_file,
                caption=f"*PREVIEW* (not posted)\n\n{caption[:900]}",
                parse_mode=ParseMode.MARKDOWN,
            )
    except Exception as e:
        await update.message.reply_text(f"Image error: {e}\n\nCaption:\n{caption[:500]}")
    finally:
        Path(img_path).unlink(missing_ok=True)


async def send_post_notification(app: Application, image_path: str, caption: str, chat_id: str):
    """Called by scheduler after a successful Instagram post."""
    try:
        with open(image_path, "rb") as f:
            await app.bot.send_photo(
                chat_id=chat_id,
                photo=f,
                caption=f"✅ *Posted to Instagram!*\n\n{caption[:900]}",
                parse_mode=ParseMode.MARKDOWN,
            )
    except Exception as e:
        print(f"[bot] Failed to send notification: {e}")


def build_app(token: str) -> Application:
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("pause", cmd_pause))
    app.add_handler(CommandHandler("resume", cmd_resume))
    app.add_handler(CommandHandler("logs", cmd_logs))
    app.add_handler(CommandHandler("post", cmd_post))
    app.add_handler(CommandHandler("preview", cmd_preview))
    return app
