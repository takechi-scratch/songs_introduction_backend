import discord
from discord.ext import commands


class BackendDiscordClient(commands.Bot):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")


default_intents = discord.Intents.default()
default_intents.message_content = True
