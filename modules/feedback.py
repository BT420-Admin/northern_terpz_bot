import os
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMemberUpdated
from telegram.ext import CommandHandler, ContextTypes, ChatMemberHandler
from utils.logging import log_command, safe_execute

GROUP_CHAT_ID = int(os.getenv("AUTO_CHAT_ID", "0"))
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
STATIC_GROUP_LINK = "https://t.me/+jO2iG16k9f5hNTY0"

DATA_FILE = "referrals.json"
FEEDBACK_FILE = "feedback_log.txt"

referrals = {}        # { inviter_id: count }
invite_links = {}     # { invite_link: inviter_id }

BUILD_TAG = "NT-FEEDBACK v1.0"

# --- Persistence helpers ---
def load_data():
    global referrals, invite_links
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            referrals = {int(k): v for k, v in data.get("referrals", {}).items()}
            invite_links = data.get("invite_links", {})
    else:
        referrals, invite_links = {}, {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "referrals": referrals,
            "invite_links": invite_links
        }, f)

# --- Referral commands ---
async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_command(update, "referral")
    user = update.effective_user
    user_id = user.id

    if not GROUP_CHAT_ID:
        await update.message.reply_text(f"🔗 Your group link: {STATIC_GROUP_LINK}")
        return

    try:
        invite = await context.bot.create_chat_invite_link(
            chat_id=GROUP_CHAT_ID,
            name=f"Referral from {user_id}",
            creates_join_request=False,
            expire_date=None,
            member_limit=0
        )

        referrals.setdefault(user_id, 0)
        invite_links[invite.invite_link] = user_id
        save_data()

        await update.message.reply_text(
            f"🔗 Your personal invite link:\n{invite.invite_link}\n"
            f"Referrals so far: {referrals[user_id]}"
        )

    except Exception as e:
        await update.message.reply_text(
            f"⚠️ Could not create a personal link ({e})\n"
            f"Here’s the group link instead:\n{STATIC_GROUP_LINK}"
        )

async def track_joins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member = update.chat_member
    if chat_member.new_chat_member.status == "member":
        inviter_id = None
        if chat_member.invite_link:
            inviter_id = invite_links.get(chat_member.invite_link.invite_link)
        if inviter_id:
            referrals[inviter_id] = referrals.get(inviter_id, 0) + 1
            save_data()
            await context.bot.send_message(
                chat_id=inviter_id,
                text=f"🎉 Someone joined Northern Terpz via your invite!"
            )

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not referrals:
        await update.message.reply_text("📊 No referrals yet.")
        return
    sorted_referrals = sorted(referrals.items(), key=lambda x: x[1], reverse=True)
    text = "🏆 Referral Leaderboard 🏆\n\n"
    for i, (uid, count) in enumerate(sorted_referrals, start=1):
        try:
            user = await context.bot.get_chat(uid)
            name = user.full_name
        except:
            name = f"User {uid}"
        text += f"{i}. {name} — {count} referrals\n"
    await update.message.reply_text(text)

async def reset_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ You are not authorized to reset the leaderboard.")
        return
    referrals.clear()
    invite_links.clear()
    save_data()
    await update.message.reply_text("✅ Referral leaderboard reset.")

# --- Old /feedback command ---
async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_command(update, "feedback_command")
    user = update.effective_user
    message_text = " ".join(context.args) if context.args else None

    if not message_text:
        await update.message.reply_text(
            "✏️ Please include your feedback after the command.\nExample: `/feedback Love the bot!`",
            parse_mode="Markdown"
        )
        return

    # Save to file
    with open(FEEDBACK_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {user.full_name} ({user.id}): {message_text}\n")

    # Send confirmation to user
    await update.message.reply_text("✅ Thanks! Your feedback has been recorded.")

    # Forward to admin
    if ADMIN_CHAT_ID:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"📩 Feedback from {user.full_name} ({user.id}):\n\n{message_text}"
        )

# --- View feedback ---
async def view_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ You are not authorized to view feedback.")
        return

    if not os.path.exists(FEEDBACK_FILE):
        await update.message.reply_text("📭 No feedback yet.")
        return

    with open(FEEDBACK_FILE, "r") as f:
        lines = f.readlines()

    if not lines:
        await update.message.reply_text("📭 No feedback yet.")
        return

    try:
        count = int(context.args[0]) if context.args else 10
    except ValueError:
        count = 10

    last_entries = lines[-count:]
    text = "🗒 Last Feedback Entries:\n\n" + "".join(last_entries)

    if len(text) > 4000:
        text = text[-4000:]

    await update.message.reply_text(f"```\n{text}\n```", parse_mode="Markdown")

# --- New interactive feedback flow ---
async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the feedback button click from welcome.py"""
    user = update.effective_user
    log_command(update, "feedback_button")

    feedback_text = (
        "🟠 *Northern Terpz Feedback*\n\n"
        "We value your thoughts — they help us keep the vibe premium and the community strong.\n\n"
        "💬 Please type your feedback below.\n"
        "_(Your message will be sent privately to the admin team)_\n\n"
        f"`Build: {BUILD_TAG}`"
    )

    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_feedback")]]

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=feedback_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            text=feedback_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    context.user_data["awaiting_feedback"] = True

async def handle_feedback_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Captures the user's feedback message and sends it to admins"""
    if context.user_data.get("awaiting_feedback"):
        feedback_msg = update.message.text
        user = update.effective_user

        # Save to file
        with open(FEEDBACK_FILE, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {user.full_name} ({user.id}): {feedback_msg}\n")

        # Forward to admin
        if ADMIN_CHAT_ID:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"🟠 *Feedback from {user.full_name}:*\n\n{feedback_msg}",
                parse_mode="Markdown"
            )

        await update.message.reply_text("✅ Thanks for your feedback! Our team will review it soon.")
        context.user_data["awaiting_feedback"] = False

async def cancel_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels the feedback process"""
    context.user_data["awaiting_feedback"] = False
    await update.callback_query.edit_message_text("❌ Feedback cancelled.")
    log_command(update, "feedback_cancelled")

# --- Register handlers ---
def register(app):
    load_data()
    app.add_handler(CommandHandler("referral", lambda u, c: safe_execute(referral, u, c)))
    app.add_handler(CommandHandler("leaderboard", lambda u, c: safe_execute(leaderboard, u, c)))
    app.add_handler(CommandHandler("resetleaderboard", lambda u, c: safe_execute(reset_leaderboard, u, c)))
    app.add_handler(CommandHandler("feedback", lambda u, c: safe_execute(feedback_command, u, c)))
