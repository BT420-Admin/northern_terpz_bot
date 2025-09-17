import logging
from rich.logging import RichHandler

# Base logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)]
)

# File logging
from logging.handlers import RotatingFileHandler

file_handler = RotatingFileHandler(
    "bot.log",           # Log file name
    maxBytes=500_000,    # Rotate after ~500 KB
    backupCount=5,       # Keep 5 old logs: bot.log.1, bot.log.2, ...
    encoding="utf-8"
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.getLogger().addHandler(file_handler)

# Silence noisy libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

logger = logging.getLogger("NorthernTerpz")
