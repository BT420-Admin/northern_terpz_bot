import time
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from utils.logging import log_command, safe_execute

START_TIME = time.time()

async def version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_command(update, "version")
    await update.message.reply_text("Northern Terpz Bot v1.2 — Official Build ✅")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_command(update, "ping")
    start = time.time()
    msg = await update.message.reply_text("Pong!")
    latency = round((time.time() - start) * 1000)
    await msg.edit_text(f"Pong! 🏓 {latency}ms")

async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_command(update, "uptime")
    elapsed = time.time() - START_TIME
    hours, rem = divmod(int(elapsed), 3600)
    minutes, seconds = divmod(rem, 60)
    await update.message.reply_text(f"⏱ Uptime: {hours}h {minutes}m {seconds}s")

def register(app):
    app.add_handler(CommandHandler("version", lambda u, c: safe_execute(version, u, c)))
    app.add_handler(CommandHandler("ping", lambda u, c: safe_execute(ping, u, c)))
    app.add_handler(CommandHandler("uptime", lambda u, c: safe_execute(uptime, u, c)))
