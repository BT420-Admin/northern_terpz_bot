from datetime import datetime
import os
from utils.assets import send_menu

AUTO_CHAT_ID = int(os.getenv("AUTO_CHAT_ID", "0"))
AUTO_ENABLED = True

async def auto_menu_job(context):
    now_str = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    if AUTO_ENABLED and AUTO_CHAT_ID != 0:
        print(f"{now_str} Posting daily menu to {AUTO_CHAT_ID}")
        await send_menu(context.bot, AUTO_CHAT_ID)
    else:
        print(f"{now_str} Auto-menu disabled or AUTO_CHAT_ID not set — skipping post.")
