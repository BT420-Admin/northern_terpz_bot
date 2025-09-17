import time
import platform
import psutil
from telegram import ChatAction, Update
from telegram.ext import ContextTypes
from modules.utils import start_time, BOT_VERSION, get_links, get_about, get_logo

async def links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("\n".join(get_links()))

async def version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = time.strftime(
        "%H:%M:%S", time.gmtime(time.time() - start_time)
    )
    await update.message.reply_text(f"Version: {BOT_VERSION}\nUptime: {uptime}")
async def logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(photo=get_logo())

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_about())
async def uptime_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    up_secs = time.time() - start_time
    await update.message.reply_text(time.strftime("%H:%M:%S", time.gmtime(up_secs)))

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t0 = time.monotonic()
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING
    )
    latency_ms = (time.monotonic() - t0) * 1000
    up_secs = time.time() - start_time
    uptime_str = time.strftime("%Hh %Mm %Ss", time.gmtime(up_secs))
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory().percent

    text = (
        f"🏓 Pong!\n"
        f"Latency: {latency_ms:.0f} ms\n"
        f"Uptime: {uptime_str}\n"
        f"CPU: {cpu:.0f}%\n"
        f"Memory: {mem:.0f}%\n"
        f"Python: {platform.python_version()}"
    )
    await update.message.reply_text(text)
