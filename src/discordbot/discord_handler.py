# Discord logging handler for sending log messages as embeds to a Discord channel.
# created by takechi in MIT License

import logging
from typing import Optional, Callable
import asyncio

import discord
from discord import Embed
from discord.ext import commands


class DiscordHandler(logging.Handler):
    def __init__(
        self,
        send_channel: int | discord.abc.Messageable,
        bot: Optional[commands.Bot] = None,
        token: Optional[str] = None,
        embed_factory: Optional[Callable[[logging.LogRecord], Embed]] = None,
        embed_template: Optional[Embed] = None,
        level=logging.NOTSET,
    ):
        super().__init__(level=level)
        self.send_channel = send_channel
        self.bot: Optional[commands.Bot] = None

        if bot is not None or token is not None:
            self.init_bot(bot=bot, token=token)
        else:
            print("DiscordHandler is waiting bot initialized; call init_bot() later.")

        self.embed_factory = embed_factory
        self.embed_template = embed_template or default_embed()

        self.send_queue = asyncio.Queue()

    def emit(self, record):
        try:
            if self.embed_factory is not None:
                embed = self.embed_factory(record)
            else:
                embed = self.embed_template.copy()
                embed.title = embed.title % record.__dict__
                embed.description = embed.description % record.__dict__

                # fieldsは読み取り専用のため、そのまま書き換えはできない
                fields = embed.fields
                embed.clear_fields()
                for field in fields:
                    embed.add_field(name=field.name, value=field.value % record.__dict__, inline=field.inline)

                if embed.color is None:
                    level = record.levelno
                    if level >= logging.CRITICAL:
                        embed.color = 0xB31478
                    elif level >= logging.ERROR:
                        embed.color = 0xCC0022
                    elif level >= logging.WARNING:
                        embed.color = 0xE63D00
                    elif level >= logging.INFO:
                        embed.color = 0x1E90FF
                    else:
                        embed.color = 0x808080

                embed.set_footer(text=embed.footer.text % record.__dict__)
                embed.timestamp = discord.utils.utcnow()

            if self._is_ready_to_send():
                asyncio.create_task(self.send_channel.send(embed=embed))
            else:
                self.send_queue.put_nowait(embed)

        except Exception:
            self.handleError(record)

    async def handle_send_queue(self):
        while True:
            if self._is_ready_to_send():
                while self.send_queue.qsize() > 0:
                    embed = await self.send_queue.get()
                    await self.send_channel.send(embed=embed)

            await asyncio.sleep(10)

    def init_bot(self, bot: Optional[commands.Bot] = None, token: Optional[str] = None):
        if bot is not None:
            self.bot = bot
        else:
            intents = discord.Intents.default()
            intents.message_content = True
            self.bot = commands.Bot(intents=intents, command_prefix="!")

            loop = asyncio.get_event_loop()
            loop.create_task(self.bot.start(token))

        # botを渡した場合でも、キュー処理タスクを起動する
        loop = asyncio.get_event_loop()
        loop.create_task(self.handle_send_queue())

        if isinstance(self.send_channel, int):
            channel_id = self.send_channel  # IDを保存

            @self.bot.listen("on_ready")
            async def on_ready_handler():
                self.send_channel = self.bot.get_channel(channel_id)
                if self.send_channel is None:
                    raise ValueError(f"Channel with ID {channel_id} not found")

                print("Ready to run Discord bot!")

            print("Discord bot is starting...")

        else:
            print("Discord bot initialized successfully.")

    def _is_ready_to_send(self) -> bool:
        return self.bot is not None and isinstance(self.send_channel, discord.abc.Messageable)


def default_embed() -> Embed:
    embed = Embed(title="%(filename)s 実行ログ", description="%(message)s")
    embed.set_footer(text="Discord Log Handler@takechi")

    return embed
