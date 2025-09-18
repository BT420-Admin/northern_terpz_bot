import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ChatMemberHandler, CallbackQueryHandler, CommandHandler, ContextTypes
from utils.logging import safe_execute, log_event
from modules.menu import about as about_cmd, start as menu_cmd
from modules import feedback, referrals
from utils.logging import log_event
from modules.utils import log_event

GROUP_CHAT_ID = int(os.getenv("AUTO_CHAT_ID", "0"))
BUILD_TAG = "NT-Bot-v1.0"

# Store inviter IDs for each new user so we can track conversions
user_inviter_map = {}

async def send_welcome_message(chat_id, context: ContextTypes.DEFAULT_TYPE, user_full_name: str, inviter_name: str = None, inviter_id: int = None):
    welcome_text = (
        "🍁💨🍁 *Welcome to Northern Terpz!* 🍁💨🍁\n\n"
        f"👋 Hey {user_full_name}!\n"
        f"{f'You were invited by {inviter_name}.\n' if inviter_name else ''}"
        "We’re all about *premium quality*, *community vibes*, and *privacy‑first* engagement.\n\n"
        "🛒 *Explore the menu*\n"
        "📝 *Learn about us*\n"
        "🗣 *Share your thoughts*\n\n"
        f"`Build: {BUILD_TAG}`"
    )

    keyboard = [
        [InlineKeyboardButton("📝 About", callback_data="about_cmd")],
        [InlineKeyboardButton("🆘️ Help", callback_data="menu_cmd")],
        [InlineKeyboardButton("🗣 Send Feedback", callback_data="feedback_cmd")]
    ]

    # Store inviter for conversion tracking
    if inviter_id:
        user_inviter_map[chat_id] = inviter_id

    await context.bot.send_message(
        chat_id=chat_id,
        text=welcome_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member = update.chat_member

    if GROUP_CHAT_ID and chat_member.chat.id != GROUP_CHAT_ID:
        return

    if chat_member.new_chat_member.status == "member":
        inviter_name = None
        inviter_id = None

        if chat_member.invite_link:
            inviter_id = context.bot_data.get("invite_links", {}).get(
                chat_member.invite_link.invite_link
            )
            if inviter_id:
                try:
                    inviter_user = await context.bot.get_chat(inviter_id)
                    inviter_name = inviter_user.full_name
                except Exception:
                    inviter_name = "someone"

        if inviter_id:
            referrals.record_referral(inviter_id)

    await send_welcome_message(
        chat_id=chat_member.chat.id,
        context=context,
        user_full_name=chat_member.new_chat_member.full_name,
        inviter_name=invite,
        inviter_id=inviter_id
    )

    await menu_cmd(update, context)

    log_event("NEW MEMBER", f"{chat_member.new_chat_member.user.full_name} joined", "green")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_welcome_message(
        chat_id=update.effective_chat.id,
        context=context,
        user_full_name=update.effective_user.full_name
    )
    log_event("COMMAND", f"/start by {update.effective_user.full_name}", "cyan")
    await about_cmd(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    log_event("🔵 BUTTON CLICK", f"{query.data} by {query.from_user.full_name}", colour="blue")

    if query.data == "about_cmd":
        await about_cmd(update, context)  # pass update, not query

    elif query.data == "menu_cmd":
        await menu_cmd(update, context)   # pass update, not query

    elif query.data == "feedback_cmd":
        inviter_id = user_inviter_map.get(query.from_user.id)
        if inviter_id:
            referrals.record_conversion(inviter_id)
        await feedback.feedback(update, context)  # pass update
        log_event("BUTTON", f"{query.from_user.full_name} pressed {query.data}", "yellow")
def register(app):
    app.add_handler(ChatMemberHandler(
        lambda u, c: safe_execute(welcome_new_member, u, c),
        ChatMemberHandler.CHAT_MEMBER
    ))
    app.add_handler(CommandHandler("start", lambda u, c: safe_execute(start_command, u, c)))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: safe_execute(button_handler, u, c),
        pattern="^(about_cmd|menu_cmd|feedback_cmd)$"
    ))
