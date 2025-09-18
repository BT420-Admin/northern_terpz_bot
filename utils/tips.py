import random

TIPS = [
    "💡 Tip: Use /uptime to check if the bot’s been running smoothly.",
    "💡 Tip: Click the buttons below instead of typing links.",
    "💡 Tip: /feedback sends your thoughts straight to the dev.",
    "💡 Tip: /ping checks bot speed instantly.",
    "💡 Tip: Keep your build official — only shop from trusted suppliers."
]

def get_tip():
    return random.choice(TIPS)
