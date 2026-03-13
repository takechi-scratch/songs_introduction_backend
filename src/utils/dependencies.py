from fastapi import Request

from src.db.comment_database import CommentsDatabase
from src.db.user_database import UsersDatabase
from src.discordbot.bot import BackendDiscordClient
from src.db.songs_database import SongsDatabase
from src.utils.config import ConfigStore
from src.utils.youtube.playlists import PlaylistManager


def get_db(request: Request) -> SongsDatabase:
    return request.app.state.db


def get_users_db(request: Request) -> UsersDatabase:
    return request.app.state.users_db


def get_comments_db(request: Request) -> CommentsDatabase:
    return request.app.state.comments_db


def get_playlist_manager(request: Request) -> PlaylistManager:
    return request.app.state.playlist_manager


async def get_config_store(request: Request) -> ConfigStore:
    return request.app.state.config_store


async def get_discord_client(request: Request) -> BackendDiscordClient:
    return request.app.state.discord_client
