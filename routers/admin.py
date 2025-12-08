from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from utils.auth import get_current_user
from utils.config import ConfigStore
from utils.dependencies import get_playlist_manager, get_config_store
from utils.youtube.playlists import PlaylistManager
from utils.youtube.api import OAuthClient


router = APIRouter(tags=["Admin"])


class UpdateRefreshTokenRequest(BaseModel):
    token: str


@router.post("/admin/update-refresh-token/")
async def update_refresh_token(
    request: UpdateRefreshTokenRequest,
    cred: dict = Depends(get_current_user),
    playlist_manager: PlaylistManager = Depends(get_playlist_manager),
    config_store: ConfigStore = Depends(get_config_store),
):
    """YouTube OAuthのリフレッシュトークンを更新するエンドポイント"""
    if not cred.get("admin", False):
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")

    await config_store.update_config(youtube_oauth_refresh_token=request.token)

    oauth_client: OAuthClient = playlist_manager.oauth_client
    oauth_client.refresh_token = request.token
    await oauth_client.refresh_access_token()
    return {"status": "success"}
