import os
import re
from datetime import datetime
from logging import getLogger, StreamHandler, DEBUG

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db.songs_database import SongsDatabase
from utils.songs_class import Song, SongVideoData

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False


def handle_video_response(item: dict) -> SongVideoData:
    snippet = item.get("snippet", {})
    content_details = item.get("contentDetails", {})

    duration_str = content_details.get("duration", "PT0S")
    match = re.match(r"^PT((\d+)H)?((\d+)M)?((\d+)S)?$", duration_str)
    hours = int(match.group(2) or 0)
    minutes = int(match.group(4) or 0)
    seconds = int(match.group(6) or 0)
    duration_seconds = hours * 3600 + minutes * 60 + seconds

    published_at = datetime.fromisoformat(snippet.get("publishedAt", "1970-01-01T00:00:00Z").replace("Z", "+00:00"))
    published_timestamp = int(published_at.timestamp())

    thumbnails = snippet["thumbnails"]
    if "maxres" in thumbnails:
        thumbnail_url = thumbnails["maxres"].get("url", "")
    elif "high" in thumbnails:
        thumbnail_url = thumbnails["high"].get("url", "")
    else:
        thumbnail_url = ""

    return SongVideoData(
        id=item.get("id", ""),
        title=snippet.get("title", ""),
        publishedTimestamp=published_timestamp,
        durationSeconds=duration_seconds,
        thumbnailURL=thumbnail_url,
    )


async def fetch_and_update_all(db: SongsDatabase) -> bool:
    if not os.getenv("YOUTUBE_DATA_API_KEY"):
        logger.error("YOUTUBE_DATA_API_KEY is not set.")
        return False

    all_ids = [song.id for song in db.get_all_songs() if song.publishedType != -1]

    songs = []
    async with httpx.AsyncClient() as client:
        for i in range(0, len(all_ids), 50):
            response = await client.get(
                f"https://youtube.googleapis.com/youtube/v3/videos",
                params={
                    "part": "snippet,contentDetails",
                    "id": ",".join(all_ids[i : i + 50]),
                    "key": os.getenv("YOUTUBE_DATA_API_KEY"),
                },
            )

            if response.status_code == 200:
                data = response.json()
                songs.extend(handle_video_response(item) for item in data.get("items", []))
            else:
                logger.error(f"Error fetching YouTube data: {response.text}")

    logger.info(f"Fetched data for {len(songs)} videos from YouTube.")
    return db.update_songs_data_batch(songs)


async def fetch_youtube_data(db: SongsDatabase, song: Song | str) -> Song:
    if not os.getenv("YOUTUBE_DATA_API_KEY"):
        logger.error("YOUTUBE_DATA_API_KEY is not set.")
        return False

    if isinstance(song, str):
        song = db.get_song_by_id(song)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://youtube.googleapis.com/youtube/v3/videos",
            params={
                "part": "snippet,contentDetails",
                "id": song.id,
                "key": os.getenv("YOUTUBE_DATA_API_KEY"),
            },
        )

        if response.status_code == 200:
            raw_data = response.json()
            if len(raw_data.get("items", [])) == 0:
                raise ValueError(f"Song with ID {song.id} not found on YouTube.")

            songs_video_data = handle_video_response(raw_data["items"][0])

            new_song = song.model_copy(update=songs_video_data.model_dump())
        else:
            raise RuntimeError(f"Error fetching YouTube data: {response.text}")

    logger.info(f"Fetched video data (title: {new_song.title}) from YouTube.")
    return new_song


def regist_scheduler(db: SongsDatabase) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(fetch_and_update_all, "interval", args=[db], hours=24, next_run_time=datetime.now())
    scheduler.start()
    logger.info("Scheduler started for updating YouTube data every 24 hours.")
    return scheduler


if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv

    load_dotenv()

    db = SongsDatabase("db/data/songs.db")
    asyncio.run(fetch_and_update_all(db))
