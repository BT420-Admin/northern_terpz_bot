from modules.logging_setup import logger

def log_event(event_type: str, message: str, colour: str = "white"):
    """
    Logs a formatted event to console and file.
    event_type: short label like 'NEW MEMBER', 'COMMAND', 'ERROR'
    message: details of the event
    colour: rich colour name (green, yellow, red, cyan, etc.)
    """
    emoji_map = {
        "NEW MEMBER": "🟢",
        "COMMAND": "🔵",
        "WARNING": "🟡",
        "ERROR": "🔴",
        "INFO": "ℹ️"
    }
    emoji = emoji_map.get(event_type.upper(), "📜")
    logger.info(f"[{colour}]{emoji} {event_type}[/] — {message}")
