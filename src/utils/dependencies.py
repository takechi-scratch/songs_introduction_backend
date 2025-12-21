from fastapi import Request

from src.db.songs_database import SongsDatabase
from src.utils.config import ConfigStore
from src.utils.youtube.playlists import PlaylistManager


def get_db(request: Request) -> SongsDatabase:
    return request.app.state.db


def get_playlist_manager(request: Request) -> PlaylistManager:
    return request.app.state.playlist_manager


async def get_config_store(request: Request) -> ConfigStore:
    return request.app.state.config_store
