import httpx

from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.config import ConfigStore
from utils.logger import logger

config_store = ConfigStore()

# Refresh Tokenの再発行
# https://developers.google.com/oauthplayground/


async def list_videos(video_ids: list[str]) -> list[dict]:
    config = await config_store.get_config()

    res = []
    async with httpx.AsyncClient() as client:
        for i in range(0, len(video_ids), 50):
            response = await client.get(
                f"https://youtube.googleapis.com/youtube/v3/videos",
                params={
                    "part": "snippet,contentDetails",
                    "id": ",".join(video_ids[i : i + 50]),
                    "key": config.youtube_data_api_key,
                },
            )

            if response.status_code != 200:
                logger.error(f"Error fetching YouTube data: {response.text}")

            data = response.json()
            res.extend(data.get("items", []))

    return res


class OAuthClient:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.access_token = None
        self._started = False

    async def start(self):
        """スケジューラーを起動し、初回のアクセストークンを取得"""
        if self._started:
            return

        await self.refresh_access_token()
        self.scheduler.start()
        self._started = True
        logger.info("OAuthClient started successfully.")

    async def refresh_access_token(self) -> dict:
        config = await config_store.get_config()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": config.youtube_oauth_client_id,
                    "client_secret": config.youtube_oauth_client_secret,
                    "refresh_token": config.youtube_oauth_refresh_token,
                    "grant_type": "refresh_token",
                },
            )

            if response.status_code != 200:
                logger.error(f"Error refreshing access token: {response.text}")
                return {}

        next_run_time = datetime.now() + timedelta(seconds=response.json().get("expires_in", 3600) - 60)
        self.scheduler.add_job(
            self.refresh_access_token,
            "date",
            run_date=next_run_time,
        )
        logger.info(f"Refreshed access token and scheduled next refresh at {next_run_time}.")
        self.access_token = response.json().get("access_token")

        return response.json()

    async def insert_playlist(self, title: str, description: str) -> dict:
        if not self.access_token:
            await self.refresh_access_token()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://youtube.googleapis.com/youtube/v3/playlists",
                params={"part": "snippet,status"},
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                json={
                    "snippet": {
                        "title": title,
                        "description": description,
                    },
                    "status": {
                        "privacyStatus": "public",
                    },
                },
            )

            if response.status_code != 200:
                logger.error(f"Error creating YouTube playlist: {response.text}")
                return {"status": response.status_code}

            return response.json()

    async def insert_playlist_items(self, playlist_id: str, video_ids: list[str]) -> int:
        if not self.access_token:
            await self.refresh_access_token()

        url = "https://youtube.googleapis.com/youtube/v3/playlistItems"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        # 非同期リクエストは409の恐れがあるのでやらない
        async with httpx.AsyncClient() as client:
            results = []
            for video_id in video_ids:
                results.append(
                    await client.post(
                        url,
                        params={"part": "snippet"},
                        headers=headers,
                        json=self._playlist_items_payload(playlist_id, video_id),
                    )
                )
                logger.debug(f"Added video {video_id} to playlist {playlist_id}.")

            # results = await asyncio.gather(*tasks)
            status = 200

            for res in results:
                if res.status_code != 200:
                    logger.error(f"Error adding video to playlist: {res.text}")
                    status = res.status_code

        return status

    def _playlist_items_payload(self, playlist_id: str, video_id: str) -> dict:
        return {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id,
                },
            }
        }
