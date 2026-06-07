from starlette.requests import HTTPConnection

from src.db.comment_database import CommentsDatabase
from src.db.user_database import UsersDatabase
from src.discordbot.bot import BackendDiscordClient
from src.db.songs_database import SongsDatabase
from src.utils.config import ConfigStore
from src.utils.youtube.playlists import PlaylistManager


def get_db(connection: HTTPConnection) -> SongsDatabase:
    return connection.app.state.db


def get_users_db(connection: HTTPConnection) -> UsersDatabase:
    return connection.app.state.users_db


def get_comments_db(connection: HTTPConnection) -> CommentsDatabase:
    return connection.app.state.comments_db


def get_playlist_manager(connection: HTTPConnection) -> PlaylistManager:
    return connection.app.state.playlist_manager


async def get_config_store(connection: HTTPConnection) -> ConfigStore:
    return connection.app.state.config_store


async def get_discord_client(connection: HTTPConnection) -> BackendDiscordClient:
    return connection.app.state.discord_client
