from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from utils.logging import log_command, safe_execute
from utils.keyboards import build_links_keyboard
from utils.assets import send_menu

# Helper to reply whether it's a command or a button click
async def _reply(update: Update, context: ContextTypes.DEFAULT_TYPE, text=None, photo=None, reply_markup=None):
    if getattr(update, "callback_query", None):
        q = update.callback_query
        if text:
            await q.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)
        elif photo:
            await q.message.reply_photo(photo=photo, reply_markup=reply_markup)
    else:
        if text:
            await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)
        elif photo:
            await update.message.reply_photo(photo=photo, reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_command(update, "start")
    if update.effective_chat.type != "private":
        await _reply(update, context, "👋 Welcome to <b>Northern Terpz</b> Bot! Type /help for commands.")
        return
    await send_menu(context.bot, update.effective_chat.id)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_command(update, "about")
    await _reply(
        update,
        context,
        "🌿 <b>Northern Terpz</b> — Store and a community that’s always in session.",
        reply_markup=build_links_keyboard()
    )

async def links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_command(update, "links")
    await _reply(
        update,
        context,
        "🔗 <b>Official Northern Terpz Links</b>",
        reply_markup=build_links_keyboard()
    )

async def logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_command(update, "logo")
    with open("assets/Bot-Logo.png", "rb") as img:
        await _reply(update, context, photo=img)

def register(app):
    app.add_handler(CommandHandler("start", lambda u, c: safe_execute(start, u, c)))
    app.add_handler(CommandHandler("about", lambda u, c: safe_execute(about, u, c)))
    app.add_handler(CommandHandler("links", lambda u, c: safe_execute(links, u, c)))
    app.add_handler(CommandHandler("logo", lambda u, c: safe_execute(logo, u, c)))
