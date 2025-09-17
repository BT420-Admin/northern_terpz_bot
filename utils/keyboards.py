from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def build_links_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Telegram", url="https://t.me/+jO2iG16k9f5hNTY0")],
        [InlineKeyboardButton("🎮 Discord", url="https://discord.gg/MBM57QPm")],
        [InlineKeyboardButton("📸 Instagram", url="https://www.instagram.com/northern_terpz?igsh=N2xubjN0dHZ6NWxi")]
    ])
