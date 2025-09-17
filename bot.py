import os
import importlib
import pkgutil
import logging
import time
from telegram import BotCommand, ChatAction
from modules.commands import links, version, logo, about, uptime_cmd, ping
from datetime import time as dtime
from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    CommandHandler,
    filters
)

from utils.scheduler import auto_menu_job
from utils.logging import safe_execute
from modules import welcome, feedback, referrals
from modules.logging_setup import logger
from rich.logging import RichHandler
from modules.utils import log_event

# Base logging config
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more detail
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(rich_tracebacks=True, markup=True)  # Pretty colours + tracebacks
    ]
)

# File logging (keeps a clean history)
file_handler = logging.FileHandler("bot.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.getLogger().addHandler(file_handler)

# Silence noisy libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

logger = logging.getLogger("NorthernTerpz")

# --- Enable debug logging if requested ---
if "--debug" in os.sys.argv:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG
    )
    print("🛠 Debug mode ON — all updates will be logged")
else:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

# --- Load environment variables ---
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
POST_HOUR = int(os.getenv("POST_HOUR", "9"))
POST_MINUTE = int(os.getenv("POST_MINUTE", "0"))

if not TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN not set in .env")

# --- Build the bot application ---
app = (
    ApplicationBuilder()
    .token(TOKEN)
    .post_init(lambda app: app.bot.set_my_commands([
        BotCommand("links",   "Show useful links"),
        BotCommand("version", "Show version & uptime"),
        BotCommand("logo",    "Display the logo"),
        BotCommand("about",   "About Northern Terpz"),
        BotCommand("uptime",  "Show uptime"),
        BotCommand("ping",    "Health check with stats"),
    ]))
    .build()
)

# ─── Register Northern Terpz commands ───────────────────────────────────
app.add_handler(CommandHandler("links",   safe_execute(links)))
app.add_handler(CommandHandler("version", safe_execute(version)))
app.add_handler(CommandHandler("logo",    safe_execute(logo)))
app.add_handler(CommandHandler("about",   safe_execute(about)))
app.add_handler(CommandHandler("uptime",  safe_execute(uptime_cmd)))
app.add_handler(CommandHandler("ping",    safe_execute(ping)))

# --- Register core modules ---
welcome.register(app)
feedback.register(app)
referrals.register(app)  # so /referral and /leaderboard work

# Feedback message handler (captures typed feedback)
app.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    lambda u, c: safe_execute(feedback.handle_feedback_message, u, c)
))

# Feedback cancel button handler
app.add_handler(CallbackQueryHandler(
    lambda u, c: safe_execute(feedback.cancel_feedback, u, c),
    pattern="^cancel_feedback$"
))

# --- Simple ping command for testing ---
async def ping(update, context):
    await update.message.reply_text("Pong 🏓")

app.add_handler(CommandHandler("ping", ping))

# --- Catch-all debug logger for any update ---
async def debug_logger(update, context):
    print(f"📥 RAW UPDATE: {update.to_dict()}")

app.add_handler(MessageHandler(filters.ALL, debug_logger), group=99)

# --- Schedule daily menu post ---
app.job_queue.run_daily(
    auto_menu_job,
    time=dtime(hour=POST_HOUR, minute=POST_MINUTE)
)

# --- Auto-load other modules (skip ones we already registered) ---
for _, module_name, _ in pkgutil.iter_modules(['modules']):
    if module_name not in ('welcome', 'feedback', 'referrals'):
        importlib.import_module(f'modules.{module_name}')

# --- Start the bot ---
if __name__ == "__main__":
    print("🚀 Northern_Terpz-bot is now running...")
    app.run_polling()
