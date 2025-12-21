import logging

from discordbot.discord_handler import DiscordHandler, default_embed
from utils.config import ConfigStore

config = ConfigStore()._config


logger = logging.getLogger("songs_introduction")

if not logger.handlers:  # 重複を防ぐ
    # コンソールハンドラ
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    # Discordハンドラ
    embed_template = default_embed()
    if not config.is_production:
        embed_template.title = "[DEV] " + embed_template.title

    discord_handler = DiscordHandler(
        send_channel=config.discord_channel_id,
        embed_template=embed_template,
    )
    discord_handler.setLevel(logging.WARNING)
    logger.addHandler(discord_handler)

    logger.setLevel(logging.DEBUG)
