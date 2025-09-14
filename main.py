import asyncio
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.params import Query
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

from db.songs_database import SongsDatabase
from db.update_youtube_data import regist_scheduler
from utils.config import docs_description
from utils.songs_class import Song
from utils.fastapi_models import APIInfo, SongWithScore

load_dotenv()

scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler
    scheduler = regist_scheduler(db)
    yield
    if scheduler:
        scheduler.shutdown()


app = FastAPI(
    title="MIMIさん全曲分析 バックエンドAPI",
    description=docs_description,
    version="0.1.0",
    # terms_of_service="https://takechi.f5.si/",
    contact={
        "name": "takechi",
        "url": "https://x.com/takechi_scratch/",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    # openapi_tags=tags_metadata,
    lifespan=lifespan,
)


origins = [
    os.getenv("PRODUCTION_URL", "http://localhost:3000"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = SongsDatabase("db/data/songs.db")


@app.get("/", response_model=APIInfo)
async def api_info():
    """APIの基本情報を取得します。"""
    return APIInfo()

@app.get("/songs/{song_id}/", response_model=Song)
async def get_song_info(song_id: str):
    """指定した曲の情報を取得します。"""
    song = db.get_song_by_id(song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@app.get("/songs_all/", response_model=list[Song])
async def get_all_songs():
    """全ての曲の情報を取得します。"""
    songs = db.get_all_songs()
    return songs

@app.get("/songs_count/")
async def get_songs_count():
    """データベース内の曲数を取得します。"""
    count = db.get_songs_count()
    return {"count": count}

@app.get("/nearest_songs/", response_model=list[SongWithScore])
async def get_nearest_songs(target_song_id: str, limit: int = Query(10, ge=1)):
    """指定した条件に基づいて、最も近い曲を検索します。"""
    try:
        songs_queue = db.find_nearest_song(target_song_id, limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Target song not found")

    if not songs_queue:
        raise HTTPException(status_code=404, detail="No similar songs found")
    return [SongWithScore(id=song_in_queue.song.id, song=song_in_queue.song, score=float(song_in_queue.score)) for song_in_queue in songs_queue]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
