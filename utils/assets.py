from utils.keyboards import build_links_keyboard
from utils.tips import get_tip

ASSETS_DIR = "assets"

async def send_menu(bot, chat_id):
    await bot.send_photo(chat_id=chat_id, photo=open(f"{ASSETS_DIR}/Bot-Logo.png", "rb"))
    welcome_text = (
        "👋 Welcome to <b>Northern Terpz</b> Bot!\n\n"
        "🌿 Open‑source tools, privacy‑first automation, and a community that’s always in session.\n\n"
        f"{get_tip()}\n\n"
        "🤖 <b>Commands you can use:</b>\n"
        "/about — Who we are + links\n"
        "/logo — Official logo\n"
        "/version — Build info\n"
        "/links — All official links\n"
        "/ping — Bot health check\n"
        "/uptime — Bot running time\n"
        "/feedback — Send feedback to the dev\n"
        "/referral — Get your invite link"
    )
    await bot.send_message(chat_id=chat_id, text=welcome_text, parse_mode="HTML", reply_markup=build_links_keyboard())
