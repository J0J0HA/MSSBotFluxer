import fluxer
import os
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def get_log_level() -> int:
    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    return getattr(logging, log_level, logging.INFO)


# Set up logging
logging.basicConfig(level=get_log_level())
logger = logging.getLogger(__name__)

bot = fluxer.Bot(
    command_prefix=os.getenv("PREFIX", "!"), intents=fluxer.Intents.default()
)


async def load_extensions():
    cogs_dir = Path(__file__).parent / "cogs"
    for filename in cogs_dir.glob("*.py"):
        await bot.load_extension(f"cogs.{filename.name[:-3]}")


@bot.event
async def on_ready():
    if bot.user is not None:
        logger.info(f"Logged in as {bot.user}")
    else:
        logger.error("Logged in, but bot user is None. Exiting.")


if __name__ == "__main__":
    asyncio.run(load_extensions())
    bot.run(os.getenv("FLUXER_TOKEN", ""))