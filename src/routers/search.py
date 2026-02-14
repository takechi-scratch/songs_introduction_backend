from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from src.db.songs_database import SongsDatabase
from src.utils.dependencies import get_db
from src.utils.fastapi_models import SongSearchParams, SongWithScore
from src.utils.songs import Song

router = APIRouter(tags=["Search"])


@router.get("/search/", response_model=list[Song])
async def search(
    q: Optional[str] = Query(None, description="検索キーワード", example="初音ミク"),
    db: SongsDatabase = Depends(get_db),
):
    """キーワードがタイトル・クリエイター・歌詞などに含まれる曲を検索します。"""
    songs = db.search_songs(q=q)
    return songs


@router.get("/nearest-search/", response_model=list[SongWithScore])
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


@router.post("/advanced-search/", response_model=list[SongWithScore])
async def advanced_search(params: SongSearchParams, db: SongsDatabase = Depends(get_db)):
    """詳しいフィルター条件や、任意の重みをつけた類似度を用いた高度な検索を行います。"""
    if params.nearest and params.order and params.order != "similarityScore":
        raise HTTPException(status_code=400, detail="order must be 'similarityScore' when nearest is specified")

    search_query = {}
    search_query["q"] = params.q if params.q else None

    if params.filter:
        search_query |= params.filter.model_dump(exclude_none=True)

    songs = db.search_songs(**search_query, order=params.order, asc=params.asc)

    if params.nearest is None:
        songs = [SongWithScore(id=song.id, song=song, score=0.0) for song in songs]
        return songs[: params.limit] if params.limit else songs

    try:
        songs = db.find_nearest_song(
            target=params.nearest.targetSongID if params.nearest else None,
            songs=songs,
            limit=params.limit if params.limit else 10,
            parameters=params.nearest.parameters if params.nearest.parameters else None,
            is_reversed=params.asc,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Target song not found")

    if not songs:
        raise HTTPException(status_code=404, detail="No similar songs found")

    return songs
