import os
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from utils.logging import safe_execute, log_command

# Simple in-memory store for testing
referral_counts = {}
conversion_counts = {}

# Load admin IDs from .env (comma-separated)
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

def record_referral(inviter_id: int):
    """Increment referral count for inviter_id."""
    if inviter_id:
        referral_counts[inviter_id] = referral_counts.get(inviter_id, 0) + 1

def record_conversion(inviter_id: int):
    """Increment conversion count for inviter_id."""
    if inviter_id:
        conversion_counts[inviter_id] = conversion_counts.get(inviter_id, 0) + 1

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_command(update, "referral")
    user_id = update.effective_user.id
    referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
    await update.message.reply_text(
        f"🔗 Your referral link:\n{referral_link}\n\n"
        "Share this link — when someone joins via it, you’ll earn a point!"
    )

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_command(update, "leaderboard")

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Check if user is in ADMIN_IDS or is a chat admin
    is_admin = False
    if user_id in ADMIN_IDS:
        is_admin = True
    else:
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            if member.status in ("administrator", "creator"):
                is_admin = True
        except Exception:
            pass

    if not is_admin:
        await update.message.reply_text("⛔ You are not authorised to view the leaderboard.")
        return

    if not referral_counts:
        await update.message.reply_text("📊 No referrals yet.")
        return

    sorted_board = sorted(referral_counts.items(), key=lambda x: x[1], reverse=True)
    text = "🏆 *Referral Leaderboard:*\n\n"
    for idx, (uid, count) in enumerate(sorted_board, start=1):
        try:
            user = await context.bot.get_chat(uid)
            conversions = conversion_counts.get(uid, 0)
            text += f"{idx}. {user.full_name} — {count} joins, {conversions} conversions\n"
        except Exception:
            text += f"{idx}. [User {uid}] — {count} joins, {conversion_counts.get(uid, 0)} conversions\n"
    await update.message.reply_text(text, parse_mode="Markdown")

def register(app):
    app.add_handler(CommandHandler("referral", lambda u, c: safe_execute(referral, u, c)))
    app.add_handler(CommandHandler("leaderboard", lambda u, c: safe_execute(leaderboard, u, c)))
