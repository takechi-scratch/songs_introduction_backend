import discord
from discord.ext import commands

from src.utils.config import ConfigStore

config = ConfigStore()._config


class BackendDiscordClient(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_channel = None

    async def on_ready(self):
        self.default_channel = self.get_channel(config.discord_channel_id)
        print(f"Logged on as {self.user}!")


default_intents = discord.Intents.default()
default_intents.message_content = True
