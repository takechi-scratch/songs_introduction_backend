import re
from datetime import datetime
from utils.logger import logger

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db.songs_database import SongsDatabase
from utils.config import ConfigStore
from utils.songs_class import Song, SongVideoData
from utils.youtube.api import list_videos


config_store = ConfigStore()


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
    all_ids = [song.id for song in db.get_all_songs() if song.publishedType != -1]

    songs = [handle_video_response(item) for item in await list_videos(all_ids)]

    logger.info(f"Fetched data for {len(songs)} videos from YouTube.")
    return db.update_songs_data_batch(songs)


async def fetch_youtube_data(db: SongsDatabase, song: Song | str) -> Song:
    if isinstance(song, str):
        song = db.get_song_by_id(song)

    raw_data = await list_videos([song.id])
    if len(raw_data) == 0:
        raise ValueError(f"Song with ID {song.id} not found on YouTube.")

    songs_video_data = handle_video_response(raw_data[0])

    new_song = song.model_copy(update=songs_video_data.model_dump())

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
