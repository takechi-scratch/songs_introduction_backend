from datetime import datetime, timedelta
from fastapi import HTTPException
from pydantic import BaseModel

from src.utils.logger import logger
from src.utils.youtube.api import OAuthClient


class YoutubePlaylist(BaseModel):
    id: str
    title: str
    description: str
    createdAt: datetime
    videoIDs: list[str]


class PlaylistManager:
    def __init__(self, oauth_client: OAuthClient, ttl: timedelta = timedelta(days=3)):
        """曲のプレイリスト管理クラス

        Args:
            oauth_client (OAuthClient): YouTube Data APIのクライアント
            ttl (timedelta, optional): キャッシュとして同じプレイリストを返す期間. Defaults to timedelta(days=3).
        """
        self.oauth_client = oauth_client
        self.ttl = ttl
        self.playlists: dict[tuple[str], YoutubePlaylist] = {}

    async def create_playlist(self, title: str, description: str, video_ids: list[str]) -> YoutubePlaylist:
        tuple_video_ids = tuple(sorted(video_ids))
        if tuple_video_ids in self.playlists:
            cached_playlist = self.playlists[tuple_video_ids]
            if datetime.now() - self.ttl < cached_playlist.createdAt:
                return cached_playlist

        playlist_response = await self.oauth_client.insert_playlist(
            title,
            description,
        )
        if "id" not in playlist_response:
            if playlist_response.get("status") == 403:
                raise HTTPException(status_code=503, detail="Backend service are not able to request YouTube Data API")

            if playlist_response.get("status") == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded when creating YouTube playlist")

            raise HTTPException(status_code=500, detail="Failed to create YouTube playlist")

        playlist_id = playlist_response.get("id")
        status = await self.oauth_client.insert_playlist_items(playlist_id, video_ids)
        logger.info(f"Insert playlist items status: {status}")
        if status != 200:
            if status == 403:
                raise HTTPException(status_code=503, detail="Backend service are not able to request YouTube Data API")

            if status == 429:
                raise HTTPException(
                    status_code=429, detail="Rate limit exceeded when adding videos to YouTube playlist"
                )

            raise HTTPException(status_code=500, detail="Failed to add videos to YouTube playlist")

        playlist = YoutubePlaylist(
            id=playlist_id,
            title=title,
            description=description,
            createdAt=datetime.now(),
            videoIDs=video_ids,
        )

        self.playlists[tuple_video_ids] = playlist

        return playlist
