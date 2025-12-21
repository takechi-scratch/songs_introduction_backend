from fastapi import APIRouter, Depends, HTTPException

from utils.auth import get_current_user
from utils.dependencies import get_playlist_manager
from utils.fastapi_models import CreatePlaylistRequest
from utils.youtube.playlists import PlaylistManager
from utils.logger import logger

router = APIRouter(tags=["YouTube"])


@router.post("/playlists/create/")
async def create_youtube_playlist(
    query: CreatePlaylistRequest,
    cred: dict = Depends(get_current_user),
    playlist_manager: PlaylistManager = Depends(get_playlist_manager),
):
    """YouTubeのプレイリストを作成し、指定した動画を追加します。"""
    try:
        logger.info(f"Creating YouTube playlist: {query.title} with {len(query.video_ids)} videos")
        logger.debug(f"User ID: {cred.get('uid', 'unknown')} email: {cred.get('email', 'unknown')}")
        playlist = await playlist_manager.create_playlist(query.title, query.description, query.video_ids)
        return playlist
    except HTTPException as e:
        raise e
