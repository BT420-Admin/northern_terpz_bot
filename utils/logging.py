import os
import traceback
from datetime import datetime

ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

def log_command(update, command_name):
    """Logs when a user runs a command."""
    user = update.effective_user
    now_str = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{now_str} {user.id} ({user.first_name}) used /{command_name}")

def log_event(tag: str, message: str, colour: str = "blue"):
    """
    Prints a timestamped, colour-coded log line.
    colour can be: blue, green, orange, red
    """
    colours = {
        "blue": "\033[94m",
        "green": "\033[92m",
        "orange": "\033[93m",
        "red": "\033[91m"
    }
    reset = "\033[0m"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    colour_code = colours.get(colour, "")
    print(f"{colour_code}[{timestamp}] {tag}: {message}{reset}")

def is_admin(user_id):
    """Checks if a given user ID matches the admin ID from .env."""
    return user_id == ADMIN_CHAT_ID

async def safe_execute(func, update, context):
    """
    Wraps a coroutine handler to catch and log exceptions without crashing the bot.
    """
    try:
        await func(update, context)
    except Exception as e:
        log_event("❌ ERROR", f"{e}\n{traceback.format_exc()}", colour="red")
        try:
            await update.message.reply_text("⚠️ An error occurred while processing your request.")
        except:
           pass
