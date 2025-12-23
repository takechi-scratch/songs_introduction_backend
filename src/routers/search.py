from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from src.db.songs_database import SongsDatabase
from src.utils.dependencies import get_db
from src.utils.fastapi_models import AdvancedNearestSearch, SongWithScore
from src.utils.songs import Song

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/filter/", response_model=list[Song])
async def filter_songs(
    id: Optional[str] = None,
    title: Optional[str] = None,
    publishedType: Optional[bool] = None,
    vocal: Optional[str] = None,
    illustrations: Optional[str] = None,
    movie: Optional[str] = None,
    comment: Optional[str] = None,
    mainChord: Optional[str] = None,
    mainKey: Optional[int] = None,
    publishedAfter: Optional[int] = None,
    publishedBefore: Optional[int] = None,
    order: Optional[
        Literal[
            "id",
            "title",
            "publishedTimestamp",
            "durationSeconds",
            "bpm",
            "mainKey",
            "chordRate6451",
            "chordRate4561",
            "pianoRate",
            "modulationTimes",
        ]
    ] = None,
    asc: Optional[bool] = Query(None),
    db: SongsDatabase = Depends(get_db),
):
    """指定した条件に基づいて曲を検索します。"""
    songs = db.search_songs(
        id=id,
        title=title,
        publishedType=publishedType,
        vocal=vocal,
        illustrations=illustrations,
        movie=movie,
        comment=comment,
        mainChord=mainChord,
        mainKey=mainKey,
        order=order,
        asc=asc,
        publishedAfter=publishedAfter,
        publishedBefore=publishedBefore,
    )
    return songs


@router.get("/nearest/", response_model=list[SongWithScore])
async def get_nearest_songs(target_song_id: str, limit: int = Query(10, ge=1), db: SongsDatabase = Depends(get_db)):
    """指定した条件に基づいて、最も近い曲を検索します。"""
    try:
        songs_queue = db.find_nearest_song(target_song_id, limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Target song not found")

    if not songs_queue:
        raise HTTPException(status_code=404, detail="No similar songs found")
    return [
        SongWithScore(
            id=song_in_queue.song.id,
            song=song_in_queue.song,
            score=float(song_in_queue.score),
        )
        for song_in_queue in songs_queue
    ]


@router.post("/nearest_advanced/", response_model=list[SongWithScore])
async def get_nearest_songs_advanced(data: AdvancedNearestSearch, db: SongsDatabase = Depends(get_db)):
    """指定した条件に基づいて、最も近い曲を検索します。"""

    try:
        songs_queue = db.find_nearest_song(
            data.target_song_id,
            data.limit,
            data.parameters,
            data.is_reversed,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Target song not found")

    if not songs_queue:
        raise HTTPException(status_code=404, detail="No similar songs found")
    return [
        SongWithScore(
            id=song_in_queue.song.id,
            song=song_in_queue.song,
            score=float(song_in_queue.score),
        )
        for song_in_queue in songs_queue
    ]
