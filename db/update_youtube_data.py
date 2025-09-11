import os
import re
from datetime import datetime

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db.songs_database import SongsDatabase
from utils.songs_class import SongVideoData

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

    return SongVideoData(
        id=item.get("id", ""),
        title=snippet.get("title", ""),
        publishedTimestamp=published_timestamp,
        durationSeconds=duration_seconds,
        isPublishedInOriginalChannel= snippet.get("channelId", "") == os.getenv("OFFICIAL_CHANNEL_ID"),
        thumbnailURL=snippet.get("thumbnails", {}).get("high", {}).get("url", "")
    )


async def fetch_and_update_all(db: SongsDatabase) -> bool:
    if not os.getenv("YOUTUBE_DATA_API_KEY"):
        print("YOUTUBE_DATA_API_KEY is not set.")
        return False

    all_ids = [song.id for song in db.get_all_songs()]

    songs = []
    async with httpx.AsyncClient() as client:
        for i in range(0, len(all_ids), 50):
            response = await client.get(
                f"https://youtube.googleapis.com/youtube/v3/videos",
                params={
                    "part": "snippet,contentDetails",
                    "id": ",".join(all_ids[i:i+50]),
                    "key": os.getenv("YOUTUBE_DATA_API_KEY"),
                })

            if response.status_code == 200:
                data = response.json()
                songs.extend(handle_video_response(item) for item in data.get("items", []))
            else:
                print(f"Error fetching YouTube data: {response.text}")

    print(f"Fetched data for {len(songs)} videos from YouTube.")
    return db.update_songs_data_batch(songs)


def regist_scheduler(db: SongsDatabase) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(fetch_and_update_all, 'interval', args=[db], hours=24, next_run_time=datetime.now())
    scheduler.start()
    print("Scheduler started for updating YouTube data every 24 hours.")
    return scheduler


if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    load_dotenv()

    db = SongsDatabase("db/data/songs.db")
    asyncio.run(fetch_and_update_all(db))
