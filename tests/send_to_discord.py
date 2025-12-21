from logging import getLogger, StreamHandler, DEBUG
from src.discordbot.discord_handler import DiscordHandler
from dotenv import load_dotenv
import os

load_dotenv()

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)

discord_handler = DiscordHandler(
    send_channel=1302532991989321769,
    token=os.getenv("DISCORD_TOKEN"),
)
discord_handler.setLevel(DEBUG)

logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.addHandler(discord_handler)
logger.propagate = False

if __name__ == "__main__":
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    import asyncio

    asyncio.get_event_loop().run_forever()
