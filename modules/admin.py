from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from utils.logging import log_command, safe_execute, is_admin
import os

AUTO_CHAT_ID = int(os.getenv("AUTO_CHAT_ID", "0"))
AUTO_ENABLED = True

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_command(update, "broadcast")
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ You are not authorized to use this command.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    message = " ".join(context.args)
    if AUTO_CHAT_ID:
        await context.bot.send_message(chat_id=AUTO_CHAT_ID, text=message, parse_mode="HTML")
        await update.message.reply_text("✅ Broadcast sent.")

async def toggleauto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_command(update, "toggleauto")
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ You are not authorized to use this command.")
        return
    global AUTO_ENABLED
    AUTO_ENABLED = not AUTO_ENABLED
    status = "enabled" if AUTO_ENABLED else "disabled"
    await update.message.reply_text(f"Auto-menu is now {status}.")

async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_command(update, "chatid")
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ You are not authorized to use this command.")
        return
    await update.message.reply_text(f"Chat ID: {update.effective_chat.id}")

def register(app):
    app.add_handler(CommandHandler("broadcast", lambda u, c: safe_execute(broadcast, u, c)))
    app.add_handler(CommandHandler("toggleauto", lambda u, c: safe_execute(toggleauto, u, c)))
    app.add_handler(CommandHandler("chatid", lambda u, c: safe_execute(chatid, u, c)))
